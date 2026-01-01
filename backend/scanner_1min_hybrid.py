#!/usr/bin/env python3
"""
1-Minute Hybrid Scanner - WebSocket Prices Only
================================================
Runs every minute to update prices via WebSocket streaming

Features:
- WebSocket for real-time prices (NO rate limits)
- Updates: current_price, price_change, price_change_percent
- Runs continuously every 60 seconds
- Fast execution (<60s for 8782 tickers)
"""

import os
import sys
import django
import asyncio
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Set
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

    @sync_to_async
    def get_all_tickers(self):
        """Get all tickers from database"""
        return list(Stock.objects.values_list('ticker', flat=True))

    def websocket_message_handler(self, message):
        """Handle WebSocket messages - store price updates"""
        ticker = message.get('id', '')
        if ticker:
            self.websocket_updates[ticker] = {
                'current_price': message.get('price'),
                'price_change': message.get('change'),
                'price_change_percent': message.get('change_percent'),
                'timestamp': datetime.now()
            }

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

                # Update from WebSocket data (real-time prices)
                if ws_data.get('current_price'):
                    stock.current_price = ws_data['current_price']
                if ws_data.get('price_change') is not None:
                    stock.price_change = ws_data['price_change']
                if ws_data.get('price_change_percent') is not None:
                    stock.price_change_percent = ws_data['price_change_percent']

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
        print(f"[INFO] Found {len(tickers)} tickers in database\n")

        # Clear previous updates
        self.websocket_updates = {}

        # Fetch prices via WebSocket (60 second timeout)
        await self.fetch_realtime_prices_websocket(tickers, timeout=60)

        # Update database
        successful, failed = await self.update_database()

        # Results
        total_time = time.time() - start_time
        rate = len(tickers) / total_time if total_time > 0 else 0
        success_rate = (successful / len(tickers)) * 100 if tickers else 0

        print(f"\n{'='*80}")
        print("SCAN COMPLETE")
        print(f"{'='*80}")
        print(f"Total tickers: {len(tickers)}")
        print(f"WebSocket updates: {len(self.websocket_updates)}")
        print(f"Successfully updated: {successful} ({success_rate:.1f}%)")
        print(f"Failed: {failed}")
        print(f"Total time: {total_time:.1f}s")
        print(f"Rate: {rate:.1f} tickers/second")
        print(f"Next scan in 60s\n")

    async def run_continuous(self):
        """Run scanner continuously every minute"""
        print("="*80)
        print("1-MINUTE PRICE SCANNER (WEBSOCKET)")
        print("="*80)
        print("Updates prices every 60 seconds")
        print("Press Ctrl+C to stop")
        print("="*80)

        while True:
            try:
                await self.run_once()

                # Wait 60 seconds before next scan
                print(f"[SLEEP] Waiting 60 seconds until next scan...")
                await asyncio.sleep(60)

            except KeyboardInterrupt:
                print("\n[STOP] Scanner stopped by user")
                break
            except Exception as e:
                print(f"\n[ERROR] Scan failed: {e}")
                print("Retrying in 60s...")
                await asyncio.sleep(60)


async def main():
    scanner = OneMinuteScanner()
    await scanner.run_continuous()


if __name__ == "__main__":
    asyncio.run(main())
