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
from datetime import datetime, timedelta
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
        'yahoo finance is down', 'yahoo finance may be down'
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
                    return symbol, None, True

            # Skip heavy endpoints (history/info/calendar/earnings) to meet <200ms budget
            hist = None
            info = None

            # Current price
            current_price = None
            if fast is not None:
                for key in ('last_price', 'regular_market_price'):
                    if key in fast and fast[key] is not None:
                        current_price = fast.get(key)
                        break
            # Day-over-day change using fast_info when available
            price_change_today = None
            change_percent = None
            if fast is not None and current_price is not None:
                prev_close = fast.get('previous_close') or fast.get('regular_market_previous_close')
                try:
                    if prev_close is not None and float(prev_close) != 0:
                        price_change_today = float(current_price) - float(prev_close)
                        change_percent = (price_change_today / float(prev_close)) * 100.0
                except Exception:
                    price_change_today = None
                    change_percent = None

            # Day low/high/volume
            days_low = days_high = None
            volume_today = None
            if fast is not None:
                days_low = fast.get('day_low')
                days_high = fast.get('day_high')
                volume_today = fast.get('last_volume') or fast.get('regular_market_volume')

            avg_volume_3mon = None
            if fast is not None:
                avg_volume_3mon = fast.get('three_month_average_volume')
            if avg_volume_3mon is None and info:
                avg_volume_3mon = info.get('averageVolume')

            # Market cap
            market_cap = None
            if fast is not None:
                market_cap = fast.get('market_cap')
            # Derive from price × shares outstanding when missing (info skipped for speed)
            shares_outstanding = None

            # 52-week
            wk_low = wk_high = None
            if fast is not None:
                wk_low = fast.get('year_low')
                wk_high = fast.get('year_high')
            # No fallback to info (skipped for speed)

            # Shares available from float/sharesOutstanding best-effort
            shares_available = None
            # info skipped for speed

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
                'last_updated': (django_timezone.now() if django_timezone else datetime.utcnow()),
                'created_at': (django_timezone.now() if django_timezone else datetime.utcnow()),
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
                # Convert Decimals to floats for CSV
                for col in df.columns:
                    if df[col].map(lambda x: isinstance(x, Decimal)).any():
                        df[col] = df[col].astype(str).astype(float)
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
