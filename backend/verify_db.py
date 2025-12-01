#!/usr/bin/env python
"""Verify database records after stock update"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import Stock, StockPrice

print("=" * 80)
print("DATABASE VERIFICATION")
print("=" * 80)

# Count records
total_stocks = Stock.objects.count()
total_prices = StockPrice.objects.count()

print(f"\n[COUNTS]")
print(f"  Total stocks in DB: {total_stocks}")
print(f"  Total price records: {total_prices}")

# Recent updates
recent = Stock.objects.order_by('-last_updated')[:10]

print(f"\n[RECENT UPDATES] Last 10 updated stocks:")
for s in recent:
    print(f"  {s.ticker:6s} | ${s.current_price or 0:8.2f} | {s.company_name[:40]:40s} | {s.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")

# Data quality check
stocks_with_price = Stock.objects.filter(current_price__isnull=False).count()
stocks_with_market_cap = Stock.objects.filter(market_cap__isnull=False).count()
stocks_with_volume = Stock.objects.filter(volume__isnull=False).count()

print(f"\n[DATA QUALITY]")
print(f"  Stocks with price: {stocks_with_price}/{total_stocks} ({stocks_with_price/total_stocks*100:.1f}%)")
print(f"  Stocks with market cap: {stocks_with_market_cap}/{total_stocks} ({stocks_with_market_cap/total_stocks*100:.1f}%)")
print(f"  Stocks with volume: {stocks_with_volume}/{total_stocks} ({stocks_with_volume/total_stocks*100:.1f}%)")

print("\n" + "=" * 80)
