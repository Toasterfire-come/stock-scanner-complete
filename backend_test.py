#!/usr/bin/env python3
"""
Stock Scanner MVP Backend API Testing
Tests all 6 main features with their respective endpoints
"""
import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

class StockScannerAPITester:
    def __init__(self, base_url="https://toaster-stock-update.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.passed_tests = []
        
    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            self.passed_tests.append(f"✅ {name}")
            print(f"✅ {name} - PASSED")
        else:
            self.failed_tests.append(f"❌ {name}: {details}")
            print(f"❌ {name} - FAILED: {details}")
        
        if details:
            print(f"   Details: {details}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, timeout: int = 30) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            else:
                return False, {}, 0
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}
            
            return response.status_code == 200, response_data, response.status_code
        
        except requests.exceptions.Timeout:
            return False, {"error": "Request timeout"}, 0
        except requests.exceptions.ConnectionError:
            return False, {"error": "Connection error"}, 0
        except Exception as e:
            return False, {"error": str(e)}, 0
    
    def test_ai_backtester_features(self):
        """Test Feature 1: AI Backtester with Groq Integration"""
        print("\n🤖 Testing AI Backtester Features...")
        
        # Test 1: AI Status
        success, data, status = self.make_request('GET', 'backtesting/ai-status/')
        if success and data.get('success'):
            ai_available = data.get('ai_available', False)
            self.log_test("AI Status Check", True, f"AI Available: {ai_available}")
        else:
            self.log_test("AI Status Check", False, f"Status: {status}, Data: {data}")
        
        # Test 2: AI Strategy Understanding
        strategy_text = "Buy when RSI is below 30 and sell when RSI is above 70 with 5% stop loss"
        success, data, status = self.make_request('POST', 'backtesting/understand/', {
            "strategy_text": strategy_text,
            "category": "swing_trading"
        })
        
        if success and data.get('success'):
            understanding = data.get('understanding', {})
            self.log_test("AI Strategy Understanding", True, f"Confidence: {understanding.get('confidence', 'N/A')}")
        else:
            self.log_test("AI Strategy Understanding", False, f"Status: {status}, Error: {data.get('error', 'Unknown')}")
        
        # Test 3: AI Chat
        success, data, status = self.make_request('POST', 'backtesting/chat/', {
            "message": "I want to create a simple RSI strategy",
            "conversation_history": [],
            "category": "swing_trading"
        })
        
        if success and data.get('success'):
            response = data.get('response', '')
            self.log_test("AI Chat", True, f"Response length: {len(response)} chars")
        else:
            self.log_test("AI Chat", False, f"Status: {status}, Error: {data.get('error', 'Unknown')}")
    
    def test_enhanced_screener_features(self):
        """Test Feature 2: Enhanced Screener with ALL fields"""
        print("\n🔍 Testing Enhanced Screener Features...")
        
        # Test 1: Get Filter Fields
        success, data, status = self.make_request('GET', 'screener/fields/')
        if success and data.get('success'):
            fields_data = data.get('data', {})
            total_fields = fields_data.get('total_fields', 0)
            self.log_test("Screener Fields", total_fields >= 50, f"Total fields: {total_fields}")
        else:
            self.log_test("Screener Fields", False, f"Status: {status}, Error: {data.get('error', 'Unknown')}")
        
        # Test 2: Get Presets
        success, data, status = self.make_request('GET', 'screener/presets/')
        if success and data.get('success'):
            presets = data.get('data', {}).get('presets', [])
            self.log_test("Screener Presets", len(presets) > 0, f"Presets count: {len(presets)}")
        else:
            self.log_test("Screener Presets", False, f"Status: {status}, Error: {data.get('error', 'Unknown')}")
        
        # Test 3: Advanced Filter
        success, data, status = self.make_request('POST', 'screener/filter/', {
            "filters": [
                {"field": "market_cap", "operator": "gte", "value": 1000000000},
                {"field": "pe_ratio", "operator": "lte", "value": 25}
            ],
            "sort_by": "market_cap",
            "sort_order": "desc",
            "page": 1,
            "page_size": 10
        })
        
        if success and data.get('success'):
            results = data.get('data', {}).get('results', [])
            self.log_test("Advanced Filter", True, f"Results count: {len(results)}")
        else:
            self.log_test("Advanced Filter", False, f"Status: {status}, Error: {data.get('error', 'Unknown')}")
    
    def test_fast_charting_features(self):
        """Test Feature 3: Fast Charting with Quick Updates"""
        print("\n📈 Testing Fast Charting Features...")
        
        test_ticker = "AAPL"
        
        # Test 1: Fast Quote
        success, data, status = self.make_request('GET', f'chart/{test_ticker}/quote/')
        if success and data.get('success'):
            quote_data = data.get('data', {})
            price = quote_data.get('price')
            self.log_test("Fast Quote", price is not None, f"Price: ${price}")
        else:
            self.log_test("Fast Quote", False, f"Status: {status}, Error: {data.get('error', 'Unknown')}")
        
        # Test 2: Intraday Data
        success, data, status = self.make_request('GET', f'chart/{test_ticker}/intraday/?interval=5m&period=1d')
        if success and data.get('success'):
            chart_data = data.get('data', {}).get('data', [])
            self.log_test("Intraday Chart", len(chart_data) > 0, f"Data points: {len(chart_data)}")
        else:
            self.log_test("Intraday Chart", False, f"Status: {status}, Error: {data.get('error', 'Unknown')}")
        
        # Test 3: Latest Candle
        success, data, status = self.make_request('GET', f'chart/{test_ticker}/latest/?interval=5m')
        if success and data.get('success'):
            candle = data.get('data', {}).get('candle', {})
            self.log_test("Latest Candle", 'close' in candle, f"Close price: {candle.get('close')}")
        else:
            self.log_test("Latest Candle", False, f"Status: {status}, Error: {data.get('error', 'Unknown')}")
        
        # Test 4: Full Chart with Indicators
        success, data, status = self.make_request('GET', f'chart/{test_ticker}/full/?period=1mo&indicators=sma_20,rsi')
        if success and data.get('success'):
            chart_data = data.get('data', {})
            candles = chart_data.get('candles', [])
            indicators = chart_data.get('indicators', {})
            self.log_test("Full Chart", len(candles) > 0 and len(indicators) > 0, 
                         f"Candles: {len(candles)}, Indicators: {list(indicators.keys())}")
        else:
            self.log_test("Full Chart", False, f"Status: {status}, Error: {data.get('error', 'Unknown')}")
        
        # Test 5: Batch Quotes
        success, data, status = self.make_request('POST', 'chart/batch-quotes/', {
            "symbols": ["AAPL", "MSFT", "GOOGL"]
        })
        
        if success and data.get('success'):
            quotes = data.get('data', {}).get('quotes', {})
            self.log_test("Batch Quotes", len(quotes) >= 2, f"Quotes received: {len(quotes)}")
        else:
            self.log_test("Batch Quotes", False, f"Status: {status}, Error: {data.get('error', 'Unknown')}")
    
    def test_valuation_display_features(self):
        """Test Feature 4: Aesthetic Valuation Display"""
        print("\n💰 Testing Valuation Display Features...")
        
        test_ticker = "AAPL"
        
        # Test 1: Valuation Display
        success, data, status = self.make_request('GET', f'valuation/{test_ticker}/display/')
        if success and data.get('success'):
            valuation_data = data.get('data', {})
            fair_values = valuation_data.get('fair_values', {})
            current_price = valuation_data.get('current_price')
            self.log_test("Valuation Display", current_price is not None, 
                         f"Price: ${current_price}, Fair values: {len(fair_values)}")
        else:
            self.log_test("Valuation Display", False, f"Status: {status}, Error: {data.get('error', 'Unknown')}")
    
    def test_stock_grouping_features(self):
        """Test Feature 5: Stock Grouping"""
        print("\n👥 Testing Stock Grouping Features...")
        
        # Test 1: Create Stock Group
        success, data, status = self.make_request('POST', 'groups/create/', {
            "name": "Tech Giants Test",
            "symbols": ["AAPL", "MSFT", "GOOGL"]
        })
        
        group_id = None
        if success and data.get('success'):
            group = data.get('group', {})
            group_id = group.get('id')
            stocks_count = group.get('count', 0)
            self.log_test("Create Stock Group", group_id is not None, 
                         f"Group ID: {group_id}, Stocks: {stocks_count}")
        else:
            self.log_test("Create Stock Group", False, f"Status: {status}, Error: {data.get('error', 'Unknown')}")
        
        # Test 2: Get Stock Group (if created successfully)
        if group_id:
            success, data, status = self.make_request('GET', f'groups/{group_id}/')
            if success and data.get('success'):
                group = data.get('group', {})
                metrics = group.get('metrics', {})
                self.log_test("Get Stock Group", len(metrics) > 0, f"Metrics available: {len(metrics)}")
            else:
                self.log_test("Get Stock Group", False, f"Status: {status}, Error: {data.get('error', 'Unknown')}")
    
    def test_comparison_features(self):
        """Test Feature 6: Stock/Group Comparison"""
        print("\n⚖️ Testing Comparison Features...")
        
        # Test 1: Compare Stocks
        success, data, status = self.make_request('POST', 'compare/stocks/', {
            "symbols": ["AAPL", "MSFT", "GOOGL"],
            "metrics": ["pe_ratio", "roe", "valuation_score"]
        })
        
        if success and data.get('success'):
            comparison_data = data.get('data', {})
            comparison = comparison_data.get('comparison', [])
            stocks = comparison_data.get('stocks', {})
            self.log_test("Compare Stocks", len(comparison) > 0 and len(stocks) > 0, 
                         f"Metrics: {len(comparison)}, Stocks: {len(stocks)}")
        else:
            self.log_test("Compare Stocks", False, f"Status: {status}, Error: {data.get('error', 'Unknown')}")
        
        # Test 2: Comparison Chart
        success, data, status = self.make_request('GET', 'compare/chart/?symbols=AAPL,MSFT&period=1mo&normalize=true')
        if success and data.get('success'):
            chart_data = data.get('data', {})
            chart = chart_data.get('chart', [])
            returns = chart_data.get('returns', {})
            self.log_test("Comparison Chart", len(chart) > 0, 
                         f"Chart points: {len(chart)}, Returns: {returns}")
        else:
            self.log_test("Comparison Chart", False, f"Status: {status}, Error: {data.get('error', 'Unknown')}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Stock Scanner MVP Backend API Tests")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test all 6 MVP features
        self.test_ai_backtester_features()
        self.test_enhanced_screener_features()
        self.test_fast_charting_features()
        self.test_valuation_display_features()
        self.test_stock_grouping_features()
        self.test_comparison_features()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for failure in self.failed_tests:
                print(f"  {failure}")
        
        if self.passed_tests:
            print(f"\n✅ PASSED TESTS ({len(self.passed_tests)}):")
            for success in self.passed_tests[:5]:  # Show first 5
                print(f"  {success}")
            if len(self.passed_tests) > 5:
                print(f"  ... and {len(self.passed_tests) - 5} more")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = StockScannerAPITester()
    success = tester.run_all_tests()
    
    # Return appropriate exit code
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())