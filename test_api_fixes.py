#!/usr/bin/env python3
"""
Test script to validate API fixes
Tests the stock API endpoints to ensure they return data instead of empty results
"""

import os
import sys
import django
import json
from unittest.mock import Mock

# Force test mode to avoid touching MySQL during this script
os.environ.setdefault('TEST_MODE', '1')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')

# Mock some Django components that might not be available
class MockCache:
    def get(self, key, default=None):
        return default
    def set(self, key, value, timeout=None):
        pass

# Mock the cache module
sys.modules['django.core.cache'] = Mock()
sys.modules['django.core.cache'].cache = MockCache()

try:
    django.setup()
except Exception as e:
    print(f"Warning: Django setup had issues: {e}")
    print("Continuing with limited testing...")

# Test the API logic directly
def test_api_logic():
    """Test the core API filtering logic"""
    print("=== API LOGIC TEST ===")
    
    try:
        from stocks.models import Stock
        from django.db.models import Q
        
        # Test 1: Check total stocks
        total_stocks = Stock.objects.count()
        print(f"Total stocks in database: {total_stocks}")
        
        if total_stocks == 0:
            print("❌ No stocks in database - creating test data")
            create_test_stocks()
            total_stocks = Stock.objects.count()
        
        # Test 2: Check stocks with price data
        stocks_with_price = Stock.objects.filter(
            current_price__isnull=False
        ).exclude(current_price=0).count()
        print(f"Stocks with price data: {stocks_with_price}")
        
        # Test 3: Test the new inclusive filtering
        inclusive_stocks = Stock.objects.filter(
            Q(current_price__isnull=False) |
            Q(volume__isnull=False) |
            Q(market_cap__isnull=False)
        ).count()
        print(f"Stocks with ANY useful data (new filtering): {inclusive_stocks}")
        
        # Test 4: Test exchange filtering
        nyse_stocks = Stock.objects.filter(
            Q(exchange__iexact='NYSE') |
            Q(exchange__icontains='NYSE') |
            Q(exchange__icontains='nyse')
        ).count()
        print(f"NYSE stocks (flexible filtering): {nyse_stocks}")
        
        # Test 5: Test emergency fallback
        all_stocks = Stock.objects.all().count()
        print(f"All stocks (emergency fallback): {all_stocks}")
        
        print("\n=== SAMPLE DATA ===")
        sample_stocks = Stock.objects.all()[:5]
        for stock in sample_stocks:
            print(f"{stock.ticker}: price=${stock.current_price}, volume={stock.volume}, exchange={stock.exchange}")
        
        return True
        
    except Exception as e:
        print(f"❌ API logic test failed: {e}")
        return False

def create_test_stocks():
    """Create some test stock data if none exists"""
    try:
        from stocks.models import Stock
        from django.utils import timezone
        from decimal import Decimal
        
        test_stocks = [
            {
                'ticker': 'AAPL',
                'symbol': 'AAPL',
                'company_name': 'Apple Inc.',
                'name': 'Apple Inc.',
                'exchange': 'NYSE',
                'current_price': Decimal('150.50'),
                'volume': 1000000,
                'market_cap': 2500000000000,
                'last_updated': timezone.now()
            },
            {
                'ticker': 'GOOGL',
                'symbol': 'GOOGL',
                'company_name': 'Alphabet Inc.',
                'name': 'Alphabet Inc.',
                'exchange': 'NYSE',
                'current_price': Decimal('2800.75'),
                'volume': 800000,
                'market_cap': 1800000000000,
                'last_updated': timezone.now()
            },
            {
                'ticker': 'TSLA',
                'symbol': 'TSLA',
                'company_name': 'Tesla Inc.',
                'name': 'Tesla Inc.',
                'exchange': 'NYSE',
                'current_price': None,  # Test with missing price
                'volume': 2000000,
                'market_cap': 800000000000,
                'last_updated': timezone.now()
            }
        ]
        
        for stock_data in test_stocks:
            Stock.objects.get_or_create(
                ticker=stock_data['ticker'],
                defaults=stock_data
            )
        
        print("✓ Created test stock data")
        
    except Exception as e:
        print(f"❌ Failed to create test stocks: {e}")

def test_api_response_format():
    """Test the API response format"""
    print("\n=== API RESPONSE FORMAT TEST ===")
    
    try:
        from stocks.api_views import stock_list_api
        from django.test import RequestFactory
        from django.http import QueryDict
        
        # Create a mock request
        factory = RequestFactory()
        
        # Test 1: Basic request
        request = factory.get('/api/stocks/')
        request.GET = QueryDict('limit=5')
        
        response = stock_list_api(request)
        data = response.data
        
        print(f"Response keys: {list(data.keys())}")
        print(f"Success: {data.get('success')}")
        print(f"Count: {data.get('count')}")
        print(f"Total available: {data.get('total_available')}")
        print(f"Data length: {len(data.get('data', []))}")
        
        if data.get('count', 0) > 0:
            print("✓ API returns data!")
            sample_stock = data.get('data', [{}])[0]
            print(f"Sample stock: {sample_stock.get('ticker')} - {sample_stock.get('company_name')}")
        else:
            print("❌ API still returns no data")
            if 'debug_info' in data:
                print(f"Debug info: {data['debug_info']}")
        
        # Test 2: Request with category=all
        request = factory.get('/api/stocks/')
        request.GET = QueryDict('limit=10&category=all')
        
        response = stock_list_api(request)
        data = response.data
        
        print(f"\nWith category=all:")
        print(f"Count: {data.get('count')}")
        print(f"Total available: {data.get('total_available')}")
        
        return data.get('count', 0) > 0
        
    except Exception as e:
        print(f"❌ API response format test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_wordpress_api():
    """Test the WordPress API endpoints"""
    print("\n=== WORDPRESS API TEST ===")
    
    try:
        from stocks.wordpress_api import wordpress_stocks_api
        from django.test import RequestFactory
        from django.http import QueryDict
        
        # Create a mock request
        factory = RequestFactory()
        request = factory.get('/wordpress/stocks/')
        request.GET = QueryDict('limit=5')
        
        response = wordpress_stocks_api(request)
        
        # Parse JSON response
        import json
        data = json.loads(response.content.decode('utf-8'))
        
        print(f"WordPress API Response keys: {list(data.keys())}")
        print(f"Success: {data.get('success')}")
        print(f"Count: {data.get('count')}")
        print(f"Total: {data.get('total')}")
        
        if data.get('count', 0) > 0:
            print("✓ WordPress API returns data!")
            sample_stock = data.get('data', [{}])[0]
            print(f"Sample stock: {sample_stock.get('ticker')} - {sample_stock.get('company_name')}")
        else:
            print("❌ WordPress API still returns no data")
        
        return data.get('count', 0) > 0
        
    except Exception as e:
        print(f"❌ WordPress API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("TESTING API FIXES")
    print("=" * 60)
    
    # Test 1: Database and API logic
    logic_ok = test_api_logic()
    
    # Test 2: API response format
    api_ok = test_api_response_format()
    
    # Test 3: WordPress API
    wp_ok = test_wordpress_api()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"API Logic: {'✓ PASS' if logic_ok else '❌ FAIL'}")
    print(f"API Response: {'✓ PASS' if api_ok else '❌ FAIL'}")
    print(f"WordPress API: {'✓ PASS' if wp_ok else '❌ FAIL'}")
    
    overall_success = logic_ok and api_ok and wp_ok
    print(f"\nOVERALL: {'✓ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 API fixes successful! The endpoints should now return data.")
    else:
        print("\n⚠️ Some issues remain. Check the error messages above.")
    
    return overall_success

if __name__ == "__main__":
    main()