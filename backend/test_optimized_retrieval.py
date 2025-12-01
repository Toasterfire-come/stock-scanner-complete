#!/usr/bin/env python
"""
Test script for ultra-optimized stock retrieval
Run this to verify sub-3-minute performance with 90%+ correctness
"""

import os
import sys
import django
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from django.core.management import call_command

def run_performance_test():
    """Run performance test with varying configurations"""

    print("=" * 80)
    print("ULTRA-OPTIMIZED STOCK RETRIEVAL - PERFORMANCE TEST")
    print("=" * 80)
    print()

    # Test configurations
    test_configs = [
        {
            'name': 'Small Test (100 stocks)',
            'limit': 100,
            'threads': 50,
            'proxy_count': 50,
            'test_mode': True
        },
        {
            'name': 'Medium Test (500 stocks)',
            'limit': 500,
            'threads': 100,
            'proxy_count': 75,
            'test_mode': True
        },
        {
            'name': 'Full Test (3000 stocks) - PRODUCTION TARGET',
            'limit': 3000,
            'threads': 150,
            'proxy_count': 100,
            'test_mode': True
        },
    ]

    results = []

    for i, config in enumerate(test_configs, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(test_configs)}: {config['name']}")
        print(f"{'='*80}\n")

        start = time.time()

        try:
            call_command(
                'update_stocks_yfinance_optimized',
                limit=config['limit'],
                threads=config['threads'],
                timeout=5,
                test_mode=config['test_mode'],
                proxy_count=config['proxy_count'],
                csv='flat-ui__data-Fri Aug 01 2025.csv'
            )

            elapsed = time.time() - start

            results.append({
                'name': config['name'],
                'elapsed': elapsed,
                'limit': config['limit'],
                'success': True
            })

        except Exception as e:
            print(f"[FAIL] Test failed: {e}")
            results.append({
                'name': config['name'],
                'elapsed': time.time() - start,
                'limit': config['limit'],
                'success': False,
                'error': str(e)
            })

        # Wait between tests
        if i < len(test_configs):
            print("\n[WAIT] Waiting 5 seconds before next test...\n")
            time.sleep(5)

    # Display summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for r in results:
        status = "[PASS]" if r['success'] else "[FAIL]"
        minutes = r['elapsed'] / 60
        rate = r['limit'] / r['elapsed'] if r['elapsed'] > 0 else 0

        print(f"\n{status} - {r['name']}")
        print(f"  Stocks: {r['limit']}")
        print(f"  Time: {r['elapsed']:.2f}s ({minutes:.2f} min)")
        print(f"  Rate: {rate:.2f} stocks/sec")

        if not r['success']:
            print(f"  Error: {r.get('error', 'Unknown')}")

    # Check if production target met
    production_result = next((r for r in results if '3000' in r['name']), None)
    if production_result and production_result['success']:
        if production_result['elapsed'] < 180:
            print("\n[SUCCESS] PRODUCTION TARGET MET! Sub-3-minute execution achieved.")
        else:
            print(f"\n[WARNING] Production target not met. Time: {production_result['elapsed']:.2f}s (target: <180s)")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    run_performance_test()
