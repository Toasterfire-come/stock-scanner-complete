#!/usr/bin/env python3
"""
Combine and deduplicate NASDAQ and NYSE/AMEX tickers from NASDAQ FTP files.

Inputs:
  - Django/data/nasdaq_only/nasdaqlisted.txt (NASDAQ-listed)
  - Django/data/complete_nasdaq/otherlisted.txt (NYSE/AMEX-listed)

Outputs:
  - Django/data/combined/combined_tickers_<timestamp>.py
    with COMBINED_TICKERS (sorted, unique, uppercase) and TOTAL_TICKERS

Notes:
  - Skips headers and the footer lines (File Creation Time)
  - Skips empty symbols and test issues if detected
  - Keeps ETFs and other instrument types unless explicitly excluded
"""

import os
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]

NASDAQ_FILE = BASE_DIR / 'data' / 'nasdaq_only' / 'nasdaqlisted.txt'
OTHER_FILE = BASE_DIR / 'data' / 'complete_nasdaq' / 'otherlisted.txt'
OUTPUT_DIR = BASE_DIR / 'data' / 'combined'


def iter_symbols_from_pipe_file(path: Path):
    """Yield symbols from a NASDAQ FTP pipe-delimited list file.

    The first column is Symbol. Skip header and footer lines.
    """
    if not path.exists():
        return
    with path.open('r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('Symbol|'):
                continue
            if line.startswith('File Creation Time'):
                break
            # Some files have notes lines starting with '#'
            if line.startswith('#'):
                continue
            parts = line.split('|')
            if not parts:
                continue
            symbol = (parts[0] or '').strip()
            if not symbol or symbol.upper() == 'SYMBOL':
                continue
            # Optional: filter test issues if column present
            # The typical column order has 'Test Issue' near the end with 'Y'/'N'
            # We try to detect and skip when explicitly marked as test
            test_issue = None
            for idx, name in enumerate(('Test Issue', 'TestIssue')):
                # No header row mapping available here; best-effort detection by position
                # If length looks sufficient, NASDAQ list usually has Test Issue at index 5 or 6
                try:
                    if len(parts) >= 7:
                        # Heuristic: often index 5 is Market Category, 6 Test Issue
                        test_issue = parts[6].strip() if parts[6] else None
                except Exception:
                    test_issue = None
            if test_issue and test_issue.upper() == 'Y':
                continue
            yield symbol.upper()


def main():
    symbols = set()

    # NASDAQ-listed
    for sym in iter_symbols_from_pipe_file(NASDAQ_FILE):
        if sym:
            symbols.add(sym)

    # NYSE/AMEX-listed
    for sym in iter_symbols_from_pipe_file(OTHER_FILE):
        if sym:
            symbols.add(sym)

    combined = sorted(symbols)
    total = len(combined)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    out_path = OUTPUT_DIR / f'combined_tickers_{ts}.py'

    header = (
        '#!/usr/bin/env python3\n'
        '"""\n'
        'Combined NASDAQ + NYSE/AMEX ticker list generated from NASDAQ FTP files.\n'
        f'Generated on UTC: {datetime.utcnow().isoformat()}\n'
        f'Total unique tickers: {total}\n'
        'Source files:\n'
        f' - {NASDAQ_FILE}\n'
        f' - {OTHER_FILE}\n'
        '"""\n\n'
    )

    body_prefix = 'COMBINED_TICKERS = [\n'
    body_items = []
    for sym in combined:
        body_items.append(f'    "{sym}",')
    body_suffix = '\n]\n\n'
    meta = f'TOTAL_TICKERS = {total}\n'

    with out_path.open('w', encoding='utf-8') as f:
        f.write(header)
        f.write(body_prefix)
        f.write('\n'.join(body_items))
        f.write(body_suffix)
        f.write(meta)

    print(f"Wrote combined list: {out_path}")
    print(f"Total unique tickers: {total}")


if __name__ == '__main__':
    sys.exit(main())

