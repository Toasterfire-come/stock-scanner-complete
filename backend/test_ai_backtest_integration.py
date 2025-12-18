"""
AI Chat and Backtest Integration Testing
Tests all AI chat endpoints and backtest functionality without requiring historical data
"""
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List
import time

# Configuration
API_URL = "http://localhost:8000/api"
VIP_EMAIL = "carter.kiefer2010@outlook.com"
VIP_PASSWORD = "C2rt3rK#2010"

# Test results
class TestResults:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.results = []

    def add_result(self, category: str, test_name: str, status: str, details: str = "", response_time: float = 0):
        self.total += 1
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        elif status == "WARN":
            self.warnings += 1

        self.results.append({
            "category": category,
            "test_name": test_name,
            "status": status,
            "details": details,
            "response_time": f"{response_time:.3f}s" if response_time else "N/A"
        })

    def print_summary(self):
        print("\n" + "="*80)
        print("AI CHAT & BACKTEST INTEGRATION TEST RESULTS")
        print("="*80)
        print(f"Total Tests: {self.total}")
        print(f"Passed: {self.passed} ({self.passed/self.total*100:.1f}%)" if self.total > 0 else "Passed: 0")
        print(f"Failed: {self.failed} ({self.failed/self.total*100:.1f}%)" if self.total > 0 else "Failed: 0")
        print(f"Warnings: {self.warnings} ({self.warnings/self.total*100:.1f}%)" if self.total > 0 else "Warnings: 0")
        print("="*80)

        for category in ["AI Status", "AI Chat", "Strategy Understanding", "Code Generation", "Backtest Management", "Backtest Limits"]:
            category_tests = [r for r in self.results if r["category"] == category]
            if category_tests:
                print(f"\n{category}:")
                for result in category_tests:
                    status_symbol = {
                        "PASS": "[OK]",
                        "FAIL": "[X]",
                        "WARN": "[!]"
                    }.get(result["status"], "[?]")

                    print(f"  {status_symbol} {result['test_name']}")
                    if result["details"]:
                        print(f"     {result['details']}")
                    if result["response_time"] != "N/A":
                        print(f"     Response time: {result['response_time']}")


results = TestResults()


def test_api_call(test_name: str, category: str, method: str, endpoint: str,
                  expected_status: int = 200, json_data: Dict = None,
                  headers: Dict = None) -> Dict:
    """Make API call and record result"""
    try:
        url = f"{API_URL}/{endpoint}"
        start_time = time.time()

        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=json_data, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        elapsed_time = time.time() - start_time

        if response.status_code == expected_status:
            try:
                data = response.json()
                results.add_result(category, test_name, "PASS",
                                 f"Status {response.status_code}", elapsed_time)
                return data
            except:
                results.add_result(category, test_name, "PASS",
                                 f"Status {response.status_code} (no JSON)", elapsed_time)
                return {}
        else:
            error_msg = f"Expected {expected_status}, got {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f": {error_data.get('error', '')}"
            except:
                error_msg += f": {response.text[:100]}"

            results.add_result(category, test_name, "FAIL", error_msg, elapsed_time)
            return {}

    except Exception as e:
        results.add_result(category, test_name, "FAIL", f"Exception: {str(e)}")
        return {}


def login_and_get_token() -> str:
    """Login with VIP account and get bearer token"""
    print("\nLogging in with VIP account...")
    response = test_api_call(
        "VIP Login",
        "Authentication",
        "POST",
        "auth/login/",
        expected_status=200,
        json_data={
            "username": VIP_EMAIL,
            "password": VIP_PASSWORD
        }
    )

    if response.get('success') and response.get('data', {}).get('api_token'):
        token = response['data']['api_token']
        print(f"Login successful. Token: {token[:20]}...")
        return token
    else:
        print("Login failed!")
        return None


def test_ai_status():
    """Test AI availability status"""
    print("\n[1/6] Testing AI Status...")

    response = test_api_call(
        "AI Status Check",
        "AI Status",
        "GET",
        "backtesting/ai-status/",
        expected_status=200
    )

    if response:
        ai_available = response.get('ai_available', False)
        model = response.get('model', 'N/A')

        if ai_available:
            results.add_result("AI Status", "AI Available", "PASS",
                             f"Model: {model}")
        else:
            results.add_result("AI Status", "AI Available", "WARN",
                             "AI not available - GROQ_API_KEY may not be configured")


def test_ai_chat():
    """Test conversational AI strategy refinement"""
    print("\n[2/6] Testing AI Chat...")

    # Test 1: Initial message
    test_api_call(
        "Chat - Initial Message",
        "AI Chat",
        "POST",
        "backtesting/chat/",
        expected_status=200,
        json_data={
            "message": "I want to create a simple RSI-based swing trading strategy",
            "conversation_history": [],
            "category": "swing_trading"
        }
    )

    # Test 2: Follow-up message
    test_api_call(
        "Chat - Follow-up",
        "AI Chat",
        "POST",
        "backtesting/chat/",
        expected_status=200,
        json_data={
            "message": "I want to buy when RSI is below 30 and sell when it's above 70",
            "conversation_history": [
                {"role": "user", "content": "I want to create a simple RSI-based swing trading strategy"},
                {"role": "assistant", "content": "That sounds great! Can you tell me more about the entry and exit conditions?"}
            ],
            "category": "swing_trading"
        }
    )

    # Test 3: Empty message (should fail)
    test_api_call(
        "Chat - Empty Message",
        "AI Chat",
        "POST",
        "backtesting/chat/",
        expected_status=400,
        json_data={
            "message": "",
            "conversation_history": [],
            "category": "swing_trading"
        }
    )


def test_strategy_understanding():
    """Test AI strategy understanding"""
    print("\n[3/6] Testing Strategy Understanding...")

    test_strategies = [
        {
            "name": "Simple RSI Strategy",
            "text": "Buy when RSI drops below 30 (oversold), sell when RSI goes above 70 (overbought). Use 5% stop loss and 10% take profit.",
            "category": "swing_trading"
        },
        {
            "name": "MACD Crossover",
            "text": "Enter long when MACD line crosses above signal line. Exit when MACD crosses below signal line. 3% stop loss.",
            "category": "day_trading"
        },
        {
            "name": "Moving Average Cross",
            "text": "Buy when 20-day SMA crosses above 50-day SMA. Sell when 20-day crosses below 50-day. Hold for weeks.",
            "category": "long_term"
        }
    ]

    for strategy in test_strategies:
        response = test_api_call(
            f"Understand - {strategy['name']}",
            "Strategy Understanding",
            "POST",
            "backtesting/understand/",
            expected_status=200,
            json_data={
                "strategy_text": strategy['text'],
                "category": strategy['category']
            }
        )

        if response and response.get('understanding'):
            understanding = response['understanding']
            indicators = understanding.get('indicators', [])
            entry_conds = understanding.get('entry_conditions', [])

            results.add_result(
                "Strategy Understanding",
                f"{strategy['name']} - Parsed",
                "PASS" if indicators and entry_conds else "WARN",
                f"Indicators: {', '.join(indicators[:3])}..." if indicators else "No indicators parsed"
            )


def test_code_generation():
    """Test AI code generation"""
    print("\n[4/6] Testing Code Generation...")

    test_strategies = [
        {
            "name": "RSI Strategy",
            "text": "Buy when RSI < 30, sell when RSI > 70. 5% stop loss, 10% take profit.",
            "category": "swing_trading"
        },
        {
            "name": "Invalid Strategy",
            "text": "Just buy stocks randomly",
            "category": "swing_trading"
        }
    ]

    for strategy in test_strategies:
        response = test_api_call(
            f"Generate Code - {strategy['name']}",
            "Code Generation",
            "POST",
            "backtesting/generate-code/",
            expected_status=200 if "randomly" not in strategy['text'] else 400,
            json_data={
                "strategy_text": strategy['text'],
                "category": strategy['category']
            }
        )

        if response and response.get('code'):
            code = response['code']
            has_entry = 'entry_condition' in code
            has_exit = 'exit_condition' in code
            has_indicators = 'calculate_indicators' in code

            if has_entry and has_exit and has_indicators:
                results.add_result(
                    "Code Generation",
                    f"{strategy['name']} - Code Quality",
                    "PASS",
                    f"Generated {len(code)} chars with all required functions"
                )
            else:
                results.add_result(
                    "Code Generation",
                    f"{strategy['name']} - Code Quality",
                    "WARN",
                    f"Missing functions: entry={has_entry}, exit={has_exit}, indicators={has_indicators}"
                )


def test_backtest_management(bearer_token: str = None):
    """Test backtest creation and management"""
    print("\n[5/6] Testing Backtest Management...")

    headers = {}
    if bearer_token:
        headers['Authorization'] = f'Bearer {bearer_token}'

    # Test 1: Create backtest
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    response = test_api_call(
        "Create Backtest",
        "Backtest Management",
        "POST",
        "backtesting/create/",
        expected_status=200,
        json_data={
            "name": "Test RSI Strategy",
            "strategy_text": "Buy when RSI < 30, sell when RSI > 70",
            "category": "swing_trading",
            "symbols": ["AAPL"],
            "start_date": start_date,
            "end_date": end_date,
            "initial_capital": 10000.00
        },
        headers=headers
    )

    backtest_id = None
    if response and response.get('success'):
        backtest_id = response.get('backtest_id')
        status = response.get('status')
        remaining = response.get('backtests_remaining', 'Unknown')

        results.add_result(
            "Backtest Management",
            "Backtest Created",
            "PASS",
            f"ID: {backtest_id}, Status: {status}, Remaining: {remaining}"
        )

    # Test 2: List backtests
    test_api_call(
        "List Backtests",
        "Backtest Management",
        "GET",
        "backtesting/list/",
        expected_status=200,
        headers=headers
    )

    # Test 3: List baseline strategies
    response = test_api_call(
        "List Baseline Strategies",
        "Backtest Management",
        "GET",
        "backtesting/baseline-strategies/",
        expected_status=200,
        headers=headers
    )

    if response and response.get('strategies'):
        num_strategies = len(response['strategies'])
        results.add_result(
            "Backtest Management",
            "Baseline Strategies Available",
            "PASS" if num_strategies > 0 else "WARN",
            f"{num_strategies} baseline strategies found"
        )

    # Test 4: Get specific backtest (if created)
    if backtest_id:
        response = test_api_call(
            "Get Backtest Details",
            "Backtest Management",
            "GET",
            f"backtesting/{backtest_id}/",
            expected_status=200,
            headers=headers
        )

        if response and response.get('backtest'):
            backtest = response['backtest']
            results.add_result(
                "Backtest Management",
                "Backtest Details Retrieved",
                "PASS",
                f"Name: {backtest.get('name')}, Status: {backtest.get('status')}"
            )

    # Test 5: Missing required fields
    test_api_call(
        "Create Backtest - Missing Fields",
        "Backtest Management",
        "POST",
        "backtesting/create/",
        expected_status=400,
        json_data={
            "name": "Incomplete Test"
            # Missing required fields
        },
        headers=headers
    )

    return backtest_id


def test_backtest_limits(bearer_token: str = None):
    """Test backtest limits and subscription tiers"""
    print("\n[6/6] Testing Backtest Limits...")

    headers = {}
    if bearer_token:
        headers['Authorization'] = f'Bearer {bearer_token}'

    response = test_api_call(
        "Get Backtest Limits",
        "Backtest Limits",
        "GET",
        "backtesting/limits/",
        expected_status=200,
        headers=headers
    )

    if response and response.get('data'):
        data = response['data']
        tier = data.get('tier', 'unknown')
        limit = data.get('limit', 0)
        used = data.get('used', 0)
        remaining = data.get('remaining', 0)
        unlimited = data.get('unlimited', False)

        if unlimited or limit == -1:
            results.add_result(
                "Backtest Limits",
                "Subscription Tier",
                "PASS",
                f"Tier: {tier}, Unlimited backtests"
            )
        else:
            results.add_result(
                "Backtest Limits",
                "Subscription Tier",
                "PASS" if remaining > 0 else "WARN",
                f"Tier: {tier}, Used: {used}/{limit}, Remaining: {remaining}"
            )


def main():
    print("="*80)
    print("AI CHAT & BACKTEST INTEGRATION TESTING")
    print("="*80)
    print(f"Base URL: {API_URL}")
    print(f"VIP Email: {VIP_EMAIL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Login
    bearer_token = login_and_get_token()

    # Run tests
    test_ai_status()
    test_ai_chat()
    test_strategy_understanding()
    test_code_generation()
    backtest_id = test_backtest_management(bearer_token)
    test_backtest_limits(bearer_token)

    # Print results
    results.print_summary()

    # Save results to JSON
    report_file = f"ai_backtest_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "api_url": API_URL,
            "summary": {
                "total": results.total,
                "passed": results.passed,
                "failed": results.failed,
                "warnings": results.warnings,
                "pass_rate": f"{results.passed/results.total*100:.1f}%" if results.total > 0 else "0%"
            },
            "results": results.results
        }, f, indent=2)

    print(f"\nDetailed report saved to: {report_file}")

    # Return exit code
    return 0 if results.failed == 0 else 1


if __name__ == "__main__":
    exit(main())
