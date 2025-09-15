#!/usr/bin/env python3
import os
import sys
import json
import time
import argparse
import requests


def get_csrf(session: requests.Session, base_url: str) -> str | None:
    try:
        # Prefer dedicated API CSRF endpoint
        r = session.get(f"{base_url}/api/auth/csrf/", timeout=10)
        if r.ok:
            try:
                data = r.json()
                token = data.get('csrfToken') or data.get('csrf_token') or data.get('token')
                return token
            except Exception:
                pass
        # Fallback to accounts login page to set cookie only
        session.get(f"{base_url}/accounts/login/", timeout=10)
        return None
    except Exception:
        return None


def login(session: requests.Session, base_url: str, username: str, password: str) -> bool:
    token = get_csrf(session, base_url)
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    if token:
        headers['X-CSRFToken'] = token
    try:
        r = session.post(
            f"{base_url}/api/auth/login/",
            json={"username": username, "password": password},
            headers=headers,
            timeout=15,
        )
        if r.status_code == 200:
            try:
                data = r.json()
            except Exception:
                return False
            return bool(data.get('success'))
        return False
    except Exception:
        return False


GET_ENDPOINTS = [
    "/api/health/",
    "/api/endpoint-status/",
    "/api/stocks/",
    "/api/trending/",
    "/api/search/?q=AAPL",
    "/api/market-stats/",
    "/api/stock/AAPL/",
    "/api/realtime/AAPL/",
    "/api/statistics/",
    "/api/portfolio/",
    "/api/watchlist/",
    "/api/news/feed/",
    "/api/news/analytics/",
    "/api/alerts/",  # list
    "/api/billing/history/",
    "/api/billing/current-plan/",
    "/api/billing/stats/",
    "/api/usage-stats/",
    "/api/usage/",
    "/api/usage/history/",
]


def probe(session: requests.Session, base_url: str) -> list[dict]:
    results = []
    for path in GET_ENDPOINTS:
        url = f"{base_url}{path}"
        t0 = time.time()
        try:
            r = session.get(url, timeout=15, headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"})
            elapsed = round((time.time() - t0) * 1000)
            ok = r.status_code < 400
            meta = {}
            try:
                data = r.json()
                if isinstance(data, dict):
                    # include a tiny bit of context
                    meta['keys'] = list(data.keys())[:5]
                    # common contract flags
                    if 'success' in data:
                        meta['success'] = data.get('success')
                    if 'count' in data:
                        meta['count'] = data.get('count')
            except Exception:
                pass
            results.append({
                "method": "GET",
                "path": path,
                "status": r.status_code,
                "ok": ok,
                "ms": elapsed,
                "meta": meta,
            })
        except Exception as e:
            elapsed = round((time.time() - t0) * 1000)
            results.append({
                "method": "GET",
                "path": path,
                "status": 0,
                "ok": False,
                "ms": elapsed,
                "error": str(e)[:120],
            })
    return results


def main():
    parser = argparse.ArgumentParser(description="Probe API GET endpoints")
    parser.add_argument("--base-url", default="https://api.retailtradescanner.com", help="Base URL, e.g., https://api.retailtradescanner.com")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    session = requests.Session()
    session.headers.update({"User-Agent": "api-probe/1.0"})
    session.verify = True

    authed = login(session, args.base_url, args.username, args.password)
    print(json.dumps({"login": authed}, indent=2))

    results = probe(session, args.base_url)
    print(json.dumps({"base_url": args.base_url, "results": results}, indent=2))


if __name__ == "__main__":
    sys.exit(main())

