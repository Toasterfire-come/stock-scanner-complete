#!/usr/bin/env python3
"""
Diagnose Proxy Issue - Detailed Error Analysis
==============================================

Captures exact error messages and responses when using proxies with yfinance.
"""

import os
import sys
import time
import logging
import traceback

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
    level=logging.DEBUG,  # DEBUG level to see everything
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Enable yfinance debug logging
logging.getLogger('yfinance').setLevel(logging.DEBUG)

# =====================================================
# PROXY DIAGNOSTIC
# =====================================================

def test_with_proxy(proxy_url: str, ticker: str = 'AAPL'):
    """
    Test a single yfinance call with proxy and capture ALL details

    Args:
        proxy_url: Proxy URL to test
        ticker: Ticker symbol to fetch
    """

    logger.info("=" * 70)
    logger.info("DIAGNOSTIC TEST WITH PROXY")
    logger.info("=" * 70)
    logger.info(f"Proxy: {proxy_url}")
    logger.info(f"Ticker: {ticker}")
    logger.info("")

    try:
        # Set proxy environment variables
        logger.info("Step 1: Setting proxy environment variables...")
        os.environ['HTTP_PROXY'] = proxy_url
        os.environ['HTTPS_PROXY'] = proxy_url
        os.environ['http_proxy'] = proxy_url
        os.environ['https_proxy'] = proxy_url
        os.environ['ALL_PROXY'] = proxy_url
        os.environ['all_proxy'] = proxy_url
        os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
        os.environ['no_proxy'] = 'localhost,127.0.0.1'

        logger.info("✓ Proxy environment variables set")
        logger.info(f"  HTTP_PROXY = {os.environ.get('HTTP_PROXY')}")
        logger.info(f"  HTTPS_PROXY = {os.environ.get('HTTPS_PROXY')}")
        logger.info("")

        # Force garbage collection
        logger.info("Step 2: Clearing cached sessions...")
        import gc
        gc.collect()
        logger.info("✓ Garbage collection complete")
        logger.info("")

        # Brief pause
        logger.info("Step 3: Waiting 0.5s for OS to pick up proxy settings...")
        time.sleep(0.5)
        logger.info("✓ Ready to make request")
        logger.info("")

        # Make yfinance call
        logger.info(f"Step 4: Creating yfinance Ticker object for {ticker}...")
        ticker_obj = yf.Ticker(ticker)
        logger.info("✓ Ticker object created")
        logger.info("")

        logger.info("Step 5: Fetching fast_info...")
        logger.info("(This is where the HTTP request happens)")
        logger.info("")

        start_time = time.time()

        # This will show all HTTP requests in debug logs
        data = ticker_obj.fast_info

        elapsed = time.time() - start_time
        logger.info(f"✓ fast_info retrieved in {elapsed:.2f}s")
        logger.info("")

        # Try to get price
        logger.info("Step 6: Extracting last_price...")
        price = getattr(data, 'last_price', None)

        if price:
            logger.info(f"✓ SUCCESS: Price = ${price}")
            logger.info("")
            logger.info("=" * 70)
            logger.info("TEST PASSED - PROXY WORKS!")
            logger.info("=" * 70)
            return True
        else:
            logger.warning("✗ No price data returned")
            logger.info("")
            logger.info("=" * 70)
            logger.info("TEST FAILED - No price in response")
            logger.info("=" * 70)
            return False

    except Exception as e:
        logger.error("")
        logger.error("=" * 70)
        logger.error("EXCEPTION CAUGHT")
        logger.error("=" * 70)
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Exception message: {str(e)}")
        logger.error("")
        logger.error("Full traceback:")
        logger.error(traceback.format_exc())
        logger.error("=" * 70)
        return False

    finally:
        # Clear proxy
        logger.info("")
        logger.info("Cleanup: Clearing proxy settings...")
        for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']:
            if var in os.environ:
                del os.environ[var]
        import gc
        gc.collect()
        logger.info("✓ Cleanup complete")
        logger.info("")


def test_without_proxy(ticker: str = 'AAPL'):
    """
    Test the same call WITHOUT proxy for comparison

    Args:
        ticker: Ticker symbol to fetch
    """

    logger.info("=" * 70)
    logger.info("CONTROL TEST WITHOUT PROXY")
    logger.info("=" * 70)
    logger.info(f"Ticker: {ticker}")
    logger.info("Connection: Direct (no proxy)")
    logger.info("")

    try:
        # Ensure no proxy is set
        for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']:
            if var in os.environ:
                del os.environ[var]

        import gc
        gc.collect()

        logger.info("Step 1: Making direct connection to yfinance...")
        logger.info("")

        start_time = time.time()

        ticker_obj = yf.Ticker(ticker)
        data = ticker_obj.fast_info
        price = getattr(data, 'last_price', None)

        elapsed = time.time() - start_time

        if price:
            logger.info(f"✓ SUCCESS: Price = ${price}")
            logger.info(f"✓ Time: {elapsed:.2f}s")
            logger.info("")
            logger.info("=" * 70)
            logger.info("CONTROL TEST PASSED")
            logger.info("=" * 70)
            return True
        else:
            logger.warning("✗ No price data returned")
            logger.info("")
            logger.info("=" * 70)
            logger.info("CONTROL TEST FAILED")
            logger.info("=" * 70)
            return False

    except Exception as e:
        logger.error("")
        logger.error("=" * 70)
        logger.error("CONTROL TEST EXCEPTION")
        logger.error("=" * 70)
        logger.error(f"Exception: {type(e).__name__}: {str(e)}")
        logger.error(traceback.format_exc())
        logger.error("=" * 70)
        return False


# =====================================================
# MAIN
# =====================================================

def main():
    """Run diagnostic tests"""

    logger.info("=" * 70)
    logger.info("YFINANCE PROXY DIAGNOSTIC TOOL")
    logger.info("=" * 70)
    logger.info("")
    logger.info("This will:")
    logger.info("1. Test WITHOUT proxy (control)")
    logger.info("2. Test WITH Geonode SOCKS proxy")
    logger.info("3. Test WITH user-provided HTTP proxy")
    logger.info("")
    logger.info("All HTTP requests and errors will be logged in detail.")
    logger.info("")
    logger.info("=" * 70)
    logger.info("")

    # Test 1: Control (no proxy)
    logger.info("TEST 1: CONTROL (NO PROXY)")
    logger.info("-" * 70)
    logger.info("")

    control_result = test_without_proxy('AAPL')

    time.sleep(2)
    logger.info("")
    logger.info("")

    # Test 2: With SOCKS proxy from Geonode
    logger.info("TEST 2: WITH SOCKS PROXY (from Geonode)")
    logger.info("-" * 70)
    logger.info("")

    # Get a proxy from Geonode
    from unified_proxy_manager import GeonodeProxyFetcher

    logger.info("Fetching proxy from Geonode API...")
    proxies = GeonodeProxyFetcher.fetch_proxies(limit=5)

    if proxies:
        proxy_data = proxies[0]
        proxy_url, is_http = GeonodeProxyFetcher.format_proxy(proxy_data)
        logger.info(f"Selected proxy: {proxy_url}")
        logger.info(f"Type: {'HTTP/HTTPS' if is_http else 'SOCKS'}")
        logger.info(f"Location: {proxy_data.get('country', 'Unknown')}")
        logger.info("")

        # Set a shorter timeout for this test
        import socket
        socket.setdefaulttimeout(15)  # 15 second timeout

        socks_result = test_with_proxy(proxy_url, 'AAPL')
    else:
        logger.error("Failed to fetch proxy from Geonode")
        socks_result = False

    time.sleep(2)
    logger.info("")
    logger.info("")

    # Test 3: With HTTP proxy from user list
    logger.info("TEST 3: WITH HTTP PROXY (from user list)")
    logger.info("-" * 70)
    logger.info("")

    # Try a couple of the user's proxies
    user_proxies = [
        "http://50.174.9.163:80",      # US
        "http://198.49.70.81:80",      # US
        "http://66.29.156.106:3128",   # US
    ]

    http_result = False
    for proxy in user_proxies:
        logger.info(f"Testing {proxy}...")
        logger.info("")

        import socket
        socket.setdefaulttimeout(15)  # 15 second timeout

        result = test_with_proxy(proxy, 'AAPL')

        if result:
            http_result = True
            break
        else:
            logger.info("")
            logger.info("Trying next proxy...")
            logger.info("")
            time.sleep(1)

    # Summary
    logger.info("")
    logger.info("")
    logger.info("=" * 70)
    logger.info("DIAGNOSTIC SUMMARY")
    logger.info("=" * 70)
    logger.info("")
    logger.info(f"Control (no proxy):     {'✓ PASS' if control_result else '✗ FAIL'}")
    logger.info(f"SOCKS proxy (Geonode):  {'✓ PASS' if socks_result else '✗ FAIL'}")
    logger.info(f"HTTP proxy (user list): {'✓ PASS' if http_result else '✗ FAIL'}")
    logger.info("")

    if control_result and not (socks_result or http_result):
        logger.info("CONCLUSION: Direct connection works, all proxies fail")
        logger.info("RECOMMENDATION: Run without proxies")
    elif control_result and (socks_result or http_result):
        logger.info("CONCLUSION: Both direct and proxy connections work")
        logger.info("RECOMMENDATION: Use working proxies found above")
    else:
        logger.info("CONCLUSION: Network issues detected")
        logger.info("RECOMMENDATION: Check network connectivity")

    logger.info("")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
