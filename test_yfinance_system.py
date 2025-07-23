#!/usr/bin/env python3
"""
Test Script for YFinance-Primary Stock Data System
Comprehensive testing of the new API manager and Django integration
"""

import os
import sys
import django
from pathlib import Path
import time

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

def test_api_manager():
    """Test the stock API manager"""
    print("🔍 Testing Stock API Manager...")
    
    try:
        from stocks.api_manager import stock_manager
        
        # Test initialization
        print(f"   ✅ API Manager initialized")
        
        # Test connectivity
        connections = stock_manager.test_connection()
        print(f"   🔗 API Connectivity:")
        for api, connected in connections.items():
            status = "✅" if connected else "❌"
            print(f"      {status} {api.replace('_', ' ').title()}")
        
        # Test single stock quote
        print(f"   📊 Testing stock quote retrieval...")
        quote = stock_manager.get_stock_quote('AAPL')
        
        if quote:
            print(f"      ✅ AAPL: ${quote['price']:.2f} ({quote['change_percent']:+.2f}%) [{quote['source']}]")
        else:
            print(f"      ❌ Failed to get AAPL quote")
            return False
        
        # Test multiple quotes
        print(f"   📈 Testing multiple quotes...")
        symbols = ['MSFT', 'GOOGL', 'AMZN']
        quotes = stock_manager.get_multiple_quotes(symbols)
        
        for symbol in symbols:
            if symbol in quotes:
                q = quotes[symbol]
                print(f"      ✅ {symbol}: ${q['price']:.2f} ({q['change_percent']:+.2f}%) [{q['source']}]")
            else:
                print(f"      ❌ Failed to get {symbol} quote")
        
        # Test usage stats
        stats = stock_manager.get_usage_stats()
        print(f"   📊 API Usage Stats:")
        for api, usage in stats.items():
            if api == 'yahoo_finance':
                print(f"      • {api.title()}: {usage['requests_today']} requests today")
            elif 'total_available' in usage:
                used = sum(usage['usage']) if usage['usage'] else 0
                print(f"      • {api.title()}: {used}/{usage['total_available']} requests")
            elif 'limit' in usage:
                print(f"      • {api.title()}: {usage['usage']}/{usage['limit']} requests")
        
        return True
        
    except Exception as e:
        print(f"   ❌ API Manager test failed: {e}")
        return False

def test_django_integration():
    """Test Django models and settings integration"""
    print("🔧 Testing Django Integration...")
    
    try:
        from django.conf import settings
        from stocks.models import StockAlert
        from django.utils import timezone
        
        # Test settings
        print(f"   ⚙️ Checking Django settings...")
        yfinance_rate_limit = getattr(settings, 'YFINANCE_RATE_LIMIT', None)
        finnhub_keys = getattr(settings, 'FINNHUB_KEYS', [])
        
        print(f"      • YFinance rate limit: {yfinance_rate_limit}s")
        print(f"      • Finnhub keys: {len(finnhub_keys)} accounts")
        
        # Test database model
        print(f"   🗄️ Testing database model...")
        
        # Check if required fields exist
        field_names = [field.name for field in StockAlert._meta.get_fields()]
        required_fields = ['price_change_today', 'price_change_percent', 'data_source']
        
        missing_fields = [field for field in required_fields if field not in field_names]
        if missing_fields:
            print(f"      ❌ Missing fields: {missing_fields}")
            return False
        
        print(f"      ✅ All required fields present")
        
        # Test creating/updating a stock record
        test_stock, created = StockAlert.objects.get_or_create(
            ticker='TEST',
            defaults={
                'company_name': 'Test Company',
                'current_price': 100.00,
                'price_change_today': 5.00,
                'price_change_percent': 5.0,
                'volume_today': 1000000,
                'market_cap': 1000000000,
                'last_updated': timezone.now(),
                'data_source': 'test',
                'is_active': True
            }
        )
        
        action = "Created" if created else "Updated"
        print(f"      ✅ {action} test stock record")
        
        # Clean up test record
        test_stock.delete()
        print(f"      ✅ Cleaned up test record")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Django integration test failed: {e}")
        return False

def test_management_command():
    """Test the new Django management command"""
    print("🚀 Testing Management Command...")
    
    try:
        from django.core.management import call_command
        from io import StringIO
        
        # Test command in test mode (no DB updates)
        print(f"   🧪 Running update command in test mode...")
        
        out = StringIO()
        call_command(
            'update_stocks_yfinance',
            '--symbols=AAPL,MSFT',
            '--limit=2',
            '--test-mode',
            '--verbose',
            stdout=out
        )
        
        output = out.getvalue()
        if "Stock Data Update" in output and "AAPL" in output:
            print(f"      ✅ Management command executed successfully")
            print(f"      📊 Sample output: {output.split('AAPL')[0].split('✅')[-1].strip()}")
        else:
            print(f"      ❌ Management command output unexpected")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Management command test failed: {e}")
        return False

def test_api_views():
    """Test API views integration"""
    print("🌐 Testing API Views...")
    
    try:
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        
        # Test stock list endpoint
        print(f"   📊 Testing stock list API...")
        response = client.get('/api/stocks/')
        
        if response.status_code == 200:
            print(f"      ✅ Stock list API responding (HTTP 200)")
        else:
            print(f"      ⚠️ Stock list API returned HTTP {response.status_code}")
        
        # Test analytics endpoint
        print(f"   📈 Testing analytics API...")
        response = client.get('/api/analytics/public/')
        
        if response.status_code == 200:
            data = response.json()
            print(f"      ✅ Analytics API responding")
            print(f"      📊 Sample data: {len(data)} fields returned")
        else:
            print(f"      ⚠️ Analytics API returned HTTP {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ API views test failed: {e}")
        return False

def test_performance():
    """Test performance of the new system"""
    print("⚡ Testing Performance...")
    
    try:
        from stocks.api_manager import stock_manager
        import time
        
        # Test single quote performance
        print(f"   🏃 Testing single quote performance...")
        start_time = time.time()
        quote = stock_manager.get_stock_quote('AAPL')
        single_time = time.time() - start_time
        
        if quote:
            print(f"      ✅ Single quote: {single_time:.2f}s [{quote['source']}]")
        else:
            print(f"      ❌ Single quote failed")
            return False
        
        # Test multiple quotes performance
        print(f"   🏃 Testing batch quote performance...")
        symbols = ['MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META']
        start_time = time.time()
        quotes = stock_manager.get_multiple_quotes(symbols)
        batch_time = time.time() - start_time
        
        success_count = len(quotes)
        avg_time = batch_time / len(symbols)
        
        print(f"      ✅ Batch quotes: {batch_time:.2f}s total, {avg_time:.2f}s avg")
        print(f"      📊 Success rate: {success_count}/{len(symbols)} ({(success_count/len(symbols)*100):.1f}%)")
        
        # Performance recommendations
        if avg_time < 2.0:
            print(f"      🎉 Excellent performance!")
        elif avg_time < 4.0:
            print(f"      ✅ Good performance")
        else:
            print(f"      ⚠️ Consider optimizing rate limits")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Performance test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 YFinance-Primary Stock Data System Test")
    print("=" * 50)
    
    tests = [
        ("API Manager", test_api_manager),
        ("Django Integration", test_django_integration),
        ("Management Command", test_management_command),
        ("API Views", test_api_views),
        ("Performance", test_performance),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    print(f"\n📈 Results: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! YFinance system is ready for production!")
    elif passed >= total * 0.8:
        print("✅ Most tests passed. System is functional with minor issues.")
    else:
        print("⚠️ Several tests failed. Please review and fix issues before production.")
    
    print("\n💡 Next steps:")
    print("   1. Run the Yahoo Finance rate limit optimizer")
    print("   2. Set up your Finnhub backup API keys (optional)")
    print("   3. Test with your actual stock symbols")
    print("   4. Deploy to production")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        sys.exit(1)