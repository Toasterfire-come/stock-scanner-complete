#!/usr/bin/env python3
"""
Test All Scanners with 1000 Tickers
====================================
Identifies specific failure points in each scanner under load
"""

import os
import sys
import django
import time
import traceback
from datetime import datetime

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")
django.setup()

from stocks.models import Stock

def test_section(title):
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80 + "\n")

# Get exactly 1000 tickers
print("Loading exactly 1000 tickers for testing...")
test_tickers = list(Stock.objects.values_list('ticker', flat=True)[:1000])
print(f"[OK] Loaded {len(test_tickers)} tickers\n")

# ============================================================================
# TEST 1: Daily Scanner - realtime_daily_yfinance.py
# ============================================================================
test_section("TEST 1: Daily Scanner (realtime_daily_yfinance.py)")

try:
    from realtime_daily_yfinance import fetch_stock_yfinance, batch_update_stocks
    import yfinance as yf
    from concurrent.futures import ThreadPoolExecutor, as_completed

    print("Configuration:")
    print("  - MAX_THREADS: 50")
    print("  - BATCH_SIZE: 100")
    print("  - TIMEOUT: 15.0s")
    print("  - Method: yfinance direct (no proxies)\n")

    start_time = time.time()
    results = []
    success = 0
    failed = 0
    errors = {}

    # Test with threading (like production)
    print("Testing with 100 tickers (sample)...")
    with ThreadPoolExecutor(max_workers=50) as executor:
        future_to_ticker = {
            executor.submit(fetch_stock_yfinance, ticker): ticker
            for ticker in test_tickers[:100]
        }

        for i, future in enumerate(as_completed(future_to_ticker), 1):
            ticker = future_to_ticker[future]
            try:
                data = future.result()
                if data:
                    results.append(data)
                    success += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                error_type = type(e).__name__
                errors[error_type] = errors.get(error_type, 0) + 1
                if i <= 5:  # Show first 5 errors
                    print(f"  ERROR {ticker}: {e}")

    # Test database batch update
    db_updated = 0
    db_failed = 0
    if results:
        try:
            db_updated, db_failed = batch_update_stocks(results)
        except Exception as e:
            print(f"  DATABASE ERROR: {e}")
            traceback.print_exc()

    elapsed = time.time() - start_time

    print(f"\nResults:")
    print(f"  Total tested: 100")
    print(f"  Successful: {success} ({success/100*100:.1f}%)")
    print(f"  Failed: {failed}")
    print(f"  DB Updated: {db_updated}")
    print(f"  DB Failed: {db_failed}")
    print(f"  Time: {elapsed:.1f}s")
    print(f"  Rate: {100/elapsed:.1f} tickers/sec")
    if errors:
        print(f"  Error types: {errors}")

    # Check for issues
    if success < 50:
        print("\n  ⚠️  ISSUE: Less than 50% success rate - likely rate limiting")
    if elapsed > 60:
        print(f"\n  ⚠️  ISSUE: Too slow ({elapsed:.1f}s > 60s target)")
    if db_failed > 0:
        print(f"\n  ⚠️  ISSUE: Database update failures ({db_failed})")

except Exception as e:
    print(f"✗ TEST FAILED: {e}")
    traceback.print_exc()

# ============================================================================
# TEST 2: Scheduled Daily Scanner - run_daily_scanner_scheduled.py
# ============================================================================
test_section("TEST 2: Scheduled Daily Scanner (run_daily_scanner_scheduled.py)")

try:
    from realtime_daily_yfinance import fetch_stock_yfinance, batch_update_stocks
    from concurrent.futures import ThreadPoolExecutor, as_completed

    print("Configuration:")
    print("  - STOCKS_PER_BATCH: 500")
    print("  - DELAY_BETWEEN_BATCHES: 60s")
    print("  - MAX_THREADS: 30")
    print("  - Method: Batch with rate limiting\n")

    # Test one batch (500 stocks, but we'll use 100 for speed)
    print("Testing one batch (100 tickers with rate limiting logic)...")

    batch = test_tickers[:100]
    start_time = time.time()
    results = []
    success = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=30) as executor:
        future_to_ticker = {
            executor.submit(fetch_stock_yfinance, ticker): ticker
            for ticker in batch
        }

        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                data = future.result()
                if data:
                    results.append(data)
                    success += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1

    # Database update
    db_updated = 0
    if results:
        db_updated, _ = batch_update_stocks(results)

    elapsed = time.time() - start_time

    print(f"\nResults:")
    print(f"  Batch size: 100")
    print(f"  Successful: {success} ({success/100*100:.1f}%)")
    print(f"  Failed: {failed}")
    print(f"  DB Updated: {db_updated}")
    print(f"  Time: {elapsed:.1f}s")
    print(f"  Rate: {100/elapsed:.1f} tickers/sec")

    # Estimate full run
    estimated_time = (1000 / 500) * (elapsed + 60)  # 2 batches with 60s delay
    print(f"\n  Estimated time for 1000 tickers: {estimated_time/60:.1f} min")

    if success < 50:
        print("\n  ⚠️  ISSUE: Less than 50% success rate")

except Exception as e:
    print(f"✗ TEST FAILED: {e}")
    traceback.print_exc()

# ============================================================================
# TEST 3: 10-Min Scanner - scanner_10min_metrics_improved.py
# ============================================================================
test_section("TEST 3: 10-Minute Scanner (scanner_10min_metrics_improved.py)")

try:
    from scanner_10min_metrics_improved import ImprovedMetricsScanner

    scanner = ImprovedMetricsScanner()

    print("Configuration:")
    print(f"  - BATCH_SIZE: 50")
    print(f"  - Proxies loaded: {len(scanner.proxies)}")
    print(f"  - No-proxy fallback: {scanner.no_proxy_fallback}")
    print(f"  - MAX_RETRIES: 3\n")

    # Test one batch
    print("Testing one batch (50 tickers)...")
    batch = test_tickers[:50]

    start_time = time.time()
    results = scanner.fetch_batch_metrics(batch)

    success_count = sum(1 for r in results.values() if r.get('success'))
    failed_count = len(batch) - success_count

    # Update database
    updated = 0
    for ticker, data in results.items():
        if scanner.update_database(ticker, data):
            updated += 1

    elapsed = time.time() - start_time

    print(f"\nResults:")
    print(f"  Batch size: 50")
    print(f"  Successful: {success_count} ({success_count/50*100:.1f}%)")
    print(f"  Failed: {failed_count}")
    print(f"  DB Updated: {updated}")
    print(f"  Time: {elapsed:.1f}s")
    print(f"  Rate: {50/elapsed:.1f} tickers/sec")
    print(f"  Proxy failures: {scanner.stats.get('proxy_failures', 0)}")
    print(f"  No-proxy successes: {scanner.stats.get('no_proxy_success', 0)}")

    # Estimate full run
    batches_needed = 1000 / 50
    estimated_time = batches_needed * (elapsed + 2)  # +2s delay between batches
    print(f"\n  Estimated time for 1000 tickers: {estimated_time/60:.1f} min")

    if success_count < 25:
        print("\n  ⚠️  ISSUE: Less than 50% success rate")
    if scanner.stats.get('proxy_failures', 0) > 10:
        print(f"\n  ⚠️  ISSUE: High proxy failure rate")

except Exception as e:
    print(f"✗ TEST FAILED: {e}")
    traceback.print_exc()

# ============================================================================
# TEST 4: 1-Min Scanner - scanner_1min_hybrid.py
# ============================================================================
test_section("TEST 4: 1-Minute Scanner (scanner_1min_hybrid.py)")

try:
    import asyncio
    from scanner_1min_hybrid import OneMinuteScanner

    print("Configuration:")
    print("  - Method: WebSocket streaming")
    print("  - Timeout: 60s")
    print("  - Expected: Real-time price updates\n")

    async def test_1min():
        scanner = OneMinuteScanner()

        # Get small sample
        tickers = test_tickers[:100]

        print(f"Testing WebSocket with {len(tickers)} tickers...")
        print("NOTE: WebSocket requires market hours for real data\n")

        start_time = time.time()

        try:
            await scanner.fetch_realtime_prices_websocket(tickers, timeout=10)
            elapsed = time.time() - start_time

            updates = len(scanner.websocket_updates)

            print(f"Results:")
            print(f"  Tickers requested: {len(tickers)}")
            print(f"  WebSocket updates: {updates}")
            print(f"  Success rate: {updates/len(tickers)*100:.1f}%")
            print(f"  Time: {elapsed:.1f}s")

            if updates == 0:
                print("\n  ⚠️  ISSUE: No WebSocket updates (market closed or connection failed)")
            elif updates < len(tickers) * 0.5:
                print("\n  ⚠️  ISSUE: Less than 50% updates received")

        except Exception as e:
            print(f"  WebSocket error: {e}")
            print("\n  ⚠️  ISSUE: WebSocket connection failed")
            print("  This is expected outside market hours or without streaming access")

    asyncio.run(test_1min())

except Exception as e:
    print(f"✗ TEST FAILED: {e}")
    print("WebSocket scanner requires asyncio support")

# ============================================================================
# SUMMARY
# ============================================================================
test_section("TEST SUMMARY")

print("Key Findings:")
print("")
print("1. Daily Scanner (realtime_daily_yfinance.py):")
print("   - Check success rate above")
print("   - Look for rate limiting issues")
print("   - Verify database updates work")
print("")
print("2. Scheduled Daily Scanner (run_daily_scanner_scheduled.py):")
print("   - Tests batching with delays")
print("   - Should handle rate limits better")
print("   - Check estimated time for full run")
print("")
print("3. 10-Min Scanner (scanner_10min_metrics_improved.py):")
print("   - Tests proxy rotation and fallback")
print("   - Check proxy failure rate")
print("   - Verify no-proxy fallback works")
print("")
print("4. 1-Min Scanner (scanner_1min_hybrid.py):")
print("   - WebSocket-based (no HTTP rate limits)")
print("   - Requires market hours for real data")
print("   - May show 0% success outside market hours")
print("")
print("=" * 80)
print("Run this test to identify specific failure points before fixing!")
print("=" * 80)
