#!/usr/bin/env python3
"""
Blazing Fast Ticker Data Puller
================================

Maximum speed yfinance data extraction with intelligent optimization.

Features:
- Multi-strategy fetching (fast_info -> info -> history)
- Dynamic worker pool (auto-tuning based on performance)
- Adaptive rate limiting with real-time monitoring
- Streaming database writes for memory efficiency
- Comprehensive metrics and progress tracking
- Zero-copy data passing where possible

Usage:
    python blazing_fast_ticker_puller.py --max-workers 50 --target-time 180
    python blazing_fast_ticker_puller.py --strategy fast_info_first --stream-to-db
    python blazing_fast_ticker_puller.py --max-tickers 100 --test-mode
"""

import os
import sys
import time
import json
import random
import logging
import threading
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from queue import Queue

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")

import django
django.setup()

import yfinance as yf
from django.utils import timezone
from django.db import transaction
from stocks.models import Stock

# Import existing infrastructure
from stock_retrieval.session_factory import ProxyPool, create_requests_session
from stock_retrieval.config import StockRetrievalConfig
from stock_retrieval.ticker_loader import load_combined_tickers

# =====================================================
# CONFIGURATION
# =====================================================

@dataclass
class PullerConfig:
    """Configuration for blazing fast puller"""
    # Performance
    min_workers: int = 10
    max_workers: int = 100
    initial_workers: int = 30
    target_runtime_seconds: int = 180
    request_timeout: int = 5

    # Strategy
    strategy: str = "fast_info_first"  # fast_info_first, info_only, balanced, aggressive
    use_fast_info: bool = True
    use_info_fallback: bool = True
    use_history_fallback: bool = True

    # Rate limiting
    min_delay: float = 0.005  # 5ms
    max_delay: float = 0.15   # 150ms
    adaptive_delay: bool = True
    rate_limit_backoff: float = 2.0  # seconds

    # Database
    stream_to_db: bool = True
    batch_write_size: int = 100
    max_db_queue_size: int = 500

    # Retries
    max_retries: int = 2
    retry_delay: float = 0.3

    # Monitoring
    progress_interval: int = 100  # Show progress every N tickers
    save_metrics: bool = True
    verbose: bool = True

    # Auto-tuning
    auto_tune_workers: bool = True
    tune_interval: int = 500  # Adjust workers every N tickers
    target_success_rate: float = 0.95

CONFIG = PullerConfig()

# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'blazing_fast_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

# =====================================================
# METRICS COLLECTOR
# =====================================================

class PerformanceMetrics:
    """Thread-safe performance metrics collector"""

    def __init__(self):
        self.lock = threading.Lock()
        self.start_time = None
        self.end_time = None

        # Counters
        self.attempted = 0
        self.fast_info_success = 0
        self.info_success = 0
        self.history_success = 0
        self.failures = 0
        self.rate_limits = 0
        self.retries = 0

        # Timing
        self.fast_info_times = []
        self.info_times = []
        self.history_times = []

        # Quality
        self.complete_records = 0
        self.partial_records = 0

        # Workers
        self.current_workers = CONFIG.initial_workers
        self.worker_adjustments = []

        # Database
        self.db_writes = 0
        self.db_failures = 0

    def start(self):
        self.start_time = time.time()

    def finish(self):
        self.end_time = time.time()

    def record_attempt(self):
        with self.lock:
            self.attempted += 1

    def record_fast_info_success(self, duration: float):
        with self.lock:
            self.fast_info_success += 1
            self.fast_info_times.append(duration)

    def record_info_success(self, duration: float):
        with self.lock:
            self.info_success += 1
            self.info_times.append(duration)

    def record_history_success(self, duration: float):
        with self.lock:
            self.history_success += 1
            self.history_times.append(duration)

    def record_failure(self):
        with self.lock:
            self.failures += 1

    def record_rate_limit(self):
        with self.lock:
            self.rate_limits += 1

    def record_retry(self):
        with self.lock:
            self.retries += 1

    def record_complete(self):
        with self.lock:
            self.complete_records += 1

    def record_partial(self):
        with self.lock:
            self.partial_records += 1

    def record_db_write(self, count: int):
        with self.lock:
            self.db_writes += count

    def record_db_failure(self):
        with self.lock:
            self.db_failures += 1

    def adjust_workers(self, new_count: int, reason: str):
        with self.lock:
            old_count = self.current_workers
            self.current_workers = new_count
            self.worker_adjustments.append({
                'time': time.time() - (self.start_time or time.time()),
                'from': old_count,
                'to': new_count,
                'reason': reason
            })
            logger.info(f"Workers adjusted: {old_count} → {new_count} ({reason})")

    def get_success_rate(self) -> float:
        with self.lock:
            if self.attempted == 0:
                return 0.0
            successes = self.fast_info_success + self.info_success + self.history_success
            return successes / self.attempted

    def get_elapsed(self) -> float:
        return time.time() - (self.start_time or time.time())

    def get_throughput(self) -> float:
        elapsed = self.get_elapsed()
        if elapsed == 0:
            return 0.0
        with self.lock:
            return self.attempted / elapsed

    def get_eta_seconds(self, total_tickers: int) -> float:
        """Estimate time remaining"""
        with self.lock:
            if self.attempted == 0:
                return 0.0
            elapsed = self.get_elapsed()
            rate = self.attempted / elapsed
            remaining = total_tickers - self.attempted
            return remaining / rate if rate > 0 else 0.0

    def get_optimal_delay(self) -> float:
        """Calculate optimal delay based on current performance"""
        if not CONFIG.adaptive_delay:
            return CONFIG.min_delay

        success_rate = self.get_success_rate()

        # If too many failures, slow down
        if success_rate < 0.85:
            return CONFIG.max_delay
        elif success_rate < 0.92:
            return CONFIG.max_delay * 0.7
        elif success_rate > 0.98:
            return CONFIG.min_delay
        else:
            # Linear interpolation between min and max
            return CONFIG.min_delay + (CONFIG.max_delay - CONFIG.min_delay) * (0.98 - success_rate) / 0.13

    def print_progress(self, total: int):
        """Print progress bar"""
        with self.lock:
            pct = (self.attempted / total * 100) if total > 0 else 0
            success_rate = self.get_success_rate() * 100
            throughput = self.get_throughput()
            eta = self.get_eta_seconds(total)

            bar_length = 40
            filled = int(bar_length * self.attempted / total) if total > 0 else 0
            bar = '█' * filled + '░' * (bar_length - filled)

            print(f"\r[{bar}] {pct:.1f}% | "
                  f"{self.attempted}/{total} | "
                  f"Success: {success_rate:.1f}% | "
                  f"Speed: {throughput:.1f}/s | "
                  f"ETA: {eta:.0f}s", end='', flush=True)

    def get_summary(self) -> Dict:
        """Get complete metrics summary"""
        runtime = (self.end_time or time.time()) - (self.start_time or time.time())

        with self.lock:
            total_success = self.fast_info_success + self.info_success + self.history_success

            return {
                'runtime_seconds': round(runtime, 2),
                'runtime_minutes': round(runtime / 60, 2),
                'total_attempted': self.attempted,
                'total_success': total_success,
                'success_rate': round(self.get_success_rate() * 100, 2),
                'throughput': round(self.get_throughput(), 2),
                'fast_info_success': self.fast_info_success,
                'info_success': self.info_success,
                'history_success': self.history_success,
                'failures': self.failures,
                'rate_limits': self.rate_limits,
                'retries': self.retries,
                'complete_records': self.complete_records,
                'partial_records': self.partial_records,
                'db_writes': self.db_writes,
                'db_failures': self.db_failures,
                'avg_fast_info_time': round(sum(self.fast_info_times) / len(self.fast_info_times), 3) if self.fast_info_times else 0,
                'avg_info_time': round(sum(self.info_times) / len(self.info_times), 3) if self.info_times else 0,
                'avg_history_time': round(sum(self.history_times) / len(self.history_times), 3) if self.history_times else 0,
                'worker_adjustments': self.worker_adjustments,
                'final_worker_count': self.current_workers
            }

metrics = PerformanceMetrics()

# =====================================================
# DATABASE WRITER
# =====================================================

class DatabaseWriter:
    """Background database writer for streaming saves"""

    def __init__(self):
        self.queue = Queue(maxsize=CONFIG.max_db_queue_size)
        self.running = True
        self.thread = None
        self.batch = []

    def start(self):
        """Start background writer thread"""
        self.thread = threading.Thread(target=self._write_loop, daemon=True)
        self.thread.start()
        logger.info("Database writer started")

    def stop(self):
        """Stop writer and flush remaining data"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        self._flush_batch()
        logger.info("Database writer stopped")

    def enqueue(self, data: Dict):
        """Add data to write queue"""
        try:
            self.queue.put(data, timeout=1)
        except:
            logger.warning("Database queue full, writing synchronously")
            self._write_single(data)

    def _write_loop(self):
        """Background write loop"""
        while self.running or not self.queue.empty():
            try:
                data = self.queue.get(timeout=0.5)
                self.batch.append(data)

                if len(self.batch) >= CONFIG.batch_write_size:
                    self._flush_batch()

            except:
                # Timeout or empty queue
                if self.batch and (time.time() % 5 < 0.5):  # Flush every ~5 sec
                    self._flush_batch()
                continue

    def _flush_batch(self):
        """Write batch to database"""
        if not self.batch:
            return

        try:
            with transaction.atomic():
                for data in self.batch:
                    self._write_single(data)

            metrics.record_db_write(len(self.batch))
            logger.debug(f"Flushed {len(self.batch)} records to DB")
            self.batch = []

        except Exception as e:
            logger.error(f"Batch write failed: {e}")
            metrics.record_db_failure()
            self.batch = []

    def _write_single(self, data: Dict):
        """Write single record to database"""
        try:
            # Calculate DVAV
            dvav = 1.0
            if data.get('volume') and data.get('avg_volume_3mon'):
                try:
                    dvav = float(data['volume']) / float(data['avg_volume_3mon'])
                except:
                    pass

            Stock.objects.update_or_create(
                ticker=data['ticker'],
                defaults={
                    'symbol': data.get('symbol', data['ticker']),
                    'company_name': data.get('company_name', data['ticker']),
                    'exchange': data.get('exchange', 'UNKNOWN'),
                    'current_price': data.get('current_price'),
                    'bid_price': data.get('bid_price'),
                    'ask_price': data.get('ask_price'),
                    'volume': data.get('volume'),
                    'avg_volume_3mon': data.get('avg_volume_3mon'),
                    'market_cap': data.get('market_cap'),
                    'pe_ratio': data.get('pe_ratio'),
                    'dividend_yield': data.get('dividend_yield'),
                    'week_52_low': data.get('week_52_low'),
                    'week_52_high': data.get('week_52_high'),
                    'dvav': dvav,
                    'last_updated': timezone.now(),
                }
            )
        except Exception as e:
            logger.error(f"Failed to save {data.get('ticker', 'UNKNOWN')}: {e}")
            raise

db_writer = DatabaseWriter() if CONFIG.stream_to_db else None

# =====================================================
# DATA EXTRACTION
# =====================================================

def extract_from_fast_info(ticker_obj, ticker: str) -> Optional[Dict]:
    """Extract data from fast_info API"""
    try:
        fast_info = ticker_obj.fast_info

        data = {
            'ticker': ticker,
            'symbol': ticker,
            'current_price': getattr(fast_info, 'last_price', None),
            'market_cap': getattr(fast_info, 'market_cap', None),
            'volume': getattr(fast_info, 'last_volume', None),
            'week_52_high': getattr(fast_info, 'year_high', None),
            'week_52_low': getattr(fast_info, 'year_low', None),
            'pe_ratio': getattr(fast_info, 'trailing_pe', None) or getattr(fast_info, 'forward_pe', None),
            'company_name': ticker,
            'exchange': getattr(fast_info, 'exchange', 'UNKNOWN'),
        }

        # Require minimum data
        if data.get('current_price') and data.get('volume'):
            return data
        return None

    except Exception as e:
        logger.debug(f"fast_info failed for {ticker}: {e}")
        return None

def extract_from_info(ticker_obj, ticker: str) -> Optional[Dict]:
    """Extract data from info API"""
    try:
        info = ticker_obj.info

        if not info or len(info) < 5:
            return None

        data = {
            'ticker': ticker,
            'symbol': info.get('symbol', ticker),
            'company_name': info.get('longName') or info.get('shortName') or ticker,
            'exchange': info.get('exchange', 'UNKNOWN'),
            'current_price': (
                info.get('currentPrice') or
                info.get('regularMarketPrice') or
                info.get('previousClose')
            ),
            'bid_price': info.get('bid'),
            'ask_price': info.get('ask'),
            'volume': info.get('volume') or info.get('regularMarketVolume'),
            'avg_volume_3mon': info.get('averageVolume') or info.get('averageDailyVolume3Month'),
            'market_cap': info.get('marketCap'),
            'pe_ratio': info.get('trailingPE') or info.get('forwardPE'),
            'dividend_yield': info.get('dividendYield'),
            'week_52_low': info.get('fiftyTwoWeekLow'),
            'week_52_high': info.get('fiftyTwoWeekHigh'),
        }

        if data.get('current_price') and data.get('volume'):
            return data
        return None

    except Exception as e:
        logger.debug(f"info failed for {ticker}: {e}")
        return None

def extract_from_history(ticker_obj, ticker: str) -> Optional[Dict]:
    """Extract minimal data from history API"""
    try:
        hist = ticker_obj.history(period='5d')

        if hist.empty:
            return None

        latest = hist.iloc[-1]

        data = {
            'ticker': ticker,
            'symbol': ticker,
            'company_name': ticker,
            'exchange': 'UNKNOWN',
            'current_price': float(latest['Close']),
            'volume': int(latest['Volume']),
            'week_52_high': float(hist['High'].max()),
            'week_52_low': float(hist['Low'].min()),
        }

        return data

    except Exception as e:
        logger.debug(f"history failed for {ticker}: {e}")
        return None

# =====================================================
# FETCHING LOGIC
# =====================================================

def fetch_ticker(ticker: str, worker_id: int) -> Optional[Dict]:
    """
    Fetch ticker data using multi-strategy approach

    Strategy priority:
    1. fast_info (fastest, ~0.3s)
    2. info (slower, ~1.2s, more complete)
    3. history (fallback, ~0.8s, minimal data)
    """
    metrics.record_attempt()

    try:
        # Create ticker object
        ticker_obj = yf.Ticker(ticker)

        # Strategy 1: fast_info
        if CONFIG.use_fast_info:
            start = time.time()
            data = extract_from_fast_info(ticker_obj, ticker)
            if data:
                duration = time.time() - start
                metrics.record_fast_info_success(duration)
                return data

        # Strategy 2: info (fallback)
        if CONFIG.use_info_fallback:
            start = time.time()
            data = extract_from_info(ticker_obj, ticker)
            if data:
                duration = time.time() - start
                metrics.record_info_success(duration)
                return data

        # Strategy 3: history (last resort)
        if CONFIG.use_history_fallback:
            start = time.time()
            data = extract_from_history(ticker_obj, ticker)
            if data:
                duration = time.time() - start
                metrics.record_history_success(duration)
                return data

        # All strategies failed
        metrics.record_failure()
        return None

    except Exception as e:
        if "429" in str(e) or "Too Many Requests" in str(e):
            metrics.record_rate_limit()
            logger.warning(f"Rate limit hit for {ticker}")
        else:
            logger.debug(f"Error fetching {ticker}: {e}")
        metrics.record_failure()
        return None

def fetch_with_retry(ticker: str, worker_id: int) -> Optional[Dict]:
    """Fetch with retry logic"""

    for attempt in range(CONFIG.max_retries + 1):
        if attempt > 0:
            metrics.record_retry()
            delay = CONFIG.retry_delay * (1.5 ** (attempt - 1))
            time.sleep(delay + random.uniform(0, delay * 0.3))

        # Adaptive delay
        if attempt == 0 and CONFIG.adaptive_delay:
            delay = metrics.get_optimal_delay()
            if delay > CONFIG.min_delay:
                time.sleep(delay)

        data = fetch_ticker(ticker, worker_id)

        if data:
            # Check quality
            required_fields = ['current_price', 'volume']
            if all(data.get(f) for f in required_fields):
                nice_to_have = ['company_name', 'market_cap', 'week_52_high', 'week_52_low']
                if all(data.get(f) for f in nice_to_have):
                    metrics.record_complete()
                else:
                    metrics.record_partial()
            else:
                metrics.record_partial()

            return data

    return None

# =====================================================
# WORKER POOL MANAGEMENT
# =====================================================

def process_tickers(tickers: List[str]) -> List[Dict]:
    """Process all tickers with dynamic worker pool"""

    results = []
    total = len(tickers)

    # Start database writer if streaming
    if db_writer:
        db_writer.start()

    # Use dynamic worker count
    current_workers = CONFIG.initial_workers

    with ThreadPoolExecutor(max_workers=CONFIG.max_workers) as executor:
        futures = {}

        # Submit initial batch
        for idx, ticker in enumerate(tickers):
            if len(futures) >= current_workers:
                # Wait for one to complete before submitting more
                done, pending = as_completed(futures.keys()), None

                for future in done:
                    ticker_name = futures[future]
                    del futures[future]

                    try:
                        data = future.result()
                        if data:
                            if db_writer:
                                db_writer.enqueue(data)
                            else:
                                results.append(data)
                    except Exception as e:
                        logger.error(f"Error processing {ticker_name}: {e}")

                    # Progress update
                    if metrics.attempted % CONFIG.progress_interval == 0:
                        metrics.print_progress(total)

                        # Auto-tune workers
                        if CONFIG.auto_tune_workers and metrics.attempted % CONFIG.tune_interval == 0:
                            current_workers = tune_worker_count(current_workers)

                    break  # Only wait for one

            worker_id = idx % current_workers
            future = executor.submit(fetch_with_retry, ticker, worker_id)
            futures[future] = ticker

        # Collect remaining
        for future in as_completed(futures):
            ticker_name = futures[future]
            try:
                data = future.result()
                if data:
                    if db_writer:
                        db_writer.enqueue(data)
                    else:
                        results.append(data)
            except Exception as e:
                logger.error(f"Error processing {ticker_name}: {e}")

            if metrics.attempted % CONFIG.progress_interval == 0:
                metrics.print_progress(total)

    print()  # New line after progress

    # Stop database writer
    if db_writer:
        db_writer.stop()

    return results

def tune_worker_count(current: int) -> int:
    """Auto-tune worker count based on performance"""
    success_rate = metrics.get_success_rate()
    throughput = metrics.get_throughput()

    # Too many failures - reduce workers
    if success_rate < 0.90:
        new_count = max(CONFIG.min_workers, int(current * 0.8))
        if new_count != current:
            metrics.adjust_workers(new_count, f"Low success rate: {success_rate:.2%}")
        return new_count

    # Great success rate - can increase workers
    elif success_rate > 0.97 and current < CONFIG.max_workers:
        new_count = min(CONFIG.max_workers, int(current * 1.2))
        if new_count != current:
            metrics.adjust_workers(new_count, f"High success rate: {success_rate:.2%}")
        return new_count

    return current

# =====================================================
# MAIN RUNNER
# =====================================================

def run_blazing_fast_pull(max_tickers: Optional[int] = None):
    """Run the blazing fast ticker puller"""

    logger.info("=" * 70)
    logger.info("BLAZING FAST TICKER PULLER")
    logger.info("=" * 70)

    # Load tickers
    logger.info("Loading tickers...")
    config = StockRetrievalConfig()
    ticker_result = load_combined_tickers(config)
    tickers = ticker_result.tickers[:max_tickers] if max_tickers else ticker_result.tickers

    logger.info(f"Loaded {len(tickers)} tickers")
    logger.info(f"Strategy: {CONFIG.strategy}")
    logger.info(f"Workers: {CONFIG.initial_workers} (auto-tune: {CONFIG.auto_tune_workers})")
    logger.info(f"Stream to DB: {CONFIG.stream_to_db}")
    logger.info(f"Target time: {CONFIG.target_runtime_seconds}s")
    logger.info("")

    # Start
    metrics.start()

    # Process
    results = process_tickers(tickers)

    # Finish
    metrics.finish()

    # Save results if not streaming
    if not CONFIG.stream_to_db and results:
        logger.info(f"Saving {len(results)} records to database...")
        writer = DatabaseWriter()
        for data in results:
            writer._write_single(data)
        logger.info("Save complete")

    # Summary
    summary = metrics.get_summary()

    logger.info("")
    logger.info("=" * 70)
    logger.info("PULL COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Runtime: {summary['runtime_minutes']:.2f} minutes ({summary['runtime_seconds']:.1f}s)")
    logger.info(f"Throughput: {summary['throughput']:.2f} tickers/second")
    logger.info(f"Success rate: {summary['success_rate']:.1f}%")
    logger.info(f"Total processed: {summary['total_attempted']}")
    logger.info(f"  - fast_info: {summary['fast_info_success']}")
    logger.info(f"  - info: {summary['info_success']}")
    logger.info(f"  - history: {summary['history_success']}")
    logger.info(f"  - failures: {summary['failures']}")
    logger.info(f"Rate limits: {summary['rate_limits']}")
    logger.info(f"Complete records: {summary['complete_records']}")
    logger.info(f"Partial records: {summary['partial_records']}")
    logger.info(f"Database writes: {summary['db_writes']}")
    logger.info(f"Worker adjustments: {len(summary['worker_adjustments'])}")
    logger.info("")

    # Performance assessment
    target_met = summary['runtime_seconds'] <= CONFIG.target_runtime_seconds
    quality_met = summary['success_rate'] >= CONFIG.target_success_rate * 100

    logger.info(f"Target time ({CONFIG.target_runtime_seconds}s): {'✓ PASS' if target_met else '✗ FAIL'}")
    logger.info(f"Target success ({CONFIG.target_success_rate*100}%): {'✓ PASS' if quality_met else '✗ FAIL'}")

    # Save metrics
    if CONFIG.save_metrics:
        metrics_file = f"blazing_fast_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Metrics saved to: {metrics_file}")

    logger.info("=" * 70)

    return summary

# =====================================================
# CLI
# =====================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Blazing Fast Ticker Puller")
    parser.add_argument('--max-tickers', type=int, help='Limit number of tickers')
    parser.add_argument('--max-workers', type=int, help='Maximum concurrent workers')
    parser.add_argument('--initial-workers', type=int, help='Initial worker count')
    parser.add_argument('--target-time', type=int, help='Target runtime in seconds')
    parser.add_argument('--strategy', choices=['fast_info_first', 'info_only', 'balanced', 'aggressive'],
                       help='Data fetching strategy')
    parser.add_argument('--stream-to-db', action='store_true', help='Stream results to DB')
    parser.add_argument('--no-auto-tune', action='store_true', help='Disable worker auto-tuning')
    parser.add_argument('--batch-size', type=int, help='Database batch write size')
    parser.add_argument('--test-mode', action='store_true', help='Test mode (100 tickers)')

    args = parser.parse_args()

    # Apply overrides
    if args.max_workers:
        CONFIG.max_workers = args.max_workers
    if args.initial_workers:
        CONFIG.initial_workers = args.initial_workers
    if args.target_time:
        CONFIG.target_runtime_seconds = args.target_time
    if args.strategy:
        CONFIG.strategy = args.strategy
        if args.strategy == 'info_only':
            CONFIG.use_fast_info = False
        elif args.strategy == 'aggressive':
            CONFIG.min_delay = 0.001
            CONFIG.max_delay = 0.05
    if args.stream_to_db:
        CONFIG.stream_to_db = True
    if args.no_auto_tune:
        CONFIG.auto_tune_workers = False
    if args.batch_size:
        CONFIG.batch_write_size = args.batch_size

    max_tickers = 100 if args.test_mode else args.max_tickers

    try:
        run_blazing_fast_pull(max_tickers=max_tickers)
    except KeyboardInterrupt:
        logger.info("\n\nInterrupted by user")
        metrics.finish()
        if db_writer:
            db_writer.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
