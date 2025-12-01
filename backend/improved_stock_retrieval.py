#!/usr/bin/env python3
"""
Improved Stock Retrieval - Optimized for 95%+ success, <180s runtime
Key fixes:
- NO proxies by default (avoids 401 errors)
- Small batch sizes (100) for reliability
- High parallelism (30 workers)
- Aggressive timeouts and retry logic
"""

import os
import sys
import time
import logging
import argparse
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed
import math
import random

import pandas as pd
import yfinance as yf

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Quiet noisy loggers
for name in ('yfinance', 'yfinance.scrapers', 'peewee', 'urllib3'):
    logging.getLogger(name).setLevel(logging.ERROR)


def safe_decimal(value: Any) -> Optional[Decimal]:
    """Safely convert to Decimal"""
    if value is None or pd.isna(value):
        return None
    try:
        if isinstance(value, (int, float)):
            if math.isfinite(float(value)):
                return Decimal(str(value))
        return Decimal(str(value))
    except Exception:
        return None


def load_tickers_from_files() -> List[str]:
    """Load tickers from data directory"""
    import glob
    import importlib.util

    tickers = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')

    for subdir in ['nasdaq_only', 'complete_nasdaq']:
        pattern = os.path.join(data_dir, subdir, '*_tickers_*.py')
        files = sorted(glob.glob(pattern))
        if files:
            latest = files[-1]
            try:
                spec = importlib.util.spec_from_file_location("tickers_mod", latest)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

                for var_name in ['NASDAQ_ONLY_TICKERS', 'COMPLETE_NASDAQ_TICKERS', 'TICKERS']:
                    if hasattr(mod, var_name):
                        data = getattr(mod, var_name)
                        if isinstance(data, list):
                            tickers.extend([str(x).strip().upper() for x in data if str(x).strip()])
                            break
            except Exception as e:
                logger.warning(f"Failed to load {latest}: {e}")

    # De-duplicate
    seen = set()
    unique = []
    for t in tickers:
        if t and t not in seen:
            seen.add(t)
            unique.append(t)

    return unique


def fetch_ticker_fast(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Fetch single ticker using minimal yfinance calls
    Returns None if failed, otherwise dict with data
    """
    try:
        # Add tiny random delay to avoid rate limiting
        time.sleep(random.uniform(0.001, 0.005))

        ticker = yf.Ticker(symbol)

        # Use fast_info (fastest method)
        try:
            fi = ticker.fast_info
            if not fi:
                return None

            def get_val(key: str) -> Optional[float]:
                try:
                    v = fi.get(key)
                    return float(v) if v is not None else None
                except Exception:
                    return None

            price = get_val('lastPrice') or get_val('regularMarketPrice') or get_val('previousClose')
            if not price:
                return None

            volume = get_val('regularMarketVolume') or get_val('volume')
            market_cap = get_val('marketCap')

            return {
                'ticker': symbol,
                'symbol': symbol,
                'current_price': safe_decimal(price),
                'volume': int(volume) if volume else None,
                'market_cap': int(market_cap) if market_cap else None,
                'days_low': safe_decimal(get_val('dayLow')),
                'days_high': safe_decimal(get_val('dayHigh')),
                'week_52_low': safe_decimal(get_val('yearLow')),
                'week_52_high': safe_decimal(get_val('yearHigh')),
                'pe_ratio': safe_decimal(get_val('trailingPE')),
                'company_name': symbol,
                'name': symbol,
                'exchange': 'NASDAQ'
            }
        except Exception:
            return None

    except Exception:
        return None


def process_batch_parallel(symbols: List[str], batch_id: int) -> tuple:
    """Process batch of tickers in parallel"""
    results = {}
    failed = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_ticker_fast, sym): sym for sym in symbols}
        for future in as_completed(futures):
            sym = futures[future]
            try:
                data = future.result(timeout=5)
                if data:
                    results[sym] = data
                else:
                    failed.append(sym)
            except Exception:
                failed.append(sym)

    return batch_id, results, failed


def run_improved_scan(symbols: List[str], batch_size: int = 100,
                     max_workers: int = 30) -> Dict[str, Any]:
    """
    Run improved scan with small batches and high parallelism

    Args:
        symbols: List of ticker symbols
        batch_size: Tickers per batch (100 for reliability)
        max_workers: Parallel batch workers (30 for speed)
    """
    start_time = time.time()

    logger.info(f"Starting scan of {len(symbols)} tickers...")
    logger.info(f"Batch size: {batch_size}, Workers: {max_workers}")

    # Split into batches
    batches = [symbols[i:i+batch_size] for i in range(0, len(symbols), batch_size)]
    logger.info(f"Created {len(batches)} batches")

    # Process batches in parallel
    all_results = {}
    all_failed = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_batch_parallel, batch, i): i
                   for i, batch in enumerate(batches)}

        completed = 0
        for future in as_completed(futures):
            batch_id = futures[future]
            try:
                _, results, failed = future.result(timeout=60)
                all_results.update(results)
                all_failed.extend(failed)
                completed += 1

                if completed % 5 == 0 or completed == len(batches):
                    logger.info(f"Progress: {completed}/{len(batches)} batches, "
                              f"{len(all_results)} successful")
            except Exception as e:
                logger.error(f"Batch {batch_id} failed: {e}")

    # Retry failed tickers once
    if all_failed:
        logger.info(f"Retrying {len(all_failed)} failed tickers...")
        retry_results = {}
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(fetch_ticker_fast, sym): sym for sym in all_failed}
            for future in as_completed(futures):
                sym = futures[future]
                try:
                    data = future.result(timeout=5)
                    if data:
                        retry_results[sym] = data
                except Exception:
                    pass
        all_results.update(retry_results)
        logger.info(f"Recovered {len(retry_results)} tickers on retry")

    elapsed = time.time() - start_time
    success_rate = len(all_results) / len(symbols) * 100 if symbols else 0

    return {
        'results': all_results,
        'total': len(symbols),
        'successful': len(all_results),
        'failed': len(symbols) - len(all_results),
        'success_rate': round(success_rate, 2),
        'elapsed': round(elapsed, 2),
        'rate_per_sec': round(len(symbols) / elapsed, 2) if elapsed > 0 else 0
    }


def save_to_csv(results: Dict[str, Dict[str, Any]], filename: str):
    """Save results to CSV"""
    if not results:
        logger.warning("No results to save")
        return

    rows = []
    for symbol, data in results.items():
        row = {k: (float(v) if isinstance(v, Decimal) else v) for k, v in data.items()}
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)
    logger.info(f"Saved {len(df)} records to {filename}")


def main():
    parser = argparse.ArgumentParser(description='Improved Stock Retrieval')
    parser.add_argument('--batch-size', type=int, default=100)
    parser.add_argument('--workers', type=int, default=30)
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--output', type=str, default=None)

    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("IMPROVED STOCK RETRIEVAL")
    logger.info("Target: 95%+ success, <180s runtime")
    logger.info("=" * 70)

    # Load tickers
    symbols = load_tickers_from_files()
    if args.limit:
        symbols = symbols[:args.limit]

    logger.info(f"Loaded {len(symbols)} tickers\n")

    # Run scan
    result = run_improved_scan(symbols, args.batch_size, args.workers)

    # Print results
    logger.info("\n" + "=" * 70)
    logger.info("RESULTS")
    logger.info("=" * 70)
    logger.info(f"Total:         {result['total']}")
    logger.info(f"Successful:    {result['successful']}")
    logger.info(f"Failed:        {result['failed']}")
    logger.info(f"Success Rate:  {result['success_rate']}%")
    logger.info(f"Elapsed:       {result['elapsed']}s")
    logger.info(f"Rate:          {result['rate_per_sec']} tickers/sec")
    logger.info("=" * 70)

    # Check requirements
    meets_success = result['success_rate'] >= 95
    meets_runtime = result['elapsed'] <= 180

    logger.info("\nRequirements Check:")
    logger.info(f"  ✓ Success ≥95%: {'PASS' if meets_success else 'FAIL'} ({result['success_rate']}%)")
    logger.info(f"  ✓ Runtime ≤180s: {'PASS' if meets_runtime else 'FAIL'} ({result['elapsed']}s)")

    if meets_success and meets_runtime:
        logger.info("\n✅ ALL REQUIREMENTS MET!")
    else:
        logger.info("\n⚠️  Adjustments needed")

    # Save CSV
    if not args.output:
        args.output = f"improved_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    save_to_csv(result['results'], args.output)

    return 0 if (meets_success and meets_runtime) else 1


if __name__ == '__main__':
    sys.exit(main())
