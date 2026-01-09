#!/usr/bin/env python3
"""
Fetch + verify proxy candidates for yfinance/Yahoo (production-oriented)
========================================================================

What this does:
- Pulls proxy candidates from several public proxy list sources (HTTP/HTTPS).
- Deduplicates.
- Quick-checks HTTPS CONNECT to a Yahoo quote endpoint using `requests` (fast).
- Then verifies a smaller set using a REAL `yf.download()` call in subprocesses
  (this matches your bulk snapshot pipeline much more closely than requests).

Outputs:
- Raw fetched proxies: backend/stock_retrieval/http_proxies_fetched.txt
- Quick-pass proxies: backend/stock_retrieval/http_proxies_quickpass.txt
- yfinance-verified proxies: backend/stock_retrieval/http_proxies_verified.txt

Notes:
- Free/public proxies are extremely unreliable; expect low yield.
- If your environment uses Git Bash, set cert env vars with `export`, not `set`.
  Example:
    export SSL_CERT_FILE="C:/.../certifi/cacert.pem"
    export CURL_CA_BUNDLE="$SSL_CERT_FILE"
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


HERE = Path(__file__).resolve().parent


def normalize_proxy(line: str) -> Optional[str]:
    s = str(line).strip()
    if not s or s.startswith("#"):
        return None
    # Strip scheme if present
    if s.startswith("http://"):
        s = s[len("http://") :]
    if s.startswith("https://"):
        s = s[len("https://") :]
    # keep only host:port-ish
    if "@" in s:
        # keep creds if present; yfinance/curl can handle http://user:pass@host:port
        # (we re-add scheme later)
        pass
    if ":" not in s:
        return None
    return s


def dedupe_preserve_order(items: Iterable[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for x in items:
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


DEFAULT_SOURCES = [
    # ProxyScrape (commonly used; may rate-limit)
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=https&timeout=10000&country=all&ssl=all&anonymity=all",
    # GitHub raw lists
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/https.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/https.txt",
]


def fetch_sources(urls: List[str], *, timeout_s: float) -> List[str]:
    import requests

    proxies: List[str] = []
    for url in urls:
        try:
            r = requests.get(url, timeout=timeout_s, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code != 200:
                continue
            for line in r.text.splitlines():
                p = normalize_proxy(line)
                if p:
                    proxies.append(p)
        except Exception:
            continue
    return dedupe_preserve_order(proxies)


@dataclass
class QuickCheckResult:
    proxy: str
    ok: bool
    elapsed_ms: int


def quick_check_yahoo_https_connect(proxy_hostport: str, *, timeout_s: float) -> QuickCheckResult:
    """
    Fast filter: does this proxy successfully tunnel HTTPS to Yahoo?
    Uses requests for speed. This is a filter only; final verification is yfinance.
    """
    import requests

    p_url = proxy_hostport
    if not (p_url.startswith("http://") or p_url.startswith("https://")):
        p_url = "http://" + p_url

    url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=AAPL"
    headers = {"User-Agent": "Mozilla/5.0"}

    t0 = time.time()
    ok = False
    try:
        r = requests.get(
            url,
            headers=headers,
            proxies={"http": p_url, "https": p_url},
            timeout=timeout_s,
        )
        ok = r.status_code == 200 and "quoteResponse" in r.text
    except Exception:
        ok = False

    return QuickCheckResult(proxy=proxy_hostport, ok=ok, elapsed_ms=int((time.time() - t0) * 1000))


def yfinance_verify(proxies_hostport: List[str], *, max_workers: int, timeout_s: float, attempts: int) -> List[str]:
    """
    True verification using yfinance yf.download(), in subprocesses.
    Reuses the verifier implementation from verify_yfinance_proxies.py.
    """
    # Ensure we can import sibling script
    sys.path.insert(0, str(HERE))
    import multiprocessing as mp
    from concurrent.futures import ProcessPoolExecutor, as_completed

    try:
        from verify_yfinance_proxies import _test_one_proxy_in_subprocess  # type: ignore
    except Exception as e:
        raise RuntimeError(f"Failed to import verify_yfinance_proxies.py helpers: {e}")

    ctx = mp.get_context("spawn")

    # Normalize to full scheme for yfinance verifier
    norm = []
    for p in proxies_hostport:
        p = p.strip()
        if not p:
            continue
        if p.startswith("http://") or p.startswith("https://"):
            norm.append(p)
        else:
            norm.append("http://" + p)

    good: List[Tuple[int, str]] = []
    with ProcessPoolExecutor(max_workers=max_workers, mp_context=ctx) as ex:
        futs = [
            ex.submit(_test_one_proxy_in_subprocess, p, "1d", "1m", float(timeout_s), int(attempts))
            for p in norm
        ]
        for fut in as_completed(futs):
            r = fut.result()
            if getattr(r, "ok", False):
                good.append((int(getattr(r, "elapsed_ms", 10**9)), str(getattr(r, "proxy", ""))))

    good.sort(key=lambda x: x[0])
    return [p for _, p in good]


def write_list(path: Path, items: List[str]) -> None:
    path.write_text("\n".join(items) + ("\n" if items else ""), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch + verify proxies for Yahoo/yfinance")
    parser.add_argument("--sources", nargs="*", default=DEFAULT_SOURCES, help="Proxy list source URLs")
    parser.add_argument("--fetch-timeout", type=float, default=12.0, help="Timeout for fetching sources (seconds)")
    parser.add_argument("--max-fetch", type=int, default=20000, help="Max proxies to keep after fetch/dedupe")

    parser.add_argument("--quick-timeout", type=float, default=3.0, help="Timeout for quick Yahoo CONNECT check")
    parser.add_argument("--quick-workers", type=int, default=80, help="Parallel workers for quick check")
    parser.add_argument("--max-quickpass", type=int, default=800, help="Max proxies to keep after quick check")

    parser.add_argument("--yf-timeout", type=float, default=12.0, help="Timeout for yfinance verification download")
    parser.add_argument("--yf-workers", type=int, default=20, help="Parallel subprocesses for yfinance verification")
    parser.add_argument("--yf-attempts", type=int, default=1, help="Attempts per proxy during yfinance verification")
    parser.add_argument("--max-verified", type=int, default=200, help="Keep top N verified proxies by speed")

    parser.add_argument("--out-fetched", type=str, default=str(HERE / "http_proxies_fetched.txt"))
    parser.add_argument("--out-quickpass", type=str, default=str(HERE / "http_proxies_quickpass.txt"))
    parser.add_argument("--out-verified", type=str, default=str(HERE / "http_proxies_verified.txt"))
    args = parser.parse_args()

    out_fetched = Path(args.out_fetched)
    out_quickpass = Path(args.out_quickpass)
    out_verified = Path(args.out_verified)

    print(f"[INFO] Fetching proxies from {len(args.sources)} sources...")
    fetched = fetch_sources(list(args.sources), timeout_s=float(args.fetch_timeout))
    if args.max_fetch and len(fetched) > int(args.max_fetch):
        fetched = fetched[: int(args.max_fetch)]
    print(f"[INFO] Fetched+deduped: {len(fetched)}")
    write_list(out_fetched, fetched)
    print(f"[INFO] Wrote: {out_fetched}")

    if not fetched:
        print("[ERROR] No proxies fetched")
        return 2

    print(f"[INFO] Quick-checking HTTPS CONNECT to Yahoo (timeout={args.quick_timeout}s)...")
    from concurrent.futures import ThreadPoolExecutor, as_completed

    quick_ok: List[Tuple[int, str]] = []
    with ThreadPoolExecutor(max_workers=int(args.quick_workers)) as ex:
        futs = [ex.submit(quick_check_yahoo_https_connect, p, timeout_s=float(args.quick_timeout)) for p in fetched]
        checked = 0
        for fut in as_completed(futs):
            r = fut.result()
            checked += 1
            if r.ok:
                quick_ok.append((r.elapsed_ms, r.proxy))
            if checked % 500 == 0:
                print(f"[PROGRESS] quick checked {checked}/{len(fetched)} ok={len(quick_ok)}")
            if args.max_quickpass and len(quick_ok) >= int(args.max_quickpass):
                # stop early once we have enough candidates
                break

    quick_ok.sort(key=lambda x: x[0])
    quickpass = [p for _, p in quick_ok]
    write_list(out_quickpass, quickpass)
    print(f"[INFO] Quick-pass: {len(quickpass)} (wrote {out_quickpass})")

    if not quickpass:
        print("[WARN] 0 proxies passed the Yahoo HTTPS CONNECT quick check.")
        print("[WARN] Public proxies often fail HTTPS tunneling; try different sources or paid proxies.")
        return 0

    print(f"[INFO] Verifying with yfinance yf.download() (workers={args.yf_workers}, timeout={args.yf_timeout}s)...")
    verified = yfinance_verify(
        quickpass,
        max_workers=int(args.yf_workers),
        timeout_s=float(args.yf_timeout),
        attempts=int(args.yf_attempts),
    )
    if args.max_verified and len(verified) > int(args.max_verified):
        verified = verified[: int(args.max_verified)]
    write_list(out_verified, verified)
    print(f"[INFO] Verified: {len(verified)} (wrote {out_verified})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

