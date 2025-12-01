#!/usr/bin/env python3
"""
Ultra-Fast Stock Retrieval Script - TARGET: 50+ tickers/second
Optimized for maximum throughput with concurrent batch processing.

Key Optimizations:
1. Async-style concurrent fetching with high thread count
2. Batch yfinance downloads (50-100 symbols at once)
3. Connection pooling and keep-alive
4. Minimal data extraction (price, volume, market cap only in fast mode)
5. Smart proxy rotation with circuit breakers
6. Zero delays in fast mode
"""

import os
import sys
import time
import random
import json
import argparse
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from datetime import datetime
import logging
import signal
import threading
from decimal import Decimal
from collections import defaultdict
import pytz
from pathlib import Path

# Django imports - lazy initialization
DJANGO_READY = False
Stock = None
StockPrice = None

def ensure_django_initialized():
    """Initialize Django only when needed for DB operations."""
    global DJANGO_READY, Stock, StockPrice
    if DJANGO_READY:
        return True
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
        django.setup()
        from stocks.models import Stock as StockModel, StockPrice as StockPriceModel
        Stock = StockModel
        StockPrice = StockPriceModel
        DJANGO_READY = True
        return True
    except Exception as e:
        logger.error(f"Django init failed: {e}")
        return False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global shutdown flag
shutdown_flag = False

# Market hours (ET)
EASTERN_TZ = pytz.timezone('US/Eastern')
MARKET_OPEN = "09:30"
MARKET_CLOSE = "16:00"

# Proxy health tracking
proxy_health = defaultdict(lambda: {"failures": 0, "blocked": False, "last_used": 0})
proxy_lock = threading.Lock()

# Performance counters
perf_stats = {
    "total_fetched": 0,
    "batch_times": [],
    "lock": threading.Lock()
}

def signal_handler(signum, frame):
    global shutdown_flag
    logger.info("Shutdown signal received...")
    shutdown_flag = True

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Ultra-Fast Stock Retrieval - Under 3 min for 9,394 stocks')
    parser.add_argument('-test', action='store_true', help='Test mode - first 100 tickers')
    parser.add_argument('-threads', type=int, default=200, help='Thread count (default: 200 for parallel batches)')
    parser.add_argument('-batch-size', type=int, default=20, help='Batch size for yf.download (default: 20 for best Yahoo API success)')
    parser.add_argument('-timeout', type=int, default=5, help='Request timeout (default: 5s)')
    parser.add_argument('-noproxy', action='store_true', help='Disable proxies')
    parser.add_argument('-proxy-file', type=str, default='working_proxies.json', help='Proxy file')
    parser.add_argument('-save-to-db', action='store_true', help='Save to database')
    parser.add_argument('-fast', action='store_true', help='Fast mode - minimal data extraction')
    parser.add_argument('-ignore-market-hours', action='store_true', help='Run outside market hours')
    parser.add_argument('-max-symbols', type=int, default=None, help='Max symbols to process')
    parser.add_argument('-output', type=str, default=None, help='Output JSON file')
    return parser.parse_args()

def load_proxies(proxy_file):
    """Load proxies from JSON file."""
    try:
        with open(proxy_file, 'r') as f:
            data = json.load(f)
        proxies = data.get('proxies', [])
        # Normalize format
        normalized = []
        for p in proxies:
            if p and isinstance(p, str):
                p = p.strip()
                if '://' not in p:
                    p = f"http://{p}"
                normalized.append(p)
        logger.info(f"Loaded {len(normalized)} proxies")
        return normalized
    except Exception as e:
        logger.warning(f"Failed to load proxies: {e}")
        return []

def get_healthy_proxy(proxies):
    """Get a healthy proxy with circuit breaker."""
    if not proxies:
        return None

    now = time.time()
    with proxy_lock:
        # Find healthy proxies not recently used
        healthy = []
        for p in proxies:
            health = proxy_health[p]
            if health["blocked"]:
                # Check 5-minute cooldown
                if now - health.get("last_used", 0) > 300:
                    health["blocked"] = False
                    health["failures"] = 0
                else:
                    continue
            healthy.append(p)

        if not healthy:
            # All blocked - reset oldest
            oldest = min(proxies, key=lambda p: proxy_health[p].get("last_used", 0))
            proxy_health[oldest]["blocked"] = False
            proxy_health[oldest]["failures"] = 0
            return oldest

        # Prefer less-used proxies
        selected = min(healthy, key=lambda p: proxy_health[p].get("last_used", 0))
        proxy_health[selected]["last_used"] = now
        return selected

def mark_proxy_success(proxy):
    if proxy:
        with proxy_lock:
            proxy_health[proxy]["failures"] = 0
            proxy_health[proxy]["blocked"] = False

def mark_proxy_failure(proxy):
    if proxy:
        with proxy_lock:
            proxy_health[proxy]["failures"] += 1
            if proxy_health[proxy]["failures"] >= 3:
                proxy_health[proxy]["blocked"] = True

def create_session(proxy=None, timeout=5):
    """Create optimized session with connection pooling."""
    try:
        from curl_cffi.requests import Session as CurlSession
        session = CurlSession()
    except ImportError:
        session = requests.Session()
        from requests.adapters import HTTPAdapter
        adapter = HTTPAdapter(pool_connections=50, pool_maxsize=100)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

    if proxy:
        session.proxies = {"http": proxy, "https": proxy}

    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    })

    return session

def load_symbols(test_mode=False, max_symbols=None):
    """Load symbols from database (preferred) or fallback to combined tickers/CSV."""
    symbols = []

    # Try database first (9,394 validated stocks)
    try:
        if ensure_django_initialized():
            symbols = list(Stock.objects.values_list('ticker', flat=True).order_by('ticker'))
            logger.info(f"Loaded {len(symbols)} symbols from database (validated stocks)")
    except Exception as e:
        logger.warning(f"Failed to load from database: {e}")

    # Fallback to combined tickers
    if not symbols:
        combined_dir = Path(__file__).resolve().parent / 'data' / 'combined'
        if combined_dir.exists():
            try:
                import importlib.util
                candidates = sorted(combined_dir.glob('combined_tickers_*.py'),
                                  key=lambda f: f.stat().st_mtime, reverse=True)
                if candidates:
                    spec = importlib.util.spec_from_file_location('tickers', str(candidates[0]))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    symbols = list(getattr(module, 'COMBINED_TICKERS', []))
                    logger.info(f"Loaded {len(symbols)} symbols from {candidates[0].name}")
            except Exception as e:
                logger.warning(f"Failed to load combined tickers: {e}")

    # Fallback to CSV
    if not symbols:
        csv_path = Path(__file__).resolve().parent / 'flat-ui__data-Fri Aug 01 2025.csv'
        if csv_path.exists():
            try:
                import csv
                with open(csv_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        sym = row.get('Symbol', '').strip().upper()
                        if sym and not any(c in sym for c in ['$', '^', ' ', '/']):
                            symbols.append(sym)
                logger.info(f"Loaded {len(symbols)} symbols from CSV")
            except Exception as e:
                logger.error(f"Failed to load CSV: {e}")

    # Apply limits
    if test_mode:
        symbols = symbols[:100]
    if max_symbols:
        symbols = symbols[:max_symbols]

    return list(set(symbols))  # Dedupe

def safe_decimal(value):
    """Convert to Decimal safely."""
    try:
        if value is None or pd.isna(value):
            return None
        return Decimal(str(float(value)))
    except:
        return None

def batch_download_fast(symbols, proxy=None, timeout=5):
    """
    Ultra-fast batch download using yf.download().
    Returns dict of {symbol: data} for successful fetches.
    """
    if not symbols:
        return {}

    results = {}

    try:
        session = create_session(proxy, timeout)

        # Use yf.download for batch efficiency - use 5d period for better data availability
        df = yf.download(
            tickers=symbols,
            period="5d",
            interval="1d",
            progress=False,
            threads=True,
            session=session,
            timeout=timeout
        )

        if df is None or df.empty:
            return {}

        # Determine if we have multi-index columns (multiple symbols)
        is_multi = isinstance(df.columns, pd.MultiIndex)

        if is_multi:
            # Multiple symbols - columns are (Price, Ticker)
            # Get available tickers from the dataframe
            available_tickers = df.columns.get_level_values(1).unique().tolist()

            for sym in symbols:
                try:
                    # Check if symbol is in the downloaded data
                    if sym not in available_tickers:
                        continue

                    # Use .loc with tuple indexing for MultiIndex
                    close_series = df['Close'][sym].dropna()
                    if close_series.empty:
                        continue

                    close = close_series.iloc[-1]
                    volume = 0
                    try:
                        vol_val = df['Volume'][sym].iloc[-1]
                        volume = int(vol_val) if vol_val and not pd.isna(vol_val) else 0
                    except:
                        pass

                    # Calculate change
                    change = None
                    change_pct = None
                    if len(close_series) >= 2:
                        prev = close_series.iloc[-2]
                        if prev and prev != 0:
                            change = close - prev
                            change_pct = (change / prev) * 100

                    results[sym] = {
                        'ticker': sym,
                        'current_price': safe_decimal(close),
                        'volume': volume,
                        'price_change_today': safe_decimal(change),
                        'change_percent': safe_decimal(change_pct),
                    }
                except Exception as e:
                    logger.debug(f"Symbol {sym} parse error: {e}")
                    continue
        else:
            # Single symbol - simple columns
            sym = symbols[0]
            try:
                if 'Close' in df.columns:
                    close_series = df['Close'].dropna()
                    if not close_series.empty:
                        close = close_series.iloc[-1]
                        volume = 0
                        if 'Volume' in df.columns:
                            vol_val = df['Volume'].iloc[-1]
                            volume = int(vol_val) if vol_val and not pd.isna(vol_val) else 0

                        # Calculate change
                        change = None
                        change_pct = None
                        if len(close_series) >= 2:
                            prev = close_series.iloc[-2]
                            if prev and prev != 0:
                                change = close - prev
                                change_pct = (change / prev) * 100

                        results[sym] = {
                            'ticker': sym,
                            'current_price': safe_decimal(close),
                            'volume': volume,
                            'price_change_today': safe_decimal(change),
                            'change_percent': safe_decimal(change_pct),
                        }
            except Exception as e:
                logger.debug(f"Single symbol {sym} parse error: {e}")

        if proxy and results:
            mark_proxy_success(proxy)

    except Exception as e:
        if proxy:
            mark_proxy_failure(proxy)
        logger.debug(f"Batch download error: {e}")

    return results

def fetch_detailed_data(symbol, proxy=None, timeout=5):
    """
    Fetch detailed data for a single symbol.
    Used for full mode or when batch fails.
    """
    try:
        session = create_session(proxy, timeout)
        ticker = yf.Ticker(symbol.replace('.', '-'), session=session)

        # Try fast_info first (fastest)
        data = {'ticker': symbol}

        try:
            fast = ticker.fast_info
            if fast:
                data['current_price'] = safe_decimal(getattr(fast, 'last_price', None))
                data['market_cap'] = safe_decimal(getattr(fast, 'market_cap', None))
                data['volume'] = int(getattr(fast, 'last_volume', 0) or 0)
                data['fifty_day_average'] = safe_decimal(getattr(fast, 'fifty_day_average', None))
                data['two_hundred_day_average'] = safe_decimal(getattr(fast, 'two_hundred_day_average', None))
        except:
            pass

        # Get full info if needed
        if not data.get('current_price'):
            try:
                info = ticker.info
                if info and len(info) > 3:
                    data['current_price'] = safe_decimal(
                        info.get('regularMarketPrice') or
                        info.get('currentPrice') or
                        info.get('previousClose')
                    )
                    data['market_cap'] = safe_decimal(info.get('marketCap'))
                    data['volume'] = int(info.get('volume') or info.get('regularMarketVolume') or 0)
                    data['company_name'] = info.get('longName') or info.get('shortName')
                    data['sector'] = info.get('sector')
                    data['industry'] = info.get('industry')
                    data['pe_ratio'] = safe_decimal(info.get('trailingPE'))
                    data['dividend_yield'] = safe_decimal(info.get('dividendYield'))
                    data['week_52_high'] = safe_decimal(info.get('fiftyTwoWeekHigh'))
                    data['week_52_low'] = safe_decimal(info.get('fiftyTwoWeekLow'))
                    data['avg_volume_3mon'] = int(info.get('averageVolume') or 0)
            except:
                pass

        # Calculate change from history
        if data.get('current_price'):
            try:
                hist = ticker.history(period="2d", interval="1d")
                if hist is not None and len(hist) >= 2:
                    prev_close = hist['Close'].iloc[-2]
                    curr_close = hist['Close'].iloc[-1]
                    data['price_change_today'] = safe_decimal(curr_close - prev_close)
                    if prev_close and prev_close != 0:
                        data['change_percent'] = safe_decimal(
                            ((curr_close - prev_close) / prev_close) * 100
                        )
            except:
                pass

        if proxy and data.get('current_price'):
            mark_proxy_success(proxy)
            return data
        elif data.get('current_price'):
            return data

        if proxy:
            mark_proxy_failure(proxy)
        return None

    except Exception as e:
        if proxy:
            mark_proxy_failure(proxy)
        return None

def batch_fetch_fast_info(symbols, proxy=None, timeout=5):
    """Batch fetch using individual fast_info calls in parallel - faster than full info."""
    results = {}
    if not symbols:
        return results

    def fetch_single_fast(sym):
        try:
            session = create_session(proxy, timeout)
            ticker = yf.Ticker(sym.replace('.', '-'), session=session)
            fast = ticker.fast_info
            if fast and hasattr(fast, 'last_price') and fast.last_price:
                return {
                    'ticker': sym,
                    'current_price': safe_decimal(fast.last_price),
                    'volume': int(getattr(fast, 'last_volume', 0) or 0),
                    'market_cap': safe_decimal(getattr(fast, 'market_cap', None)),
                }
        except:
            pass
        return None

    with ThreadPoolExecutor(max_workers=min(len(symbols), 100)) as executor:
        futures = {executor.submit(fetch_single_fast, sym): sym for sym in symbols}
        for future in as_completed(futures):
            sym = futures[future]
            try:
                data = future.result(timeout=timeout + 1)
                if data:
                    results[sym] = data
            except:
                pass

    return results

def process_batch(symbols, proxies, timeout, fast_mode=False):
    """Process a batch of symbols using batch download."""
    if not symbols:
        return []

    proxy = get_healthy_proxy(proxies) if proxies else None

    if fast_mode:
        # Ultra-fast: batch download only
        results = batch_download_fast(symbols, proxy, timeout)
        return list(results.values())
    else:
        # Full mode: batch download + fast_info fallback for failed symbols
        results = batch_download_fast(symbols, proxy, timeout)

        # Get fast_info for symbols that failed batch download
        failed = [s for s in symbols if s not in results]
        if failed:
            proxy = get_healthy_proxy(proxies) if proxies else None
            fast_results = batch_fetch_fast_info(failed, proxy, timeout)
            results.update(fast_results)

        return list(results.values())

def run_ultra_fast_update(args):
    """Main update function optimized for speed."""
    global shutdown_flag

    logger.info("=" * 70)
    logger.info("ULTRA-FAST STOCK RETRIEVAL - TARGET: 50+ tickers/second")
    logger.info("=" * 70)

    # Market hours check
    if not args.ignore_market_hours:
        now_et = datetime.now(EASTERN_TZ)
        current_hhmm = now_et.strftime("%H:%M")
        if now_et.weekday() >= 5 or not (MARKET_OPEN <= current_hhmm < MARKET_CLOSE):
            logger.info(f"Outside market hours ({now_et.strftime('%H:%M %Z')}). Use -ignore-market-hours to override.")
            return []

    # Load symbols
    symbols = load_symbols(args.test, args.max_symbols)
    if not symbols:
        logger.error("No symbols loaded!")
        return []

    logger.info(f"Processing {len(symbols)} symbols")
    logger.info(f"Threads: {args.threads}, Batch size: {args.batch_size}, Fast mode: {args.fast}")

    # Load proxies
    proxies = []
    if not args.noproxy:
        proxies = load_proxies(args.proxy_file)

    # Split into batches
    batches = []
    for i in range(0, len(symbols), args.batch_size):
        batches.append(symbols[i:i + args.batch_size])

    logger.info(f"Created {len(batches)} batches of ~{args.batch_size} symbols")

    start_time = time.time()
    all_results = []
    completed = 0
    failed = 0

    # Process batches concurrently
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {
            executor.submit(process_batch, batch, proxies, args.timeout, args.fast): i
            for i, batch in enumerate(batches)
        }

        for future in as_completed(futures):
            if shutdown_flag:
                break

            batch_idx = futures[future]
            try:
                results = future.result(timeout=args.timeout * 2)
                all_results.extend(results)
                completed += len(results)
                failed += args.batch_size - len(results)
            except Exception as e:
                logger.debug(f"Batch {batch_idx} error: {e}")
                failed += args.batch_size

            # Progress every 10 batches
            if (batch_idx + 1) % 10 == 0:
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                logger.info(f"Progress: {completed}/{len(symbols)} ({rate:.1f} tickers/sec)")

    elapsed = time.time() - start_time
    rate = len(symbols) / elapsed if elapsed > 0 else 0

    # Results summary
    logger.info("=" * 70)
    logger.info("RESULTS")
    logger.info("=" * 70)
    logger.info(f"Total symbols: {len(symbols)}")
    logger.info(f"Successful: {len(all_results)}")
    logger.info(f"Failed: {len(symbols) - len(all_results)}")
    logger.info(f"Success rate: {len(all_results)/len(symbols)*100:.1f}%")
    logger.info(f"Time: {elapsed:.2f}s")
    logger.info(f"Rate: {rate:.2f} tickers/second")

    if rate >= 50:
        logger.info("TARGET ACHIEVED: 50+ tickers/second!")
    elif rate >= 30:
        logger.info("Good performance: 30+ tickers/second")
    else:
        logger.info(f"Performance below target. Consider: more threads, larger batches")

    # Proxy stats
    if proxies:
        blocked = sum(1 for p in proxies if proxy_health[p]["blocked"])
        logger.info(f"Proxy health: {len(proxies) - blocked}/{len(proxies)} healthy")

    # Save to database
    if args.save_to_db and all_results:
        if ensure_django_initialized():
            db_lock = threading.Lock()
            saved = 0
            for data in all_results:
                if not data.get('ticker'):
                    continue
                try:
                    with db_lock:
                        # Remove non-model fields
                        db_data = {k: v for k, v in data.items()
                                  if k not in ['valuation', 'shares_outstanding']}
                        stock, _ = Stock.objects.update_or_create(
                            ticker=data['ticker'],
                            defaults=db_data
                        )
                        if data.get('current_price'):
                            StockPrice.objects.create(stock=stock, price=data['current_price'])
                        saved += 1
                except Exception as e:
                    logger.debug(f"DB save error {data.get('ticker')}: {e}")
            logger.info(f"Saved {saved} stocks to database")

    # Output file
    if args.output and all_results:
        try:
            # Convert Decimals for JSON
            def serialize(obj):
                if isinstance(obj, Decimal):
                    return float(obj)
                return str(obj)

            with open(args.output, 'w') as f:
                json.dump({
                    'success': True,
                    'count': len(all_results),
                    'rate': rate,
                    'data': all_results
                }, f, default=serialize, indent=2)
            logger.info(f"Wrote {len(all_results)} results to {args.output}")
        except Exception as e:
            logger.error(f"Failed to write output: {e}")

    logger.info("=" * 70)
    return all_results

def main():
    args = parse_arguments()

    logger.info("Configuration:")
    logger.info(f"  Threads: {args.threads}")
    logger.info(f"  Batch size: {args.batch_size}")
    logger.info(f"  Timeout: {args.timeout}s")
    logger.info(f"  Fast mode: {args.fast}")
    logger.info(f"  Use proxies: {not args.noproxy}")

    results = run_ultra_fast_update(args)

    if results:
        logger.info(f"Completed with {len(results)} results")
    else:
        logger.warning("No results returned")

if __name__ == "__main__":
    main()
