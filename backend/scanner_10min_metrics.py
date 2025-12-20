#!/usr/bin/env python3
"""
10-Minute Volume/Metrics Scanner with Proxy Rotation
=====================================================
Updates volume and other metrics every 10 minutes using proxied batch calls

Features:
- Proxy rotation to bypass rate limits
- Batch downloads for efficiency
- Updates: volume, market_cap, PE ratio, dividend_yield, highs/lows, etc.
- Runs every 10 minutes
- Handles proxy failures gracefully
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
BATCH_SIZE = 100
SCAN_INTERVAL = 600  # 10 minutes
PROXY_FILE = Path(__file__).parent / "http_proxies.txt"
TIMEOUT_PER_BATCH = 30


class MetricsScanner:
    """10-minute metrics scanner with proxy rotation"""

    def __init__(self):
        self.proxies = self.load_proxies()
        self.current_proxy_index = 0
        self.stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'proxy_failures': 0
        }

    def load_proxies(self) -> List[str]:
        """Load HTTP/HTTPS proxies from file"""
        if not PROXY_FILE.exists():
            print(f"[WARNING] Proxy file not found: {PROXY_FILE}")
            print("[WARNING] Running without proxies (may hit rate limits)")
            return []

        proxies = []
        with open(PROXY_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    proxies.append(line)

        print(f"[INFO] Loaded {len(proxies)} proxies from {PROXY_FILE}")
        return proxies

    def get_next_proxy(self) -> Optional[Dict]:
        """Get next proxy in rotation (round-robin)"""
        if not self.proxies:
            return None

        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)

        return {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }

    def fetch_batch_metrics(self, tickers: List[str], retry_count: int = 3) -> Dict:
        """Fetch metrics for a batch of tickers with proxy rotation"""
        batch_str = " ".join(tickers)

        for attempt in range(retry_count):
            proxy_dict = self.get_next_proxy()

            try:
                # Fetch historical data (5 days for volume calculations)
                data = yf.download(
                    batch_str,
                    period="5d",
                    interval="1d",
                    group_by='ticker',
                    auto_adjust=True,
                    prepost=False,
                    threads=True,
                    progress=False,
                    timeout=TIMEOUT_PER_BATCH,
                    proxies=proxy_dict
                )

                # Process each ticker
                results = {}
                for ticker in tickers:
                    try:
                        # Handle single vs multiple tickers
                        if len(tickers) == 1:
                            ticker_data = data
                        else:
                            ticker_data = data[ticker] if ticker in data.columns.levels[0] else None

                        if ticker_data is not None and not ticker_data.empty:
                            latest = ticker_data.iloc[-1]

                            # Fetch additional info (market cap, PE, etc.)
                            try:
                                stock_obj = yf.Ticker(ticker, proxies=proxy_dict)
                                info = stock_obj.info
                            except:
                                info = {}

                            results[ticker] = {
                                'volume': int(latest['Volume']) if pd.notna(latest['Volume']) else None,
                                'days_high': float(latest['High']) if pd.notna(latest['High']) else None,
                                'days_low': float(latest['Low']) if pd.notna(latest['Low']) else None,
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
                        results[ticker] = {'success': False, 'error': str(e)}

                return results

            except Exception as e:
                self.stats['proxy_failures'] += 1
                if attempt < retry_count - 1:
                    # Try next proxy
                    continue
                else:
                    # All retries failed
                    return {ticker: {'success': False, 'error': str(e)} for ticker in tickers}

        return {}

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
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting 10-minute metrics scan")
        print(f"{'='*80}")

        # Get all tickers
        tickers = list(Stock.objects.values_list('ticker', flat=True))
        total_tickers = len(tickers)

        print(f"Total tickers: {total_tickers}")
        print(f"Batch size: {BATCH_SIZE}")
        print(f"Proxies available: {len(self.proxies)}")

        # Reset stats
        self.stats = {
            'total': total_tickers,
            'successful': 0,
            'failed': 0,
            'proxy_failures': 0,
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
            print(f"[PROGRESS] {i}/{total_batches} batches ({progress:.1f}%) | "
                  f"Success: {self.stats['successful']}/{self.stats['total']}")

            # Small delay between batches
            if i < total_batches:
                time.sleep(1)

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
        print(f"Time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
        print(f"Rate: {rate:.1f} tickers/second")
        print(f"Next scan in {SCAN_INTERVAL}s (10 minutes)\n")

    def run_continuous(self):
        """Run scanner continuously every 10 minutes"""
        print("="*80)
        print("10-MINUTE METRICS SCANNER - CONTINUOUS MODE")
        print("="*80)
        print(f"Scan interval: {SCAN_INTERVAL}s (10 minutes)")
        print(f"Batch size: {BATCH_SIZE}")
        print(f"Proxies: {len(self.proxies)}")
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
    scanner = MetricsScanner()
    scanner.run_continuous()


if __name__ == "__main__":
    main()
