#!/usr/bin/env python3
"""
Production Load Testing - 1000 & 2000 Tickers
==============================================
Tests scanners under production constraints:

Daily Scanner:
- Target: 0.25 tickers/second (avoid rate limits)
- Threads: 20
- Tests: 1000 and 2000 tickers

10-Minute Scanner:
- Target: >1.5 tickers/second
- Threads: 20
- Tests: 1000 and 2000 tickers
"""

import os
import sys
import django
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")
django.setup()

from stocks.models import Stock

def test_header(title):
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80)

def test_scanner(scanner_name, fetch_func, batch_update_func, test_size, threads, target_rate, target_name):
    """
    Generic scanner test function

    Args:
        scanner_name: Name of scanner being tested
        fetch_func: Function to fetch data for a ticker
        batch_update_func: Function to batch update database
        test_size: Number of tickers to test (1000 or 2000)
        threads: Number of concurrent threads
        target_rate: Target tickers/second
        target_name: Description of target (e.g., "0.25 t/s for rate limits")
    """
    test_header(f"{scanner_name} - {test_size} Tickers - {threads} Threads")

    print(f"Test Configuration:")
    print(f"  Tickers: {test_size}")
    print(f"  Threads: {threads}")
    print(f"  Target Rate: {target_name}")
    print(f"  Started: {datetime.now().strftime('%H:%M:%S')}")
    print("")

    # Get test tickers
    tickers = list(Stock.objects.values_list('ticker', flat=True)[:test_size])
    print(f"Loaded {len(tickers)} tickers\n")

    # Run test
    start_time = time.time()
    results = []
    success = 0
    failed = 0
    errors = {}

    print(f"Processing {len(tickers)} tickers with {threads} threads...")
    print("")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_ticker = {
            executor.submit(fetch_func, ticker): ticker
            for ticker in tickers
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
                    print(f"  ERROR [{ticker}]: {str(e)[:80]}")

            # Progress updates every 200 tickers
            if i % 200 == 0:
                elapsed = time.time() - start_time
                current_rate = i / elapsed if elapsed > 0 else 0
                eta = (len(tickers) - i) / current_rate if current_rate > 0 else 0

                print(f"  Progress: {i}/{len(tickers)} ({i/len(tickers)*100:.1f}%) | "
                      f"Success: {success} | Failed: {failed} | "
                      f"Rate: {current_rate:.2f} t/s | ETA: {eta:.0f}s")

    elapsed = time.time() - start_time
    actual_rate = len(tickers) / elapsed if elapsed > 0 else 0

    # Database update
    db_updated = 0
    db_failed = 0
    if results:
        print(f"\nUpdating database...")
        db_start = time.time()
        db_updated, db_failed = batch_update_func(results)
        db_elapsed = time.time() - db_start
        print(f"  Database updated: {db_updated} stocks in {db_elapsed:.1f}s")

    # Results
    print("")
    print("=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print(f"Total tickers: {len(tickers)}")
    print(f"Successful: {success} ({success/len(tickers)*100:.1f}%)")
    print(f"Failed: {failed}")
    print(f"DB Updated: {db_updated}")
    print(f"DB Failed: {db_failed}")
    print(f"Total time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
    print(f"Actual rate: {actual_rate:.3f} tickers/second")
    print(f"Target rate: {target_rate:.3f} tickers/second")

    if errors:
        print(f"\nError types:")
        for error_type, count in sorted(errors.items(), key=lambda x: -x[1])[:5]:
            print(f"  {error_type}: {count}")

    # Check targets
    print("")
    print("TARGET ANALYSIS:")
    print("-" * 80)

    if success / len(tickers) >= 0.95:
        print(f"[OK] Success rate: {success/len(tickers)*100:.1f}% >= 95%")
    else:
        print(f"[FAIL] Success rate: {success/len(tickers)*100:.1f}% < 95%")

    if actual_rate <= target_rate * 1.1:  # Within 10% of target
        print(f"[OK] Rate: {actual_rate:.3f} t/s ~= {target_rate:.3f} t/s (target)")
    elif actual_rate > target_rate * 1.1:
        print(f"[WARN] Rate: {actual_rate:.3f} t/s > {target_rate:.3f} t/s (too fast, may hit rate limits)")
    else:
        print(f"[WARN] Rate: {actual_rate:.3f} t/s < {target_rate:.3f} t/s (too slow)")

    if db_updated == success:
        print(f"[OK] All successful fetches updated in database")
    else:
        print(f"[FAIL] DB updates ({db_updated}) != successful fetches ({success})")

    print("=" * 80)

    return {
        'tickers': len(tickers),
        'success': success,
        'failed': failed,
        'db_updated': db_updated,
        'elapsed': elapsed,
        'rate': actual_rate,
        'target_rate': target_rate,
        'errors': errors
    }

# ============================================================================
# MAIN TESTING
# ============================================================================

print("=" * 80)
print("PRODUCTION LOAD TESTING SUITE")
print("=" * 80)
print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("")
print("Configuration:")
print("  Daily Scanner: 0.25 t/s, 20 threads (rate limit safety)")
print("  10-Min Scanner: >1.5 t/s, 20 threads (fast updates)")
print("")
print("Test Plan:")
print("  1. Daily Scanner - 1000 tickers")
print("  2. Daily Scanner - 2000 tickers")
print("  3. 10-Min Scanner - 1000 tickers")
print("  4. 10-Min Scanner - 2000 tickers")
print("=" * 80)

all_results = {}

# ============================================================================
# TEST 1: Daily Scanner - 1000 Tickers
# ============================================================================

try:
    from realtime_daily_yfinance import fetch_stock_yfinance, batch_update_stocks

    results = test_scanner(
        scanner_name="DAILY SCANNER",
        fetch_func=fetch_stock_yfinance,
        batch_update_func=batch_update_stocks,
        test_size=1000,
        threads=20,
        target_rate=0.25,
        target_name="0.25 t/s (rate limit safe)"
    )

    all_results['daily_1000'] = results

except Exception as e:
    print(f"[ERROR] Daily Scanner 1000 test failed: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# TEST 2: Daily Scanner - 2000 Tickers
# ============================================================================

try:
    from realtime_daily_yfinance import fetch_stock_yfinance, batch_update_stocks

    results = test_scanner(
        scanner_name="DAILY SCANNER",
        fetch_func=fetch_stock_yfinance,
        batch_update_func=batch_update_stocks,
        test_size=2000,
        threads=20,
        target_rate=0.25,
        target_name="0.25 t/s (rate limit safe)"
    )

    all_results['daily_2000'] = results

except Exception as e:
    print(f"[ERROR] Daily Scanner 2000 test failed: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# TEST 3: 10-Minute Scanner - 1000 Tickers
# ============================================================================

try:
    from scanner_10min_production import fetch_10min_metrics, batch_update_10min

    results = test_scanner(
        scanner_name="10-MINUTE SCANNER",
        fetch_func=fetch_10min_metrics,
        batch_update_func=batch_update_10min,
        test_size=1000,
        threads=20,
        target_rate=1.5,
        target_name=">1.5 t/s (minimum for 10-min window)"
    )

    all_results['10min_1000'] = results

except Exception as e:
    print(f"[ERROR] 10-Min Scanner 1000 test failed: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# TEST 4: 10-Minute Scanner - 2000 Tickers
# ============================================================================

try:
    from scanner_10min_production import fetch_10min_metrics, batch_update_10min

    results = test_scanner(
        scanner_name="10-MINUTE SCANNER",
        fetch_func=fetch_10min_metrics,
        batch_update_func=batch_update_10min,
        test_size=2000,
        threads=20,
        target_rate=1.5,
        target_name=">1.5 t/s (minimum for 10-min window)"
    )

    all_results['10min_2000'] = results

except Exception as e:
    print(f"[ERROR] 10-Min Scanner 2000 test failed: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# FINAL SUMMARY
# ============================================================================

test_header("FINAL SUMMARY - ALL TESTS")

print("\nDaily Scanner (Target: 0.25 t/s, 20 threads):")
print("-" * 80)

if 'daily_1000' in all_results:
    r = all_results['daily_1000']
    print(f"1000 tickers: {r['success']}/{r['tickers']} ({r['success']/r['tickers']*100:.1f}%) | "
          f"Rate: {r['rate']:.3f} t/s | Time: {r['elapsed']:.1f}s")

if 'daily_2000' in all_results:
    r = all_results['daily_2000']
    print(f"2000 tickers: {r['success']}/{r['tickers']} ({r['success']/r['tickers']*100:.1f}%) | "
          f"Rate: {r['rate']:.3f} t/s | Time: {r['elapsed']:.1f}s")

print("\n10-Minute Scanner (Target: >1.5 t/s, 20 threads):")
print("-" * 80)

if '10min_1000' in all_results:
    r = all_results['10min_1000']
    print(f"1000 tickers: {r['success']}/{r['tickers']} ({r['success']/r['tickers']*100:.1f}%) | "
          f"Rate: {r['rate']:.3f} t/s | Time: {r['elapsed']:.1f}s")

if '10min_2000' in all_results:
    r = all_results['10min_2000']
    print(f"2000 tickers: {r['success']}/{r['tickers']} ({r['success']/r['tickers']*100:.1f}%) | "
          f"Rate: {r['rate']:.3f} t/s | Time: {r['elapsed']:.1f}s")

print("\n" + "=" * 80)
print("PRODUCTION READINESS:")
print("=" * 80)

# Check daily scanner
daily_ready = True
if 'daily_1000' in all_results and 'daily_2000' in all_results:
    r1 = all_results['daily_1000']
    r2 = all_results['daily_2000']

    if r1['success']/r1['tickers'] >= 0.95 and r2['success']/r2['tickers'] >= 0.95:
        print("[OK] Daily Scanner: 95%+ success rate on both tests")
    else:
        print("[FAIL] Daily Scanner: <95% success rate")
        daily_ready = False

    if r1['rate'] <= 0.30 and r2['rate'] <= 0.30:  # Within 20% of 0.25 target
        print("[OK] Daily Scanner: Rate limit safe (<=0.30 t/s)")
    else:
        print("[WARN] Daily Scanner: May hit rate limits (>0.30 t/s)")

# Check 10-min scanner
tenmin_ready = True
if '10min_1000' in all_results and '10min_2000' in all_results:
    r1 = all_results['10min_1000']
    r2 = all_results['10min_2000']

    if r1['success']/r1['tickers'] >= 0.95 and r2['success']/r2['tickers'] >= 0.95:
        print("[OK] 10-Min Scanner: 95%+ success rate on both tests")
    else:
        print("[FAIL] 10-Min Scanner: <95% success rate")
        tenmin_ready = False

    if r1['rate'] >= 1.5 and r2['rate'] >= 1.5:
        print("[OK] 10-Min Scanner: Fast enough (>=1.5 t/s)")
    else:
        print("[FAIL] 10-Min Scanner: Too slow (<1.5 t/s)")
        tenmin_ready = False

print("")
if daily_ready and tenmin_ready:
    print("[SUCCESS] ALL SCANNERS PRODUCTION READY")
else:
    print("[FAIL] Some scanners need fixes")

print("=" * 80)
print(f"Testing completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
