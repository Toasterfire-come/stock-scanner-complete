#!/usr/bin/env python3
"""
Multi-Timeframe Historical Data Collector
==========================================

Collects historical data for backtesting across multiple timeframes:
- 1 minute
- 5 minutes
- 15 minutes
- 1 hour
- 4 hours
- 1 day

Uses the unified proxy manager for rate limit handling and automatic
proxy switching.
"""

import os
import sys
import time
import json
import logging
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unified_proxy_manager import UnifiedProxyManager
from comprehensive_ticker_list import get_all_tickers

# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress yfinance noise
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# =====================================================
# CONFIGURATION
# =====================================================

class HistoricalDataConfig:
    """Configuration for historical data collection"""

    # Timeframes to collect
    TIMEFRAMES = {
        '1m': '1m',      # 1 minute
        '5m': '5m',      # 5 minutes
        '15m': '15m',    # 15 minutes
        '1h': '1h',      # 1 hour
        '4h': '4h',      # 4 hours (calculated from 1h)
        '1d': '1d'       # 1 day
    }

    # Historical periods - at least 1 year for all timeframes
    # Note: yfinance has limits on intraday data, we'll fetch max available
    PERIODS = {
        '1m': '7d',      # 1min data: max 7 days (yfinance limit)
        '5m': '60d',     # 5min data: max 60 days (yfinance limit)
        '15m': '60d',    # 15min data: max 60 days (yfinance limit)
        '1h': '2y',      # 1hr data: 2 years (730 days)
        '1d': '5y'       # Daily data: 5 years for backtesting
    }

    # Performance settings
    max_workers = 20
    request_timeout = 10
    retry_attempts = 3
    retry_delay = 2

    # Progress
    progress_interval = 50

    # Output
    output_dir = 'historical_data'
    save_format = 'parquet'  # 'parquet' or 'csv'

CONFIG = HistoricalDataConfig()

# =====================================================
# DATA COLLECTOR
# =====================================================

class HistoricalDataCollector:
    """Collects multi-timeframe historical data with proxy management"""

    def __init__(self, proxy_manager: UnifiedProxyManager):
        self.proxy_manager = proxy_manager
        self.lock = threading.Lock()

        # Metrics
        self.total_attempted = 0
        self.success_count = 0
        self.failure_count = 0
        self.rate_limits = 0

        # Create output directory
        self.output_dir = Path(CONFIG.output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Create subdirectories for each timeframe
        for tf in CONFIG.TIMEFRAMES.keys():
            (self.output_dir / tf).mkdir(exist_ok=True)

    def fetch_historical_data(
        self,
        symbol: str,
        timeframe: str,
        worker_id: int = 0
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical data for a symbol at specific timeframe

        Args:
            symbol: Ticker symbol
            timeframe: One of '1m', '5m', '15m', '1h', '4h', '1d'
            worker_id: Worker thread ID

        Returns:
            DataFrame with OHLCV data or None if failed
        """

        try:
            # Increment request count for proxy management
            with self.lock:
                self.total_attempted += 1
                self.proxy_manager.increment_request_count()

            # Get period and interval for this timeframe
            if timeframe == '4h':
                # 4h calculated from 1h data
                interval = '1h'
                period = CONFIG.PERIODS['1h']
            else:
                interval = CONFIG.TIMEFRAMES[timeframe]
                period = CONFIG.PERIODS.get(timeframe, '1y')

            # Fetch data
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                period=period,
                interval=interval,
                timeout=CONFIG.request_timeout
            )

            if df is None or df.empty:
                with self.lock:
                    self.failure_count += 1
                return None

            # Resample to 4h if needed
            if timeframe == '4h':
                df = df.resample('4H').agg({
                    'Open': 'first',
                    'High': 'max',
                    'Low': 'min',
                    'Close': 'last',
                    'Volume': 'sum'
                }).dropna()

            # Add symbol column
            df['Symbol'] = symbol

            with self.lock:
                self.success_count += 1

            return df

        except Exception as e:
            # Check for rate limit
            if UnifiedProxyManager.detect_rate_limit(e):
                with self.lock:
                    self.rate_limits += 1
                logger.warning(f"[RATE LIMIT] {symbol} @ {timeframe} - switching proxy")
                self.proxy_manager.handle_rate_limit()

            with self.lock:
                self.failure_count += 1

            return None

    def save_data(self, df: pd.DataFrame, symbol: str, timeframe: str):
        """Save historical data to disk"""
        try:
            output_path = self.output_dir / timeframe / f"{symbol}.{CONFIG.save_format}"

            if CONFIG.save_format == 'parquet':
                df.to_parquet(output_path)
            else:
                df.to_csv(output_path)

        except Exception as e:
            logger.error(f"Failed to save {symbol} @ {timeframe}: {e}")

    def collect_timeframe(
        self,
        tickers: List[str],
        timeframe: str
    ) -> Dict[str, int]:
        """
        Collect historical data for all tickers at specific timeframe

        Returns dict with statistics
        """

        logger.info("")
        logger.info("=" * 70)
        logger.info(f"COLLECTING {timeframe.upper()} DATA")
        logger.info("=" * 70)
        logger.info(f"Tickers: {len(tickers)}")
        logger.info(f"Period: {CONFIG.PERIODS.get(timeframe, 'calculated')}")
        logger.info(f"Workers: {CONFIG.max_workers}")
        logger.info("")

        start_time = time.time()
        success = 0
        failed = 0

        with ThreadPoolExecutor(max_workers=CONFIG.max_workers) as executor:
            futures = {
                executor.submit(
                    self.fetch_historical_data,
                    ticker,
                    timeframe,
                    i % CONFIG.max_workers
                ): ticker
                for i, ticker in enumerate(tickers)
            }

            for i, future in enumerate(as_completed(futures)):
                ticker = futures[future]

                try:
                    df = future.result()

                    if df is not None and not df.empty:
                        # Save to disk
                        self.save_data(df, ticker, timeframe)
                        success += 1
                    else:
                        failed += 1

                except Exception as e:
                    logger.error(f"Error processing {ticker}: {e}")
                    failed += 1

                # Progress
                if (i + 1) % CONFIG.progress_interval == 0:
                    elapsed = time.time() - start_time
                    progress = (i + 1) / len(tickers) * 100
                    rate = (i + 1) / elapsed
                    eta = (len(tickers) - (i + 1)) / rate if rate > 0 else 0

                    logger.info(
                        f"[{i+1}/{len(tickers)}] "
                        f"{progress:.1f}% | "
                        f"Success: {success} | "
                        f"Failed: {failed} | "
                        f"Rate: {rate:.1f}/s | "
                        f"ETA: {eta:.0f}s"
                    )

        elapsed = time.time() - start_time

        logger.info("")
        logger.info("=" * 70)
        logger.info(f"{timeframe.upper()} COLLECTION COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Runtime: {elapsed:.2f}s ({elapsed/60:.2f} min)")
        logger.info(f"Success: {success}/{len(tickers)} ({success/len(tickers)*100:.1f}%)")
        logger.info(f"Failed: {failed}")
        logger.info(f"Rate: {len(tickers)/elapsed:.2f} tickers/sec")
        logger.info("=" * 70)

        return {
            'timeframe': timeframe,
            'total': len(tickers),
            'success': success,
            'failed': failed,
            'runtime': elapsed,
            'success_rate': success / len(tickers) * 100
        }

    def collect_all_timeframes(self, tickers: List[str]) -> Dict:
        """Collect data for all timeframes"""

        logger.info("=" * 70)
        logger.info("MULTI-TIMEFRAME HISTORICAL DATA COLLECTION")
        logger.info("=" * 70)
        logger.info(f"Total tickers: {len(tickers)}")
        logger.info(f"Timeframes: {', '.join(CONFIG.TIMEFRAMES.keys())}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Format: {CONFIG.save_format}")
        logger.info("=" * 70)

        # Show proxy stats
        proxy_stats = self.proxy_manager.get_stats()
        logger.info("\nProxy Configuration:")
        logger.info(f"  Total proxies: {proxy_stats['total_proxies']}")
        logger.info(f"  Working proxies: {proxy_stats['working_proxies']}")
        logger.info(f"  Current proxy: {proxy_stats['current_proxy']}")
        logger.info("")

        overall_start = time.time()
        results = {}

        # Collect each timeframe
        for timeframe in CONFIG.TIMEFRAMES.keys():
            result = self.collect_timeframe(tickers, timeframe)
            results[timeframe] = result

        overall_elapsed = time.time() - overall_start

        # Summary
        logger.info("")
        logger.info("=" * 70)
        logger.info("COLLECTION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total runtime: {overall_elapsed:.2f}s ({overall_elapsed/60:.2f} min)")
        logger.info("")
        logger.info("Timeframe Results:")

        for tf, result in results.items():
            logger.info(
                f"  {tf:>3} | "
                f"Success: {result['success']:>5} ({result['success_rate']:>5.1f}%) | "
                f"Failed: {result['failed']:>4} | "
                f"Time: {result['runtime']/60:>5.1f}min"
            )

        logger.info("")
        logger.info("Proxy Statistics:")
        final_stats = self.proxy_manager.get_stats()
        logger.info(f"  Proxy switches: {final_stats['proxy_switches']}")
        logger.info(f"  Rate limits detected: {final_stats['rate_limits_detected']}")
        logger.info(f"  Failed proxies: {final_stats['failed_proxies']}")

        logger.info("")
        logger.info(f"Data saved to: {self.output_dir}/")
        logger.info("=" * 70)

        # Save summary
        summary = {
            'generated_at': datetime.now().isoformat(),
            'total_runtime_seconds': overall_elapsed,
            'tickers_processed': len(tickers),
            'timeframes': results,
            'proxy_stats': final_stats,
            'output_directory': str(self.output_dir),
            'format': CONFIG.save_format
        }

        summary_file = self.output_dir / 'collection_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Summary saved to: {summary_file}")

        return summary

# =====================================================
# CONVENIENCE FUNCTIONS
# =====================================================

def collect_historical_data(
    tickers: List[str] = None,
    timeframes: List[str] = None,
    use_proxies: bool = True
) -> Dict:
    """
    Convenience function to collect historical data

    Args:
        tickers: List of ticker symbols (default: all from comprehensive list)
        timeframes: List of timeframes to collect (default: all)
        use_proxies: Whether to use proxy manager (default: True)

    Returns:
        Summary dict
    """

    # Load tickers if not provided
    if tickers is None:
        logger.info("Loading comprehensive ticker list...")
        tickers = get_all_tickers()
        logger.info(f"Loaded {len(tickers)} tickers")

    # Initialize proxy manager
    if use_proxies:
        proxy_manager = UnifiedProxyManager(auto_fetch=True)
        if proxy_manager.proxies:
            proxy_manager.switch_proxy(reason="initialization")
    else:
        logger.info("Running WITHOUT proxies")
        proxy_manager = UnifiedProxyManager(auto_fetch=False)

    # Create collector
    collector = HistoricalDataCollector(proxy_manager)

    # Override timeframes if specified
    if timeframes:
        original_timeframes = CONFIG.TIMEFRAMES.copy()
        CONFIG.TIMEFRAMES = {
            tf: original_timeframes[tf]
            for tf in timeframes
            if tf in original_timeframes
        }

    try:
        # Collect data
        summary = collector.collect_all_timeframes(tickers)
        return summary

    finally:
        # Cleanup
        proxy_manager.clear()

# =====================================================
# MAIN
# =====================================================

def main():
    """Main entry point"""

    import argparse

    parser = argparse.ArgumentParser(
        description='Collect multi-timeframe historical data'
    )
    parser.add_argument(
        '--timeframes',
        nargs='+',
        choices=['1m', '5m', '15m', '1h', '4h', '1d'],
        help='Timeframes to collect (default: all)'
    )
    parser.add_argument(
        '--no-proxies',
        action='store_true',
        help='Run without proxies'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=20,
        help='Number of worker threads'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='historical_data',
        help='Output directory'
    )
    parser.add_argument(
        '--format',
        choices=['parquet', 'csv'],
        default='parquet',
        help='Output format'
    )

    args = parser.parse_args()

    # Apply config
    CONFIG.max_workers = args.workers
    CONFIG.output_dir = args.output_dir
    CONFIG.save_format = args.format

    # Collect data
    summary = collect_historical_data(
        timeframes=args.timeframes,
        use_proxies=not args.no_proxies
    )

    logger.info("")
    logger.info("=" * 70)
    logger.info("HISTORICAL DATA COLLECTION COMPLETE")
    logger.info("=" * 70)

if __name__ == "__main__":
    main()
