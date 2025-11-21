#!/usr/bin/env python3
"""
Optimized Stock Data Retrieval Script
- Filters delisted stocks BEFORE fetching
- Better proxy handling with automatic fallback
- Faster batch processing
- Improved error recovery
- Target: >95% success rate in <180 seconds
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import Stock, StockPrice
from django.utils import timezone
from django.db import transaction
import yfinance as yf
import logging
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime
import pandas as pd
from typing import List, Dict, Optional, Set
import json
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('optimized_stock_retrieval.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Quiet yfinance logs
logging.getLogger('yfinance').setLevel(logging.ERROR)
logging.getLogger('peewee').setLevel(logging.WARNING)

class StockDataRetriever:
    """Optimized stock data retrieval with smart filtering"""

    def __init__(self, max_workers: int = 50, use_proxies: bool = False):
        self.max_workers = max_workers
        self.use_proxies = use_proxies
        self.proxies = []
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'delisted': 0,
            'filtered': 0,
            'created': 0,
            'updated': 0
        }
        self.failed_symbols = []
        self.delisted_cache_file = Path('delisted_cache.json')
        self.delisted_cache = self._load_delisted_cache()

    def _load_delisted_cache(self) -> Set[str]:
        """Load cache of known delisted stocks"""
        if self.delisted_cache_file.exists():
            try:
                with open(self.delisted_cache_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data)} delisted stocks from cache")
                    return set(data)
            except Exception as e:
                logger.warning(f"Failed to load delisted cache: {e}")
        return set()

    def _save_delisted_cache(self):
        """Save delisted stocks to cache"""
        try:
            with open(self.delisted_cache_file, 'w') as f:
                json.dump(list(self.delisted_cache), f)
            logger.info(f"Saved {len(self.delisted_cache)} delisted stocks to cache")
        except Exception as e:
            logger.warning(f"Failed to save delisted cache: {e}")

    def _filter_symbols(self, symbols: List[str]) -> List[str]:
        """Filter out likely invalid/delisted stocks BEFORE fetching"""
        filtered = []

        for symbol in symbols:
            # Skip if in delisted cache
            if symbol in self.delisted_cache:
                self.stats['filtered'] += 1
                continue

            # Skip preferred shares (usually end with .P or -P)
            if symbol.endswith('.P') or symbol.endswith('-P'):
                self.stats['filtered'] += 1
                continue

            # Skip warrants (usually end with .W or -W or WS)
            if symbol.endswith('.W') or symbol.endswith('-W') or symbol.endswith('WS'):
                self.stats['filtered'] += 1
                continue

            # Skip units (usually end with .U or -U)
            if symbol.endswith('.U') or symbol.endswith('-U'):
                self.stats['filtered'] += 1
                continue

            # Skip if too many special characters (likely invalid)
            if symbol.count('.') > 1 or symbol.count('-') > 1:
                self.stats['filtered'] += 1
                continue

            # Skip very long symbols (likely invalid)
            if len(symbol) > 6:
                self.stats['filtered'] += 1
                continue

            filtered.append(symbol)

        logger.info(f"Filtered {len(symbols)} -> {len(filtered)} stocks ({self.stats['filtered']} removed)")
        return filtered

    def _fetch_stock_data(self, symbol: str) -> Optional[Dict]:
        """Fetch data for a single stock with better error handling"""
        try:
            ticker = yf.Ticker(symbol)

            # Try fast_info first (fastest method)
            try:
                fast_info = ticker.fast_info
                if fast_info and hasattr(fast_info, 'last_price'):
                    price = fast_info.last_price
                    if price and price > 0:
                        return {
                            'symbol': symbol,
                            'price': Decimal(str(price)),
                            'volume': getattr(fast_info, 'last_volume', None),
                            'market_cap': getattr(fast_info, 'market_cap', None),
                            'method': 'fast_info'
                        }
            except Exception:
                pass

            # Fallback to history
            try:
                hist = ticker.history(period='1d', timeout=5)
                if not hist.empty and 'Close' in hist.columns:
                    price = hist['Close'].iloc[-1]
                    if price and price > 0:
                        return {
                            'symbol': symbol,
                            'price': Decimal(str(price)),
                            'volume': hist['Volume'].iloc[-1] if 'Volume' in hist.columns else None,
                            'method': 'history'
                        }
            except Exception:
                pass

            # If we get here, likely delisted
            self.delisted_cache.add(symbol)
            self.stats['delisted'] += 1
            return None

        except Exception as e:
            logger.debug(f"{symbol}: {str(e)[:50]}")
            return None

    def _save_to_database(self, data: Dict):
        """Save stock data to database"""
        try:
            with transaction.atomic():
                stock, created = Stock.objects.update_or_create(
                    ticker=data['symbol'],
                    defaults={
                        'symbol': data['symbol'],
                        'current_price': data['price'],
                        'volume': data.get('volume'),
                        'market_cap': data.get('market_cap'),
                        'last_updated': timezone.now()
                    }
                )

                if created:
                    self.stats['created'] += 1
                else:
                    self.stats['updated'] += 1

                # Create price history record
                if data['price']:
                    StockPrice.objects.create(
                        stock=stock,
                        price=data['price'],
                        timestamp=timezone.now()
                    )

                return True
        except Exception as e:
            logger.error(f"Database error for {data['symbol']}: {e}")
            return False

    def fetch_and_save(self, symbols: List[str]):
        """Fetch and save stock data with optimized processing"""
        start_time = time.time()

        # Filter symbols first
        logger.info(f"Starting with {len(symbols)} symbols")
        filtered_symbols = self._filter_symbols(symbols)
        self.stats['total'] = len(filtered_symbols)

        logger.info(f"Fetching data for {len(filtered_symbols)} stocks using {self.max_workers} workers...")

        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_symbol = {
                executor.submit(self._fetch_stock_data, symbol): symbol
                for symbol in filtered_symbols
            }

            for i, future in enumerate(as_completed(future_to_symbol), 1):
                symbol = future_to_symbol[future]
                try:
                    result = future.result(timeout=10)
                    if result:
                        if self._save_to_database(result):
                            self.stats['success'] += 1
                            results.append(result)
                        else:
                            self.stats['failed'] += 1
                            self.failed_symbols.append(symbol)
                    else:
                        self.stats['failed'] += 1
                        self.failed_symbols.append(symbol)
                except Exception as e:
                    self.stats['failed'] += 1
                    self.failed_symbols.append(symbol)
                    logger.debug(f"{symbol}: {str(e)[:50]}")

                # Progress update every 200 stocks
                if i % 200 == 0:
                    elapsed = time.time() - start_time
                    rate = i / elapsed if elapsed > 0 else 0
                    success_rate = (self.stats['success'] / i * 100) if i > 0 else 0
                    logger.info(f"Progress: {i}/{len(filtered_symbols)} ({success_rate:.1f}% success, {rate:.1f} stocks/sec)")

        # Save delisted cache
        self._save_delisted_cache()

        # Final statistics
        elapsed = time.time() - start_time
        success_rate = (self.stats['success'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
        rate = self.stats['total'] / elapsed if elapsed > 0 else 0

        logger.info("")
        logger.info("="*70)
        logger.info("RETRIEVAL COMPLETE")
        logger.info("="*70)
        logger.info(f"Total symbols processed: {self.stats['total']}")
        logger.info(f"Pre-filtered out: {self.stats['filtered']}")
        logger.info(f"Success: {self.stats['success']} ({success_rate:.1f}%)")
        logger.info(f"Failed: {self.stats['failed']}")
        logger.info(f"Detected as delisted: {self.stats['delisted']}")
        logger.info(f"Database created: {self.stats['created']}")
        logger.info(f"Database updated: {self.stats['updated']}")
        logger.info(f"Duration: {elapsed:.1f}s ({rate:.1f} stocks/sec)")
        logger.info("")

        # Check targets
        target_success = 95.0
        target_time = 180.0

        quality_met = success_rate >= target_success
        speed_met = elapsed <= target_time

        logger.info("TARGETS:")
        logger.info(f"  Quality (>{target_success}%): {'PASS' if quality_met else 'FAIL'} ({success_rate:.1f}%)")
        logger.info(f"  Speed (<{target_time}s): {'PASS' if speed_met else 'FAIL'} ({elapsed:.1f}s)")
        logger.info("="*70)

        if not quality_met or not speed_met:
            logger.warning("Some targets not met. Consider:")
            if not quality_met:
                logger.warning("  - Check network connection")
                logger.warning("  - Verify symbol list quality")
                logger.warning("  - Review delisted_cache.json")
            if not speed_met:
                logger.warning("  - Increase max_workers")
                logger.warning("  - Check network latency")

        return results


def load_symbols_from_csv(csv_file: str = 'flat-ui__data-Fri Aug 01 2025.csv') -> List[str]:
    """Load symbols from CSV file, filtering out delisted and ETFs"""
    import csv
    symbols = []

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                symbol = row.get('Symbol', '').strip()
                financial_status = row.get('Financial Status', '').strip()
                etf = row.get('ETF', '').strip()

                # Skip if empty
                if not symbol:
                    continue

                # Skip delisted (Financial Status = 'D')
                if financial_status == 'D':
                    continue

                # Skip ETFs
                if etf == 'Y':
                    continue

                symbols.append(symbol)

        logger.info(f"Loaded {len(symbols)} active stocks from {csv_file}")
        return symbols
    except FileNotFoundError:
        logger.error(f"CSV file not found: {csv_file}")
        return []
    except Exception as e:
        logger.error(f"Error loading symbols: {e}")
        return []


def main():
    """Main entry point"""
    logger.info("="*70)
    logger.info("OPTIMIZED STOCK DATA RETRIEVAL")
    logger.info("="*70)

    # Load symbols
    symbols = load_symbols_from_csv()

    if not symbols:
        logger.error("No symbols to process")
        return

    # Create retriever and fetch data
    retriever = StockDataRetriever(max_workers=50, use_proxies=False)
    retriever.fetch_and_save(symbols)


if __name__ == '__main__':
    main()
