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
            default=10,
            help='Number of concurrent threads (default: 10)'
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
        
        total_symbols = len(symbols)
        self.stdout.write(f"[UP] Processing {total_symbols} symbols")
        
        # Test yfinance connectivity
        self._test_yfinance_connectivity()
        
        # Process stocks with multithreading
        results = self._process_stocks_batch(
            symbols, 
            options['delay'], 
            options['test_mode'], 
            options['threads'],
            batch_name="NASDAQ UPDATE"
        )
        
        # Calculate final duration
        results['duration'] = time.time() - start_time
        
        # Display final results
        self._display_final_results(results)
        
        # Schedule next run info if in scheduler mode
        if options.get('schedule'):
            next_run = schedule.next_run()
            if next_run:
                self.stdout.write(f" Next update: {next_run.strftime('%H:%M:%S')}")

    def _get_nasdaq_symbols(self, limit, nasdaq_only=True):
        """Get NASDAQ ticker symbols from database and NASDAQ ticker list"""
        symbols = []
        
        if nasdaq_only:
            # Load NASDAQ-only tickers from data file
            try:
                sys.path.append(str(Path(__file__).parent.parent.parent.parent / 'data' / 'nasdaq_only'))
                from nasdaq_only_tickers_20250724_184741 import NASDAQ_ONLY_TICKERS
                
                # Get existing stocks from database that are NASDAQ-listed
                existing_stocks = Stock.objects.filter(
                    ticker__in=NASDAQ_ONLY_TICKERS,
                    exchange__iexact='NASDAQ'
                ).values_list('ticker', flat=True)
                
                # Start with existing stocks
                symbols.extend(list(existing_stocks))
                
                # Add missing NASDAQ tickers that should be in database
                missing_tickers = set(NASDAQ_ONLY_TICKERS) - set(symbols)
                symbols.extend(list(missing_tickers)[:limit - len(symbols)])
                
                self.stdout.write(f"[STATS] NASDAQ-only mode: {len(NASDAQ_ONLY_TICKERS)} total tickers available")
                self.stdout.write(f"[SAVE] Found {len(existing_stocks)} existing stocks in database")
                self.stdout.write(f" Adding {len(missing_tickers)} missing tickers")
                
            except ImportError:
                self.stdout.write(self.style.WARNING("[WARNING]  NASDAQ ticker list not found, falling back to database"))
                symbols = list(Stock.objects.filter(
                    exchange__iexact='NASDAQ'
                ).values_list('ticker', flat=True)[:limit])
        else:
            # Get all stocks from database
            symbols = list(Stock.objects.all().values_list('ticker', flat=True)[:limit])
        
        return symbols[:limit]

    def _process_stocks_batch(self, symbols, delay, test_mode, num_threads, batch_name="BATCH"):
        """Process stocks with multithreading and comprehensive data collection"""
        
        start_time = time.time()
        total_symbols = len(symbols)
        
        # Thread-safe counters
        successful = 0
        failed = 0
        processed = 0
        lock = threading.Lock()
        
        def update_counters(success):
            nonlocal successful, failed, processed
            with lock:
                processed += 1
                if success:
                    successful += 1
                else:
                    failed += 1

        def process_symbol(symbol):
            """Process a single symbol with comprehensive data collection"""
            try:
                time.sleep(delay)  # Rate limiting
                
                # Get comprehensive stock data
                ticker_obj = yf.Ticker(symbol)
                info = ticker_obj.info
                hist = ticker_obj.history(period="5d")
                
                if hist.empty or not info:
                    update_counters(False)
                    return False
                
                # Get current price data
                current_price = hist['Close'].iloc[-1] if len(hist) > 0 else None
                if current_price is None or pd.isna(current_price):
                    update_counters(False)
                    return False
                
                # Calculate price changes
                price_change_today = None
                change_percent = None
                if len(hist) > 1:
                    prev_price = hist['Close'].iloc[-2]
                    if not pd.isna(prev_price) and prev_price > 0:
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
                    'current_price': Decimal(str(current_price)) if current_price else None,
                    'price_change_today': Decimal(str(price_change_today)) if price_change_today else None,
                    'change_percent': Decimal(str(change_percent)) if change_percent else None,
                    
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
                    stock_data['dvav'] = Decimal(str(stock_data['volume'] / stock_data['avg_volume_3mon']))
                
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
                logger.error(f"Error processing {symbol}: {e}")
                update_counters(False)
                return False

        # Execute with thread pool
        self.stdout.write(f"[RUN] Starting {batch_name} with {num_threads} threads...")
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(process_symbol, symbol) for symbol in symbols]
            
            # Monitor progress
            for i, future in enumerate(as_completed(futures), 1):
                if i % 10 == 0 or i == total_symbols:
                    progress = (i / total_symbols) * 100
                    elapsed = time.time() - start_time
                    self.stdout.write(f"[STATS] Progress: {i}/{total_symbols} ({progress:.1f}%) - {elapsed:.1f}s elapsed")

        return {
            'total': total_symbols,
            'successful': successful,
            'failed': failed,
            'duration': time.time() - start_time
        }

    def _safe_decimal(self, value):
        """Safely convert value to Decimal"""
        if value is None or pd.isna(value):
            return None
        try:
            return Decimal(str(value))
        except (ValueError, TypeError):
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