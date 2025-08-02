#!/usr/bin/env python3
"""
Enhanced Stock Retrieval Script - DJANGO VERSION (Direct Proxy Loading)
Uses entire NYSE CSV, filters delisted stocks, supports production settings
Command line options: -noproxy, -test (100 first tickers), -threads, -timeout
Integrated with Django models and database
"""

import os
import sys
import time
import random
import json
import csv
import argparse
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import requests
from datetime import datetime
import logging
import signal
from pathlib import Path

# Django setup
import django
from django.core.management import execute_from_command_line
from django.utils import timezone
from decimal import Decimal

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

# Import Django models
from stocks.models import Stock, StockPrice

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('django_stock_retrieval_enhanced.log'),
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
    parser = argparse.ArgumentParser(description='Enhanced Stock Retrieval Script - DJANGO VERSION')
    parser.add_argument('-noproxy', action='store_true', help='Disable proxy usage')
    parser.add_argument('-test', action='store_true', help='Test mode - process only first 100 tickers')
    parser.add_argument('-threads', type=int, default=30, help='Number of threads (default: 30)')
    parser.add_argument('-timeout', type=int, default=8, help='Request timeout in seconds (default: 8)')
    parser.add_argument('-csv', type=str, default='flat-ui__data-Fri Aug 01 2025.csv', 
                       help='NYSE CSV file path (default: flat-ui__data-Fri Aug 01 2025.csv)')
    parser.add_argument('-output', type=str, default=None, 
                       help='Output JSON file (default: auto-generated timestamp)')
    parser.add_argument('-max-symbols', type=int, default=None, 
                       help='Maximum number of symbols to process (for testing)')
    parser.add_argument('-proxy-file', type=str, default='working_proxies.json',
                       help='Proxy JSON file path (default: working_proxies.json)')
    parser.add_argument('-save-to-db', action='store_true', default=True,
                       help='Save results to database (default: True)')
    return parser.parse_args()

def load_proxies_direct(proxy_file):
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
        
        logger.info(f"Loaded {len(proxies)} proxies directly from {proxy_file}")
        return proxies
        
    except FileNotFoundError:
        logger.warning(f"Proxy file not found: {proxy_file}")
        return []
    except Exception as e:
        logger.error(f"Error loading proxies: {e}")
        return []

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
        import yfinance.shared
        yfinance.shared._requests = session
    except Exception as e:
        logger.error(f"Failed to set proxy {proxy}: {e}")

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

def _safe_decimal(value):
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

def process_symbol(symbol, ticker_number, proxies, timeout=8, save_to_db=True):
    """Process a single symbol with comprehensive data collection and Django integration"""
    global shutdown_flag
    
    if shutdown_flag:
        return None
        
    try:
        # Get proxy for this ticker (if available)
        proxy = None
        if proxies and len(proxies) > 0:
            proxy = proxies[ticker_number % len(proxies)]
            if ticker_number <= 5:  # Show proxy info for first 5 tickers
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
        
        # Extract comprehensive data with better PE ratio and dividend yield handling
        stock_data = {
            'symbol': symbol,
            'name': info.get('longName', info.get('shortName', symbol)) if info else symbol,
            'current_price': _safe_decimal(current_price) if current_price else None,
            'previous_close': _safe_decimal(info.get('previousClose')) if info else None,
            'open_price': _safe_decimal(info.get('regularMarketOpen')) if info else None,
            'days_low': _safe_decimal(info.get('dayLow')) if info else None,
            'days_high': _safe_decimal(info.get('dayHigh')) if info else None,
            'volume': _safe_decimal(info.get('volume')) if info else None,
            'volume_today': _safe_decimal(info.get('volume')) if info else None,
            'avg_volume_3mon': _safe_decimal(info.get('averageVolume')) if info else None,
            'market_cap': _safe_decimal(info.get('marketCap')) if info else None,
            'pe_ratio': _safe_decimal(_extract_pe_ratio(info)) if info else None,
            'dividend_yield': _safe_decimal(_extract_dividend_yield(info)) if info else None,
            'week_52_low': _safe_decimal(info.get('fiftyTwoWeekLow')) if info else None,
            'week_52_high': _safe_decimal(info.get('fiftyTwoWeekHigh')) if info else None,
            'beta': _safe_decimal(info.get('beta')) if info else None,
            'exchange': info.get('exchange') if info else None,
            'earnings_per_share': _safe_decimal(info.get('trailingEps')) if info else None,
            'book_value': _safe_decimal(info.get('bookValue')) if info else None,
            'price_to_book': _safe_decimal(info.get('priceToBook')) if info else None,
            'one_year_target': _safe_decimal(info.get('targetMeanPrice')) if info else None,
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
                    stock_data['price_change_today'] = _safe_decimal(change)
                    stock_data['change_percent'] = _safe_decimal(change_percent)
            except:
                pass
        
        # Add volume analysis
        if stock_data.get('volume') and stock_data.get('avg_volume_3mon'):
            try:
                volume_ratio = stock_data['volume'] / stock_data['avg_volume_3mon']
                stock_data['dvav'] = _safe_decimal(volume_ratio)
            except:
                pass
        
        # Save to database if requested
        if save_to_db:
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
                
                logger.info(f"SUCCESS {symbol}: ${stock_data.get('current_price', 'N/A')} - {stock_data.get('name', 'N/A')} - PE: {stock_data.get('pe_ratio', 'N/A')} - Div: {stock_data.get('dividend_yield', 'N/A')}%")
                return stock_data
                
            except Exception as e:
                logger.error(f"DB ERROR {symbol}: {e}")
                return None
        else:
            # Just return the data without saving
            logger.info(f"SUCCESS {symbol}: ${stock_data.get('current_price', 'N/A')} - {stock_data.get('name', 'N/A')} - PE: {stock_data.get('pe_ratio', 'N/A')} - Div: {stock_data.get('dividend_yield', 'N/A')}%")
            return stock_data
        
    except Exception as e:
        logger.error(f"ERROR {symbol}: {e}")
        return None

def main():
    """Main function"""
    global shutdown_flag
    
    args = parse_arguments()
    
    print("ENHANCED STOCK RETRIEVAL SCRIPT - DJANGO VERSION WITH PROXIES")
    print("=" * 70)
    print(f"Configuration:")
    print(f"  CSV File: {args.csv}")
    print(f"  Test Mode: {args.test}")
    print(f"  Use Proxies: {not args.noproxy}")
    print(f"  Proxy File: {args.proxy_file}")
    print(f"  Threads: {args.threads}")
    print(f"  Timeout: {args.timeout}s")
    print(f"  Max Symbols: {args.max_symbols or 'All'}")
    print(f"  Save to DB: {args.save_to_db}")
    print("=" * 70)
    
    # Load NYSE symbols
    print(f"\nLoading NYSE symbols from {args.csv}...")
    symbols = load_nyse_symbols(args.csv, args.test, args.max_symbols)
    
    if not symbols:
        print("ERROR: No symbols loaded. Exiting.")
        return
    
    print(f"Processing {len(symbols)} symbols...")
    
    # Load proxies directly (without validation)
    proxies = []
    if not args.noproxy:
        print(f"Loading proxies from {args.proxy_file}...")
        proxies = load_proxies_direct(args.proxy_file)
        if proxies:
            print(f"SUCCESS: Loaded {len(proxies)} proxies (no validation)")
        else:
            print("WARNING: No proxies loaded - continuing without proxies")
    else:
        print("DISABLED: Proxy usage disabled")
    
    # Process stocks
    print(f"\nStarting to process {len(symbols)} symbols...")
    print("=" * 70)
    
    start_time = time.time()
    successful = 0
    failed = 0
    results = []
    
    # Use ThreadPoolExecutor for parallel processing with better timeout handling
    print(f"Submitting {len(symbols)} tasks to thread pool...")
    
    try:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            future_to_symbol = {}
            for i, symbol in enumerate(symbols, 1):
                if shutdown_flag:
                    break
                future = executor.submit(process_symbol, symbol, i, proxies, args.timeout, args.save_to_db)
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
                    # Use shorter timeout for individual tasks
                    result = future.result(timeout=args.timeout + 2)
                    if result:
                        successful += 1
                        results.append(result)
                    else:
                        failed += 1
                except TimeoutError:
                    logger.error(f"TIMEOUT {symbol}: Task timed out")
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
    print("\n" + "=" * 70)
    print("SCAN RESULTS")
    print("=" * 70)
    print(f"SUCCESSFUL: {successful}")
    print(f"FAILED: {failed}")
    if len(symbols) > 0:
        print(f"SUCCESS RATE: {(successful/len(symbols)*100):.1f}%")
    print(f"TIME: {elapsed:.2f}s")
    if elapsed > 0:
        print(f"RATE: {len(symbols)/elapsed:.2f} symbols/sec")
    
    if proxies:
        print(f"PROXY STATS: Used {len(proxies)} proxies (no validation)")
    
    if args.save_to_db:
        print(f"DATABASE: Saved {successful} stocks to database")
    
    # Save results to JSON if requested
    if results and args.output:
        try:
            output_data = {
                'scan_info': {
                    'timestamp': datetime.now().isoformat(),
                    'csv_file': args.csv,
                    'test_mode': args.test,
                    'use_proxies': not args.noproxy,
                    'proxy_file': args.proxy_file,
                    'proxies_loaded': len(proxies),
                    'threads': args.threads,
                    'timeout': args.timeout,
                    'max_symbols': args.max_symbols,
                    'total_symbols': len(symbols),
                    'successful': successful,
                    'failed': failed,
                    'success_rate': f"{(successful/len(symbols)*100):.1f}%" if len(symbols) > 0 else "0%",
                    'elapsed_time': f"{elapsed:.2f}s",
                    'rate': f"{len(symbols)/elapsed:.2f} symbols/sec" if elapsed > 0 else "0 symbols/sec",
                    'saved_to_db': args.save_to_db
                },
                'stocks': results
            }
            
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2, default=str)
            
            print(f"\nSUCCESS: Results saved to {args.output}")
            
        except Exception as e:
            print(f"ERROR: Failed to save results: {e}")
    
    print("\nScan completed!")

if __name__ == "__main__":
    main()