#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rate-Limit Aware Stock Scanner

Implements:
1. Exponential backoff with retries
2. Adaptive rate limiting (slows down when 429 detected)
3. Reduced concurrency to avoid triggering rate limits
4. Progress tracking and ETA

Target: 5193 tickers in <180 seconds with >95% success rate
Strategy: Balance speed with rate limit avoidance
"""

import os
import sys
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import threading

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
    max_workers: int = 30  # Start conservatively
    max_retries: int = 3
    base_delay: float = 0.5  # Base delay for exponential backoff
    rate_limit_backoff: float = 2.0  # Seconds to wait after rate limit
    target_tickers: int = 5193
    target_seconds: int = 180
    adaptive_slowdown: bool = True  # Slow down if rate limits detected

CONFIG = Config()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RateLimitManager:
    """Manage rate limiting across threads"""

    def __init__(self):
        self.rate_limited = False
        self.rate_limit_count = 0
        self.lock = threading.Lock()
        self.last_rate_limit = None

    def mark_rate_limited(self):
        """Mark that we hit a rate limit"""
        with self.lock:
            self.rate_limited = True
            self.rate_limit_count += 1
            self.last_rate_limit = time.time()
            logger.warning(f"Rate limit detected! Count: {self.rate_limit_count}")

    def should_slow_down(self) -> bool:
        """Check if we should slow down due to rate limiting"""
        with self.lock:
            if not self.rate_limited:
                return False

            # If we hit rate limit in last 5 seconds, slow down
            if self.last_rate_limit and (time.time() - self.last_rate_limit) < 5:
                return True

            # If we've hit many rate limits, keep slowing down
            if self.rate_limit_count > 10:
                return True

            return False

    def get_delay(self) -> float:
        """Get appropriate delay based on rate limiting"""
        with self.lock:
            if not self.rate_limited:
                return 0

            # Adaptive delay based on how many rate limits we've hit
            if self.rate_limit_count < 5:
                return 0.5
            elif self.rate_limit_count < 20:
                return 1.0
            else:
                return 2.0


rate_limit_manager = RateLimitManager()


class Metrics:
    """Track performance metrics"""

    def __init__(self):
        self.start_time = None
        self.processed = 0
        self.successful = 0
        self.failed = 0
        self.rate_limited = 0
        self.fast_info_success = 0
        self.info_success = 0
        self.retries_used = 0
        self.lock = threading.Lock()

    def start(self):
        self.start_time = time.time()

    def record_success(self, method: str, retries: int = 0):
        with self.lock:
            self.processed += 1
            self.successful += 1
            self.retries_used += retries
            if method == 'fast_info':
                self.fast_info_success += 1
            else:
                self.info_success += 1

    def record_failure(self, is_rate_limit: bool = False):
        with self.lock:
            self.processed += 1
            self.failed += 1
            if is_rate_limit:
                self.rate_limited += 1

    def get_progress(self):
        with self.lock:
            elapsed = time.time() - self.start_time if self.start_time else 0
            rate = self.processed / elapsed if elapsed > 0 else 0
            success_rate = self.successful / self.processed if self.processed > 0 else 0

            return {
                'elapsed': elapsed,
                'processed': self.processed,
                'successful': self.successful,
                'failed': self.failed,
                'rate_limited': self.rate_limited,
                'rate': rate,
                'success_rate': success_rate,
                'eta': (CONFIG.target_tickers - self.processed) / rate if rate > 0 else 0
            }


metrics = Metrics()


def fetch_ticker_with_retry(ticker: str) -> Optional[Dict]:
    """Fetch data for a single ticker with retry logic"""

    for attempt in range(CONFIG.max_retries):
        # Check if we should slow down
        if rate_limit_manager.should_slow_down():
            delay = rate_limit_manager.get_delay()
            time.sleep(delay)

        try:
            ticker_obj = yf.Ticker(ticker)

            # Try fast_info first
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
                    metrics.record_success('fast_info', retries=attempt)
                    return data

            except Exception as e:
                error_msg = str(e).lower()
                if 'rate limit' in error_msg or '429' in error_msg:
                    rate_limit_manager.mark_rate_limited()
                    # Wait before retry
                    if attempt < CONFIG.max_retries - 1:
                        backoff_time = CONFIG.rate_limit_backoff * (2 ** attempt)
                        logger.debug(f"Rate limited on {ticker}, waiting {backoff_time:.1f}s before retry")
                        time.sleep(backoff_time)
                        continue

            # Fallback to info
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
                    metrics.record_success('info', retries=attempt)
                    return data

            except Exception as e:
                error_msg = str(e).lower()
                if 'rate limit' in error_msg or '429' in error_msg:
                    rate_limit_manager.mark_rate_limited()
                    if attempt < CONFIG.max_retries - 1:
                        backoff_time = CONFIG.rate_limit_backoff * (2 ** attempt)
                        logger.debug(f"Rate limited on {ticker}, waiting {backoff_time:.1f}s before retry")
                        time.sleep(backoff_time)
                        continue

            # If we got here without success and have retries left, try again
            if attempt < CONFIG.max_retries - 1:
                backoff_time = CONFIG.base_delay * (2 ** attempt)
                time.sleep(backoff_time)

        except Exception as e:
            logger.debug(f"Error on {ticker} (attempt {attempt+1}): {e}")
            if attempt < CONFIG.max_retries - 1:
                backoff_time = CONFIG.base_delay * (2 ** attempt)
                time.sleep(backoff_time)

    # All retries exhausted
    is_rate_limit = rate_limit_manager.should_slow_down()
    metrics.record_failure(is_rate_limit=is_rate_limit)
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
    """Process a batch of tickers with adaptive concurrency"""

    saved = 0
    max_workers = CONFIG.max_workers

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_ticker_with_retry, ticker): ticker for ticker in tickers}

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
                    f"Rate limited: {metrics.rate_limited} | "
                    f"ETA: {progress['eta']:.0f}s"
                )

                # Adaptive slowdown warning
                if rate_limit_manager.should_slow_down():
                    logger.warning("Adaptive slowdown active due to rate limiting")

    return saved


def main():
    """Main execution"""

    logger.info("="*70)
    logger.info("RATE-LIMIT AWARE STOCK SCANNER")
    logger.info("="*70)
    logger.info(f"Target: {CONFIG.target_tickers} tickers in {CONFIG.target_seconds}s")
    logger.info(f"Workers: {CONFIG.max_workers}")
    logger.info(f"Max retries: {CONFIG.max_retries}")
    logger.info(f"Strategy: Exponential backoff with adaptive rate limiting")
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
    logger.info("\nStarting scan...\n")

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
    logger.info(f"Rate limited: {metrics.rate_limited}")
    logger.info(f"Retries used: {metrics.retries_used}")
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

    logger.info("")
    logger.info("Rate Limiting Summary:")
    logger.info(f"  Total rate limit hits: {rate_limit_manager.rate_limit_count}")
    logger.info(f"  Tickers affected: {metrics.rate_limited}")
    logger.info(f"  Adaptive slowdown triggered: {'Yes' if rate_limit_manager.rate_limit_count > 0 else 'No'}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\nScan interrupted by user")
    except Exception as e:
        logger.error(f"\nError during scan: {e}")
        import traceback
        traceback.print_exc()
