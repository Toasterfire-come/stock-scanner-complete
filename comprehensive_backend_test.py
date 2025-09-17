#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Trade Scan Pro Stock Scanner
Focus: Data Integrity, API Consistency, and Real Database Data Verification
"""

import requests
import sys
import json
from datetime import datetime
import time

class TradeScanProBackendTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.critical_issues = []
        self.data_integrity_issues = []
        self.session = requests.Session()
        
        # Expected test data from populate_test_data.py
        self.expected_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'JPM', 'V', 'WMT']
        self.expected_stock_count = 10

    def log_critical_issue(self, issue):
        """Log critical issues that affect user experience"""
        self.critical_issues.append(issue)
        print(f"🚨 CRITICAL: {issue}")

    def log_data_integrity_issue(self, issue):
        """Log data integrity issues (hardcoded/sample data)"""
        self.data_integrity_issues.append(issue)
        print(f"⚠️  DATA INTEGRITY: {issue}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, timeout=15):
        """Run a single API test with detailed logging"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            start_time = time.time()
            
            if method == 'GET':
                response = self.session.get(url, headers=default_headers, timeout=timeout)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=default_headers, timeout=timeout)
            
            response_time = time.time() - start_time
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code} ({response_time:.2f}s)")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:500]}...")
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")
                return False, {}

        except requests.exceptions.Timeout:
            error_msg = f"Timeout after {timeout}s"
            print(f"❌ Failed - {error_msg}")
            self.failed_tests.append(f"{name}: {error_msg}")
            self.log_critical_issue(f"{name} - API timeout indicates performance issues")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append(f"{name}: {str(e)}")
            return False, {}

    def check_for_hardcoded_data(self, data, endpoint_name):
        """Check if response contains hardcoded/sample data indicators"""
        data_str = json.dumps(data).lower()
        
        # Common indicators of hardcoded/sample data
        sample_indicators = [
            'sample', 'test', 'mock', 'dummy', 'fake', 'placeholder',
            'example.com', 'lorem ipsum', 'hardcoded', 'static'
        ]
        
        found_indicators = []
        for indicator in sample_indicators:
            if indicator in data_str:
                found_indicators.append(indicator)
        
        if found_indicators:
            self.log_data_integrity_issue(
                f"{endpoint_name} contains sample data indicators: {', '.join(found_indicators)}"
            )
            return True
        return False

    def verify_real_stock_data(self, stock_data, endpoint_name):
        """Verify that stock data appears to be real, not hardcoded"""
        if not stock_data:
            self.log_data_integrity_issue(f"{endpoint_name} returned empty stock data")
            return False
        
        # Check for realistic price variations
        prices = []
        for stock in stock_data:
            price = stock.get('current_price', 0)
            if isinstance(price, (int, float)) and price > 0:
                prices.append(price)
        
        if len(prices) < 2:
            self.log_data_integrity_issue(f"{endpoint_name} has insufficient price data for verification")
            return False
        
        # Real stock data should have price variation
        price_range = max(prices) - min(prices)
        if price_range == 0:
            self.log_data_integrity_issue(f"{endpoint_name} has identical prices - likely hardcoded")
            return False
        
        # Check for expected stock symbols
        symbols = [stock.get('ticker', '').upper() for stock in stock_data]
        expected_found = sum(1 for symbol in self.expected_stocks if symbol in symbols)
        
        if expected_found == 0:
            self.log_data_integrity_issue(f"{endpoint_name} contains no expected test stocks")
            return False
        
        print(f"   ✅ Real data verified: {expected_found}/{len(self.expected_stocks)} expected stocks found")
        return True

    # CRITICAL PRIORITY TESTS - DATA INTEGRITY

    def test_simple_stocks_api(self):
        """Test /api/simple/stocks/ for hardcoded data"""
        success, response = self.run_test("Simple Stocks API", "GET", "/api/simple/stocks/", 200)
        if success:
            self.check_for_hardcoded_data(response, "Simple Stocks API")
            
            # Check if it's returning real database data
            if response.get('success') and response.get('data'):
                self.verify_real_stock_data(response['data'], "Simple Stocks API")
            elif response.get('success') == False:
                if 'database is empty' in response.get('message', '').lower():
                    self.log_critical_issue("Simple Stocks API - Database is empty, no real data available")
                else:
                    self.log_data_integrity_issue(f"Simple Stocks API error: {response.get('message', 'Unknown error')}")
        return success

    def test_stocks_list_api(self):
        """Test /api/stocks/ for real database data"""
        success, response = self.run_test("Stocks List API", "GET", "/api/stocks/", 200)
        if success:
            self.check_for_hardcoded_data(response, "Stocks List API")
            
            stock_data = response.get('data', [])
            total_count = response.get('count', 0) or response.get('total_count', 0)
            
            print(f"   📊 Total stocks: {total_count}, Returned: {len(stock_data)}")
            
            if total_count == 0:
                self.log_critical_issue("Stocks List API - No stocks in database")
            elif total_count != self.expected_stock_count:
                self.log_data_integrity_issue(f"Expected {self.expected_stock_count} stocks, found {total_count}")
            
            if stock_data:
                self.verify_real_stock_data(stock_data, "Stocks List API")
        return success

    def test_market_stats_api(self):
        """Test /api/market-stats/ for real data"""
        success, response = self.run_test("Market Stats API", "GET", "/api/market-stats/", 200)
        if success:
            self.check_for_hardcoded_data(response, "Market Stats API")
            
            # Check for realistic market data
            market_overview = response.get('market_overview', {})
            total_stocks = market_overview.get('total_stocks', 0)
            gainers = market_overview.get('gainers', 0)
            losers = market_overview.get('losers', 0)
            
            print(f"   📊 Market Overview - Total: {total_stocks}, Gainers: {gainers}, Losers: {losers}")
            
            if total_stocks == 0:
                self.log_critical_issue("Market Stats API - No market data available")
            elif total_stocks != self.expected_stock_count:
                self.log_data_integrity_issue(f"Market stats shows {total_stocks} stocks, expected {self.expected_stock_count}")
        return success

    def test_trending_stocks_api(self):
        """Test /api/trending/ for real data"""
        success, response = self.run_test("Trending Stocks API", "GET", "/api/trending/", 200)
        if success:
            self.check_for_hardcoded_data(response, "Trending Stocks API")
            
            # Check trending categories
            categories = ['high_volume', 'top_gainers', 'most_active']
            for category in categories:
                category_data = response.get(category, [])
                print(f"   📊 {category.title()}: {len(category_data)} stocks")
                
                if len(category_data) == 0:
                    self.log_data_integrity_issue(f"Trending API - No {category} data available")
                else:
                    self.verify_real_stock_data(category_data, f"Trending API ({category})")
        return success

    # API CONSISTENCY TESTS

    def test_individual_stock_details(self):
        """Test individual stock detail endpoints"""
        test_symbols = ['AAPL', 'MSFT', 'GOOGL']  # Test a few key stocks
        
        for symbol in test_symbols:
            success, response = self.run_test(
                f"Stock Detail ({symbol})", 
                "GET", 
                f"/api/stocks/{symbol}/", 
                200
            )
            
            if success:
                stock_data = response.get('data', response)
                ticker = stock_data.get('ticker')
                price = stock_data.get('current_price')
                
                if ticker != symbol:
                    self.log_data_integrity_issue(f"Stock detail for {symbol} returned ticker {ticker}")
                
                if not price or price <= 0:
                    self.log_data_integrity_issue(f"Stock {symbol} has invalid price: {price}")
                else:
                    print(f"   ✅ {symbol}: ${price}")
            else:
                self.log_critical_issue(f"Stock detail API failed for {symbol}")

    def test_search_functionality(self):
        """Test stock search functionality"""
        search_terms = ['AAPL', 'Apple', 'MSFT']
        
        for term in search_terms:
            success, response = self.run_test(
                f"Stock Search ({term})", 
                "GET", 
                f"/api/search/?q={term}", 
                200
            )
            
            if success:
                results = response.get('results', []) or response.get('data', [])
                print(f"   📊 Search '{term}': {len(results)} results")
                
                if len(results) == 0:
                    self.log_critical_issue(f"Search for '{term}' returned no results")
                else:
                    # Verify search relevance
                    relevant_found = False
                    for result in results:
                        ticker = result.get('ticker', '').upper()
                        company = result.get('company_name', '').upper()
                        if term.upper() in ticker or term.upper() in company:
                            relevant_found = True
                            break
                    
                    if not relevant_found:
                        self.log_data_integrity_issue(f"Search for '{term}' returned irrelevant results")

    def test_error_handling(self):
        """Test API error handling"""
        error_tests = [
            ("Invalid Stock Symbol", "GET", "/api/stocks/INVALID123/", 404),
            ("Invalid Search", "GET", "/api/search/?q=", 400),
        ]
        
        for name, method, endpoint, expected_status in error_tests:
            success, response = self.run_test(name, method, endpoint, expected_status)
            if success:
                # Check if error response is helpful
                error_msg = response.get('error', '') or response.get('message', '')
                if not error_msg:
                    self.log_critical_issue(f"{name} - No helpful error message provided")
                else:
                    print(f"   ✅ Error message: {error_msg}")

    # PERFORMANCE AND RELIABILITY TESTS

    def test_api_response_times(self):
        """Test API response times for user experience"""
        performance_tests = [
            ("Stocks List Performance", "GET", "/api/stocks/?limit=50"),
            ("Market Stats Performance", "GET", "/api/market-stats/"),
            ("Trending Performance", "GET", "/api/trending/"),
        ]
        
        slow_endpoints = []
        
        for name, method, endpoint in performance_tests:
            start_time = time.time()
            success, response = self.run_test(name, method, endpoint, 200, timeout=10)
            response_time = time.time() - start_time
            
            if response_time > 5.0:  # 5 second threshold
                slow_endpoints.append(f"{name}: {response_time:.2f}s")
                self.log_critical_issue(f"{name} is too slow ({response_time:.2f}s)")
            elif response_time > 2.0:  # 2 second warning
                print(f"   ⚠️  {name} is slow ({response_time:.2f}s)")
        
        if slow_endpoints:
            self.log_critical_issue(f"Slow API endpoints detected: {', '.join(slow_endpoints)}")

    def test_data_consistency(self):
        """Test data consistency across different endpoints"""
        # Get total count from different endpoints
        endpoints_data = {}
        
        # Test total tickers endpoint
        success, response = self.run_test("Total Tickers", "GET", "/api/stats/total-tickers/", 200)
        if success:
            endpoints_data['total_tickers'] = response.get('total_tickers', 0)
        
        # Test stocks list count
        success, response = self.run_test("Stocks Count Check", "GET", "/api/stocks/?limit=1", 200)
        if success:
            endpoints_data['stocks_list_count'] = response.get('count', 0) or response.get('total_count', 0)
        
        # Test market stats count
        success, response = self.run_test("Market Stats Count", "GET", "/api/market-stats/", 200)
        if success:
            market_overview = response.get('market_overview', {})
            endpoints_data['market_stats_count'] = market_overview.get('total_stocks', 0)
        
        # Check consistency
        counts = list(endpoints_data.values())
        if len(set(counts)) > 1:  # More than one unique count
            self.log_data_integrity_issue(f"Inconsistent stock counts across endpoints: {endpoints_data}")
        else:
            print(f"   ✅ Consistent stock count across endpoints: {counts[0] if counts else 'N/A'}")

    def run_comprehensive_test_suite(self):
        """Run all tests in priority order"""
        print("🚀 Starting Trade Scan Pro Backend Comprehensive Testing...")
        print("=" * 80)
        print("Focus: Data Integrity, API Consistency, User Experience")
        print("=" * 80)
        
        # HIGHEST PRIORITY: Data Integrity Tests
        print("\n📋 CRITICAL PRIORITY: DATA INTEGRITY TESTS")
        print("-" * 50)
        data_integrity_tests = [
            self.test_simple_stocks_api,
            self.test_stocks_list_api,
            self.test_market_stats_api,
            self.test_trending_stocks_api,
        ]
        
        for test_method in data_integrity_tests:
            try:
                test_method()
            except Exception as e:
                print(f"❌ Test {test_method.__name__} failed with exception: {str(e)}")
                self.failed_tests.append(f"{test_method.__name__}: {str(e)}")
        
        # HIGH PRIORITY: API Consistency Tests
        print("\n📋 HIGH PRIORITY: API CONSISTENCY TESTS")
        print("-" * 50)
        consistency_tests = [
            self.test_individual_stock_details,
            self.test_search_functionality,
            self.test_error_handling,
            self.test_data_consistency,
        ]
        
        for test_method in consistency_tests:
            try:
                test_method()
            except Exception as e:
                print(f"❌ Test {test_method.__name__} failed with exception: {str(e)}")
                self.failed_tests.append(f"{test_method.__name__}: {str(e)}")
        
        # MEDIUM PRIORITY: Performance Tests
        print("\n📋 MEDIUM PRIORITY: PERFORMANCE TESTS")
        print("-" * 50)
        try:
            self.test_api_response_times()
        except Exception as e:
            print(f"❌ Performance test failed with exception: {str(e)}")
            self.failed_tests.append(f"Performance test: {str(e)}")

    def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {len(self.failed_tests)}")
        
        # Critical Issues Report
        if self.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES ({len(self.critical_issues)}):")
            print("These issues severely impact user experience and must be fixed immediately:")
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"   {i}. {issue}")
        
        # Data Integrity Issues Report
        if self.data_integrity_issues:
            print(f"\n⚠️  DATA INTEGRITY ISSUES ({len(self.data_integrity_issues)}):")
            print("These issues indicate hardcoded/sample data being served to users:")
            for i, issue in enumerate(self.data_integrity_issues, 1):
                print(f"   {i}. {issue}")
        
        # General Failed Tests
        other_failures = [f for f in self.failed_tests if not any(
            critical in f for critical in [issue.split(' - ')[0] if ' - ' in issue else issue 
                                         for issue in self.critical_issues + self.data_integrity_issues]
        )]
        
        if other_failures:
            print(f"\n❌ OTHER FAILED TESTS ({len(other_failures)}):")
            for failure in other_failures:
                print(f"   - {failure}")
        
        # Success Summary
        if not self.critical_issues and not self.data_integrity_issues and not other_failures:
            print(f"\n✅ ALL TESTS PASSED!")
            print("The backend API is serving real database data and functioning correctly.")
        
        # Recommendations
        print(f"\n📋 RECOMMENDATIONS:")
        if self.critical_issues:
            print("1. Fix critical issues immediately - these prevent basic functionality")
        if self.data_integrity_issues:
            print("2. Ensure all APIs serve real database data, not hardcoded samples")
        if len(self.failed_tests) > len(self.critical_issues) + len(self.data_integrity_issues):
            print("3. Address remaining API consistency and error handling issues")
        if not any([self.critical_issues, self.data_integrity_issues, other_failures]):
            print("1. Backend is ready for production use")
            print("2. Consider adding more comprehensive error handling")
            print("3. Monitor API performance under load")
        
        return len(self.critical_issues) + len(self.data_integrity_issues) + len(other_failures)

def main():
    tester = TradeScanProBackendTester()
    tester.run_comprehensive_test_suite()
    total_issues = tester.generate_final_report()
    
    return 0 if total_issues == 0 else 1

if __name__ == "__main__":
    sys.exit(main())