import os
import json
import random
import signal
import logging
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urlencode
import pytz
import pandas as pd
import yfinance as yf
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from django.core.management.base import BaseCommand
from django.utils.timezone import now, make_aware
from django.core.cache import cache
from stocks.models import StockAlert

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class TimeoutException(Exception): 
pass

def timeout_handler(signum, frame): 
raise TimeoutException()

signal.signal(signal.SIGALRM, timeout_handler)

@dataclass
class ProxyConfig:
"""Configuration for proxy rotation"""
http: Optional[str] = None
https: Optional[str] = None

class RateLimitManager:
"""Manages rate limiting with exponential backoff"""

def __init__(self, initial_delay: float = 1.0, max_delay: float = 300.0):
self.initial_delay = initial_delay
self.max_delay = max_delay
self.request_times: Dict[str, List[float]] = {}
self.backoff_delays: Dict[str, float] = {}

def can_make_request(self, key: str, max_requests_per_minute: int = 60) -> bool:
"""Check if we can make a request without hitting rate limits"""
current_time = time.time()
minute_ago = current_time - 60

if key not in self.request_times:
self.request_times[key] = []

# Remove old requests
self.request_times[key] = [
req_time for req_time in self.request_times[key] 
if req_time > minute_ago
]

return len(self.request_times[key]) < max_requests_per_minute

def record_request(self, key: str):
"""Record a request timestamp"""
if key not in self.request_times:
self.request_times[key] = []
self.request_times[key].append(time.time())

def get_backoff_delay(self, key: str) -> float:
"""Get current backoff delay for a key"""
return self.backoff_delays.get(key, self.initial_delay)

def increase_backoff(self, key: str):
"""Increase backoff delay for a key"""
current_delay = self.backoff_delays.get(key, self.initial_delay)
self.backoff_delays[key] = min(current_delay * 2, self.max_delay)

def reset_backoff(self, key: str):
"""Reset backoff delay for a key"""
self.backoff_delays[key] = self.initial_delay

class UserAgentRotator:
"""Rotates User-Agent strings to avoid detection"""

USER_AGENTS = [
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
"Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
]

@classmethod
def get_random_user_agent(cls) -> str:
return random.choice(cls.USER_AGENTS)

@classmethod
def get_headers(cls) -> Dict[str, str]:
"""Get randomized headers"""
return {
'User-Agent': cls.get_random_user_agent(),
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.9', 'en-CA,en;q=0.9']),
'Accept-Encoding': 'gzip, deflate, br',
'DNT': '1',
'Connection': 'keep-alive',
'Upgrade-Insecure-Requests': '1',
'Sec-Fetch-Dest': 'document',
'Sec-Fetch-Mode': 'navigate',
'Sec-Fetch-Site': 'none',
'Cache-Control': 'max-age=0'
}

class ProxyRotator:
"""Manages proxy rotation for bypassing IP blocks"""

def __init__(self, proxy_list: Optional[List[str]] = None):
self.proxy_list = proxy_list or []
self.current_index = 0
self.failed_proxies = set()

def get_next_proxy(self) -> Optional[ProxyConfig]:
"""Get the next working proxy"""
if not self.proxy_list:
return None

attempts = 0
while attempts < len(self.proxy_list):
proxy = self.proxy_list[self.current_index]
self.current_index = (self.current_index + 1) % len(self.proxy_list)

if proxy not in self.failed_proxies:
return ProxyConfig(http=proxy, https=proxy)

attempts += 1

return None

def mark_proxy_failed(self, proxy: str):
"""Mark a proxy as failed"""
self.failed_proxies.add(proxy)

class SessionManager:
"""Manages HTTP sessions with retry logic and connection pooling"""

def __init__(self, max_retries: int = 3, pool_connections: int = 10, pool_maxsize: int = 20):
self.sessions = {}
self.max_retries = max_retries
self.pool_connections = pool_connections
self.pool_maxsize = pool_maxsize

def get_session(self, proxy: Optional[ProxyConfig] = None) -> requests.Session:
"""Get or create a session with retry strategy"""
session_key = f"{proxy.http if proxy else 'no_proxy'}"

if session_key not in self.sessions:
session = requests.Session()

# Configure retry strategy
retry_strategy = Retry(
total=self.max_retries,
status_forcelist=[429, 500, 502, 503, 504],
backoff_factor=1,
respect_retry_after_header=True
)

adapter = HTTPAdapter(
max_retries=retry_strategy,
pool_connections=self.pool_connections,
pool_maxsize=self.pool_maxsize
)

session.mount("http://", adapter)
session.mount("https://", adapter)

if proxy:
session.proxies = {
'http': proxy.http,
'https': proxy.https
}

self.sessions[session_key] = session

return self.sessions[session_key]

class CacheManager:
"""Manages caching to reduce API calls"""

@staticmethod
def get_cache_key(ticker: str, data_type: str = "stock_data") -> str:
"""Generate cache key for ticker data"""
return f"stock_data_{data_type}_{ticker}_{datetime.now().strftime('%Y%m%d')}"

@staticmethod
def get_cached_data(ticker: str) -> Optional[Dict]:
"""Get cached data for ticker"""
try:
cache_key = CacheManager.get_cache_key(ticker)
return cache.get(cache_key)
except Exception:
return None

@staticmethod
def set_cached_data(ticker: str, data: Dict, timeout: int = 3600):
"""Cache data for ticker"""
try:
cache_key = CacheManager.get_cache_key(ticker)
cache.set(cache_key, data, timeout)
except Exception:
pass

class OptimizedYFinance:
"""Optimized wrapper around yfinance with rate limiting and caching"""

def __init__(self, proxy_list: Optional[List[str]] = None):
self.rate_limiter = RateLimitManager()
self.session_manager = SessionManager()
self.proxy_rotator = ProxyRotator(proxy_list)
self.user_agent_rotator = UserAgentRotator()

def _make_request_with_retry(self, ticker: str, operation: str, **kwargs) -> Optional[any]:
"""Make a request with retry logic and rate limiting"""
max_retries = 4
base_delay = 2

for attempt in range(max_retries + 1):
try:
# Check rate limiting
if not self.rate_limiter.can_make_request('yfinance_api'):
wait_time = 60 - (time.time() % 60) + random.uniform(1, 5)
logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
time.sleep(wait_time)

# Add random delay to avoid pattern detection
time.sleep(random.uniform(0.5, 2.5))

# Set up session with headers
proxy = self.proxy_rotator.get_next_proxy()
session = self.session_manager.get_session(proxy)

# Update session headers
headers = self.user_agent_rotator.get_headers()
session.headers.update(headers)

# Make the request
self.rate_limiter.record_request('yfinance_api')

# Override yfinance session
yf.Ticker._session = session

ticker_obj = yf.Ticker(ticker)

if operation == 'history':
return ticker_obj.history(period="3mo", **kwargs)
elif operation == 'info':
return ticker_obj.info
elif operation == 'fast_info':
return ticker_obj.fast_info

except Exception as e:
error_msg = str(e).lower()

if "too many requests" in error_msg or "rate limit" in error_msg:
wait_time = base_delay * (2 ** attempt) + random.uniform(1, 5)
logger.warning(f"Rate limited on attempt {attempt + 1} for {ticker}, waiting {wait_time:.1f}s")
time.sleep(wait_time)
self.rate_limiter.increase_backoff('yfinance_api')
continue
elif "timeout" in error_msg:
logger.warning(f"Timeout on attempt {attempt + 1} for {ticker}")
time.sleep(base_delay * (attempt + 1))
continue
else:
logger.error(f"Error on attempt {attempt + 1} for {ticker}: {e}")
if attempt < max_retries:
time.sleep(base_delay * (attempt + 1))
continue
break

return None

class Command(BaseCommand):
help = "Fetch stock data and store it in the database with advanced rate limiting bypass"

def add_arguments(self, parser):
parser.add_argument('--batch-size', type=int, default=50, help='Number of tickers to process per batch')
parser.add_argument('--max-workers', type=int, default=3, help='Maximum number of worker threads')
parser.add_argument('--use-cache', action='store_true', help='Use caching to reduce API calls')
parser.add_argument('--delay-range', nargs=2, type=float, default=[1.0, 3.0], 
help='Random delay range between requests (min max)')
parser.add_argument('--proxy-list', nargs='*', help='List of proxy URLs to use for rotation')
parser.add_argument('--auto-export', action='store_true', default=True, 
help='Automatically export data for filtering/email systems (default: True)')
parser.add_argument('--no-auto-export', dest='auto_export', action='store_false',
help='Disable automatic data export')

def handle(self, *args, **options):
start_time = time.time()

# Configuration
batch_size = options['batch_size']
max_workers = options['max_workers']
use_cache = options['use_cache']
delay_min, delay_max = options['delay_range']
proxy_list = options.get('proxy_list', [])
auto_export = options['auto_export']

logger.info(f"Starting optimized stock data fetch with {max_workers} workers, batch size {batch_size}")
if proxy_list:
logger.info(f"Using {len(proxy_list)} proxies for rotation")

# Load tickers
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
formatted_path = os.path.join(BASE_DIR, '../../../../../json/formatted_tickers.json')

with open(formatted_path, 'r') as f:
tickers_json = json.load(f)

tickers_data = {
entry["Ticker"]: {"name": entry.get("Company Name", "")}
for entry in tickers_json.get("tickers", []) if "Ticker" in entry
}

if not tickers_data:
logger.error(" No valid tickers found in formatted_tickers.json — exiting.")
return

tickers = list(tickers_data.keys())
total_tickers = len(tickers)
logger.info(f" Processing {total_tickers} tickers in batches of {batch_size}...")

# Initialize optimized yfinance
optimized_yf = OptimizedYFinance(proxy_list)

# Process in batches to manage memory and rate limits
processed = 0
failed = 0
cached_hits = 0

for i in range(0, total_tickers, batch_size):
batch = tickers[i:i + batch_size]
logger.info(f"Processing batch {i//batch_size + 1}/{(total_tickers + batch_size - 1)//batch_size}")

with ThreadPoolExecutor(max_workers=max_workers) as executor:
futures = {
executor.submit(
self.process_ticker_optimized, 
ticker, 
tickers_data[ticker]["name"],
optimized_yf, 
use_cache,
delay_min,
delay_max
): ticker 
for ticker in batch
}

for future in as_completed(futures):
ticker = futures[future]
try:
result = future.result()
if result == "success":
processed += 1
elif result == "cached":
cached_hits += 1
processed += 1
else:
failed += 1
except Exception as e:
logger.error(f" Error processing {ticker}: {e}")
failed += 1

# Longer delay between batches
if i + batch_size < total_tickers:
batch_delay = random.uniform(10, 20)
logger.info(f"Batch complete. Waiting {batch_delay:.1f}s before next batch...")
time.sleep(batch_delay)

elapsed = time.time() - start_time
logger.info(f"⏱ Completed in {int(elapsed//60)} min {int(elapsed%60)} sec.")
logger.info(f" Stats: {processed} processed, {failed} failed, {cached_hits} from cache")

# Auto-export data for web filtering and email systems
if processed > 0 and auto_export:
logger.info(" Exporting data for web filtering system...")
try:
from django.core.management import call_command
call_command('export_stock_data', format='web', verbosity=0)
logger.info(" Data export completed successfully")
except Exception as e:
logger.warning(f" Data export failed: {e}")
logger.info(" Run manually: python manage.py export_stock_data")

def process_ticker_optimized(self, ticker: str, company_name: str, optimized_yf: OptimizedYFinance, 
use_cache: bool, delay_min: float, delay_max: float) -> str:
"""Process a single ticker with optimization"""

try:
# Check cache first
if use_cache:
cached_data = CacheManager.get_cached_data(ticker)
if cached_data:
logger.debug(f" Using cached data for {ticker}")
return "cached"

# Add random delay
time.sleep(random.uniform(delay_min, delay_max))

# Get historical data
hist_data = optimized_yf._make_request_with_retry(ticker, 'history')
if hist_data is None or hist_data.empty:
logger.warning(f" No historical data for {ticker}")
return "failed"

# Get company info
info = optimized_yf._make_request_with_retry(ticker, 'fast_info')
if not info:
info = optimized_yf._make_request_with_retry(ticker, 'info')

if not info:
logger.warning(f"ℹ No info data for {ticker}")
return "failed"

# Process data
current_price = float(hist_data['Close'].iloc[-1])
prev_price = float(hist_data['Close'].iloc[-2]) if len(hist_data) >= 2 else current_price
volume_today = int(hist_data['Volume'].iloc[-1])

# Handle different info formats
if hasattr(info, '__dict__'):
# fast_info object
avg_volume = getattr(info, 'average_volume', 0) or 0
shares = getattr(info, 'shares_outstanding', 0) or 0
pe = getattr(info, 'trailing_pe', None)
mc = getattr(info, 'market_cap', None)
else:
# regular info dict
avg_volume = info.get('averageVolume', 0) or 0
shares = info.get('sharesOutstanding', 0) or 0
pe = info.get('trailingPE')
mc = info.get('marketCap')

# Calculate metrics
dvav = round(volume_today / avg_volume, 4) if avg_volume else None
dvsa = round(volume_today / shares, 4) if shares else None

# Generate notes
note_parts = []

# DVSA analysis
if dvsa:
if dvsa >= 1.0:
note_parts.append("dvsa volume 100")
elif dvsa >= 0.5:
note_parts.append("dvsa volume 50")

# PE analysis
if pe and isinstance(pe, (int, float)) and pe > 0:
if pe >= 30:
note_parts.append("pe increase 30")
elif pe >= 20:
note_parts.append("pe increase 20")
elif pe >= 10:
note_parts.append("pe increase 10")
elif pe <= 10:
note_parts.append("pe decrease 10")

# Price change analysis
if prev_price > 0:
price_change = ((current_price - prev_price) / prev_price) * 100
if price_change <= -20:
note_parts.append("price drop 20")
elif price_change <= -15:
note_parts.append("price drop 15")
elif price_change <= -10:
note_parts.append("price drop 10")

note = ", ".join(note_parts) if note_parts else "dvsa volume 50"

# Save to database
stock_data = {
'company_name': company_name,
'current_price': current_price,
'volume_today': volume_today,
'avg_volume': avg_volume if avg_volume else None,
'dvav': dvav,
'dvsa': dvsa,
'pe_ratio': pe if isinstance(pe, (int, float)) else None,
'market_cap': mc if isinstance(mc, (int, float)) else None,
'note': note,
'last_update': make_aware(datetime.utcnow())
}

StockAlert.objects.update_or_create(
ticker=ticker,
defaults=stock_data
)

# Cache the data
if use_cache:
CacheManager.set_cached_data(ticker, stock_data)

logger.info(f" Saved {ticker} (Price: ${current_price:.2f}, Volume: {volume_today:,})")
return "success"

except Exception as e:
logger.error(f" Failed to process {ticker}: {e}")
return "failed"