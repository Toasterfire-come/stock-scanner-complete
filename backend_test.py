import requests
import sys
from datetime import datetime

class SimpleAPITester:
    def __init__(self, base_url="https://mint-market-ui.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/api{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {response_data}")
                except:
                    print(f"   Response: {response.text[:200]}")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")

            return success, response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append(f"{name}: {str(e)}")
            return False, {}

def main():
    # Setup
    tester = SimpleAPITester()
    
    print("🚀 Starting Backend API Tests")
    print("=" * 50)

    # Test existing backend endpoints
    print("\n📋 Testing Existing Backend Endpoints:")
    tester.run_test("Root Endpoint", "GET", "/", 200)
    tester.run_test("Get Status Checks", "GET", "/status", 200)
    tester.run_test("Create Status Check", "POST", "/status", 200, 
                   data={"client_name": f"test_client_{datetime.now().strftime('%H%M%S')}"})

    # Test frontend expected endpoints (these will likely fail)
    print("\n📋 Testing Frontend Expected Endpoints:")
    tester.run_test("Health Check", "GET", "/health/", 200)
    tester.run_test("Trending Data", "GET", "/trending/", 200)
    tester.run_test("Alert Schema", "GET", "/alerts/create/", 200)
    tester.run_test("List Alerts", "GET", "/wordpress/alerts/", 200)
    
    # Test alert creation (will likely fail)
    tester.run_test("Create Alert", "POST", "/alerts/create/", 201, 
                   data={
                       "ticker": "AAPL",
                       "target_price": 200.0,
                       "condition": "above",
                       "email": "test@example.com"
                   })

    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Tests Summary: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.failed_tests:
        print("\n❌ Failed Tests:")
        for failure in tester.failed_tests:
            print(f"   • {failure}")
    
    print("\n🔍 Analysis:")
    if tester.tests_passed < 3:
        print("   • Major backend issues detected - most endpoints are failing")
        return 1
    elif tester.tests_passed < tester.tests_run * 0.7:
        print("   • Significant backend issues - frontend integration will likely fail")
        return 1
    else:
        print("   • Backend appears mostly functional")
        return 0

if __name__ == "__main__":
    sys.exit(main())