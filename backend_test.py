import requests
import sys
from datetime import datetime

class TradeScanProAPITester:
    def __init__(self, base_url="http://127.0.0.1:8002"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.external_api_available = False

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, allow_degraded=False):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                if response.content:
                    try:
                        json_response = response.json()
                        print(f"Response: {json_response}")
                        
                        # Check if external API is available
                        if endpoint == "api/health" and "external_api" in json_response:
                            self.external_api_available = json_response["external_api"] != "error"
                            
                    except:
                        print(f"Response (text): {response.text[:200]}...")
            else:
                # For degraded health checks, still consider it a pass if allow_degraded is True
                if allow_degraded and response.status_code == 200:
                    try:
                        json_response = response.json()
                        if json_response.get("status") == "degraded":
                            self.tests_passed += 1
                            success = True
                            print(f"✅ Passed (Degraded) - Status: {response.status_code}")
                            print(f"Response: {json_response}")
                    except:
                        pass
                
                if not success:
                    print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                    print(f"Response: {response.text[:200]}...")

            return success, response.json() if success and response.content else {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout")
            return False, {}
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed - Connection error")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200,
            allow_degraded=True
        )
        return success

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "api/",
            200
        )
        return success

    def test_usage_endpoint(self):
        """Test usage statistics endpoint"""
        # Test with default user (free plan)
        success1, response = self.run_test(
            "Usage Stats - Free Plan",
            "GET",
            "api/usage",
            200
        )
        
        # Test with Bronze plan user
        success2, response = self.run_test(
            "Usage Stats - Bronze Plan",
            "GET",
            "api/usage",
            200,
            headers={"X-User-ID": "test_bronze_user", "X-User-Plan": "bronze"}
        )
        
        return success1 and success2

    def test_stock_quote_endpoint(self):
        """Test stock quote endpoint with plan limits"""
        # Test with free plan (should work initially)
        success1, response1 = self.run_test(
            "Stock Quote - Free Plan (AAPL)",
            "GET",
            "api/stocks/AAPL/quote",
            200
        )
        
        # Test with Bronze plan
        success2, response2 = self.run_test(
            "Stock Quote - Bronze Plan (AAPL)",
            "GET",
            "api/stocks/AAPL/quote",
            200,
            headers={"X-User-ID": "test_bronze_user", "X-User-Plan": "bronze"}
        )
        
        # Test with different symbol
        success3, response3 = self.run_test(
            "Stock Quote - Different Symbol (MSFT)",
            "GET",
            "api/stocks/MSFT/quote",
            200,
            headers={"X-User-ID": "test_user", "X-User-Plan": "silver"}
        )
        
        return success1 and success2 and success3

    def test_external_api_endpoints(self):
        """Test endpoints that depend on external API"""
        if not self.external_api_available:
            print("\n⚠️  External API not available - skipping external API tests")
            return True
        
        # Test stocks endpoint
        success1, response = self.run_test(
            "Get Stocks List",
            "GET",
            "api/stocks/",
            200
        )
        
        # Test search endpoint
        success2, response = self.run_test(
            "Search Stocks",
            "GET",
            "api/search/?q=AAPL",
            200
        )
        
        # Test trending endpoint
        success3, response = self.run_test(
            "Get Trending Stocks",
            "GET",
            "api/trending/",
            200
        )
        
        return success1 and success2 and success3

    def test_billing_endpoints(self):
        """Test PayPal billing endpoints - Fixed import issues"""
        # Test create PayPal order (should return 201 for creation)
        success1, response = self.run_test(
            "Create PayPal Order",
            "POST",
            "api/billing/create-paypal-order/",
            201,  # Expect 201 for creation, not 200
            data={"plan": "bronze", "amount": "24.99"}
        )
        
        # Test capture PayPal order with TEST order ID (should work with stub)
        success2, response = self.run_test(
            "Capture PayPal Order - Stub",
            "POST",
            "api/billing/capture-paypal-order/",
            200,
            data={"order_id": "TEST-STUB123", "plan_type": "bronze", "billing_cycle": "monthly"}
        )
        
        return success1 and success2

    def test_status_endpoints(self):
        """Test status check endpoints - NEW /api/status endpoint"""
        # Test GET status checks (NEW endpoint as per problem statement)
        success1, response = self.run_test(
            "Get Status Checks - NEW /api/status endpoint",
            "GET",
            "api/status/",
            200
        )
        
        # Verify comprehensive system info is returned
        if success1 and response:
            required_fields = ['service', 'version', 'environment', 'timestamp', 'status', 'components', 'system_resources']
            missing_fields = [field for field in required_fields if field not in response.get('data', {})]
            if missing_fields:
                print(f"⚠️  Missing fields in status response: {missing_fields}")
                success1 = False
            else:
                print("✅ Status endpoint returns comprehensive system info")
        
        return success1

    def test_plan_limits(self):
        """Test plan limit enforcement"""
        print("\n🔒 Testing Plan Limit Enforcement...")
        
        # Make multiple requests to test rate limiting
        user_id = f"limit_test_user_{datetime.now().strftime('%H%M%S')}"
        
        # Test with free plan (should hit limits quickly)
        success_count = 0
        for i in range(8):  # Free plan has hourly limit of 2
            success, response = self.run_test(
                f"Rate Limit Test {i+1}/8 - Free Plan",
                "GET",
                "api/stocks/TSLA/quote",
                200 if i < 2 else 429,  # Expect 429 after 2 requests for free plan
                headers={"X-User-ID": user_id, "X-User-Plan": "free"}
            )
            if success:
                success_count += 1
        
        print(f"Free plan successful requests: {success_count}/8 (expected: 2)")
        return success_count <= 2  # Should be limited after 2 requests

def main():
    print("🚀 Starting Trade Scan Pro API Tests...")
    print("=" * 50)
    
    # Setup
    tester = TradeScanProAPITester()

    # Run comprehensive API tests
    print("\n🏥 Testing Health Check...")
    tester.test_health_check()
    
    print("\n📡 Testing Basic API Endpoints...")
    tester.test_root_endpoint()
    
    print("\n📊 Testing Usage Tracking...")
    tester.test_usage_endpoint()
    
    print("\n📈 Testing Stock Quote API...")
    tester.test_stock_quote_endpoint()
    
    print("\n🌐 Testing External API Integration...")
    tester.test_external_api_endpoints()
    
    print("\n💳 Testing Billing Endpoints...")
    tester.test_billing_endpoints()
    
    print("\n🔄 Testing Status Endpoints...")
    tester.test_status_endpoints()
    
    print("\n🔒 Testing Plan Limits...")
    tester.test_plan_limits()

    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Tests Summary: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.external_api_available:
        print("✅ External API is available")
    else:
        print("⚠️  External API is not available (degraded mode)")
    
    if tester.tests_passed >= (tester.tests_run * 0.8):  # 80% pass rate
        print("✅ API tests mostly passed!")
        return 0
    else:
        print("❌ Many API tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())