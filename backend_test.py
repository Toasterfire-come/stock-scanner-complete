#!/usr/bin/env python3
"""
Comprehensive Django Stock Scanner API Test Suite
Tests all critical endpoints mentioned in the review request
"""

import requests
import json
import sys
from datetime import datetime
import time

class StockScannerAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.token = "1edc7e6a-3c60-4320-b121-b7e82a5817b3"  # Provided test token
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        })

    def log_test(self, name, success, response_data=None, error_msg=None):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
            if response_data and isinstance(response_data, dict):
                # Check if response indicates success
                if response_data.get('success') == False:
                    self.tests_passed -= 1
                    self.failed_tests.append(name)
                    print(f"❌ {name} - FAILED (API returned success=false)")
                    print(f"   Error: {response_data.get('error', 'Unknown error')}")
                    return
                print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
        else:
            self.failed_tests.append(name)
            print(f"❌ {name} - FAILED")
            if error_msg:
                print(f"   Error: {error_msg}")
        print("-" * 60)

    def test_health_check(self):
        """Test basic health check"""
        try:
            response = requests.get(f"{self.base_url}/health/")
            success = response.status_code == 200
            data = response.json() if success else {}
            self.log_test("Health Check", success, data)
            return success
        except Exception as e:
            self.log_test("Health Check", False, error_msg=str(e))
            return False

    def test_auth_register(self):
        """Test user registration"""
        try:
            test_user = f"testuser_{int(time.time())}"
            data = {
                "username": test_user,
                "email": f"{test_user}@test.com",
                "password": "testpass123",
                "first_name": "Test",
                "last_name": "User"
            }
            response = self.session.post(f"{self.api_base}/auth/register/", json=data)
            success = response.status_code in [200, 201]
            result = response.json() if success else {"error": response.text}
            self.log_test("Auth Register", success, result)
            return success
        except Exception as e:
            self.log_test("Auth Register", False, error_msg=str(e))
            return False

    def test_auth_login(self):
        """Test user login with provided credentials"""
        try:
            data = {
                "username": "testuser",
                "password": "testpass123"
            }
            response = self.session.post(f"{self.api_base}/auth/login/", json=data)
            success = response.status_code == 200
            result = response.json() if success else {"error": response.text}
            self.log_test("Auth Login", success, result)
            return success
        except Exception as e:
            self.log_test("Auth Login", False, error_msg=str(e))
            return False

    def test_user_profile(self):
        """Test getting user profile with token"""
        try:
            response = self.session.get(f"{self.api_base}/user/profile/")
            success = response.status_code == 200
            result = response.json() if success else {"error": response.text}
            self.log_test("User Profile", success, result)
            return success
        except Exception as e:
            self.log_test("User Profile", False, error_msg=str(e))
            return False

    def test_billing_current_plan(self):
        """Test getting current billing plan"""
        try:
            response = self.session.get(f"{self.api_base}/billing/current-plan/")
            success = response.status_code == 200
            result = response.json() if success else {"error": response.text}
            self.log_test("Billing Current Plan", success, result)
            return success
        except Exception as e:
            self.log_test("Billing Current Plan", False, error_msg=str(e))
            return False

    def test_billing_history(self):
        """Test getting billing history"""
        try:
            response = self.session.get(f"{self.api_base}/billing/history/")
            success = response.status_code == 200
            result = response.json() if success else {"error": response.text}
            self.log_test("Billing History", success, result)
            return success
        except Exception as e:
            self.log_test("Billing History", False, error_msg=str(e))
            return False

    def test_create_paypal_order(self):
        """Test creating PayPal order for different plans"""
        plans = ["bronze", "silver", "gold"]
        for plan in plans:
            try:
                data = {"plan": plan}
                response = self.session.post(f"{self.api_base}/billing/create-paypal-order/", json=data)
                success = response.status_code in [200, 201]
                result = response.json() if success else {"error": response.text}
                self.log_test(f"Create PayPal Order ({plan})", success, result)
            except Exception as e:
                self.log_test(f"Create PayPal Order ({plan})", False, error_msg=str(e))

    def test_usage_stats(self):
        """Test API usage statistics"""
        try:
            response = self.session.get(f"{self.api_base}/usage/")
            success = response.status_code == 200
            result = response.json() if success else {"error": response.text}
            self.log_test("Usage Statistics", success, result)
            return success
        except Exception as e:
            self.log_test("Usage Statistics", False, error_msg=str(e))
            return False

    def test_platform_stats(self):
        """Test platform statistics"""
        try:
            response = self.session.get(f"{self.api_base}/platform-stats/")
            success = response.status_code == 200
            result = response.json() if success else {"error": response.text}
            self.log_test("Platform Statistics", success, result)
            return success
        except Exception as e:
            self.log_test("Platform Statistics", False, error_msg=str(e))
            return False

    def test_stock_quote(self):
        """Test individual stock quote endpoint"""
        symbols = ["AAPL", "GOOGL", "MSFT"]
        for symbol in symbols:
            try:
                response = self.session.get(f"{self.api_base}/stocks/{symbol}/quote/")
                success = response.status_code == 200
                result = response.json() if success else {"error": response.text}
                self.log_test(f"Stock Quote ({symbol})", success, result)
            except Exception as e:
                self.log_test(f"Stock Quote ({symbol})", False, error_msg=str(e))

    def test_realtime_data(self):
        """Test real-time stock data endpoint"""
        symbols = ["AAPL", "GOOGL", "MSFT"]
        for symbol in symbols:
            try:
                response = self.session.get(f"{self.api_base}/realtime/{symbol}/")
                success = response.status_code == 200
                result = response.json() if success else {"error": response.text}
                self.log_test(f"Realtime Data ({symbol})", success, result)
            except Exception as e:
                self.log_test(f"Realtime Data ({symbol})", False, error_msg=str(e))

    def test_batch_quotes(self):
        """Test batch quotes endpoint"""
        try:
            symbols = "AAPL,GOOGL,MSFT"
            response = self.session.get(f"{self.api_base}/stocks/quotes/batch/?symbols={symbols}")
            success = response.status_code == 200
            result = response.json() if success else {"error": response.text}
            self.log_test("Batch Quotes", success, result)
            return success
        except Exception as e:
            self.log_test("Batch Quotes", False, error_msg=str(e))
            return False

    def test_stock_list(self):
        """Test stock list endpoint"""
        try:
            response = self.session.get(f"{self.api_base}/stocks/")
            success = response.status_code == 200
            result = response.json() if success else {"error": response.text}
            self.log_test("Stock List", success, result)
            return success
        except Exception as e:
            self.log_test("Stock List", False, error_msg=str(e))
            return False

    def test_stock_search(self):
        """Test stock search endpoint"""
        try:
            response = self.session.get(f"{self.api_base}/stocks/search/?q=Apple")
            success = response.status_code == 200
            result = response.json() if success else {"error": response.text}
            self.log_test("Stock Search", success, result)
            return success
        except Exception as e:
            self.log_test("Stock Search", False, error_msg=str(e))
            return False

    def test_rate_limiting(self):
        """Test rate limiting behavior"""
        try:
            # Make multiple rapid requests to test rate limiting
            responses = []
            for i in range(5):
                response = self.session.get(f"{self.api_base}/stocks/AAPL/quote/")
                responses.append(response.status_code)
                time.sleep(0.1)  # Small delay between requests
            
            # Check if any requests were rate limited (429 status)
            rate_limited = any(status == 429 for status in responses)
            success_responses = sum(1 for status in responses if status == 200)
            
            self.log_test("Rate Limiting Test", True, {
                "responses": responses,
                "rate_limited": rate_limited,
                "successful": success_responses
            })
            return True
        except Exception as e:
            self.log_test("Rate Limiting Test", False, error_msg=str(e))
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Django Stock Scanner API Tests")
        print(f"📍 Base URL: {self.base_url}")
        print(f"🔑 Using Token: {self.token[:20]}...")
        print("=" * 60)

        # Basic connectivity
        if not self.test_health_check():
            print("❌ Health check failed - stopping tests")
            return False

        # Authentication tests
        print("\n🔐 AUTHENTICATION TESTS")
        self.test_auth_register()
        self.test_auth_login()
        self.test_user_profile()

        # Billing tests
        print("\n💳 BILLING TESTS")
        self.test_billing_current_plan()
        self.test_billing_history()
        self.test_create_paypal_order()

        # Usage and platform stats
        print("\n📊 USAGE & PLATFORM TESTS")
        self.test_usage_stats()
        self.test_platform_stats()

        # Stock data tests
        print("\n📈 STOCK DATA TESTS")
        self.test_stock_quote()
        self.test_realtime_data()
        self.test_batch_quotes()
        self.test_stock_list()
        self.test_stock_search()

        # Performance tests
        print("\n⚡ PERFORMANCE TESTS")
        self.test_rate_limiting()

        # Final results
        print("\n" + "=" * 60)
        print(f"📊 TEST RESULTS: {self.tests_passed}/{self.tests_run} PASSED")
        
        if self.failed_tests:
            print(f"❌ FAILED TESTS: {', '.join(self.failed_tests)}")
            return False
        else:
            print("✅ ALL TESTS PASSED!")
            return True

def main():
    """Main test runner"""
    tester = StockScannerAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())