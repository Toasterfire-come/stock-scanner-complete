from __future__ import annotations

import asyncio
import json
import sys
import webbrowser
from dataclasses import dataclass
from typing import Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table

from .config import load_config, AppConfig
from .proxies import ProxyRotator
from .market import MarketClient
from .float_api import FloatClient
from .utils import sleep_with_jitter, RateLimiter


app = typer.Typer(add_completion=False)
console = Console()


@dataclass
class Match:
    item_id: int
    url: str
    price: Optional[float]
    float_value: Optional[float]


async def scan_once(
    cfg: AppConfig,
    market: MarketClient,
    float_client: FloatClient,
    already_opened_counts: Dict[int, int],
) -> List[Match]:
    matches: List[Match] = []
    for item in cfg.items:
        data = await market.fetch_listing_page(item.url, count=cfg.listing_page_count)
        listings = market.parse_listing_results(data)
        for listing in listings:
            buy_href = listing.get("buy_href")
            price = listing.get("price")
            if price is None or price > item.max_price:
                continue
            # Fetch float for the exact buy link via csfloat, which supports Steam market link
            float_data = await float_client.fetch_float(buy_href)
            if not float_data:
                continue
            float_value = float_data.get("iteminfo", {}).get("floatvalue")
            if float_value is None:
                continue
            if float_value <= item.max_float:
                # respect per-item max open count
                opened = already_opened_counts.get(item.id, 0)
                if opened >= item.max_open:
                    continue
                matches.append(
                    Match(item_id=item.id, url=buy_href, price=price, float_value=float_value)
                )
    return matches


@app.command()
def main(
    config: str = typer.Option(..., "--config", help="Path to config.yaml"),
    proxies: Optional[str] = typer.Option(None, "--proxies", help="Path to proxies.json"),
):
    cfg = load_config(config)
    proxy_rotator = ProxyRotator.from_file(proxies) if proxies else None
    market = MarketClient(cfg.user_agent, cfg.currency, proxy_rotator)
    float_client = FloatClient(cfg.user_agent)

    rate_limiter = RateLimiter(cfg.polling_interval_seconds)
    already_opened_counts: Dict[int, int] = {}

    console.print("Starting CS2 Float Monitor (manual open mode)")
    console.print(f"Items: {[i.id for i in cfg.items]}")

    async def loop() -> None:
        while True:
            async with rate_limiter.throttle():
                matches = await scan_once(cfg, market, float_client, already_opened_counts)
                if matches:
                    table = Table(title="Matches Found")
                    table.add_column("Item ID")
                    table.add_column("Price")
                    table.add_column("Float")
                    table.add_column("URL")
                    for m in matches:
                        table.add_row(str(m.item_id), f"{m.price}", f"{m.float_value}", m.url)
                    console.print(table)
                    for m in matches:
                        opened = already_opened_counts.get(m.item_id, 0)
                        if opened < next(i for i in cfg.items if i.id == m.item_id).max_open:
                            webbrowser.open(m.url, new=2)
                            already_opened_counts[m.item_id] = opened + 1
                await sleep_with_jitter(cfg.polling_interval_seconds)

    try:
        asyncio.run(loop())
    except KeyboardInterrupt:
        console.print("Exiting...")
        raise SystemExit(0)


if __name__ == "__main__":
    main()

