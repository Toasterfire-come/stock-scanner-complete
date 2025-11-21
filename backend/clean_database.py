#!/usr/bin/env python
"""
Clean database - keep only active NYSE and NASDAQ stocks
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import Stock
from django.utils import timezone
from datetime import timedelta

print("=" * 80)
print("DATABASE CLEANUP - NYSE AND NASDAQ ACTIVE STOCKS ONLY")
print("=" * 80)

# Count before cleanup
total_before = Stock.objects.count()
print(f"\n[BEFORE] Total stocks in database: {total_before}")

# Count by exchange
nyse_count = Stock.objects.filter(exchange__icontains='NYSE').count()
nasdaq_count = Stock.objects.filter(exchange__icontains='NASDAQ').count()
other_count = Stock.objects.exclude(exchange__icontains='NYSE').exclude(exchange__icontains='NASDAQ').count()

print(f"  NYSE stocks: {nyse_count}")
print(f"  NASDAQ stocks: {nasdaq_count}")
print(f"  Other exchanges: {other_count}")

# Count stocks with no price data
no_price = Stock.objects.filter(current_price__isnull=True).count()
print(f"  Stocks with no price: {no_price}")

# Step 1: Delete stocks with no price data (likely delisted)
print("\n[STEP 1] Removing stocks with no current price (likely delisted)...")
deleted_no_price = Stock.objects.filter(current_price__isnull=True).delete()
print(f"  Deleted {deleted_no_price[0]} stocks with no price data")

# Step 2: Delete stocks not from NYSE or NASDAQ
print("\n[STEP 2] Removing stocks not from NYSE or NASDAQ...")
deleted_other = Stock.objects.exclude(
    exchange__icontains='NYSE'
).exclude(
    exchange__icontains='NASDAQ'
).delete()
print(f"  Deleted {deleted_other[0]} stocks from other exchanges")

# Step 3: Delete stocks with invalid/zero prices
print("\n[STEP 3] Removing stocks with invalid prices (<=0 or >100000)...")
deleted_invalid = Stock.objects.filter(
    current_price__lte=0
).delete()
deleted_unrealistic = Stock.objects.filter(
    current_price__gte=100000
).delete()
print(f"  Deleted {deleted_invalid[0]} stocks with price <= 0")
print(f"  Deleted {deleted_unrealistic[0]} stocks with price >= 100000")

# Count after cleanup
total_after = Stock.objects.count()
nyse_after = Stock.objects.filter(exchange__icontains='NYSE').count()
nasdaq_after = Stock.objects.filter(exchange__icontains='NASDAQ').count()

print("\n" + "=" * 80)
print("CLEANUP COMPLETE")
print("=" * 80)

print(f"\n[AFTER] Total stocks in database: {total_after}")
print(f"  NYSE stocks: {nyse_after}")
print(f"  NASDAQ stocks: {nasdaq_after}")
print(f"  Total removed: {total_before - total_after}")

# Show sample of remaining stocks
print("\n[SAMPLE] First 10 active stocks:")
sample = Stock.objects.all()[:10]
for s in sample:
    print(f"  {s.ticker:6s} | ${s.current_price:8.2f} | {s.exchange:10s} | {s.company_name[:40]}")

print("\n[READY] Database is now clean and ready for testing!")
print(f"[TEST] Run with: python manage.py update_stocks_yfinance_optimized --limit {total_after} --threads 150")
print("=" * 80)
