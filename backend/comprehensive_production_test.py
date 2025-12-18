"""
Comprehensive Production Testing Suite
Tests all backend APIs, authentication, and features
Run: python comprehensive_production_test.py
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

# Test credentials
TEST_EMAIL = "carter.kiefer2010@outlook.com"
TEST_PASSWORD = "C2rt3rK#2010"

class TestResults:
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.start_time = time.time()

    def add_result(self, category, test_name, status, details="", response_time=0):
        self.tests.append({
            'category': category,
            'test': test_name,
            'status': status,
            'details': details,
            'response_time': response_time
        })

        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        elif status == "WARN":
            self.warnings += 1

    def print_summary(self):
        duration = time.time() - self.start_time
        total = self.passed + self.failed + self.warnings

        print("\n" + "="*80)
        print("COMPREHENSIVE PRODUCTION TEST RESULTS")
        print("="*80)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed} ({(self.passed/total*100) if total > 0 else 0:.1f}%)")
        print(f"Failed: {self.failed} ({(self.failed/total*100) if total > 0 else 0:.1f}%)")
        print(f"Warnings: {self.warnings} ({(self.warnings/total*100) if total > 0 else 0:.1f}%)")
        print(f"Duration: {duration:.2f}s")
        print("="*80)

        # Group by category
        categories = {}
        for test in self.tests:
            cat = test['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(test)

        for category, tests in categories.items():
            print(f"\n{category}:")
            for test in tests:
                status_icon = "[OK]" if test['status'] == "PASS" else "[X]" if test['status'] == "FAIL" else "[!]"
                print(f"  {status_icon} {test['test']}")
                if test['details']:
                    print(f"     {test['details']}")
                if test['response_time'] > 0:
                    print(f"     Response time: {test['response_time']:.3f}s")

        # Save detailed report
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'summary': {
                    'total': total,
                    'passed': self.passed,
                    'failed': self.failed,
                    'warnings': self.warnings,
                    'duration': duration,
                    'timestamp': datetime.now().isoformat()
                },
                'tests': self.tests
            }, f, indent=2)

        print(f"\nDetailed report saved to: {report_file}")

        return self.failed == 0

results = TestResults()

def test_endpoint(category, name, method, url, expected_status=200, auth=None, data=None, json_data=None):
    """Test a single endpoint"""
    start = time.time()
    try:
        headers = {}
        if auth:
            headers['Authorization'] = f'Bearer {auth}'

        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            if json_data:
                headers['Content-Type'] = 'application/json'
                response = requests.post(url, headers=headers, json=json_data, timeout=10)
            else:
                response = requests.post(url, headers=headers, data=data, timeout=10)
        else:
            response = requests.request(method, url, headers=headers, timeout=10)

        response_time = time.time() - start

        if response.status_code == expected_status:
            results.add_result(category, name, "PASS",
                             f"Status {response.status_code}", response_time)
            return response
        else:
            results.add_result(category, name, "FAIL",
                             f"Expected {expected_status}, got {response.status_code}: {response.text[:100]}",
                             response_time)
            return None
    except Exception as e:
        response_time = time.time() - start
        results.add_result(category, name, "FAIL", str(e), response_time)
        return None

def main():
    print("="*80)
    print("COMPREHENSIVE PRODUCTION TESTING")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Test User: {TEST_EMAIL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # 1. Health Checks
    print("\n[1/10] Testing Health Endpoints...")
    test_endpoint("Health Checks", "Basic health check", "GET", f"{API_URL}/health/")
    test_endpoint("Health Checks", "Detailed health check", "GET", f"{API_URL}/health/detailed/")
    test_endpoint("Health Checks", "Readiness check", "GET", f"{API_URL}/health/ready/")
    test_endpoint("Health Checks", "Liveness check", "GET", f"{API_URL}/health/live/")
    test_endpoint("Health Checks", "Status endpoint", "GET", f"{API_URL}/status/")

    # 2. Public Stock Endpoints
    print("\n[2/10] Testing Public Stock Endpoints...")
    test_endpoint("Stock Data", "Stock list", "GET", f"{API_URL}/stocks/")
    test_endpoint("Stock Data", "Stock detail (AAPL)", "GET", f"{API_URL}/stocks/AAPL/")
    test_endpoint("Stock Data", "Stock search", "GET", f"{API_URL}/search/?q=Apple")
    test_endpoint("Stock Data", "Top gainers", "GET", f"{API_URL}/stocks/top-gainers/")
    test_endpoint("Stock Data", "Top losers", "GET", f"{API_URL}/stocks/top-losers/")
    test_endpoint("Stock Data", "Most active", "GET", f"{API_URL}/stocks/most-active/")
    test_endpoint("Stock Data", "Trending stocks", "GET", f"{API_URL}/trending/")
    test_endpoint("Stock Data", "Market stats", "GET", f"{API_URL}/market-stats/")

    # 3. Billing Endpoints (Public)
    print("\n[3/10] Testing Billing Endpoints...")
    response = test_endpoint("Billing", "Plans metadata", "GET", f"{API_URL}/billing/plans-meta/")
    if response:
        try:
            data = response.json()
            if 'data' in data and 'plans' in data['data']:
                plans = data['data']['plans']
                if 'basic' in plans and 'plus' in plans:
                    basic = plans['basic']
                    plus = plans['plus']

                    # Verify pricing
                    if basic['monthly_price'] == 14.99 and basic['annual_price'] == 149.99:
                        results.add_result("Billing", "Basic plan pricing correct", "PASS",
                                         f"Monthly: ${basic['monthly_price']}, Annual: ${basic['annual_price']}")
                    else:
                        results.add_result("Billing", "Basic plan pricing", "FAIL",
                                         f"Expected $14.99/$149.99, got ${basic['monthly_price']}/${basic['annual_price']}")

                    if plus['monthly_price'] == 24.99 and plus['annual_price'] == 249.99:
                        results.add_result("Billing", "Plus plan pricing correct", "PASS",
                                         f"Monthly: ${plus['monthly_price']}, Annual: ${plus['annual_price']}")
                    else:
                        results.add_result("Billing", "Plus plan pricing", "FAIL",
                                         f"Expected $24.99/$249.99, got ${plus['monthly_price']}/${plus['annual_price']}")

                    # Verify PayPal plan IDs
                    if basic['paypal_plan_ids']['monthly']:
                        results.add_result("Billing", "Basic monthly PayPal ID configured", "PASS",
                                         basic['paypal_plan_ids']['monthly'])
                    else:
                        results.add_result("Billing", "Basic monthly PayPal ID", "FAIL", "Not configured")

                    if plus['paypal_plan_ids']['monthly']:
                        results.add_result("Billing", "Plus monthly PayPal ID configured", "PASS",
                                         plus['paypal_plan_ids']['monthly'])
                    else:
                        results.add_result("Billing", "Plus monthly PayPal ID", "FAIL", "Not configured")
        except Exception as e:
            results.add_result("Billing", "Plans metadata parsing", "FAIL", str(e))

    # 4. Authentication
    print("\n[4/10] Testing Authentication...")
    login_response = test_endpoint("Authentication", "Login attempt", "POST", f"{API_URL}/auth/login/",
                                   expected_status=200,
                                   json_data={'username': TEST_EMAIL, 'password': TEST_PASSWORD})

    auth_token = None
    if login_response:
        try:
            login_data = login_response.json()
            if 'data' in login_data and 'api_token' in login_data['data']:
                auth_token = login_data['data']['api_token']
                results.add_result("Authentication", "Login successful - API token received", "PASS",
                                 f"Token: {auth_token[:20]}...")
            elif 'token' in login_data:
                auth_token = login_data['token']
                results.add_result("Authentication", "Login successful - Token received", "PASS",
                                 f"Token: {auth_token[:20]}...")
            elif 'key' in login_data:
                auth_token = login_data['key']
                results.add_result("Authentication", "Login successful - Key received", "PASS",
                                 f"Key: {auth_token[:20]}...")
            else:
                results.add_result("Authentication", "Login token", "FAIL",
                                 f"No token in response: {login_data}")
        except:
            results.add_result("Authentication", "Login response parsing", "FAIL",
                             "Could not parse login response")

    # 5. Authenticated Endpoints
    print("\n[5/10] Testing Authenticated Endpoints...")
    if auth_token:
        test_endpoint("Authenticated", "Current plan", "GET", f"{API_URL}/billing/current-plan/",
                     auth=auth_token)
        test_endpoint("Authenticated", "Billing history", "GET", f"{API_URL}/billing/history/",
                     auth=auth_token)
        test_endpoint("Authenticated", "Billing stats", "GET", f"{API_URL}/billing/stats/",
                     auth=auth_token)
    else:
        results.add_result("Authenticated", "Skipped - No auth token", "WARN",
                         "Could not test authenticated endpoints")

    # 6. Screener Endpoints
    print("\n[6/10] Testing Screener Endpoints...")
    test_endpoint("Screeners", "Screener templates", "GET", f"{API_URL}/screeners/templates/")
    if auth_token:
        test_endpoint("Screeners", "User screeners list", "GET", f"{API_URL}/screeners/",
                     auth=auth_token)

    # 7. Analytics Endpoints
    print("\n[7/10] Testing Analytics Endpoints...")
    test_endpoint("Analytics", "Total tickers", "GET", f"{API_URL}/stats/total-tickers/")
    test_endpoint("Analytics", "Gainers/Losers stats", "GET", f"{API_URL}/stats/gainers-losers/")

    # 8. News & Alerts
    print("\n[8/10] Testing News & Alerts...")
    if auth_token:
        test_endpoint("News & Alerts", "Alerts list", "GET", f"{API_URL}/alerts/",
                     auth=auth_token)
        test_endpoint("News & Alerts", "Alerts meta", "GET", f"{API_URL}/alerts/meta/",
                     auth=auth_token)

    # 9. Export Endpoints
    print("\n[9/10] Testing Export Endpoints...")
    if auth_token:
        test_endpoint("Exports", "Export stocks CSV", "GET", f"{API_URL}/export/stocks/csv",
                     auth=auth_token)

    # 10. Configuration Checks
    print("\n[10/10] Validating Configuration...")

    # Check .env file
    import os
    env_path = "C:\\Stock-scanner-project\\v2mvp-stock-scanner-complete\\stock-scanner-complete\\backend\\.env"
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_content = f.read()

            if 'GROQ_API_KEY=gsk_' in env_content:
                results.add_result("Configuration", "GROQ API key configured", "PASS")
            else:
                results.add_result("Configuration", "GROQ API key", "FAIL", "Not configured")

            if 'GOOGLE_CLIENT_ID=763397569924-' in env_content:
                results.add_result("Configuration", "Google Client ID configured", "PASS")
            else:
                results.add_result("Configuration", "Google Client ID", "FAIL", "Not configured")

            if 'GOOGLE_CLIENT_SECRET=your_google_client_secret_here' in env_content:
                results.add_result("Configuration", "Google Client Secret", "WARN",
                                 "Placeholder value - needs actual secret")
            else:
                results.add_result("Configuration", "Google Client Secret configured", "PASS")

            if 'PAYPAL_PLAN_BASIC_MONTHLY=P-8M220235GJ619423XNEY3SBQ' in env_content:
                results.add_result("Configuration", "Basic Monthly PayPal plan ID", "PASS")
            else:
                results.add_result("Configuration", "Basic Monthly PayPal plan ID", "FAIL")

            if 'PAYPAL_PLAN_PLUS_MONTHLY=P-7XV80093416938244NEY3OBA' in env_content:
                results.add_result("Configuration", "Plus Monthly PayPal plan ID", "PASS")
            else:
                results.add_result("Configuration", "Plus Monthly PayPal plan ID", "FAIL")
    else:
        results.add_result("Configuration", ".env file", "FAIL", "File not found")

    # Print results
    results.print_summary()

    return results.failed == 0

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
