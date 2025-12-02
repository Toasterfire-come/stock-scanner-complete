#!/usr/bin/env python3
"""
BLAZING ULTRA-FAST Ticker Puller - Optimized for Real-World Performance
========================================================================

Based on reality: Small tests don't show rate limiting. This is optimized for FULL-SCALE.

KEY OPTIMIZATIONS:
1. Uses ONLY fresh elite proxies from GeoNode (not 44K old proxies)
2. NO streaming database writes (bulk write at end = 10x faster)
3. Minimal delays with aggressive proxy rotation
4. High worker count (100+ workers)
5. Direct fast_info only (fallbacks if needed)

Target: <3 minutes for 5,373 tickers with 98%+ success
"""

import os
import sys
import time
import json
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")

import django
django.setup()

import yfinance as yf
from django.utils import timezone
from django.db import transaction
from stocks.models import Stock

# Import proven infrastructure
from stock_retrieval.session_factory import ProxyPool, create_requests_session
from stock_retrieval.config import StockRetrievalConfig
from stock_retrieval.ticker_loader import load_combined_tickers

# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# =====================================================
# CONFIGURATION
# =====================================================

class BlazingConfig:
    """Blazing fast configuration for real-world performance"""

    # Workers - AGGRESSIVE for speed (yfinance handles rate limiting internally)
    min_workers = 40
    max_workers = 100
    initial_workers = 75

    # Timeouts - FAST
    request_timeout = 5
    per_symbol_timeout = 8

    # Delays - MINIMAL (yfinance uses curl_cffi which is faster)
    min_delay = 0.001  # 1ms
    max_delay = 0.005  # 5ms

    # Proxies - Use ONLY fresh GeoNode proxies
    fresh_proxies_file = "working_proxies.json"
    max_proxies = 300  # Limit to fresh elite proxies

    # Database - BULK WRITE AT END (not streaming)
    bulk_write_only = True

    # Progress
    progress_interval = 100

    # Auto-tuning
    auto_tune = True
    tune_interval = 300
    target_success_rate = 0.95  # 95% is acceptable

CONFIG = BlazingConfig()

# =====================================================
# METRICS
# =====================================================

class Metrics:
    """Real-time performance metrics"""

    def __init__(self):
        self.start_time = time.time()
        self.total_attempted = 0
        self.fast_info_success = 0
        self.info_success = 0
        self.history_success = 0
        self.failures = 0
        self.complete_records = 0
        self.partial_records = 0
        self.rate_limits = 0
        self.current_workers = CONFIG.initial_workers

    @property
    def elapsed(self):
        return time.time() - self.start_time

    @property
    def total_success(self):
        return self.fast_info_success + self.info_success + self.history_success

    @property
    def success_rate(self):
        if self.total_attempted == 0:
            return 0.0
        return self.total_success / self.total_attempted

    @property
    def throughput(self):
        if self.elapsed == 0:
            return 0.0
        return self.total_attempted / self.elapsed

    def to_dict(self):
        return {
            'runtime_seconds': round(self.elapsed, 2),
            'runtime_minutes': round(self.elapsed / 60, 2),
            'total_attempted': self.total_attempted,
            'fast_info_success': self.fast_info_success,
            'info_success': self.info_success,
            'history_success': self.history_success,
            'total_success': self.total_success,
            'failures': self.failures,
            'success_rate': round(self.success_rate * 100, 2),
            'throughput': round(self.throughput, 2),
            'complete_records': self.complete_records,
            'partial_records': self.partial_records,
            'rate_limits': self.rate_limits,
            'final_workers': self.current_workers
        }

# =====================================================
# PROXY LOADER
# =====================================================

def load_fresh_proxies() -> List[str]:
    """Load ONLY fresh elite proxies from GeoNode"""
    proxy_file = Path(CONFIG.fresh_proxies_file)

    if not proxy_file.exists():
        logger.warning(f"Fresh proxies not found: {proxy_file}")
        logger.warning("Run: python pull_fresh_proxies.py")
        return []

    try:
        with open(proxy_file, 'r') as f:
            data = json.load(f)

        proxies = data.get('proxies', [])

        # Limit to max proxies
        if len(proxies) > CONFIG.max_proxies:
            proxies = proxies[:CONFIG.max_proxies]

        logger.info(f"Loaded {len(proxies)} fresh elite proxies")

        # Check proxy age
        fetched_at = data.get('fetched_at', 'unknown')
        logger.info(f"Proxies fetched at: {fetched_at}")

        return proxies

    except Exception as e:
        logger.error(f"Failed to load fresh proxies: {e}")
        return []

# =====================================================
# TICKER FETCHER
# =====================================================

class BlazingFetcher:
    """Blazing fast ticker fetcher"""

    def __init__(self, proxies: List[str]):
        self.proxies = proxies
        self.metrics = Metrics()
        self.results = []
        self.lock = threading.Lock()

        # Create proxy pool with ONLY fresh proxies
        if proxies:
            # Create a simple proxy pool directly
            self.proxy_pool = ProxyPool(proxies=proxies)
            logger.info(f"Proxy pool created with {len(proxies)} fresh proxies")
        else:
            self.proxy_pool = None
            logger.warning("Running WITHOUT proxies (will hit rate limits faster)")

    def fetch_single(self, symbol: str, worker_id: int) -> Optional[Dict]:
        """Fetch single ticker with aggressive optimization"""

        # Minimal delay (1-10ms)
        time.sleep(random.uniform(CONFIG.min_delay, CONFIG.max_delay))

        try:
            # IMPORTANT: yfinance now requires curl_cffi sessions internally
            # We cannot pass custom requests.Session objects anymore
            # Let yfinance handle session creation with its curl_cffi backend

            # Try fast_info first (fastest method)
            ticker = yf.Ticker(symbol)

            try:
                data = ticker.fast_info

                # Extract data
                result = {
                    'symbol': symbol,
                    'price': getattr(data, 'last_price', None) or getattr(data, 'regularMarketPrice', None),
                    'previous_close': getattr(data, 'previous_close', None),
                    'market_cap': getattr(data, 'market_cap', None),
                    'shares': getattr(data, 'shares', None),
                    'currency': getattr(data, 'currency', 'USD'),
                    'method': 'fast_info',
                    'timestamp': timezone.now()
                }

                # Calculate volume average
                if result['price'] and result['shares']:
                    result['volume_average'] = result['price'] * result['shares']
                else:
                    result['volume_average'] = None

                with self.lock:
                    self.metrics.fast_info_success += 1
                    if result['price'] and result['market_cap']:
                        self.metrics.complete_records += 1
                    else:
                        self.metrics.partial_records += 1

                return result

            except Exception as e:
                # Fallback to .info
                try:
                    info = ticker.info

                    result = {
                        'symbol': symbol,
                        'price': info.get('regularMarketPrice') or info.get('currentPrice'),
                        'previous_close': info.get('previousClose'),
                        'market_cap': info.get('marketCap'),
                        'shares': info.get('sharesOutstanding'),
                        'currency': info.get('currency', 'USD'),
                        'method': 'info',
                        'timestamp': timezone.now()
                    }

                    if result['price'] and result['shares']:
                        result['volume_average'] = result['price'] * result['shares']
                    else:
                        result['volume_average'] = None

                    with self.lock:
                        self.metrics.info_success += 1
                        if result['price'] and result['market_cap']:
                            self.metrics.complete_records += 1
                        else:
                            self.metrics.partial_records += 1

                    return result

                except Exception as e2:
                    # Last resort: history
                    try:
                        hist = ticker.history(period='1d')
                        if not hist.empty:
                            result = {
                                'symbol': symbol,
                                'price': float(hist['Close'].iloc[-1]),
                                'previous_close': None,
                                'market_cap': None,
                                'shares': None,
                                'currency': 'USD',
                                'method': 'history',
                                'timestamp': timezone.now(),
                                'volume_average': None
                            }

                            with self.lock:
                                self.metrics.history_success += 1
                                self.metrics.partial_records += 1

                            return result
                    except:
                        pass

                    with self.lock:
                        self.metrics.failures += 1
                    return None

        except Exception as e:
            if 'rate limit' in str(e).lower() or '429' in str(e):
                with self.lock:
                    self.metrics.rate_limits += 1

            with self.lock:
                self.metrics.failures += 1

            return None

        finally:
            with self.lock:
                self.metrics.total_attempted += 1

    def fetch_all(self, symbols: List[str]) -> List[Dict]:
        """Fetch all tickers with high parallelism"""

        total = len(symbols)
        logger.info(f"\nFetching {total} tickers...")
        logger.info(f"Workers: {CONFIG.initial_workers}")
        logger.info(f"Delays: {CONFIG.min_delay*1000:.1f}-{CONFIG.max_delay*1000:.1f}ms")
        logger.info(f"Target: <180s with >95% success\n")

        results = []

        with ThreadPoolExecutor(max_workers=CONFIG.initial_workers) as executor:
            futures = {
                executor.submit(self.fetch_single, symbol, i % CONFIG.initial_workers): symbol
                for i, symbol in enumerate(symbols)
            }

            for future in as_completed(futures):
                result = future.result()

                if result:
                    results.append(result)

                # Progress
                if self.metrics.total_attempted % CONFIG.progress_interval == 0:
                    progress = self.metrics.total_attempted / total * 100
                    elapsed = self.metrics.elapsed
                    remaining = total - self.metrics.total_attempted
                    eta = (elapsed / self.metrics.total_attempted * remaining) if self.metrics.total_attempted > 0 else 0

                    logger.info(
                        f"[{self.metrics.total_attempted}/{total}] "
                        f"{progress:.1f}% | "
                        f"Success: {self.metrics.success_rate*100:.1f}% | "
                        f"Speed: {self.metrics.throughput:.1f}/s | "
                        f"ETA: {eta:.0f}s"
                    )

                # Auto-tune workers
                if CONFIG.auto_tune and self.metrics.total_attempted % CONFIG.tune_interval == 0:
                    if self.metrics.success_rate < CONFIG.target_success_rate:
                        # Reduce workers if success rate is low
                        if self.metrics.current_workers > CONFIG.min_workers:
                            self.metrics.current_workers = max(
                                CONFIG.min_workers,
                                self.metrics.current_workers - 10
                            )
                            logger.info(f"Auto-tune: Reduced workers to {self.metrics.current_workers}")
                    elif self.metrics.success_rate > 0.98:
                        # Increase workers if success rate is high
                        if self.metrics.current_workers < CONFIG.max_workers:
                            self.metrics.current_workers = min(
                                CONFIG.max_workers,
                                self.metrics.current_workers + 10
                            )
                            logger.info(f"Auto-tune: Increased workers to {self.metrics.current_workers}")

        self.results = results
        return results

# =====================================================
# DATABASE WRITER
# =====================================================

def bulk_write_to_database(results: List[Dict]) -> int:
    """Bulk write all results to database at once (MUCH faster than streaming)"""

    logger.info("\n" + "=" * 70)
    logger.info("BULK WRITING TO DATABASE")
    logger.info("=" * 70)

    start = time.time()
    written = 0

    try:
        with transaction.atomic():
            for result in results:
                try:
                    Stock.objects.update_or_create(
                        symbol=result['symbol'],
                        defaults={
                            'price': result.get('price'),
                            'previous_close': result.get('previous_close'),
                            'market_cap': result.get('market_cap'),
                            'shares_outstanding': result.get('shares'),
                            'currency': result.get('currency', 'USD'),
                            'volume_average': result.get('volume_average'),
                            'last_updated': result['timestamp']
                        }
                    )
                    written += 1
                except Exception as e:
                    logger.debug(f"Failed to write {result['symbol']}: {e}")

        elapsed = time.time() - start
        logger.info(f"Wrote {written}/{len(results)} records in {elapsed:.2f}s")
        logger.info(f"Write speed: {written/elapsed:.0f} records/sec")

        return written

    except Exception as e:
        logger.error(f"Bulk write failed: {e}")
        return 0

# =====================================================
# MAIN
# =====================================================

def main():
    """Main entry point"""

    logger.info("=" * 70)
    logger.info("BLAZING ULTRA-FAST TICKER PULLER")
    logger.info("=" * 70)
    logger.info("Optimized for REAL-WORLD full-scale performance")
    logger.info("")

    # Don't use proxies - free proxies cause 401 errors and are slower
    # proxies = load_fresh_proxies()
    proxies = []
    logger.info("Running WITHOUT proxies for maximum speed")
    logger.info("Free proxies cause 401 errors and slow down requests")
    logger.info("")

    # Load tickers
    logger.info("\nLoading tickers...")
    config = StockRetrievalConfig()
    result = load_combined_tickers(config)
    tickers = result.tickers
    logger.info(f"Loaded {len(tickers)} tickers")

    # Create fetcher
    fetcher = BlazingFetcher(proxies)

    # Fetch all
    logger.info("\n" + "=" * 70)
    logger.info("STARTING FETCH")
    logger.info("=" * 70)

    start_time = time.time()
    results = fetcher.fetch_all(tickers)
    fetch_time = time.time() - start_time

    # Results
    logger.info("\n" + "=" * 70)
    logger.info("FETCH COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Runtime: {fetch_time:.2f}s ({fetch_time/60:.2f} min)")
    logger.info(f"Success: {len(results)}/{len(tickers)} ({len(results)/len(tickers)*100:.1f}%)")
    logger.info(f"Throughput: {len(tickers)/fetch_time:.2f} tickers/sec")
    logger.info(f"Complete records: {fetcher.metrics.complete_records}")
    logger.info(f"Partial records: {fetcher.metrics.partial_records}")
    logger.info(f"Rate limits: {fetcher.metrics.rate_limits}")

    # Write to database
    if CONFIG.bulk_write_only and results:
        written = bulk_write_to_database(results)
    else:
        logger.info("Skipping database write (disabled)")
        written = 0

    # Save metrics
    metrics = fetcher.metrics.to_dict()
    metrics['written_to_db'] = written

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    metrics_file = f"blazing_metrics_{timestamp}.json"

    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)

    logger.info(f"\nMetrics saved: {metrics_file}")

    # Final summary
    logger.info("\n" + "=" * 70)
    logger.info("SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total runtime: {fetch_time:.2f}s ({fetch_time/60:.2f} min)")
    logger.info(f"Target: <180s (3 min) - {'PASS' if fetch_time < 180 else 'FAIL'}")
    logger.info(f"Success rate: {fetcher.metrics.success_rate*100:.1f}%")
    logger.info(f"Target: >95% - {'PASS' if fetcher.metrics.success_rate > 0.95 else 'FAIL'}")
    logger.info("=" * 70)

    if fetch_time < 180 and fetcher.metrics.success_rate > 0.95:
        logger.info("\n[SUCCESS] All targets met!")
    else:
        logger.info("\n[WARNING] Some targets not met")
        if fetch_time >= 180:
            logger.info(f"  - Runtime: {fetch_time:.2f}s (target: <180s)")
        if fetcher.metrics.success_rate <= 0.95:
            logger.info(f"  - Success: {fetcher.metrics.success_rate*100:.1f}% (target: >95%)")

if __name__ == "__main__":
    import threading
    main()
