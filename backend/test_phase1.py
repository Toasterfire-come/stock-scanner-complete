#!/usr/bin/env python3
"""
Test Phase 1 bypass improvements
Tests with 100 stocks to measure success rate
Expected: 30-50% success rate (vs 1-3% before)
"""

import os
import sys
import django
import time

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from stocks.models import Stock
from ultra_fast_yfinance_v3 import UltraFastStockUpdater

def test_phase1(num_stocks=100):
    """Test Phase 1 improvements with small batch"""
    print("="*70)
    print("PHASE 1 BYPASS TEST")
    print("="*70)
    print(f"Testing with {num_stocks} stocks...")
    print(f"Expected success rate: 30-50%")
    print(f"Previous success rate: 1-3%")
    print("="*70)

    # Get first N stocks
    stocks = list(Stock.objects.all()[:num_stocks].values_list('ticker', flat=True))
    print(f"\nSelected {len(stocks)} stocks for testing")

    # Create updater
    updater = UltraFastStockUpdater()

    # Test fetching
    print(f"\nStarting fetch test...")
    start_time = time.time()

    success_count = 0
    fail_count = 0
    rate_limit_count = 0

    for i, symbol in enumerate(stocks):
        # Get proxy
        proxy = updater.proxy_pool.get_next()

        # Fetch data
        result = updater.fetch_stock_data(symbol, proxy)

        if result:
            success_count += 1
            updater.proxy_pool.record_success(proxy)
            status = "OK"
        else:
            fail_count += 1
            updater.proxy_pool.record_failure(proxy)
            status = "FAIL"

        # Progress update every 20 stocks
        if (i + 1) % 20 == 0:
            current_rate = (success_count / (i + 1)) * 100
            print(f"  Progress: {i+1}/{num_stocks} | Success: {success_count} ({current_rate:.1f}%)")

    elapsed = time.time() - start_time
    success_rate = (success_count / num_stocks) * 100

    print("\n" + "="*70)
    print("TEST RESULTS")
    print("="*70)
    print(f"Total stocks tested: {num_stocks}")
    print(f"Successful: {success_count} ({success_rate:.1f}%)")
    print(f"Failed: {fail_count}")
    print(f"Time elapsed: {elapsed:.1f}s")
    print(f"Rate: {num_stocks/elapsed:.2f} stocks/sec")
    print("="*70)

    # Evaluation
    print("\nEVALUATION:")
    if success_rate >= 30:
        print(f"PASS - Success rate {success_rate:.1f}% meets target (>= 30%)")
        print("Phase 1 improvements are working!")
    elif success_rate >= 15:
        print(f"PARTIAL - Success rate {success_rate:.1f}% improved but below target")
        print("Some improvements working, may need Phase 2")
    else:
        print(f"FAIL - Success rate {success_rate:.1f}% below minimum (< 15%)")
        print("Phase 1 improvements not effective, needs debugging")

    print("\n" + "="*70)

    return success_rate

if __name__ == "__main__":
    import sys
    num_stocks = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    test_phase1(num_stocks)
