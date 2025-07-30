#!/usr/bin/env python3
"""
Standalone test script for stock scanner with proxy functionality
Tests the proxy integration without requiring database connection
"""

import os
import sys
import time
import random
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from proxy_manager import ProxyManager

def patch_yfinance_proxy(proxy):
    """Patch yfinance to use proxy"""
    if not proxy:
        return
        
    try:
        session = requests.Session()
        session.proxies = {
            'http': proxy,
            'https': proxy
        }
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        yfinance.shared._requests = session
    except Exception as e:
        print(f"[PROXY ERROR] Failed to set proxy {proxy}: {e}")

def test_stock_with_proxy(symbol, ticker_number, proxy_manager):
    """Test a single stock with proxy"""
    try:
        # Get proxy for this ticker
        proxy = None
        if proxy_manager:
            proxy = proxy_manager.get_proxy_for_ticker(ticker_number)
            if proxy and ticker_number <= 3:  # Show proxy info for first 3 tickers
                print(f"[PROXY] {symbol}: Using proxy {proxy}")
        
        patch_yfinance_proxy(proxy)
        
        # Minimal delay
        time.sleep(random.uniform(0.01, 0.02))
        
        # Test multiple approaches
        ticker_obj = yf.Ticker(symbol)
        info = None
        hist = None
        current_price = None
        
        # Approach 1: Try basic info
        try:
            info = ticker_obj.info
        except:
            pass
        
        # Approach 2: Try historical data
        for period in ["1d", "5d"]:
            try:
                hist = ticker_obj.history(period=period, timeout=8)
                if hist is not None and not hist.empty and len(hist) > 0:
                    current_price = hist['Close'].iloc[-1]
                    if current_price is not None and not pd.isna(current_price):
                        break
            except Exception as e:
                continue
        
        # Approach 3: Try current price from info
        if current_price is None and info:
            try:
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            except:
                pass
        
        # Determine success
        has_data = hist is not None and not hist.empty
        has_info = info and isinstance(info, dict) and len(info) > 3
        has_price = current_price is not None and not pd.isna(current_price)
        
        if has_data or has_info or has_price:
            change_str = "N/A"
            if has_data and len(hist) > 1:
                try:
                    prev_price = hist['Close'].iloc[-2]
                    if not pd.isna(prev_price) and prev_price > 0 and current_price:
                        price_change = current_price - prev_price
                        change_percent = (price_change / prev_price) * 100
                        change_str = f"{change_percent:+.2f}%"
                except:
                    pass
            
            print(f"[SUCCESS] {symbol}: ${current_price:.2f} ({change_str}) - Proxy: {proxy}")
            return True
        else:
            print(f"[FAILED] {symbol}: No data found - Proxy: {proxy}")
            return False
            
    except Exception as e:
        err_str = str(e).lower()
        if 'too many requests' in err_str or 'rate limit' in err_str or '401' in err_str:
            if proxy and proxy_manager:
                proxy_manager.mark_proxy_failed(proxy)
            print(f"[RATE LIMIT] {symbol}: {e}")
            time.sleep(random.uniform(0.5, 1.0))
        elif any(x in err_str for x in ['no data found', 'delisted', 'not found', '404']):
            print(f"[DELISTED] {symbol}: {e}")
        else:
            print(f"[ERROR] {symbol}: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 PROXY STOCK SCANNER TEST")
    print("=" * 50)
    
    # Test symbols
    test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'ADBE', 'CRM']
    
    # Initialize proxy manager
    print("\n📡 Initializing proxy manager...")
    try:
        proxy_manager = ProxyManager()
        stats = proxy_manager.get_proxy_stats()
        print(f"✅ Proxy manager ready: {stats}")
    except Exception as e:
        print(f"❌ Proxy manager failed: {e}")
        proxy_manager = None
    
    # Test connectivity
    print("\n🌐 Testing yfinance connectivity...")
    try:
        test_ticker = yf.Ticker("AAPL")
        test_info = test_ticker.info
        if test_info:
            print("✅ yfinance connectivity test passed")
        else:
            print("⚠️  yfinance connectivity test failed")
    except Exception as e:
        print(f"❌ yfinance connectivity error: {e}")
    
    # Test stocks with proxies
    print(f"\n📊 Testing {len(test_symbols)} stocks with proxy rotation...")
    print("=" * 50)
    
    start_time = time.time()
    successful = 0
    failed = 0
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_symbol = {}
        for i, symbol in enumerate(test_symbols, 1):
            future = executor.submit(test_stock_with_proxy, symbol, i, proxy_manager)
            future_to_symbol[future] = symbol
        
        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                result = future.result(timeout=10)
                if result:
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"[TIMEOUT] {symbol}: {e}")
                failed += 1
    
    elapsed = time.time() - start_time
    
    # Results
    print("\n" + "=" * 50)
    print("📈 TEST RESULTS")
    print("=" * 50)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️  Time: {elapsed:.2f}s")
    print(f"🚀 Rate: {len(test_symbols)/elapsed:.2f} symbols/sec")
    
    if proxy_manager:
        final_stats = proxy_manager.get_proxy_stats()
        print(f"🌐 Final proxy stats: {final_stats}")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    main()