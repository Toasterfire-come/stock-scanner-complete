import requests
import sys
from datetime import datetime
import json

class SimpleAPITester:
    def __init__(self, base_url="https://api.retailtradescanner.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"URL: {url}")
        
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
                    print(f"Response: {json.dumps(response_data, indent=2)}")
                except:
                    print(f"Response: {response.text}")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text}")
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")

            return success, response.json() if success and response.text else {}

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            self.failed_tests.append(f"{name}: Network Error - {str(e)}")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append(f"{name}: Error - {str(e)}")
            return False, {}

    def test_actual_backend_endpoints(self):
        """Test actual backend endpoints based on server.py"""
        # Test basic API health check
        success, response = self.run_test(
            "API Root Endpoint",
            "GET",
            "api/",
            200
        )
        
        # Test status endpoints
        success, response = self.run_test(
            "Get Status Checks",
            "GET", 
            "api/status",
            200
        )
        
        # Test creating a status check
        success, response = self.run_test(
            "Create Status Check",
            "POST",
            "api/status",
            200,
            data={"client_name": "test_client"}
        )
        
        return success

    def test_configuration_verification(self):
        """Test that we're hitting the correct backend URL"""
        print(f"\n🔧 Configuration Check:")
        print(f"Testing backend URL: {self.base_url}")
        print(f"Expected URL: https://api.retailtradescanner.com")
        
        if self.base_url == "https://api.retailtradescanner.com":
            print("✅ Backend URL configuration is correct")
            return True
        else:
            print("❌ Backend URL configuration is incorrect")
            self.failed_tests.append("Backend URL configuration mismatch")
            return False

def main():
    print("🚀 Starting Backend API Tests for Trade Scan Pro")
    print("=" * 50)
    
    # Setup
    tester = SimpleAPITester()

    # Run tests
    print("\n📡 Testing Trade Scanner API Endpoints...")
    tester.test_trade_scanner_endpoints()
    
    print("\n🔐 Testing Authentication Endpoints...")
    tester.test_authentication_endpoints()

    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.failed_tests:
        print("\n❌ Failed Tests:")
        for failed_test in tester.failed_tests:
            print(f"  - {failed_test}")
    
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate < 50:
        print("❌ CRITICAL: More than 50% of API tests failed")
        return 1
    elif tester.tests_passed == tester.tests_run:
        print("🎉 All backend tests passed!")
        return 0
    else:
        print("⚠️  Some backend tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())