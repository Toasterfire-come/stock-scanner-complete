"""
Django Management Command: Enhanced Stock Data Update using YFinance
Auto-scheduler every 5 minutes with NASDAQ-only focus and comprehensive data retrieval
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from stocks.models import Stock, StockPrice
import yfinance as yf
import logging
import time
import sys
from decimal import Decimal
import pandas as pd
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import schedule
from datetime import datetime, timedelta
import os
from pathlib import Path
import random
import requests
from proxy_manager import ProxyManager

# Add XAMPP MySQL to PATH if it exists
XAMPP_MYSQL_PATH = r"C:\xampp\mysql\bin"
if os.path.exists(XAMPP_MYSQL_PATH) and XAMPP_MYSQL_PATH not in os.environ.get('PATH', ''):
    os.environ['PATH'] = os.environ.get('PATH', '') + os.pathsep + XAMPP_MYSQL_PATH
    print(f"INFO: Added XAMPP MySQL to PATH for stock updates: {XAMPP_MYSQL_PATH}")

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Enhanced stock data update with 5-minute auto-scheduler and NASDAQ focus'

    def add_arguments(self, parser):
        parser.add_argument(
            '--symbols',
            type=str,
            help='Comma-separated list of stock symbols to update'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=3500,
            help='Maximum number of stocks to update (default: 3500)'
        )
        parser.add_argument(
            '--schedule',
            action='store_true',
            help='Run scheduler mode (updates every 5 minutes continuously)'
        )
        parser.add_argument(
            '--startup',
            action='store_true',
            help='Run initial startup update then start scheduler'
        )
        parser.add_argument(
            '--nasdaq-only',
            action='store_true',
            default=True,
            help='Update only NASDAQ-listed tickers (default: True)'
        )
        parser.add_argument(
            '--threads',
            type=int,
            default=20,
            help='Number of concurrent threads (default: 20)'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=0.1,
            help='Delay between requests in seconds (default: 0.1)'
        )
        parser.add_argument(
            '--test-mode',
            action='store_true',
            help='Run in test mode (display data without saving to database)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )
        parser.add_argument(
            '--no-proxy',
            action='store_true',
            help='Disable proxy usage (run without proxies)'
        )
        parser.add_argument(
            '--filter-delisted',
            action='store_true',
            help='Pre-filter delisted symbols before processing (faster processing)'
        )

    def handle(self, *args, **options):
        if options['verbose']:
            logging.basicConfig(level=logging.INFO)
            
        if options['startup']:
            self.stdout.write(self.style.SUCCESS("[RUN] STARTUP MODE: Running initial update then starting scheduler"))
            self._run_single_update(options)
            options['schedule'] = True
        
        if options['schedule']:
            self._run_scheduler(options)
        else:
            self._run_single_update(options)

    def _run_scheduler(self, options):
        """Run continuous scheduler every 5 minutes"""
        self.stdout.write(self.style.SUCCESS(" ENHANCED NASDAQ SCHEDULER STARTED"))
        self.stdout.write("=" * 70)
        self.stdout.write(" Schedule: Every 5 minutes")
        self.stdout.write("[TARGET] Target: NASDAQ tickers only")
        self.stdout.write(" Mode: Continuous updates")
        self.stdout.write(" Multithreading: Enabled")
        self.stdout.write(" Press Ctrl+C to stop the scheduler\n")

        # Schedule the job every 5 minutes
        schedule.every(5).minutes.do(self._run_single_update, options)
        
        # Show next run time
        next_run = schedule.next_run()
        self.stdout.write(f" Next update: {next_run.strftime('%H:%M:%S')}")

        try:
            while True:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\n[STOP]  Scheduler stopped by user"))

    def _run_single_update(self, options):
        """Run a comprehensive single stock update"""
        
        start_time = time.time()
        
        # Display configuration
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS("[UP] COMPREHENSIVE NASDAQ STOCK UPDATE"))
        self.stdout.write("="*70)
        self.stdout.write(f"[SETTINGS]  Threads: {options['threads']}")
        self.stdout.write(f"[TIME]  Delay per thread: {options['delay']}s")
        self.stdout.write(f"[TARGET] NASDAQ-only: {options['nasdaq_only']}")
        self.stdout.write(f"[STATS] Max stocks: {options['limit']}")
        self.stdout.write(f"[TEST] Test mode: {'ON' if options['test_mode'] else 'OFF'}")
        self.stdout.write(f" Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get symbols to update
        if options['symbols']:
            symbols = [s.strip().upper() for s in options['symbols'].split(',')]
        else:
            symbols = self._get_nasdaq_symbols(options['limit'], options['nasdaq_only'])
        
        # Test yfinance connectivity
        self._test_yfinance_connectivity()
        
        # Pre-filter delisted symbols if requested
        if options.get('filter_delisted', False):
            symbols = self._filter_delisted_symbols(symbols, sample_size=100)
        
        total_symbols = len(symbols)
        self.stdout.write(f"[UP] Processing {total_symbols} symbols")
        
        # Add immediate progress indicator
        self.stdout.write(f"[READY] Starting to process {total_symbols} symbols...")
        self.stdout.write(f"[FIRST] First 5 symbols: {', '.join(symbols[:5])}")
        self.stdout.flush()
        
        # Process the symbols
        results = self._process_stocks_batch(symbols, options['delay'], options['test_mode'], options['threads'], "NASDAQ UPDATE", options.get('no_proxy', False))
        
        # Calculate final duration
        results['duration'] = time.time() - start_time
        
        # Display final results
        self._display_final_results(results)
        
        # Check if interrupted
        if results.get('interrupted', False):
            self.stdout.write(self.style.WARNING(f"[INTERRUPTED] Script stopped by user after {results['duration']:.1f} seconds"))
            return
        
        # Schedule next run info if in scheduler mode
        if options.get('schedule'):
            next_run = schedule.next_run()
            if next_run:
                self.stdout.write(f" Next update: {next_run.strftime('%H:%M:%S')}")

    def _get_nasdaq_symbols(self, limit, nasdaq_only=True):
        """Get NASDAQ ticker symbols from database and NASDAQ ticker list"""
        symbols = []
        
        if nasdaq_only:
            # Load NASDAQ-only tickers from COMPLETE dataset (5,390+ tickers)
            try:
                import csv
                csv_file = Path(__file__).parent.parent.parent.parent / 'data' / 'complete_nasdaq' / 'complete_nasdaq_export_20250724_182723.csv'
                
                if csv_file.exists():
                    nasdaq_tickers = []
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row.get('Exchange', '').upper() == 'NASDAQ':
                                symbol = row.get('Symbol', '').strip()
                                if symbol and len(symbol) <= 5:  # Filter out weird symbols
                                    nasdaq_tickers.append(symbol)
                    
                    self.stdout.write(f"[STATS] NASDAQ-only mode: {len(nasdaq_tickers):,} total NASDAQ tickers available")
                    
                    # Get existing stocks from database that are NASDAQ-listed
                    existing_stocks = Stock.objects.filter(
                        ticker__in=nasdaq_tickers,
                        exchange__iexact='NASDAQ'
                    ).values_list('ticker', flat=True)
                    
                    # Start with existing stocks
                    symbols.extend(list(existing_stocks))
                    
                    # Add missing NASDAQ tickers
                    missing_tickers = set(nasdaq_tickers) - set(symbols)
                    remaining_limit = limit - len(symbols)
                    symbols.extend(list(missing_tickers)[:remaining_limit])
                    
                    self.stdout.write(f"[SAVE] Found {len(existing_stocks)} existing NASDAQ stocks in database")
                    self.stdout.write(f"[UPDATE] Adding {min(len(missing_tickers), remaining_limit)} new NASDAQ tickers")
                    self.stdout.write(f"[TARGET] Processing {len(symbols)} NASDAQ stocks (limit: {limit})")
                    
                else:
                    # Fallback to small NASDAQ list
                    self.stdout.write(self.style.WARNING("[WARNING] Complete NASDAQ CSV not found, using small list"))
                    sys.path.append(str(Path(__file__).parent.parent.parent.parent / 'data' / 'nasdaq_only'))
                    from nasdaq_only_tickers_20250724_184741 import NASDAQ_ONLY_TICKERS
                    symbols = NASDAQ_ONLY_TICKERS[:limit]
                    self.stdout.write(f"[FALLBACK] Using {len(symbols)} tickers from small NASDAQ list")
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"[ERROR] Failed to load NASDAQ tickers: {e}"))
                self.stdout.write(self.style.WARNING("[FALLBACK] Using database stocks only"))
                symbols = list(Stock.objects.filter(
                    exchange__iexact='NASDAQ'
                ).values_list('ticker', flat=True)[:limit])
        else:
            # Get all stocks from database
            symbols = list(Stock.objects.all().values_list('ticker', flat=True)[:limit])
        
        return symbols[:limit]

    def _filter_delisted_symbols(self, symbols, sample_size=100):
        """Pre-filter symbols to remove delisted/invalid ones"""
        if not symbols:
            return []
        
        self.stdout.write(f"[FILTER] Pre-filtering {len(symbols)} symbols to remove delisted ones...")
        self.stdout.write(f"[FILTER] Testing first {min(sample_size, len(symbols))} symbols...")
        self.stdout.flush()
        
        valid_symbols = []
        delisted_symbols = []
        
        # Test symbols in batches for efficiency
        test_symbols = symbols[:sample_size]
        
        for i, symbol in enumerate(test_symbols, 1):
            try:
                # Quick test with minimal delay
                time.sleep(0.05)  # Very fast testing
                
                ticker_obj = yf.Ticker(symbol)
                info = ticker_obj.info
                
                # Try multiple periods to be more lenient
                hist = None
                for period in ["5d", "1mo", "3mo"]:
                    try:
                        hist = ticker_obj.history(period=period)
                        if not hist.empty:
                            break
                    except:
                        continue
                
                # Check if we have any data and basic info
                has_data = hist is not None and not hist.empty
                has_info = info and len(info) > 5  # Basic check for meaningful info
                
                if not has_data and not has_info:
                    delisted_symbols.append(symbol)
                    if i <= 20:  # Show first 20 delisted
                        self.stdout.write(f"[DELISTED] {symbol}: No data found")
                else:
                    valid_symbols.append(symbol)
                    if i <= 10:  # Show first 10 valid
                        if has_data:
                            price = hist['Close'].iloc[-1]
                            self.stdout.write(f"[VALID] {symbol}: ${price:.2f}")
                        else:
                            self.stdout.write(f"[VALID] {symbol}: Info only")
                
                # Progress update every 20 symbols
                if i % 20 == 0:
                    self.stdout.write(f"[FILTER PROGRESS] {i}/{len(test_symbols)} - Valid: {len(valid_symbols)}, Delisted: {len(delisted_symbols)}")
                    self.stdout.flush()
                    
            except Exception as e:
                delisted_symbols.append(symbol)
                error_msg = str(e).lower()
                if any(x in error_msg for x in ['no data found', 'delisted', '404', 'not found']):
                    if i <= 20:  # Show first 20 errors
                        self.stdout.write(f"[DELISTED] {symbol}: {e}")
                else:
                    if i <= 20:  # Show first 20 errors
                        self.stdout.write(f"[ERROR] {symbol}: {e}")
        
        # Calculate statistics
        if test_symbols:
            valid_percentage = len(valid_symbols) / len(test_symbols)
            delisted_percentage = len(delisted_symbols) / len(test_symbols)
            
            self.stdout.write(f"[FILTER STATS] Tested: {len(test_symbols)} symbols")
            self.stdout.write(f"[FILTER STATS] Valid: {len(valid_symbols)} ({valid_percentage*100:.1f}%)")
            self.stdout.write(f"[FILTER STATS] Delisted: {len(delisted_symbols)} ({delisted_percentage*100:.1f}%)")
            self.stdout.flush()
            
            # Estimate total valid symbols in full list
            estimated_valid = int(len(symbols) * valid_percentage)
            estimated_delisted = len(symbols) - estimated_valid
            
            self.stdout.write(f"[FILTER ESTIMATE] Full list: {len(symbols):,} symbols")
            self.stdout.write(f"[FILTER ESTIMATE] Expected valid: ~{estimated_valid:,} symbols")
            self.stdout.write(f"[FILTER ESTIMATE] Expected delisted: ~{estimated_delisted:,} symbols")
            self.stdout.flush()
            
            # Return only valid symbols from the test, plus remaining untested symbols
            # This gives us a cleaner list to process
            remaining_symbols = symbols[sample_size:]
            final_symbols = valid_symbols + remaining_symbols
            
            self.stdout.write(f"[FILTER RESULT] Returning {len(final_symbols)} symbols for processing")
            self.stdout.write(f"[FILTER RESULT] Includes {len(valid_symbols)} pre-validated + {len(remaining_symbols)} untested")
            self.stdout.flush()
            
            return final_symbols
            
        return symbols

    def _process_stocks_batch(self, symbols, delay, test_mode, num_threads, batch_name="BATCH", no_proxy=False):
        """Process stocks with comprehensive data collection and proxy support"""
        start_time = time.time()
        total_symbols = len(symbols)
        successful = 0
        failed = 0
        
        # Initialize proxy manager only if not disabled
        proxy_manager = None
        if not no_proxy:
            proxy_manager = ProxyManager(min_proxies=50, max_proxies=200)
            self.stdout.write(f"[PROXY] Proxy manager initialized")
        else:
            self.stdout.write(f"[PROXY] Proxy usage disabled")
        self.stdout.flush()
        
        # Add signal handler for graceful shutdown
        import signal
        stop_flag = threading.Event()
        lock = threading.Lock()
        processed = 0
        
        def signal_handler(signum, frame):
            stop_flag.set()
            self.stdout.write("\n[STOP] Signal received. Stopping gracefully...")
            self.stdout.flush()
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        def update_counters(success):
            nonlocal successful, failed, processed
            with lock:
                if success:
                    successful += 1
                else:
                    failed += 1
                processed += 1
                # Update progress safely
                progress['current'] = processed
        
        def patch_yfinance_proxy(proxy):
            import yfinance
            if proxy:
                session = requests.Session()
                session.proxies = {
                    'http': proxy,
                    'https': proxy
                }
                yfinance.shared._requests = session
            else:
                import yfinance
                yfinance.shared._requests = requests.Session()
        
        def process_symbol(symbol, ticker_number):
            """Process a single symbol with comprehensive data collection"""
            try:
                # Get proxy for this ticker (switches every 200) - only if proxy manager exists
                proxy = None
                if proxy_manager:
                    proxy = proxy_manager.get_proxy_for_ticker(ticker_number)
                patch_yfinance_proxy(proxy)
                
                # Minimal delay to avoid overwhelming the API
                time.sleep(random.uniform(0.02, 0.05))
                
                retry = False
                for attempt in range(3):  # Try up to 3 times if rate limited
                    try:
                        # Get comprehensive stock data using individual ticker method
                        ticker_obj = yf.Ticker(symbol)
                        info = ticker_obj.info
                        
                        # Try multiple periods to get historical data
                        hist = None
                        for period in ["5d", "1mo", "3mo"]:
                            try:
                                hist = ticker_obj.history(period=period)
                                if not hist.empty:
                                    break
                            except:
                                continue
                        
                        # Check if we have any meaningful data
                        has_data = hist is not None and not hist.empty
                        has_info = info and len(info) > 5
                        
                        if not has_data and not has_info:
                            # Mark as inactive if no data at all
                            stock = Stock.objects.filter(ticker=symbol).first()
                            if stock:
                                stock.is_active = False
                                stock.save()
                            self.stdout.write(f"[DELISTED] {symbol}: No data found, marking inactive")
                            self.stdout.flush()
                            update_counters(False)
                            return False
                        
                        # Get current price data if available
                        current_price = None
                        if has_data:
                            current_price = hist['Close'].iloc[-1] if len(hist) > 0 else None
                            if current_price is None or pd.isna(current_price):
                                current_price = None  # Will use info data instead
                        
                        # Fallback to info data for current price
                        if current_price is None and has_info:
                            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                        
                        # Calculate price changes
                        price_change_today = None
                        change_percent = None
                        if has_data and len(hist) > 1:
                            prev_price = hist['Close'].iloc[-2]
                            if not pd.isna(prev_price) and prev_price > 0 and current_price:
                                price_change_today = current_price - prev_price
                                change_percent = (price_change_today / prev_price) * 100
                        
                        # Extract comprehensive data from info
                        stock_data = {
                            'ticker': symbol,
                            'symbol': symbol,
                            'company_name': info.get('longName') or info.get('shortName', ''),
                            'name': info.get('longName') or info.get('shortName', ''),
                            'exchange': info.get('exchange', 'NASDAQ'),
                            
                            # Price data
                            'current_price': self._safe_decimal(current_price),
                            'price_change_today': self._safe_decimal(price_change_today),
                            'change_percent': self._safe_decimal(change_percent),
                            
                            # Bid/Ask data
                            'bid_price': self._safe_decimal(info.get('bid')),
                            'ask_price': self._safe_decimal(info.get('ask')),
                            'days_low': self._safe_decimal(info.get('dayLow')),
                            'days_high': self._safe_decimal(info.get('dayHigh')),
                            
                            # Volume data
                            'volume': info.get('volume'),
                            'volume_today': info.get('volume'),
                            'avg_volume_3mon': info.get('averageVolume'),
                            'shares_available': info.get('sharesOutstanding'),
                            
                            # Market data
                            'market_cap': info.get('marketCap'),
                            
                            # Financial ratios
                            'pe_ratio': self._safe_decimal(info.get('trailingPE')),
                            'dividend_yield': self._safe_decimal(info.get('dividendYield')),
                            'earnings_per_share': self._safe_decimal(info.get('trailingEps')),
                            'book_value': self._safe_decimal(info.get('bookValue')),
                            'price_to_book': self._safe_decimal(info.get('priceToBook')),
                            
                            # 52-week range
                            'week_52_low': self._safe_decimal(info.get('fiftyTwoWeekLow')),
                            'week_52_high': self._safe_decimal(info.get('fiftyTwoWeekHigh')),
                            
                            # Target
                            'one_year_target': self._safe_decimal(info.get('targetMeanPrice')),
                        }
                        
                        # Calculate DVAV (Day Volume over Average Volume)
                        if stock_data['volume'] and stock_data['avg_volume_3mon']:
                            try:
                                dvav_val = Decimal(str(stock_data['volume'])) / Decimal(str(stock_data['avg_volume_3mon']))
                                if dvav_val.is_infinite() or dvav_val.is_nan():
                                    stock_data['dvav'] = None
                                else:
                                    stock_data['dvav'] = dvav_val
                            except Exception:
                                stock_data['dvav'] = None
                        
                        # Check for any invalid values (Infinity, NaN, etc.)
                        for k, v in list(stock_data.items()):
                            if isinstance(v, Decimal) and (v.is_infinite() or v.is_nan()):
                                stock_data[k] = None
                        
                        if test_mode:
                            change_str = f"{change_percent:+.2f}%" if change_percent else "N/A"
                            self.stdout.write(f"[SUCCESS] {symbol}: ${current_price:.2f} ({change_str})")
                        else:
                            # Save to database
                            stock, created = Stock.objects.update_or_create(
                                ticker=symbol,
                                defaults=stock_data
                            )
                            
                            # Save price history
                            if current_price:
                                StockPrice.objects.create(
                                    stock=stock,
                                    price=current_price
                                )
                        
                        update_counters(True)
                        return True
                        
                    except Exception as e:
                        err_str = str(e).lower()
                        if 'too many requests' in err_str or 'rate limit' in err_str:
                            if not retry:
                                retry = True
                                # Mark current proxy as failed
                                if proxy:
                                    proxy_manager.mark_proxy_failed(proxy)
                                time.sleep(random.uniform(5, 10))  # Wait longer before retry
                                continue
                        
                        # Mark as inactive if delisted or no data
                        if any(x in err_str for x in ['no data found', 'delisted', 'no price data found', 'not found', '404']):
                            stock = Stock.objects.filter(ticker=symbol).first()
                            if stock:
                                stock.is_active = False
                                stock.save()
                            self.stdout.write(f"[DELISTED] {symbol}: {e}")
                            self.stdout.flush()
                        else:
                            self.stdout.write(f"[ERROR] Error processing {symbol}: {e}")
                            self.stdout.flush()
                        update_counters(False)
                        return False
                
                return False
                
            except Exception as e:
                self.stdout.write(f"[ERROR] Error processing {symbol}: {e}")
                update_counters(False)
                return False
        
        # Process symbols individually
        self.stdout.write(f"[RUN] Starting {batch_name} with individual ticker processing...")
        self.stdout.flush()  # Force output

        progress = {'current': 0}
        
        def print_progress():
            while not stop_flag.is_set():
                try:
                    percent = (progress['current'] / total_symbols) * 100
                    elapsed = time.time() - start_time
                    self.stdout.write(f"[PROGRESS] {progress['current']}/{total_symbols} ({percent:.1f}%) - {elapsed:.1f}s elapsed")
                    self.stdout.flush()  # Force output
                    stop_flag.wait(5)
                except Exception as e:
                    self.stdout.write(f"[PROGRESS ERROR] {e}")
                    break
        
        progress_thread = threading.Thread(target=print_progress, daemon=True)
        progress_thread.start()

        # Add immediate feedback
        self.stdout.write(f"[START] Beginning to process {total_symbols} symbols...")
        self.stdout.flush()

        import concurrent.futures
        
        def process_symbol_with_timeout(symbol, ticker_number, timeout=15):
            """Process symbol with timeout using ThreadPoolExecutor"""
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(process_symbol, symbol, ticker_number)
                    return future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                self.stdout.write(f"[TIMEOUT] {symbol} timed out after {timeout}s, skipping...")
                self.stdout.flush()
                update_counters(False)
                return False
            except Exception as e:
                self.stdout.write(f"[TIMEOUT ERROR] {symbol}: {e}")
                self.stdout.flush()
                update_counters(False)
                return False

        # Use ThreadPoolExecutor for true parallel processing
        self.stdout.write(f"[THREADS] Using {num_threads} threads for parallel processing")
        self.stdout.flush()
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                # Submit all tasks
                future_to_symbol = {}
                for i, symbol in enumerate(symbols, 1):
                    if stop_flag.is_set():
                        break
                    future = executor.submit(process_symbol, symbol, i)
                    future_to_symbol[future] = (symbol, i)
                
                # Process completed tasks
                completed = 0
                for future in concurrent.futures.as_completed(future_to_symbol):
                    if stop_flag.is_set():
                        break
                        
                    symbol, i = future_to_symbol[future]
                    completed += 1
                    
                    try:
                        result = future.result(timeout=15)
                        if completed <= 10:  # Show first 10 results
                            self.stdout.write(f"[RESULT] {symbol}: {'SUCCESS' if result else 'FAILED'}")
                            self.stdout.flush()
                    except concurrent.futures.TimeoutError:
                        self.stdout.write(f"[TIMEOUT] {symbol} timed out")
                        self.stdout.flush()
                        update_counters(False)
                    except Exception as e:
                        self.stdout.write(f"[ERROR] {symbol}: {e}")
                        self.stdout.flush()
                        update_counters(False)
                    
                    # Update progress
                    progress['current'] = completed
                    
                    # Show progress every 50 completed tasks
                    if completed % 50 == 0 or completed == total_symbols:
                        progress_percent = (completed / total_symbols) * 100
                        elapsed = time.time() - start_time
                        rate = completed / elapsed if elapsed > 0 else 0
                        self.stdout.write(f"[STATS] Progress: {completed}/{total_symbols} ({progress_percent:.1f}%) - {elapsed:.1f}s elapsed - {rate:.1f} symbols/sec")
                        self.stdout.flush()
                    
                    # Pause every 500 symbols
                    if completed % 500 == 0 and completed > 0:
                        if proxy_manager:
                            stats = proxy_manager.get_proxy_stats()
                            self.stdout.write(f"[PAUSE] Pausing for 30s after {completed} tickers...")
                            self.stdout.write(f"[PROXY STATS] Working: {stats['total_working']}, Used: {stats['used_in_run']}, Available: {stats['available']}")
                        else:
                            self.stdout.write(f"[PAUSE] Pausing for 30s after {completed} tickers... (no proxy)")
                        self.stdout.flush()
                        time.sleep(30)
        except KeyboardInterrupt:
            self.stdout.write("\n[STOP] Keyboard interrupt detected. Stopping gracefully...")
            self.stdout.write(f"[STOP] Processed {progress['current']} out of {total_symbols} symbols")
            self.stdout.flush()
            stop_flag.set()
            if progress_thread.is_alive():
                progress_thread.join(timeout=2)
            return {
                'total': progress['current'],
                'successful': successful,
                'failed': failed,
                'duration': time.time() - start_time,
                'interrupted': True
            }

        stop_flag.set()
        if progress_thread.is_alive():
            progress_thread.join(timeout=2)  # Wait max 2 seconds
        
        # Final proxy stats
        if proxy_manager:
            final_stats = proxy_manager.get_proxy_stats()
            self.stdout.write(f"[FINAL PROXY STATS] Total: {final_stats['total_working']}, Used: {final_stats['used_in_run']}")
        else:
            self.stdout.write(f"[FINAL PROXY STATS] No proxy used")
        self.stdout.flush()
        
        return {
            'total': total_symbols,
            'successful': successful,
            'failed': failed,
            'duration': time.time() - start_time
        }

    def _safe_decimal(self, value):
        """Safely convert value to Decimal, skip Infinity/NaN"""
        if value is None or pd.isna(value):
            return None
        try:
            d = Decimal(str(value))
            if d.is_infinite() or d.is_nan():
                return None
            return d
        except (ValueError, TypeError, Exception):
            return None

    def _test_yfinance_connectivity(self):
        """Test yfinance API connectivity"""
        try:
            test_ticker = yf.Ticker("AAPL")
            test_info = test_ticker.info
            if test_info:
                self.stdout.write("[SUCCESS] yfinance connectivity test passed")
            else:
                self.stdout.write(self.style.WARNING("[WARNING]  yfinance connectivity test failed"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[ERROR] yfinance connectivity error: {e}"))

    def _display_final_results(self, results):
        """Display comprehensive final results"""
        duration = results['duration']
        success_rate = (results['successful'] / results['total']) * 100 if results['total'] > 0 else 0
        
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS("[STATS] UPDATE COMPLETED"))
        self.stdout.write("="*70)
        self.stdout.write(f"[SUCCESS] Successful: {results['successful']}")
        self.stdout.write(f"[ERROR] Failed: {results['failed']}")
        self.stdout.write(f"[UP] Total processed: {results['total']}")
        self.stdout.write(f"[STATS] Success rate: {success_rate:.1f}%")
        self.stdout.write(f"[TIME]  Duration: {duration:.1f} seconds")
        self.stdout.write(f" Rate: {results['total']/duration:.1f} stocks/second")
        self.stdout.write(f" Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if success_rate < 80:
            self.stdout.write(self.style.WARNING(f"[WARNING]  Low success rate: {success_rate:.1f}%"))
        
        self.stdout.write("="*70)

    def _get_free_proxies(self):
        """Legacy method - now handled by ProxyManager"""
        return []