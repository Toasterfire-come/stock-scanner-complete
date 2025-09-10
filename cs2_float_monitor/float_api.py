from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter


CSGOFLOAT_ITEM_ENDPOINT = "https://api.csgofloat.com/"


class FloatClient:
    def __init__(self, user_agent: str) -> None:
        self.user_agent = user_agent

    @retry(stop=stop_after_attempt(3), wait=wait_exponential_jitter(initial=0.5, max=3))
    async def fetch_float(
        self,
        market_url: str,
        listing_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        # CSGOFloat supports either inspecting link or marketplace listing URL for Steam Community
        params = {
            "url": market_url,
        }
        headers = {"User-Agent": self.user_agent}
        timeout = httpx.Timeout(15.0, connect=15.0)
        async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
            r = await client.get(CSGOFLOAT_ITEM_ENDPOINT, params=params)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            data = r.json()
            return data

