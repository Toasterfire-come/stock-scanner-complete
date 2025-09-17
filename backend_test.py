import requests
import sys
import json
from datetime import datetime

class StockScannerAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.session = requests.Session()
        self.csrf_token = None
        self.auth_headers = {}

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)
        if self.auth_headers:
            default_headers.update(self.auth_headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=default_headers, timeout=10)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=default_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:500]}...")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:500]}...")
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append(f"{name}: {str(e)}")
            return False, {}

    def get_csrf_token(self):
        """Get CSRF token for authentication"""
        try:
            response = self.session.get(f"{self.base_url}/api/auth/csrf/")
            if response.status_code == 200:
                data = response.json()
                self.csrf_token = data.get('csrfToken')
                print(f"✅ CSRF token obtained: {self.csrf_token[:20]}...")
                return True
        except Exception as e:
            print(f"❌ Failed to get CSRF token: {str(e)}")
        return False

    def test_login(self):
        """Test login with admin credentials"""
        if not self.get_csrf_token():
            return False
            
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        headers = {
            'X-CSRFToken': self.csrf_token,
            'Referer': self.base_url
        }
        
        success, response = self.run_test(
            "Admin Login", 
            "POST", 
            "/api/auth/login/", 
            200, 
            data=login_data,
            headers=headers
        )
        
        if success:
            # Update auth headers for subsequent requests
            if 'sessionid' in self.session.cookies:
                self.auth_headers['X-CSRFToken'] = self.csrf_token
                print("✅ Authentication successful")
                return True
        
        return False

    # Core API Endpoints Tests
    def test_health_check(self):
        """Test health check endpoint"""
        return self.run_test("Health Check", "GET", "/api/health/", 200)

    def test_stocks_list(self):
        """Test stock list endpoint"""
        success, response = self.run_test("Stock List", "GET", "/api/stocks/", 200)
        if success:
            stocks = response.get('results', []) or response.get('data', [])
            total = response.get('count', 0) or len(stocks)
            print(f"   📊 Total stocks: {total}")
            print(f"   📊 Stocks returned: {len(stocks)}")
            
            if total == 0:
                print(f"   ⚠️  No stocks found in database")
                self.failed_tests.append("Stocks endpoint: No stocks found in database")
            elif total != 15:
                print(f"   ⚠️  Expected 15 stocks, got {total}")
                self.failed_tests.append(f"Stocks endpoint: Expected 15 stocks, got {total}")
        return success

    def test_total_tickers(self):
        """Test total tickers count endpoint"""
        success, response = self.run_test("Total Tickers", "GET", "/api/stats/total-tickers/", 200)
        if success:
            total = response.get('total_tickers', 0)
            print(f"   📊 Total tickers: {total}")
            if total != 15:
                print(f"   ⚠️  Expected 15 tickers, got {total}")
                self.failed_tests.append(f"Total Tickers: Expected 15, got {total}")
        return success

    def test_gainers_losers_stats(self):
        """Test gainers/losers statistics endpoint"""
        success, response = self.run_test("Gainers/Losers Stats", "GET", "/api/stats/gainers-losers/", 200)
        if success:
            gainers = response.get('total_gainers', 0)
            losers = response.get('total_losers', 0)
            gainers_percent = response.get('gainer_percentage', 0)
            losers_percent = response.get('loser_percentage', 0)
            
            print(f"   📊 Gainers: {gainers} ({gainers_percent}%)")
            print(f"   📊 Losers: {losers} ({losers_percent}%)")
            
            # Expected approximately 8 gainers, 7 losers
            if gainers < 5 or gainers > 10:
                print(f"   ⚠️  Expected ~8 gainers, got {gainers}")
                self.failed_tests.append(f"Gainers/Losers: Expected ~8 gainers, got {gainers}")
            if losers < 5 or losers > 10:
                print(f"   ⚠️  Expected ~7 losers, got {losers}")
                self.failed_tests.append(f"Gainers/Losers: Expected ~7 losers, got {losers}")
        return success

    def test_total_alerts(self):
        """Test total alerts count endpoint"""
        success, response = self.run_test("Total Alerts", "GET", "/api/stats/total-alerts/", 200)
        if success:
            total = response.get('total_alerts', 0)
            print(f"   📊 Total alerts: {total}")
            if total != 8:
                print(f"   ⚠️  Expected 8 alerts, got {total}")
                self.failed_tests.append(f"Total Alerts: Expected 8, got {total}")
        return success

    # Portfolio Endpoints (require authentication)
    def test_portfolio_value(self):
        """Test portfolio value endpoint (requires auth)"""
        # Try with API token from login response
        headers = {'Authorization': f'Bearer {getattr(self, "api_token", "")}'}
        success, response = self.run_test("Portfolio Value", "GET", "/api/portfolio/value/", 200, headers=headers)
        if success:
            value = response.get('total_value', 0)
            print(f"   📊 Portfolio value: ${value}")
            if value != 50000:
                print(f"   ⚠️  Expected $50,000, got ${value}")
                self.failed_tests.append(f"Portfolio Value: Expected $50,000, got ${value}")
        return success

    def test_portfolio_pnl(self):
        """Test portfolio P&L endpoint (requires auth)"""
        headers = {'Authorization': f'Bearer {getattr(self, "api_token", "")}'}
        success, response = self.run_test("Portfolio P&L", "GET", "/api/portfolio/pnl/", 200, headers=headers)
        if success:
            pnl = response.get('total_pnl', 0)
            pnl_percent = response.get('pnl_percentage', 0)
            print(f"   📊 Portfolio P&L: ${pnl} ({pnl_percent}%)")
        return success

    def test_portfolio_holdings_count(self):
        """Test portfolio holdings count endpoint (requires auth)"""
        headers = {'Authorization': f'Bearer {getattr(self, "api_token", "")}'}
        success, response = self.run_test("Portfolio Holdings Count", "GET", "/api/portfolio/holdings-count/", 200, headers=headers)
        if success:
            count = response.get('total_holdings', 0)
            print(f"   📊 Portfolio holdings: {count}")
            if count != 3:
                print(f"   ⚠️  Expected 3 holdings, got {count}")
                self.failed_tests.append(f"Portfolio Holdings: Expected 3, got {count}")
        return success

    # Additional Stock Endpoints
    def test_top_gainers(self):
        """Test top gainers endpoint"""
        success, response = self.run_test("Top Gainers", "GET", "/api/stocks/top-gainers/", 200)
        if success:
            stocks = response.get('results', []) or response.get('data', [])
            print(f"   📊 Top gainers returned: {len(stocks)}")
            if len(stocks) == 0:
                print(f"   ⚠️  No gainers found")
                self.failed_tests.append("Top Gainers: No gainers returned")
        return success

    def test_top_losers(self):
        """Test top losers endpoint"""
        success, response = self.run_test("Top Losers", "GET", "/api/stocks/top-losers/", 200)
        if success:
            stocks = response.get('results', []) or response.get('data', [])
            print(f"   📊 Top losers returned: {len(stocks)}")
            if len(stocks) == 0:
                print(f"   ⚠️  No losers found")
                self.failed_tests.append("Top Losers: No losers returned")
        return success

    def test_most_active(self):
        """Test most active stocks endpoint"""
        success, response = self.run_test("Most Active", "GET", "/api/stocks/most-active/", 200)
        if success:
            stocks = response.get('results', []) or response.get('data', [])
            print(f"   📊 Most active returned: {len(stocks)}")
            if len(stocks) == 0:
                print(f"   ⚠️  No active stocks found")
                self.failed_tests.append("Most Active: No active stocks returned")
        return success

    def test_stock_search(self):
        """Test stock search endpoint"""
        success, response = self.run_test("Stock Search (AAPL)", "GET", "/api/search/?q=AAPL", 200)
        if success:
            results = response.get('results', []) or response.get('data', [])
            print(f"   📊 Search results: {len(results)}")
            if len(results) == 0:
                print(f"   ⚠️  No search results for AAPL")
                self.failed_tests.append("Stock Search: No results for AAPL")
        return success

    def test_individual_stock(self):
        """Test individual stock detail endpoint"""
        success, response = self.run_test("Stock Detail (AAPL)", "GET", "/api/stocks/AAPL/", 200)
        if success:
            # Check if data is nested
            data = response.get('data', response)
            ticker = data.get('ticker') or data.get('symbol')
            price = data.get('current_price') or data.get('price')
            print(f"   📊 Stock: {ticker}, Price: ${price}")
            if not ticker:
                print(f"   ⚠️  No ticker found in response")
                self.failed_tests.append("Stock Detail: No ticker in response")
        return success

    def test_market_stats(self):
        """Test market statistics endpoint"""
        success, response = self.run_test("Market Statistics", "GET", "/api/market-stats/", 200)
        if success:
            # Check for basic market stats
            if not response:
                print(f"   ⚠️  Empty market stats response")
                self.failed_tests.append("Market Stats: Empty response")
        return success

def main():
    print("🚀 Starting Stock Scanner API Tests...")
    print("=" * 60)
    
    tester = StockScannerAPITester()
    
    # Test authentication first
    print("\n📋 AUTHENTICATION TESTS")
    print("-" * 30)
    auth_success = tester.test_login()
    
    # Core API endpoint tests
    print("\n📋 CORE API TESTS")
    print("-" * 30)
    core_tests = [
        tester.test_health_check,
        tester.test_stocks_list,
        tester.test_total_tickers,
        tester.test_gainers_losers_stats,
        tester.test_total_alerts,
    ]
    
    for test_method in core_tests:
        try:
            test_method()
        except Exception as e:
            print(f"❌ Test {test_method.__name__} failed with exception: {str(e)}")
            tester.failed_tests.append(f"{test_method.__name__}: {str(e)}")
    
    # Portfolio tests (require authentication)
    print("\n📋 PORTFOLIO TESTS (Authenticated)")
    print("-" * 30)
    if auth_success:
        portfolio_tests = [
            tester.test_portfolio_value,
            tester.test_portfolio_pnl,
            tester.test_portfolio_holdings_count,
        ]
        
        for test_method in portfolio_tests:
            try:
                test_method()
            except Exception as e:
                print(f"❌ Test {test_method.__name__} failed with exception: {str(e)}")
                tester.failed_tests.append(f"{test_method.__name__}: {str(e)}")
    else:
        print("⚠️  Skipping portfolio tests - authentication failed")
        tester.failed_tests.append("Portfolio tests skipped - authentication failed")
    
    # Stock data tests
    print("\n📋 STOCK DATA TESTS")
    print("-" * 30)
    stock_tests = [
        tester.test_top_gainers,
        tester.test_top_losers,
        tester.test_most_active,
        tester.test_stock_search,
        tester.test_individual_stock,
        tester.test_market_stats,
    ]
    
    for test_method in stock_tests:
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