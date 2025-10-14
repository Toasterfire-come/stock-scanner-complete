#!/usr/bin/env python3
"""
Proxy filter using a full yfinance ticker fetch per proxy.

- Iterates over every proxy in an input JSON file
- For each proxy, patches yfinance session to use that proxy
- Attempts to fetch a broad set of data for a single ticker (fast_info, info,
  daily and intraday history, earnings trend)
- Proxies that fail network/SSL/proxy/timeouts are removed
- Writes a pruned output JSON containing only working proxies

Example:
  python backend/tools/proxy_filter_full_ticker.py \
    --input backend/working_proxies.json \
    --output backend/working_proxies.json \
    --ticker AAPL \
    --procs 24 \
    --timeout 8
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import multiprocessing as mp
import os
import random
import sys
import time
from typing import List, Tuple

# Third-party
import requests
import yfinance as yf


def normalize_proxy_string(proxy_str: str) -> str | None:
    if not proxy_str or not isinstance(proxy_str, str):
        return None
    s = proxy_str.strip()
    if not s:
        return None
    if "://" not in s:
        s = f"http://{s}"
    return s


def load_proxies(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        raw = data
    elif isinstance(data, dict):
        if isinstance(data.get("proxies"), list):
            raw = data["proxies"]
        elif isinstance(data.get("working_proxies"), list):
            raw = data["working_proxies"]
        else:
            raw = [v for v in data.values() if isinstance(v, str)]
    else:
        raw = []
    # Normalize & de-dupe
    out: List[str] = []
    seen = set()
    for p in raw:
        np = normalize_proxy_string(p)
        if not np:
            continue
        if np not in seen:
            seen.add(np)
            out.append(np)
    return out


def patch_yfinance_proxy(proxy: str) -> None:
    import yfinance.shared
    session = requests.Session()
    session.proxies = {"http": proxy, "https": proxy}
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    })
    yfinance.shared._requests = session


def _is_networkish_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    for kw in ("proxy", "timeout", "timed out", "ssl", "connection", "connect", "read", "max retries"):
        if kw in msg:
            return True
    return False


def test_single_proxy(args_tuple: Tuple[str, str, float]) -> Tuple[str, bool, str]:
    proxy, ticker, timeout = args_tuple
    try:
        patch_yfinance_proxy(proxy)
        # Small jitter to avoid hammering
        time.sleep(random.uniform(0.01, 0.05))

        # Fetch a broad set of data to exercise endpoints
        tkr = yf.Ticker(ticker)

        # 1) fast_info (cheap, but exercises one path)
        fast_info = None
        try:
            fast_info = tkr.fast_info
        except Exception as e:
            # Ignore non-network issues for fast_info
            if _is_networkish_error(e):
                return proxy, False, f"fast_info:{type(e).__name__}"

        # 2) info (heavier)
        info = None
        try:
            info = tkr.info
        except Exception as e:
            if _is_networkish_error(e):
                return proxy, False, f"info:{type(e).__name__}"

        # 3) daily history
        try:
            hist = tkr.history(period="1mo", timeout=timeout)
        except TypeError:
            hist = tkr.history(period="1mo")
        except Exception as e:
            if _is_networkish_error(e):
                return proxy, False, f"history:{type(e).__name__}"
            hist = None

        # 4) intraday history
        try:
            intraday = tkr.history(period="1d", interval="1m", timeout=timeout)
        except TypeError:
            intraday = tkr.history(period="1d", interval="1m")
        except Exception as e:
            if _is_networkish_error(e):
                return proxy, False, f"intraday:{type(e).__name__}"
            intraday = None

        # 5) earnings trend
        try:
            _ = tkr.get_earnings_trend()
        except Exception as e:
            if _is_networkish_error(e):
                return proxy, False, f"earnings:{type(e).__name__}"

        # Decide pass/fail: we expect at least one of fast_info/info/history paths to have data
        has_fast = bool(fast_info)
        has_info = isinstance(info, dict) and len(info) > 3
        has_hist = (hist is not None and not hist.empty) if 'hist' in locals() else False
        has_intraday = (intraday is not None and not intraday.empty) if 'intraday' in locals() else False

        if has_fast or has_info or has_hist or has_intraday:
            return proxy, True, "ok"
        # If no data but no network error, consider it inconclusive but not a proxy failure
        return proxy, True, "weak"
    except Exception as e:
        # Any unexpected exception => treat as failure if network-ish, otherwise pass weakly
        return (proxy, False, f"unexpected:{type(e).__name__}") if _is_networkish_error(e) else (proxy, True, "weak")


def write_output(path: str, proxies: List[str], source: str, tested: int, bad_reasons: dict[str, int]) -> None:
    payload = {
        "proxies": proxies,
        "metadata": {
            "total": len(proxies),
            "source": source,
            "timestamp": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "success_rate": f"{(len(proxies)/tested*100.0):.1f}%" if tested else "0.0%",
            "total_tested": tested,
        },
        "stats": {
            "bad_reasons": bad_reasons,
        }
    }
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, path)


def main():
    parser = argparse.ArgumentParser(description="Filter proxies by performing a full yfinance fetch for one ticker")
    parser.add_argument("--input", required=True, help="Input proxies JSON path")
    parser.add_argument("--output", required=True, help="Output JSON path (can equal input)")
    parser.add_argument("--ticker", default="AAPL", help="Ticker symbol to use for testing")
    parser.add_argument("--procs", type=int, default=max(2, mp.cpu_count() // 2), help="Number of parallel processes")
    parser.add_argument("--timeout", type=float, default=8.0, help="Per-call timeout passed to yfinance history where supported")
    parser.add_argument("--max", type=int, default=None, help="Optional cap on proxies to test (debug)")
    args = parser.parse_args()

    in_path = args.input
    out_path = args.output

    if not os.path.exists(in_path):
        print(f"ERROR: Input not found: {in_path}")
        sys.exit(1)

    try:
        proxies = load_proxies(in_path)
    except Exception as e:
        print(f"ERROR: Failed to load proxies: {e}")
        sys.exit(1)

    if not proxies:
        print("No proxies to test.")
        write_output(out_path, [], source="proxy_filter_full_ticker", tested=0, bad_reasons={})
        return

    if args.max is not None:
        proxies = proxies[: max(0, args.max)]

    print(f"Testing {len(proxies)} proxies with yfinance for ticker {args.ticker} using {args.procs} processes ...")

    # Backup if overwriting
    if os.path.abspath(in_path) == os.path.abspath(out_path):
        bk = f"{out_path}.backup_{int(time.time())}.json"
        try:
            with open(in_path, "r", encoding="utf-8") as src, open(bk, "w", encoding="utf-8") as dst:
                dst.write(src.read())
            print(f"Backup written: {bk}")
        except Exception as e:
            print(f"WARN: Could not create backup: {e}")

    start = time.time()
    tested = 0
    good: List[str] = []
    bad_reasons: dict[str, int] = {}

    # Multiprocessing with chunks
    with mp.Pool(processes=max(1, args.procs)) as pool:
        for i, (proxy, ok, reason) in enumerate(pool.imap_unordered(
            test_single_proxy, ((p, args.ticker, args.timeout) for p in proxies), chunksize=4
        ), start=1):
            tested += 1
            if ok:
                good.append(proxy)
            else:
                bad_reasons[reason] = bad_reasons.get(reason, 0) + 1
            if i % 20 == 0 or i == len(proxies):
                elapsed = time.time() - start
                rate = tested / elapsed if elapsed > 0 else 0.0
                print(f"[PROGRESS] {tested}/{len(proxies)} tested, {len(good)} kept, {elapsed:.1f}s, {rate:.1f}/s")

    elapsed = time.time() - start
    print("=" * 60)
    print("PROXY FILTER RESULTS")
    print("=" * 60)
    print(f"Ticker:     {args.ticker}")
    print(f"Tested:     {tested}")
    print(f"Kept:       {len(good)}")
    print(f"Success %:  {(len(good)/tested*100.0):.1f}%")
    print(f"Duration:   {elapsed:.1f}s")
    if bad_reasons:
        top = sorted(bad_reasons.items(), key=lambda kv: kv[1], reverse=True)[:10]
        print("Top failure reasons:")
        for reason, count in top:
            print(f"  - {reason}: {count}")

    write_output(out_path, good, source="proxy_filter_full_ticker", tested=tested, bad_reasons=bad_reasons)
    print(f"Wrote {len(good)} working proxies to {out_path}")

    sys.exit(0 if good else 2)


if __name__ == "__main__":
    # Make fork start method safer for yfinance
    try:
        mp.set_start_method("spawn")
    except RuntimeError:
        pass
    main()
