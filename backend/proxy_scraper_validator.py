#!/usr/bin/env python
"""
Comprehensive Proxy Scraper and Validator for YFinance
Fetches proxies from multiple free sources and validates them against yfinance
"""

import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple
from datetime import datetime
import random

# Import yfinance with error handling
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("[WARNING] yfinance not installed. Install with: pip install yfinance>=0.2.25")
    print("[WARNING] Script will exit if yfinance is not available.")

# Comprehensive list of free proxy sources
PROXY_SOURCES = [
    # ProxyScrape API
    'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
    'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=10000&country=all',
    'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all',

    # Proxy-List Download API
    'https://www.proxy-list.download/api/v1/get?type=http',
    'https://www.proxy-list.download/api/v1/get?type=https',
    'https://www.proxy-list.download/api/v1/get?type=socks4',
    'https://www.proxy-list.download/api/v1/get?type=socks5',

    # GitHub proxy lists
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
    'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
    'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt',
    'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt',
    'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt',
    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt',
    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt',
    'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt',
    'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt',
    'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt',
    'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt',
    'https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt',
    'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt',
    'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt',
    'https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/http.txt',
    'https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/https.txt',
    'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
    'https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-Repo/master/proxy_list.txt',

    # Additional sources
    'https://raw.githubusercontent.com/almroot/proxylist/master/list.txt',
    'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt',
    'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt',
    'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/https.txt',
    'https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/http.txt',
]

# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
]

# Test stocks for validation
TEST_STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'WMT']


def fetch_proxies_from_source(url: str) -> List[str]:
    """Fetch proxies from a single source"""
    try:
        print(f"[FETCH] {url[:70]}...")
        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            proxies = response.text.strip().split('\n')
            # Clean and filter proxies
            proxies = [p.strip() for p in proxies if p.strip() and ':' in p and not p.startswith('#')]
            print(f"[FETCH] ✓ Found {len(proxies)} proxies")
            return proxies
        else:
            print(f"[FETCH] ✗ HTTP {response.status_code}")
            return []

    except requests.exceptions.Timeout:
        print(f"[FETCH] ✗ Timeout")
        return []
    except Exception as e:
        print(f"[FETCH] ✗ Error: {str(e)[:40]}")
        return []


def test_proxy_with_yfinance(proxy: str, timeout: int = 8) -> Dict:
    """
    Test proxy with yfinance library
    Returns dict with proxy info and test results
    """
    try:
        # Format proxy for requests/yfinance
        if not proxy.startswith(('http://', 'https://', 'socks4://', 'socks5://')):
            # Try as HTTP first
            proxy_url = f'http://{proxy}'
        else:
            proxy_url = proxy

        # Create session with proxy
        session = requests.Session()
        session.proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        session.headers.update({'User-Agent': random.choice(USER_AGENTS)})

        # Test with random stock
        test_symbol = random.choice(TEST_STOCKS)
        start_time = time.time()

        # Use yfinance with the proxy session
        ticker = yf.Ticker(test_symbol, session=session)

        # Try to get info (this will use the proxy)
        info = ticker.info
        response_time = time.time() - start_time

        # Validate we got real data
        if info and len(info) > 5:
            # Check for key fields that indicate success
            has_price = info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose')
            has_name = info.get('longName') or info.get('shortName')

            if has_price or has_name:
                return {
                    'proxy': proxy,
                    'working': True,
                    'response_time': round(response_time, 2),
                    'test_symbol': test_symbol,
                    'status': 'SUCCESS'
                }

        return {
            'proxy': proxy,
            'working': False,
            'response_time': round(response_time, 2),
            'status': 'INVALID_DATA'
        }

    except requests.exceptions.Timeout:
        return {
            'proxy': proxy,
            'working': False,
            'status': 'TIMEOUT'
        }
    except requests.exceptions.ProxyError:
        return {
            'proxy': proxy,
            'working': False,
            'status': 'PROXY_ERROR'
        }
    except requests.exceptions.ConnectionError:
        return {
            'proxy': proxy,
            'working': False,
            'status': 'CONNECTION_ERROR'
        }
    except Exception as e:
        return {
            'proxy': proxy,
            'working': False,
            'status': f'ERROR: {str(e)[:30]}'
        }


def save_working_proxies(proxies: List[str], filename: str = 'yfinance_working_proxies.json'):
    """Save working proxies to JSON file"""

    # Load existing proxies if file exists
    existing_proxies = []
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            existing_proxies = data.get('proxies', [])
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[WARNING] Could not load existing proxies: {e}")

    # Combine and deduplicate
    all_proxies = list(set(existing_proxies + proxies))

    # Create output data
    output_data = {
        'proxies': all_proxies,
        'total_count': len(all_proxies),
        'new_proxies_added': len(proxies),
        'existing_proxies': len(existing_proxies),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'validation_method': 'yfinance',
        'note': 'These proxies have been validated to work with yfinance library'
    }

    # Save to file
    with open(filename, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n[SAVE] Saved to {filename}")
    print(f"[SAVE] Total proxies: {len(all_proxies)}")
    print(f"[SAVE] New proxies added: {len(proxies)}")

    # Also save as simple text file for easy use
    txt_filename = filename.replace('.json', '.txt')
    with open(txt_filename, 'w') as f:
        for proxy in all_proxies:
            f.write(f"{proxy}\n")

    print(f"[SAVE] Also saved to {txt_filename} (plain text)")


def main():
    """Main function to scrape and validate proxies"""
    # Check if yfinance is available
    if not YFINANCE_AVAILABLE:
        print("=" * 80)
        print("ERROR: yfinance is not installed!")
        print("=" * 80)
        print("Please install yfinance first:")
        print("  pip install yfinance>=0.2.25")
        print("\nOr install all requirements:")
        print("  pip install -r requirements.txt")
        print("=" * 80)
        return

    print("=" * 80)
    print("PROXY SCRAPER & VALIDATOR FOR YFINANCE")
    print("=" * 80)
    print(f"Sources to check: {len(PROXY_SOURCES)}")
    print(f"Validation method: yfinance library")
    print("=" * 80)

    # Step 1: Fetch proxies from all sources
    print("\n[STEP 1] FETCHING PROXIES FROM SOURCES")
    print("-" * 80)

    all_proxies = set()
    for i, source_url in enumerate(PROXY_SOURCES, 1):
        print(f"[{i}/{len(PROXY_SOURCES)}] ", end="")
        proxies = fetch_proxies_from_source(source_url)
        all_proxies.update(proxies)
        time.sleep(0.3)  # Be respectful to free APIs

    total_proxies = len(all_proxies)
    print(f"\n[STEP 1] ✓ Collected {total_proxies} unique proxies")

    if total_proxies == 0:
        print("[ERROR] No proxies collected! Exiting.")
        return

    # Step 2: Test proxies with yfinance
    print("\n[STEP 2] VALIDATING PROXIES WITH YFINANCE")
    print("-" * 80)
    print(f"Testing {total_proxies} proxies (this may take a while)...")
    print("Using concurrent testing with 30 workers")
    print("-" * 80)

    working_proxies = []
    failed_count = 0
    tested_count = 0

    proxy_list = list(all_proxies)
    start_time = time.time()

    # Test in batches
    batch_size = 100
    max_workers = 30

    for batch_num in range(0, len(proxy_list), batch_size):
        batch = proxy_list[batch_num:batch_num + batch_size]
        batch_number = batch_num // batch_size + 1
        total_batches = (len(proxy_list) + batch_size - 1) // batch_size

        print(f"\n[BATCH {batch_number}/{total_batches}] Testing {len(batch)} proxies...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {
                executor.submit(test_proxy_with_yfinance, proxy): proxy
                for proxy in batch
            }

            for future in as_completed(future_to_proxy):
                result = future.result()
                tested_count += 1

                if result['working']:
                    working_proxies.append(result['proxy'])
                    print(f"  ✓ [{len(working_proxies)}] {result['proxy']} "
                          f"({result['response_time']}s, {result['test_symbol']})")
                else:
                    failed_count += 1

        # Progress update
        elapsed = time.time() - start_time
        rate = tested_count / elapsed if elapsed > 0 else 0
        remaining = total_proxies - tested_count
        eta_seconds = remaining / rate if rate > 0 else 0

        print(f"\n[PROGRESS] Tested: {tested_count}/{total_proxies} "
              f"({tested_count/total_proxies*100:.1f}%)")
        print(f"[PROGRESS] Working: {len(working_proxies)}, "
              f"Failed: {failed_count}, "
              f"Rate: {rate:.1f}/s, "
              f"ETA: {eta_seconds/60:.1f}min")

        # Stop early if we have enough working proxies
        if len(working_proxies) >= 1000:
            print(f"\n[INFO] Reached 1000 working proxies! Stopping early.")
            break

    total_time = time.time() - start_time

    # Step 3: Save results
    print("\n[STEP 3] SAVING RESULTS")
    print("-" * 80)

    if len(working_proxies) > 0:
        save_working_proxies(working_proxies)
    else:
        print("[WARNING] No working proxies found!")

    # Final summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total proxies fetched:    {total_proxies}")
    print(f"Total proxies tested:     {tested_count}")
    print(f"Working proxies:          {len(working_proxies)}")
    print(f"Failed proxies:           {failed_count}")
    print(f"Success rate:             {len(working_proxies)/tested_count*100:.2f}%")
    print(f"Total time:               {total_time/60:.2f} minutes")
    print(f"Average test rate:        {tested_count/total_time:.1f} proxies/second")
    print("=" * 80)

    if len(working_proxies) > 0:
        print(f"\n✓ Success! {len(working_proxies)} working proxies saved.")
        print("  Files created:")
        print("    - yfinance_working_proxies.json (detailed)")
        print("    - yfinance_working_proxies.txt (plain text)")
    else:
        print("\n✗ No working proxies found. This could mean:")
        print("  - Yahoo Finance is rate limiting")
        print("  - All proxy sources are down")
        print("  - Network connectivity issues")
        print("  Try running again later.")

    print("=" * 80)


if __name__ == '__main__':
    main()
