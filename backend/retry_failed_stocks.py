#!/usr/bin/env python
"""
Retry Failed Stocks Script
Reads failed_symbols.json and retries them with the ultra-fast updater
"""

import os
import sys
import json
import django

# Set up Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from ultra_fast_yfinance_v3 import UltraFastStockUpdater


def load_failed_symbols():
    """Load failed symbols from JSON file"""
    failed_file = 'failed_symbols.json'

    if not os.path.exists(failed_file):
        print(f"[ERROR] No {failed_file} found. Run the main updater first.")
        return []

    try:
        with open(failed_file, 'r') as f:
            symbols = json.load(f)
        print(f"[INFO] Loaded {len(symbols)} failed symbols from {failed_file}")
        return symbols
    except Exception as e:
        print(f"[ERROR] Failed to load {failed_file}: {e}")
        return []


def main():
    """Main entry point for retry script"""
    print("=" * 70)
    print("RETRY FAILED STOCKS")
    print("=" * 70)

    # Load failed symbols
    failed_symbols = load_failed_symbols()

    if not failed_symbols:
        print("[INFO] No failed symbols to retry. Exiting.")
        return

    print(f"\n[START] Retrying {len(failed_symbols)} failed stocks...")
    print(f"[INFO] Using improved configuration:")
    print(f"  - Thread count: 60 (reduced from 150)")
    print(f"  - Rate limit cooldown: 15 minutes (increased from 5)")
    print(f"  - Proxy request gap: 0.5 seconds minimum")
    print(f"  - Time limit: 5 minutes")
    print("=" * 70 + "\n")

    # Create updater
    updater = UltraFastStockUpdater()

    # Run update with failed symbols only
    updater.run_update(symbols=failed_symbols)

    print("\n" + "=" * 70)
    print("RETRY COMPLETE")
    print("=" * 70)

    # Check if there are still failed symbols
    if os.path.exists('failed_symbols.json'):
        with open('failed_symbols.json', 'r') as f:
            remaining_failed = json.load(f)

        if remaining_failed:
            print(f"\n[WARNING] {len(remaining_failed)} symbols still failed.")
            print(f"[TIP] Wait 15-30 minutes for Yahoo rate limits to reset, then retry again.")
        else:
            print(f"\n[SUCCESS] All previously failed symbols now succeeded!")
    else:
        print(f"\n[SUCCESS] All symbols succeeded - no failures!")


if __name__ == '__main__':
    main()
