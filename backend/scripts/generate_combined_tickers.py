#!/usr/bin/env python3
"""
Generate a cleaned combined tickers list from NASDAQ and OTHERLISTED datasets.

Outputs a Python file backend/data/combined/combined_tickers_<timestamp>.py with COMBINED_TICKERS.

Rules:
- Include only tickers from exchanges NYSE (N), NYSE American (A), NYSE Arca (P), NASDAQ (Q/G/S/Z), Cboe BZX (Z) when appropriate.
- Exclude Test issues and non-standard symbols.
- Exclude tickers with spaces or obvious invalid characters.
- Normalize to uppercase and deduplicate.
"""
import os
import re
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'
NASDAQ_DIR = DATA_DIR / 'nasdaq_only'
COMPLETE_DIR = DATA_DIR / 'complete_nasdaq'
COMBINED_DIR = DATA_DIR / 'combined'


def load_nasdaqlisted(path: Path) -> set[str]:
    tickers: set[str] = set()
    if not path.exists():
        return tickers
    with path.open('r', encoding='utf-8', errors='ignore') as f:
        # Skip header line; pipe-separated
        next(f, None)
        for line in f:
            parts = line.strip().split('|')
            if len(parts) < 8:
                continue
            symbol, name, market_category, test_issue = parts[0], parts[1], parts[2], parts[6]
            if (test_issue or '').upper() == 'Y':
                continue
            if not symbol:
                continue
            if ' ' in symbol or '\t' in symbol:
                continue
            s = symbol.strip().upper()
            # Exclude very odd formats
            if len(s) > 10:
                continue
            tickers.add(s)
    return tickers


def load_otherlisted(path: Path) -> set[str]:
    tickers: set[str] = set()
    if not path.exists():
        return tickers
    with path.open('r', encoding='utf-8', errors='ignore') as f:
        next(f, None)
        for line in f:
            parts = line.strip().split('|')
            if len(parts) < 8:
                continue
            act_symbol, security_name, exch, cqs_symbol, etf, lot_size, test_issue, nasdaq_symbol = parts[:8]
            if (test_issue or '').upper() == 'Y':
                continue
            if not act_symbol:
                continue
            if ' ' in act_symbol or '\t' in act_symbol:
                continue
            s = act_symbol.strip().upper()
            if len(s) > 14:
                continue
            # Keep only primary exchanges N (NYSE), A (AMEX), P (ARCA), Z (Cboe), Q/G/S (NASDAQ)
            if exch not in ('N','A','P','Z','Q','G','S'):
                continue
            tickers.add(s)
    return tickers


def write_output(tickers: list[str], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime('%Y%m%d_%H%M%S')
    out_path = out_dir / f'combined_tickers_{ts}.py'
    with out_path.open('w', encoding='utf-8') as f:
        f.write('COMBINED_TICKERS = [\n')
        for t in tickers:
            f.write(f'    "{t}",\n')
        f.write(']\n')
    return out_path


def main():
    nasdaq_listed = load_nasdaqlisted(NASDAQ_DIR / 'nasdaqlisted.txt')
    other_listed = load_otherlisted(COMPLETE_DIR / 'otherlisted.txt')
    combined = sorted(nasdaq_listed.union(other_listed))
    out_path = write_output(combined, COMBINED_DIR)
    print(f'Wrote {len(combined)} tickers to {out_path}')


if __name__ == '__main__':
    main()

