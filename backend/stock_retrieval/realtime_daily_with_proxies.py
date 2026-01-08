#!/usr/bin/env python3
"""
Daily Scanner with Proxy Rotation & Rate Limiting
==================================================
Target: 0.488 tickers/second (spread over 5 hours to avoid rate limits)
Threads: 20
Proxies: Rotate through working proxies from http_proxies.txt
Rate Limit: ~800 requests spread across proxies over 5-hour period
"""

import os
import sys
import time
import logging
from logging.handlers import TimedRotatingFileHandler
import threading
import random
import math
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, Optional, List
from decimal import Decimal, InvalidOperation

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")
import django
django.setup()

from django.utils import timezone as django_tz
from stocks.models import Stock

import yfinance as yf

def configure_logging() -> logging.Logger:
    """
    Configure logging to BOTH stdout and a file under backend/logs.

    Why:
    - If this script is run directly (not via run_daily_scanner.sh + tee),
      you still get a durable log file.
    - Time-based heartbeat logs make it obvious the scanner is working,
      even at very low target rates.
    """
    log_level = os.getenv("DAILY_SCANNER_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, log_level, logging.INFO)

    backend_dir = Path(__file__).resolve().parents[1]
    default_log_dir = backend_dir / "logs"
    log_dir = Path(os.getenv("DAILY_SCANNER_LOG_DIR", str(default_log_dir)))
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "daily_scanner.log"

    logger = logging.getLogger("daily_proxies")
    logger.setLevel(level)
    logger.propagate = False

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # Avoid duplicate handlers if module reloaded
    if not logger.handlers:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(fmt)
        stream_handler.setLevel(level)

        # Rotate daily, keep last 7 days by default
        backup_count = int(os.getenv("DAILY_SCANNER_LOG_BACKUPS", "7"))
        file_handler = TimedRotatingFileHandler(
            filename=str(log_file),
            when="midnight",
            interval=1,
            backupCount=backup_count,
            encoding="utf-8",
            utc=False,
        )
        file_handler.setFormatter(fmt)
        file_handler.setLevel(level)

        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

    # Ensure yfinance noise is suppressed
    logging.getLogger("yfinance").setLevel(logging.ERROR)

    logger.info(f"Daily scanner log file: {log_file}")
    return logger


logger = configure_logging()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def sanitize_float(value, default=None, max_value=9999999999.9999):
    """
    Sanitize float values to prevent infinity and out-of-range issues

    Args:
        value: The value to sanitize
        default: Default value if sanitization fails
        max_value: Maximum allowed value

    Returns:
        Sanitized float or default value
    """
    if value is None:
        return default

    try:
        float_val = float(value)

        # Check for infinity or NaN
        if math.isinf(float_val) or math.isnan(float_val):
            return default

        # Check for out-of-range values
        if abs(float_val) > max_value:
            return default

        return float_val
    except (ValueError, TypeError, InvalidOperation):
        return default

# ============================================================================
# CONFIGURATION
# ============================================================================

MAX_THREADS = 20
BATCH_SIZE = 100
TIMEOUT = 10.0  # Reasonable timeout for stability
TARGET_RATE = 0.488  # 0.488 tickers/second (spread over 5 hours to avoid rate limits)
DELAY_PER_REQUEST = 1 / TARGET_RATE  # ~2.05 seconds per request
USE_PROXIES = True  # Proxies enabled for rate limit distribution
PROXY_FILE = Path(__file__).parent / "http_proxies.txt"

# Rate limiting
rate_limiter = threading.Semaphore(1)
last_request_time = [time.time()]

# Proxy management
proxy_list = []
proxy_index = [0]
failed_proxies = set()
proxy_lock = threading.Lock()

# ============================================================================
# PROXY MANAGEMENT
# ============================================================================

def load_proxies() -> List[str]:
    """Load proxies from file (disabled if USE_PROXIES=False)"""
    if not USE_PROXIES:
        logger.info("Proxies disabled (USE_PROXIES=False)")
        return []

    if not PROXY_FILE or not PROXY_FILE.exists():
        logger.warning(f"Proxy file not found: {PROXY_FILE}")
        return []

    proxies = []
    with open(PROXY_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                proxies.append(line)

    logger.info(f"Loaded {len(proxies)} proxies from {PROXY_FILE.name}")
    return proxies

def get_next_proxy() -> Optional[str]:
    """Get next working proxy with rotation"""
    global proxy_list, proxy_index, failed_proxies

    if not proxy_list:
        return None

    with proxy_lock:
        attempts = 0
        max_attempts = min(20, len(proxy_list))

        while attempts < max_attempts:
            proxy = proxy_list[proxy_index[0]]
            proxy_index[0] = (proxy_index[0] + 1) % len(proxy_list)

            # Skip recently failed proxies
            if proxy not in failed_proxies:
                return proxy

            attempts += 1

        # All proxies failed, reset failed set
        if len(failed_proxies) > len(proxy_list) * 0.5:
            logger.warning(f"Resetting failed proxy tracking ({len(failed_proxies)} failed)")
            failed_proxies.clear()

        return proxy_list[proxy_index[0]] if proxy_list else None

def mark_proxy_failed(proxy: str):
    """Mark a proxy as failed"""
    global failed_proxies
    with proxy_lock:
        failed_proxies.add(proxy)

# ============================================================================
# RATE-LIMITED FETCHER WITH PROXIES
# ============================================================================

def fetch_stock_with_proxy(ticker: str) -> Optional[Dict]:
    """
    Fetch stock data using proxy rotation and rate limiting

    Key features:
    - Rate limited to 0.25 t/s
    - Rotates through working proxies
    - Falls back to no-proxy if needed
    """
    global last_request_time

    # Rate limiting
    with rate_limiter:
        elapsed_since_last = time.time() - last_request_time[0]
        if elapsed_since_last < DELAY_PER_REQUEST:
            delay_needed = DELAY_PER_REQUEST - elapsed_since_last
            time.sleep(delay_needed)

        last_request_time[0] = time.time()

        # Try with proxy first
        max_retries = 3
        for attempt in range(max_retries):
            proxy = get_next_proxy()

            try:
                if proxy:
                    # Use proxy (new yfinance API)
                    yf.set_config(proxy=f"http://{proxy}")
                    stock = yf.Ticker(ticker)
                else:
                    # No proxy available, use direct
                    yf.set_config(proxy=None)
                    stock = yf.Ticker(ticker)

                info = stock.info

                if not info or 'regularMarketPrice' not in info:
                    if proxy and attempt < max_retries - 1:
                        mark_proxy_failed(proxy)
                        continue
                    return None

                # Extract comprehensive daily data
                current_price = info.get('regularMarketPrice', info.get('currentPrice', 0))
                prev_close = info.get('regularMarketPreviousClose', current_price)

                if current_price == 0:
                    return None

                price_change = current_price - prev_close
                price_change_percent = (price_change / prev_close * 100) if prev_close > 0 else 0

                # Extract bid/ask for spread calculation (with sanitization)
                bid_price = sanitize_float(info.get('bid'))
                ask_price = sanitize_float(info.get('ask'))

                # Extract volume data for DVAV calculation
                volume = int(info.get('volume', 0)) if info.get('volume') else None
                avg_volume_3mon = int(info.get('averageVolume', 0)) if info.get('averageVolume') else None

                # Extract range data for days_range string (with sanitization)
                days_low = sanitize_float(info.get('dayLow'), default=current_price)
                days_high = sanitize_float(info.get('dayHigh'), default=current_price)

                # DERIVED FIELD CALCULATIONS
                # Calculate bid-ask spread (for liquidity analysis)
                bid_ask_spread = None
                if bid_price and ask_price and bid_price > 0 and ask_price > 0:
                    spread_value = sanitize_float(ask_price - bid_price)
                    if spread_value is not None:
                        bid_ask_spread = f"{spread_value:.4f}"

                # Calculate days_range string (for trading range visualization)
                days_range = f"{days_low:.2f} - {days_high:.2f}"

                # Calculate DVAV (Day Volume / Average Volume - momentum indicator)
                dvav = None
                if volume and avg_volume_3mon and avg_volume_3mon > 0:
                    dvav = sanitize_float(float(volume) / float(avg_volume_3mon))

                data = {
                    "ticker": ticker,
                    # Price data (with sanitization)
                    "current_price": sanitize_float(current_price),
                    "price_change": sanitize_float(price_change),
                    "price_change_percent": sanitize_float(price_change_percent),
                    "price_change_today": sanitize_float(price_change),  # Same as price_change for daily scanner

                    # Bid/Ask and range
                    "bid_price": bid_price,
                    "ask_price": ask_price,
                    "bid_ask_spread": bid_ask_spread,  # CALCULATED: ask - bid
                    "days_low": days_low,
                    "days_high": days_high,
                    "days_range": days_range,  # CALCULATED: formatted range string

                    # Volume data
                    "volume": volume,
                    "volume_today": volume,  # Same as volume for daily scanner
                    "avg_volume_3mon": avg_volume_3mon,
                    "dvav": dvav,  # CALCULATED: volume / avg_volume_3mon (sanitized)
                    "shares_available": int(info.get('sharesOutstanding', 0)) if info.get('sharesOutstanding') else None,

                    # Market data
                    "market_cap": int(info.get('marketCap', 0)) if info.get('marketCap') else None,

                    # Financial ratios (with sanitization for edge cases)
                    "pe_ratio": sanitize_float(info.get('trailingPE'), max_value=9999.9999),
                    "dividend_yield": sanitize_float(info.get('dividendYield'), max_value=1.0),  # Max 100%

                    # Target and Predictions
                    "one_year_target": sanitize_float(info.get('targetMeanPrice')),

                    # 52 week range
                    "week_52_low": sanitize_float(info.get('fiftyTwoWeekLow')),
                    "week_52_high": sanitize_float(info.get('fiftyTwoWeekHigh')),

                    # Additional metrics (with sanitization)
                    "earnings_per_share": sanitize_float(info.get('trailingEps')),
                    "book_value": sanitize_float(info.get('bookValue')),
                    "price_to_book": sanitize_float(info.get('priceToBook'), max_value=9999.9999),

                    # Basic info
                    "company_name": info.get('longName', info.get('shortName', '')),
                    "exchange": info.get('exchange', ''),

                    # Metadata
                    "last_updated": django_tz.now(),
                    "used_proxy": proxy is not None
                }

                return data

            except Exception as e:
                error_msg = str(e)
                if proxy and ('401' in error_msg or '403' in error_msg or 'timeout' in error_msg.lower()):
                    mark_proxy_failed(proxy)

                if attempt < max_retries - 1:
                    time.sleep(1)  # Wait before retry
                    continue

                logger.debug(f"{ticker}: {error_msg[:100]}")
                return None

        return None

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def batch_update_stocks(data_list: list) -> tuple:
    """Update stocks in database with comprehensive daily data"""
    updated = 0
    failed = 0

    for data in data_list:
        try:
            ticker = data["ticker"]

            # Build update dictionary dynamically (only non-None values)
            update_fields = {
                "last_updated": data["last_updated"],
            }

            # Add fields if they exist and are not None
            field_mapping = {
                # Price data
                "current_price": "current_price",
                "price_change": "price_change",
                "price_change_percent": "price_change_percent",
                "price_change_today": "price_change_today",

                # Bid/Ask and range
                "bid_price": "bid_price",
                "ask_price": "ask_price",
                "bid_ask_spread": "bid_ask_spread",
                "days_low": "days_low",
                "days_high": "days_high",
                "days_range": "days_range",

                # Volume data
                "volume": "volume",
                "volume_today": "volume_today",
                "avg_volume_3mon": "avg_volume_3mon",
                "dvav": "dvav",
                "shares_available": "shares_available",

                # Market data
                "market_cap": "market_cap",

                # Financial ratios
                "pe_ratio": "pe_ratio",
                "dividend_yield": "dividend_yield",

                # Target and predictions
                "one_year_target": "one_year_target",

                # 52 week range
                "week_52_low": "week_52_low",
                "week_52_high": "week_52_high",

                # Additional metrics
                "earnings_per_share": "earnings_per_share",
                "book_value": "book_value",
                "price_to_book": "price_to_book",

                # Basic info
                "company_name": "company_name",
                "exchange": "exchange",
            }

            for data_key, model_field in field_mapping.items():
                if data_key in data and data[data_key] is not None:
                    update_fields[model_field] = data[data_key]

            Stock.objects.filter(ticker=ticker).update(**update_fields)
            updated += 1
        except Exception as e:
            logger.error(f"Failed to update {data.get('ticker', 'UNKNOWN')}: {e}")
            failed += 1

    return updated, failed

# ============================================================================
# MAIN SCANNER
# ============================================================================

def run_daily_scanner():
    """Run daily scanner with proxy rotation and rate limiting"""
    global proxy_list

    start_time = time.time()
    last_progress_log = start_time
    progress_interval_seconds = int(os.getenv("DAILY_SCANNER_PROGRESS_INTERVAL_SECONDS", "30"))

    logger.info("="*80)
    logger.info("DAILY SCANNER - WITH PROXY ROTATION & RATE LIMITING")
    logger.info("="*80)
    logger.info(f"Target rate: {TARGET_RATE} t/s (1 request every {DELAY_PER_REQUEST:.1f}s)")
    logger.info(f"Threads: {MAX_THREADS}")
    logger.info(f"Current time: {datetime.now().strftime('%I:%M:%S %p')}")

    # Load proxies
    proxy_list = load_proxies()
    logger.info(f"Proxies loaded: {len(proxy_list)}")
    logger.info("")

    # Load tickers
    logger.info("Loading tickers from database...")
    tickers = list(Stock.objects.values_list('ticker', flat=True))
    logger.info(f"Loaded {len(tickers)} tickers")

    # Estimate time
    estimated_time = len(tickers) / TARGET_RATE
    logger.info(f"Estimated time: {estimated_time/3600:.1f} hours at {TARGET_RATE} t/s")
    logger.info(
        f"Note: at this rate, in ~2 minutes you should only expect ~{int(120 * TARGET_RATE)} tickers updated."
    )
    logger.info("")

    # Scan
    logger.info(f"Starting scan with proxy rotation...")
    logger.info("")

    results = []
    success_count = 0
    failed_count = 0
    proxy_used_count = 0

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_ticker = {
            executor.submit(fetch_stock_with_proxy, ticker): ticker
            for ticker in tickers
        }

        for i, future in enumerate(as_completed(future_to_ticker), 1):
            ticker = future_to_ticker[future]

            try:
                data = future.result()

                if data:
                    results.append(data)
                    success_count += 1
                    if data.get('used_proxy'):
                        proxy_used_count += 1
                else:
                    failed_count += 1

                # Progress update: time-based heartbeat (default every 30s) + every 100 completions
                now = time.time()
                if (i % 100 == 0) or (now - last_progress_log >= progress_interval_seconds):
                    elapsed = time.time() - start_time
                    rate = i / elapsed if elapsed > 0 else 0
                    remaining = len(tickers) - i
                    eta = remaining / rate if rate > 0 else 0
                    success_rate = (success_count / i) * 100
                    proxy_usage = (proxy_used_count / success_count * 100) if success_count > 0 else 0
                    last_progress_log = now

                    logger.info(
                        f"Progress: {i}/{len(tickers)} ({i/len(tickers)*100:.1f}%) | "
                        f"Success: {success_count} ({success_rate:.1f}%) | "
                        f"Failed: {failed_count} | "
                        f"Proxy: {proxy_usage:.0f}% | "
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
    actual_rate = len(tickers) / elapsed if elapsed > 0 else 0

    logger.info("")
    logger.info("="*80)
    logger.info("SCAN COMPLETE")
    logger.info("="*80)
    logger.info(f"Total tickers: {len(tickers)}")
    logger.info(f"Successful: {success_count} ({success_count/len(tickers)*100:.1f}%)")
    logger.info(f"Failed: {failed_count}")
    logger.info(f"Proxy usage: {proxy_used_count}/{success_count} ({proxy_used_count/success_count*100:.0f}%)")
    logger.info(f"Failed proxies: {len(failed_proxies)}")
    logger.info(f"Total time: {elapsed:.1f}s ({elapsed/3600:.1f} hours)")
    logger.info(f"Average rate: {actual_rate:.3f} t/s")
    logger.info(f"Target rate: {TARGET_RATE} t/s")
    logger.info("="*80)

    # Check results
    if success_count / len(tickers) >= 0.95:
        logger.info(f"[SUCCESS] Excellent success rate (>95%)")
    else:
        logger.warning(f"[WARN] Low success rate ({success_count/len(tickers)*100:.1f}%)")

    if abs(actual_rate - TARGET_RATE) / TARGET_RATE < 0.2:
        logger.info(f"[SUCCESS] Rate within target ({actual_rate:.3f} ~= {TARGET_RATE} t/s)")
    else:
        logger.warning(f"[WARN] Rate off target ({actual_rate:.3f} vs {TARGET_RATE} t/s)")

if __name__ == "__main__":
    run_daily_scanner()
