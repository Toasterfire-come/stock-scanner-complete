#!/usr/bin/env python3
"""
Simple test to verify Django setup
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')

try:
    django.setup()
    print("✅ Django setup successful")
    
    # Test basic imports
    from stocks.models import Stock, StockPrice
    print("✅ Model imports successful")
    
    # Test database connection
    stock_count = Stock.objects.count()
    print(f"✅ Database connection successful - {stock_count} stocks in database")
    
    print("✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()