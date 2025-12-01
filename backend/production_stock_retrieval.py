#!/usr/bin/env python3
"""
Production Stock Retrieval - Final optimized version
Target: 95%+ success rate, <180s for 2000 tickers

Key strategy:
- Use yf.download() batch method (most reliable)
- Moderate parallelism (10 workers) to avoid rate limits
- Batch size 200 (optimal for yfinance)
- NO proxies (they cause 401 errors)
- Aggressive retry logic
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

import pandas as pd
import yfinance as yf

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Quiet noisy loggers
for name in ('yfinance', 'yfinance.scrapers', 'peewee', 'urllib3', 'yfinance.data'):
    logging.getLogger(name).setLevel(logging.CRITICAL)


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


def load_tickers() -> List[str]:
    """Load tickers from data files"""
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
                spec = importlib.util.spec_from_file_location("mod", latest)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

                for var in ['NASDAQ_ONLY_TICKERS', 'COMPLETE_NASDAQ_TICKERS', 'TICKERS']:
                    if hasattr(mod, var):
                        data = getattr(mod, var)
                        if isinstance(data, list):
                            tickers.extend([str(x).strip().upper() for x in data if str(x).strip()])
                            break
            except Exception:
                pass

    # De-duplicate
    return list(dict.fromkeys([t for t in tickers if t]))


def download_batch(symbols: List[str], retry_delay: float = 2.0) -> Dict[str, Dict[str, Any]]:
    """Download batch using yf.download (most reliable method)"""
    results = {}

    # Add delay to avoid rate limiting
    time.sleep(retry_delay)

    try:
        df = yf.download(
            tickers=symbols,
            period='1d',
            interval='1d',
            group_by='ticker',
            auto_adjust=False,
            progress=False,
            threads=False
        )

        if df is None or df.empty:
            return results

        is_multi = isinstance(df.columns, pd.MultiIndex)

        for symbol in symbols:
            try:
                if is_multi:
                    if symbol not in df.columns.get_level_values(0):
                        continue
                    ticker_df = df[symbol]
                else:
                    ticker_df = df

                if ticker_df is None or ticker_df.empty:
                    continue

                last = ticker_df.iloc[-1]
                close = last.get('Close')
                volume = last.get('Volume')

                if pd.isna(close) or pd.isna(volume):
                    continue

                results[symbol] = {
                    'ticker': symbol,
                    'symbol': symbol,
                    'current_price': safe_decimal(close),
                    'days_high': safe_decimal(last.get('High')),
                    'days_low': safe_decimal(last.get('Low')),
                    'volume': int(volume) if not pd.isna(volume) else None,
                    'company_name': symbol,
                    'name': symbol,
                    'exchange': 'NASDAQ'
                }

            except Exception:
                continue

    except Exception:
        pass

    return results


def process_batch_with_retry(symbols: List[str], batch_id: int) -> tuple:
    """Process batch with retry logic"""
    results = download_batch(symbols, retry_delay=1.0)

    # Retry failed symbols individually
    failed = [s for s in symbols if s not in results]
    if failed and len(failed) < 50:  # Only retry if not too many failures
        time.sleep(2.0)  # Delay before retry to avoid rate limits
        retry_results = download_batch(failed, retry_delay=1.5)
        results.update(retry_results)

    return batch_id, results


def run_production_scan(symbols: List[str], batch_size: int = 200,
                       max_workers: int = 10) -> Dict[str, Any]:
    """
    Run production-quality scan

    Args:
        symbols: Ticker symbols to scan
        batch_size: Batch size (200 optimal)
        max_workers: Parallel workers (10 to avoid rate limits)
    """
    start_time = time.time()

    logger.info(f"Scanning {len(symbols)} tickers...")
    logger.info(f"Batch size: {batch_size}, Workers: {max_workers}")

    # Create batches
    batches = [symbols[i:i+batch_size] for i in range(0, len(symbols), batch_size)]
    logger.info(f"Created {len(batches)} batches\n")

    # Process batches
    all_results = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_batch_with_retry, batch, i): i
                   for i, batch in enumerate(batches)}

        completed = 0
        for future in as_completed(futures):
            try:
                _, results = future.result(timeout=90)
                all_results.update(results)
                completed += 1

                if completed % 2 == 0 or completed == len(batches):
                    logger.info(f"Progress: {completed}/{len(batches)} batches "
                              f"→ {len(all_results)} successful")
            except Exception as e:
                logger.error(f"Batch failed: {e}")

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


def save_csv(results: Dict[str, Dict[str, Any]], filename: str):
    """Save to CSV"""
    if not results:
        return

    rows = []
    for data in results.values():
        row = {k: (float(v) if isinstance(v, Decimal) else v) for k, v in data.items()}
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)
    logger.info(f"Saved {len(df)} records to {filename}")


def main():
    parser = argparse.ArgumentParser(description='Production Stock Retrieval')
    parser.add_argument('--batch-size', type=int, default=200)
    parser.add_argument('--workers', type=int, default=10)
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--output', type=str, default=None)

    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("PRODUCTION STOCK RETRIEVAL")
    logger.info("=" * 70)

    # Load tickers
    symbols = load_tickers()
    if args.limit:
        symbols = symbols[:args.limit]

    logger.info(f"Loaded {len(symbols)} tickers\n")

    # Run scan
    result = run_production_scan(symbols, args.batch_size, args.workers)

    # Results
    logger.info("\n" + "=" * 70)
    logger.info("RESULTS")
    logger.info("=" * 70)
    logger.info(f"Total:          {result['total']}")
    logger.info(f"Successful:     {result['successful']}")
    logger.info(f"Failed:         {result['failed']}")
    logger.info(f"Success Rate:   {result['success_rate']}%")
    logger.info(f"Elapsed:        {result['elapsed']}s")
    logger.info(f"Rate:           {result['rate_per_sec']} tickers/sec")
    logger.info("=" * 70)

    # Check requirements
    meets_success = result['success_rate'] >= 95
    meets_runtime = result['elapsed'] <= 180

    logger.info("\nRequirements:")
    logger.info(f"  Success ≥95%: {'✓ PASS' if meets_success else '✗ FAIL'} ({result['success_rate']}%)")
    logger.info(f"  Runtime ≤180s: {'✓ PASS' if meets_runtime else '✗ FAIL'} ({result['elapsed']}s)")

    if meets_success and meets_runtime:
        logger.info("\n✅ ALL REQUIREMENTS MET!")
    else:
        logger.info("\n⚠️  Some requirements not met")

    # Save
    if not args.output:
        args.output = f"stock_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    save_csv(result['results'], args.output)

    return 0 if (meets_success and meets_runtime) else 1


if __name__ == '__main__':
    sys.exit(main())
