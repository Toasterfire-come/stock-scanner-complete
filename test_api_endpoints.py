#!/usr/bin/env python3
"""
Stock Scanner API Endpoint Testing Script
Tests all the new comprehensive API endpoints
"""

import requests
import json
import time
from datetime import datetime

class APITester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.results = []
    
    def test_endpoint(self, endpoint, method="GET", params=None, data=None, description=""):
        """Test a single API endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        print(f"\n[TEST] Testing: {method} {endpoint}")
        if description:
            print(f" Description: {description}")
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(url, params=params, timeout=30)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=30)
            else:
                response = self.session.request(method, url, params=params, json=data, timeout=30)
            
            elapsed = time.time() - start_time
            
            # Check response
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    success = json_data.get('success', True)
                    count = json_data.get('count', len(json_data.get('data', [])))
                    
                    if success:
                        print(f"[SUCCESS] SUCCESS - Status: {response.status_code}, Time: {elapsed:.2f}s, Count: {count}")
                        self.results.append({"endpoint": endpoint, "status": "PASS", "time": elapsed, "count": count})
                        return True
                    else:
                        error = json_data.get('error', 'Unknown error')
                        print(f"[ERROR] API ERROR - {error}")
                        self.results.append({"endpoint": endpoint, "status": "API_ERROR", "error": error})
                        return False
                        
                except json.JSONDecodeError:
                    print(f"[WARNING]  NON-JSON RESPONSE - Status: {response.status_code}, Length: {len(response.text)}")
                    self.results.append({"endpoint": endpoint, "status": "NON_JSON", "status_code": response.status_code})
                    return False
            else:
                print(f"[ERROR] HTTP ERROR - Status: {response.status_code}")
                self.results.append({"endpoint": endpoint, "status": "HTTP_ERROR", "status_code": response.status_code})
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] REQUEST ERROR - {e}")
            self.results.append({"endpoint": endpoint, "status": "REQUEST_ERROR", "error": str(e)})
            return False
    
    def run_comprehensive_tests(self):
        """Run comprehensive API endpoint tests"""
        print("="*70)
        print("[RUN] STOCK SCANNER API COMPREHENSIVE TESTING")
        print("="*70)
        print(f" Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[WEB] Base URL: {self.base_url}")
        print("="*70)
        
        # Test core stock endpoints
        print("\n[UP] TESTING CORE STOCK ENDPOINTS")
        self.test_endpoint("/api/stocks/", description="Get all stocks with default parameters")
        self.test_endpoint("/api/stocks/", params={"limit": 10}, description="Get 10 stocks")
        self.test_endpoint("/api/stocks/", params={"category": "gainers", "limit": 5}, description="Get top 5 gainers")
        self.test_endpoint("/api/stocks/", params={"min_price": 100, "max_price": 500}, description="Filter by price range")
        self.test_endpoint("/api/stocks/", params={"search": "Apple"}, description="Search for Apple")
        self.test_endpoint("/api/stocks/", params={"sort_by": "volume", "sort_order": "desc"}, description="Sort by volume")
        
        # Test individual stock endpoints
        print("\n[STATS] TESTING INDIVIDUAL STOCK ENDPOINTS")
        self.test_endpoint("/api/stocks/AAPL/", description="Get Apple Inc. detailed data")
        self.test_endpoint("/api/stocks/MSFT/", description="Get Microsoft detailed data")
        self.test_endpoint("/api/stocks/GOOGL/", description="Get Google detailed data")
        self.test_endpoint("/api/stocks/INVALID/", description="Test invalid ticker (should fail gracefully)")
        
        # Test NASDAQ endpoint
        print("\n[TARGET] TESTING NASDAQ ENDPOINTS")
        self.test_endpoint("/api/stocks/nasdaq/", description="Get all NASDAQ stocks")
        self.test_endpoint("/api/stocks/nasdaq/", params={"limit": 20}, description="Get 20 NASDAQ stocks")
        
        # Test search endpoint
        print("\n[SEARCH] TESTING SEARCH ENDPOINTS")
        self.test_endpoint("/api/stocks/search/", params={"q": "Apple"}, description="Search for Apple")
        self.test_endpoint("/api/stocks/search/", params={"q": "AAPL"}, description="Search for AAPL ticker")
        self.test_endpoint("/api/stocks/search/", params={"q": "Microsoft"}, description="Search for Microsoft")
        self.test_endpoint("/api/stocks/search/", description="Search without query (should fail)")
        
        # Test market endpoints
        print("\n[UP] TESTING MARKET ENDPOINTS")
        self.test_endpoint("/api/market/stats/", description="Get market statistics")
        self.test_endpoint("/api/market/filter/", params={"min_market_cap": 1000000000}, description="Filter by market cap")
        
        # Test real-time endpoints
        print("\n TESTING REAL-TIME ENDPOINTS")
        self.test_endpoint("/api/realtime/AAPL/", description="Get real-time Apple data")
        self.test_endpoint("/api/trending/", description="Get trending stocks")
        
        # Test admin endpoints
        print("\n[CONFIG] TESTING ADMIN ENDPOINTS")
        self.test_endpoint("/api/admin/status/", description="Get system status")
        self.test_endpoint("/admin-dashboard/", description="Admin dashboard (HTML)")
        
        # Test WordPress integration
        print("\n[WEB] TESTING WORDPRESS INTEGRATION")
        self.test_endpoint("/api/wordpress/", description="WordPress stock data")
        self.test_endpoint("/api/wordpress/stocks/", description="WordPress detailed stocks")
        self.test_endpoint("/api/wordpress/news/", description="WordPress news data")
        
        # Test advanced filtering
        print("\n[CONTROL] TESTING ADVANCED FILTERING")
        self.test_endpoint("/api/stocks/", params={
            "category": "large_cap",
            "min_pe": 10,
            "max_pe": 30,
            "min_volume": 1000000,
            "sort_by": "market_cap",
            "limit": 15
        }, description="Complex filtering: Large cap stocks with PE 10-30")
        
        self.test_endpoint("/api/stocks/", params={
            "category": "high_volume",
            "min_price": 50,
            "exchange": "NASDAQ",
            "sort_by": "volume",
            "sort_order": "desc"
        }, description="High volume NASDAQ stocks over $50")
        
        # Display results
        self.display_results()
    
    def display_results(self):
        """Display comprehensive test results"""
        print("\n" + "="*70)
        print("[STATS] TEST RESULTS SUMMARY")
        print("="*70)
        
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = len(self.results) - passed
        success_rate = (passed / len(self.results)) * 100 if self.results else 0
        
        print(f"[SUCCESS] Passed: {passed}")
        print(f"[ERROR] Failed: {failed}")
        print(f"[UP] Total: {len(self.results)}")
        print(f"[TARGET] Success Rate: {success_rate:.1f}%")
        
        # Show failed tests
        if failed > 0:
            print(f"\n[ERROR] FAILED TESTS:")
            for result in self.results:
                if result['status'] != 'PASS':
                    status = result['status']
                    endpoint = result['endpoint']
                    error = result.get('error', result.get('status_code', 'Unknown'))
                    print(f"   - {endpoint} - {status}: {error}")
        
        # Show performance metrics
        pass_results = [r for r in self.results if r['status'] == 'PASS']
        if pass_results:
            avg_time = sum(r['time'] for r in pass_results) / len(pass_results)
            max_time = max(r['time'] for r in pass_results)
            min_time = min(r['time'] for r in pass_results)
            
            print(f"\n PERFORMANCE METRICS:")
            print(f"   - Average Response Time: {avg_time:.3f}s")
            print(f"   - Fastest Response: {min_time:.3f}s")
            print(f"   - Slowest Response: {max_time:.3f}s")
        
        # Show data counts
        data_results = [r for r in self.results if r['status'] == 'PASS' and 'count' in r]
        if data_results:
            total_data = sum(r['count'] for r in data_results)
            avg_data = total_data / len(data_results)
            
            print(f"\n[STATS] DATA METRICS:")
            print(f"   - Total Records Retrieved: {total_data:,}")
            print(f"   - Average Records per Endpoint: {avg_data:.1f}")
        
        print("\n" + "="*70)
        print(f" Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if success_rate >= 90:
            print("[SUCCESS] EXCELLENT - All systems operational!")
        elif success_rate >= 70:
            print("[WARNING]  GOOD - Some issues detected")
        else:
            print("[ERROR] POOR - Significant issues detected")
        
        print("="*70)

def main():
    """Main testing function"""
    import sys
    
    # Check if custom URL provided
    base_url = "http://127.0.0.1:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    # Initialize tester
    tester = APITester(base_url)
    
    # Run tests
    try:
        tester.run_comprehensive_tests()
    except KeyboardInterrupt:
        print("\n[STOP]  Testing interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Testing failed with error: {e}")

if __name__ == "__main__":
    main()