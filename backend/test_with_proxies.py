#!/usr/bin/env python3
"""
Test scanner WITH proxies - using yfinance (avoiding crumb errors)
"""

import sys
import os
import time
import csv

sys.path.insert(0, os.path.dirname(__file__))

from optimized_9600_scanner import OptimizedScanner, ScannerConfig
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

def load_tickers(csv_path: str, limit: int = None) -> list:
    """Load tickers from CSV file"""
    tickers = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tickers.append(row['Symbol'])
            if limit and len(tickers) >= limit:
                break
    return tickers

def test_with_proxies():
    """Test WITH proxies using yfinance (no custom sessions)"""
    print("=" * 70)
    print("PROXY TEST - Using yfinance (avoiding crumb errors)")
    print("=" * 70)
    print()

    ticker_file = 'data/combined_tickers_20251105_145319.csv'
    test_size = 500  # Test with 500 stocks

    tickers = load_tickers(ticker_file, limit=test_size)
    print(f"Testing {len(tickers)} stocks WITH proxies")
    print(f"Sample: {', '.join(tickers[:10])}...")
    print()

    # Configure WITH proxies
    config = ScannerConfig()
    config.USE_PROXIES = True  # ENABLE PROXIES
    config.MAX_PROXIES_TO_USE = 1000  # Use top 1000 proxies
    config.BATCH_SIZE = 50  # Sweet spot batch size
    config.MAX_WORKERS = 15  # Moderate parallelism
    config.REQUEST_TIMEOUT = 5.0
    config.MAX_RETRIES = 3  # More retries with proxies
    config.ENABLE_SIMULATION = False

    print(f"Config:")
    print(f"  Batch size: {config.BATCH_SIZE}")
    print(f"  Workers: {config.MAX_WORKERS}")
    print(f"  Proxies: {config.MAX_PROXIES_TO_USE}")
    print(f"  Retries: {config.MAX_RETRIES}")
    print()

    # Run scan
    start = time.time()
    scanner = OptimizedScanner(config)
    result = scanner.scan(symbols=tickers, write_db=False)
    duration = time.time() - start

    # Results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Total symbols: {result['total_symbols']}")
    print(f"Real data: {result['real_data_count']}")
    print(f"Success rate: {result['success_percentage']}")
    print(f"Duration: {duration:.2f}s ({duration/60:.2f} min)")
    print(f"Rate: {result['rate_per_second']:.1f} stocks/sec")
    print()

    # Extrapolate to 7000 stocks
    success_rate = float(result['success_percentage'].rstrip('%'))
    estimated_time_7k = (duration / result['total_symbols']) * 7000

    print("EXTRAPOLATION TO 7000 STOCKS:")
    print(f"  Estimated time: {estimated_time_7k:.1f}s ({estimated_time_7k/60:.1f} min)")
    print(f"  Expected quality: ~{success_rate:.1f}%")
    print()

    # Check if within targets
    passes_quality = success_rate >= 95.0
    passes_time = estimated_time_7k < 180

    print("TARGET CHECKS:")
    print(f"  Quality (≥95%): {'✓ PASS' if passes_quality else '✗ FAIL'} ({success_rate:.1f}%)")
    print(f"  Est. runtime (<180s): {'✓ PASS' if passes_time else '✗ FAIL'} ({estimated_time_7k:.1f}s)")
    print()

    if passes_quality and passes_time:
        print("✓ PROXY SCANNER WORKING - Meets all targets!")
    elif passes_quality:
        print("✓ QUALITY GOOD - Need speed optimization")
    elif passes_time:
        print("✓ SPEED GOOD - Need quality improvement (test better proxies)")
    else:
        print("✗ NEEDS WORK - Both quality and speed need improvement")

    print("=" * 70)

if __name__ == '__main__':
    test_with_proxies()
