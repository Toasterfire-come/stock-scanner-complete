#!/usr/bin/env python
"""
Quick Proxy Fetch - Fetch and test proxies quickly
"""

import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Quick proxy sources
PROXY_SOURCES = [
    'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
]

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

def fetch_proxies():
    """Fetch proxies from sources"""
    print("Fetching proxies from sources...")
    all_proxies = set()

    for url in PROXY_SOURCES:
        try:
            print(f"  Fetching from {url[:50]}...")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                proxies = response.text.strip().split('\n')
                proxies = [p.strip() for p in proxies if p.strip() and ':' in p]
                all_proxies.update(proxies)
                print(f"  Found {len(proxies)} proxies")
        except Exception as e:
            print(f"  Error: {str(e)[:30]}")

    return list(all_proxies)

def test_proxy(proxy):
    """Test proxy with Yahoo Finance"""
    try:
        proxy_dict = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
        response = requests.get(
            'https://query1.finance.yahoo.com/v8/finance/chart/AAPL',
            proxies=proxy_dict,
            timeout=5,
            headers={'User-Agent': USER_AGENT}
        )

        if response.status_code == 200 and 'chart' in response.text.lower():
            return {'proxy': proxy, 'working': True}
        return {'proxy': proxy, 'working': False}
    except:
        return {'proxy': proxy, 'working': False}

def main():
    print("=" * 70)
    print("QUICK PROXY FETCH")
    print("=" * 70)

    # Fetch proxies
    all_proxies = fetch_proxies()
    print(f"\nTotal proxies collected: {len(all_proxies)}")

    # Test up to 500 proxies
    test_count = min(500, len(all_proxies))
    print(f"\nTesting first {test_count} proxies...")

    working = []
    failed = 0

    # Test in batches
    batch_size = 50
    for i in range(0, test_count, batch_size):
        batch = all_proxies[i:i + batch_size]
        print(f"\nBatch {i//batch_size + 1}: Testing {len(batch)} proxies...")

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(test_proxy, p): p for p in batch}

            for future in as_completed(futures):
                result = future.result()
                if result['working']:
                    working.append(result['proxy'])
                    print(f"  [OK] {result['proxy']}")
                else:
                    failed += 1

        print(f"  Working: {len(working)}, Failed: {failed}")

        # Stop if we have enough
        if len(working) >= 100:
            print(f"\nGot {len(working)} working proxies, stopping...")
            break

    # Load existing and combine
    try:
        with open('working_proxies.json', 'r') as f:
            data = json.load(f)
            existing = data.get('proxies', [])
    except:
        existing = []

    # Combine
    all_working = list(set(existing + working))

    # Save
    output = {
        'proxies': all_working,
        'total': len(all_working),
        'last_updated': time.strftime('%Y-%m-%d %H:%M:%S'),
        'new_proxies_added': len(working)
    }

    with open('working_proxies.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)
    print(f"New working proxies: {len(working)}")
    print(f"Existing proxies: {len(existing)}")
    print(f"Total proxies: {len(all_working)}")
    print(f"Success rate: {len(working)/test_count*100:.1f}%")
    print("=" * 70)

if __name__ == '__main__':
    main()
