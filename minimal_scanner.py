#!/usr/bin/env python3
"""
Minimal stock scanner - skips potential hanging points
"""

import time
import yfinance as yf
import pandas as pd
from proxy_manager import ProxyManager

def process_single_stock(symbol, proxy=None):
    """Process a single stock with minimal overhead"""
    try:
        # Set proxy if provided
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
            yfinance.shared._requests = session
        
        # Get data with timeout
        ticker = yf.Ticker(symbol)
        
        # Try to get current price
        try:
            hist = ticker.history(period="1d", timeout=5)
            if hist is not None and not hist.empty:
                price = hist['Close'].iloc[-1]
                if price and not pd.isna(price):
                    print(f"SUCCESS: {symbol} = ${price:.2f}")
                    return {'symbol': symbol, 'price': price, 'proxy': proxy}
        except:
            pass
        
        # Fallback to info
        try:
            info = ticker.info
            if info:
                price = info.get('currentPrice') or info.get('regularMarketPrice')
                if price:
                    print(f"SUCCESS: {symbol} = ${price:.2f}")
                    return {'symbol': symbol, 'price': price, 'proxy': proxy}
        except:
            pass
        
        print(f"FAILED: {symbol}")
        return None
        
    except Exception as e:
        print(f"ERROR: {symbol} - {str(e)[:50]}")
        return None

def main():
    print("MINIMAL STOCK SCANNER")
    print("=" * 30)
    
    # Test symbols
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    
    print(f"Processing {len(symbols)} symbols...")
    
    # Load proxies
    try:
        proxy_manager = ProxyManager()
        stats = proxy_manager.get_proxy_stats()
        print(f"Loaded {stats['total_working']} proxies")
        use_proxies = True
    except:
        print("No proxies available")
        use_proxies = False
        proxy_manager = None
    
    # Process each symbol
    results = []
    for i, symbol in enumerate(symbols):
        print(f"\nProcessing {i+1}/{len(symbols)}: {symbol}")
        
        proxy = None
        if use_proxies and proxy_manager:
            proxy = proxy_manager.get_proxy_for_ticker(i + 1)
            if proxy:
                print(f"  Using proxy: {proxy}")
        
        result = process_single_stock(symbol, proxy)
        if result:
            results.append(result)
        
        time.sleep(0.1)  # Small delay
    
    # Summary
    print(f"\nSUMMARY:")
    print(f"Successful: {len(results)}/{len(symbols)}")
    for result in results:
        print(f"  {result['symbol']}: ${result['price']:.2f}")

if __name__ == "__main__":
    main()