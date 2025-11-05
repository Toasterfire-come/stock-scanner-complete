#!/usr/bin/env python3
"""
Validate proxies for Yahoo Finance access and prune failing ones.
- Loads proxies from a JSON file (supports keys: "proxies", "working_proxies" or top-level list)
- Tests each proxy by calling Yahoo Finance quote API for AAPL
- Writes back only working proxies to the output JSON in {'proxies': [...], 'metadata': {...}} format

Usage:
  python backend/tools/validate_proxies_yfinance.py \
    --input backend/working_proxies.json \
    --output backend/working_proxies.json \
    --threads 50 \
    --timeout 6
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import os
import random
import sys
import time
from typing import Iterable, List, Tuple

import requests

YF_QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=AAPL"


def load_proxies(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        raw = data
    elif isinstance(data, dict):
        if "proxies" in data and isinstance(data["proxies"], list):
            raw = data["proxies"]
        elif "working_proxies" in data and isinstance(data["working_proxies"], list):
            raw = data["working_proxies"]
        else:
            # Fallback: any string values in dict
            raw = [v for v in data.values() if isinstance(v, str)]
    else:
        raw = []

    # Normalize and de-duplicate
    normalized: List[str] = []
    seen = set()
    for p in raw:
        if not isinstance(p, str):
            continue
        s = p.strip()
        if not s:
            continue
        if "://" not in s:
            s = f"http://{s}"
        if s not in seen:
            seen.add(s)
            normalized.append(s)
    return normalized


def is_working_proxy(proxy: str, timeout: float = 6.0) -> Tuple[str, bool, str]:
    """Return (proxy, ok, reason). Uses Yahoo Finance quote API.
    We only mark ok=True when we get a 200 and parse expected JSON shape.
    """
    session = requests.Session()
    session.proxies = {"http": proxy, "https": proxy}
    # Keep UA realistic; some endpoints block generic clients
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    })
    # Light jitter to avoid burst
    time.sleep(random.uniform(0.0, 0.05))
    try:
        # connect/read timeouts
        resp = session.get(YF_QUOTE_URL, timeout=(min(3.0, timeout), timeout))
        if resp.status_code != 200:
            return proxy, False, f"HTTP {resp.status_code}"
        try:
            data = resp.json()
        except Exception:
            return proxy, False, "invalid_json"
        if not isinstance(data, dict) or "quoteResponse" not in data:
            return proxy, False, "unexpected_shape"
        result = data.get("quoteResponse", {}).get("result", [])
        if isinstance(result, list) and len(result) >= 0:
            # Consider any well-formed response a pass (availability proven)
            return proxy, True, "ok"
        return proxy, False, "empty_result"
    except requests.exceptions.ProxyError:
        return proxy, False, "proxy_error"
    except requests.exceptions.ConnectTimeout:
        return proxy, False, "connect_timeout"
    except requests.exceptions.ReadTimeout:
        return proxy, False, "read_timeout"
    except requests.exceptions.SSLError:
        return proxy, False, "ssl_error"
    except requests.exceptions.RequestException as e:
        return proxy, False, f"request_exception:{type(e).__name__}"
    except Exception as e:
        return proxy, False, f"unexpected:{type(e).__name__}"


def write_output(path: str, proxies: List[str], source: str, tested: int, stats: dict | None = None) -> None:
    payload = {
        "proxies": proxies,
        "metadata": {
            "total": len(proxies),
            "source": source,
            "timestamp": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "success_rate": f"{(len(proxies)/tested*100.0):.1f}%" if tested else "0.0%",
            "total_tested": tested,
        },
    }
    if stats:
        payload["stats"] = stats
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    # Atomic-ish replace
    os.replace(tmp_path, path)


def main():
    parser = argparse.ArgumentParser(description="Validate proxies for Yahoo Finance access and prune failing ones")
    parser.add_argument("--input", required=True, help="Input proxies JSON path")
    parser.add_argument("--output", required=True, help="Output JSON path (can be same as input)")
    parser.add_argument("--threads", type=int, default=50, help="Max concurrent validations")
    parser.add_argument("--timeout", type=float, default=6.0, help="Per-request timeout in seconds")
    parser.add_argument("--max", type=int, default=None, help="Optional max proxies to test (debug)")
    args = parser.parse_args()

    in_path = args.input
    out_path = args.output

    if not os.path.exists(in_path):
        print(f"ERROR: Input file not found: {in_path}")
        sys.exit(1)

    try:
        proxies = load_proxies(in_path)
    except Exception as e:
        print(f"ERROR: Failed to load proxies from {in_path}: {e}")
        sys.exit(1)

    if not proxies:
        print("No proxies found to validate.")
        write_output(out_path, [], source="validation", tested=0)
        return

    if args.max is not None:
        proxies = proxies[: max(0, args.max)]

    print(f"Validating {len(proxies)} proxies against Yahoo Finance ...")
    start = time.time()

    tested = 0
    good: List[str] = []
    bad_reasons: dict[str, int] = {}

    # Use a bounded pool
    workers = max(1, min(args.threads, 128))
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(is_working_proxy, p, args.timeout): p for p in proxies}
        for i, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            proxy = futures[future]
            try:
                p, ok, reason = future.result()
            except Exception as e:
                ok = False
                reason = f"future_exc:{type(e).__name__}"
                p = proxy
            tested += 1
            if ok:
                good.append(p)
            else:
                bad_reasons[reason] = bad_reasons.get(reason, 0) + 1
            if i % 25 == 0 or i == len(proxies):
                elapsed = time.time() - start
                rate = tested / elapsed if elapsed > 0 else 0.0
                print(f"[PROGRESS] {tested}/{len(proxies)} tested, {len(good)} good, {elapsed:.1f}s, {rate:.1f}/s")

    elapsed = time.time() - start
    print("=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)
    print(f"Tested:     {tested}")
    print(f"Working:    {len(good)}")
    print(f"Success %:  {(len(good)/tested*100.0):.1f}%")
    print(f"Duration:   {elapsed:.1f}s")
    if bad_reasons:
        top = sorted(bad_reasons.items(), key=lambda kv: kv[1], reverse=True)[:10]
        print("Top failure reasons:")
        for reason, count in top:
            print(f"  - {reason}: {count}")

    # Write output
    # Backup if overwriting
    if os.path.abspath(in_path) == os.path.abspath(out_path):
        backup = f"{out_path}.backup_{int(time.time())}.json"
        try:
            with open(in_path, "r", encoding="utf-8") as src, open(backup, "w", encoding="utf-8") as dst:
                dst.write(src.read())
            print(f"Backup written: {backup}")
        except Exception as e:
            print(f"WARN: Could not write backup: {e}")

    write_output(out_path, good, source="validation", tested=tested, stats={"bad_reasons": bad_reasons})
    print(f"Wrote {len(good)} working proxies to {out_path}")

    # Exit code: 0 if at least 1 good proxy, else 2
    sys.exit(0 if good else 2)


if __name__ == "__main__":
    main()
