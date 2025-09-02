import requests
import sys
import json
from datetime import datetime

class TradeScanProAPITester:
    def __init__(self, base_url="https://stock-tracker-158.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)}")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text}")
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append(f"{name}: {str(e)}")
            return False, {}

    def test_api_root(self):
        """Test API root endpoint"""
        return self.run_test("API Root", "GET", "/api/", 200)

    def test_platform_stats(self):
        """Test platform statistics - verify factual claims"""
        success, response = self.run_test("Platform Stats", "GET", "/api/platform-stats", 200)
        if success:
            # Verify factual claims
            nyse_stocks = response.get('nyse_stocks', 0)
            total_indicators = response.get('total_indicators', 0)
            
            print(f"   📊 NYSE Stocks: {nyse_stocks} (should be ~3,200)")
            print(f"   📊 Total Indicators: {total_indicators} (should be 14)")
            
            # Check if values are factual
            if nyse_stocks != 3200:
                print(f"   ⚠️  NYSE stock count should be 3200, got {nyse_stocks}")
                self.failed_tests.append(f"Platform Stats: NYSE stocks should be 3200, got {nyse_stocks}")
            
            if total_indicators != 14:
                print(f"   ⚠️  Indicator count should be 14, got {total_indicators}")
                self.failed_tests.append(f"Platform Stats: Indicators should be 14, got {total_indicators}")
        
        return success

    def test_health_check(self):
        """Test health check endpoint"""
        return self.run_test("Health Check", "GET", "/api/health", 200)

    def test_usage_endpoint(self):
        """Test usage tracking endpoint"""
        headers = {
            'X-User-ID': 'test_user_123',
            'X-User-Plan': 'free'
        }
        return self.run_test("Usage Stats", "GET", "/api/usage", 200, headers=headers)

    def test_rate_limiting_free_plan(self):
        """Test rate limiting for free plan"""
        headers = {
            'X-User-ID': 'test_free_user',
            'X-User-Plan': 'free'
        }
        
        print(f"\n🔍 Testing Rate Limiting for Free Plan...")
        
        # Make multiple requests to test limits
        for i in range(3):
            success, response = self.run_test(
                f"Stock Quote Request {i+1}", 
                "GET", 
                "/api/stocks/AAPL/quote", 
                200, 
                headers=headers
            )
            if not success:
                break
        
        return True

    def test_rate_limiting_gold_plan(self):
        """Test unlimited access for gold plan"""
        headers = {
            'X-User-ID': 'test_gold_user',
            'X-User-Plan': 'gold'
        }
        
        return self.run_test("Gold Plan Access", "GET", "/api/stocks/AAPL/quote", 200, headers=headers)

    def test_billing_endpoints(self):
        """Test billing endpoints for $1 trial"""
        # Test PayPal order creation
        order_data = {
            "plan": "bronze",
            "trial": True,
            "amount": "1.00"
        }
        
        success, response = self.run_test(
            "Create PayPal Order ($1 Trial)", 
            "POST", 
            "/api/billing/create-paypal-order/", 
            200, 
            data=order_data
        )
        
        if success:
            amount = response.get('amount', '')
            if amount != "1.00":
                print(f"   ⚠️  Trial amount should be $1.00, got ${amount}")
                self.failed_tests.append(f"Billing: Trial amount should be $1.00, got ${amount}")
        
        return success

    def test_stocks_endpoint(self):
        """Test stocks endpoint with NYSE focus"""
        return self.run_test("Stocks List (NYSE)", "GET", "/api/stocks/?category=nyse&limit=10", 200)

    def test_search_endpoint(self):
        """Test stock search"""
        return self.run_test("Stock Search", "GET", "/api/search/?q=AAPL", 200)

    def test_trending_endpoint(self):
        """Test trending stocks"""
        return self.run_test("Trending Stocks", "GET", "/api/trending/", 200)

def main():
    print("🚀 Starting Trade Scan Pro API Tests...")
    print("=" * 60)
    
    tester = TradeScanProAPITester()
    
    # Run all tests
    test_methods = [
        tester.test_api_root,
        tester.test_platform_stats,
        tester.test_health_check,
        tester.test_usage_endpoint,
        tester.test_rate_limiting_free_plan,
        tester.test_rate_limiting_gold_plan,
        tester.test_billing_endpoints,
        tester.test_stocks_endpoint,
        tester.test_search_endpoint,
        tester.test_trending_endpoint
    ]
    
    for test_method in test_methods:
        try:
            test_method()
        except Exception as e:
            print(f"❌ Test {test_method.__name__} failed with exception: {str(e)}")
            tester.failed_tests.append(f"{test_method.__name__}: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULTS")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {len(tester.failed_tests)}")
    
    if tester.failed_tests:
        print(f"\n❌ FAILED TESTS:")
        for failure in tester.failed_tests:
            print(f"   - {failure}")
    else:
        print(f"\n✅ All tests passed!")
    
    return 0 if len(tester.failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())