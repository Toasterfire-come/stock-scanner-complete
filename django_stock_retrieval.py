#!/usr/bin/env python3
"""
Django Stock Retrieval Script
Comprehensive stock data retrieval with improved PE ratio and dividend yield extraction
"""

import os
import sys
import time
import random
import json
import csv
import argparse
import django
from pathlib import Path
from datetime import datetime
import logging
import signal

# Setup Django environment
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')

# Set production environment variables
os.environ['DB_ENGINE'] = 'django.db.backends.mysql'
os.environ['DB_NAME'] = 'stockscanner'
os.environ['DB_USER'] = 'root'
os.environ['DB_PASSWORD'] = ''
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '3306'

try:
    django.setup()
    print("SUCCESS: Django environment loaded successfully")
except Exception as e:
    print(f"ERROR: Failed to setup Django: {e}")
    sys.exit(1)

# Now import Django models and other modules
from stocks.models import Stock, StockPrice
from django.utils import timezone
from decimal import Decimal
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('django_stock_retrieval.log'),
        logging.StreamHandler()
    ]
)
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

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Django Stock Retrieval Script')
    parser.add_argument('-test', action='store_true', help='Test mode - process only first 100 tickers')
    parser.add_argument('-threads', type=int, default=30, help='Number of threads (default: 30)')
    parser.add_argument('-timeout', type=int, default=10, help='Request timeout in seconds (default: 10)')
    parser.add_argument('-csv', type=str, default='flat-ui__data-Fri Aug 01 2025.csv', 
                       help='NYSE CSV file path (default: flat-ui__data-Fri Aug 01 2025.csv)')
    parser.add_argument('-save', action='store_true', help='Save results to database')
    parser.add_argument('-output', type=str, default=None, 
                       help='Output JSON file (default: auto-generated timestamp)')
    parser.add_argument('-max-symbols', type=int, default=None, 
                       help='Maximum number of symbols to process (for testing)')
    return parser.parse_args()

def _extract_pe_ratio(info):
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

def _extract_dividend_yield(info):
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

def load_nyse_symbols(csv_file, test_mode=False, max_symbols=None):
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
        logger.error(f"CSV file not found: {csv_file}")
        return []
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return []
    
    logger.info(f"Loaded {len(symbols)} active NYSE symbols")
    logger.info(f"Filtered out {delisted_count} delisted stocks")
    logger.info(f"Filtered out {etf_count} ETFs")
    logger.info(f"Active stocks: {active_count}")
    
    return symbols

def process_symbol(symbol, ticker_number, timeout=10, save_to_db=False):
    """Process a single symbol with comprehensive data collection"""
    global shutdown_flag
    
    if shutdown_flag:
        return None
        
    try:
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
            logger.warning(f"{symbol}: No data available")
            return None
        
        # Extract comprehensive data with improved PE ratio and dividend yield handling
        result = {
            'symbol': symbol,
            'company_name': info.get('longName', info.get('shortName', symbol)) if info else symbol,
            'current_price': float(current_price) if current_price else None,
            'previous_close': info.get('previousClose') if info else None,
            'open_price': info.get('regularMarketOpen') if info else None,
            'day_low': info.get('dayLow') if info else None,
            'day_high': info.get('dayHigh') if info else None,
            'volume': info.get('volume') if info else None,
            'avg_volume': info.get('averageVolume') if info else None,
            'market_cap': info.get('marketCap') if info else None,
            'pe_ratio': _extract_pe_ratio(info),
            'dividend_yield': _extract_dividend_yield(info),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow') if info else None,
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh') if info else None,
            'beta': info.get('beta') if info else None,
            'sector': info.get('sector') if info else None,
            'industry': info.get('industry') if info else None,
            'exchange': info.get('exchange') if info else None,
            'currency': info.get('currency') if info else None,
            'country': info.get('country') if info else None,
            'timestamp': datetime.now().isoformat()
        }
        
        # Calculate price changes if historical data available
        if has_data and len(hist) > 1:
            try:
                current = hist['Close'].iloc[-1]
                previous = hist['Close'].iloc[-2]
                if current and previous:
                    change = current - previous
                    change_percent = (change / previous) * 100
                    result['price_change'] = float(change)
                    result['change_percent'] = float(change_percent)
            except:
                pass
        
        # Add volume analysis
        if result.get('volume') and result.get('avg_volume'):
            try:
                volume_ratio = result['volume'] / result['avg_volume']
                result['volume_ratio'] = float(volume_ratio)
            except:
                pass
        
        # Save to database if requested
        if save_to_db and result.get('current_price'):
            try:
                stock, created = Stock.objects.get_or_create(
                    ticker=symbol,
                    defaults={
                        'symbol': symbol,
                        'company_name': result.get('company_name', symbol),
                        'name': result.get('company_name', symbol),
                        'exchange': result.get('exchange', 'NYSE'),
                        'current_price': Decimal(str(result.get('current_price', 0))),
                        'price_change_today': Decimal(str(result.get('price_change', 0))) if result.get('price_change') else None,
                        'change_percent': Decimal(str(result.get('change_percent', 0))) if result.get('change_percent') else None,
                        'days_low': Decimal(str(result.get('day_low', 0))) if result.get('day_low') else None,
                        'days_high': Decimal(str(result.get('day_high', 0))) if result.get('day_high') else None,
                        'volume': result.get('volume'),
                        'avg_volume_3mon': result.get('avg_volume'),
                        'market_cap': result.get('market_cap'),
                        'pe_ratio': Decimal(str(result.get('pe_ratio', 0))) if result.get('pe_ratio') else None,
                        'dividend_yield': Decimal(str(result.get('dividend_yield', 0))) if result.get('dividend_yield') else None,
                        'week_52_low': Decimal(str(result.get('fifty_two_week_low', 0))) if result.get('fifty_two_week_low') else None,
                        'week_52_high': Decimal(str(result.get('fifty_two_week_high', 0))) if result.get('fifty_two_week_high') else None,
                        'earnings_per_share': None,  # Not available from yfinance
                        'book_value': None,  # Not available from yfinance
                        'price_to_book': None,  # Not available from yfinance
                        'one_year_target': None,  # Not available from yfinance
                    }
                )
                
                # Update existing stock if not created
                if not created:
                    stock.current_price = Decimal(str(result.get('current_price', 0)))
                    stock.price_change_today = Decimal(str(result.get('price_change', 0))) if result.get('price_change') else None
                    stock.change_percent = Decimal(str(result.get('change_percent', 0))) if result.get('change_percent') else None
                    stock.days_low = Decimal(str(result.get('day_low', 0))) if result.get('day_low') else None
                    stock.days_high = Decimal(str(result.get('day_high', 0))) if result.get('day_high') else None
                    stock.volume = result.get('volume')
                    stock.avg_volume_3mon = result.get('avg_volume')
                    stock.market_cap = result.get('market_cap')
                    stock.pe_ratio = Decimal(str(result.get('pe_ratio', 0))) if result.get('pe_ratio') else None
                    stock.dividend_yield = Decimal(str(result.get('dividend_yield', 0))) if result.get('dividend_yield') else None
                    stock.week_52_low = Decimal(str(result.get('fifty_two_week_low', 0))) if result.get('fifty_two_week_low') else None
                    stock.week_52_high = Decimal(str(result.get('fifty_two_week_high', 0))) if result.get('fifty_two_week_high') else None
                    stock.save()
                
                # Create price record
                StockPrice.objects.create(
                    stock=stock,
                    price=Decimal(str(result.get('current_price', 0))),
                    timestamp=timezone.now()
                )
                
                result['db_saved'] = True
                logger.info(f"SUCCESS {symbol}: ${result.get('current_price', 'N/A')} - {result.get('company_name', 'N/A')} - PE: {result.get('pe_ratio', 'N/A')} - Div: {result.get('dividend_yield', 'N/A')}%")
            except Exception as e:
                logger.error(f"ERROR {symbol}: Database save failed - {e}")
                result['db_saved'] = False
        else:
            logger.info(f"SUCCESS {symbol}: ${result.get('current_price', 'N/A')} - {result.get('company_name', 'N/A')} - PE: {result.get('pe_ratio', 'N/A')} - Div: {result.get('dividend_yield', 'N/A')}%")
        
        return result
        
    except Exception as e:
        logger.error(f"ERROR {symbol}: {e}")
        return None

def main():
    """Main function"""
    global shutdown_flag
    
    args = parse_arguments()
    
    print("DJANGO STOCK RETRIEVAL SCRIPT")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  CSV File: {args.csv}")
    print(f"  Test Mode: {args.test}")
    print(f"  Save to DB: {args.save}")
    print(f"  Threads: {args.threads}")
    print(f"  Timeout: {args.timeout}s")
    print(f"  Max Symbols: {args.max_symbols or 'All'}")
    print("=" * 60)
    
    # Load NYSE symbols
    print(f"\nLoading NYSE symbols from {args.csv}...")
    symbols = load_nyse_symbols(args.csv, args.test, args.max_symbols)
    
    if not symbols:
        print("ERROR: No symbols loaded. Exiting.")
        return
    
    print(f"Processing {len(symbols)} symbols...")
    
    # Process stocks
    print(f"\nStarting to process {len(symbols)} symbols...")
    print("=" * 60)
    
    start_time = time.time()
    successful = 0
    failed = 0
    results = []
    
    # Use ThreadPoolExecutor for parallel processing
    print(f"Submitting {len(symbols)} tasks to thread pool...")
    
    try:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            future_to_symbol = {}
            for i, symbol in enumerate(symbols, 1):
                if shutdown_flag:
                    break
                future = executor.submit(process_symbol, symbol, i, args.timeout, args.save)
                future_to_symbol[future] = symbol
            
            print(f"Submitted {len(future_to_symbol)} tasks. Processing...")
            completed = 0
            
            for future in as_completed(future_to_symbol):
                if shutdown_flag:
                    print("Shutdown requested. Cancelling remaining tasks...")
                    break
                    
                symbol = future_to_symbol[future]
                completed += 1
                
                try:
                    result = future.result(timeout=args.timeout + 2)
                    if result:
                        successful += 1
                        results.append(result)
                    else:
                        failed += 1
                except Exception as e:
                    logger.error(f"ERROR {symbol}: {e}")
                    failed += 1
                
                # Show progress every 10 completed or at the end
                if completed % 10 == 0 or completed == len(symbols):
                    print(f"[PROGRESS] {completed}/{len(symbols)} completed ({successful} successful, {failed} failed)")
                    
                # Add a small delay to prevent overwhelming
                time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\nInterrupted by user. Shutting down gracefully...")
        shutdown_flag = True
    except Exception as e:
        print(f"ERROR: Thread pool execution failed: {e}")
    
    elapsed = time.time() - start_time
    
    # Results
    print("\n" + "=" * 60)
    print("SCAN RESULTS")
    print("=" * 60)
    print(f"SUCCESSFUL: {successful}")
    print(f"FAILED: {failed}")
    if len(symbols) > 0:
        print(f"SUCCESS RATE: {(successful/len(symbols)*100):.1f}%")
    print(f"TIME: {elapsed:.2f}s")
    if elapsed > 0:
        print(f"RATE: {len(symbols)/elapsed:.2f} symbols/sec")
    
    # Save results
    if results:
        if args.output:
            filename = args.output
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mode = "test" if args.test else "full"
            filename = f"django_stock_retrieval_{mode}_{timestamp}.json"
        
        output_data = {
            'scan_info': {
                'timestamp': datetime.now().isoformat(),
                'csv_file': args.csv,
                'test_mode': args.test,
                'save_to_db': args.save,
                'threads': args.threads,
                'timeout': args.timeout,
                'max_symbols': args.max_symbols,
                'total_symbols': len(symbols),
                'successful': successful,
                'failed': failed,
                'success_rate': f"{(successful/len(symbols)*100):.1f}%" if len(symbols) > 0 else "0%",
                'elapsed_time': f"{elapsed:.2f}s",
                'rate': f"{len(symbols)/elapsed:.2f} symbols/sec" if elapsed > 0 else "0 symbols/sec"
            },
            'stocks': results
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(output_data, f, indent=2, default=str)
            
            print(f"\nSUCCESS: Results saved to {filename}")
            print(f"Total stocks processed: {len(results)}")
            
            # Show some sample results with PE ratio and dividend yield
            if results:
                print(f"\nSample Results (with PE Ratio and Dividend Yield):")
                for i, stock in enumerate(results[:5]):
                    pe_ratio = stock.get('pe_ratio', 'N/A')
                    dividend_yield = stock.get('dividend_yield', 'N/A')
                    print(f"  {i+1}. {stock['symbol']}: ${stock.get('current_price', 'N/A')} - PE: {pe_ratio} - Div: {dividend_yield}%")
        except Exception as e:
            print(f"ERROR: Failed to save results: {e}")
    else:
        print("\nWARNING: No results to save")
    
    print("\nScan completed!")

if __name__ == "__main__":
    main()