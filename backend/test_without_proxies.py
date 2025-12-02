#!/usr/bin/env python3
"""
Test Real-Time Price Updater WITHOUT Proxies
==============================================

Tests the real-time updater with direct connection (no proxies).
"""

import os
import sys

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")

import django
django.setup()

from realtime_price_updater import PriceUpdater, CONFIG, logger

# Test configuration
TEST_TICKERS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
    'NVDA', 'META', 'BRK.B', 'JPM', 'V'
]

def main():
    """Test the real-time updater WITHOUT proxies"""

    logger.info("=" * 70)
    logger.info("REAL-TIME UPDATER - DIRECT CONNECTION TEST")
    logger.info("=" * 70)
    logger.info(f"Testing with {len(TEST_TICKERS)} sample tickers")
    logger.info(f"Workers: {CONFIG.initial_workers}")
    logger.info(f"Delays: {CONFIG.min_delay*1000:.1f}-{CONFIG.max_delay*1000:.1f}ms")
    logger.info("Proxy: DISABLED (Direct connection)")
    logger.info("")

    # Create updater WITHOUT proxies
    logger.info("Initializing WITHOUT proxies...")
    updater = PriceUpdater(use_proxies=False)

    # Update prices for test tickers
    logger.info("=" * 70)
    logger.info("STARTING TEST FETCH WITHOUT PROXIES")
    logger.info("=" * 70)

    import time
    start_time = time.time()

    results = updater.update_prices(TEST_TICKERS)

    test_time = time.time() - start_time

    # Results
    logger.info("")
    logger.info("=" * 70)
    logger.info("TEST COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Runtime: {test_time:.2f}s")
    logger.info(f"Success: {len(results)}/{len(TEST_TICKERS)} ({len(results)/len(TEST_TICKERS)*100:.1f}%)")
    logger.info(f"Throughput: {len(TEST_TICKERS)/test_time:.2f} tickers/sec")
    logger.info(f"DB Updates: {updater.metrics.updates}")
    logger.info("")

    # Show sample results
    if results:
        logger.info("Sample Results:")
        for i, result in enumerate(results[:5]):
            logger.info(f"  {result['symbol']}: ${result.get('price', 'N/A')}")
        logger.info("")

    # Check if targets met
    success_rate = len(results) / len(TEST_TICKERS)
    if success_rate > 0.95:
        logger.info("[SUCCESS] Met >95% success target!")
    else:
        logger.info(f"[WARNING] Success rate: {success_rate*100:.1f}% (target: >95%)")

    logger.info("=" * 70)

if __name__ == "__main__":
    main()
