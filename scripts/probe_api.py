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


def login(session: requests.Session, base_url: str, username: str, password: str) -> tuple[bool, str | None, str | None]:
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
                return False, token, None
            # After login, CSRF token may rotate; refresh it
            fresh_token = get_csrf(session, base_url) or token
            # Extract Django session key for Bearer auth fallback
            session_key = session.cookies.get('sessionid') or session.cookies.get('SESSIONID')
            return bool(data.get('success')), fresh_token, session_key
        return False, token, None
    except Exception:
        return False, token, None


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


def probe(session: requests.Session, base_url: str, bearer: str | None = None) -> list[dict]:
    results = []
    for path in GET_ENDPOINTS:
        url = f"{base_url}{path}"
        t0 = time.time()
        try:
            headers = {"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"}
            if bearer:
                headers["Authorization"] = f"Bearer {bearer}"
            r = session.get(url, timeout=15, headers=headers)
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


def _csrf_headers(session: requests.Session, base_url: str, cached_token: str | None, bearer: str | None) -> dict:
    # Always refresh CSRF to keep header aligned with cookie
    token = get_csrf(session, base_url) or cached_token
    headers = {"X-Requested-With": "XMLHttpRequest"}
    if token:
        headers["X-CSRFToken"] = token
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"
    return headers


def exercise_mutations(session: requests.Session, base_url: str, email: str, cached_token: str | None, bearer: str | None) -> list[dict]:
    results: list[dict] = []
    headers = _csrf_headers(session, base_url, cached_token, bearer)

    # 1) Alerts: create -> toggle -> delete
    alert_id = None
    try:
        payload = {"ticker": "AAPL", "target_price": 9999.99, "condition": "above", "email": email}
        r = session.post(f"{base_url}/api/alerts/create/", json=payload, headers=headers, timeout=15)
        ok = r.status_code in (200, 201, 409)  # 409 if duplicate
        data = {}
        try:
            data = r.json() or {}
        except Exception:
            pass
        alert_id = data.get("alert_id") or (data.get("alert") or {}).get("id")
        results.append({"op": "alerts_create", "status": r.status_code, "ok": ok, "alert_id": alert_id})
    except Exception as e:
        results.append({"op": "alerts_create", "status": 0, "ok": False, "error": str(e)[:120]})

    if alert_id:
        try:
            r = session.post(f"{base_url}/api/alerts/{alert_id}/toggle/", json={"isActive": False}, headers=headers, timeout=15)
            results.append({"op": "alerts_toggle_off", "status": r.status_code, "ok": r.status_code < 400})
        except Exception as e:
            results.append({"op": "alerts_toggle_off", "status": 0, "ok": False, "error": str(e)[:120]})
        try:
            r = session.post(f"{base_url}/api/alerts/{alert_id}/toggle/", json={"isActive": True}, headers=headers, timeout=15)
            results.append({"op": "alerts_toggle_on", "status": r.status_code, "ok": r.status_code < 400})
        except Exception as e:
            results.append({"op": "alerts_toggle_on", "status": 0, "ok": False, "error": str(e)[:120]})
        try:
            # Prefer DELETE branch
            r = session.delete(f"{base_url}/api/alerts/{alert_id}/delete/", headers=headers, timeout=15)
            # Fallback to POST if DELETE blocked by intermediary
            if r.status_code >= 400:
                r = session.post(f"{base_url}/api/alerts/{alert_id}/delete/", headers=headers, timeout=15)
            results.append({"op": "alerts_delete", "status": r.status_code, "ok": r.status_code < 400})
        except Exception as e:
            results.append({"op": "alerts_delete", "status": 0, "ok": False, "error": str(e)[:120]})

    # 2) Portfolio: add -> delete
    holding_id = None
    try:
        payload = {"symbol": "AAPL", "shares": 1, "avg_cost": 100.12, "portfolio_name": "Test Portfolio"}
        r = session.post(f"{base_url}/api/portfolio/add/", json=payload, headers=headers, timeout=15)
        ok = r.status_code < 400
        data = {}
        try:
            data = r.json() or {}
        except Exception:
            pass
        holding_id = ((data.get("data") or {}).get("id") or "").strip()
        results.append({"op": "portfolio_add", "status": r.status_code, "ok": ok, "holding_id": holding_id})
    except Exception as e:
        results.append({"op": "portfolio_add", "status": 0, "ok": False, "error": str(e)[:120]})

    if holding_id:
        try:
            r = session.delete(f"{base_url}/api/portfolio/{holding_id}/", headers=headers, timeout=15)
            results.append({"op": "portfolio_delete", "status": r.status_code, "ok": r.status_code < 400})
        except Exception as e:
            results.append({"op": "portfolio_delete", "status": 0, "ok": False, "error": str(e)[:120]})

    # 3) Watchlist: add -> delete
    item_id = None
    try:
        payload = {"symbol": "AAPL", "watchlist_name": "Test Watchlist"}
        r = session.post(f"{base_url}/api/watchlist/add/", json=payload, headers=headers, timeout=15)
        ok = r.status_code < 400
        data = {}
        try:
            data = r.json() or {}
        except Exception:
            pass
        item_id = ((data.get("data") or {}).get("id") or "").strip()
        results.append({"op": "watchlist_add", "status": r.status_code, "ok": ok, "item_id": item_id})
    except Exception as e:
        results.append({"op": "watchlist_add", "status": 0, "ok": False, "error": str(e)[:120]})

    if item_id:
        try:
            r = session.delete(f"{base_url}/api/watchlist/{item_id}/", headers=headers, timeout=15)
            results.append({"op": "watchlist_delete", "status": r.status_code, "ok": r.status_code < 400})
        except Exception as e:
            results.append({"op": "watchlist_delete", "status": 0, "ok": False, "error": str(e)[:120]})

    # 4) Notifications: mark-read (mark_all true) to exercise branch
    try:
        r = session.post(f"{base_url}/api/notifications/mark-read/", json={"mark_all": True}, headers=headers, timeout=15)
        results.append({"op": "notifications_mark_all_read", "status": r.status_code, "ok": r.status_code < 400})
    except Exception as e:
        results.append({"op": "notifications_mark_all_read", "status": 0, "ok": False, "error": str(e)[:120]})

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

    authed, csrf_token, session_key = login(session, args.base_url, args.username, args.password)
    print(json.dumps({"login": authed}, indent=2))

    results = probe(session, args.base_url, bearer=session_key)
    print(json.dumps({"base_url": args.base_url, "results": results}, indent=2))

    if authed:
        mutations = exercise_mutations(session, args.base_url, args.username, csrf_token, session_key)
        print(json.dumps({"mutations": mutations}, indent=2))


if __name__ == "__main__":
    sys.exit(main())

