#!/usr/bin/env python3
"""
Enhanced Stock Retrieval Script - WORKING VERSION (Direct Proxy Loading)
Uses entire NYSE CSV, filters delisted stocks, supports production settings
Command line options: -noproxy, -test (100 first tickers), -threads, -timeout
Runs every 3 minutes in background with database integration
"""

import os
import sys
import time
import random
import json
import csv
import argparse
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import requests
from datetime import datetime, timedelta
import logging
import signal
import schedule
import threading
from decimal import Decimal
from collections import defaultdict
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import subprocess
import pytz
from pathlib import Path
import importlib.util
from numbers import Number

# Django imports for database integration
# Lazy Django initialization: only import when saving to DB
DJANGO_READY = False
Stock = None
StockPrice = None
try:
    from django.utils import timezone as django_timezone  # Optional, used if Django is available
except Exception:  # pragma: no cover
    django_timezone = None

def ensure_django_initialized():
    """Initialize Django and import models only when needed."""
    global DJANGO_READY, Stock, StockPrice, django_timezone
    if DJANGO_READY:
        return
    try:
        import django  # type: ignore
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings'))
        django.setup()
        from django.utils import timezone as tz  # type: ignore
        from stocks.models import Stock as StockModel, StockPrice as StockPriceModel  # type: ignore
        django_timezone = tz
        Stock = StockModel
        StockPrice = StockPriceModel
        DJANGO_READY = True
        logger.info("Django initialized for DB operations")
    except Exception as e:  # pragma: no cover
        logger.error(f"Failed to initialize Django: {e}")
        DJANGO_READY = False

def now_ts():
    """Return a timezone-aware timestamp if Django is available; otherwise UTC now."""
    try:
        if django_timezone is not None:
            return django_timezone.now()
    except Exception:
        pass
    return datetime.now(pytz.UTC)

# Import shared utilities
from utils.stock_data import (
    safe_decimal_conversion, 
    load_nyse_symbols_from_csv, 
    extract_pe_ratio, 
    extract_dividend_yield,
    calculate_change_percent_from_history,
    extract_stock_data_from_info,
    extract_stock_data_from_fast_info,
    calculate_volume_ratio,
    compute_market_cap_fallback
)

# Setup logging with rotation
from logging.handlers import RotatingFileHandler

# Configure logger with rotation to avoid unbounded log growth
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handlers
file_handler = RotatingFileHandler(
    'enhanced_stock_retrieval_working.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
console_handler = logging.StreamHandler()

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Prevent propagation to avoid duplicate messages
logger.propagate = False

# Global flag for graceful shutdown
shutdown_flag = False
# DB write serialization lock (prevents SQLite 'database is locked' errors)
db_write_lock = threading.Lock()


# Market window configuration (US/Eastern) - ONLY REGULAR MARKET HOURS
EASTERN_TZ = pytz.timezone('US/Eastern')
# Only update during regular market hours
MARKET_OPEN = os.getenv('MARKET_OPEN', "09:30")    # 9:30 AM ET
MARKET_CLOSE = os.getenv('MARKET_CLOSE', "16:00")  # 4:00 PM ET
# Pre-market and post-market disabled
# PREMARKET_START = os.getenv('PREMARKET_START', "04:00")  # DISABLED
# POSTMARKET_END = os.getenv('POSTMARKET_END', "20:00")   # DISABLED

# Global proxy health tracking with thread safety
proxy_health = defaultdict(lambda: {"failures": 0, "successes": 0, "last_failure": None, "blocked": False})
proxy_health_lock = threading.Lock()  # Protect proxy_health dict updates
proxy_failure_threshold = 3  # Mark proxy as blocked after 3 consecutive failures
proxy_retry_cooldown = 300  # 5 minutes before retrying a blocked proxy

# New: normalize and validate proxy strings

def normalize_proxy_string(proxy_str: str) -> str | None:
    """Ensure proxy has a scheme and basic host:port shape."""
    if not proxy_str or not isinstance(proxy_str, str):
        return None
    p = proxy_str.strip()
    if not p:
        return None
    if '://' not in p:
        # Assume HTTP if not specified
        p = f"http://{p}"
    return p


# Build a per-proxy requests.Session configured for Yahoo endpoints
def create_session_for_proxy(proxy: str | None, timeout_seconds: int) -> requests.Session:
    """Create a session with proxy, UA headers, retries, and response hook.

    yfinance supports passing a custom requests.Session to Ticker; we avoid
    globally patching shared session to keep each thread isolated.
    """
    session = requests.Session()

    # Proxies if provided
    if proxy:
        session.proxies = {"http": proxy, "https": proxy}

    # Reasonable browser-like headers
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    })

    # Retry policy including 429/999 with backoff
    retry = Retry(
        total=3,
        read=3,
        connect=3,
        status=3,
        backoff_factor=0.4,
        status_forcelist=(429, 500, 502, 503, 504, 520, 521, 522, 524, 999),
        allowed_methods=frozenset(["HEAD", "GET", "OPTIONS"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=16, pool_maxsize=32)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Default timeout injection for all requests made via this session
    _orig_request = session.request

    def _request_with_timeout(method, url, **kwargs):
        if "timeout" not in kwargs or kwargs["timeout"] is None:
            kwargs["timeout"] = timeout_seconds
        return _orig_request(method, url, **kwargs)

    session.request = _request_with_timeout  # type: ignore[assignment]

    # Hook: mark proxy as failing on HTTP 429/999 to trigger rotation
    def _response_hook(resp, *args, **kwargs):
        try:
            if proxy and resp is not None and resp.status_code in (429, 999):
                mark_proxy_failure(proxy, f"HTTP {resp.status_code}")
        except Exception:
            pass

    session.hooks["response"].append(_response_hook)
    return session

# Thread-safe proxy manager to lease unique proxies per thread
class ProxyManager:
    def __init__(self, proxies: list[str] | None = None):
        self.lock = threading.Lock()
        self.proxies: list[str] = list(proxies) if proxies else []
        self.in_use: set[str] = set()

    def _healthy_candidates(self, exclude: set[str] | None = None) -> list[str]:
        """Return proxies that are not in use, not excluded, and not blocked (or cooled down)."""
        if exclude is None:
            exclude = set()
        now = datetime.now()
        candidates: list[str] = []
        for px in self.proxies:
            if px in self.in_use or px in exclude:
                continue
            health = proxy_health[px]
            if health["blocked"]:
                if health["last_failure"] and (now - health["last_failure"]).total_seconds() > proxy_retry_cooldown:
                    # Cooldown expired; un-block
                    health["blocked"] = False
                    health["failures"] = 0
                else:
                    continue
            candidates.append(px)
        # Prefer proxies with fewer failures
        candidates.sort(key=lambda p: proxy_health[p]["failures"])
        return candidates

    def lease_proxy(self, exclude: set[str] | None = None, wait: bool = True, timeout: float = 5.0) -> str | None:
        """Lease a proxy not currently in use. Optionally wait up to timeout seconds."""
        deadline = time.time() + max(0.0, timeout)
        while True:
            with self.lock:
                candidates = self._healthy_candidates(exclude)
                if candidates:
                    px = candidates[0]
                    self.in_use.add(px)
                    return px
            if not wait or time.time() >= deadline:
                return None
            time.sleep(0.05)

    def release_proxy(self, proxy: str | None) -> None:
        if not proxy:
            return
        with self.lock:
            if proxy in self.in_use:
                self.in_use.remove(proxy)

    def refresh_proxies(self, new_proxies: list[str] | None) -> None:
        """Replace the proxy list and clear in-use assignments."""
        with self.lock:
            self.proxies = list(new_proxies) if new_proxies else []
            self.in_use.clear()

def signal_handler(signum, frame):
    """Handle interrupt signals gracefully"""
    global shutdown_flag
    logger.info("Received interrupt signal. Shutting down gracefully...")
    shutdown_flag = True

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Enhanced Stock Retrieval Script - WORKING')
    parser.add_argument('-noproxy', action='store_true', help='Disable proxy usage')
    parser.add_argument('-test', action='store_true', help='Test mode - process only first 100 tickers')
    parser.add_argument('-threads', type=int, default=12, help='Number of threads (default: 12)')
    parser.add_argument('-timeout', type=int, default=10, help='Request timeout in seconds (default: 10)')
    parser.add_argument('-csv', type=str, default=os.getenv('NYSE_CSV_PATH', 'flat-ui__data-Fri Aug 01 2025.csv'), 
                       help='NYSE CSV file path (default from NYSE_CSV_PATH env var or flat-ui__data-Fri Aug 01 2025.csv)')
    parser.add_argument('-output', type=str, default=None, 
                       help='Output JSON file (default: auto-generated timestamp)')
    parser.add_argument('-output-csv', type=str, default=None,
                       help='Optional: Output CSV file path')
    parser.add_argument('-max-symbols', type=int, default=None, 
                       help='Maximum number of symbols to process (for testing)')
    parser.add_argument('-proxy-file', type=str, default=os.getenv('PROXY_FILE_PATH', 'working_proxies.json'),
                       help='Proxy JSON file path (default from PROXY_FILE_PATH env var or working_proxies.json)')
    parser.add_argument('-schedule', action='store_true', help='Run in scheduler mode (every 3 minutes)')
    parser.add_argument('-save-to-db', action='store_true', default=False, help='Save results to database (default: False)')
    parser.add_argument('-update-proxies', action='store_true', help='Force proxy update before starting')
    parser.add_argument('-daily-update', action='store_true', help='Run daily 9 AM update with proxy refresh')
    parser.add_argument('-combined', action='store_true', help='Use combined tickers from data/combined instead of CSV')
    parser.add_argument('-combined-file', type=str, default=None, help='Path to specific combined_tickers_*.py file')
    parser.add_argument('-ignore-market-hours', action='store_true', help='Run even outside regular market hours')
    return parser.parse_args()

# ---------------------
# JSON sanitization helpers (convert Decimals, numpy/pandas types to primitives)
# ---------------------
def _coerce_number(x):
    try:
        import numpy as _np  # type: ignore
        if isinstance(x, _np.generic):
            if _np.isnan(x):
                return None
            return x.item()
    except Exception:
        pass
    try:
        import pandas as _pd  # type: ignore
        if isinstance(x, _pd.Timestamp):
            return x.isoformat()
        if _pd.isna(x):
            return None
    except Exception:
        pass
    try:
        from decimal import Decimal as _Dec
        if isinstance(x, _Dec):
            return float(x)
    except Exception:
        pass
    if isinstance(x, Number):
        return x
    return x

def _json_sanitize(obj):
    if isinstance(obj, dict):
        return { k: _json_sanitize(v) for k, v in obj.items() }
    if isinstance(obj, list):
        return [ _json_sanitize(v) for v in obj ]
    return _coerce_number(obj)

# Removed _safe_decimal - using shared safe_decimal_conversion from utils.stock_data

def update_proxy_list(proxy_file):
    """Update proxy list by running the proxy scraper"""
    try:
        logger.info("Updating proxy list from scraper...")
        # Check if proxy scraper exists
        scraper_path = os.path.join(os.path.dirname(__file__), 'proxy_scraper_validator.py')
        if os.path.exists(scraper_path):
            # Run proxy scraper with validation
            cmd = [sys.executable, scraper_path, '-threads', '50', '-timeout', '5', '-output', proxy_file]
            logger.info(f"Running proxy scraper: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info("Proxy scraper completed successfully")
                # Check output for statistics
                for line in result.stdout.split('\n'):
                    if 'Working:' in line or 'Success Rate:' in line:
                        logger.info(f"  {line.strip()}")
            else:
                logger.warning(f"Proxy scraper failed: {result.stderr}")
        else:
            logger.warning(f"Proxy scraper not found at {scraper_path}")
    except subprocess.TimeoutExpired:
        logger.error("Proxy scraper timed out after 5 minutes")
    except Exception as e:
        logger.error(f"Error updating proxy list: {e}")

def load_proxies_direct(proxy_file):
    """Load proxies directly from JSON file without validation"""
    try:
        # First check if we need to update proxies (older than 1 hour)
        if os.path.exists(proxy_file):
            file_age = time.time() - os.path.getmtime(proxy_file)
            if file_age > 3600:  # Older than 1 hour
                logger.info(f"Proxy file is {file_age/3600:.1f} hours old, updating...")
                update_proxy_list(proxy_file)
        else:
            logger.info("No proxy file found, scraping new proxies...")
            update_proxy_list(proxy_file)
        
        with open(proxy_file, 'r') as f:
            proxy_data = json.load(f)
        
        # Extract proxy list from the JSON structure
        if isinstance(proxy_data, dict):
            # Try different possible keys
            if 'proxies' in proxy_data:
                proxies = proxy_data['proxies']
            elif 'working_proxies' in proxy_data:
                proxies = proxy_data['working_proxies']
            else:
                # Assume the entire dict is the proxy list
                proxies = list(proxy_data.values()) if proxy_data else []
        elif isinstance(proxy_data, list):
            proxies = proxy_data
        else:
            proxies = []
        
        # Normalize and filter
        normalized = []
        for p in proxies:
            np = normalize_proxy_string(p) if isinstance(p, str) else None
            if np:
                normalized.append(np)
        # De-dupe while preserving order
        seen = set()
        deduped = []
        for p in normalized:
            if p not in seen:
                seen.add(p)
                deduped.append(p)
        logger.info(f"Loaded {len(deduped)} proxies directly from {proxy_file}")
        return deduped
        
    except FileNotFoundError:
        logger.warning(f"Proxy file not found: {proxy_file}")
        logger.info("Attempting to scrape new proxies...")
        update_proxy_list(proxy_file)
        # Try loading again
        try:
            with open(proxy_file, 'r') as f:
                proxies = json.load(f)
                if isinstance(proxies, list):
                    return [normalize_proxy_string(p) for p in proxies if normalize_proxy_string(p)]
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to reload proxy file after scraping: {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading proxies: {e}")
        return []

def get_healthy_proxy(proxies, used_proxies=None):
    """Get a healthy proxy, avoiding blocked ones"""
    if not proxies:
        return None
    
    if used_proxies is None:
        used_proxies = set()
    
    current_time = datetime.now()
    healthy_proxies = []
    
    for proxy in proxies:
        if proxy in used_proxies:
            continue
            
        with proxy_health_lock:
            health = proxy_health[proxy]
            
            # Check if proxy is blocked and cooldown period has passed
            if health["blocked"]:
                if health["last_failure"] and (current_time - health["last_failure"]).total_seconds() > proxy_retry_cooldown:
                    health["blocked"] = False
                    health["failures"] = 0
                    logger.info(f"Proxy {proxy} cooldown expired, marking as available")
                else:
                    continue
        
        healthy_proxies.append(proxy)
    
    if not healthy_proxies:
        # If no healthy proxies, return a random one (last resort)
        return random.choice(proxies) if proxies else None
    
    # Prefer proxies with fewer failures
    with proxy_health_lock:
        healthy_proxies.sort(key=lambda p: proxy_health[p]["failures"])
    return healthy_proxies[0]

def mark_proxy_success(proxy):
    """Mark a proxy as successful"""
    if proxy:
        with proxy_health_lock:
            proxy_health[proxy]["successes"] += 1
            proxy_health[proxy]["failures"] = 0  # Reset failure count on success
            proxy_health[proxy]["blocked"] = False

def mark_proxy_failure(proxy, reason=""):
    """Mark a proxy as failed"""
    if not proxy:
        return
    
    with proxy_health_lock:
        health = proxy_health[proxy]
        health["failures"] += 1
        health["last_failure"] = datetime.now()
        
        if health["failures"] >= proxy_failure_threshold:
            health["blocked"] = True
            logger.warning(f"Proxy {proxy} marked as blocked after {health['failures']} failures. Reason: {reason}")

# Removed _extract_pe_ratio and _extract_dividend_yield - using shared utilities from utils.stock_data

# Using shared load_nyse_symbols_from_csv from utils.stock_data
def load_nyse_symbols(csv_file, test_mode=False, max_symbols=None):
    """Load NYSE symbols from CSV file, filtering delisted stocks - wrapper for shared utility"""
    return load_nyse_symbols_from_csv(csv_file, test_mode, max_symbols)

def load_combined_symbols(combined_file: str | None = None, test_mode: bool = False, max_symbols: int | None = None) -> list[str]:
    """Load combined tickers list from Django/data/combined/combined_tickers_*.py.

    If combined_file is None, auto-select the most recent combined file.
    """
    try:
        combined_dir = Path(__file__).resolve().parent / 'data' / 'combined'
        target_path: Path | None = None
        if combined_file:
            p = Path(combined_file)
            target_path = p if p.exists() else None
        if target_path is None:
            if not combined_dir.exists():
                logger.error(f"Combined tickers directory not found: {combined_dir}")
                return []
            candidates = sorted(combined_dir.glob('combined_tickers_*.py'), key=lambda fp: fp.stat().st_mtime, reverse=True)
            if not candidates:
                logger.error(f"No combined_tickers_*.py files found in {combined_dir}")
                return []
            target_path = candidates[0]

        spec = importlib.util.spec_from_file_location('combined_tickers_module', str(target_path))
        if not spec or not spec.loader:
            logger.error(f"Failed to prepare import for {target_path}")
            return []
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        symbols = list(getattr(module, 'COMBINED_TICKERS', []))
        if not symbols:
            logger.error(f"COMBINED_TICKERS not found in {target_path}")
            return []
        # Normalize, de-dupe, and optionally trim
        seen = set()
        out: list[str] = []
        for s in symbols:
            us = str(s).strip().upper()
            if us and us not in seen:
                seen.add(us)
                out.append(us)
        if test_mode and len(out) > 100:
            out = out[:100]
        if max_symbols and len(out) > max_symbols:
            out = out[:max_symbols]
        logger.info(f"Loaded {len(out)} combined tickers from {target_path.name}")
        return out
    except Exception as e:
        logger.error(f"Failed to load combined symbols: {e}")
        return []

def process_symbol_with_retry(symbol, ticker_number, proxy_manager_or_list, timeout=10, test_mode=False, save_to_db=True, max_retries=3):
    """Process a single symbol with retry logic using a ProxyManager for unique leases."""
    global shutdown_flag
    
    if shutdown_flag:
        return None
    
    used_proxies = set()
    last_error = None
    
    for attempt in range(max_retries):
        if shutdown_flag:
            return None
            
        try:
            # Lease a unique healthy proxy
            proxy = None
            if proxy_manager_or_list:
                if isinstance(proxy_manager_or_list, ProxyManager):
                    # Wait briefly for a proxy to avoid falling back to direct IP
                    proxy = proxy_manager_or_list.lease_proxy(exclude=used_proxies, wait=True, timeout=1.0)
                else:
                    # Backward compatibility with list of proxies
                    proxy = get_healthy_proxy(proxy_manager_or_list, used_proxies)
            # If proxying is enabled but none available, wait a bit and retry
            if proxy_manager_or_list and not proxy:
                time.sleep(random.uniform(0.08, 0.18))
                continue
            if proxy:
                used_proxies.add(proxy)
                if ticker_number <= 5 or attempt > 0:  # Show proxy info for first 5 tickers or retries
                    logger.info(f"{symbol} (attempt {attempt + 1}): Using proxy {proxy}")
            
            result = process_symbol_attempt(symbol, proxy, timeout, test_mode, save_to_db)
            
            if result is not None:
                # Success - mark proxy as working
                if proxy:
                    mark_proxy_success(proxy)
                    if isinstance(proxy_manager_or_list, ProxyManager):
                        proxy_manager_or_list.release_proxy(proxy)
                return result
            else:
                # No data but no error - might be legitimate (delisted stock)
                if proxy:
                    mark_proxy_success(proxy)  # Don't penalize proxy for legitimate no-data
                    if isinstance(proxy_manager_or_list, ProxyManager):
                        proxy_manager_or_list.release_proxy(proxy)
                return None
                
        except Exception as e:
            last_error = e
            if proxy:
                error_msg = str(e).lower()
                
                # Check if it's a proxy-related error
                if any(keyword in error_msg for keyword in ['timeout', 'connection', 'proxy', 'network', 'ssl', 'timed out']):
                    mark_proxy_failure(proxy, str(e))
                    logger.warning(f"{symbol} (attempt {attempt + 1}): Proxy error with {proxy}: {e}")
                    if isinstance(proxy_manager_or_list, ProxyManager):
                        proxy_manager_or_list.release_proxy(proxy)
                    
                    # Add small delay before retry
                    time.sleep(random.uniform(0.1, 0.3))
                    continue
                else:
                    # Non-proxy error, might be legitimate (delisted stock, etc.)
                    mark_proxy_success(proxy)  # Don't penalize proxy
                    logger.warning(f"{symbol}: Non-proxy error: {e}")
                    if isinstance(proxy_manager_or_list, ProxyManager):
                        proxy_manager_or_list.release_proxy(proxy)
                    return None
            else:
                logger.warning(f"{symbol}: Error without proxy: {e}")
                return None
    
    # All retries failed
    logger.error(f"{symbol}: All {max_retries} attempts failed. Last error: {last_error}")
    return None

def process_symbol_attempt(symbol, proxy, timeout=10, test_mode=False, save_to_db=True):
    """Single attempt to process a symbol"""
    # Minimal delay to avoid rate limiting
    time.sleep(random.uniform(0.01, 0.02))

    def yfinance_retry_wrapper(func, max_attempts=3, backoff_factor=0.5):
        """Wrapper to add retry logic with exponential backoff to yfinance calls"""
        for attempt in range(max_attempts):
            try:
                return func()
            except Exception as e:
                if attempt == max_attempts - 1:  # Last attempt
                    if any(keyword in str(e).lower() for keyword in ['timeout', 'connection', 'proxy', 'ssl']):
                        raise
                    return None
                # Exponential backoff
                sleep_time = backoff_factor * (2 ** attempt)
                time.sleep(sleep_time)
        return None

    # Build a per-attempt session (with proxy if provided) and pass to yfinance
    session = create_session_for_proxy(proxy, timeout)

    # Filter out symbols with obvious invalid characters that yfinance rejects
    if any(ch in symbol for ch in ['$', '^', ' ', '/']):
        logger.warning(f"{symbol}: Skipping invalid or preferred share ticker format")
        return None

    # Try multiple approaches to get data letting yfinance manage its own session
    # Normalize special share classes: replace '.' with '-' (e.g., BRK.B -> BRK-B)
    norm_symbol = symbol.replace('.', '-')
    ticker_obj = yf.Ticker(norm_symbol, session=session)
    info = None
    hist = None
    current_price = None
    earnings_trend = None

    # Approach 1: Try fast_info first for speed, then fall back to full info with retry
    info = None
    
    # Try fast_info with retry - it's faster and has key price/market cap data
    fast_info = yfinance_retry_wrapper(lambda: ticker_obj.fast_info)
    if fast_info and hasattr(fast_info, 'last_price') and fast_info.last_price:
        current_price = fast_info.last_price
    
    # Try full info with retry if we need more comprehensive data
    if fast_info is None or not hasattr(fast_info, 'market_cap') or not fast_info.market_cap:
        info = yfinance_retry_wrapper(lambda: ticker_obj.info)
        if info and len(info) <= 3:
            info = None

    # Helper: history with fallback if yfinance doesn't accept timeout kwarg
    def yf_history(period=None, interval=None):
        def _call():
            try:
                if interval is None:
                    return ticker_obj.history(period=period, timeout=timeout)
                return ticker_obj.history(period=period, interval=interval, timeout=timeout)
            except TypeError:
                # Some versions of yfinance don't support timeout kwarg
                if interval is None:
                    return ticker_obj.history(period=period)
                return ticker_obj.history(period=period, interval=interval)
        return yfinance_retry_wrapper(_call)

    # Approach 2: Try to get historical data with multiple periods using retry
    # Start with longer periods for better price change calculations
    for period in ["1y", "6mo", "3mo", "1mo", "5d", "1d"]:
        hist = yf_history(period=period)
        if hist is not None and not hist.empty and len(hist) > 0:
            try:
                current_price = hist['Close'].iloc[-1]
                if current_price is not None and not pd.isna(current_price):
                    break
            except (KeyError, IndexError, ValueError) as e:
                logger.debug(f"Failed to extract price from history for {symbol}: {e}")
                continue

    # Approach 3: Try to get current price from info if historical failed
    if current_price is None and info:
        try:
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('regularMarketOpen')
        except Exception:
            pass

    # As last resort, attempt '1d' with interval to get a recent close
    if current_price is None:
        try:
            intraday = yf_history(period="1d", interval="1m")
            if intraday is not None and not intraday.empty:
                current_price = intraday['Close'].dropna().iloc[-1]
        except Exception:
            pass

    # Try to fetch earnings trend for forward EPS and growth
    try:
        earnings_trend = yfinance_retry_wrapper(lambda: ticker_obj.get_earnings_trend())
    except Exception:
        earnings_trend = None

    # Determine if we have enough data to process
    has_data = hist is not None and not hist.empty
    has_info = info and isinstance(info, dict) and len(info) > 3
    has_fast_info = fast_info is not None
    has_price = current_price is not None and not pd.isna(current_price)

    # Check for delisted or invalid stocks
    if info and info.get('quoteType') == 'NONE':
        logger.warning(f"{symbol}: possibly delisted; no price data found (period=1d)")
        return None

    if not has_data and not has_info and not has_fast_info:
        logger.warning(f"{symbol}: No data available")
        return None

    if not has_price and info and info.get('volume', 0) == 0:
        logger.warning(f"{symbol}: No current trading activity")
        return None

    # Extract comprehensive stock data using utility functions
    base_data = extract_stock_data_from_info(info, symbol, current_price) if info else extract_stock_data_from_fast_info(fast_info, symbol, current_price)
    
    # Calculate price changes from historical data (prefer intraday 1m when available for accuracy)
    price_change_today, change_percent = (None, None)
    try:
        intraday_close_prev = None
        intraday_close_curr = None
        intraday = yf_history(period="1d", interval="1m")
        if intraday is not None and not intraday.empty and len(intraday) >= 2:
            closes = intraday['Close'].dropna()
            if len(closes) >= 2:
                intraday_close_prev = closes.iloc[-2]
                intraday_close_curr = closes.iloc[-1]
        if intraday_close_prev is not None and intraday_close_curr is not None and intraday_close_prev != 0:
            price_change_today = safe_decimal_conversion(intraday_close_curr - intraday_close_prev)
            change_percent = safe_decimal_conversion(((intraday_close_curr - intraday_close_prev) / intraday_close_prev) * 100)
    except Exception:
        price_change_today, change_percent = (None, None)
    if price_change_today is None or change_percent is None:
        price_change_today, change_percent = calculate_change_percent_from_history(hist, symbol) if hist is not None and not hist.empty else (None, None)
    # Fallback to info-provided change metrics if history unavailable
    if (price_change_today is None or change_percent is None) and info:
        try:
            if price_change_today is None:
                price_change_today = safe_decimal_conversion(info.get('regularMarketChange') or info.get('priceHint'))
            if change_percent is None:
                cp = info.get('regularMarketChangePercent')
                if cp is not None:
                    change_percent = safe_decimal_conversion(cp)
        except Exception:
            pass
    
    # Calculate additional metrics
    # Ensure avg_volume_3mon fallback before DVAV
    if (not base_data.get('avg_volume_3mon')) and base_data.get('volume'):
        base_data['avg_volume_3mon'] = base_data['volume']
    dvav = calculate_volume_ratio(base_data.get('volume'), base_data.get('avg_volume_3mon'))
    
    # Extract bid/ask data
    bid_price = safe_decimal_conversion(info.get('bid')) if info else None
    ask_price = safe_decimal_conversion(info.get('ask')) if info else None
    bid_ask_spread = safe_decimal_conversion(float(ask_price) - float(bid_price)) if bid_price and ask_price else None
    
    # Calculate days range
    days_low = base_data.get('days_low')
    days_high = base_data.get('days_high')
    def _fmt2(x):
        try:
            xv = float(x)
            return f"{xv:.2f}"
        except Exception:
            return str(x) if x is not None else ""
    days_range = f"{_fmt2(days_low)} - {_fmt2(days_high)}" if days_low and days_high else ""
    
    # Extract shares outstanding
    # Prefer extracted shares_outstanding from base_data; otherwise fallback to info
    shares_available = base_data.get('shares_outstanding')
    if shares_available is None and info:
        shares_available = safe_decimal_conversion(info.get('sharesOutstanding'))
    
    # Try to get year-over-year price change from 1-year historical data
    price_change_year = None
    try:
        if hist is not None and not hist.empty and len(hist) >= 252:  # Approx 1 year of trading days
            year_ago_price = hist['Close'].iloc[0] if len(hist) > 252 else hist['Close'].iloc[0]
            if current_price and year_ago_price:
                price_change_year = safe_decimal_conversion(current_price - year_ago_price)
    except (IndexError, KeyError, TypeError):
        pass
    
    # Calculate week and month changes from historical data
    price_change_week = None
    price_change_month = None
    try:
        if hist is not None and not hist.empty:
            if len(hist) >= 5:  # At least 5 days for weekly
                week_ago_price = hist['Close'].iloc[-5] if len(hist) >= 5 else hist['Close'].iloc[0]
                if current_price and week_ago_price:
                    price_change_week = safe_decimal_conversion(current_price - week_ago_price)
            
            if len(hist) >= 22:  # At least 22 days for monthly
                month_ago_price = hist['Close'].iloc[-22] if len(hist) >= 22 else hist['Close'].iloc[0]
                if current_price and month_ago_price:
                    price_change_month = safe_decimal_conversion(current_price - month_ago_price)
    except (IndexError, KeyError, TypeError):
        pass

    # Compute market cap fallback if missing
    mc_value = base_data.get('market_cap')
    try:
        if mc_value is None or mc_value == 0:
            mc_fb = compute_market_cap_fallback(current_price, shares_available)
            if mc_fb:
                mc_value = mc_fb
    except Exception:
        pass

    # Build comprehensive stock data
    stock_data = {
        **base_data,  # Start with extracted data from utility functions
        'price_change_today': price_change_today,
        'price_change_week': price_change_week,
        'price_change_month': price_change_month,
        'price_change_year': price_change_year,
        'change_percent': change_percent,
        'bid_price': bid_price,
        'ask_price': ask_price,
        'bid_ask_spread': str(bid_ask_spread) if bid_ask_spread else '',
        'days_range': days_range,
        'dvav': dvav,
        'shares_available': shares_available,
        'market_cap': mc_value if mc_value is not None else base_data.get('market_cap'),
        'market_cap_change_3mon': None,  # Would need 3-month historical market cap data
        'pe_change_3mon': None,  # Would need 3-month historical PE data
        # Calculate basic price_change and price_change_percent for model compatibility
        'price_change': price_change_today,
        'price_change_percent': change_percent,
        'last_updated': now_ts(),
        'created_at': now_ts()
    }

    # Fill price_to_book if not present and book_value + current_price available
    try:
        if not stock_data.get('price_to_book') and stock_data.get('book_value') and stock_data.get('current_price'):
            bv = float(stock_data['book_value'])
            cp = float(stock_data['current_price'])
            if bv > 0:
                stock_data['price_to_book'] = safe_decimal_conversion(cp / bv)
    except Exception:
        pass

    # Fill P/E ratio if missing using current price and EPS
    try:
        pe_val = stock_data.get('pe_ratio')
        eps_val = stock_data.get('earnings_per_share')
        cp_val = stock_data.get('current_price')
        if (pe_val in (None, 0)) and (eps_val not in (None, 0)) and (cp_val not in (None, 0)):
            epsf = float(eps_val)
            cpf = float(cp_val)
            if epsf and epsf > 0:
                stock_data['pe_ratio'] = safe_decimal_conversion(cpf / epsf)
    except Exception:
        pass

    # If critical valuation fields are missing, try fetching full info now
    try:
        need_full_info = (
            not has_info or
            (info and not isinstance(info, dict)) or
            (info and len(info) <= 3) or
            not base_data.get('earnings_per_share')
        )
        if need_full_info:
            info2 = yfinance_retry_wrapper(lambda: ticker_obj.info)
            if info2 and isinstance(info2, dict) and len(info2) > 3:
                info = info2
                has_info = True
                # Refresh base_data preferentially with richer info
                base_data = extract_stock_data_from_info(info, symbol, current_price)
    except Exception:
        pass

    # =========================
    # Valuation & Technicals (MVP)
    # - Forward EPS & PE
    # - Sector subsector PE mapping (restricted fair value)
    # - Company forward PE × EPS (unrestricted fair value)
    # - Analyst target mean price
    # - RSI(14)
    # =========================

    def _safe_float(x):
        try:
            return float(x) if x is not None and not pd.isna(x) else None
        except Exception:
            return None

    # Forward EPS (multi-source with robust parsing)
    forward_eps = None
    try:
        # 1) Direct from info
        if info:
            forward_eps = _safe_float(info.get('forwardEps'))
        # 2) Parse from earnings_trend DataFrame (nextYear avg or epsTrend current)
        if forward_eps is None and earnings_trend is not None:
            try:
                import pandas as _pd  # local import guard
                if hasattr(earnings_trend, 'to_dict'):
                    # Orient records to iterate rows safely across versions
                    rows = earnings_trend.to_dict(orient='records')
                    candidates = []
                    for row in rows:
                        period = (row.get('period') or row.get('endDate') or '').lower()
                        # Prefer next year estimates
                        is_next_year = any(key in period for key in ['next', '+1y', '1y'])
                        ee = row.get('earningsEstimate') or {}
                        et = row.get('epsTrend') or {}
                        # Try earningsEstimate.avg first
                        avg_est = ee.get('avg') if isinstance(ee, dict) else None
                        if avg_est is not None:
                            candidates.append((2 if is_next_year else 1, _safe_float(avg_est)))
                        # Try epsTrend.current as a weaker signal
                        current_est = et.get('current') if isinstance(et, dict) else None
                        if current_est is not None:
                            candidates.append((1 if is_next_year else 0, _safe_float(current_est)))
                    # Pick best candidate by priority then value presence
                    candidates = [c for c in candidates if c[1] is not None and c[1] > 0]
                    if candidates:
                        candidates.sort(key=lambda x: (-x[0]))
                        forward_eps = candidates[0][1]
            except Exception as _e:
                logger.debug(f"{symbol}: Failed to parse earnings_trend for forward EPS: {_e}")
        # 3) Fallback: use earnings_per_share from base_data (may be trailing)
        if forward_eps is None:
            forward_eps = _safe_float(base_data.get('earnings_per_share'))
    except Exception as _e:
        logger.debug(f"{symbol}: Forward EPS extraction error: {_e}")

    # Forward PE
    forward_pe = None
    try:
        if fast_info is not None and hasattr(fast_info, 'forward_pe') and getattr(fast_info, 'forward_pe'):
            forward_pe = _safe_float(getattr(fast_info, 'forward_pe'))
        if forward_pe is None and info:
            forward_pe = _safe_float(info.get('forwardPE'))
        if forward_pe is None and forward_eps and current_price:
            # Compute from price / forward EPS
            try:
                cpf = float(current_price)
                if forward_eps and forward_eps > 0:
                    forward_pe = round(cpf / float(forward_eps), 2)
            except Exception:
                pass
        if forward_pe is None and info:
            # As last resort use trailing PE
            forward_pe = _safe_float(info.get('trailingPE'))
    except Exception:
        pass

    # Sector/Industry and mapping to subsector multiples
    sector = None
    industry = None
    if info:
        sector = info.get('sector') or None
        industry = info.get('industry') or None

    SECTOR_PE_MULTIPLES = {
        'Technology': {'low': 15.0, 'base': 22.0, 'high': 30.0},
        'Information Technology': {'low': 15.0, 'base': 22.0, 'high': 30.0},
        'Consumer Discretionary': {'low': 12.0, 'base': 18.0, 'high': 24.0},
        'Consumer Staples': {'low': 12.0, 'base': 17.0, 'high': 22.0},
        'Health Care': {'low': 12.0, 'base': 18.0, 'high': 25.0},
        'Healthcare': {'low': 12.0, 'base': 18.0, 'high': 25.0},
        'Financials': {'low': 8.0, 'base': 12.0, 'high': 16.0},
        'Industrials': {'low': 10.0, 'base': 16.0, 'high': 20.0},
        'Energy': {'low': 6.0, 'base': 9.0, 'high': 12.0},
        'Utilities': {'low': 10.0, 'base': 15.0, 'high': 18.0},
        'Real Estate': {'low': 12.0, 'base': 16.0, 'high': 20.0},
        'Materials': {'low': 9.0, 'base': 13.0, 'high': 17.0},
        'Communication Services': {'low': 12.0, 'base': 18.0, 'high': 24.0},
    }
    default_multiples = {'low': 10.0, 'base': 15.0, 'high': 20.0}
    multiples = SECTOR_PE_MULTIPLES.get(sector or '', default_multiples)

    # Fair values
    fv_restricted = {'low': None, 'base': None, 'high': None}
    fv_unrestricted = None
    if forward_eps and forward_eps > 0:
        try:
            fv_restricted = {
                'low': round(multiples['low'] * forward_eps, 2),
                'base': round(multiples['base'] * forward_eps, 2),
                'high': round(multiples['high'] * forward_eps, 2),
            }
        except Exception:
            pass
        if forward_pe and forward_pe > 0:
            try:
                fv_unrestricted = round(forward_pe * forward_eps, 2)
            except Exception:
                fv_unrestricted = None

    # Analyst target
    analyst_target = None
    try:
        if info:
            analyst_target = _safe_float(info.get('targetMeanPrice'))
    except Exception:
        pass

    # RSI(14)
    rsi14 = None
    try:
        # Use existing hist if available; otherwise fetch a month of daily data
        hist_for_rsi = None
        if hist is not None and not hist.empty and len(hist) >= 15:
            hist_for_rsi = hist
        else:
            hist_for_rsi = yf_history(period="1mo", interval="1d")
        if hist_for_rsi is not None and not hist_for_rsi.empty:
            closes = hist_for_rsi['Close'].dropna()
            if len(closes) >= 15:
                delta = closes.diff()
                gain = delta.where(delta > 0, 0.0)
                loss = -delta.where(delta < 0, 0.0)
                roll_up = gain.rolling(window=14, min_periods=14).mean()
                roll_down = loss.rolling(window=14, min_periods=14).mean()
                rs = roll_up / roll_down
                rsi = 100.0 - (100.0 / (1.0 + rs))
                rsi14 = round(float(rsi.iloc[-1]), 2)
    except Exception:
        rsi14 = None

    # VWAP (intraday 1m for current trading day)
    vwap_val = None
    try:
        intraday_for_vwap = yfinance_retry_wrapper(lambda: ticker_obj.history(period="1d", interval="1m", timeout=timeout))
        if intraday_for_vwap is not None and not intraday_for_vwap.empty:
            df = intraday_for_vwap.dropna(subset=['High', 'Low', 'Close', 'Volume']).copy()
            if not df.empty and df['Volume'].sum() > 0:
                typical_price = (df['High'] + df['Low'] + df['Close']) / 3.0
                vwap_calc = (typical_price * df['Volume']).sum() / df['Volume'].sum()
                vwap_val = round(float(vwap_calc), 4)
    except Exception:
        vwap_val = None

    valuation_payload = {
        'forward_eps': forward_eps,
        'forward_pe': forward_pe,
        'sector': sector,
        'industry': industry,
        'subsector_pe_low': multiples['low'],
        'subsector_pe_base': multiples['base'],
        'subsector_pe_high': multiples['high'],
        'fair_value_restricted': fv_restricted,
        'fair_value_unrestricted': fv_unrestricted,
        'analyst_target': analyst_target,
        'rsi14': rsi14,
        'vwap': vwap_val,
    }

    # Attach to returned payload for non-DB flows (test/export); ensure DB save ignores it
    stock_data['valuation'] = valuation_payload

    # Remove transient fields not present in DB schema
    stock_data.pop('shares_outstanding', None)

    # Best-effort fill avg_volume_3mon when missing using volume_today/volume
    if not stock_data.get('avg_volume_3mon') and stock_data.get('volume'):
        stock_data['avg_volume_3mon'] = stock_data['volume']

    try:
        if save_to_db and not test_mode:
            ensure_django_initialized()
            if not DJANGO_READY:
                logger.error("Skipping DB save: Django not initialized")
                return stock_data
            # Serialize DB writes to avoid SQLite lock errors
            with db_write_lock:
                # Prepare defaults: store valuation in JSON field
                db_defaults = dict(stock_data)
                db_defaults.pop('valuation', None)
                try:
                    db_defaults['valuation_json'] = valuation_payload
                except Exception:
                    pass
                stock, created = Stock.objects.update_or_create(
                    ticker=symbol,
                    defaults=db_defaults
                )
                if stock_data.get('current_price'):
                    try:
                        StockPrice.objects.create(stock=stock, price=stock_data['current_price'])
                    except Exception as e:
                        logger.debug(f"Failed to create StockPrice for {symbol}: {e}")
        return stock_data if not save_to_db or test_mode else stock_data
    except Exception as e:
        logger.error(f"DB ERROR {symbol}: {e}")
        raise

# Create an alias for backward compatibility
def process_symbol(symbol, ticker_number, proxies, timeout=10, test_mode=False, save_to_db=True):
    """Backward compatibility wrapper"""
    return process_symbol_with_retry(symbol, ticker_number, proxies, timeout, test_mode, save_to_db)

def run_stock_update(args):
    """Run a single stock update cycle"""
    global shutdown_flag
    
    logger.info(f"{'='*60}")
    logger.info(f"STOCK UPDATE CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'='*60}")

    # Hard guard: run ONLY during regular market hours (weekdays 09:30–16:00 ET)
    now_et = datetime.now(EASTERN_TZ)
    current_hhmm = now_et.strftime("%H:%M")
    if not getattr(args, 'ignore_market_hours', False):
        if now_et.weekday() >= 5 or not (MARKET_OPEN <= current_hhmm < MARKET_CLOSE):
            logger.info(
                f"Skipping stock update cycle outside regular hours at "
                f"{now_et.strftime('%Y-%m-%d %H:%M:%S %Z')} (allowed {MARKET_OPEN}-{MARKET_CLOSE} ET)"
            )
            return
    
    # Load symbols (prefer combined tickers when available)
    use_combined = bool(getattr(args, 'combined', False) or os.environ.get('USE_COMBINED_TICKERS', '').lower() == 'true')
    if not use_combined:
        try:
            combined_dir = Path(__file__).resolve().parent / 'data' / 'combined'
            if combined_dir.exists() and any(combined_dir.glob('combined_tickers_*.py')):
                logger.info("Detected combined tickers file. Defaulting to combined (NASDAQ + NYSE/AMEX).")
                use_combined = True
        except Exception:
            pass
    if use_combined:
        logger.info("Loading combined tickers list (NASDAQ + NYSE/AMEX)...")
        symbols = load_combined_symbols(getattr(args, 'combined_file', None), args.test, args.max_symbols)
    else:
        logger.info(f"Loading NYSE symbols from {args.csv}...")
        symbols = load_nyse_symbols(args.csv, args.test, args.max_symbols)
    
    if not symbols:
        logger.error("No symbols loaded. Skipping cycle.")
        return
    
    logger.info(f"Processing {len(symbols)} symbols...")
    
    # Load proxies directly (without validation)
    proxies = []
    if not args.noproxy:
        logger.info(f"Loading proxies from {args.proxy_file}...")
        proxies = load_proxies_direct(args.proxy_file)
        if proxies:
            logger.info(f"SUCCESS: Loaded {len(proxies)} proxies (no validation)")
        else:
            logger.warning("No proxies loaded - continuing without proxies")
    else:
        logger.info("DISABLED: Proxy usage disabled")
    # Initialize proxy manager for unique leasing across threads
    proxy_manager = ProxyManager(proxies) if (proxies and not args.noproxy) else None
    
    # Process stocks
    logger.info(f"Starting to process {len(symbols)} symbols...")
    logger.info("=" * 60)
    
    start_time = time.time()
    successful = 0
    failed = 0
    results = []
    
    # Use ThreadPoolExecutor for parallel processing with better timeout handling
    logger.info(f"Submitting {len(symbols)} tasks to thread pool...")
    
    try:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            future_to_symbol = {}
            ticker_count_since_refresh = 0
            refresh_every = 100
            for i, symbol in enumerate(symbols, 1):
                if shutdown_flag:
                    break
                # Refresh proxies every N tickers processed (submission-time refresh)
                if proxy_manager and ticker_count_since_refresh >= refresh_every:
                    try:
                        logger.info(f"Refreshing proxies after {ticker_count_since_refresh} tickers...")
                        updated = load_proxies_direct(args.proxy_file)
                        proxy_manager.refresh_proxies(updated)
                        ticker_count_since_refresh = 0
                        logger.info(f"Proxy list refreshed: {len(updated)} proxies available")
                    except Exception as _e:
                        logger.warning(f"Failed to refresh proxies: {_e}")
                future = executor.submit(process_symbol_with_retry, symbol, i, proxy_manager or proxies, args.timeout, args.test, args.save_to_db)
                future_to_symbol[future] = symbol
                ticker_count_since_refresh += 1
            
            logger.info(f"Submitted {len(future_to_symbol)} tasks. Processing...")
            completed = 0
            
            for future in as_completed(future_to_symbol):
                if shutdown_flag:
                    logger.info("Shutdown requested. Cancelling remaining tasks...")
                    break
                    
                symbol = future_to_symbol[future]
                completed += 1
                
                try:
                    # Use shorter timeout for individual tasks
                    result = future.result(timeout=args.timeout + 2)
                    if result:
                        successful += 1
                        results.append(result)
                    else:
                        failed += 1
                except TimeoutError:
                    logger.error(f"TIMEOUT {symbol}: Task timed out")
                    failed += 1
                except Exception as e:
                    logger.error(f"ERROR {symbol}: {e}")
                    failed += 1
                
                # Show progress every 10 completed or at the end
                if completed % 10 == 0 or completed == len(symbols):
                    logger.info(f"[PROGRESS] {completed}/{len(symbols)} completed ({successful} successful, {failed} failed)")
                    
                # Add a small delay to prevent overwhelming
                time.sleep(0.01)
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user. Shutting down gracefully...")
        shutdown_flag = True
    except Exception as e:
        logger.error(f"Thread pool execution failed: {e}")
    
    elapsed = time.time() - start_time
    
    # Results
    logger.info("=" * 60)
    logger.info("CYCLE RESULTS")
    logger.info("=" * 60)
    logger.info(f"SUCCESSFUL: {successful}")
    logger.info(f"FAILED: {failed}")
    if len(symbols) > 0:
        logger.info(f"SUCCESS RATE: {(successful/len(symbols)*100):.1f}%")
    logger.info(f"TIME: {elapsed:.2f}s")
    if elapsed > 0:
        logger.info(f"RATE: {len(symbols)/elapsed:.2f} symbols/sec")
    
    if proxies:
        logger.info(f"PROXY STATS: Used {len(proxies)} proxies")
        
        # Show proxy health summary
        healthy_count = 0
        blocked_count = 0
        total_failures = 0
        total_successes = 0
        
        with proxy_health_lock:
            for proxy in proxies:
                health = proxy_health[proxy]
                if health["blocked"]:
                    blocked_count += 1
                else:
                    healthy_count += 1
                total_failures += health["failures"]
                total_successes += health["successes"]
        
        logger.info(f"PROXY HEALTH: {healthy_count} healthy, {blocked_count} blocked")
        if total_successes + total_failures > 0:
            success_rate = (total_successes / (total_successes + total_failures)) * 100
            logger.info(f"PROXY SUCCESS RATE: {success_rate:.1f}% ({total_successes} successes, {total_failures} failures)")
    
    if args.save_to_db and not args.test:
        logger.info(f"DATABASE: Saved {successful} stocks to database")
    
    logger.info(f"CYCLE COMPLETED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # Optional output file for test/export flows
    try:
        out_path = getattr(args, 'output', None)
        if out_path:
            safe_results = [r for r in results if r]
            with open(out_path, 'w') as f:
                json.dump({ 'success': True, 'count': len(safe_results), 'data': _json_sanitize(safe_results) }, f, default=str)
            logger.info(f"WROTE OUTPUT: {out_path} ({len(safe_results)} records)")
        csv_path = getattr(args, 'output_csv', None)
        if csv_path:
            safe_results = [dict(r) for r in results if r]
            # Drop nested valuation for CSV simplicity
            for rec in safe_results:
                rec.pop('valuation', None)
            # Build header as union of keys
            fieldnames = []
            seen_fields = set()
            for rec in safe_results:
                for k in rec.keys():
                    if k not in seen_fields:
                        seen_fields.add(k)
                        fieldnames.append(k)
            # Ensure deterministic order for common keys
            preferred = [
                'ticker', 'symbol', 'company_name', 'current_price',
                'price_change_today', 'price_change_percent', 'price_change_week', 'price_change_month', 'price_change_year',
                'dvav', 'volume', 'avg_volume_3mon', 'market_cap',
                'bid_price', 'ask_price', 'bid_ask_spread', 'days_range',
                'week_52_low', 'week_52_high', 'one_year_target', 'pe_ratio', 'dividend_yield',
                'last_updated'
            ]
            # Reorder: preferred first, then remaining
            ordered = [k for k in preferred if k in seen_fields] + [k for k in fieldnames if k not in preferred]
            def _to_str(v):
                if v is None:
                    return ''
                try:
                    # pandas timestamp
                    import pandas as _pd  # type: ignore
                    if isinstance(v, _pd.Timestamp):
                        return v.isoformat()
                except Exception:
                    pass
                try:
                    from decimal import Decimal as _Dec
                    if isinstance(v, _Dec):
                        return str(v)
                except Exception:
                    pass
                try:
                    from datetime import datetime as _dt
                    if isinstance(v, _dt):
                        return v.isoformat()
                except Exception:
                    pass
                return str(v)
            # Write CSV
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=ordered)
                writer.writeheader()
                for rec in safe_results:
                    row = {k: _to_str(rec.get(k)) for k in ordered}
                    writer.writerow(row)
            logger.info(f"WROTE CSV: {csv_path} ({len(safe_results)} records)")
    except Exception as e:
        logger.error(f"Failed to write output JSON: {e}")

def _build_subprocess_args(args) -> list[str]:
    """Build argument list to spawn a one-off cycle in a separate process."""
    cmd = [sys.executable, os.path.abspath(__file__)]
    if args.noproxy:
        cmd.append('-noproxy')
    if args.test:
        cmd.append('-test')
    cmd += ['-threads', str(args.threads)]
    cmd += ['-timeout', str(args.timeout)]
    if args.csv:
        cmd += ['-csv', args.csv]
    if args.output:
        cmd += ['-output', args.output]
    if args.max_symbols:
        cmd += ['-max-symbols', str(args.max_symbols)]
    if args.proxy_file:
        cmd += ['-proxy-file', args.proxy_file]
    if args.save_to_db:
        cmd.append('-save-to-db')
    # Do NOT include '-schedule' here; child should run a single cycle and exit
    return cmd

# New helpers to launch companion tasks

def _build_news_subprocess_args() -> list[str]:
    """Build argument list for a single-run news scraping cycle."""
    news_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'news_scraper_with_restart.py'))
    cmd = [sys.executable, news_script]
    # Single run: do not pass -schedule
    # Keep defaults for limit/interval; can be extended later via env or args
    return cmd

def _build_email_subprocess_args() -> list[str]:
    """Build argument list for a single-run email sender cycle."""
    email_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'email_sender_with_restart.py'))
    cmd = [sys.executable, email_script]
    # Single run: do not pass -schedule
    # Keep defaults; can be extended later via env or args
    return cmd

def start_cycle_in_subprocess(args):
    """Start a single stock update cycle in a separate process, returning immediately.
    This allows a new cycle to begin every 3 minutes regardless of the prior run time.
    """
    try:
        cmd = _build_subprocess_args(args)
        logger.info(f"Spawning new stock cycle subprocess: {' '.join(cmd)}")
        subprocess.Popen(cmd)
    except Exception as e:
        logger.error(f"Failed to start subprocess cycle: {e}")

# New: launch all three cycles (stocks, news, email)

def run_daily_update(args):
    """Run daily update at 9 AM with proxy refresh"""
    logger.info("="*60)
    logger.info(f"DAILY 9 AM UPDATE - {datetime.now(EASTERN_TZ).strftime('%Y-%m-%d %H:%M:%S ET')}")
    logger.info("="*60)
    
    # Check if it's a market day
    now_et = datetime.now(EASTERN_TZ)
    if now_et.weekday() >= 5:
        logger.info("Not a market day, skipping update")
        return
    
    # Update proxies first
    if not args.noproxy:
        logger.info("Updating proxy list for daily update...")
        update_proxy_list(args.proxy_file)
    
    # Run stock update
    logger.info("Running stock update cycle...")
    run_stock_update(args)
    
    logger.info("Daily update completed")

def start_all_cycles_in_subprocess(args):
    """Spawn stock, news scraper, and email sender cycles as separate subprocesses."""
    # Only run during regular market hours (weekdays 09:30-16:00 ET)
    now_et = datetime.now(EASTERN_TZ)
    current_hhmm = now_et.strftime("%H:%M")
    if now_et.weekday() >= 5 or not (MARKET_OPEN <= current_hhmm < MARKET_CLOSE):
        logger.info(f"Skipping cycle spawn (outside regular market hours) at {now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        return
    
    # Stocks
    start_cycle_in_subprocess(args)
    # News scraper
    try:
        news_cmd = _build_news_subprocess_args()
        logger.info(f"Spawning news scraper subprocess: {' '.join(news_cmd)}")
        subprocess.Popen(news_cmd)
    except Exception as e:
        logger.error(f"Failed to start news scraper subprocess: {e}")
    # Email sender
    try:
        email_cmd = _build_email_subprocess_args()
        logger.info(f"Spawning email sender subprocess: {' '.join(email_cmd)}")
        subprocess.Popen(email_cmd)
    except Exception as e:
        logger.error(f"Failed to start email sender subprocess: {e}")

def main():
    """Main function"""
    global shutdown_flag
    
    args = parse_arguments()
    
    logger.info("ENHANCED STOCK RETRIEVAL SCRIPT - WORKING VERSION WITH PROXIES")
    logger.info("=" * 60)
    logger.info(f"Configuration:")
    logger.info(f"  CSV File: {args.csv}")
    logger.info(f"  Test Mode: {args.test}")
    logger.info(f"  Use Proxies: {not args.noproxy}")
    logger.info(f"  Proxy File: {args.proxy_file}")
    logger.info(f"  Threads: {args.threads}")
    logger.info(f"  Timeout: {args.timeout}s")
    logger.info(f"  Max Symbols: {args.max_symbols or 'All'}")
    logger.info(f"  Save to DB: {args.save_to_db}")
    logger.info(f"  Schedule Mode: {args.schedule}")
    logger.info(f"  Daily Update: {args.daily_update}")
    logger.info("=" * 60)
    
    # Force proxy update if requested
    if args.update_proxies and not args.noproxy:
        update_proxy_list(args.proxy_file)
    
    # Daily update mode - run at 9 AM ET
    if args.daily_update:
        logger.info("DAILY UPDATE MODE: Running at 9:00 AM ET every market day")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)
        
        # Schedule daily update at 9 AM ET
        schedule.every().day.at("09:00").do(lambda: run_daily_update(args))
        
        # Check if we should run immediately (if after 9 AM)
        now_et = datetime.now(EASTERN_TZ)
        if now_et.hour >= 9 and now_et.weekday() < 5:
            logger.info("Running immediate update (after 9 AM)")
            run_daily_update(args)
        
        try:
            while not shutdown_flag:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Daily updater stopped by user")
            shutdown_flag = True
        return
    
    if args.schedule:
        logger.info("SCHEDULER MODE: Spawning stock, news, and email cycles every 3 minutes (overlap allowed)")
        logger.info("Press Ctrl+C to stop the scheduler")
        logger.info("=" * 60)
        
        # Immediate run of all three
        start_all_cycles_in_subprocess(args)
        # Schedule subsequent runs every 3 minutes
        schedule.every(3).minutes.do(start_all_cycles_in_subprocess, args)
        
        try:
            while True:
                schedule.run_pending()
                
                # Stop scheduler after market close on weekdays
                now_et = datetime.now(EASTERN_TZ)
                current_hhmm = now_et.strftime("%H:%M")
                if now_et.weekday() < 5 and current_hhmm >= MARKET_CLOSE:
                    logger.info(f"Market closed at {now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}. Stopping scheduler.")
                    break
                
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            shutdown_flag = True
    else:
        # Run single update in the current process
        run_stock_update(args)
    
    logger.info("Script completed!")

if __name__ == "__main__":
    main()