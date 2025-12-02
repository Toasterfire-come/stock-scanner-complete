#!/usr/bin/env python3
"""
Real-Time Price Updater
========================

Runs CONTINUOUSLY during market hours to update prices only.
Ultra-lightweight - just fetches current price, no heavy calculations.

Target: Update all 5,193 tickers every 2-3 minutes with >98% success
Strategy: ONLY fast_info.last_price with aggressive proxy rotation
"""

import os
import sys
import time
import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")

import django
django.setup()

import yfinance as yf
from django.utils import timezone
from django.db import transaction
from stocks.models import Stock

from stock_retrieval.config import StockRetrievalConfig
from stock_retrieval.ticker_loader import load_combined_tickers
from unified_proxy_manager import UnifiedProxyManager

# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress yfinance errors for cleaner output
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# =====================================================
# CONFIGURATION
# =====================================================

class RealtimeConfig:
    """Real-time price updater configuration"""

    # Workers - VERY aggressive for speed
    min_workers = 50
    max_workers = 150
    initial_workers = 100

    # Timeouts - SHORT since we only get price
    request_timeout = 3
    per_symbol_timeout = 5

    # Delays - MINIMAL for maximum speed
    min_delay = 0.001  # 1ms
    max_delay = 0.003  # 3ms

    # Progress
    progress_interval = 250

    # Database - Stream writes for real-time updates
    stream_writes = True
    batch_size = 50

    # Auto-tuning
    auto_tune = True
    tune_interval = 300
    target_success_rate = 0.98

    # Update frequency
    update_interval_seconds = 150  # 2.5 minutes

CONFIG = RealtimeConfig()

# =====================================================
# METRICS
# =====================================================

class Metrics:
    """Track updater performance"""

    def __init__(self):
        self.start_time = time.time()
        self.total_attempted = 0
        self.success = 0
        self.failures = 0
        self.updates = 0
        self.current_workers = CONFIG.initial_workers

    @property
    def elapsed(self):
        return time.time() - self.start_time

    @property
    def success_rate(self):
        if self.total_attempted == 0:
            return 0.0
        return self.success / self.total_attempted

    @property
    def throughput(self):
        if self.elapsed == 0:
            return 0.0
        return self.total_attempted / self.elapsed

    def reset(self):
        """Reset for next cycle"""
        self.start_time = time.time()
        self.total_attempted = 0
        self.success = 0
        self.failures = 0

# =====================================================
# PRICE UPDATER
# =====================================================

class PriceUpdater:
    """Ultra-fast price updater with unified proxy management"""

    def __init__(self, use_proxies=False):
        self.metrics = Metrics()
        self.lock = threading.Lock()

        # CRITICAL: Initialize proxy manager FIRST, before any yfinance usage
        if use_proxies:
            try:
                logger.info("Initializing unified proxy manager...")
                logger.info("CRITICAL: Setting proxy BEFORE any yfinance calls...")

                # Create proxy manager and fetch proxies
                self.proxy_manager = UnifiedProxyManager(auto_fetch=True)

                if self.proxy_manager.proxies:
                    # CRITICAL: Set initial proxy IMMEDIATELY before any network calls
                    self.proxy_manager.switch_proxy(reason="initialization")
                    logger.info(f"Loaded {len(self.proxy_manager.proxies)} elite proxies from Geonode")
                    logger.info(f"Current proxy: {self.proxy_manager.current_proxy}")

                    # Brief pause to ensure OS picks up environment variables
                    time.sleep(0.5)
                else:
                    logger.warning("No proxies available, running without proxies")
                    self.proxy_manager = None
            except Exception as e:
                logger.warning(f"Failed to initialize proxy manager: {e}")
                logger.info("Running WITHOUT proxies")
                self.proxy_manager = None
        else:
            self.proxy_manager = None
            logger.info("Running WITHOUT proxies (yfinance handles connections internally)")

    def fetch_price(self, symbol: str, worker_id: int = 0) -> Optional[Dict]:
        """
        Fetch current price AND volume-dependent metrics.
        This includes all metrics that change with real-time price/volume.
        """

        # Tiny delay for proxy rotation
        time.sleep(random.uniform(CONFIG.min_delay, CONFIG.max_delay))

        try:
            # Increment request count for proxy manager (if enabled)
            if self.proxy_manager:
                self.proxy_manager.increment_request_count()

            # Fetch data using yfinance
            ticker = yf.Ticker(symbol)

            # Get fast_info for real-time data
            data = ticker.fast_info

            # Current price (REQUIRED)
            price = getattr(data, 'last_price', None)

            if price:
                result = {
                    'symbol': symbol,
                    'timestamp': timezone.now(),

                    # Real-time price metrics
                    'price': float(price),
                    'previous_close': getattr(data, 'previous_close', None),
                    'open': getattr(data, 'open', None),
                    'day_high': getattr(data, 'day_high', None),
                    'day_low': getattr(data, 'day_low', None),

                    # Real-time volume metrics
                    'volume': getattr(data, 'last_volume', None),

                    # Calculated metrics that depend on current price/volume
                    'market_cap': getattr(data, 'market_cap', None),
                    'shares': getattr(data, 'shares', None),
                }

                # Calculate volume_average (price * shares for dollar volume)
                if result['price'] and result['shares']:
                    result['volume_average'] = result['price'] * result['shares']
                else:
                    result['volume_average'] = None

                # Calculate price change
                if result['price'] and result['previous_close']:
                    result['price_change'] = result['price'] - result['previous_close']
                    result['price_change_percent'] = ((result['price'] - result['previous_close']) / result['previous_close']) * 100
                else:
                    result['price_change'] = None
                    result['price_change_percent'] = None

                # Calculate day range percent
                if result['day_high'] and result['day_low'] and result['day_low'] != 0:
                    result['day_range_percent'] = ((result['day_high'] - result['day_low']) / result['day_low']) * 100
                else:
                    result['day_range_percent'] = None

                with self.lock:
                    self.metrics.success += 1

                return result
            else:
                with self.lock:
                    self.metrics.failures += 1
                return None

        except Exception as e:
            # Check for rate limit and handle proxy switching
            if self.proxy_manager and UnifiedProxyManager.detect_rate_limit(e):
                logger.warning(f"[RATE LIMIT] Detected for {symbol}, switching proxy...")
                self.proxy_manager.handle_rate_limit()

            with self.lock:
                self.metrics.failures += 1
            return None

        finally:
            with self.lock:
                self.metrics.total_attempted += 1

    def update_prices(self, symbols: List[str]) -> List[Dict]:
        """Update prices for all symbols"""

        total = len(symbols)
        results = []
        batch = []

        logger.info(f"Updating prices for {total} tickers...")

        with ThreadPoolExecutor(max_workers=self.metrics.current_workers) as executor:
            futures = {
                executor.submit(self.fetch_price, symbol, i % self.metrics.current_workers): symbol
                for i, symbol in enumerate(symbols)
            }

            for future in as_completed(futures):
                result = future.result()

                if result:
                    results.append(result)
                    batch.append(result)

                    # Stream write in batches if enabled
                    if CONFIG.stream_writes and len(batch) >= CONFIG.batch_size:
                        self._write_batch(batch)
                        with self.lock:
                            self.metrics.updates += len(batch)
                        batch = []

                # Progress
                if self.metrics.total_attempted % CONFIG.progress_interval == 0:
                    progress = self.metrics.total_attempted / total * 100
                    elapsed = self.metrics.elapsed
                    remaining = total - self.metrics.total_attempted
                    eta = (elapsed / self.metrics.total_attempted * remaining) if self.metrics.total_attempted > 0 else 0

                    logger.info(
                        f"[{self.metrics.total_attempted}/{total}] "
                        f"{progress:.1f}% | "
                        f"Success: {self.metrics.success_rate*100:.1f}% | "
                        f"Speed: {self.metrics.throughput:.1f}/s | "
                        f"ETA: {eta:.0f}s"
                    )

                # Auto-tune
                if CONFIG.auto_tune and self.metrics.total_attempted % CONFIG.tune_interval == 0:
                    if self.metrics.success_rate < CONFIG.target_success_rate:
                        # Reduce workers if success rate is low
                        if self.metrics.current_workers > CONFIG.min_workers:
                            self.metrics.current_workers = max(
                                CONFIG.min_workers,
                                self.metrics.current_workers - 10
                            )
                            logger.info(f"Auto-tune: Reduced workers to {self.metrics.current_workers}")
                    elif self.metrics.success_rate > 0.99:
                        # Increase workers if success rate is very high
                        if self.metrics.current_workers < CONFIG.max_workers:
                            self.metrics.current_workers = min(
                                CONFIG.max_workers,
                                self.metrics.current_workers + 10
                            )
                            logger.info(f"Auto-tune: Increased workers to {self.metrics.current_workers}")

            # Write remaining batch
            if batch:
                self._write_batch(batch)
                with self.lock:
                    self.metrics.updates += len(batch)

        return results

    def _write_batch(self, batch: List[Dict]):
        """Write a batch of price and volume updates to database"""
        try:
            with transaction.atomic():
                for result in batch:
                    try:
                        # Map to actual database field names
                        update_fields = {
                            # Real-time price data (map to actual model fields)
                            'current_price': result.get('price'),
                            # Note: previous_close stored separately, not in model
                            'days_high': result.get('day_high'),
                            'days_low': result.get('day_low'),

                            # Real-time volume data
                            'volume': result.get('volume'),

                            # Calculated metrics
                            'market_cap': result.get('market_cap'),
                            'shares_available': result.get('shares'),
                            'price_change': result.get('price_change'),
                            'price_change_percent': result.get('price_change_percent'),
                            # Note: day_range_percent stored as days_range string in model

                            # Timestamp
                            'last_updated': result['timestamp']
                        }

                        Stock.objects.filter(symbol=result['symbol']).update(**update_fields)
                    except Exception as e:
                        pass  # Ignore errors for speed
        except:
            pass  # Ignore batch errors

# =====================================================
# MAIN
# =====================================================

def is_market_hours() -> bool:
    """Check if US market is open (rough check)"""

    # US market: Mon-Fri, 9:30 AM - 4:00 PM ET
    # For now, run anytime (user can control via cron/scheduler)

    return True

def main():
    """Main entry point - runs continuously"""

    logger.info("=" * 70)
    logger.info("REAL-TIME PRICE & VOLUME UPDATER")
    logger.info("=" * 70)
    logger.info("Updates:")
    logger.info("  - Current price, open, high, low")
    logger.info("  - Volume and market cap")
    logger.info("  - Price change, % change, day range %")
    logger.info("  - Volume average (dollar volume)")
    logger.info("Frequency: Continuous (every 2-3 minutes)")
    logger.info(f"Workers: {CONFIG.initial_workers}")
    logger.info(f"Target: <3 minutes per cycle with >98% success")
    logger.info("")

    # Load tickers once
    logger.info("Loading tickers...")
    config = StockRetrievalConfig()
    result = load_combined_tickers(config)
    tickers = result.tickers
    logger.info(f"Loaded {len(tickers)} tickers\n")

    # Create updater with proxies enabled
    updater = PriceUpdater(use_proxies=True)

    # Run continuously
    cycle = 1

    try:
        while True:
            if not is_market_hours():
                logger.info("Market is closed. Sleeping for 1 hour...")
                time.sleep(3600)
                continue

            logger.info("=" * 70)
            logger.info(f"CYCLE {cycle} - {datetime.now().strftime('%H:%M:%S')}")
            logger.info("=" * 70)

            # Reset metrics for this cycle
            updater.metrics.reset()

            # Update all prices
            start_time = time.time()
            results = updater.update_prices(tickers)
            cycle_time = time.time() - start_time

            # Results
            logger.info("")
            logger.info("=" * 70)
            logger.info(f"CYCLE {cycle} COMPLETE")
            logger.info("=" * 70)
            logger.info(f"Runtime: {cycle_time:.2f}s ({cycle_time/60:.2f} min)")
            logger.info(f"Success: {len(results)}/{len(tickers)} ({len(results)/len(tickers)*100:.1f}%)")
            logger.info(f"Throughput: {len(tickers)/cycle_time:.2f} tickers/sec")
            logger.info(f"DB Updates: {updater.metrics.updates}")
            logger.info(f"Workers: {updater.metrics.current_workers}")

            # Check if we met targets
            if cycle_time < 180 and updater.metrics.success_rate > 0.98:
                logger.info("[SUCCESS] Met all targets!")
            else:
                logger.info("[WARNING] Targets not met")
                if cycle_time >= 180:
                    logger.info(f"  - Runtime: {cycle_time:.2f}s (target: <180s)")
                if updater.metrics.success_rate <= 0.98:
                    logger.info(f"  - Success: {updater.metrics.success_rate*100:.1f}% (target: >98%)")

            # Save cycle metrics
            metrics = {
                'cycle': cycle,
                'runtime_seconds': round(cycle_time, 2),
                'total_attempted': updater.metrics.total_attempted,
                'success': updater.metrics.success,
                'failures': updater.metrics.failures,
                'success_rate': round(updater.metrics.success_rate * 100, 2),
                'throughput': round(updater.metrics.throughput, 2),
                'updates': updater.metrics.updates,
                'workers': updater.metrics.current_workers,
                'timestamp': datetime.now().isoformat()
            }

            # Append to daily log
            log_file = f"realtime_log_{datetime.now().strftime('%Y%m%d')}.jsonl"
            with open(log_file, 'a') as f:
                f.write(json.dumps(metrics) + '\n')

            # Wait before next cycle
            wait_time = max(0, CONFIG.update_interval_seconds - cycle_time)
            if wait_time > 0:
                logger.info(f"\nWaiting {wait_time:.0f}s before next cycle...")
                logger.info("=" * 70)
                logger.info("")
                time.sleep(wait_time)

            cycle += 1

    except KeyboardInterrupt:
        logger.info("\n\nStopping real-time updater...")
        logger.info(f"Completed {cycle} cycles")
        logger.info("=" * 70)

    finally:
        # Cleanup proxy settings
        if updater.proxy_manager:
            updater.proxy_manager.clear()
            logger.info("Proxy settings cleared")

if __name__ == "__main__":
    main()
