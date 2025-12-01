#!/usr/bin/env python3
"""
Ultra-Fast Stock Scanner - Optimized for <180s runtime with 95%+ success
Strategy: Minimal proxy use, aggressive batch downloads, parallel processing
"""

import os
import sys
import time
import logging
from typing import List, Dict, Any
from datetime import datetime

# Import the existing fast scanner's classes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fast_stock_scanner import (
    StockScanner, load_combined_tickers, logger as base_logger
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Quiet yfinance logs
for name in ('yfinance', 'yfinance.scrapers', 'peewee'):
    logging.getLogger(name).setLevel(logging.ERROR)


def run_ultra_fast_scan(limit: int = None) -> Dict[str, Any]:
    """
    Run ultra-fast stock scan optimized for speed and reliability

    Args:
        limit: Optional limit on number of tickers

    Returns:
        Dict with results and statistics
    """
    start_time = time.time()

    logger.info("=" * 70)
    logger.info("ULTRA-FAST STOCK SCANNER")
    logger.info("Target: 95%+ success rate, <180s for ~6200 tickers")
    logger.info("=" * 70)

    # Load tickers
    logger.info("Loading tickers...")
    symbols = load_combined_tickers()

    if limit:
        symbols = symbols[:limit]

    logger.info(f"Loaded {len(symbols)} tickers")

    # Create scanner with NO proxies (proxies cause 401 errors)
    # Use aggressive threading for speed
    scanner = StockScanner(
        threads=16,  # Aggressive parallelization
        timeout=12,   # Reasonable timeout
        use_proxies=False,  # DISABLE PROXIES to avoid 401 errors
        db_enabled=False    # Disable DB writes for speed (can enable later)
    )

    # Generate output filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_out = f"ultra_fast_scan_{timestamp}.csv"

    logger.info(f"\nConfiguration:")
    logger.info(f"  Tickers: {len(symbols)}")
    logger.info(f"  Threads: 16")
    logger.info(f"  Proxies: DISABLED (avoids 401 errors)")
    logger.info(f"  Output: {csv_out}")
    logger.info("=" * 70)

    # Run scan using the optimized scan_batch method
    logger.info(f"\nStarting scan of {len(symbols)} tickers...")
    scan_result = scanner.scan_batch(
        symbols=symbols,
        csv_out=csv_out,
        chunk_size=300  # Optimal chunk size for yfinance
    )

    elapsed = time.time() - start_time

    # Print results
    logger.info("\n" + "=" * 70)
    logger.info("SCAN COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Total Tickers:     {scan_result['total']}")
    logger.info(f"Successful:        {scan_result['success']}")
    logger.info(f"Failed:            {scan_result['failed']}")
    logger.info(f"Success Rate:      {scan_result['completeness_ratio'] * 100:.1f}%")
    logger.info(f"Elapsed Time:      {elapsed:.2f}s")
    logger.info(f"Processing Rate:   {scan_result['rate_per_sec']:.2f} tickers/sec")
    logger.info(f"CSV Output:        {csv_out}")
    logger.info("=" * 70)

    # Check requirements
    success_rate = scan_result['completeness_ratio'] * 100
    meets_success = success_rate >= 95
    meets_runtime = elapsed <= 180

    logger.info(f"\nRequirements Check:")
    logger.info(f"  ✓ Success rate ≥95%: {'PASS' if meets_success else 'FAIL'} ({success_rate:.1f}%)")
    logger.info(f"  ✓ Runtime ≤180s:     {'PASS' if meets_runtime else 'FAIL'} ({elapsed:.1f}s)")

    if meets_success and meets_runtime:
        logger.info("\n✅ ALL REQUIREMENTS MET!")
    else:
        logger.info("\n⚠️  Requirements not fully met - may need further optimization")

    return {
        'success': meets_success and meets_runtime,
        'scan_result': scan_result,
        'elapsed': elapsed,
        'success_rate': success_rate,
        'csv_file': csv_out
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Ultra-Fast Stock Scanner')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of tickers (for testing)')

    args = parser.parse_args()

    result = run_ultra_fast_scan(limit=args.limit)

    return 0 if result['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
