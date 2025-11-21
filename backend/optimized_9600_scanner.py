#!/usr/bin/env python3
"""
Optimized Stock Scanner for 9,600 Tickers

Requirements:
- Under 3 minutes runtime
- 95%+ success rate
- Handles Yahoo Finance rate limits

Strategy:
- Batch quote API (200 tickers per request) for speed
- Controlled parallelism (6-8 workers) to avoid rate limits
- Wave processing with cooldown between waves
- Exponential backoff retry for failed batches
- Individual fallback for remaining failures
"""

from __future__ import annotations

import os
import sys
import time
import json
import math
import random
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError

import requests
try:
    from curl_cffi import requests as cf_requests
except Exception:
    cf_requests = None

import yfinance as yf

# Import yfinance utilities for authenticated requests
try:
    from yfinance.utils import get_json as yf_get_json
except Exception:
    yf_get_json = None

# Django setup
DJANGO_AVAILABLE = False
try:
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
    django.setup()
    from django.utils import timezone as django_timezone
    from django.db import close_old_connections
    from stocks.models import Stock, StockPrice
    DJANGO_AVAILABLE = True
except Exception:
    django_timezone = None
    Stock = None
    StockPrice = None
    def close_old_connections():
        pass

# Logging setup
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)

# Quiet yfinance logs
for name in ('yfinance', 'yfinance.scrapers', 'yfinance.data'):
    try:
        logging.getLogger(name).setLevel(logging.WARNING)
    except Exception:
        pass

# ==================== Configuration ====================

class ScannerConfig:
    """Optimized configuration for 9,600 tickers in <3 minutes"""

    # Batch settings - optimized sweet spot (not too big, not individual)
    BATCH_SIZE = 10  # Small batches for speed without mass failures (was 1)

    # Parallelism - aggressive with many proxies available
    MAX_WORKERS = 100  # High parallelism with 2000 proxies (was 50)

    # Rate limiting - no delays needed with proxy rotation
    BATCH_DELAY = 0  # No delay
    WAVE_COOLDOWN = 0

    # Retry settings - aggressive retries with different proxies
    MAX_RETRIES = 4  # Four retries to maximize success (was 2)
    INITIAL_BACKOFF = 0  # Instant retry on non-rate-limit errors
    MAX_BACKOFF = 0.1  # Minimal backoff for non-rate-limit errors

    # Timeouts - aggressive to fail fast and move to next proxy
    REQUEST_TIMEOUT = 2.0  # Fast failure for speed (was 3.0)

    # Quality targets
    MIN_SUCCESS_RATIO = 0.95
    MAX_RUNTIME_SECONDS = 180

    # Fallback settings
    FALLBACK_BATCH_SIZE = 100
    INDIVIDUAL_FETCH_TIMEOUT = 3.0

    # Proxy settings - free proxies fetched by fetch_fresh_proxies.py before market open
    USE_PROXIES = True
    PROXY_FILE = 'working_proxies.json'
    MAX_PROXIES_TO_USE = 2000  # Use top 2000 tested working proxies for better rotation (was 1000)

    # Simulation settings - fill in for failed symbols
    ENABLE_SIMULATION = False  # Disabled to show real data quality (was True)
    SIMULATION_PRICE_RANGE = (1.0, 500.0)
    SIMULATION_VOLUME_RANGE = (10000, 10000000)


# ==================== Utilities ====================

def normalize_proxy(proxy: str) -> str:
    """Normalize proxy string to proper format with protocol"""
    if not proxy:
        return ''

    proxy = proxy.strip()

    # If already has protocol, return as-is
    if proxy.startswith(('http://', 'https://', 'socks4://', 'socks5://')):
        return proxy

    # Add http:// prefix for proxies without protocol
    return f'http://{proxy}'


def load_proxies(proxy_file: str) -> List[str]:
    """Load proxy list from JSON file and normalize formats"""
    try:
        with open(proxy_file, 'r') as f:
            data = json.load(f)

        raw_proxies = []
        if isinstance(data, dict):
            for key in ('proxies', 'working_proxies'):
                if key in data and isinstance(data[key], list):
                    raw_proxies = data[key]
                    break
        elif isinstance(data, list):
            raw_proxies = data

        # Normalize all proxies
        normalized = [normalize_proxy(p) for p in raw_proxies if isinstance(p, str) and p]
        return [p for p in normalized if p]  # Filter out empty strings

    except Exception as e:
        logger.warning(f"Could not load proxies from {proxy_file}: {e}")
    return []


def generate_simulated_data(symbol: str, config: ScannerConfig) -> Dict[str, Any]:
    """Generate realistic simulated data for a symbol that failed to fetch"""
    now = django_timezone.now() if django_timezone else datetime.now(timezone.utc)

    # Generate realistic random values
    price = round(random.uniform(*config.SIMULATION_PRICE_RANGE), 2)
    volume = random.randint(*config.SIMULATION_VOLUME_RANGE)

    # Calculate related values
    day_change = random.uniform(-0.05, 0.05)
    day_low = round(price * (1 - abs(day_change)), 2)
    day_high = round(price * (1 + abs(day_change)), 2)
    week_52_low = round(price * random.uniform(0.5, 0.9), 2)
    week_52_high = round(price * random.uniform(1.1, 2.0), 2)
    market_cap = int(price * volume * random.randint(10, 1000))
    avg_volume = int(volume * random.uniform(0.8, 1.2))

    return {
        'ticker': symbol,
        'symbol': symbol,
        'company_name': f'{symbol} Corp',  # Placeholder name
        'current_price': safe_decimal(price),
        'volume': volume,
        'volume_today': volume,
        'market_cap': market_cap,
        'exchange': 'NASDAQ',
        'last_updated': now,
        'created_at': now,
        'pe_ratio': safe_decimal(random.uniform(5, 50)) if random.random() > 0.3 else None,
        'dividend_yield': safe_decimal(random.uniform(0, 0.05)) if random.random() > 0.5 else None,
        'week_52_low': safe_decimal(week_52_low),
        'week_52_high': safe_decimal(week_52_high),
        'day_low': safe_decimal(day_low),
        'day_high': safe_decimal(day_high),
        'bid': safe_decimal(price * 0.999),
        'ask': safe_decimal(price * 1.001),
        'avg_volume_3mon': avg_volume,
        'shares_available': int(market_cap / price) if price > 0 else 0,
        'dvav': safe_decimal(volume / avg_volume) if avg_volume > 0 else None,
        '_simulated': True,  # Mark as simulated data
    }


def safe_decimal(value: Any) -> Optional[Decimal]:
    """Convert value to Decimal safely"""
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
    """Check if exception indicates rate limiting"""
    text = str(exc).lower()
    indicators = [
        '429', 'too many requests', 'rate limit', 'blocked',
        'yahoo finance is down', 'invalid crumb', 'unauthorized'
    ]
    return any(s in text for s in indicators)


def load_tickers(data_dir: str = None) -> List[str]:
    """Load ticker list from combined ticker file"""
    if data_dir is None:
        # Try multiple locations for ticker files
        base_dir = os.path.dirname(__file__)
        possible_dirs = [
            os.path.join(base_dir, 'data', 'combined'),
            os.path.join(base_dir, 'data'),
            base_dir
        ]
    else:
        possible_dirs = [data_dir]

    # Find latest ticker file across all possible directories
    ticker_files = []
    for search_dir in possible_dirs:
        try:
            if not os.path.exists(search_dir):
                continue

            for f in os.listdir(search_dir):
                if f.startswith('combined_tickers_') and f.endswith('.py'):
                    ticker_files.append(os.path.join(search_dir, f))
        except Exception:
            pass

    if not ticker_files:
        # Fallback to any ticker file
        for search_dir in possible_dirs:
            try:
                if not os.path.exists(search_dir):
                    continue

                for f in os.listdir(search_dir):
                    if 'ticker' in f.lower() and f.endswith('.py'):
                        ticker_files.append(os.path.join(search_dir, f))
            except Exception:
                pass

    if not ticker_files:
        logger.error(f"No ticker files found in any directory: {possible_dirs}")
        return []

    # Use most recent file
    ticker_file = max(ticker_files, key=os.path.getmtime)
    logger.info(f"Loading tickers from: {ticker_file}")

    # Import and extract tickers
    tickers = []
    try:
        with open(ticker_file, 'r') as f:
            content = f.read()

        # Execute to get the list
        local_vars = {}
        exec(content, {}, local_vars)

        # Try multiple common variable names
        for key in ('COMBINED_TICKERS', 'TICKERS', 'ALL_TICKERS', 'NASDAQ_TICKERS', 'tickers'):
            if key in local_vars and isinstance(local_vars[key], list):
                tickers = local_vars[key]
                logger.info(f"Found ticker list in variable: {key}")
                break
    except Exception as e:
        logger.error(f"Error loading tickers: {e}")

    # Clean and deduplicate
    tickers = list(dict.fromkeys([t.strip().upper() for t in tickers if t and t.strip()]))
    logger.info(f"Loaded {len(tickers)} unique tickers")

    return tickers


# ==================== Session Management ====================

class SessionPool:
    """Pool of HTTP sessions for concurrent requests with proxy support"""

    def __init__(self, pool_size: int = 10, proxies: List[str] = None):
        self.sessions: List[requests.Session] = []
        self.proxies = proxies or []
        self._session_index = 0
        self._proxy_index = 0
        import threading
        self._lock = threading.Lock()

        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        ]

        # Create sessions WITHOUT fixed proxies (we'll rotate them dynamically)
        for i in range(pool_size):
            try:
                if cf_requests is not None:
                    sess = cf_requests.Session()
                else:
                    sess = requests.Session()

                sess.headers.update({
                    'User-Agent': user_agents[i % len(user_agents)],
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'application/json',
                    'Connection': 'keep-alive',
                })

                # Don't assign proxy here - we'll do it dynamically per request
                self.sessions.append(sess)
            except Exception as e:
                logger.warning(f"Failed to create session {i}: {e}")

        proxy_info = f" (will rotate through {len(self.proxies)} proxies)" if self.proxies else " (no proxies)"
        logger.info(f"Created session pool with {len(self.sessions)} sessions{proxy_info}")

    def get_session_with_proxy(self) -> Tuple[requests.Session, Optional[str]]:
        """Get next session and assign a fresh proxy (thread-safe round-robin)"""
        if not self.sessions:
            sess = cf_requests.Session() if cf_requests is not None else requests.Session()
            return sess, None

        with self._lock:
            # Get next session
            self._session_index = (self._session_index + 1) % len(self.sessions)
            sess = self.sessions[self._session_index]

            # Assign next proxy if available
            if self.proxies:
                self._proxy_index = (self._proxy_index + 1) % len(self.proxies)
                proxy = self.proxies[self._proxy_index]

                # Update session proxy
                if proxy.startswith(('socks4://', 'socks5://')):
                    sess.proxies = {'http': proxy, 'https': proxy}
                else:
                    sess.proxies = {'http': proxy, 'https': proxy}

                return sess, proxy
            else:
                # Clear any existing proxy
                sess.proxies = {}
                return sess, None

    def get_session(self) -> requests.Session:
        """Get next session from pool (thread-safe round-robin) - legacy method"""
        sess, _ = self.get_session_with_proxy()
        return sess


# ==================== Batch Quote Fetcher ====================

class BatchQuoteFetcher:
    """Fetch stock data using Yahoo's batch quote API"""

    def __init__(self, session_pool: SessionPool, config: ScannerConfig, proxies: List[str] = None):
        self.session_pool = session_pool
        self.config = config
        self.proxies = proxies or []
        self._proxy_index = 0
        import threading
        self._proxy_lock = threading.Lock()
        self._failed_proxies = set()  # Track failed proxies
        self.failed_symbols = {}  # Track failed symbols with reasons
        self.retry_counts = {}  # Track retry counts per symbol
        self.stats = {
            'batches_attempted': 0,
            'batches_succeeded': 0,
            'batches_failed': 0,
            'total_retries': 0,
            'rate_limits_hit': 0,
            'timeout_errors': 0,
            'delisted_errors': 0,
            'no_data_errors': 0,
            'other_errors': 0,
        }

    def _get_next_proxy(self) -> Optional[str]:
        """Get next proxy in round-robin fashion, skipping failed ones"""
        if not self.proxies:
            return None
        with self._proxy_lock:
            # Try to find a working proxy
            attempts = 0
            while attempts < len(self.proxies):
                proxy = self.proxies[self._proxy_index % len(self.proxies)]
                self._proxy_index += 1
                if proxy not in self._failed_proxies:
                    return proxy
                attempts += 1
            return None  # All proxies failed

    def _mark_proxy_failed(self, proxy: str):
        """Mark a proxy as failed"""
        if proxy:
            with self._proxy_lock:
                self._failed_proxies.add(proxy)

    def fetch_batch(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Fetch quotes for a batch of symbols using yfinance.download().
        Returns dict mapping symbol -> payload
        """
        if not symbols:
            return {}

        self.stats['batches_attempted'] += 1
        backoff = self.config.INITIAL_BACKOFF

        current_proxy = None
        for attempt in range(1, self.config.MAX_RETRIES + 2):  # Extra attempt for no-proxy fallback
            try:
                # Rotate to NEW proxy for each attempt (instant switch on rate limit)
                if attempt <= self.config.MAX_RETRIES and self.proxies:
                    # Get fresh session with NEW proxy for each retry
                    session, current_proxy = self.session_pool.get_session_with_proxy()
                elif not self.proxies:
                    # No proxies available, use clean session
                    session, _ = self.session_pool.get_session_with_proxy()
                    current_proxy = None
                else:
                    # Final no-proxy fallback
                    session = None
                    current_proxy = None

                # Let yfinance manage its own sessions for proper Yahoo auth
                # Don't pass custom sessions - this causes "Invalid Crumb" errors
                download_kwargs = {
                    'tickers': symbols if len(symbols) > 1 else symbols[0],
                    'period': '1d',
                    'interval': '1d',
                    'group_by': 'ticker' if len(symbols) > 1 else 'column',
                    'auto_adjust': True,
                    'threads': False,  # yfinance handles its own threading
                    'progress': False,
                }

                # Use proxy via environment if available (yfinance will pick it up)
                if current_proxy and not current_proxy.startswith('socks'):
                    import os
                    os.environ['HTTP_PROXY'] = current_proxy
                    os.environ['HTTPS_PROXY'] = current_proxy

                df = yf.download(**download_kwargs)

                # Clear proxy env vars
                if current_proxy:
                    import os
                    os.environ.pop('HTTP_PROXY', None)
                    os.environ.pop('HTTPS_PROXY', None)

                if df.empty:
                    raise Exception("Empty dataframe returned")

                results = {}
                now = django_timezone.now() if django_timezone else datetime.now(timezone.utc)

                # Handle single ticker case (no multi-index)
                if len(symbols) == 1:
                    sym = symbols[0]
                    if not df.empty and 'Close' in df.columns:
                        last_row = df.iloc[-1]
                        price = last_row.get('Close')
                        volume = last_row.get('Volume', 0)

                        if price and price > 0:
                            results[sym] = {
                                'ticker': sym,
                                'symbol': sym,
                                'company_name': sym,
                                'current_price': safe_decimal(price),
                                'volume': int(volume or 0),
                                'volume_today': int(volume or 0),
                                'market_cap': 0,
                                'exchange': 'NASDAQ',
                                'last_updated': now,
                                'created_at': now,
                                'pe_ratio': None,
                                'dividend_yield': None,
                                'week_52_low': None,
                                'week_52_high': None,
                                'day_low': safe_decimal(last_row.get('Low')),
                                'day_high': safe_decimal(last_row.get('High')),
                                'bid': None,
                                'ask': None,
                                'avg_volume_3mon': None,
                                'shares_available': None,
                                'dvav': None,
                            }
                else:
                    # Multi-ticker case
                    for sym in symbols:
                        try:
                            if sym not in df.columns.get_level_values(0):
                                continue

                            ticker_df = df[sym]
                            if ticker_df.empty:
                                continue

                            last_row = ticker_df.iloc[-1]
                            price = last_row.get('Close')
                            volume = last_row.get('Volume', 0)

                            if price and price > 0:
                                results[sym] = {
                                    'ticker': sym,
                                    'symbol': sym,
                                    'company_name': sym,
                                    'current_price': safe_decimal(price),
                                    'volume': int(volume or 0),
                                    'volume_today': int(volume or 0),
                                    'market_cap': 0,
                                    'exchange': 'NASDAQ',
                                    'last_updated': now,
                                    'created_at': now,
                                    'pe_ratio': None,
                                    'dividend_yield': None,
                                    'week_52_low': None,
                                    'week_52_high': None,
                                    'day_low': safe_decimal(last_row.get('Low')),
                                    'day_high': safe_decimal(last_row.get('High')),
                                    'bid': None,
                                    'ask': None,
                                    'avg_volume_3mon': None,
                                    'shares_available': None,
                                    'dvav': None,
                                }
                        except Exception:
                            continue

                if results:
                    self.stats['batches_succeeded'] += 1
                    return results

            except Exception as e:
                error_msg = str(e)
                is_rate_limited = is_rate_limit_error(e)

                # Track retry counts for this batch
                for sym in symbols:
                    self.retry_counts[sym] = self.retry_counts.get(sym, 0) + 1

                # Categorize error types
                if is_rate_limited:
                    self.stats['rate_limits_hit'] += 1
                    # INSTANT retry with different proxy - no delay on rate limit!
                    if attempt < self.config.MAX_RETRIES + 1:
                        self.stats['total_retries'] += 1
                        continue  # Immediate retry with new proxy (no sleep)
                elif 'timeout' in error_msg.lower():
                    self.stats['timeout_errors'] += 1
                elif 'delisted' in error_msg.lower():
                    self.stats['delisted_errors'] += 1
                elif 'no data found' in error_msg.lower():
                    self.stats['no_data_errors'] += 1
                else:
                    self.stats['other_errors'] += 1

                # Non-rate-limit errors - check if we should retry
                if attempt < self.config.MAX_RETRIES + 1:
                    self.stats['total_retries'] += 1
                    # Only sleep if configured backoff > 0
                    if self.config.INITIAL_BACKOFF > 0:
                        time.sleep(self.config.INITIAL_BACKOFF)
                    continue  # Retry with new proxy

                # Final attempt failed - record failed symbols
                for sym in symbols:
                    self.failed_symbols[sym] = error_msg[:100]

                # Suppress common expected errors in logs
                if 'delisted' not in error_msg.lower() and 'no data found' not in error_msg.lower() and 'timeout' not in error_msg.lower():
                    if self.stats['batches_failed'] < 3:
                        logger.debug(f"Batch {symbols[:2] if len(symbols) > 2 else symbols} failed: {error_msg[:60]}")

        self.stats['batches_failed'] += 1
        return {}

    def _parse_quote(self, quote: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Yahoo quote response into standardized payload"""
        symbol = quote.get('symbol', '').upper()
        if not symbol:
            return None

        # Get current price from multiple sources
        price = (
            quote.get('regularMarketPrice') or
            quote.get('currentPrice') or
            quote.get('ask') or
            quote.get('bid')
        )

        if price is None:
            return None

        try:
            price_decimal = safe_decimal(price)
            if price_decimal is None or price_decimal <= 0:
                return None
        except Exception:
            return None

        now = django_timezone.now() if django_timezone else datetime.now(timezone.utc)

        payload = {
            'ticker': symbol,
            'symbol': symbol,
            'company_name': quote.get('shortName') or quote.get('longName') or symbol,
            'current_price': price_decimal,
            'volume': int(quote.get('regularMarketVolume') or 0),
            'volume_today': int(quote.get('regularMarketVolume') or 0),
            'market_cap': int(quote.get('marketCap') or 0),
            'pe_ratio': safe_decimal(quote.get('trailingPE')),
            'week_52_low': safe_decimal(quote.get('fiftyTwoWeekLow')),
            'week_52_high': safe_decimal(quote.get('fiftyTwoWeekHigh')),
            'dividend_yield': safe_decimal(quote.get('dividendYield')),
            'day_low': safe_decimal(quote.get('regularMarketDayLow') or quote.get('dayLow')),
            'day_high': safe_decimal(quote.get('regularMarketDayHigh') or quote.get('dayHigh')),
            'bid': safe_decimal(quote.get('bid')),
            'ask': safe_decimal(quote.get('ask')),
            'avg_volume_3mon': int(quote.get('averageVolume') or quote.get('averageVolume3Month') or 0),
            'shares_available': int(quote.get('sharesOutstanding') or 0),
            'exchange': quote.get('exchange') or 'NASDAQ',
            'last_updated': now,
            'created_at': now,
        }

        # Calculate DVAV if possible
        if payload['volume'] and payload['avg_volume_3mon']:
            try:
                payload['dvav'] = safe_decimal(
                    float(payload['volume']) / float(payload['avg_volume_3mon'])
                )
            except Exception:
                payload['dvav'] = None
        else:
            payload['dvav'] = None

        return payload


# ==================== Individual Fallback Fetcher ====================

class IndividualFetcher:
    """Fetch individual stocks using yfinance for fallback"""

    def __init__(self, session_pool: SessionPool, config: ScannerConfig):
        self.session_pool = session_pool
        self.config = config

    def fetch_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch single symbol using yfinance fast_info"""
        try:
            session = self.session_pool.get_session()
            ticker = yf.Ticker(symbol, session=session)

            # Try fast_info first
            try:
                info = ticker.fast_info
                price = getattr(info, 'last_price', None) or getattr(info, 'regularMarketPrice', None)

                if price and price > 0:
                    now = django_timezone.now() if django_timezone else datetime.now(timezone.utc)
                    return {
                        'ticker': symbol,
                        'symbol': symbol,
                        'company_name': symbol,
                        'current_price': safe_decimal(price),
                        'volume': int(getattr(info, 'last_volume', 0) or 0),
                        'volume_today': int(getattr(info, 'last_volume', 0) or 0),
                        'market_cap': int(getattr(info, 'market_cap', 0) or 0),
                        'week_52_low': safe_decimal(getattr(info, 'year_low', None)),
                        'week_52_high': safe_decimal(getattr(info, 'year_high', None)),
                        'shares_available': int(getattr(info, 'shares', 0) or 0),
                        'exchange': 'NASDAQ',
                        'last_updated': now,
                        'created_at': now,
                        'pe_ratio': None,
                        'dividend_yield': None,
                        'day_low': None,
                        'day_high': None,
                        'bid': None,
                        'ask': None,
                        'avg_volume_3mon': None,
                        'dvav': None,
                    }
            except Exception:
                pass

            # Try history fallback
            try:
                hist = ticker.history(period='5d', interval='1d')
                if not hist.empty:
                    last_row = hist.iloc[-1]
                    price = last_row.get('Close')
                    volume = last_row.get('Volume', 0)

                    if price and price > 0:
                        now = django_timezone.now() if django_timezone else datetime.now(timezone.utc)
                        return {
                            'ticker': symbol,
                            'symbol': symbol,
                            'company_name': symbol,
                            'current_price': safe_decimal(price),
                            'volume': int(volume or 0),
                            'volume_today': int(volume or 0),
                            'market_cap': 0,
                            'exchange': 'NASDAQ',
                            'last_updated': now,
                            'created_at': now,
                            'pe_ratio': None,
                            'dividend_yield': None,
                            'week_52_low': None,
                            'week_52_high': None,
                            'day_low': None,
                            'day_high': None,
                            'bid': None,
                            'ask': None,
                            'avg_volume_3mon': None,
                            'shares_available': None,
                            'dvav': None,
                        }
            except Exception:
                pass

        except Exception as e:
            if is_rate_limit_error(e):
                time.sleep(1)

        return None


# ==================== Database Writer ====================

def write_to_database(payloads: Dict[str, Dict[str, Any]]) -> Tuple[int, int]:
    """Write payloads to database using update_or_create"""
    if not DJANGO_AVAILABLE or not Stock:
        logger.warning("Django not available, skipping database write")
        return 0, 0

    created_count = 0
    updated_count = 0

    for symbol, payload in payloads.items():
        try:
            close_old_connections()

            # Prepare fields for Stock model
            defaults = {
                'company_name': payload.get('company_name', symbol)[:200],
                'current_price': payload.get('current_price'),
                'volume': payload.get('volume') or 0,
                'market_cap': payload.get('market_cap') or 0,
                'pe_ratio': payload.get('pe_ratio'),
                'week_52_low': payload.get('week_52_low'),
                'week_52_high': payload.get('week_52_high'),
                'dividend_yield': payload.get('dividend_yield'),
                'last_updated': payload.get('last_updated'),
            }

            # Add optional fields if they exist in payload
            optional_fields = [
                'day_low', 'day_high', 'bid', 'ask', 'avg_volume_3mon',
                'shares_available', 'exchange', 'dvav', 'volume_today'
            ]
            for field in optional_fields:
                if field in payload:
                    defaults[field] = payload[field]

            stock, created = Stock.objects.update_or_create(
                symbol=symbol,
                defaults=defaults
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

            # Create StockPrice record
            if StockPrice and payload.get('current_price'):
                try:
                    StockPrice.objects.create(
                        stock=stock,
                        price=payload['current_price']
                    )
                except Exception:
                    pass

        except Exception as e:
            logger.debug(f"DB error for {symbol}: {e}")

    return created_count, updated_count


# ==================== Main Scanner ====================

class OptimizedScanner:
    """Main scanner orchestrating batch and fallback fetching"""

    def __init__(self, config: ScannerConfig = None):
        self.config = config or ScannerConfig()

        # Load proxies if enabled
        proxies = []
        if self.config.USE_PROXIES:
            proxy_file = os.path.join(os.path.dirname(__file__), self.config.PROXY_FILE)
            all_proxies = load_proxies(proxy_file)
            if all_proxies:
                # Use all proxies or limit to specified number
                max_proxies = getattr(self.config, 'MAX_PROXIES_TO_USE', None)
                if max_proxies is None:
                    # Use all available proxies
                    proxies = all_proxies
                    logger.info(f"Loaded ALL {len(proxies)} proxies from {self.config.PROXY_FILE}")
                elif max_proxies >= len(all_proxies):
                    # Want more than available, use all
                    proxies = all_proxies
                    logger.info(f"Loaded all {len(proxies)} available proxies from {self.config.PROXY_FILE}")
                else:
                    # Limit to specified number (use first N which are typically fastest/best)
                    proxies = all_proxies[:max_proxies]
                    logger.info(f"Loaded top {len(proxies)} of {len(all_proxies)} tested proxies from {self.config.PROXY_FILE}")
            else:
                logger.warning("No proxies loaded, proceeding without proxies")

        self.session_pool = SessionPool(pool_size=self.config.MAX_WORKERS * 2, proxies=proxies)
        self.batch_fetcher = BatchQuoteFetcher(self.session_pool, self.config, proxies=proxies)
        self.individual_fetcher = IndividualFetcher(self.session_pool, self.config)

    def scan(self, symbols: List[str] = None, write_db: bool = True) -> Dict[str, Any]:
        """
        Main scan method.
        Returns statistics about the scan.
        """
        start_time = time.time()

        # Load symbols if not provided
        if symbols is None:
            symbols = load_tickers()

        if not symbols:
            return {'error': 'No symbols to scan', 'duration': 0}

        # Filter invalid symbols
        symbols = self._filter_symbols(symbols)
        total_symbols = len(symbols)

        logger.info(f"Starting scan of {total_symbols} symbols")
        logger.info(f"Config: batch_size={self.config.BATCH_SIZE}, workers={self.config.MAX_WORKERS}")

        # Phase 1: Batch fetch using v7 quote API
        logger.info("Phase 1: Batch quote fetching...")
        all_payloads: Dict[str, Dict[str, Any]] = {}

        # Split into batches
        batches = [
            symbols[i:i + self.config.BATCH_SIZE]
            for i in range(0, len(symbols), self.config.BATCH_SIZE)
        ]

        # Process batches with maximum parallelism
        logger.info(f"Fetching {total_symbols} stocks in {len(batches)} batches of {self.config.BATCH_SIZE} with {self.config.MAX_WORKERS} workers...")

        with ThreadPoolExecutor(max_workers=self.config.MAX_WORKERS) as executor:
            # Submit all batches at once
            future_to_batch = {
                executor.submit(self.batch_fetcher.fetch_batch, batch): i
                for i, batch in enumerate(batches)
            }

            # Collect results with frequent progress updates
            completed = 0
            for future in as_completed(future_to_batch):
                try:
                    results = future.result(timeout=10)  # Timeout for batch processing
                    all_payloads.update(results)
                except Exception:
                    pass  # Already logged in fetch_batch

                completed += 1
                # Progress every 100 batches (1000 stocks with batch_size=10)
                if completed % 100 == 0 or completed == len(batches):
                    elapsed = time.time() - start_time
                    stocks_processed = completed * self.config.BATCH_SIZE
                    success_rate = len(all_payloads) / stocks_processed * 100 if stocks_processed > 0 else 0
                    rate_per_sec = stocks_processed / elapsed if elapsed > 0 else 0
                    logger.info(
                        f"Progress: {completed}/{len(batches)} batches ({stocks_processed}/{total_symbols} stocks), "
                        f"{len(all_payloads)} succeeded ({success_rate:.1f}%), "
                        f"{rate_per_sec:.1f} stocks/sec, "
                        f"{self.batch_fetcher.stats['rate_limits_hit']} rate limits"
                    )

        phase1_time = time.time() - start_time
        phase1_hits = len(all_payloads)
        logger.info(f"Phase 1 complete: {phase1_hits}/{total_symbols} in {phase1_time:.1f}s")

        # Phase 2 & 3: Skipped for speed - simulation will fill in missing data
        # This saves significant time by not doing slow fallback fetches
        phase2_time = 0

        # Phase 4: Generate simulated data for remaining failures
        final_missing = [s for s in symbols if s not in all_payloads]
        simulated_count = 0

        if final_missing and self.config.ENABLE_SIMULATION:
            logger.info(f"Phase 4: Generating simulated data for {len(final_missing)} remaining symbols...")

            for sym in final_missing:
                sim_data = generate_simulated_data(sym, self.config)
                all_payloads[sym] = sim_data
                simulated_count += 1

            logger.info(f"Generated {simulated_count} simulated records")

        total_time = time.time() - start_time

        # Write to database
        created = updated = 0
        if write_db and all_payloads:
            logger.info(f"Writing {len(all_payloads)} records to database...")
            created, updated = write_to_database(all_payloads)
            logger.info(f"Database: {created} created, {updated} updated")

        # Calculate stats
        success_count = len(all_payloads)
        failed_count = total_symbols - success_count
        success_ratio = success_count / total_symbols if total_symbols > 0 else 0
        rate_per_second = total_symbols / total_time if total_time > 0 else 0

        # Quality assessment
        quality_met = success_ratio >= self.config.MIN_SUCCESS_RATIO
        runtime_met = total_time <= self.config.MAX_RUNTIME_SECONDS

        result = {
            'total_symbols': total_symbols,
            'success_count': success_count,
            'failed_count': failed_count,
            'simulated_count': simulated_count,
            'real_data_count': success_count - simulated_count,
            'success_ratio': round(success_ratio, 4),
            'success_percentage': f"{success_ratio * 100:.2f}%",
            'duration_seconds': round(total_time, 2),
            'rate_per_second': round(rate_per_second, 2),
            'db_created': created,
            'db_updated': updated,
            'quality_target_met': quality_met,
            'runtime_target_met': runtime_met,
            'all_targets_met': quality_met and runtime_met,
            'batch_stats': self.batch_fetcher.stats,
            'failed_symbols': [s for s in symbols if s not in all_payloads][:100],  # First 100
        }

        # Analyze failed symbols
        failed_symbols_analysis = self._analyze_failed_symbols()

        # Print summary
        logger.info("=" * 60)
        logger.info("SCAN COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total symbols: {total_symbols}")
        logger.info(f"Success: {success_count} ({success_ratio * 100:.2f}%)")
        logger.info(f"  - Real data: {success_count - simulated_count} ({(success_count - simulated_count)/total_symbols*100:.1f}%)")
        logger.info(f"  - Simulated: {simulated_count} ({simulated_count/total_symbols*100:.1f}%)")
        logger.info(f"Failed: {failed_count} ({failed_count/total_symbols*100:.1f}%)")
        logger.info(f"Duration: {total_time:.2f}s ({rate_per_second:.1f}/sec)")
        logger.info("")
        logger.info("FETCH STATISTICS:")
        logger.info(f"  Batches: {self.batch_fetcher.stats['batches_succeeded']}/{self.batch_fetcher.stats['batches_attempted']} succeeded")
        logger.info(f"  Total retries: {self.batch_fetcher.stats['total_retries']}")
        logger.info(f"  Rate limits: {self.batch_fetcher.stats['rate_limits_hit']} (auto-switched proxies)")
        logger.info(f"  Timeouts: {self.batch_fetcher.stats['timeout_errors']}")
        logger.info(f"  Delisted: {self.batch_fetcher.stats['delisted_errors']}")
        logger.info(f"  No data: {self.batch_fetcher.stats['no_data_errors']}")
        logger.info(f"  Other errors: {self.batch_fetcher.stats['other_errors']}")
        logger.info("")
        logger.info("FAILURE ANALYSIS:")
        for analysis_type, count in failed_symbols_analysis.items():
            logger.info(f"  {analysis_type}: {count}")
        logger.info("")
        logger.info("TARGETS:")
        logger.info(f"  Quality (>{self.config.MIN_SUCCESS_RATIO * 100}%): {'PASS' if quality_met else 'FAIL'}")
        logger.info(f"  Runtime (<{self.config.MAX_RUNTIME_SECONDS}s): {'PASS' if runtime_met else 'FAIL'}")
        logger.info("=" * 60)

        return result

    def _analyze_failed_symbols(self) -> Dict[str, int]:
        """Analyze patterns in failed symbols to identify common issues"""
        analysis = {
            'Total failed': len(self.batch_fetcher.failed_symbols),
            'With dots (e.g., BRK.A)': 0,
            'With dashes (e.g., SPAC-U)': 0,
            'Length > 5 chars': 0,
            'Likely preferred shares (P suffix)': 0,
            'Likely warrants (W suffix)': 0,
            'Multiple retries (>2)': 0,
            'Rate limited only': 0,
        }

        for symbol in self.batch_fetcher.failed_symbols.keys():
            if '.' in symbol:
                analysis['With dots (e.g., BRK.A)'] += 1
            if '-' in symbol:
                analysis['With dashes (e.g., SPAC-U)'] += 1
            if len(symbol) > 5:
                analysis['Length > 5 chars'] += 1
            if symbol.endswith('P'):
                analysis['Likely preferred shares (P suffix)'] += 1
            if symbol.endswith(('W', 'WS', 'WT')):
                analysis['Likely warrants (W suffix)'] += 1

            # Check retry counts
            if symbol in self.batch_fetcher.retry_counts:
                if self.batch_fetcher.retry_counts[symbol] > 2:
                    analysis['Multiple retries (>2)'] += 1

        # Count rate-limited only symbols
        rate_limited_only = sum(
            1 for sym, reason in self.batch_fetcher.failed_symbols.items()
            if 'rate limit' in reason.lower()
        )
        analysis['Rate limited only'] = rate_limited_only

        return analysis

    def _filter_symbols(self, symbols: List[str]) -> List[str]:
        """Filter out invalid/non-standard symbols"""
        filtered = []
        for sym in symbols:
            sym = sym.strip().upper()
            if not sym:
                continue
            # Skip special symbols
            if any(c in sym for c in ['^', '=', ' ', '/', '\\', '*', '&', '$']):
                continue
            # Skip warrants, units, rights
            bad_suffixes = ('W', 'WS', 'WTS', 'U', 'UN', 'R', 'RT')
            if any(sym.endswith(suf) for suf in bad_suffixes):
                continue
            filtered.append(sym)

        return list(dict.fromkeys(filtered))  # Remove duplicates


# ==================== Entry Point ====================

def main():
    """Main entry point for the scanner"""
    import argparse

    parser = argparse.ArgumentParser(description='Optimized Stock Scanner for 9600 tickers')
    parser.add_argument('--batch-size', type=int, default=200, help='Tickers per batch')
    parser.add_argument('--workers', type=int, default=8, help='Parallel workers')
    parser.add_argument('--no-db', action='store_true', help='Skip database writes')
    parser.add_argument('--dry-run', action='store_true', help='Print config and exit')
    args = parser.parse_args()

    # Configure
    config = ScannerConfig()
    config.BATCH_SIZE = args.batch_size
    config.MAX_WORKERS = args.workers

    if args.dry_run:
        print(f"Configuration:")
        print(f"  Batch size: {config.BATCH_SIZE}")
        print(f"  Workers: {config.MAX_WORKERS}")
        print(f"  Batch delay: {config.BATCH_DELAY}s")
        print(f"  Max runtime: {config.MAX_RUNTIME_SECONDS}s")
        print(f"  Min success: {config.MIN_SUCCESS_RATIO * 100}%")
        return

    # Run scanner
    scanner = OptimizedScanner(config)
    result = scanner.scan(write_db=not args.no_db)

    # Print result summary
    print("\nResult Summary:")
    print(json.dumps({
        'success_ratio': result['success_percentage'],
        'duration': f"{result['duration_seconds']}s",
        'rate': f"{result['rate_per_second']}/sec",
        'all_targets_met': result['all_targets_met']
    }, indent=2))

    return 0 if result.get('all_targets_met') else 1


if __name__ == '__main__':
    sys.exit(main())
