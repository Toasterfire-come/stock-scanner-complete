#!/usr/bin/env python3
"""
Test Aggressive Scanner Configuration
======================================
Tests both scanners with 1000 and 2000 tickers to verify:
1. Daily scanner: 0.488 t/s rate, completes in expected time
2. 10-min scanner: 15 t/s rate, completes in expected time
3. Proxy usage >70%
4. Success rate >90%
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")
import django
django.setup()

from stocks.models import Stock

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("test_aggressive")

# Suppress yfinance noise
logging.getLogger("yfinance").setLevel(logging.ERROR)

def test_daily_scanner(num_tickers=1000):
    """Test daily scanner with aggressive 0.488 t/s rate"""
    logger.info("="*80)
    logger.info(f"TEST: Daily Scanner (0.488 t/s) - {num_tickers} tickers")
    logger.info("="*80)

    # Import scanner module
    sys.path.insert(0, str(Path(__file__).parent))
    import realtime_daily_with_proxies as daily

    # Get test tickers
    tickers = list(Stock.objects.values_list('ticker', flat=True)[:num_tickers])
    logger.info(f"Testing with {len(tickers)} tickers")

    # Expected time
    expected_time = len(tickers) / daily.TARGET_RATE
    logger.info(f"Expected time: {expected_time:.1f}s ({expected_time/60:.1f} min)")
    logger.info(f"Target rate: {daily.TARGET_RATE} t/s")
    logger.info(f"Threads: {daily.MAX_THREADS}")
    logger.info("")

    # Load proxies
    daily.proxy_list = daily.load_proxies()
    logger.info(f"Loaded {len(daily.proxy_list)} proxies")
    logger.info("")

    # Test scanning
    start_time = time.time()
    success_count = 0
    failed_count = 0
    proxy_used_count = 0

    from concurrent.futures import ThreadPoolExecutor, as_completed

    with ThreadPoolExecutor(max_workers=daily.MAX_THREADS) as executor:
        future_to_ticker = {
            executor.submit(daily.fetch_stock_with_proxy, ticker): ticker
            for ticker in tickers
        }

        for i, future in enumerate(as_completed(future_to_ticker), 1):
            ticker = future_to_ticker[future]

            try:
                data = future.result()

                if data:
                    success_count += 1
                    if data.get('used_proxy'):
                        proxy_used_count += 1
                else:
                    failed_count += 1

                # Progress every 100
                if i % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = i / elapsed if elapsed > 0 else 0
                    success_rate = (success_count / i) * 100
                    proxy_usage = (proxy_used_count / success_count * 100) if success_count > 0 else 0

                    logger.info(
                        f"Progress: {i}/{len(tickers)} ({i/len(tickers)*100:.0f}%) | "
                        f"Success: {success_rate:.0f}% | "
                        f"Proxy: {proxy_usage:.0f}% | "
                        f"Rate: {rate:.2f} t/s"
                    )

            except Exception as e:
                logger.error(f"Error processing {ticker}: {e}")
                failed_count += 1

    # Results
    elapsed = time.time() - start_time
    actual_rate = len(tickers) / elapsed if elapsed > 0 else 0
    success_rate = (success_count / len(tickers)) * 100
    proxy_usage = (proxy_used_count / success_count * 100) if success_count > 0 else 0

    logger.info("")
    logger.info("="*80)
    logger.info("DAILY SCANNER TEST RESULTS")
    logger.info("="*80)
    logger.info(f"Tickers: {len(tickers)}")
    logger.info(f"Success: {success_count} ({success_rate:.1f}%)")
    logger.info(f"Failed: {failed_count}")
    logger.info(f"Proxy usage: {proxy_used_count}/{success_count} ({proxy_usage:.0f}%)")
    logger.info(f"Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    logger.info(f"Expected: {expected_time:.1f}s ({expected_time/60:.1f} min)")
    logger.info(f"Rate: {actual_rate:.3f} t/s (target: {daily.TARGET_RATE} t/s)")
    logger.info("")

    # Verify
    rate_ok = abs(actual_rate - daily.TARGET_RATE) / daily.TARGET_RATE < 0.1  # Within 10%
    success_ok = success_rate >= 90
    proxy_ok = proxy_usage >= 70

    if rate_ok:
        logger.info(f"[OK] Rate within 10% of target")
    else:
        logger.warning(f"[FAIL] Rate not within 10% of target")

    if success_ok:
        logger.info(f"[OK] Success rate >= 90%")
    else:
        logger.warning(f"[FAIL] Success rate < 90%")

    if proxy_ok:
        logger.info(f"[OK] Proxy usage >= 70%")
    else:
        logger.warning(f"[FAIL] Proxy usage < 70%")

    logger.info("="*80)
    logger.info("")

    return {
        'success_rate': success_rate,
        'proxy_usage': proxy_usage,
        'actual_rate': actual_rate,
        'elapsed': elapsed,
        'rate_ok': rate_ok,
        'success_ok': success_ok,
        'proxy_ok': proxy_ok
    }

def test_10min_scanner(num_tickers=1000):
    """Test 10-min scanner with aggressive 15 t/s rate"""
    logger.info("="*80)
    logger.info(f"TEST: 10-Min Scanner (15 t/s) - {num_tickers} tickers")
    logger.info("="*80)

    # Import scanner module
    sys.path.insert(0, str(Path(__file__).parent))
    import scanner_10min_fast as fast

    # Get test tickers
    tickers = list(Stock.objects.values_list('ticker', flat=True)[:num_tickers])
    logger.info(f"Testing with {len(tickers)} tickers")

    # Expected time
    expected_time = len(tickers) / fast.TARGET_RATE
    logger.info(f"Expected time: {expected_time:.1f}s ({expected_time/60:.1f} min)")
    logger.info(f"Target rate: {fast.TARGET_RATE} t/s")
    logger.info(f"Threads: {fast.MAX_THREADS}")
    logger.info(f"Timeout: {fast.TIMEOUT}s (fail fast)")
    logger.info(f"Retries: {fast.MAX_RETRIES} (fail fast)")
    logger.info("")

    # Load proxies
    fast.proxy_list = fast.load_proxies()
    logger.info(f"Loaded {len(fast.proxy_list)} proxies")
    logger.info("")

    # Test scanning
    start_time = time.time()
    success_count = 0
    failed_count = 0
    proxy_used_count = 0

    from concurrent.futures import ThreadPoolExecutor, as_completed

    with ThreadPoolExecutor(max_workers=fast.MAX_THREADS) as executor:
        future_to_ticker = {
            executor.submit(fast.fetch_10min_fast, ticker): ticker
            for ticker in tickers
        }

        for i, future in enumerate(as_completed(future_to_ticker), 1):
            ticker = future_to_ticker[future]

            try:
                data = future.result()

                if data:
                    success_count += 1
                    if data.get('used_proxy'):
                        proxy_used_count += 1
                else:
                    failed_count += 1

                # Progress every 100
                if i % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = i / elapsed if elapsed > 0 else 0
                    success_rate = (success_count / i) * 100
                    proxy_usage = (proxy_used_count / success_count * 100) if success_count > 0 else 0

                    logger.info(
                        f"Progress: {i}/{len(tickers)} ({i/len(tickers)*100:.0f}%) | "
                        f"Success: {success_rate:.0f}% | "
                        f"Proxy: {proxy_usage:.0f}% | "
                        f"Rate: {rate:.1f} t/s"
                    )

            except Exception as e:
                logger.error(f"Error processing {ticker}: {e}")
                failed_count += 1

    # Results
    elapsed = time.time() - start_time
    actual_rate = len(tickers) / elapsed if elapsed > 0 else 0
    success_rate = (success_count / len(tickers)) * 100
    proxy_usage = (proxy_used_count / success_count * 100) if success_count > 0 else 0

    logger.info("")
    logger.info("="*80)
    logger.info("10-MIN SCANNER TEST RESULTS")
    logger.info("="*80)
    logger.info(f"Tickers: {len(tickers)}")
    logger.info(f"Success: {success_count} ({success_rate:.1f}%)")
    logger.info(f"Failed: {failed_count}")
    logger.info(f"Proxy usage: {proxy_used_count}/{success_count} ({proxy_usage:.0f}%)")
    logger.info(f"Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    logger.info(f"Expected: {expected_time:.1f}s ({expected_time/60:.1f} min)")
    logger.info(f"Rate: {actual_rate:.1f} t/s (target: {fast.TARGET_RATE} t/s)")
    logger.info("")

    # Verify
    rate_ok = abs(actual_rate - fast.TARGET_RATE) / fast.TARGET_RATE < 0.15  # Within 15% (more lenient for fast scanner)
    success_ok = success_rate >= 90
    proxy_ok = proxy_usage >= 70

    if rate_ok:
        logger.info(f"[OK] Rate within 15% of target")
    else:
        logger.warning(f"[FAIL] Rate not within 15% of target")

    if success_ok:
        logger.info(f"[OK] Success rate >= 90%")
    else:
        logger.warning(f"[FAIL] Success rate < 90%")

    if proxy_ok:
        logger.info(f"[OK] Proxy usage >= 70%")
    else:
        logger.warning(f"[FAIL] Proxy usage < 70%")

    logger.info("="*80)
    logger.info("")

    return {
        'success_rate': success_rate,
        'proxy_usage': proxy_usage,
        'actual_rate': actual_rate,
        'elapsed': elapsed,
        'rate_ok': rate_ok,
        'success_ok': success_ok,
        'proxy_ok': proxy_ok
    }

if __name__ == "__main__":
    logger.info("="*80)
    logger.info("AGGRESSIVE SCANNER CONFIGURATION TEST")
    logger.info("="*80)
    logger.info(f"Start time: {datetime.now().strftime('%I:%M:%S %p')}")
    logger.info("")

    # Test 1: Daily scanner with 1000 tickers
    daily_1000 = test_daily_scanner(1000)

    logger.info("\n" + "="*80 + "\n")
    time.sleep(5)  # Small break

    # Test 2: 10-min scanner with 1000 tickers
    fast_1000 = test_10min_scanner(1000)

    # Final summary
    logger.info("\n" + "="*80)
    logger.info("FINAL SUMMARY")
    logger.info("="*80)
    logger.info("")
    logger.info("Daily Scanner (1000 tickers):")
    logger.info(f"  Rate: {daily_1000['actual_rate']:.3f} t/s (target: 0.488 t/s)")
    logger.info(f"  Success: {daily_1000['success_rate']:.1f}%")
    logger.info(f"  Proxy usage: {daily_1000['proxy_usage']:.0f}%")
    logger.info(f"  Status: {'[PASS]' if all([daily_1000['rate_ok'], daily_1000['success_ok'], daily_1000['proxy_ok']]) else '[FAIL]'}")
    logger.info("")
    logger.info("10-Min Scanner (1000 tickers):")
    logger.info(f"  Rate: {fast_1000['actual_rate']:.1f} t/s (target: 15 t/s)")
    logger.info(f"  Success: {fast_1000['success_rate']:.1f}%")
    logger.info(f"  Proxy usage: {fast_1000['proxy_usage']:.0f}%")
    logger.info(f"  Status: {'[PASS]' if all([fast_1000['rate_ok'], fast_1000['success_ok'], fast_1000['proxy_ok']]) else '[FAIL]'}")
    logger.info("")
    logger.info("="*80)
    logger.info(f"End time: {datetime.now().strftime('%I:%M:%S %p')}")
    logger.info("="*80)
