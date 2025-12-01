#!/usr/bin/env python
"""
Fetch Fresh Free Proxies
Scrapes multiple free proxy sources and tests them for Yahoo Finance compatibility
"""

import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import random

# Multiple free proxy sources
PROXY_SOURCES = [
    'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
    'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=10000&country=all',
    'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all',
    'https://www.proxy-list.download/api/v1/get?type=http',
    'https://www.proxy-list.download/api/v1/get?type=https',
    'https://www.proxy-list.download/api/v1/get?type=socks4',
    'https://www.proxy-list.download/api/v1/get?type=socks5',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
    'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
    'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt',
    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt',
    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt',
]

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def fetch_proxies_from_source(url: str) -> List[str]:
    """Fetch proxies from a single source"""
    try:
        print(f"[FETCH] Fetching from {url[:60]}...")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            proxies = response.text.strip().split('\n')
            proxies = [p.strip() for p in proxies if p.strip() and ':' in p]
            print(f"[FETCH] Found {len(proxies)} proxies from source")
            return proxies
        else:
            print(f"[FETCH] Failed: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"[FETCH] Error: {str(e)[:50]}")
        return []

def test_proxy_for_yahoo(proxy: str) -> Dict:
    """Test if proxy works with Yahoo Finance"""
    try:
        # Format proxy for requests
        if proxy.startswith('socks4://') or proxy.startswith('socks5://'):
            proxy_dict = {'http': proxy, 'https': proxy}
        elif '://' in proxy:
            proxy_dict = {'http': proxy, 'https': proxy}
        else:
            # Assume HTTP if no protocol specified
            proxy_dict = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }

        # Test with Yahoo Finance API
        test_url = 'https://query1.finance.yahoo.com/v8/finance/chart/AAPL'

        start_time = time.time()
        response = requests.get(
            test_url,
            proxies=proxy_dict,
            timeout=5,
            headers={'User-Agent': USER_AGENT}
        )
        response_time = time.time() - start_time

        # Check if response is valid
        if response.status_code == 200 and 'chart' in response.text.lower():
            return {
                'proxy': proxy,
                'working': True,
                'response_time': response_time,
                'status_code': 200
            }
        else:
            return {
                'proxy': proxy,
                'working': False,
                'response_time': response_time,
                'status_code': response.status_code,
                'error': f'HTTP {response.status_code}'
            }

    except requests.exceptions.Timeout:
        return {'proxy': proxy, 'working': False, 'error': 'Timeout'}
    except requests.exceptions.ProxyError:
        return {'proxy': proxy, 'working': False, 'error': 'Proxy Error'}
    except requests.exceptions.ConnectionError:
        return {'proxy': proxy, 'working': False, 'error': 'Connection Error'}
    except Exception as e:
        return {'proxy': proxy, 'working': False, 'error': str(e)[:50]}

def main():
    """Main function to fetch and test proxies"""
    print("=" * 70)
    print("FETCHING FRESH FREE PROXIES")
    print("=" * 70)

    # Step 1: Fetch proxies from all sources
    print("\n[STEP 1] Fetching proxies from multiple sources...")
    all_proxies = set()

    for source_url in PROXY_SOURCES:
        proxies = fetch_proxies_from_source(source_url)
        all_proxies.update(proxies)
        time.sleep(0.5)  # Be nice to the free APIs

    print(f"\n[STEP 1] Total unique proxies collected: {len(all_proxies)}")

    # Step 2: Test proxies concurrently
    print(f"\n[STEP 2] Testing {len(all_proxies)} proxies with Yahoo Finance...")
    print("[STEP 2] This may take a few minutes...")

    working_proxies = []
    failed_count = 0

    # Test in batches with limited concurrency
    proxy_list = list(all_proxies)
    batch_size = 50
    max_workers = 20

    for i in range(0, len(proxy_list), batch_size):
        batch = proxy_list[i:i + batch_size]
        print(f"\n[TESTING] Batch {i//batch_size + 1}/{(len(proxy_list) + batch_size - 1)//batch_size} ({len(batch)} proxies)...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {executor.submit(test_proxy_for_yahoo, proxy): proxy for proxy in batch}

            for future in as_completed(future_to_proxy):
                result = future.result()
                if result['working']:
                    working_proxies.append(result['proxy'])
                    print(f"[OK] Working: {result['proxy']} ({result['response_time']:.2f}s)")
                else:
                    failed_count += 1

        print(f"[BATCH] Working so far: {len(working_proxies)}, Failed: {failed_count}")

        # Stop if we have enough working proxies
        if len(working_proxies) >= 1000:
            print(f"\n[INFO] Reached 1000 working proxies, stopping early...")
            break

    # Step 3: Save working proxies
    print(f"\n[STEP 3] Saving {len(working_proxies)} working proxies...")

    # Load existing proxies
    existing_proxies = []
    try:
        with open('working_proxies.json', 'r') as f:
            data = json.load(f)
            existing_proxies = data.get('proxies', [])
    except:
        pass

    # Combine with existing (remove duplicates)
    all_working = list(set(existing_proxies + working_proxies))

    # Save to file
    output_data = {
        'proxies': all_working,
        'total': len(all_working),
        'last_updated': time.strftime('%Y-%m-%d %H:%M:%S'),
        'sources': len(PROXY_SOURCES)
    }

    with open('working_proxies.json', 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n[SUCCESS] Saved {len(all_working)} total working proxies to working_proxies.json")
    print(f"[INFO] New proxies added: {len(working_proxies)}")
    print(f"[INFO] Existing proxies: {len(existing_proxies)}")

    # Summary
    print("\n" + "=" * 70)
    print("PROXY FETCH COMPLETE")
    print("=" * 70)
    print(f"Total proxies fetched: {len(all_proxies)}")
    print(f"Working proxies: {len(working_proxies)}")
    print(f"Failed proxies: {failed_count}")
    print(f"Success rate: {len(working_proxies)/len(all_proxies)*100:.1f}%")
    print(f"Total in database: {len(all_working)}")
    print("=" * 70)

if __name__ == '__main__':
    main()
