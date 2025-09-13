#!/usr/bin/env python
"""
Django Backend API Testing Script
Tests all the endpoints mentioned in the review request using Django test client
"""

import os
import sys
import json
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')

# Add the project directory to Python path
sys.path.insert(0, '/app')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User

class DjangoAPITester:
    def __init__(self):
        self.client = Client()
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, expected_content=None):
        """Run a single API test"""
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   {method} {endpoint}")
        
        try:
            if method == 'GET':
                response = self.client.get(endpoint)
            elif method == 'POST':
                if data:
                    response = self.client.post(endpoint, data=json.dumps(data), content_type='application/json')
                else:
                    response = self.client.post(endpoint, content_type='application/json')
            else:
                print(f"❌ Unsupported method: {method}")
                self.failed_tests.append(f"{name}: Unsupported method {method}")
                return False, {}

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                # Try to parse JSON response if possible
                try:
                    response_data = response.json() if hasattr(response, 'json') else {}
                    if response_data:
                        print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                except:
                    response_data = {}
                    if response.content:
                        print(f"   Content: {response.content.decode()[:200]}...")
                
                # Check expected content if provided
                if expected_content:
                    for key, expected_value in expected_content.items():
                        if key in response_data and response_data[key] != expected_value:
                            print(f"⚠️  Warning: Expected {key}={expected_value}, got {response_data[key]}")
                
                return True, response_data
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.content.decode()[:300]}")
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append(f"{name}: Exception - {str(e)}")
            return False, {}

    def test_homepage(self):
        """Test homepage endpoint"""
        return self.run_test("Homepage", "GET", "/", 200)

    def test_docs_endpoints(self):
        """Test documentation endpoints"""
        results = []
        results.append(self.run_test("Docs Page", "GET", "/docs/", 200))
        results.append(self.run_test("Schema Page", "GET", "/schema/", 404))  # Expected 404
        results.append(self.run_test("OpenAPI JSON", "GET", "/openapi.json", 200))
        results.append(self.run_test("Endpoint Status", "GET", "/endpoint-status/", 200))
        return results

    def test_usage_track(self):
        """Test usage tracking endpoint"""
        data = {
            "event": "test_event",
            "meta": {"test": True}
        }
        return self.run_test("Usage Track", "POST", "/api/usage/track/", 200, data)

    def test_revenue_discount(self):
        """Test revenue discount validation"""
        data = {
            "code": "WELCOME10",
            "amount": 100
        }
        expected_content = {
            "amount_after": 90.0
        }
        return self.run_test("Revenue Discount Validation", "POST", "/api/revenue/validate-discount/", 200, data, expected_content)

    def test_billing_endpoints(self):
        """Test billing endpoints"""
        results = []
        
        # Test PayPal status
        success, response_data = self.run_test("PayPal Status", "GET", "/api/billing/paypal-status/", 200)
        results.append((success, response_data))
        
        # Test create PayPal order
        data = {}
        success, response_data = self.run_test("Create PayPal Order", "POST", "/api/billing/create-paypal-order/", 200, data)
        results.append((success, response_data))
        
        # Test capture PayPal order
        data = {"orderID": "TEST-ORDER-123"}
        success, response_data = self.run_test("Capture PayPal Order", "POST", "/api/billing/capture-paypal-order/", 200, data)
        results.append((success, response_data))
        
        return results

    def test_api_endpoints(self):
        """Test main API endpoints"""
        results = []
        results.append(self.run_test("News Feed", "GET", "/api/news/feed/", 200))
        results.append(self.run_test("Portfolio List", "GET", "/api/portfolio/list/", 200))
        results.append(self.run_test("Watchlist List", "GET", "/api/watchlist/list/", 200))
        results.append(self.run_test("Stocks API", "GET", "/api/stocks/", 200))
        return results

    def test_auth_endpoint(self):
        """Test auth login endpoint"""
        data = {
            "username": "testuser",
            "password": "testpass"
        }
        # This should return 401 for invalid credentials, but not 500
        success, response_data = self.run_test("Auth Login", "POST", "/api/auth/login/", 401, data)
        return success, response_data

def main():
    print("🚀 Starting Django Backend API Tests")
    print("=" * 50)
    
    tester = DjangoAPITester()
    
    # Run all tests
    print("\n📋 Testing Core Endpoints...")
    tester.test_homepage()
    
    print("\n📚 Testing Documentation Endpoints...")
    tester.test_docs_endpoints()
    
    print("\n📊 Testing Usage Tracking...")
    tester.test_usage_track()
    
    print("\n💰 Testing Revenue Endpoints...")
    tester.test_revenue_discount()
    
    print("\n💳 Testing Billing Endpoints...")
    tester.test_billing_endpoints()
    
    print("\n🔐 Testing Auth Endpoints...")
    tester.test_auth_endpoint()
    
    print("\n📈 Testing API Endpoints...")
    tester.test_api_endpoints()
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    
    if tester.failed_tests:
        print(f"\n❌ Failed Tests:")
        for failed_test in tester.failed_tests:
            print(f"   • {failed_test}")
    else:
        print(f"\n✅ All tests passed!")
    
    success_rate = (tester.tests_passed / tester.tests_run) * 100 if tester.tests_run > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())