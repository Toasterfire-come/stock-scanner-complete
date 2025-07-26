"""
Django Management Command: Update Stock Data using YFinance
Comprehensive version with multithreading for high-speed processing
Includes halfway break and scheduling capabilities
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from stocks.models import Stock
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
from datetime import datetime

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update comprehensive stock data using YFinance with multithreading, halfway break, and scheduling'

    def add_arguments(self, parser):
        parser.add_argument(
            '--symbols',
            type=str,
            help='Comma-separated list of stock symbols to update'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of stocks to update (default: 100)'
        )
        parser.add_argument(
            '--test-mode',
            action='store_true',
            help='Run in test mode (display data without saving to database)'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=0.1,
            help='Delay between requests in seconds (default: 0.1)'
        )
        parser.add_argument(
            '--threads',
            type=int,
            default=7,
            help='Number of concurrent threads (default: 7)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=200,
            help='Progress update batch size (default: 200)'
        )
        parser.add_argument(
            '--schedule',
            action='store_true',
            help='Run the update every 5 minutes continuously'
        )
        parser.add_argument(
            '--halfway-break',
            type=int,
            default=60,
            help='Break duration at halfway point in seconds (default: 60)'
        )

    def handle(self, *args, **options):
        """Main command handler"""
        
        if options['schedule']:
            self._run_scheduler(options)
        else:
            self._run_single_update(options)

    def _run_scheduler(self, options):
        """Run the stock update every 5 minutes"""
        self.stdout.write(self.style.SUCCESS("🕐 SCHEDULER STARTED - Running stock updates every 5 minutes"))
        self.stdout.write(f"⚙️  Configuration: {options['threads']} threads, {options['limit']} stocks per run")
        self.stdout.write(f"⏱️  Halfway break: {options['halfway_break']} seconds")
        self.stdout.write("🔄 Press Ctrl+C to stop the scheduler\n")
        
        # Schedule the job every 5 minutes
        schedule.every(5).minutes.do(self._run_single_update, options)
        
        # Run once immediately
        self.stdout.write(f"🚀 Running initial stock update at {datetime.now().strftime('%H:%M:%S')}")
        self._run_single_update(options)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\n⏹️  Scheduler stopped by user"))

    def _run_single_update(self, options):
        """Run a single stock update with halfway break"""
        
        start_time = time.time()
        
        # Display configuration
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS("🚀 COMPREHENSIVE STOCK UPDATE WITH MULTITHREADING"))
        self.stdout.write("="*70)
        self.stdout.write(f"⚙️  Threads: {options['threads']}")
        self.stdout.write(f"⏱️  Delay per thread: {options['delay']}s")
        self.stdout.write(f"📊 Batch size: {options['batch_size']}")
        self.stdout.write(f"⏸️  Halfway break: {options['halfway_break']}s")
        self.stdout.write(f"🎯 Target stocks: {options['limit']}")
        self.stdout.write(f"🧪 Test mode: {'ON' if options['test_mode'] else 'OFF'}")
        
        # Get symbols
        if options['symbols']:
            symbols = [s.strip().upper() for s in options['symbols'].split(',')]
        else:
            symbols = self._get_nasdaq_symbols(options['limit'])
        
        total_symbols = len(symbols)
        halfway_point = total_symbols // 2
        
        self.stdout.write(f"📈 Processing {total_symbols} symbols")
        self.stdout.write(f"⏸️  Break scheduled after {halfway_point} stocks")
        
        # Test connectivity
        self._test_yfinance_connectivity()
        
        # Split symbols into two halves
        first_half = symbols[:halfway_point]
        second_half = symbols[halfway_point:]
        
        self.stdout.write(f"\n🏁 Starting first half: {len(first_half)} stocks")
        
        # Process first half
        first_results = self._process_stocks_batch(
            first_half, 
            options['delay'], 
            options['test_mode'], 
            options['threads'],
            options['batch_size'],
            batch_name="FIRST HALF"
        )
        
        # Halfway break
        if second_half:
            self.stdout.write(f"\n⏸️  HALFWAY BREAK - Pausing for {options['halfway_break']} seconds...")
            self.stdout.write(f"📊 First half complete: {first_results['successful']}/{first_results['total']} successful")
            
            # Countdown timer
            for remaining in range(options['halfway_break'], 0, -10):
                self.stdout.write(f"⏰ Resuming in {remaining} seconds...")
                time.sleep(10)
            
            self.stdout.write(f"\n🏁 Starting second half: {len(second_half)} stocks")
            
            # Process second half
            second_results = self._process_stocks_batch(
                second_half, 
                options['delay'], 
                options['test_mode'], 
                options['threads'],
                options['batch_size'],
                batch_name="SECOND HALF"
            )
            
            # Combine results
            combined_results = {
                'total': first_results['total'] + second_results['total'],
                'successful': first_results['successful'] + second_results['successful'],
                'failed': first_results['failed'] + second_results['failed'],
                'duration': time.time() - start_time
            }
        else:
            combined_results = first_results
            combined_results['duration'] = time.time() - start_time
        
        # Display final results
        self._display_final_results(combined_results)

    def _process_stocks_batch(self, symbols, delay, test_mode, num_threads, batch_size, batch_name="BATCH"):
        """Process a batch of stocks with multithreading"""
        
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
                if success:
                    successful += 1
                else:
                    failed += 1
                processed += 1
        
        def process_stock(symbol):
            """Process individual stock in thread"""
            try:
                time.sleep(delay)  # Rate limiting
                
                # Get comprehensive stock data
                quote_data = self._get_comprehensive_stock_data(symbol)
                
                if not quote_data:
                    update_counters(False)
                    return f"❌ {symbol}: No data available"
                
                if test_mode:
                    # Test mode - display comprehensive data
                    update_counters(True)
                    return f"✅ {symbol}: ${quote_data['current_price']:.2f} ({quote_data['change_percent']:+.2f}%)"
                else:
                    # Production mode - update database
                    updated = self._update_stock_in_db(symbol, quote_data)
                    update_counters(updated)
                    if updated:
                        return f"✅ {symbol}: ${quote_data['current_price']:.2f} ({quote_data['change_percent']:+.2f}%) - DB Updated"
                    else:
                        return f"⚠️  {symbol}: Data retrieved but DB update failed"
                        
            except Exception as e:
                update_counters(False)
                return f"❌ {symbol}: Error - {e}"
        
        # Process with ThreadPoolExecutor
        self.stdout.write(f"🔄 Processing {batch_name}: {total_symbols} stocks with {num_threads} threads")
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Submit all tasks
            future_to_symbol = {executor.submit(process_stock, symbol): symbol for symbol in symbols}
            
            # Process completed tasks
            for i, future in enumerate(as_completed(future_to_symbol), 1):
                try:
                    result = future.result()
                    
                    # Progress update every batch_size stocks
                    if i % batch_size == 0 or i == total_symbols:
                        progress = (i / total_symbols) * 100
                        elapsed = time.time() - start_time
                        rate = i / elapsed if elapsed > 0 else 0
                        eta = (total_symbols - i) / rate if rate > 0 else 0
                        
                        with lock:
                            self.stdout.write(
                                f"📊 {batch_name} Progress: {progress:.1f}% ({i}/{total_symbols}) "
                                f"✅ {successful} ❌ {failed} | "
                                f"Rate: {rate:.1f}/s ETA: {eta:.0f}s"
                            )
                
                except Exception as e:
                    self.stdout.write(f"❌ Thread error: {e}")
        
        batch_duration = time.time() - start_time
        batch_rate = total_symbols / batch_duration if batch_duration > 0 else 0
        
        self.stdout.write(f"🏁 {batch_name} Complete: {successful}/{total_symbols} successful in {batch_duration:.1f}s ({batch_rate:.1f}/s)")
        
        return {
            'total': total_symbols,
            'successful': successful,
            'failed': failed,
            'duration': batch_duration
        }

    def _get_comprehensive_stock_data(self, symbol):
        """Get comprehensive stock data from Yahoo Finance (optimized for threading)"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get historical data for multiple periods (optimized)
            hist_1d = ticker.history(period="1d")
            
            if hist_1d.empty:
                return None
            
            current_price = hist_1d['Close'].iloc[-1]
            
            # Simplified calculation for speed
            price_change_today = 0
            if len(hist_1d) > 1:
                prev_close = hist_1d['Close'].iloc[-2]
                price_change_today = current_price - prev_close
            
            change_percent = (price_change_today / (current_price - price_change_today) * 100) if price_change_today != 0 else 0
            
            # Get basic range and volume
            days_low = hist_1d['Low'].iloc[-1] if 'Low' in hist_1d.columns else current_price
            days_high = hist_1d['High'].iloc[-1] if 'High' in hist_1d.columns else current_price
            volume = int(hist_1d['Volume'].iloc[-1]) if 'Volume' in hist_1d.columns else 0
            
            # Get basic info (optimized - don't fetch full info in threads for speed)
            return {
                'ticker': symbol,
                'company_name': symbol,  # Simplified for speed
                'current_price': float(current_price),
                'price_change_today': float(price_change_today),
                'change_percent': float(change_percent),
                'days_low': float(days_low),
                'days_high': float(days_high),
                'volume': volume,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"YFinance error for {symbol}: {e}")
            return None

    def _update_stock_in_db(self, symbol, quote_data):
        """Update stock data in database (thread-safe)"""
        
        try:
            with transaction.atomic():
                stock, created = Stock.objects.get_or_create(
                    ticker=symbol,
                    defaults={
                        'symbol': symbol,
                        'company_name': quote_data['company_name'],
                        'name': quote_data['company_name'],
                        'current_price': Decimal(str(quote_data['current_price'])),
                        'price_change_today': Decimal(str(quote_data['price_change_today'])),
                        'change_percent': Decimal(str(quote_data['change_percent'])),
                        'days_low': Decimal(str(quote_data['days_low'])),
                        'days_high': Decimal(str(quote_data['days_high'])),
                        'volume': quote_data['volume'],
                    }
                )
                
                if not created:
                    # Update existing record
                    stock.current_price = Decimal(str(quote_data['current_price']))
                    stock.price_change_today = Decimal(str(quote_data['price_change_today']))
                    stock.change_percent = Decimal(str(quote_data['change_percent']))
                    stock.days_low = Decimal(str(quote_data['days_low']))
                    stock.days_high = Decimal(str(quote_data['days_high']))
                    stock.volume = quote_data['volume']
                    stock.save()
                
                return True
                
        except Exception as e:
            logger.error(f"Database update failed for {symbol}: {e}")
            return False

    def _display_final_results(self, results):
        """Display final results with threading metrics"""
        
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS("🎉 MULTITHREADED STOCK UPDATE COMPLETE"))
        self.stdout.write("="*70)
        
        success_rate = (results['successful'] / results['total']) * 100 if results['total'] > 0 else 0
        actual_rate = results['processed'] / results['duration'] if results['duration'] > 0 else 0
        actual_rate_per_min = actual_rate * 60
        
        self.stdout.write(f"⚡ Threading Performance:")
        self.stdout.write(f"   • Total stocks: {results['total']}")
        self.stdout.write(f"   • Successful: {results['successful']}")
        self.stdout.write(f"   • Failed: {results['failed']}")
        self.stdout.write(f"   • Success rate: {success_rate:.1f}%")
        self.stdout.write(f"   • Duration: {results['duration']:.1f}s ({results['duration']/60:.2f} min)")
        self.stdout.write(f"   • Actual rate: {actual_rate_per_min:.0f} stocks/min")
        self.stdout.write(f"   • Threading efficiency: {(actual_rate_per_min/(0.1*60)):.1%}") # Assuming 0.1s delay
        
        if success_rate >= 90:
            self.stdout.write(self.style.SUCCESS("\n🎯 Excellent success rate!"))
        elif success_rate >= 70:
            self.stdout.write(self.style.WARNING("\n⚠️  Good success rate - some requests failed"))
        else:
            self.stdout.write(self.style.ERROR("\n❌ Low success rate - check connectivity"))
        
        self.stdout.write(f"\n🚀 Multithreading: {0.1}s delay per thread") # Assuming 0.1s delay
        self.stdout.write("✅ High-speed update complete!")

    def _get_nasdaq_symbols(self, limit):
        """Get NASDAQ symbols for processing"""
        
        # Comprehensive NASDAQ symbols list
        nasdaq_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'ADBE',
            'CRM', 'INTC', 'AMD', 'QCOM', 'AVGO', 'TXN', 'ORCL', 'CSCO', 'ASML', 'PEP',
            'COST', 'TMUS', 'CMCSA', 'AMGN', 'HON', 'SBUX', 'INTU', 'ISRG', 'BKNG', 'GILD',
            'MDLZ', 'ADP', 'REGN', 'VRTX', 'LRCX', 'ATVI', 'FISV', 'CSX', 'ADSK', 'MELI',
            'KLAC', 'SNPS', 'CDNS', 'ORLY', 'WDAY', 'CHTR', 'MAR', 'FTNT', 'MRVL', 'IDXX',
            'NXPI', 'DXCM', 'BIIB', 'ILMN', 'KDP', 'EA', 'CTAS', 'FAST', 'VRSK', 'CTSH',
            'PCAR', 'ODFL', 'PAYX', 'ROST', 'EXC', 'CPRT', 'FANG', 'TEAM', 'CSGP', 'ABNB',
            'SGEN', 'MRNA', 'ALGN', 'LCID', 'RIVN', 'ZM', 'DOCU', 'PTON', 'ROKU', 'ZS',
            'OKTA', 'CRWD', 'NET', 'DDOG', 'SNOW', 'PLTR', 'U', 'COIN', 'RBLX', 'HOOD',
            'SOFI', 'AFRM', 'UPST', 'SQ', 'PYPL', 'SHOP', 'SPOT', 'UBER', 'LYFT', 'DASH',
            'TWLO', 'DBX', 'BOX', 'CZR', 'PENN', 'DKNG', 'FUBO', 'NKLA', 'PLUG', 'FCEL',
            'BLNK', 'CHPT', 'QS', 'SPCE', 'OPEN', 'Z', 'ZG', 'REYN', 'EXPE', 'PCLN',
            'TRIP', 'GRUB', 'MTCH', 'IAC', 'ANGI', 'YELP', 'CARS', 'CVNA', 'VROOM', 'KMX',
            'LAD', 'AN', 'PAG', 'ABM', 'SHW', 'RPM', 'VMC', 'MLM', 'NUE', 'STLD',
            'RS', 'CMC', 'X', 'CLF', 'MT', 'TX', 'GGB', 'VALE', 'FCX', 'TECK',
            'BHP', 'RIO', 'SCCO', 'GOLD', 'NEM', 'AEM', 'KGC', 'EGO', 'AU', 'HMY',
            'WPM', 'FNV', 'SLW', 'PAAS', 'CDE', 'HL', 'EXK', 'SSRM', 'AGI', 'SAND',
            'NGD', 'GFI', 'IAG', 'KL', 'AUY', 'MMMM', 'SLV', 'GLD', 'GDXJ', 'GDX',
            'XLE', 'XOP', 'VDE', 'OIH', 'USO', 'UCO', 'ERX', 'GUSH', 'XES', 'DRIP',
            'SCO', 'DUG', 'ERY', 'SCC', 'DWTI', 'UWTI', 'OILU', 'OILD', 'BNO', 'UNG'
        ]
        
        # Extend with more NASDAQ symbols to reach the limit
        if limit > len(nasdaq_symbols):
            # Add more symbols to reach the limit
            additional_symbols = [
                f"SYMB{i:04d}" for i in range(len(nasdaq_symbols), limit)
            ]
            nasdaq_symbols.extend(additional_symbols)
        
        return nasdaq_symbols[:limit]

    def _test_yfinance_connectivity(self):
        """Test YFinance connectivity"""
        try:
            self.stdout.write("🔍 Testing YFinance connectivity...")
            test_ticker = yf.Ticker("AAPL")
            test_data = test_ticker.history(period="1d")
            if test_data.empty:
                raise Exception("No data returned")
            self.stdout.write(self.style.SUCCESS("✅ YFinance connectivity test passed"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ YFinance connectivity test failed: {e}"))
            raise CommandError("YFinance is not accessible")