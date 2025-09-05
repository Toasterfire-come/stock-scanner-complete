#!/usr/bin/env python3
"""
Comprehensive endpoint testing script for Stock Scanner API
Tests all endpoints and reports their status
"""

import requests
import json
import sys
import os

# Base URL
BASE_URL = "http://localhost:8001"

# Test token (from registration)
TEST_TOKEN = "42ec1336-f258-4469-ae97-79a5e05dd115"

def test_endpoint(method, endpoint, data=None, token=None, description=""):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return {"status": "ERROR", "message": f"Unsupported method: {method}"}
        
        status_code = response.status_code
        
        # Try to parse JSON response
        try:
            response_data = response.json()
        except:
            response_data = response.text[:200] + "..." if len(response.text) > 200 else response.text
        
        return {
            "status": "WORKING" if 200 <= status_code < 400 else "BROKEN",
            "status_code": status_code,
            "response": response_data,
            "description": description
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "ERROR",
            "message": str(e),
            "description": description
        }

def main():
    print("🧪 COMPREHENSIVE ENDPOINT TESTING")
    print("=" * 50)
    
    # Test endpoints
    endpoints_to_test = [
        # Basic endpoints
        ("GET", "/", None, None, "Homepage"),
        ("GET", "/health/", None, None, "Health Check"),
        ("GET", "/api/", None, None, "API Index"),
        
        # Authentication endpoints (no token needed)
        ("POST", "/api/auth/register/", {
            "username": "testuser999",
            "email": "test999@example.com", 
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }, None, "User Registration"),
        
        ("POST", "/api/auth/login/", {
            "username": "testuser456",
            "password": "testpass123"
        }, None, "User Login"),
        
        # User management (requires token)
        ("GET", "/api/user/profile/", None, TEST_TOKEN, "Get User Profile"),
        ("POST", "/api/user/change-password/", {
            "current_password": "testpass123",
            "new_password": "newpass123"
        }, TEST_TOKEN, "Change Password"),
        
        # Platform stats (no auth required)
        ("GET", "/api/platform-stats/", None, None, "Platform Statistics"),
        ("GET", "/api/usage/", None, None, "Usage Statistics"),
        
        # Stock data endpoints
        ("GET", "/api/stocks/", None, None, "List All Stocks"),
        ("GET", "/api/stocks/AAPL/", None, None, "Get AAPL Stock Details"),
        ("GET", "/api/stocks/AAPL/quote/", None, None, "Get AAPL Quote"),
        ("GET", "/api/realtime/AAPL/", None, None, "Get AAPL Real-time Data"),
        ("GET", "/api/stocks/nasdaq/", None, None, "NASDAQ Stocks"),
        ("GET", "/api/stocks/search/", None, None, "Stock Search"),
        
        # Market data
        ("GET", "/api/market/stats/", None, None, "Market Statistics"),
        ("GET", "/api/market/filter/", None, None, "Filter Stocks"),
        ("GET", "/api/trending/", None, None, "Trending Stocks"),
        
        # Billing endpoints (requires token)
        ("POST", "/api/billing/create-paypal-order/", {
            "plan_type": "bronze",
            "billing_cycle": "monthly"
        }, TEST_TOKEN, "Create PayPal Order"),
        
        ("POST", "/api/billing/capture-paypal-order/", {
            "order_id": "test_order_id",
            "payment_data": {"PayerID": "test_payer"}
        }, TEST_TOKEN, "Capture PayPal Order"),
        
        ("GET", "/api/billing/current-plan/", None, TEST_TOKEN, "Get Current Plan"),
        ("POST", "/api/billing/change-plan/", {"plan": "silver"}, TEST_TOKEN, "Change Plan"),
        ("GET", "/api/billing/history/", None, TEST_TOKEN, "Billing History"),
        ("GET", "/api/billing/stats/", None, TEST_TOKEN, "Billing Statistics"),
        
        # Usage tracking (requires token)
        ("GET", "/api/usage/", None, TEST_TOKEN, "Get Usage with Auth"),
        ("POST", "/api/usage/track/", {"endpoint": "test"}, TEST_TOKEN, "Track Usage"),
        ("GET", "/api/usage/history/", None, TEST_TOKEN, "Usage History"),
        
        # Portfolio & Watchlist (requires token)
        ("GET", "/api/portfolio/", None, TEST_TOKEN, "Get Portfolio"),
        ("POST", "/api/portfolio/add/", {"symbol": "AAPL"}, TEST_TOKEN, "Add to Portfolio"),
        ("GET", "/api/watchlist/", None, TEST_TOKEN, "Get Watchlist"),
        ("POST", "/api/watchlist/add/", {"symbol": "TSLA"}, TEST_TOKEN, "Add to Watchlist"),
        
        # Alert management
        ("POST", "/api/alerts/create/", {
            "symbol": "AAPL",
            "condition": "price_above",
            "value": 200
        }, TEST_TOKEN, "Create Alert"),
        
        # WordPress Integration (no auth)
        ("GET", "/api/wordpress/", None, None, "WordPress Stocks"),
        ("GET", "/api/wordpress/stocks/", None, None, "WordPress Stocks Detailed"),
        ("GET", "/api/wordpress/news/", None, None, "WordPress News"),
        ("GET", "/api/wordpress/alerts/", None, None, "WordPress Alerts"),
        
        # Simple APIs (no auth)
        ("GET", "/api/simple/stocks/", None, None, "Simple Stocks API"),
        ("GET", "/api/simple/news/", None, None, "Simple News API"),
    ]
    
    working_count = 0
    broken_count = 0
    error_count = 0
    
    print(f"Testing {len(endpoints_to_test)} endpoints...\n")
    
    for method, endpoint, data, token, description in endpoints_to_test:
        print(f"🔍 Testing: {method} {endpoint}")
        print(f"📝 Description: {description}")
        
        result = test_endpoint(method, endpoint, data, token, description)
        
        if result["status"] == "WORKING":
            print(f"✅ WORKING (Status: {result['status_code']})")
            working_count += 1
        elif result["status"] == "BROKEN":
            print(f"❌ BROKEN (Status: {result['status_code']})")
            print(f"   Response: {result['response']}")
            broken_count += 1
        else:
            print(f"🚨 ERROR: {result['message']}")
            error_count += 1
        
        print("-" * 50)
    
    print("\n📊 SUMMARY")
    print("=" * 50)
    print(f"✅ Working endpoints: {working_count}")
    print(f"❌ Broken endpoints: {broken_count}")
    print(f"🚨 Error endpoints: {error_count}")
    print(f"📊 Total tested: {len(endpoints_to_test)}")
    print(f"📋 Success rate: {(working_count/len(endpoints_to_test)*100):.1f}%")
    
    # Identify critical missing ones based on user's list
    critical_endpoints = [
        "POST /api/auth/register/",
        "POST /api/billing/create-paypal-order/", 
        "POST /api/billing/capture-paypal-order/",
        "GET /api/platform-stats/",
        "GET /api/usage/",
        "GET /api/stocks/{symbol}/quote/",
        "GET /api/realtime/{ticker}/"
    ]
    
    print(f"\n🚨 CRITICAL ENDPOINTS STATUS:")
    print("=" * 50)
    for endpoint in critical_endpoints:
        print(f"- {endpoint}")

if __name__ == "__main__":
    main()