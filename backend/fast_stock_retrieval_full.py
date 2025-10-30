#!/usr/bin/env python3
"""
Ultra-fast NYSE & NASDAQ retrieval script.

Key features:
- Refreshes the combined ticker universe directly from the official NASDAQ and NYSE sources
  before each run (with resilient fallbacks to the NASDAQ Trader "otherlisted" feed).
- Fetches real-time quote snapshots for the entire US common equity universe (NYSE + NASDAQ)
  using Yahoo Finance batched quote endpoint with aggressive proxy rotation.
- Falls back to yfinance's historical download API for any symbols missing from the first pass
  to drive completion rate above 95% of all tickers.
- Computes data-quality metrics targeting 97% non-null coverage on core numeric fields.
- Emits JSON/CSV artifacts compatible with the previous fast stock retrieval exports while
  logging detailed performance telemetry.

Usage example:
    cd backend
    python fast_stock_retrieval_full.py --threads 32 --output data/fast_full.json --output-csv data/fast_full.csv

Requirements:
    - requests (and optionally curl_cffi.requests for better HTTP/2 performance)
    - pandas
    - yfinance (already used across the project)

The script is designed to finish end-to-end in under 3 minutes with a healthy proxy list.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd
import requests

try:  # Prefer curl_cffi for HTTP/2 support & lower latency when available
    from curl_cffi import requests as cf_requests  # type: ignore
except Exception:  # pragma: no cover - fallback when curl_cffi is missing
    cf_requests = None  # type: ignore

import yfinance as yf

# ---------------------------------------------------------------------------
# Path bootstrap so we can reuse utilities defined at repository root
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

try:
    from fast_stock_scanner import StockScanner  # type: ignore
except Exception:  # pragma: no cover
    StockScanner = None  # type: ignore


# ---------------------------------------------------------------------------
# Configuration defaults
# ---------------------------------------------------------------------------

DEFAULT_THREADS = 28
DEFAULT_TIMEOUT = 6.0
DEFAULT_BATCH_SIZE = 60
FALLBACK_BATCH_SIZE = 15
MAX_RETRY_PASSES = 3

CORE_NUMERIC_KEYS = [
    "current_price",
    "volume",
    "avg_volume_3mon",
    "market_cap",
    "days_low",
    "days_high",
    "week_52_low",
    "week_52_high",
    "change_percent",
    "dvav",
]

TICKER_BAD_SUFFIXES = ("W", "WS", "WTS", "U", "UN", "RT", "R", "PRA", "PRB", "PRC")

NASDAQ_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
OTHER_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
NYSE_PRIMARY_CSV = "https://www.nyse.com/publicdocs/nyse/data/NYSEListed.csv"
NYSE_SECONDARY_CSV = "https://www.nyse.com/publicdocs/nyse/listed/NYSEListed.csv"


# ---------------------------------------------------------------------------
# Helper dataclasses / utilities
# ---------------------------------------------------------------------------


@dataclass
class RetrievalStats:
    total_symbols: int
    quote_hits: int
    fallback_hits: int
    duration_seconds: float
    null_or_zero_pct: float
    success_rate_pct: float


def _now_ts() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _decimal_to_float(value: Any) -> Optional[float]:
    if isinstance(value, Decimal):
        try:
            return float(value)
        except Exception:
            return None
    if isinstance(value, (int, float)):
        if math.isfinite(float(value)):
            return float(value)
        return None
    return None


def _safe_decimal(value: Any) -> Optional[Decimal]:
    if value is None:
        return None
    try:
        if isinstance(value, (int, float)):
            if math.isfinite(float(value)):
                return Decimal(str(value))
            return None
        return Decimal(str(value))
    except Exception:
        return None


def _is_standard_symbol(sym: str) -> bool:
    if not sym:
        return False
    if any(ch in sym for ch in {"^", "=", " ", "/", "\\", "*", "&"}):
        return False
    if sym.startswith("$"):
        return False
    for suffix in TICKER_BAD_SUFFIXES:
        if sym.endswith(suffix):
            return False
    return True


def _normalize_symbol(sym: str) -> str:
    return sym.strip().upper()


def _normalize_for_yahoo(sym: str) -> str:
    """Convert exchange-specific class delimiters to Yahoo format."""
    sym = sym.strip().upper()
    if not sym:
        return sym
    # NYSE/AMEX class shares use "." while Yahoo expects "-"
    if "." in sym:
        return sym.replace(".", "-")
    return sym


# ---------------------------------------------------------------------------
# Proxy management
# ---------------------------------------------------------------------------


def load_proxies(proxy_file: Path) -> List[str]:
    try:
        with proxy_file.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        if isinstance(payload, dict):
            for key in ("proxies", "working_proxies"):
                data = payload.get(key)
                if isinstance(data, list):
                    return [p.strip() for p in data if isinstance(p, str) and p.strip()]
            return [str(v).strip() for v in payload.values() if isinstance(v, str) and v.strip()]
        if isinstance(payload, list):
            return [str(v).strip() for v in payload if isinstance(v, str) and v.strip()]
    except FileNotFoundError:
        print(f"[WARN] Proxy file not found: {proxy_file}")
    except Exception as exc:
        print(f"[WARN] Failed to load proxies: {exc}")
    return []


def _choose_proxy(idx: int, proxies: Sequence[str]) -> Optional[str]:
    if not proxies:
        return None
    return proxies[idx % len(proxies)]


def _init_yahoo_session(proxy: Optional[str] = None) -> Tuple[requests.Session, Optional[str]]:
    try:
        sess = cf_requests.Session() if cf_requests is not None else requests.Session()
    except Exception:  # pragma: no cover
        sess = requests.Session()

    if proxy:
        sess.proxies = {"http": proxy, "https": proxy}

    sess.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/127.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }
    )

    crumb: Optional[str] = None
    try:
        sess.get("https://finance.yahoo.com", timeout=3)
        resp = sess.get("https://query1.finance.yahoo.com/v1/test/getcrumb", timeout=3)
        if resp.status_code == 200:
            crumb_txt = (resp.text or "").strip()
            crumb = crumb_txt or None
    except Exception:
        crumb = None

    return sess, crumb


# ---------------------------------------------------------------------------
# Official ticker universe refresh
# ---------------------------------------------------------------------------


def _parse_pipe_file(data: str) -> List[List[str]]:
    lines = [line.strip() for line in data.splitlines() if line.strip()]
    if not lines or len(lines) <= 2:
        return []
    rows: List[List[str]] = []
    for line in lines[1:]:
        if line.startswith("File Creation Time"):
            break
        parts = line.split("|")
        rows.append(parts)
    return rows


def fetch_nasdaq_symbols(session: requests.Session, timeout: float = 6.0) -> List[str]:
    response = session.get(NASDAQ_LISTED_URL, timeout=timeout)
    response.raise_for_status()
    rows = _parse_pipe_file(response.text)
    symbols: List[str] = []
    for parts in rows:
        if len(parts) < 8:
            continue
        symbol, _name, _market, test_issue, financial_status, _lot, etf_flag, next_shares = parts[:8]
        if test_issue.upper() == "Y" or etf_flag.upper() == "Y" or next_shares.upper() == "Y":
            continue
        if financial_status.upper() == "D":  # Delinquent
            continue
        sym = _normalize_symbol(symbol)
        if _is_standard_symbol(sym):
            symbols.append(sym)
    return symbols


def fetch_otherlisted(session: requests.Session, timeout: float = 6.0) -> List[Dict[str, str]]:
    response = session.get(OTHER_LISTED_URL, timeout=timeout)
    response.raise_for_status()
    rows = _parse_pipe_file(response.text)
    payload: List[Dict[str, str]] = []
    for parts in rows:
        if len(parts) < 8:
            continue
        payload.append(
            {
                "symbol": parts[0].strip(),
                "exchange": parts[2].strip(),
                "etf": parts[4].strip(),
                "test_issue": parts[6].strip(),
            }
        )
    return payload


def fetch_nyse_symbols(session: requests.Session, timeout: float = 6.0) -> Tuple[List[str], str]:
    """Fetch NYSE common shares from official CSV, fallback to otherlisted feed.

    Returns a tuple of (symbols, source_description).
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.nyse.com/listings_directory/stock",
        "Accept": "text/csv,application/csv,application/octet-stream;q=0.9,*/*;q=0.8",
    }

    for url in (NYSE_PRIMARY_CSV, NYSE_SECONDARY_CSV):
        try:
            resp = session.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()
            text = resp.text
            if "Symbol" not in text.splitlines()[0]:
                continue
            reader = csv.DictReader(io.StringIO(text))
            symbols: List[str] = []
            for row in reader:
                sym = row.get("Symbol") or row.get("Ticker") or row.get("SYMBOL")
                if not sym:
                    continue
                sym_norm = _normalize_symbol(sym)
                if not _is_standard_symbol(sym_norm):
                    continue
                # Filter non-common shares via optional columns when available
                if row.get("ETF", "N").upper() == "Y":
                    continue
                if row.get("Test Issue", "N").upper() == "Y":
                    continue
                symbols.append(sym_norm)
            if len(symbols) >= 1500:  # sanity check for NYSE universe
                return sorted(set(symbols)), url
        except Exception:
            continue

    # Fallback: derive NYSE symbols from otherlisted feed (Exchange == 'N')
    try:
        derived = []
        for record in fetch_otherlisted(session, timeout=timeout):
            sym = _normalize_symbol(record.get("symbol", ""))
            if not sym:
                continue
            if record.get("exchange", "").upper() != "N":
                continue
            if record.get("etf", "N").upper() == "Y":
                continue
            if record.get("test_issue", "N").upper() == "Y":
                continue
            if not _is_standard_symbol(sym):
                continue
            derived.append(sym)
        if derived:
            return sorted(set(derived)), "nasdaqtrader_otherlisted_fallback"
    except Exception:
        pass

    return [], "unavailable"


def build_combined_universe(
    nasdaq_symbols: Sequence[str],
    nyse_symbols: Sequence[str],
) -> List[str]:
    seen = set()
    combined: List[str] = []
    for sym in list(nasdaq_symbols) + list(nyse_symbols):
        norm = _normalize_symbol(sym)
        if not norm or norm in seen:
            continue
        if not _is_standard_symbol(norm):
            continue
        seen.add(norm)
        combined.append(norm)
    return combined


def write_combined_file(symbols: Sequence[str], output_dir: Path) -> Path:
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = output_dir / f"combined_tickers_{timestamp}.py"
    output_dir.mkdir(parents=True, exist_ok=True)
    with filename.open("w", encoding="utf-8") as fh:
        fh.write("COMBINED_TICKERS = [\n")
        for sym in symbols:
            fh.write(f"    \"{sym}\",\n")
        fh.write("]\n")
    return filename


# ---------------------------------------------------------------------------
# Quote retrieval & enrichment
# ---------------------------------------------------------------------------


def _build_rows_from_quotes(quotes: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    rows: Dict[str, Dict[str, Any]] = {}
    for symbol, payload in quotes.items():
        try:
            price = payload.get("regularMarketPrice")
            volume = payload.get("regularMarketVolume")
            avg_vol = payload.get("averageDailyVolume3Month")
            day_low = payload.get("regularMarketDayLow")
            day_high = payload.get("regularMarketDayHigh")
            market_cap = payload.get("marketCap")
            wk_low = payload.get("fiftyTwoWeekLow")
            wk_high = payload.get("fiftyTwoWeekHigh")
            change_pct = payload.get("regularMarketChangePercent")
            company_name = payload.get("longName") or payload.get("shortName") or symbol
            exchange = payload.get("fullExchangeName") or payload.get("exchange") or "NYSE/NASDAQ"

            days_range = ""
            if day_low is not None and day_high is not None:
                try:
                    days_range = f"{float(day_low):.2f} - {float(day_high):.2f}"
                except Exception:
                    days_range = ""

            dvav = None
            try:
                if volume and avg_vol and float(avg_vol) != 0:
                    dvav = float(volume) / float(avg_vol)
            except Exception:
                dvav = None

            rows[symbol] = {
                "ticker": symbol,
                "symbol": symbol,
                "company_name": company_name,
                "exchange": exchange,
                "current_price": _safe_decimal(price),
                "days_low": _safe_decimal(day_low),
                "days_high": _safe_decimal(day_high),
                "days_range": days_range,
                "volume": int(volume) if isinstance(volume, (int, float)) else None,
                "volume_today": int(volume) if isinstance(volume, (int, float)) else None,
                "avg_volume_3mon": int(avg_vol) if isinstance(avg_vol, (int, float)) else None,
                "dvav": _safe_decimal(dvav),
                "market_cap": int(market_cap) if isinstance(market_cap, (int, float)) else None,
                "shares_available": None,
                "pe_ratio": _safe_decimal(payload.get("trailingPE")),
                "dividend_yield": _safe_decimal(payload.get("trailingAnnualDividendYield")),
                "one_year_target": _safe_decimal(payload.get("targetMeanPrice")),
                "week_52_low": _safe_decimal(wk_low),
                "week_52_high": _safe_decimal(wk_high),
                "earnings_per_share": _safe_decimal(payload.get("trailingEps")),
                "price_change_today": _safe_decimal(payload.get("regularMarketChange")),
                "price_change_week": None,
                "price_change_month": None,
                "price_change_year": None,
                "change_percent": _safe_decimal(change_pct),
                "bid_price": _safe_decimal(payload.get("bid")),
                "ask_price": _safe_decimal(payload.get("ask")),
                "bid_ask_spread": "",
                "last_updated": _now_ts(),
                "created_at": _now_ts(),
            }
        except Exception:
            continue
    return rows


def _fetch_quote_chunk(
    chunk: Sequence[str],
    proxy: Optional[str],
    timeout: float,
    max_retry: int = 2,
) -> Dict[str, Dict[str, Any]]:
    symbols = ",".join(chunk)
    session, crumb = _init_yahoo_session(proxy)
    params = {"symbols": symbols}
    if crumb:
        params["crumb"] = crumb
    url = "https://query1.finance.yahoo.com/v7/finance/quote"

    for attempt in range(max_retry + 1):
        try:
            resp = session.get(url, params=params, timeout=timeout)
            if resp.status_code != 200:
                # Sleep briefly and retry with per-symbol calls if rate limited
                time.sleep(0.2 * (attempt + 1))
                continue
            data = resp.json()
            result = data.get("quoteResponse", {}).get("result", [])
            out: Dict[str, Dict[str, Any]] = {}
            for item in result or []:
                symbol = (item.get("symbol") or "").upper()
                if symbol:
                    out[symbol] = item
            if out:
                return out
        except Exception:
            time.sleep(0.2 * (attempt + 1))

    # Fallback: attempt granular fetch for each symbol
    granular: Dict[str, Dict[str, Any]] = {}
    for sym in chunk:
        params = {"symbols": sym}
        if crumb:
            params["crumb"] = crumb
        try:
            resp = session.get(url, params=params, timeout=timeout)
            if resp.status_code != 200:
                continue
            data = resp.json()
            result = data.get("quoteResponse", {}).get("result", [])
            if not result:
                continue
            item = result[0]
            symbol = (item.get("symbol") or "").upper()
            if symbol:
                granular[symbol] = item
        except Exception:
            continue
    return granular


def fetch_quotes_parallel(
    symbols: Sequence[str],
    proxies: Sequence[str],
    batch_size: int,
    threads: int,
    timeout: float,
) -> Dict[str, Dict[str, Any]]:
    quotes: Dict[str, Dict[str, Any]] = {}
    chunks = [
        [
            _normalize_for_yahoo(sym)
            for sym in symbols[i : i + batch_size]
        ]
        for i in range(0, len(symbols), batch_size)
    ]

    if not chunks:
        return {}

    with ThreadPoolExecutor(max_workers=min(threads, len(chunks))) as executor:
        futures = []
        for idx, chunk in enumerate(chunks):
            proxy = _choose_proxy(idx, proxies)
            futures.append(executor.submit(_fetch_quote_chunk, chunk, proxy, timeout))
        for fut in as_completed(futures):
            try:
                data = fut.result()
                if data:
                    quotes.update(data)
            except Exception:
                continue
    return quotes


def fallback_yfinance_download(
    missing: Sequence[str],
    threads: int,
    timeout: float,
) -> Dict[str, Dict[str, Any]]:
    if not missing:
        return {}

    if StockScanner is None:
        return {}

    scanner = StockScanner(threads=threads, timeout=int(timeout), use_proxies=False, db_enabled=False)
    chunk_size = 200
    chunks = [missing[i : i + chunk_size] for i in range(0, len(missing), chunk_size)]

    def worker(chunk: Sequence[str]) -> Dict[str, Dict[str, Any]]:
        try:
            data = yf.download(
                tickers=[_normalize_for_yahoo(sym) for sym in chunk],
                period="5d",
                interval="1d",
                group_by="ticker",
                auto_adjust=False,
                progress=False,
                threads=True,
            )
            rows = scanner._build_rows_from_download(data, list(chunk))  # type: ignore[attr-defined]
            return rows
        except Exception:
            return {}

    combined: Dict[str, Dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=min(threads, len(chunks))) as executor:
        futures = [executor.submit(worker, chunk) for chunk in chunks]
        for fut in as_completed(futures):
            try:
                res = fut.result(timeout=timeout + 10)
                if res:
                    combined.update(res)
            except Exception:
                continue
    return combined


def compute_quality_metrics(rows: Iterable[Dict[str, Any]]) -> Dict[str, float]:
    rows = list(rows)
    if not rows:
        return {"null_pct": 100.0, "zero_pct": 100.0, "null_or_zero_pct": 100.0}

    df = pd.DataFrame(rows)
    keep = [c for c in CORE_NUMERIC_KEYS if c in df.columns]
    if not keep:
        return {"null_pct": 0.0, "zero_pct": 0.0, "null_or_zero_pct": 0.0}

    df = df[keep].copy()
    for col in df.columns:
        df[col] = df[col].map(_decimal_to_float)

    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        return {"null_pct": 0.0, "zero_pct": 0.0, "null_or_zero_pct": 0.0}

    numeric_df = df[numeric_cols]
    total_cells = numeric_df.shape[0] * numeric_df.shape[1]
    if total_cells == 0:
        return {"null_pct": 0.0, "zero_pct": 0.0, "null_or_zero_pct": 0.0}

    nulls = int(numeric_df.isna().sum().sum())
    zeros = int((numeric_df == 0).sum().sum())

    null_pct = (nulls / total_cells) * 100.0
    zero_pct = (zeros / total_cells) * 100.0
    null_or_zero_pct = ((nulls + zeros) / total_cells) * 100.0

    return {
        "null_pct": round(null_pct, 2),
        "zero_pct": round(zero_pct, 2),
        "null_or_zero_pct": round(null_or_zero_pct, 2),
    }


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def run_retrieval(args: argparse.Namespace) -> RetrievalStats:
    backend_dir = Path(__file__).resolve().parent
    data_dir = backend_dir / "data"
    combined_dir = data_dir / "combined"
    proxies_path = backend_dir / args.proxy_file

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    if not args.skip_universe_refresh:
        print("[INFO] Refreshing ticker universe from official sources...")
        nasdaq_symbols = fetch_nasdaq_symbols(session, timeout=args.timeout)
        nyse_symbols, nyse_source = fetch_nyse_symbols(session, timeout=args.timeout)
        if not nasdaq_symbols:
            raise RuntimeError("Unable to load NASDAQ symbols from official feed")
        if not nyse_symbols:
            raise RuntimeError("Unable to load NYSE symbols from official feed or fallback")

        combined_symbols = build_combined_universe(nasdaq_symbols, nyse_symbols)
        combined_path = write_combined_file(combined_symbols, combined_dir)
        print(f"[INFO] Wrote combined tickers file with {len(combined_symbols)} symbols -> {combined_path}")
        print(f"[INFO] NYSE source: {nyse_source}")
    else:
        print("[INFO] Skipping ticker universe refresh (using existing combined files)")
        combined_symbols = []

    # Determine symbols to fetch
    if combined_symbols:
        symbols = combined_symbols
    else:
        # load latest combined file if available
        latest = sorted(combined_dir.glob("combined_tickers_*.py"))
        if not latest:
            raise RuntimeError("No combined_tickers_*.py file available; run without --skip-universe-refresh")
        target = latest[-1]
        module_globals: Dict[str, Any] = {}
        with target.open("r", encoding="utf-8") as fh:
            exec(fh.read(), module_globals)
        symbols = module_globals.get("COMBINED_TICKERS", [])
        if not symbols:
            raise RuntimeError(f"COMBINED_TICKERS not defined in {target}")

    print(f"[INFO] Loaded {len(symbols)} symbols for retrieval")

    proxies = []
    if not args.no_proxy:
        proxies = load_proxies(proxies_path)
        if proxies:
            print(f"[INFO] Loaded {len(proxies)} proxies from {proxies_path}")
        else:
            print("[WARN] Proxy usage enabled but no proxies found; continuing without proxies")
    else:
        print("[INFO] Proxy usage disabled via flag")

    start_time = time.time()
    current_symbols = list(symbols)
    hits: Dict[str, Dict[str, Any]] = {}

    base_batch = max(1, args.batch_size)

    for attempt in range(MAX_RETRY_PASSES):
        batch = base_batch if attempt == 0 else max(5, FALLBACK_BATCH_SIZE)
        timeout = args.timeout if attempt == 0 else args.timeout + attempt
        print(f"[INFO] Quote fetch pass {attempt + 1}: {len(current_symbols)} symbols, batch={batch}, timeout={timeout}")
        quotes = fetch_quotes_parallel(current_symbols, proxies, batch, args.threads, timeout)
        rows = _build_rows_from_quotes(quotes)
        hits.update(rows)
        missing = [sym for sym in symbols if sym not in hits]
        if not missing:
            break
        current_symbols = missing
        print(f"[WARN] Pass {attempt + 1} incomplete -> {len(missing)} symbols missing")
        if not missing:
            break

    direct_hits_count = len(hits)

    missing_symbols = [sym for sym in symbols if sym not in hits]
    fallback_hits: Dict[str, Dict[str, Any]] = {}
    if missing_symbols:
        print(f"[INFO] Attempting yfinance fallback for {len(missing_symbols)} symbols")
        fallback_hits = fallback_yfinance_download(missing_symbols, args.threads, args.timeout)
        hits.update(fallback_hits)
        still_missing = [sym for sym in symbols if sym not in hits]
        if still_missing:
            print(f"[WARN] {len(still_missing)} symbols remain missing after fallback")

    duration = time.time() - start_time

    ordered_rows: List[Dict[str, Any]] = []
    for sym in symbols:
        if sym in hits:
            ordered_rows.append(hits[sym])

    quality = compute_quality_metrics(ordered_rows)
    success_rate = (len(ordered_rows) / len(symbols)) * 100.0 if symbols else 0.0

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(
                {
                    "generated_at": _now_ts(),
                    "total": len(symbols),
                    "completed": len(ordered_rows),
                    "success_rate_pct": round(success_rate, 2),
                    "quality": quality,
                    "data": ordered_rows,
                },
                fh,
                default=str,
            )
        print(f"[INFO] Wrote JSON: {out_path}")

    if args.output_csv:
        csv_path = Path(args.output_csv)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = sorted({key for row in ordered_rows for key in row.keys()})
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for row in ordered_rows:
                writer.writerow({k: (v if not isinstance(v, Decimal) else str(v)) for k, v in row.items()})
        print(f"[INFO] Wrote CSV: {csv_path}")

    valid_quality_pct = 100.0 - quality["null_or_zero_pct"]
    if valid_quality_pct < args.min_data_quality_pct:
        raise RuntimeError(
            f"Data quality {valid_quality_pct:.2f}% below target {args.min_data_quality_pct}%"
        )

    if success_rate < args.min_completion_pct:
        raise RuntimeError(
            f"Completion rate {success_rate:.2f}% below target {args.min_completion_pct}%"
        )

    return RetrievalStats(
        total_symbols=len(symbols),
        quote_hits=direct_hits_count,
        fallback_hits=len(fallback_hits),
        duration_seconds=duration,
        null_or_zero_pct=quality["null_or_zero_pct"],
        success_rate_pct=success_rate,
    )


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ultra-fast NYSE/NASDAQ retrieval script")
    parser.add_argument("--threads", type=int, default=DEFAULT_THREADS, help="Number of worker threads")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="Per-request timeout (seconds)")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="Quote batch size")
    parser.add_argument("--no-proxy", action="store_true", help="Disable proxy usage even if available")
    parser.add_argument(
        "--proxy-file",
        type=str,
        default="working_proxies.json",
        help="Relative path to proxy list JSON (within backend directory)",
    )
    parser.add_argument(
        "--skip-universe-refresh",
        action="store_true",
        help="Skip refreshing ticker universe (use latest combined file)",
    )
    parser.add_argument("--output", type=str, default=None, help="Optional JSON output file")
    parser.add_argument("--output-csv", type=str, default=None, help="Optional CSV output file")
    parser.add_argument(
        "--min-completion-pct",
        type=float,
        default=95.0,
        help="Minimum acceptable completion percentage",
    )
    parser.add_argument(
        "--min-data-quality-pct",
        type=float,
        default=97.0,
        help="Minimum acceptable data quality percentage (non-null core numeric values)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    print("[INFO] ultra-fast retrieval starting")
    print(f"[INFO] threads={args.threads} timeout={args.timeout}s batch_size={args.batch_size}")
    stats = run_retrieval(args)
    print("[INFO] Retrieval complete")
    print(f"[INFO] Symbols total        : {stats.total_symbols}")
    print(f"[INFO] Quote hits           : {stats.quote_hits}")
    print(f"[INFO] Fallback hits        : {stats.fallback_hits}")
    print(f"[INFO] Duration             : {stats.duration_seconds:.2f}s")
    print(f"[INFO] Success rate         : {stats.success_rate_pct:.2f}%")
    print(f"[INFO] Null/zero percentage : {stats.null_or_zero_pct:.2f}%")


if __name__ == "__main__":
    main()

