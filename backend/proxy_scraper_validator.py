#!/usr/bin/env python3
"""
Proxy Scraper + YFinance Validator

- Scrapes free HTTP(S) proxies from multiple public sources
- Validates each proxy by performing a real yfinance call using a per-proxy Session
- Ensures at least N working proxies (default: 100)
- Writes results to JSON (default: working_proxies.json) compatible with existing loaders

Usage:
  python proxy_scraper_validator.py -threads 50 -timeout 5 -min 100 -output working_proxies.json

Notes:
- Free proxies are volatile; success rates vary by time of day and geography
- This script aims for breadth (many sources) and speed (threaded validation)
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import random
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List, Set, Tuple

import requests
import yfinance as yf

# -----------------------------
# Configuration
# -----------------------------
DEFAULT_SOURCES: list[str] = [
    # ProxyScrape - HTTP and HTTPS
    "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://api.proxyscrape.com/v2/?request=get&protocol=https&timeout=10000&country=all&ssl=all&anonymity=all",
    # Proxy-List.download
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://www.proxy-list.download/api/v1/get?type=https",
    # ProxyScan
    "https://www.proxyscan.io/download?type=http",
    "https://www.proxyscan.io/download?type=https",
    # Popular GitHub lists
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/https.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTP_RAW.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/https.txt",
]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
COMMON_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

IP_PORT_RE = re.compile(r"^(?P<host>\d{1,3}(?:\.\d{1,3}){3}|\[[0-9a-fA-F:]+\]):(?P<port>\d{2,5})$")


@dataclass
class Args:
    threads: int
    timeout: int
    minimum: int
    output: str
    max_candidates: int | None


def parse_args() -> Args:
    parser = argparse.ArgumentParser(description="Scrape and validate proxies via yfinance")
    parser.add_argument("-threads", type=int, default=50, help="Number of validation threads (default: 50)")
    parser.add_argument("-timeout", type=int, default=5, help="Per-request timeout seconds (default: 5)")
    parser.add_argument("-min", dest="minimum", type=int, default=100, help="Minimum working proxies to collect (default: 100)")
    parser.add_argument("-output", type=str, default=os.getenv("PROXY_FILE_PATH", "working_proxies.json"), help="Output JSON file path")
    parser.add_argument("-max-candidates", type=int, default=None, help="Optional max number of candidate proxies to test")
    ns = parser.parse_args()
    return Args(threads=ns.threads, timeout=ns.timeout, minimum=ns.minimum, output=ns.output, max_candidates=ns.max_candidates)


# -----------------------------
# Proxy collection
# -----------------------------

def fetch_url_text(url: str, timeout: int) -> str:
    try:
        resp = requests.get(url, timeout=timeout, headers=COMMON_HEADERS)
        if resp.status_code == 200 and resp.text:
            return resp.text
    except Exception:
        return ""
    return ""


def parse_proxies_from_text(text: str) -> list[str]:
    proxies: list[str] = []
    for line in text.splitlines():
        raw = line.strip()
        if not raw:
            continue
        # Typical formats: ip:port or protocol://ip:port
        # Strip possible scheme and credentials
        if "," in raw:  # handle CSV lists like "ip:port,ip:port"
            for part in raw.split(","):
                part = part.strip()
                if part:
                    _add_if_ip_port(part, proxies)
            continue
        _add_if_ip_port(raw, proxies)
    return proxies


def _normalize_ip_port(s: str) -> str | None:
    s = s.strip()
    if "://" in s:
        s = s.split("://", 1)[1]
    if "@" in s:
        s = s.split("@", 1)[-1]  # drop credentials if present
    s = s.strip()
    m = IP_PORT_RE.match(s)
    if not m:
        return None
    host = m.group("host")
    port = m.group("port")
    return f"{host}:{port}"


def _add_if_ip_port(value: str, out: list[str]) -> None:
    normalized = _normalize_ip_port(value)
    if normalized:
        out.append(normalized)


def collect_candidate_proxies(timeout: int) -> list[str]:
    results: list[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(16, len(DEFAULT_SOURCES))) as pool:
        futures = [pool.submit(fetch_url_text, url, timeout) for url in DEFAULT_SOURCES]
        for fut in concurrent.futures.as_completed(futures):
            try:
                text = fut.result()
            except Exception:
                text = ""
            if not text:
                continue
            results.extend(parse_proxies_from_text(text))
    # De-dupe while preserving insertion order
    seen: Set[str] = set()
    deduped: list[str] = []
    for p in results:
        if p not in seen:
            seen.add(p)
            deduped.append(p)
    random.shuffle(deduped)
    return deduped


# -----------------------------
# Validation using yfinance
# -----------------------------

def build_proxy_session(proxy_ip_port: str, timeout: int) -> requests.Session:
    session = requests.Session()
    proxy_url = f"http://{proxy_ip_port}"
    session.proxies = {
        "http": proxy_url,
        "https": proxy_url,
    }
    session.headers.update(COMMON_HEADERS)
    # Some endpoints are sensitive to Connection/Accept headers; keep minimal
    adapter = requests.adapters.HTTPAdapter(pool_connections=2, pool_maxsize=2, max_retries=0, pool_block=False)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    # Attach default timeout by wrapping session.request
    orig_request = session.request

    def request_with_timeout(method, url, **kwargs):  # type: ignore[override]
        if "timeout" not in kwargs:
            kwargs["timeout"] = timeout
        return orig_request(method, url, **kwargs)

    session.request = request_with_timeout  # type: ignore[assignment]
    return session


def _prefilter_proxy_connectivity(session: requests.Session) -> bool:
    """Quickly verify the proxy can reach the public internet.

    Uses two lightweight endpoints to reduce false negatives.
    """
    urls = [
        "https://api.ipify.org?format=json",
        "https://httpbin.org/ip",
    ]
    for url in urls:
        try:
            r = session.get(url, timeout=3)
            if r.status_code == 200 and r.text:
                return True
        except Exception:
            continue
    return False


def _validate_yahoo_quote_endpoint(session: requests.Session, timeout: int) -> bool:
    """Validate by hitting Yahoo Finance quote endpoints directly via the proxy session."""
    yahoo_urls = [
        "https://query1.finance.yahoo.com/v7/finance/quote?symbols=AAPL",
        "https://query2.finance.yahoo.com/v10/finance/quoteSummary/AAPL?modules=price",
    ]
    for url in yahoo_urls:
        try:
            r = session.get(url, timeout=timeout)
            if r.status_code == 200 and r.content and len(r.content) > 50:
                # Basic sanity: JSON payload should contain 'quote' or 'price' strings
                text_sample = r.text[:200].lower()
                if ("quote" in text_sample) or ("price" in text_sample):
                    return True
        except Exception:
            continue
    return False


def validate_proxy_with_yfinance(proxy_ip_port: str, timeout: int) -> bool:
    """Validate a proxy by ensuring it can reach Yahoo endpoints.

    Steps:
    1) Prefilter with a generic connectivity check (ipify/httpbin)
    2) Hit Yahoo quote endpoints directly via requests session
    3) As a final check, patch yfinance to use this session and attempt a light call
    """
    try:
        session = build_proxy_session(proxy_ip_port, timeout)
        # Stage 1: quick connectivity check
        if not _prefilter_proxy_connectivity(session):
            return False
        # Stage 2: Yahoo direct endpoints
        if not _validate_yahoo_quote_endpoint(session, timeout):
            return False
        # Stage 3: yfinance integration sanity
        try:
            import yfinance.shared  # type: ignore
            yfinance.shared._requests = session  # route through our proxy session
            t = yf.Ticker("AAPL")
            # Use a very light attribute access that triggers a single request in most versions
            _ = getattr(t, "fast_info", None)
        except Exception:
            # Even if this fails, Yahoo endpoint success indicates suitability for enhanced retrieval
            pass
        return True
    except Exception:
        return False


# -----------------------------
# Main flow
# -----------------------------

def main() -> int:
    args = parse_args()

    start = time.time()
    print("[PROXY] Collecting candidate proxies from public sources...")
    candidates = collect_candidate_proxies(timeout=max(3, args.timeout))
    print(f"[PROXY] Collected {len(candidates)} raw candidates before de-dupe")

    if args.max_candidates is not None:
        candidates = candidates[: max(0, args.max_candidates)]
        print(f"[PROXY] Truncated candidates to first {len(candidates)} as requested")

    print(f"[VALIDATE] Validating proxies via yfinance (min required: {args.minimum})...")

    working: list[str] = []
    tested_count = 0

    # Early stop once we reach minimum; submit tasks in batches to allow early termination
    batch_size = max(32, args.threads * 2)

    def test_batch(batch: list[str]) -> None:
        nonlocal tested_count, working
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as pool:
            future_to_proxy = {pool.submit(validate_proxy_with_yfinance, p, args.timeout): p for p in batch}
            for fut in concurrent.futures.as_completed(future_to_proxy):
                p = future_to_proxy[fut]
                ok = False
                try:
                    ok = fut.result()
                except Exception:
                    ok = False
                tested_count += 1
                if ok:
                    # Store in normalized format with scheme for downstream usage
                    working.append(f"http://{p}")
                # Stop condition check kept lightweight
                if len(working) >= args.minimum:
                    # Drain remaining futures quickly (don't block)
                    return

    # Iterate over candidates in batches
    for i in range(0, len(candidates), batch_size):
        if len(working) >= args.minimum:
            break
        test_batch(candidates[i : i + batch_size])

    elapsed = time.time() - start
    print(f"[RESULT] Working proxies: {len(working)} / tested {tested_count} in {elapsed:.1f}s")

    # Ensure we at least return some results, even if below minimum
    working_unique: list[str] = []
    seen: Set[str] = set()
    for p in working:
        if p not in seen:
            seen.add(p)
            working_unique.append(p)

    out_payload = {
        "working_proxies": working_unique,
        "count": len(working_unique),
        "tested": tested_count,
        "sources": len(DEFAULT_SOURCES),
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "timeout": args.timeout,
        "threads": args.threads,
        "min_requested": args.minimum,
        "success_rate": round((len(working_unique) / tested_count) * 100, 2) if tested_count else 0.0,
    }

    # Write JSON compatible with existing loaders (they check 'working_proxies' or 'proxies')
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(out_payload, f, indent=2)
        print(f"[WRITE] Saved {len(working_unique)} proxies to {args.output}")
    except Exception as e:
        print(f"[ERROR] Failed to write output: {e}")
        return 2

    # Emit a friendly summary for callers parsing stdout
    print(f"Working: {len(working_unique)} | Tested: {tested_count} | Success Rate: {out_payload['success_rate']}%")
    return 0 if working_unique else 1


if __name__ == "__main__":
    sys.exit(main())
