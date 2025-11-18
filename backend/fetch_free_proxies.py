#!/usr/bin/env python3
"""
Free Proxy Fetcher

Fetches free proxies from multiple public sources and validates them.
Saves working proxies to working_proxies.json for use with the scanner.
"""

import requests
import json
import time
import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple

# Proxy sources
PROXY_SOURCES = [
    # Free Proxy List APIs
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
    "https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/http.txt",
]

def fetch_proxies_from_source(url: str) -> List[str]:
    """Fetch proxies from a single source"""
    proxies = []
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            text = response.text
            # Extract IP:PORT patterns
            pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}'
            matches = re.findall(pattern, text)
            proxies = [f"http://{m}" for m in matches]
            print(f"  [+] {url.split('/')[2]}: {len(proxies)} proxies")
    except Exception as e:
        print(f"  [-] {url.split('/')[2]}: Failed ({str(e)[:50]})")
    return proxies


def fetch_all_proxies() -> List[str]:
    """Fetch proxies from all sources"""
    print("Fetching proxies from free sources...")
    all_proxies = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_proxies_from_source, url): url for url in PROXY_SOURCES}
        for future in as_completed(futures):
            try:
                proxies = future.result()
                all_proxies.extend(proxies)
            except Exception:
                pass

    # Remove duplicates
    unique_proxies = list(set(all_proxies))
    print(f"\nTotal unique proxies fetched: {len(unique_proxies)}")
    return unique_proxies


def test_proxy(proxy: str, test_url: str = "http://ip-api.com/json", timeout: int = 10) -> Tuple[str, bool, float]:
    """Test if a proxy is working"""
    start = time.time()
    try:
        response = requests.get(
            test_url,
            proxies={"http": proxy, "https": proxy},
            timeout=timeout,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        elapsed = time.time() - start
        if response.status_code == 200:
            return (proxy, True, elapsed)
    except Exception:
        pass
    return (proxy, False, 0)


def test_proxy_yahoo(proxy: str, timeout: int = 10) -> Tuple[str, bool, float]:
    """Test if a proxy works with Yahoo Finance"""
    start = time.time()
    try:
        response = requests.get(
            "https://query1.finance.yahoo.com/v7/finance/quote?symbols=AAPL",
            proxies={"http": proxy, "https": proxy},
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        elapsed = time.time() - start
        if response.status_code == 200:
            return (proxy, True, elapsed)
    except Exception:
        pass
    return (proxy, False, 0)


def validate_proxies(proxies: List[str], max_workers: int = 100, test_yahoo: bool = False) -> List[Dict]:
    """Validate proxies in parallel"""
    print(f"\nValidating {len(proxies)} proxies...")
    working = []

    test_func = test_proxy_yahoo if test_yahoo else test_proxy

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(test_func, proxy): proxy for proxy in proxies}
        completed = 0

        for future in as_completed(futures):
            completed += 1
            if completed % 100 == 0:
                print(f"  Progress: {completed}/{len(proxies)} tested, {len(working)} working")

            try:
                proxy, is_working, response_time = future.result()
                if is_working:
                    working.append({
                        "proxy": proxy,
                        "response_time": round(response_time, 3)
                    })
            except Exception:
                pass

    # Sort by response time
    working.sort(key=lambda x: x["response_time"])

    print(f"\nWorking proxies: {len(working)}/{len(proxies)}")
    return working


def save_proxies(working_proxies: List[Dict], output_file: str = "working_proxies.json"):
    """Save working proxies to JSON file"""
    # Extract just the proxy strings for compatibility
    proxy_list = [p["proxy"] for p in working_proxies]

    output = {
        "proxies": proxy_list,
        "count": len(proxy_list),
        "updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "details": working_proxies[:50]  # Include timing for top 50
    }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved {len(proxy_list)} proxies to {output_file}")
    return output_file


def main():
    """Main function to fetch and validate free proxies"""
    import argparse

    parser = argparse.ArgumentParser(description='Fetch and validate free proxies')
    parser.add_argument('--test-yahoo', action='store_true', help='Test proxies against Yahoo Finance')
    parser.add_argument('--workers', type=int, default=100, help='Number of validation workers')
    parser.add_argument('--output', type=str, default='working_proxies.json', help='Output file')
    parser.add_argument('--limit', type=int, default=0, help='Limit number of proxies to test')
    args = parser.parse_args()

    # Fetch proxies
    all_proxies = fetch_all_proxies()

    if not all_proxies:
        print("No proxies fetched!")
        return 1

    # Limit if specified
    if args.limit > 0:
        all_proxies = all_proxies[:args.limit]
        print(f"Testing first {args.limit} proxies")

    # Validate proxies
    working = validate_proxies(all_proxies, max_workers=args.workers, test_yahoo=args.test_yahoo)

    if not working:
        print("No working proxies found!")
        return 1

    # Save to file
    output_path = os.path.join(os.path.dirname(__file__), args.output)
    save_proxies(working, output_path)

    # Print top 10
    print("\nTop 10 fastest proxies:")
    for i, p in enumerate(working[:10], 1):
        print(f"  {i}. {p['proxy']} ({p['response_time']}s)")

    return 0


if __name__ == '__main__':
    exit(main())
