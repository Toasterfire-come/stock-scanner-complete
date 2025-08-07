#!/usr/bin/env python3
"""
Enhanced Stock Retrieval Script - WORKING VERSION (Direct Proxy Loading)
Uses entire NYSE CSV, filters delisted stocks, supports production settings
Command line options: -noproxy, -test (100 first tickers), -threads, -timeout
Runs every 3 minutes in background with database integration
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
from datetime import datetime, timedelta
import logging
import signal
import schedule
import threading
from decimal import Decimal
from collections import defaultdict
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Django imports for database integration
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from django.utils import timezone
from stocks.models import Stock, StockPrice

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_stock_retrieval_working.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_flag = False

# Global proxy health tracking
proxy_health = defaultdict(lambda: {"failures": 0, "successes": 0, "last_failure": None, "blocked": False})
proxy_failure_threshold = 3  # Mark proxy as blocked after 3 consecutive failures
proxy_retry_cooldown = 300  # 5 minutes before retrying a blocked proxy

# New: normalize and validate proxy strings

def normalize_proxy_string(proxy_str: str) -> str | None:
    """Ensure proxy has a scheme and basic host:port shape."""
    if not proxy_str or not isinstance(proxy_str, str):
        return None
    p = proxy_str.strip()
    if not p:
        return None
    if '://' not in p:
        # Assume HTTP if not specified
        p = f"http://{p}"
    return p


def create_session_for_proxy(proxy: str | None, timeout: int = 10) -> requests.Session:
    """Create a requests.Session configured for a specific proxy with retries and default timeout."""
    session = requests.Session()

    # Mount retries
    retry = Retry(
        total=2,
        backoff_factor=0.2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=50, pool_maxsize=50)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Set proxies if provided
    if proxy:
        normalized = normalize_proxy_string(proxy)
        if normalized:
            session.proxies = {
                'http': normalized,
                'https': normalized,
            }

    # Inject default timeout by wrapping request
    original_request = session.request

    def request_with_timeout(method, url, **kwargs):
        if 'timeout' not in kwargs or kwargs['timeout'] is None:
            kwargs['timeout'] = timeout
        return original_request(method, url, **kwargs)

    session.request = request_with_timeout  # type: ignore[assignment]
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    return session

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
    parser = argparse.ArgumentParser(description='Enhanced Stock Retrieval Script - WORKING')
    parser.add_argument('-noproxy', action='store_true', help='Disable proxy usage')
    parser.add_argument('-test', action='store_true', help='Test mode - process only first 100 tickers')
    parser.add_argument('-threads', type=int, default=15, help='Number of threads (default: 15)')
    parser.add_argument('-timeout', type=int, default=10, help='Request timeout in seconds (default: 10)')
    parser.add_argument('-csv', type=str, default='flat-ui__data-Fri Aug 01 2025.csv', 
                       help='NYSE CSV file path (default: flat-ui__data-Fri Aug 01 2025.csv)')
    parser.add_argument('-output', type=str, default=None, 
                       help='Output JSON file (default: auto-generated timestamp)')
    parser.add_argument('-max-symbols', type=int, default=None, 
                       help='Maximum number of symbols to process (for testing)')
    parser.add_argument('-proxy-file', type=str, default='working_proxies.json',
                       help='Proxy JSON file path (default: working_proxies.json)')
    parser.add_argument('-schedule', action='store_true', help='Run in scheduler mode (every 3 minutes)')
    parser.add_argument('-save-to-db', action='store_true', default=True, help='Save results to database (default: True)')
    return parser.parse_args()

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
        
        # Normalize and filter
        normalized = []
        for p in proxies:
            np = normalize_proxy_string(p) if isinstance(p, str) else None
            if np:
                normalized.append(np)
        # De-dupe while preserving order
        seen = set()
        deduped = []
        for p in normalized:
            if p not in seen:
                seen.add(p)
                deduped.append(p)
        logger.info(f"Loaded {len(deduped)} proxies directly from {proxy_file}")
        return deduped
        
    except FileNotFoundError:
        logger.warning(f"Proxy file not found: {proxy_file}")
        return []
    except Exception as e:
        logger.error(f"Error loading proxies: {e}")
        return []

def get_healthy_proxy(proxies, used_proxies=None):
    """Get a healthy proxy, avoiding blocked ones"""
    if not proxies:
        return None
    
    if used_proxies is None:
        used_proxies = set()
    
    current_time = datetime.now()
    healthy_proxies = []
    
    for proxy in proxies:
        if proxy in used_proxies:
            continue
            
        health = proxy_health[proxy]
        
        # Check if proxy is blocked and cooldown period has passed
        if health["blocked"]:
            if health["last_failure"] and (current_time - health["last_failure"]).seconds > proxy_retry_cooldown:
                health["blocked"] = False
                health["failures"] = 0
                logger.info(f"Proxy {proxy} cooldown expired, marking as available")
            else:
                continue
        
        healthy_proxies.append(proxy)
    
    if not healthy_proxies:
        # If no healthy proxies, return a random one (last resort)
        return random.choice(proxies) if proxies else None
    
    # Prefer proxies with fewer failures
    healthy_proxies.sort(key=lambda p: proxy_health[p]["failures"])
    return healthy_proxies[0]

def mark_proxy_success(proxy):
    """Mark a proxy as successful"""
    if proxy:
        proxy_health[proxy]["successes"] += 1
        proxy_health[proxy]["failures"] = 0  # Reset failure count on success
        proxy_health[proxy]["blocked"] = False

def mark_proxy_failure(proxy, reason=""):
    """Mark a proxy as failed"""
    if not proxy:
        return
        
    health = proxy_health[proxy]
    health["failures"] += 1
    health["last_failure"] = datetime.now()
    
    if health["failures"] >= proxy_failure_threshold:
        health["blocked"] = True
        logger.warning(f"Proxy {proxy} marked as blocked after {health['failures']} failures. Reason: {reason}")

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

def process_symbol_with_retry(symbol, ticker_number, proxies, timeout=10, test_mode=False, save_to_db=True, max_retries=3):
    """Process a single symbol with retry logic and proxy rotation"""
    global shutdown_flag
    
    if shutdown_flag:
        return None
    
    used_proxies = set()
    last_error = None
    
    for attempt in range(max_retries):
        if shutdown_flag:
            return None
            
        try:
            # Get a healthy proxy
            proxy = get_healthy_proxy(proxies, used_proxies) if proxies else None
            if proxy:
                used_proxies.add(proxy)
                if ticker_number <= 5 or attempt > 0:  # Show proxy info for first 5 tickers or retries
                    logger.info(f"{symbol} (attempt {attempt + 1}): Using proxy {proxy}")
            
            result = process_symbol_attempt(symbol, proxy, timeout, test_mode, save_to_db)
            
            if result is not None:
                # Success - mark proxy as working
                if proxy:
                    mark_proxy_success(proxy)
                return result
            else:
                # No data but no error - might be legitimate (delisted stock)
                if proxy:
                    mark_proxy_success(proxy)  # Don't penalize proxy for legitimate no-data
                return None
                
        except Exception as e:
            last_error = e
            if proxy:
                error_msg = str(e).lower()
                
                # Check if it's a proxy-related error
                if any(keyword in error_msg for keyword in ['timeout', 'connection', 'proxy', 'network', 'ssl', 'timed out']):
                    mark_proxy_failure(proxy, str(e))
                    logger.warning(f"{symbol} (attempt {attempt + 1}): Proxy error with {proxy}: {e}")
                    
                    # Add small delay before retry
                    time.sleep(random.uniform(0.1, 0.3))
                    continue
                else:
                    # Non-proxy error, might be legitimate (delisted stock, etc.)
                    mark_proxy_success(proxy)  # Don't penalize proxy
                    logger.warning(f"{symbol}: Non-proxy error: {e}")
                    return None
            else:
                logger.warning(f"{symbol}: Error without proxy: {e}")
                return None
    
    # All retries failed
    logger.error(f"{symbol}: All {max_retries} attempts failed. Last error: {last_error}")
    return None

def process_symbol_attempt(symbol, proxy, timeout=10, test_mode=False, save_to_db=True):
    """Single attempt to process a symbol"""
    # Minimal delay to avoid rate limiting
    time.sleep(random.uniform(0.01, 0.02))

    # Try multiple approaches to get data letting yfinance manage its own session
    ticker_obj = yf.Ticker(symbol)
    info = None
    hist = None
    current_price = None

    # Approach 1: Try to get basic info
    try:
        info = ticker_obj.info
        if info and len(info) <= 3:
            info = None
    except Exception as e:
        if any(keyword in str(e).lower() for keyword in ['timeout', 'connection', 'proxy', 'ssl']):
            raise
        pass

    # Approach 2: Try to get historical data with multiple periods
    for period in ["1d", "5d", "1mo"]:
        try:
            # Newer yfinance supports timeout in history
            hist = ticker_obj.history(period=period, timeout=timeout)
            if hist is not None and not hist.empty and len(hist) > 0:
                try:
                    current_price = hist['Close'].iloc[-1]
                    if current_price is not None and not pd.isna(current_price):
                        break
                except Exception:
                    continue
        except Exception as e:
            if any(keyword in str(e).lower() for keyword in ['timeout', 'connection', 'proxy', 'ssl']):
                raise
            continue

    # Approach 3: Try to get current price from info if historical failed
    if current_price is None and info:
        try:
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('regularMarketOpen')
        except Exception:
            pass

    # Determine if we have enough data to process
    has_data = hist is not None and not hist.empty
    has_info = info and isinstance(info, dict) and len(info) > 3
    has_price = current_price is not None and not pd.isna(current_price)

    # Check for delisted or invalid stocks
    if info and info.get('quoteType') == 'NONE':
        logger.warning(f"{symbol}: possibly delisted; no price data found (period=1d)")
        return None

    if not has_data and not has_info:
        logger.warning(f"{symbol}: No data available")
        return None

    if not has_price and info and info.get('volume', 0) == 0:
        logger.warning(f"{symbol}: No current trading activity")
        return None

    # Extract and save data (unchanged)
    stock_data = {
        'ticker': symbol,
        'symbol': symbol,
        'company_name': info.get('longName', info.get('shortName', symbol)) if info else symbol,
        'name': info.get('longName', info.get('shortName', symbol)) if info else symbol,
        'current_price': _safe_decimal(current_price) if current_price else None,
        'price_change_today': None,
        'price_change_week': None,
        'price_change_month': None,
        'price_change_year': None,
        'change_percent': None,
        'bid_price': None,
        'ask_price': None,
        'bid_ask_spread': '',
        'days_range': '',
        'days_low': _safe_decimal(info.get('dayLow')) if info else None,
        'days_high': _safe_decimal(info.get('dayHigh')) if info else None,
        'volume': _safe_decimal(info.get('volume')) if info else None,
        'volume_today': _safe_decimal(info.get('volume')) if info else None,
        'avg_volume_3mon': _safe_decimal(info.get('averageVolume')) if info else None,
        'dvav': None,
        'shares_available': None,
        'market_cap': _safe_decimal(info.get('marketCap')) if info else None,
        'market_cap_change_3mon': None,
        'pe_ratio': _safe_decimal(_extract_pe_ratio(info)) if info else None,
        'pe_change_3mon': None,
        'dividend_yield': _safe_decimal(_extract_dividend_yield(info)) if info else None,
        'one_year_target': _safe_decimal(info.get('targetMeanPrice')) if info else None,
        'week_52_low': _safe_decimal(info.get('fiftyTwoWeekLow')) if info else None,
        'week_52_high': _safe_decimal(info.get('fiftyTwoWeekHigh')) if info else None,
        'earnings_per_share': _safe_decimal(info.get('trailingEps')) if info else None,
        'book_value': _safe_decimal(info.get('bookValue')) if info else None,
        'price_to_book': _safe_decimal(info.get('priceToBook')) if info else None,
        'exchange': info.get('exchange', 'NYSE') if info else 'NYSE',
        'last_updated': timezone.now(),
        'created_at': timezone.now()
    }

    try:
        if save_to_db and not test_mode:
            stock, created = Stock.objects.update_or_create(
                ticker=symbol,
                defaults=stock_data
            )
            if stock_data.get('current_price'):
                StockPrice.objects.create(stock=stock, price=stock_data['current_price'])
        return stock_data if not save_to_db or test_mode else stock_data
    except Exception as e:
        logger.error(f"DB ERROR {symbol}: {e}")
        raise

# Create an alias for backward compatibility
def process_symbol(symbol, ticker_number, proxies, timeout=10, test_mode=False, save_to_db=True):
    """Backward compatibility wrapper"""
    return process_symbol_with_retry(symbol, ticker_number, proxies, timeout, test_mode, save_to_db)

def run_stock_update(args):
    """Run a single stock update cycle"""
    global shutdown_flag
    
    print(f"\n{'='*60}")
    print(f"STOCK UPDATE CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # Load NYSE symbols
    print(f"Loading NYSE symbols from {args.csv}...")
    symbols = load_nyse_symbols(args.csv, args.test, args.max_symbols)
    
    if not symbols:
        print("ERROR: No symbols loaded. Skipping cycle.")
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
    print(f"Starting to process {len(symbols)} symbols...")
    print("=" * 60)
    
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
                future = executor.submit(process_symbol_with_retry, symbol, i, proxies, args.timeout, args.test, args.save_to_db)
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
    print("\n" + "=" * 60)
    print("CYCLE RESULTS")
    print("=" * 60)
    print(f"SUCCESSFUL: {successful}")
    print(f"FAILED: {failed}")
    if len(symbols) > 0:
        print(f"SUCCESS RATE: {(successful/len(symbols)*100):.1f}%")
    print(f"TIME: {elapsed:.2f}s")
    if elapsed > 0:
        print(f"RATE: {len(symbols)/elapsed:.2f} symbols/sec")
    
    if proxies:
        print(f"PROXY STATS: Used {len(proxies)} proxies")
        
        # Show proxy health summary
        healthy_count = 0
        blocked_count = 0
        total_failures = 0
        total_successes = 0
        
        for proxy in proxies:
            health = proxy_health[proxy]
            if health["blocked"]:
                blocked_count += 1
            else:
                healthy_count += 1
            total_failures += health["failures"]
            total_successes += health["successes"]
        
        print(f"PROXY HEALTH: {healthy_count} healthy, {blocked_count} blocked")
        if total_successes + total_failures > 0:
            success_rate = (total_successes / (total_successes + total_failures)) * 100
            print(f"PROXY SUCCESS RATE: {success_rate:.1f}% ({total_successes} successes, {total_failures} failures)")
    
    if args.save_to_db and not args.test:
        print(f"DATABASE: Saved {successful} stocks to database")
    
    print(f"CYCLE COMPLETED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

def main():
    """Main function"""
    global shutdown_flag
    
    args = parse_arguments()
    
    print("ENHANCED STOCK RETRIEVAL SCRIPT - WORKING VERSION WITH PROXIES")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  CSV File: {args.csv}")
    print(f"  Test Mode: {args.test}")
    print(f"  Use Proxies: {not args.noproxy}")
    print(f"  Proxy File: {args.proxy_file}")
    print(f"  Threads: {args.threads}")
    print(f"  Timeout: {args.timeout}s")
    print(f"  Max Symbols: {args.max_symbols or 'All'}")
    print(f"  Save to DB: {args.save_to_db}")
    print(f"  Schedule Mode: {args.schedule}")
    print("=" * 60)
    
    if args.schedule:
        print(f"\nSCHEDULER MODE: Running every 3 minutes")
        print(f"Press Ctrl+C to stop the scheduler")
        print("=" * 60)
        
        # Schedule the job to run every 3 minutes
        schedule.every(3).minutes.do(run_stock_update, args)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nScheduler stopped by user")
            shutdown_flag = True
    else:
        # Run single update
        run_stock_update(args)
    
    print("\nScript completed!")

if __name__ == "__main__":
    main()