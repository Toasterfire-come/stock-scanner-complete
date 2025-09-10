#!/usr/bin/env python3
"""
Database Cleanup Script for Stock Scanner
Removes stocks with no price data and fixes exchange field issues
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import Stock, StockPrice
from django.db.models import Q
from django.utils import timezone
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def cleanup_database():
    """Clean up the stock database"""
    
    logger.info("Starting database cleanup...")
    
    # 1. Fix null exchange values
    logger.info("Fixing null exchange values...")
    null_exchange_count = Stock.objects.filter(exchange__isnull=True).update(exchange='NYSE')
    logger.info(f"Fixed {null_exchange_count} stocks with null exchange values")
    
    # 2. Fix empty exchange values
    empty_exchange_count = Stock.objects.filter(exchange='').update(exchange='NYSE')
    logger.info(f"Fixed {empty_exchange_count} stocks with empty exchange values")
    
    # 3. Remove stocks with no price data and no volume (likely delisted)
    logger.info("Identifying stocks with no trading data...")
    
    # Count stocks with no price data
    no_price_stocks = Stock.objects.filter(
        Q(current_price__isnull=True) | Q(current_price=0)
    ).filter(
        Q(volume__isnull=True) | Q(volume=0)
    )
    
    no_price_count = no_price_stocks.count()
    logger.info(f"Found {no_price_count} stocks with no price or volume data")
    
    # Show some examples
    if no_price_count > 0:
        logger.info("Examples of stocks to be removed:")
        for stock in no_price_stocks[:10]:
            logger.info(f"  {stock.ticker}: {stock.company_name} - Price: {stock.current_price}, Volume: {stock.volume}")
    
    # 4. Count total stocks before cleanup
    total_before = Stock.objects.count()
    logger.info(f"Total stocks before cleanup: {total_before}")
    
    # 5. Remove stocks with no data (uncomment to actually delete)
    # deleted_count = no_price_stocks.delete()[0]
    # logger.info(f"Removed {deleted_count} stocks with no trading data")
    
    # 6. Clean up orphaned StockPrice records
    logger.info("Cleaning up orphaned stock price records...")
    orphaned_prices = StockPrice.objects.filter(stock__isnull=True)
    orphaned_count = orphaned_prices.count()
    if orphaned_count > 0:
        # orphaned_prices.delete()
        logger.info(f"Found {orphaned_count} orphaned price records (not deleted)")
    else:
        logger.info("No orphaned price records found")
    
    # 7. Report exchange distribution
    logger.info("Exchange distribution:")
    from django.db.models import Count
    exchanges = Stock.objects.values('exchange').annotate(count=Count('exchange')).order_by('-count')
    for exc in exchanges:
        logger.info(f"  {exc['exchange']}: {exc['count']} stocks")
    
    # 8. Report stocks with actual data
    stocks_with_data = Stock.objects.exclude(
        Q(current_price__isnull=True) | Q(current_price=0)
    ).count()
    logger.info(f"Stocks with price data: {stocks_with_data}")
    
    stocks_with_volume = Stock.objects.exclude(
        Q(volume__isnull=True) | Q(volume=0)
    ).count()
    logger.info(f"Stocks with volume data: {stocks_with_volume}")
    
    logger.info("Database cleanup analysis complete!")
    logger.info("To actually delete stocks with no data, uncomment the deletion line in the script")

if __name__ == "__main__":
    cleanup_database()