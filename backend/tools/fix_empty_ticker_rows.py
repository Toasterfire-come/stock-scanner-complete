import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import Stock
from django.db.models import Q


def clean_empty_ticker_rows():
    # Delete stocks with empty or whitespace-only ticker or symbol
    empty_ticker_qs = Stock.objects.filter(Q(ticker__isnull=True) | Q(ticker='') | Q(ticker__regex=r'^\s+$'))
    empty_symbol_qs = Stock.objects.filter(Q(symbol__isnull=True) | Q(symbol='') | Q(symbol__regex=r'^\s+$'))
    count_ticker = empty_ticker_qs.count()
    count_symbol = empty_symbol_qs.count()
    empty_ticker_qs.delete()
    empty_symbol_qs.delete()
    print(f"Deleted {count_ticker} stocks with empty/whitespace ticker.")
    print(f"Deleted {count_symbol} stocks with empty/whitespace symbol.")

    # Check for duplicate tickers
    from django.db.models import Count
    dups = Stock.objects.values('ticker').annotate(count=Count('id')).filter(count__gt=1)
    if dups.exists():
        print("Duplicate tickers found:")
        for dup in dups:
            print(f"Ticker: {dup['ticker']} (Count: {dup['count']})")
    else:
        print("No duplicate tickers found.")

    # Check for nulls in required fields
    null_name = Stock.objects.filter(Q(name__isnull=True) | Q(name=''))
    if null_name.exists():
        print(f"Stocks with null/empty name: {null_name.count()}")
    else:
        print("No stocks with null/empty name.")

if __name__ == "__main__":
    clean_empty_ticker_rows()