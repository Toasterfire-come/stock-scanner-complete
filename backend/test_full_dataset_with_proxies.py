#!/usr/bin/env python3
"""
Test Real-Time Updater with Full Dataset and OS-Level Proxy Switching
=====================================================================

Tests the real-time price updater with all 5,193 tickers using OS-level
proxy management and automatic proxy switching on rate limits.
"""

import os
import sys
import time
import json
import logging
from datetime import datetime

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")

import django
django.setup()

from stock_retrieval.config import StockRetrievalConfig
from stock_retrieval.ticker_loader import load_combined_tickers
from stock_retrieval.session_factory import ProxyPool
from proxy_manager import ProxyManager
from realtime_price_updater import PriceUpdater, CONFIG, logger as base_logger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedPriceUpdater(PriceUpdater):
    """Enhanced updater with OS-level proxy switching and rate limit handling"""

    def __init__(self, proxy_manager: ProxyManager):
        # Initialize parent without proxy pool (we'll use OS-level)
        super().__init__(use_proxies=False)
        self.proxy_manager = proxy_manager
        self.rate_limit_count = 0
        self.proxy_switches = 0

    def update_prices(self, symbols):
        """Override to add rate limit detection and proxy switching"""

        total = len(symbols)
        results = []
        batch = []
        consecutive_failures = 0
        max_consecutive_failures = 50  # Switch proxy after 50 consecutive failures

        logger.info(f"Updating prices for {total} tickers...")
        logger.info(f"Using OS-level proxy management with {len(self.proxy_manager.proxies)} proxies")

        from concurrent.futures import ThreadPoolExecutor, as_completed

        with ThreadPoolExecutor(max_workers=self.metrics.current_workers) as executor:
            futures = {
                executor.submit(self.fetch_price, symbol, i % self.metrics.current_workers): symbol
                for i, symbol in enumerate(symbols)
            }

            for future in as_completed(futures):
                try:
                    result = future.result()

                    if result:
                        results.append(result)
                        batch.append(result)
                        consecutive_failures = 0  # Reset on success

                        # Stream write in batches if enabled
                        if CONFIG.stream_writes and len(batch) >= CONFIG.batch_size:
                            self._write_batch(batch)
                            with self.lock:
                                self.metrics.updates += len(batch)
                            batch = []
                    else:
                        consecutive_failures += 1

                        # Check if we should switch proxy
                        if consecutive_failures >= max_consecutive_failures:
                            logger.warning(f"{consecutive_failures} consecutive failures detected")
                            if self.proxy_manager.handle_rate_limit():
                                self.proxy_switches += 1
                                logger.info(f"Switched to proxy {self.proxy_switches}")
                                consecutive_failures = 0  # Reset after switch
                                time.sleep(2)  # Brief pause after switching

                except Exception as e:
                    # Check if it's a rate limit error
                    if ProxyManager.detect_rate_limit(e):
                        self.rate_limit_count += 1
                        logger.warning(f"Rate limit detected (#{self.rate_limit_count}): {str(e)[:100]}")

                        if self.proxy_manager.handle_rate_limit():
                            self.proxy_switches += 1
                            logger.info(f"Switched to proxy {self.proxy_switches}")
                            time.sleep(2)  # Brief pause after switching
                            consecutive_failures = 0

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
                        f"ETA: {eta:.0f}s | "
                        f"Switches: {self.proxy_switches}"
                    )

            # Write remaining batch
            if batch:
                self._write_batch(batch)
                with self.lock:
                    self.metrics.updates += len(batch)

        return results


def main():
    """Test with full dataset using OS-level proxy switching"""

    logger.info("=" * 70)
    logger.info("FULL DATASET TEST - WITH OS-LEVEL PROXY SWITCHING")
    logger.info("=" * 70)
    logger.info("Testing real-time updater with all tickers")
    logger.info("Using OS-level proxy management with automatic switching")
    logger.info("")

    # Load proxies
    logger.info("Loading proxy pool...")
    try:
        config = StockRetrievalConfig()
        proxy_pool = ProxyPool.from_config(config)
        proxy_manager = ProxyManager.from_proxy_pool(proxy_pool)
        logger.info(f"Loaded {len(proxy_manager.proxies)} proxies")
    except Exception as e:
        logger.warning(f"Failed to load proxies: {e}")
        logger.info("Running WITHOUT proxies (direct connection)")
        proxy_manager = ProxyManager(proxies=[])

    # Load all tickers
    logger.info("\nLoading tickers...")
    result = load_combined_tickers(config)
    tickers = result.tickers
    logger.info(f"Loaded {len(tickers)} tickers\n")

    # Create enhanced updater with proxy manager
    updater = EnhancedPriceUpdater(proxy_manager)

    # Set initial proxy if available
    if proxy_manager.proxies:
        proxy_manager.switch_proxy()

    # Run test
    logger.info("=" * 70)
    logger.info("STARTING FULL DATASET FETCH")
    logger.info("=" * 70)
    logger.info(f"Workers: {CONFIG.initial_workers}")
    logger.info(f"Delays: {CONFIG.min_delay*1000:.1f}-{CONFIG.max_delay*1000:.1f}ms")
    logger.info(f"Target: <180s with >95% success")
    logger.info("")

    start_time = time.time()

    try:
        results = updater.update_prices(tickers)
    finally:
        # Always clear proxies when done
        proxy_manager.clear()

    test_time = time.time() - start_time

    # Results
    logger.info("")
    logger.info("=" * 70)
    logger.info("FULL DATASET TEST COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Runtime: {test_time:.2f}s ({test_time/60:.2f} min)")
    logger.info(f"Success: {len(results)}/{len(tickers)} ({len(results)/len(tickers)*100:.1f}%)")
    logger.info(f"Throughput: {len(tickers)/test_time:.2f} tickers/sec")
    logger.info(f"DB Updates: {updater.metrics.updates}")
    logger.info(f"Rate Limits: {updater.rate_limit_count}")
    logger.info(f"Proxy Switches: {updater.proxy_switches}")
    logger.info("")

    # Check if targets met
    success_rate = len(results) / len(tickers)
    target_met = test_time < 180 and success_rate > 0.95

    if target_met:
        logger.info("[SUCCESS] Met all targets!")
        logger.info(f"  ✅ Runtime: {test_time:.2f}s (target: <180s)")
        logger.info(f"  ✅ Success: {success_rate*100:.1f}% (target: >95%)")
    else:
        logger.info("[RESULTS] Performance summary:")
        if test_time >= 180:
            logger.info(f"  ⚠️  Runtime: {test_time:.2f}s (target: <180s) - {test_time-180:.1f}s over")
        else:
            logger.info(f"  ✅ Runtime: {test_time:.2f}s (target: <180s)")

        if success_rate <= 0.95:
            logger.info(f"  ⚠️  Success: {success_rate*100:.1f}% (target: >95%) - {(0.95-success_rate)*100:.1f}% under")
        else:
            logger.info(f"  ✅ Success: {success_rate*100:.1f}% (target: >95%)")

    # Save metrics
    metrics = {
        'test_type': 'full_dataset_with_os_proxies',
        'runtime_seconds': round(test_time, 2),
        'runtime_minutes': round(test_time / 60, 2),
        'total_tickers': len(tickers),
        'successful': len(results),
        'failed': len(tickers) - len(results),
        'success_rate': round(success_rate * 100, 2),
        'throughput': round(len(tickers) / test_time, 2),
        'db_updates': updater.metrics.updates,
        'rate_limits': updater.rate_limit_count,
        'proxy_switches': updater.proxy_switches,
        'proxies_used': len(proxy_manager.proxies),
        'target_met': target_met,
        'timestamp': datetime.now().isoformat()
    }

    metrics_file = f"full_test_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)

    logger.info(f"\nMetrics saved: {metrics_file}")
    logger.info("=" * 70)

if __name__ == "__main__":
    main()
