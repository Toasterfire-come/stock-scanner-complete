#!/usr/bin/env python3
"""
Production Stock Retrieval Script
Django-integrated version with NYSE CSV support and production settings
Command line options: -noproxy, -test (100 first tickers)
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
from proxy_manager import ProxyManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_stock_retrieval.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Production Stock Retrieval Script')
    parser.add_argument('-noproxy', action='store_true', help='Disable proxy usage')
    parser.add_argument('-test', action='store_true', help='Test mode - process only first 100 tickers')
    parser.add_argument('-threads', type=int, default=10, help='Number of threads (default: 10)')
    parser.add_argument('-timeout', type=int, default=10, help='Request timeout in seconds (default: 10)')
    parser.add_argument('-csv', type=str, default='flat-ui__data-Fri Aug 01 2025.csv', 
                       help='NYSE CSV file path (default: flat-ui__data-Fri Aug 01 2025.csv)')
    parser.add_argument('-save', action='store_true', help='Save results to database')
    parser.add_argument('-output', type=str, default=None, 
                       help='Output JSON file (default: auto-generated timestamp)')
    return parser.parse_args()

def patch_yfinance_proxy(proxy):
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
        yfinance.shared._requests = session
    except Exception as e:
        logger.error(f"Failed to set proxy {proxy}: {e}")

def load_nyse_symbols(csv_file, test_mode=False):
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

def process_symbol(symbol, ticker_number, proxy_manager, timeout=10, save_to_db=False):
    """Process a single symbol with comprehensive data collection"""
    try:
        # Get proxy for this ticker
        proxy = None
        if proxy_manager:
            proxy = proxy_manager.get_proxy_for_ticker(ticker_number)
            if proxy and ticker_number <= 5:  # Show proxy info for first 5 tickers
                logger.info(f"{symbol}: Using proxy {proxy}")
        
        patch_yfinance_proxy(proxy)
        
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
        
        # Determine if we have enough data to process
        has_data = hist is not None and not hist.empty
        has_info = info and isinstance(info, dict) and len(info) > 3
        has_price = current_price is not None and not pd.isna(current_price)
        
        if not has_data and not has_info:
            logger.warning(f"{symbol}: No data available")
            return None
        
        # Extract comprehensive data
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
            'pe_ratio': info.get('trailingPE') if info else None,
            'dividend_yield': info.get('dividendYield') if info else None,
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
                
            except Exception as db_error:
                logger.error(f"Database save failed for {symbol}: {db_error}")
                result['db_saved'] = False
        
        logger.info(f"✅ {symbol}: ${result.get('current_price', 'N/A')} - {result.get('company_name', 'N/A')}")
        return result
        
    except Exception as e:
        logger.error(f"❌ {symbol}: {e}")
        return None

def main():
    """Main function"""
    args = parse_arguments()
    
    print("PRODUCTION STOCK RETRIEVAL SCRIPT")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  CSV File: {args.csv}")
    print(f"  Test Mode: {args.test}")
    print(f"  Use Proxies: {not args.noproxy}")
    print(f"  Save to DB: {args.save}")
    print(f"  Threads: {args.threads}")
    print(f"  Timeout: {args.timeout}s")
    print("=" * 60)
    
    # Load NYSE symbols
    print(f"\n📊 Loading NYSE symbols from {args.csv}...")
    symbols = load_nyse_symbols(args.csv, args.test)
    
    if not symbols:
        print("❌ No symbols loaded. Exiting.")
        return
    
    print(f"📈 Processing {len(symbols)} symbols...")
    
    # Initialize proxy manager
    proxy_manager = None
    if not args.noproxy:
        try:
            proxy_manager = ProxyManager()
            stats = proxy_manager.get_proxy_stats()
            if stats['total_working'] > 0:
                print(f"✅ Loaded {stats['total_working']} proxies")
            else:
                print("⚠️  No proxies available - trying to refresh...")
                count = proxy_manager.refresh_proxy_pool(force=True)
                if count > 0:
                    stats = proxy_manager.get_proxy_stats()
                    print(f"✅ Refreshed pool - {stats['total_working']} proxies")
                else:
                    print("⚠️  No proxies available - continuing without proxies")
                    proxy_manager = None
        except Exception as e:
            print(f"❌ Proxy manager failed: {e}")
            proxy_manager = None
    else:
        print("🚫 Proxy usage disabled")
    
    # Process stocks
    print(f"\n🚀 Starting to process {len(symbols)} symbols...")
    print("=" * 60)
    
    start_time = time.time()
    successful = 0
    failed = 0
    results = []
    
    # Use ThreadPoolExecutor for parallel processing
    print(f"Submitting {len(symbols)} tasks to thread pool...")
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        future_to_symbol = {}
        for i, symbol in enumerate(symbols, 1):
            future = executor.submit(process_symbol, symbol, i, proxy_manager, args.timeout, args.save)
            future_to_symbol[future] = symbol
        
        print(f"Submitted {len(symbols)} tasks. Processing...")
        completed = 0
        
        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            completed += 1
            
            try:
                result = future.result(timeout=args.timeout + 5)  # Extra timeout for thread management
                if result:
                    successful += 1
                    results.append(result)
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"TIMEOUT {symbol}: {e}")
                failed += 1
            
            # Show progress every 10 completed or at the end
            if completed % 10 == 0 or completed == len(symbols):
                print(f"[PROGRESS] {completed}/{len(symbols)} completed ({successful} successful, {failed} failed)")
    
    elapsed = time.time() - start_time
    
    # Results
    print("\n" + "=" * 60)
    print("SCAN RESULTS")
    print("=" * 60)
    print(f"✅ SUCCESSFUL: {successful}")
    print(f"❌ FAILED: {failed}")
    print(f"📊 SUCCESS RATE: {(successful/len(symbols)*100):.1f}%")
    print(f"⏱️  TIME: {elapsed:.2f}s")
    print(f"🚀 RATE: {len(symbols)/elapsed:.2f} symbols/sec")
    
    if proxy_manager:
        final_stats = proxy_manager.get_proxy_stats()
        print(f"🌐 PROXY STATS: {final_stats}")
    
    # Save results to JSON if requested
    if results and args.output:
        output_data = {
            'scan_info': {
                'timestamp': datetime.now().isoformat(),
                'csv_file': args.csv,
                'test_mode': args.test,
                'use_proxies': not args.noproxy,
                'save_to_db': args.save,
                'threads': args.threads,
                'timeout': args.timeout,
                'total_symbols': len(symbols),
                'successful': successful,
                'failed': failed,
                'success_rate': f"{(successful/len(symbols)*100):.1f}%",
                'elapsed_time': f"{elapsed:.2f}s",
                'rate': f"{len(symbols)/elapsed:.2f} symbols/sec"
            },
            'stocks': results
        }
        
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        print(f"\n✅ Results saved to {args.output}")
    
    # Show database stats if saving to DB
    if args.save:
        try:
            total_stocks = Stock.objects.count()
            print(f"\n📊 Database Stats:")
            print(f"  Total stocks in DB: {total_stocks}")
            print(f"  New stocks added: {successful}")
        except Exception as e:
            print(f"⚠️  Could not get database stats: {e}")
    
    # Show some sample results
    if results:
        print(f"\n📋 Sample Results:")
        for i, stock in enumerate(results[:5]):
            print(f"  {i+1}. {stock['symbol']}: ${stock.get('current_price', 'N/A')} - {stock.get('company_name', 'N/A')}")
    
    print("\n🎯 Scan completed!")

if __name__ == "__main__":
    main()