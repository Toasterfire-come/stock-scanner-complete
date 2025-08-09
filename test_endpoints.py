#!/usr/bin/env python3
"""
Comprehensive endpoint testing script for Stock Scanner API
Tests all major endpoints and reports status
"""

import requests
import json
import time
from urllib.parse import urljoin

class EndpointTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EndpointTester/1.0',
            'Accept': 'application/json'
        })
    
    def test_endpoint(self, path, method='GET', data=None, expected_status=200):
        """Test a single endpoint"""
        url = urljoin(self.base_url, path)
        
        try:
            start_time = time.time()
            
            if method == 'GET':
                response = self.session.get(url, timeout=10)
            elif method == 'POST':
                response = self.session.post(url, json=data, timeout=10)
            else:
                response = self.session.request(method, url, json=data, timeout=10)
            
            response_time = time.time() - start_time
            
            # Try to parse JSON
            try:
                json_data = response.json()
                has_json = True
            except:
                json_data = None
                has_json = False
            
            result = {
                'path': path,
                'method': method,
                'status_code': response.status_code,
                'expected_status': expected_status,
                'success': response.status_code == expected_status,
                'response_time': round(response_time, 3),
                'has_json': has_json,
                'content_length': len(response.content),
                'json_data': json_data
            }
            
            self.results.append(result)
            return result
            
        except Exception as e:
            result = {
                'path': path,
                'method': method,
                'status_code': 0,
                'expected_status': expected_status,
                'success': False,
                'response_time': 0,
                'has_json': False,
                'error': str(e),
                'content_length': 0,
                'json_data': None
            }
            
            self.results.append(result)
            return result
    
    def run_all_tests(self):
        """Run comprehensive endpoint tests"""
        print(f"Testing Stock Scanner API at {self.base_url}")
        print("=" * 60)
        
        # Core endpoints
        print("\nCore Endpoints:")
        self.test_endpoint("/", expected_status=200)
        self.test_endpoint("/health/", expected_status=200)
        self.test_endpoint("/api/health/", expected_status=200)
        self.test_endpoint("/docs/", expected_status=200)
        self.test_endpoint("/endpoint-status/?format=json", expected_status=200)
        
        # Stock data endpoints
        print("\nStock Data Endpoints:")
        self.test_endpoint("/api/stocks/", expected_status=200)
        self.test_endpoint("/api/stock/AAPL/", expected_status=200)
        self.test_endpoint("/api/trending/", expected_status=200)
        self.test_endpoint("/api/search/?q=apple", expected_status=200)
        self.test_endpoint("/api/market-stats/", expected_status=200)
        self.test_endpoint("/api/statistics/", expected_status=200)
        self.test_endpoint("/api/filter/", expected_status=200)
        
        # Revenue endpoints
        print("\nRevenue Endpoints:")
        self.test_endpoint("/revenue/revenue-analytics/?format=json", expected_status=200)
        
        # Portfolio endpoints (may require authentication)
        print("\nPortfolio Endpoints:")
        self.test_endpoint("/api/portfolio/list/", expected_status=200)
        
        # Watchlist endpoints
        print("\nWatchlist Endpoints:")
        self.test_endpoint("/api/watchlist/list/", expected_status=200)
        
        # News endpoints
        print("\nNews Endpoints:")
        self.test_endpoint("/api/news/feed/", expected_status=200)
        self.test_endpoint("/api/news/analytics/", expected_status=200)
        
        # Test some POST endpoints (should return method details)
        print("\nPOST Endpoints (Info Only):")
        self.test_endpoint("/api/alerts/create/", method='POST', expected_status=400)  # Should fail without data
        self.test_endpoint("/api/subscription/", method='POST', expected_status=400)  # Should fail without data
        
        # Test non-existent endpoint
        print("\nError Handling:")
        self.test_endpoint("/api/nonexistent/", expected_status=404)
        
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r['success']])
        failed_tests = total_tests - successful_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Show successful endpoints
        print(f"\nWORKING ENDPOINTS ({successful_tests}):")
        for result in self.results:
            if result['success']:
                json_indicator = "JSON" if result['has_json'] else "RAW"
                print(f"  {json_indicator} {result['method']} {result['path']} ({result['response_time']}s)")
        
        # Show failed endpoints
        if failed_tests > 0:
            print(f"\nFAILED ENDPOINTS ({failed_tests}):")
            for result in self.results:
                if not result['success']:
                    error_info = result.get('error', f"Status {result['status_code']}")
                    print(f"  - {result['method']} {result['path']} - {error_info}")
        
        # Show performance stats
        response_times = [r['response_time'] for r in self.results if r['success']]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            print(f"\nPERFORMANCE:")
            print(f"  Average Response Time: {avg_time:.3f}s")
            print(f"  Slowest Response: {max_time:.3f}s")
        
        print("\n" + "=" * 60)
        
        # JSON output for detailed analysis
        print("\nDetailed JSON Results:")
        print(json.dumps(self.results, indent=2))

if __name__ == "__main__":
    import sys
    
    # Allow custom base URL
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    tester = EndpointTester(base_url)
    tester.run_all_tests()