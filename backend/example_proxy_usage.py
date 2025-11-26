#!/usr/bin/env python
"""
Example: How to use the scraped proxies with yfinance
"""

import json
import random
import requests

def load_proxies(filename='yfinance_working_proxies.json'):
    """Load working proxies from JSON file"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            return data.get('proxies', [])
    except FileNotFoundError:
        print(f"[ERROR] {filename} not found!")
        print("Run proxy_scraper_validator.py first to generate working proxies.")
        return []
    except Exception as e:
        print(f"[ERROR] Failed to load proxies: {e}")
        return []


def get_stock_with_proxy(symbol, proxy):
    """Fetch stock data using a specific proxy"""
    try:
        import yfinance as yf

        # Create session with proxy
        session = requests.Session()
        session.proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Fetch stock data
        ticker = yf.Ticker(symbol, session=session)
        info = ticker.info

        # Extract key information
        return {
            'symbol': symbol,
            'proxy': proxy,
            'success': True,
            'name': info.get('longName', 'N/A'),
            'price': info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose', 'N/A'),
            'currency': info.get('currency', 'USD')
        }

    except Exception as e:
        return {
            'symbol': symbol,
            'proxy': proxy,
            'success': False,
            'error': str(e)
        }


def main():
    print("=" * 70)
    print("EXAMPLE: Using Scraped Proxies with YFinance")
    print("=" * 70)

    # Load proxies
    print("\n[1] Loading proxies...")
    proxies = load_proxies()

    if not proxies:
        print("No proxies available. Exiting.")
        return

    print(f"[1] ✓ Loaded {len(proxies)} working proxies")

    # Test with a few stocks
    test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']

    print(f"\n[2] Testing with {len(test_symbols)} stocks...")
    print("-" * 70)

    for symbol in test_symbols:
        # Use a random proxy
        proxy = random.choice(proxies)

        print(f"\n[{symbol}] Fetching with proxy {proxy}...")
        result = get_stock_with_proxy(symbol, proxy)

        if result['success']:
            print(f"[{symbol}] ✓ Success!")
            print(f"  Name:  {result['name']}")
            print(f"  Price: {result['price']} {result['currency']}")
        else:
            print(f"[{symbol}] ✗ Failed: {result.get('error', 'Unknown error')}")

    print("\n" + "=" * 70)
    print("EXAMPLE COMPLETE")
    print("=" * 70)
    print("\nTips:")
    print("- Rotate proxies to avoid rate limiting")
    print("- Keep a pool of working proxies and rotate through them")
    print("- Re-run proxy_scraper_validator.py periodically to refresh")
    print("- Some proxies may stop working - have fallback logic")
    print("=" * 70)


if __name__ == '__main__':
    main()
