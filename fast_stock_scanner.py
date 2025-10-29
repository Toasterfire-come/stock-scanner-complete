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
try:
    # Prefer yfinance utils to access crumbless quote endpoint in batch
    from yfinance.utils import get_json as yf_get_json  # type: ignore
except Exception:
    yf_get_json = None  # type: ignore

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
        # Optional cap to limit active proxies (e.g., prioritize healthiest subset)
        proxy_limit_env = os.environ.get('SCANNER_PROXY_LIMIT')
        try:
            proxy_limit = int(proxy_limit_env) if proxy_limit_env else None
        except Exception:
            proxy_limit = None
        incoming = [p.strip() for p in proxies if p]
        if proxy_limit is not None and proxy_limit > 0:
            incoming = incoming[:proxy_limit]
        self.proxies = list(dict.fromkeys(incoming))
        self._index = 0
        self._lock = None
        try:
            import threading
            self._lock = threading.Lock()
        except Exception:
            self._lock = None
        # Build and warm persistent sessions per proxy (or one no-proxy session)
        self._sessions: List[object] = []
        # We DO NOT share cookies across proxies to avoid identity coupling across IPs
        master_cookies = None

        targets = self.proxies if self.proxies else [None]
        # Diverse User-Agents for each proxy session
        uas = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36'
        ]
        for i, proxy in enumerate(targets):
            try:
                if cf_requests is not None:
                    sess = cf_requests.Session()
                else:
                    sess = requests.Session()
                if proxy:
                    sess.proxies = {'http': proxy, 'https': proxy}
                sess.headers.update({
                    'User-Agent': uas[i % len(uas)],
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                })
                # Warm cookie jar once to reduce crumb-related 401s inside yfinance
                try:
                    sess.get('https://finance.yahoo.com', timeout=4)
                except Exception:
                    pass
                # Trigger yfinance to establish crumb/cookies within this session
                try:
                    _ = yf.Ticker('AAPL', session=sess).fast_info
                except Exception:
                    pass
                self._sessions.append(sess)
            except Exception:
                continue

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
        if not self._sessions:
            return None
        if rotate:
            self._next_index()
        # Ensure index in range
        idx = self._index % len(self._sessions)
        return self._sessions[idx]

    def rotate_and_get_session(self) -> Optional[requests.Session]:
        return self.get_session(rotate=True)


## Direct Yahoo quote client removed: we rely solely on yfinance interfaces.

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
    # Optionally include NYSE tickers from NASDAQ "otherlisted.txt" (Exchange 'N'), common shares only
    nyse: List[str] = []
    otherlisted_path = os.path.join(complete_dir, 'otherlisted.txt')
    if os.path.exists(otherlisted_path):
        try:
            with open(otherlisted_path, 'r', encoding='utf-8', errors='ignore') as f:
                header = f.readline()  # skip header
                for line in f:
                    parts = [p.strip() for p in line.strip().split('|')]
                    # Columns: ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot Size|Test Issue|NASDAQ Symbol
                    if len(parts) < 8:
                        continue
                    act_symbol, _, exchange, _, etf_flag, _, test_issue, _ = parts[:8]
                    # Only NYSE ('N'), non-ETF, non-test issues
                    if exchange != 'N' or etf_flag == 'Y' or test_issue == 'Y':
                        continue
                    # Filter out units/warrants/preferred series and exotic symbols
                    if any(x in act_symbol for x in ['.', '$', '=', '+', ' ']):
                        continue
                    bad_suffixes = ('W', 'WS', 'WTS', 'U', 'UN', 'RT', 'R')
                    if any(act_symbol.endswith(suf) for suf in bad_suffixes):
                        continue
                    if act_symbol:
                        nyse.append(act_symbol.upper())
        except Exception:
            nyse = []

    # De-dup while preserving order preference: NASDAQ-only first, then complete NASDAQ, then NYSE
    seen = set()
    combined: List[str] = []
    for s in nasdaq_only + complete:
        if s not in seen:
            seen.add(s)
            combined.append(s)
    for s in nyse:
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
        # Set to 0.0 to avoid fallback .info calls which can trigger crumb-protected endpoints
        self.completeness_threshold = 0.0
        # Base headers for sessions
        # No-proxy warmed session (used when proxies disabled)
        self._no_proxy_session = None
        # Auto-denylist support (skip delisted/invalid tickers on future runs)
        self._auto_denylist_path = os.environ.get('SCANNER_DENYLIST_FILE') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'denylist_auto.json')
        self._auto_denylist: set[str] = set()
        self._delisted_found: set[str] = set()
        try:
            if os.path.exists(self._auto_denylist_path):
                with open(self._auto_denylist_path, 'r', encoding='utf-8', errors='ignore') as f:
                    dj = json.load(f)
                    if isinstance(dj, list):
                        self._auto_denylist.update([str(x).strip().upper() for x in dj if str(x).strip()])
                    elif isinstance(dj, dict) and 'tickers' in dj and isinstance(dj['tickers'], list):
                        self._auto_denylist.update([str(x).strip().upper() for x in dj['tickers'] if str(x).strip()])
        except Exception:
            self._auto_denylist = set()
        try:
            if cf_requests is not None:
                s = cf_requests.Session()
            else:
                s = requests.Session()
            s.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
            })
            try:
                s.get('https://finance.yahoo.com', timeout=4)
            except Exception:
                pass
            self._no_proxy_session = s
        except Exception:
            self._no_proxy_session = None

    # ------------------------- Batch quote (v7) pipeline ------------------------- #
    def _map_quote_to_payload(self, q: Dict[str, Any], symbol_hint: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Map Yahoo v7 quote JSON to our Stock payload shape (fast, yfinance-only)."""
        if not isinstance(q, dict):
            return None
        try:
            symbol = str(q.get('symbol') or symbol_hint or '').strip().upper()
            if not symbol:
                return None
            # Filter non-equities if quoteType present
            qtype = str(q.get('quoteType') or '').upper()
            if qtype and qtype not in ('EQUITY', 'COMMONSTOCK', 'COMMON_STOCK'):
                return None

            # Core numerics
            def _get_num(keys: List[str]) -> Optional[float]:
                for k in keys:
                    v = q.get(k)
                    if v is not None:
                        try:
                            f = float(v)
                            if math.isfinite(f):
                                return f
                        except Exception:
                            continue
                return None

            current_price = _get_num(['regularMarketPrice', 'postMarketPrice', 'preMarketPrice'])
            prev_close = _get_num(['regularMarketPreviousClose', 'previousClose'])
            price_change_today = None
            change_percent = None
            if current_price is not None and prev_close not in (None, 0):
                try:
                    price_change_today = current_price - float(prev_close)
                    change_percent = (price_change_today / float(prev_close)) * 100.0
                except Exception:
                    price_change_today = None
                    change_percent = None

            days_low = _get_num(['regularMarketDayLow'])
            days_high = _get_num(['regularMarketDayHigh'])
            days_range = None
            if days_low is not None and days_high is not None:
                try:
                    days_range = f"{days_low:.2f} - {days_high:.2f}"
                except Exception:
                    days_range = None

            volume = _get_num(['regularMarketVolume'])
            avg_volume_3mon = _get_num(['threeMonthAverageVolume']) or _get_num(['tenDayAverageVolume'])
            dvav = None
            if volume is not None and avg_volume_3mon not in (None, 0):
                try:
                    dvav = float(volume) / float(avg_volume_3mon)
                except Exception:
                    dvav = None

            market_cap = _get_num(['marketCap'])
            shares_available = _get_num(['sharesOutstanding', 'shares'])
            if market_cap is None and current_price is not None and shares_available is not None:
                try:
                    market_cap = float(current_price) * float(shares_available)
                except Exception:
                    pass

            wk_low = _get_num(['fiftyTwoWeekLow', 'yearLow'])
            wk_high = _get_num(['fiftyTwoWeekHigh', 'yearHigh'])
            eps = _get_num(['epsTrailingTwelveMonths', 'trailingEps'])
            pe_ratio = _get_num(['trailingPE'])
            if pe_ratio is None and current_price is not None and eps not in (None, 0):
                try:
                    pe_ratio = float(current_price) / float(eps)
                except Exception:
                    pe_ratio = None

            book_value = _get_num(['bookValue'])
            price_to_book = _get_num(['priceToBook'])
            if price_to_book is None and current_price is not None and book_value not in (None, 0):
                try:
                    price_to_book = float(current_price) / float(book_value)
                except Exception:
                    price_to_book = None

            bid_price = _get_num(['bid'])
            ask_price = _get_num(['ask'])
            bid_ask_spread = None
            if bid_price is not None and ask_price is not None:
                try:
                    bid_ask_spread = f"{bid_price:.2f} - {ask_price:.2f}"
                except Exception:
                    bid_ask_spread = None

            # Dividend yield handling (ensure percentage)
            dividend_yield = _get_num(['trailingAnnualDividendYield', 'dividendYield'])
            if dividend_yield is not None and dividend_yield < 1.0:
                dividend_yield = dividend_yield * 100.0

            one_year_target = _get_num(['targetMeanPrice'])

            company_name = q.get('longName') or q.get('shortName') or symbol
            exchange = q.get('fullExchangeName') or q.get('exchange') or 'NASDAQ'

            payload: Dict[str, Any] = {
                'ticker': symbol,
                'symbol': symbol,
                'company_name': company_name,
                'name': company_name,
                'exchange': exchange,
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
                'price_change_week': None,
                'price_change_month': None,
                'price_change_year': None,
                'change_percent': safe_decimal(change_percent),
                'market_cap_change_3mon': None,
                'pe_change_3mon': None,
                'last_updated': (django_timezone.now() if django_timezone else datetime.now(timezone.utc)),
                'created_at': (django_timezone.now() if django_timezone else datetime.now(timezone.utc)),
            }
            # Analytics (minimal, keep shape compatible)
            payload['_analytics'] = {
                'rsi14': None,
                'atr14': None,
                'sma_5': None,
                'sma_20': None,
                'ema_5': None,
                'ema_20': None,
                'macd': None,
                'macd_signal': None,
                'stochastic14': None,
                'vwap': None,
                'gap_open_vs_prev_close': None,
                'gap_open_percent': None,
                'premarket_active': None,
                'postmarket_active': None,
                'earnings_bucket': None,
                'days_to_cover': None,
                'liquidity_score': None,
                'flags': {
                    'large_cap': (market_cap is not None and float(market_cap) >= 10_000_000_000),
                    'high_dvav': (dvav is not None and float(dvav) >= 2.0) if dvav is not None else None,
                    'rsi_overbought': None,
                    'rsi_oversold': None,
                },
                'dollar_volume': (float(current_price) * float(volume)) if (current_price is not None and volume is not None) else None,
                'momentum_1m': None,
            }
            return payload
        except Exception:
            return None

    def _batch_quote(self, symbols: List[str], session: Optional[object]) -> Dict[str, Dict[str, Any]]:
        """Fetch quote data for many tickers at once via yfinance's crumbless quote endpoint.
        Returns mapping: sym -> payload
        """
        out: Dict[str, Dict[str, Any]] = {}
        if not symbols:
            return out
        # Build symbols param (Yahoo limit is generous, but we cap to ~250 per call upstream)
        try:
            url = 'https://query2.finance.yahoo.com/v7/finance/quote'
            data = None
            # Determine proxy URL from provided session if possible
            proxy_url = None
            try:
                if session is not None and getattr(session, 'proxies', None):
                    px = getattr(session, 'proxies', {}) or {}
                    proxy_url = px.get('https') or px.get('http')
            except Exception:
                proxy_url = None

            params = {'symbols': ','.join(symbols)}

            if yf_get_json is not None:
                # Try with session argument first; if unsupported, retry with proxy only
                try:
                    data = yf_get_json(url, params=params, session=session)  # type: ignore[arg-type]
                except TypeError:
                    try:
                        if proxy_url:
                            data = yf_get_json(url, params=params, proxy=proxy_url)  # type: ignore[arg-type]
                    except Exception:
                        data = None
                except Exception:
                    data = None

            # If utils not available or failed, attempt through yf.utils.get_json
            if data is None:
                try:
                    utils = getattr(yf, 'utils', None)
                    gj = getattr(utils, 'get_json', None) if utils is not None else None
                    if callable(gj):
                        try:
                            data = gj(url, params=params, session=session)
                        except TypeError:
                            if proxy_url:
                                data = gj(url, params=params, proxy=proxy_url)
                        except Exception:
                            data = None
                except Exception:
                    data = None
            if not isinstance(data, dict):
                return out
            results = []
            try:
                results = data.get('quoteResponse', {}).get('result', []) or []
            except Exception:
                results = data.get('result', []) or []
            for q in results:
                payload = self._map_quote_to_payload(q)
                if payload and payload.get('symbol'):
                    out[payload['symbol']] = payload
        except Exception as e:
            logger.error(f"Quote batch failed for {len(symbols)} tickers: {e}")
        return out

    # ------------------------- Batch download pipeline ------------------------- #
    def _download_chunk(self, symbols: List[str], session: Optional[object], timeout: int,
                        period: str = '5d', interval: str = '1d', actions: bool = True) -> Optional[pd.DataFrame]:
        try:
            df = yf.download(
                tickers=symbols,
                period=period,
                interval=interval,
                group_by='ticker',
                auto_adjust=False,
                progress=False,
                threads=False,
                session=session,
                actions=actions,
                repair=False,
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
                    # Access subframe for ticker reliably
                    if s not in df.columns.get_level_values(0):
                        continue
                    sub = df[s]
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
                # Only include fields we can guarantee quickly; omit null-heavy metrics entirely
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
                    'change_percent': safe_decimal(change_percent),
                    'last_updated': (django_timezone.now() if django_timezone else datetime.now(timezone.utc)),
                    'created_at': (django_timezone.now() if django_timezone else datetime.now(timezone.utc)),
                }
            except Exception:
                continue
        return rows

    def scan_batch(self, symbols: List[str], csv_out: Optional[str] = None, chunk_size: int = 100) -> Dict[str, Any]:
        start = time.time()
        # Normalize symbols
        symbols = [s.strip().upper() for s in symbols if s and s.strip()]
        # Auto-filter non-standard tickers (basic heuristics)
        def is_standard(sym: str) -> bool:
            if not sym or any(c in sym for c in ['^', '=', ' ', '/', '\\', '*', '&']):
                return False
            if sym.startswith('$'):
                return False
            # Exclude common warrant/unit/right suffixes
            bad_suffixes = ('W', 'WS', 'WTS', 'U', 'UN', 'R', 'RT')
            for suf in bad_suffixes:
                if sym.endswith(suf):
                    return False
            return True
        symbols = [s for s in symbols if is_standard(s)]

        # Split into chunks
        # Allow env override of chunk size
        try:
            env_chunk = int(os.environ.get('SCANNER_BATCH_CHUNK', str(chunk_size)))
            chunk_size = max(1, env_chunk)
        except Exception:
            pass
        chunks: List[List[str]] = [symbols[i:i+chunk_size] for i in range(0, len(symbols), chunk_size)]
        results: Dict[str, Dict[str, Any]] = {}
        rate_limited_chunks = 0
        proxy_rotations = 0
        # Global throttle knobs
        try:
            min_interval = float(os.environ.get('SCANNER_MIN_INTERVAL', '0'))
        except Exception:
            min_interval = 0.0

        def process_chunk(chunk: List[str]) -> Tuple[List[str], Dict[str, Dict[str, Any]]]:
            # Try with (proxy or none) sessions, rotate on rate limit
            max_attempts = 4
            attempt = 0
            session = None
            # Seed a session up-front to reduce crumb/auth misses
            if self.use_proxies and self.proxy_mgr.proxies:
                # Attempt to give each worker a unique session via rotation at start
                session = self.proxy_mgr.rotate_and_get_session()
                # Track rotation used to obtain this session
                nonlocal proxy_rotations
                proxy_rotations += 1
            else:
                session = self._no_proxy_session
            while attempt < max_attempts:
                if min_interval > 0:
                    time.sleep(min_interval)
                # 5d prices for last-day fields (fast path)
                df_5d = self._download_chunk(chunk, session=session, timeout=self.timeout, period='5d', interval='1d', actions=False)
                rows = self._build_rows_from_download(df_5d, chunk)
                # If we got some rows, accept; else rotate proxy and retry smaller chunk_size
                if rows:
                    return chunk, rows
                attempt += 1
                # rotate proxy
                if self.use_proxies and self.proxy_mgr.proxies:
                    session = self.proxy_mgr.rotate_and_get_session()
                    proxy_rotations += 1
                else:
                    session = self._no_proxy_session
                # brief backoff
                time.sleep(min(0.5 + random.random(), 2.0))
            return chunk, {}

        # Cap concurrency by env and available proxies (to avoid sharing same proxy across threads)
        max_workers_env = os.environ.get('SCANNER_MAX_NET_WORKERS')
        try:
            max_workers_cap = int(max_workers_env) if max_workers_env else self.threads
        except Exception:
            max_workers_cap = self.threads
        if self.use_proxies and self.proxy_mgr.proxies:
            max_workers_cap = min(max_workers_cap, self.threads, len(self.proxy_mgr.proxies))
        else:
            max_workers_cap = min(max_workers_cap, self.threads)

        # Run chunks concurrently with capped workers
        with ThreadPoolExecutor(max_workers=max_workers_cap) as ex:
            futures = [ex.submit(process_chunk, ch) for ch in chunks]
            for fut in as_completed(futures):
                ch, rows = fut.result()
                if not rows:
                    rate_limited_chunks += 1
                results.update(rows)

        # Keep only complete rows (price & volume present)
        complete = {s: p for s, p in results.items() if p.get('current_price') is not None and p.get('volume') is not None}

        # Fast-info enrichment (yfinance-only; no crumb) with selective retries and session reuse
        def enrich_chunk_fastinfo(chunk_syms: List[str]) -> Tuple[Dict[str, Dict[str, Any]], List[str]]:
            updates: Dict[str, Dict[str, Any]] = {}
            drop_non_equity: List[str] = []
            # Reuse one session per chunk
            sess = None
            if self.use_proxies and self.proxy_mgr.proxies:
                sess = self.proxy_mgr.get_session(rotate=False)
            for sym in chunk_syms:
                attempts = 0
                while attempts < 2:
                    try:
                        t = yf.Ticker(sym, session=sess)
                        fi = t.fast_info
                        if not fi:
                            raise RuntimeError('no fast_info')
                        # Filter non-equities when quoteType present
                        qtype = None
                        try:
                            qtype = fi.get('quoteType')
                        except Exception:
                            qtype = None
                        if qtype and str(qtype).upper() not in ('EQUITY', 'COMMONSTOCK', 'COMMON_STOCK'):
                            drop_non_equity.append(sym)
                            break
                        def getf(k: str) -> Optional[float]:
                            try:
                                v = fi.get(k)
                                return float(v) if v is not None else None
                            except Exception:
                                return None
                        upd: Dict[str, Any] = {}
                        mc = getf('marketCap')
                        if mc is not None:
                            upd['market_cap'] = int(mc)
                        sh = getf('shares')
                        if sh is not None:
                            upd['shares_available'] = int(sh)
                        avg3 = getf('threeMonthAverageVolume')
                        if avg3 is not None and math.isfinite(avg3):
                            upd['avg_volume_3mon'] = int(avg3)
                        yl = getf('yearLow')
                        yh = getf('yearHigh')
                        if yl is not None:
                            upd['week_52_low'] = safe_decimal(yl)
                        if yh is not None:
                            upd['week_52_high'] = safe_decimal(yh)
                        pe = getf('trailingPE')
                        if pe is not None and math.isfinite(pe):
                            upd['pe_ratio'] = safe_decimal(pe)
                        eps = getf('trailingEps')
                        if eps is not None and math.isfinite(eps):
                            upd['earnings_per_share'] = safe_decimal(eps)
                        updates[sym] = upd
                        break
                    except Exception as e:
                        attempts += 1
                        # Rotate session on second attempt for this symbol
                        if attempts >= 2 and self.use_proxies and self.proxy_mgr.proxies:
                            sess = self.proxy_mgr.rotate_and_get_session()
            return updates, drop_non_equity

        if complete and str(os.environ.get('SCANNER_ENRICH_FASTINFO', '')).lower() in ('1', 'true', 'yes'):
            enrich_syms = list(complete.keys())
            # Process fast_info in chunks with parallelism, session reuse within each chunk
            fi_chunk_size = 300
            fi_chunks = [enrich_syms[i:i+fi_chunk_size] for i in range(0, len(enrich_syms), fi_chunk_size)]
            all_updates: Dict[str, Dict[str, Any]] = {}
            to_drop: List[str] = []
            with ThreadPoolExecutor(max_workers=min(self.threads, len(fi_chunks) or 1)) as ex:
                futures = [ex.submit(enrich_chunk_fastinfo, ch) for ch in fi_chunks]
                for fut in as_completed(futures):
                    upd, drop_list = fut.result()
                    all_updates.update(upd)
                    to_drop.extend(drop_list)
            for sym, upd in all_updates.items():
                if sym in complete and upd:
                    complete[sym].update({k: v for k, v in upd.items() if v is not None})
            # Drop non-equities
            for sym in set(to_drop):
                complete.pop(sym, None)
            # Compute dvav where possible
            for sym, p in complete.items():
                try:
                    v = p.get('volume')
                    av = p.get('avg_volume_3mon')
                    if v is not None and av is not None and float(av) != 0:
                        p['dvav'] = safe_decimal(float(v)/float(av))
                except Exception:
                    pass

        # Dividend yield via 1y actions (yfinance-only), limited pass to control runtime
        need_div = [s for s, p in complete.items() if p.get('dividend_yield') is None]
        # Widened subset (up to ~4000 symbols), parallelized downloads
        max_div_symbols = min(len(need_div), 4000)
        div_chunk_size = 400
        div_chunks = [need_div[i:i+div_chunk_size] for i in range(0, max_div_symbols, div_chunk_size)]
        def fetch_div_chunk(chunk_syms: List[str]) -> Tuple[List[str], Optional[pd.DataFrame]]:
            df_div = self._download_chunk(chunk_syms, session=None, timeout=self.timeout, period='1y', interval='1d', actions=True)
            return chunk_syms, df_div
        if div_chunks:
            with ThreadPoolExecutor(max_workers=min(6, len(div_chunks))) as ex:
                for ch_syms, df_div in ex.map(fetch_div_chunk, div_chunks):
                    if not isinstance(df_div, pd.DataFrame) or df_div.empty:
                        continue
                    multi = isinstance(df_div.columns, pd.MultiIndex)
                    for s in ch_syms:
                        try:
                            sub = df_div[s] if multi and s in df_div.columns.get_level_values(0) else df_div
                            if sub is None or sub.empty or 'Dividends' not in sub.columns:
                                continue
                            div_sum = pd.to_numeric(sub['Dividends'], errors='coerce').fillna(0.0).sum()
                            cp = complete[s].get('current_price')
                            if cp is not None and float(cp) != 0:
                                dy = (float(div_sum)/float(cp)) * 100.0
                                complete[s]['dividend_yield'] = safe_decimal(dy)
                        except Exception:
                            continue

        # CSV export
        if csv_out:
            try:
                df = pd.DataFrame([{k: v for k, v in p.items() if not str(k).startswith('_')} for p in complete.values()])
                # Drop columns that are entirely null to avoid null-heavy fields
                df.dropna(axis=1, how='all', inplace=True)
                for col in df.columns:
                    if df[col].map(lambda x: isinstance(x, Decimal)).any():
                        df[col] = df[col].map(lambda v: float(v) if isinstance(v, Decimal) else (float('nan') if v is None else v))
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                df.to_csv(csv_out, index=False)
                logger.info(f"Saved CSV: {csv_out} with {len(df)} rows")
            except Exception as e:
                logger.error(f"CSV export failed: {e}")

        # Deep-dive stats (nulls, zeros)
        deep_dive = {}
        try:
            if csv_out and os.path.exists(csv_out):
                df_dd = pd.read_csv(csv_out)
            else:
                df_dd = pd.DataFrame([{k: v for k, v in p.items() if not str(k).startswith('_')} for p in complete.values()])
            null_counts = df_dd.isna().sum().to_dict()
            zero_counts = {}
            for col in df_dd.columns:
                if df_dd[col].dtype.kind in 'biufc':
                    zero_counts[col] = int((df_dd[col] == 0).sum())
            deep_dive = {
                'null_counts': null_counts,
                'zero_counts': zero_counts,
            }
        except Exception as e:
            logger.error(f"Deep-dive analysis failed: {e}")

        duration = time.time() - start
        completeness_ratio = round(len(complete) / max(1, len(symbols)), 3)
        return {
            'total': len(symbols),
            'success': len(complete),
            'failed': (len(symbols) - len(complete)),
            'failed_symbols': [s for s in symbols if s not in complete],
            'proxies_available': len(self.proxy_mgr.proxies) if self.use_proxies else 0,
            'rate_limited_chunks': rate_limited_chunks,
            'proxy_rotations': proxy_rotations,
            'csv_out': csv_out,
            'duration_sec': round(duration, 2),
            'rate_per_sec': round(len(symbols) / duration, 2) if duration > 0 else None,
            'completeness_ratio': completeness_ratio,
            'deep_dive': deep_dive,
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
                session=(self.proxy_mgr.get_session(rotate=False) if (self.use_proxies and self.proxy_mgr.proxies) else self._no_proxy_session),
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
            # Helper: build a fresh session with same proxy (refresh crumb/cookies without rotating proxy pool)
            def _fresh_session_like(sess: Optional[object]) -> Optional[object]:
                try:
                    new_sess = cf_requests.Session() if cf_requests is not None else requests.Session()
                    # copy proxies if present
                    try:
                        if sess is not None and getattr(sess, 'proxies', None):
                            new_sess.proxies = dict(getattr(sess, 'proxies'))
                    except Exception:
                        pass
                    uas = [
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
                    ]
                    new_sess.headers.update({
                        'User-Agent': random.choice(uas),
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Connection': 'keep-alive',
                    })
                    try:
                        new_sess.get('https://finance.yahoo.com', timeout=4)
                    except Exception:
                        pass
                    try:
                        _ = yf.Ticker('AAPL', session=new_sess).fast_info
                    except Exception:
                        pass
                    return new_sess
                except Exception:
                    return None

            def _is_crumb_error(exc: Exception) -> bool:
                t = str(exc).lower()
                return ('invalid crumb' in t) or ('unauthorized' in t)

            ticker = yf.Ticker(symbol, session=session)

            # Fast path: rely on fast_info first
            fast = None
            try:
                fast = ticker.fast_info
            except Exception as e:
                if _is_crumb_error(e):
                    # Refresh crumb/cookies with same proxy and retry once
                    session = _fresh_session_like(session) or session
                    try:
                        fast = yf.Ticker(symbol, session=session).fast_info
                    except Exception as e2:
                        if is_rate_limit_error(e2):
                            return symbol, None, True
                        return symbol, None, False
                elif is_rate_limit_error(e):
                    # rotate proxy and retry once
                    if self.use_proxies:
                        session = self.proxy_mgr.rotate_and_get_session()
                    try:
                        fast = yf.Ticker(symbol, session=session).fast_info
                    except Exception:
                        return symbol, None, True

            # Skip heavy endpoints (history/info/calendar/earnings) to meet <200ms budget
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
            # Derive from price × shares outstanding when missing; may fill from .info later
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
            book_value = None

            pe_ratio = None

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

            # If key fields missing, try .info to enrich before building payload
            need_info = (
                current_price is None or
                volume is None or
                market_cap is None or
                shares_outstanding is None or
                eps is None or
                pe_ratio is None or
                book_value is None or
                change_percent is None
            )
            if need_info:
                try:
                    info = ticker.info
                except Exception as e:
                    if _is_crumb_error(e):
                        session = _fresh_session_like(session) or session
                        try:
                            info = yf.Ticker(symbol, session=session).info
                        except Exception:
                            info = None
                    else:
                        info = None
                if isinstance(info, dict) and info:
                    def iget_num(keys: List[str]) -> Optional[float]:
                        for k in keys:
                            v = info.get(k)
                            if v is not None:
                                try:
                                    f = float(v)
                                    if math.isfinite(f):
                                        return f
                                except Exception:
                                    continue
                        return None
                    if current_price is None:
                        current_price = iget_num(['regularMarketPrice','postMarketPrice','preMarketPrice','open'])
                    if volume is None:
                        v = iget_num(['regularMarketVolume'])
                        volume = int(v) if v is not None else None
                    if market_cap is None:
                        mc = iget_num(['marketCap'])
                        market_cap = mc if mc is not None else market_cap
                    if shares_outstanding is None:
                        so = iget_num(['sharesOutstanding','shares'])
                        shares_outstanding = so
                    if eps is None:
                        eps = iget_num(['epsTrailingTwelveMonths','trailingEps'])
                    if pe_ratio is None:
                        pe_ratio = iget_num(['trailingPE'])
                    if book_value is None:
                        book_value = iget_num(['bookValue'])
                    if change_percent is None and current_price is not None:
                        pc = iget_num(['regularMarketPreviousClose','previousClose'])
                        if pc is not None and pc != 0:
                            try:
                                price_change_today = float(current_price) - float(pc)
                                change_percent = (price_change_today / float(pc)) * 100.0
                            except Exception:
                                pass

            # As last resort, if price/volume still missing, try per-symbol history
            if (current_price is None or volume is None):
                try:
                    h = ticker.history(period="5d", interval="1d", prepost=False)
                    if h is not None and not h.empty:
                        last = h.iloc[-1]
                        if current_price is None and pd.notna(last.get('Close')):
                            current_price = float(last.get('Close'))
                        if volume is None and pd.notna(last.get('Volume')):
                            volume = int(last.get('Volume'))
                        # Try to compute change from previousClose if available in history
                        if change_percent is None and current_price is not None and len(h) >= 2:
                            try:
                                prev = float(h.iloc[-2].get('Close'))
                                if prev != 0:
                                    price_change_today = float(current_price) - prev
                                    change_percent = (price_change_today / prev) * 100.0
                            except Exception:
                                pass
                except Exception:
                    pass

            # If still no core fields, mark as delisted/invalid for future runs
            if current_price is None and volume is None and (fast is None or not isinstance(fast, dict)):
                try:
                    self._delisted_found.add(symbol)
                except Exception:
                    pass
                return symbol, None, False

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
                'shares_available': int(shares_available) if shares_available is not None else (int(shares_outstanding) if shares_outstanding is not None else None),
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
        failed_symbols: List[str] = []
        rate_limited_failures: List[str] = []
        proxy_rotations = 0
        rate_limited_chunks = 0

        # Per-symbol mode: use fast_info and .info, download only as last resort
        symbols = [s.strip().upper() for s in symbols if s and s.strip()]
        # Apply auto denylist
        if self._auto_denylist:
            before = len(symbols)
            symbols = [s for s in symbols if s not in self._auto_denylist]
            after = len(symbols)
            if before != after:
                logger.info(f"Skipped {before-after} symbols from auto denylist")

        # Concurrency cap by env and proxies
        max_workers_env = os.environ.get('SCANNER_MAX_NET_WORKERS')
        try:
            max_workers_cap = int(max_workers_env) if max_workers_env else self.threads
        except Exception:
            max_workers_cap = self.threads
        if self.use_proxies and self.proxy_mgr.proxies:
            max_workers_cap = min(max_workers_cap, self.threads, len(self.proxy_mgr.proxies))
        else:
            max_workers_cap = min(max_workers_cap, self.threads)

        # Global throttle between task dispatches
        try:
            min_interval = float(os.environ.get('SCANNER_MIN_INTERVAL', '0'))
        except Exception:
            min_interval = 0.0

        def work(sym_idx: Tuple[int, str]) -> Tuple[str, Optional[Dict[str, Any]], bool]:
            i, s = sym_idx
            if min_interval > 0:
                time.sleep(min_interval)
            return self._fetch_symbol(s, i)

        indices = list(enumerate(symbols))
        with ThreadPoolExecutor(max_workers=max_workers_cap) as ex:
            futures = [ex.submit(work, pair) for pair in indices]
            for fut in as_completed(futures):
                sym, payload, rate_limited = fut.result()
                if payload is not None:
                    successes[sym] = payload
                else:
                    failed_symbols.append(sym)
                    if rate_limited:
                        rate_limited_failures.append(sym)
                if rate_limited:
                    rate_limited_chunks += 1

        # Retry wave for rate-limited symbols using per-symbol path with rotation
        retry_success = 0
        if rate_limited_failures:
            def retry_work(sym: str) -> Tuple[str, Optional[Dict[str, Any]], bool]:
                # brief jitter
                time.sleep(0.2 + random.random()*0.3)
                return self._fetch_symbol(sym, 0)
            with ThreadPoolExecutor(max_workers=max_workers_cap) as ex:
                futures = [ex.submit(retry_work, s) for s in rate_limited_failures]
                new_failed: List[str] = []
                for fut in as_completed(futures):
                    sym, payload, rate_limited = fut.result()
                    if payload is not None:
                        before = len(successes)
                        successes[sym] = payload
                        retry_success += (len(successes) - before)
                    else:
                        new_failed.append(sym)
                        if rate_limited:
                            rate_limited_chunks += 1
                # Merge remaining failures back
                failed_symbols = [s for s in failed_symbols if s not in rate_limited_failures] + new_failed

        # Optional batch fill disabled by default; per request recommends only last-resort download
        # If still missing essentials, perform limited per-symbol history salvage (already in _fetch_symbol)

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

        # Ensure completeness threshold via targeted info calls (disabled by default)
        target_complete = math.ceil(self.completeness_threshold * len(symbols))
        complete_now = sum(1 for p in successes.values() if self._is_complete(p))
        if complete_now < target_complete and target_complete > 0:
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

        # Persist to DB (mirror prior behavior) - update_or_create and add price point
        if self.db_enabled and Stock is not None and StockPrice is not None:
            try:
                for symbol, payload in successes.items():
                    try:
                        stock, created = Stock.objects.get_or_create(ticker=symbol, defaults={
                            'symbol': symbol,
                            'company_name': payload.get('company_name') or symbol,
                            'name': payload.get('name') or symbol,
                            'exchange': payload.get('exchange') or 'NASDAQ',
                        })
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
                            setattr(stock, f, val)
                            changed = True
                        if changed:
                            stock.last_updated = payload.get('last_updated') or (django_timezone.now() if django_timezone else datetime.now(timezone.utc))
                            stock.save()
                        if payload.get('current_price') is not None:
                            try:
                                StockPrice.objects.create(stock=stock, price=payload['current_price'])
                            except Exception:
                                pass
                    except Exception as e:
                        logger.error(f"DB write failed for {symbol}: {e}")
            except Exception as e:
                logger.error(f"DB bulk write error: {e}")

        duration = time.time() - start
        # Persist updated auto denylist (merge newly detected delisted symbols)
        try:
            if self._delisted_found:
                merged = sorted(set(self._auto_denylist).union({s for s in self._delisted_found}))
                os.makedirs(os.path.dirname(self._auto_denylist_path), exist_ok=True)
                with open(self._auto_denylist_path, 'w', encoding='utf-8') as f:
                    json.dump({'tickers': merged, 'count': len(merged)}, f, indent=2)
        except Exception:
            pass
        return {
            'total': len(symbols),
            'success': len(successes),
            'failed': (len(symbols) - len(successes)),
            'failed_symbols': failed_symbols,
            'retried_success': retry_success,
            'rate_limited_chunks': rate_limited_chunks,
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
    # Per request: stop batching; use per-symbol fast_info/.info; download only as last resort
    stats = scanner.scan(symbols, csv_out=args.csv_out)
    # Pretty print summary (robust when fields are missing)
    logger.info(
        f"Scan complete. Total={stats.get('total')} Success={stats.get('success')} Failed={stats.get('failed')} "
        f"Duration={stats.get('duration_sec')}s Proxies={stats.get('proxies_available')} "
        f"Rotations={stats.get('proxy_rotations', 0)}\nCSV={stats.get('csv_out')}"
    )
    # Print top-level deep dive signals
    dd = stats.get('deep_dive') or {}
    if dd:
        # Focus metrics: key nulls/zeros
        null_counts = dd.get('null_counts', {})
        zero_counts = dd.get('zero_counts', {})
        chg_null = int(null_counts.get('change_percent', 0) or 0)
        vol_zero = int(zero_counts.get('volume', 0) or 0)
        volt_zero = int(zero_counts.get('volume_today', 0) or 0)
        chg_zero = int(zero_counts.get('change_percent', 0) or 0)
        div_zero = int(zero_counts.get('dividend_yield', 0) or 0)
        logger.info(
            f"Nulls: change_percent has {chg_null} null; core price/volume fields non-null for successes."
        )
        logger.info(
            f"Zeros: volume={vol_zero}, volume_today={volt_zero}, change_percent={chg_zero}, dividend_yield={div_zero}"
        )
        # Also show top 10 for additional context
        nulls = sorted(null_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        zeros = sorted(zero_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        logger.info(f"Null-heavy columns (top 10): {nulls}")
        logger.info(f"Zero-heavy columns (top 10): {zeros}")
    logger.info(json.dumps({k: v for k, v in stats.items() if k not in ('deep_dive','failed_symbols')}, indent=2))
    # Keep failed list manageable in logs
    if stats.get('failed_symbols'):
        sample_failed = stats['failed_symbols'][:50]
        logger.info(f"Failed tickers (sample {len(sample_failed)}/{len(stats['failed_symbols'])}): {sample_failed}")


if __name__ == '__main__':
    main()
