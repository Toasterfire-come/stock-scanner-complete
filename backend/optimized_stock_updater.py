#!/usr/bin/env python3
"""
Optimized Stock Updater Wrapper for Market Hours Manager
Integrates optimized_stock_retrieval.py with Django database
Runs during market hours with automatic restarts
"""

import os
import sys
import time
import logging
from pathlib import Path

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
sys.path.insert(0, str(Path(__file__).parent.absolute()))

import django
django.setup()

from stocks.models import Stock, StockPrice
from optimized_stock_retrieval import run_optimized_scan, load_combined_tickers
from decimal import Decimal

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Quiet verbose loggers
for name in ('yfinance', 'yfinance.scrapers', 'yfinance.data', 'peewee'):
    logging.getLogger(name).setLevel(logging.ERROR)


def save_to_database(results_dict):
    """Save scan results to Django database"""
    saved_count = 0
    error_count = 0

    for symbol, data in results_dict.items():
        try:
            # Prepare data for Stock model
            stock_data = {
                'ticker': data.get('ticker', symbol),
                'symbol': data.get('symbol', symbol),
                'company_name': data.get('company_name', symbol),
                'name': data.get('name', symbol),
                'exchange': data.get('exchange', 'NASDAQ'),
                'current_price': data.get('current_price'),
                'days_high': data.get('days_high'),
                'days_low': data.get('days_low'),
                'volume': data.get('volume'),
                'market_cap': data.get('market_cap'),
                'shares_available': data.get('shares_available'),
                'avg_volume_3mon': data.get('avg_volume_3mon'),
                'week_52_low': data.get('week_52_low'),
                'week_52_high': data.get('week_52_high'),
                'pe_ratio': data.get('pe_ratio'),
                'dvav': data.get('dvav'),
                'change_percent': data.get('change_percent'),
            }

            # Remove None values
            stock_data = {k: v for k, v in stock_data.items() if v is not None}

            # Update or create stock record
            stock, created = Stock.objects.update_or_create(
                ticker=symbol,
                defaults=stock_data
            )

            # Create price history record if we have a price
            if data.get('current_price'):
                StockPrice.objects.create(
                    stock=stock,
                    price=data['current_price']
                )

            saved_count += 1

        except Exception as e:
            logger.error(f"Failed to save {symbol}: {e}")
            error_count += 1

    logger.info(f"Database save complete: {saved_count} saved, {error_count} errors")
    return saved_count, error_count


def run_scheduled_update(max_symbols=None):
    """Run optimized stock update and save to database"""
    logger.info("=" * 70)
    logger.info("OPTIMIZED STOCK UPDATER - Scheduled Run")
    logger.info("=" * 70)

    # Load symbols
    symbols = load_combined_tickers()

    if max_symbols:
        symbols = symbols[:max_symbols]

    if not symbols:
        logger.error("No symbols to process!")
        return False

    logger.info(f"Processing {len(symbols)} symbols")

    # Run optimized scan with aggressive settings for speed
    # These settings target: 95%+ success, <180s for ~2000 stocks
    result = run_optimized_scan(
        symbols=symbols,
        batch_size=100,      # Optimized batch size
        max_workers=20,       # Parallel workers
        enrich=False         # Disable enrichment for speed
    )

    stats = result['stats']
    logger.info("\n" + "=" * 70)
    logger.info("SCAN RESULTS")
    logger.info("=" * 70)
    logger.info(f"Success Rate:    {stats['success_rate']}%")
    logger.info(f"Elapsed Time:    {stats['elapsed_seconds']}s")
    logger.info(f"Processing Rate: {stats['rate_per_second']} symbols/sec")

    # Check if requirements met
    meets_criteria = stats['success_rate'] >= 95 and stats['elapsed_seconds'] <= 180
    logger.info(f"Meets Criteria:  {'YES' if meets_criteria else 'NO'}")
    logger.info("=" * 70)

    # Save to database
    logger.info("Saving results to database...")
    saved, errors = save_to_database(result['results'])

    logger.info("\n" + "=" * 70)
    logger.info("UPDATE COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Database: {saved} saved, {errors} errors")
    logger.info("=" * 70)

    return meets_criteria


def main():
    """Main entry point for scheduled updates"""
    import argparse

    parser = argparse.ArgumentParser(description='Optimized Stock Updater')
    parser.add_argument('--schedule', action='store_true',
                       help='Run continuously with 3-minute intervals')
    parser.add_argument('--max-symbols', type=int, default=None,
                       help='Limit number of symbols (for testing)')

    args = parser.parse_args()

    if args.schedule:
        logger.info("Starting scheduled mode (3-minute intervals)")
        while True:
            try:
                run_scheduled_update(max_symbols=args.max_symbols)
                logger.info("Waiting 3 minutes before next update...")
                time.sleep(180)  # 3 minutes
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            except Exception as e:
                logger.error(f"Update failed: {e}")
                logger.info("Waiting 3 minutes before retry...")
                time.sleep(180)
    else:
        # Single run
        success = run_scheduled_update(max_symbols=args.max_symbols)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
