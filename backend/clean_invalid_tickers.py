#!/usr/bin/env python
"""
Clean Invalid Tickers from Database
Removes delisted, invalid, or duplicate stock entries
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SECRET_KEY', 'temp-key-for-script')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import Stock
from django.db.models import Count

def clean_invalid_tickers():
    """Remove invalid tickers from database"""

    print("=" * 70)
    print("CLEANING INVALID TICKERS")
    print("=" * 70)

    total_before = Stock.objects.count()
    print(f"\nTotal stocks before cleaning: {total_before}")

    # 1. Remove duplicates (keep oldest)
    print("\n[1/4] Checking for duplicates...")
    duplicates = Stock.objects.values('ticker').annotate(
        count=Count('ticker')
    ).filter(count__gt=1)

    dup_count = 0
    for dup in duplicates:
        ticker = dup['ticker']
        # Keep the first one, delete the rest
        stocks = Stock.objects.filter(ticker=ticker).order_by('created_at')
        for stock in stocks[1:]:
            stock.delete()
            dup_count += 1

    print(f"   Removed {dup_count} duplicate entries")

    # 2. Remove stocks with no price data
    print("\n[2/4] Removing stocks with no price...")
    no_price = Stock.objects.filter(current_price__isnull=True) | Stock.objects.filter(current_price__lte=0)
    no_price_count = no_price.count()
    no_price.delete()
    print(f"   Removed {no_price_count} stocks with no price")

    # 3. Remove stocks with invalid names (likely delisted)
    print("\n[3/4] Removing stocks with placeholder names...")
    invalid_names = Stock.objects.filter(
        company_name=''
    ) | Stock.objects.filter(
        company_name__isnull=True
    )
    invalid_count = invalid_names.count()
    invalid_names.delete()
    print(f"   Removed {invalid_count} stocks with invalid names")

    # 4. Show summary by exchange
    print("\n[4/4] Stock count by exchange:")
    exchanges = Stock.objects.values('exchange').annotate(count=Count('exchange')).order_by('-count')
    for ex in exchanges:
        print(f"   {ex['exchange']}: {ex['count']} stocks")

    total_after = Stock.objects.count()
    removed = total_before - total_after

    print("\n" + "=" * 70)
    print("CLEANING COMPLETE")
    print("=" * 70)
    print(f"Total before: {total_before}")
    print(f"Total after:  {total_after}")
    print(f"Removed:      {removed}")
    print(f"Retention:    {total_after/total_before*100:.1f}%")
    print("=" * 70)

if __name__ == '__main__':
    clean_invalid_tickers()
