#!/usr/bin/env python3
"""
Daily End-of-Day Scanner
========================

Runs ONCE per day to update heavy calculations and fundamentals.
This includes all expensive API calls that don't need real-time updates.

Target: Complete all 5,193 tickers in <10 minutes with >95% success
Strategy: Use ALL available methods with proper proxy rotation
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, time as dt_time
from pathlib import Path
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")

import django
django.setup()

import yfinance as yf
from django.utils import timezone
from django.db import transaction
from stocks.models import Stock

from stock_retrieval.config import StockRetrievalConfig
from stock_retrieval.ticker_loader import load_combined_tickers
from stock_retrieval.session_factory import ProxyPool

# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# =====================================================
# CONFIGURATION
# =====================================================

class EODConfig:
    """End-of-Day scanner configuration"""

    # Workers - More aggressive since we have all day
    min_workers = 30
    max_workers = 80
    initial_workers = 50

    # Timeouts - Longer since we're getting more data
    request_timeout = 10
    per_symbol_timeout = 15

    # Delays - Moderate for proxy rotation
    min_delay = 0.01  # 10ms
    max_delay = 0.05  # 50ms

    # Progress
    progress_interval = 100

    # Database
    batch_size = 100  # Write in batches

    # Auto-tuning
    auto_tune = True
    tune_interval = 200
    target_success_rate = 0.95

CONFIG = EODConfig()

# =====================================================
# METRICS
# =====================================================

class Metrics:
    """Track scanner performance"""

    def __init__(self):
        self.start_time = time.time()
        self.total_attempted = 0
        self.success = 0
        self.failures = 0
        self.complete_records = 0
        self.partial_records = 0

    @property
    def elapsed(self):
        return time.time() - self.start_time

    @property
    def success_rate(self):
        if self.total_attempted == 0:
            return 0.0
        return self.success / self.total_attempted

    @property
    def throughput(self):
        if self.elapsed == 0:
            return 0.0
        return self.total_attempted / self.elapsed

# =====================================================
# EOD FETCHER
# =====================================================

class EODFetcher:
    """Fetches end-of-day fundamentals and calculations"""

    def __init__(self, use_proxies=False):
        self.metrics = Metrics()
        self.results = []
        self.lock = threading.Lock()

        # Initialize proxy pool if requested
        if use_proxies:
            try:
                logger.info("Initializing proxy pool...")
                config = StockRetrievalConfig()
                self.proxy_pool = ProxyPool.from_config(config)
                logger.info(f"Loaded {len(self.proxy_pool.proxies)} proxies for rotation")
            except Exception as e:
                logger.warning(f"Failed to load proxies: {e}")
                logger.info("Running WITHOUT proxies")
                self.proxy_pool = None
        else:
            self.proxy_pool = None
            logger.info("Running WITHOUT proxies (yfinance handles connections internally)")

    def fetch_eod_data(self, symbol: str) -> Optional[Dict]:
        """
        Fetch all EOD data for a symbol.
        This includes fundamentals, valuations, technicals, etc.
        """

        # Small delay for proxy rotation
        time.sleep(CONFIG.min_delay + (CONFIG.max_delay - CONFIG.min_delay) * self.metrics.total_attempted / 5000)

        try:
            # Let yfinance handle sessions with curl_cffi
            ticker = yf.Ticker(symbol)

            result = {
                'symbol': symbol,
                'last_updated': timezone.now(),
                'method': 'eod'
            }

            # Try to get comprehensive data
            try:
                # Get info (contains most fundamentals)
                info = ticker.info

                # Basic info
                result['market_cap'] = info.get('marketCap')
                result['shares_outstanding'] = info.get('sharesOutstanding')
                result['currency'] = info.get('currency', 'USD')
                result['previous_close'] = info.get('previousClose')

                # 52-week range
                result['fifty_two_week_high'] = info.get('fiftyTwoWeekHigh')
                result['fifty_two_week_low'] = info.get('fiftyTwoWeekLow')

                # Volume
                result['average_volume'] = info.get('averageVolume')
                result['average_volume_10days'] = info.get('averageVolume10days')

                # Target price
                result['target_mean_price'] = info.get('targetMeanPrice')
                result['target_high_price'] = info.get('targetHighPrice')
                result['target_low_price'] = info.get('targetLowPrice')

                # Valuation metrics
                result['pe_ratio'] = info.get('trailingPE')
                result['forward_pe'] = info.get('forwardPE')
                result['peg_ratio'] = info.get('pegRatio')
                result['price_to_book'] = info.get('priceToBook')
                result['enterprise_value'] = info.get('enterpriseValue')
                result['ev_to_revenue'] = info.get('enterpriseToRevenue')
                result['ev_to_ebitda'] = info.get('enterpriseToEbitda')

                # Profitability
                result['profit_margin'] = info.get('profitMargins')
                result['operating_margin'] = info.get('operatingMargins')
                result['return_on_assets'] = info.get('returnOnAssets')
                result['return_on_equity'] = info.get('returnOnEquity')

                # Growth
                result['revenue_growth'] = info.get('revenueGrowth')
                result['earnings_growth'] = info.get('earningsGrowth')
                result['earnings_quarterly_growth'] = info.get('earningsQuarterlyGrowth')

                # Financial health
                result['total_debt'] = info.get('totalDebt')
                result['total_cash'] = info.get('totalCash')
                result['debt_to_equity'] = info.get('debtToEquity')
                result['current_ratio'] = info.get('currentRatio')
                result['quick_ratio'] = info.get('quickRatio')

                # Cash flow
                result['free_cashflow'] = info.get('freeCashflow')
                result['operating_cashflow'] = info.get('operatingCashflow')

                # Dividend
                result['dividend_rate'] = info.get('dividendRate')
                result['dividend_yield'] = info.get('dividendYield')
                result['payout_ratio'] = info.get('payoutRatio')
                result['five_year_avg_dividend_yield'] = info.get('fiveYearAvgDividendYield')

                # EPS
                result['trailing_eps'] = info.get('trailingEps')
                result['forward_eps'] = info.get('forwardEps')

                # Book value
                result['book_value'] = info.get('bookValue')

                # Analyst recommendations
                result['recommendation'] = info.get('recommendationKey')
                result['number_of_analyst_opinions'] = info.get('numberOfAnalystOpinions')

                with self.lock:
                    self.metrics.success += 1
                    if result.get('market_cap') and result.get('pe_ratio'):
                        self.metrics.complete_records += 1
                    else:
                        self.metrics.partial_records += 1

                return result

            except Exception as e:
                # If info fails, try to get at least basic data from fast_info
                try:
                    data = ticker.fast_info
                    result['market_cap'] = getattr(data, 'market_cap', None)
                    result['shares_outstanding'] = getattr(data, 'shares', None)
                    result['currency'] = getattr(data, 'currency', 'USD')
                    result['previous_close'] = getattr(data, 'previous_close', None)
                    result['fifty_two_week_high'] = getattr(data, 'year_high', None)
                    result['fifty_two_week_low'] = getattr(data, 'year_low', None)

                    with self.lock:
                        self.metrics.success += 1
                        self.metrics.partial_records += 1

                    return result

                except:
                    with self.lock:
                        self.metrics.failures += 1
                    return None

        except Exception as e:
            logger.debug(f"Failed to fetch {symbol}: {e}")
            with self.lock:
                self.metrics.failures += 1
            return None

        finally:
            with self.lock:
                self.metrics.total_attempted += 1

    def fetch_all(self, symbols: List[str]) -> List[Dict]:
        """Fetch EOD data for all symbols"""

        total = len(symbols)
        logger.info(f"\nFetching EOD data for {total} tickers...")
        logger.info(f"Workers: {CONFIG.initial_workers}")
        logger.info(f"Target: Complete in <10 minutes with >95% success\n")

        results = []

        with ThreadPoolExecutor(max_workers=CONFIG.initial_workers) as executor:
            futures = {
                executor.submit(self.fetch_eod_data, symbol): symbol
                for symbol in symbols
            }

            for future in as_completed(futures):
                result = future.result()

                if result:
                    results.append(result)

                # Progress
                if self.metrics.total_attempted % CONFIG.progress_interval == 0:
                    progress = self.metrics.total_attempted / total * 100
                    elapsed = self.metrics.elapsed
                    remaining = total - self.metrics.total_attempted
                    eta = (elapsed / self.metrics.total_attempted * remaining) if self.metrics.total_attempted > 0 else 0

                    logger.info(
                        f"[{self.metrics.total_attempted}/{total}] "
                        f"{progress:.1f}% | "
                        f"Success: {self.metrics.success_rate*100:.1f}% | "
                        f"Speed: {self.metrics.throughput:.1f}/s | "
                        f"ETA: {eta/60:.1f}min"
                    )

        return results

# =====================================================
# DATABASE WRITER
# =====================================================

def write_eod_to_database(results: List[Dict]) -> int:
    """Write EOD data to database in batches"""

    logger.info(f"\nWriting {len(results)} EOD records to database...")
    start = time.time()
    written = 0

    try:
        # Write in batches for efficiency
        for i in range(0, len(results), CONFIG.batch_size):
            batch = results[i:i + CONFIG.batch_size]

            with transaction.atomic():
                for result in batch:
                    try:
                        # Map to actual database field names
                        defaults = {
                            # Basic info
                            'market_cap': result.get('market_cap'),
                            'shares_available': result.get('shares_outstanding'),
                            # Note: currency not in model schema

                            # 52-week range
                            'week_52_high': result.get('fifty_two_week_high'),
                            'week_52_low': result.get('fifty_two_week_low'),

                            # Volume
                            'avg_volume_3mon': result.get('average_volume'),

                            # Valuation metrics
                            'pe_ratio': result.get('pe_ratio'),
                            # Note: forward_pe and peg_ratio stored in valuation_json
                            'price_to_book': result.get('price_to_book'),

                            # Dividend
                            'dividend_yield': result.get('dividend_yield'),

                            # Target price
                            'one_year_target': result.get('target_mean_price'),

                            # Earnings
                            'earnings_per_share': result.get('trailing_eps'),
                            'book_value': result.get('book_value'),

                            # Timestamp
                            'last_updated': result['last_updated']
                        }

                        # Store additional metrics in valuation_json
                        valuation_data = {}
                        if result.get('forward_pe'):
                            valuation_data['forward_pe'] = result.get('forward_pe')
                        if result.get('peg_ratio'):
                            valuation_data['peg_ratio'] = result.get('peg_ratio')
                        if result.get('enterprise_value'):
                            valuation_data['enterprise_value'] = result.get('enterprise_value')
                        if result.get('ev_to_revenue'):
                            valuation_data['ev_to_revenue'] = result.get('ev_to_revenue')
                        if result.get('ev_to_ebitda'):
                            valuation_data['ev_to_ebitda'] = result.get('ev_to_ebitda')
                        if result.get('profit_margin'):
                            valuation_data['profit_margin'] = result.get('profit_margin')
                        if result.get('operating_margin'):
                            valuation_data['operating_margin'] = result.get('operating_margin')
                        if result.get('return_on_assets'):
                            valuation_data['return_on_assets'] = result.get('return_on_assets')
                        if result.get('return_on_equity'):
                            valuation_data['return_on_equity'] = result.get('return_on_equity')
                        if result.get('revenue_growth'):
                            valuation_data['revenue_growth'] = result.get('revenue_growth')
                        if result.get('earnings_growth'):
                            valuation_data['earnings_growth'] = result.get('earnings_growth')
                        if result.get('debt_to_equity'):
                            valuation_data['debt_to_equity'] = result.get('debt_to_equity')
                        if result.get('current_ratio'):
                            valuation_data['current_ratio'] = result.get('current_ratio')
                        if result.get('quick_ratio'):
                            valuation_data['quick_ratio'] = result.get('quick_ratio')
                        if result.get('free_cashflow'):
                            valuation_data['free_cashflow'] = result.get('free_cashflow')
                        if result.get('operating_cashflow'):
                            valuation_data['operating_cashflow'] = result.get('operating_cashflow')
                        if result.get('payout_ratio'):
                            valuation_data['payout_ratio'] = result.get('payout_ratio')
                        if result.get('forward_eps'):
                            valuation_data['forward_eps'] = result.get('forward_eps')

                        if valuation_data:
                            defaults['valuation_json'] = valuation_data

                        # Update or create with EOD data
                        Stock.objects.update_or_create(
                            symbol=result['symbol'],
                            defaults=defaults
                        )
                        written += 1
                    except Exception as e:
                        logger.debug(f"Failed to write {result['symbol']}: {e}")

            logger.info(f"Written {written}/{len(results)} records...")

        elapsed = time.time() - start
        logger.info(f"Completed in {elapsed:.2f}s ({written/elapsed:.0f} records/sec)")

        return written

    except Exception as e:
        logger.error(f"Database write failed: {e}")
        return 0

# =====================================================
# MAIN
# =====================================================

def should_run_eod_scan() -> bool:
    """Check if we should run EOD scan (market has closed)"""

    # US market closes at 4:00 PM ET
    # Run EOD scan after 4:30 PM ET to ensure all data is available
    # For now, allow manual running anytime

    return True

def main():
    """Main entry point"""

    logger.info("=" * 70)
    logger.info("DAILY END-OF-DAY SCANNER")
    logger.info("=" * 70)
    logger.info("Updates: Fundamentals, Valuations, Ratios, Technical Indicators")
    logger.info("Frequency: Once per day after market close")
    logger.info("")

    # Check if we should run
    if not should_run_eod_scan():
        logger.info("Market hasn't closed yet. EOD scan should run after 4:30 PM ET.")
        return

    # Load tickers
    logger.info("Loading tickers...")
    config = StockRetrievalConfig()
    result = load_combined_tickers(config)
    tickers = result.tickers
    logger.info(f"Loaded {len(tickers)} tickers\n")

    # Create fetcher
    fetcher = EODFetcher()

    # Fetch all EOD data
    logger.info("=" * 70)
    logger.info("STARTING EOD FETCH")
    logger.info("=" * 70)

    start_time = time.time()
    results = fetcher.fetch_all(tickers)
    fetch_time = time.time() - start_time

    # Results
    logger.info("\n" + "=" * 70)
    logger.info("FETCH COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Runtime: {fetch_time:.2f}s ({fetch_time/60:.2f} min)")
    logger.info(f"Success: {len(results)}/{len(tickers)} ({len(results)/len(tickers)*100:.1f}%)")
    logger.info(f"Throughput: {len(tickers)/fetch_time:.2f} tickers/sec")
    logger.info(f"Complete records: {fetcher.metrics.complete_records}")
    logger.info(f"Partial records: {fetcher.metrics.partial_records}")

    # Write to database
    if results:
        written = write_eod_to_database(results)
        logger.info(f"Database: {written} records written")

    # Save metrics
    metrics = {
        'runtime_seconds': round(fetch_time, 2),
        'runtime_minutes': round(fetch_time / 60, 2),
        'total_attempted': fetcher.metrics.total_attempted,
        'success': fetcher.metrics.success,
        'failures': fetcher.metrics.failures,
        'success_rate': round(fetcher.metrics.success_rate * 100, 2),
        'throughput': round(fetcher.metrics.throughput, 2),
        'complete_records': fetcher.metrics.complete_records,
        'partial_records': fetcher.metrics.partial_records,
        'timestamp': datetime.now().isoformat()
    }

    metrics_file = f"eod_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)

    logger.info(f"\nMetrics saved: {metrics_file}")

    # Final summary
    logger.info("\n" + "=" * 70)
    logger.info("EOD SCAN COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Runtime: {fetch_time/60:.2f} minutes")
    logger.info(f"Success rate: {fetcher.metrics.success_rate*100:.1f}%")
    logger.info("Next scan: Tomorrow after market close")
    logger.info("=" * 70)

if __name__ == "__main__":
    main()
