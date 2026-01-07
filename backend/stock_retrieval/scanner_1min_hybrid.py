#!/usr/bin/env python3
"""
1-Minute Hybrid Scanner - WebSocket Prices and Volume
======================================================
Runs continuously during market hours (9:30 AM - 4:00 PM EST)
Updates prices and volume via WebSocket streaming every minute

Features:
- WebSocket for real-time data (NO rate limits)
- Updates: current_price, price_change, price_change_percent, volume
- Self-managing: checks market hours and exits when market closes
- Runs continuously every 60 seconds during market hours
- Fast execution (<60s for 8782 tickers)
"""

import os
import sys
import django
import asyncio
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from zoneinfo import ZoneInfo
import yfinance as yf

# Django setup
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import Stock
from asgiref.sync import sync_to_async


class OneMinuteScanner:
    """1-minute price scanner using WebSocket"""

    def __init__(self):
        self.websocket_updates = {}  # Store WebSocket price updates
        self.est_tz = ZoneInfo("America/New_York")
        # IMPORTANT:
        # Yahoo/yfinance streaming is event-driven (no guaranteed per-ticker snapshot),
        # and large universes can hit provider subscription/capacity limits.
        # To avoid "only 50-60 tickers updated" when subscribing to thousands,
        # we rotate through chunks each minute (configurable via env vars).
        self.ws_timeout_seconds = int(os.getenv("YF_WS_TIMEOUT_SECONDS", "60"))
        self.rotate_universe = os.getenv("YF_WS_ROTATE_UNIVERSE", "1").lower() in ("1", "true", "yes")
        self.rotation_chunk_size = int(os.getenv("YF_WS_ROTATION_CHUNK_SIZE", "750"))
        self.rotation_state_path = Path(os.getenv(
            "YF_WS_ROTATION_STATE_PATH",
            str(Path(__file__).with_suffix(".rotation_state.json"))
        ))

    def is_market_hours(self):
        """Check if current time is within market hours (9:30 AM - 4:00 PM EST, weekdays)"""
        now_est = datetime.now(self.est_tz)

        # Check if weekday (Monday=0, Sunday=6)
        if now_est.weekday() >= 5:  # Saturday or Sunday
            return False

        # Check if between 9:30 AM and 4:00 PM EST
        # Market closes AT 4:00 PM, so we use < instead of <=
        market_open = now_est.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now_est.replace(hour=16, minute=0, second=0, microsecond=0)

        return market_open <= now_est < market_close

    @sync_to_async
    def get_all_tickers(self):
        """Get all tickers from database"""
        return list(Stock.objects.values_list('ticker', flat=True))

    def websocket_message_handler(self, message):
        """Handle WebSocket messages - store price and volume updates"""
        ticker = message.get('id', '')
        if ticker:
            # Extract volume from day_volume field (Yahoo's actual field name)
            day_volume_str = message.get('day_volume', '0')
            try:
                volume = int(day_volume_str) if day_volume_str else None
            except (ValueError, TypeError):
                volume = None

            self.websocket_updates[ticker] = {
                'current_price': message.get('price'),
                'price_change': message.get('change'),
                'price_change_percent': message.get('change_percent'),
                'volume': volume,  # Properly extracted from day_volume
                'timestamp': datetime.now()
            }

    def _load_rotation_offset(self) -> int:
        """Load last rotation offset from disk (best-effort)."""
        try:
            if not self.rotation_state_path.exists():
                return 0
            payload = json.loads(self.rotation_state_path.read_text())
            offset = int(payload.get("offset", 0))
            return max(0, offset)
        except Exception:
            # If state is corrupt/unreadable, start from 0.
            return 0

    def _save_rotation_offset(self, offset: int) -> None:
        """Persist rotation offset to disk (best-effort)."""
        try:
            self.rotation_state_path.write_text(json.dumps({"offset": int(offset)}, indent=2))
        except Exception:
            # Non-fatal: rotation state persistence is only an optimization.
            pass

    def select_tickers_for_cycle(self, all_tickers: list[str]) -> tuple[list[str], Optional[dict]]:
        """
        Select a subset of tickers for this 60s websocket listen window.

        Rationale:
        - Streaming is event-driven; you will *not* reliably get an update for every subscribed ticker.
        - Many providers/yfinance implementations effectively cap large subscriptions.
        - Rotating a chunk each minute ensures broad coverage over time.
        """
        total = len(all_tickers)
        if total == 0:
            return [], None

        # If rotation disabled or universe is small, subscribe to all.
        if (not self.rotate_universe) or total <= self.rotation_chunk_size:
            return all_tickers, {"mode": "all", "total": total, "chunk_size": total, "offset": 0}

        offset = self._load_rotation_offset() % total
        end = offset + self.rotation_chunk_size

        if end <= total:
            chunk = all_tickers[offset:end]
        else:
            # Wraparound
            chunk = all_tickers[offset:] + all_tickers[: (end % total)]

        next_offset = (offset + len(chunk)) % total
        self._save_rotation_offset(next_offset)

        return chunk, {"mode": "rotating", "total": total, "chunk_size": len(chunk), "offset": offset, "next_offset": next_offset}

    async def fetch_realtime_prices_websocket(self, tickers, timeout=60):
        """Fetch real-time prices via WebSocket"""
        print(f"[WEBSOCKET] Fetching prices for {len(tickers)} tickers...")

        try:
            async with yf.AsyncWebSocket() as ws:
                await ws.subscribe(tickers)

                try:
                    await asyncio.wait_for(
                        ws.listen(message_handler=self.websocket_message_handler),
                        timeout=timeout
                    )
                except asyncio.TimeoutError:
                    pass

        except Exception as e:
            print(f"[ERROR] WebSocket failed: {e}")

        print(f"[WEBSOCKET] Received {len(self.websocket_updates)} price updates")

    @sync_to_async
    def update_database(self):
        """Update all tickers in database with WebSocket data"""
        print("[DATABASE] Updating database...")

        successful = 0
        failed = 0

        for ticker, ws_data in self.websocket_updates.items():
            try:
                stock = Stock.objects.get(ticker=ticker)

                # Update from WebSocket data (real-time prices and volume)
                if ws_data.get('current_price'):
                    stock.current_price = ws_data['current_price']
                if ws_data.get('price_change') is not None:
                    stock.price_change = ws_data['price_change']
                if ws_data.get('price_change_percent') is not None:
                    stock.price_change_percent = ws_data['price_change_percent']
                if ws_data.get('volume') is not None:
                    stock.volume = ws_data['volume']

                stock.last_updated = datetime.now()
                stock.save()
                successful += 1

            except Stock.DoesNotExist:
                failed += 1
            except Exception as e:
                failed += 1

        return successful, failed

    async def run_once(self):
        """Run one scan cycle"""
        print(f"\n{'='*80}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 1-MINUTE PRICE SCAN")
        print(f"{'='*80}")

        start_time = time.time()

        # Get all tickers
        tickers = await self.get_all_tickers()
        print(f"[INFO] Found {len(tickers)} tickers in database")

        # Choose what we actually subscribe to this minute (chunk rotation)
        tickers_for_ws, rotation_meta = self.select_tickers_for_cycle(tickers)
        if rotation_meta:
            if rotation_meta.get("mode") == "rotating":
                print(
                    f"[INFO] WebSocket universe rotation enabled: "
                    f"subscribing to {rotation_meta['chunk_size']}/{rotation_meta['total']} "
                    f"(offset={rotation_meta['offset']}, next_offset={rotation_meta['next_offset']})"
                )
            else:
                print(f"[INFO] WebSocket subscribing to all {rotation_meta['total']} tickers (rotation disabled/not needed)")
        print("")

        # Clear previous updates
        self.websocket_updates = {}

        # Fetch prices via WebSocket (event-driven; no per-ticker snapshot guarantee)
        await self.fetch_realtime_prices_websocket(tickers_for_ws, timeout=self.ws_timeout_seconds)

        # Update database
        successful, failed = await self.update_database()

        # Results
        total_time = time.time() - start_time
        subscribed_count = len(tickers_for_ws)
        subscribed_rate = subscribed_count / total_time if total_time > 0 else 0
        update_rate = successful / total_time if total_time > 0 else 0
        subscribed_success_rate = (successful / subscribed_count) * 100 if subscribed_count else 0

        print(f"\n{'='*80}")
        print("SCAN COMPLETE")
        print(f"{'='*80}")
        print(f"Total tickers in DB: {len(tickers)}")
        print(f"Subscribed this cycle: {subscribed_count}")
        print(f"WebSocket updates: {len(self.websocket_updates)}")
        print(f"Successfully updated: {successful} ({subscribed_success_rate:.1f}% of subscribed)")
        print(f"Failed: {failed}")
        print(f"Total time: {total_time:.1f}s")
        print(f"Subscribe rate: {subscribed_rate:.1f} tickers/second")
        print(f"DB update rate: {update_rate:.1f} stocks/second")
        if subscribed_count and len(self.websocket_updates) < max(25, int(subscribed_count * 0.10)):
            print(
                f"[WARN] Very low streaming update coverage "
                f"({len(self.websocket_updates)}/{subscribed_count}). "
                f"This is expected if the provider caps subscriptions or only emits events for a subset. "
                f"Try smaller chunks (YF_WS_ROTATION_CHUNK_SIZE) and/or longer listen (YF_WS_TIMEOUT_SECONDS)."
            )
        print(f"Next scan in 60s\n")

    async def run_continuous(self):
        """Run scanner continuously every minute during market hours"""
        print("="*80)
        print("1-MINUTE PRICE SCANNER (WEBSOCKET)")
        print("="*80)
        print("Updates prices every 60 seconds during market hours")
        print("Market hours: 9:30 AM - 4:00 PM EST (weekdays)")
        print("Press Ctrl+C to stop")
        print("="*80)

        # Check if market is open before starting
        if not self.is_market_hours():
            now_est = datetime.now(self.est_tz)
            print(f"\n[INFO] Market is currently closed")
            print(f"[INFO] Current time (EST): {now_est.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"[INFO] Market hours: Monday-Friday, 9:30 AM - 4:00 PM EST")
            print(f"[EXIT] Exiting scanner")
            return

        print(f"\n[INFO] Market is open - starting continuous scan")

        while True:
            try:
                # Check if market is still open
                if not self.is_market_hours():
                    now_est = datetime.now(self.est_tz)
                    print(f"\n{'='*80}")
                    print(f"[MARKET CLOSED] Market hours ended")
                    print(f"[INFO] Current time (EST): {now_est.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                    print(f"[EXIT] Stopping scanner")
                    print(f"{'='*80}")
                    break

                await self.run_once()

                # Check again after scan (in case market closed during scan)
                if not self.is_market_hours():
                    now_est = datetime.now(self.est_tz)
                    print(f"\n{'='*80}")
                    print(f"[MARKET CLOSED] Market hours ended")
                    print(f"[INFO] Current time (EST): {now_est.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                    print(f"[EXIT] Stopping scanner")
                    print(f"{'='*80}")
                    break

                # Wait 60 seconds before next scan
                print(f"[SLEEP] Waiting 60 seconds until next scan...")
                await asyncio.sleep(60)

            except KeyboardInterrupt:
                print("\n[STOP] Scanner stopped by user (Ctrl+C)")
                break
            except Exception as e:
                print(f"\n[ERROR] Scan failed: {e}")
                # Check if market is still open before retrying
                if not self.is_market_hours():
                    print("[EXIT] Market closed, stopping scanner")
                    break
                print("Retrying in 60s...")
                await asyncio.sleep(60)


async def main():
    scanner = OneMinuteScanner()
    await scanner.run_continuous()


if __name__ == "__main__":
    asyncio.run(main())
