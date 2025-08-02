"""
Django Management Command: Enhanced Stock Data Update using YFinance
WORKING VERSION - Based on enhanced_stock_retrieval_working.py
Auto-scheduler every 3 minutes with NYSE focus and comprehensive data retrieval
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
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import json
import schedule
from datetime import datetime, timedelta
import os
from pathlib import Path
import random
import requests
import csv
import signal

# Add XAMPP MySQL to PATH if it exists
XAMPP_MYSQL_PATH = r"C:\xampp\mysql\bin"
if os.path.exists(XAMPP_MYSQL_PATH) and XAMPP_MYSQL_PATH not in os.environ.get('PATH', ''):
    os.environ['PATH'] = os.environ.get('PATH', '') + os.pathsep + XAMPP_MYSQL_PATH
    print(f"INFO: Added XAMPP MySQL to PATH for stock updates: {XAMPP_MYSQL_PATH}")

logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_flag = False

def signal_handler(signum, frame):
    """Handle interrupt signals gracefully"""
    global shutdown_flag
    print("\nReceived interrupt signal. Shutting down gracefully...")
    shutdown_flag = True

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

class Command(BaseCommand):
    help = 'Enhanced stock data update with 3-minute auto-scheduler and NYSE focus - WORKING VERSION'

    def add_arguments(self, parser):
        parser.add_argument(
            '--symbols',
            type=str,
            help='Comma-separated list of stock symbols to update'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=1000,
            help='Maximum number of stocks to update (default: 1000 for NYSE)'
        )
        parser.add_argument(
            '--schedule',
            action='store_true',
            help='Run scheduler mode (updates every 3 minutes continuously)'
        )
        parser.add_argument(
            '--startup',
            action='store_true',
            help='Run initial startup update then start scheduler'
        )
        parser.add_argument(
            '--nyse-only',
            action='store_true',
            default=True,
            help='Update only NYSE-listed tickers (default: True)'
        )
        parser.add_argument(
            '--threads',
            type=int,
            default=30,
            help='Number of concurrent threads (default: 30)'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=0.01,
            help='Delay between requests in seconds (default: 0.01)'
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
            '--timeout',
            type=int,
            default=8,
            help='Request timeout in seconds (default: 8)'
        )
        parser.add_argument(
            '--csv',
            type=str,
            default='flat-ui__data-Fri Aug 01 2025.csv',
            help='NYSE CSV file path (default: flat-ui__data-Fri Aug 01 2025.csv)'
        )

    def handle(self, *args, **options):
        """Main command handler"""
        global shutdown_flag
        
        if options['schedule']:
            self._run_scheduler(options)
        elif options['startup']:
            self._run_startup_mode(options)
        else:
            self._run_single_update(options)

    def _run_scheduler(self, options):
        """Run the scheduler mode"""
        self.stdout.write("=" * 70)
        self.stdout.write("[UP] COMPREHENSIVE NYSE STOCK UPDATE")
        self.stdout.write("=" * 70)
        self.stdout.write(f"[SETTINGS] Threads: {options['threads']}")
        self.stdout.write(f"[TIME] Delay per thread: {options['delay']}s")
        self.stdout.write(f"[TARGET] NYSE-only: {options['nyse_only']}")
        self.stdout.write(f"[STATS] Max stocks: {options['limit']}")
        self.stdout.write(f"[TEST] Test mode: {'ON' if options['test_mode'] else 'OFF'}")
        self.stdout.write(f" Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Schedule the job to run every 3 minutes
        schedule.every(3).minutes.do(self._run_single_update, options)
        
        self.stdout.write(f"[SCHEDULER] Stock data updates scheduled every 3 minutes")
        self.stdout.write(f"[SCHEDULER] Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write("\n[SCHEDULER] Stopped by user")
            shutdown_flag = True

    def _run_startup_mode(self, options):
        """Run initial update then start scheduler"""
        self.stdout.write("[RUN] STARTUP MODE: Running initial update then starting scheduler")
        
        # Run initial update
        self._run_single_update(options)
        
        # Start scheduler
        self._run_scheduler(options)

    def _run_single_update(self, options):
        """Run a single update cycle"""
        global shutdown_flag
        
        start_time = time.time()
        
        self.stdout.write("=" * 70)
        self.stdout.write("[UP] COMPREHENSIVE NYSE STOCK UPDATE")
        self.stdout.write("=" * 70)
        self.stdout.write(f"[SETTINGS] Threads: {options['threads']}")
        self.stdout.write(f"[TIME] Delay per thread: {options['delay']}s")
        self.stdout.write(f"[TARGET] NYSE-only: {options['nyse_only']}")
        self.stdout.write(f"[STATS] Max stocks: {options['limit']}")
        self.stdout.write(f"[TEST] Test mode: {'ON' if options['test_mode'] else 'OFF'}")
        self.stdout.write(f" Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get symbols to update
        if options['symbols']:
            symbols = [s.strip().upper() for s in options['symbols'].split(',')]
        else:
            # Use the working approach from enhanced_stock_retrieval_working.py
            csv_file = options['csv']
            symbols = self.load_nyse_symbols(csv_file, test_mode=False, max_symbols=options['limit'])
        
        if not symbols:
            self.stdout.write("ERROR: No symbols loaded. Exiting.")
            return
        
        # Test yfinance connectivity
        connectivity_ok = self._test_yfinance_connectivity()
        if not connectivity_ok:
            self.stdout.write("[INFO] Proceeding with limited connectivity - individual requests may still work")
        self.stdout.flush()
        
        # Pre-filter delisted symbols if requested
        if options.get('filter_delisted', False):
            symbols = self._filter_delisted_symbols(symbols, sample_size=100)
        else:
            self.stdout.write(f"[INFO] Skipping delisted filtering - processing all {len(symbols)} symbols")
            self.stdout.flush()
        
        total_symbols = len(symbols)
        self.stdout.write(f"[UP] Processing {total_symbols} symbols")
        
        # Add immediate progress indicator
        self.stdout.write(f"[READY] Starting to process {total_symbols} symbols...")
        self.stdout.write(f"[FIRST] First 5 symbols: {', '.join(symbols[:5])}")
        self.stdout.flush()
        
        # Process the symbols using the working approach
        results = self._process_stocks_working(symbols, options['delay'], options['test_mode'], options['threads'], options['timeout'], options['no_proxy'])
        
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

    def load_proxies_direct(self, proxy_file):
        """Load proxies directly from JSON file without validation"""
        try:
            with open(proxy_file, 'r') as f:
                proxy_data = json.load(f)
            
            # Extract proxy list from the JSON structure
            if isinstance(proxy_data, dict):
                # Try different possible keys
                if 'proxies' in proxy_data:
                    proxies = proxy_data['proxies']
                elif 'working_proxies' in proxy_data:
                    proxies = proxy_data['working_proxies']
                else:
                    # Assume the entire dict is the proxy list
                    proxies = list(proxy_data.values()) if proxy_data else []
            elif isinstance(proxy_data, list):
                proxies = proxy_data
            else:
                proxies = []
            
            # Filter out None/empty values
            proxies = [p for p in proxies if p and isinstance(p, str)]
            
            self.stdout.write(f"Loaded {len(proxies)} proxies directly from {proxy_file}")
            return proxies
            
        except FileNotFoundError:
            self.stdout.write(f"Proxy file not found: {proxy_file}")
            return []
        except Exception as e:
            self.stdout.write(f"Error loading proxies: {e}")
            return []

    def patch_yfinance_proxy(self, proxy):
        """Patch yfinance to use proxy"""
        if not proxy:
            return
            
        try:
            session = requests.Session()
            session.proxies = {
                'http': proxy,
                'https': proxy
            }
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            import yfinance.shared
            yfinance.shared._requests = session
        except Exception as e:
            self.stdout.write(f"Failed to set proxy {proxy}: {e}")

    def _extract_pe_ratio(self, info):
        """Extract PE ratio with multiple fallback options"""
        if not info:
            return None
        
        # Try multiple PE ratio fields
        pe_fields = ['trailingPE', 'forwardPE', 'priceToBook', 'priceToSalesTrailing12Months']
        
        for field in pe_fields:
            value = info.get(field)
            if value is not None and value != 0 and not pd.isna(value):
                try:
                    return float(value)
                except (ValueError, TypeError):
                    continue
        
        return None

    def _extract_dividend_yield(self, info):
        """Extract dividend yield with proper formatting"""
        if not info:
            return None
        
        # Try multiple dividend yield fields
        dividend_fields = ['dividendYield', 'fiveYearAvgDividendYield', 'trailingAnnualDividendYield']
        
        for field in dividend_fields:
            value = info.get(field)
            if value is not None and not pd.isna(value):
                try:
                    # Convert to percentage if it's a decimal
                    if isinstance(value, float) and value < 1:
                        return float(value * 100)
                    else:
                        return float(value)
                except (ValueError, TypeError):
                    continue
        
        return None

    def _safe_decimal(self, value):
        """Safely convert value to Decimal, skip Infinity/NaN"""
        if value is None or pd.isna(value):
            return None
        try:
            if isinstance(value, (int, float)):
                if pd.isna(value) or value == float('inf') or value == float('-inf'):
                    return None
                return Decimal(str(value))
            else:
                return Decimal(str(value))
        except (ValueError, TypeError, OverflowError):
            return None

    def load_nyse_symbols(self, csv_file, test_mode=False, max_symbols=None):
        """Load NYSE symbols from CSV file, filtering delisted stocks"""
        symbols = []
        delisted_count = 0
        etf_count = 0
        active_count = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    symbol = row.get('Symbol', '').strip()
                    financial_status = row.get('Financial Status', '').strip()
                    etf = row.get('ETF', '').strip()
                    
                    # Skip empty symbols
                    if not symbol:
                        continue
                    
                    # Filter out delisted stocks (Financial Status = 'D')
                    if financial_status == 'D':
                        delisted_count += 1
                        continue
                    
                    # Filter out ETFs (ETF = 'Y')
                    if etf == 'Y':
                        etf_count += 1
                        continue
                    
                    # Only include active stocks
                    symbols.append(symbol)
                    active_count += 1
                    
                    # Limit to 100 for test mode
                    if test_mode and len(symbols) >= 100:
                        break
                    
                    # Limit to max_symbols if specified
                    if max_symbols and len(symbols) >= max_symbols:
                        break
        
        except FileNotFoundError:
            self.stdout.write(f"CSV file not found: {csv_file}")
            return []
        except Exception as e:
            self.stdout.write(f"Error reading CSV file: {e}")
            return []
        
        self.stdout.write(f"Loaded {len(symbols)} active NYSE symbols")
        self.stdout.write(f"Filtered out {delisted_count} delisted stocks")
        self.stdout.write(f"Filtered out {etf_count} ETFs")
        self.stdout.write(f"Active stocks: {active_count}")
        
        return symbols

    def process_symbol(self, symbol, ticker_number, proxies, timeout=8, test_mode=False):
        """Process a single symbol with comprehensive data collection and Django integration"""
        global shutdown_flag
        
        if shutdown_flag:
            return None
            
        try:
            # Get proxy for this ticker (if available)
            proxy = None
            if proxies and len(proxies) > 0:
                proxy = proxies[ticker_number % len(proxies)]
                if ticker_number <= 3: # Show proxy info for first 3 tickers only
                    self.stdout.write(f"[PROXY] {symbol}: Using proxy {proxy}")
            
            self.patch_yfinance_proxy(proxy)
            
            # Minimal delay to avoid rate limiting
            time.sleep(random.uniform(0.01, 0.02))
            
            # Try multiple approaches to get data
            ticker_obj = yf.Ticker(symbol)
            info = None
            hist = None
            current_price = None
            
            # Approach 1: Try to get basic info
            try:
                info = ticker_obj.info
            except:
                pass
            
            # Approach 2: Try to get historical data with multiple periods
            for period in ["1d", "5d", "1mo"]:
                try:
                    hist = ticker_obj.history(period=period, timeout=timeout)
                    if hist is not None and not hist.empty and len(hist) > 0:
                        try:
                            current_price = hist['Close'].iloc[-1]
                            if current_price is not None and not pd.isna(current_price):
                                break
                        except:
                            continue
                except Exception as e:
                    continue
            
            # Approach 3: Try to get current price from info if historical failed
            if current_price is None and info:
                try:
                    current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('regularMarketOpen')
                except:
                    pass
            
            # Approach 4: Try a simple quote request
            if current_price is None:
                try:
                    quote = ticker_obj.quote_type
                    if quote:
                        # If we can get quote type, symbol exists
                        pass
                except:
                    pass
            
            # Determine if we have enough data to process
            has_data = hist is not None and not hist.empty
            has_info = info and isinstance(info, dict) and len(info) > 3
            has_price = current_price is not None and not pd.isna(current_price)
            
            if not has_data and not has_info:
                self.stdout.write(f"[NO DATA] {symbol}: No data available")
                return None
            
            # Extract comprehensive data with better PE ratio and dividend yield handling
            stock_data = {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', symbol)) if info else symbol,
                'current_price': self._safe_decimal(current_price) if current_price else None,
                'previous_close': self._safe_decimal(info.get('previousClose')) if info else None,
                'open_price': self._safe_decimal(info.get('regularMarketOpen')) if info else None,
                'days_low': self._safe_decimal(info.get('dayLow')) if info else None,
                'days_high': self._safe_decimal(info.get('dayHigh')) if info else None,
                'volume': self._safe_decimal(info.get('volume')) if info else None,
                'volume_today': self._safe_decimal(info.get('volume')) if info else None,
                'avg_volume_3mon': self._safe_decimal(info.get('averageVolume')) if info else None,
                'market_cap': self._safe_decimal(info.get('marketCap')) if info else None,
                'pe_ratio': self._safe_decimal(self._extract_pe_ratio(info)) if info else None,
                'dividend_yield': self._safe_decimal(self._extract_dividend_yield(info)) if info else None,
                'week_52_low': self._safe_decimal(info.get('fiftyTwoWeekLow')) if info else None,
                'week_52_high': self._safe_decimal(info.get('fiftyTwoWeekHigh')) if info else None,
                'beta': self._safe_decimal(info.get('beta')) if info else None,
                'exchange': info.get('exchange') if info else None,
                'earnings_per_share': self._safe_decimal(info.get('trailingEps')) if info else None,
                'book_value': self._safe_decimal(info.get('bookValue')) if info else None,
                'price_to_book': self._safe_decimal(info.get('priceToBook')) if info else None,
                'one_year_target': self._safe_decimal(info.get('targetMeanPrice')) if info else None,
                'price_change_today': None,
                'change_percent': None,
                'price_change_week': None,
                'price_change_month': None,
                'price_change_year': None,
                'pe_change_3mon': None,
                'market_cap_change_3mon': None,
                'bid_price': None,
                'ask_price': None,
                'bid_ask_spread': None,
                'shares_available': None,
                'dvav': None,
                'last_updated': timezone.now(),
                'created_at': timezone.now()
            }
            
            # Calculate price changes if historical data available
            if has_data and len(hist) > 1:
                try:
                    current = hist['Close'].iloc[-1]
                    previous = hist['Close'].iloc[-2]
                    if current and previous:
                        change = current - previous
                        change_percent = (change / previous) * 100
                        stock_data['price_change_today'] = self._safe_decimal(change)
                        stock_data['change_percent'] = self._safe_decimal(change_percent)
                except:
                    pass
            
            # Add volume analysis
            if stock_data.get('volume') and stock_data.get('avg_volume_3mon'):
                try:
                    volume_ratio = stock_data['volume'] / stock_data['avg_volume_3mon']
                    stock_data['dvav'] = self._safe_decimal(volume_ratio)
                except:
                    pass
            
            # Save to database if not in test mode
            if not test_mode:
                try:
                    # Create or update Stock object
                    stock, created = Stock.objects.update_or_create(
                        symbol=symbol,
                        defaults=stock_data
                    )
                    
                    # Create StockPrice record
                    if stock_data.get('current_price'):
                        StockPrice.objects.create(
                            stock=stock,
                            price=stock_data['current_price'],
                            volume=stock_data.get('volume_today'),
                            date=timezone.now()
                        )
                    
                    # Log successful data extraction (only every 50th success to reduce noise)
                    if ticker_number % 50 == 0:
                        pe_ratio = stock_data.get('pe_ratio', 'N/A')
                        dividend_yield = stock_data.get('dividend_yield', 'N/A')
                        self.stdout.write(f"[SUCCESS] {symbol}: ${stock_data.get('current_price', 'N/A')} - {stock_data.get('name', 'N/A')} - PE: {pe_ratio} - Div: {dividend_yield}%")
                    
                    return stock_data
                    
                except Exception as e:
                    self.stdout.write(f"[DB ERROR] {symbol}: {e}")
                    return None
            else:
                # Test mode - log the data without saving (only every 50th to reduce noise)
                if ticker_number % 50 == 0:
                    pe_ratio = stock_data.get('pe_ratio', 'N/A')
                    dividend_yield = stock_data.get('dividend_yield', 'N/A')
                    self.stdout.write(f"[TEST] {symbol}: ${stock_data.get('current_price', 'N/A')} - {stock_data.get('name', 'N/A')} - PE: {pe_ratio} - Div: {dividend_yield}%")
                
                return stock_data
            
        except Exception as e:
            self.stdout.write(f"[ERROR] {symbol}: {e}")
            return None

    def _process_stocks_working(self, symbols, delay, test_mode, num_threads, timeout, no_proxy=False):
        """Process stocks using the working approach from enhanced_stock_retrieval_working.py"""
        start_time = time.time()
        total_symbols = len(symbols)
        successful = 0
        failed = 0
        
        # Load proxies directly from JSON file (non-validating approach)
        proxies = []
        if not no_proxy:
            proxies = self.load_proxies_direct('working_proxies.json')
        else:
            self.stdout.write(f"[PROXY] Proxy usage disabled")
        
        self.stdout.flush()
        
        # Process symbols using ThreadPoolExecutor
        self.stdout.write(f"[RUN] Starting NYSE UPDATE with individual ticker processing...")
        self.stdout.flush()
        
        # Use ThreadPoolExecutor for parallel processing with better timeout handling
        self.stdout.write(f"Submitting {len(symbols)} tasks to thread pool...")
        
        try:
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                future_to_symbol = {}
                for i, symbol in enumerate(symbols, 1):
                    if shutdown_flag:
                        break
                    future = executor.submit(self.process_symbol, symbol, i, proxies, timeout, test_mode)
                    future_to_symbol[future] = symbol
                
                self.stdout.write(f"Submitted {len(future_to_symbol)} tasks. Processing...")
                completed = 0
                
                for future in as_completed(future_to_symbol):
                    if shutdown_flag:
                        self.stdout.write("Shutdown requested. Cancelling remaining tasks...")
                        break
                        
                    symbol = future_to_symbol[future]
                    completed += 1
                    
                    try:
                        # Use shorter timeout for individual tasks
                        result = future.result(timeout=timeout + 2)
                        if result:
                            successful += 1
                        else:
                            failed += 1
                    except TimeoutError:
                        self.stdout.write(f"[TIMEOUT] {symbol}: Task timed out")
                        failed += 1
                    except Exception as e:
                        self.stdout.write(f"[ERROR] {symbol}: {e}")
                        failed += 1
                    
                    # Show progress every 10 completed or at the end
                    if completed % 10 == 0 or completed == len(symbols):
                        self.stdout.write(f"[PROGRESS] {completed}/{len(symbols)} completed ({successful} successful, {failed} failed)")
                        
                    # Add a small delay to prevent overwhelming
                    time.sleep(0.01)
        
        except KeyboardInterrupt:
            self.stdout.write("\nInterrupted by user. Shutting down gracefully...")
            shutdown_flag = True
        except Exception as e:
            self.stdout.write(f"ERROR: Thread pool execution failed: {e}")
        
        elapsed = time.time() - start_time
        
        return {
            'successful': successful,
            'failed': failed,
            'total': total_symbols,
            'duration': elapsed,
            'interrupted': shutdown_flag
        }

    def _test_yfinance_connectivity(self):
        """Test yfinance connectivity"""
        try:
            ticker = yf.Ticker('AAPL')
            info = ticker.info
            if info and isinstance(info, dict):
                self.stdout.write("[SUCCESS] yfinance connectivity test passed")
                return True
        except Exception as e:
            self.stdout.write(f"[WARNING] yfinance connectivity test failed: {e}")
            return False

    def _display_final_results(self, results):
        """Display final results"""
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write("SCAN RESULTS")
        self.stdout.write("=" * 70)
        self.stdout.write(f"SUCCESSFUL: {results['successful']}")
        self.stdout.write(f"FAILED: {results['failed']}")
        if results['total'] > 0:
            success_rate = (results['successful'] / results['total']) * 100
            self.stdout.write(f"SUCCESS RATE: {success_rate:.1f}%")
        self.stdout.write(f"TIME: {results['duration']:.2f}s")
        if results['duration'] > 0:
            rate = results['total'] / results['duration']
            self.stdout.write(f"RATE: {rate:.2f} symbols/sec")
        
        self.stdout.write("=" * 70)

    def _filter_delisted_symbols(self, symbols, sample_size=100):
        """Filter out delisted symbols (placeholder for compatibility)"""
        # This is a simplified version - the CSV loading already filters delisted symbols
        return symbols