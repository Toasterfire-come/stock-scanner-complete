#!/usr/bin/env python
"""Remove delisted and invalid stocks from database"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SECRET_KEY', 'temp-key-for-script')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import Stock

def clean_delisted_stocks():
    """Remove stocks with invalid symbols or known delisted patterns"""
    print("=" * 70)
    print("CLEANING DELISTED STOCKS")
    print("=" * 70)

    # Patterns for delisted/invalid stocks
    invalid_patterns = [
        '.W',  # Warrants
        '.U',  # Units
        '.R',  # Rights
        'W$',  # Warrants ending in W
        'U$',  # Units ending in U
    ]

    # Known delisted stocks from our test
    known_delisted = [
        'LEN.B', 'UHAL.B', 'BH.A', 'BF.A', 'BRK.B', 'AKO.B', 'CRD.B',
        'ALXN', 'CELG', 'BRK.A', 'AGM.A', 'AYRO', 'YORK', 'YORKW',
        'PARA', 'AC', 'NOVA', 'ABLLW', 'BAD'
    ]

    total_deleted = 0

    # Delete known delisted
    for symbol in known_delisted:
        deleted = Stock.objects.filter(symbol=symbol).delete()[0]
        if deleted > 0:
            print(f"[DELETED] {symbol}")
            total_deleted += deleted

    # Delete stocks with invalid patterns
    for pattern in invalid_patterns:
        if pattern.endswith('$'):
            # Ends with pattern
            suffix = pattern[:-1]
            stocks = Stock.objects.filter(symbol__endswith=suffix)
        else:
            # Contains pattern
            stocks = Stock.objects.filter(symbol__contains=pattern)

        count = stocks.count()
        if count > 0:
            print(f"[PATTERN] Deleting {count} stocks matching '{pattern}'")
            stocks.delete()
            total_deleted += count

    # Delete stocks with null or empty prices that haven't been updated in 30 days
    from django.utils import timezone
    from datetime import timedelta

    cutoff_date = timezone.now() - timedelta(days=30)
    old_stocks = Stock.objects.filter(
        last_updated__lt=cutoff_date,
        current_price__isnull=True
    )
    old_count = old_stocks.count()
    if old_count > 0:
        print(f"[OLD] Deleting {old_count} stocks with no price data for 30+ days")
        old_stocks.delete()
        total_deleted += old_count

    print(f"\n[TOTAL] Deleted {total_deleted} invalid/delisted stocks")

    # Final count
    remaining = Stock.objects.count()
    nasdaq = Stock.objects.filter(exchange__startswith='N').count()
    nyse = Stock.objects.filter(exchange='NYSE').count()

    print(f"\nRemaining stocks: {remaining}")
    print(f"  NASDAQ: {nasdaq}")
    print(f"  NYSE: {nyse}")

if __name__ == '__main__':
    clean_delisted_stocks()
