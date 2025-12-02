#!/usr/bin/env python3
"""Verify database updates"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")

import django
django.setup()

from stocks.models import Stock
from datetime import datetime, timedelta

# Check recently updated stocks
recent = datetime.now() - timedelta(minutes=5)
updated_stocks = Stock.objects.filter(last_updated__gte=recent).order_by('-last_updated')[:10]

print(f'Recently updated stocks (last 5 min): {updated_stocks.count()}')
print()

for stock in updated_stocks:
    price = stock.current_price if stock.current_price else 0
    updated_time = stock.last_updated.strftime("%H:%M:%S") if stock.last_updated else "N/A"
    print(f'{stock.symbol:6} | Price: ${price:10.2f} | Updated: {updated_time}')
