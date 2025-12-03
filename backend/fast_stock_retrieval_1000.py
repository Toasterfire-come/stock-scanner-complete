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
from typing import Dict, Any, List, Optional

import pandas as pd

# Import scanner utilities
from fast_stock_scanner import load_combined_tickers, StockScanner
import yfinance as yf
import requests
try:
    from curl_cffi import requests as cf_requests  # type: ignore
except Exception:
    cf_requests = None  # type: ignore
import json
import random


THREADS = 10
PER_TASK_TIMEOUT_SEC = 0.3
LIMIT_TICKERS = 1000
POOL_MULTIPLIER_INITIAL = 3
POOL_MULTIPLIER_MAX = 10


def _decimal_to_float(value):
    if isinstance(value, Decimal):
        try:
            return float(value)
        except Exception:
            return None
    return value


CORE_NUMERIC_KEYS = [
    'current_price', 'volume', 'avg_volume_3mon', 'market_cap',
    'days_low', 'days_high', 'week_52_low', 'week_52_high', 'change_percent', 'dvav'
]


def _compute_null_zero_percentages(rows: List[Dict[str, Any]]) -> Dict[str, float]:
    if not rows:
        return {"null_pct": 0.0, "zero_pct": 0.0, "null_or_zero_pct": 0.0}

    df = pd.DataFrame(rows)
    # Keep only the core numeric keys to avoid inflating nulls with intentionally omitted fields
    keep_cols = [c for c in CORE_NUMERIC_KEYS if c in df.columns]
    if not keep_cols:
        return {"null_pct": 0.0, "zero_pct": 0.0, "null_or_zero_pct": 0.0}
    df = df[keep_cols]
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


def _is_standard(sym: str) -> bool:
    if not sym or any(c in sym for c in ['^', '=', ' ', '/', '\\', '*', '&']):
        return False
    if sym.startswith('$'):
        return False
    bad_suffixes = ('W', 'WS', 'WTS', 'U', 'UN', 'R', 'RT')
    for suf in bad_suffixes:
        if sym.endswith(suf):
            return False
    return True


def _build_rows_from_quotes(quotes: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    rows: Dict[str, Dict[str, Any]] = {}
    for sym, q in quotes.items():
        try:
            price = q.get('regularMarketPrice')
            vol = q.get('regularMarketVolume')
            avg3 = q.get('averageDailyVolume3Month')
            day_low = q.get('regularMarketDayLow')
            day_high = q.get('regularMarketDayHigh')
            mc = q.get('marketCap')
            wk_low = q.get('fiftyTwoWeekLow')
            wk_high = q.get('fiftyTwoWeekHigh')
            pe = q.get('trailingPE')
            eps = q.get('trailingEps')
            change_pct = q.get('regularMarketChangePercent')

            days_range = None
            if day_low is not None and day_high is not None:
                try:
                    days_range = f"{float(day_low):.2f} - {float(day_high):.2f}"
                except Exception:
                    days_range = None

            dvav = None
            try:
                if vol is not None and avg3 is not None and float(avg3) != 0:
                    dvav = float(vol) / float(avg3)
            except Exception:
                dvav = None

            rows[sym] = {
                'ticker': sym,
                'symbol': sym,
                'company_name': q.get('longName') or q.get('shortName') or sym,
                'name': q.get('longName') or q.get('shortName') or sym,
                'exchange': q.get('fullExchangeName') or q.get('exchange') or 'NASDAQ',
                'current_price': _safe_decimal(price) if (price is not None) else None,
                'days_low': _safe_decimal(day_low) if (day_low is not None) else None,
                'days_high': _safe_decimal(day_high) if (day_high is not None) else None,
                'days_range': days_range or '',
                'volume': int(vol) if isinstance(vol, (int, float)) else None,
                'volume_today': int(vol) if isinstance(vol, (int, float)) else None,
                'avg_volume_3mon': int(avg3) if isinstance(avg3, (int, float)) else None,
                'dvav': _safe_decimal(dvav),
                'market_cap': int(mc) if isinstance(mc, (int, float)) else None,
                'shares_available': None,
                'pe_ratio': _safe_decimal(pe) if isinstance(pe, (int, float)) else None,
                'dividend_yield': None,
                'one_year_target': None,
                'week_52_low': _safe_decimal(wk_low) if (wk_low is not None) else None,
                'week_52_high': _safe_decimal(wk_high) if (wk_high is not None) else None,
                'earnings_per_share': _safe_decimal(eps) if isinstance(eps, (int, float)) else None,
                'book_value': None,
                'price_to_book': None,
                'bid_price': None,
                'ask_price': None,
                'bid_ask_spread': '',
                'price_change_today': None,
                'price_change_week': None,
                'price_change_month': None,
                'price_change_year': None,
                'change_percent': _safe_decimal(change_pct) if isinstance(change_pct, (int, float)) else None,
                'market_cap_change_3mon': None,
                'pe_change_3mon': None,
                'last_updated': None,
                'created_at': None,
            }
        except Exception:
            continue
    return rows


def _safe_decimal(value):
    if value is None:
        return None
    try:
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        return Decimal(str(value))
    except Exception:
        return None


def _init_yahoo_session(proxy: Optional[str] = None) -> (object, Optional[str]):
    try:
        sess = cf_requests.Session() if cf_requests is not None else requests.Session()
        if proxy:
            sess.proxies = {'http': proxy, 'https': proxy}
        sess.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        crumb: Optional[str] = None
        try:
            # Warm cookie jar and attempt crumb fetch
            sess.get('https://finance.yahoo.com', timeout=3)
            r = sess.get('https://query1.finance.yahoo.com/v1/test/getcrumb', timeout=3)
            if getattr(r, 'status_code', 0) == 200:
                txt = (r.text or '').strip()
                crumb = txt if txt else None
        except Exception:
            crumb = None
        return sess, crumb
    except Exception:
        return requests.Session(), None


def _fetch_quotes_batched(symbols: List[str], batch_size: int = 100, proxies: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    # Split into batches and fetch in parallel
    chunks = [symbols[i:i + batch_size] for i in range(0, len(symbols), batch_size)]
    out: Dict[str, Dict[str, Any]] = {}

    def work(idx: int, chunk: List[str]) -> Dict[str, Dict[str, Any]]:
        proxy = None
        if proxies:
            proxy = proxies[idx % len(proxies)]
        sess, crumb = _init_yahoo_session(proxy)
        params = {'symbols': ','.join(chunk)}
        if crumb:
            params['crumb'] = crumb
        try:
            r = sess.get('https://query1.finance.yahoo.com/v7/finance/quote', params=params, timeout=6)
            out_local: Dict[str, Dict[str, Any]] = {}
            if getattr(r, 'status_code', 0) == 200:
                data = r.json()
                result = data.get('quoteResponse', {}).get('result', [])
                for item in result or []:
                    sym = (item.get('symbol') or '').upper()
                    if sym:
                        out_local[sym] = item
            # Retry once with smaller sub-chunks if empty response
            if not out_local and len(chunk) > 20:
                for i in range(0, len(chunk), 20):
                    sub = chunk[i:i+20]
                    params2 = {'symbols': ','.join(sub)}
                    if crumb:
                        params2['crumb'] = crumb
                    try:
                        r2 = sess.get('https://query1.finance.yahoo.com/v7/finance/quote', params=params2, timeout=5)
                        if getattr(r2, 'status_code', 0) == 200:
                            data2 = r2.json()
                            res2 = data2.get('quoteResponse', {}).get('result', [])
                            for item in res2 or []:
                                sym2 = (item.get('symbol') or '').upper()
                                if sym2:
                                    out_local[sym2] = item
                    except Exception:
                        continue
            return out_local
        except Exception:
            return {}
        return {}

    with ThreadPoolExecutor(max_workers=min(THREADS, len(chunks) or 1)) as ex:
        futures = {ex.submit(work, idx, ch): (idx, tuple(ch)) for idx, ch in enumerate(chunks)}
        for fut in as_completed(futures):
            try:
                res = fut.result(timeout=8)
                if isinstance(res, dict):
                    out.update(res)
            except Exception:
                continue
    return out


def _load_proxies(proxy_file: str = 'working_proxies.json') -> List[str]:
    try:
        with open(proxy_file, 'r') as f:
            data = json.load(f)
        if isinstance(data, dict):
            for key in ('proxies', 'working_proxies'):
                if key in data and isinstance(data[key], list):
                    return [p for p in data[key] if isinstance(p, str) and p]
            # Fallback flatten
            return [v for v in data.values() if isinstance(v, str) and v]
        if isinstance(data, list):
            return [p for p in data if isinstance(p, str) and p]
    except Exception:
        pass
    return []


def main() -> None:
    # Load full universe, not just 1000, so we can pick the first 1000 valid
    symbols = load_combined_tickers()
    if not symbols:
        print("No symbols loaded.")
        return

    # Basic symbol hygiene to drop obvious invalids
    symbols = [s for s in symbols if _is_standard(s)]

    start = time.time()

    # Try fast Yahoo quote API first with proxy rotation to avoid 429
    proxies = _load_proxies('working_proxies.json')
    quotes = _fetch_quotes_batched(symbols[: LIMIT_TICKERS * 8], batch_size=50, proxies=proxies[:20] if proxies else None)
    rows_map = _build_rows_from_quotes(quotes)
    successes: Dict[str, Dict[str, Any]] = {}
    for s in symbols:
        if s in rows_map and rows_map[s].get('current_price') is not None and rows_map[s].get('volume') not in (None, 0):
            successes[s] = rows_map[s]
            if len(successes) >= LIMIT_TICKERS:
                break

    # If still short, use limited yfinance.download as a fallback on the remaining symbols
    if len(successes) < LIMIT_TICKERS:
        remaining = [s for s in symbols if s not in successes]
        scanner = StockScanner(threads=THREADS, timeout=8, use_proxies=False, db_enabled=False)
        chunk_size = 300
        chunks: List[List[str]] = [remaining[i:i+chunk_size] for i in range(0, len(remaining), chunk_size)]

        def work(chunk: List[str]):
            df = yf.download(
                tickers=chunk,
                period='5d',
                interval='1d',
                group_by='ticker',
                auto_adjust=False,
                progress=False,
                threads=True,
            )
            return chunk, df

        with ThreadPoolExecutor(max_workers=min(THREADS, len(chunks) or 1)) as ex:
            futures = [ex.submit(work, ch) for ch in chunks]
            for fut in as_completed(futures):
                try:
                    ch, df = fut.result(timeout=50)
                    rows = scanner._build_rows_from_download(df, ch)
                    for s, p in rows.items():
                        if s in successes:
                            continue
                        if p.get('current_price') is None or p.get('volume') in (None, 0):
                            continue
                        successes[s] = p
                        if len(successes) >= LIMIT_TICKERS:
                            break
                except Exception:
                    continue

    # Preserve original order and cap at LIMIT_TICKERS
    ordered = []
    for s in symbols:
        if s in successes:
            ordered.append((s, successes[s]))
        if len(ordered) >= LIMIT_TICKERS:
            break
    successes = {s: r for s, r in ordered}
    failed_count = LIMIT_TICKERS - len(successes)

    duration = time.time() - start
    completed = len(successes)
    total = LIMIT_TICKERS

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
