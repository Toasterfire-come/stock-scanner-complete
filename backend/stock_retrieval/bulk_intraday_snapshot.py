#!/usr/bin/env python3
"""
Bulk Intraday Snapshot Updater (yfinance)
========================================
Goal:
- Pull *all* tickers in DB (~8.5k) as fast as yfinance/Yahoo allows by using
  bulk `yf.download()` calls (chunked) instead of per-ticker `.info`.
- Optional proxy support (process-isolated) to distribute load.
- Best-effort intraday "current price" + volume (from 1m bars).

Reality check:
- Yahoo Finance streaming is event-driven; this script is a *snapshot* puller.
- If Yahoo throttles, this script will auto-split chunks and retry.

Usage examples:
  python3 backend/stock_retrieval/bulk_intraday_snapshot.py
  python3 backend/stock_retrieval/bulk_intraday_snapshot.py --limit 500 --workers 6
  python3 backend/stock_retrieval/bulk_intraday_snapshot.py --chunk-size 250 --workers 10 --use-proxies

Env overrides:
  BULK_SNAPSHOT_LOG_DIR=backend/logs
  BULK_SNAPSHOT_LOG_LEVEL=INFO
"""

from __future__ import annotations

import os
import sys
import time
import json
import math
import argparse
import logging
from logging.handlers import TimedRotatingFileHandler
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd

# Ensure backend package imports work when running as a script
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Django setup (mirror other stock_retrieval scripts)
# This script updates the DB, so it must run in the backend environment (venv/docker).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")
try:
    import django  # noqa: E402
except ModuleNotFoundError as e:  # pragma: no cover
    raise SystemExit(
        "Django is not installed in this Python environment.\n"
        "Run this script inside your backend venv or docker container where backend/requirements.txt is installed.\n"
        f"Original error: {e}"
    )

django.setup()

from django.utils import timezone as django_tz  # noqa: E402
from django.db import transaction  # noqa: E402
from stocks.models import Stock  # noqa: E402

import yfinance as yf  # noqa: E402


def configure_logging() -> logging.Logger:
    log_level = os.getenv("BULK_SNAPSHOT_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, log_level, logging.INFO)

    backend_dir = Path(__file__).resolve().parents[1]
    default_log_dir = backend_dir / "logs"
    log_dir = Path(os.getenv("BULK_SNAPSHOT_LOG_DIR", str(default_log_dir)))
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "bulk_intraday_snapshot.log"

    logger = logging.getLogger("bulk_intraday_snapshot")
    logger.setLevel(level)
    logger.propagate = False

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    if not logger.handlers:
        sh = logging.StreamHandler()
        sh.setLevel(level)
        sh.setFormatter(fmt)

        fh = TimedRotatingFileHandler(
            filename=str(log_file),
            when="midnight",
            interval=1,
            backupCount=int(os.getenv("BULK_SNAPSHOT_LOG_BACKUPS", "7")),
            encoding="utf-8",
        )
        fh.setLevel(level)
        fh.setFormatter(fmt)

        logger.addHandler(sh)
        logger.addHandler(fh)

    # Quiet noisy libs
    for name in ("yfinance", "yfinance.scrapers", "urllib3", "peewee"):
        logging.getLogger(name).setLevel(logging.ERROR)

    logger.info(f"Bulk snapshot log file: {log_file}")
    return logger


logger = configure_logging()

_MP_CFG: Dict[str, Any] = {}


def _init_pool(cfg: Dict[str, Any]) -> None:
    # Called once per worker process.
    global _MP_CFG
    _MP_CFG = cfg


def _mp_worker(job: Tuple[int, List[str], Optional[str]]) -> List["ChunkResult"]:
    # Top-level function so it can be pickled under spawn.
    _, symbols, proxy = job
    return fetch_chunk_snapshot(
        symbols,
        proxy=proxy,
        period=str(_MP_CFG["period"]),
        interval=str(_MP_CFG["interval"]),
        timeout_s=float(_MP_CFG["timeout_s"]),
        retries=int(_MP_CFG["retries"]),
        min_chunk_size=int(_MP_CFG["min_chunk_size"]),
    )


def load_proxies(proxy_file: Path) -> List[str]:
    """
    Load proxies. Supports either:
    - plain text file: host:port per line
    - JSON file: {"proxies": ["http://host:port", ...]} or {"proxies": ["host:port", ...]}
    """
    if not proxy_file.exists():
        logger.warning(f"Proxy file not found: {proxy_file}")
        return []

    try:
        if proxy_file.suffix.lower() == ".json":
            payload = json.loads(proxy_file.read_text())
            raw = payload.get("proxies", [])
            proxies: List[str] = []
            for p in raw:
                p = str(p).strip()
                if not p:
                    continue
                proxies.append(p)
            return proxies
        else:
            proxies = []
            for line in proxy_file.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                proxies.append(line)
            return proxies
    except Exception as e:
        logger.warning(f"Failed reading proxy file {proxy_file}: {e}")
        return []

def verify_proxies_for_yahoo(proxies: List[str], *, timeout_s: float, max_keep: int) -> List[str]:
    """
    Best-effort proxy verification for Yahoo endpoints.
    Keeps only proxies that can fetch a tiny Yahoo quote payload quickly.
    """
    if not proxies:
        return []

    import requests
    from concurrent.futures import ThreadPoolExecutor, as_completed

    url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=AAPL"
    headers = {"User-Agent": "Mozilla/5.0"}

    def test(p: str) -> Optional[Tuple[float, str]]:
        try:
            t0 = time.time()
            r = requests.get(url, headers=headers, proxies={"http": p, "https": p}, timeout=timeout_s)
            if r.status_code == 200 and "quoteResponse" in r.text:
                return (time.time() - t0), p
        except Exception:
            return None
        return None

    good: List[Tuple[float, str]] = []
    workers = min(60, max(10, len(proxies)))
    logger.info(f"Verifying proxies (workers={workers}, timeout={timeout_s}s, target_keep={max_keep})...")

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(test, p) for p in proxies]
        for fut in as_completed(futs):
            res = fut.result()
            if not res:
                continue
            good.append(res)
            if len(good) >= max_keep:
                break

    good.sort(key=lambda x: x[0])
    verified = [p for _, p in good]
    logger.info(f"Verified {len(verified)}/{len(proxies)} proxies")
    return verified


def normalize_proxy(proxy: str) -> str:
    proxy = proxy.strip()
    if not proxy:
        return proxy
    if proxy.startswith("http://") or proxy.startswith("https://"):
        return proxy
    return f"http://{proxy}"


def set_process_proxy(proxy: Optional[str]) -> None:
    """
    Configure yfinance to use a proxy in *this process*.
    This is intentionally process-scoped (we use multiprocessing to avoid global races).
    """
    if not proxy:
        # Best effort to clear
        try:
            if hasattr(yf, "set_config"):
                yf.set_config(proxy=None)
        except Exception:
            pass
        os.environ.pop("HTTP_PROXY", None)
        os.environ.pop("HTTPS_PROXY", None)
        return

    proxy_url = normalize_proxy(proxy)
    proxy_dict = {"http": proxy_url, "https": proxy_url}

    # Preferred (newer yfinance)
    try:
        if hasattr(yf, "set_config"):
            # yfinance expects a requests-style proxies dict, not a string
            yf.set_config(proxy=proxy_dict)
            return
    except Exception:
        pass

    # Alternate new API (yfinance 1.0+)
    try:
        if hasattr(yf, "config") and hasattr(yf.config, "network"):
            yf.config.network.proxy = proxy_dict
            return
    except Exception:
        pass

    # Fallback: environment (used by requests)
    os.environ["HTTP_PROXY"] = proxy_url
    os.environ["HTTPS_PROXY"] = proxy_url


def chunked(items: List[str], size: int) -> List[List[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def _extract_ticker_frame(df: pd.DataFrame, ticker: str) -> Optional[pd.DataFrame]:
    """
    yfinance returns multi-index columns in different layouts depending on version:
    - group_by='ticker': columns like ('AAPL','Open') etc
    - default: columns like ('Close','AAPL') etc
    This tries to extract a per-ticker frame with columns: Open/High/Low/Close/Volume.
    """
    if df is None or df.empty:
        return None

    cols = df.columns

    # MultiIndex expected for multi-ticker downloads
    if isinstance(cols, pd.MultiIndex):
        # Case 1: first level is ticker
        if ticker in cols.get_level_values(0):
            sub = df[ticker].copy()
            return sub

        # Case 2: second level is ticker (e.g. ('Close','AAPL'))
        if ticker in cols.get_level_values(1):
            try:
                sub = df.xs(ticker, level=1, axis=1).copy()
                return sub
            except Exception:
                return None

    # Single ticker download may return single-level columns
    if ticker == "" and isinstance(cols, pd.Index):
        return df.copy()

    return None


def compute_latest_bar_metrics(ticker_df: pd.DataFrame) -> Optional[Tuple[float, Optional[int], Optional[float]]]:
    """
    Return (last_close, last_volume, prev_close).
    prev_close is best-effort: last close from previous calendar date in the returned frame.
    """
    if ticker_df is None or ticker_df.empty:
        return None

    # Ensure expected columns exist
    close_col = "Close" if "Close" in ticker_df.columns else None
    vol_col = "Volume" if "Volume" in ticker_df.columns else None
    if not close_col:
        return None

    # Drop rows with NaN close
    s = ticker_df[close_col].dropna()
    if s.empty:
        return None

    last_close = float(s.iloc[-1])
    last_volume: Optional[int] = None
    if vol_col and vol_col in ticker_df.columns:
        try:
            v = ticker_df[vol_col].iloc[-1]
            if v is not None and not (isinstance(v, float) and math.isnan(v)):
                last_volume = int(v)
        except Exception:
            last_volume = None

    # prev close from previous date (best effort)
    prev_close: Optional[float] = None
    try:
        idx = s.index
        # Convert index to date (handles tz-aware)
        dates = pd.to_datetime(idx).date
        last_date = dates[-1]
        # Find last close where date != last_date
        for i in range(len(s) - 2, -1, -1):
            if dates[i] != last_date:
                prev_close = float(s.iloc[i])
                break
    except Exception:
        prev_close = None

    return last_close, last_volume, prev_close


@dataclass
class ChunkResult:
    tickers: List[str]
    rows: Dict[str, Dict[str, Any]]
    failed: List[str]
    duration_s: float
    used_proxy: Optional[str]
    error: Optional[str] = None


def fetch_chunk_snapshot(
    tickers: List[str],
    *,
    proxy: Optional[str],
    period: str,
    interval: str,
    timeout_s: float,
    retries: int,
    min_chunk_size: int,
) -> List[ChunkResult]:
    """
    Fetch a chunk snapshot. Returns a list because failures may cause recursive splitting.
    """
    started = time.time()
    set_process_proxy(proxy)

    def _attempt(symbols: List[str]) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        try:
            # yfinance: pass tickers as space-separated string
            tickers_str = " ".join(symbols)
            df = yf.download(
                tickers=tickers_str,
                period=period,
                interval=interval,
                group_by="ticker",
                auto_adjust=False,
                actions=False,
                prepost=False,
                progress=False,
                threads=False,
                timeout=timeout_s,
            )
            return df, None
        except Exception as e:
            return None, str(e)

    last_error: Optional[str] = None
    df: Optional[pd.DataFrame] = None

    for attempt in range(retries + 1):
        df, last_error = _attempt(tickers)
        if df is not None and not df.empty:
            break
        # backoff
        time.sleep(min(2.0, 0.25 * (attempt + 1)))

    if df is None or df.empty:
        # If chunk is large, split and retry smaller pieces (most effective anti-throttle strategy)
        if len(tickers) > min_chunk_size:
            mid = max(min_chunk_size, len(tickers) // 2)
            left = tickers[:mid]
            right = tickers[mid:]
            out: List[ChunkResult] = []
            out.extend(
                fetch_chunk_snapshot(
                    left,
                    proxy=proxy,
                    period=period,
                    interval=interval,
                    timeout_s=timeout_s,
                    retries=retries,
                    min_chunk_size=min_chunk_size,
                )
            )
            out.extend(
                fetch_chunk_snapshot(
                    right,
                    proxy=proxy,
                    period=period,
                    interval=interval,
                    timeout_s=timeout_s,
                    retries=retries,
                    min_chunk_size=min_chunk_size,
                )
            )
            return out

        return [
            ChunkResult(
                tickers=tickers,
                rows={},
                failed=list(tickers),
                duration_s=time.time() - started,
                used_proxy=proxy,
                error=last_error or "empty response",
            )
        ]

    # Parse dataframe into per-ticker snapshot rows
    now = django_tz.now()
    rows: Dict[str, Dict[str, Any]] = {}
    failed: List[str] = []

    for t in tickers:
        try:
            tdf = _extract_ticker_frame(df, t)
            metrics = compute_latest_bar_metrics(tdf) if tdf is not None else None
            if not metrics:
                failed.append(t)
                continue
            last_close, last_vol, prev_close = metrics
            price_change = None
            price_change_percent = None
            if prev_close and prev_close > 0:
                price_change = last_close - prev_close
                price_change_percent = (price_change / prev_close) * 100.0

            rows[t] = {
                "ticker": t,
                "current_price": last_close,
                "volume": last_vol,
                "price_change": price_change,
                "price_change_percent": price_change_percent,
                "last_updated": now,
            }
        except Exception:
            failed.append(t)

    return [
        ChunkResult(
            tickers=tickers,
            rows=rows,
            failed=failed,
            duration_s=time.time() - started,
            used_proxy=proxy,
        )
    ]


def bulk_apply_updates(rows: Dict[str, Dict[str, Any]], *, batch_size: int = 1000) -> int:
    """
    Bulk update Stock rows for price/volume/change fields.
    Only updates existing Stock rows (does not create).
    """
    if not rows:
        return 0

    tickers = list(rows.keys())
    updated_total = 0

    # Fetch existing stocks
    existing = Stock.objects.in_bulk(tickers, field_name="ticker")

    to_update: List[Stock] = []
    now = django_tz.now()

    for t, data in rows.items():
        stock = existing.get(t)
        if not stock:
            continue

        # Only update if we have a price
        price = data.get("current_price")
        if price is None:
            continue

        stock.current_price = price
        if data.get("volume") is not None:
            stock.volume = data["volume"]
        if data.get("price_change") is not None:
            stock.price_change = data["price_change"]
        if data.get("price_change_percent") is not None:
            stock.price_change_percent = data["price_change_percent"]
        stock.last_updated = data.get("last_updated") or now

        to_update.append(stock)

    fields = ["current_price", "volume", "price_change", "price_change_percent", "last_updated"]
    for chunk in chunked(to_update, batch_size):
        with transaction.atomic():
            Stock.objects.bulk_update(chunk, fields=fields, batch_size=batch_size)
        updated_total += len(chunk)

    return updated_total


def main() -> int:
    parser = argparse.ArgumentParser(description="Bulk intraday snapshot updater (yfinance)")
    parser.add_argument(
        "--tickers-file",
        type=str,
        default=None,
        help="Optional ticker source file (e.g. backend/data/nasdaq_latest.txt). If set, DB is not required.",
    )
    parser.add_argument(
        "--no-db",
        action="store_true",
        help="Do not update database (still downloads and reports coverage).",
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit number of tickers (debug)")
    parser.add_argument("--chunk-size", type=int, default=300, help="Tickers per yf.download call")
    parser.add_argument("--min-chunk-size", type=int, default=50, help="Smallest chunk size after splitting")
    parser.add_argument("--workers", type=int, default=6, help="Parallel worker processes")
    parser.add_argument("--timeout", type=float, default=12.0, help="Per-request timeout (seconds)")
    parser.add_argument("--retries", type=int, default=1, help="Retries per chunk before splitting")
    parser.add_argument("--period", type=str, default="2d", help="yfinance download period")
    parser.add_argument("--interval", type=str, default="1m", help="yfinance download interval")
    parser.add_argument("--use-proxies", action="store_true", help="Enable proxy rotation across worker processes")
    parser.add_argument(
        "--proxy-file",
        type=str,
        default=str(Path(__file__).parent / "http_proxies.txt"),
        help="Proxy file path (txt or json)",
    )
    parser.add_argument("--verify-proxies", action="store_true", help="Verify proxies against Yahoo before use")
    parser.add_argument("--proxy-verify-timeout", type=float, default=2.5, help="Proxy verification timeout (seconds)")
    parser.add_argument("--max-proxies", type=int, default=50, help="Max proxies to use after verification")
    parser.add_argument("--progress-seconds", type=int, default=15, help="Progress log interval")
    parser.add_argument("--db-batch-size", type=int, default=1000, help="bulk_update batch size")
    args = parser.parse_args()

    start = time.time()

    logger.info("=" * 80)
    logger.info("BULK INTRADAY SNAPSHOT (yfinance)")
    logger.info("=" * 80)
    logger.info(
        f"Config: workers={args.workers} chunk_size={args.chunk_size} min_chunk={args.min_chunk_size} "
        f"period={args.period} interval={args.interval} timeout={args.timeout}s retries={args.retries} "
        f"use_proxies={args.use_proxies}"
    )

    def load_tickers_from_file(path: Path) -> List[str]:
        """
        Load tickers from a simple line file or the pipe-delimited NASDAQ/NYSE lists in backend/data.
        - If a line contains '|', uses the first column as ticker.
        - Skips obvious header rows.
        """
        raw: List[str] = []
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "|" in line:
                sym = line.split("|", 1)[0].strip()
                if sym.lower() in ("symbol", "act symbol"):
                    continue
                raw.append(sym)
            else:
                raw.append(line)

        # de-dupe while preserving order
        seen = set()
        out: List[str] = []
        for t in raw:
            t = t.strip()
            if not t or t in seen:
                continue
            seen.add(t)
            out.append(t)
        return out

    # Load tickers (DB by default, or file if provided)
    tickers: List[str]
    if args.tickers_file:
        p = Path(args.tickers_file)
        if not p.exists():
            logger.error(f"--tickers-file not found: {p}")
            return 2
        tickers = load_tickers_from_file(p)
        logger.info(f"Loaded {len(tickers)} tickers from file: {p}")
    else:
        try:
            tickers = list(Stock.objects.values_list("ticker", flat=True))
            logger.info(f"Loaded {len(tickers)} tickers from DB")
        except Exception as e:
            logger.error(
                "Failed to load tickers from DB (DB not reachable in this environment).\n"
                "Use --tickers-file backend/data/nasdaq_latest.txt --no-db to test downloads without DB.\n"
                f"DB error: {e}"
            )
            return 2

    if args.limit:
        tickers = tickers[: args.limit]

    # Proxies
    proxies: List[Optional[str]] = [None]
    if args.use_proxies:
        proxy_file = Path(args.proxy_file)
        proxies_raw = load_proxies(proxy_file)
        proxies = [normalize_proxy(p) for p in proxies_raw if p]
        if proxies and args.verify_proxies:
            proxies = verify_proxies_for_yahoo(
                proxies,
                timeout_s=args.proxy_verify_timeout,
                max_keep=args.max_proxies,
            )

        if not proxies:
            logger.warning("No proxies loaded; continuing without proxies")
            proxies = [None]
        else:
            logger.info(f"Loaded {len(proxies)} proxies")

    # Prepare work chunks
    work = chunked(tickers, args.chunk_size)
    logger.info(f"Created {len(work)} chunks")

    # Run multiprocessing workers
    import multiprocessing as mp

    ctx = mp.get_context("spawn")

    jobs: List[Tuple[int, List[str], Optional[str]]] = []
    for i, symbols in enumerate(work):
        proxy = proxies[i % len(proxies)] if proxies else None
        jobs.append((i, symbols, proxy))

    manager_rows: Dict[str, Dict[str, Any]] = {}
    failed_total: List[str] = []
    completed = 0
    last_progress = time.time()

    logger.info("Starting bulk downloads...")

    cfg = {
        "period": args.period,
        "interval": args.interval,
        "timeout_s": args.timeout,
        "retries": args.retries,
        "min_chunk_size": args.min_chunk_size,
    }

    with ctx.Pool(processes=args.workers, initializer=_init_pool, initargs=(cfg,)) as pool:
        for results in pool.imap_unordered(_mp_worker, jobs, chunksize=1):
            # results is a list (because the fetcher may split chunks recursively)
            for r in results:
                manager_rows.update(r.rows)
                failed_total.extend(r.failed)
            completed += 1

            now = time.time()
            if now - last_progress >= args.progress_seconds:
                elapsed = now - start
                rate_chunks = completed / elapsed if elapsed > 0 else 0
                logger.info(
                    f"Progress: {completed}/{len(jobs)} chunks | "
                    f"rows={len(manager_rows)} failed={len(set(failed_total))} | "
                    f"chunk_rate={rate_chunks:.2f}/s | elapsed={elapsed:.1f}s"
                )
                last_progress = now

    updated = 0
    if args.no_db:
        logger.info("Skipping DB updates (--no-db)")
    else:
        logger.info(f"Applying DB updates for {len(manager_rows)} tickers...")
        try:
            updated = bulk_apply_updates(manager_rows, batch_size=args.db_batch_size)
        except Exception as e:
            logger.error(f"DB update failed: {e}")
            logger.error("Tip: run with --no-db to validate downloads without a DB connection.")

    elapsed = time.time() - start
    unique_failed = sorted(set([t for t in failed_total if t not in manager_rows]))

    logger.info("=" * 80)
    logger.info("BULK SNAPSHOT COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total tickers requested: {len(tickers)}")
    logger.info(f"Tickers with snapshot rows: {len(manager_rows)}")
    logger.info(f"DB updated rows: {updated}")
    logger.info(f"Unique failed tickers: {len(unique_failed)}")
    logger.info(f"Elapsed: {elapsed:.1f}s ({elapsed/60:.2f} min)")
    if elapsed > 0:
        logger.info(f"Effective rate: {len(tickers)/elapsed:.1f} tickers/sec requested")

    if unique_failed:
        # Keep the output small; log first 25
        logger.warning(f"Sample failed tickers (first 25): {', '.join(unique_failed[:25])}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

