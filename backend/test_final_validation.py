#!/usr/bin/env python3
"""
Final validation test - 3000+ stocks to confirm production targets
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

def main():
    """Run final validation with 3000 stocks"""
    print("=" * 80)
    print("FINAL VALIDATION TEST - 3000 STOCKS")
    print("Confirm production targets: 95%+ quality, <3 minute runtime")
    print("=" * 80)
    print()

    ticker_file = 'data/combined_tickers_20251105_145319.csv'
    test_size = 3000

    tickers = load_tickers(ticker_file, limit=test_size)
    print(f"Testing with {len(tickers)} stocks")
    print(f"Sample: {', '.join(tickers[:10])}...")
    print()

    # Production configuration - optimized for speed and quality
    config = ScannerConfig()
    config.USE_PROXIES = True  # Use proxies for better rate limits
    config.MAX_PROXIES_TO_USE = 1000  # Top 1000 proxies
    config.BATCH_SIZE = 50  # Optimal batch size
    config.MAX_WORKERS = 15  # Balanced parallelism
    config.REQUEST_TIMEOUT = 5.0
    config.MAX_RETRIES = 3
    config.ENABLE_SIMULATION = False

    print(f"Production Config:")
    print(f"  Batch size: {config.BATCH_SIZE}")
    print(f"  Workers: {config.MAX_WORKERS}")
    print(f"  Proxies: {config.MAX_PROXIES_TO_USE}")
    print(f"  Retries: {config.MAX_RETRIES}")
    print()

    # Run scan
    print("Starting scan...")
    start = time.time()
    scanner = OptimizedScanner(config)
    result = scanner.scan(symbols=tickers, write_db=False)
    duration = time.time() - start

    # Results
    print("\n" + "=" * 80)
    print("FINAL VALIDATION RESULTS")
    print("=" * 80)
    print(f"Total symbols processed: {result['total_symbols']}")
    print(f"Real data retrieved: {result['real_data_count']}")
    print(f"Success rate: {result['success_percentage']}")
    print(f"Duration: {duration:.2f}s ({duration/60:.2f} min)")
    print(f"Throughput: {result['rate_per_second']:.1f} stocks/sec")
    print()

    # Analyze results
    success_rate = float(result['success_percentage'].rstrip('%'))
    passes_quality = success_rate >= 95.0
    passes_time = duration < 180

    print("=" * 80)
    print("TARGET VALIDATION")
    print("=" * 80)
    print(f"Quality Target (≥95%):    {'✓ PASS' if passes_quality else '✗ FAIL'}  ({success_rate:.2f}%)")
    print(f"Runtime Target (<180s):   {'✓ PASS' if passes_time else '✗ FAIL'}  ({duration:.1f}s / 3.0min)")
    print()

    # Extrapolate to full dataset
    estimated_time_7k = (duration / result['total_symbols']) * 7000
    print("FULL DATASET PROJECTION (7000 stocks):")
    print(f"  Estimated time: {estimated_time_7k:.1f}s ({estimated_time_7k/60:.1f} min)")
    print(f"  Expected quality: ~{success_rate:.1f}%")
    print()

    # Final verdict
    if passes_quality and passes_time:
        print("=" * 80)
        print("✓✓✓ VALIDATION PASSED ✓✓✓")
        print("Scanner meets all production requirements!")
        print("=" * 80)
        return 0
    elif passes_quality:
        print("⚠ PARTIAL SUCCESS - Quality good, speed needs work")
        return 1
    elif passes_time:
        print("⚠ PARTIAL SUCCESS - Speed good, quality needs work")
        return 1
    else:
        print("✗ VALIDATION FAILED - Both targets missed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
