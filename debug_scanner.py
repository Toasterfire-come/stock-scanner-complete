#!/usr/bin/env python3
"""
Debug version of standalone stock scanner
"""

import time
import yfinance as yf
from proxy_manager import ProxyManager

def main():
    print("DEBUG SCANNER")
    print("=" * 30)
    
    print("Step 1: Testing imports...")
    print("✓ Imports successful")
    
    print("\nStep 2: Testing proxy manager...")
    try:
        proxy_manager = ProxyManager()
        stats = proxy_manager.get_proxy_stats()
        print(f"✓ Proxy manager loaded: {stats['total_working']} proxies")
    except Exception as e:
        print(f"✗ Proxy manager failed: {e}")
        return
    
    print("\nStep 3: Testing yfinance import...")
    try:
        print("✓ yfinance imported successfully")
    except Exception as e:
        print(f"✗ yfinance import failed: {e}")
        return
    
    print("\nStep 4: Testing basic yfinance call...")
    try:
        print("  Creating ticker object...")
        ticker = yf.Ticker("AAPL")
        print("  ✓ Ticker object created")
        
        print("  Getting info...")
        info = ticker.info
        print("  ✓ Info retrieved")
        
        if info:
            print(f"  ✓ AAPL price: ${info.get('currentPrice', 'N/A')}")
        else:
            print("  ⚠ No info returned")
            
    except Exception as e:
        print(f"✗ yfinance test failed: {e}")
        return
    
    print("\nStep 5: Testing proxy with yfinance...")
    try:
        proxy = proxy_manager.get_proxy_for_ticker(1)
        print(f"  Got proxy: {proxy}")
        
        if proxy:
            import requests
            session = requests.Session()
            session.proxies = {
                'http': proxy,
                'https': proxy
            }
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            print("  Setting yfinance session...")
            yfinance.shared._requests = session
            print("  ✓ Session set")
            
            print("  Testing with proxy...")
            ticker2 = yf.Ticker("MSFT")
            info2 = ticker2.info
            print("  ✓ Proxy test successful")
            
    except Exception as e:
        print(f"✗ Proxy test failed: {e}")
    
    print("\nDEBUG COMPLETED!")

if __name__ == "__main__":
    main()