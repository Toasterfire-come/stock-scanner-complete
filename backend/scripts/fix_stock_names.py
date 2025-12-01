#!/usr/bin/env python3
"""
Fix Stock Company Names
Updates stock company names to proper professional names
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import Stock
import yfinance as yf
from time import sleep

def fix_stock_names():
    """Update stock company names from Yahoo Finance"""
    stocks = Stock.objects.all()
    total = stocks.count()
    updated = 0
    failed = 0

    print(f"Total stocks to update: {total}")
    print("=" * 60)

    for idx, stock in enumerate(stocks, 1):
        ticker = stock.ticker
        current_name = stock.company_name or stock.name

        # Skip if already has a proper name (not just ticker + Corporation)
        if current_name and current_name != f"{ticker} Corporation" and current_name != ticker:
            print(f"[{idx}/{total}] {ticker}: Already has proper name '{current_name}'")
            continue

        try:
            # Fetch company info from Yahoo Finance
            print(f"[{idx}/{total}] Fetching {ticker}...", end=" ")
            yf_ticker = yf.Ticker(ticker)
            info = yf_ticker.info

            # Try multiple fields for company name
            proper_name = None
            if 'longName' in info and info['longName']:
                proper_name = info['longName']
            elif 'shortName' in info and info['shortName']:
                proper_name = info['shortName']
            elif 'name' in info and info['name']:
                proper_name = info['name']

            if proper_name and proper_name != ticker:
                # Update both company_name and name fields
                stock.company_name = proper_name
                stock.name = proper_name
                stock.save(update_fields=['company_name', 'name'])
                updated += 1
                print(f"✅ Updated to '{proper_name}'")
            else:
                print(f"⚠️  No name found, keeping current")
                failed += 1

            # Rate limiting to avoid being blocked
            if idx % 10 == 0:
                sleep(1)

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            failed += 1
            continue

    print("\n" + "=" * 60)
    print(f"Update complete!")
    print(f"  Total processed: {total}")
    print(f"  Successfully updated: {updated}")
    print(f"  Failed/Skipped: {failed}")
    print("=" * 60)

if __name__ == '__main__':
    print("Stock Company Name Fixer")
    print("=" * 60)
    print("This will update all stock company names from Yahoo Finance")
    print("=" * 60)

    # Show sample of current data
    print("\nCurrent stock names (first 5):")
    for stock in Stock.objects.all()[:5]:
        print(f"  {stock.ticker}: {stock.company_name or stock.name}")

    response = input("\nProceed with update? (yes/no): ").strip().lower()
    if response == 'yes':
        fix_stock_names()
    else:
        print("Update cancelled.")
