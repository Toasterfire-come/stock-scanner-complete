#!/usr/bin/env python3
"""
Quick test script to verify scanner works without proxies
Tests with a small sample of tickers to validate basic functionality
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from optimized_9600_scanner import OptimizedScanner, ScannerConfig
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

def test_without_proxies():
    """Test scanner with a small sample, no proxies"""
    print("=" * 70)
    print("TESTING SCANNER WITHOUT PROXIES (Quick Test)")
    print("=" * 70)
    print()

    # Create config without proxies
    config = ScannerConfig()
    config.USE_PROXIES = False  # Disable proxies for testing
    config.BATCH_SIZE = 50  # Smaller batches for testing
    config.MAX_WORKERS = 4  # Fewer workers
    config.ENABLE_SIMULATION = False  # Disable simulation to see real success rate

    # Test with popular stocks
    test_symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
        'TSLA', 'NVDA', 'JPM', 'V', 'WMT',
        'MA', 'UNH', 'HD', 'PG', 'DIS',
        'NFLX', 'PYPL', 'ADBE', 'CMCSA', 'INTC'
    ]

    print(f"Testing with {len(test_symbols)} popular stocks")
    print(f"Stocks: {', '.join(test_symbols[:10])}...")
    print()

    # Run scan
    scanner = OptimizedScanner(config)
    result = scanner.scan(symbols=test_symbols, write_db=False)

    # Display results
    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print(f"Total symbols: {result['total_symbols']}")
    print(f"Real data retrieved: {result['real_data_count']}")
    print(f"Success rate: {result['success_percentage']}")
    print(f"Duration: {result['duration_seconds']}s")
    print(f"Rate: {result['rate_per_second']:.1f} stocks/sec")
    print()

    # Check if test passed
    if result['real_data_count'] >= 15:  # At least 75% should work
        print("✓ TEST PASSED - Scanner is working correctly!")
        print(f"  Successfully fetched {result['real_data_count']}/{result['total_symbols']} stocks")
        return True
    else:
        print("✗ TEST FAILED - Too few successful fetches")
        print(f"  Only got {result['real_data_count']}/{result['total_symbols']} stocks")
        print("\nPossible issues:")
        print("  - Internet connection problem")
        print("  - Yahoo Finance API is down or blocking requests")
        print("  - yfinance library needs updating")
        return False


def test_with_proxies():
    """Test scanner with proxies"""
    print("\n" + "=" * 70)
    print("TESTING SCANNER WITH PROXIES")
    print("=" * 70)
    print()

    config = ScannerConfig()
    config.USE_PROXIES = True
    config.MAX_PROXIES_TO_USE = 100  # Use 100 best proxies for testing
    config.BATCH_SIZE = 50
    config.MAX_WORKERS = 10

    # Test with 50 stocks
    test_symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
        'TSLA', 'NVDA', 'JPM', 'V', 'WMT',
        'MA', 'UNH', 'HD', 'PG', 'DIS',
        'NFLX', 'PYPL', 'ADBE', 'CMCSA', 'INTC',
        'CSCO', 'XOM', 'ABT', 'CVX', 'PFE',
        'KO', 'PEP', 'TMO', 'ABBV', 'COST',
        'NKE', 'AVGO', 'ORCL', 'ACN', 'MRK',
        'LLY', 'DHR', 'TXN', 'UNP', 'MDT',
        'NEE', 'QCOM', 'PM', 'LOW', 'HON',
        'UPS', 'BMY', 'IBM', 'BA', 'RTX'
    ]

    print(f"Testing with {len(test_symbols)} stocks using proxies")
    print()

    scanner = OptimizedScanner(config)
    result = scanner.scan(symbols=test_symbols, write_db=False)

    # Display results
    print("\n" + "=" * 70)
    print("PROXY TEST RESULTS")
    print("=" * 70)
    print(f"Total symbols: {result['total_symbols']}")
    print(f"Real data retrieved: {result['real_data_count']}")
    print(f"Simulated data: {result['simulated_count']}")
    print(f"Success rate: {result['success_percentage']}")
    print(f"Duration: {result['duration_seconds']}s")
    print(f"Rate: {result['rate_per_second']:.1f} stocks/sec")
    print()
    print(f"Batch stats:")
    print(f"  Attempted: {result['batch_stats']['batches_attempted']}")
    print(f"  Succeeded: {result['batch_stats']['batches_succeeded']}")
    print(f"  Failed: {result['batch_stats']['batches_failed']}")
    print(f"  Rate limits hit: {result['batch_stats']['rate_limits_hit']}")
    print()

    success_rate = result['real_data_count'] / result['total_symbols']
    if success_rate >= 0.7:  # At least 70% with proxies
        print(f"✓ PROXY TEST PASSED - {success_rate*100:.0f}% real data retrieved")
        return True
    else:
        print(f"✗ PROXY TEST MARGINAL - Only {success_rate*100:.0f}% real data")
        print("\nThis may be normal if:")
        print("  - Proxies are slow or getting blocked")
        print("  - Need to fetch fresh proxies")
        return False


if __name__ == '__main__':
    print("\nQuick Scanner Test Suite")
    print("=" * 70)

    # Test 1: No proxies (baseline)
    test1_passed = test_without_proxies()

    # Test 2: With proxies (if baseline passed)
    if test1_passed:
        test2_passed = test_with_proxies()
    else:
        print("\nSkipping proxy test since baseline test failed")
        print("Fix the basic connectivity issue first")
        test2_passed = False

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Basic functionality (no proxy): {'PASS' if test1_passed else 'FAIL'}")
    if test1_passed:
        print(f"Proxy functionality: {'PASS' if test2_passed else 'MARGINAL'}")
    print("=" * 70)

    sys.exit(0 if test1_passed else 1)
