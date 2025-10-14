#!/usr/bin/env python3
"""
Proxy Scraper + Validator
- Scrapes free HTTP(S) proxies from multiple public sources
- Validates them against Yahoo Finance quote endpoint
- Outputs a JSON file consumable by enhanced_stock_retrieval_working.py

CLI:
  -threads N            Number of concurrent validators (default: 50)
  -timeout SECONDS      Per-request timeout for validation (default: 5)
  -output PATH          Output JSON file path (required)
  -limit N              Cap number of scraped proxies to test (optional)
  -sources CSV          Optional comma-separated list of source URLs

Exit code 0 on success; prints brief stats to stdout as hints for caller logs.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import sys
import time
from typing import Iterable

import requests

DEFAULT_SOURCES: list[str] = [
    # Proxyscrape
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=https&timeout=5000&country=all&ssl=yes&anonymity=all",
    # Public GitHub lists
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/https.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/https.txt",
    "https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/https.txt",
    # Proxy-list.download
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://www.proxy-list.download/api/v1/get?type=https",
]

# SOCKS proxy sources (often more reliable for HTTPS)
SOCKS4_SOURCES: list[str] = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
]
SOCKS5_SOURCES: list[str] = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
]

IP_PORT_RE = re.compile(r"^\s*(?P<ip>(?:\d{1,3}\.){3}\d{1,3}):(?P<port>\d{2,5})\s*$")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Free proxy scraper and validator")
    p.add_argument("-threads", type=int, default=50, help="Concurrent workers for validation")
    p.add_argument("-timeout", type=int, default=5, help="Per-request timeout seconds")
    p.add_argument("-output", type=str, required=True, help="Output JSON file path")
    p.add_argument("-limit", type=int, default=None, help="Max proxies to validate")
    p.add_argument("-sources", type=str, default=None, help="Override sources (comma-separated URLs)")
    return p.parse_args()


def fetch_text(url: str, timeout_s: int = 8) -> str:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        r = requests.get(url, headers=headers, timeout=timeout_s)
        if r.status_code == 200:
            return r.text
    except Exception:
        return ""
    return ""


def parse_proxies_from_text(text: str) -> list[str]:
    out: list[str] = []
    if not text:
        return out
    for line in text.splitlines():
        m = IP_PORT_RE.match(line)
        if not m:
            continue
        out.append(f"http://{m.group('ip')}:{m.group('port')}")
    return out


def parse_socks_from_text(text: str, scheme: str) -> list[str]:
    out: list[str] = []
    if not text:
        return out
    for line in text.splitlines():
        m = IP_PORT_RE.match(line)
        if not m:
            continue
        out.append(f"{scheme}://{m.group('ip')}:{m.group('port')}")
    return out


def scrape_sources(sources: Iterable[str]) -> list[str]:
    all_proxies: list[str] = []
    seen = set()
    for url in sources:
        txt = fetch_text(url, timeout_s=12)
        candidates = parse_proxies_from_text(txt)
        for p in candidates:
            if p not in seen:
                seen.add(p)
                all_proxies.append(p)
    # Also scrape HTML tables from well-known sites for HTTPS elite proxies
    try:
        from bs4 import BeautifulSoup  # type: ignore
        html_urls = [
            "https://free-proxy-list.net/",
            "https://www.sslproxies.org/",
        ]
        for hurl in html_urls:
            html = fetch_text(hurl, timeout_s=12)
            if not html:
                continue
            soup = BeautifulSoup(html, "lxml")
            table = soup.find("table")
            if not table:
                continue
            for tr in table.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) < 7:
                    continue
                ip = tds[0].get_text(strip=True)
                port = tds[1].get_text(strip=True)
                https_flag = tds[6].get_text(strip=True).lower() in ("yes", "true")
                anonymity = tds[4].get_text(strip=True).lower()
                if https_flag and ip and port and anonymity in ("elite proxy", "anonymous"):
                    px = f"http://{ip}:{port}"
                    if px not in seen:
                        seen.add(px)
                        all_proxies.append(px)
    except Exception:
        pass
    # Also scrape SOCKS sources
    try:
        for url in SOCKS4_SOURCES:
            txt = fetch_text(url, timeout_s=12)
            for p in parse_socks_from_text(txt, "socks4"):
                if p not in seen:
                    seen.add(p)
                    all_proxies.append(p)
        for url in SOCKS5_SOURCES:
            txt = fetch_text(url, timeout_s=12)
            for p in parse_socks_from_text(txt, "socks5"):
                if p not in seen:
                    seen.add(p)
                    all_proxies.append(p)
    except Exception:
        pass
    return all_proxies


TEST_URL = "https://query2.finance.yahoo.com/v7/finance/quote?symbols=AAPL"
SECONDARY_TEST_URL = "https://www.google.com/generate_204"


def validate_proxy(px: str, timeout_s: int) -> tuple[bool, bool, float | None, float | None] | None:
    """Return (conn_ok, yahoo_ok, conn_latency, yahoo_latency) or None if total failure."""
    conn_ok = False
    yh_ok = False
    conn_lat = None
    yh_lat = None
    try:
        s = requests.Session()
        s.proxies = {"http": px, "https": px}
        s.headers.update({"User-Agent": "Mozilla/5.0"})
        t0 = time.time()
        r1 = s.get(SECONDARY_TEST_URL, timeout=timeout_s)
        if r1.status_code in (204, 200):
            conn_ok = True
            conn_lat = time.time() - t0
            t1 = time.time()
            r2 = s.get(TEST_URL, timeout=timeout_s)
            if r2.status_code == 200 and "quoteResponse" in r2.text:
                yh_ok = True
                yh_lat = time.time() - t1
        if not conn_ok and not yh_ok:
            return None
        return (conn_ok, yh_ok, conn_lat, yh_lat)
    except Exception:
        return None


def validate_proxies(proxies: list[str], timeout_s: int, workers: int, limit: int | None) -> tuple[list[tuple[float, str]], list[tuple[float, str]]]:
    if limit is not None and limit > 0:
        proxies = proxies[:limit]
    yahoo_results: list[tuple[float, str]] = []
    conn_results: list[tuple[float, str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        futs = {ex.submit(validate_proxy, px, timeout_s): px for px in proxies}
        for fut in concurrent.futures.as_completed(futs):
            res = fut.result()
            px = futs[fut]
            if res is None:
                continue
            conn_ok, yh_ok, conn_lat, yh_lat = res
            if conn_ok and conn_lat is not None:
                conn_results.append((conn_lat, px))
            if yh_ok and yh_lat is not None:
                yahoo_results.append((yh_lat, px))
    conn_results.sort(key=lambda x: x[0])
    yahoo_results.sort(key=lambda x: x[0])
    return yahoo_results, conn_results


def main() -> None:
    args = parse_args()
    sources = DEFAULT_SOURCES
    if args.sources:
        sources = [s.strip() for s in args.sources.split(",") if s.strip()]

    print("Scraping free proxy sources...")
    proxies = scrape_sources(sources)
    total = len(proxies)
    print(f"Found candidates: {total}")

    if not proxies:
        payload = {"proxies": [], "working_proxies": [], "stats": {"total": 0, "working": 0}}
        with open(args.output, "w") as f:
            json.dump(payload, f)
        print("Working: 0")
        print("Success Rate: 0.0%")
        sys.exit(0)

    print("Validating proxies (connectivity + Yahoo)...")
    yahoo_validated, conn_validated = validate_proxies(proxies, timeout_s=args.timeout, workers=args.threads, limit=args.limit)
    working_yahoo = [px for _, px in yahoo_validated]
    working_conn = [px for _, px in conn_validated]

    payload = {
        "proxies": working_conn,
        "working_proxies": working_conn,
        "yahoo_working_proxies": working_yahoo,
        "stats": {
            "total": total,
            "tested": args.limit if args.limit else total,
            "working_connectivity": len(working_conn),
            "working_yahoo": len(working_yahoo),
            "fastest_connectivity_ms": int(conn_validated[0][0] * 1000) if conn_validated else None,
            "fastest_yahoo_ms": int(yahoo_validated[0][0] * 1000) if yahoo_validated else None,
        },
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source_count": len(sources),
    }
    with open(args.output, "w") as f:
        json.dump(payload, f)

    # Hints for caller logs
    print(f"Working (connectivity): {len(working_conn)}")
    rate_c = (len(working_conn) / (args.limit if args.limit else total)) * 100 if (args.limit if args.limit else total) > 0 else 0.0
    print(f"Connectivity Success Rate: {rate_c:.1f}%")
    print(f"Working (Yahoo): {len(working_yahoo)}")
    rate_y = (len(working_yahoo) / (args.limit if args.limit else total)) * 100 if (args.limit if args.limit else total) > 0 else 0.0
    print(f"Yahoo Success Rate: {rate_y:.1f}%")

    sys.exit(0)


if __name__ == "__main__":
    main()
