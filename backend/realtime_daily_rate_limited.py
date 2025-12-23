#!/usr/bin/env python3
"""
Daily Scanner with Proper Rate Limiting
========================================
Target: 0.25 tickers/second (4 seconds per ticker average)
Threads: 20
Method: Add delays to enforce rate limit and avoid Yahoo Finance blocks

Key Fix: Semaphore + delay to control request rate
"""

import os
import sys
import time
import logging
import threading
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
logger = logging.getLogger("daily_rate_limited")

# Suppress yfinance noise
logging.getLogger("yfinance").setLevel(logging.ERROR)

# ============================================================================
# CONFIGURATION - RATE LIMITED FOR SAFETY
# ============================================================================

MAX_THREADS = 20           # Concurrent workers
BATCH_SIZE = 100           # Database batch updates
TIMEOUT = 15.0             # Request timeout
TARGET_RATE = 0.25         # 0.25 tickers/second = 4 seconds per ticker
DELAY_PER_REQUEST = 1 / TARGET_RATE  # 4 seconds delay per request

# Rate limiting semaphore
rate_limiter = threading.Semaphore(1)  # Only 1 request at a time
last_request_time = [time.time()]      # Mutable to share across threads

# ============================================================================
# RATE LIMITED FETCHER
# ============================================================================

def fetch_stock_rate_limited(ticker: str) -> Optional[Dict]:
    """
    Fetch stock data with rate limiting to avoid Yahoo Finance blocks

    Enforces 0.25 t/s rate by adding delays between requests
    """
    global last_request_time

    # Acquire semaphore (wait if another thread is requesting)
    with rate_limiter:
        # Calculate required delay
        elapsed_since_last = time.time() - last_request_time[0]
        if elapsed_since_last < DELAY_PER_REQUEST:
            delay_needed = DELAY_PER_REQUEST - elapsed_since_last
            time.sleep(delay_needed)

        # Update last request time
        last_request_time[0] = time.time()

        # Now make the actual request
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
                "volume": int(info.get('volume', 0)) if info.get('volume') else None,
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
                volume=data.get("volume"),
                days_low=data["days_low"],
                days_high=data["days_high"],
                bid_price=data.get("bid_price"),
                ask_price=data.get("ask_price"),
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

def run_daily_scanner_rate_limited():
    """Run daily scanner with proper rate limiting"""

    start_time = time.time()

    logger.info("="*80)
    logger.info("DAILY SCANNER - RATE LIMITED VERSION")
    logger.info("="*80)
    logger.info(f"Target rate: {TARGET_RATE} tickers/second")
    logger.info(f"Delay per request: {DELAY_PER_REQUEST:.1f} seconds")
    logger.info(f"Current time: {datetime.now().strftime('%I:%M:%S %p')}")
    logger.info(f"Threads: {MAX_THREADS} (sequential requests with rate limit)")
    logger.info("")

    # Load tickers
    logger.info("Loading tickers from database...")
    tickers = list(Stock.objects.values_list('ticker', flat=True))
    logger.info(f"Loaded {len(tickers)} tickers")

    # Estimate time
    estimated_time = len(tickers) * DELAY_PER_REQUEST
    logger.info(f"Estimated time: {estimated_time/3600:.1f} hours at {TARGET_RATE} t/s")
    logger.info("")

    # Scan with threading (but rate-limited)
    logger.info(f"Starting rate-limited scan...")
    logger.info("")

    results = []
    success_count = 0
    failed_count = 0

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_ticker = {
            executor.submit(fetch_stock_rate_limited, ticker): ticker
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

                # Progress update every 100 tickers
                if i % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = i / elapsed if elapsed > 0 else 0
                    remaining = len(tickers) - i
                    eta = remaining / rate if rate > 0 else 0
                    success_rate = (success_count / i) * 100

                    logger.info(
                        f"Progress: {i}/{len(tickers)} ({i/len(tickers)*100:.1f}%) | "
                        f"Success: {success_count} ({success_rate:.1f}%) | "
                        f"Failed: {failed_count} | "
                        f"Rate: {rate:.3f} t/s | "
                        f"ETA: {eta/3600:.1f}h"
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
    logger.info(f"Total time: {elapsed:.1f}s ({elapsed/3600:.1f} hours)")
    logger.info(f"Average rate: {len(tickers)/elapsed:.3f} tickers/second")
    logger.info("="*80)

    # Check targets
    actual_rate = len(tickers)/elapsed
    if abs(actual_rate - TARGET_RATE) / TARGET_RATE < 0.2:  # Within 20%
        logger.info(f"[SUCCESS] Rate within target ({actual_rate:.3f} ~= {TARGET_RATE} t/s)")
    else:
        logger.warning(f"[WARN] Rate off target ({actual_rate:.3f} vs {TARGET_RATE} t/s)")

    if success_count / len(tickers) >= 0.95:
        logger.info(f"[SUCCESS] Excellent success rate (>95%)")
    else:
        logger.warning(f"[WARN] Low success rate ({success_count/len(tickers)*100:.1f}%)")

if __name__ == "__main__":
    run_daily_scanner_rate_limited()
