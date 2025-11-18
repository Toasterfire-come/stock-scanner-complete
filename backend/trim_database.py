#!/usr/bin/env python
"""Trim database to only NYSE and NASDAQ stocks"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SECRET_KEY', 'temp-key-for-script')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import Stock
from django.db.models import Q

def trim_database():
    """Delete all stocks that are not NYSE or NASDAQ"""
    print("=" * 70)
    print("DATABASE TRIM - NYSE + NASDAQ ONLY")
    print("=" * 70)

    # Get current counts
    total = Stock.objects.count()
    nyse = Stock.objects.filter(exchange='NYSE').count()
    nasdaq = Stock.objects.filter(Q(exchange__startswith='N') & ~Q(exchange='NYSE')).count()

    print(f"\nCurrent Database:")
    print(f"  Total stocks: {total}")
    print(f"  NYSE: {nyse}")
    print(f"  NASDAQ (N*): {nasdaq}")
    print(f"  NYSE + NASDAQ: {nyse + nasdaq}")

    # Find stocks to delete
    other = Stock.objects.exclude(Q(exchange='NYSE') | Q(exchange__startswith='N'))
    other_count = other.count()

    print(f"\nStocks to DELETE: {other_count}")

    if other_count > 0:
        print("\nStocks being deleted:")
        for stock in other[:20]:  # Show first 20
            print(f"  {stock.symbol:8} | {stock.exchange or 'NULL':10} | {stock.name}")

        if other_count > 20:
            print(f"  ... and {other_count - 20} more")

        # Confirm deletion
        response = input(f"\nDelete {other_count} stocks? (yes/no): ")
        if response.lower() == 'yes':
            deleted_count, _ = other.delete()
            print(f"\n[OK] Deleted {deleted_count} stocks")

            # Verify
            new_total = Stock.objects.count()
            print(f"\nDatabase after trim:")
            print(f"  Total stocks: {new_total}")
            print(f"  NYSE: {Stock.objects.filter(exchange='NYSE').count()}")
            print(f"  NASDAQ: {Stock.objects.filter(Q(exchange__startswith='N') & ~Q(exchange='NYSE')).count()}")
            print(f"\n[OK] Database trimmed to NYSE + NASDAQ only")
        else:
            print("\n[X] Deletion cancelled")
    else:
        print("\n[OK] Database already contains only NYSE + NASDAQ stocks")

if __name__ == '__main__':
    trim_database()
