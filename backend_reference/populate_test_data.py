#!/usr/bin/env python3
"""
Simple script to populate test stock data
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
import random

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from django.utils import timezone
from stocks.models import Stock

def create_test_stocks():
    """Create realistic test stock data"""
    
    # Sample stock data based on real companies but with simulated prices
    test_stocks = [
        {
            'ticker': 'AAPL',
            'company_name': 'Apple Inc.',
            'exchange': 'NASDAQ',
            'current_price': Decimal('175.25'),
            'price_change_today': Decimal('2.15'),
            'change_percent': Decimal('1.24'),
            'volume': 45678900,
            'market_cap': 2750000000000,
            'pe_ratio': Decimal('28.5'),
            'dividend_yield': Decimal('0.82')
        },
        {
            'ticker': 'MSFT',
            'company_name': 'Microsoft Corporation', 
            'exchange': 'NASDAQ',
            'current_price': Decimal('412.80'),
            'price_change_today': Decimal('-3.20'),
            'change_percent': Decimal('-0.77'),
            'volume': 23456780,
            'market_cap': 3100000000000,
            'pe_ratio': Decimal('32.1'),
            'dividend_yield': Decimal('0.68')
        },
        {
            'ticker': 'GOOGL',
            'company_name': 'Alphabet Inc.',
            'exchange': 'NASDAQ',
            'current_price': Decimal('142.65'),
            'price_change_today': Decimal('2.25'),
            'change_percent': Decimal('1.60'),
            'volume': 34567890,
            'market_cap': 1800000000000,
            'pe_ratio': Decimal('24.8'),
            'dividend_yield': Decimal('0.00')
        },
        {
            'ticker': 'AMZN',
            'company_name': 'Amazon.com Inc.',
            'exchange': 'NASDAQ',
            'current_price': Decimal('145.30'),
            'price_change_today': Decimal('1.85'),
            'change_percent': Decimal('1.29'),
            'volume': 28900000,
            'market_cap': 1520000000000,
            'pe_ratio': Decimal('45.2'),
            'dividend_yield': Decimal('0.00')
        },
        {
            'ticker': 'TSLA',
            'company_name': 'Tesla Inc.',
            'exchange': 'NASDAQ',
            'current_price': Decimal('248.50'),
            'price_change_today': Decimal('-12.30'),
            'change_percent': Decimal('-4.72'),
            'volume': 89000000,
            'market_cap': 795000000000,
            'pe_ratio': Decimal('65.8'),
            'dividend_yield': Decimal('0.00')
        },
        {
            'ticker': 'NVDA',
            'company_name': 'NVIDIA Corporation',
            'exchange': 'NASDAQ',
            'current_price': Decimal('875.28'),
            'price_change_today': Decimal('15.45'),
            'change_percent': Decimal('1.80'),
            'volume': 45600000,
            'market_cap': 2150000000000,
            'pe_ratio': Decimal('58.3'),
            'dividend_yield': Decimal('0.03')
        },
        {
            'ticker': 'META',
            'company_name': 'Meta Platforms Inc.',
            'exchange': 'NASDAQ',
            'current_price': Decimal('385.75'),
            'price_change_today': Decimal('8.90'),
            'change_percent': Decimal('2.36'),
            'volume': 18500000,
            'market_cap': 980000000000,
            'pe_ratio': Decimal('22.5'),
            'dividend_yield': Decimal('0.35')
        },
        {
            'ticker': 'JPM',
            'company_name': 'JPMorgan Chase & Co.',
            'exchange': 'NYSE',
            'current_price': Decimal('158.45'),
            'price_change_today': Decimal('-1.25'),
            'change_percent': Decimal('-0.78'),
            'volume': 12400000,
            'market_cap': 465000000000,
            'pe_ratio': Decimal('11.8'),
            'dividend_yield': Decimal('2.15')
        },
        {
            'ticker': 'V',
            'company_name': 'Visa Inc.',
            'exchange': 'NYSE',
            'current_price': Decimal('275.60'),
            'price_change_today': Decimal('3.80'),
            'change_percent': Decimal('1.40'),
            'volume': 6800000,
            'market_cap': 595000000000,
            'pe_ratio': Decimal('34.2'),
            'dividend_yield': Decimal('0.74')
        },
        {
            'ticker': 'WMT',
            'company_name': 'Walmart Inc.',
            'exchange': 'NYSE',
            'current_price': Decimal('162.85'),
            'price_change_today': Decimal('0.95'),
            'change_percent': Decimal('0.59'),
            'volume': 8900000,
            'market_cap': 665000000000,
            'pe_ratio': Decimal('28.1'),
            'dividend_yield': Decimal('1.02')
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for stock_data in test_stocks:
        # Add calculated fields
        stock_data.update({
            'symbol': stock_data['ticker'],  # For compatibility
            'name': stock_data['company_name'],  # For compatibility
            'price_change': stock_data['price_change_today'],  # For compatibility
            'week_52_low': stock_data['current_price'] * Decimal('0.75'),  # Estimate
            'week_52_high': stock_data['current_price'] * Decimal('1.35'),  # Estimate
            'days_low': stock_data['current_price'] * Decimal('0.98'),  # Estimate
            'days_high': stock_data['current_price'] * Decimal('1.02'),  # Estimate
            'avg_volume_3mon': int(stock_data['volume'] * 1.1),  # Estimate
            'last_updated': timezone.now(),
            'created_at': timezone.now()
        })
        
        # Create or update stock
        stock, created = Stock.objects.update_or_create(
            ticker=stock_data['ticker'],
            defaults=stock_data
        )
        
        if created:
            created_count += 1
            print(f"Created: {stock.ticker} - {stock.company_name}")
        else:
            updated_count += 1
            print(f"Updated: {stock.ticker} - {stock.company_name}")
    
    print(f"\nSummary:")
    print(f"Created: {created_count} stocks")
    print(f"Updated: {updated_count} stocks")
    print(f"Total stocks in database: {Stock.objects.count()}")

if __name__ == "__main__":
    print("Populating test stock data...")
    create_test_stocks()
    print("Done!")