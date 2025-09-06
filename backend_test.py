import requests
import sys
import json
from datetime import datetime

class StockScannerAPITester:
    def __init__(self, base_url="https://romantic-napier.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        # Default headers
        default_headers = {'Content-Type': 'application/json'}
        if self.token:
            default_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            default_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers, timeout=10)

            success = response.status_code == expected_status
            
            if success:
                try:
                    response_data = response.json()
                    self.log_test(name, True, f"Status: {response.status_code}")
                    return True, response_data
                except:
                    self.log_test(name, True, f"Status: {response.status_code} (No JSON)")
                    return True, {}
            else:
                try:
                    error_data = response.json()
                    self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}: {error_data}")
                except:
                    self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}: {response.text}")
                return False, {}

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}

    def test_health_endpoints(self):
        """Test basic health endpoints"""
        print("\n🔍 Testing Health Endpoints...")
        
        # Test root endpoint
        self.run_test("Root Endpoint", "GET", "", 200)
        
        # Test health endpoint
        self.run_test("Health Check", "GET", "health/", 200)
        
        # Test API index
        self.run_test("API Index", "GET", "api/", 200)

    def test_platform_stats(self):
        """Test platform statistics"""
        print("\n🔍 Testing Platform Stats...")
        
        success, data = self.run_test("Platform Stats", "GET", "api/platform-stats/", 200)
        if success and data:
            print(f"   📊 Total Stocks: {data.get('total_stocks', 'N/A')}")
            print(f"   📊 NYSE Stocks: {data.get('nyse_stocks', 'N/A')}")
            print(f"   📊 NASDAQ Stocks: {data.get('nasdaq_stocks', 'N/A')}")

    def test_stock_endpoints(self):
        """Test stock data endpoints"""
        print("\n🔍 Testing Stock Data Endpoints...")
        
        # Test get stocks
        success, data = self.run_test("Get Stocks", "GET", "api/stocks/", 200)
        if success and data:
            stocks = data.get('data', [])
            print(f"   📈 Retrieved {len(stocks)} stocks")
            if stocks:
                print(f"   📈 Sample stock: {stocks[0].get('symbol', 'N/A')} - ${stocks[0].get('current_price', 'N/A')}")

        # Test specific stock details
        self.run_test("Get AAPL Details", "GET", "api/stocks/AAPL/", 200)
        
        # Test stock quote
        self.run_test("Get AAPL Quote", "GET", "api/stocks/AAPL/quote/", 200)
        
        # Test realtime data
        self.run_test("Get AAPL Realtime", "GET", "api/realtime/AAPL/", 200)
        
        # Test stock search
        self.run_test("Search Stocks", "GET", "api/stocks/search/?q=AAPL", 200)
        
        # Test trending stocks
        success, data = self.run_test("Trending Stocks", "GET", "api/trending/", 200)
        if success and data:
            print(f"   🔥 High Volume: {len(data.get('high_volume', []))}")
            print(f"   🔥 Top Gainers: {len(data.get('top_gainers', []))}")

    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n🔍 Testing Authentication...")
        
        # Generate unique test user
        timestamp = datetime.now().strftime("%H%M%S")
        test_user = {
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        # Test registration
        success, data = self.run_test("User Registration", "POST", "api/auth/register/", 200, test_user)
        if success and data:
            self.user_data = data.get('data', {})
            print(f"   👤 Registered user: {self.user_data.get('username', 'N/A')}")
            print(f"   👤 User ID: {self.user_data.get('user_id', 'N/A')}")
        
        # Test login
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        success, data = self.run_test("User Login", "POST", "api/auth/login/", 200, login_data)
        if success and data:
            self.user_data = data.get('data', {})
            self.token = self.user_data.get('api_token')
            print(f"   🔑 Login successful, got token: {self.token[:20]}..." if self.token else "   ❌ No token received")

    def test_authenticated_endpoints(self):
        """Test endpoints that require authentication"""
        if not self.token:
            print("\n⚠️  Skipping authenticated tests - no token available")
            return
            
        print("\n🔍 Testing Authenticated Endpoints...")
        
        # Test user profile
        self.run_test("Get User Profile", "GET", "api/user/profile/", 200)
        
        # Test portfolio
        self.run_test("Get Portfolio", "GET", "api/portfolio/", 200)
        
        # Test add to portfolio
        portfolio_data = {"symbol": "AAPL"}
        self.run_test("Add to Portfolio", "POST", "api/portfolio/add/", 200, portfolio_data)
        
        # Test watchlist
        self.run_test("Get Watchlist", "GET", "api/watchlist/", 200)
        
        # Test add to watchlist
        watchlist_data = {"symbol": "GOOGL"}
        self.run_test("Add to Watchlist", "POST", "api/watchlist/add/", 200, watchlist_data)

    def test_market_endpoints(self):
        """Test market-related endpoints"""
        print("\n🔍 Testing Market Endpoints...")
        
        # Test market stats
        self.run_test("Market Stats", "GET", "api/market/stats/", 200)
        
        # Test NASDAQ stocks
        self.run_test("NASDAQ Stocks", "GET", "api/stocks/nasdaq/", 200)
        
        # Test market filter
        self.run_test("Market Filter", "GET", "api/market/filter/?min_price=100&max_price=500", 200)

    def test_usage_endpoints(self):
        """Test usage and billing endpoints"""
        print("\n🔍 Testing Usage Endpoints...")
        
        # Test usage stats
        self.run_test("Usage Stats", "GET", "api/usage/", 200)

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Stock Scanner API Tests...")
        print(f"🌐 Testing against: {self.base_url}")
        
        # Run test suites
        self.test_health_endpoints()
        self.test_platform_stats()
        self.test_stock_endpoints()
        self.test_authentication()
        self.test_authenticated_endpoints()
        self.test_market_endpoints()
        self.test_usage_endpoints()
        
        # Print summary
        print(f"\n📊 Test Summary:")
        print(f"   Total Tests: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Print failed tests
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"   • {test['name']}: {test['details']}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = StockScannerAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())