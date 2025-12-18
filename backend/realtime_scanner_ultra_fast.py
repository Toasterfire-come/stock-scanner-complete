#!/usr/bin/env python3
"""
full_scanner.py

Ultra-Fast Real-Time Stock Scanner with optional Django DB saving.

Usage:
    python full_scanner.py <ticker_list.txt> <proxies.csv> [--project-path /abs/path/to/project --settings myproject.settings]

If you provide either environment variable DJANGO_SETTINGS_MODULE or the CLI flags
--project-path and --settings, the script will attempt to bootstrap Django and
save results to your app's Stock model using the update_stock_in_db() function.

If no Django settings are supplied, the scanner runs standalone and prints results.
"""

from __future__ import annotations

import sys
import os
import argparse
import time
import json
import csv
import random
import logging
import threading
from pathlib import Path
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Dict, Any, Tuple

# Try import yfinance
try:
    import yfinance as yf
except Exception as exc:
    print("ERROR: yfinance must be installed (pip install yfinance).", exc)
    raise

# Optional, faster TLS fingerprinting – fall back to plain requests.
try:
    from curl_cffi import requests as curl_requests      # type: ignore
    CURL_CFFI = True
except Exception:
    import requests  # type: ignore
    curl_requests = None
    CURL_CFFI = False

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("full_scanner")

# -----------------------------------------------------------------------------
# Configuration dataclass-like container
# -----------------------------------------------------------------------------
class ScanConfig:
    bootstrap_workers: int = 10
    bootstrap_delay_range_ms: Tuple[int, int] = (10, 60)
    max_threads: int = 200
    timeout: float = 4.0
    max_retries: int = 2
    retry_delay: float = 0.1
    target_time: int = 160
    min_success_rate: float = 0.95
    session_ttl: int = 300
    rotate_per_request: bool = True
    use_socks5h: bool = False
    proxy_pool_size: int = 200

cfg = ScanConfig()

# ---- small helper ----
def tiny_sleep():
    low, high = cfg.bootstrap_delay_range_ms
    time.sleep(random.uniform(low, high) / 1000.0)

# -----------------------------------------------------------------------------
# Proxy / Session management
# -----------------------------------------------------------------------------
class ProxySession:
    __slots__ = ("proxy", "session", "created_at")

    def __init__(self, proxy: str, session: Any):
        self.proxy = proxy
        self.session = session
        self.created_at = datetime.utcnow()

    def is_fresh(self, ttl_seconds: int) -> bool:
        return (datetime.utcnow() - self.created_at) < timedelta(seconds=ttl_seconds)


class ProxyRotator:
    def __init__(self, proxies: List[str], cfg: ScanConfig):
        self.cfg = cfg
        self.proxies = proxies[: cfg.proxy_pool_size] if len(proxies) > cfg.proxy_pool_size else proxies
        self.lock = threading.Lock()
        self.index = 0
        self.failures: Dict[str, int] = {}
        self.successes: Dict[str, int] = {}
        self.auth_failed: set = set()
        self.sessions: Dict[str, ProxySession] = {}
        log.info(f"ProxyRotator initialised with {len(self.proxies)} proxies")

    def _next_proxy(self, exclude: Optional[str] = None) -> Optional[str]:
        if not self.proxies:
            return None
        with self.lock:
            healthy = [
                p for p in self.proxies
                if p not in self.auth_failed
                and p != exclude
                and self.failures.get(p, 0) < 5
            ]
            if not healthy:
                log.debug("All proxies exhausted – resetting failure counters")
                self.failures.clear()
                healthy = [p for p in self.proxies if p != exclude]
            proxy = healthy[self.index % len(healthy)]
            self.index = (self.index + 1) % len(healthy)
            return proxy

    def get_proxy(self, exclude: Optional[str] = None) -> Optional[str]:
        return self._next_proxy(exclude)

    def mark_success(self, proxy: str):
        with self.lock:
            self.successes[proxy] = self.successes.get(proxy, 0) + 1
            if self.failures.get(proxy, 0):
                self.failures[proxy] -= 1

    def mark_failure(self, proxy: str, reason: str = ""):
        with self.lock:
            auth = "401" in reason or "unauthorized" in reason.lower()
            if auth:
                self.auth_failed.add(proxy)
                log.debug(f"Proxy {proxy} marked auth-failed ({reason[:30]})")
            else:
                self.failures[proxy] = self.failures.get(proxy, 0) + 1
                log.debug(f"Proxy {proxy} failure #{self.failures[proxy]} ({reason[:30]})")

    def _make_raw_session(self, proxy: str) -> Any:
        if CURL_CFFI and curl_requests:
            sess = curl_requests.Session()
        else:
            import requests
            sess = requests.Session()
        sess.proxies = {"http": proxy, "https": proxy}
        sess.headers.update({
            "User-Agent": random.choice(YFinanceClient.USER_AGENTS),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "DNT": "1",
        })
        return sess

    def get_warmed_session(self, proxy: str) -> Any:
        with self.lock:
            ps = self.sessions.get(proxy)
            if ps and ps.is_fresh(self.cfg.session_ttl):
                return ps.session

        sess = self._make_raw_session(proxy)

        crumb_url = "https://query1.finance.yahoo.com/v1/test/getcrumb"
        try:
            r = sess.get(crumb_url, timeout=self.cfg.timeout)
            r.raise_for_status()
            crumb = r.text.strip()
            if crumb:
                # put crumb in cookie header so later yfinance reads cookies
                sess.headers.update({"Cookie": f"crumb={crumb}"})
            log.debug(f"[bootstrap] crumb retrieved for {proxy[:30]}…")
            self.mark_success(proxy)
        except Exception as exc:
            self.mark_failure(proxy, str(exc))
            log.debug(f"[bootstrap] crumb fetch failed for {proxy[:30]} – {exc}")
        tiny_sleep()

        tiny_json = "https://query2.finance.yahoo.com/v7/finance/quote?symbols=AAPL"
        try:
            r = sess.get(tiny_json, timeout=self.cfg.timeout)
            r.raise_for_status()
            _ = r.json()
            log.debug(f"[bootstrap] tiny JSON ok for {proxy[:30]}…")
            self.mark_success(proxy)
        except Exception as exc:
            self.mark_failure(proxy, str(exc))
            log.debug(f"[bootstrap] tiny JSON failed for {proxy[:30]} – {exc}")

        tiny_sleep()

        with self.lock:
            self.sessions[proxy] = ProxySession(proxy, sess)
        return sess

    def stats(self) -> Dict[str, Any]:
        with self.lock:
            total_success = sum(self.successes.values())
            total_fail = sum(self.failures.values())
            healthy = len([p for p in self.proxies
                           if p not in self.auth_failed and self.failures.get(p, 0) < 5])
            return {
                "total_proxies": len(self.proxies),
                "healthy_proxies": healthy,
                "auth_failed": len(self.auth_failed),
                "total_successes": total_success,
                "total_failures": total_fail,
                "success_rate": (total_success / (total_success + total_fail)
                                 if (total_success + total_fail) else 0.0),
            }

# -----------------------------------------------------------------------------
# YFinance client
# -----------------------------------------------------------------------------
class YFinanceClient:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def __init__(self, rotator: ProxyRotator, cfg: ScanConfig):
        self.rot = rotator
        self.cfg = cfg

    def fetch(self, ticker: str) -> Optional[Dict[str, Any]]:
        proxy = self.rot.get_proxy() if self.cfg.rotate_per_request else None
        failed_proxy = None

        for attempt in range(self.cfg.max_retries):
            session = None
            if proxy:
                session = self.rot.get_warmed_session(proxy)
            else:
                if CURL_CFFI and curl_requests:
                    session = curl_requests.Session()
                else:
                    import requests
                    session = requests.Session()
                session.headers.update({
                    "User-Agent": random.choice(self.USER_AGENTS),
                    "Accept": "*/*",
                    "Connection": "keep-alive",
                })

            try:
                yf_ticker = yf.Ticker(ticker, session=session)
                info = yf_ticker.info

                if not info or len(info) < 5:
                    raise ValueError("empty/partial info payload")

                data = {
                    "ticker": ticker,
                    "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                    "price_change": info.get("regularMarketChange"),
                    "price_change_percent": info.get("regularMarketChangePercent"),
                    "change_percent": info.get("regularMarketChangePercent"),
                    "volume": info.get("volume") or info.get("regularMarketVolume"),
                    "volume_today": info.get("regularMarketVolume"),
                    "dvav": None,
                    "bid_price": info.get("bid"),
                    "ask_price": info.get("ask"),
                    "bid_ask_spread": None,
                    "days_low": info.get("dayLow") or info.get("regularMarketDayLow"),
                    "days_high": info.get("dayHigh") or info.get("regularMarketDayHigh"),
                    "days_range": info.get("regularMarketDayRange"),
                    "price_change_week": None,
                    "price_change_month": None,
                    "price_change_year": None,
                }

                if data["volume_today"] and info.get("averageVolume"):
                    avg = info["averageVolume"]
                    if avg:
                        try:
                            data["dvav"] = float(data["volume_today"]) / float(avg)
                        except Exception:
                            data["dvav"] = None

                if data["bid_price"] and data["ask_price"]:
                    try:
                        data["bid_ask_spread"] = f"{float(data['bid_price']):.2f} - {float(data['ask_price']):.2f}"
                    except Exception:
                        data["bid_ask_spread"] = None

                if proxy:
                    self.rot.mark_success(proxy)
                return data

            except Exception as exc:
                err_msg = str(exc)
                auth_failure = "401" in err_msg or "unauthorized" in err_msg.lower()
                log.debug(f"[fetch] attempt {attempt+1}/{self.cfg.max_retries} "
                          f"failed for {ticker} via {proxy or 'no-proxy'}: {err_msg}")

                if proxy:
                    self.rot.mark_failure(proxy, err_msg)
                    if auth_failure:
                        failed_proxy = proxy

                if attempt < self.cfg.max_retries - 1:
                    proxy = self.rot.get_proxy(exclude=failed_proxy)
                    if not auth_failure:
                        time.sleep(self.cfg.retry_delay * (attempt + 1))

        return None

# -----------------------------------------------------------------------------
# CSV proxy loader & tickers loader
# -----------------------------------------------------------------------------
def load_proxies_from_csv(csv_path: Path) -> List[str]:
    proxies = []
    with csv_path.open(newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if not row:
                continue
            proxy = row[0].strip()
            if proxy:
                proxies.append(proxy)
    log.info(f"Loaded {len(proxies)} proxies from {csv_path.name}")
    return proxies

def load_tickers(ticker_file: Path) -> List[str]:
    if not ticker_file.is_file():
        log.error(f"Ticker file not found: {ticker_file}")
        return []
    tickers = [line.strip().upper() for line in ticker_file.read_text().splitlines()
               if line.strip()]
    log.info(f"Loaded {len(tickers)} tickers from {ticker_file.name}")
    return tickers

# -----------------------------------------------------------------------------
# Django integration: dynamic bootstrap + update_stock_in_db
# -----------------------------------------------------------------------------
USE_DJANGO = False
Stock = None
django = None
logger = log  # for the DB function to use

def try_bootstrap_django(project_path: Optional[str], settings_module: Optional[str]) -> bool:
    """
    Attempt to bootstrap Django. Returns True if Django is successfully set up and
    the Stock model is available.
    """
    global USE_DJANGO, Stock, django, logger

    try:
        import importlib
        # If a project path is supplied, add it to sys.path so Django imports work
        if project_path:
            proj_path = Path(project_path).resolve()
            if str(proj_path) not in sys.path:
                sys.path.insert(0, str(proj_path))
            log.debug(f"Added project path to sys.path: {proj_path}")

        # If settings_module provided, set env var
        if settings_module:
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
            log.debug(f"Set DJANGO_SETTINGS_MODULE={settings_module}")

        # If DJANGO_SETTINGS_MODULE not set, we cannot bootstrap
        if "DJANGO_SETTINGS_MODULE" not in os.environ:
            log.warning("DJANGO_SETTINGS_MODULE not found in environment; skipping Django bootstrap.")
            return False

        import django as django_pkg
        django_pkg.setup()
        django = django_pkg

        # Import DB connection helper
        from django.db import close_old_connections  # noqa: F401

        # Try to import app model 'Stock' under common apps - user should adjust if needed.
        # We will attempt to find Stock model by searching installed apps for 'Stock'
        from django.apps import apps
        found = None
        for app_config in apps.get_app_configs():
            try:
                m = app_config.get_model("Stock")
                if m:
                    found = m
                    break
            except LookupError:
                continue

        if not found:
            log.warning("Could not find a 'Stock' model automatically. Make sure your app defines a model named 'Stock'.")
            # still return True (Django set up) but Stock remains None
            USE_DJANGO = True
            return True

        Stock = found
        USE_DJANGO = True
        log.info(f"Django bootstrapped. Stock model from app '{Stock._meta.app_label}' loaded.")
        return True

    except Exception as exc:
        log.exception("Django bootstrap failed: %s", exc)
        USE_DJANGO = False
        return False

# The DB save function (uses the Stock model if available).
def update_stock_in_db(data: Dict[str, Any]) -> bool:
    """Update stock in database (uses Django ORM)."""
    global Stock, django, logger
    if not USE_DJANGO or Stock is None:
        logger.error("Django is not configured or Stock model isn't available. Skipping DB save.")
        return False

    try:
        # Close old connections to avoid transaction sharing between threads
        from django.db import close_old_connections, transaction
        close_old_connections()

        # Ensure a consistent last_updated timestamp
        last_updated = data.get("last_updated") or datetime.utcnow()

        with transaction.atomic():
            stock, created = Stock.objects.update_or_create(
                ticker=data["ticker"],
                defaults={
                    "current_price": data.get("current_price"),
                    "price_change": data.get("price_change"),
                    "price_change_percent": data.get("price_change_percent"),
                    "change_percent": data.get("change_percent"),
                    "volume": data.get("volume"),
                    "volume_today": data.get("volume_today"),
                    "dvav": data.get("dvav"),
                    "bid_price": data.get("bid_price"),
                    "ask_price": data.get("ask_price"),
                    "bid_ask_spread": data.get("bid_ask_spread"),
                    "days_low": data.get("days_low"),
                    "days_high": data.get("days_high"),
                    "days_range": data.get("days_range"),
                    "last_updated": last_updated,
                }
            )
        return True
    except Exception as e:
        logger.error(f"Database error for {data.get('ticker')}: {str(e)}")
        return False

# -----------------------------------------------------------------------------
# Main scanning orchestration
# -----------------------------------------------------------------------------
def run_scan(ticker_path: Path, proxy_csv_path: Path, save_to_db: bool):
    global cfg

    tickers = load_tickers(ticker_path)
    if not tickers:
        log.error("No tickers found – aborting.")
        return

    raw_proxies = load_proxies_from_csv(proxy_csv_path)
    rotator = ProxyRotator(raw_proxies, cfg)

    # Bootstrap proxies
    log.info("=== Bootstrap phase – warming proxies ===")
    bootstrap_start = time.time()

    def bootstrap_one(proxy_url: str):
        try:
            rotator.get_warmed_session(proxy_url)
        except Exception as e:
            log.debug(f"Bootstrap error for {proxy_url[:30]}: {e}")

    with ThreadPoolExecutor(max_workers=cfg.bootstrap_workers) as boot_ex:
        list(boot_ex.map(bootstrap_one, rotator.proxies))

    bootstrap_elapsed = time.time() - bootstrap_start
    log.info(f"Bootstrap finished in {bootstrap_elapsed:.2f}s")
    log.debug("Bootstrap statistics: %s", json.dumps(rotator.stats(), indent=2))

    # Scanning phase
    log.info("=== Scanning phase ===")
    client = YFinanceClient(rotator, cfg)

    stats = {
        "total": len(tickers),
        "success": 0,
        "failed": 0,
        "start": time.time(),
    }

    # We'll use a thread pool for fetch + optional DB save.
    def process_ticker(ticker: str) -> Tuple[str, Optional[Dict[str, Any]], bool]:
        """
        Returns tuple (ticker, payload or None, saved_to_db flag)
        This runs per thread and is safe to call concurrently.
        """
        # If Django is used, ensure old DB connections are closed in this thread
        if USE_DJANGO:
            try:
                from django.db import close_old_connections
                close_old_connections()
            except Exception:
                pass

        payload = client.fetch(ticker)
        saved = False
        if payload:
            payload["last_updated"] = datetime.utcnow()
            if save_to_db and USE_DJANGO and Stock is not None:
                saved = update_stock_in_db(payload)
            # else: saved stays False (or we could set to None)
        return (ticker, payload, saved)

    with ThreadPoolExecutor(max_workers=cfg.max_threads) as executor:
        future_to_ticker = {executor.submit(process_ticker, t): t for t in tickers}

        for i, fut in enumerate(as_completed(future_to_ticker), 1):
            ticker = future_to_ticker[fut]
            try:
                payload = fut.result()
                # payload is (ticker, data_or_none, saved_flag)
                _, data, saved = payload
                if data:
                    stats["success"] += 1
                    if save_to_db and saved:
                        log.info(f"[{ticker}] saved => price={data['current_price']}")
                    else:
                        # Either not saving or DB save failed
                        log.info(f"[{ticker}] fetched => price={data['current_price']}")
                else:
                    stats["failed"] += 1
                    log.warning(f"[{ticker}] fetch FAILED")
            except Exception as exc:
                log.exception(f"Unhandled error for {ticker}: {exc}")
                stats["failed"] += 1

            if i % 200 == 0 or i == stats["total"]:
                elapsed = time.time() - stats["start"]
                rate = i / elapsed if elapsed else 0
                succ_pct = (stats["success"] / i) * 100
                log.info(
                    f"[progress] {i}/{stats['total']} ({succ_pct:.1f}% ok) | "
                    f"{rate:.2f} tickers/s | elapsed {elapsed:.1f}s"
                )

    # Final summary
    total_time = time.time() - stats["start"]
    success_rate = (stats["success"] / stats["total"]) * 100 if stats["total"] else 0

    log.info("=" * 80)
    log.info("SCAN COMPLETE")
    log.info(f"Time elapsed: {total_time:.2f}s ({stats['total']/total_time:.2f} tickers/s)")
    log.info(f"Success: {stats['success']}/{stats['total']} ({success_rate:.2f}%)")
    log.info(f"Failed : {stats['failed']}/{stats['total']} ({100-success_rate:.2f}%)")
    log.info("-" * 80)
    log.info("PROXY STATISTICS")
    log.info(json.dumps(rotator.stats(), indent=2))
    log.info("-" * 80)
    if total_time <= cfg.target_time:
        log.info(f"✓ TIME TARGET MET ({total_time:.2f}s ≤ {cfg.target_time}s)")
    else:
        log.warning(f"✗ TIME TARGET MISSED ({total_time:.2f}s > {cfg.target_time}s)")
    if success_rate >= cfg.min_success_rate * 100:
        log.info(f"✓ SUCCESS-RATE TARGET MET ({success_rate:.2f}% ≥ {cfg.min_success_rate*100:.0f}%)")
    else:
        log.warning(f"✗ SUCCESS-RATE TARGET MISSED ({success_rate:.2f}% < {cfg.min_success_rate*100:.0f}%)")
    log.info("=" * 80)

# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
def main(argv: Optional[List[str]] = None):
    p = argparse.ArgumentParser(description="Ultra-fast stock scanner (optional Django DB save)")
    p.add_argument("tickers", type=str, help="Path to ticker list (one symbol per line)")
    p.add_argument("proxies", type=str, help="Path to proxies CSV (first column: proxy URL)")
    p.add_argument("--project-path", type=str, default=None,
                   help="(optional) absolute path to Django project root (so imports work)")
    p.add_argument("--settings", type=str, default=None,
                   help="(optional) DJANGO_SETTINGS_MODULE (e.g. myproject.settings)")
    p.add_argument("--no-db", action="store_true", help="Do not attempt to save results to Django DB")
    p.add_argument("--debug", action="store_true", help="Set logging to DEBUG")
    args = p.parse_args(argv)

    if args.debug:
        log.setLevel(logging.DEBUG)

    ticker_file = Path(args.tickers)
    proxy_file = Path(args.proxies)

    # Try bootstrapping Django if settings or env var present and user hasn't asked --no-db
    save_to_db = False
    if not args.no_db and (args.settings or "DJANGO_SETTINGS_MODULE" in os.environ):
        ok = try_bootstrap_django(args.project_path, args.settings)
        if ok and USE_DJANGO:
            save_to_db = True
        else:
            log.warning("Django not available; running without DB saving.")
            save_to_db = False
    else:
        if args.no_db:
            log.info("Running with --no-db: DB saves disabled by CLI flag.")
        else:
            log.info("Django settings not provided and DJANGO_SETTINGS_MODULE not set: running without DB saves.")

    run_scan(ticker_file, proxy_file, save_to_db)

if __name__ == "__main__":
    main()
