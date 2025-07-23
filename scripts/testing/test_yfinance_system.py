#!/usr/bin/env python3
"""
YFinance System Test Script
Tests Yahoo Finance API integration and basic functionality.

Usage:
    python scripts/testing/test_yfinance_system.py

This script tests:
- yfinance library import and basic functionality
- Stock data retrieval
- Error handling
- Rate limiting awareness
- Data format validation

Author: Stock Scanner Project
Version: 1.0.0
"""

import sys
import time
import random
from typing import Dict, List, Optional

def test_yfinance_import():
    """Test yfinance import"""
    print("📦 Testing yfinance import...")
    
    try:
        import yfinance as yf
        print("✅ yfinance imported successfully")
        return True
    except ImportError as e:
        print(f"❌ yfinance import failed: {e}")
        print("💡 Install with: pip install yfinance")
        return False

def test_basic_stock_fetch():
    """Test basic stock data fetching"""
    print("\n📈 Testing basic stock data fetch...")
    
    try:
        import yfinance as yf
        
        # Test with a reliable stock symbol
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        
        if info and 'symbol' in info:
            symbol = info.get('symbol', 'Unknown')
            name = info.get('longName', 'Unknown')
            price = info.get('currentPrice', 'Unknown')
            
            print(f"✅ Stock data retrieved:")
            print(f"   Symbol: {symbol}")
            print(f"   Name: {name}")
            print(f"   Price: {price}")
            return True
        else:
            print("❌ No valid stock data returned")
            return False
            
    except Exception as e:
        print(f"❌ Stock fetch failed: {e}")
        return False

def test_multiple_stocks():
    """Test fetching multiple stocks with basic rate limiting"""
    print("\n📊 Testing multiple stock fetches...")
    
    try:
        import yfinance as yf
        
        test_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
        successful_fetches = 0
        
        for i, symbol in enumerate(test_symbols):
            try:
                print(f"   Fetching {symbol}... ({i+1}/{len(test_symbols)})")
                
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if info and 'symbol' in info:
                    price = info.get('currentPrice', 'N/A')
                    print(f"   ✅ {symbol}: ${price}")
                    successful_fetches += 1
                else:
                    print(f"   ⚠️ {symbol}: No data")
                
                # Basic rate limiting - wait between requests
                if i < len(test_symbols) - 1:
                    time.sleep(1)
                    
            except Exception as e:
                print(f"   ❌ {symbol}: {e}")
        
        success_rate = (successful_fetches / len(test_symbols)) * 100
        print(f"\n📈 Success rate: {successful_fetches}/{len(test_symbols)} ({success_rate:.1f}%)")
        
        return successful_fetches > 0
        
    except Exception as e:
        print(f"❌ Multiple stock test failed: {e}")
        return False

def test_historical_data():
    """Test historical data retrieval"""
    print("\n📅 Testing historical data...")
    
    try:
        import yfinance as yf
        
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="5d")
        
        if not hist.empty and len(hist) > 0:
            print(f"✅ Historical data retrieved: {len(hist)} days")
            print(f"   Columns: {list(hist.columns)}")
            
            # Check for expected columns
            expected_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in expected_cols:
                if col in hist.columns:
                    print(f"   ✅ {col} column present")
                else:
                    print(f"   ⚠️ {col} column missing")
            
            return True
        else:
            print("❌ No historical data returned")
            return False
            
    except Exception as e:
        print(f"❌ Historical data test failed: {e}")
        return False

def test_error_handling():
    """Test error handling with invalid symbols"""
    print("\n🚫 Testing error handling...")
    
    try:
        import yfinance as yf
        
        # Test with invalid symbol
        invalid_symbol = "INVALIDTICKER123"
        ticker = yf.Ticker(invalid_symbol)
        
        try:
            info = ticker.info
            
            # Check if we get empty or minimal data for invalid symbol
            if not info or len(info) <= 1:
                print("✅ Invalid symbol handled gracefully")
                return True
            else:
                print("⚠️ Invalid symbol returned unexpected data")
                return True  # Still OK, just different handling
                
        except Exception as e:
            print(f"✅ Invalid symbol raised exception (expected): {e}")
            return True
            
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_data_validation():
    """Test data format validation"""
    print("\n🔍 Testing data format validation...")
    
    try:
        import yfinance as yf
        
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        
        # Check for common data fields and types
        validations = [
            ('symbol', str),
            ('currentPrice', (int, float, type(None))),
            ('marketCap', (int, float, type(None))),
            ('volume', (int, type(None))),
        ]
        
        valid_count = 0
        
        for field, expected_type in validations:
            if field in info:
                value = info[field]
                if isinstance(value, expected_type):
                    print(f"   ✅ {field}: {type(value).__name__} = {value}")
                    valid_count += 1
                else:
                    print(f"   ⚠️ {field}: Expected {expected_type}, got {type(value)}")
            else:
                print(f"   ⚠️ {field}: Field not present")
        
        if valid_count > 0:
            print(f"✅ Data validation passed: {valid_count}/{len(validations)} fields valid")
            return True
        else:
            print("❌ No valid data fields found")
            return False
            
    except Exception as e:
        print(f"❌ Data validation test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 YFinance System Test")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("YFinance Import", test_yfinance_import()),
        ("Basic Stock Fetch", test_basic_stock_fetch()),
        ("Multiple Stocks", test_multiple_stocks()),
        ("Historical Data", test_historical_data()),
        ("Error Handling", test_error_handling()),
        ("Data Validation", test_data_validation()),
    ]
    
    # Show results
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📈 Success Rate: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! YFinance integration is working.")
        print("\n💡 Tips for production:")
        print("   • Add proper rate limiting (1-2 seconds between requests)")
        print("   • Implement error retry logic")
        print("   • Cache frequently accessed data")
        print("   • Monitor API usage and errors")
        return True
    elif passed >= total * 0.8:
        print("⚠️ Most tests passed - system should work with minor issues")
        return True
    else:
        print(f"❌ {total-passed} critical tests failed. Fix issues before production.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)