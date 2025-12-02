#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final Optimized Stock Scanner

Optimizations:
1. No proxies (system SSL issue)
2. Let yfinance handle sessions internally (curl_cffi requirement)
3. High concurrency (50-100 workers)
4. Fast_info first with info fallback
5. Minimal delays to maximize throughput
6. Real-time progress tracking

Target: 5193 tickers in <180 seconds with >95% accuracy
"""

import os
import sys
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")

import django
django.setup()

import yfinance as yf
from django.utils import timezone as dj_timezone
from stocks.models import Stock

# Configuration
@dataclass
class Config:
    max_workers: int = 80  # High concurrency
    request_timeout: int = 6
    use_fast_info_first: bool = True
    fallback_to_info: bool = True
    target_tickers: int = 5193
    target_seconds: int = 180

CONFIG = Config()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Metrics:
    """Track performance metrics"""

    def __init__(self):
        self.start_time = None
        self.processed = 0
        self.successful = 0
        self.failed = 0
        self.fast_info_success = 0
        self.info_success = 0

    def start(self):
        self.start_time = time.time()

    def record_success(self, method: str):
        self.processed += 1
        self.successful += 1
        if method == 'fast_info':
            self.fast_info_success += 1
        else:
            self.info_success += 1

    def record_failure(self):
        self.processed += 1
        self.failed += 1

    def get_progress(self):
        elapsed = time.time() - self.start_time if self.start_time else 0
        rate = self.processed / elapsed if elapsed > 0 else 0
        success_rate = self.successful / self.processed if self.processed > 0 else 0

        return {
            'elapsed': elapsed,
            'processed': self.processed,
            'successful': self.successful,
            'failed': self.failed,
            'rate': rate,
            'success_rate': success_rate,
            'eta': (CONFIG.target_tickers - self.processed) / rate if rate > 0 else 0
        }


metrics = Metrics()


def fetch_ticker(ticker: str) -> Optional[Dict]:
    """Fetch data for a single ticker"""

    try:
        # Let yfinance handle session (curl_cffi)
        ticker_obj = yf.Ticker(ticker)

        # Try fast_info first
        if CONFIG.use_fast_info_first:
            try:
                fast_info = ticker_obj.fast_info
                data = {
                    'ticker': ticker,
                    'current_price': fast_info.last_price,
                    'volume': fast_info.last_volume,
                    'market_cap': fast_info.market_cap,
                    'day_high': fast_info.day_high,
                    'day_low': fast_info.day_low,
                    'year_high': fast_info.year_high,
                    'year_low': fast_info.year_low,
                    'method': 'fast_info'
                }

                if data['current_price'] and data['current_price'] > 0:
                    metrics.record_success('fast_info')
                    return data

            except Exception:
                pass

        # Fallback to info
        if CONFIG.fallback_to_info:
            try:
                info = ticker_obj.info
                data = {
                    'ticker': ticker,
                    'current_price': info.get('currentPrice') or info.get('regularMarketPrice'),
                    'volume': info.get('volume'),
                    'market_cap': info.get('marketCap'),
                    'day_high': info.get('dayHigh'),
                    'day_low': info.get('dayLow'),
                    'year_high': info.get('fiftyTwoWeekHigh'),
                    'year_low': info.get('fiftyTwoWeekLow'),
                    'method': 'info'
                }

                if data['current_price'] and data['current_price'] > 0:
                    metrics.record_success('info')
                    return data

            except Exception:
                pass

        metrics.record_failure()
        return None

    except Exception as e:
        metrics.record_failure()
        logger.debug(f"Failed {ticker}: {e}")
        return None


def save_to_database(data: Dict):
    """Save stock data to database"""

    try:
        now = dj_timezone.now()

        # Calculate dollar volume
        dvav = (data['current_price'] * data['volume']) if data['volume'] else 0

        Stock.objects.update_or_create(
            ticker=data['ticker'],
            defaults={
                'current_price': data['current_price'],
                'volume': data['volume'],
                'market_cap': data['market_cap'],
                'day_high': data['day_high'],
                'day_low': data['day_low'],
                'week_52_high': data['year_high'],
                'week_52_low': data['year_low'],
                'dvav': dvav,
                'last_updated': now,
            }
        )
        return True

    except Exception as e:
        logger.error(f"Error saving {data['ticker']}: {e}")
        return False


def process_batch(tickers: List[str]) -> int:
    """Process a batch of tickers"""

    saved = 0

    with ThreadPoolExecutor(max_workers=CONFIG.max_workers) as executor:
        futures = {executor.submit(fetch_ticker, ticker): ticker for ticker in tickers}

        for future in as_completed(futures):
            data = future.result()

            if data:
                if save_to_database(data):
                    saved += 1

            # Print progress every 50 tickers
            if metrics.processed % 50 == 0:
                progress = metrics.get_progress()
                logger.info(
                    f"Progress: {metrics.processed}/{CONFIG.target_tickers} | "
                    f"Success: {progress['success_rate']*100:.1f}% | "
                    f"Rate: {progress['rate']:.1f}/s | "
                    f"ETA: {progress['eta']:.0f}s"
                )

    return saved


def main():
    """Main execution"""

    logger.info("="*70)
    logger.info("FINAL OPTIMIZED STOCK SCANNER")
    logger.info("="*70)
    logger.info(f"Target: {CONFIG.target_tickers} tickers in {CONFIG.target_seconds}s")
    logger.info(f"Workers: {CONFIG.max_workers}")
    logger.info(f"Strategy: fast_info first, info fallback")
    logger.info("")

    # Get all tickers from database
    logger.info("Loading tickers from database...")
    tickers = list(Stock.objects.all().values_list('ticker', flat=True))
    logger.info(f"Loaded {len(tickers)} tickers")

    if len(tickers) > CONFIG.target_tickers:
        tickers = tickers[:CONFIG.target_tickers]
        logger.info(f"Limited to {CONFIG.target_tickers} tickers")

    # Start processing
    metrics.start()
    logger.info("\nStarting scan...")

    # Process all tickers
    total_saved = process_batch(tickers)

    # Final statistics
    progress = metrics.get_progress()

    logger.info("\n" + "="*70)
    logger.info("SCAN COMPLETE")
    logger.info("="*70)
    logger.info(f"Runtime: {progress['elapsed']:.1f}s ({progress['elapsed']/60:.2f} min)")
    logger.info(f"Processed: {metrics.processed}")
    logger.info(f"Successful: {metrics.successful}")
    logger.info(f"Failed: {metrics.failed}")
    logger.info(f"Saved to database: {total_saved}")
    logger.info(f"Success rate: {progress['success_rate']*100:.1f}%")
    logger.info(f"Throughput: {progress['rate']:.2f} tickers/sec")
    logger.info("")
    logger.info(f"Fast_info successes: {metrics.fast_info_success}")
    logger.info(f"Info fallback successes: {metrics.info_success}")

    # Check if we met targets
    target_met = progress['elapsed'] <= CONFIG.target_seconds
    accuracy_met = progress['success_rate'] >= 0.95

    logger.info("")
    if target_met and accuracy_met:
        logger.info("[SUCCESS] All targets met!")
    else:
        if not target_met:
            logger.info(f"[WARN] Runtime target missed by {progress['elapsed'] - CONFIG.target_seconds:.1f}s")
        if not accuracy_met:
            logger.info(f"[WARN] Accuracy target missed: {progress['success_rate']*100:.1f}% < 95%")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\nScan interrupted by user")
    except Exception as e:
        logger.error(f"\nError during scan: {e}")
        import traceback
        traceback.print_exc()
