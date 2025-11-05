#!/usr/bin/env python3
"""
High-Throughput Stock Retrieval System
Target: 6200 tickers in <180 seconds with 95%+ success rate

Architecture:
- Proxy rotation across 50+ working proxies
- 50+ concurrent workers for maximum parallelization
- Small batch sizes (50 tickers) for reliability and speed
- Multiple session pooling to avoid rate limits
- Intelligent retry with proxy rotation on failures
- Aggressive timeouts for fast failure recovery
"""

import os
import sys
import time
import json
import logging
import argparse
import random
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import math

import pandas as pd
import yfinance as yf
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Quiet noisy loggers
for name in ('yfinance', 'yfinance.scrapers', 'peewee', 'urllib3', 'yfinance.data'):
    logging.getLogger(name).setLevel(logging.ERROR)


class ProxyRotator:
    """Thread-safe proxy rotation manager"""

    def __init__(self, proxy_file: str = 'working_proxies.json'):
        self.proxies = self._load_proxies(proxy_file)
        self.index = 0
        self.lock = Lock()
        self.failed_proxies = set()
        logger.info(f"Loaded {len(self.proxies)} proxies")

    def _load_proxies(self, proxy_file: str) -> List[str]:
        """Load proxies from JSON file"""
        try:
            with open(proxy_file, 'r') as f:
                data = json.load(f)
            proxies = data.get('proxies', [])
            return [p for p in proxies if p and isinstance(p, str)]
        except Exception as e:
            logger.error(f"Failed to load proxies: {e}")
            return []

    def get_proxy(self) -> Optional[str]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None

        with self.lock:
            # Skip failed proxies
            attempts = 0
            while attempts < len(self.proxies):
                proxy = self.proxies[self.index % len(self.proxies)]
                self.index += 1

                if proxy not in self.failed_proxies:
                    return proxy

                attempts += 1

            return None  # All proxies failed

    def mark_failed(self, proxy: str):
        """Mark proxy as failed"""
        with self.lock:
            self.failed_proxies.add(proxy)

    def get_working_count(self) -> int:
        """Get count of working proxies"""
        return len(self.proxies) - len(self.failed_proxies)


class SessionPool:
    """Pool of HTTP sessions with different proxies"""

    def __init__(self, proxy_rotator: ProxyRotator, pool_size: int = 20):
        self.proxy_rotator = proxy_rotator
        self.sessions = []
        self.lock = Lock()

        # Create session pool
        for _ in range(pool_size):
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            self.sessions.append(session)

        logger.info(f"Created session pool with {pool_size} sessions")

    def get_session_with_proxy(self) -> tuple:
        """Get a session and assign a proxy"""
        with self.lock:
            session = random.choice(self.sessions)

        proxy = self.proxy_rotator.get_proxy()
        if proxy:
            session.proxies = {'http': proxy, 'https': proxy}
        else:
            session.proxies = {}

        return session, proxy


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

    return list(dict.fromkeys([t for t in tickers if t]))


def fetch_batch_fast(symbols: List[str], session_pool: SessionPool,
                     max_retries: int = 3, use_proxy: bool = True) -> Dict[str, Dict[str, Any]]:
    """
    Fetch batch of tickers using yf.download with session and proxy rotation
    Falls back to no-proxy if proxies fail
    """
    results = {}

    for attempt in range(max_retries):
        try:
            # Use proxy for first 2 attempts, then fallback to no proxy
            if use_proxy and attempt < 2:
                session, proxy = session_pool.get_session_with_proxy()
            else:
                # Fallback: no proxy
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                proxy = None

            # Small delay to avoid hammering
            time.sleep(0.05 if attempt == 0 else 0.2)

            df = yf.download(
                tickers=symbols,
                period='1d',
                interval='1d',
                group_by='ticker',
                auto_adjust=False,
                progress=False,
                threads=False,
                session=session if proxy else None  # Use session only with proxy
            )

            if df is None or df.empty:
                if attempt < max_retries - 1:
                    time.sleep(0.5)
                    continue
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

            # Success - break retry loop
            break

        except Exception as e:
            if 'rate limit' in str(e).lower() or '429' in str(e):
                # Rate limited - wait longer
                time.sleep(2.0)

            if attempt < max_retries - 1:
                time.sleep(1.0)
                continue

    return results


def process_batch_parallel(batch_info: tuple, session_pool: SessionPool, use_proxy: bool = True) -> tuple:
    """Process batch with parallel execution"""
    batch_id, symbols = batch_info
    results = fetch_batch_fast(symbols, session_pool, max_retries=3, use_proxy=use_proxy)
    return batch_id, results


def run_high_throughput_scan(symbols: List[str],
                             batch_size: int = 50,
                             max_workers: int = 50,
                             session_pool_size: int = 30,
                             use_proxies: bool = True) -> Dict[str, Any]:
    """
    Run high-throughput scan with aggressive parallelization

    Args:
        symbols: Ticker symbols to scan
        batch_size: Tickers per batch (50 for speed+reliability)
        max_workers: Parallel workers (50+ for high throughput)
        session_pool_size: Size of session pool (30 for diversity)
    """
    start_time = time.time()

    logger.info("=" * 70)
    logger.info("HIGH-THROUGHPUT STOCK RETRIEVAL")
    logger.info(f"Target: {len(symbols)} tickers in <180s with proxies")
    logger.info("=" * 70)

    # Initialize proxy rotator and session pool
    proxy_rotator = ProxyRotator()
    session_pool = SessionPool(proxy_rotator, pool_size=session_pool_size)

    logger.info(f"\nConfiguration:")
    logger.info(f"  Tickers: {len(symbols)}")
    logger.info(f"  Batch size: {batch_size}")
    logger.info(f"  Workers: {max_workers}")
    logger.info(f"  Session pool: {session_pool_size}")
    logger.info(f"  Proxies available: {len(proxy_rotator.proxies)}")
    logger.info("=" * 70)

    # Create batches
    batches = [(i, symbols[i:i+batch_size])
               for i in range(0, len(symbols), batch_size)]
    logger.info(f"\nCreated {len(batches)} batches\n")

    # Process batches in parallel
    all_results = {}
    completed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_batch_parallel, batch, session_pool, use_proxies): batch[0]
                   for batch in batches}

        for future in as_completed(futures):
            try:
                batch_id, results = future.result(timeout=45)
                all_results.update(results)
                completed += 1

                if completed % 10 == 0 or completed == len(batches):
                    elapsed = time.time() - start_time
                    rate = len(all_results) / elapsed if elapsed > 0 else 0
                    logger.info(f"Progress: {completed}/{len(batches)} batches "
                              f"| {len(all_results)} successful "
                              f"| {rate:.1f} tickers/sec "
                              f"| {elapsed:.1f}s elapsed")

            except Exception as e:
                logger.error(f"Batch failed: {e}")

    elapsed = time.time() - start_time
    success_rate = len(all_results) / len(symbols) * 100 if symbols else 0

    logger.info(f"\nWorking proxies: {proxy_rotator.get_working_count()}/{len(proxy_rotator.proxies)}")

    return {
        'results': all_results,
        'total': len(symbols),
        'successful': len(all_results),
        'failed': len(symbols) - len(all_results),
        'success_rate': round(success_rate, 2),
        'elapsed': round(elapsed, 2),
        'rate_per_sec': round(len(symbols) / elapsed, 2) if elapsed > 0 else 0,
        'working_proxies': proxy_rotator.get_working_count()
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
    parser = argparse.ArgumentParser(description='High-Throughput Stock Retrieval')
    parser.add_argument('--batch-size', type=int, default=50,
                       help='Tickers per batch (default: 50)')
    parser.add_argument('--workers', type=int, default=50,
                       help='Parallel workers (default: 50)')
    parser.add_argument('--session-pool', type=int, default=30,
                       help='Session pool size (default: 30)')
    parser.add_argument('--no-proxies', action='store_true',
                       help='Disable proxy usage (fallback mode)')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit tickers for testing')
    parser.add_argument('--output', type=str, default=None,
                       help='Output CSV filename')

    args = parser.parse_args()

    # Load tickers
    symbols = load_tickers()
    if args.limit:
        symbols = symbols[:args.limit]

    # Run scan
    result = run_high_throughput_scan(
        symbols,
        batch_size=args.batch_size,
        max_workers=args.workers,
        session_pool_size=args.session_pool,
        use_proxies=not args.no_proxies
    )

    # Results
    logger.info("\n" + "=" * 70)
    logger.info("RESULTS")
    logger.info("=" * 70)
    logger.info(f"Total:           {result['total']}")
    logger.info(f"Successful:      {result['successful']}")
    logger.info(f"Failed:          {result['failed']}")
    logger.info(f"Success Rate:    {result['success_rate']}%")
    logger.info(f"Elapsed:         {result['elapsed']}s")
    logger.info(f"Throughput:      {result['rate_per_sec']} tickers/sec")
    logger.info(f"Working Proxies: {result['working_proxies']}")
    logger.info("=" * 70)

    # Check requirements
    meets_success = result['success_rate'] >= 95
    meets_runtime = result['elapsed'] <= 180

    logger.info("\nRequirements:")
    logger.info(f"  Success ≥95%:  {'✓ PASS' if meets_success else '✗ FAIL'} ({result['success_rate']}%)")
    logger.info(f"  Runtime ≤180s: {'✓ PASS' if meets_runtime else '✗ FAIL'} ({result['elapsed']}s)")

    if meets_success and meets_runtime:
        logger.info("\n✅ ALL REQUIREMENTS MET - Ready for 3-minute intervals!")
    else:
        logger.info("\n⚠️  Optimization needed for 3-minute interval requirement")

    # Save
    if not args.output:
        args.output = f"high_throughput_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    save_csv(result['results'], args.output)

    return 0 if (meets_success and meets_runtime) else 1


if __name__ == '__main__':
    sys.exit(main())
