#!/usr/bin/env python3
"""
Backend API Testing Suite for Retail Trade Scanner
Tests all backend endpoints as specified in the review request.
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://retailscanner.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.watchlist_id = None
        self.portfolio_id = None
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    Details: {details}")
        if response_data and not success:
            print(f"    Response: {response_data}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response": response_data if not success else None
        })
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None, use_auth: bool = False) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        url = f"{API_BASE}{endpoint}"
        req_headers = headers or {}
        
        # Add authorization as query parameter if needed
        if use_auth and self.auth_token:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}authorization=Bearer {self.auth_token}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=req_headers)
            elif method.upper() == "POST":
                req_headers["Content-Type"] = "application/json"
                response = self.session.post(url, json=data, headers=req_headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=req_headers)
            else:
                return False, f"Unsupported method: {method}", 0
            
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            return response.status_code < 400, response_data, response.status_code
        except Exception as e:
            return False, str(e), 0

    def test_public_endpoints(self):
        """Test public endpoints that don't require authentication"""
        print("=== Testing Public Endpoints ===")
        
        # Test root endpoint
        success, data, status = self.make_request("GET", "/")
        self.log_test("GET /api/", success, f"Status: {status}", data if not success else None)
        
        # Test health endpoint
        success, data, status = self.make_request("GET", "/health/")
        expected_fields = ["status", "database", "version", "timestamp", "endpoints", "features"]
        if success and isinstance(data, dict):
            missing_fields = [f for f in expected_fields if f not in data]
            if missing_fields:
                success = False
                data = f"Missing fields: {missing_fields}"
        self.log_test("GET /api/health/", success, f"Status: {status}", data if not success else None)

    def test_stocks_endpoints(self):
        """Test stock-related endpoints"""
        print("=== Testing Stocks Endpoints ===")
        
        # Test stocks list with limit
        success, data, status = self.make_request("GET", "/stocks/?limit=5")
        if success and isinstance(data, dict):
            if "data" not in data or not isinstance(data["data"], list):
                success = False
                data = "Expected 'data' field with list of stocks"
        self.log_test("GET /api/stocks/?limit=5", success, f"Status: {status}", data if not success else None)
        
        # Test stock detail
        success, data, status = self.make_request("GET", "/stock/AAPL/")
        if success and isinstance(data, dict):
            if "data" not in data or not data["data"]:
                success = False
                data = "Expected stock data for AAPL"
        self.log_test("GET /api/stock/AAPL/", success, f"Status: {status}", data if not success else None)
        
        # Test search
        success, data, status = self.make_request("GET", "/search/?q=NVDA")
        if success and isinstance(data, dict):
            if "results" not in data or not isinstance(data["results"], list):
                success = False
                data = "Expected 'results' field with search results"
        self.log_test("GET /api/search/?q=NVDA", success, f"Status: {status}", data if not success else None)
        
        # Test trending
        success, data, status = self.make_request("GET", "/trending/")
        if success and isinstance(data, dict):
            expected_keys = ["high_volume", "top_gainers", "most_active"]
            missing_keys = [k for k in expected_keys if k not in data]
            if missing_keys:
                success = False
                data = f"Missing keys: {missing_keys}"
        self.log_test("GET /api/trending/", success, f"Status: {status}", data if not success else None)
        
        # Test market stats
        success, data, status = self.make_request("GET", "/market-stats/")
        if success and isinstance(data, dict):
            expected_keys = ["market_overview", "top_gainers", "top_losers", "most_active"]
            missing_keys = [k for k in expected_keys if k not in data]
            if missing_keys:
                success = False
                data = f"Missing keys: {missing_keys}"
        self.log_test("GET /api/market-stats/", success, f"Status: {status}", data if not success else None)

    def test_authentication(self):
        """Test authentication endpoints"""
        print("=== Testing Authentication ===")
        
        # Test login
        login_data = {"username": "demo", "password": "password123"}
        success, data, status = self.make_request("POST", "/auth/login/", login_data)
        
        if success and isinstance(data, dict) and "token" in data:
            self.auth_token = data["token"]
            self.log_test("POST /api/auth/login/", True, f"Status: {status}, Token received")
        else:
            self.log_test("POST /api/auth/login/", False, f"Status: {status}", data)
            return False
        
        # Test profile with token
        success, data, status = self.make_request("GET", "/user/profile/", use_auth=True)
        if success and isinstance(data, dict) and "data" in data:
            profile_data = data["data"]
            expected_fields = ["user_id", "username", "email"]
            missing_fields = [f for f in expected_fields if f not in profile_data]
            if missing_fields:
                success = False
                data = f"Missing profile fields: {missing_fields}"
        self.log_test("GET /api/user/profile/", success, f"Status: {status}", data if not success else None)
        
        return True

    def test_watchlist(self):
        """Test watchlist endpoints"""
        print("=== Testing Watchlist ===")
        
        if not self.auth_token:
            self.log_test("Watchlist Tests", False, "No auth token available")
            return
        
        # Add to watchlist
        watchlist_data = {"symbol": "AAPL"}
        success, data, status = self.make_request("POST", "/watchlist/add/", watchlist_data, use_auth=True)
        if success and isinstance(data, dict) and "data" in data:
            self.watchlist_id = data["data"].get("id")
        self.log_test("POST /api/watchlist/add/", success, f"Status: {status}", data if not success else None)
        
        # Get watchlist
        success, data, status = self.make_request("GET", "/watchlist/", use_auth=True)
        if success and isinstance(data, dict):
            if "data" not in data or not isinstance(data["data"], list):
                success = False
                data = "Expected 'data' field with watchlist items"
        self.log_test("GET /api/watchlist/", success, f"Status: {status}", data if not success else None)
        
        # Delete from watchlist
        if self.watchlist_id:
            success, data, status = self.make_request("DELETE", f"/watchlist/{self.watchlist_id}/", use_auth=True)
            self.log_test(f"DELETE /api/watchlist/{self.watchlist_id}/", success, f"Status: {status}", data if not success else None)

    def test_portfolio(self):
        """Test portfolio endpoints"""
        print("=== Testing Portfolio ===")
        
        if not self.auth_token:
            self.log_test("Portfolio Tests", False, "No auth token available")
            return
        
        # Add to portfolio
        portfolio_data = {"symbol": "AAPL", "shares": 2, "avg_cost": 180}
        success, data, status = self.make_request("POST", "/portfolio/add/", portfolio_data, use_auth=True)
        if success and isinstance(data, dict) and "data" in data:
            self.portfolio_id = data["data"].get("id")
        self.log_test("POST /api/portfolio/add/", success, f"Status: {status}", data if not success else None)
        
        # Get portfolio
        success, data, status = self.make_request("GET", "/portfolio/", use_auth=True)
        if success and isinstance(data, dict):
            if "data" not in data or not isinstance(data["data"], list):
                success = False
                data = "Expected 'data' field with portfolio items"
        self.log_test("GET /api/portfolio/", success, f"Status: {status}", data if not success else None)
        
        # Delete from portfolio
        if self.portfolio_id:
            success, data, status = self.make_request("DELETE", f"/portfolio/{self.portfolio_id}/", use_auth=True)
            self.log_test(f"DELETE /api/portfolio/{self.portfolio_id}/", success, f"Status: {status}", data if not success else None)

    def test_alerts(self):
        """Test alerts endpoints"""
        print("=== Testing Alerts ===")
        
        # Get alerts create meta
        success, data, status = self.make_request("GET", "/alerts/create/")
        if success and isinstance(data, dict):
            expected_fields = ["endpoint", "method", "description", "required_fields"]
            missing_fields = [f for f in expected_fields if f not in data]
            if missing_fields:
                success = False
                data = f"Missing fields: {missing_fields}"
        self.log_test("GET /api/alerts/create/", success, f"Status: {status}", data if not success else None)
        
        # Create alert
        alert_data = {"ticker": "MSFT", "target_price": 500, "condition": "above", "email": "demo@example.com"}
        success, data, status = self.make_request("POST", "/alerts/create/", alert_data)
        if success and isinstance(data, dict):
            if "alert_id" not in data:
                success = False
                data = "Expected 'alert_id' in response"
        self.log_test("POST /api/alerts/create/", success, f"Status: {status}", data if not success else None)

    def test_revenue(self):
        """Test revenue endpoints"""
        print("=== Testing Revenue ===")
        
        # Initialize codes
        success, data, status = self.make_request("POST", "/revenue/initialize-codes/")
        self.log_test("POST /api/revenue/initialize-codes/", success, f"Status: {status}", data if not success else None)
        
        # Validate discount
        validate_data = {"code": "ref50"}
        success, data, status = self.make_request("POST", "/revenue/validate-discount/", validate_data)
        if success and isinstance(data, dict):
            if "valid" not in data:
                success = False
                data = "Expected 'valid' field in response"
        self.log_test("POST /api/revenue/validate-discount/", success, f"Status: {status}", data if not success else None)
        
        # Apply discount
        apply_data = {"code": "ref50", "amount": 100}
        success, data, status = self.make_request("POST", "/revenue/apply-discount/", apply_data)
        if success and isinstance(data, dict):
            expected_fields = ["original_amount", "discount_amount", "final_amount"]
            missing_fields = [f for f in expected_fields if f not in data]
            if missing_fields:
                success = False
                data = f"Missing fields: {missing_fields}"
        self.log_test("POST /api/revenue/apply-discount/", success, f"Status: {status}", data if not success else None)
        
        # Record payment
        payment_data = {"user_id": 1, "amount": 100, "discount_code": "ref50"}
        success, data, status = self.make_request("POST", "/revenue/record-payment/", payment_data)
        if success and isinstance(data, dict):
            if "revenue_id" not in data:
                success = False
                data = "Expected 'revenue_id' in response"
        self.log_test("POST /api/revenue/record-payment/", success, f"Status: {status}", data if not success else None)
        
        # Get revenue analytics
        success, data, status = self.make_request("GET", "/revenue/revenue-analytics/")
        if success and isinstance(data, dict):
            if "data" not in data or "total_revenue" not in data["data"]:
                success = False
                data = "Expected 'data' with 'total_revenue'"
        self.log_test("GET /api/revenue/revenue-analytics/", success, f"Status: {status}", data if not success else None)

    def test_notifications(self):
        """Test notifications endpoints"""
        print("=== Testing Notifications ===")
        
        if not self.auth_token:
            self.log_test("Notifications Tests", False, "No auth token available")
            return
        
        # Get notification settings
        success, data, status = self.make_request("GET", "/user/notification-settings/", use_auth=True)
        settings_data = None
        if success and isinstance(data, dict) and "data" in data:
            settings_data = data["data"]
        self.log_test("GET /api/user/notification-settings/", success, f"Status: {status}", data if not success else None)
        
        # Update notification settings (send same structure back)
        if settings_data:
            success, data, status = self.make_request("POST", "/notifications/settings/", settings_data, use_auth=True)
            self.log_test("POST /api/notifications/settings/", success, f"Status: {status}", data if not success else None)
        
        # Get notification history
        success, data, status = self.make_request("GET", "/notifications/history/", use_auth=True)
        if success and isinstance(data, dict):
            if "data" not in data or not isinstance(data["data"], list):
                success = False
                data = "Expected 'data' field with notification items"
        self.log_test("GET /api/notifications/history/", success, f"Status: {status}", data if not success else None)
        
        # Mark all as read
        mark_read_data = {"mark_all": True}
        success, data, status = self.make_request("POST", "/notifications/mark-read/", mark_read_data, use_auth=True)
        self.log_test("POST /api/notifications/mark-read/", success, f"Status: {status}", data if not success else None)

    def test_news(self):
        """Test news endpoints"""
        print("=== Testing News ===")
        
        if not self.auth_token:
            self.log_test("News Tests", False, "No auth token available")
            return
        
        # Get news feed
        success, data, status = self.make_request("GET", "/news/feed/", use_auth=True)
        if success and isinstance(data, dict):
            if "data" not in data:
                success = False
                data = "Expected 'data' field in response"
        self.log_test("GET /api/news/feed/", success, f"Status: {status}", data if not success else None)
        
        # Mark news as read
        mark_read_data = {"news_id": 1}
        success, data, status = self.make_request("POST", "/news/mark-read/", mark_read_data, use_auth=True)
        self.log_test("POST /api/news/mark-read/", success, f"Status: {status}", data if not success else None)
        
        # Update news preferences
        prefs_data = {"categories": ["technology", "finance"], "frequency": "daily"}
        success, data, status = self.make_request("POST", "/news/preferences/", prefs_data, use_auth=True)
        self.log_test("POST /api/news/preferences/", success, f"Status: {status}", data if not success else None)
        
        # Sync portfolio
        success, data, status = self.make_request("POST", "/news/sync-portfolio/", use_auth=True)
        self.log_test("POST /api/news/sync-portfolio/", success, f"Status: {status}", data if not success else None)

    def run_all_tests(self):
        """Run all test suites"""
        print(f"Starting Backend API Tests for: {BASE_URL}")
        print("=" * 60)
        
        self.test_public_endpoints()
        self.test_stocks_endpoints()
        
        if self.test_authentication():
            self.test_watchlist()
            self.test_portfolio()
            self.test_notifications()
            self.test_news()
        
        self.test_alerts()
        self.test_revenue()
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test']}: {result['details']}")
        
        return passed == total

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)