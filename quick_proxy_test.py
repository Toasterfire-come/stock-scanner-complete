#!/usr/bin/env python3
"""
Quick proxy test - tests a few symbols to verify proxy functionality
"""

import time
import random
import yfinance as yf
import pandas as pd
import requests
from proxy_manager import ProxyManager

def test_single_proxy(symbol, proxy):
    """Test a single symbol with a specific proxy"""
    try:
        # Set up proxy session
        session = requests.Session()
        session.proxies = {
            'http': proxy,
            'https': proxy
        }
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Patch yfinance
        yfinance.shared._requests = session
        
        # Get data
        ticker_obj = yf.Ticker(symbol)
        
        # Try to get info
        info = None
        try:
            info = ticker_obj.info
        except:
            pass
        
        # Try to get historical data
        hist = None
        try:
            hist = ticker_obj.history(period="1d", timeout=5)
        except:
            pass
        
        # Check if we got meaningful data
        has_info = info and isinstance(info, dict) and len(info) > 3
        has_hist = hist is not None and not hist.empty
        
        if has_info or has_hist:
            current_price = None
            if has_hist and len(hist) > 0:
                current_price = hist['Close'].iloc[-1]
            elif has_info:
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            if current_price and not pd.isna(current_price):
                print(f"✅ {symbol}: ${current_price:.2f} via {proxy}")
                return True
        
        print(f"❌ {symbol}: No valid data via {proxy}")
        return False
        
    except Exception as e:
        print(f"❌ {symbol}: Error via {proxy} - {str(e)[:50]}")
        return False

def main():
    print("🔍 QUICK PROXY TEST")
    print("=" * 40)
    
    # Test symbols
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    
    # Initialize proxy manager
    print("\n📡 Loading proxies...")
    try:
        proxy_manager = ProxyManager()
        stats = proxy_manager.get_proxy_stats()
        print(f"✅ Loaded {stats['total_working']} proxies")
    except Exception as e:
        print(f"❌ Proxy manager failed: {e}")
        return
    
    # Test each symbol with different proxies
    print(f"\n🧪 Testing {len(symbols)} symbols...")
    successful = 0
    total_tests = 0
    
    for i, symbol in enumerate(symbols):
        # Get a proxy for this symbol
        proxy = proxy_manager.get_proxy_for_ticker(i + 1)
        if proxy:
            total_tests += 1
            if test_single_proxy(symbol, proxy):
                successful += 1
            time.sleep(0.1)  # Small delay
    
    # Results
    print(f"\n📊 Results: {successful}/{total_tests} successful ({successful/total_tests*100:.1f}%)")
    
    # Test without proxy for comparison
    print(f"\n🌐 Testing without proxy...")
    try:
        yfinance.shared._requests = requests.Session()
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        if info:
            print("✅ Direct connection works")
        else:
            print("❌ Direct connection failed")
    except Exception as e:
        print(f"❌ Direct connection error: {str(e)[:50]}")

if __name__ == "__main__":
    main()