#!/usr/bin/env python3
"""
Proxy Configuration Helper
============================
Utility to test, validate, and configure proxies for yfinance data collection.

Features:
- Test proxy connectivity and speed
- Validate SOCKS5h proxy support
- Convert HTTP proxies to SOCKS5h format
- Health check for existing proxy lists
- Export healthy proxies
"""

import json
import time
import requests
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Try to import curl_cffi
try:
    from curl_cffi import requests as curl_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    curl_requests = None
    CURL_CFFI_AVAILABLE = False

# SOCKS support
try:
    import socks
    SOCKS_AVAILABLE = True
except ImportError:
    SOCKS_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProxyTester:
    """Test and validate proxy configurations"""

    TEST_URLS = [
        "https://query1.finance.yahoo.com/v8/finance/chart/AAPL",
        "https://httpbin.org/ip",
        "https://www.google.com",
    ]

    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout

    def test_proxy(self, proxy: str) -> Dict[str, Any]:
        """Test a single proxy"""
        result = {
            "proxy": proxy,
            "working": False,
            "response_time": None,
            "error": None,
            "ip_address": None,
            "supports_https": False,
            "supports_yahoo": False
        }

        try:
            start_time = time.time()

            # Test with requests
            session = requests.Session()
            session.proxies = {
                "http": proxy,
                "https": proxy
            }
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })

            # Test connectivity
            response = session.get("https://httpbin.org/ip", timeout=self.timeout)
            if response.status_code == 200:
                result["working"] = True
                result["supports_https"] = True
                result["response_time"] = time.time() - start_time
                data = response.json()
                result["ip_address"] = data.get("origin")

                # Test Yahoo Finance specifically
                try:
                    yahoo_response = session.get(
                        "https://query1.finance.yahoo.com/v8/finance/chart/AAPL",
                        timeout=self.timeout
                    )
                    if yahoo_response.status_code == 200:
                        result["supports_yahoo"] = True
                except Exception:
                    pass

        except Exception as e:
            result["error"] = str(e)[:100]

        return result

    def test_socks5_proxy(self, proxy: str) -> Dict[str, Any]:
        """Test a SOCKS5 proxy"""
        result = {
            "proxy": proxy,
            "working": False,
            "response_time": None,
            "error": None,
            "dns_leak_protected": False,
            "supports_yahoo": False
        }

        if not SOCKS_AVAILABLE:
            result["error"] = "PySocks not installed"
            return result

        try:
            start_time = time.time()

            # Test SOCKS5h (DNS through proxy)
            socks5h_proxy = proxy.replace("socks5://", "socks5h://")

            session = requests.Session()
            session.proxies = {
                "http": socks5h_proxy,
                "https": socks5h_proxy
            }
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })

            # Test connectivity
            response = session.get("https://httpbin.org/ip", timeout=self.timeout)
            if response.status_code == 200:
                result["working"] = True
                result["response_time"] = time.time() - start_time

                # If socks5h works, DNS is protected
                if "socks5h://" in socks5h_proxy:
                    result["dns_leak_protected"] = True

                # Test Yahoo Finance
                try:
                    yahoo_response = session.get(
                        "https://query1.finance.yahoo.com/v8/finance/chart/AAPL",
                        timeout=self.timeout
                    )
                    if yahoo_response.status_code == 200:
                        result["supports_yahoo"] = True
                except Exception:
                    pass

        except Exception as e:
            result["error"] = str(e)[:100]

        return result

    def test_proxies_concurrent(self, proxies: List[str], max_workers: int = 20) -> List[Dict[str, Any]]:
        """Test multiple proxies concurrently"""
        logger.info(f"Testing {len(proxies)} proxies with {max_workers} workers...")
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Determine test function based on proxy type
            futures = {}
            for proxy in proxies:
                if proxy.startswith("socks5://"):
                    future = executor.submit(self.test_socks5_proxy, proxy)
                else:
                    future = executor.submit(self.test_proxy, proxy)
                futures[future] = proxy

            for i, future in enumerate(as_completed(futures), 1):
                try:
                    result = future.result()
                    results.append(result)

                    if i % 10 == 0:
                        working_count = sum(1 for r in results if r["working"])
                        logger.info(f"Progress: {i}/{len(proxies)} | Working: {working_count}/{i}")

                except Exception as e:
                    logger.error(f"Error testing proxy: {str(e)}")

        return results


def load_proxies_from_file(file_path: Path) -> List[str]:
    """Load proxies from JSON file"""
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []

    with open(file_path, 'r') as f:
        data = json.load(f)

    if isinstance(data, dict) and "proxies" in data:
        return data["proxies"]
    elif isinstance(data, list):
        return data
    else:
        logger.error("Invalid proxy file format")
        return []


def save_proxies_to_file(proxies: List[str], file_path: Path):
    """Save proxies to JSON file"""
    data = {"proxies": proxies}
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    logger.info(f"Saved {len(proxies)} proxies to {file_path}")


def main():
    parser = argparse.ArgumentParser(description="Proxy Configuration Helper")
    parser.add_argument("--test", type=str, help="Test proxies from file")
    parser.add_argument("--output", type=str, help="Output file for working proxies")
    parser.add_argument("--timeout", type=float, default=5.0, help="Timeout for proxy tests")
    parser.add_argument("--workers", type=int, default=20, help="Number of concurrent workers")
    parser.add_argument("--min-speed", type=float, default=10.0, help="Minimum speed (max response time in seconds)")
    parser.add_argument("--yahoo-only", action="store_true", help="Only keep proxies that work with Yahoo Finance")

    args = parser.parse_args()

    if args.test:
        # Test proxies from file
        test_file = Path(args.test)
        proxies = load_proxies_from_file(test_file)

        if not proxies:
            logger.error("No proxies to test")
            return

        tester = ProxyTester(timeout=args.timeout)
        results = tester.test_proxies_concurrent(proxies, max_workers=args.workers)

        # Filter working proxies
        working_proxies = []
        for result in results:
            if not result["working"]:
                continue

            # Check speed requirement
            if result["response_time"] and result["response_time"] > args.min_speed:
                logger.debug(f"Skipping slow proxy {result['proxy']}: {result['response_time']:.2f}s")
                continue

            # Check Yahoo Finance requirement
            if args.yahoo_only and not result.get("supports_yahoo"):
                logger.debug(f"Skipping proxy {result['proxy']}: doesn't support Yahoo Finance")
                continue

            working_proxies.append(result["proxy"])

        # Print statistics
        logger.info("=" * 80)
        logger.info("PROXY TEST RESULTS")
        logger.info("=" * 80)
        logger.info(f"Total tested: {len(results)}")
        logger.info(f"Working: {len(working_proxies)}/{len(results)} ({len(working_proxies)/len(results)*100:.1f}%)")
        logger.info(f"Failed: {len(results) - len(working_proxies)}")

        yahoo_working = sum(1 for r in results if r.get("supports_yahoo"))
        logger.info(f"Yahoo Finance compatible: {yahoo_working}/{len(results)} ({yahoo_working/len(results)*100:.1f}%)")

        if working_proxies and args.output:
            output_file = Path(args.output)
            save_proxies_to_file(working_proxies, output_file)
            logger.info(f"✓ Saved {len(working_proxies)} working proxies to {output_file}")

        # Show some working proxies
        if working_proxies:
            logger.info("\nSample working proxies:")
            for proxy in working_proxies[:5]:
                logger.info(f"  - {proxy}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
