"""
Django Management Command: Update Stock Data using YFinance
Simple, working version with proper rate limiting and error handling
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

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update stock data using YFinance with rate limiting'

    def add_arguments(self, parser):
        parser.add_argument(
            '--symbols',
            type=str,
            help='Comma-separated list of stock symbols to update (e.g., AAPL,MSFT,GOOGL)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Maximum number of stocks to update (default: 10)'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=0.5,
            help='Delay between requests in seconds (default: 0.5)'
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
        if options['verbose']:
            logging.basicConfig(level=logging.INFO)
        
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting Stock Data Update (YFinance)')
        )
        
        # Configuration
        symbols = self._get_symbols(options.get('symbols'))
        limit = options['limit']
        delay = options['delay']
        test_mode = options['test_mode']
        
        if test_mode:
            self.stdout.write(
                self.style.WARNING('⚠️  Running in TEST MODE - no database updates')
            )
        
        # Display configuration
        self.stdout.write(f"📊 Configuration:")
        self.stdout.write(f"   • Symbols: {len(symbols)} stocks")
        self.stdout.write(f"   • Limit: {limit}")
        self.stdout.write(f"   • Delay: {delay}s")
        self.stdout.write(f"   • Test mode: {test_mode}")
        
        # Test YFinance connectivity
        self._test_yfinance_connectivity()
        
        # Process stocks
        try:
            results = self._process_stocks(symbols[:limit], delay, test_mode)
            self._display_results(results)
            
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\n❌ Update interrupted by user'))
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
            Stock.objects.values_list('ticker', flat=True)
            .distinct()
            .order_by('ticker')
        )
        
        if db_symbols:
            self.stdout.write(f"📊 Using {len(db_symbols)} symbols from database")
            return db_symbols
        
        # Default popular symbols if database is empty
        default_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'AMD', 'INTC', 'ORCL', 'CRM', 'ADBE', 'PYPL', 'UBER', 'SHOP'
        ]
        
        self.stdout.write(f"🎯 Using default popular symbols: {len(default_symbols)} stocks")
        return default_symbols

    def _test_yfinance_connectivity(self):
        """Test YFinance connectivity"""
        
        self.stdout.write("🔍 Testing YFinance connectivity...")
        
        try:
            # Test with AAPL
            ticker = yf.Ticker("AAPL")
            hist = ticker.history(period="1d")
            
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                self.stdout.write(f"✅ YFinance connected successfully (AAPL: ${price:.2f})")
            else:
                self.stdout.write(self.style.WARNING("⚠️  YFinance connected but no data returned"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ YFinance connectivity test failed: {e}"))
            raise CommandError("YFinance is not accessible")

    def _process_stocks(self, symbols, delay, test_mode):
        """Process stocks with rate limiting"""
        
        total_symbols = len(symbols)
        processed = 0
        successful = 0
        failed = 0
        
        start_time = time.time()
        
        self.stdout.write(f"\n📈 Processing {total_symbols} stocks...")
        
        for i, symbol in enumerate(symbols):
            try:
                # Rate limiting
                if i > 0:
                    time.sleep(delay)
                
                # Get stock data
                quote_data = self._get_yfinance_quote(symbol)
                
                if not quote_data:
                    self.stdout.write(f"❌ {symbol}: No data available")
                    failed += 1
                    continue
                
                if test_mode:
                    # Test mode - just log the data
                    self.stdout.write(
                        f"✅ {symbol}: ${quote_data['price']:.2f} "
                        f"({quote_data['change_percent']:+.2f}%) "
                        f"Vol: {quote_data['volume']:,}"
                    )
                    successful += 1
                else:
                    # Production mode - update database
                    updated = self._update_stock_in_db(symbol, quote_data)
                    if updated:
                        self.stdout.write(
                            f"✅ {symbol}: ${quote_data['price']:.2f} "
                            f"({quote_data['change_percent']:+.2f}%) - DB Updated"
                        )
                        successful += 1
                    else:
                        self.stdout.write(f"⚠️  {symbol}: Data retrieved but DB update failed")
                        failed += 1
                
                processed += 1
                
                # Progress update every 5 stocks
                if processed % 5 == 0:
                    progress = (processed / total_symbols) * 100
                    self.stdout.write(f"📊 Progress: {progress:.1f}% ({processed}/{total_symbols})")
                
            except Exception as e:
                self.stdout.write(f"❌ {symbol}: Error - {e}")
                failed += 1
                processed += 1
        
        return {
            'total': total_symbols,
            'processed': processed,
            'successful': successful,
            'failed': failed,
            'duration': time.time() - start_time
        }

    def _get_yfinance_quote(self, symbol):
        """Get quote from Yahoo Finance using yfinance library"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get historical data (2 days to calculate change)
            hist = ticker.history(period="2d")
            
            if hist.empty or len(hist) < 1:
                return None
            
            current_price = hist['Close'].iloc[-1]
            
            # Calculate price change
            if len(hist) > 1:
                prev_close = hist['Close'].iloc[-2]
                price_change = current_price - prev_close
                price_change_percent = (price_change / prev_close * 100) if prev_close != 0 else 0
            else:
                price_change = 0
                price_change_percent = 0
            
            # Get volume
            volume = int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0
            
            # Get additional info
            try:
                info = ticker.info
                market_cap = info.get('marketCap', 0) if info else 0
                pe_ratio = info.get('trailingPE', 0) if info else 0
                company_name = info.get('longName', symbol) if info else symbol
            except:
                market_cap = 0
                pe_ratio = 0
                company_name = symbol
            
            return {
                'symbol': symbol,
                'price': float(current_price),
                'change': float(price_change),
                'change_percent': float(price_change_percent),
                'volume': volume,
                'market_cap': market_cap,
                'pe_ratio': pe_ratio,
                'company_name': company_name,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"YFinance error for {symbol}: {e}")
            return None

    def _update_stock_in_db(self, symbol, quote_data):
        """Update stock data in database"""
        
        try:
            with transaction.atomic():
                stock, created = Stock.objects.get_or_create(
                    ticker=symbol,
                    defaults={
                        'symbol': symbol,
                        'company_name': quote_data['company_name'],
                        'name': quote_data['company_name'],
                        'current_price': Decimal(str(quote_data['price'])),
                        'change_percent': Decimal(str(quote_data['change_percent'])),
                        'volume': quote_data['volume'],
                        'market_cap': quote_data['market_cap'],
                        'pe_ratio': Decimal(str(quote_data['pe_ratio'])) if quote_data['pe_ratio'] else None,
                    }
                )
                
                if not created:
                    # Update existing record
                    stock.current_price = Decimal(str(quote_data['price']))
                    stock.change_percent = Decimal(str(quote_data['change_percent']))
                    stock.volume = quote_data['volume']
                    stock.market_cap = quote_data['market_cap']
                    if quote_data['pe_ratio']:
                        stock.pe_ratio = Decimal(str(quote_data['pe_ratio']))
                    stock.save()
                
                return True
                
        except Exception as e:
            logger.error(f"Database update failed for {symbol}: {e}")
            return False

    def _display_results(self, results):
        """Display final results"""
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("🎉 STOCK UPDATE COMPLETE"))
        self.stdout.write("="*60)
        
        success_rate = (results['successful'] / results['total']) * 100 if results['total'] > 0 else 0
        
        self.stdout.write(f"📊 Results Summary:")
        self.stdout.write(f"   • Total stocks: {results['total']}")
        self.stdout.write(f"   • Successful: {results['successful']}")
        self.stdout.write(f"   • Failed: {results['failed']}")
        self.stdout.write(f"   • Success rate: {success_rate:.1f}%")
        self.stdout.write(f"   • Duration: {results['duration']:.1f}s")
        
        if success_rate >= 90:
            self.stdout.write(self.style.SUCCESS("\n🎯 Excellent success rate!"))
        elif success_rate >= 70:
            self.stdout.write(self.style.WARNING("\n⚠️  Good success rate - some requests failed"))
        else:
            self.stdout.write(self.style.ERROR("\n❌ Low success rate - check connectivity"))
        
        self.stdout.write("\n✅ Update complete!")