#!/usr/bin/env python3
"""
Rate-Limited Daily Scanner Runner
==================================
Runs the daily scanner in controlled chunks from 12am-9am to handle rate limits.

Features:
- Splits 8,782 stocks into manageable batches
- Adds delays between batches to avoid rate limiting
- Monitors progress and logs execution
- Automatically adjusts timing to complete within 9-hour window
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import List

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")
import django
django.setup()

from stocks.models import Stock
from realtime_daily_yfinance import fetch_stock_yfinance, batch_update_stocks

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("daily_scanner_scheduled")

# Suppress yfinance noise
logging.getLogger("yfinance").setLevel(logging.ERROR)

# ============================================================================
# CONFIGURATION - RATE LIMIT AWARE
# ============================================================================

TOTAL_RUNTIME_HOURS = 9  # 12am to 9am
STOCKS_PER_BATCH = 500   # Process 500 stocks per batch
DELAY_BETWEEN_BATCHES = 60  # 60 seconds between batches (rate limit safety)
MAX_THREADS = 30  # Conservative threading to avoid overwhelming Yahoo

# ============================================================================
# BATCH PROCESSOR
# ============================================================================

def process_batch(tickers: List[str], batch_num: int, total_batches: int) -> tuple:
    """Process a single batch of tickers with rate limiting"""

    logger.info("=" * 70)
    logger.info(f"BATCH {batch_num}/{total_batches} - Processing {len(tickers)} stocks")
    logger.info("=" * 70)

    from concurrent.futures import ThreadPoolExecutor, as_completed

    results = []
    success_count = 0
    failed_count = 0
    batch_start = time.time()

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_ticker = {
            executor.submit(fetch_stock_yfinance, ticker): ticker
            for ticker in tickers
        }

        for i, future in enumerate(as_completed(future_to_ticker), 1):
            ticker = future_to_ticker[future]

            try:
                data = future.result()

                if data:
                    results.append(data)
                    success_count += 1
                else:
                    failed_count += 1

                # Progress update every 100 stocks within batch
                if i % 100 == 0:
                    elapsed = time.time() - batch_start
                    rate = i / elapsed if elapsed > 0 else 0
                    logger.info(
                        f"  Progress: {i}/{len(tickers)} | "
                        f"Success: {success_count} | "
                        f"Failed: {failed_count} | "
                        f"Rate: {rate:.1f} stocks/s"
                    )

            except Exception as e:
                logger.error(f"Error processing {ticker}: {e}")
                failed_count += 1

    # Update database
    updated = 0
    if results:
        updated, db_failed = batch_update_stocks(results)
        logger.info(f"✓ Database updated: {updated} stocks")

    batch_elapsed = time.time() - batch_start
    logger.info(f"✓ Batch completed in {batch_elapsed:.1f}s")
    logger.info(f"✓ Success rate: {(success_count/len(tickers)*100):.1f}%")

    return success_count, failed_count

# ============================================================================
# MAIN RUNNER
# ============================================================================

def run_scheduled_daily_scanner():
    """Run daily scanner with rate limiting over 9-hour window"""

    overall_start = time.time()
    current_time = datetime.now()

    logger.info("=" * 70)
    logger.info("SCHEDULED DAILY SCANNER - RATE LIMIT AWARE")
    logger.info("=" * 70)
    logger.info(f"Start time: {current_time.strftime('%Y-%m-%d %I:%M:%S %p')}")
    logger.info(f"Target window: 12:00 AM - 9:00 AM ({TOTAL_RUNTIME_HOURS} hours)")
    logger.info(f"Batch size: {STOCKS_PER_BATCH} stocks")
    logger.info(f"Delay between batches: {DELAY_BETWEEN_BATCHES}s")
    logger.info(f"Max threads per batch: {MAX_THREADS}")
    logger.info("")

    # Check if we're in the recommended time window
    current_hour = current_time.hour
    if not (0 <= current_hour < 9):
        logger.warning("⚠️  WARNING: Running outside recommended hours (12am-9am)")
        logger.warning("⚠️  May experience higher rate limiting")
        logger.info("")

    # Load all tickers
    logger.info("Loading tickers from database...")
    all_tickers = list(Stock.objects.values_list('ticker', flat=True))
    total_stocks = len(all_tickers)
    logger.info(f"✓ Loaded {total_stocks:,} tickers")
    logger.info("")

    # Calculate batches
    total_batches = (total_stocks + STOCKS_PER_BATCH - 1) // STOCKS_PER_BATCH
    estimated_time = (total_batches * DELAY_BETWEEN_BATCHES) / 3600  # hours

    logger.info(f"Total batches: {total_batches}")
    logger.info(f"Estimated time: {estimated_time:.1f} hours (including delays)")

    if estimated_time > TOTAL_RUNTIME_HOURS:
        logger.warning(f"⚠️  WARNING: Estimated time ({estimated_time:.1f}h) exceeds target ({TOTAL_RUNTIME_HOURS}h)")
        logger.warning(f"⚠️  Consider reducing DELAY_BETWEEN_BATCHES or increasing STOCKS_PER_BATCH")

    logger.info("")

    # Process batches
    total_success = 0
    total_failed = 0

    for batch_num in range(1, total_batches + 1):
        # Get batch tickers
        start_idx = (batch_num - 1) * STOCKS_PER_BATCH
        end_idx = min(start_idx + STOCKS_PER_BATCH, total_stocks)
        batch_tickers = all_tickers[start_idx:end_idx]

        # Process batch
        success, failed = process_batch(batch_tickers, batch_num, total_batches)
        total_success += success
        total_failed += failed

        # Delay before next batch (except after last batch)
        if batch_num < total_batches:
            logger.info(f"⏸  Waiting {DELAY_BETWEEN_BATCHES}s before next batch (rate limit cooldown)...")
            logger.info("")
            time.sleep(DELAY_BETWEEN_BATCHES)

    # Final summary
    overall_elapsed = time.time() - overall_start

    logger.info("")
    logger.info("=" * 70)
    logger.info("SCAN COMPLETE")
    logger.info("=" * 70)
    logger.info(f"End time: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
    logger.info(f"Total stocks: {total_stocks:,}")
    logger.info(f"Successful: {total_success:,} ({total_success/total_stocks*100:.1f}%)")
    logger.info(f"Failed: {total_failed:,} ({total_failed/total_stocks*100:.1f}%)")
    logger.info(f"Total runtime: {overall_elapsed/3600:.2f} hours ({overall_elapsed/60:.1f} minutes)")
    logger.info(f"Average rate: {total_stocks/overall_elapsed:.1f} stocks/second")
    logger.info("=" * 70)

    # Check completion status
    completion_rate = (total_success / total_stocks) * 100
    if completion_rate >= 95:
        logger.info("✓ EXCELLENT: >95% completion rate")
    elif completion_rate >= 90:
        logger.info("✓ GOOD: 90-95% completion rate")
    elif completion_rate >= 80:
        logger.warning("⚠️  FAIR: 80-90% completion rate - check for rate limiting")
    else:
        logger.error("✗ POOR: <80% completion rate - rate limiting or connectivity issues")

    if overall_elapsed/3600 <= TOTAL_RUNTIME_HOURS:
        logger.info(f"✓ Completed within target window ({TOTAL_RUNTIME_HOURS} hours)")
    else:
        logger.warning(f"⚠️  Exceeded target window: {overall_elapsed/3600:.1f}h > {TOTAL_RUNTIME_HOURS}h")

    logger.info("=" * 70)

if __name__ == "__main__":
    run_scheduled_daily_scanner()
