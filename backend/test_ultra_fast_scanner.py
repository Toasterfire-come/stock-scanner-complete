#!/usr/bin/env python3
"""
Test script for ultra-fast scanner
Tests with a small sample to validate functionality before full run
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stock_scanner_backend.settings")

import django
django.setup()

from ultra_fast_5373_scanner import run_ultra_fast_scan, CONFIG

def run_test():
    """Run test with 100 tickers"""
    print("=" * 70)
    print("ULTRA-FAST SCANNER - TEST RUN")
    print("=" * 70)
    print("Testing with 100 tickers to validate functionality...")
    print()

    # Run with limited tickers
    result = run_ultra_fast_scan(max_tickers=100)

    if result:
        print("\n✓ Test completed successfully!")
        print(f"  Success rate: {result['success_rate']:.1f}%")
        print(f"  Runtime: {result['runtime_seconds']:.1f}s")
        print(f"  Throughput: {result['throughput_per_second']:.1f} tickers/sec")

        # Extrapolate to full run
        if result['throughput_per_second'] > 0:
            estimated_full_runtime = 5373 / result['throughput_per_second']
            print(f"\nEstimated runtime for 5373 tickers: {estimated_full_runtime/60:.2f} minutes")

            if estimated_full_runtime <= 180:
                print("✓ Should meet <3 minute target!")
            else:
                shortfall = estimated_full_runtime - 180
                print(f"⚠ May exceed target by {shortfall:.1f}s")
                print("  Consider increasing workers or reducing timeout")

        return True
    else:
        print("\n✗ Test failed")
        return False

if __name__ == "__main__":
    try:
        run_test()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
