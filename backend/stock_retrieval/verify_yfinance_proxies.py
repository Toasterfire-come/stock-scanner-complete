#!/usr/bin/env python3
"""
Verify Yahoo/yfinance proxies using REAL yf.download()
======================================================

Problem this solves:
- "Proxies work in other scripts" often means they work for *some* HTTP traffic,
  but yfinance (newer versions) uses curl_cffi + different internals.
- If a proxy is dead/unreachable, yfinance will waste 20-30s per request (curl timeout),
  killing throughput for bulk downloads.

This script:
- Reads proxies from a file (default: backend/stock_retrieval/http_proxies.txt)
- Tests each proxy using *yf.download()* (the same primitive your bulk snapshot uses)
- Tries multiple configuration methods, because yfinance has changed proxy handling over time:
  1) yf.set_config(proxy={"http": p, "https": p})
  2) yf.config.network.proxy = {"http": p, "https": p}
  3) Environment variables HTTP_PROXY/HTTPS_PROXY
- Runs each test in an isolated subprocess (avoids global config races)
- Produces a cleaned proxy list of only working proxies

Typical usage:
  python3 backend/stock_retrieval/verify_yfinance_proxies.py
  python3 backend/stock_retrieval/verify_yfinance_proxies.py --max-workers 40 --timeout 6
  python3 backend/stock_retrieval/verify_yfinance_proxies.py --in-place

Output:
- Writes working proxies to: backend/stock_retrieval/http_proxies_verified.txt
- With --in-place, overwrites the input file with only working proxies.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _now_ms() -> int:
    return int(time.time() * 1000)


def normalize_proxy(proxy: str) -> str:
    p = proxy.strip()
    if not p:
        return p
    if p.startswith("http://") or p.startswith("https://"):
        return p
    return f"http://{p}"


def load_proxy_lines(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"Proxy file not found: {path}")
    out: List[str] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line)
    # de-dupe preserve order
    seen = set()
    unique: List[str] = []
    for p in out:
        p2 = p.strip()
        if not p2 or p2 in seen:
            continue
        seen.add(p2)
        unique.append(p2)
    return unique


@dataclass
class ProxyTestResult:
    proxy: str
    ok: bool
    method: Optional[str]
    elapsed_ms: int
    error: Optional[str]


def _yf_download_smoke(period: str, interval: str, timeout_s: float) -> Tuple[bool, str]:
    """
    Runs a tiny yf.download to validate connectivity via currently-configured proxy.
    Returns (ok, message).
    """
    import yfinance as yf
    import pandas as pd

    # Use a single very liquid ticker for stable availability
    df = yf.download(
        tickers="AAPL",
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

    if df is None or getattr(df, "empty", True):
        return False, "empty dataframe"

    # Single ticker should have simple columns, but yfinance can still return MultiIndex.
    try:
        if isinstance(df.columns, pd.MultiIndex):
            # Try AAPL group_by=ticker shape: df['AAPL']['Close']
            if "AAPL" in df.columns.get_level_values(0):
                sub = df["AAPL"]
                close = sub["Close"] if "Close" in sub.columns else None
            else:
                # Other shape: ('Close','AAPL')
                close = df.xs("AAPL", level=1, axis=1)["Close"]
        else:
            close = df["Close"] if "Close" in df.columns else None
    except Exception as e:
        return False, f"parse error: {e}"

    if close is None:
        return False, "missing Close column"

    try:
        # Ensure at least one non-NaN close
        if close.dropna().empty:
            return False, "Close is all NaN"
    except Exception as e:
        return False, f"Close validation failed: {e}"

    return True, "ok"

def _direct_connectivity_check(period: str, interval: str, timeout_s: float) -> Tuple[bool, str]:
    """
    Before testing proxies, ensure yfinance can reach Yahoo *directly*.

    If direct connectivity fails with curl: (60) on Windows, that's almost always
    a local CA bundle / certificate store issue (not proxy-related). In that case,
    proxy tests are meaningless and will all fail.
    """
    # Ensure no proxy env interferes with the direct test
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        os.environ.pop(k, None)
    try:
        import yfinance as yf
        if hasattr(yf, "set_config"):
            yf.set_config(proxy=None)
        if hasattr(yf, "config") and hasattr(yf.config, "network"):
            yf.config.network.proxy = None
    except Exception:
        pass

    return _yf_download_smoke(period=period, interval=interval, timeout_s=timeout_s)


def _test_one_proxy_in_subprocess(
    proxy: str,
    period: str,
    interval: str,
    timeout_s: float,
    max_attempts: int,
) -> ProxyTestResult:
    """
    Runs inside a subprocess (spawn). Must be top-level picklable.
    """
    t0 = _now_ms()
    p = normalize_proxy(proxy)

    def clear_proxy_env() -> None:
        os.environ.pop("HTTP_PROXY", None)
        os.environ.pop("HTTPS_PROXY", None)
        os.environ.pop("http_proxy", None)
        os.environ.pop("https_proxy", None)

    def clear_yf_proxy() -> None:
        try:
            import yfinance as yf
            if hasattr(yf, "set_config"):
                yf.set_config(proxy=None)
            if hasattr(yf, "config") and hasattr(yf.config, "network"):
                yf.config.network.proxy = None
        except Exception:
            pass

    proxy_dict: Dict[str, str] = {"http": p, "https": p}

    methods: List[Tuple[str, callable]] = []

    def m_set_config() -> None:
        import yfinance as yf
        yf.set_config(proxy=proxy_dict)

    def m_config_network() -> None:
        import yfinance as yf
        # yfinance 1.x has yf.config.network.proxy
        yf.config.network.proxy = proxy_dict

    def m_env() -> None:
        os.environ["HTTP_PROXY"] = p
        os.environ["HTTPS_PROXY"] = p
        os.environ["http_proxy"] = p
        os.environ["https_proxy"] = p

    methods.append(("yf.set_config(dict)", m_set_config))
    methods.append(("yf.config.network.proxy", m_config_network))
    methods.append(("env HTTP(S)_PROXY", m_env))

    last_err: Optional[str] = None

    for name, setter in methods:
        for attempt in range(max_attempts):
            try:
                clear_proxy_env()
                clear_yf_proxy()
                setter()
                ok, msg = _yf_download_smoke(period=period, interval=interval, timeout_s=timeout_s)
                if ok:
                    return ProxyTestResult(proxy=p, ok=True, method=name, elapsed_ms=_now_ms() - t0, error=None)
                last_err = msg
            except Exception as e:
                last_err = str(e)
                # small backoff
                time.sleep(min(0.5, 0.1 * (attempt + 1)))

    return ProxyTestResult(proxy=p, ok=False, method=None, elapsed_ms=_now_ms() - t0, error=last_err or "unknown")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify proxies using yfinance download")
    parser.add_argument(
        "--proxy-file",
        type=str,
        default=str(Path(__file__).parent / "http_proxies.txt"),
        help="Input proxy file (one proxy per line: host:port or http://host:port)",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=str(Path(__file__).parent / "http_proxies_verified.txt"),
        help="Output file path for working proxies only",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite the input proxy file with only working proxies",
    )
    parser.add_argument(
        "--in-place-backup",
        action="store_true",
        default=True,
        help="When using --in-place, create a .bak copy first (default: on)",
    )
    parser.add_argument(
        "--force-in-place",
        action="store_true",
        help="Allow --in-place overwrite even if 0 proxies are verified (NOT recommended)",
    )
    parser.add_argument("--max-workers", type=int, default=30, help="Max parallel subprocesses")
    parser.add_argument("--timeout", type=float, default=8.0, help="yfinance download timeout seconds")
    parser.add_argument("--attempts", type=int, default=1, help="Attempts per method per proxy")
    parser.add_argument("--period", type=str, default="1d", help="yfinance period for test download")
    parser.add_argument("--interval", type=str, default="1m", help="yfinance interval for test download")
    parser.add_argument("--max-keep", type=int, default=200, help="Keep at most N fastest working proxies")
    args = parser.parse_args()

    proxy_path = Path(args.proxy_file)
    out_path = Path(args.output_file)

    proxies_raw = load_proxy_lines(proxy_path)
    proxies = [normalize_proxy(p) for p in proxies_raw if p.strip()]

    print(f"[INFO] Loaded {len(proxies)} proxies from {proxy_path}")
    if not proxies:
        print("[ERROR] No proxies to test")
        return 2

    # Direct connectivity sanity check
    print("[INFO] Checking direct yfinance connectivity (no proxy)...")
    ok_direct, msg_direct = _direct_connectivity_check(
        period=args.period,
        interval=args.interval,
        timeout_s=float(args.timeout),
    )
    if not ok_direct:
        print("[ERROR] Direct yfinance download failed; proxy verification aborted.")
        print(f"[ERROR] Reason: {msg_direct}")
        print("")
        print("Most common fix on Windows for `curl: (60) SSL certificate problem`:")
        print("  - Upgrade cert bundle + curl stack:")
        print("      python -m pip install --upgrade certifi curl_cffi yfinance")
        print("  - Ensure CA bundle is discoverable by curl_cffi:")
        print("      python -c \"import certifi; print(certifi.where())\"")
        print("    Then set one of these env vars to that path and re-run:")
        print("      set SSL_CERT_FILE=C:\\\\path\\\\to\\\\cacert.pem")
        print("      set CURL_CA_BUNDLE=C:\\\\path\\\\to\\\\cacert.pem")
        print("")
        print("If direct works but proxies fail with CONNECT 502/503/400, those proxies do not support HTTPS tunneling.")
        return 2

    # Multiprocessing spawn for Windows safety
    import multiprocessing as mp
    from concurrent.futures import ProcessPoolExecutor, as_completed

    ctx = mp.get_context("spawn")

    started = time.time()
    results: List[ProxyTestResult] = []

    print(f"[INFO] Testing with yf.download(period={args.period}, interval={args.interval})")
    print(f"[INFO] Workers={args.max_workers} timeout={args.timeout}s attempts={args.attempts}")

    with ProcessPoolExecutor(max_workers=args.max_workers, mp_context=ctx) as ex:
        futs = [
            ex.submit(
                _test_one_proxy_in_subprocess,
                p,
                args.period,
                args.interval,
                float(args.timeout),
                int(args.attempts),
            )
            for p in proxies
        ]

        completed = 0
        ok_count = 0

        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            completed += 1
            if r.ok:
                ok_count += 1
                print(f"[OK] {ok_count:03d}  {r.elapsed_ms:5d}ms  {r.method}  {r.proxy}")
            elif completed % 25 == 0:
                # heartbeat
                elapsed = time.time() - started
                print(f"[PROGRESS] {completed}/{len(proxies)} tested | ok={ok_count} | elapsed={elapsed:.1f}s")

    elapsed = time.time() - started
    oks = [r for r in results if r.ok]
    oks.sort(key=lambda x: x.elapsed_ms)
    oks = oks[: int(args.max_keep)]

    # Write output
    out_path.write_text("\n".join([r.proxy for r in oks]) + ("\n" if oks else ""), encoding="utf-8")
    print(f"[INFO] Wrote {len(oks)} working proxies to {out_path}")

    if args.in_place:
        if len(oks) == 0 and not args.force_in_place:
            print("[WARN] 0 proxies verified; refusing to overwrite input file without --force-in-place.")
        else:
            if args.in_place_backup:
                bak = proxy_path.with_suffix(proxy_path.suffix + ".bak")
                try:
                    bak.write_text(proxy_path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
                    print(f"[INFO] Backup written: {bak}")
                except Exception as e:
                    print(f"[WARN] Failed to write backup file: {e}")
            proxy_path.write_text(out_path.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"[INFO] Overwrote input proxy file with working-only list: {proxy_path}")

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Tested: {len(proxies)}")
    print(f"Working: {len([r for r in results if r.ok])}")
    print(f"Kept: {len(oks)}")
    print(f"Elapsed: {elapsed:.1f}s")

    if oks:
        # Show method distribution
        by_method: Dict[str, int] = {}
        for r in results:
            if r.ok and r.method:
                by_method[r.method] = by_method.get(r.method, 0) + 1
        print("Method distribution (working):")
        for k, v in sorted(by_method.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {k}: {v}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

