#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Script
Tests all API endpoints against api.tradescanpro.com
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Tuple

# Configuration
API_BASE_URL = "https://api.tradescanpro.com"
TEST_EMAIL = "carter.kiefer2010@outlook.com"
TEST_PASSWORD = ""  # Will prompt if not set

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class APITester:
    def __init__(self, base_url: str, email: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.auth_token = None
        self.results = []

    def print_header(self, text: str):
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

    def print_test(self, name: str, status: str, details: str = ""):
        if status == "PASS":
            icon = f"{Colors.GREEN}✓{Colors.RESET}"
            status_text = f"{Colors.GREEN}PASS{Colors.RESET}"
        elif status == "FAIL":
            icon = f"{Colors.RED}✗{Colors.RESET}"
            status_text = f"{Colors.RED}FAIL{Colors.RESET}"
        else:
            icon = f"{Colors.YELLOW}•{Colors.RESET}"
            status_text = f"{Colors.YELLOW}SKIP{Colors.RESET}"

        print(f"{icon} {name:<50} [{status_text}]")
        if details:
            print(f"   {Colors.YELLOW}{details}{Colors.RESET}")

    def test_endpoint(self, name: str, method: str, url: str, **kwargs) -> Tuple[bool, Dict]:
        """Test a single endpoint and return (success, response_data)"""
        full_url = f"{self.base_url}{url}" if not url.startswith('http') else url

        try:
            if method.upper() == "GET":
                response = self.session.get(full_url, timeout=10, **kwargs)
            elif method.upper() == "POST":
                response = self.session.post(full_url, timeout=10, **kwargs)
            elif method.upper() == "PUT":
                response = self.session.put(full_url, timeout=10, **kwargs)
            elif method.upper() == "DELETE":
                response = self.session.delete(full_url, timeout=10, **kwargs)
            else:
                return False, {"error": f"Unsupported method: {method}"}

            success = 200 <= response.status_code < 400

            try:
                data = response.json()
            except:
                data = {"response_text": response.text[:200]}

            result = {
                "name": name,
                "method": method,
                "url": full_url,
                "status_code": response.status_code,
                "success": success,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }

            self.results.append(result)

            if success:
                self.print_test(name, "PASS", f"Status: {response.status_code}")
            else:
                self.print_test(name, "FAIL", f"Status: {response.status_code} - {data.get('error', '')}")

            return success, data

        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            self.print_test(name, "FAIL", f"Connection error: {error_msg}")

            result = {
                "name": name,
                "method": method,
                "url": full_url,
                "status_code": 0,
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
            self.results.append(result)

            return False, {"error": error_msg}

    def test_health_check(self):
        """Test health check endpoint"""
        self.print_header("HEALTH CHECK")
        self.test_endpoint(
            "Health Check",
            "GET",
            "/health/"
        )

    def test_authentication(self):
        """Test authentication endpoints"""
        self.print_header("AUTHENTICATION TESTS")

        # Test login
        success, data = self.test_endpoint(
            "User Login",
            "POST",
            "/api/auth/login/",
            json={"email": self.email, "password": self.password}
        )

        if success and 'token' in data:
            self.auth_token = data['token']
            self.session.headers.update({'Authorization': f'Token {self.auth_token}'})
            print(f"   {Colors.GREEN}Authenticated successfully{Colors.RESET}")
        elif success and 'access' in data:
            self.auth_token = data['access']
            self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
            print(f"   {Colors.GREEN}Authenticated successfully (JWT){Colors.RESET}")

        # Test token verification
        if self.auth_token:
            self.test_endpoint(
                "Verify Auth Token",
                "GET",
                "/api/auth/user/"
            )

    def test_stock_endpoints(self):
        """Test stock data endpoints"""
        self.print_header("STOCK DATA ENDPOINTS")

        # List stocks
        self.test_endpoint(
            "List Stocks",
            "GET",
            "/api/stocks/?limit=10"
        )

        # Search stocks
        self.test_endpoint(
            "Search Stocks (AAPL)",
            "GET",
            "/api/stocks/search/?q=AAPL"
        )

        # Search with multiple results
        self.test_endpoint(
            "Search Stocks (Multiple Results)",
            "GET",
            "/api/stocks/search/?q=tech"
        )

        # Stock detail - major tickers
        for ticker in ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]:
            self.test_endpoint(
                f"Stock Detail ({ticker})",
                "GET",
                f"/api/stocks/{ticker}/"
            )

        # Top gainers
        self.test_endpoint(
            "Top Gainers",
            "GET",
            "/api/stocks/top-gainers/"
        )

        # Top gainers with limit
        self.test_endpoint(
            "Top Gainers (Limit 20)",
            "GET",
            "/api/stocks/top-gainers/?limit=20"
        )

        # Top losers
        self.test_endpoint(
            "Top Losers",
            "GET",
            "/api/stocks/top-losers/"
        )

        # Top losers with limit
        self.test_endpoint(
            "Top Losers (Limit 20)",
            "GET",
            "/api/stocks/top-losers/?limit=20"
        )

        # Most active
        self.test_endpoint(
            "Most Active",
            "GET",
            "/api/stocks/most-active/"
        )

        # Most active with limit
        self.test_endpoint(
            "Most Active (Limit 50)",
            "GET",
            "/api/stocks/most-active/?limit=50"
        )

        # Historical data
        self.test_endpoint(
            "Historical Data (AAPL)",
            "GET",
            "/api/stocks/AAPL/history/?period=1mo"
        )

        # Intraday data
        self.test_endpoint(
            "Intraday Data (AAPL)",
            "GET",
            "/api/stocks/AAPL/intraday/"
        )

    def test_day_trading_endpoints(self):
        """Test day trading specific endpoints"""
        self.print_header("DAY TRADING ENDPOINTS")

        # Intraday charts - 1min, 5min, 15min
        for interval in ["1min", "5min", "15min", "30min", "1hour"]:
            self.test_endpoint(
                f"Intraday Chart ({interval})",
                "GET",
                f"/api/stocks/AAPL/chart/?interval={interval}"
            )

        # Volume profile
        self.test_endpoint(
            "Volume Profile (AAPL)",
            "GET",
            "/api/stocks/AAPL/volume-profile/"
        )

        # Level 2 data (if available)
        self.test_endpoint(
            "Market Depth/Level 2",
            "GET",
            "/api/stocks/AAPL/market-depth/"
        )

        # Real-time quotes
        self.test_endpoint(
            "Real-time Quote (AAPL)",
            "GET",
            "/api/stocks/AAPL/quote/"
        )

        # Day trading screeners
        self.test_endpoint(
            "High Volume Movers",
            "GET",
            "/api/market/screener/?min_volume=1000000&order_by=volume"
        )

        self.test_endpoint(
            "Volatile Stocks (Day Trading)",
            "GET",
            "/api/market/screener/?min_price_change_percent=5"
        )

        self.test_endpoint(
            "Gap Up Stocks",
            "GET",
            "/api/market/screener/?gap_up=true"
        )

        self.test_endpoint(
            "Gap Down Stocks",
            "GET",
            "/api/market/screener/?gap_down=true"
        )

        # Technical indicators for day trading
        self.test_endpoint(
            "RSI Indicator (AAPL)",
            "GET",
            "/api/stocks/AAPL/indicators/rsi/"
        )

        self.test_endpoint(
            "MACD Indicator (AAPL)",
            "GET",
            "/api/stocks/AAPL/indicators/macd/"
        )

        self.test_endpoint(
            "Bollinger Bands (AAPL)",
            "GET",
            "/api/stocks/AAPL/indicators/bollinger/"
        )

        # Market sentiment
        self.test_endpoint(
            "Market Sentiment",
            "GET",
            "/api/market/sentiment/"
        )

    def test_long_term_trading_endpoints(self):
        """Test long-term trading specific endpoints"""
        self.print_header("LONG-TERM TRADING ENDPOINTS")

        # Fundamental data
        self.test_endpoint(
            "Fundamentals (AAPL)",
            "GET",
            "/api/stocks/AAPL/fundamentals/"
        )

        self.test_endpoint(
            "Income Statement (AAPL)",
            "GET",
            "/api/stocks/AAPL/financials/income/"
        )

        self.test_endpoint(
            "Balance Sheet (AAPL)",
            "GET",
            "/api/stocks/AAPL/financials/balance/"
        )

        self.test_endpoint(
            "Cash Flow (AAPL)",
            "GET",
            "/api/stocks/AAPL/financials/cashflow/"
        )

        # Valuation metrics
        self.test_endpoint(
            "Valuation Metrics (AAPL)",
            "GET",
            "/api/stocks/AAPL/valuation/"
        )

        self.test_endpoint(
            "PE Ratio History (AAPL)",
            "GET",
            "/api/stocks/AAPL/valuation/pe-history/"
        )

        # Dividend data
        self.test_endpoint(
            "Dividend History (AAPL)",
            "GET",
            "/api/stocks/AAPL/dividends/"
        )

        # Long-term screeners
        self.test_endpoint(
            "Dividend Growth Stocks",
            "GET",
            "/api/market/screener/?min_dividend_yield=2&dividend_growth=true"
        )

        self.test_endpoint(
            "Value Stocks (Low PE)",
            "GET",
            "/api/market/screener/?max_pe=15&min_market_cap=1000000000"
        )

        self.test_endpoint(
            "Growth Stocks",
            "GET",
            "/api/market/screener/?min_revenue_growth=20"
        )

        self.test_endpoint(
            "Blue Chip Stocks",
            "GET",
            "/api/market/screener/?min_market_cap=100000000000"
        )

        # Earnings data
        self.test_endpoint(
            "Earnings History (AAPL)",
            "GET",
            "/api/stocks/AAPL/earnings/"
        )

        self.test_endpoint(
            "Upcoming Earnings",
            "GET",
            "/api/market/earnings/upcoming/"
        )

        # Analyst ratings
        self.test_endpoint(
            "Analyst Ratings (AAPL)",
            "GET",
            "/api/stocks/AAPL/analyst-ratings/"
        )

        # Insider trading
        self.test_endpoint(
            "Insider Transactions (AAPL)",
            "GET",
            "/api/stocks/AAPL/insider-trades/"
        )

        # News and sentiment (long-term)
        self.test_endpoint(
            "Company News (AAPL)",
            "GET",
            "/api/stocks/AAPL/news/"
        )

    def test_backtesting_endpoints(self):
        """Test backtesting endpoints"""
        self.print_header("BACKTESTING ENDPOINTS")

        # List strategies
        self.test_endpoint(
            "List Strategies",
            "GET",
            "/api/backtesting/strategies/"
        )

        # Day trading backtests
        if self.auth_token:
            # Day trading strategy
            self.test_endpoint(
                "Backtest Day Trading Strategy",
                "POST",
                "/api/backtesting/run/",
                json={
                    "ticker": "AAPL",
                    "strategy": "momentum",
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-01",
                    "timeframe": "intraday",
                    "initial_capital": 10000
                }
            )

            # Swing trading strategy
            self.test_endpoint(
                "Backtest Swing Trading Strategy",
                "POST",
                "/api/backtesting/run/",
                json={
                    "ticker": "MSFT",
                    "strategy": "mean_reversion",
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-01",
                    "timeframe": "daily",
                    "initial_capital": 10000
                }
            )

            # Long-term buy and hold
            self.test_endpoint(
                "Backtest Long-term Strategy",
                "POST",
                "/api/backtesting/run/",
                json={
                    "ticker": "SPY",
                    "strategy": "buy_and_hold",
                    "start_date": "2020-01-01",
                    "end_date": "2024-12-01",
                    "timeframe": "weekly",
                    "initial_capital": 10000
                }
            )

            # AI-assisted backtest
            self.test_endpoint(
                "AI Backtest Analysis",
                "POST",
                "/api/backtesting/ai-analyze/",
                json={
                    "ticker": "NVDA",
                    "strategy": "momentum",
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-01"
                }
            )

        # Get backtest results
        if self.auth_token:
            self.test_endpoint(
                "Get Backtest Results",
                "GET",
                "/api/backtesting/results/"
            )

    def test_billing_endpoints(self):
        """Test billing endpoints"""
        self.print_header("BILLING & SUBSCRIPTION ENDPOINTS")

        # Get plans
        self.test_endpoint(
            "Get Subscription Plans",
            "GET",
            "/api/billing/plans/"
        )

        # Check subscription status (requires auth)
        if self.auth_token:
            self.test_endpoint(
                "Check Subscription Status",
                "GET",
                "/api/billing/subscription/"
            )

    def test_watchlist_endpoints(self):
        """Test watchlist and favorites endpoints"""
        self.print_header("WATCHLIST & FAVORITES")

        if self.auth_token:
            # Get watchlists
            self.test_endpoint(
                "Get Watchlists",
                "GET",
                "/api/watchlists/"
            )

            # Create watchlist
            self.test_endpoint(
                "Create Watchlist",
                "POST",
                "/api/watchlists/",
                json={"name": "Day Trading Favorites", "description": "My day trading picks"}
            )

            # Add stock to watchlist
            self.test_endpoint(
                "Add Stock to Watchlist",
                "POST",
                "/api/watchlists/1/add/",
                json={"ticker": "AAPL"}
            )

            # Get watchlist stocks
            self.test_endpoint(
                "Get Watchlist Stocks",
                "GET",
                "/api/watchlists/1/stocks/"
            )

            # Remove from watchlist
            self.test_endpoint(
                "Remove from Watchlist",
                "DELETE",
                "/api/watchlists/1/remove/AAPL/"
            )

    def test_alerts_endpoints(self):
        """Test price alerts and notifications"""
        self.print_header("ALERTS & NOTIFICATIONS")

        if self.auth_token:
            # Get alerts
            self.test_endpoint(
                "Get Price Alerts",
                "GET",
                "/api/alerts/"
            )

            # Create price alert
            self.test_endpoint(
                "Create Price Alert (Above)",
                "POST",
                "/api/alerts/",
                json={
                    "ticker": "AAPL",
                    "condition": "above",
                    "price": 200,
                    "notification_method": "email"
                }
            )

            # Create price alert (below)
            self.test_endpoint(
                "Create Price Alert (Below)",
                "POST",
                "/api/alerts/",
                json={
                    "ticker": "TSLA",
                    "condition": "below",
                    "price": 150,
                    "notification_method": "email"
                }
            )

            # Volume alert
            self.test_endpoint(
                "Create Volume Alert",
                "POST",
                "/api/alerts/",
                json={
                    "ticker": "NVDA",
                    "alert_type": "volume",
                    "threshold": 50000000
                }
            )

            # Delete alert
            self.test_endpoint(
                "Delete Alert",
                "DELETE",
                "/api/alerts/1/"
            )

    def test_education_endpoints(self):
        """Test education/learning endpoints"""
        self.print_header("EDUCATION & LEARNING")

        # List courses
        self.test_endpoint(
            "List Courses",
            "GET",
            "/api/education/courses/"
        )

        # Get course detail
        self.test_endpoint(
            "Course Detail",
            "GET",
            "/api/education/courses/1/"
        )

        # Get lessons
        self.test_endpoint(
            "Get Course Lessons",
            "GET",
            "/api/education/courses/1/lessons/"
        )

        # Glossary terms
        self.test_endpoint(
            "Trading Glossary",
            "GET",
            "/api/education/glossary/"
        )

        # Get specific term
        self.test_endpoint(
            "Glossary Term (Market Cap)",
            "GET",
            "/api/education/glossary/market-cap/"
        )

        if self.auth_token:
            # User progress
            self.test_endpoint(
                "Course Progress",
                "GET",
                "/api/education/progress/"
            )

            # Mark lesson complete
            self.test_endpoint(
                "Mark Lesson Complete",
                "POST",
                "/api/education/lessons/1/complete/"
            )

    def test_analytics_endpoints(self):
        """Test analytics and referral endpoints"""
        self.print_header("ANALYTICS & REFERRALS")

        if self.auth_token:
            # Partner analytics dashboard
            self.test_endpoint(
                "Partner Analytics Dashboard",
                "GET",
                "/api/partner-analytics/"
            )

            # Referral statistics
            self.test_endpoint(
                "Referral Statistics",
                "GET",
                "/api/partner-analytics/referrals/"
            )

            # Earnings data
            self.test_endpoint(
                "Referral Earnings",
                "GET",
                "/api/partner-analytics/earnings/"
            )

            # Conversion stats
            self.test_endpoint(
                "Conversion Statistics",
                "GET",
                "/api/partner-analytics/conversions/"
            )

            # Get referral link
            self.test_endpoint(
                "Get Referral Link",
                "GET",
                "/api/partner-analytics/referral-link/"
            )

    def test_market_data_endpoints(self):
        """Test market-wide data endpoints"""
        self.print_header("MARKET DATA & INDICES")

        # Market overview
        self.test_endpoint(
            "Market Overview",
            "GET",
            "/api/market/overview/"
        )

        # Major indices
        for index in ["SPY", "QQQ", "DIA", "IWM"]:
            self.test_endpoint(
                f"Index Data ({index})",
                "GET",
                f"/api/market/indices/{index}/"
            )

        # Sector performance
        self.test_endpoint(
            "Sector Performance",
            "GET",
            "/api/market/sectors/"
        )

        # Market movers
        self.test_endpoint(
            "Market Movers Summary",
            "GET",
            "/api/market/movers/"
        )

        # Pre-market data
        self.test_endpoint(
            "Pre-market Movers",
            "GET",
            "/api/market/pre-market/"
        )

        # After-hours data
        self.test_endpoint(
            "After-hours Movers",
            "GET",
            "/api/market/after-hours/"
        )

        # Market calendar
        self.test_endpoint(
            "Market Calendar",
            "GET",
            "/api/market/calendar/"
        )

        # IPO calendar
        self.test_endpoint(
            "IPO Calendar",
            "GET",
            "/api/market/ipos/"
        )

    def test_charting_endpoints(self):
        """Test charting endpoints - charts served by Stooq on frontend"""
        self.print_header("CHARTING DATA (Backend provides data only)")

        # Note: Actual charts are served by Stooq HTML5 on the frontend
        # Backend only provides data endpoints for technical indicators

        # All technical indicators
        indicators = ["sma", "ema", "rsi", "macd", "bollinger", "stochastic", "atr", "adx", "obv"]
        for indicator in indicators:
            self.test_endpoint(
                f"Indicator: {indicator.upper()}",
                "GET",
                f"/api/stocks/AAPL/indicators/{indicator}/"
            )

        # Custom indicator combinations
        self.test_endpoint(
            "Multi-indicator Analysis",
            "GET",
            "/api/stocks/AAPL/indicators/multi/?indicators=rsi,macd,bollinger"
        )

        # Pattern recognition
        self.test_endpoint(
            "Chart Pattern Recognition",
            "GET",
            "/api/stocks/AAPL/patterns/"
        )

        # Support and resistance levels
        self.test_endpoint(
            "Support/Resistance Levels",
            "GET",
            "/api/stocks/AAPL/levels/"
        )

    def test_api_root(self):
        """Test API root endpoint"""
        self.print_header("API ROOT")
        self.test_endpoint(
            "API Root Info",
            "GET",
            "/"
        )

    def generate_report(self):
        """Generate test report"""
        self.print_header("TEST SUMMARY")

        total = len(self.results)
        passed = sum(1 for r in self.results if r['success'])
        failed = total - passed

        print(f"Total Tests:  {total}")
        print(f"{Colors.GREEN}Passed:       {passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed:       {failed}{Colors.RESET}")
        print(f"Success Rate: {(passed/total*100):.1f}%")

        # Save detailed results
        report_file = f"api_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'summary': {
                    'total': total,
                    'passed': passed,
                    'failed': failed,
                    'success_rate': f"{(passed/total*100):.1f}%"
                },
                'tests': self.results
            }, f, indent=2)

        print(f"\n{Colors.BLUE}Detailed report saved to: {report_file}{Colors.RESET}\n")

        # Print failed tests
        if failed > 0:
            print(f"\n{Colors.RED}Failed Tests:{Colors.RESET}")
            for result in self.results:
                if not result['success']:
                    print(f"  - {result['name']}: {result.get('error', 'HTTP ' + str(result.get('status_code')))}")

    def run_all_tests(self):
        """Run all API tests - each test is isolated and won't stop on failure"""
        print(f"{Colors.BOLD}TradeScanPro Comprehensive API Testing Suite{Colors.RESET}")
        print(f"Target: {self.base_url}")
        print(f"Email: {self.email}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n{Colors.YELLOW}Note: Each test runs independently. Failures won't stop other tests.{Colors.RESET}")

        # Core API tests
        try:
            self.test_api_root()
        except Exception as e:
            print(f"{Colors.RED}API Root test suite failed: {e}{Colors.RESET}")

        try:
            self.test_health_check()
        except Exception as e:
            print(f"{Colors.RED}Health check test suite failed: {e}{Colors.RESET}")

        try:
            self.test_authentication()
        except Exception as e:
            print(f"{Colors.RED}Authentication test suite failed: {e}{Colors.RESET}")

        # Stock data tests
        try:
            self.test_stock_endpoints()
        except Exception as e:
            print(f"{Colors.RED}Stock endpoints test suite failed: {e}{Colors.RESET}")

        # Trading-specific tests
        try:
            self.test_day_trading_endpoints()
        except Exception as e:
            print(f"{Colors.RED}Day trading endpoints test suite failed: {e}{Colors.RESET}")

        try:
            self.test_long_term_trading_endpoints()
        except Exception as e:
            print(f"{Colors.RED}Long-term trading endpoints test suite failed: {e}{Colors.RESET}")

        # Charting and technical analysis
        try:
            self.test_charting_endpoints()
        except Exception as e:
            print(f"{Colors.RED}Charting endpoints test suite failed: {e}{Colors.RESET}")

        # Market data
        try:
            self.test_market_data_endpoints()
        except Exception as e:
            print(f"{Colors.RED}Market data endpoints test suite failed: {e}{Colors.RESET}")

        # Backtesting
        try:
            self.test_backtesting_endpoints()
        except Exception as e:
            print(f"{Colors.RED}Backtesting endpoints test suite failed: {e}{Colors.RESET}")

        # User features
        try:
            self.test_watchlist_endpoints()
        except Exception as e:
            print(f"{Colors.RED}Watchlist endpoints test suite failed: {e}{Colors.RESET}")

        try:
            self.test_alerts_endpoints()
        except Exception as e:
            print(f"{Colors.RED}Alerts endpoints test suite failed: {e}{Colors.RESET}")

        # Billing and subscriptions
        try:
            self.test_billing_endpoints()
        except Exception as e:
            print(f"{Colors.RED}Billing endpoints test suite failed: {e}{Colors.RESET}")

        # Analytics and referrals
        try:
            self.test_analytics_endpoints()
        except Exception as e:
            print(f"{Colors.RED}Analytics endpoints test suite failed: {e}{Colors.RESET}")

        # Education
        try:
            self.test_education_endpoints()
        except Exception as e:
            print(f"{Colors.RED}Education endpoints test suite failed: {e}{Colors.RESET}")

        self.generate_report()

def main():
    """Main entry point"""
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}TradeScanPro API Endpoint Testing{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")

    # Get password if not set
    password = TEST_PASSWORD
    if not password:
        import getpass
        password = getpass.getpass(f"Enter password for {TEST_EMAIL}: ")

    # Create tester and run
    tester = APITester(API_BASE_URL, TEST_EMAIL, password)
    tester.run_all_tests()

if __name__ == "__main__":
    main()
