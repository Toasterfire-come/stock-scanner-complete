#!/usr/bin/env python3
"""
Test version of Enhanced Stock Retrieval Script - WITHOUT DJANGO
Tests proxy rotation, retry logic, and error handling improvements
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
from decimal import Decimal
from collections import defaultdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_enhanced_stock.log'),
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
    parser = argparse.ArgumentParser(description='Test Enhanced Stock Retrieval Script')
    parser.add_argument('-noproxy', action='store_true', help='Disable proxy usage')
    parser.add_argument('-test', action='store_true', help='Test mode - process only first 100 tickers')
    parser.add_argument('-threads', type=int, default=5, help='Number of threads (default: 5)')
    parser.add_argument('-timeout', type=int, default=10, help='Request timeout in seconds (default: 10)')
    parser.add_argument('-csv', type=str, default='flat-ui__data-Fri Aug 01 2025.csv', 
                       help='NYSE CSV file path (default: flat-ui__data-Fri Aug 01 2025.csv)')
    parser.add_argument('-max-symbols', type=int, default=20, 
                       help='Maximum number of symbols to process (default: 20)')
    parser.add_argument('-proxy-file', type=str, default='working_proxies.json',
                       help='Proxy JSON file path (default: working_proxies.json)')
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
        
        # Filter out None/empty values
        proxies = [p for p in proxies if p and isinstance(p, str)]
        
        logger.info(f"Loaded {len(proxies)} proxies directly from {proxy_file}")
        return proxies[:50]  # Limit to first 50 for testing
        
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

def patch_yfinance_proxy(proxy):
    """Patch yfinance to use proxy with enhanced error handling"""
    if not proxy:
        return
        
    try:
        session = requests.Session()
        session.proxies = {
            'http': proxy,
            'https': proxy
        }
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Set timeouts
        session.timeout = 10
        
        import yfinance.shared
        yfinance.shared._requests = session
        
    except Exception as e:
        logger.error(f"Failed to set proxy {proxy}: {e}")
        mark_proxy_failure(proxy, f"Session setup failed: {e}")

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

def process_symbol_with_retry(symbol, ticker_number, proxies, timeout=10, max_retries=3):
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
            
            result = process_symbol_attempt(symbol, proxy, timeout)
            
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

def process_symbol_attempt(symbol, proxy, timeout=10):
    """Single attempt to process a symbol"""
    
    # Set up proxy
    patch_yfinance_proxy(proxy)
    
    # Minimal delay to avoid rate limiting
    time.sleep(random.uniform(0.01, 0.02))
    
    # Try multiple approaches to get data
    ticker_obj = yf.Ticker(symbol)
    info = None
    fast_info = None
    hist = None
    current_price = None
    
    # Approach 0: Try to get fast_info first
    try:
        fast_info = ticker_obj.fast_info
        if fast_info and hasattr(fast_info, 'last_price') and fast_info.last_price:
            current_price = fast_info.last_price
    except Exception as e:
        if any(keyword in str(e).lower() for keyword in ['timeout', 'connection', 'proxy', 'ssl']):
            raise
        pass
    
    # Approach 1: Try to get basic info with timeout
    try:
        info = ticker_obj.info
        if info and len(info) <= 3:  # Minimal info suggests issue
            info = None
    except Exception as e:
        if any(keyword in str(e).lower() for keyword in ['timeout', 'connection', 'proxy', 'ssl']):
            raise  # Re-raise network errors for retry
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
            if any(keyword in str(e).lower() for keyword in ['timeout', 'connection', 'proxy', 'ssl']):
                raise  # Re-raise network errors for retry
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
    has_fast_info = fast_info is not None
    has_price = current_price is not None and not pd.isna(current_price)
    
    # Check for delisted or invalid stocks
    if info and info.get('quoteType') == 'NONE':
        logger.warning(f"{symbol}: possibly delisted; no price data found (period=1d)")
        return None
        
    if not has_data and not has_info and not has_fast_info:
        logger.warning(f"{symbol}: No data available")
        return None
        
    # Skip stocks with no current price data and no recent volume
    if not has_price and info and info.get('volume', 0) == 0:
        logger.warning(f"{symbol}: No current trading activity")
        return None
    
    # Helper to map from fast_info when info is missing
    def map_from_fast_info(fi, sym, cur_price):
        if not fi:
            return {}
        get = lambda names: next((getattr(fi, n, None) for n in names if getattr(fi, n, None) is not None), None)
        day_low = get(['day_low', 'low'])
        day_high = get(['day_high', 'high'])
        volume = get(['last_volume', 'volume'])
        avg_vol_3m = get(['three_month_average_volume', 'ten_day_average_volume'])
        market_cap = get(['market_cap'])
        wk52_low = get(['fifty_two_week_low', 'year_low'])
        wk52_high = get(['fifty_two_week_high', 'year_high'])
        name = get(['short_name', 'long_name']) or sym
        return {
            'symbol': sym,
            'current_price': float(cur_price) if cur_price else None,
            'company_name': name,
            'volume': volume,
            'market_cap': market_cap,
            'days_low': day_low,
            'days_high': day_high,
            'avg_volume_3mon': avg_vol_3m,
            'week_52_low': wk52_low,
            'week_52_high': wk52_high,
        }
    
    # Return enriched stock data
    if has_info:
        stock_data = {
            'symbol': symbol,
            'current_price': float(current_price) if current_price else None,
            'company_name': info.get('longName', info.get('shortName', symbol)) if info else symbol,
            'volume': info.get('volume') if info else None,
            'market_cap': info.get('marketCap') if info else None,
            'days_low': info.get('dayLow') if info else None,
            'days_high': info.get('dayHigh') if info else None,
            'avg_volume_3mon': info.get('averageVolume') if info else None,
            'week_52_low': info.get('fiftyTwoWeekLow') if info else None,
            'week_52_high': info.get('fiftyTwoWeekHigh') if info else None,
        }
    else:
        stock_data = map_from_fast_info(fast_info, symbol, current_price)
    
    return stock_data

def run_test():
    """Run test with enhanced proxy management"""
    global shutdown_flag
    
    args = parse_arguments()
    
    print("TEST ENHANCED STOCK RETRIEVAL SCRIPT")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  CSV File: {args.csv}")
    print(f"  Use Proxies: {not args.noproxy}")
    print(f"  Proxy File: {args.proxy_file}")
    print(f"  Threads: {args.threads}")
    print(f"  Timeout: {args.timeout}s")
    print(f"  Max Symbols: {args.max_symbols}")
    print("=" * 60)
    
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
            print(f"SUCCESS: Loaded {len(proxies)} proxies")
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
    
    try:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            future_to_symbol = {}
            for i, symbol in enumerate(symbols, 1):
                if shutdown_flag:
                    break
                future = executor.submit(process_symbol_with_retry, symbol, i, proxies, args.timeout)
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
                        print(f"✓ {symbol}: ${result.get('current_price', 'N/A')} - {result.get('company_name', 'N/A')}")
                    else:
                        failed += 1
                        print(f"✗ {symbol}: No data")
                except TimeoutError:
                    logger.error(f"TIMEOUT {symbol}: Task timed out")
                    failed += 1
                except Exception as e:
                    logger.error(f"ERROR {symbol}: {e}")
                    failed += 1
                
                # Show progress every 5 completed or at the end
                if completed % 5 == 0 or completed == len(symbols):
                    print(f"[PROGRESS] {completed}/{len(symbols)} completed ({successful} successful, {failed} failed)")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user. Shutting down gracefully...")
        shutdown_flag = True
    except Exception as e:
        print(f"ERROR: Thread pool execution failed: {e}")
    
    elapsed = time.time() - start_time
    
    # Results
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"SUCCESSFUL: {successful}")
    print(f"FAILED: {failed}")
    if len(symbols) > 0:
        print(f"SUCCESS RATE: {(successful/len(symbols)*100):.1f}%")
    print(f"TIME: {elapsed:.2f}s")
    if elapsed > 0:
        print(f"RATE: {len(symbols)/elapsed:.2f} symbols/sec")
    
    # Compute null counts for key fields across results
    if results:
        fields = ['company_name', 'current_price', 'volume', 'market_cap', 'days_low', 'days_high', 'avg_volume_3mon', 'week_52_low', 'week_52_high']
        null_counts = {f: 0 for f in fields}
        for r in results:
            for f in fields:
                if r.get(f) in (None, 0, 0.0):
                    null_counts[f] += 1
        print("\nNULL FIELD COUNTS (out of {} results):".format(len(results)))
        for f in fields:
            print(f"  {f}: {null_counts[f]}")

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
        
        # Show detailed health for first few proxies
        print("\nTOP PROXY PERFORMANCE:")
        proxy_list = sorted(proxies, key=lambda p: proxy_health[p]["successes"], reverse=True)[:5]
        for proxy in proxy_list:
            health = proxy_health[proxy]
            status = "BLOCKED" if health["blocked"] else "HEALTHY"
            print(f"  {proxy}: {health['successes']} successes, {health['failures']} failures [{status}]")
    
    print(f"\nTEST COMPLETED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    run_test()