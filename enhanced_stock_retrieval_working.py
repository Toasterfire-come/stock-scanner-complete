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
import subprocess
import pytz

# Django imports for database integration
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from django.utils import timezone
from stocks.models import Stock, StockPrice

# Import shared utilities
from utils.stock_data import (
    safe_decimal_conversion, 
    load_nyse_symbols_from_csv, 
    extract_pe_ratio, 
    extract_dividend_yield,
    calculate_change_percent_from_history,
    extract_stock_data_from_info,
    calculate_volume_ratio
)

# Setup logging with rotation
from logging.handlers import RotatingFileHandler

# Configure logger with rotation to avoid unbounded log growth
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handlers
file_handler = RotatingFileHandler(
    'enhanced_stock_retrieval_working.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
console_handler = logging.StreamHandler()

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Prevent propagation to avoid duplicate messages
logger.propagate = False

# Global flag for graceful shutdown
shutdown_flag = False

# Market window configuration (US/Eastern) - configurable via environment variables
EASTERN_TZ = pytz.timezone('US/Eastern')
PREMARKET_START = os.getenv('PREMARKET_START', "04:00")  # 4:00 AM ET
POSTMARKET_END = os.getenv('POSTMARKET_END', "20:00")   # 8:00 PM ET

# Global proxy health tracking with thread safety
proxy_health = defaultdict(lambda: {"failures": 0, "successes": 0, "last_failure": None, "blocked": False})
proxy_health_lock = threading.Lock()  # Protect proxy_health dict updates
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


# Removed unused create_session_for_proxy function

def signal_handler(signum, frame):
    """Handle interrupt signals gracefully"""
    global shutdown_flag
    logger.info("Received interrupt signal. Shutting down gracefully...")
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
    parser.add_argument('-csv', type=str, default=os.getenv('NYSE_CSV_PATH', 'flat-ui__data-Fri Aug 01 2025.csv'), 
                       help='NYSE CSV file path (default from NYSE_CSV_PATH env var or flat-ui__data-Fri Aug 01 2025.csv)')
    parser.add_argument('-output', type=str, default=None, 
                       help='Output JSON file (default: auto-generated timestamp)')
    parser.add_argument('-max-symbols', type=int, default=None, 
                       help='Maximum number of symbols to process (for testing)')
    parser.add_argument('-proxy-file', type=str, default=os.getenv('PROXY_FILE_PATH', 'working_proxies.json'),
                       help='Proxy JSON file path (default from PROXY_FILE_PATH env var or working_proxies.json)')
    parser.add_argument('-schedule', action='store_true', help='Run in scheduler mode (every 3 minutes)')
    parser.add_argument('-save-to-db', action='store_true', default=True, help='Save results to database (default: True)')
    return parser.parse_args()

# Removed _safe_decimal - using shared safe_decimal_conversion from utils.stock_data

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
            
        with proxy_health_lock:
            health = proxy_health[proxy]
            
            # Check if proxy is blocked and cooldown period has passed
            if health["blocked"]:
                if health["last_failure"] and (current_time - health["last_failure"]).total_seconds() > proxy_retry_cooldown:
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
    with proxy_health_lock:
        healthy_proxies.sort(key=lambda p: proxy_health[p]["failures"])
    return healthy_proxies[0]

def mark_proxy_success(proxy):
    """Mark a proxy as successful"""
    if proxy:
        with proxy_health_lock:
            proxy_health[proxy]["successes"] += 1
            proxy_health[proxy]["failures"] = 0  # Reset failure count on success
            proxy_health[proxy]["blocked"] = False

def mark_proxy_failure(proxy, reason=""):
    """Mark a proxy as failed"""
    if not proxy:
        return
    
    with proxy_health_lock:
        health = proxy_health[proxy]
        health["failures"] += 1
        health["last_failure"] = datetime.now()
        
        if health["failures"] >= proxy_failure_threshold:
            health["blocked"] = True
            logger.warning(f"Proxy {proxy} marked as blocked after {health['failures']} failures. Reason: {reason}")

# Removed _extract_pe_ratio and _extract_dividend_yield - using shared utilities from utils.stock_data

# Using shared load_nyse_symbols_from_csv from utils.stock_data
def load_nyse_symbols(csv_file, test_mode=False, max_symbols=None):
    """Load NYSE symbols from CSV file, filtering delisted stocks - wrapper for shared utility"""
    return load_nyse_symbols_from_csv(csv_file, test_mode, max_symbols)

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

    def yfinance_retry_wrapper(func, max_attempts=3, backoff_factor=0.5):
        """Wrapper to add retry logic with exponential backoff to yfinance calls"""
        for attempt in range(max_attempts):
            try:
                return func()
            except Exception as e:
                if attempt == max_attempts - 1:  # Last attempt
                    if any(keyword in str(e).lower() for keyword in ['timeout', 'connection', 'proxy', 'ssl']):
                        raise
                    return None
                # Exponential backoff
                sleep_time = backoff_factor * (2 ** attempt)
                time.sleep(sleep_time)
        return None

    # Try multiple approaches to get data letting yfinance manage its own session
    ticker_obj = yf.Ticker(symbol)
    info = None
    hist = None
    current_price = None

    # Approach 1: Try fast_info first for speed, then fall back to full info with retry
    info = None
    
    # Try fast_info with retry - it's faster and has key price/market cap data
    fast_info = yfinance_retry_wrapper(lambda: ticker_obj.fast_info)
    if fast_info and hasattr(fast_info, 'last_price') and fast_info.last_price:
        current_price = fast_info.last_price
    
    # Try full info with retry if we need more comprehensive data
    if fast_info is None or not hasattr(fast_info, 'market_cap') or not fast_info.market_cap:
        info = yfinance_retry_wrapper(lambda: ticker_obj.info)
        if info and len(info) <= 3:
            info = None

    # Approach 2: Try to get historical data with multiple periods using retry
    for period in ["1d", "5d", "1mo"]:
        hist = yfinance_retry_wrapper(lambda: ticker_obj.history(period=period, timeout=timeout))
        if hist is not None and not hist.empty and len(hist) > 0:
            try:
                current_price = hist['Close'].iloc[-1]
                if current_price is not None and not pd.isna(current_price):
                    break
            except (KeyError, IndexError, ValueError) as e:
                logger.debug(f"Failed to extract price from history for {symbol}: {e}")
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
        'current_price': safe_decimal_conversion(current_price) if current_price else None,
        'price_change_today': None,
        'price_change_week': None,
        'price_change_month': None,
        'price_change_year': None,
        'change_percent': None,
        'bid_price': None,
        'ask_price': None,
        'bid_ask_spread': '',
        'days_range': '',
        # Use shared utility for extracting stock data from info
        **extract_stock_data_from_info(info, symbol, current_price) if info else {
            'days_low': None, 'days_high': None, 'volume': None, 'volume_today': None,
            'avg_volume_3mon': None, 'market_cap': None, 'pe_ratio': None, 'dividend_yield': None,
            'one_year_target': None, 'week_52_low': None, 'week_52_high': None,
            'earnings_per_share': None, 'book_value': None, 'price_to_book': None, 'exchange': 'NYSE'
        },
        'dvav': None,
        'shares_available': None,
        'market_cap_change_3mon': None,
        'pe_change_3mon': None,
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
    
    logger.info(f"{'='*60}")
    logger.info(f"STOCK UPDATE CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'='*60}")
    
    # Load NYSE symbols
    logger.info(f"Loading NYSE symbols from {args.csv}...")
    symbols = load_nyse_symbols(args.csv, args.test, args.max_symbols)
    
    if not symbols:
        logger.error("No symbols loaded. Skipping cycle.")
        return
    
    logger.info(f"Processing {len(symbols)} symbols...")
    
    # Load proxies directly (without validation)
    proxies = []
    if not args.noproxy:
        logger.info(f"Loading proxies from {args.proxy_file}...")
        proxies = load_proxies_direct(args.proxy_file)
        if proxies:
            logger.info(f"SUCCESS: Loaded {len(proxies)} proxies (no validation)")
        else:
            logger.warning("No proxies loaded - continuing without proxies")
    else:
        logger.info("DISABLED: Proxy usage disabled")
    
    # Process stocks
    logger.info(f"Starting to process {len(symbols)} symbols...")
    logger.info("=" * 60)
    
    start_time = time.time()
    successful = 0
    failed = 0
    results = []
    
    # Use ThreadPoolExecutor for parallel processing with better timeout handling
    logger.info(f"Submitting {len(symbols)} tasks to thread pool...")
    
    try:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            future_to_symbol = {}
            for i, symbol in enumerate(symbols, 1):
                if shutdown_flag:
                    break
                future = executor.submit(process_symbol_with_retry, symbol, i, proxies, args.timeout, args.test, args.save_to_db)
                future_to_symbol[future] = symbol
            
            logger.info(f"Submitted {len(future_to_symbol)} tasks. Processing...")
            completed = 0
            
            for future in as_completed(future_to_symbol):
                if shutdown_flag:
                    logger.info("Shutdown requested. Cancelling remaining tasks...")
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
                    logger.info(f"[PROGRESS] {completed}/{len(symbols)} completed ({successful} successful, {failed} failed)")
                    
                # Add a small delay to prevent overwhelming
                time.sleep(0.01)
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user. Shutting down gracefully...")
        shutdown_flag = True
    except Exception as e:
        logger.error(f"Thread pool execution failed: {e}")
    
    elapsed = time.time() - start_time
    
    # Results
    logger.info("=" * 60)
    logger.info("CYCLE RESULTS")
    logger.info("=" * 60)
    logger.info(f"SUCCESSFUL: {successful}")
    logger.info(f"FAILED: {failed}")
    if len(symbols) > 0:
        logger.info(f"SUCCESS RATE: {(successful/len(symbols)*100):.1f}%")
    logger.info(f"TIME: {elapsed:.2f}s")
    if elapsed > 0:
        logger.info(f"RATE: {len(symbols)/elapsed:.2f} symbols/sec")
    
    if proxies:
        logger.info(f"PROXY STATS: Used {len(proxies)} proxies")
        
        # Show proxy health summary
        healthy_count = 0
        blocked_count = 0
        total_failures = 0
        total_successes = 0
        
        with proxy_health_lock:
            for proxy in proxies:
                health = proxy_health[proxy]
                if health["blocked"]:
                    blocked_count += 1
                else:
                    healthy_count += 1
                total_failures += health["failures"]
                total_successes += health["successes"]
        
        logger.info(f"PROXY HEALTH: {healthy_count} healthy, {blocked_count} blocked")
        if total_successes + total_failures > 0:
            success_rate = (total_successes / (total_successes + total_failures)) * 100
            logger.info(f"PROXY SUCCESS RATE: {success_rate:.1f}% ({total_successes} successes, {total_failures} failures)")
    
    if args.save_to_db and not args.test:
        logger.info(f"DATABASE: Saved {successful} stocks to database")
    
    logger.info(f"CYCLE COMPLETED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

def _build_subprocess_args(args) -> list[str]:
    """Build argument list to spawn a one-off cycle in a separate process."""
    cmd = [sys.executable, os.path.abspath(__file__)]
    if args.noproxy:
        cmd.append('-noproxy')
    if args.test:
        cmd.append('-test')
    cmd += ['-threads', str(args.threads)]
    cmd += ['-timeout', str(args.timeout)]
    if args.csv:
        cmd += ['-csv', args.csv]
    if args.output:
        cmd += ['-output', args.output]
    if args.max_symbols:
        cmd += ['-max-symbols', str(args.max_symbols)]
    if args.proxy_file:
        cmd += ['-proxy-file', args.proxy_file]
    if args.save_to_db:
        cmd.append('-save-to-db')
    # Do NOT include '-schedule' here; child should run a single cycle and exit
    return cmd

# New helpers to launch companion tasks

def _build_news_subprocess_args() -> list[str]:
    """Build argument list for a single-run news scraping cycle."""
    news_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'news_scraper_with_restart.py'))
    cmd = [sys.executable, news_script]
    # Single run: do not pass -schedule
    # Keep defaults for limit/interval; can be extended later via env or args
    return cmd

def _build_email_subprocess_args() -> list[str]:
    """Build argument list for a single-run email sender cycle."""
    email_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'email_sender_with_restart.py'))
    cmd = [sys.executable, email_script]
    # Single run: do not pass -schedule
    # Keep defaults; can be extended later via env or args
    return cmd

def start_cycle_in_subprocess(args):
    """Start a single stock update cycle in a separate process, returning immediately.
    This allows a new cycle to begin every 3 minutes regardless of the prior run time.
    """
    try:
        cmd = _build_subprocess_args(args)
        logger.info(f"Spawning new stock cycle subprocess: {' '.join(cmd)}")
        subprocess.Popen(cmd)
    except Exception as e:
        logger.error(f"Failed to start subprocess cycle: {e}")

# New: launch all three cycles (stocks, news, email)

def start_all_cycles_in_subprocess(args):
    """Spawn stock, news scraper, and email sender cycles as separate subprocesses."""
    # Only run within market window (weekdays 04:00–20:00 ET)
    now_et = datetime.now(EASTERN_TZ)
    current_hhmm = now_et.strftime("%H:%M")
    if now_et.weekday() >= 5 or not (PREMARKET_START <= current_hhmm < POSTMARKET_END):
        logger.info(f"Skipping cycle spawn (outside market window) at {now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        return
    
    # Stocks
    start_cycle_in_subprocess(args)
    # News scraper
    try:
        news_cmd = _build_news_subprocess_args()
        logger.info(f"Spawning news scraper subprocess: {' '.join(news_cmd)}")
        subprocess.Popen(news_cmd)
    except Exception as e:
        logger.error(f"Failed to start news scraper subprocess: {e}")
    # Email sender
    try:
        email_cmd = _build_email_subprocess_args()
        logger.info(f"Spawning email sender subprocess: {' '.join(email_cmd)}")
        subprocess.Popen(email_cmd)
    except Exception as e:
        logger.error(f"Failed to start email sender subprocess: {e}")

def main():
    """Main function"""
    global shutdown_flag
    
    args = parse_arguments()
    
    logger.info("ENHANCED STOCK RETRIEVAL SCRIPT - WORKING VERSION WITH PROXIES")
    logger.info("=" * 60)
    logger.info(f"Configuration:")
    logger.info(f"  CSV File: {args.csv}")
    logger.info(f"  Test Mode: {args.test}")
    logger.info(f"  Use Proxies: {not args.noproxy}")
    logger.info(f"  Proxy File: {args.proxy_file}")
    logger.info(f"  Threads: {args.threads}")
    logger.info(f"  Timeout: {args.timeout}s")
    logger.info(f"  Max Symbols: {args.max_symbols or 'All'}")
    logger.info(f"  Save to DB: {args.save_to_db}")
    logger.info(f"  Schedule Mode: {args.schedule}")
    logger.info("=" * 60)
    
    if args.schedule:
        logger.info("SCHEDULER MODE: Spawning stock, news, and email cycles every 3 minutes (overlap allowed)")
        logger.info("Press Ctrl+C to stop the scheduler")
        logger.info("=" * 60)
        
        # Immediate run of all three
        start_all_cycles_in_subprocess(args)
        # Schedule subsequent runs every 3 minutes
        schedule.every(3).minutes.do(start_all_cycles_in_subprocess, args)
        
        try:
            while True:
                schedule.run_pending()
                
                # Stop scheduler after postmarket end on weekdays
                now_et = datetime.now(EASTERN_TZ)
                current_hhmm = now_et.strftime("%H:%M")
                if now_et.weekday() < 5 and current_hhmm >= POSTMARKET_END:
                    logger.info(f"Postmarket ended at {now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}. Stopping scheduler.")
                    break
                
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            shutdown_flag = True
    else:
        # Run single update in the current process
        run_stock_update(args)
    
    logger.info("Script completed!")

if __name__ == "__main__":
    main()