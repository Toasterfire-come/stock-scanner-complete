#!/usr/bin/env python3
"""
Optimized Daily Scanner - yfinance
===================================
Runs during off-hours (12am-5am) when Yahoo throttling is minimal.

Target: Complete 9,060 stocks in under 3 hours (no proxies needed at night).

Features:
- No proxy overhead (minimal throttling at night)
- Optimized for speed
- Batch database updates
- Progress tracking
"""

import os
import sys
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, Optional

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")
import django
django.setup()

from django.utils import timezone as django_tz
from stocks.models import Stock

import yfinance as yf

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("daily_yfinance")

# Suppress yfinance noise
logging.getLogger("yfinance").setLevel(logging.ERROR)

# ============================================================================
# CONFIGURATION - OPTIMIZED FOR NIGHT RUNS
# ============================================================================

MAX_THREADS = 50   # Conservative - no need to hammer Yahoo at night
BATCH_SIZE = 100   # Database batch updates
TIMEOUT = 15.0     # Generous timeout

# ============================================================================
# YFINANCE FETCHER
# ============================================================================

def fetch_stock_yfinance(ticker: str) -> Optional[Dict]:
    """
    Fetch stock data using yfinance (no proxies)

    During off-hours (12am-5am), Yahoo Finance throttling is minimal.
    No need for proxies or complex auth.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or 'regularMarketPrice' not in info:
            return None

        # Extract data
        current_price = info.get('regularMarketPrice', info.get('currentPrice', 0))
        prev_close = info.get('regularMarketPreviousClose', current_price)

        if current_price == 0:
            return None

        price_change = current_price - prev_close
        price_change_percent = (price_change / prev_close * 100) if prev_close > 0 else 0

        data = {
            "ticker": ticker,
            "current_price": float(current_price),
            "price_change": float(price_change),
            "price_change_percent": float(price_change_percent),
            "volume": int(info.get('volume', 0)),
            "days_low": float(info.get('dayLow', current_price)),
            "days_high": float(info.get('dayHigh', current_price)),
            "bid_price": float(info.get('bid', 0)) if info.get('bid') else None,
            "ask_price": float(info.get('ask', 0)) if info.get('ask') else None,
            "last_updated": django_tz.now(),
        }

        return data

    except Exception as e:
        logger.debug(f"{ticker}: {str(e)[:100]}")
        return None

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def batch_update_stocks(data_list: list) -> tuple:
    """Update stocks in database"""
    updated = 0
    failed = 0

    for data in data_list:
        try:
            ticker = data["ticker"]
            Stock.objects.filter(ticker=ticker).update(
                current_price=data["current_price"],
                price_change=data["price_change"],
                price_change_percent=data["price_change_percent"],
                volume=data["volume"],
                days_low=data["days_low"],
                days_high=data["days_high"],
                bid_price=data["bid_price"],
                ask_price=data["ask_price"],
                last_updated=data["last_updated"],
            )
            updated += 1
        except Exception as e:
            logger.error(f"Failed to update {data.get('ticker', 'UNKNOWN')}: {e}")
            failed += 1

    return updated, failed

# ============================================================================
# MAIN SCANNER
# ============================================================================

def run_daily_scanner():
    """Run optimized daily scanner (no proxies, designed for off-hours)"""

    start_time = time.time()

    logger.info("="*80)
    logger.info("DAILY YFINANCE SCANNER - OPTIMIZED FOR OFF-HOURS")
    logger.info("="*80)
    logger.info(f"Best run time: 12:00 AM - 5:00 AM (minimal throttling)")
    logger.info(f"Current time: {datetime.now().strftime('%I:%M %p')}")
    logger.info(f"Threads: {MAX_THREADS} (conservative)")
    logger.info(f"No proxies needed at night")
    logger.info("")

    # Load tickers
    logger.info("Loading tickers from database...")
    tickers = list(Stock.objects.values_list('ticker', flat=True))
    logger.info(f"Loaded {len(tickers)} tickers")
    logger.info("")

    # Check if it's a good time to run
    current_hour = datetime.now().hour
    if not (0 <= current_hour <= 5):
        logger.warning("⚠️  WARNING: Running outside recommended hours (12am-5am)")
        logger.warning("⚠️  May experience higher throttling rates")
        logger.info("")

    # Scan with threading
    logger.info(f"Starting scan with {MAX_THREADS} threads...")
    logger.info("")

    results = []
    success_count = 0
    failed_count = 0

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

                # Progress update every 500 tickers
                if i % 500 == 0:
                    elapsed = time.time() - start_time
                    rate = i / elapsed
                    remaining = len(tickers) - i
                    eta = remaining / rate if rate > 0 else 0
                    success_rate = (success_count / i) * 100

                    logger.info(
                        f"Progress: {i}/{len(tickers)} ({i/len(tickers)*100:.1f}%) | "
                        f"Success: {success_count} ({success_rate:.1f}%) | "
                        f"Failed: {failed_count} | "
                        f"Rate: {rate:.1f} t/s | "
                        f"ETA: {eta/60:.1f} min"
                    )

                # Batch database updates
                if len(results) >= BATCH_SIZE:
                    updated, db_failed = batch_update_stocks(results)
                    logger.info(f"Database: Updated {updated} stocks")
                    results = []

            except Exception as e:
                logger.error(f"Error processing {ticker}: {e}")
                failed_count += 1

    # Final batch update
    if results:
        updated, db_failed = batch_update_stocks(results)
        logger.info(f"Database: Updated {updated} stocks (final batch)")

    # Summary
    elapsed = time.time() - start_time

    logger.info("")
    logger.info("="*80)
    logger.info("SCAN COMPLETE")
    logger.info("="*80)
    logger.info(f"Total tickers: {len(tickers)}")
    logger.info(f"Successful: {success_count} ({success_count/len(tickers)*100:.1f}%)")
    logger.info(f"Failed: {failed_count} ({failed_count/len(tickers)*100:.1f}%)")
    logger.info(f"Total time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
    logger.info(f"Average rate: {len(tickers)/elapsed:.1f} tickers/second")
    logger.info("="*80)

    # Check if we met target
    if elapsed <= 10800:  # 3 hours = 10800 seconds
        logger.info("✓ Target met: Completed in under 3 hours")
    else:
        logger.warning(f"⚠️ Target missed: Took {elapsed/3600:.1f} hours (target: 3 hours)")

if __name__ == "__main__":
    run_daily_scanner()
