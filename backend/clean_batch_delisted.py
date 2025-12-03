#!/usr/bin/env python
"""Clean delisted stocks identified from enhanced_updater test runs"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SECRET_KEY', 'temp-key-for-script')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import Stock

def clean_batch_delisted():
    """Remove stocks identified as delisted from test runs"""
    print("=" * 70)
    print("CLEANING DELISTED STOCKS FROM TEST RESULTS")
    print("=" * 70)

    # Delisted stocks from enhanced_updater test (300 stocks)
    delisted_stocks = [
        # Batch 1 delisted
        'AFMD', 'AHI', 'AIFER', 'AIFE', 'ALKSV', 'ANGIV', 'AGFS',
        'AIF', 'DISH', 'AKYA', 'AEPPZ', 'AKUS', 'AITR', 'AAPGV',
        'ABST', 'ALOR', 'AGTC',

        # Batch 2 delisted
        'ANSS', 'APGB',

        # Batch 3 delisted
        'ARIS', 'ARCK', 'AQNA', 'APRN', 'ARGO',

        # Batch 4 delisted
        'ARTE',

        # Batch 6 delisted
        'ATNF', 'ATCOL', 'ATIF',
    ]

    total_deleted = 0

    for symbol in delisted_stocks:
        try:
            deleted_count = Stock.objects.filter(symbol=symbol).delete()[0]
            if deleted_count > 0:
                print(f"[DELETED] {symbol}")
                total_deleted += deleted_count
            else:
                print(f"[NOT FOUND] {symbol}")
        except Exception as e:
            print(f"[ERROR] {symbol}: {e}")

    print(f"\n[TOTAL] Deleted {total_deleted} delisted stocks")

    # Final count
    remaining = Stock.objects.count()
    nasdaq = Stock.objects.filter(exchange__startswith='N').count()
    nyse = Stock.objects.filter(exchange='NYSE').count()

    print(f"\nRemaining stocks: {remaining}")
    print(f"  NASDAQ: {nasdaq}")
    print(f"  NYSE: {nyse}")

    print("\n" + "=" * 70)
    print("CLEANUP COMPLETE")
    print("=" * 70)

if __name__ == '__main__':
    clean_batch_delisted()
