"""
Ultra-Optimized Stock Data Retrieval using YFinance Individual Calls
REQUIREMENTS:
- Individual yfinance calls per ticker (no batch)
- Verified proxy pool with stress testing
- Post-call data validation for correctness
- Full ticker pull in under 3 minutes
- 90%+ data correctness on first run
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from stocks.models import Stock, StockPrice
import yfinance as yf
import logging
import time
import random
import json
import requests
from decimal import Decimal
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import threading
from datetime import datetime
from pathlib import Path
import csv

logger = logging.getLogger(__name__)

class ProxyPool:
    """Manages verified proxies with stress testing and rotation"""

    def __init__(self, proxy_file='working_proxies.json'):
        self.proxy_file = proxy_file
        self.verified_proxies = []
        self.proxy_stats = {}  # Track success/failure per proxy
        self.lock = threading.Lock()
        self.current_index = 0

    def load_and_verify_proxies(self, max_proxies=100, quick_test=True):
        """Load proxies and verify them with stress testing"""
        try:
            with open(self.proxy_file, 'r') as f:
                data = json.load(f)
                all_proxies = data.get('proxies', [])[:max_proxies]

            print(f"[PROXY] Testing {len(all_proxies)} proxies for reliability...")

            if quick_test:
                # Quick verification - just check if proxy responds
                verified = []
                for proxy in all_proxies[:max_proxies]:
                    if self._quick_verify_proxy(proxy):
                        verified.append(proxy)
                        self.proxy_stats[proxy] = {'success': 0, 'failure': 0, 'avg_time': 0}
                    if len(verified) >= max_proxies:
                        break

                self.verified_proxies = verified
                print(f"[PROXY] SUCCESS: Verified {len(self.verified_proxies)} working proxies")
                return len(self.verified_proxies)
            else:
                # Full stress test - verify with actual yfinance calls
                return self._stress_test_proxies(all_proxies, max_verified=max_proxies)

        except Exception as e:
            print(f"[PROXY] ERROR: Error loading proxies: {e}")
            return 0

    def _quick_verify_proxy(self, proxy, timeout=2):
        """Quick proxy verification"""
        try:
            response = requests.get(
                'http://www.google.com',  # Use HTTP not HTTPS for proxy testing
                proxies={'http': proxy, 'https': proxy},
                timeout=timeout,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            return response.status_code == 200
        except Exception as e:
            return False

    def _stress_test_proxies(self, proxies, max_verified=100):
        """Stress test proxies with actual yfinance calls"""
        verified = []
        test_symbol = 'AAPL'

        print(f"[PROXY] Running stress test on {len(proxies)} proxies...")

        for i, proxy in enumerate(proxies):
            if len(verified) >= max_verified:
                break

            try:
                # Test proxy with actual yfinance call
                session = requests.Session()
                session.proxies = {'http': proxy, 'https': proxy}
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })

                start = time.time()
                ticker = yf.Ticker(test_symbol)

                # Monkey-patch yfinance session
                import yfinance.shared
                yfinance.shared._requests = session

                info = ticker.info
                elapsed = time.time() - start

                if info and info.get('regularMarketPrice'):
                    verified.append(proxy)
                    self.proxy_stats[proxy] = {
                        'success': 1,
                        'failure': 0,
                        'avg_time': elapsed
                    }
                    if (i + 1) % 10 == 0:
                        print(f"[PROXY] Verified {len(verified)}/{max_verified} proxies...")

            except Exception as e:
                continue

        self.verified_proxies = verified
        print(f"[PROXY] SUCCESS: Stress tested and verified {len(verified)} high-performance proxies")
        return len(verified)

    def get_next_proxy(self):
        """Get next proxy using round-robin with smart selection"""
        with self.lock:
            if not self.verified_proxies:
                return None

            # Round-robin selection
            proxy = self.verified_proxies[self.current_index % len(self.verified_proxies)]
            self.current_index += 1
            return proxy

    def record_success(self, proxy, response_time):
        """Record successful proxy usage"""
        with self.lock:
            if proxy in self.proxy_stats:
                stats = self.proxy_stats[proxy]
                stats['success'] += 1
                # Update rolling average
                total = stats['success'] + stats['failure']
                stats['avg_time'] = (stats['avg_time'] * (total - 1) + response_time) / total

    def record_failure(self, proxy):
        """Record proxy failure"""
        with self.lock:
            if proxy in self.proxy_stats:
                self.proxy_stats[proxy]['failure'] += 1

    def get_stats(self):
        """Get proxy pool statistics"""
        with self.lock:
            total_success = sum(s['success'] for s in self.proxy_stats.values())
            total_failure = sum(s['failure'] for s in self.proxy_stats.values())
            avg_time = sum(s['avg_time'] for s in self.proxy_stats.values()) / max(len(self.proxy_stats), 1)

            return {
                'total_proxies': len(self.verified_proxies),
                'total_success': total_success,
                'total_failure': total_failure,
                'success_rate': (total_success / max(total_success + total_failure, 1)) * 100,
                'avg_response_time': avg_time
            }


class DataValidator:
    """Validates retrieved stock data for correctness"""

    @staticmethod
    def validate_stock_data(symbol, data):
        """
        Validate stock data quality and completeness
        Returns (is_valid, quality_score, issues)
        """
        if not data:
            return False, 0, ['No data returned']

        issues = []
        score = 0
        max_score = 100

        # Critical fields (40 points)
        critical_fields = {
            'current_price': 15,
            'company_name': 10,
            'volume': 10,
            'market_cap': 5,
        }

        for field, points in critical_fields.items():
            value = data.get(field)
            if value is not None and value != 0:
                score += points
            else:
                issues.append(f"Missing critical field: {field}")

        # Important fields (40 points)
        important_fields = {
            'days_low': 5,
            'days_high': 5,
            'week_52_low': 5,
            'week_52_high': 5,
            'pe_ratio': 5,
            'dividend_yield': 5,
            'earnings_per_share': 5,
            'avg_volume_3mon': 5,
        }

        for field, points in important_fields.items():
            value = data.get(field)
            if value is not None:
                score += points

        # Data consistency checks (20 points)
        consistency_score = 20

        # Check price ranges
        if data.get('current_price') and data.get('days_low') and data.get('days_high'):
            price = float(data['current_price'])
            low = float(data['days_low'])
            high = float(data['days_high'])

            if not (low <= price <= high):
                issues.append(f"Price {price} outside day range [{low}, {high}]")
                consistency_score -= 5
            else:
                # Valid range
                pass

        # Check 52-week range
        if data.get('current_price') and data.get('week_52_low') and data.get('week_52_high'):
            price = float(data['current_price'])
            low_52 = float(data['week_52_low'])
            high_52 = float(data['week_52_high'])

            if not (low_52 <= price <= high_52 * 1.1):  # Allow 10% overshoot
                issues.append(f"Price {price} outside 52-week range [{low_52}, {high_52}]")
                consistency_score -= 5

        # Check PE ratio sanity
        if data.get('pe_ratio'):
            pe = float(data['pe_ratio'])
            if pe < 0 or pe > 1000:
                issues.append(f"Suspicious PE ratio: {pe}")
                consistency_score -= 5

        # Check dividend yield sanity
        if data.get('dividend_yield'):
            div = float(data['dividend_yield'])
            if div < 0 or div > 20:
                issues.append(f"Suspicious dividend yield: {div}%")
                consistency_score -= 5

        score += consistency_score

        is_valid = score >= 60  # 60% threshold for validity

        return is_valid, score, issues


class Command(BaseCommand):
    help = 'Ultra-optimized stock data update - sub-3-minute, 90%+ correctness'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=3000, help='Number of stocks to update')
        parser.add_argument('--threads', type=int, default=150, help='Concurrent threads (default: 150)')
        parser.add_argument('--timeout', type=int, default=5, help='Request timeout (default: 5s)')
        parser.add_argument('--test-mode', action='store_true', help='Test mode - no database writes')
        parser.add_argument('--csv', type=str, default='flat-ui__data-Fri Aug 01 2025.csv', help='CSV file')
        parser.add_argument('--proxy-count', type=int, default=100, help='Number of proxies to use')
        parser.add_argument('--stress-test-proxies', action='store_true', help='Full proxy stress test')

    def handle(self, *args, **options):
        """Main execution"""
        start_time = time.time()

        self.stdout.write("=" * 80)
        self.stdout.write("ULTRA-OPTIMIZED STOCK RETRIEVAL SYSTEM")
        self.stdout.write("=" * 80)
        self.stdout.write(f"[TARGET] Sub-3-minute full pull | 90%+ data correctness")
        self.stdout.write(f"[CONFIG] Threads: {options['threads']} | Timeout: {options['timeout']}s")
        self.stdout.write(f"[LIMIT] {options['limit']} stocks")
        self.stdout.write(f"[MODE] Test Mode: {'ON' if options['test_mode'] else 'OFF'}")
        self.stdout.write("=" * 80)

        # Initialize proxy pool with verification
        self.stdout.write("\n[1/5] Initializing and verifying proxy pool...")
        proxy_pool = ProxyPool()
        proxy_count = proxy_pool.load_and_verify_proxies(
            max_proxies=options['proxy_count'],
            quick_test=not options['stress_test_proxies']
        )

        if proxy_count == 0:
            self.stdout.write("[WARNING] No proxies available, continuing without proxies")

        # Load stock symbols
        self.stdout.write("\n[2/5] Loading stock symbols...")
        symbols = self._load_symbols(options['csv'], options['limit'])
        self.stdout.write(f"[SUCCESS] Loaded {len(symbols)} symbols")

        # Initialize metrics
        metrics = {
            'total': len(symbols),
            'successful': 0,
            'failed': 0,
            'validation_passed': 0,
            'validation_failed': 0,
            'avg_quality_score': 0,
            'start_time': start_time
        }

        # Process stocks with ultra-fast parallel execution
        self.stdout.write(f"\n[3/5] Processing {len(symbols)} stocks with {options['threads']} threads...")
        self.stdout.write("[START] Starting ultra-fast retrieval...\n")

        results = self._process_stocks_ultra_fast(
            symbols=symbols,
            proxy_pool=proxy_pool,
            num_threads=options['threads'],
            timeout=options['timeout'],
            test_mode=options['test_mode'],
            metrics=metrics
        )

        # Calculate final metrics
        elapsed = time.time() - start_time

        self.stdout.write("\n[4/5] Validating data quality...")
        self._display_validation_report(results, metrics)

        self.stdout.write("\n[5/5] Performance analysis...")
        self._display_final_report(metrics, elapsed, proxy_pool)

        # Check if requirements met
        self._check_requirements(metrics, elapsed)

    def _load_symbols(self, csv_file, limit):
        """Load stock symbols from CSV"""
        symbols = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    symbol = row.get('Symbol', '').strip()
                    financial_status = row.get('Financial Status', '').strip()
                    etf = row.get('ETF', '').strip()

                    # Skip delisted and ETFs
                    if symbol and financial_status != 'D' and etf != 'Y':
                        symbols.append(symbol)

                    if len(symbols) >= limit:
                        break
        except Exception as e:
            self.stdout.write(f"[WARNING] CSV load failed: {e}, using database fallback")
            symbols = list(Stock.objects.all()[:limit].values_list('ticker', flat=True))

        return symbols

    def _process_stocks_ultra_fast(self, symbols, proxy_pool, num_threads, timeout, test_mode, metrics):
        """Ultra-fast parallel stock processing"""
        results = []
        results_lock = threading.Lock()
        progress_counter = {'count': 0}

        def process_single_stock(symbol, idx):
            """Process individual stock with validation"""
            try:
                # Get proxy
                proxy = proxy_pool.get_next_proxy()

                # Fetch data
                start = time.time()
                stock_data = self._fetch_stock_data(symbol, proxy, timeout)
                fetch_time = time.time() - start

                if stock_data:
                    # Validate data
                    is_valid, quality_score, issues = DataValidator.validate_stock_data(symbol, stock_data)

                    # Record proxy success
                    if proxy:
                        proxy_pool.record_success(proxy, fetch_time)

                    # Save to database if not test mode and data is valid
                    if not test_mode and is_valid:
                        self._save_to_database(symbol, stock_data)

                    with results_lock:
                        metrics['successful'] += 1
                        if is_valid:
                            metrics['validation_passed'] += 1
                        else:
                            metrics['validation_failed'] += 1

                        # Update average quality score
                        total = metrics['successful']
                        metrics['avg_quality_score'] = (
                            (metrics['avg_quality_score'] * (total - 1) + quality_score) / total
                        )

                        results.append({
                            'symbol': symbol,
                            'success': True,
                            'valid': is_valid,
                            'quality_score': quality_score,
                            'issues': issues,
                            'fetch_time': fetch_time
                        })

                    # Progress reporting
                    with results_lock:
                        progress_counter['count'] += 1
                        if progress_counter['count'] % 50 == 0:
                            elapsed = time.time() - metrics['start_time']
                            rate = progress_counter['count'] / elapsed
                            eta = (metrics['total'] - progress_counter['count']) / rate if rate > 0 else 0
                            pct = (progress_counter['count'] / metrics['total']) * 100

                            self.stdout.write(
                                f"[PROGRESS] {progress_counter['count']}/{metrics['total']} "
                                f"({pct:.1f}%) | "
                                f"Rate: {rate:.1f} stocks/sec | "
                                f"ETA: {eta:.0f}s | "
                                f"Quality: {metrics['avg_quality_score']:.1f}%"
                            )
                else:
                    # Record failure
                    if proxy:
                        proxy_pool.record_failure(proxy)

                    with results_lock:
                        metrics['failed'] += 1
                        results.append({
                            'symbol': symbol,
                            'success': False,
                            'valid': False,
                            'quality_score': 0,
                            'issues': ['No data retrieved'],
                            'fetch_time': 0
                        })

            except Exception as e:
                with results_lock:
                    metrics['failed'] += 1
                    results.append({
                        'symbol': symbol,
                        'success': False,
                        'valid': False,
                        'quality_score': 0,
                        'issues': [str(e)],
                        'fetch_time': 0
                    })

        # Execute with thread pool
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = {
                executor.submit(process_single_stock, symbol, i): symbol
                for i, symbol in enumerate(symbols)
            }

            for future in as_completed(futures):
                try:
                    future.result(timeout=timeout + 5)
                except Exception as e:
                    symbol = futures[future]
                    self.stdout.write(f"[ERROR] Thread error for {symbol}: {e}")

        return results

    def _fetch_stock_data(self, symbol, proxy, timeout):
        """Fetch data for individual stock using yfinance"""
        try:
            # Configure session with proxy
            session = None
            if proxy:
                session = requests.Session()
                session.proxies = {'http': proxy, 'https': proxy}
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
                })

                # Monkey-patch yfinance
                import yfinance.shared
                yfinance.shared._requests = session

            # Small random delay to avoid rate limiting
            time.sleep(random.uniform(0.001, 0.005))

            # Create ticker object
            ticker = yf.Ticker(symbol)

            # Try multiple data sources
            info = None
            fast_info = None
            hist = None
            current_price = None

            # Get fast_info first (fastest method)
            try:
                fast_info = ticker.fast_info
                if fast_info and hasattr(fast_info, 'last_price'):
                    current_price = fast_info.last_price
            except:
                pass

            # Get full info
            try:
                info = ticker.info
            except:
                pass

            # Get historical data as fallback
            if current_price is None:
                try:
                    hist = ticker.history(period="1d", timeout=timeout)
                    if hist is not None and not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                except:
                    pass

            # Get price from info if still missing
            if current_price is None and info:
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')

            # Build stock data dictionary
            stock_data = self._extract_stock_data(symbol, info, fast_info, hist, current_price)

            return stock_data

        except Exception as e:
            return None

    def _extract_stock_data(self, symbol, info, fast_info, hist, current_price):
        """Extract comprehensive stock data from yfinance responses"""

        def safe_decimal(value):
            """Safely convert to Decimal"""
            if value is None or pd.isna(value):
                return None
            try:
                if isinstance(value, (int, float)):
                    if pd.isna(value) or value == float('inf') or value == float('-inf'):
                        return None
                    return Decimal(str(value))
                return Decimal(str(value))
            except:
                return None

        def get_from_info(field_names, default=None):
            """Get value from info with multiple field name fallbacks"""
            if not info:
                return default
            for field in field_names if isinstance(field_names, list) else [field_names]:
                value = info.get(field)
                if value is not None and not pd.isna(value):
                    return value
            return default

        def get_from_fast_info(attr_names, default=None):
            """Get value from fast_info with multiple attribute fallbacks"""
            if not fast_info:
                return default
            for attr in attr_names if isinstance(attr_names, list) else [attr_names]:
                try:
                    value = getattr(fast_info, attr, None)
                    if value is not None:
                        return value
                except:
                    continue
            return default

        # Extract PE ratio
        pe_ratio = get_from_info(['trailingPE', 'forwardPE'])

        # Extract dividend yield
        dividend_yield = get_from_info(['dividendYield', 'trailingAnnualDividendYield'])
        if dividend_yield and dividend_yield < 1:
            dividend_yield = dividend_yield * 100  # Convert to percentage

        # Build comprehensive data
        stock_data = {
            'ticker': symbol,
            'symbol': symbol,
            'company_name': get_from_info(['longName', 'shortName'], symbol),
            'name': get_from_info(['longName', 'shortName'], symbol),
            'current_price': safe_decimal(current_price),
            'days_low': safe_decimal(get_from_info('dayLow') or get_from_fast_info(['day_low', 'low'])),
            'days_high': safe_decimal(get_from_info('dayHigh') or get_from_fast_info(['day_high', 'high'])),
            'volume': safe_decimal(get_from_info('volume') or get_from_fast_info(['last_volume', 'volume'])),
            'volume_today': safe_decimal(get_from_info('volume') or get_from_fast_info(['last_volume', 'volume'])),
            'avg_volume_3mon': safe_decimal(get_from_info(['averageVolume', 'averageVolume10days']) or get_from_fast_info('three_month_average_volume')),
            'market_cap': safe_decimal(get_from_info('marketCap') or get_from_fast_info('market_cap')),
            'pe_ratio': safe_decimal(pe_ratio),
            'dividend_yield': safe_decimal(dividend_yield),
            'one_year_target': safe_decimal(get_from_info('targetMeanPrice')),
            'week_52_low': safe_decimal(get_from_info('fiftyTwoWeekLow') or get_from_fast_info('fifty_two_week_low')),
            'week_52_high': safe_decimal(get_from_info('fiftyTwoWeekHigh') or get_from_fast_info('fifty_two_week_high')),
            'earnings_per_share': safe_decimal(get_from_info('trailingEps')),
            'book_value': safe_decimal(get_from_info('bookValue')),
            'price_to_book': safe_decimal(get_from_info('priceToBook')),
            'exchange': get_from_info('exchange') or get_from_fast_info('exchange') or 'NASDAQ',
            'last_updated': timezone.now(),
            'created_at': timezone.now(),
            # Additional fields
            'price_change_today': None,
            'price_change_week': None,
            'price_change_month': None,
            'price_change_year': None,
            'change_percent': None,
            'bid_price': None,
            'ask_price': None,
            'bid_ask_spread': '',
            'days_range': '',
            'dvav': None,
            'shares_available': None,
            'market_cap_change_3mon': None,
            'pe_change_3mon': None,
        }

        # Calculate price changes from historical data
        if hist is not None and len(hist) > 1:
            try:
                current = hist['Close'].iloc[-1]
                previous = hist['Close'].iloc[-2]
                if current and previous:
                    change = current - previous
                    change_percent = (change / previous) * 100
                    stock_data['price_change_today'] = safe_decimal(change)
                    stock_data['change_percent'] = safe_decimal(change_percent)
            except:
                pass

        # Calculate DVAV (Day Volume Over Average Volume)
        if stock_data.get('volume') and stock_data.get('avg_volume_3mon'):
            try:
                dvav = stock_data['volume'] / stock_data['avg_volume_3mon']
                stock_data['dvav'] = safe_decimal(dvav)
            except:
                pass

        return stock_data

    def _save_to_database(self, symbol, stock_data):
        """Save stock data to database"""
        try:
            # Update or create Stock
            stock, created = Stock.objects.update_or_create(
                ticker=symbol,
                defaults=stock_data
            )

            # Create StockPrice record
            if stock_data.get('current_price'):
                StockPrice.objects.create(
                    stock=stock,
                    price=stock_data['current_price']
                )

        except Exception as e:
            logger.error(f"Database save failed for {symbol}: {e}")

    def _display_validation_report(self, results, metrics):
        """Display data validation report"""
        self.stdout.write("-" * 80)
        self.stdout.write("DATA VALIDATION REPORT")
        self.stdout.write("-" * 80)

        # Quality distribution
        quality_ranges = {'90-100%': 0, '80-89%': 0, '70-79%': 0, '60-69%': 0, '<60%': 0}
        for r in results:
            score = r['quality_score']
            if score >= 90:
                quality_ranges['90-100%'] += 1
            elif score >= 80:
                quality_ranges['80-89%'] += 1
            elif score >= 70:
                quality_ranges['70-79%'] += 1
            elif score >= 60:
                quality_ranges['60-69%'] += 1
            else:
                quality_ranges['<60%'] += 1

        self.stdout.write("\n[QUALITY] Quality Score Distribution:")
        for range_name, count in quality_ranges.items():
            pct = (count / metrics['total']) * 100 if metrics['total'] > 0 else 0
            bar = '#' * int(pct / 2)
            self.stdout.write(f"  {range_name:10s} | {bar:50s} {count:4d} ({pct:5.1f}%)")

        # Common issues
        issue_counts = {}
        for r in results:
            for issue in r.get('issues', []):
                issue_counts[issue] = issue_counts.get(issue, 0) + 1

        if issue_counts:
            self.stdout.write("\n[ISSUES] Top Data Issues:")
            for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                self.stdout.write(f"  - {issue}: {count} occurrences")

    def _display_final_report(self, metrics, elapsed, proxy_pool):
        """Display final performance report"""
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("FINAL PERFORMANCE REPORT")
        self.stdout.write("=" * 80)

        # Processing metrics
        success_rate = (metrics['successful'] / metrics['total']) * 100 if metrics['total'] > 0 else 0
        validation_rate = (metrics['validation_passed'] / metrics['successful']) * 100 if metrics['successful'] > 0 else 0
        overall_correctness = (metrics['validation_passed'] / metrics['total']) * 100 if metrics['total'] > 0 else 0

        self.stdout.write("\n[RESULTS] Processing Results:")
        self.stdout.write(f"  Total Stocks:      {metrics['total']}")
        self.stdout.write(f"  Successful:        {metrics['successful']} ({success_rate:.1f}%)")
        self.stdout.write(f"  Failed:            {metrics['failed']}")
        self.stdout.write(f"  Validation Passed: {metrics['validation_passed']} ({validation_rate:.1f}%)")
        self.stdout.write(f"  Validation Failed: {metrics['validation_failed']}")

        self.stdout.write(f"\n[QUALITY] Data Quality:")
        self.stdout.write(f"  Average Quality Score: {metrics['avg_quality_score']:.1f}%")
        self.stdout.write(f"  Overall Correctness:   {overall_correctness:.1f}%")

        # Performance metrics
        rate = metrics['total'] / elapsed if elapsed > 0 else 0

        self.stdout.write(f"\n[PERFORMANCE] Performance:")
        self.stdout.write(f"  Total Time:     {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
        self.stdout.write(f"  Processing Rate: {rate:.2f} stocks/second")
        self.stdout.write(f"  Avg Time/Stock:  {(elapsed/metrics['total']*1000):.0f}ms")

        # Proxy statistics
        proxy_stats = proxy_pool.get_stats()
        self.stdout.write(f"\n[PROXY] Proxy Performance:")
        self.stdout.write(f"  Active Proxies:    {proxy_stats['total_proxies']}")
        self.stdout.write(f"  Total Requests:    {proxy_stats['total_success'] + proxy_stats['total_failure']}")
        self.stdout.write(f"  Success Rate:      {proxy_stats['success_rate']:.1f}%")
        self.stdout.write(f"  Avg Response Time: {proxy_stats['avg_response_time']:.3f}s")

    def _check_requirements(self, metrics, elapsed):
        """Check if requirements are met"""
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("REQUIREMENTS CHECK")
        self.stdout.write("=" * 80)

        # Requirement 1: Sub-3-minute execution
        time_ok = elapsed < 180
        time_status = "[PASS]" if time_ok else "[FAIL]"
        self.stdout.write(f"\n{time_status} - Execution Time: {elapsed:.2f}s (requirement: <180s)")

        # Requirement 2: 90%+ data correctness
        correctness = (metrics['validation_passed'] / metrics['total']) * 100 if metrics['total'] > 0 else 0
        correctness_ok = correctness >= 90
        correctness_status = "[PASS]" if correctness_ok else "[FAIL]"
        self.stdout.write(f"{correctness_status} - Data Correctness: {correctness:.1f}% (requirement: >=90%)")

        # Overall status
        all_ok = time_ok and correctness_ok
        if all_ok:
            self.stdout.write("\n[SUCCESS] ALL REQUIREMENTS MET! System is production-ready.")
        else:
            self.stdout.write("\n[WARNING] Some requirements not met. See above for details.")

        self.stdout.write("=" * 80)
