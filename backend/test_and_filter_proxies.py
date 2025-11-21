#!/usr/bin/env python3
"""
Test and Filter Proxies
Tests all proxies against Yahoo Finance and keeps only working ones
Target: 1000+ working proxies
"""

import os
import sys
import json
import time
import random
import requests
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Set, Tuple

# Django setup for using the models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

# Test configuration
TEST_TIMEOUT = 5  # seconds per proxy test
MAX_WORKERS = 100  # concurrent tests
TEST_SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']  # Rotate through these

# User agents for testing
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

def test_proxy(proxy: str, symbol: str = None) -> Tuple[str, bool, float]:
    """
    Test a single proxy against Yahoo Finance
    Returns: (proxy, success, response_time)
    """
    if symbol is None:
        symbol = random.choice(TEST_SYMBOLS)

    start_time = time.time()

    try:
        # Create session with proxy
        session = requests.Session()
        session.proxies = {'http': proxy, 'https': proxy}
        session.headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

        # Test with yfinance
        ticker = yf.Ticker(symbol, session=session)
        info = ticker.info

        response_time = time.time() - start_time

        # Validate response
        if info and len(info) > 10:
            price = info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose')
            if price and price > 0:
                return (proxy, True, response_time)

        return (proxy, False, response_time)

    except Exception as e:
        response_time = time.time() - start_time
        return (proxy, False, response_time)

def load_proxies(file_path: str = 'working_proxies.json') -> List[str]:
    """Load proxies from JSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data.get('proxies', [])
    except Exception as e:
        print(f"Error loading proxies: {e}")
        return []

def save_working_proxies(proxies: List[str], file_path: str = 'working_proxies.json'):
    """Save working proxies to JSON file"""
    data = {
        'last_updated': datetime.now().isoformat(),
        'total_count': len(proxies),
        'proxies': proxies,
        'note': 'Tested and verified working with Yahoo Finance'
    }

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n[SAVED] {len(proxies)} working proxies to {file_path}")

def main():
    """Main execution"""
    print("="*70)
    print("PROXY TESTER AND FILTER")
    print("="*70)
    print("Testing all proxies against Yahoo Finance...")
    print(f"Test timeout: {TEST_TIMEOUT}s per proxy")
    print(f"Concurrent tests: {MAX_WORKERS}")
    print("="*70)

    # Load all proxies
    all_proxies = load_proxies()
    total = len(all_proxies)

    if total == 0:
        print("ERROR: No proxies to test!")
        return

    print(f"\nLoaded {total} proxies to test")
    print(f"Estimated time: {(total / MAX_WORKERS * TEST_TIMEOUT / 60):.1f} minutes")
    print("\nStarting tests...\n")

    # Track results
    working_proxies = []
    failed_count = 0
    tested_count = 0
    start_time = time.time()

    # Test in batches for progress reporting
    batch_size = 500

    for batch_start in range(0, total, batch_size):
        batch_end = min(batch_start + batch_size, total)
        batch = all_proxies[batch_start:batch_end]
        batch_num = (batch_start // batch_size) + 1
        total_batches = (total + batch_size - 1) // batch_size

        print(f"[BATCH {batch_num}/{total_batches}] Testing {len(batch)} proxies...")

        batch_working = []
        batch_failed = 0

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(test_proxy, proxy): proxy for proxy in batch}

            for future in as_completed(futures):
                proxy, success, response_time = future.result()
                tested_count += 1

                if success:
                    batch_working.append(proxy)
                    working_proxies.append(proxy)
                else:
                    batch_failed += 1
                    failed_count += 1

        # Batch progress
        elapsed = time.time() - start_time
        rate = tested_count / elapsed if elapsed > 0 else 0
        eta = (total - tested_count) / rate / 60 if rate > 0 else 0

        print(f"  Working: {len(batch_working)} | Failed: {batch_failed}")
        print(f"  Total working so far: {len(working_proxies)}")
        print(f"  Progress: {tested_count}/{total} ({tested_count/total*100:.1f}%)")
        print(f"  Rate: {rate:.1f} proxies/sec | ETA: {eta:.1f} min")
        print()

        # Save intermediate results every 5000 proxies
        if tested_count % 5000 < batch_size and tested_count > 0:
            save_working_proxies(working_proxies, 'working_proxies_partial.json')
            print(f"  [CHECKPOINT] Saved {len(working_proxies)} working proxies")
            print()

    # Final results
    elapsed = time.time() - start_time

    print("="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"Total tested: {total}")
    print(f"Working: {len(working_proxies)} ({len(working_proxies)/total*100:.2f}%)")
    print(f"Failed: {failed_count}")
    print(f"Time elapsed: {elapsed/60:.1f} minutes")
    print(f"Rate: {total/elapsed:.1f} proxies/sec")
    print("="*70)

    # Save final results
    if len(working_proxies) >= 1000:
        save_working_proxies(working_proxies)
        print(f"\nTARGET ACHIEVED: {len(working_proxies)} working proxies (>= 1000)")
    elif len(working_proxies) > 0:
        save_working_proxies(working_proxies)
        print(f"\nTARGET NOT MET: {len(working_proxies)} working proxies (< 1000)")
        print(f"Need {1000 - len(working_proxies)} more working proxies")
        print("Consider:")
        print("  - Running fetch_1000_proxies.py to get more proxies")
        print("  - Running this test again later (proxy availability varies)")
    else:
        print("\nWARNING: No working proxies found!")
        print("This may be due to Yahoo Finance rate limiting.")
        print("Try again later when rate limits reset.")

    # Clean up partial file
    try:
        os.remove('working_proxies_partial.json')
    except:
        pass

    return len(working_proxies)

if __name__ == "__main__":
    main()
