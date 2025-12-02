#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test known-good tickers to diagnose API issues"""

import yfinance as yf
import time

def test_ticker(symbol):
    """Test a single ticker"""
    print(f"\n{'='*50}")
    print(f"Testing {symbol}")
    print('='*50)

    start = time.time()

    try:
        ticker = yf.Ticker(symbol)

        # Try fast_info
        print(f"[*] Trying fast_info...")
        try:
            info = ticker.fast_info
            print(f"  Price: ${info.last_price}")
            print(f"  Volume: {info.last_volume:,}")
            print(f"  Market Cap: ${info.market_cap:,}" if info.market_cap else "  Market Cap: N/A")
            print(f"  [OK] fast_info successful")
            return True
        except Exception as e:
            print(f"  [FAIL] fast_info error: {e}")

        # Try info
        print(f"[*] Trying info...")
        try:
            info_data = ticker.info
            price = info_data.get('currentPrice') or info_data.get('regularMarketPrice')
            volume = info_data.get('volume')
            print(f"  Price: ${price}")
            print(f"  Volume: {volume:,}" if volume else "  Volume: N/A")
            print(f"  [OK] info successful")
            return True
        except Exception as e:
            print(f"  [FAIL] info error: {e}")

        print(f"  [FAIL] Both methods failed")
        return False

    except Exception as e:
        print(f"[ERROR] Failed to create ticker: {e}")
        return False
    finally:
        elapsed = time.time() - start
        print(f"Time: {elapsed:.2f}s")


if __name__ == "__main__":
    # Test known-good tickers
    test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META']

    print("="*50)
    print("TESTING KNOWN-GOOD TICKERS")
    print("="*50)

    successes = 0
    for symbol in test_tickers:
        if test_ticker(symbol):
            successes += 1

    print(f"\n{'='*50}")
    print(f"RESULTS: {successes}/{len(test_tickers)} successful")
    print(f"Success rate: {successes/len(test_tickers)*100:.1f}%")
    print('='*50)
