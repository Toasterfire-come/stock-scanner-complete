#!/usr/bin/env python3
"""
Ultra-Fast Stock Retrieval - Aggressive Mode
Direct parallel fast_info approach for maximum speed
Target: 50-70 tickers/second (9,394 stocks in ~2.6 minutes)
"""

import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import django
    django.setup()
    from stocks.models import Stock, StockPrice
    DJANGO_AVAILABLE = True
except Exception as e:
    print(f"Warning: Django not available: {e}")
    DJANGO_AVAILABLE = False

import yfinance as yf
try:
    from curl_cffi.requests import Session
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False
    print("Warning: curl_cffi not available, proxy support disabled")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def safe_decimal(value, default=None):
    """Safely convert value to Decimal."""
    if value is None or value == '':
        return default
    try:
        return Decimal(str(value))
    except:
        return default

def create_session(proxy=None, timeout=3):
    """Create curl_cffi session with optional proxy."""
    if not CURL_CFFI_AVAILABLE or not proxy:
        return None
    try:
        session = Session(impersonate="chrome110")
        session.proxies = {"http": proxy, "https": proxy}
        session.timeout = timeout
        return session
    except:
        return None

def load_symbols():
    """Load symbols from database."""
    if not DJANGO_AVAILABLE:
        logger.error("Django not available!")
        return []

    try:
        symbols = list(Stock.objects.values_list('ticker', flat=True).order_by('ticker'))
        logger.info(f"Loaded {len(symbols)} symbols from database")
        return symbols
    except Exception as e:
        logger.error(f"Failed to load symbols: {e}")
        return []

def load_proxies(proxy_file="working_proxies.json"):
    """Load proxies from JSON file."""
    if not os.path.exists(proxy_file):
        return []

    try:
        with open(proxy_file, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict) and 'proxies' in data:
                proxies = data['proxies']
            elif isinstance(data, list):
                proxies = data
            else:
                return []

            logger.info(f"Loaded {len(proxies)} proxies from {proxy_file}")
            return proxies
    except Exception as e:
        logger.warning(f"Failed to load proxies: {e}")
        return []

class ProxyManager:
    """Manages proxy rotation with health tracking."""

    def __init__(self, proxies):
        self.proxies = proxies
        self.health = {p: {"failures": 0, "successes": 0} for p in proxies}
        self.lock = threading.Lock()
        self.index = 0

    def get_proxy(self):
        """Get next healthy proxy."""
        if not self.proxies:
            return None

        with self.lock:
            # Find next healthy proxy (failures < 5)
            for _ in range(len(self.proxies)):
                proxy = self.proxies[self.index]
                self.index = (self.index + 1) % len(self.proxies)

                if self.health[proxy]["failures"] < 5:
                    return proxy

            # All proxies failed, reset and try again
            for p in self.proxies:
                self.health[p]["failures"] = 0
            return self.proxies[0] if self.proxies else None

    def mark_success(self, proxy):
        """Mark proxy as successful."""
        if proxy and proxy in self.health:
            with self.lock:
                self.health[proxy]["successes"] += 1
                self.health[proxy]["failures"] = max(0, self.health[proxy]["failures"] - 1)

    def mark_failure(self, proxy):
        """Mark proxy as failed."""
        if proxy and proxy in self.health:
            with self.lock:
                self.health[proxy]["failures"] += 1

def fetch_single_stock(symbol, proxy_manager=None, timeout=3):
    """Fetch single stock using fast_info."""
    try:
        proxy = proxy_manager.get_proxy() if proxy_manager else None
        session = create_session(proxy, timeout) if proxy else None

        ticker = yf.Ticker(symbol.replace('.', '-'), session=session)
        fast = ticker.fast_info

        if fast and hasattr(fast, 'last_price') and fast.last_price:
            if proxy_manager:
                proxy_manager.mark_success(proxy)

            return {
                'ticker': symbol,
                'current_price': safe_decimal(fast.last_price),
                'volume': int(getattr(fast, 'last_volume', 0) or 0),
                'market_cap': safe_decimal(getattr(fast, 'market_cap', None)),
                'last_updated': datetime.now()
            }
    except Exception as e:
        if proxy_manager and proxy:
            proxy_manager.mark_failure(proxy)
        logger.debug(f"Failed to fetch {symbol}: {e}")

    return None

def aggressive_parallel_update(symbols, threads=250, timeout=3, use_proxies=False):
    """
    Aggressive parallel update using direct fast_info calls.
    No batching - pure parallel processing for maximum speed.
    """
    logger.info("=" * 70)
    logger.info("AGGRESSIVE MODE: Direct parallel fast_info")
    logger.info("=" * 70)
    logger.info(f"Symbols: {len(symbols)}")
    logger.info(f"Threads: {threads}")
    logger.info(f"Timeout: {timeout}s")
    logger.info(f"Proxies: {'Enabled' if use_proxies else 'Disabled'}")
    logger.info("=" * 70)

    # Load proxies if enabled
    proxy_manager = None
    if use_proxies:
        proxies = load_proxies()
        if proxies:
            proxy_manager = ProxyManager(proxies)
            logger.info(f"Using {len(proxies)} proxies")

    all_results = []
    start_time = time.time()

    # Direct parallel processing
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(fetch_single_stock, sym, proxy_manager, timeout): sym
            for sym in symbols
        }

        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            if result:
                all_results.append(result)

            # Progress every 100 symbols
            if i % 100 == 0:
                elapsed = time.time() - start_time
                rate = i / elapsed if elapsed > 0 else 0
                eta = (len(symbols) - i) / rate / 60 if rate > 0 else 0
                logger.info(f"Progress: {i}/{len(symbols)} ({i/len(symbols)*100:.1f}%) | "
                          f"Rate: {rate:.1f} t/s | ETA: {eta:.1f} min")

    elapsed = time.time() - start_time
    rate = len(symbols) / elapsed if elapsed > 0 else 0

    # Results
    logger.info("=" * 70)
    logger.info("RESULTS")
    logger.info("=" * 70)
    logger.info(f"Total symbols: {len(symbols)}")
    logger.info(f"Successful: {len(all_results)}")
    logger.info(f"Failed: {len(symbols) - len(all_results)}")
    logger.info(f"Success rate: {len(all_results)/len(symbols)*100:.1f}%")
    logger.info(f"Time: {elapsed:.2f}s ({elapsed/60:.2f} min)")
    logger.info(f"Rate: {rate:.2f} tickers/second")

    if rate >= 50:
        logger.info("SUCCESS: 50+ tickers/second achieved!")
    elif rate >= 30:
        logger.info("GOOD: 30+ tickers/second")
    else:
        logger.info("SLOW: Consider increasing threads or using proxies")

    logger.info("=" * 70)

    # Proxy stats
    if proxy_manager:
        total_successes = sum(h["successes"] for h in proxy_manager.health.values())
        total_failures = sum(h["failures"] for h in proxy_manager.health.values())
        logger.info(f"Proxy stats: {total_successes} successes, {total_failures} failures")

    return all_results

def save_to_database(results):
    """Save results to database."""
    if not DJANGO_AVAILABLE or not results:
        return 0

    logger.info(f"Saving {len(results)} stocks to database...")
    saved = 0

    for data in results:
        if not data.get('ticker'):
            continue

        try:
            # Remove non-model fields
            db_data = {k: v for k, v in data.items()
                      if k not in ['valuation', 'shares_outstanding']}

            stock, _ = Stock.objects.update_or_create(
                ticker=data['ticker'],
                defaults=db_data
            )

            if data.get('current_price'):
                StockPrice.objects.create(
                    stock=stock,
                    price=data['current_price']
                )

            saved += 1
        except Exception as e:
            logger.debug(f"DB save error {data.get('ticker')}: {e}")

    logger.info(f"Saved {saved}/{len(results)} stocks to database")
    return saved

def main():
    parser = argparse.ArgumentParser(description='Ultra-Fast Aggressive Stock Retrieval')
    parser.add_argument('-test', action='store_true', help='Test mode (100 symbols)')
    parser.add_argument('-threads', type=int, default=250, help='Thread count (default: 250)')
    parser.add_argument('-timeout', type=int, default=3, help='Timeout in seconds (default: 3)')
    parser.add_argument('-noproxy', action='store_true', help='Disable proxy usage')
    parser.add_argument('-save-to-db', action='store_true', help='Save results to database')
    parser.add_argument('-max-symbols', type=int, help='Max symbols to process')
    args = parser.parse_args()

    # Load symbols
    symbols = load_symbols()

    if not symbols:
        logger.error("No symbols loaded!")
        return

    # Apply limits
    if args.test:
        symbols = symbols[:100]
        logger.info("TEST MODE: Processing first 100 symbols")
    elif args.max_symbols:
        symbols = symbols[:args.max_symbols]
        logger.info(f"Processing first {args.max_symbols} symbols")

    # Run aggressive update
    results = aggressive_parallel_update(
        symbols,
        threads=args.threads,
        timeout=args.timeout,
        use_proxies=not args.noproxy
    )

    # Save to database
    if args.save_to_db:
        save_to_database(results)

    logger.info(f"Completed with {len(results)} results")

if __name__ == "__main__":
    main()
