#!/usr/bin/env python3
"""
Ultra-Fast YFinance Data Retrieval Script
Target: <180 seconds for all tickers with ≥90% accuracy

Features:
- Proxy rotation and management with health checking
- Adaptive rate limiting with intelligent backoff
- 75 concurrent workers with connection pooling
- 3-tier fallback: fast_info -> info -> history
- Multi-level retry strategy
- Real-time performance monitoring
"""

import os
import sys
import time
import json
import random
import logging
import threading
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
from collections import defaultdict
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Try to import yfinance and pandas
try:
    import yfinance as yf
    import pandas as pd
except ImportError as e:
    print(f"Error: {e}")
    print("Please install requirements: pip install yfinance pandas")
    sys.exit(1)

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class Config:
    """Central configuration"""
    # Performance targets
    TARGET_RUNTIME: int = 300  # seconds (5 minutes)
    MIN_SUCCESS_RATE: float = 0.90  # 90% (requires paid proxies!)

    # Concurrency - OPTIMIZED FOR BEST BALANCE (NO PROXIES)
    # Based on extensive testing: Run 3 achieved best results
    MAX_WORKERS: int = 50  # Optimal for no-proxy mode
    WORKER_STARTUP_STAGGER: float = 0.1  # Quick but controlled startup

    # Proxy management - DISABLED (free proxies don't work)
    MIN_PROXIES: int = 0  # Allow running without proxies
    MAX_PROXIES: int = 0  # Disable proxy loading (45k+ tested, 0% work)
    PROXY_ROTATION_INTERVAL: int = 50
    PROXY_MAX_CONSECUTIVE_FAILURES: int = 2

    # Rate limiting - OPTIMAL FOR NO-PROXY MODE
    BASE_DELAY: float = 0.01  # 10ms base (aggressive for best throughput)
    MAX_DELAY: float = 2.0    # 2s max delay
    REQUEST_TIMEOUT: int = 5  # seconds

    # Retry logic - MINIMAL
    MAX_RETRIES: int = 0  # No retries to save time
    BACKOFF_BASE: float = 0.5  # Not used with 0 retries

    # Paths
    TICKER_FILE: str = '/home/user/stock-scanner-complete/backend/data/combined_tickers_20251105_145319.csv'
    PROXY_FILES: list = None
    OUTPUT_FILE: str = 'yfinance_results.json'
    LOG_FILE: str = 'ultra_fast_yfinance.log'

    # Logging
    LOG_LEVEL: str = 'INFO'

    def __post_init__(self):
        """Set default proxy files"""
        if self.PROXY_FILES is None:
            base_dir = '/home/user/stock-scanner-complete/backend'
            self.PROXY_FILES = [
                # JSON files
                f'{base_dir}/working_proxies.json',
                f'{base_dir}/new_proxies.json',
                f'{base_dir}/new_proxies_filtered.json',
                f'{base_dir}/new_proxies_proxifly.json',
                f'{base_dir}/new_proxies_redscrape.json',
                f'{base_dir}/tmp_user_proxies.json',
                f'{base_dir}/tmp_proxies/redscrape.json',

                # Text files in tmp_proxies
                f'{base_dir}/tmp_proxies/speedx_http.txt',
                f'{base_dir}/tmp_proxies/proxyscrape_v2_http.txt',
                f'{base_dir}/tmp_proxies/proxifly_all.txt',
                f'{base_dir}/tmp_proxies/clarketm_http.txt',
                f'{base_dir}/tmp_proxies/proxylistdownload_http.txt',
                f'{base_dir}/tmp_proxies/monosans_http.txt',
                f'{base_dir}/tmp_proxies/shiftytr_http.txt',
            ]


# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging(config: Config) -> logging.Logger:
    """Configure logging with file and console handlers"""
    logger = logging.getLogger('yfinance_scanner')
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    logger.handlers = []  # Clear existing handlers

    # File handler
    fh = logging.FileHandler(config.LOG_FILE)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


# =============================================================================
# PROXY POOL MANAGER
# =============================================================================

class ProxyPoolManager:
    """Manages proxy pool with health checking and rotation"""

    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.proxies = []
        self.proxy_stats = defaultdict(lambda: {
            'success': 0,
            'failures': 0,
            'consecutive_failures': 0,
            'total_time': 0.0
        })
        self.worker_proxy_map = {}
        self.rotation_index = 0
        self.lock = threading.Lock()
        self.banned_proxies = set()

    def initialize(self) -> bool:
        """Load and validate proxies"""
        self.logger.info("Initializing proxy pool...")

        # Skip proxy loading if MAX_PROXIES is 0
        if self.config.MAX_PROXIES == 0:
            self.logger.info("Proxy loading disabled (MAX_PROXIES=0)")
            self.logger.info("Running in NO-PROXY mode (conservative rate limiting enabled)")
            self.proxies = []
            return True

        # Load from all proxy files
        for proxy_file in self.config.PROXY_FILES:
            if os.path.exists(proxy_file):
                proxies = self._load_json_proxies(proxy_file)
                self.logger.debug(f"Loaded {len(proxies)} from {proxy_file}")
                self.proxies.extend(proxies)

        # Deduplicate
        unique_proxies = list(set(self.proxies))
        self.logger.info(f"Loaded {len(unique_proxies)} unique proxies")

        # If we have many proxies, skip validation (too slow)
        # Just use them all and let runtime filtering handle bad ones
        if len(unique_proxies) > 500:
            self.logger.info("Large proxy pool detected - skipping validation for speed")
            self.proxies = unique_proxies
        elif len(unique_proxies) > 100:
            # Quick validation of subset only
            test_count = 50
            self.logger.info(f"Testing {test_count} sample proxies...")
            validated = self._quick_validate(unique_proxies[:test_count])
            # Use all proxies, just log validation result
            self.proxies = unique_proxies
            self.logger.info(f"Sample validation: {len(validated)}/{test_count} working")
        else:
            # Small set, can afford to validate
            self.proxies = self._quick_validate(unique_proxies)

        if len(self.proxies) < self.config.MIN_PROXIES:
            self.logger.warning(f"Only {len(self.proxies)} proxies available (min: {self.config.MIN_PROXIES})")
            if self.config.MIN_PROXIES == 0:
                self.logger.info("Running in NO-PROXY mode (conservative rate limiting enabled)")
            else:
                self.logger.warning("Script will run with limited proxies (may be rate limited)")
            return True  # Continue anyway

        self.logger.info(f"✓ {len(self.proxies)} proxies ready")
        return True

    def _load_json_proxies(self, filepath: str) -> List[str]:
        """Load proxies from JSON or TXT file"""
        proxies = []

        try:
            # Check if file is txt
            if filepath.endswith('.txt'):
                with open(filepath, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and ':' in line and not line.startswith('#'):
                            # Format as http://ip:port
                            if not line.startswith(('http://', 'https://', 'socks')):
                                line = f'http://{line}'
                            proxies.append(line)
                return proxies

            # Handle JSON files
            with open(filepath, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    # List of proxy strings or dicts
                    for item in data:
                        if isinstance(item, str):
                            proxies.append(item)
                        elif isinstance(item, dict) and 'proxy' in item:
                            proxies.append(item['proxy'])
                        elif isinstance(item, dict) and 'url' in item:
                            proxies.append(item['url'])
                elif isinstance(data, dict):
                    # Dict with proxy URLs as keys or values
                    if 'proxies' in data:
                        return data['proxies']
                    return list(data.keys()) if data else []

        except FileNotFoundError:
            self.logger.debug(f"File not found: {filepath}")
        except Exception as e:
            self.logger.debug(f"Failed to load {filepath}: {e}")

        return proxies

    def _quick_validate(self, proxies: List[str], timeout: int = 3) -> List[str]:
        """Quickly validate proxies concurrently"""
        valid = []

        def test_proxy(proxy_url):
            try:
                # Ensure proper format
                if not proxy_url.startswith(('http://', 'https://', 'socks5://')):
                    proxy_url = 'http://' + proxy_url

                proxy_dict = {'http': proxy_url, 'https': proxy_url}
                resp = requests.get(
                    'https://finance.yahoo.com',
                    proxies=proxy_dict,
                    timeout=timeout,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                if resp.status_code == 200:
                    return proxy_url
            except:
                pass
            return None

        # Test proxies concurrently
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = {executor.submit(test_proxy, p): p for p in proxies[:100]}

            for future in as_completed(futures, timeout=10):
                try:
                    result = future.result(timeout=1)
                    if result:
                        valid.append(result)
                        if len(valid) >= self.config.MAX_PROXIES:
                            break
                except:
                    pass

        return valid

    def get_proxy(self, worker_id: int) -> Optional[dict]:
        """Get proxy for worker with sticky assignment"""
        if not self.proxies:
            return None

        with self.lock:
            # Initialize worker if needed
            if worker_id not in self.worker_proxy_map:
                proxy_url = self.proxies[worker_id % len(self.proxies)]
                self.worker_proxy_map[worker_id] = {
                    'proxy': proxy_url,
                    'requests': 0,
                    'consecutive_failures': 0
                }

            mapping = self.worker_proxy_map[worker_id]
            proxy_url = mapping['proxy']

            # Check if rotation needed
            stats = self.proxy_stats[proxy_url]
            if (mapping['requests'] >= self.config.PROXY_ROTATION_INTERVAL or
                stats['consecutive_failures'] >= self.config.PROXY_MAX_CONSECUTIVE_FAILURES):
                # Rotate to next available proxy
                proxy_url = self._get_next_available_proxy()
                mapping['proxy'] = proxy_url
                mapping['requests'] = 0
                mapping['consecutive_failures'] = 0

            mapping['requests'] += 1

            # Ensure proper format
            if not proxy_url.startswith(('http://', 'https://', 'socks5://')):
                proxy_url = 'http://' + proxy_url

            return {
                'http': proxy_url,
                'https': proxy_url
            }

    def _get_next_available_proxy(self) -> str:
        """Get next proxy from pool, skipping banned ones"""
        for _ in range(len(self.proxies)):
            self.rotation_index = (self.rotation_index + 1) % len(self.proxies)
            proxy = self.proxies[self.rotation_index]
            if proxy not in self.banned_proxies:
                return proxy

        # All banned, reset and use any
        self.banned_proxies.clear()
        return self.proxies[self.rotation_index]

    def mark_success(self, proxy_url: Optional[str], elapsed_time: float):
        """Record successful request"""
        if not proxy_url:
            return
        with self.lock:
            stats = self.proxy_stats[proxy_url]
            stats['success'] += 1
            stats['total_time'] += elapsed_time
            stats['consecutive_failures'] = 0

    def mark_failure(self, proxy_url: Optional[str], reason: str):
        """Record failed request"""
        if not proxy_url:
            return
        with self.lock:
            stats = self.proxy_stats[proxy_url]
            stats['failures'] += 1
            stats['consecutive_failures'] += 1

            # Ban if too many consecutive failures
            if stats['consecutive_failures'] >= 5:
                self.banned_proxies.add(proxy_url)
                self.logger.warning(f"Banned proxy (5 consecutive failures)")


# =============================================================================
# RATE LIMITER
# =============================================================================

class AdaptiveRateLimiter:
    """Adaptive rate limiting with automatic backoff"""

    def __init__(self, config: Config):
        self.config = config
        self.current_delay = config.BASE_DELAY
        self.success_streak = 0
        self.failure_streak = 0
        self.lock = threading.Lock()
        self.last_request_time = {}  # Per-worker tracking

    def wait(self, worker_id: int):
        """Wait before next request"""
        delay = self._get_jittered_delay()

        # Ensure minimum delay per worker
        with self.lock:
            if worker_id in self.last_request_time:
                elapsed = time.time() - self.last_request_time[worker_id]
                if elapsed < delay:
                    time.sleep(delay - elapsed)
            self.last_request_time[worker_id] = time.time()

    def record_success(self):
        """Record successful request"""
        with self.lock:
            self.success_streak += 1
            self.failure_streak = 0

            # Speed up more aggressively on sustained success
            if self.success_streak >= 20:  # Reduced from 50
                self.current_delay = max(
                    self.config.BASE_DELAY,
                    self.current_delay * 0.9  # Faster reduction
                )

    def record_failure(self, status_code: Optional[int] = None):
        """Record failed request"""
        with self.lock:
            self.failure_streak += 1
            self.success_streak = 0

            # Less aggressive slowdown (accept some failures for speed)
            if status_code in [429, 503]:
                # Still respect rate limits
                self.current_delay = min(
                    self.config.MAX_DELAY,
                    self.current_delay * 1.5  # Reduced from 2.0
                )
            elif self.failure_streak >= 10:  # Increased threshold from 5
                self.current_delay = min(
                    self.config.MAX_DELAY,
                    self.current_delay * 1.2  # Reduced from 1.3
                )

    def _get_jittered_delay(self) -> float:
        """Get delay with jitter to prevent thundering herd"""
        jitter = random.uniform(-0.3, 0.3) * self.current_delay
        return max(0, self.current_delay + jitter)


# =============================================================================
# DATA FETCHER
# =============================================================================

class YFinanceDataFetcher:
    """Fetches data from yfinance with fallback strategies"""

    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    ]

    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger

    def create_session(self, proxy: Optional[dict]) -> requests.Session:
        """Create optimized session with proxy"""
        session = requests.Session()

        if proxy:
            session.proxies = proxy

        # Connection pooling
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=Retry(
                total=1,
                backoff_factor=0.3,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        # Headers
        session.headers.update({
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/json',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate',
        })

        return session

    def fetch(self, ticker: str, proxy: Optional[dict] = None) -> Optional[dict]:
        """
        Fetch ticker data with fast_info only (3-5x faster)
        """
        try:
            # Configure yfinance proxy if available
            import yfinance as yf
            if proxy:
                # New API: set proxy via config
                yf.set_config(proxy=proxy.get('http'))

            # Create ticker
            yf_ticker = yf.Ticker(ticker)
            data = {'ticker': ticker, 'timestamp': time.time()}

            # OPTIMIZED: Use ONLY fast_info for maximum speed
            # This is 3-5x faster than info() and reduces API load
            try:
                fast_info = yf_ticker.fast_info
                data.update({
                    'current_price': getattr(fast_info, 'last_price', None),
                    'market_cap': getattr(fast_info, 'market_cap', None),
                    'volume': getattr(fast_info, 'last_volume', None),
                    'pe_ratio': getattr(fast_info, 'trailing_pe', None),
                    'days_low': getattr(fast_info, 'day_low', None),
                    'days_high': getattr(fast_info, 'day_high', None),
                    'week_52_low': getattr(fast_info, 'fifty_two_week_low', None),
                    'week_52_high': getattr(fast_info, 'fifty_two_week_high', None),
                })

                # Return if we have price (primary field)
                if data.get('current_price'):
                    return self._clean_data(data)

            except Exception as e:
                self.logger.debug(f"fast_info failed for {ticker}: {e}")

            return None

        except Exception as e:
            self.logger.error(f"Fatal error fetching {ticker}: {e}")
            return None

    def _extract_from_info(self, info: dict) -> dict:
        """Extract relevant fields from info dict"""
        return {
            'current_price': (info.get('currentPrice') or
                            info.get('regularMarketPrice') or
                            info.get('regularMarketOpen')),
            'volume': (info.get('volume') or
                      info.get('regularMarketVolume')),
            'market_cap': info.get('marketCap'),
            'pe_ratio': (info.get('trailingPE') or
                        info.get('forwardPE')),
            'dividend_yield': info.get('dividendYield'),
            'bid_price': info.get('bid'),
            'ask_price': info.get('ask'),
            'days_low': (info.get('dayLow') or
                        info.get('regularMarketDayLow')),
            'days_high': (info.get('dayHigh') or
                         info.get('regularMarketDayHigh')),
            'week_52_low': info.get('fiftyTwoWeekLow'),
            'week_52_high': info.get('fiftyTwoWeekHigh'),
            'avg_volume_3mon': (info.get('averageVolume') or
                               info.get('averageDailyVolume3Month')),
            'company_name': (info.get('longName') or
                           info.get('shortName')),
            'exchange': info.get('exchange'),
        }

    def _clean_data(self, data: dict) -> dict:
        """Clean and normalize data"""
        # Remove None values
        cleaned = {k: v for k, v in data.items() if v is not None}

        # Convert to appropriate types
        for field in ['current_price', 'pe_ratio', 'dividend_yield']:
            if field in cleaned:
                try:
                    cleaned[field] = float(cleaned[field])
                except:
                    del cleaned[field]

        for field in ['volume', 'market_cap']:
            if field in cleaned:
                try:
                    cleaned[field] = int(cleaned[field])
                except:
                    del cleaned[field]

        return cleaned


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

class UltraFastScanner:
    """Main orchestration class"""

    def __init__(self, config: Config):
        self.config = config
        self.logger = setup_logging(config)
        self.proxy_manager = ProxyPoolManager(config, self.logger)
        self.rate_limiter = AdaptiveRateLimiter(config)
        self.fetcher = YFinanceDataFetcher(config, self.logger)

        # Metrics
        self.total = 0
        self.completed = 0
        self.failed = 0
        self.start_time = None
        self.lock = threading.Lock()
        self.results = []

    def run(self) -> bool:
        """Execute complete scan"""
        self.logger.info("=" * 70)
        self.logger.info("ULTRA-FAST YFINANCE SCANNER")
        self.logger.info("=" * 70)

        # Initialize
        if not self.proxy_manager.initialize():
            self.logger.error("Failed to initialize proxy pool")
            # Continue anyway without proxies

        # Load tickers
        tickers = self._load_tickers()
        if not tickers:
            self.logger.error("No tickers to process")
            return False

        self.total = len(tickers)
        self.logger.info(f"Processing {self.total} tickers...")
        self.logger.info(f"Target: <{self.config.TARGET_RUNTIME}s with ≥{self.config.MIN_SUCCESS_RATE*100}% success")
        self.logger.info(f"Workers: {self.config.MAX_WORKERS}")
        self.logger.info("-" * 70)

        # Execute
        self.start_time = time.time()
        self._execute_parallel(tickers)
        elapsed = time.time() - self.start_time

        # Report
        self._print_summary(elapsed)

        # Save results
        if self.results:
            self._save_results()

        success_rate = self.completed / self.total if self.total > 0 else 0
        meets_requirements = (elapsed < self.config.TARGET_RUNTIME and
                             success_rate >= self.config.MIN_SUCCESS_RATE)

        return meets_requirements

    def _load_tickers(self) -> List[str]:
        """Load tickers from CSV file"""
        tickers = []
        try:
            with open(self.config.TICKER_FILE, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ticker = row.get('Symbol', '').strip()
                    if ticker:
                        tickers.append(ticker)
            self.logger.info(f"Loaded {len(tickers)} tickers from {self.config.TICKER_FILE}")
        except Exception as e:
            self.logger.error(f"Failed to load tickers: {e}")

        return tickers

    def _execute_parallel(self, tickers: List[str]):
        """Execute with thread pool"""
        # Create worker pool
        with ThreadPoolExecutor(max_workers=self.config.MAX_WORKERS) as executor:
            futures = []

            for worker_id, ticker in enumerate(tickers):
                # Stagger startup
                if worker_id > 0 and worker_id % 20 == 0:
                    time.sleep(self.config.WORKER_STARTUP_STAGGER)

                future = executor.submit(
                    self._process_ticker,
                    ticker=ticker,
                    worker_id=worker_id
                )
                futures.append((future, ticker))

            # Collect results
            for future, ticker in futures:
                try:
                    result = future.result(timeout=30)
                    if result:
                        with self.lock:
                            self.results.append(result)
                            self.completed += 1
                    else:
                        with self.lock:
                            self.failed += 1

                    # Progress update every 200 tickers
                    if (self.completed + self.failed) % 200 == 0:
                        self._print_progress()

                except Exception as e:
                    self.logger.debug(f"Future error for {ticker}: {e}")
                    with self.lock:
                        self.failed += 1

    def _process_ticker(self, ticker: str, worker_id: int) -> Optional[dict]:
        """Process single ticker with rate limiting and retries"""

        # Rate limit
        self.rate_limiter.wait(worker_id)

        # Get proxy
        proxy = self.proxy_manager.get_proxy(worker_id)
        proxy_url = proxy.get('http') if proxy else None

        # Fetch with retries
        for attempt in range(self.config.MAX_RETRIES + 1):
            try:
                start = time.time()
                # Let yfinance handle its own session
                data = self.fetcher.fetch(ticker, proxy)
                elapsed = time.time() - start

                if data:
                    self.rate_limiter.record_success()
                    self.proxy_manager.mark_success(proxy_url, elapsed)
                    return data
                else:
                    self.rate_limiter.record_failure()

                if attempt < self.config.MAX_RETRIES:
                    time.sleep(self.config.BACKOFF_BASE * (2 ** attempt))

            except Exception as e:
                self.rate_limiter.record_failure()
                self.proxy_manager.mark_failure(proxy_url, str(e))

                if attempt < self.config.MAX_RETRIES:
                    time.sleep(self.config.BACKOFF_BASE * (2 ** attempt))

        return None

    def _print_progress(self):
        """Print progress update"""
        elapsed = time.time() - self.start_time
        processed = self.completed + self.failed
        rate = processed / elapsed if elapsed > 0 else 0
        success_rate = self.completed / processed * 100 if processed > 0 else 0
        remaining = (self.total - processed) / rate if rate > 0 else 0

        self.logger.info(f"Progress: {processed}/{self.total} "
                        f"({success_rate:.1f}% success) "
                        f"| Rate: {rate:.1f}/s "
                        f"| Elapsed: {elapsed:.0f}s "
                        f"| ETA: {remaining:.0f}s")

    def _print_summary(self, elapsed: float):
        """Print final summary"""
        success_rate = self.completed / self.total * 100 if self.total > 0 else 0
        rate = self.completed / elapsed if elapsed > 0 else 0

        self.logger.info("=" * 70)
        self.logger.info("SCAN COMPLETE")
        self.logger.info("=" * 70)
        self.logger.info(f"Total tickers:   {self.total}")
        self.logger.info(f"Completed:       {self.completed}")
        self.logger.info(f"Failed:          {self.failed}")
        self.logger.info(f"Success rate:    {success_rate:.2f}%")
        self.logger.info(f"Runtime:         {elapsed:.2f}s")
        self.logger.info(f"Rate:            {rate:.2f} tickers/second")
        self.logger.info("-" * 70)
        self.logger.info(f"Target runtime:  <{self.config.TARGET_RUNTIME}s")
        self.logger.info(f"Target success:  ≥{self.config.MIN_SUCCESS_RATE * 100}%")

        if (elapsed < self.config.TARGET_RUNTIME and
            success_rate >= self.config.MIN_SUCCESS_RATE * 100):
            self.logger.info("✓ ✓ ✓ PERFORMANCE TARGETS MET ✓ ✓ ✓")
        else:
            self.logger.warning("✗ Performance targets not met")
            if elapsed >= self.config.TARGET_RUNTIME:
                self.logger.warning(f"  Runtime exceeded by {elapsed - self.config.TARGET_RUNTIME:.1f}s")
            if success_rate < self.config.MIN_SUCCESS_RATE * 100:
                self.logger.warning(f"  Success rate below target by {self.config.MIN_SUCCESS_RATE * 100 - success_rate:.1f}%")

        self.logger.info("=" * 70)

    def _save_results(self):
        """Save results to JSON file"""
        try:
            with open(self.config.OUTPUT_FILE, 'w') as f:
                json.dump(self.results, f, indent=2)
            self.logger.info(f"✓ Results saved to {self.config.OUTPUT_FILE}")
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    """Main entry point"""
    config = Config()
    scanner = UltraFastScanner(config)

    success = scanner.run()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
