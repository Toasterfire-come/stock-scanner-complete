#!/usr/bin/env python3
"""
10-Minute Volume/Metrics Scanner - IMPROVED VERSION
====================================================
Updates volume and other metrics every 10 minutes using proxied batch calls

IMPROVEMENTS:
- Smart retry logic with exponential backoff
- No-proxy fallback for better success rates
- Smaller batch sizes for reliability
- Better error handling and logging
- Separate fetch for price data vs metadata
"""

import os
import sys
import django
import time
import random
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import yfinance as yf
import pandas as pd

# Django setup
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import Stock

# Configuration
BATCH_SIZE = 50  # Reduced from 100 for better reliability
SCAN_INTERVAL = 600  # 10 minutes
PROXY_FILE = Path(__file__).parent / "http_proxies.txt"
TIMEOUT_PER_BATCH = 45  # Increased timeout
MAX_RETRIES = 3
BACKOFF_FACTOR = 2  # Exponential backoff


class ImprovedMetricsScanner:
    """Enhanced 10-minute metrics scanner with better success rate"""

    def __init__(self):
        self.proxies = self.load_proxies()
        self.current_proxy_index = 0
        self.failed_proxies = set()  # Track failed proxies
        self.no_proxy_fallback = True  # Allow running without proxies
        self.stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'proxy_failures': 0,
            'no_proxy_success': 0
        }

    def load_proxies(self) -> List[str]:
        """Load HTTP/HTTPS proxies from file"""
        if not PROXY_FILE.exists():
            print(f"[WARNING] Proxy file not found: {PROXY_FILE}")
            print("[WARNING] Will run without proxies (may hit rate limits)")
            return []

        proxies = []
        with open(PROXY_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    proxies.append(line)

        print(f"[INFO] Loaded {len(proxies)} proxies from {PROXY_FILE}")
        return proxies

    def get_next_proxy(self, skip_failed: bool = True) -> Optional[Dict]:
        """Get next proxy in rotation, skipping known failures"""
        if not self.proxies:
            return None

        # Try up to len(proxies) times to find a working proxy
        attempts = 0
        max_attempts = len(self.proxies)

        while attempts < max_attempts:
            proxy = self.proxies[self.current_proxy_index]
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)

            if skip_failed and proxy in self.failed_proxies:
                attempts += 1
                continue

            return {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }

        # All proxies failed, reset failed set and try again
        if skip_failed and self.failed_proxies:
            print("[WARNING] All proxies failed, resetting failed proxy tracking")
            self.failed_proxies.clear()
            return self.get_next_proxy(skip_failed=False)

        return None

    def fetch_price_data_only(self, tickers: List[str], proxies: Optional[Dict] = None) -> Dict:
        """Fetch just price/volume data (fast, reliable)"""
        batch_str = " ".join(tickers)
        results = {}

        try:
            # Fetch recent data (just 2 days for speed)
            data = yf.download(
                batch_str,
                period="2d",
                interval="1d",
                group_by='ticker',
                auto_adjust=True,
                prepost=False,
                threads=True,
                progress=False,
                timeout=TIMEOUT_PER_BATCH,
                proxies=proxies
            )

            # Process each ticker
            for ticker in tickers:
                try:
                    # Handle single vs multiple tickers
                    if len(tickers) == 1:
                        ticker_data = data
                    else:
                        if ticker not in data.columns.levels[0]:
                            continue
                        ticker_data = data[ticker]

                    if ticker_data is not None and not ticker_data.empty:
                        latest = ticker_data.iloc[-1]

                        results[ticker] = {
                            'volume': int(latest['Volume']) if pd.notna(latest['Volume']) else None,
                            'days_high': float(latest['High']) if pd.notna(latest['High']) else None,
                            'days_low': float(latest['Low']) if pd.notna(latest['Low']) else None,
                            'success': True
                        }

                except Exception as e:
                    results[ticker] = {'success': False, 'error': str(e)}

            return results

        except Exception as e:
            return {ticker: {'success': False, 'error': str(e)} for ticker in tickers}

    def fetch_metadata(self, ticker: str, proxies: Optional[Dict] = None) -> Dict:
        """Fetch metadata (market cap, PE, etc.) for a single ticker"""
        try:
            stock_obj = yf.Ticker(ticker, proxies=proxies)
            info = stock_obj.info

            return {
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                'week_52_high': info.get('fiftyTwoWeekHigh'),
                'week_52_low': info.get('fiftyTwoWeekLow'),
                'avg_volume_3mon': info.get('averageVolume'),
                'bid_price': info.get('bid'),
                'ask_price': info.get('ask'),
                'earnings_per_share': info.get('trailingEps'),
                'book_value': info.get('bookValue'),
                'success': True
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def fetch_batch_metrics(self, tickers: List[str]) -> Dict:
        """
        Fetch metrics for a batch with smart retry logic

        Strategy:
        1. Try with proxy (3 attempts with different proxies)
        2. If all proxies fail, try without proxy
        3. Split batch and retry if still failing
        """
        results = {}

        # Strategy 1: Try with proxies
        if self.proxies:
            for attempt in range(MAX_RETRIES):
                proxy_dict = self.get_next_proxy()

                if proxy_dict:
                    try:
                        batch_results = self.fetch_price_data_only(tickers, proxy_dict)

                        # Check success rate
                        success_count = sum(1 for r in batch_results.values() if r.get('success'))
                        success_rate = success_count / len(tickers) if tickers else 0

                        if success_rate > 0.5:  # At least 50% success
                            results = batch_results
                            break
                        else:
                            # Mark proxy as potentially bad
                            proxy_str = list(proxy_dict.values())[0].replace('http://', '')
                            self.failed_proxies.add(proxy_str)
                            self.stats['proxy_failures'] += 1

                    except Exception as e:
                        # Mark proxy as failed
                        if proxy_dict:
                            proxy_str = list(proxy_dict.values())[0].replace('http://', '')
                            self.failed_proxies.add(proxy_str)
                        self.stats['proxy_failures'] += 1

                        # Wait before retry (exponential backoff)
                        if attempt < MAX_RETRIES - 1:
                            wait_time = BACKOFF_FACTOR ** attempt
                            time.sleep(wait_time)

        # Strategy 2: Try without proxy (fallback)
        if not results and self.no_proxy_fallback:
            try:
                results = self.fetch_price_data_only(tickers, proxies=None)

                success_count = sum(1 for r in results.values() if r.get('success'))
                if success_count > 0:
                    self.stats['no_proxy_success'] += success_count

            except Exception as e:
                pass

        # Strategy 3: Split batch if still failing
        if not results and len(tickers) > 10:
            mid = len(tickers) // 2
            results1 = self.fetch_batch_metrics(tickers[:mid])
            results2 = self.fetch_batch_metrics(tickers[mid:])
            results = {**results1, **results2}

        return results

    def update_database(self, ticker: str, data: Dict) -> bool:
        """Update stock metrics in database"""
        if not data.get('success'):
            return False

        try:
            stock = Stock.objects.get(ticker=ticker)

            # Update all available metrics
            if data.get('volume') is not None:
                stock.volume = data['volume']
            if data.get('days_high'):
                stock.days_high = data['days_high']
            if data.get('days_low'):
                stock.days_low = data['days_low']
            if data.get('market_cap'):
                stock.market_cap = data['market_cap']
            if data.get('pe_ratio'):
                stock.pe_ratio = data['pe_ratio']
            if data.get('dividend_yield'):
                stock.dividend_yield = data['dividend_yield']
            if data.get('week_52_high'):
                stock.week_52_high = data['week_52_high']
            if data.get('week_52_low'):
                stock.week_52_low = data['week_52_low']
            if data.get('avg_volume_3mon'):
                stock.avg_volume_3mon = data['avg_volume_3mon']
            if data.get('bid_price'):
                stock.bid_price = data['bid_price']
            if data.get('ask_price'):
                stock.ask_price = data['ask_price']
            if data.get('earnings_per_share'):
                stock.earnings_per_share = data['earnings_per_share']
            if data.get('book_value'):
                stock.book_value = data['book_value']

            stock.last_updated = datetime.now()
            stock.save()

            return True

        except Stock.DoesNotExist:
            return False
        except Exception as e:
            return False

    def scan_all_tickers(self):
        """Scan all tickers for volume/metrics"""
        print(f"\n{'='*80}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 10-MINUTE METRICS SCAN (IMPROVED)")
        print(f"{'='*80}")

        # Get all tickers
        tickers = list(Stock.objects.values_list('ticker', flat=True))
        total_tickers = len(tickers)

        print(f"Total tickers: {total_tickers}")
        print(f"Batch size: {BATCH_SIZE}")
        print(f"Proxies available: {len(self.proxies)}")
        print(f"Fallback to no-proxy: {self.no_proxy_fallback}")

        # Reset stats
        self.stats = {
            'total': total_tickers,
            'successful': 0,
            'failed': 0,
            'proxy_failures': 0,
            'no_proxy_success': 0,
            'start_time': time.time()
        }

        # Process in batches
        batches = [tickers[i:i+BATCH_SIZE] for i in range(0, total_tickers, BATCH_SIZE)]
        total_batches = len(batches)

        print(f"Total batches: {total_batches}\n")

        for i, batch in enumerate(batches, 1):
            print(f"[BATCH {i}/{total_batches}] Processing {len(batch)} tickers...")

            # Fetch batch metrics
            results = self.fetch_batch_metrics(batch)

            # Update database
            for ticker, data in results.items():
                if self.update_database(ticker, data):
                    self.stats['successful'] += 1
                else:
                    self.stats['failed'] += 1

            # Progress
            progress = (i / total_batches) * 100
            success_rate = (self.stats['successful'] / (i * BATCH_SIZE)) * 100 if i > 0 else 0

            print(f"[PROGRESS] {i}/{total_batches} batches ({progress:.1f}%) | "
                  f"Success: {self.stats['successful']}/{self.stats['total']} ({success_rate:.1f}%)")

            # Small delay between batches
            if i < total_batches:
                time.sleep(2)  # Increased delay for better rate limit handling

        # Final stats
        elapsed = time.time() - self.stats['start_time']
        rate = total_tickers / elapsed if elapsed > 0 else 0
        success_rate = (self.stats['successful'] / total_tickers) * 100 if total_tickers > 0 else 0

        print(f"\n{'='*80}")
        print(f"SCAN COMPLETE")
        print(f"{'='*80}")
        print(f"Total: {total_tickers}")
        print(f"Successful: {self.stats['successful']} ({success_rate:.1f}%)")
        print(f"Failed: {self.stats['failed']}")
        print(f"Proxy failures: {self.stats['proxy_failures']}")
        print(f"No-proxy successes: {self.stats['no_proxy_success']}")
        print(f"Time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
        print(f"Rate: {rate:.1f} tickers/second")
        print(f"Next scan in {SCAN_INTERVAL}s (10 minutes)\n")

    def run_continuous(self):
        """Run scanner continuously every 10 minutes"""
        print("="*80)
        print("10-MINUTE METRICS SCANNER (IMPROVED VERSION)")
        print("="*80)
        print(f"Scan interval: {SCAN_INTERVAL}s (10 minutes)")
        print(f"Batch size: {BATCH_SIZE}")
        print(f"Proxies: {len(self.proxies)}")
        print(f"No-proxy fallback: {self.no_proxy_fallback}")
        print(f"Press Ctrl+C to stop")
        print("="*80)

        while True:
            try:
                self.scan_all_tickers()
                print(f"[SLEEP] Waiting {SCAN_INTERVAL}s until next scan...")
                time.sleep(SCAN_INTERVAL)
            except KeyboardInterrupt:
                print("\n[STOP] Scanner stopped by user")
                break
            except Exception as e:
                print(f"\n[ERROR] Scan failed: {e}")
                print(f"Retrying in {SCAN_INTERVAL}s...")
                time.sleep(SCAN_INTERVAL)


def main():
    scanner = ImprovedMetricsScanner()
    scanner.run_continuous()


if __name__ == "__main__":
    main()
