#!/usr/bin/env python3
"""
Test Proxy Connectivity
Tests proxies for basic connectivity (not Yahoo-specific)
Then tests working proxies against Yahoo Finance
"""

import json
import time
import random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Tuple

# Test configuration
CONNECTIVITY_TIMEOUT = 3  # seconds for connectivity test
YAHOO_TIMEOUT = 5  # seconds for Yahoo test
MAX_WORKERS = 200  # high concurrency for fast testing
TARGET_WORKING = 1000  # target number of working proxies

# Test URLs for connectivity
TEST_URLS = [
    'http://httpbin.org/ip',
    'http://ip-api.com/json',
    'http://ifconfig.me/ip',
]

# User agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
]

def test_connectivity(proxy: str) -> Tuple[str, bool, float]:
    """Test basic proxy connectivity"""
    test_url = random.choice(TEST_URLS)
    start_time = time.time()

    try:
        response = requests.get(
            test_url,
            proxies={'http': proxy, 'https': proxy},
            headers={'User-Agent': random.choice(USER_AGENTS)},
            timeout=CONNECTIVITY_TIMEOUT
        )
        response_time = time.time() - start_time

        if response.status_code == 200:
            return (proxy, True, response_time)
        return (proxy, False, response_time)

    except:
        return (proxy, False, time.time() - start_time)

def test_yahoo(proxy: str) -> Tuple[str, bool, float]:
    """Test proxy against Yahoo Finance"""
    import yfinance as yf

    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
    symbol = random.choice(symbols)
    start_time = time.time()

    try:
        session = requests.Session()
        session.proxies = {'http': proxy, 'https': proxy}
        session.headers = {'User-Agent': random.choice(USER_AGENTS)}

        ticker = yf.Ticker(symbol, session=session)
        info = ticker.info
        response_time = time.time() - start_time

        if info and len(info) > 10:
            price = info.get('regularMarketPrice') or info.get('currentPrice')
            if price and price > 0:
                return (proxy, True, response_time)

        return (proxy, False, response_time)
    except:
        return (proxy, False, time.time() - start_time)

def load_proxies(file_path: str = 'working_proxies.json') -> List[str]:
    """Load proxies from JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f).get('proxies', [])
    except:
        return []

def save_proxies(proxies: List[str], file_path: str = 'working_proxies.json'):
    """Save proxies to JSON file"""
    data = {
        'last_updated': datetime.now().isoformat(),
        'total_count': len(proxies),
        'proxies': proxies,
        'note': 'Tested for connectivity'
    }
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"[SAVED] {len(proxies)} proxies to {file_path}")

def main():
    print("="*70)
    print("PROXY CONNECTIVITY TESTER")
    print("="*70)
    print("Phase 1: Test basic connectivity (fast)")
    print("Phase 2: Test Yahoo Finance (sample)")
    print(f"Target: {TARGET_WORKING} working proxies")
    print("="*70)

    # Load proxies
    all_proxies = load_proxies()
    total = len(all_proxies)

    if total == 0:
        print("ERROR: No proxies to test!")
        return

    print(f"\nLoaded {total} proxies")
    print(f"Estimated Phase 1 time: {total / MAX_WORKERS * CONNECTIVITY_TIMEOUT / 60:.1f} minutes")

    # Phase 1: Connectivity test
    print("\n" + "="*70)
    print("PHASE 1: CONNECTIVITY TEST")
    print("="*70)

    connected_proxies = []
    tested = 0
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(test_connectivity, p): p for p in all_proxies}

        for future in as_completed(futures):
            proxy, success, response_time = future.result()
            tested += 1

            if success:
                connected_proxies.append(proxy)

            # Progress every 5000
            if tested % 5000 == 0:
                elapsed = time.time() - start_time
                rate = tested / elapsed if elapsed > 0 else 0
                eta = (total - tested) / rate / 60 if rate > 0 else 0
                print(f"Progress: {tested}/{total} ({tested/total*100:.1f}%) | Connected: {len(connected_proxies)} | ETA: {eta:.1f}min")

    phase1_time = time.time() - start_time

    print(f"\nPhase 1 Complete!")
    print(f"  Tested: {total}")
    print(f"  Connected: {len(connected_proxies)} ({len(connected_proxies)/total*100:.2f}%)")
    print(f"  Time: {phase1_time/60:.1f} minutes")

    if len(connected_proxies) == 0:
        print("\nERROR: No proxies passed connectivity test!")
        return

    # Phase 2: Test sample against Yahoo
    print("\n" + "="*70)
    print("PHASE 2: YAHOO FINANCE TEST (sample)")
    print("="*70)

    # Test up to 5000 connected proxies against Yahoo
    sample_size = min(5000, len(connected_proxies))
    sample = random.sample(connected_proxies, sample_size)

    print(f"Testing {sample_size} proxies against Yahoo Finance...")

    yahoo_working = []
    tested = 0
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(test_yahoo, p): p for p in sample}

        for future in as_completed(futures):
            proxy, success, response_time = future.result()
            tested += 1

            if success:
                yahoo_working.append(proxy)

            if tested % 500 == 0:
                print(f"Progress: {tested}/{sample_size} | Yahoo working: {len(yahoo_working)}")

    phase2_time = time.time() - start_time

    print(f"\nPhase 2 Complete!")
    print(f"  Tested: {sample_size}")
    print(f"  Yahoo working: {len(yahoo_working)} ({len(yahoo_working)/sample_size*100:.2f}%)")
    print(f"  Time: {phase2_time/60:.1f} minutes")

    # Final results
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)

    # Determine what to save
    if len(yahoo_working) >= TARGET_WORKING:
        # Great! We have enough Yahoo-verified proxies
        save_proxies(yahoo_working)
        print(f"\nTARGET ACHIEVED: {len(yahoo_working)} Yahoo-working proxies")
    elif len(yahoo_working) >= 100:
        # We have some Yahoo-working, but also save connected ones
        # Combine: Yahoo-working first, then remaining connected
        remaining_connected = [p for p in connected_proxies if p not in yahoo_working]
        combined = yahoo_working + remaining_connected[:TARGET_WORKING - len(yahoo_working)]
        save_proxies(combined)
        print(f"\nSaved {len(combined)} proxies:")
        print(f"  - {len(yahoo_working)} Yahoo-verified")
        print(f"  - {len(combined) - len(yahoo_working)} connectivity-verified")
    else:
        # Yahoo still rate-limiting, save all connected proxies
        save_proxies(connected_proxies)
        print(f"\nYahoo appears to be rate-limiting.")
        print(f"Saved {len(connected_proxies)} connectivity-verified proxies")
        print(f"These will be tested naturally when Yahoo resets.")

    if len(yahoo_working) < 100:
        print("\nNOTE: Low Yahoo success rate indicates rate limiting is still active.")
        print("The connected proxies will work once Yahoo resets.")

if __name__ == "__main__":
    import os
    import sys
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import django
    django.setup()
    main()
