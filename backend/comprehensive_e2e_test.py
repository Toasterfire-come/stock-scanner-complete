"""
Comprehensive End-to-End and Integration Testing Suite
Tests frontend APIs, authentication flows, PayPal integration, and critical user journeys
Run: python comprehensive_e2e_test.py
"""

import requests
import json
import time
from datetime import datetime
from decimal import Decimal

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

# Test credentials
VIP_EMAIL = "carter.kiefer2010@outlook.com"
VIP_PASSWORD = "C2rt3rK#2010"
VIP_EMAIL_2 = "hamzashehata3000@gmail.com"
VIP_PASSWORD_2 = "HamzaVIP@2024"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

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
            print(f"  {Colors.GREEN}[OK]{Colors.RESET} {test_name}")
        elif status == "FAIL":
            self.failed += 1
            print(f"  {Colors.RED}[X]{Colors.RESET} {test_name}")
            if details:
                print(f"     {Colors.RED}{details}{Colors.RESET}")
        elif status == "WARN":
            self.warnings += 1
            print(f"  {Colors.YELLOW}[!]{Colors.RESET} {test_name}")

        if response_time > 0:
            print(f"     {Colors.CYAN}Response time: {response_time:.3f}s{Colors.RESET}")

    def print_summary(self):
        duration = time.time() - self.start_time
        total = self.passed + self.failed + self.warnings

        print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}END-TO-END TEST RESULTS{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {self.passed} ({(self.passed/total*100) if total > 0 else 0:.1f}%){Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed} ({(self.failed/total*100) if total > 0 else 0:.1f}%){Colors.RESET}")
        print(f"{Colors.YELLOW}Warnings: {self.warnings} ({(self.warnings/total*100) if total > 0 else 0:.1f}%){Colors.RESET}")
        print(f"Duration: {duration:.2f}s")
        print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")

        return self.failed == 0

results = TestResults()

def test_api_call(name, method, url, expected_status=200, headers=None, json_data=None):
    """Make API call and return response"""
    start = time.time()
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=json_data, timeout=10)
        else:
            response = requests.request(method, url, headers=headers, json=json_data, timeout=10)

        response_time = time.time() - start

        if response.status_code == expected_status:
            results.add_result("API Tests", name, "PASS", f"Status {response.status_code}", response_time)
            return response
        else:
            results.add_result("API Tests", name, "FAIL",
                             f"Expected {expected_status}, got {response.status_code}", response_time)
            return None
    except Exception as e:
        response_time = time.time() - start
        results.add_result("API Tests", name, "FAIL", str(e), response_time)
        return None

def main():
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}COMPREHENSIVE END-TO-END & INTEGRATION TESTING{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"Base URL: {BASE_URL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")

    # ====================================================================
    # SECTION 1: VIP AUTHENTICATION TESTING
    # ====================================================================
    print(f"\n{Colors.BOLD}[1/6] VIP AUTHENTICATION TESTING{Colors.RESET}")
    print(f"{Colors.CYAN}Testing VIP account login and token authentication{Colors.RESET}\n")

    # Test VIP Account #1 Login
    print(f"{Colors.MAGENTA}Testing VIP Account #1: {VIP_EMAIL}{Colors.RESET}")
    login_response = test_api_call(
        "VIP #1 Login",
        "POST",
        f"{API_URL}/auth/login/",
        expected_status=200,
        json_data={'username': VIP_EMAIL, 'password': VIP_PASSWORD}
    )

    vip1_token = None
    if login_response:
        try:
            data = login_response.json()
            if 'data' in data and 'api_token' in data['data']:
                vip1_token = data['data']['api_token']
                user_data = data['data']
                results.add_result("VIP Authentication", "VIP #1 Token Received", "PASS",
                                 f"User: {user_data['username']}, Premium: {user_data['is_premium']}")

                # Test using the token
                test_api_call(
                    "VIP #1 Token Authentication",
                    "GET",
                    f"{API_URL}/billing/current-plan/",
                    expected_status=200,
                    headers={'Authorization': f'Bearer {vip1_token}'}
                )
        except Exception as e:
            results.add_result("VIP Authentication", "VIP #1 Token Parsing", "FAIL", str(e))

    # Test VIP Account #2 Login
    print(f"\n{Colors.MAGENTA}Testing VIP Account #2: {VIP_EMAIL_2}{Colors.RESET}")
    login_response = test_api_call(
        "VIP #2 Login",
        "POST",
        f"{API_URL}/auth/login/",
        expected_status=200,
        json_data={'username': VIP_EMAIL_2, 'password': VIP_PASSWORD_2}
    )

    vip2_token = None
    if login_response:
        try:
            data = login_response.json()
            if 'data' in data and 'api_token' in data['data']:
                vip2_token = data['data']['api_token']
                user_data = data['data']
                results.add_result("VIP Authentication", "VIP #2 Token Received", "PASS",
                                 f"User: {user_data['username']}, Premium: {user_data['is_premium']}")

                # Test using the token
                test_api_call(
                    "VIP #2 Token Authentication",
                    "GET",
                    f"{API_URL}/billing/current-plan/",
                    expected_status=200,
                    headers={'Authorization': f'Bearer {vip2_token}'}
                )
        except Exception as e:
            results.add_result("VIP Authentication", "VIP #2 Token Parsing", "FAIL", str(e))

    # ====================================================================
    # SECTION 2: BILLING & SUBSCRIPTION TESTING
    # ====================================================================
    print(f"\n{Colors.BOLD}[2/6] BILLING & SUBSCRIPTION TESTING{Colors.RESET}")
    print(f"{Colors.CYAN}Testing plan metadata and subscription endpoints{Colors.RESET}\n")

    # Test Plans Metadata
    response = test_api_call(
        "Get Plans Metadata",
        "GET",
        f"{API_URL}/billing/plans-meta/",
        expected_status=200
    )

    if response:
        try:
            data = response.json()
            if 'data' in data and 'plans' in data['data']:
                plans = data['data']['plans']

                # Verify Basic Plan
                if 'basic' in plans:
                    basic = plans['basic']
                    if basic['monthly_price'] == 14.99 and basic['annual_price'] == 149.99:
                        results.add_result("Billing", "Basic Plan Pricing", "PASS",
                                         f"Monthly: ${basic['monthly_price']}, Annual: ${basic['annual_price']}")
                    else:
                        results.add_result("Billing", "Basic Plan Pricing", "FAIL",
                                         f"Expected $14.99/$149.99, got ${basic['monthly_price']}/${basic['annual_price']}")

                # Verify Plus Plan
                if 'plus' in plans:
                    plus = plans['plus']
                    if plus['monthly_price'] == 24.99 and plus['annual_price'] == 249.99:
                        results.add_result("Billing", "Plus Plan Pricing", "PASS",
                                         f"Monthly: ${plus['monthly_price']}, Annual: ${plus['annual_price']}")
                    else:
                        results.add_result("Billing", "Plus Plan Pricing", "FAIL",
                                         f"Expected $24.99/$249.99, got ${plus['monthly_price']}/${plus['annual_price']}")

                    # Check PayPal Plan IDs
                    if plus.get('paypal_plan_ids', {}).get('monthly'):
                        results.add_result("Billing", "Plus PayPal Plan ID Configured", "PASS",
                                         plus['paypal_plan_ids']['monthly'])
        except Exception as e:
            results.add_result("Billing", "Plans Metadata Parsing", "FAIL", str(e))

    # Test VIP Subscription Details
    if vip1_token:
        print(f"\n{Colors.MAGENTA}Checking VIP #1 Subscription Details{Colors.RESET}")
        response = test_api_call(
            "VIP #1 Current Plan",
            "GET",
            f"{API_URL}/billing/current-plan/",
            expected_status=200,
            headers={'Authorization': f'Bearer {vip1_token}'}
        )

        if response:
            try:
                data = response.json()
                if 'data' in data:
                    plan_data = data['data']
                    results.add_result("VIP Subscriptions", "VIP #1 Plan Details", "PASS",
                                     f"Plan: {plan_data.get('plan_name')}, Premium: {plan_data.get('is_premium')}")
            except Exception as e:
                results.add_result("VIP Subscriptions", "VIP #1 Plan Parsing", "FAIL", str(e))

    # ====================================================================
    # SECTION 3: PAYPAL INTEGRATION TESTING
    # ====================================================================
    print(f"\n{Colors.BOLD}[3/6] PAYPAL INTEGRATION TESTING{Colors.RESET}")
    print(f"{Colors.CYAN}Testing PayPal plan configuration and webhook setup{Colors.RESET}\n")

    # Check PayPal Environment Configuration
    try:
        import os
        import sys
        sys.path.insert(0, 'C:\\Stock-scanner-project\\v2mvp-stock-scanner-complete\\stock-scanner-complete\\backend')
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')

        import django
        django.setup()

        from django.conf import settings

        # Check PayPal Mode
        paypal_mode = getattr(settings, 'PAYPAL_MODE', 'sandbox')
        if paypal_mode == 'live':
            results.add_result("PayPal Config", "PayPal Mode", "PASS", "Live mode configured")
        else:
            results.add_result("PayPal Config", "PayPal Mode", "WARN", f"Currently in {paypal_mode} mode")

        # Check PayPal Plan IDs
        plan_ids = {
            'Basic Monthly': getattr(settings, 'PAYPAL_PLAN_BASIC_MONTHLY', None),
            'Basic Annual': getattr(settings, 'PAYPAL_PLAN_BASIC_ANNUAL', None),
            'Plus Monthly': getattr(settings, 'PAYPAL_PLAN_PLUS_MONTHLY', None),
            'Plus Annual': getattr(settings, 'PAYPAL_PLAN_PLUS_ANNUAL', None),
        }

        for plan_name, plan_id in plan_ids.items():
            if plan_id and plan_id.startswith('P-'):
                results.add_result("PayPal Config", f"{plan_name} Plan ID", "PASS", plan_id)
            else:
                results.add_result("PayPal Config", f"{plan_name} Plan ID", "FAIL", "Not configured")

        # Check PayPal Webhook ID
        webhook_id = getattr(settings, 'PAYPAL_WEBHOOK_ID', None)
        if webhook_id:
            results.add_result("PayPal Config", "Webhook ID Configured", "PASS", webhook_id[:20] + "...")
        else:
            results.add_result("PayPal Config", "Webhook ID", "FAIL", "Not configured")

    except Exception as e:
        results.add_result("PayPal Config", "Configuration Check", "FAIL", str(e))

    # Test PayPal Webhook Endpoint
    print(f"\n{Colors.MAGENTA}Testing PayPal Webhook Endpoint{Colors.RESET}")
    webhook_response = test_api_call(
        "PayPal Webhook Accessible",
        "POST",
        f"{API_URL}/billing/paypal-webhook/",
        expected_status=400,  # Expected - we're not sending valid PayPal data
        json_data={}
    )

    # ====================================================================
    # SECTION 4: STOCK DATA API TESTING
    # ====================================================================
    print(f"\n{Colors.BOLD}[4/6] STOCK DATA API TESTING{Colors.RESET}")
    print(f"{Colors.CYAN}Testing stock data endpoints{Colors.RESET}\n")

    # Test public endpoints
    test_api_call("Top Gainers", "GET", f"{API_URL}/stocks/top-gainers/", expected_status=200)
    test_api_call("Top Losers", "GET", f"{API_URL}/stocks/top-losers/", expected_status=200)
    test_api_call("Most Active", "GET", f"{API_URL}/stocks/most-active/", expected_status=200)

    # Test authenticated endpoints (should fail without auth)
    test_api_call("Stock List (No Auth)", "GET", f"{API_URL}/stocks/", expected_status=403)

    # Test with auth
    if vip1_token:
        response = test_api_call(
            "Stock List (With Auth)",
            "GET",
            f"{API_URL}/stocks/",
            expected_status=200,
            headers={'Authorization': f'Bearer {vip1_token}'}
        )

    # ====================================================================
    # SECTION 5: ANALYTICS & STATS TESTING
    # ====================================================================
    print(f"\n{Colors.BOLD}[5/6] ANALYTICS & STATS TESTING{Colors.RESET}")
    print(f"{Colors.CYAN}Testing analytics endpoints{Colors.RESET}\n")

    test_api_call("Total Tickers", "GET", f"{API_URL}/stats/total-tickers/", expected_status=200)
    test_api_call("Gainers/Losers Stats", "GET", f"{API_URL}/stats/gainers-losers/", expected_status=200)

    # Test authenticated analytics
    if vip1_token:
        test_api_call(
            "Billing Stats",
            "GET",
            f"{API_URL}/billing/stats/",
            expected_status=200,
            headers={'Authorization': f'Bearer {vip1_token}'}
        )

    # ====================================================================
    # SECTION 6: END-TO-END USER JOURNEY TESTING
    # ====================================================================
    print(f"\n{Colors.BOLD}[6/6] END-TO-END USER JOURNEY TESTING{Colors.RESET}")
    print(f"{Colors.CYAN}Testing complete user flows{Colors.RESET}\n")

    if vip1_token:
        print(f"{Colors.MAGENTA}Testing Complete VIP User Journey{Colors.RESET}")

        # 1. Login
        results.add_result("E2E Journey", "Step 1: Login", "PASS", "VIP account logged in")

        # 2. Get Current Plan
        plan_response = test_api_call(
            "Step 2: Get Current Plan",
            "GET",
            f"{API_URL}/billing/current-plan/",
            expected_status=200,
            headers={'Authorization': f'Bearer {vip1_token}'}
        )

        # 3. View Billing History
        test_api_call(
            "Step 3: View Billing History",
            "GET",
            f"{API_URL}/billing/history/",
            expected_status=200,
            headers={'Authorization': f'Bearer {vip1_token}'}
        )

        # 4. Access Stock Data
        test_api_call(
            "Step 4: Access Stock Data",
            "GET",
            f"{API_URL}/stocks/top-gainers/",
            expected_status=200,
            headers={'Authorization': f'Bearer {vip1_token}'}
        )

        # 5. Create/View Alerts
        test_api_call(
            "Step 5: View Alerts",
            "GET",
            f"{API_URL}/alerts/",
            expected_status=200,
            headers={'Authorization': f'Bearer {vip1_token}'}
        )

        # 6. View Screeners
        test_api_call(
            "Step 6: View Screeners",
            "GET",
            f"{API_URL}/screeners/",
            expected_status=200,
            headers={'Authorization': f'Bearer {vip1_token}'}
        )

    # Print final summary
    results.print_summary()

    # Generate detailed report
    report_file = f"e2e_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump({
            'summary': {
                'total': results.passed + results.failed + results.warnings,
                'passed': results.passed,
                'failed': results.failed,
                'warnings': results.warnings,
                'timestamp': datetime.now().isoformat()
            },
            'tests': results.tests
        }, f, indent=2)

    print(f"{Colors.CYAN}Detailed report saved to: {report_file}{Colors.RESET}\n")

    return results.failed == 0

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
