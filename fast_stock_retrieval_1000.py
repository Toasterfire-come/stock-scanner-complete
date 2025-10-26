#!/usr/bin/env python3
"""
Fast stock retrieval (limited):
- Processes exactly 1000 tickers from the combined NASDAQ universe
- Runs on 10 threads
- Enforces a per-ticker max timeout of 0.3 seconds
- Prints runtime, runtime x10.5, completed vs failed counts
- Prints percentage of null or zero values across numeric fields in the results

Note: Uses fast path from fast_stock_scanner without DB writes and without proxies.
"""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from decimal import Decimal
from typing import Dict, Any, List

import pandas as pd

# Import scanner utilities
from fast_stock_scanner import load_combined_tickers, StockScanner


THREADS = 10
PER_TASK_TIMEOUT_SEC = 0.3
LIMIT_TICKERS = 1000


def _decimal_to_float(value):
    if isinstance(value, Decimal):
        try:
            return float(value)
        except Exception:
            return None
    return value


def _compute_null_zero_percentages(rows: List[Dict[str, Any]]) -> Dict[str, float]:
    if not rows:
        return {"null_pct": 0.0, "zero_pct": 0.0, "null_or_zero_pct": 0.0}

    df = pd.DataFrame(rows)
    # Coerce Decimal to float for numeric analysis
    for col in df.columns:
        df[col] = df[col].map(_decimal_to_float)

    # Keep only numeric columns for zero analysis
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        return {"null_pct": 0.0, "zero_pct": 0.0, "null_or_zero_pct": 0.0}

    numeric_df = df[numeric_cols]
    total_numeric_cells = numeric_df.shape[0] * numeric_df.shape[1]
    if total_numeric_cells == 0:
        return {"null_pct": 0.0, "zero_pct": 0.0, "null_or_zero_pct": 0.0}

    null_count = int(numeric_df.isna().sum().sum())
    zero_count = int((numeric_df == 0).sum().sum())

    null_pct = (null_count / total_numeric_cells) * 100.0
    zero_pct = (zero_count / total_numeric_cells) * 100.0
    null_or_zero_pct = ((null_count + zero_count) / total_numeric_cells) * 100.0

    return {
        "null_pct": round(null_pct, 2),
        "zero_pct": round(zero_pct, 2),
        "null_or_zero_pct": round(null_or_zero_pct, 2),
    }


def main() -> None:
    symbols = load_combined_tickers()[:LIMIT_TICKERS]
    if not symbols:
        print("No symbols loaded.")
        return

    # Instantiate scanner with DB disabled and proxies off
    scanner = StockScanner(threads=THREADS, timeout=0, use_proxies=False, db_enabled=False)

    start = time.time()
    successes: Dict[str, Dict[str, Any]] = {}
    failed: List[str] = []

    # Run concurrency with enforced per-future timeout
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(scanner._fetch_symbol, sym, i): sym for i, sym in enumerate(symbols)}
        for fut in as_completed(futures):
            s = futures[fut]
            try:
                sym, payload, rate_limited = fut.result(timeout=PER_TASK_TIMEOUT_SEC)
                if payload and not rate_limited:
                    successes[sym] = {k: v for k, v in payload.items() if not str(k).startswith('_')}
                else:
                    failed.append(s)
            except TimeoutError:
                failed.append(s)
            except Exception:
                failed.append(s)

    duration = time.time() - start
    completed = len(successes)
    total = len(symbols)
    failed_count = total - completed

    # Metrics for null/zero
    rows = list(successes.values())
    nz = _compute_null_zero_percentages(rows)

    # Output
    print(f"Run time: {duration:.2f}s")
    print(f"Run time x10.5: {duration * 10.5:.2f}s")
    print(f"Completed: {completed} | Failed: {failed_count}")
    print(f"Null or zero % (numeric fields): {nz['null_or_zero_pct']:.2f}%")


if __name__ == "__main__":
    main()
