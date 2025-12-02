#!/usr/bin/env python3
"""Test script for rate-limit aware scanner with 100 tickers"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")

import django
django.setup()

from stocks.models import Stock
import rate_limit_aware_scanner

# Test with 100 tickers
rate_limit_aware_scanner.CONFIG.target_tickers = 100

# Get first 100 tickers
tickers = list(Stock.objects.all()[:100].values_list('ticker', flat=True))
print(f"Testing with {len(tickers)} tickers")

# Run scanner
rate_limit_aware_scanner.main()
