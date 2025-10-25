#!/usr/bin/env python3
"""
Simple script to check database content
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import Stock

def check_database():
    print("=== DATABASE CHECK ===")
    
    total_stocks = Stock.objects.count()
    print(f"Total stocks in database: {total_stocks}")
    
    if total_stocks == 0:
        print("❌ No stocks found in database!")
        return
    
    nyse_stocks = Stock.objects.filter(exchange__iexact='NYSE').count()
    print(f"NYSE stocks: {nyse_stocks}")
    
    nasdaq_stocks = Stock.objects.filter(exchange__iexact='NASDAQ').count()
    print(f"NASDAQ stocks: {nasdaq_stocks}")
    
    stocks_with_price = Stock.objects.filter(current_price__isnull=False).exclude(current_price=0).count()
    print(f"Stocks with price data: {stocks_with_price}")
    
    stocks_with_volume = Stock.objects.filter(volume__isnull=False).exclude(volume=0).count()
    print(f"Stocks with volume data: {stocks_with_volume}")
    
    print("\n=== SAMPLE STOCKS ===")
    sample_stocks = Stock.objects.filter(current_price__isnull=False)[:10]
    for stock in sample_stocks:
        print(f"{stock.ticker} ({stock.exchange}): ${stock.current_price} - {stock.company_name}")
    
    if stocks_with_price == 0:
        print("\n❌ No stocks have price data - this is why the API returns empty!")
        print("Recent stocks:")
        recent_stocks = Stock.objects.order_by('-last_updated')[:5]
        for stock in recent_stocks:
            print(f"  {stock.ticker}: price={stock.current_price}, volume={stock.volume}, updated={stock.last_updated}")
    
    # Check default filters that might be causing issues
    print(f"\n=== DEFAULT QUERY ANALYSIS ===")
    
    # This is what the API does by default
    default_query = Stock.objects.filter(exchange__iexact='NYSE').exclude(
        current_price__isnull=True
    ).exclude(
        current_price=0
    )
    default_count = default_query.count()
    print(f"Default API query returns: {default_count} stocks")
    
    if default_count == 0:
        print("❌ Default API query returns 0 stocks!")
        print("Let's check what's wrong:")
        
        nyse_all = Stock.objects.filter(exchange__iexact='NYSE').count()
        print(f"  Total NYSE stocks: {nyse_all}")
        
        nyse_null_price = Stock.objects.filter(exchange__iexact='NYSE', current_price__isnull=True).count()
        print(f"  NYSE stocks with NULL price: {nyse_null_price}")
        
        nyse_zero_price = Stock.objects.filter(exchange__iexact='NYSE', current_price=0).count()
        print(f"  NYSE stocks with zero price: {nyse_zero_price}")
        
        # Check for different exchange values
        print(f"\n=== EXCHANGE VALUES ===")
        exchanges = Stock.objects.values_list('exchange', flat=True).distinct()
        for exchange in exchanges:
            count = Stock.objects.filter(exchange=exchange).count()
            print(f"  '{exchange}': {count} stocks")

if __name__ == "__main__":
    check_database()