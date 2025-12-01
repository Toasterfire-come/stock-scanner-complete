#!/usr/bin/env python3
"""
Aggressive Proxy Fetcher - Target: 1000+ Working Proxies
Strategy: Fetch massive pool, don't test (add all), let ultra_fast script filter naturally
"""

import requests
import json
import time
from typing import List, Set
from datetime import datetime

# Proxy sources - expanded list
PROXY_SOURCES = [
    # ProxyScrape (largest source)
    'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
    'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=https&timeout=10000&country=all&ssl=all&anonymity=all',
    'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=10000&country=all',
    'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all',

    # Proxy-list.download
    'https://www.proxy-list.download/api/v1/get?type=http',
    'https://www.proxy-list.download/api/v1/get?type=https',
    'https://www.proxy-list.download/api/v1/get?type=socks4',
    'https://www.proxy-list.download/api/v1/get?type=socks5',

    # GitHub proxy lists (most reliable)
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
    'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
    'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt',
    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt',
    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt',
    'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
    'https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-Repo/master/proxy_list.txt',
    'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies.txt',
    'https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt',
    'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt',
    'https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/http.txt',
    'https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/https.txt',

    # Additional sources
    'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt',
    'https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt',
    'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt',
    'https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt',
    'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt',
    'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/https.txt',
    'https://raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt',
    'https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt',
    'https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/https.txt',
]

def fetch_proxies_from_source(url: str) -> Set[str]:
    """Fetch proxies from a single source"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Parse proxies
            proxies = set()
            for line in response.text.strip().split('\n'):
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                # Format: IP:PORT or http://IP:PORT
                if ':' in line:
                    # Clean up and standardize format
                    proxy = line.replace('http://', '').replace('https://', '')
                    # Validate basic format (IP:PORT)
                    parts = proxy.split(':')
                    if len(parts) == 2:
                        try:
                            # Validate port is a number
                            port = int(parts[1])
                            if 1 <= port <= 65535:
                                # Add as http://IP:PORT
                                proxies.add(f'http://{proxy}')
                        except ValueError:
                            continue

            print(f"[FETCH] OK {len(proxies)} from {url[:60]}...")
            return proxies
        else:
            print(f"[FETCH] FAIL HTTP {response.status_code} from {url[:60]}...")
            return set()
    except Exception as e:
        print(f"[FETCH] ERROR from {url[:60]}...: {str(e)[:50]}")
        return set()

def fetch_all_proxies() -> Set[str]:
    """Fetch proxies from all sources"""
    print("="*70)
    print("AGGRESSIVE PROXY FETCHER - TARGET: 1000+ PROXIES")
    print("="*70)
    print(f"\nFetching from {len(PROXY_SOURCES)} sources...")
    print("Strategy: Collect all, don't test, let ultra_fast script filter naturally")
    print()

    all_proxies = set()

    for i, source in enumerate(PROXY_SOURCES, 1):
        print(f"[{i}/{len(PROXY_SOURCES)}] ", end='')
        proxies = fetch_proxies_from_source(source)
        all_proxies.update(proxies)
        print(f"    Total unique so far: {len(all_proxies)}")

        # Small delay to avoid hammering sources
        time.sleep(0.5)

    return all_proxies

def load_existing_proxies(file_path: str = 'working_proxies.json') -> Set[str]:
    """Load existing proxy pool"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            existing = set(data.get('proxies', []))
            print(f"\n[EXISTING] Loaded {len(existing)} proxies from {file_path}")
            return existing
    except FileNotFoundError:
        print(f"\n[EXISTING] No existing proxy file found")
        return set()
    except Exception as e:
        print(f"\n[EXISTING] Error loading: {e}")
        return set()

def save_proxies(proxies: List[str], file_path: str = 'working_proxies.json'):
    """Save proxies to JSON file"""
    data = {
        'last_updated': datetime.now().isoformat(),
        'total_count': len(proxies),
        'proxies': proxies,
        'note': 'Untested proxy pool - will be filtered naturally by ultra_fast script'
    }

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n[SAVED] {len(proxies)} proxies to {file_path}")

def main():
    """Main execution"""
    start_time = time.time()

    # Load existing proxies
    existing = load_existing_proxies()

    # Fetch new proxies
    fetched = fetch_all_proxies()

    # Combine and deduplicate
    combined = existing.union(fetched)

    # Convert to list and save
    proxy_list = sorted(list(combined))

    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Existing proxies: {len(existing)}")
    print(f"Newly fetched: {len(fetched)}")
    print(f"New unique: {len(fetched - existing)}")
    print(f"Total unique: {len(combined)}")
    print(f"Time elapsed: {time.time() - start_time:.1f}s")
    print("="*70)

    # Save combined pool
    save_proxies(proxy_list)

    print("\nSUCCESS: Proxy pool updated successfully!")
    print(f"\nNOTE: These proxies are UNTESTED.")
    print("The ultra_fast_yfinance_v3.py script will:")
    print("  1. Try each proxy")
    print("  2. Track success/failure rates")
    print("  3. Auto-disable bad proxies")
    print("  4. Naturally filter to working proxies over time")
    print("\nThis approach is FASTER than testing 40k+ proxies upfront.")

    # Show target status
    if len(combined) >= 1000:
        print(f"\nTARGET ACHIEVED: {len(combined)} proxies (>= 1000)")
    else:
        print(f"\nTARGET NOT MET: {len(combined)} proxies (< 1000)")
        print(f"  Need {1000 - len(combined)} more proxies")
        print(f"  Consider:")
        print(f"    - Running this script again later")
        print(f"    - Adding more proxy sources")
        print(f"    - Using paid proxy services")

if __name__ == "__main__":
    main()
