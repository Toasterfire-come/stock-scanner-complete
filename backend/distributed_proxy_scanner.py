#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Distributed Proxy-Based Stock Scanner

Strategy:
1. Validate all 85,000 proxies rapidly in parallel
2. Each working proxy handles batches of 100-150 tickers
3. Distribute load across all working proxies
4. Even with 1% success rate (850 proxies), we can handle massive volume

Target: 5,193 tickers in <180s with >95% success rate
With 850 working proxies @ 100 tickers each = 85,000 ticker capacity
"""

import os
import sys
import time
import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
from dataclasses import dataclass
from queue import Queue
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")

import django
django.setup()

import yfinance as yf
from django.utils import timezone as dj_timezone
from stocks.models import Stock
from stock_retrieval.session_factory import ProxyPool
from stock_retrieval.config import StockRetrievalConfig

# Configuration
@dataclass
class Config:
    # Proxy validation
    proxy_validation_workers: int = 500  # Very high for fast validation
    proxy_test_timeout: int = 3  # Quick timeout for validation
    max_proxies_to_test: int = 85000  # Test all available

    # Stock fetching
    tickers_per_proxy: int = 100  # Each proxy handles 100 tickers
    stock_fetch_timeout: int = 8
    max_retries_per_ticker: int = 2

    # Performance
    target_tickers: int = 5193
    target_seconds: int = 180

    # Proxy rotation
    proxy_cooldown: int = 30  # Seconds before reusing a proxy

CONFIG = Config()

# Logging with unbuffered output
import sys
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)  # Line buffered

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


class ProxyManager:
    """Manage validated proxies and rotation"""

    def __init__(self):
        self.working_proxies = []
        self.proxy_usage = {}  # Track last use time
        self.lock = threading.Lock()

    def add_working_proxy(self, proxy: str):
        """Add a validated working proxy"""
        with self.lock:
            if proxy not in self.working_proxies:
                self.working_proxies.append(proxy)
                self.proxy_usage[proxy] = 0  # Never used

    def get_available_proxy(self) -> Optional[str]:
        """Get an available proxy (respecting cooldown)"""
        with self.lock:
            now = time.time()

            # Find proxy that's cooled down
            for proxy in self.working_proxies:
                last_used = self.proxy_usage.get(proxy, 0)
                if now - last_used >= CONFIG.proxy_cooldown:
                    self.proxy_usage[proxy] = now
                    return proxy

            # If all in cooldown, return least recently used
            if self.working_proxies:
                proxy = min(self.proxy_usage.items(), key=lambda x: x[1])[0]
                self.proxy_usage[proxy] = now
                return proxy

            return None

    def count(self) -> int:
        """Count working proxies"""
        with self.lock:
            return len(self.working_proxies)


class Metrics:
    """Thread-safe metrics tracking"""

    def __init__(self):
        self.lock = threading.Lock()
        self.start_time = None

        # Proxy validation
        self.proxies_tested = 0
        self.proxies_working = 0

        # Stock fetching
        self.tickers_processed = 0
        self.tickers_successful = 0
        self.tickers_failed = 0

    def start(self):
        self.start_time = time.time()

    def record_proxy_test(self, working: bool):
        with self.lock:
            self.proxies_tested += 1
            if working:
                self.proxies_working += 1

    def record_ticker_result(self, success: bool):
        with self.lock:
            self.tickers_processed += 1
            if success:
                self.tickers_successful += 1
            else:
                self.tickers_failed += 1

    def get_stats(self):
        with self.lock:
            elapsed = time.time() - self.start_time if self.start_time else 0
            return {
                'elapsed': elapsed,
                'proxies_tested': self.proxies_tested,
                'proxies_working': self.proxies_working,
                'tickers_processed': self.tickers_processed,
                'tickers_successful': self.tickers_successful,
                'tickers_failed': self.tickers_failed,
                'success_rate': self.tickers_successful / self.tickers_processed if self.tickers_processed > 0 else 0,
                'throughput': self.tickers_processed / elapsed if elapsed > 0 else 0
            }


metrics = Metrics()
proxy_manager = ProxyManager()


def validate_proxy_fast(proxy: str) -> bool:
    """Quick validation - can this proxy reach Yahoo Finance?"""

    try:
        proxies = {
            'http': proxy,
            'https': proxy
        }

        # Quick test - just try to fetch AAPL
        response = requests.get(
            'https://query2.finance.yahoo.com/v8/finance/chart/AAPL',
            proxies=proxies,
            timeout=CONFIG.proxy_test_timeout,
            verify=False  # Skip SSL verification for speed
        )

        # Any non-error response means proxy works
        if response.status_code in [200, 404]:  # 200 = success, 404 = ticker not found but proxy works
            metrics.record_proxy_test(working=True)
            proxy_manager.add_working_proxy(proxy)
            return True

    except Exception:
        pass

    metrics.record_proxy_test(working=False)
    return False


def validate_all_proxies(proxy_pool: ProxyPool) -> int:
    """Validate all proxies in parallel - find working ones"""

    logger.info("="*70)
    logger.info("PHASE 1: PROXY VALIDATION")
    logger.info("="*70)

    all_proxies = proxy_pool.proxies[:CONFIG.max_proxies_to_test]
    logger.info(f"Testing {len(all_proxies)} proxies with {CONFIG.proxy_validation_workers} workers...")

    metrics.start()

    # Test all proxies in parallel
    with ThreadPoolExecutor(max_workers=CONFIG.proxy_validation_workers) as executor:
        futures = {executor.submit(validate_proxy_fast, proxy): proxy for proxy in all_proxies}

        for future in as_completed(futures):
            # Progress update every 1000 proxies
            if metrics.proxies_tested % 1000 == 0:
                stats = metrics.get_stats()
                logger.info(
                    f"Progress: {stats['proxies_tested']}/{len(all_proxies)} tested | "
                    f"Working: {stats['proxies_working']} "
                    f"({stats['proxies_working']/stats['proxies_tested']*100:.2f}%)"
                )

    stats = metrics.get_stats()
    logger.info("")
    logger.info(f"Validation complete in {stats['elapsed']:.1f}s")
    logger.info(f"Working proxies: {stats['proxies_working']}/{stats['proxies_tested']}")
    logger.info(f"Success rate: {stats['proxies_working']/stats['proxies_tested']*100:.2f}%")

    return stats['proxies_working']


def fetch_ticker_with_proxy(ticker: str, proxy: str) -> Optional[Dict]:
    """Fetch a single ticker using specified proxy"""

    for attempt in range(CONFIG.max_retries_per_ticker):
        try:
            # Set up proxy for requests
            proxies = {
                'http': proxy,
                'https': proxy
            }

            # Create session with proxy
            session = requests.Session()
            session.proxies = proxies
            session.verify = False  # Skip SSL verification

            # Create ticker object with session
            ticker_obj = yf.Ticker(ticker, session=session)

            # Try fast_info first
            try:
                info = ticker_obj.fast_info
                data = {
                    'ticker': ticker,
                    'current_price': info.last_price,
                    'volume': info.last_volume,
                    'market_cap': info.market_cap,
                    'day_high': info.day_high,
                    'day_low': info.day_low,
                    'year_high': info.year_high,
                    'year_low': info.year_low,
                }

                if data['current_price'] and data['current_price'] > 0:
                    return data

            except Exception:
                pass

            # Fallback to info
            try:
                info_data = ticker_obj.info
                data = {
                    'ticker': ticker,
                    'current_price': info_data.get('currentPrice') or info_data.get('regularMarketPrice'),
                    'volume': info_data.get('volume'),
                    'market_cap': info_data.get('marketCap'),
                    'day_high': info_data.get('dayHigh'),
                    'day_low': info_data.get('dayLow'),
                    'year_high': info_data.get('fiftyTwoWeekHigh'),
                    'year_low': info_data.get('fiftyTwoWeekLow'),
                }

                if data['current_price'] and data['current_price'] > 0:
                    return data

            except Exception:
                pass

        except Exception as e:
            if attempt < CONFIG.max_retries_per_ticker - 1:
                time.sleep(0.5 * (attempt + 1))  # Brief backoff
                continue

    return None


def process_ticker_batch(tickers: List[str], proxy: str) -> List[Dict]:
    """Process a batch of tickers with a single proxy"""

    results = []

    for ticker in tickers:
        data = fetch_ticker_with_proxy(ticker, proxy)

        if data:
            results.append(data)
            metrics.record_ticker_result(success=True)
        else:
            metrics.record_ticker_result(success=False)

    return results


def save_to_database(data: Dict):
    """Save stock data to database"""
    try:
        now = dj_timezone.now()
        dvav = (data['current_price'] * data['volume']) if data.get('volume') else 0

        Stock.objects.update_or_create(
            ticker=data['ticker'],
            defaults={
                'current_price': data['current_price'],
                'volume': data['volume'],
                'market_cap': data['market_cap'],
                'day_high': data['day_high'],
                'day_low': data['day_low'],
                'week_52_high': data['year_high'],
                'week_52_low': data['year_low'],
                'dvav': dvav,
                'last_updated': now,
            }
        )
        return True
    except Exception as e:
        logger.error(f"Error saving {data['ticker']}: {e}")
        return False


def distribute_and_fetch(tickers: List[str]) -> int:
    """Distribute tickers across working proxies and fetch data"""

    logger.info("")
    logger.info("="*70)
    logger.info("PHASE 2: DISTRIBUTED STOCK FETCHING")
    logger.info("="*70)

    working_proxy_count = proxy_manager.count()
    logger.info(f"Working proxies: {working_proxy_count}")
    logger.info(f"Tickers to fetch: {len(tickers)}")
    logger.info(f"Tickers per proxy: {CONFIG.tickers_per_proxy}")

    # Calculate batches
    batches = []
    for i in range(0, len(tickers), CONFIG.tickers_per_proxy):
        batch = tickers[i:i + CONFIG.tickers_per_proxy]
        batches.append(batch)

    logger.info(f"Total batches: {len(batches)}")
    logger.info(f"Starting distributed fetch...")
    logger.info("")

    saved_count = 0

    def process_batch_with_proxy(batch):
        """Worker function - get proxy and process batch"""
        proxy = proxy_manager.get_available_proxy()
        if not proxy:
            logger.warning("No available proxy for batch!")
            return []

        results = process_ticker_batch(batch, proxy)
        return results

    # Process all batches in parallel
    with ThreadPoolExecutor(max_workers=min(working_proxy_count, 100)) as executor:
        futures = {executor.submit(process_batch_with_proxy, batch): batch for batch in batches}

        for future in as_completed(futures):
            batch_results = future.result()

            # Save results to database
            for data in batch_results:
                if save_to_database(data):
                    saved_count += 1

            # Progress update
            stats = metrics.get_stats()
            if stats['tickers_processed'] % 100 == 0:
                logger.info(
                    f"Progress: {stats['tickers_processed']}/{len(tickers)} | "
                    f"Success: {stats['success_rate']*100:.1f}% | "
                    f"Rate: {stats['throughput']:.1f}/s | "
                    f"Saved: {saved_count}"
                )

    return saved_count


def main():
    """Main execution"""

    logger.info("="*70)
    logger.info("DISTRIBUTED PROXY-BASED STOCK SCANNER")
    logger.info("="*70)
    logger.info(f"Target: {CONFIG.target_tickers} tickers in {CONFIG.target_seconds}s")
    logger.info(f"Strategy: Distribute load across all working proxies")
    logger.info("")

    # Load proxy pool
    logger.info("Loading proxy pool...")
    config = StockRetrievalConfig()
    proxy_pool = ProxyPool.from_config(config)
    logger.info(f"Loaded {len(proxy_pool.proxies)} proxies")
    logger.info("")

    # Phase 1: Validate proxies
    working_count = validate_all_proxies(proxy_pool)

    if working_count == 0:
        logger.error("No working proxies found! Cannot proceed.")
        return

    capacity = working_count * CONFIG.tickers_per_proxy
    logger.info(f"")
    logger.info(f"Capacity: {capacity} tickers ({working_count} proxies × {CONFIG.tickers_per_proxy})")

    if capacity < CONFIG.target_tickers:
        logger.warning(f"Warning: Capacity ({capacity}) < Target ({CONFIG.target_tickers})")
        logger.warning("Some tickers may need multiple passes")

    # Get tickers from database
    logger.info("")
    logger.info("Loading tickers from database...")
    tickers = list(Stock.objects.all()[:CONFIG.target_tickers].values_list('ticker', flat=True))
    logger.info(f"Loaded {len(tickers)} tickers")

    # Phase 2: Distributed fetching
    metrics.start()  # Reset timer for fetching phase
    saved = distribute_and_fetch(tickers)

    # Final results
    stats = metrics.get_stats()

    logger.info("")
    logger.info("="*70)
    logger.info("SCAN COMPLETE")
    logger.info("="*70)
    logger.info(f"Runtime: {stats['elapsed']:.1f}s ({stats['elapsed']/60:.2f} min)")
    logger.info(f"Processed: {stats['tickers_processed']}")
    logger.info(f"Successful: {stats['tickers_successful']}")
    logger.info(f"Failed: {stats['tickers_failed']}")
    logger.info(f"Saved to DB: {saved}")
    logger.info(f"Success rate: {stats['success_rate']*100:.1f}%")
    logger.info(f"Throughput: {stats['throughput']:.2f} tickers/sec")
    logger.info("")

    # Check targets
    time_ok = stats['elapsed'] <= CONFIG.target_seconds
    accuracy_ok = stats['success_rate'] >= 0.95

    if time_ok and accuracy_ok:
        logger.info("[SUCCESS] All targets met!")
    else:
        if not time_ok:
            logger.info(f"[WARN] Time target missed by {stats['elapsed'] - CONFIG.target_seconds:.1f}s")
        if not accuracy_ok:
            logger.info(f"[WARN] Accuracy target missed: {stats['success_rate']*100:.1f}% < 95%")


if __name__ == "__main__":
    # Suppress SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\nScan interrupted by user")
    except Exception as e:
        logger.error(f"\nError during scan: {e}")
        import traceback
        traceback.print_exc()
