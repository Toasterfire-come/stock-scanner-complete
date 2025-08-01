#!/usr/bin/env python3
"""
Fix Stock Scanner - Run without proxies to ensure data is pulled correctly
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/workspace')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from django.core.management import execute_from_command_line

def main():
    """Run the stock scanner with fixes applied"""
    print("FIXING STOCK SCANNER - Running without proxies to ensure data retrieval")
    print("=" * 70)
    
    # Run the stock scanner with no-proxy flag and reduced limits for testing
    args = [
        'manage.py',
        'update_stocks_yfinance',
        '--limit', '50',  # Start with small limit
        '--threads', '10',  # Reduced threads
        '--no-proxy',  # Disable proxies
        '--test-mode',  # Test mode
        '--verbose'  # Verbose output
    ]
    
    print(f"Running: {' '.join(args)}")
    print("=" * 70)
    
    try:
        execute_from_command_line(args)
        print("\n✅ Stock scanner completed successfully!")
    except Exception as e:
        print(f"\n❌ Error running stock scanner: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)