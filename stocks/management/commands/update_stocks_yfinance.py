"""
Django Management Command: Update Stock Data using YFinance Primary API
Replaces IEX Cloud with Yahoo Finance + backup APIs
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from stocks.models import StockAlert
from stocks.api_manager import stock_manager
from datetime import datetime, timedelta
import logging
import time
import sys

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update stock data using YFinance primary with backup APIs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--symbols',
            type=str,
            help='Comma-separated list of stock symbols to update (e.g., AAPL,MSFT,GOOGL)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of stocks to update (default: 100)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Number of stocks to process in each batch (default: 10)'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=1.0,
            help='Delay between batches in seconds (default: 1.0)'
        )
        parser.add_argument(
            '--test-mode',
            action='store_true',
            help='Run in test mode (no database updates)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output'
        )

    def handle(self, *args, **options):
        """Main command handler"""
        
        # Set up logging
        log_level = logging.INFO if options['verbose'] else logging.WARNING
        logging.basicConfig(level=log_level)
        
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting Stock Data Update (YFinance Primary)')
        )
        
        # Configuration
        symbols = self._get_symbols(options.get('symbols'))
        limit = options['limit']
        batch_size = options['batch_size']
        delay = options['delay']
        test_mode = options['test_mode']
        
        if test_mode:
            self.stdout.write(
                self.style.WARNING('⚠️ Running in TEST MODE - no database updates')
            )
        
        # Display configuration
        self.stdout.write(f"📊 Configuration:")
        self.stdout.write(f"   • Symbols: {len(symbols)} stocks")
        self.stdout.write(f"   • Limit: {limit}")
        self.stdout.write(f"   • Batch size: {batch_size}")
        self.stdout.write(f"   • Delay: {delay}s")
        self.stdout.write(f"   • Test mode: {test_mode}")
        
        # Test API connectivity
        self._test_api_connectivity()
        
        # Process stocks
        try:
            results = self._process_stocks(symbols[:limit], batch_size, delay, test_mode)
            self._display_results(results)
            
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\n⚠️ Update interrupted by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Update failed: {e}'))
            raise CommandError(f'Stock update failed: {e}')

    def _get_symbols(self, symbols_arg):
        """Get list of symbols to update"""
        
        if symbols_arg:
            # Use provided symbols
            symbols = [s.strip().upper() for s in symbols_arg.split(',') if s.strip()]
            self.stdout.write(f"📝 Using provided symbols: {symbols}")
            return symbols
        
        # Get symbols from database
        db_symbols = list(
            StockAlert.objects.values_list('ticker', flat=True)
            .distinct()
            .order_by('ticker')
        )
        
        if db_symbols:
            self.stdout.write(f"📊 Using {len(db_symbols)} symbols from database")
            return db_symbols
        
        # Default popular symbols if database is empty
        default_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'AMD', 'INTC', 'ORCL', 'CRM', 'ADBE', 'PYPL', 'UBER', 'SHOP',
            'ZOOM', 'ROKU', 'SQ', 'SNAP', 'PINS', 'COIN', 'RBLX', 'TWTR'
        ]
        
        self.stdout.write(f"🎯 Using default popular symbols: {len(default_symbols)} stocks")
        return default_symbols

    def _test_api_connectivity(self):
        """Test connectivity to all APIs"""
        
        self.stdout.write("🔍 Testing API connectivity...")
        
        connection_tests = stock_manager.test_connection()
        
        for api_name, is_connected in connection_tests.items():
            status_icon = "✅" if is_connected else "❌"
            api_display = api_name.replace('_', ' ').title()
            self.stdout.write(f"   {status_icon} {api_display}")
        
        # Check if primary (Yahoo Finance) is working
        if not connection_tests.get('yahoo_finance', False):
            self.stdout.write(
                self.style.WARNING('⚠️ Yahoo Finance (primary) not responding - using backup APIs')
            )
        
        # Check if any API is working
        if not any(connection_tests.values()):
            raise CommandError('❌ No APIs are responding - check internet connection')

    def _process_stocks(self, symbols, batch_size, delay, test_mode):
        """Process stocks in batches"""
        
        total_symbols = len(symbols)
        processed = 0
        successful = 0
        failed = 0
        skipped = 0
        
        start_time = time.time()
        
        # Process in batches
        for i in range(0, total_symbols, batch_size):
            batch_symbols = symbols[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_symbols + batch_size - 1) // batch_size
            
            self.stdout.write(f"\n📦 Processing batch {batch_num}/{total_batches}: {batch_symbols}")
            
            # Process batch
            batch_results = self._process_batch(batch_symbols, test_mode)
            
            # Update counters
            processed += len(batch_symbols)
            successful += batch_results['successful']
            failed += batch_results['failed']
            skipped += batch_results['skipped']
            
            # Progress update
            progress = (processed / total_symbols) * 100
            elapsed = time.time() - start_time
            eta = (elapsed / processed) * (total_symbols - processed) if processed > 0 else 0
            
            self.stdout.write(
                f"   Progress: {progress:.1f}% | "
                f"Success: {successful} | Failed: {failed} | "
                f"ETA: {eta:.0f}s"
            )
            
            # Delay between batches (except last batch)
            if i + batch_size < total_symbols:
                time.sleep(delay)
        
        return {
            'total': total_symbols,
            'processed': processed,
            'successful': successful,
            'failed': failed,
            'skipped': skipped,
            'duration': time.time() - start_time
        }

    def _process_batch(self, symbols, test_mode):
        """Process a batch of symbols"""
        
        successful = 0
        failed = 0
        skipped = 0
        
        for symbol in symbols:
            try:
                # Get stock data
                quote_data = stock_manager.get_stock_quote(symbol)
                
                if not quote_data:
                    self.stdout.write(f"   ❌ {symbol}: No data available")
                    failed += 1
                    continue
                
                if test_mode:
                    # Test mode - just log the data
                    self.stdout.write(
                        f"   ✅ {symbol}: ${quote_data['price']:.2f} "
                        f"({quote_data['change_percent']:+.2f}%) "
                        f"[{quote_data['source']}]"
                    )
                    successful += 1
                else:
                    # Production mode - update database
                    updated = self._update_stock_in_db(symbol, quote_data)
                    if updated:
                        self.stdout.write(
                            f"   ✅ {symbol}: ${quote_data['price']:.2f} "
                            f"({quote_data['change_percent']:+.2f}%) "
                            f"[{quote_data['source']}] - DB Updated"
                        )
                        successful += 1
                    else:
                        self.stdout.write(f"   ⚠️ {symbol}: Data retrieved but DB update skipped")
                        skipped += 1
                
            except Exception as e:
                self.stdout.write(f"   ❌ {symbol}: Error - {e}")
                failed += 1
        
        return {
            'successful': successful,
            'failed': failed,
            'skipped': skipped
        }

    def _update_stock_in_db(self, symbol, quote_data):
        """Update stock data in database"""
        
        try:
            with transaction.atomic():
                stock_alert, created = StockAlert.objects.get_or_create(
                    ticker=symbol,
                    defaults={
                        'company_name': symbol,
                        'current_price': quote_data['price'],
                        'price_change_today': quote_data.get('change', 0),
                        'price_change_percent': quote_data.get('change_percent', 0),
                        'volume_today': quote_data.get('volume', 0),
                        'market_cap': quote_data.get('market_cap', 0),
                        'last_updated': timezone.now(),
                        'data_source': quote_data['source'],
                        'is_active': True
                    }
                )
                
                if not created:
                    # Update existing record
                    stock_alert.current_price = quote_data['price']
                    stock_alert.price_change_today = quote_data.get('change', 0)
                    stock_alert.price_change_percent = quote_data.get('change_percent', 0)
                    stock_alert.volume_today = quote_data.get('volume', 0)
                    stock_alert.market_cap = quote_data.get('market_cap', 0)
                    stock_alert.last_updated = timezone.now()
                    stock_alert.data_source = quote_data['source']
                    stock_alert.save()
                
                return True
                
        except Exception as e:
            logger.error(f"Database update failed for {symbol}: {e}")
            return False

    def _display_results(self, results):
        """Display final results"""
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("📈 STOCK UPDATE COMPLETE"))
        self.stdout.write("="*60)
        
        success_rate = (results['successful'] / results['total']) * 100 if results['total'] > 0 else 0
        
        self.stdout.write(f"📊 Results Summary:")
        self.stdout.write(f"   • Total stocks: {results['total']}")
        self.stdout.write(f"   • Successful: {results['successful']}")
        self.stdout.write(f"   • Failed: {results['failed']}")
        self.stdout.write(f"   • Skipped: {results['skipped']}")
        self.stdout.write(f"   • Success rate: {success_rate:.1f}%")
        self.stdout.write(f"   • Duration: {results['duration']:.1f}s")
        
        # API usage stats
        usage_stats = stock_manager.get_usage_stats()
        self.stdout.write(f"\n📡 API Usage Today:")
        
        for api_name, stats in usage_stats.items():
            api_display = api_name.replace('_', ' ').title()
            
            if api_name == 'yahoo_finance':
                self.stdout.write(f"   • {api_display}: {stats['requests_today']} requests (unlimited)")
            elif 'total_available' in stats:
                used = sum(stats['usage']) if stats['usage'] else 0
                self.stdout.write(f"   • {api_display}: {used}/{stats['total_available']} requests")
            elif 'limit' in stats:
                self.stdout.write(f"   • {api_display}: {stats['usage']}/{stats['limit']} requests")
        
        if success_rate >= 90:
            self.stdout.write(self.style.SUCCESS("\n🎉 Excellent success rate!"))
        elif success_rate >= 70:
            self.stdout.write(self.style.WARNING("\n⚠️ Good success rate - some backup APIs may be needed"))
        else:
            self.stdout.write(self.style.ERROR("\n❌ Low success rate - check API connectivity"))
        
        self.stdout.write("\n✅ Update complete!")