#!/usr/bin/env python3
"""
Final Production Test - With Proxies
=====================================
Tests both scanners with 1000 and 2000 tickers using proxy rotation

Requirements:
- Daily: 0.25 t/s, 20 threads, >95% success
- 10-Min: 1.5 t/s, 20 threads, >95% success
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

def run_test(scanner_name, fetch_func, batch_update_func, test_size, target_rate, rate_name):
    """Run a single test"""
    test_header(f"{scanner_name} - {test_size} Tickers Test")

    print(f"Configuration:")
    print(f"  Tickers: {test_size}")
    print(f"  Threads: 20")
    print(f"  Target: {rate_name}")
    print(f"  Start: {datetime.now().strftime('%H:%M:%S')}")
    print("")

    # Get tickers
    tickers = list(Stock.objects.values_list('ticker', flat=True)[:test_size])
    print(f"Loaded {len(tickers)} tickers\n")

    # Run test
    start = time.time()
    results = []
    success = 0
    failed = 0
    proxy_count = 0

    print(f"Processing...")

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(fetch_func, t): t for t in tickers}

        for i, future in enumerate(as_completed(futures), 1):
            data = future.result()
            if data:
                results.append(data)
                success += 1
                if data.get('used_proxy'):
                    proxy_count += 1
            else:
                failed += 1

            # Progress every 200
            if i % 200 == 0:
                elapsed = time.time() - start
                rate = i / elapsed if elapsed > 0 else 0
                eta = (len(tickers) - i) / rate if rate > 0 else 0
                print(f"  {i}/{len(tickers)} ({i/len(tickers)*100:.0f}%) | "
                      f"Success: {success} | Proxy: {proxy_count} | "
                      f"Rate: {rate:.3f} t/s | ETA: {eta:.0f}s")

    elapsed = time.time() - start
    actual_rate = len(tickers) / elapsed if elapsed > 0 else 0

    # Database update
    db_updated = 0
    if results:
        print(f"\nUpdating database...")
        db_updated, _ = batch_update_func(results)

    # Results
    print("")
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"Total: {len(tickers)}")
    print(f"Success: {success} ({success/len(tickers)*100:.1f}%)")
    print(f"Failed: {failed}")
    print(f"Proxied: {proxy_count}/{success} ({proxy_count/success*100:.0f}%)" if success > 0 else "Proxied: 0")
    print(f"DB Updated: {db_updated}")
    print(f"Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"Rate: {actual_rate:.3f} t/s")
    print(f"Target: {target_rate:.3f} t/s")
    print("")

    # Check requirements
    success_rate = success / len(tickers)
    rate_ok = abs(actual_rate - target_rate) / target_rate < 0.3  # Within 30%

    if success_rate >= 0.95:
        print("[PASS] Success rate >= 95%")
    else:
        print(f"[FAIL] Success rate {success_rate*100:.1f}% < 95%")

    if rate_ok:
        print(f"[PASS] Rate within 30% of target")
    else:
        print(f"[WARN] Rate {actual_rate:.3f} vs target {target_rate:.3f}")

    if proxy_count > 0:
        print(f"[PASS] Proxies working ({proxy_count} used)")
    else:
        print(f"[WARN] No proxies used (may be blocked or fallback)")

    print("=" * 80)

    return {
        'test': scanner_name,
        'tickers': len(tickers),
        'success': success,
        'failed': failed,
        'proxy_count': proxy_count,
        'db_updated': db_updated,
        'elapsed': elapsed,
        'rate': actual_rate,
        'target_rate': target_rate,
        'success_rate': success_rate
    }

# ============================================================================
# MAIN TEST SUITE
# ============================================================================

print("=" * 80)
print("FINAL PRODUCTION TEST - WITH PROXIES")
print("=" * 80)
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("")
print("Tests:")
print("  1. Daily Scanner - 1000 tickers (0.25 t/s)")
print("  2. Daily Scanner - 2000 tickers (0.25 t/s)")
print("  3. 10-Min Scanner - 1000 tickers (1.5 t/s)")
print("  4. 10-Min Scanner - 2000 tickers (1.5 t/s)")
print("=" * 80)

all_results = []

# TEST 1: Daily - 1000
try:
    from realtime_daily_with_proxies import fetch_stock_with_proxy, batch_update_stocks, load_proxies
    import realtime_daily_with_proxies as daily_mod

    print("\nLoading proxies for daily scanner...")
    daily_mod.proxy_list = load_proxies()
    print(f"Loaded {len(daily_mod.proxy_list)} proxies")

    result = run_test(
        "Daily Scanner - 1000",
        fetch_stock_with_proxy,
        batch_update_stocks,
        1000,
        0.25,
        "0.25 t/s"
    )
    all_results.append(result)
except Exception as e:
    print(f"[ERROR] Daily 1000 test failed: {e}")
    import traceback
    traceback.print_exc()

# TEST 2: Daily - 2000
try:
    result = run_test(
        "Daily Scanner - 2000",
        fetch_stock_with_proxy,
        batch_update_stocks,
        2000,
        0.25,
        "0.25 t/s"
    )
    all_results.append(result)
except Exception as e:
    print(f"[ERROR] Daily 2000 test failed: {e}")
    import traceback
    traceback.print_exc()

# TEST 3: 10-Min - 1000
try:
    from scanner_10min_with_proxies import fetch_10min_with_proxy, batch_update_10min, load_proxies
    import scanner_10min_with_proxies as tenmin_mod

    print("\nLoading proxies for 10-min scanner...")
    tenmin_mod.proxy_list = load_proxies()
    print(f"Loaded {len(tenmin_mod.proxy_list)} proxies")

    result = run_test(
        "10-Min Scanner - 1000",
        fetch_10min_with_proxy,
        batch_update_10min,
        1000,
        1.5,
        "1.5 t/s"
    )
    all_results.append(result)
except Exception as e:
    print(f"[ERROR] 10-Min 1000 test failed: {e}")
    import traceback
    traceback.print_exc()

# TEST 4: 10-Min - 2000
try:
    result = run_test(
        "10-Min Scanner - 2000",
        fetch_10min_with_proxy,
        batch_update_10min,
        2000,
        1.5,
        "1.5 t/s"
    )
    all_results.append(result)
except Exception as e:
    print(f"[ERROR] 10-Min 2000 test failed: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# FINAL SUMMARY
# ============================================================================

test_header("FINAL SUMMARY")

print("\nTest Results:")
print("-" * 80)
for r in all_results:
    print(f"{r['test']:30} | "
          f"Success: {r['success']}/{r['tickers']} ({r['success_rate']*100:.1f}%) | "
          f"Rate: {r['rate']:.3f} t/s | "
          f"Proxied: {r['proxy_count']}")

print("")
print("Requirements Check:")
print("-" * 80)

# Check daily
daily_pass = True
daily_tests = [r for r in all_results if 'Daily' in r['test']]
if daily_tests:
    for r in daily_tests:
        if r['success_rate'] < 0.95:
            print(f"[FAIL] {r['test']}: Success {r['success_rate']*100:.1f}% < 95%")
            daily_pass = False
        if abs(r['rate'] - 0.25) / 0.25 > 0.3:
            print(f"[WARN] {r['test']}: Rate {r['rate']:.3f} not close to 0.25 t/s")
    if daily_pass and all(r['success_rate'] >= 0.95 for r in daily_tests):
        print("[PASS] Daily Scanner: All tests passed")

# Check 10-min
tenmin_pass = True
tenmin_tests = [r for r in all_results if '10-Min' in r['test']]
if tenmin_tests:
    for r in tenmin_tests:
        if r['success_rate'] < 0.95:
            print(f"[FAIL] {r['test']}: Success {r['success_rate']*100:.1f}% < 95%")
            tenmin_pass = False
        if abs(r['rate'] - 1.5) / 1.5 > 0.3:
            print(f"[WARN] {r['test']}: Rate {r['rate']:.3f} not close to 1.5 t/s")
    if tenmin_pass and all(r['success_rate'] >= 0.95 for r in tenmin_tests):
        print("[PASS] 10-Min Scanner: All tests passed")

print("")
if all(r['success_rate'] >= 0.95 for r in all_results):
    print("[SUCCESS] ALL SCANNERS MEET REQUIREMENTS")
else:
    print("[INCOMPLETE] Some tests need investigation")

print("=" * 80)
print(f"Testing complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
