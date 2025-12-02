#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Residential Proxy Stock Scanner

Uses your 10 residential proxy accounts to scan 5,193 stocks
with proper load distribution and bandwidth tracking.

Target: <180s runtime with >95% success rate
Strategy: Distribute 520 tickers per proxy account
"""

import os
import sys
import time
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
from dataclasses import dataclass
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")

import django
django.setup()

import yfinance as yf
import requests
from django.utils import timezone as dj_timezone
from stocks.models import Stock

# Configuration
@dataclass
class Config:
    residential_proxy_config: str = "residential_proxies_config.json"
    tickers_per_proxy: int = 520  # ~5193/10 = 519-520 per proxy
    workers_per_proxy: int = 5    # Concurrent requests per proxy
    request_timeout: int = 10
    max_retries: int = 2
    target_tickers: int = 5193
    target_seconds: int = 180

CONFIG = Config()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BandwidthTracker:
    """Track bandwidth usage per proxy"""

    def __init__(self):
        self.lock = threading.Lock()
        self.usage = {}  # proxy_name -> bytes used

    def record_usage(self, proxy_name: str, bytes_used: int):
        with self.lock:
            if proxy_name not in self.usage:
                self.usage[proxy_name] = 0
            self.usage[proxy_name] += bytes_used

    def get_usage(self, proxy_name: str) -> int:
        with self.lock:
            return self.usage.get(proxy_name, 0)

    def get_all_usage(self) -> Dict[str, int]:
        with self.lock:
            return self.usage.copy()


class Metrics:
    """Track performance metrics"""

    def __init__(self):
        self.lock = threading.Lock()
        self.start_time = None
        self.processed = 0
        self.successful = 0
        self.failed = 0
        self.by_proxy = {}  # proxy_name -> {processed, successful, failed}

    def start(self):
        self.start_time = time.time()

    def record_result(self, proxy_name: str, success: bool):
        with self.lock:
            self.processed += 1
            if success:
                self.successful += 1
            else:
                self.failed += 1

            if proxy_name not in self.by_proxy:
                self.by_proxy[proxy_name] = {'processed': 0, 'successful': 0, 'failed': 0}

            self.by_proxy[proxy_name]['processed'] += 1
            if success:
                self.by_proxy[proxy_name]['successful'] += 1
            else:
                self.by_proxy[proxy_name]['failed'] += 1

    def get_stats(self):
        with self.lock:
            elapsed = time.time() - self.start_time if self.start_time else 0
            return {
                'elapsed': elapsed,
                'processed': self.processed,
                'successful': self.successful,
                'failed': self.failed,
                'success_rate': self.successful / self.processed if self.processed > 0 else 0,
                'throughput': self.processed / elapsed if elapsed > 0 else 0,
                'by_proxy': self.by_proxy.copy()
            }


bandwidth_tracker = BandwidthTracker()
metrics = Metrics()


def load_residential_proxies() -> List[Dict]:
    """Load residential proxy configuration"""

    config_path = os.path.join(os.path.dirname(__file__), CONFIG.residential_proxy_config)

    if not os.path.exists(config_path):
        logger.error(f"Residential proxy config not found: {config_path}")
        logger.error("Please create residential_proxies_config.json from the template")
        return []

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        proxies = [p for p in config['residential_proxies'] if p.get('enabled', True)]
        logger.info(f"Loaded {len(proxies)} enabled residential proxies")

        return proxies

    except Exception as e:
        logger.error(f"Error loading proxy config: {e}")
        return []


def fetch_ticker_with_proxy(ticker: str, proxy_config: Dict) -> Optional[Dict]:
    """Fetch a single ticker using specified proxy"""

    proxy_name = proxy_config['name']
    proxy_url = proxy_config['proxy_url']

    for attempt in range(CONFIG.max_retries):
        try:
            # Set up proxy
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }

            # Create session
            session = requests.Session()
            session.proxies = proxies
            session.verify = True  # Residential proxies should have valid SSL

            # Create ticker
            ticker_obj = yf.Ticker(ticker, session=session)

            # Try fast_info first
            try:
                info = ticker_obj.fast_info
                response_size = 2000  # Estimated

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
                    bandwidth_tracker.record_usage(proxy_name, response_size)
                    metrics.record_result(proxy_name, success=True)
                    return data

            except Exception:
                pass

            # Fallback to info
            try:
                info_data = ticker_obj.info
                response_size = 15000  # Estimated

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
                    bandwidth_tracker.record_usage(proxy_name, response_size)
                    metrics.record_result(proxy_name, success=True)
                    return data

            except Exception:
                pass

        except Exception as e:
            if attempt < CONFIG.max_retries - 1:
                time.sleep(0.5 * (attempt + 1))
                continue

    metrics.record_result(proxy_name, success=False)
    return None


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


def process_proxy_batch(proxy_config: Dict, tickers: List[str]) -> int:
    """Process a batch of tickers with a single proxy"""

    proxy_name = proxy_config['name']
    logger.info(f"[{proxy_name}] Processing {len(tickers)} tickers...")

    saved = 0

    # Process tickers concurrently (but limited per proxy)
    with ThreadPoolExecutor(max_workers=CONFIG.workers_per_proxy) as executor:
        futures = {
            executor.submit(fetch_ticker_with_proxy, ticker, proxy_config): ticker
            for ticker in tickers
        }

        for future in as_completed(futures):
            data = future.result()
            if data:
                if save_to_database(data):
                    saved += 1

    # Report proxy stats
    usage_mb = bandwidth_tracker.get_usage(proxy_name) / 1024 / 1024
    stats = metrics.by_proxy.get(proxy_name, {})
    success_rate = stats.get('successful', 0) / stats.get('processed', 1) * 100

    logger.info(
        f"[{proxy_name}] Complete: {saved}/{len(tickers)} saved, "
        f"{success_rate:.1f}% success, {usage_mb:.2f} MB used"
    )

    return saved


def main():
    """Main execution"""

    logger.info("="*70)
    logger.info("RESIDENTIAL PROXY STOCK SCANNER")
    logger.info("="*70)
    logger.info(f"Target: {CONFIG.target_tickers} tickers in {CONFIG.target_seconds}s")
    logger.info(f"Strategy: Distribute load across residential proxies")
    logger.info("")

    # Load residential proxies
    residential_proxies = load_residential_proxies()

    if not residential_proxies:
        logger.error("No residential proxies available!")
        logger.error("Please configure residential_proxies_config.json")
        return

    logger.info(f"Using {len(residential_proxies)} residential proxy accounts")
    logger.info("")

    # Get tickers
    logger.info("Loading tickers from database...")
    all_tickers = list(Stock.objects.all()[:CONFIG.target_tickers].values_list('ticker', flat=True))
    logger.info(f"Loaded {len(all_tickers)} tickers")
    logger.info("")

    # Distribute tickers across proxies
    tickers_per_proxy = len(all_tickers) // len(residential_proxies)
    remainder = len(all_tickers) % len(residential_proxies)

    proxy_assignments = []
    start_idx = 0

    for i, proxy in enumerate(residential_proxies):
        # Add one extra ticker to first few proxies if there's a remainder
        count = tickers_per_proxy + (1 if i < remainder else 0)
        batch = all_tickers[start_idx:start_idx + count]
        proxy_assignments.append((proxy, batch))
        start_idx += count

        logger.info(f"[{proxy['name']}] Assigned {len(batch)} tickers")

    logger.info("")
    logger.info("Starting distributed scan...")
    logger.info("")

    # Start metrics
    metrics.start()

    # Process all proxies in parallel
    total_saved = 0

    with ThreadPoolExecutor(max_workers=len(residential_proxies)) as executor:
        futures = {
            executor.submit(process_proxy_batch, proxy, batch): proxy['name']
            for proxy, batch in proxy_assignments
        }

        for future in as_completed(futures):
            saved = future.result()
            total_saved += saved

            # Progress update
            stats = metrics.get_stats()
            if stats['processed'] % 500 == 0:
                logger.info(
                    f"Overall progress: {stats['processed']}/{len(all_tickers)} | "
                    f"Success: {stats['success_rate']*100:.1f}% | "
                    f"Rate: {stats['throughput']:.1f}/s"
                )

    # Final results
    stats = metrics.get_stats()

    logger.info("")
    logger.info("="*70)
    logger.info("SCAN COMPLETE")
    logger.info("="*70)
    logger.info(f"Runtime: {stats['elapsed']:.1f}s ({stats['elapsed']/60:.2f} min)")
    logger.info(f"Processed: {stats['processed']}")
    logger.info(f"Successful: {stats['successful']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info(f"Saved to DB: {total_saved}")
    logger.info(f"Success rate: {stats['success_rate']*100:.1f}%")
    logger.info(f"Throughput: {stats['throughput']:.2f} tickers/sec")
    logger.info("")

    # Bandwidth usage per proxy
    logger.info("BANDWIDTH USAGE PER PROXY:")
    logger.info("-"*70)
    all_usage = bandwidth_tracker.get_all_usage()
    total_bandwidth = 0

    for proxy in residential_proxies:
        proxy_name = proxy['name']
        usage_bytes = all_usage.get(proxy_name, 0)
        usage_mb = usage_bytes / 1024 / 1024
        max_mb = proxy.get('max_bandwidth_mb', 1024)
        percent = (usage_mb / max_mb) * 100

        total_bandwidth += usage_bytes

        logger.info(f"{proxy_name}: {usage_mb:.2f} MB / {max_mb} MB ({percent:.1f}%)")

    total_mb = total_bandwidth / 1024 / 1024
    logger.info(f"Total bandwidth: {total_mb:.2f} MB")
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
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\nScan interrupted by user")
    except Exception as e:
        logger.error(f"\nError during scan: {e}")
        import traceback
        traceback.print_exc()
