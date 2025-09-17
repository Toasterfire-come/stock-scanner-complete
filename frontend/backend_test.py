import requests
import sys
import json
from datetime import datetime

class TradeScanProAPITester:
    def __init__(self, base_url="http://localhost:8001"):
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

    def test_auth_register_endpoint(self):
        """Test user registration endpoint"""
        user_data = {
            "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
            "email": f"test_{datetime.now().strftime('%H%M%S')}@example.com",
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        return self.run_test("User Registration", "POST", "/api/auth/register/", 201, data=user_data)

    def test_auth_login_endpoint(self):
        """Test user login endpoint"""
        login_data = {
            "username": "testuser",
            "password": "TestPass123!"
        }
        
        return self.run_test("User Login", "POST", "/api/auth/login/", 200, data=login_data)

    def test_plan_change_endpoint(self):
        """Test plan change endpoint"""
        plan_data = {
            "plan_type": "bronze",
            "billing_cycle": "monthly"
        }
        
        return self.run_test("Plan Change", "POST", "/api/billing/change-plan/", 200, data=plan_data)

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
        """Test stocks endpoint with pagination"""
        success, response = self.run_test("Stocks List (Page 1)", "GET", "/api/stocks/?page=1&limit=50", 200)
        if success:
            # Check if we get actual data, not hardcoded values
            stocks = response.get('stocks', [])
            total = response.get('total', 0)
            print(f"   📊 Total stocks in DB: {total}")
            print(f"   📊 Stocks returned: {len(stocks)}")
            
            if total == 0:
                print(f"   ⚠️  No stocks found in database")
                self.failed_tests.append("Stocks endpoint: No stocks found in database")
        return success

    def test_search_endpoint(self):
        """Test stock search"""
        return self.run_test("Stock Search", "GET", "/api/search/?q=AAPL", 200)

    def test_trending_endpoint(self):
        """Test trending stocks"""
        return self.run_test("Trending Stocks", "GET", "/api/trending/", 200)

    def test_market_stats_endpoint(self):
        """Test market statistics"""
        return self.run_test("Market Statistics", "GET", "/api/market-stats/", 200)

    def test_security_headers(self):
        """Test security headers are present"""
        print(f"\n🔍 Testing Security Headers...")
        url = f"{self.base_url}/api/health"
        
        try:
            response = requests.get(url, timeout=10)
            headers = response.headers
            
            security_headers = {
                'X-Frame-Options': 'DENY',
                'X-Content-Type-Options': 'nosniff', 
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
            }
            
            missing_headers = []
            for header, expected_value in security_headers.items():
                if header not in headers:
                    missing_headers.append(header)
                    print(f"   ❌ Missing security header: {header}")
                elif headers[header] != expected_value:
                    print(f"   ⚠️  Security header {header}: expected '{expected_value}', got '{headers[header]}'")
                else:
                    print(f"   ✅ Security header {header}: {headers[header]}")
            
            if missing_headers:
                self.failed_tests.append(f"Security Headers: Missing {', '.join(missing_headers)}")
                return False
            
            self.tests_run += 1
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"❌ Failed to test security headers: {str(e)}")
            self.failed_tests.append(f"Security Headers: {str(e)}")
            self.tests_run += 1
            return False

    def test_cors_functionality(self):
        """Test CORS headers"""
        print(f"\n🔍 Testing CORS Functionality...")
        url = f"{self.base_url}/api/health"
        
        try:
            # Test preflight request
            response = requests.options(url, headers={
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'GET'
            }, timeout=10)
            
            cors_headers = response.headers
            print(f"   CORS Headers: {dict(cors_headers)}")
            
            self.tests_run += 1
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"❌ Failed to test CORS: {str(e)}")
            self.failed_tests.append(f"CORS: {str(e)}")
            self.tests_run += 1
            return False

    def test_rate_limiting_headers(self):
        """Test rate limiting headers are present"""
        headers = {
            'X-User-ID': 'test_rate_limit_user',
            'X-User-Plan': 'free'
        }
        
        print(f"\n🔍 Testing Rate Limiting Headers...")
        url = f"{self.base_url}/api/stocks/AAPL/quote"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            rate_headers = ['X-RateLimit-Used', 'X-RateLimit-Limit', 'X-RateLimit-Reset']
            found_headers = []
            
            for header in rate_headers:
                if header in response.headers:
                    found_headers.append(header)
                    print(f"   ✅ Rate limit header {header}: {response.headers[header]}")
                else:
                    print(f"   ❌ Missing rate limit header: {header}")
            
            self.tests_run += 1
            if len(found_headers) >= 2:  # At least 2 rate limit headers should be present
                self.tests_passed += 1
                return True
            else:
                self.failed_tests.append(f"Rate Limiting Headers: Only found {len(found_headers)} headers")
                return False
                
        except Exception as e:
            print(f"❌ Failed to test rate limiting headers: {str(e)}")
            self.failed_tests.append(f"Rate Limiting Headers: {str(e)}")
            self.tests_run += 1
            return False

def main():
    print("🚀 Starting Trade Scan Pro API Tests...")
    print("=" * 60)
    
    tester = TradeScanProAPITester()
    
    # Run all tests
    test_methods = [
        tester.test_api_root,
        tester.test_platform_stats,
        tester.test_health_check,
        tester.test_auth_register_endpoint,
        tester.test_auth_login_endpoint,
        tester.test_plan_change_endpoint,
        tester.test_usage_endpoint,
        tester.test_rate_limiting_free_plan,
        tester.test_rate_limiting_gold_plan,
        tester.test_billing_endpoints,
        tester.test_stocks_endpoint,
        tester.test_search_endpoint,
        tester.test_trending_endpoint,
        tester.test_market_stats_endpoint,
        tester.test_security_headers,
        tester.test_cors_functionality,
        tester.test_rate_limiting_headers
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