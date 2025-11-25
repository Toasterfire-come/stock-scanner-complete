#!/usr/bin/env python3
"""
Aggressive Proxy Fetcher & Tester
Pulls from multiple free proxy sources and tests them against Yahoo Finance
"""

import requests
import json
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Set
import random

# Comprehensive list of free proxy sources
PROXY_SOURCES = [
    # ProxyScrape - Large lists
    'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
    'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=US&ssl=all&anonymity=elite',
    'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=10000&country=all',
    'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all',

    # GitHub proxy lists (frequently updated)
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt',
    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt',
    'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
    'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
    'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt',
    'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt',
    'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt',
    'https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt',
    'https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt',
    'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt',
    'https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/http.txt',
    'https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/https.txt',

    # ProxyList Download
    'https://www.proxy-list.download/api/v1/get?type=http',
    'https://www.proxy-list.download/api/v1/get?type=https',
    'https://www.proxy-list.download/api/v1/get?type=socks4',
    'https://www.proxy-list.download/api/v1/get?type=socks5',

    # Geonode
    'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps',

    # FreeProxyList
    'https://free-proxy-list.net/',

    # SSL Proxies
    'https://www.sslproxies.org/',
]

# User agents for requests
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
]

# Test URLs
TEST_URLS = [
    'https://query1.finance.yahoo.com/v8/finance/chart/AAPL',
    'https://query2.finance.yahoo.com/v8/finance/chart/MSFT',
    'https://finance.yahoo.com',
]


class AggressiveProxyFetcher:
    """Aggressive proxy fetcher with comprehensive testing"""

    def __init__(self, target_count: int = 200):
        self.target_count = target_count
        self.all_proxies: Set[str] = set()
        self.working_proxies: List[Dict] = []
        self.tested_count = 0
        self.working_count = 0

    def fetch_all_sources(self) -> List[str]:
        """Fetch proxies from all sources concurrently"""
        print("=" * 80)
        print("AGGRESSIVE PROXY FETCHER")
        print("=" * 80)
        print(f"Fetching from {len(PROXY_SOURCES)} sources...")

        def fetch_source(url):
            try:
                headers = {'User-Agent': random.choice(USER_AGENTS)}
                response = requests.get(url, timeout=15, headers=headers)

                if response.status_code == 200:
                    # Parse response
                    text = response.text

                    # Check if JSON (Geonode API)
                    if url.startswith('https://proxylist.geonode.com'):
                        try:
                            data = response.json()
                            proxies = []
                            for item in data.get('data', []):
                                ip = item.get('ip')
                                port = item.get('port')
                                if ip and port:
                                    proxies.append(f"{ip}:{port}")
                            return proxies
                        except:
                            pass

                    # Parse as text
                    lines = text.strip().split('\n')
                    proxies = []
                    for line in lines:
                        line = line.strip()
                        # Look for IP:PORT pattern
                        if ':' in line and len(line.split(':')) == 2:
                            try:
                                ip, port = line.split(':')
                                # Basic validation
                                if '.' in ip and port.isdigit():
                                    proxies.append(line)
                            except:
                                continue

                    if proxies:
                        print(f"  ✓ {url[:60]:60s} → {len(proxies):5d} proxies")
                        return proxies
                    else:
                        print(f"  ✗ {url[:60]:60s} → No valid proxies")
                        return []
                else:
                    print(f"  ✗ {url[:60]:60s} → HTTP {response.status_code}")
                    return []

            except Exception as e:
                print(f"  ✗ {url[:60]:60s} → {str(e)[:20]}")
                return []

        # Fetch concurrently
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(fetch_source, url): url for url in PROXY_SOURCES}

            for future in as_completed(futures):
                proxies = future.result()
                self.all_proxies.update(proxies)

        print(f"\n✓ Total unique proxies collected: {len(self.all_proxies)}")
        return list(self.all_proxies)

    def test_proxy(self, proxy: str) -> Dict:
        """Test a single proxy against Yahoo Finance"""
        self.tested_count += 1

        # Format proxy
        if not proxy.startswith(('http://', 'https://', 'socks4://', 'socks5://')):
            proxy_url = f'http://{proxy}'
        else:
            proxy_url = proxy

        proxy_dict = {
            'http': proxy_url,
            'https': proxy_url
        }

        # Test with multiple URLs
        for test_url in TEST_URLS:
            try:
                start = time.time()
                response = requests.get(
                    test_url,
                    proxies=proxy_dict,
                    timeout=5,
                    headers={'User-Agent': random.choice(USER_AGENTS)}
                )
                elapsed = time.time() - start

                # Check if response is valid
                if response.status_code == 200:
                    # For Yahoo Finance, check for actual data
                    if 'chart' in response.text.lower() or 'yahoo' in response.text.lower():
                        self.working_count += 1
                        return {
                            'proxy': proxy_url,
                            'working': True,
                            'response_time': round(elapsed, 2),
                            'tested_with': test_url
                        }
            except:
                continue

        return {'proxy': proxy_url, 'working': False}

    def test_proxies_batch(self, proxies: List[str], batch_size: int = 100,
                          max_workers: int = 50) -> List[Dict]:
        """Test proxies in batches"""
        print(f"\nTesting {len(proxies)} proxies...")
        print(f"Batch size: {batch_size}, Workers: {max_workers}")
        print("-" * 80)

        working = []

        # Process in batches to avoid overwhelming
        for i in range(0, len(proxies), batch_size):
            batch = proxies[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(proxies) + batch_size - 1) // batch_size

            print(f"\nBatch {batch_num}/{total_batches}: Testing {len(batch)} proxies...")
            batch_start = time.time()

            batch_working = []
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(self.test_proxy, p): p for p in batch}

                for future in as_completed(futures):
                    result = future.result()
                    if result['working']:
                        batch_working.append(result)
                        working.append(result)
                        print(f"  ✓ [{len(working):3d}] {result['proxy']:30s} ({result['response_time']}s)")

            batch_elapsed = time.time() - batch_start
            batch_rate = len(batch) / batch_elapsed if batch_elapsed > 0 else 0
            success_rate = len(batch_working) / len(batch) * 100 if batch else 0

            print(f"  Batch {batch_num} complete: {len(batch_working)}/{len(batch)} working ({success_rate:.1f}%)")
            print(f"  Rate: {batch_rate:.1f} tests/sec, Elapsed: {batch_elapsed:.1f}s")
            print(f"  Total working so far: {len(working)}")

            # Stop if we have enough
            if len(working) >= self.target_count:
                print(f"\n✓ Reached target of {self.target_count} working proxies!")
                break

        return working

    def save_proxies(self, working: List[Dict], filename: str = 'tested_working_proxies.json'):
        """Save working proxies to file"""
        output = {
            'proxies': [p['proxy'] for p in working],
            'proxy_details': working,
            'total': len(working),
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S'),
            'tested_count': self.tested_count,
            'success_rate': f"{len(working)/self.tested_count*100:.2f}%" if self.tested_count > 0 else "0%"
        }

        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\n✓ Saved {len(working)} working proxies to {filename}")

        # Also save simple list format
        simple_file = filename.replace('.json', '_simple.txt')
        with open(simple_file, 'w') as f:
            for p in working:
                f.write(p['proxy'] + '\n')

        print(f"✓ Saved simple list to {simple_file}")

    def run(self, test_limit: int = 2000):
        """Main execution"""
        start_time = time.time()

        # Step 1: Fetch all proxies
        all_proxies = self.fetch_all_sources()

        if not all_proxies:
            print("\n✗ No proxies fetched!")
            return []

        # Step 2: Shuffle for random distribution
        random.shuffle(all_proxies)

        # Step 3: Limit testing
        test_proxies = all_proxies[:test_limit]
        print(f"\nWill test {len(test_proxies)} proxies (out of {len(all_proxies)} total)")

        # Step 4: Test in batches
        working = self.test_proxies_batch(test_proxies, batch_size=100, max_workers=50)

        # Step 5: Save results
        if working:
            self.save_proxies(working)

        # Final summary
        elapsed = time.time() - start_time
        print("\n" + "=" * 80)
        print("FETCH COMPLETE")
        print("=" * 80)
        print(f"Total proxies fetched:  {len(all_proxies)}")
        print(f"Total proxies tested:   {self.tested_count}")
        print(f"Working proxies found:  {len(working)}")
        print(f"Success rate:           {len(working)/self.tested_count*100:.2f}%" if self.tested_count > 0 else "0%")
        print(f"Total time:             {elapsed:.1f}s")
        print(f"Test rate:              {self.tested_count/elapsed:.1f} proxies/sec")
        print("=" * 80)

        return working


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Aggressive Proxy Fetcher & Tester')
    parser.add_argument('--target', type=int, default=200,
                       help='Target number of working proxies (default: 200)')
    parser.add_argument('--test-limit', type=int, default=2000,
                       help='Maximum proxies to test (default: 2000)')
    parser.add_argument('--output', type=str, default='tested_working_proxies.json',
                       help='Output filename (default: tested_working_proxies.json)')

    args = parser.parse_args()

    fetcher = AggressiveProxyFetcher(target_count=args.target)
    working = fetcher.run(test_limit=args.test_limit)

    if working:
        print(f"\n✓ Successfully found {len(working)} working proxies!")
        print(f"  Use them with: --proxy-file {args.output}")
        return 0
    else:
        print("\n✗ No working proxies found!")
        print("  This is common with free proxies. Consider:")
        print("  1. Running again (proxy availability changes constantly)")
        print("  2. Using a paid proxy service")
        print("  3. Running the script without proxies (slower, lower success rate)")
        return 1


if __name__ == '__main__':
    sys.exit(main())
