#!/usr/bin/env python3
"""
Fetch + verify proxy candidates for yfinance/Yahoo (production-oriented)
========================================================================

What this does:
- Pulls proxy candidates from several public proxy list sources (HTTP/HTTPS).
- Deduplicates.
- Quick-checks using REAL `yf.download()` in subprocesses (fast but representative).
- Then verifies a smaller set with a longer timeout using REAL `yf.download()` again.

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
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


HERE = Path(__file__).resolve().parent
POOL_JSON_DEFAULT = HERE / "http_proxies_gold.json"


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

def _tcp_probe(host: str, port: int, *, timeout_s: float) -> bool:
    import socket

    try:
        with socket.create_connection((host, int(port)), timeout=float(timeout_s)):
            return True
    except Exception:
        return False


def _split_hostport(p: str) -> Optional[Tuple[str, int]]:
    s = str(p).strip()
    if s.startswith("http://"):
        s = s[len("http://") :]
    elif s.startswith("https://"):
        s = s[len("https://") :]
    if ":" not in s:
        return None
    host, port_s = s.rsplit(":", 1)
    try:
        return host.strip(), int(port_s.strip())
    except Exception:
        return None


def prefilter_https_connect(
    candidates: List[str],
    *,
    timeout_s: float,
    max_workers: int,
    stop_after: Optional[int],
) -> List[Tuple[float, str]]:
    """
    Stage C/D prefilter:
    - TCP reachability
    - HTTPS GET to example.com through proxy (CONNECT capability)
    - HTTPS GET to Yahoo quote endpoint through proxy (Yahoo not blocking)

    Returns list of (latency_seconds, proxy_url) sorted by latency.
    """
    import requests
    from concurrent.futures import ThreadPoolExecutor, as_completed

    example_url = "https://example.com/"
    yahoo_url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=AAPL"
    headers = {"User-Agent": "Mozilla/5.0"}

    def test(proxy_url: str) -> Optional[Tuple[float, str]]:
        hp = _split_hostport(proxy_url)
        if hp and not _tcp_probe(hp[0], hp[1], timeout_s=min(1.5, float(timeout_s))):
            return None

        proxies = {"http": proxy_url, "https": proxy_url}
        try:
            t0 = time.time()
            r1 = requests.get(example_url, headers=headers, proxies=proxies, timeout=float(timeout_s))
            if r1.status_code not in (200, 301, 302):
                return None
            r2 = requests.get(yahoo_url, headers=headers, proxies=proxies, timeout=float(timeout_s))
            if r2.status_code != 200 or "quoteResponse" not in r2.text:
                return None
            return (time.time() - t0), proxy_url
        except Exception:
            return None

    good: List[Tuple[float, str]] = []
    if not candidates:
        return good

    with ThreadPoolExecutor(max_workers=int(max_workers)) as ex:
        futs = [ex.submit(test, p) for p in candidates]
        for fut in as_completed(futs):
            res = fut.result()
            if not res:
                continue
            good.append(res)
            if stop_after is not None and len(good) >= int(stop_after):
                break

    good.sort(key=lambda x: x[0])
    return good


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


def yfinance_verify(
    proxies_hostport: List[str],
    *,
    max_workers: int,
    timeout_s: float,
    attempts: int,
    stop_after: Optional[int] = None,
) -> List[str]:
    """
    True verification using yfinance yf.download(), in subprocesses.
    Reuses the verifier implementation from verify_yfinance_proxies.py.
    """
    # Ensure we can import sibling script
    sys.path.insert(0, str(HERE))
    import multiprocessing as mp
    from concurrent.futures import ProcessPoolExecutor, as_completed

    try:
        from verify_yfinance_proxies import _test_one_proxy_in_subprocess, _direct_connectivity_check  # type: ignore
    except Exception as e:
        raise RuntimeError(f"Failed to import verify_yfinance_proxies.py helpers: {e}")

    # Sanity check: if direct yfinance can't reach Yahoo, proxy verification is meaningless.
    ok_direct, msg_direct = _direct_connectivity_check(period="1d", interval="1m", timeout_s=min(15.0, timeout_s))
    if not ok_direct:
        raise RuntimeError(f"Direct yfinance connectivity failed (no proxy). Reason: {msg_direct}")

    ctx = mp.get_context("spawn")

    # Keep as host:port (no scheme) so verifier can try http:// and https://.
    norm = []
    for p in proxies_hostport:
        p = p.strip()
        if not p:
            continue
        norm.append(p)

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
                if stop_after is not None and len(good) >= int(stop_after):
                    # Best effort to stop early once we have enough working proxies.
                    break

    good.sort(key=lambda x: x[0])
    return [p for _, p in good]


def write_list(path: Path, items: List[str]) -> None:
    path.write_text("\n".join(items) + ("\n" if items else ""), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch + verify proxies for Yahoo/yfinance")
    parser.add_argument("--sources", nargs="*", default=DEFAULT_SOURCES, help="Proxy list source URLs")
    parser.add_argument("--fetch-timeout", type=float, default=12.0, help="Timeout for fetching sources (seconds)")
    parser.add_argument("--max-fetch", type=int, default=20000, help="Max proxies to keep after fetch/dedupe")

    parser.add_argument("--shuffle", action="store_true", help="Shuffle fetched proxies before verification")

    parser.add_argument(
        "--prefilter-timeout",
        type=float,
        default=3.0,
        help="Timeout for HTTPS CONNECT prefilter (requests) (seconds)",
    )
    parser.add_argument(
        "--prefilter-workers",
        type=int,
        default=120,
        help="Parallelism for HTTPS CONNECT prefilter (threads)",
    )
    parser.add_argument(
        "--max-prefilter-pass",
        type=int,
        default=600,
        help="Stop prefilter after N currently-working Yahoo proxies (low yield is expected)",
    )

    parser.add_argument("--quick-yf-timeout", type=float, default=4.0, help="Timeout for quick yfinance verification")
    parser.add_argument("--quick-yf-workers", type=int, default=12, help="Parallel subprocesses for quick yfinance check")
    parser.add_argument("--quick-yf-attempts", type=int, default=1, help="Attempts per proxy during quick yfinance check")
    parser.add_argument("--max-quickpass", type=int, default=400, help="Stop quick check after N working proxies")

    parser.add_argument("--yf-timeout", type=float, default=12.0, help="Timeout for yfinance verification download")
    parser.add_argument("--yf-workers", type=int, default=20, help="Parallel subprocesses for yfinance verification")
    parser.add_argument("--yf-attempts", type=int, default=1, help="Attempts per proxy during yfinance verification")
    parser.add_argument("--max-verified", type=int, default=200, help="Keep top N verified proxies by speed")

    parser.add_argument("--out-fetched", type=str, default=str(HERE / "http_proxies_fetched.txt"))
    parser.add_argument("--out-quickpass", type=str, default=str(HERE / "http_proxies_quickpass.txt"))
    parser.add_argument("--out-verified", type=str, default=str(HERE / "http_proxies_verified.txt"))
    parser.add_argument(
        "--out-pool-json",
        type=str,
        default=str(POOL_JSON_DEFAULT),
        help="Persisted proxy pool stats JSON (reused across runs)",
    )
    args = parser.parse_args()

    out_fetched = Path(args.out_fetched)
    out_quickpass = Path(args.out_quickpass)
    out_verified = Path(args.out_verified)
    out_pool_json = Path(args.out_pool_json)

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

    if args.shuffle:
        random.shuffle(fetched)

    # Expand to proxy URL candidates for prefilter (http:// + https://)
    try:
        from backend.stock_retrieval.proxy_pool import candidate_proxy_urls  # type: ignore
    except Exception:
        sys.path.insert(0, str(HERE))
        from proxy_pool import candidate_proxy_urls  # type: ignore

    prefilter_candidates: List[str] = []
    for hp in fetched:
        prefilter_candidates.extend(candidate_proxy_urls(hp))
    prefilter_candidates = dedupe_preserve_order(prefilter_candidates)

    print(
        "[INFO] Prefiltering proxies for HTTPS CONNECT + Yahoo reachability "
        f"(threads={args.prefilter_workers}, timeout={args.prefilter_timeout}s)..."
    )
    prefiltered = prefilter_https_connect(
        prefilter_candidates,
        timeout_s=float(args.prefilter_timeout),
        max_workers=int(args.prefilter_workers),
        stop_after=int(args.max_prefilter_pass) if args.max_prefilter_pass else None,
    )
    prefilter_pass = [p for _lat, p in prefiltered]
    if prefilter_pass:
        print(f"[INFO] Prefilter pass: {len(prefilter_pass)}/{len(prefilter_candidates)}")
    else:
        print(f"[WARN] Prefilter pass: 0/{len(prefilter_candidates)}")
        print("[WARN] Proceeding to yfinance verification anyway (may be slow / low yield).")
        prefilter_pass = prefilter_candidates

    print(
        "[INFO] Quick-checking proxies via yfinance yf.download() "
        f"(workers={args.quick_yf_workers}, timeout={args.quick_yf_timeout}s)... "
        "(proxy setup mirrors daily scanner via yf.set_config(proxy=...) first)"
    )
    try:
        quickpass = yfinance_verify(
            prefilter_pass,
            max_workers=int(args.quick_yf_workers),
            timeout_s=float(args.quick_yf_timeout),
            attempts=int(args.quick_yf_attempts),
            stop_after=int(args.max_quickpass) if args.max_quickpass else None,
        )
    except Exception as e:
        print(f"[ERROR] Quick yfinance verification failed: {e}")
        return 2

    write_list(out_quickpass, quickpass)
    print(f"[INFO] Quick-pass: {len(quickpass)} (wrote {out_quickpass})")

    if not quickpass:
        print("[WARN] 0 proxies passed quick yfinance verification.")
        print("[WARN] Public proxies are often unusable for yfinance/Yahoo; try different sources or paid proxies.")
        return 0

    print(f"[INFO] Verifying with yfinance yf.download() (workers={args.yf_workers}, timeout={args.yf_timeout}s)...")
    try:
        verified = yfinance_verify(
        quickpass,
        max_workers=int(args.yf_workers),
        timeout_s=float(args.yf_timeout),
        attempts=int(args.yf_attempts),
        stop_after=int(args.max_verified) if args.max_verified else None,
        )
    except Exception as e:
        print(f"[ERROR] Full yfinance verification failed: {e}")
        return 2
    if args.max_verified and len(verified) > int(args.max_verified):
        verified = verified[: int(args.max_verified)]
    write_list(out_verified, verified)
    print(f"[INFO] Verified: {len(verified)} (wrote {out_verified})")

    # Persist proxy pool stats (best-effort)
    try:
        from backend.stock_retrieval.proxy_pool import ProxyPool  # type: ignore
    except Exception:
        sys.path.insert(0, str(HERE))
        from proxy_pool import ProxyPool  # type: ignore

    pool = ProxyPool.load(out_pool_json)
    now_ts = time.time()
    # Mark first-seen for anything we touched
    for p in prefilter_candidates:
        s = pool.upsert(p)
        if s.first_seen_ts is None:
            s.first_seen_ts = now_ts

    # Prefilter metadata
    for lat, p in prefiltered:
        s = pool.upsert(p)
        s.last_verified_ts = now_ts
        s.supports_https_connect = True
        s.example_ok = True
        s.yahoo_ok = True
        pool.record_success(p, latency_ms=float(lat) * 1000.0)

    # yfinance verified metadata
    for p in verified:
        s = pool.upsert(p)
        s.last_verified_ts = now_ts
        s.yfinance_ok = True
        # Treat yfinance verification as a "success" too, but don't override latency too aggressively.
        pool.record_success(p)

    out_pool_json.parent.mkdir(parents=True, exist_ok=True)
    pool.save(out_pool_json)
    print(f"[INFO] Wrote proxy pool stats: {out_pool_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

