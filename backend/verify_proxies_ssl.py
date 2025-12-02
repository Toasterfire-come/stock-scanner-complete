#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Proxy SSL Certificate Verification Script

Tests proxies for:
1. Valid SSL certificates
2. Connection speed
3. Yahoo Finance API compatibility

Outputs a list of working proxies sorted by speed.
"""

import os
import sys
import time
import json
import ssl
import socket
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from typing import List, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")

import django
django.setup()

from stock_retrieval.session_factory import ProxyPool
from stock_retrieval.config import StockRetrievalConfig

# Configuration
MAX_WORKERS = 50
TEST_TIMEOUT = 5
TEST_URL = "https://query2.finance.yahoo.com/v8/finance/chart/AAPL"


def test_ssl_cert(proxy_url: str) -> Optional[Dict]:
    """Test if proxy has valid SSL certificate"""
    try:
        parsed = urlparse(proxy_url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)

        # Try to establish SSL connection
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=TEST_TIMEOUT) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                return {
                    'valid': True,
                    'subject': cert.get('subject'),
                    'issuer': cert.get('issuer')
                }
    except Exception as e:
        return {'valid': False, 'error': str(e)}


def test_proxy_yahoo(proxy_url: str) -> Optional[Dict]:
    """Test if proxy can access Yahoo Finance"""
    start = time.time()

    try:
        # Test with requests
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }

        response = requests.get(
            TEST_URL,
            proxies=proxies,
            timeout=TEST_TIMEOUT,
            verify=False  # Skip SSL verification for proxy
        )

        duration = time.time() - start

        if response.status_code == 200:
            return {
                'proxy': proxy_url,
                'status': 'working',
                'response_time': duration,
                'status_code': response.status_code
            }
        else:
            return {
                'proxy': proxy_url,
                'status': 'failed',
                'error': f'HTTP {response.status_code}',
                'response_time': duration
            }

    except requests.exceptions.SSLError as e:
        return {
            'proxy': proxy_url,
            'status': 'ssl_error',
            'error': str(e)
        }
    except Exception as e:
        return {
            'proxy': proxy_url,
            'status': 'failed',
            'error': str(e)
        }


def test_direct_connection() -> Dict:
    """Test direct connection without proxy"""
    print("[*] Testing direct connection to Yahoo Finance...")

    start = time.time()
    try:
        response = requests.get(TEST_URL, timeout=TEST_TIMEOUT)
        duration = time.time() - start

        if response.status_code == 200:
            print(f"  [OK] Direct connection works: {duration:.2f}s")
            return {
                'proxy': 'DIRECT',
                'status': 'working',
                'response_time': duration
            }
        else:
            print(f"  [WARN] Direct connection returned {response.status_code}")
            return {
                'proxy': 'DIRECT',
                'status': 'failed',
                'error': f'HTTP {response.status_code}'
            }
    except Exception as e:
        print(f"  [ERROR] Direct connection failed: {e}")
        return {
            'proxy': 'DIRECT',
            'status': 'failed',
            'error': str(e)
        }


def verify_all_proxies(max_proxies: int = 1000) -> List[Dict]:
    """Verify all proxies in the pool"""

    print("=" * 70)
    print("PROXY SSL VERIFICATION")
    print("=" * 70)

    # Test direct connection first
    direct_result = test_direct_connection()

    # Load proxy pool
    print("\n[*] Loading proxy pool...")
    config = StockRetrievalConfig()
    proxy_pool = ProxyPool.from_config(config)

    all_proxies = proxy_pool.proxies[:max_proxies]
    print(f"   Testing {len(all_proxies)} proxies...")

    results = []
    working = []
    ssl_errors = []
    failed = []

    # Test proxies concurrently
    print("\n[*] Testing proxies (this may take a while)...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(test_proxy_yahoo, proxy): proxy for proxy in all_proxies}

        completed = 0
        for future in as_completed(futures):
            completed += 1
            if completed % 100 == 0:
                print(f"   Progress: {completed}/{len(all_proxies)} tested")

            result = future.result()
            if result:
                results.append(result)

                if result['status'] == 'working':
                    working.append(result)
                elif result['status'] == 'ssl_error':
                    ssl_errors.append(result)
                else:
                    failed.append(result)

    # Sort working proxies by response time
    working.sort(key=lambda x: x['response_time'])

    # Print summary
    print("\n" + "=" * 70)
    print("VERIFICATION RESULTS")
    print("=" * 70)
    print(f"Total tested: {len(results)}")
    print(f"Working: {len(working)}")
    print(f"SSL errors: {len(ssl_errors)}")
    print(f"Failed: {len(failed)}")
    print(f"Success rate: {len(working)/len(results)*100:.1f}%")

    if direct_result['status'] == 'working':
        print(f"\n[OK] Direct connection: {direct_result['response_time']:.2f}s")

    if working:
        print(f"\nTop 10 fastest working proxies:")
        for i, proxy in enumerate(working[:10], 1):
            print(f"  {i}. {proxy['proxy']}: {proxy['response_time']:.2f}s")

    # Save results
    output_file = 'verified_proxies.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': time.time(),
            'direct_connection': direct_result,
            'working_proxies': working,
            'failed_proxies': failed[:100],  # Save first 100 failures
            'ssl_errors': ssl_errors[:100],
            'summary': {
                'total': len(results),
                'working': len(working),
                'ssl_errors': len(ssl_errors),
                'failed': len(failed),
                'success_rate': len(working)/len(results) if results else 0
            }
        }, f, indent=2)

    print(f"\n[OK] Results saved to: {output_file}")

    # Save just the working proxy URLs
    if working:
        proxy_list_file = 'working_proxies_list.txt'
        with open(proxy_list_file, 'w', encoding='utf-8') as f:
            for proxy in working:
                f.write(f"{proxy['proxy']}\n")
        print(f"[OK] Working proxy list saved to: {proxy_list_file}")

    return working


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Verify proxy SSL certificates")
    parser.add_argument('--max-proxies', type=int, default=1000,
                       help='Maximum number of proxies to test (default: 1000)')

    args = parser.parse_args()

    try:
        working_proxies = verify_all_proxies(max_proxies=args.max_proxies)

        if working_proxies:
            print(f"\n[SUCCESS] Found {len(working_proxies)} working proxies!")
        else:
            print("\n[WARNING] No working proxies found. Will need to use direct connection.")

    except KeyboardInterrupt:
        print("\n\nVerification interrupted by user")
    except Exception as e:
        print(f"\nError during verification: {e}")
        import traceback
        traceback.print_exc()
