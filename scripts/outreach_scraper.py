#!/usr/bin/env python3
"""
Link Outreach Scraper
---------------------

Purpose:
  - Search the web for pages that accept contributions ("write for us", "guest post", "contribute")
    with finance-related keywords (finance, stocks, stock market, stock screener, stock filter).
  - Rank results by estimated average monthly visitors (if available via API).
  - Generate an AI-ready article prompt (with image guidance) that links back to TradeScanPro.com.
  - Export a CSV with columns: domain, url, title, estimated_monthly_visitors, prompt.

Notes:
  - Prefer official search APIs. This script supports SERPAPI (Google) and Bing Web Search via environment variables.
  - Traffic estimates are attempted via Similarweb API if SIMILARWEB_API_KEY is provided.
  - If APIs are not available, falls back to DuckDuckGo HTML parsing with best-effort extraction and leaves traffic empty.

Environment Variables (optional):
  SERPAPI_API_KEY           -> Use SerpAPI (Google) for search
  BING_SEARCH_API_KEY       -> Use Bing Web Search API for search
  BING_SEARCH_ENDPOINT      -> Optional, defaults to https://api.bing.microsoft.com/v7.0/search
  SIMILARWEB_API_KEY        -> Use Similarweb API for monthly visitors estimation

Usage examples:
  python /workspace/scripts/outreach_scraper.py --max 50 --csv /workspace/outreach_targets.csv
  SERPAPI_API_KEY=xxx SIMILARWEB_API_KEY=yyy python /workspace/scripts/outreach_scraper.py --max 100

"""

import os
import re
import csv
import sys
import time
import json
import math
import argparse
import urllib.parse
from typing import List, Dict, Optional

import datetime as _dt

try:
    import requests
except Exception as e:
    print("This script requires the 'requests' package.", file=sys.stderr)
    raise


FINANCE_KEYWORDS = [
    "finance",
    "stocks",
    "stock market",
    "stock screener",
    "stock filter",
]

INTENT_KEYWORDS = [
    '"write for us"',
    '"guest post"',
    '"submit article"',
    '"contribute"',
    '"become a contributor"',
]

URL_HINTS = [
    "write-for-us",
    "guest-post",
    "guest-posts",
    "submit-article",
    "submit-post",
    "contribute",
    "contributors",
]


def build_queries(finance_keywords: List[str], intent_keywords: List[str]) -> List[str]:
    q_intent = " OR ".join(intent_keywords)
    # Create a few composite queries to broaden coverage
    queries = []
    for k in finance_keywords:
        queries.append(f"({q_intent}) {k}")
    return queries


def search_serpapi(query: str, num: int = 10) -> List[Dict]:
    api_key = os.getenv("SERPAPI_API_KEY", "").strip()
    if not api_key:
        return []
    # SerpAPI Google engine
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": query,
        "num": min(num, 100),
        "api_key": api_key,
    }
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        results = []
        for item in data.get("organic_results", [])[:num]:
            link = item.get("link") or item.get("url")
            if not link:
                continue
            results.append({
                "url": link,
                "title": item.get("title") or "",
                "snippet": item.get("snippet") or "",
            })
        return results
    except Exception:
        return []


def search_bing(query: str, num: int = 10) -> List[Dict]:
    api_key = os.getenv("BING_SEARCH_API_KEY", "").strip()
    if not api_key:
        return []
    endpoint = os.getenv("BING_SEARCH_ENDPOINT", "https://api.bing.microsoft.com/v7.0/search").strip()
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {"q": query, "count": min(num, 50)}
    try:
        r = requests.get(endpoint, params=params, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        web_pages = data.get("webPages", {}).get("value", [])
        results = []
        for item in web_pages[:num]:
            link = item.get("url")
            if not link:
                continue
            results.append({
                "url": link,
                "title": item.get("name") or "",
                "snippet": item.get("snippet") or "",
            })
        return results
    except Exception:
        return []


def search_duckduckgo_html(query: str, num: int = 10) -> List[Dict]:
    # Best-effort HTML parsing without external dependencies (simple regex)
    # DuckDuckGo HTML results endpoint (non-JS):
    base = "https://duckduckgo.com/html/"
    params = {"q": query}
    try:
        r = requests.get(base, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        r.raise_for_status()
        html = r.text
    except Exception:
        return []

    # Extract result links from HTML (simplistic; subject to change by provider)
    # Look for href="/l/?kh=-1&uddg=<url-encoded>"
    urls = []
    for m in re.finditer(r'href="/l/\?kh=[^"]*?uddg=([^"&]+)', html):
        try:
            u = urllib.parse.unquote(m.group(1))
            if u.startswith("http"):
                urls.append(u)
        except Exception:
            continue
        if len(urls) >= num:
            break
    # Return bare results
    return [{"url": u, "title": "", "snippet": ""} for u in urls]


def choose_search_provider() -> str:
    if os.getenv("SERPAPI_API_KEY"):
        return "serpapi"
    if os.getenv("BING_SEARCH_API_KEY"):
        return "bing"
    return "duckduckgo"


def normalized_domain(url: str) -> str:
    try:
        parsed = urllib.parse.urlparse(url)
        host = (parsed.netloc or "").lower()
        if host.startswith("www."):
            host = host[4:]
        return host
    except Exception:
        return ""


def looks_like_contributor_page(url: str, title: str) -> bool:
    lower = (url or "").lower()
    if any(h in lower for h in URL_HINTS):
        return True
    t = (title or "").lower()
    if "write for us" in t or "guest post" in t or "contribute" in t:
        return True
    return False


def estimate_monthly_visitors(domain: str) -> Optional[int]:
    api_key = os.getenv("SIMILARWEB_API_KEY", "").strip()
    if not api_key:
        return None
    # Similarweb visits endpoint: last full month
    today = _dt.date.today().replace(day=1)
    end_month = (today - _dt.timedelta(days=1)).replace(day=1)
    start_month = end_month
    start = start_month.strftime("%Y-%m")
    end = end_month.strftime("%Y-%m")
    url = f"https://api.similarweb.com/v1/website/{domain}/total-traffic-and-engagement/visits"
    params = {
        "api_key": api_key,
        "start_date": start,
        "end_date": end,
        "granularity": "monthly",
    }
    try:
        r = requests.get(url, params=params, timeout=20)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        data = r.json()
        visits = data.get("visits", [])
        if not visits:
            return None
        v = visits[-1].get("visits")
        if v is None:
            return None
        # Return rounded monthly visitors
        return int(round(float(v)))
    except Exception:
        return None


def build_ai_prompt(target_domain: str, target_url: str) -> str:
    # Compose a high-quality prompt guiding an AI to draft an article with images and backlinks
    anchor_pairs = [
        ("professional stock screener", "https://tradescanpro.com/"),
        ("stock screener with alerts", "https://tradescanpro.com/"),
        ("watchlists and portfolios", "https://tradescanpro.com/"),
        ("fair price and insider trading metrics", "https://tradescanpro.com/"),
        ("in-depth individual stock information", "https://tradescanpro.com/"),
    ]
    anchors_text = "; ".join([f"{a} -> {u}" for a, u in anchor_pairs])
    prompt = f"""
You are a finance writer crafting an authoritative, SEO-optimized article for the site {target_domain} (target URL: {target_url}).

Topic: A comprehensive, beginner-to-pro guide covering the U.S. stock market with examples, including how to discover opportunities using screeners.

Requirements:
- Format: 1,600–2,200 words; clear headings (H2/H3), short paragraphs, bullet lists where helpful.
- Include 2–3 royalty-free image suggestions with detailed alt text (e.g., Image Idea: … | Alt: …). Do NOT include actual image URLs.
- Include a short code snippet or table where relevant (e.g., comparing screener criteria).
- Provide actionable steps, common pitfalls, and pro tips.
- Include 2–3 internal link suggestions placeholders for {target_domain} (write as: Internal Link Idea: … — URL TBD).
- Include 2–3 external references to reputable sources (Investopedia, SEC, etc.).
- Include 2–3 contextual backlinks to Trade Scan Pro using natural anchor text; use the following anchor ideas and URLs (select 2–3 where most relevant): {anchors_text}
- Mention Trade Scan Pro’s capabilities: alerts, watchlists, portfolios, fair price, insider trading metrics, in-depth stock information.
- Tone: expert, practical, and trustworthy. Avoid hype. Cite sources where appropriate.
- SEO: compelling title tag (<=60 chars), meta description (<=155 chars), and an FAQ section (4–6 Q&As) suitable for rich results.
Output:
- Title:
- Meta description:
- Outline (H2/H3):
- Article body (with inline Image Idea blocks):
- FAQ:
- Internal Link Ideas:
- External Sources:
""".strip()
    return prompt


def scrape_and_rank(max_results: int = 50) -> List[Dict]:
    provider = choose_search_provider()
    queries = build_queries(FINANCE_KEYWORDS, INTENT_KEYWORDS)
    collected: List[Dict] = []
    seen_urls = set()

    per_query = max(10, math.ceil(max_results / max(1, len(queries))))
    for q in queries:
        if provider == "serpapi":
            results = search_serpapi(q, num=per_query)
        elif provider == "bing":
            results = search_bing(q, num=per_query)
        else:
            results = search_duckduckgo_html(q, num=per_query)

        for r in results:
            url = r.get("url")
            title = r.get("title") or ""
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            if looks_like_contributor_page(url, title):
                collected.append(r)
        time.sleep(0.8)  # polite pacing

        if len(collected) >= max_results:
            break

    # Rank by traffic when possible
    ranked = []
    for r in collected:
        url = r.get("url", "")
        dom = normalized_domain(url)
        visitors = estimate_monthly_visitors(dom)
        ranked.append({
            "domain": dom,
            "url": url,
            "title": r.get("title") or "",
            "snippet": r.get("snippet") or "",
            "monthly_visitors": visitors if visitors is not None else 0,
        })
    ranked.sort(key=lambda x: (x.get("monthly_visitors") or 0), reverse=True)
    return ranked


def export_csv(rows: List[Dict], csv_path: str) -> None:
    fieldnames = ["domain", "url", "title", "monthly_visitors", "prompt"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fieldnames})


def main():
    ap = argparse.ArgumentParser(description="Scrape contribution pages and produce AI prompts + CSV")
    ap.add_argument("--max", type=int, default=50, help="Maximum number of target pages to collect")
    ap.add_argument("--csv", type=str, default="/workspace/outreach_targets.csv", help="Output CSV path")
    args = ap.parse_args()

    targets = scrape_and_rank(max_results=args.max)
    final_rows = []
    for t in targets:
        dom = t.get("domain")
        url = t.get("url")
        prompt = build_ai_prompt(dom, url)
        t_row = {
            "domain": dom,
            "url": url,
            "title": t.get("title") or "",
            "monthly_visitors": t.get("monthly_visitors") or 0,
            "prompt": prompt,
        }
        final_rows.append(t_row)

    export_csv(final_rows, args.csv)
    print(f"Saved {len(final_rows)} rows to {args.csv}")


if __name__ == "__main__":
    main()

