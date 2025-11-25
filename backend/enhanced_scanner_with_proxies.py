#!/usr/bin/env python3
"""
Enhanced Stock Scanner with Smart Proxy Support
- Automatic proxy rotation to avoid rate limits
- Fallback to direct connection if proxies fail
- Fast processing with intelligent retry logic
"""

import os
import sys
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from proxy_manager import ProxyManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Quiet noisy loggers
for name in ('yfinance', 'yfinance.scrapers', 'peewee', 'urllib3'):
    logging.getLogger(name).setLevel(logging.ERROR)


class EnhancedStockScanner:
    """
    Stock scanner with intelligent proxy support.

    Features:
    - Automatic proxy rotation
    - Rate limit avoidance
    - Fallback to direct connection
    - High-speed parallel processing
    """

    def __init__(
        self,
        use_proxies: bool = True,
        proxy_dir: str = "./proxies",
        threads: int = 16,
        timeout: int = 12
    ):
        self.use_proxies = use_proxies
        self.proxy_dir = Path(proxy_dir)
        self.threads = threads
        self.timeout = timeout

        # Initialize proxy list
        self.proxies: List[str] = []
        if use_proxies:
            self._load_proxies()

        logger.info(f"Scanner initialized: proxies={'enabled' if use_proxies else 'disabled'}, threads={threads}")

    def _load_proxies(self) -> None:
        """Load proxies from storage"""
        manager = ProxyManager(self.proxy_dir)
        self.proxies = manager.load_latest_proxies()

        if not self.proxies:
            logger.warning("No proxies found. Scanner will run without proxies.")
            self.use_proxies = False
        else:
            logger.info(f"Loaded {len(self.proxies)} proxies for rotation")

    def refresh_proxies(self, fetch_limit: int = 300, validate_limit: int = 100) -> int:
        """Fetch and validate fresh proxies"""
        logger.info("Refreshing proxy list...")
        manager = ProxyManager(self.proxy_dir)
        working_proxies = manager.refresh_proxies(
            fetch_limit=fetch_limit,
            validate_limit=validate_limit
        )

        self.proxies = [p.address for p in working_proxies]
        self.use_proxies = len(self.proxies) > 0

        return len(self.proxies)

    def scan_stocks(
        self,
        symbols: List[str],
        csv_output: Optional[str] = None,
        use_existing_scanner: bool = True
    ) -> Dict[str, Any]:
        """
        Scan stocks using the fast_stock_scanner with proxy support

        Args:
            symbols: List of stock symbols to scan
            csv_output: Optional CSV output file
            use_existing_scanner: Use the existing StockScanner class (recommended)

        Returns:
            Dictionary with scan results and statistics
        """
        if use_existing_scanner:
            return self._scan_with_existing_scanner(symbols, csv_output)
        else:
            return self._scan_with_yfinance_client(symbols, csv_output)

    def _scan_with_existing_scanner(self, symbols: List[str], csv_output: Optional[str]) -> Dict[str, Any]:
        """Use the existing fast_stock_scanner.py with proxy support"""
        try:
            from fast_stock_scanner import StockScanner
        except ImportError:
            logger.error("fast_stock_scanner not found, falling back to direct yfinance")
            return self._scan_with_yfinance_client(symbols, csv_output)

        # Setup proxy configuration if enabled
        if self.use_proxies and self.proxies:
            # Save proxies to a JSON file for the scanner to load
            import json
            proxy_file = self.proxy_dir / "active_proxies.json"
            with open(proxy_file, 'w') as f:
                json.dump(self.proxies, f)

            logger.info(f"Saved {len(self.proxies)} proxies to {proxy_file}")

            # Create scanner with proxies enabled
            scanner = StockScanner(
                threads=self.threads,
                timeout=self.timeout,
                use_proxies=True,
                db_enabled=False
            )
        else:
            # Create scanner without proxies
            scanner = StockScanner(
                threads=self.threads,
                timeout=self.timeout,
                use_proxies=False,
                db_enabled=False
            )

        # Generate output filename if not provided
        if not csv_output:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_output = f"stock_scan_{timestamp}.csv"

        # Run the scan
        logger.info(f"Starting scan of {len(symbols)} symbols...")
        start_time = time.time()

        result = scanner.scan_batch(
            symbols=symbols,
            csv_out=csv_output,
            chunk_size=300
        )

        elapsed = time.time() - start_time

        logger.info(f"Scan completed in {elapsed:.2f}s")
        logger.info(f"Success rate: {result.get('completeness_ratio', 0) * 100:.1f}%")
        logger.info(f"Output saved to: {csv_output}")

        return {
            **result,
            'elapsed': elapsed,
            'csv_file': csv_output
        }

    def _scan_with_yfinance_client(self, symbols: List[str], csv_output: Optional[str]) -> Dict[str, Any]:
        """Direct scanning using yfinance client with proxy support"""
        try:
            from stock_retrieval.yfinance_client import YFinanceFetcher
            from stock_retrieval.session_factory import ProxyPool
        except ImportError:
            logger.error("yfinance_client modules not found")
            return {'error': 'Required modules not found'}

        # Setup proxy pool
        proxy_pool = None
        if self.use_proxies and self.proxies:
            proxy_pool = ProxyPool(proxies=self.proxies, enabled=True)
            logger.info(f"Initialized proxy pool with {len(self.proxies)} proxies")

        # Create fetcher
        fetcher = YFinanceFetcher(
            proxy_pool=proxy_pool,
            max_attempts=3,
            request_timeout=float(self.timeout)
        )

        # Scan stocks
        logger.info(f"Scanning {len(symbols)} symbols with YFinanceFetcher...")
        start_time = time.time()

        results = []
        success_count = 0

        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(fetcher.fetch, symbol): symbol for symbol in symbols}

            for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
                try:
                    result = future.result()
                    if result.has_data:
                        success_count += 1
                        results.append({
                            'symbol': result.symbol,
                            'price': result.current_price,
                            'has_data': True
                        })
                    else:
                        results.append({
                            'symbol': result.symbol,
                            'has_data': False
                        })

                    if i % 100 == 0:
                        logger.info(f"Progress: {i}/{len(symbols)} ({success_count} successful)")

                except Exception as e:
                    logger.error(f"Error processing future: {e}")

        elapsed = time.time() - start_time

        # Save results if requested
        if csv_output:
            import csv
            with open(csv_output, 'w', newline='') as f:
                if results:
                    writer = csv.DictWriter(f, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
            logger.info(f"Results saved to {csv_output}")

        return {
            'total': len(symbols),
            'success': success_count,
            'failed': len(symbols) - success_count,
            'completeness_ratio': success_count / len(symbols) if symbols else 0,
            'elapsed': elapsed,
            'rate_per_sec': len(symbols) / elapsed if elapsed > 0 else 0,
            'csv_file': csv_output
        }


def load_tickers(limit: Optional[int] = None) -> List[str]:
    """Load ticker symbols from combined ticker file"""
    try:
        from fast_stock_scanner import load_combined_tickers
        symbols = load_combined_tickers()
        if limit:
            symbols = symbols[:limit]
        return symbols
    except ImportError:
        logger.warning("Could not import load_combined_tickers, using sample tickers")
        # Sample tickers for testing
        return ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX'][:limit]


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Enhanced Stock Scanner with Proxy Support')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of tickers to scan')
    parser.add_argument('--no-proxies', action='store_true',
                       help='Disable proxy usage')
    parser.add_argument('--refresh-proxies', action='store_true',
                       help='Refresh proxy list before scanning')
    parser.add_argument('--fetch-limit', type=int, default=300,
                       help='Max proxies to fetch when refreshing (default: 300)')
    parser.add_argument('--validate-limit', type=int, default=100,
                       help='Max proxies to validate when refreshing (default: 100)')
    parser.add_argument('--threads', type=int, default=16,
                       help='Number of worker threads (default: 16)')
    parser.add_argument('--output', type=str, default=None,
                       help='CSV output filename')

    args = parser.parse_args()

    # Load symbols
    logger.info("Loading stock symbols...")
    symbols = load_tickers(limit=args.limit)
    logger.info(f"Loaded {len(symbols)} symbols")

    # Initialize scanner
    scanner = EnhancedStockScanner(
        use_proxies=not args.no_proxies,
        threads=args.threads
    )

    # Refresh proxies if requested
    if args.refresh_proxies and not args.no_proxies:
        proxy_count = scanner.refresh_proxies(
            fetch_limit=args.fetch_limit,
            validate_limit=args.validate_limit
        )
        logger.info(f"Proxy refresh complete: {proxy_count} working proxies available")

        if proxy_count == 0:
            logger.warning("No working proxies found. Continuing without proxies.")

    # Run scan
    logger.info("=" * 70)
    logger.info("STARTING STOCK SCAN")
    logger.info("=" * 70)

    result = scanner.scan_stocks(
        symbols=symbols,
        csv_output=args.output
    )

    # Print summary
    logger.info("=" * 70)
    logger.info("SCAN COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Total symbols:     {result.get('total', 0)}")
    logger.info(f"Successful:        {result.get('success', 0)}")
    logger.info(f"Failed:            {result.get('failed', 0)}")
    logger.info(f"Success rate:      {result.get('completeness_ratio', 0) * 100:.1f}%")
    logger.info(f"Elapsed time:      {result.get('elapsed', 0):.2f}s")
    logger.info(f"Processing rate:   {result.get('rate_per_sec', 0):.2f} symbols/sec")
    if result.get('csv_file'):
        logger.info(f"Output file:       {result['csv_file']}")
    logger.info("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())
