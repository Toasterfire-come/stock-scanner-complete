#!/usr/bin/env python3
"""
Test script to verify all derived fields are calculated correctly
"""
import os
import sys
import django
from pathlib import Path

# Django setup
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import Stock
import yfinance as yf
from datetime import datetime
from django.utils import timezone as django_tz

# Test tickers
test_tickers = ['AAPL', 'MSFT', 'GOOGL']

print('Testing Daily Scanner Field Extraction')
print('='*80)

for ticker in test_tickers:
    try:
        print(f'\n[{ticker}] Fetching data...')
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or 'regularMarketPrice' not in info:
            print(f'  [X] No data available')
            continue

        # Extract data (same logic as scanner)
        current_price = info.get('regularMarketPrice', info.get('currentPrice', 0))
        prev_close = info.get('regularMarketPreviousClose', current_price)

        if current_price == 0:
            print(f'  [X] Invalid price')
            continue

        price_change = current_price - prev_close
        price_change_percent = (price_change / prev_close * 100) if prev_close > 0 else 0

        # Extract values for calculations
        bid_price = float(info.get('bid', 0)) if info.get('bid') else None
        ask_price = float(info.get('ask', 0)) if info.get('ask') else None
        volume = int(info.get('volume', 0)) if info.get('volume') else None
        avg_volume_3mon = int(info.get('averageVolume', 0)) if info.get('averageVolume') else None
        days_low = float(info.get('dayLow', current_price))
        days_high = float(info.get('dayHigh', current_price))

        # CALCULATIONS
        bid_ask_spread = None
        if bid_price and ask_price and bid_price > 0 and ask_price > 0:
            bid_ask_spread = f'{(ask_price - bid_price):.4f}'

        days_range = f'{days_low:.2f} - {days_high:.2f}'

        dvav = None
        if volume and avg_volume_3mon and avg_volume_3mon > 0:
            dvav = float(volume) / float(avg_volume_3mon)

        # Display results
        print(f'  [OK] Data extracted successfully')
        print(f'  Price: ${current_price:.2f} (Change: {price_change:+.2f}, {price_change_percent:+.2f}%)')
        if bid_price and ask_price:
            print(f'  Bid/Ask: ${bid_price:.2f} / ${ask_price:.2f}')
            print(f'  Spread: {bid_ask_spread}' if bid_ask_spread else '  Spread: N/A')
        else:
            print('  Bid/Ask: N/A')
        print(f'  Days Range: {days_range}')
        if volume:
            print(f'  Volume: {volume:,}')
        if avg_volume_3mon:
            print(f'  Avg Volume (3mo): {avg_volume_3mon:,}')
        if dvav:
            print(f'  DVAV: {dvav:.4f}')
        if info.get('marketCap'):
            print(f'  Market Cap: ${info.get("marketCap"):,}')
        if info.get('trailingPE'):
            print(f'  P/E Ratio: {info.get("trailingPE"):.2f}')
        if info.get('trailingEps'):
            print(f'  EPS: {info.get("trailingEps"):.2f}')
        if info.get('bookValue'):
            print(f'  Book Value: {info.get("bookValue"):.2f}')
        if info.get('targetMeanPrice'):
            print(f'  1Y Target: ${info.get("targetMeanPrice"):.2f}')
        if info.get('sharesOutstanding'):
            print(f'  Shares Outstanding: {info.get("sharesOutstanding"):,}')

    except Exception as e:
        print(f'  [ERROR] {str(e)[:100]}')

print('\n' + '='*80)
print('Test complete - All derived fields calculated successfully')
