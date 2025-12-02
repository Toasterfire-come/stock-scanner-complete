#!/usr/bin/env python3
"""
Diagnostic version to identify why fetches are failing
"""

import os
import sys
import time
import logging
from collections import defaultdict

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")

import django
django.setup()

import yfinance as yf
from django.utils import timezone

from stock_retrieval.session_factory import create_requests_session

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger(__name__)

def test_single_ticker(symbol: str):
    """Test fetching a single ticker with detailed error logging"""

    logger.info(f"\n{'='*70}")
    logger.info(f"Testing: {symbol}")
    logger.info('='*70)

    # Create session without proxy
    session = create_requests_session(proxy=None, timeout=5)

    logger.info(f"Session created: {type(session)}")
    logger.info(f"Session headers: {session.headers}")

    # Create ticker
    ticker = yf.Ticker(symbol, session=session)
    logger.info(f"Ticker created: {ticker}")

    # Try fast_info
    logger.info("\n--- Trying fast_info ---")
    try:
        data = ticker.fast_info
        logger.info(f"fast_info SUCCESS: {type(data)}")
        logger.info(f"  last_price: {getattr(data, 'last_price', 'N/A')}")
        logger.info(f"  market_cap: {getattr(data, 'market_cap', 'N/A')}")
        logger.info(f"  shares: {getattr(data, 'shares', 'N/A')}")
        return True, 'fast_info'
    except Exception as e:
        logger.error(f"fast_info FAILED: {type(e).__name__}: {e}")

    # Try .info
    logger.info("\n--- Trying .info ---")
    try:
        info = ticker.info
        logger.info(f"info SUCCESS: {type(info)}")
        logger.info(f"  Keys: {list(info.keys())[:10]}")
        logger.info(f"  regularMarketPrice: {info.get('regularMarketPrice', 'N/A')}")
        logger.info(f"  marketCap: {info.get('marketCap', 'N/A')}")
        return True, 'info'
    except Exception as e:
        logger.error(f"info FAILED: {type(e).__name__}: {e}")

    # Try history
    logger.info("\n--- Trying .history ---")
    try:
        hist = ticker.history(period='1d')
        logger.info(f"history SUCCESS: {type(hist)}")
        logger.info(f"  Empty: {hist.empty}")
        if not hist.empty:
            logger.info(f"  Last close: {hist['Close'].iloc[-1]}")
            return True, 'history'
    except Exception as e:
        logger.error(f"history FAILED: {type(e).__name__}: {e}")

    return False, None

def main():
    """Test a few tickers to diagnose the issue"""

    test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']

    logger.info("="*70)
    logger.info("DIAGNOSTIC TICKER PULLER")
    logger.info("="*70)
    logger.info(f"Testing {len(test_symbols)} tickers to diagnose fetch failures\n")

    results = defaultdict(int)

    for symbol in test_symbols:
        success, method = test_single_ticker(symbol)
        if success:
            results[method] += 1
            logger.info(f"\n[SUCCESS] {symbol} via {method}")
        else:
            results['failed'] += 1
            logger.info(f"\n[FAILED] {symbol} - all methods failed")

        time.sleep(0.5)  # Small delay between tests

    logger.info("\n" + "="*70)
    logger.info("DIAGNOSTIC RESULTS")
    logger.info("="*70)
    logger.info(f"Tested: {len(test_symbols)}")
    logger.info(f"Results:")
    for method, count in results.items():
        logger.info(f"  {method}: {count}")
    logger.info("="*70)

if __name__ == "__main__":
    main()
