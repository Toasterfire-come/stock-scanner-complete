#!/usr/bin/env python3
"""
Optimized Stock Retrieval Script
Targets: 95%+ success rate, <180s runtime for 2000 tickers
Strategy: Batch processing with yfinance, smart error handling, no proxies by default
"""

import os
import sys
import time
import json
import logging
import argparse
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed
import math

import pandas as pd
import yfinance as yf

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Quiet yfinance logs
for name in ('yfinance', 'yfinance.scrapers', 'yfinance.data', 'peewee'):
    logging.getLogger(name).setLevel(logging.ERROR)


def safe_decimal(value: Any) -> Optional[Decimal]:
    """Safely convert value to Decimal"""
    if value is None or pd.isna(value):
        return None
    try:
        if isinstance(value, (int, float)):
            if math.isfinite(float(value)):
                return Decimal(str(value))
        return Decimal(str(value))
    except Exception:
        return None


def load_combined_tickers() -> List[str]:
    """Load tickers from data directory (NASDAQ + NYSE)"""
    import glob
    import importlib.util

    tickers = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')

    # Load NASDAQ tickers
    for subdir in ['nasdaq_only', 'complete_nasdaq']:
        pattern = os.path.join(data_dir, subdir, '*_tickers_*.py')
        files = sorted(glob.glob(pattern))
        if files:
            latest = files[-1]
            try:
                spec = importlib.util.spec_from_file_location("tickers_mod", latest)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

                # Try different variable names
                for var_name in ['NASDAQ_ONLY_TICKERS', 'COMPLETE_NASDAQ_TICKERS', 'TICKERS']:
                    if hasattr(mod, var_name):
                        data = getattr(mod, var_name)
                        if isinstance(data, list):
                            tickers.extend([str(x).strip().upper() for x in data if str(x).strip()])
                            logger.info(f"Loaded {len(data)} tickers from {os.path.basename(latest)}")
                            break
            except Exception as e:
                logger.warning(f"Failed to load {latest}: {e}")

    # De-duplicate while preserving order
    seen = set()
    unique_tickers = []
    for t in tickers:
        if t and t not in seen:
            seen.add(t)
            unique_tickers.append(t)

    logger.info(f"Total unique tickers: {len(unique_tickers)}")
    return unique_tickers


def batch_download_tickers(symbols: List[str], period: str = '5d',
                           timeout: int = 30) -> Dict[str, Dict[str, Any]]:
    """
    Download data for multiple tickers at once using yf.download
    Returns dict mapping symbol -> data dict
    """
    results = {}

    try:
        # Download batch data
        df = yf.download(
            tickers=symbols,
            period=period,
            interval='1d',
            group_by='ticker',
            auto_adjust=False,
            progress=False,
            threads=False,
            timeout=timeout
        )

        if df is None or df.empty:
            return results

        # Handle multi-ticker response
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

                # Get last valid row
                last_row = ticker_df.iloc[-1]

                # Extract OHLCV data
                close = last_row.get('Close')
                high = last_row.get('High')
                low = last_row.get('Low')
                volume = last_row.get('Volume')

                if pd.isna(close) or pd.isna(volume):
                    continue

                # Calculate change if we have previous close
                change_percent = None
                if len(ticker_df) >= 2:
                    try:
                        prev_close = ticker_df.iloc[-2]['Close']
                        if not pd.isna(prev_close) and float(prev_close) != 0:
                            change_percent = ((float(close) - float(prev_close)) / float(prev_close)) * 100.0
                    except Exception:
                        pass

                results[symbol] = {
                    'ticker': symbol,
                    'symbol': symbol,
                    'current_price': safe_decimal(close),
                    'days_high': safe_decimal(high),
                    'days_low': safe_decimal(low),
                    'volume': int(volume) if not pd.isna(volume) else None,
                    'change_percent': safe_decimal(change_percent),
                }

            except Exception as e:
                logger.debug(f"Error processing {symbol}: {e}")
                continue

    except Exception as e:
        logger.error(f"Batch download failed for {len(symbols)} symbols: {e}")

    return results


def enrich_with_fast_info(symbol: str, base_data: Dict[str, Any], timeout: int = 5) -> Dict[str, Any]:
    """Enrich ticker data with fast_info for additional fields"""
    try:
        ticker = yf.Ticker(symbol)
        fast_info = ticker.fast_info

        if not fast_info:
            return base_data

        # Helper to get float value safely
        def get_float(key: str) -> Optional[float]:
            try:
                val = fast_info.get(key)
                return float(val) if val is not None else None
            except Exception:
                return None

        # Enrich with additional fields
        market_cap = get_float('marketCap')
        if market_cap:
            base_data['market_cap'] = int(market_cap)

        shares = get_float('shares')
        if shares:
            base_data['shares_available'] = int(shares)

        avg_vol = get_float('threeMonthAverageVolume') or get_float('tenDayAverageVolume')
        if avg_vol:
            base_data['avg_volume_3mon'] = int(avg_vol)

        week_52_low = get_float('yearLow')
        if week_52_low:
            base_data['week_52_low'] = safe_decimal(week_52_low)

        week_52_high = get_float('yearHigh')
        if week_52_high:
            base_data['week_52_high'] = safe_decimal(week_52_high)

        pe_ratio = get_float('trailingPE')
        if pe_ratio and math.isfinite(pe_ratio):
            base_data['pe_ratio'] = safe_decimal(pe_ratio)

        # Calculate DVAV if possible
        if base_data.get('volume') and base_data.get('avg_volume_3mon'):
            try:
                dvav = float(base_data['volume']) / float(base_data['avg_volume_3mon'])
                base_data['dvav'] = safe_decimal(dvav)
            except Exception:
                pass

        # Add company name
        base_data['company_name'] = symbol
        base_data['name'] = symbol
        base_data['exchange'] = 'NASDAQ'

    except Exception as e:
        logger.debug(f"Fast info enrichment failed for {symbol}: {e}")

    return base_data


def process_batch(symbols: List[str], batch_id: int, enrich: bool = True) -> Tuple[int, Dict[str, Dict[str, Any]]]:
    """Process a batch of symbols"""
    logger.info(f"Batch {batch_id}: Processing {len(symbols)} symbols")

    # Download batch data
    results = batch_download_tickers(symbols, period='5d', timeout=30)
    logger.info(f"Batch {batch_id}: Downloaded data for {len(results)}/{len(symbols)} symbols")

    # Enrich with fast_info if requested
    if enrich and results:
        enriched_count = 0
        for symbol in list(results.keys()):
            try:
                results[symbol] = enrich_with_fast_info(symbol, results[symbol])
                enriched_count += 1
            except Exception as e:
                logger.debug(f"Enrichment failed for {symbol}: {e}")
        logger.info(f"Batch {batch_id}: Enriched {enriched_count} symbols")

    return batch_id, results


def retry_failed_symbols(symbols: List[str], max_retries: int = 2) -> Dict[str, Dict[str, Any]]:
    """Retry failed symbols individually with multiple attempts"""
    results = {}

    for symbol in symbols:
        for attempt in range(max_retries):
            try:
                # Try batch download for single symbol
                batch_result = batch_download_tickers([symbol], period='1d', timeout=10)
                if symbol in batch_result:
                    # Enrich with fast_info
                    results[symbol] = enrich_with_fast_info(symbol, batch_result[symbol], timeout=5)
                    break
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.debug(f"Failed to retrieve {symbol} after {max_retries} attempts: {e}")
                time.sleep(0.5)

    return results


def run_optimized_scan(symbols: List[str], batch_size: int = 250,
                       max_workers: int = 24, enrich: bool = False) -> Dict[str, Any]:
    """
    Run optimized stock scan with batch processing

    Args:
        symbols: List of ticker symbols to scan
        batch_size: Number of symbols per batch (250 optimized for speed/reliability)
        max_workers: Number of parallel batch workers (24 for maximum parallelization)
        enrich: Whether to enrich with fast_info (disabled by default for speed)

    Returns:
        Dict with results and statistics
    """
    start_time = time.time()

    # Split into batches
    batches = [symbols[i:i+batch_size] for i in range(0, len(symbols), batch_size)]
    logger.info(f"Split {len(symbols)} symbols into {len(batches)} batches of ~{batch_size}")

    # Process batches in parallel
    all_results = {}
    batch_success = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_batch, batch, i, enrich): i
                   for i, batch in enumerate(batches)}

        for future in as_completed(futures):
            batch_id = futures[future]
            try:
                _, results = future.result(timeout=90)
                all_results.update(results)
                batch_success += 1
                logger.info(f"Completed batch {batch_id}: Total results = {len(all_results)}")
            except Exception as e:
                logger.error(f"Batch {batch_id} failed: {e}")

    elapsed = time.time() - start_time
    success_rate = len(all_results) / len(symbols) * 100 if symbols else 0

    logger.info(f"\nBatch processing complete:")
    logger.info(f"  Time: {elapsed:.2f}s")
    logger.info(f"  Success: {len(all_results)}/{len(symbols)} ({success_rate:.1f}%)")

    # Retry failed symbols if success rate is below target
    failed_symbols = [s for s in symbols if s not in all_results]
    if failed_symbols and success_rate < 95:
        logger.info(f"\nRetrying {len(failed_symbols)} failed symbols...")
        retry_start = time.time()
        retry_results = retry_failed_symbols(failed_symbols, max_retries=2)
        all_results.update(retry_results)
        retry_elapsed = time.time() - retry_start
        logger.info(f"Retry complete: {len(retry_results)} recovered in {retry_elapsed:.2f}s")

    total_elapsed = time.time() - start_time
    final_success_rate = len(all_results) / len(symbols) * 100 if symbols else 0

    # Calculate data quality metrics
    complete_records = sum(1 for r in all_results.values()
                          if r.get('current_price') and r.get('volume') and r.get('market_cap'))
    quality_rate = complete_records / len(all_results) * 100 if all_results else 0

    stats = {
        'total_symbols': len(symbols),
        'successful': len(all_results),
        'failed': len(symbols) - len(all_results),
        'success_rate': round(final_success_rate, 2),
        'quality_rate': round(quality_rate, 2),
        'complete_records': complete_records,
        'elapsed_seconds': round(total_elapsed, 2),
        'rate_per_second': round(len(symbols) / total_elapsed, 2) if total_elapsed > 0 else 0,
        'batch_size': batch_size,
        'max_workers': max_workers,
    }

    return {'results': all_results, 'stats': stats}


def save_to_csv(results: Dict[str, Dict[str, Any]], filename: str):
    """Save results to CSV file"""
    if not results:
        logger.warning("No results to save")
        return

    # Convert to DataFrame
    rows = []
    for symbol, data in results.items():
        row = {k: v for k, v in data.items()}
        # Convert Decimal to float for CSV
        for key, val in row.items():
            if isinstance(val, Decimal):
                row[key] = float(val)
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)
    logger.info(f"Saved {len(df)} records to {filename}")


def main():
    parser = argparse.ArgumentParser(description='Optimized Stock Retrieval Script')
    parser.add_argument('--batch-size', type=int, default=250,
                       help='Number of symbols per batch (default: 250)')
    parser.add_argument('--workers', type=int, default=24,
                       help='Number of parallel workers (default: 24)')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of symbols to process (for testing)')
    parser.add_argument('--symbols', type=str, default=None,
                       help='Comma-separated list of symbols (overrides file load)')
    parser.add_argument('--enrich', action='store_true',
                       help='Enable fast_info enrichment (slower but more data)')
    parser.add_argument('--output', type=str, default=None,
                       help='Output CSV filename')

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("OPTIMIZED STOCK RETRIEVAL SCRIPT")
    logger.info("=" * 60)

    # Load symbols
    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(',') if s.strip()]
        logger.info(f"Using provided symbols: {len(symbols)}")
    else:
        symbols = load_combined_tickers()

    if args.limit:
        symbols = symbols[:args.limit]
        logger.info(f"Limited to {len(symbols)} symbols")

    if not symbols:
        logger.error("No symbols to process!")
        return 1

    logger.info(f"\nConfiguration:")
    logger.info(f"  Symbols: {len(symbols)}")
    logger.info(f"  Batch size: {args.batch_size}")
    logger.info(f"  Workers: {args.workers}")
    logger.info(f"  Enrich: {args.enrich}")
    logger.info("=" * 60)

    # Run scan
    result = run_optimized_scan(
        symbols=symbols,
        batch_size=args.batch_size,
        max_workers=args.workers,
        enrich=args.enrich
    )

    # Print statistics
    stats = result['stats']
    logger.info("\n" + "=" * 60)
    logger.info("SCAN COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total Symbols:    {stats['total_symbols']}")
    logger.info(f"Successful:       {stats['successful']}")
    logger.info(f"Failed:           {stats['failed']}")
    logger.info(f"Success Rate:     {stats['success_rate']}%")
    logger.info(f"Quality Rate:     {stats['quality_rate']}%")
    logger.info(f"Complete Records: {stats['complete_records']}")
    logger.info(f"Elapsed Time:     {stats['elapsed_seconds']}s")
    logger.info(f"Processing Rate:  {stats['rate_per_second']} symbols/sec")
    logger.info("=" * 60)

    # Check if requirements met
    meets_success = stats['success_rate'] >= 95
    meets_runtime = stats['elapsed_seconds'] <= 180

    logger.info(f"\nRequirements Check:")
    logger.info(f"  ✓ Success rate ≥95%: {'PASS' if meets_success else 'FAIL'} ({stats['success_rate']}%)")
    logger.info(f"  ✓ Runtime ≤180s:     {'PASS' if meets_runtime else 'FAIL'} ({stats['elapsed_seconds']}s)")

    # Save results
    if args.output:
        save_to_csv(result['results'], args.output)
    else:
        # Auto-generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"stock_scan_{timestamp}.csv"
        save_to_csv(result['results'], filename)

    return 0 if (meets_success and meets_runtime) else 1


if __name__ == '__main__':
    sys.exit(main())
