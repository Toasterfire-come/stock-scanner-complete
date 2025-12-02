#!/usr/bin/env python3
"""
Test Specific Free HTTP Proxies
================================

Tests a curated list of free HTTP proxies to find working ones.
"""

import os
import sys
import time
import logging
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")

import django
django.setup()

import yfinance as yf

# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress yfinance noise
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# =====================================================
# TEST PROXIES
# =====================================================

# Curated list of free HTTP/HTTPS proxies
TEST_PROXIES = [
    "http://209.121.166.51:31147",      # CA - anonymous
    "http://72.10.162.95:8355",         # CA - elite
    "http://159.65.247.256:80",         # US - elite (note: IP might be typo, .256 invalid)
    "http://51.83.64.246:8080",         # FR - anonymous
    "http://128.199.204.123:3128",      # SG - anonymous
    "http://160.86.244.24:8080",        # JP - elite
    "http://185.250.47.80:8888",        # NL - anonymous
    "http://50.174.9.163:80",           # US - anonymous
    "http://38.54.73.68:80",            # NP - elite
    "http://198.49.70.81:80",           # US - elite
    "http://66.29.156.106:3128",        # US - anonymous
    "http://195.23.59.79:80",           # PT - anonymous
    "http://50.172.77.128:80",          # US - anonymous
    "http://50.217.228.42:80",          # US - anonymous
    "http://78.28.154.112:80",          # BA - elite
    "http://50.223.248.238:80",         # US - anonymous
    "http://172.96.194.45:8888",        # US - anonymous
    "http://103.127.3.131:80",          # BD - anonymous
    "http://50.171.189.52:80",          # US - anonymous
    "http://49.245.98.146:80",          # SG - anonymous
]

TEST_TICKERS = ['AAPL', 'MSFT', 'GOOGL']

# =====================================================
# PROXY TESTER
# =====================================================

class ProxyTester:
    """Test individual proxies"""

    @staticmethod
    def test_proxy(proxy_url: str, timeout: int = 10) -> Dict:
        """
        Test a single proxy by fetching data from yfinance

        Returns dict with:
            - proxy: proxy URL
            - working: True if proxy works
            - latency: response time in seconds
            - error: error message if failed
        """

        result = {
            'proxy': proxy_url,
            'working': False,
            'latency': None,
            'success_count': 0,
            'error': None
        }

        try:
            # Set proxy environment variables
            os.environ['HTTP_PROXY'] = proxy_url
            os.environ['HTTPS_PROXY'] = proxy_url
            os.environ['http_proxy'] = proxy_url
            os.environ['https_proxy'] = proxy_url
            os.environ['ALL_PROXY'] = proxy_url
            os.environ['all_proxy'] = proxy_url

            # Force garbage collection to clear cached sessions
            import gc
            gc.collect()

            # Brief pause to ensure OS picks up env vars
            time.sleep(0.1)

            # Test with multiple tickers
            start = time.time()

            for ticker_symbol in TEST_TICKERS:
                try:
                    ticker = yf.Ticker(ticker_symbol)
                    data = ticker.fast_info
                    price = getattr(data, 'last_price', None)

                    if price and price > 0:
                        result['success_count'] += 1
                except:
                    pass

            elapsed = time.time() - start

            # Consider working if at least 2 out of 3 tickers succeeded
            if result['success_count'] >= 2:
                result['working'] = True
                result['latency'] = round(elapsed, 2)
            else:
                result['error'] = f"Only {result['success_count']}/3 tickers succeeded"

        except Exception as e:
            result['error'] = str(e)[:100]

        finally:
            # Clear proxy settings
            for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']:
                if var in os.environ:
                    del os.environ[var]

            import gc
            gc.collect()

        return result

    @staticmethod
    def test_all_proxies(proxies: List[str], max_workers: int = 5) -> List[Dict]:
        """
        Test all proxies concurrently

        Args:
            proxies: List of proxy URLs
            max_workers: Number of concurrent tests

        Returns:
            List of test results sorted by working/latency
        """

        logger.info("=" * 70)
        logger.info("TESTING FREE HTTP PROXIES")
        logger.info("=" * 70)
        logger.info(f"Total proxies to test: {len(proxies)}")
        logger.info(f"Test tickers: {', '.join(TEST_TICKERS)}")
        logger.info(f"Concurrent tests: {max_workers}")
        logger.info("")

        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(ProxyTester.test_proxy, proxy): proxy
                for proxy in proxies
            }

            for i, future in enumerate(as_completed(futures)):
                result = future.result()
                results.append(result)

                status = "✅ WORKING" if result['working'] else "❌ FAILED"
                latency_str = f"{result['latency']}s" if result['latency'] else "N/A"

                logger.info(
                    f"[{i+1}/{len(proxies)}] {status} | "
                    f"{result['proxy']:45} | "
                    f"Latency: {latency_str:6} | "
                    f"Success: {result['success_count']}/3"
                )

                if result['error'] and not result['working']:
                    logger.debug(f"  Error: {result['error']}")

        # Sort by working status, then by latency
        results.sort(key=lambda x: (not x['working'], x['latency'] or 999))

        return results

# =====================================================
# MAIN
# =====================================================

def main():
    """Test all proxies and save working ones"""

    logger.info("=" * 70)
    logger.info("FREE PROXY TESTING UTILITY")
    logger.info("=" * 70)
    logger.info("")

    # Test all proxies
    start = time.time()
    results = ProxyTester.test_all_proxies(TEST_PROXIES, max_workers=10)
    elapsed = time.time() - start

    # Separate working and failed
    working = [r for r in results if r['working']]
    failed = [r for r in results if not r['working']]

    # Results summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("TEST RESULTS")
    logger.info("=" * 70)
    logger.info(f"Total tested: {len(results)}")
    logger.info(f"Working: {len(working)} ({len(working)/len(results)*100:.1f}%)")
    logger.info(f"Failed: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")
    logger.info(f"Test time: {elapsed:.1f}s")
    logger.info("")

    if working:
        logger.info("=" * 70)
        logger.info("WORKING PROXIES (sorted by latency)")
        logger.info("=" * 70)

        for i, proxy in enumerate(working, 1):
            logger.info(
                f"{i}. {proxy['proxy']:45} | "
                f"Latency: {proxy['latency']:5.2f}s | "
                f"Success: {proxy['success_count']}/3"
            )

        # Save working proxies to file
        output_file = "working_free_proxies.txt"
        with open(output_file, 'w') as f:
            f.write("# Working Free HTTP Proxies\n")
            f.write(f"# Tested: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Working: {len(working)}/{len(results)}\n")
            f.write("\n")

            for proxy in working:
                f.write(f"{proxy['proxy']}\n")

        logger.info("")
        logger.info(f"Working proxies saved to: {output_file}")

    else:
        logger.warning("=" * 70)
        logger.warning("NO WORKING PROXIES FOUND")
        logger.warning("=" * 70)
        logger.warning("All tested proxies failed or timed out.")
        logger.warning("Recommendation: Run without proxies or use paid service.")

    logger.info("")
    logger.info("=" * 70)
    logger.info("TEST COMPLETE")
    logger.info("=" * 70)

if __name__ == "__main__":
    main()
