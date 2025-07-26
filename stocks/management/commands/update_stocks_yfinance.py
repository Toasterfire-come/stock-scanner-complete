"""
Django Management Command: Update Stock Data using YFinance
Comprehensive version with all financial data fields
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

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update comprehensive stock data using YFinance with rate limiting'

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
            '--delay',
            type=float,
            default=0.2,
            help='Delay between requests in seconds (default: 0.2)'
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
            self.style.SUCCESS('🚀 Starting Comprehensive Stock Data Update (YFinance)')
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
        
        # Default NASDAQ 100+ symbols for comprehensive testing
        default_symbols = [
            # FAANG + Big Tech
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX',
            # Other Major Tech
            'AMD', 'INTC', 'ORCL', 'CRM', 'ADBE', 'PYPL', 'UBER', 'SHOP', 'ZOOM', 'ROKU',
            'SQ', 'SNAP', 'PINS', 'COIN', 'RBLX', 'DOCU', 'ZM', 'PTON', 'HOOD',
            # Biotech & Healthcare
            'MRNA', 'BNTX', 'GILD', 'AMGN', 'BIIB', 'REGN', 'VRTX', 'ILMN', 'INCY',
            # Semiconductors
            'QCOM', 'AVGO', 'TXN', 'AMAT', 'LRCX', 'KLAC', 'MRVL', 'MCHP', 'ADI',
            # Consumer & Retail
            'COST', 'SBUX', 'MAR', 'ABNB', 'EBAY', 'BKNG', 'EXPD', 'FAST', 'DLTR',
            # Communication & Media
            'CMCSA', 'CHTR', 'TMUS', 'VZ', 'T', 'NFLX', 'DIS', 'PARA', 'WBD',
            # Financial Services
            'FISV', 'ISRG', 'LCID', 'RIVN', 'F', 'GM', 'TSLA', 'NIO', 'XPEV',
            # Energy & Materials
            'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'HAL', 'DVN', 'FANG', 'MPC',
            # Industrial & Aerospace
            'BA', 'CAT', 'DE', 'HON', 'UPS', 'FDX', 'LMT', 'RTX', 'GD',
            # REITs & Utilities
            'AMT', 'CCI', 'EQIX', 'PLD', 'SPG', 'O', 'WELL', 'AVB', 'EQR',
            # Additional Growth Stocks
            'DDOG', 'SNOW', 'PLTR', 'NET', 'CRWD', 'ZS', 'OKTA', 'TWLO', 'MDB'
        ]
        
        self.stdout.write(f"🎯 Using comprehensive NASDAQ symbols: {len(default_symbols)} stocks")
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
        
        self.stdout.write(f"\n📈 Processing {total_symbols} stocks with comprehensive data...")
        
        for i, symbol in enumerate(symbols):
            try:
                # Rate limiting
                if i > 0:
                    time.sleep(delay)
                
                # Get comprehensive stock data
                quote_data = self._get_comprehensive_stock_data(symbol)
                
                if not quote_data:
                    self.stdout.write(f"❌ {symbol}: No data available")
                    failed += 1
                    continue
                
                if test_mode:
                    # Test mode - display comprehensive data
                    self._display_test_data(symbol, quote_data)
                    successful += 1
                else:
                    # Production mode - update database
                    updated = self._update_stock_in_db(symbol, quote_data)
                    if updated:
                        self.stdout.write(
                            f"✅ {symbol}: ${quote_data['current_price']:.2f} "
                            f"({quote_data['change_percent']:+.2f}%) "
                            f"Vol: {quote_data['volume']:,} - DB Updated"
                        )
                        successful += 1
                    else:
                        self.stdout.write(f"⚠️  {symbol}: Data retrieved but DB update failed")
                        failed += 1
                
                processed += 1
                
                # Progress update every 10 stocks
                if processed % 10 == 0:
                    progress = (processed / total_symbols) * 100
                    elapsed = time.time() - start_time
                    rate = processed / elapsed if elapsed > 0 else 0
                    eta = (total_symbols - processed) / rate if rate > 0 else 0
                    self.stdout.write(
                        f"📊 Progress: {progress:.1f}% ({processed}/{total_symbols}) "
                        f"Rate: {rate:.1f}/s ETA: {eta:.0f}s"
                    )
                
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

    def _get_comprehensive_stock_data(self, symbol):
        """Get comprehensive stock data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get historical data for multiple periods
            hist_1d = ticker.history(period="1d")
            hist_5d = ticker.history(period="5d")  # For week change
            hist_1mo = ticker.history(period="1mo")  # For month change
            hist_1y = ticker.history(period="1y")   # For year change
            
            if hist_1d.empty:
                return None
            
            current_price = hist_1d['Close'].iloc[-1]
            
            # Calculate price changes
            price_change_today = 0
            price_change_week = 0
            price_change_month = 0
            price_change_year = 0
            
            if len(hist_1d) > 1:
                prev_close = hist_1d['Close'].iloc[-2]
                price_change_today = current_price - prev_close
            
            if len(hist_5d) > 1:
                week_ago_price = hist_5d['Close'].iloc[0]
                price_change_week = current_price - week_ago_price
            
            if len(hist_1mo) > 1:
                month_ago_price = hist_1mo['Close'].iloc[0]
                price_change_month = current_price - month_ago_price
            
            if len(hist_1y) > 1:
                year_ago_price = hist_1y['Close'].iloc[0]
                price_change_year = current_price - year_ago_price
            
            # Calculate percentage change
            change_percent = (price_change_today / (current_price - price_change_today) * 100) if price_change_today != 0 else 0
            
            # Get today's range
            days_low = hist_1d['Low'].iloc[-1] if 'Low' in hist_1d.columns else current_price
            days_high = hist_1d['High'].iloc[-1] if 'High' in hist_1d.columns else current_price
            days_range = f"{days_low:.2f} - {days_high:.2f}"
            
            # Get volume data
            volume = int(hist_1d['Volume'].iloc[-1]) if 'Volume' in hist_1d.columns else 0
            avg_volume_3mon = int(hist_1mo['Volume'].mean()) if len(hist_1mo) > 0 and 'Volume' in hist_1mo.columns else 0
            dvav = volume / avg_volume_3mon if avg_volume_3mon > 0 else 0
            
            # Get 52-week range
            week_52_low = hist_1y['Low'].min() if len(hist_1y) > 0 and 'Low' in hist_1y.columns else None
            week_52_high = hist_1y['High'].max() if len(hist_1y) > 0 and 'High' in hist_1y.columns else None
            
            # Get comprehensive info from ticker.info
            try:
                info = ticker.info
                company_name = info.get('longName', symbol)
                market_cap = info.get('marketCap', 0)
                pe_ratio = info.get('trailingPE', 0)
                dividend_yield = info.get('dividendYield', 0)
                shares_outstanding = info.get('sharesOutstanding', 0)
                book_value = info.get('bookValue', 0)
                price_to_book = info.get('priceToBook', 0)
                earnings_per_share = info.get('trailingEps', 0)
                target_mean_price = info.get('targetMeanPrice', 0)
                bid = info.get('bid', 0)
                ask = info.get('ask', 0)
                
                # Create bid-ask spread
                bid_ask_spread = f"{bid:.2f} - {ask:.2f}" if bid and ask else ""
                
            except Exception as e:
                logger.warning(f"Failed to get info for {symbol}: {e}")
                company_name = symbol
                market_cap = 0
                pe_ratio = 0
                dividend_yield = 0
                shares_outstanding = 0
                book_value = 0
                price_to_book = 0
                earnings_per_share = 0
                target_mean_price = 0
                bid = 0
                ask = 0
                bid_ask_spread = ""
            
            return {
                'ticker': symbol,
                'company_name': company_name,
                'current_price': float(current_price),
                'price_change_today': float(price_change_today),
                'price_change_week': float(price_change_week),
                'price_change_month': float(price_change_month),
                'price_change_year': float(price_change_year),
                'change_percent': float(change_percent),
                'bid_price': float(bid) if bid else None,
                'ask_price': float(ask) if ask else None,
                'bid_ask_spread': bid_ask_spread,
                'days_range': days_range,
                'days_low': float(days_low),
                'days_high': float(days_high),
                'volume': volume,
                'volume_today': volume,
                'avg_volume_3mon': avg_volume_3mon,
                'dvav': float(dvav),
                'shares_available': shares_outstanding,
                'market_cap': market_cap,
                'pe_ratio': float(pe_ratio) if pe_ratio else None,
                'dividend_yield': float(dividend_yield) if dividend_yield else None,
                'one_year_target': float(target_mean_price) if target_mean_price else None,
                'week_52_low': float(week_52_low) if week_52_low else None,
                'week_52_high': float(week_52_high) if week_52_high else None,
                'earnings_per_share': float(earnings_per_share) if earnings_per_share else None,
                'book_value': float(book_value) if book_value else None,
                'price_to_book': float(price_to_book) if price_to_book else None,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Comprehensive YFinance error for {symbol}: {e}")
            return None

    def _display_test_data(self, symbol, data):
        """Display comprehensive test data"""
        self.stdout.write(f"\n🔍 {symbol} - {data['company_name']}")
        self.stdout.write(f"   Price: ${data['current_price']:.2f} ({data['change_percent']:+.2f}%)")
        self.stdout.write(f"   Volume: {data['volume']:,} (Avg: {data['avg_volume_3mon']:,})")
        self.stdout.write(f"   Market Cap: ${data['market_cap']:,}" if data['market_cap'] else "   Market Cap: N/A")
        self.stdout.write(f"   P/E: {data['pe_ratio']:.2f}" if data['pe_ratio'] else "   P/E: N/A")
        self.stdout.write(f"   Range: {data['days_range']}")

    def _update_stock_in_db(self, symbol, quote_data):
        """Update comprehensive stock data in database"""
        
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
                        'price_change_week': Decimal(str(quote_data['price_change_week'])),
                        'price_change_month': Decimal(str(quote_data['price_change_month'])),
                        'price_change_year': Decimal(str(quote_data['price_change_year'])),
                        'change_percent': Decimal(str(quote_data['change_percent'])),
                        'bid_price': Decimal(str(quote_data['bid_price'])) if quote_data['bid_price'] else None,
                        'ask_price': Decimal(str(quote_data['ask_price'])) if quote_data['ask_price'] else None,
                        'bid_ask_spread': quote_data['bid_ask_spread'],
                        'days_range': quote_data['days_range'],
                        'days_low': Decimal(str(quote_data['days_low'])),
                        'days_high': Decimal(str(quote_data['days_high'])),
                        'volume': quote_data['volume'],
                        'volume_today': quote_data['volume_today'],
                        'avg_volume_3mon': quote_data['avg_volume_3mon'],
                        'dvav': Decimal(str(quote_data['dvav'])),
                        'shares_available': quote_data['shares_available'],
                        'market_cap': quote_data['market_cap'],
                        'pe_ratio': Decimal(str(quote_data['pe_ratio'])) if quote_data['pe_ratio'] else None,
                        'dividend_yield': Decimal(str(quote_data['dividend_yield'])) if quote_data['dividend_yield'] else None,
                        'one_year_target': Decimal(str(quote_data['one_year_target'])) if quote_data['one_year_target'] else None,
                        'week_52_low': Decimal(str(quote_data['week_52_low'])) if quote_data['week_52_low'] else None,
                        'week_52_high': Decimal(str(quote_data['week_52_high'])) if quote_data['week_52_high'] else None,
                        'earnings_per_share': Decimal(str(quote_data['earnings_per_share'])) if quote_data['earnings_per_share'] else None,
                        'book_value': Decimal(str(quote_data['book_value'])) if quote_data['book_value'] else None,
                        'price_to_book': Decimal(str(quote_data['price_to_book'])) if quote_data['price_to_book'] else None,
                    }
                )
                
                if not created:
                    # Update existing record with all fields
                    for field, value in {
                        'company_name': quote_data['company_name'],
                        'name': quote_data['company_name'],
                        'current_price': Decimal(str(quote_data['current_price'])),
                        'price_change_today': Decimal(str(quote_data['price_change_today'])),
                        'price_change_week': Decimal(str(quote_data['price_change_week'])),
                        'price_change_month': Decimal(str(quote_data['price_change_month'])),
                        'price_change_year': Decimal(str(quote_data['price_change_year'])),
                        'change_percent': Decimal(str(quote_data['change_percent'])),
                        'bid_price': Decimal(str(quote_data['bid_price'])) if quote_data['bid_price'] else None,
                        'ask_price': Decimal(str(quote_data['ask_price'])) if quote_data['ask_price'] else None,
                        'bid_ask_spread': quote_data['bid_ask_spread'],
                        'days_range': quote_data['days_range'],
                        'days_low': Decimal(str(quote_data['days_low'])),
                        'days_high': Decimal(str(quote_data['days_high'])),
                        'volume': quote_data['volume'],
                        'volume_today': quote_data['volume_today'],
                        'avg_volume_3mon': quote_data['avg_volume_3mon'],
                        'dvav': Decimal(str(quote_data['dvav'])),
                        'shares_available': quote_data['shares_available'],
                        'market_cap': quote_data['market_cap'],
                        'pe_ratio': Decimal(str(quote_data['pe_ratio'])) if quote_data['pe_ratio'] else None,
                        'dividend_yield': Decimal(str(quote_data['dividend_yield'])) if quote_data['dividend_yield'] else None,
                        'one_year_target': Decimal(str(quote_data['one_year_target'])) if quote_data['one_year_target'] else None,
                        'week_52_low': Decimal(str(quote_data['week_52_low'])) if quote_data['week_52_low'] else None,
                        'week_52_high': Decimal(str(quote_data['week_52_high'])) if quote_data['week_52_high'] else None,
                        'earnings_per_share': Decimal(str(quote_data['earnings_per_share'])) if quote_data['earnings_per_share'] else None,
                        'book_value': Decimal(str(quote_data['book_value'])) if quote_data['book_value'] else None,
                        'price_to_book': Decimal(str(quote_data['price_to_book'])) if quote_data['price_to_book'] else None,
                    }.items():
                        setattr(stock, field, value)
                    stock.save()
                
                return True
                
        except Exception as e:
            logger.error(f"Database update failed for {symbol}: {e}")
            return False

    def _display_results(self, results):
        """Display final results"""
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("🎉 COMPREHENSIVE STOCK UPDATE COMPLETE"))
        self.stdout.write("="*60)
        
        success_rate = (results['successful'] / results['total']) * 100 if results['total'] > 0 else 0
        rate = results['processed'] / results['duration'] if results['duration'] > 0 else 0
        
        self.stdout.write(f"📊 Results Summary:")
        self.stdout.write(f"   • Total stocks: {results['total']}")
        self.stdout.write(f"   • Successful: {results['successful']}")
        self.stdout.write(f"   • Failed: {results['failed']}")
        self.stdout.write(f"   • Success rate: {success_rate:.1f}%")
        self.stdout.write(f"   • Duration: {results['duration']:.1f}s")
        self.stdout.write(f"   • Processing rate: {rate:.1f} stocks/second")
        
        if success_rate >= 90:
            self.stdout.write(self.style.SUCCESS("\n🎯 Excellent success rate!"))
        elif success_rate >= 70:
            self.stdout.write(self.style.WARNING("\n⚠️  Good success rate - some requests failed"))
        else:
            self.stdout.write(self.style.ERROR("\n❌ Low success rate - check connectivity"))
        
        self.stdout.write(f"\n📈 Rate limiting: {0.2}s delay between requests")
        self.stdout.write("✅ Comprehensive update complete!")