#!/usr/bin/env python3
"""
Scanner Load Testing Suite
===========================
Tests both 1-minute and 10-minute scanners with real load to get actual metrics

Tests:
1. 1-Minute Scanner - WebSocket performance
2. 10-Minute Scanner (Original) - Proxy-based performance
3. 10-Minute Scanner (Improved) - Enhanced version performance

Metrics Collected:
- Execution time
- Success rate
- Tickers per second
- Database update rate
- Error types and counts
"""

import os
import sys
import django
import asyncio
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import json

# Django setup
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import Stock
from asgiref.sync import sync_to_async
from scanner_1min_hybrid import OneMinuteScanner
from scanner_10min_metrics import MetricsScanner
from scanner_10min_metrics_improved import ImprovedMetricsScanner


class ScannerLoadTester:
    """Load testing for production scanners"""

    def __init__(self):
        self.results = {}

    def print_header(self, title: str):
        """Print test section header"""
        print(f"\n{'='*80}")
        print(f"{title.center(80)}")
        print(f"{'='*80}\n")

    async def test_1min_scanner(self) -> Dict:
        """Test 1-minute WebSocket scanner"""
        self.print_header("TEST 1: 1-MINUTE WEBSOCKET SCANNER")

        scanner = OneMinuteScanner()

        # Get total tickers
        tickers = await scanner.get_all_tickers()
        total_tickers = len(tickers)

        print(f"[INFO] Testing with {total_tickers} tickers")
        print(f"[INFO] Method: WebSocket streaming")
        print(f"[INFO] Starting test...")

        # Record start state
        start_time = time.time()
        start_updated_count = await sync_to_async(
            lambda: Stock.objects.filter(last_updated__isnull=False).count()
        )()

        # Run one scan
        await scanner.run_once()

        # Record end state
        end_time = time.time()
        elapsed = end_time - start_time

        # Check database updates
        end_updated_count = await sync_to_async(
            lambda: Stock.objects.filter(last_updated__isnull=False).count()
        )()
        db_updates = end_updated_count - start_updated_count

        # Calculate metrics
        websocket_updates = len(scanner.websocket_updates)
        success_rate = (websocket_updates / total_tickers) * 100 if total_tickers > 0 else 0
        tickers_per_sec = total_tickers / elapsed if elapsed > 0 else 0

        results = {
            'scanner': '1-Minute WebSocket',
            'total_tickers': total_tickers,
            'elapsed_seconds': round(elapsed, 2),
            'websocket_updates': websocket_updates,
            'database_updates': db_updates,
            'success_rate': round(success_rate, 2),
            'tickers_per_second': round(tickers_per_sec, 2),
            'meets_60s_target': elapsed < 60,
            'timestamp': datetime.now().isoformat()
        }

        self.print_results(results)
        return results

    async def test_10min_scanner_original(self) -> Dict:
        """Test original 10-minute scanner"""
        self.print_header("TEST 2: 10-MINUTE SCANNER (ORIGINAL)")

        scanner = MetricsScanner()

        # Get total tickers
        tickers = await sync_to_async(
            lambda: list(Stock.objects.values_list('ticker', flat=True))
        )()
        total_tickers = len(tickers)

        print(f"[INFO] Testing with {total_tickers} tickers")
        print(f"[INFO] Method: Batch downloads with proxy rotation")
        print(f"[INFO] Batch size: 100")
        print(f"[INFO] Proxies: {len(scanner.proxies)}")
        print(f"[INFO] Starting test...")

        # Record start time
        start_time = time.time()

        # Run one scan (wrap in sync_to_async since scan_all_tickers is synchronous)
        await sync_to_async(scanner.scan_all_tickers)()

        # Record end time
        elapsed = time.time() - start_time

        # Get stats
        results = {
            'scanner': '10-Minute Original',
            'total_tickers': scanner.stats['total'],
            'elapsed_seconds': round(elapsed, 2),
            'successful': scanner.stats['successful'],
            'failed': scanner.stats['failed'],
            'proxy_failures': scanner.stats['proxy_failures'],
            'success_rate': round((scanner.stats['successful'] / scanner.stats['total']) * 100, 2) if scanner.stats['total'] > 0 else 0,
            'tickers_per_second': round(scanner.stats['total'] / elapsed, 2) if elapsed > 0 else 0,
            'meets_600s_target': elapsed < 600,
            'timestamp': datetime.now().isoformat()
        }

        self.print_results(results)
        return results

    async def test_10min_scanner_improved(self) -> Dict:
        """Test improved 10-minute scanner"""
        self.print_header("TEST 3: 10-MINUTE SCANNER (IMPROVED)")

        scanner = ImprovedMetricsScanner()

        # Get total tickers
        tickers = await sync_to_async(
            lambda: list(Stock.objects.values_list('ticker', flat=True))
        )()
        total_tickers = len(tickers)

        print(f"[INFO] Testing with {total_tickers} tickers")
        print(f"[INFO] Method: Smart retry + no-proxy fallback")
        print(f"[INFO] Batch size: 50")
        print(f"[INFO] Proxies: {len(scanner.proxies)}")
        print(f"[INFO] Fallback enabled: {scanner.no_proxy_fallback}")
        print(f"[INFO] Starting test...")

        # Record start time
        start_time = time.time()

        # Run one scan (wrap in sync_to_async since scan_all_tickers is synchronous)
        await sync_to_async(scanner.scan_all_tickers)()

        # Record end time
        elapsed = time.time() - start_time

        # Get stats
        results = {
            'scanner': '10-Minute Improved',
            'total_tickers': scanner.stats['total'],
            'elapsed_seconds': round(elapsed, 2),
            'successful': scanner.stats['successful'],
            'failed': scanner.stats['failed'],
            'proxy_failures': scanner.stats['proxy_failures'],
            'no_proxy_success': scanner.stats['no_proxy_success'],
            'success_rate': round((scanner.stats['successful'] / scanner.stats['total']) * 100, 2) if scanner.stats['total'] > 0 else 0,
            'tickers_per_second': round(scanner.stats['total'] / elapsed, 2) if elapsed > 0 else 0,
            'meets_600s_target': elapsed < 600,
            'timestamp': datetime.now().isoformat()
        }

        self.print_results(results)
        return results

    def print_results(self, results: Dict):
        """Print test results"""
        print(f"\n{'='*80}")
        print(f"RESULTS: {results['scanner']}")
        print(f"{'='*80}")

        for key, value in results.items():
            if key == 'scanner' or key == 'timestamp':
                continue

            # Format key
            label = key.replace('_', ' ').title()

            # Format value
            if isinstance(value, bool):
                display = "YES" if value else "NO"
            elif isinstance(value, float):
                display = f"{value:,.2f}"
            elif isinstance(value, int):
                display = f"{value:,}"
            else:
                display = str(value)

            print(f"{label:30} {display}")

        print(f"{'='*80}\n")

    @sync_to_async
    def get_ticker_count(self):
        """Get total ticker count (async-safe)"""
        return Stock.objects.count()

    async def run_all_tests(self):
        """Run all scanner tests"""
        print("="*80)
        print("SCANNER LOAD TESTING SUITE".center(80))
        print("="*80)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        ticker_count = await self.get_ticker_count()
        print(f"Total Tickers: {ticker_count:,}")
        print("="*80)

        all_results = {}

        # Test 1: 1-Minute Scanner
        try:
            results_1min = await self.test_1min_scanner()
            all_results['1min_websocket'] = results_1min
        except Exception as e:
            print(f"[ERROR] 1-minute scanner test failed: {e}")
            import traceback
            traceback.print_exc()

        # Test 2: 10-Minute Original
        try:
            results_10min_orig = await self.test_10min_scanner_original()
            all_results['10min_original'] = results_10min_orig
        except Exception as e:
            print(f"[ERROR] 10-minute original test failed: {e}")
            import traceback
            traceback.print_exc()

        # Test 3: 10-Minute Improved
        try:
            results_10min_imp = await self.test_10min_scanner_improved()
            all_results['10min_improved'] = results_10min_imp
        except Exception as e:
            print(f"[ERROR] 10-minute improved test failed: {e}")
            import traceback
            traceback.print_exc()

        # Save results to file
        self.save_results(all_results)

        # Print comparison
        self.print_comparison(all_results)

    def save_results(self, results: Dict):
        """Save test results to JSON file"""
        filename = f"scanner_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = Path(__file__).parent / filename

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n[SAVED] Results saved to: {filename}")

    def print_comparison(self, results: Dict):
        """Print comparison of all scanners"""
        self.print_header("COMPARISON SUMMARY")

        if '1min_websocket' in results:
            r = results['1min_websocket']
            print("1-MINUTE WEBSOCKET SCANNER:")
            print(f"  Time: {r.get('elapsed_seconds', 0):.1f}s | Success: {r.get('success_rate', 0):.1f}% | Rate: {r.get('tickers_per_second', 0):.1f} t/s")
            print(f"  Meets 60s target: {'YES' if r.get('meets_60s_target') else 'NO'}")
            print()

        if '10min_original' in results:
            r = results['10min_original']
            print("10-MINUTE ORIGINAL SCANNER:")
            print(f"  Time: {r.get('elapsed_seconds', 0):.1f}s | Success: {r.get('success_rate', 0):.1f}% | Rate: {r.get('tickers_per_second', 0):.1f} t/s")
            print(f"  Proxy failures: {r.get('proxy_failures', 0)}")
            print(f"  Meets 600s target: {'YES' if r.get('meets_600s_target') else 'NO'}")
            print()

        if '10min_improved' in results:
            r = results['10min_improved']
            print("10-MINUTE IMPROVED SCANNER:")
            print(f"  Time: {r.get('elapsed_seconds', 0):.1f}s | Success: {r.get('success_rate', 0):.1f}% | Rate: {r.get('tickers_per_second', 0):.1f} t/s")
            print(f"  Proxy failures: {r.get('proxy_failures', 0)} | No-proxy success: {r.get('no_proxy_success', 0)}")
            print(f"  Meets 600s target: {'YES' if r.get('meets_600s_target') else 'NO'}")
            print()

        # Winner
        if '10min_original' in results and '10min_improved' in results:
            orig_success = results['10min_original'].get('success_rate', 0)
            imp_success = results['10min_improved'].get('success_rate', 0)

            print("="*80)
            if imp_success > orig_success:
                improvement = imp_success - orig_success
                print(f"WINNER: Improved scanner (+{improvement:.1f}% success rate)")
            elif orig_success > imp_success:
                print(f"WINNER: Original scanner")
            else:
                print("RESULT: Tie")
            print("="*80)


async def main():
    tester = ScannerLoadTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
