from __future__ import annotations

import asyncio
import math
import random
import time
from typing import Any, Dict, List, Optional

import httpx
from bs4 import BeautifulSoup
from tenacity import RetryError, retry, stop_after_attempt, wait_exponential_jitter

from .proxies import ProxyRotator, Proxy


STEAM_LISTING_RENDER = (
    "https://steamcommunity.com/market/listings/{appid}/{market_hash_name}/render"
)


class MarketClient:
    def __init__(
        self,
        user_agent: str,
        currency: int,
        proxy_rotator: Optional[ProxyRotator] = None,
    ) -> None:
        self.user_agent = user_agent
        self.currency = currency
        self.proxy_rotator = proxy_rotator

    async def _request_json(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        proxy = self.proxy_rotator.next_available() if self.proxy_rotator else None
        headers = {"User-Agent": self.user_agent}
        timeout = httpx.Timeout(15.0, connect=15.0)
        async with httpx.AsyncClient(
            headers=headers,
            timeout=timeout,
            proxies=proxy.to_httpx_proxies() if proxy else None,
        ) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()

    async def fetch_listing_page(
        self,
        listing_url: str,
        count: int = 20,
        start: int = 0,
    ) -> Dict[str, Any]:
        # listing_url sample: https://steamcommunity.com/market/listings/730/AK-47%20%7C%20Case%20Hardened%20%28Field-Tested%29
        # split into appid and market_hash_name
        try:
            parts = listing_url.split("/market/listings/")[1]
            appid, market_hash_name = parts.split("/", 1)
        except Exception as e:
            raise ValueError(f"Invalid listing URL: {listing_url}") from e

        params = {
            "query": "",
            "start": start,
            "count": count,
            "country": "US",
            "currency": self.currency,
            "language": "english",
        }
        url = STEAM_LISTING_RENDER.format(appid=appid, market_hash_name=market_hash_name)
        return await self._request_json(url, params)

    @staticmethod
    def parse_listing_results(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        # data contains 'results_html' with listings; parse to extract listing ids, actions, and prices
        html = data.get("results_html", "")
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select(".market_listing_row")
        listings: List[Dict[str, Any]] = []
        for row in rows:
            listing_id = row.get("id")
            # Price strings can be in .market_listing_price_with_fee or .sale_price
            price_el = row.select_one(".sale_price, .market_listing_price_with_fee")
            price_str = price_el.get_text(strip=True) if price_el else ""
            buy_button = row.select_one("a.market_listing_buy_button")
            # Asset id often appears in data; but for float API, assetid is needed later when going deeper
            if listing_id and buy_button:
                # Extract numeric price in user's currency where possible
                price_value = MarketClient._parse_price_to_number(price_str)
                listings.append(
                    {
                        "listing_id": listing_id,
                        "price_str": price_str,
                        "price": price_value,
                        "buy_href": buy_button.get("href"),
                    }
                )
        return listings

    @staticmethod
    def _parse_price_to_number(text: str) -> Optional[float]:
        # Attempt to parse common Steam price formats, e.g. $12.34, 12,34 TL, etc.
        if not text:
            return None
        digits = "".join(ch for ch in text if ch.isdigit() or ch in ".,")
        if not digits:
            return None
        # Heuristic: if both , and . present, assume , is thousands sep
        if "," in digits and "." in digits:
            digits = digits.replace(",", "")
        else:
            # If only , present, treat it as decimal
            digits = digits.replace(",", ".")
        try:
            return float(digits)
        except ValueError:
            return None

