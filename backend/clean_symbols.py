#!/usr/bin/env python3
"""
Clean Symbols List
Removes delisted and invalid stocks from the database
"""

import os
import sys
import json
import time
from datetime import datetime
from decimal import Decimal

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from stocks.models import Stock
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_symbol_validity(symbol: str, timeout: int = 3) -> tuple[str, bool, str]:
    """
    Test if a symbol is valid and tradable
    Returns: (symbol, is_valid, reason)
    """
    try:
        ticker = yf.Ticker(symbol.replace('.', '-'))

        # Try to get fast_info (fastest check)
        try:
            fast = ticker.fast_info
            if hasattr(fast, 'last_price') and fast.last_price and fast.last_price > 0:
                return (symbol, True, "Active")
        except:
            pass

        # Fallback: Try to get info
        try:
            info = ticker.info
            if info and len(info) > 5:
                # Check if delisted or invalid
                if info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose'):
                    return (symbol, True, "Active")

                # Check for specific delisting indicators
                if 'delisted' in str(info.get('longName', '')).lower():
                    return (symbol, False, "Delisted")
                if info.get('quoteType') == 'MUTUALFUND' and not info.get('regularMarketPrice'):
                    return (symbol, False, "No price data")
        except:
            pass

        # If we got here, symbol is likely invalid
        return (symbol, False, "No data available")

    except Exception as e:
        return (symbol, False, f"Error: {str(e)[:50]}")


def main():
    print("="*70)
    print("SYMBOL LIST CLEANER")
    print("="*70)
    print("Removing delisted and invalid stocks from database...")
    print("="*70)

    # Get all stocks from database
    all_stocks = Stock.objects.all().order_by('ticker')
    total = all_stocks.count()

    print(f"\nTotal stocks in database: {total}")

    if total == 0:
        print("No stocks found in database!")
        return

    # Extract symbols
    symbols = [stock.ticker for stock in all_stocks]

    print(f"Testing {len(symbols)} symbols for validity...")
    print(f"This will take approximately {len(symbols) * 3 / 60 / 50:.1f} minutes\n")

    # Test symbols in parallel
    valid_symbols = []
    invalid_symbols = []
    tested = 0
    start_time = time.time()

    batch_size = 100
    max_workers = 50  # Moderate concurrency to avoid rate limiting

    for batch_start in range(0, len(symbols), batch_size):
        batch_end = min(batch_start + batch_size, len(symbols))
        batch = symbols[batch_start:batch_end]
        batch_num = (batch_start // batch_size) + 1
        total_batches = (len(symbols) + batch_size - 1) // batch_size

        print(f"[BATCH {batch_num}/{total_batches}] Testing {len(batch)} symbols...")

        batch_valid = []
        batch_invalid = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(test_symbol_validity, sym): sym for sym in batch}

            for future in as_completed(futures):
                symbol, is_valid, reason = future.result()
                tested += 1

                if is_valid:
                    batch_valid.append(symbol)
                    valid_symbols.append(symbol)
                else:
                    batch_invalid.append((symbol, reason))
                    invalid_symbols.append(symbol)

        # Batch progress
        elapsed = time.time() - start_time
        rate = tested / elapsed if elapsed > 0 else 0
        eta = (len(symbols) - tested) / rate / 60 if rate > 0 else 0

        print(f"  Valid: {len(batch_valid)} | Invalid: {len(batch_invalid)}")
        print(f"  Total valid so far: {len(valid_symbols)} ({len(valid_symbols)/tested*100:.1f}%)")
        print(f"  Progress: {tested}/{len(symbols)} ({tested/len(symbols)*100:.1f}%)")
        print(f"  Rate: {rate:.1f} symbols/sec | ETA: {eta:.1f} min")
        print()

        # Brief pause to avoid rate limiting
        time.sleep(0.5)

    # Final results
    elapsed = time.time() - start_time

    print("="*70)
    print("TEST RESULTS")
    print("="*70)
    print(f"Total tested: {len(symbols)}")
    print(f"Valid symbols: {len(valid_symbols)} ({len(valid_symbols)/len(symbols)*100:.1f}%)")
    print(f"Invalid symbols: {len(invalid_symbols)} ({len(invalid_symbols)/len(symbols)*100:.1f}%)")
    print(f"Time elapsed: {elapsed/60:.1f} minutes")
    print(f"Rate: {len(symbols)/elapsed:.1f} symbols/sec")
    print("="*70)

    if len(invalid_symbols) == 0:
        print("\n✅ All symbols are valid! No cleaning needed.")
        return

    # Show sample of invalid symbols
    print(f"\nSample of invalid symbols (first 20):")
    sample_invalid = [(sym, reason) for sym, reason in
                      zip(invalid_symbols[:20], [r for s, r in batch_invalid[:20]])]
    for sym in invalid_symbols[:20]:
        # Find reason
        reason = "Unknown"
        for s, r in batch_invalid:
            if s == sym:
                reason = r
                break
        print(f"  {sym}: {reason}")

    if len(invalid_symbols) > 20:
        print(f"  ... and {len(invalid_symbols) - 20} more")

    # Ask for confirmation
    print(f"\n⚠️  READY TO DELETE {len(invalid_symbols)} invalid stocks from database")
    response = input("Continue? (yes/no): ").strip().lower()

    if response != 'yes':
        print("Aborted. No changes made.")

        # Save invalid symbols list for reference
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tested': len(symbols),
            'valid_count': len(valid_symbols),
            'invalid_count': len(invalid_symbols),
            'invalid_symbols': invalid_symbols
        }

        with open('invalid_symbols_report.json', 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Invalid symbols saved to: invalid_symbols_report.json")
        return

    # Delete invalid stocks
    print(f"\n🗑️  Deleting {len(invalid_symbols)} invalid stocks...")

    deleted_count = 0
    for symbol in invalid_symbols:
        try:
            Stock.objects.filter(ticker=symbol).delete()
            deleted_count += 1
        except Exception as e:
            print(f"  ❌ Failed to delete {symbol}: {e}")

    print(f"\n✅ Successfully deleted {deleted_count} stocks")
    print(f"✅ Remaining stocks: {Stock.objects.count()}")

    # Save cleanup report
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_tested': len(symbols),
        'valid_count': len(valid_symbols),
        'invalid_count': len(invalid_symbols),
        'deleted_count': deleted_count,
        'remaining_count': Stock.objects.count(),
        'invalid_symbols': invalid_symbols
    }

    with open('cleanup_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Cleanup report saved to: cleanup_report.json")

    # Update the combined_tickers list if it exists
    try:
        remaining_tickers = list(Stock.objects.values_list('ticker', flat=True))
        print(f"\n✅ Database now contains {len(remaining_tickers)} valid stocks")
    except Exception as e:
        print(f"\n⚠️  Could not update ticker list: {e}")


if __name__ == "__main__":
    main()
