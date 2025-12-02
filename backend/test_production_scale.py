#!/usr/bin/env python3
"""
Production-scale test: Verify <3 minute runtime with 95%+ accuracy on 3000+ stocks
"""

import sys
import os
import time
import csv

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from optimized_9600_scanner import OptimizedScanner, ScannerConfig
import logging

# Set up logging
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

def test_production_scale():
    """Test with production-scale ticker count"""
    print("=" * 70)
    print("PRODUCTION-SCALE TEST")
    print("Target: <3 minutes with 95%+ accuracy for 3000+ stocks")
    print("=" * 70)
    print()

    # Load tickers
    ticker_file = 'data/combined_tickers_20251105_145319.csv'
    test_sizes = [500, 1000, 3000]

    for size in test_sizes:
        print(f"\n{'='*70}")
        print(f"TEST: {size} stocks")
        print(f"{'='*70}\n")

        tickers = load_tickers(ticker_file, limit=size)
        print(f"Loaded {len(tickers)} tickers from {ticker_file}")
        print(f"Sample: {', '.join(tickers[:10])}...")
        print()

        # Configure for production
        config = ScannerConfig()
        config.USE_PROXIES = True
        config.MAX_PROXIES_TO_USE = 2000  # Use all available proxies
        config.BATCH_SIZE = 10  # Optimized batch size
        config.MAX_WORKERS = 100  # High parallelism
        config.REQUEST_TIMEOUT = 2.0  # Fast timeout
        config.MAX_RETRIES = 4  # Aggressive retries
        config.ENABLE_SIMULATION = False  # Real data only

        print(f"Scanner config:")
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
        print(f"RESULTS: {size} stocks")
        print("=" * 70)
        print(f"Total symbols: {result['total_symbols']}")
        print(f"Real data: {result['real_data_count']}")
        print(f"Success rate: {result['success_percentage']}")
        print(f"Duration: {duration:.2f}s ({duration/60:.2f} min)")
        print(f"Rate: {result['rate_per_second']:.1f} stocks/sec")
        print()

        # Check targets
        success_rate = float(result['success_percentage'].rstrip('%'))
        passes_quality = success_rate >= 95.0
        passes_time = duration < 180  # <3 minutes

        print("TARGET CHECKS:")
        print(f"  Quality (≥95%): {'✓ PASS' if passes_quality else '✗ FAIL'} ({success_rate:.1f}%)")
        print(f"  Runtime (<180s): {'✓ PASS' if passes_time else '✗ FAIL'} ({duration:.1f}s)")

        # Estimate full dataset time
        if size < 7000:
            estimated_full_time = (duration / size) * 7000
            print(f"\nEstimated time for 7000 stocks: {estimated_full_time:.1f}s ({estimated_full_time/60:.1f} min)")

        print("=" * 70)

        # Wait between tests
        if size < test_sizes[-1]:
            print("\n[WAIT] Waiting 10 seconds before next test...")
            time.sleep(10)

    print("\n" + "=" * 70)
    print("PRODUCTION TEST COMPLETE")
    print("=" * 70)

if __name__ == '__main__':
    test_production_scale()
