#!/usr/bin/env python3
"""
High-speed stock scanner using yfinance only, with proxy rotation and retries.
- Loads combined ticker universe (NASDAQ complete + NASDAQ-only) and de-duplicates
- Uses up to 10 threads (default) with per-request proxy sessions
- Detects rate limiting (HTTP 429/blocked), rotates proxy immediately, tracks, and retries at end
- Focuses on yfinance fast_info for sub-200ms per-ticker latency (avoids heavy endpoints)
- Writes results into existing Django Stock model (update_or_create)

Notes:
- Only fields that exist in the current Stock model are persisted to DB
- Heavy endpoints (full info, earnings, long history, 1m intraday) are skipped to keep latency low
- Additional analytics are best-effort and may be None by design for speed
"""

from __future__ import annotations

import os
import sys
import time
import json
import math
import glob
import logging
import random
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
try:
    from curl_cffi import requests as cf_requests  # yfinance prefers curl_cffi sessions
except Exception:
    cf_requests = None  # type: ignore
import pandas as pd
import yfinance as yf

# Optional Django setup for DB writes (graceful fallback when unavailable)
DJANGO_AVAILABLE = False
try:
    import django  # type: ignore
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
    django.setup()
    from django.utils import timezone as django_timezone  # type: ignore
    from django.db import close_old_connections as django_close_old_connections  # type: ignore
    from stocks.models import Stock, StockPrice  # type: ignore
    DJANGO_AVAILABLE = True
except Exception:
    django_timezone = None
    Stock = None  # type: ignore
    StockPrice = None  # type: ignore
    def django_close_old_connections():  # type: ignore
        return None

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)
# Quiet verbose logs from yfinance internals
for _name in (
    'yfinance', 'yfinance.scrapers', 'yfinance.data', 'yfinance.tz', 'yf'
):
    try:
        logging.getLogger(_name).setLevel(logging.WARNING)
    except Exception:
        pass

# ----------------------------- Utility helpers ----------------------------- #

def safe_decimal(value: Any) -> Optional[Decimal]:
    if value is None:
        return None
    try:
        if isinstance(value, (int, float)):
            if math.isfinite(float(value)):
                return Decimal(str(value))
            return None
        return Decimal(str(value))
    except Exception:
        return None


def is_rate_limit_error(exc: Exception) -> bool:
    text = str(exc).lower()
    substrings = [
        '429', 'too many requests', 'rate limit', 'rate-limited', 'blocked',
        'yahoo finance is down', 'yahoo finance may be down',
        'invalid crumb', 'unauthorized', 'unable to access this feature'
    ]
    return any(s in text for s in substrings)


# ----------------------------- Proxy management ---------------------------- #

class ProxyManager:
    """Thread-safe round-robin proxy/session manager."""
    def __init__(self, proxies: List[str]):
        self.proxies = list(dict.fromkeys([p.strip() for p in proxies if p]))
        self._index = 0
        self._lock = None
        try:
            import threading
            self._lock = threading.Lock()
        except Exception:
            self._lock = None

    def _next_index(self) -> int:
        if not self.proxies:
            return -1
        if self._lock:
            with self._lock:
                self._index = (self._index + 1) % len(self.proxies)
                return self._index
        self._index = (self._index + 1) % len(self.proxies)
        return self._index

    def get_session(self, rotate: bool = False) -> Optional[object]:
        if not self.proxies:
            return None
        idx = self._next_index() if rotate else self._index
        if idx < 0 and self.proxies:
            idx = 0
        proxy = self.proxies[idx % len(self.proxies)]
        # Prefer curl_cffi session when available (required by yfinance >=0.2.66)
        if cf_requests is not None:
            sess = cf_requests.Session()
            sess.proxies = {'http': proxy, 'https': proxy}
            sess.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
            return sess
        # Fallback to requests (may be rejected by yfinance)
        sess = requests.Session()
        sess.proxies = {'http': proxy, 'https': proxy}
        sess.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        # Conservative timeouts via HTTPAdapter are optional; rely on yfinance timeouts
        return sess

    def rotate_and_get_session(self) -> Optional[requests.Session]:
        return self.get_session(rotate=True)


class YahooQuoteClient:
    """Lightweight client for Yahoo quote API with automatic crumb/cookie handling.
    Uses a persistent no-proxy session to avoid 401/crumb issues; batch-friendly.
    """
    BASE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"

    def __init__(self) -> None:
        # Prefer curl_cffi session for yfinance compatibility
        if cf_requests is not None:
            sess = cf_requests.Session()
        else:
            sess = requests.Session()
        sess.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        self.session = sess
        self.crumb: Optional[str] = None
        self._init_crumb()

    def _init_crumb(self) -> None:
        try:
            # Warm cookies then retrieve crumb
            self.session.get('https://finance.yahoo.com', timeout=6)
            r = self.session.get('https://query1.finance.yahoo.com/v1/test/getcrumb', timeout=6)
            if getattr(r, 'status_code', 0) == 200:
                txt = (r.text or '').strip()
                if txt:
                    self.crumb = txt
        except Exception:
            self.crumb = None

    def fetch_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        if not symbols:
            return {}
        params = {'symbols': ','.join(symbols)}
        if self.crumb:
            params['crumb'] = self.crumb
        try:
            r = self.session.get(self.BASE_URL, params=params, timeout=8)
            # Refresh crumb on auth failures and retry once
            body = r.text or ''
            if r.status_code in (401, 403) or ('Invalid Crumb' in body):
                self._init_crumb()
                if self.crumb:
                    params['crumb'] = self.crumb
                r = self.session.get(self.BASE_URL, params=params, timeout=8)
            r.raise_for_status()
            data = r.json()
            result = data.get('quoteResponse', {}).get('result', [])
            out: Dict[str, Dict[str, Any]] = {}
            for item in result or []:
                sym = item.get('symbol')
                if not sym:
                    continue
                out[sym.upper()] = item
            return out
        except Exception as e:
            logger.error(f"Quote fetch failed for {len(symbols)} tickers: {e}")
            return {}

def load_proxies(proxy_file: str) -> List[str]:
    try:
        with open(proxy_file, 'r') as f:
            data = json.load(f)
        if isinstance(data, dict):
            for key in ('proxies', 'working_proxies'):
                if key in data and isinstance(data[key], list):
                    return [p for p in data[key] if isinstance(p, str) and p]
            # Flatten dict values as last resort
            return [v for v in data.values() if isinstance(v, str) and v]
        if isinstance(data, list):
            return [p for p in data if isinstance(p, str) and p]
        return []
    except FileNotFoundError:
        logger.warning(f"Proxy file not found: {proxy_file}")
        return []
    except Exception as e:
        logger.error(f"Failed to load proxies: {e}")
        return []


# --------------------------- Ticker universe load -------------------------- #

def _import_list_from_latest_py(directory: str, pattern: str, var_name: str) -> List[str]:
    files = sorted(glob.glob(os.path.join(directory, pattern)))
    if not files:
        return []
    latest = files[-1]
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("tickers_mod", latest)
        mod = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
        data = getattr(mod, var_name, [])
        if isinstance(data, list):
            return [str(x).strip().upper() for x in data if str(x).strip()]
    except Exception as e:
        logger.error(f"Failed importing {var_name} from {latest}: {e}")
    return []


def load_combined_tickers() -> List[str]:
    base = os.path.dirname(os.path.abspath(__file__))
    nasdaq_only_dir = os.path.join(base, 'data', 'nasdaq_only')
    complete_dir = os.path.join(base, 'data', 'complete_nasdaq')

    nasdaq_only = _import_list_from_latest_py(
        nasdaq_only_dir,
        'nasdaq_only_tickers_*.py',
        'NASDAQ_ONLY_TICKERS'
    )
    complete = _import_list_from_latest_py(
        complete_dir,
        'complete_nasdaq_tickers_*.py',
        'COMPLETE_NASDAQ_TICKERS'
    )
    # De-dup while preserving order preference: nasdaq_only first, then rest
    seen = set()
    combined: List[str] = []
    for s in nasdaq_only + complete:
        if s not in seen:
            seen.add(s)
            combined.append(s)
    return combined


# --------------------------- Technical indicators -------------------------- #

def compute_rsi(series: pd.Series, period: int = 14) -> Optional[float]:
    if series is None or len(series) < period + 1:
        return None
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ema_up = up.ewm(alpha=1/period, adjust=False).mean()
    ema_down = down.ewm(alpha=1/period, adjust=False).mean()
    rs = ema_up / ema_down.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    try:
        value = float(rsi.iloc[-1])
        return value if math.isfinite(value) else None
    except Exception:
        return None


def compute_atr(df: pd.DataFrame, period: int = 14) -> Optional[float]:
    if df is None or df.empty or len(df) < period + 1:
        return None
    high = df['High']
    low = df['Low']
    close = df['Close']
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low),
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    try:
        value = float(atr.iloc[-1])
        return value if math.isfinite(value) else None
    except Exception:
        return None


def compute_macd(series: pd.Series) -> Tuple[Optional[float], Optional[float]]:
    if series is None or len(series) < 26 + 9:
        return None, None
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    try:
        macd_val = float(macd.iloc[-1])
        signal_val = float(signal.iloc[-1])
        return (macd_val if math.isfinite(macd_val) else None,
                signal_val if math.isfinite(signal_val) else None)
    except Exception:
        return None, None


def compute_stochastic(df: pd.DataFrame, period: int = 14) -> Optional[float]:
    if df is None or df.empty or len(df) < period:
        return None
    low_min = df['Low'].rolling(window=period).min()
    high_max = df['High'].rolling(window=period).max()
    stoch = (df['Close'] - low_min) / (high_max - low_min)
    try:
        value = float(stoch.iloc[-1] * 100)
        return value if math.isfinite(value) else None
    except Exception:
        return None


def compute_sma(series: pd.Series, window: int) -> Optional[float]:
    if series is None or len(series) < window:
        return None
    try:
        val = float(series.rolling(window=window).mean().iloc[-1])
        return val if math.isfinite(val) else None
    except Exception:
        return None


def compute_ema(series: pd.Series, span: int) -> Optional[float]:
    if series is None or len(series) < span:
        return None
    try:
        val = float(series.ewm(span=span, adjust=False).mean().iloc[-1])
        return val if math.isfinite(val) else None
    except Exception:
        return None


def compute_vwap_1m(ticker: yf.Ticker) -> Optional[float]:
    try:
        intraday = ticker.history(period="1d", interval="1m", prepost=False)
        if intraday is None or intraday.empty or 'Volume' not in intraday:
            return None
        typical = (intraday['High'] + intraday['Low'] + intraday['Close']) / 3.0
        vol = intraday['Volume'].replace(0, pd.NA)
        vwap = (typical * vol).sum() / vol.sum()
        if pd.isna(vwap):
            return None
        val = float(vwap)
        return val if math.isfinite(val) else None
    except Exception:
        return None


# ------------------------------ Core scanning ------------------------------ #

class StockScanner:
    def __init__(
        self,
        threads: int = 10,
        timeout: int = 8,
        proxy_file: str = 'working_proxies.json',
        use_proxies: bool = True,
        db_enabled: bool = True,
    ) -> None:
        self.threads = threads
        self.timeout = timeout
        self.use_proxies = use_proxies
        self.proxy_mgr = ProxyManager(load_proxies(proxy_file) if use_proxies else [])
        self.rate_limited: List[str] = []
        self.results: List[Dict[str, Any]] = []
        self._earnings_cache: Dict[str, Optional[datetime]] = {}
        self.db_enabled = db_enabled and DJANGO_AVAILABLE
        # Target completeness threshold (price, volume, market_cap present)
        self.completeness_threshold = 0.92
        # Reusable no-proxy session preferred by yfinance (curl_cffi when available)
        self._no_proxy_session = None
        try:
            if cf_requests is not None:
                s = cf_requests.Session()
                s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
                self._no_proxy_session = s
            else:
                s = requests.Session()
                s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
                self._no_proxy_session = s
        except Exception:
            self._no_proxy_session = None
        # Yahoo direct quote client for batch validation and fast fields
        self._yahoo_client = YahooQuoteClient()

    # ------------------------- Batch download pipeline ------------------------- #
    def _download_chunk(self, symbols: List[str], session: Optional[object], timeout: int) -> Optional[pd.DataFrame]:
        try:
            df = yf.download(
                tickers=symbols,
                period='5d',
                interval='1d',
                group_by='ticker',
                auto_adjust=False,
                progress=False,
                threads=True,
                session=session,
            )
            return df
        except Exception as e:
            logger.error(f"download() failed for {len(symbols)} tickers: {e}")
            return None

    def _build_rows_from_download(self, df: pd.DataFrame, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        rows: Dict[str, Dict[str, Any]] = {}
        if df is None or df.empty:
            return rows
        multi = isinstance(df.columns, pd.MultiIndex)
        try:
            last_idx = df.index[-1]
        except Exception:
            return rows
        for s in symbols:
            try:
                if multi:
                    sub = df.get(s)
                    if sub is None or sub.empty:
                        continue
                    row = sub.loc[last_idx]
                    close = row.get('Close')
                    volume = row.get('Volume')
                    low = row.get('Low')
                    high = row.get('High')
                    # prior close for change
                    prev_close = None
                    if len(sub.index) >= 2:
                        try:
                            prev_close = float(sub.iloc[-2].get('Close'))
                        except Exception:
                            prev_close = None
                else:
                    # Single ticker frame edge case
                    row = df.iloc[-1]
                    close = row.get('Close')
                    volume = row.get('Volume')
                    low = row.get('Low')
                    high = row.get('High')
                    prev_close = float(df.iloc[-2].get('Close')) if len(df) >= 2 else None

                if pd.isna(close) or pd.isna(volume):
                    continue
                price = float(close)
                vol = int(volume)
                day_low = float(low) if not pd.isna(low) else None
                day_high = float(high) if not pd.isna(high) else None
                days_range = None
                if day_low is not None and day_high is not None:
                    try:
                        days_range = f"{day_low:.2f} - {day_high:.2f}"
                    except Exception:
                        days_range = None
                change_percent = None
                if prev_close is not None and prev_close != 0:
                    try:
                        change_percent = ((price - float(prev_close)) / float(prev_close)) * 100.0
                    except Exception:
                        change_percent = None
                rows[s] = {
                    'ticker': s,
                    'symbol': s,
                    'company_name': s,
                    'name': s,
                    'exchange': 'NASDAQ',
                    'current_price': safe_decimal(price),
                    'days_low': safe_decimal(day_low),
                    'days_high': safe_decimal(day_high),
                    'days_range': days_range,
                    'volume': vol,
                    'volume_today': vol,
                    'avg_volume_3mon': None,
                    'dvav': None,
                    'market_cap': None,  # batch path does not fetch mc to stay fast
                    'shares_available': None,
                    'pe_ratio': None,
                    'dividend_yield': None,
                    'one_year_target': None,
                    'week_52_low': None,
                    'week_52_high': None,
                    'earnings_per_share': None,
                    'book_value': None,
                    'price_to_book': None,
                    'bid_price': None,
                    'ask_price': None,
                    'bid_ask_spread': None,
                    'price_change_today': None,
                    'price_change_week': None,
                    'price_change_month': None,
                    'price_change_year': None,
                    'change_percent': safe_decimal(change_percent),
                    'market_cap_change_3mon': None,
                    'pe_change_3mon': None,
                    'last_updated': (django_timezone.now() if django_timezone else datetime.now(timezone.utc)),
                    'created_at': (django_timezone.now() if django_timezone else datetime.now(timezone.utc)),
                }
            except Exception:
                continue
        return rows

    def scan_batch(self, symbols: List[str], csv_out: Optional[str] = None, chunk_size: int = 250) -> Dict[str, Any]:
        start = time.time()
        # Normalize symbols
        symbols = [s.strip().upper() for s in symbols if s and s.strip()]
        # Split into chunks
        chunks: List[List[str]] = [symbols[i:i+chunk_size] for i in range(0, len(symbols), chunk_size)]
        results: Dict[str, Dict[str, Any]] = {}
        rate_limited_chunks = 0

        def process_chunk(chunk: List[str]) -> Tuple[List[str], Dict[str, Dict[str, Any]]]:
            # Try with (proxy or none) sessions, rotate on rate limit
            max_attempts = 3
            attempt = 0
            session = None
            while attempt < max_attempts:
                df = self._download_chunk(chunk, session=session, timeout=self.timeout)
                rows = self._build_rows_from_download(df, chunk)
                # If we got some rows, accept; else rotate proxy and retry smaller chunk_size
                if rows:
                    return chunk, rows
                attempt += 1
                # rotate proxy
                if self.use_proxies and self.proxy_mgr.proxies:
                    session = self.proxy_mgr.rotate_and_get_session()
                else:
                    session = None
                # brief backoff
                time.sleep(min(1.0 * attempt, 3.0))
            return chunk, {}

        # Run up to self.threads chunks concurrently
        with ThreadPoolExecutor(max_workers=self.threads) as ex:
            futures = [ex.submit(process_chunk, ch) for ch in chunks]
            for fut in as_completed(futures):
                ch, rows = fut.result()
                if not rows:
                    rate_limited_chunks += 1
                results.update(rows)

        # Keep only complete rows (price & volume present)
        complete = {s: p for s, p in results.items() if p.get('current_price') is not None and p.get('volume') is not None}

        # CSV export
        if csv_out:
            try:
                df = pd.DataFrame([{k: v for k, v in p.items() if not str(k).startswith('_')} for p in complete.values()])
                for col in df.columns:
                    if df[col].map(lambda x: isinstance(x, Decimal)).any():
                        df[col] = df[col].map(lambda v: float(v) if isinstance(v, Decimal) else (float('nan') if v is None else v))
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                df.to_csv(csv_out, index=False)
                logger.info(f"Saved CSV: {csv_out} with {len(df)} rows")
            except Exception as e:
                logger.error(f"CSV export failed: {e}")

        duration = time.time() - start
        completeness_ratio = round(len(complete) / max(1, len(symbols)), 3)
        return {
            'total': len(symbols),
            'success': len(complete),
            'failed': (len(symbols) - len(complete)),
            'failed_symbols': [s for s in symbols if s not in complete],
            'proxies_available': len(self.proxy_mgr.proxies) if self.use_proxies else 0,
            'rate_limited_chunks': rate_limited_chunks,
            'csv_out': csv_out,
            'duration_sec': round(duration, 2),
            'rate_per_sec': round(len(symbols) / duration, 2) if duration > 0 else None,
            'completeness_ratio': completeness_ratio,
        }

    @staticmethod
    def _is_complete(payload: Dict[str, Any]) -> bool:
        return (
            payload.get('current_price') is not None and
            payload.get('volume') is not None and
            payload.get('market_cap') is not None
        )

    def _batch_download_ohlcv(self, symbols: List[str], session: Optional[object]) -> Dict[str, Dict[str, Any]]:
        """Fetch last daily OHLCV for many tickers at once using yfinance.download.
        Returns mapping: sym -> { 'close': float|None, 'high': float|None, 'low': float|None, 'volume': float|None }
        """
        result: Dict[str, Dict[str, Any]] = {s: {'close': None, 'high': None, 'low': None, 'volume': None} for s in symbols}
        try:
            # yfinance supports list of tickers; group_by='ticker' yields columns per ticker
            df = yf.download(
                tickers=symbols,
                period='1d',
                interval='1d',
                group_by='ticker',
                auto_adjust=False,
                progress=False,
                # Avoid proxies; pass persistent no-proxy session to minimize crumb
                session=self._no_proxy_session,
                threads=True
            )
            if df is None or df.empty:
                return result
            # Handle single vs multi-ticker frames
            if isinstance(df.columns, pd.MultiIndex):
                last_idx = df.index[-1]
                for s in symbols:
                    try:
                        sub = df[s]
                        if sub is None or sub.empty:
                            continue
                        row = sub.loc[last_idx]
                        result[s] = {
                            'close': float(row.get('Close')) if pd.notna(row.get('Close')) else None,
                            'high': float(row.get('High')) if pd.notna(row.get('High')) else None,
                            'low': float(row.get('Low')) if pd.notna(row.get('Low')) else None,
                            'volume': float(row.get('Volume')) if pd.notna(row.get('Volume')) else None,
                        }
                    except Exception:
                        continue
            else:
                # Single ticker
                try:
                    row = df.iloc[-1]
                    result[symbols[0]] = {
                        'close': float(row.get('Close')) if pd.notna(row.get('Close')) else None,
                        'high': float(row.get('High')) if pd.notna(row.get('High')) else None,
                        'low': float(row.get('Low')) if pd.notna(row.get('Low')) else None,
                        'volume': float(row.get('Volume')) if pd.notna(row.get('Volume')) else None,
                    }
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Batch download failed for {len(symbols)} tickers: {e}")
        return result

    def _fill_market_cap_via_info(self, symbols: List[str], payloads: Dict[str, Dict[str, Any]], target_complete: int) -> None:
        """Call get_info for a subset of symbols to obtain sharesOutstanding and marketCap.
        Stops when completeness target is met or all attempted.
        """
        completed = sum(1 for p in payloads.values() if self._is_complete(p))
        if completed >= target_complete:
            return

        def work(sym: str) -> None:
            nonlocal completed
            try:
                # Use direct session (no proxies) for info to avoid crumb issues
                t = yf.Ticker(sym, session=None)
                info = None
                try:
                    # yfinance >=0.2.66 recommends .info, but .get_info() returns dict too
                    info = t.info
                except Exception as e:
                    if is_rate_limit_error(e):
                        return
                if not isinstance(info, dict):
                    return
                p = payloads.get(sym)
                if not p:
                    return
                if p.get('market_cap') is None:
                    mc = info.get('marketCap')
                    if isinstance(mc, (int, float)):
                        p['market_cap'] = int(mc)
                if p.get('shares_available') is None:
                    shares = info.get('sharesOutstanding')
                    if isinstance(shares, (int, float)):
                        p['shares_available'] = int(shares)
                # Derive if still missing
                if p.get('market_cap') is None and p.get('current_price') is not None and p.get('shares_available') is not None:
                    try:
                        p['market_cap'] = int(float(p['current_price']) * float(p['shares_available']))
                    except Exception:
                        pass
                if self._is_complete(p):
                    completed += 1
            except Exception:
                return

        # Attempt in small batches with threads
        to_try = [s for s in symbols if not self._is_complete(payloads.get(s, {}))]
        if not to_try:
            return
        batch_size = 64
        for i in range(0, len(to_try), batch_size):
            if completed >= target_complete:
                break
            chunk = to_try[i:i+batch_size]
            with ThreadPoolExecutor(max_workers=min(10, len(chunk))) as ex:
                list(ex.map(work, chunk))

        # As last resort to reach completeness target, try shares_full for remaining
        if completed < target_complete:
            remaining = [s for s in symbols if not self._is_complete(payloads.get(s, {}))]
            def work_shares(sym: str) -> None:
                nonlocal completed
                p = payloads.get(sym)
                if not p or p.get('market_cap') is not None or p.get('current_price') is None:
                    return
                try:
                    t = yf.Ticker(sym, session=None)
                    df_sh = t.get_shares_full()
                    if df_sh is None or df_sh.empty:
                        return
                    last = df_sh['Shares'].dropna().iloc[-1]
                    if isinstance(last, (int, float)):
                        p['shares_available'] = int(last)
                        p['market_cap'] = int(float(p['current_price']) * float(p['shares_available']))
                        if self._is_complete(p):
                            completed += 1
                except Exception:
                    return
            for i in range(0, len(remaining), 32):
                if completed >= target_complete:
                    break
                chunk = remaining[i:i+32]
                with ThreadPoolExecutor(max_workers=min(8, len(chunk))) as ex:
                    list(ex.map(work_shares, chunk))

    def _get_earnings_date(self, ticker: yf.Ticker, symbol: str) -> Optional[datetime]:
        if symbol in self._earnings_cache:
            return self._earnings_cache[symbol]
        dt_val: Optional[datetime] = None
        try:
            # Preferred endpoint
            df = ticker.get_earnings_dates(limit=1)
            if df is not None and not df.empty:
                col_name = next((c for c in df.columns if 'Earnings' in c and 'Date' in c), df.columns[0])
                raw = df[col_name].iloc[0]
                if isinstance(raw, (pd.Timestamp, datetime)):
                    dt_val = raw.to_pydatetime() if isinstance(raw, pd.Timestamp) else raw
        except Exception:
            dt_val = None
        if dt_val is None:
            try:
                cal = ticker.calendar
                if isinstance(cal, pd.DataFrame) and not cal.empty:
                    # Some yfinance versions put next earnings in index 'Earnings Date'
                    if 'Earnings Date' in cal.index:
                        raw = cal.loc['Earnings Date'].dropna().iloc[0]
                        if isinstance(raw, (pd.Timestamp, datetime)):
                            dt_val = raw.to_pydatetime() if isinstance(raw, pd.Timestamp) else raw
            except Exception:
                pass
        self._earnings_cache[symbol] = dt_val
        return dt_val

    def _fetch_symbol(self, symbol: str, idx: int) -> Tuple[str, Optional[Dict[str, Any]], bool]:
        """Return (symbol, data_dict_or_none, rate_limited)."""
        # Close old DB connections only if Django is available
        if self.db_enabled:
            django_close_old_connections()
        session = None
        if self.use_proxies and self.proxy_mgr.proxies:
            # Round-robin session (curl_cffi preferred, fall back to requests)
            s = self.proxy_mgr.get_session(rotate=True)
            # Pass session through to yfinance (supports both curl_cffi and requests sessions)
            session = s
        try:
            ticker = yf.Ticker(symbol, session=session)

            # Fast path: rely on fast_info only (single lightweight call)
            fast = None
            try:
                fast = ticker.fast_info
            except Exception as e:
                if is_rate_limit_error(e):
                    # rotate proxy if possible and retry once
                    if self.use_proxies:
                        self.proxy_mgr.rotate_and_get_session()
                    try:
                        fast = yf.Ticker(symbol, session=session).fast_info
                    except Exception:
                        return symbol, None, True

            # Skip heavy endpoints (history/info/calendar/earnings) to meet <200ms budget
            hist = None
            info = None

            # Helper to read camelCase keys robustly
            def fget(keys: List[str]) -> Optional[float]:
                if fast is None:
                    return None
                for k in keys:
                    try:
                        val = fast.get(k)
                    except Exception:
                        val = None
                    if val is not None:
                        try:
                            return float(val)
                        except Exception:
                            return None
                return None

            # Current price with broader fallbacks
            current_price = fget(['lastPrice', 'regularMarketPrice', 'open', 'previousClose', 'regularMarketPreviousClose', 'fiftyDayAverage', 'twoHundredDayAverage'])
            # Day-over-day change using fast_info when available
            price_change_today = None
            change_percent = None
            if current_price is not None:
                prev_close = fget(['previousClose', 'regularMarketPreviousClose'])
                try:
                    if prev_close is not None and float(prev_close) != 0:
                        price_change_today = float(current_price) - float(prev_close)
                        change_percent = (price_change_today / float(prev_close)) * 100.0
                except Exception:
                    price_change_today = None
                    change_percent = None

            # Day low/high/volume
            days_low = fget(['dayLow'])
            days_high = fget(['dayHigh'])
            volume_today = fget(['lastVolume', 'regularMarketVolume', 'tenDayAverageVolume', 'threeMonthAverageVolume'])

            avg_volume_3mon = fget(['threeMonthAverageVolume']) or fget(['tenDayAverageVolume'])

            # Market cap
            market_cap = fget(['marketCap'])
            # Derive from price × shares outstanding when missing (info skipped for speed)
            shares_outstanding = None

            # 52-week
            wk_low = fget(['yearLow'])
            wk_high = fget(['yearHigh'])
            # No fallback to info (skipped for speed)

            # Shares available from float/sharesOutstanding best-effort
            shares_available = fget(['shares'])
            if (market_cap is None) and (current_price is not None) and (shares_available is not None):
                try:
                    market_cap = float(current_price) * float(shares_available)
                except Exception:
                    pass

            # Bid/Ask
            bid_price = ask_price = None
            # info skipped for speed

            # Earnings per share / book / price-to-book / pe
            eps = None
            # info skipped for speed
            book_value = None

            pe_ratio = None
            # info skipped for speed; derive only if eps available (not available here)

            price_to_book = None
            if current_price and book_value:
                try:
                    price_to_book = float(current_price) / float(book_value) if float(book_value) != 0 else None
                except Exception:
                    price_to_book = None

            dividend_yield = None

            one_year_target = None

            # Changes: day/week/month/year (only day via fast_info; others skipped for speed)
            price_change_week = price_change_month = price_change_year = None

            volume = volume_today
            # Fallback to today's volume if average missing
            if avg_volume_3mon is None and volume is not None:
                try:
                    avg_volume_3mon = int(volume)
                except Exception:
                    pass

            dvav = None
            if volume and avg_volume_3mon:
                try:
                    dvav = float(volume) / float(avg_volume_3mon) if float(avg_volume_3mon) != 0 else None
                except Exception:
                    dvav = None

            # Indicators skipped for speed
            rsi14 = atr14 = sma_5 = sma_20 = ema_5 = ema_20 = None
            macd_val = macd_signal = None
            stoch14 = None
            vwap = None

            # Derived strings
            days_range = None
            if days_low is not None and days_high is not None:
                try:
                    days_range = f"{float(days_low):.2f} - {float(days_high):.2f}"
                except Exception:
                    days_range = None

            bid_ask_spread = None
            if bid_price is not None and ask_price is not None:
                try:
                    bid_ask_spread = f"{float(bid_price):.2f} - {float(ask_price):.2f}"
                except Exception:
                    bid_ask_spread = None

            # Compose DB payload (only existing Stock fields)
            payload: Dict[str, Any] = {
                'ticker': symbol,
                'symbol': symbol,
                'company_name': symbol,
                'name': symbol,
                'exchange': 'NASDAQ',
                'current_price': safe_decimal(current_price),
                'days_low': safe_decimal(days_low),
                'days_high': safe_decimal(days_high),
                'days_range': days_range or '',
                'volume': int(volume) if volume is not None else None,
                'volume_today': int(volume) if volume is not None else None,
                'avg_volume_3mon': int(avg_volume_3mon) if avg_volume_3mon is not None else None,
                'dvav': safe_decimal(dvav),
                'market_cap': int(market_cap) if market_cap is not None else None,
                'shares_available': int(shares_available) if shares_available is not None else None,
                'pe_ratio': safe_decimal(pe_ratio),
                'dividend_yield': safe_decimal(dividend_yield),
                'one_year_target': safe_decimal(one_year_target),
                'week_52_low': safe_decimal(wk_low),
                'week_52_high': safe_decimal(wk_high),
                'earnings_per_share': safe_decimal(eps),
                'book_value': safe_decimal(book_value),
                'price_to_book': safe_decimal(price_to_book),
                'bid_price': safe_decimal(bid_price),
                'ask_price': safe_decimal(ask_price),
                'bid_ask_spread': bid_ask_spread or '',
                'price_change_today': safe_decimal(price_change_today),
                'price_change_week': safe_decimal(price_change_week),
                'price_change_month': safe_decimal(price_change_month),
                'price_change_year': safe_decimal(price_change_year),
                'change_percent': safe_decimal(change_percent),
                'market_cap_change_3mon': None,
                'pe_change_3mon': None,
                'last_updated': (django_timezone.now() if django_timezone else datetime.now(timezone.utc)),
                'created_at': (django_timezone.now() if django_timezone else datetime.now(timezone.utc)),
            }

            # Persist only when DB is enabled and Django is available
            if self.db_enabled and Stock is not None and StockPrice is not None:
                try:
                    stock, created = Stock.objects.get_or_create(ticker=symbol, defaults={
                        'symbol': symbol,
                        'company_name': payload['company_name'],
                        'name': payload['name'],
                        'exchange': payload['exchange']
                    })
                    # Update only non-null and non-empty values
                    updatable_fields = [
                        'company_name','name','exchange','current_price','days_low','days_high','days_range',
                        'volume','volume_today','avg_volume_3mon','dvav','market_cap','shares_available',
                        'pe_ratio','dividend_yield','one_year_target','week_52_low','week_52_high',
                        'earnings_per_share','book_value','price_to_book','bid_price','ask_price',
                        'bid_ask_spread','price_change_today','price_change_week','price_change_month',
                        'price_change_year','change_percent','market_cap_change_3mon','pe_change_3mon'
                    ]
                    changed = False
                    for f in updatable_fields:
                        val = payload.get(f)
                        if val is None:
                            continue
                        if isinstance(val, str) and val == '':
                            continue
                        # Assign
                        setattr(stock, f, val)
                        changed = True
                    if changed:
                        stock.last_updated = payload['last_updated']
                        stock.save()
                    if payload.get('current_price') is not None:
                        try:
                            StockPrice.objects.create(stock=stock, price=payload['current_price'])
                        except Exception:
                            pass
                except Exception as e:
                    logger.error(f"DB write failed for {symbol}: {e}")

            # Light-weight analytics for second pass aggregation
            analytics = {
                'ticker': symbol,
                'dvav': dvav,
                'dollar_volume': (float(current_price) * float(volume)) if current_price and volume else None,
                'momentum_1m': None,
            }
            # momentum_1m skipped (requires month history)

            # Add non-persisted technicals for reference (not saved to DB)
            payload['_analytics'] = {
                'rsi14': rsi14,
                'atr14': atr14,
                'sma_5': sma_5,
                'sma_20': sma_20,
                'ema_5': ema_5,
                'ema_20': ema_20,
                'macd': macd_val,
                'macd_signal': macd_signal,
                'stochastic14': stoch14,
                'vwap': vwap,
                'gap_open_vs_prev_close': None,
                'gap_open_percent': None,
                'premarket_active': None,
                'postmarket_active': None,
                'earnings_bucket': None,
                'days_to_cover': None,
                'liquidity_score': None,
                'flags': {
                    'large_cap': None,
                    'high_dvav': None,
                    'rsi_overbought': None,
                    'rsi_oversold': None,
                },
                'dollar_volume': analytics['dollar_volume'],
                'momentum_1m': analytics['momentum_1m'],
            }

            # Gap detection skipped (requires daily history)

            try:
                market_state = fast.get('market_state') if fast else None
                payload['_analytics']['premarket_active'] = (market_state == 'PRE') if market_state is not None else None
                payload['_analytics']['postmarket_active'] = (market_state == 'POST') if market_state is not None else None
            except Exception:
                pass

            # Earnings proximity skipped (requires calendar/earnings endpoints)

            # Short interest days-to-cover proxy
            try:
                shares_short = info.get('sharesShort') if info else None
                adv = avg_volume_3mon
                if shares_short and adv and float(adv) != 0:
                    payload['_analytics']['days_to_cover'] = float(shares_short) / float(adv)
            except Exception:
                pass

            # Simple flags
            try:
                payload['_analytics']['flags']['large_cap'] = (market_cap is not None and float(market_cap) >= 10_000_000_000)
                payload['_analytics']['flags']['high_dvav'] = (dvav is not None and float(dvav) >= 2.0)
                payload['_analytics']['flags']['rsi_overbought'] = (rsi14 is not None and float(rsi14) >= 70.0)
                payload['_analytics']['flags']['rsi_oversold'] = (rsi14 is not None and float(rsi14) <= 30.0)
            except Exception:
                pass

            return symbol, payload, False

        except Exception as e:
            if is_rate_limit_error(e):
                return symbol, None, True
            logger.error(f"{symbol} error: {e}")
            return symbol, None, False

    def scan(self, symbols: List[str], csv_out: Optional[str] = None) -> Dict[str, Any]:
        start = time.time()
        successes: Dict[str, Dict[str, Any]] = {}
        rate_limited_syms: List[str] = []
        failed_symbols: List[str] = []
        failures = 0
        proxy_rotations = 0

        # Optional pre-filter: drop obviously invalid/delisted via direct quotes
        prefilter_syms: List[str] = []
        batch = 500
        prefilter_failed = False
        for i in range(0, len(symbols), batch):
            chunk = symbols[i:i+batch]
            qm = self._yahoo_client.fetch_quotes(chunk)
            # If Yahoo rejects crumbs broadly, skip prefiltering entirely
            if i == 0 and len(qm) == 0:
                prefilter_failed = True
                break
            for s in chunk:
                q = qm.get(s.upper())
                if q and (q.get('regularMarketPrice') is not None or q.get('regularMarketVolume') is not None or q.get('marketCap') is not None):
                    prefilter_syms.append(s)
        if not prefilter_failed and prefilter_syms:
            symbols = prefilter_syms

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self._fetch_symbol, s, i): s for i, s in enumerate(symbols)}
            for fut in as_completed(futures):
                s = futures[fut]
                try:
                    sym, payload, rl = fut.result(timeout=self.timeout + 2)
                except Exception as e:
                    if is_rate_limit_error(e):
                        rate_limited_syms.append(s)
                        # rotate proxy immediately
                        if self.use_proxies:
                            self.proxy_mgr.rotate_and_get_session()
                            proxy_rotations += 1
                        continue
                    failures += 1
                    failed_symbols.append(s)
                    continue
                if rl:
                    rate_limited_syms.append(sym)
                    if self.use_proxies:
                        self.proxy_mgr.rotate_and_get_session()
                        proxy_rotations += 1
                    continue
                if payload:
                    successes[sym] = payload
                else:
                    failures += 1
                    failed_symbols.append(s)

        # Retry rate-limited at end with proxy rotation and slight backoff
        retry_success = 0
        if rate_limited_syms:
            logger.info(f"Retrying {len(rate_limited_syms)} rate-limited tickers with rotated proxies...")
            time.sleep(1.0)
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {executor.submit(self._fetch_symbol, s, i): s for i, s in enumerate(rate_limited_syms)}
                for fut in as_completed(futures):
                    s = futures[fut]
                    try:
                        sym, payload, rl = fut.result(timeout=self.timeout + 2)
                    except Exception:
                        failed_symbols.append(s)
                        continue
                    if payload and not rl:
                        successes[sym] = payload
                        retry_success += 1
                    else:
                        failed_symbols.append(s)

        # Optional aggressive fill to improve completeness (disabled by default for speed)
        aggressive_fill = str(os.environ.get('SCANNER_AGGRESSIVE_FILL', '')).lower() in ('1', 'true', 'yes')
        if aggressive_fill:
            # Fallback pass A: fill missing price/volume/day high/low from batch daily download
            sym_list = list(successes.keys())
            need_pv = [s for s, p in successes.items() if (p.get('current_price') is None or p.get('volume') is None or p.get('volume') == 0)]
            if need_pv:
                logger.info(f"Batch-filling OHLCV for {len(need_pv)} tickers via download()...")
                batch_size = 200
                for i in range(0, len(need_pv), batch_size):
                    chunk = need_pv[i:i+batch_size]
                    data = self._batch_download_ohlcv(chunk, session=None)
                    for s in chunk:
                        p = successes.get(s)
                        if not p:
                            continue
                        d = data.get(s) or {}
                        cp = d.get('close')
                        vol = d.get('volume')
                        lo = d.get('low')
                        hi = d.get('high')
                        if p.get('current_price') is None and isinstance(cp, (int, float)) and math.isfinite(cp):
                            p['current_price'] = safe_decimal(cp)
                        if (p.get('volume') is None or p.get('volume') == 0) and isinstance(vol, (int, float)) and math.isfinite(vol):
                            try:
                                p['volume'] = int(vol)
                                p['volume_today'] = int(vol)
                            except Exception:
                                pass
                        if p.get('days_low') is None and isinstance(lo, (int, float)):
                            p['days_low'] = safe_decimal(lo)
                        if p.get('days_high') is None and isinstance(hi, (int, float)):
                            p['days_high'] = safe_decimal(hi)
                        if (p.get('days_low') is not None and p.get('days_high') is not None) and (p.get('days_range') in (None, '')):
                            try:
                                p['days_range'] = f"{float(p['days_low']):.2f} - {float(p['days_high']):.2f}"
                            except Exception:
                                pass

            # Use direct quotes to fill remaining fast fields without proxies
            remaining_for_quote = [s for s, p in successes.items() if (p.get('current_price') is None or p.get('volume') is None or p.get('market_cap') is None)]
            for i in range(0, len(remaining_for_quote), 500):
                chunk = remaining_for_quote[i:i+500]
                qm = self._yahoo_client.fetch_quotes(chunk)
                for s in chunk:
                    q = qm.get(s.upper())
                    if not q:
                        continue
                    p = successes.get(s)
                    if not p:
                        continue
                    if p.get('current_price') is None and q.get('regularMarketPrice') is not None:
                        p['current_price'] = safe_decimal(q.get('regularMarketPrice'))
                    if (p.get('volume') is None or p.get('volume') == 0) and q.get('regularMarketVolume') is not None:
                        try:
                            v = int(q.get('regularMarketVolume'))
                            p['volume'] = v
                            p['volume_today'] = v
                        except Exception:
                            pass
                    if p.get('market_cap') is None and q.get('marketCap') is not None:
                        try:
                            p['market_cap'] = int(q.get('marketCap'))
                        except Exception:
                            pass

        # Fallback pass B: derive market cap from shares if possible
        for s, p in successes.items():
            if p.get('market_cap') is None and p.get('current_price') is not None and p.get('shares_available') is not None:
                try:
                    p['market_cap'] = int(float(p['current_price']) * float(p['shares_available']))
                except Exception:
                    pass

        # Fallback pass C: if volume missing/zero, use 3-month avg volume as proxy
        for s, p in successes.items():
            vol = p.get('volume')
            if vol in (None, 0) and p.get('avg_volume_3mon') is not None:
                try:
                    p['volume'] = int(p['avg_volume_3mon'])
                    p['volume_today'] = int(p['avg_volume_3mon'])
                    # mark proxy in analytics
                    p.setdefault('_analytics', {}).setdefault('flags', {})['volume_is_average'] = True
                except Exception:
                    pass

        # Ensure completeness threshold via targeted info calls
        target_complete = math.ceil(self.completeness_threshold * len(symbols))
        complete_now = sum(1 for p in successes.values() if self._is_complete(p))
        if complete_now < target_complete:
            remaining = [s for s, p in successes.items() if not self._is_complete(p)]
            logger.info(f"Completeness {complete_now}/{len(symbols)} below target {target_complete}; fetching info for {len(remaining)}...")
            self._fill_market_cap_via_info(remaining, successes, target_complete)

        # Recompute dvav with updated volume/avg
        for s, p in successes.items():
            try:
                v = p.get('volume')
                av = p.get('avg_volume_3mon')
                if v is not None and av is not None and float(av) != 0:
                    p['dvav'] = safe_decimal(float(v) / float(av))
            except Exception:
                pass

        # Filter out fields that are missing (null) from final rows — don't emit empty strings
        for s, p in successes.items():
            # Clean empty strings
            for key, val in list(p.items()):
                if isinstance(val, str) and val.strip() == '':
                    p[key] = None

        # Keep only fully complete rows to maximize completeness of included dataset
        filtered_successes = {s: p for s, p in successes.items() if self._is_complete(p)}
        removed_incomplete = len(successes) - len(filtered_successes)
        successes = filtered_successes

        # Second pass: percentiles (dvav, momentum_1m, dollar_volume)
        # Collect values
        dvavs = [v.get('dvav') for v in successes.values() if isinstance(v.get('dvav'), (int, float, Decimal))]
        moms = [v.get('_analytics', {}).get('momentum_1m') for v in successes.values() if isinstance(v.get('_analytics', {}).get('momentum_1m'), (int, float))]
        dollars = [v.get('_analytics', {}).get('dollar_volume') for v in successes.values() if isinstance(v.get('_analytics', {}).get('dollar_volume'), (int, float))]
        def percentile(value: float, arr: List[float]) -> Optional[float]:
            if not arr:
                return None
            try:
                arr_sorted = sorted(arr)
                # rank percentile
                import bisect
                pos = bisect.bisect_left(arr_sorted, value)
                return round((pos / max(1, len(arr_sorted))) * 100.0, 2)
            except Exception:
                return None

        # Attach computed percentiles into payload (not stored to DB due to schema)
        dvav_arr = [float(x) for x in dvavs if x is not None]
        mom_arr = [float(x) for x in moms if x is not None]
        dollar_arr = [float(x) for x in dollars if x is not None]
        for sym, payload in successes.items():
            dv = payload.get('dvav')
            mom = payload.get('_analytics', {}).get('momentum_1m')
            p_dv = percentile(float(dv), dvav_arr) if isinstance(dv, (int, float, Decimal)) else None
            p_mo = percentile(float(mom), mom_arr) if isinstance(mom, (int, float)) else None
            payload.setdefault('_analytics', {})['dvav_percentile'] = p_dv
            payload['_analytics']['momentum_1m_percentile'] = p_mo
            dol = payload.get('_analytics', {}).get('dollar_volume')
            p_dol = percentile(float(dol), dollar_arr) if isinstance(dol, (int, float)) else None
            payload['_analytics']['dollar_volume_percentile'] = p_dol
            # Liquidity score (simple average of percentiles available)
            comps = [x for x in [p_dv, p_dol] if isinstance(x, (int, float))]
            payload['_analytics']['liquidity_score'] = round(sum(comps) / len(comps), 2) if comps else None

        # Optional CSV export
        if csv_out:
            try:
                # Flatten payloads for DataFrame
                rows: List[Dict[str, Any]] = []
                for sym, payload in successes.items():
                    row = {k: v for k, v in payload.items() if not k.startswith('_')}
                    # Merge analytics subset
                    analytics = payload.get('_analytics', {})
                    for k in ['rsi14','atr14','sma_5','sma_20','ema_5','ema_20','macd','macd_signal',
                              'stochastic14','vwap','gap_open_vs_prev_close','gap_open_percent',
                              'premarket_active','postmarket_active','earnings_bucket','days_to_cover',
                              'dollar_volume','momentum_1m','dvav_percentile','momentum_1m_percentile',
                              'dollar_volume_percentile','liquidity_score']:
                        row[f'analytics_{k}'] = analytics.get(k)
                    flags = analytics.get('flags', {}) if isinstance(analytics.get('flags'), dict) else {}
                    row['flag_large_cap'] = flags.get('large_cap')
                    row['flag_high_dvav'] = flags.get('high_dvav')
                    row['flag_rsi_overbought'] = flags.get('rsi_overbought')
                    row['flag_rsi_oversold'] = flags.get('rsi_oversold')
                    rows.append(row)
                df = pd.DataFrame(rows)
                # Convert Decimal values to floats per-cell without stringifying None
                for col in df.columns:
                    if df[col].map(lambda x: isinstance(x, Decimal)).any():
                        def _to_float_or_nan(v):
                            if isinstance(v, Decimal):
                                try:
                                    return float(v)
                                except Exception:
                                    return float('nan')
                            if v is None or (isinstance(v, str) and v.strip() == ''):
                                return float('nan')
                            return v
                        df[col] = df[col].map(_to_float_or_nan)
                        # Coerce residual non-numerics to NaN
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                df.to_csv(csv_out, index=False)
                logger.info(f"Saved CSV: {csv_out} with {len(df)} rows")
            except Exception as e:
                logger.error(f"CSV export failed: {e}")

        # Deep-dive stats (nulls, zeros)
        deep_dive = {}
        try:
            if csv_out and os.path.exists(csv_out):
                df = pd.read_csv(csv_out)
            else:
                # Build DataFrame from successes if no CSV written
                rows = []
                for sym, payload in successes.items():
                    r = {k: v for k, v in payload.items() if not k.startswith('_')}
                    rows.append(r)
                df = pd.DataFrame(rows)
            null_counts = df.isna().sum().to_dict()
            zero_counts = {}
            for col in df.columns:
                if df[col].dtype.kind in 'biufc':
                    zero_counts[col] = int((df[col] == 0).sum())
            deep_dive = {
                'null_counts': null_counts,
                'zero_counts': zero_counts,
            }
        except Exception as e:
            logger.error(f"Deep-dive analysis failed: {e}")

        duration = time.time() - start
        return {
            'total': len(symbols),
            'success': len(successes),
            'failed': (len(symbols) - len(successes)),
            'failed_symbols': failed_symbols,
            'retried_success': retry_success,
            'rate_limited_initial': len(set(rate_limited_syms)),
            'proxies_available': len(self.proxy_mgr.proxies) if self.use_proxies else 0,
            'proxy_rotations': proxy_rotations,
            'csv_out': csv_out,
            'deep_dive': deep_dive,
            'duration_sec': round(duration, 2),
            'rate_per_sec': round(len(symbols) / duration, 2) if duration > 0 else None,
        }


# ------------------------------- Entrypoint -------------------------------- #

def main():
    import argparse
    parser = argparse.ArgumentParser(description='High-speed stock scanner with proxies and retries')
    parser.add_argument('--threads', type=int, default=10, help='Number of threads (default: 10)')
    parser.add_argument('--timeout', type=int, default=8, help='Per-task timeout seconds (default: 8)')
    parser.add_argument('--proxy-file', type=str, default='working_proxies.json', help='Proxy JSON file (default: working_proxies.json)')
    parser.add_argument('--no-proxy', action='store_true', help='Disable proxy usage')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of tickers processed')
    parser.add_argument('--symbols', type=str, default=None, help='Comma-separated list of symbols to scan (overrides universe)')
    parser.add_argument('--csv-out', type=str, default=None, help='Save results to CSV file')
    args = parser.parse_args()

    # Load symbols
    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(',') if s.strip()]
    else:
        symbols = load_combined_tickers()
    if args.limit:
        symbols = symbols[: args.limit]

    logger.info(f"Symbols: {len(symbols)} | Threads: {args.threads} | Proxies: {'ON' if not args.no_proxy else 'OFF'}")
    scanner = StockScanner(
        threads=args.threads,
        timeout=args.timeout,
        proxy_file=args.proxy_file,
        use_proxies=(not args.no_proxy),
    )
    stats = scanner.scan(symbols, csv_out=args.csv_out)
    # Pretty print summary
    logger.info(f"Scan complete. Total={stats['total']} Success={stats['success']} Failed={stats['failed']} "
                f"Duration={stats['duration_sec']}s Proxies={stats['proxies_available']} Rotations={stats['proxy_rotations']}\n"
                f"CSV={stats.get('csv_out')}")
    # Print top-level deep dive signals
    dd = stats.get('deep_dive') or {}
    if dd:
        # Show top 10 null-heavy columns
        nulls = sorted(dd.get('null_counts', {}).items(), key=lambda x: x[1], reverse=True)[:10]
        zeros = sorted(dd.get('zero_counts', {}).items(), key=lambda x: x[1], reverse=True)[:10]
        logger.info(f"Null-heavy columns (top 10): {nulls}")
        logger.info(f"Zero-heavy columns (top 10): {zeros}")
    logger.info(json.dumps({k: v for k, v in stats.items() if k not in ('deep_dive','failed_symbols')}, indent=2))
    # Keep failed list manageable in logs
    if stats.get('failed_symbols'):
        sample_failed = stats['failed_symbols'][:50]
        logger.info(f"Failed tickers (sample {len(sample_failed)}/{len(stats['failed_symbols'])}): {sample_failed}")


if __name__ == '__main__':
    main()
