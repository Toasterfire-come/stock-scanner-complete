#!/usr/bin/env python3
"""
Simple test script to check Django command functionality
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_scanner.settings')
django.setup()

# Test the command
from django.core.management import call_command

print("Testing Django command...")

try:
    # Test with minimal parameters
    call_command('update_stocks_yfinance', 
                limit=2, 
                test_mode=True, 
                threads=5,
                csv='flat-ui__data-Fri Aug 01 2025.csv')
    print("✅ Django command executed successfully!")
except Exception as e:
    print(f"❌ Django command failed: {e}")
    import traceback
    traceback.print_exc()