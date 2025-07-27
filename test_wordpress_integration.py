#!/usr/bin/env python3
"""
WordPress Integration Test Script
Tests all WordPress API endpoints for compatibility and data accuracy
"""

import requests
import json
import time
from datetime import datetime

class WordPressIntegrationTester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.results = []
    
    def test_wordpress_endpoint(self, endpoint, params=None, description=""):
        """Test a WordPress-specific endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        print(f"\n🌐 Testing WordPress: {endpoint}")
        if description:
            print(f"📝 Description: {description}")
        
        try:
            start_time = time.time()
            response = self.session.get(url, params=params, timeout=30)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Check WordPress-specific response structure
                    if data.get('success'):
                        # Validate WordPress-specific fields
                        wordpress_fields = self.validate_wordpress_fields(data, endpoint)
                        count = len(data.get('data', []))
                        
                        print(f"✅ SUCCESS - Time: {elapsed:.2f}s, Records: {count}")
                        print(f"📊 WordPress Fields: {wordpress_fields}")
                        
                        self.results.append({
                            "endpoint": endpoint,
                            "status": "PASS",
                            "time": elapsed,
                            "count": count,
                            "wordpress_fields": wordpress_fields
                        })
                        return True
                    else:
                        error = data.get('error', 'Unknown error')
                        print(f"❌ API ERROR - {error}")
                        self.results.append({
                            "endpoint": endpoint,
                            "status": "API_ERROR",
                            "error": error
                        })
                        return False
                        
                except json.JSONDecodeError:
                    print(f"⚠️  NON-JSON RESPONSE")
                    self.results.append({
                        "endpoint": endpoint,
                        "status": "NON_JSON"
                    })
                    return False
            else:
                print(f"❌ HTTP ERROR - Status: {response.status_code}")
                self.results.append({
                    "endpoint": endpoint,
                    "status": "HTTP_ERROR",
                    "status_code": response.status_code
                })
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ REQUEST ERROR - {e}")
            self.results.append({
                "endpoint": endpoint,
                "status": "REQUEST_ERROR",
                "error": str(e)
            })
            return False
    
    def validate_wordpress_fields(self, data, endpoint):
        """Validate WordPress-specific fields in the response"""
        wordpress_fields = []
        
        if '/wordpress/' in endpoint:
            # Check for WordPress-specific metadata
            meta = data.get('meta', {})
            if 'api_version' in meta:
                wordpress_fields.append('api_version')
            if 'data_source' in meta:
                wordpress_fields.append('data_source')
            
            # Check data structure
            data_items = data.get('data', [])
            if data_items:
                first_item = data_items[0]
                
                # WordPress-specific fields for stocks
                if 'stocks' in endpoint or endpoint == '/api/wordpress/':
                    wp_stock_fields = ['formatted_price', 'formatted_change', 'trend', 'permalink', 'slug']
                    for field in wp_stock_fields:
                        if field in first_item:
                            wordpress_fields.append(field)
                
                # WordPress-specific fields for news
                elif 'news' in endpoint:
                    wp_news_fields = ['sentiment', 'excerpt', 'source']
                    for field in wp_news_fields:
                        if field in first_item:
                            wordpress_fields.append(field)
                
                # WordPress-specific fields for alerts
                elif 'alerts' in endpoint:
                    wp_alert_fields = ['message', 'severity', 'is_triggered']
                    for field in wp_alert_fields:
                        if field in first_item:
                            wordpress_fields.append(field)
        
        return wordpress_fields
    
    def test_wordpress_compatibility(self):
        """Test WordPress-specific features and compatibility"""
        print("="*70)
        print("🌐 WORDPRESS INTEGRATION COMPREHENSIVE TESTING")
        print("="*70)
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Base URL: {self.base_url}")
        print("="*70)
        
        # Test WordPress stock endpoints
        print("\n📈 TESTING WORDPRESS STOCK ENDPOINTS")
        self.test_wordpress_endpoint("/api/wordpress/", description="Main WordPress stock endpoint")
        self.test_wordpress_endpoint("/api/wordpress/stocks/", description="Detailed WordPress stocks")
        self.test_wordpress_endpoint("/api/wordpress/", params={"limit": 5}, description="Limited stock results")
        self.test_wordpress_endpoint("/api/wordpress/", params={"category": "gainers"}, description="WordPress gainers")
        self.test_wordpress_endpoint("/api/wordpress/", params={"search": "Apple"}, description="WordPress stock search")
        self.test_wordpress_endpoint("/api/wordpress/stocks/", params={"featured": "true"}, description="Featured stocks")
        
        # Test WordPress news endpoints
        print("\n📰 TESTING WORDPRESS NEWS ENDPOINTS")
        self.test_wordpress_endpoint("/api/wordpress/news/", description="WordPress news endpoint")
        self.test_wordpress_endpoint("/api/wordpress/news/", params={"sentiment": "positive"}, description="Positive news filter")
        self.test_wordpress_endpoint("/api/wordpress/news/", params={"limit": 5}, description="Limited news results")
        
        # Test WordPress alerts endpoints
        print("\n🚨 TESTING WORDPRESS ALERTS ENDPOINTS")
        self.test_wordpress_endpoint("/api/wordpress/alerts/", description="WordPress alerts endpoint")
        self.test_wordpress_endpoint("/api/wordpress/alerts/", params={"active": "true"}, description="Active alerts only")
        
        # Test WordPress pagination
        print("\n📄 TESTING WORDPRESS PAGINATION")
        self.test_wordpress_endpoint("/api/wordpress/", params={"page": 1, "limit": 10}, description="First page")
        self.test_wordpress_endpoint("/api/wordpress/", params={"page": 2, "limit": 10}, description="Second page")
        
        # Test WordPress filtering
        print("\n🎛️ TESTING WORDPRESS FILTERING")
        self.test_wordpress_endpoint("/api/wordpress/", params={"sort": "price"}, description="Sort by price")
        self.test_wordpress_endpoint("/api/wordpress/", params={"sort": "volume"}, description="Sort by volume")
        self.test_wordpress_endpoint("/api/wordpress/", params={"sort": "change"}, description="Sort by change")
        
        # Test WordPress error handling
        print("\n⚠️ TESTING WORDPRESS ERROR HANDLING")
        self.test_wordpress_endpoint("/api/wordpress/nonexistent/", description="Invalid endpoint (should fail gracefully)")
        
        # Display results
        self.display_wordpress_results()
    
    def display_wordpress_results(self):
        """Display WordPress-specific test results"""
        print("\n" + "="*70)
        print("📊 WORDPRESS INTEGRATION TEST RESULTS")
        print("="*70)
        
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = len(self.results) - passed
        success_rate = (passed / len(self.results)) * 100 if self.results else 0
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Total Tests: {len(self.results)}")
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        # WordPress-specific metrics
        wordpress_endpoints = [r for r in self.results if '/wordpress/' in r['endpoint']]
        wp_passed = sum(1 for r in wordpress_endpoints if r['status'] == 'PASS')
        wp_success_rate = (wp_passed / len(wordpress_endpoints)) * 100 if wordpress_endpoints else 0
        
        print(f"\n🌐 WORDPRESS SPECIFIC METRICS:")
        print(f"   • WordPress Endpoints: {len(wordpress_endpoints)}")
        print(f"   • WordPress Success Rate: {wp_success_rate:.1f}%")
        
        # Show WordPress field validation
        wordpress_fields_found = set()
        for result in self.results:
            if result['status'] == 'PASS' and 'wordpress_fields' in result:
                wordpress_fields_found.update(result['wordpress_fields'])
        
        if wordpress_fields_found:
            print(f"   • WordPress Fields Detected: {', '.join(sorted(wordpress_fields_found))}")
        
        # Show failed tests
        if failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if result['status'] != 'PASS':
                    endpoint = result['endpoint']
                    status = result['status']
                    error = result.get('error', result.get('status_code', 'Unknown'))
                    print(f"   • {endpoint} - {status}: {error}")
        
        # Performance metrics
        pass_results = [r for r in self.results if r['status'] == 'PASS']
        if pass_results:
            avg_time = sum(r['time'] for r in pass_results) / len(pass_results)
            print(f"\n⚡ PERFORMANCE:")
            print(f"   • Average Response Time: {avg_time:.3f}s")
        
        print("\n" + "="*70)
        print(f"🕐 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if wp_success_rate >= 90:
            print("🎉 EXCELLENT - WordPress integration fully operational!")
        elif wp_success_rate >= 70:
            print("⚠️  GOOD - WordPress integration mostly working")
        else:
            print("❌ POOR - WordPress integration needs attention")
        
        print("="*70)

def main():
    """Main testing function"""
    import sys
    
    # Check if custom URL provided
    base_url = "http://127.0.0.1:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    # Initialize tester
    tester = WordPressIntegrationTester(base_url)
    
    # Run WordPress-specific tests
    try:
        tester.test_wordpress_compatibility()
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")

if __name__ == "__main__":
    main()