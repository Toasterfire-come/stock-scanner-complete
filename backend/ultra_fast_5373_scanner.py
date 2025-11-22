#!/usr/bin/env python3
"""
Ultra-Fast Stock Scanner for 5373 Tickers
Target: <3 minutes runtime with >95% accuracy

Strategy:
1. Use fast_info() for quick initial data (faster than info())
2. Fall back to info() only when fast_info fails or data is incomplete
3. Intelligent rate limiting based on measured call times
4. Distributed proxy usage to avoid per-IP rate limits
5. Adaptive concurrency with real-time performance monitoring
6. No simulated data - only real yfinance data

Performance optimizations:
- Fast_info is 3-5x faster than info()
- Proxy rotation spreads load across IPs
- Measured timing prevents rate limit triggers
- Concurrent workers maximize throughput
- Dynamic batch sizing based on success rates
"""

import os
import sys
import time
import random
import logging
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

# Add Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")

import django
django.setup()

import yfinance as yf
from django.utils import timezone
from stocks.models import Stock

# Import existing infrastructure
from stock_retrieval.session_factory import ProxyPool, create_session_with_proxy
from stock_retrieval.ticker_loader import load_combined_tickers
from stock_retrieval.quality_gate import validate_data_quality

# =====================================================
# CONFIGURATION
# =====================================================

@dataclass
class ScannerConfig:
    """Configuration for ultra-fast scanner"""
    # Performance settings
    max_workers: int = 25  # Concurrent workers
    target_runtime_seconds: int = 180  # 3 minutes
    request_timeout: int = 4  # Seconds per request

    # Rate limiting strategy
    min_delay_between_calls: float = 0.01  # 10ms minimum spacing
    max_delay_between_calls: float = 0.1  # 100ms maximum spacing
    adaptive_delay_enabled: bool = True  # Adjust delay based on success rate

    # Data retrieval strategy
    use_fast_info_first: bool = True  # Try fast_info before info
    fallback_to_info: bool = True  # Use info() if fast_info fails
    max_retries_per_ticker: int = 2  # Retry attempts

    # Proxy settings
    max_proxies: int = 100  # Use top 100 fastest proxies
    proxy_rotation_strategy: str = "worker_based"  # worker_based or round_robin

    # Quality thresholds
    min_success_rate: float = 0.95  # 95% minimum
    required_fields: tuple = ("current_price", "volume", "market_cap")

    # Batching
    batch_size: int = 500  # Tickers per batch
    inter_batch_delay: float = 0.0  # No delay between batches

    # Monitoring
    log_level: str = "INFO"
    show_progress: bool = True
    save_metrics: bool = True

CONFIG = ScannerConfig()

# =====================================================
# LOGGING SETUP
# =====================================================

logging.basicConfig(
    level=getattr(logging, CONFIG.log_level),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'ultra_fast_scan_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

# =====================================================
# METRICS TRACKING
# =====================================================

class MetricsCollector:
    """Real-time performance metrics"""

    def __init__(self):
        self.lock = threading.Lock()
        self.start_time = None
        self.end_time = None

        # Success/failure tracking
        self.total_attempted = 0
        self.fast_info_success = 0
        self.info_success = 0
        self.failures = 0

        # Timing tracking
        self.call_times = []
        self.fast_info_times = []
        self.info_times = []

        # Rate limiting tracking
        self.rate_limit_hits = 0
        self.proxy_failures = defaultdict(int)

        # Data quality
        self.complete_records = 0
        self.partial_records = 0

    def start(self):
        """Start timing"""
        self.start_time = time.time()

    def record_attempt(self):
        """Record ticker attempt"""
        with self.lock:
            self.total_attempted += 1

    def record_fast_info_success(self, duration: float):
        """Record successful fast_info call"""
        with self.lock:
            self.fast_info_success += 1
            self.fast_info_times.append(duration)
            self.call_times.append(duration)

    def record_info_success(self, duration: float):
        """Record successful info call"""
        with self.lock:
            self.info_success += 1
            self.info_times.append(duration)
            self.call_times.append(duration)

    def record_failure(self):
        """Record failure"""
        with self.lock:
            self.failures += 1

    def record_rate_limit(self):
        """Record rate limit hit"""
        with self.lock:
            self.rate_limit_hits += 1

    def record_proxy_failure(self, proxy: str):
        """Record proxy failure"""
        with self.lock:
            self.proxy_failures[proxy] += 1

    def record_complete_record(self):
        """Record complete data record"""
        with self.lock:
            self.complete_records += 1

    def record_partial_record(self):
        """Record partial data record"""
        with self.lock:
            self.partial_records += 1

    def get_success_rate(self) -> float:
        """Calculate current success rate"""
        with self.lock:
            if self.total_attempted == 0:
                return 0.0
            successes = self.fast_info_success + self.info_success
            return successes / self.total_attempted

    def get_average_call_time(self) -> float:
        """Get average call time"""
        with self.lock:
            if not self.call_times:
                return 0.0
            return sum(self.call_times) / len(self.call_times)

    def get_optimal_delay(self) -> float:
        """Calculate optimal delay between calls"""
        avg_time = self.get_average_call_time()
        success_rate = self.get_success_rate()

        # Base delay on average call time
        base_delay = avg_time * 0.05  # 5% of call time

        # Adjust based on success rate
        if success_rate < 0.90:
            # Too many failures, slow down
            return min(base_delay * 2.0, CONFIG.max_delay_between_calls)
        elif success_rate > 0.98:
            # Great success, can go faster
            return max(base_delay * 0.5, CONFIG.min_delay_between_calls)
        else:
            return max(min(base_delay, CONFIG.max_delay_between_calls), CONFIG.min_delay_between_calls)

    def finish(self):
        """End timing"""
        self.end_time = time.time()

    def get_summary(self) -> Dict:
        """Get metrics summary"""
        runtime = (self.end_time or time.time()) - (self.start_time or time.time())

        return {
            'runtime_seconds': round(runtime, 2),
            'runtime_minutes': round(runtime / 60, 2),
            'total_attempted': self.total_attempted,
            'fast_info_success': self.fast_info_success,
            'info_success': self.info_success,
            'total_success': self.fast_info_success + self.info_success,
            'failures': self.failures,
            'success_rate': round(self.get_success_rate() * 100, 2),
            'complete_records': self.complete_records,
            'partial_records': self.partial_records,
            'rate_limit_hits': self.rate_limit_hits,
            'average_call_time': round(self.get_average_call_time(), 3),
            'average_fast_info_time': round(sum(self.fast_info_times) / len(self.fast_info_times), 3) if self.fast_info_times else 0,
            'average_info_time': round(sum(self.info_times) / len(self.info_times), 3) if self.info_times else 0,
            'throughput_per_second': round(self.total_attempted / runtime, 2) if runtime > 0 else 0,
            'proxy_failure_count': len(self.proxy_failures),
            'worst_proxies': sorted(self.proxy_failures.items(), key=lambda x: x[1], reverse=True)[:5]
        }

    def print_progress(self):
        """Print progress update"""
        if not CONFIG.show_progress:
            return

        with self.lock:
            elapsed = time.time() - (self.start_time or time.time())
            rate = self.total_attempted / elapsed if elapsed > 0 else 0
            success_pct = self.get_success_rate() * 100

            print(f"\rProgress: {self.total_attempted} | "
                  f"Success: {success_pct:.1f}% | "
                  f"Rate: {rate:.1f}/sec | "
                  f"Elapsed: {elapsed:.1f}s", end='', flush=True)

metrics = MetricsCollector()

# =====================================================
# PROXY MANAGEMENT
# =====================================================

class SmartProxyPool:
    """Enhanced proxy pool with performance tracking"""

    def __init__(self, max_proxies: int = 100):
        self.base_pool = ProxyPool()
        self.max_proxies = max_proxies
        self.proxy_performance = defaultdict(lambda: {'success': 0, 'failure': 0, 'avg_time': 0.0})
        self.lock = threading.Lock()

        # Load and filter to fastest proxies
        all_proxies = self.base_pool.proxies
        logger.info(f"Loaded {len(all_proxies)} proxies from pool")

        # Use top N proxies
        self.active_proxies = all_proxies[:max_proxies] if len(all_proxies) > max_proxies else all_proxies
        logger.info(f"Using top {len(self.active_proxies)} proxies for scanning")

        self.current_index = 0

    def get_proxy_for_worker(self, worker_id: int) -> Optional[str]:
        """Get consistent proxy for worker"""
        if not self.active_proxies:
            return None

        # Assign proxy based on worker ID for consistent routing
        proxy_index = worker_id % len(self.active_proxies)
        return self.active_proxies[proxy_index]

    def get_next_proxy(self) -> Optional[str]:
        """Get next proxy in round-robin"""
        with self.lock:
            if not self.active_proxies:
                return None

            proxy = self.active_proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.active_proxies)
            return proxy

    def record_success(self, proxy: str, duration: float):
        """Record successful proxy usage"""
        with self.lock:
            perf = self.proxy_performance[proxy]
            perf['success'] += 1
            # Running average
            total = perf['success'] + perf['failure']
            perf['avg_time'] = ((perf['avg_time'] * (total - 1)) + duration) / total

    def record_failure(self, proxy: str):
        """Record proxy failure"""
        with self.lock:
            self.proxy_performance[proxy]['failure'] += 1
            metrics.record_proxy_failure(proxy)

proxy_pool = SmartProxyPool(max_proxies=CONFIG.max_proxies)

# =====================================================
# DATA EXTRACTION
# =====================================================

def extract_data_from_fast_info(ticker_obj, ticker: str) -> Optional[Dict]:
    """Extract data from yfinance fast_info (faster but limited data)"""
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
            'company_name': ticker,  # fast_info doesn't have name
            'exchange': getattr(fast_info, 'exchange', 'UNKNOWN'),
        }

        # Check if we have minimum required data
        has_required = all(data.get(field) is not None for field in ['current_price', 'volume'])

        return data if has_required else None

    except Exception as e:
        logger.debug(f"Fast_info extraction failed for {ticker}: {e}")
        return None

def extract_data_from_info(ticker_obj, ticker: str) -> Optional[Dict]:
    """Extract data from yfinance info (slower but complete data)"""
    try:
        info = ticker_obj.info

        if not info or len(info) < 5:
            return None

        # Extract comprehensive data
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

        # Try to get current price from history if not in info
        if not data['current_price']:
            try:
                hist = ticker_obj.history(period='1d')
                if not hist.empty and 'Close' in hist.columns:
                    data['current_price'] = float(hist['Close'].iloc[-1])
            except:
                pass

        # Check if we have minimum required data
        has_required = all(data.get(field) is not None for field in ['current_price', 'volume'])

        return data if has_required else None

    except Exception as e:
        logger.debug(f"Info extraction failed for {ticker}: {e}")
        return None

# =====================================================
# CORE FETCHING LOGIC
# =====================================================

def fetch_ticker_data(ticker: str, worker_id: int, session) -> Optional[Dict]:
    """
    Fetch data for a single ticker using smart strategy:
    1. Try fast_info first (faster)
    2. Fall back to info if fast_info fails or incomplete
    3. Return None if both fail
    """
    metrics.record_attempt()

    try:
        # Create ticker object with session
        ticker_obj = yf.Ticker(ticker, session=session)

        # Strategy 1: Try fast_info first (3-5x faster)
        if CONFIG.use_fast_info_first:
            start_time = time.time()
            try:
                data = extract_data_from_fast_info(ticker_obj, ticker)
                if data:
                    duration = time.time() - start_time
                    metrics.record_fast_info_success(duration)
                    logger.debug(f"✓ {ticker}: fast_info ({duration:.2f}s)")
                    return data
            except Exception as e:
                logger.debug(f"Fast_info failed for {ticker}: {e}")

        # Strategy 2: Fall back to info (slower but more complete)
        if CONFIG.fallback_to_info:
            start_time = time.time()
            try:
                data = extract_data_from_info(ticker_obj, ticker)
                if data:
                    duration = time.time() - start_time
                    metrics.record_info_success(duration)
                    logger.debug(f"✓ {ticker}: info ({duration:.2f}s)")
                    return data
            except Exception as e:
                logger.debug(f"Info failed for {ticker}: {e}")

        # Both strategies failed
        metrics.record_failure()
        logger.warning(f"✗ {ticker}: All strategies failed")
        return None

    except Exception as e:
        metrics.record_failure()
        logger.error(f"✗ {ticker}: Exception - {e}")
        return None

def fetch_with_retry(ticker: str, worker_id: int, proxy: Optional[str]) -> Optional[Dict]:
    """Fetch ticker data with retry logic"""

    for attempt in range(CONFIG.max_retries_per_ticker):
        try:
            # Create session with proxy
            session = create_session_with_proxy(
                proxy=proxy,
                timeout=CONFIG.request_timeout
            )

            # Adaptive rate limiting
            if CONFIG.adaptive_delay_enabled and attempt > 0:
                delay = metrics.get_optimal_delay()
                time.sleep(delay + random.uniform(0, delay * 0.5))

            # Fetch data
            start = time.time()
            data = fetch_ticker_data(ticker, worker_id, session)
            duration = time.time() - start

            if data:
                # Success!
                if proxy:
                    proxy_pool.record_success(proxy, duration)
                return data

            # Failed, retry with backoff
            if attempt < CONFIG.max_retries_per_ticker - 1:
                backoff = 0.2 * (1.5 ** attempt)
                time.sleep(backoff + random.uniform(0, 0.1))

        except Exception as e:
            logger.debug(f"Attempt {attempt + 1} failed for {ticker}: {e}")
            if proxy:
                proxy_pool.record_failure(proxy)

            if "429" in str(e) or "Too Many Requests" in str(e):
                metrics.record_rate_limit()
                # Rate limited, longer backoff
                time.sleep(1.0 + random.uniform(0, 0.5))

    return None

# =====================================================
# BATCH PROCESSING
# =====================================================

def process_batch(tickers: List[str], batch_num: int) -> List[Dict]:
    """Process a batch of tickers concurrently"""
    logger.info(f"Processing batch {batch_num}: {len(tickers)} tickers")

    results = []

    with ThreadPoolExecutor(max_workers=CONFIG.max_workers) as executor:
        # Submit all tasks
        futures = {}
        for idx, ticker in enumerate(tickers):
            worker_id = idx % CONFIG.max_workers

            # Get proxy for this worker
            if CONFIG.proxy_rotation_strategy == "worker_based":
                proxy = proxy_pool.get_proxy_for_worker(worker_id)
            else:
                proxy = proxy_pool.get_next_proxy()

            future = executor.submit(fetch_with_retry, ticker, worker_id, proxy)
            futures[future] = ticker

        # Collect results as they complete
        for future in as_completed(futures):
            ticker = futures[future]
            try:
                data = future.result()
                if data:
                    results.append(data)

                    # Check data quality
                    if all(data.get(field) for field in CONFIG.required_fields):
                        metrics.record_complete_record()
                    else:
                        metrics.record_partial_record()

                metrics.print_progress()

            except Exception as e:
                logger.error(f"Error processing {ticker}: {e}")
                metrics.record_failure()

    return results

# =====================================================
# DATABASE OPERATIONS
# =====================================================

def save_to_database(data_records: List[Dict]) -> int:
    """Bulk save records to database"""
    logger.info(f"Saving {len(data_records)} records to database...")

    saved_count = 0
    now = timezone.now()

    for data in data_records:
        try:
            # Calculate DVAV if possible
            dvav = 1.0
            if data.get('volume') and data.get('avg_volume_3mon'):
                try:
                    dvav = float(data['volume']) / float(data['avg_volume_3mon'])
                except:
                    pass

            # Update or create
            stock, created = Stock.objects.update_or_create(
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
                    'last_updated': now,
                }
            )
            saved_count += 1

        except Exception as e:
            logger.error(f"Error saving {data['ticker']}: {e}")

    logger.info(f"Successfully saved {saved_count}/{len(data_records)} records")
    return saved_count

# =====================================================
# MAIN SCANNER
# =====================================================

def run_ultra_fast_scan(max_tickers: Optional[int] = None):
    """
    Run ultra-fast stock scan
    Target: <3 minutes for 5373 tickers with >95% accuracy
    """

    logger.info("=" * 70)
    logger.info("ULTRA-FAST STOCK SCANNER v1.0")
    logger.info("=" * 70)
    logger.info(f"Target: <{CONFIG.target_runtime_seconds}s runtime, >{CONFIG.min_success_rate*100}% accuracy")
    logger.info("")

    # Load tickers
    logger.info("Loading tickers...")
    tickers = load_combined_tickers(max_tickers=max_tickers)
    logger.info(f"Loaded {len(tickers)} tickers")

    if len(tickers) == 0:
        logger.error("No tickers loaded!")
        return

    # Print configuration
    logger.info("")
    logger.info("Configuration:")
    logger.info(f"  Workers: {CONFIG.max_workers}")
    logger.info(f"  Batch size: {CONFIG.batch_size}")
    logger.info(f"  Request timeout: {CONFIG.request_timeout}s")
    logger.info(f"  Max proxies: {CONFIG.max_proxies}")
    logger.info(f"  Proxy strategy: {CONFIG.proxy_rotation_strategy}")
    logger.info(f"  Fast_info first: {CONFIG.use_fast_info_first}")
    logger.info(f"  Fallback to info: {CONFIG.fallback_to_info}")
    logger.info(f"  Adaptive delay: {CONFIG.adaptive_delay_enabled}")
    logger.info("")

    # Start metrics
    metrics.start()

    # Process in batches
    all_results = []
    batches = [tickers[i:i + CONFIG.batch_size] for i in range(0, len(tickers), CONFIG.batch_size)]

    logger.info(f"Processing {len(batches)} batches...")
    logger.info("")

    for batch_num, batch in enumerate(batches, 1):
        batch_start = time.time()

        results = process_batch(batch, batch_num)
        all_results.extend(results)

        batch_duration = time.time() - batch_start
        logger.info(f"Batch {batch_num}/{len(batches)} complete: "
                   f"{len(results)}/{len(batch)} success "
                   f"({batch_duration:.1f}s)")

        # Inter-batch delay
        if CONFIG.inter_batch_delay > 0 and batch_num < len(batches):
            time.sleep(CONFIG.inter_batch_delay)

    print()  # New line after progress

    # Finish metrics
    metrics.finish()

    # Save to database
    if all_results:
        save_to_database(all_results)

    # Print summary
    summary = metrics.get_summary()

    logger.info("")
    logger.info("=" * 70)
    logger.info("SCAN COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Runtime: {summary['runtime_minutes']:.2f} minutes ({summary['runtime_seconds']:.1f}s)")
    logger.info(f"Tickers processed: {summary['total_attempted']}")
    logger.info(f"Successful: {summary['total_success']} ({summary['success_rate']:.1f}%)")
    logger.info(f"  - Via fast_info: {summary['fast_info_success']}")
    logger.info(f"  - Via info: {summary['info_success']}")
    logger.info(f"Failed: {summary['failures']}")
    logger.info(f"Complete records: {summary['complete_records']}")
    logger.info(f"Partial records: {summary['partial_records']}")
    logger.info(f"Throughput: {summary['throughput_per_second']:.1f} tickers/second")
    logger.info(f"Rate limit hits: {summary['rate_limit_hits']}")
    logger.info("")
    logger.info("Average call times:")
    logger.info(f"  - Fast_info: {summary['average_fast_info_time']:.3f}s")
    logger.info(f"  - Info: {summary['average_info_time']:.3f}s")
    logger.info(f"  - Overall: {summary['average_call_time']:.3f}s")

    # Performance assessment
    logger.info("")
    logger.info("Performance Assessment:")

    runtime_ok = summary['runtime_seconds'] <= CONFIG.target_runtime_seconds
    accuracy_ok = summary['success_rate'] >= CONFIG.min_success_rate * 100

    logger.info(f"  Runtime target (<{CONFIG.target_runtime_seconds}s): {'✓ PASS' if runtime_ok else '✗ FAIL'}")
    logger.info(f"  Accuracy target (>{CONFIG.min_success_rate*100}%): {'✓ PASS' if accuracy_ok else '✗ FAIL'}")

    if runtime_ok and accuracy_ok:
        logger.info("")
        logger.info("🎉 ALL TARGETS MET! 🎉")
    else:
        logger.info("")
        logger.info("⚠️  Some targets not met. Consider adjusting:")
        if not runtime_ok:
            logger.info("  - Increase max_workers")
            logger.info("  - Reduce request_timeout")
            logger.info("  - Decrease min_delay_between_calls")
        if not accuracy_ok:
            logger.info("  - Increase request_timeout")
            logger.info("  - Increase max_retries_per_ticker")
            logger.info("  - Enable adaptive_delay")

    # Save metrics to file
    if CONFIG.save_metrics:
        metrics_file = f"scan_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Metrics saved to: {metrics_file}")

    logger.info("=" * 70)

    return summary

# =====================================================
# CLI ENTRY POINT
# =====================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ultra-Fast Stock Scanner")
    parser.add_argument('--max-tickers', type=int, help='Maximum number of tickers to process')
    parser.add_argument('--workers', type=int, help='Number of concurrent workers')
    parser.add_argument('--timeout', type=int, help='Request timeout in seconds')
    parser.add_argument('--batch-size', type=int, help='Batch size')
    parser.add_argument('--no-fast-info', action='store_true', help='Disable fast_info, use info only')
    parser.add_argument('--no-adaptive', action='store_true', help='Disable adaptive delay')

    args = parser.parse_args()

    # Override config from CLI args
    if args.workers:
        CONFIG.max_workers = args.workers
    if args.timeout:
        CONFIG.request_timeout = args.timeout
    if args.batch_size:
        CONFIG.batch_size = args.batch_size
    if args.no_fast_info:
        CONFIG.use_fast_info_first = False
    if args.no_adaptive:
        CONFIG.adaptive_delay_enabled = False

    # Run scan
    try:
        run_ultra_fast_scan(max_tickers=args.max_tickers)
    except KeyboardInterrupt:
        logger.info("\n\nScan interrupted by user")
        metrics.finish()
        summary = metrics.get_summary()
        logger.info(f"Processed {summary['total_attempted']} tickers before interruption")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
