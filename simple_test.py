#!/usr/bin/env python3
"""
Very simple test to check Django command
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_scanner.settings')

try:
    django.setup()
    print("✅ Django setup successful")
    
    # Test basic imports
    from stocks.models import Stock, StockPrice
    print("✅ Model imports successful")
    
    # Test command import
    from django.core.management import call_command
    print("✅ Command import successful")
    
    print("✅ All basic tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()