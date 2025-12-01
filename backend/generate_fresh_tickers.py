#!/usr/bin/env python3
"""
Fresh Ticker List Generator
Downloads and combines NASDAQ and NYSE tickers from official sources
Filters out invalid tickers (test issues, delisted, ETFs optionally)
"""

import os
import csv
from datetime import datetime
from typing import List, Set

def load_nasdaq_tickers(filepath: str, include_etfs: bool = False) -> Set[str]:
    """
    Load NASDAQ tickers from nasdaqlisted.txt
    Format: Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares
    """
    tickers = set()

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Skip header and footer
    for line in lines[1:]:
        if line.startswith('File Creation Time'):
            break

        parts = line.strip().split('|')
        if len(parts) < 7:
            continue

        symbol = parts[0].strip()
        test_issue = parts[3].strip()
        financial_status = parts[4].strip()
        is_etf = parts[6].strip()

        # Skip empty symbols
        if not symbol:
            continue

        # Skip test issues
        if test_issue == 'Y':
            continue

        # Skip delisted (Financial Status = 'D')
        if financial_status == 'D':
            continue

        # Optionally skip ETFs
        if not include_etfs and is_etf == 'Y':
            continue

        tickers.add(symbol)

    return tickers


def load_nyse_tickers(filepath: str, include_etfs: bool = False) -> Set[str]:
    """
    Load NYSE/AMEX/other tickers from otherlisted.txt
    Format: ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot Size|Test Issue|NASDAQ Symbol
    """
    tickers = set()

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Skip header and footer
    for line in lines[1:]:
        if line.startswith('File Creation Time'):
            break

        parts = line.strip().split('|')
        if len(parts) < 7:
            continue

        symbol = parts[0].strip()
        is_etf = parts[4].strip()
        test_issue = parts[6].strip()

        # Skip empty symbols
        if not symbol:
            continue

        # Skip test issues
        if test_issue == 'Y':
            continue

        # Optionally skip ETFs
        if not include_etfs and is_etf == 'Y':
            continue

        tickers.add(symbol)

    return tickers


def combine_and_save_tickers(nasdaq_file: str, nyse_file: str,
                            output_py: str, output_csv: str,
                            include_etfs: bool = False):
    """Combine NASDAQ and NYSE tickers and save to Python and CSV files"""

    print("Loading NASDAQ tickers...")
    nasdaq = load_nasdaq_tickers(nasdaq_file, include_etfs)
    print(f"  Loaded {len(nasdaq)} NASDAQ tickers")

    print("Loading NYSE/Other tickers...")
    nyse = load_nyse_tickers(nyse_file, include_etfs)
    print(f"  Loaded {len(nyse)} NYSE/Other tickers")

    # Combine and sort
    all_tickers = sorted(nasdaq | nyse)
    print(f"\nTotal unique tickers: {len(all_tickers)}")
    print(f"  NASDAQ only: {len(nasdaq - nyse)}")
    print(f"  NYSE only: {len(nyse - nasdaq)}")
    print(f"  Both: {len(nasdaq & nyse)}")

    # Save to Python file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(output_py, 'w') as f:
        f.write(f'"""\n')
        f.write(f'Combined NASDAQ + NYSE Ticker List\n')
        f.write(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write(f'Total tickers: {len(all_tickers)}\n')
        f.write(f'Include ETFs: {include_etfs}\n')
        f.write(f'"""\n\n')
        f.write(f'COMBINED_TICKERS = [\n')
        for ticker in all_tickers:
            f.write(f'    "{ticker}",\n')
        f.write(f']\n')

    print(f"\n✓ Saved Python file: {output_py}")

    # Save to CSV file
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Symbol', 'Source'])
        for ticker in all_tickers:
            if ticker in nasdaq and ticker in nyse:
                source = 'BOTH'
            elif ticker in nasdaq:
                source = 'NASDAQ'
            else:
                source = 'NYSE'
            writer.writerow([ticker, source])

    print(f"✓ Saved CSV file: {output_csv}")

    return all_tickers


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate combined ticker list')
    parser.add_argument('--include-etfs', action='store_true',
                       help='Include ETFs in the list')
    parser.add_argument('--nasdaq-file', default='data/nasdaq_latest.txt',
                       help='NASDAQ ticker file')
    parser.add_argument('--nyse-file', default='data/nyse_latest.txt',
                       help='NYSE ticker file')
    parser.add_argument('--output-py', default=None,
                       help='Output Python file')
    parser.add_argument('--output-csv', default=None,
                       help='Output CSV file')

    args = parser.parse_args()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if not args.output_py:
        args.output_py = f'data/combined_tickers_{timestamp}.py'

    if not args.output_csv:
        args.output_csv = f'data/combined_tickers_{timestamp}.csv'

    print("=" * 70)
    print("FRESH TICKER LIST GENERATOR")
    print("=" * 70)

    tickers = combine_and_save_tickers(
        args.nasdaq_file,
        args.nyse_file,
        args.output_py,
        args.output_csv,
        args.include_etfs
    )

    print(f"\n✅ Generated fresh ticker list with {len(tickers)} tickers")
    print("=" * 70)
