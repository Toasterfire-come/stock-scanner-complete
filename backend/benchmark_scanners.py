#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Benchmark Script for Stock Scanners

Tests each scanner script for 30 seconds and measures:
1. Total tickers processed
2. Successful tickers
3. Rate limit hits
4. Correctness of data
5. Throughput (tickers/sec)

Outputs comparison report to help choose best approach.
"""

import os
import sys
import time
import json
import subprocess
import signal
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")

import django
django.setup()

from stocks.models import Stock
from django.utils import timezone as dj_timezone

# Configuration
BENCHMARK_DURATION = 30  # seconds
TEST_TICKER_COUNT = 200  # Use first 200 tickers for testing


class BenchmarkResult:
    """Store benchmark results for a scanner"""

    def __init__(self, scanner_name: str):
        self.scanner_name = scanner_name
        self.duration = 0
        self.tickers_attempted = 0
        self.tickers_successful = 0
        self.rate_limit_hits = 0
        self.errors = 0
        self.start_time = None
        self.end_time = None
        self.output = ""

    def calculate_metrics(self):
        """Calculate derived metrics"""
        self.throughput = self.tickers_successful / self.duration if self.duration > 0 else 0
        self.success_rate = self.tickers_successful / self.tickers_attempted if self.tickers_attempted > 0 else 0
        self.error_rate = self.errors / self.tickers_attempted if self.tickers_attempted > 0 else 0

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'scanner': self.scanner_name,
            'duration': self.duration,
            'tickers_attempted': self.tickers_attempted,
            'tickers_successful': self.tickers_successful,
            'rate_limit_hits': self.rate_limit_hits,
            'errors': self.errors,
            'throughput': getattr(self, 'throughput', 0),
            'success_rate': getattr(self, 'success_rate', 0),
            'error_rate': getattr(self, 'error_rate', 0)
        }


def verify_data_correctness(limit: int = 50) -> Dict:
    """Verify correctness of recently updated data"""

    # Get recently updated stocks
    recent_stocks = Stock.objects.filter(
        last_updated__isnull=False
    ).order_by('-last_updated')[:limit]

    total_checked = 0
    correct = 0
    issues = []

    for stock in recent_stocks:
        total_checked += 1

        # Check required fields
        if not stock.current_price or stock.current_price <= 0:
            issues.append(f"{stock.ticker}: Invalid price")
            continue

        if not stock.volume or stock.volume < 0:
            issues.append(f"{stock.ticker}: Invalid volume")
            continue

        # Data looks good
        correct += 1

    correctness = correct / total_checked if total_checked > 0 else 0

    return {
        'total_checked': total_checked,
        'correct': correct,
        'correctness': correctness,
        'issues': issues[:10]  # First 10 issues
    }


def run_scanner_benchmark(scanner_name: str, command: List[str]) -> BenchmarkResult:
    """Run a scanner for 30 seconds and collect metrics"""

    print(f"\n{'='*70}")
    print(f"BENCHMARKING: {scanner_name}")
    print(f"{'='*70}")

    result = BenchmarkResult(scanner_name)

    # Record initial state
    initial_update_count = Stock.objects.filter(last_updated__isnull=False).count()

    # Start the scanner
    print(f"[*] Starting scanner...")
    result.start_time = time.time()

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd='/c/Stock-scanner-project/stock-scanner-complete/backend'
        )

        # Let it run for BENCHMARK_DURATION seconds
        print(f"[*] Running for {BENCHMARK_DURATION} seconds...")

        output_lines = []
        start = time.time()

        while time.time() - start < BENCHMARK_DURATION:
            if process.poll() is not None:
                break

            # Read output
            try:
                line = process.stdout.readline()
                if line:
                    output_lines.append(line)
                    # Parse output for metrics
                    if 'rate limit' in line.lower() or '429' in line:
                        result.rate_limit_hits += 1
                    if 'error' in line.lower() or 'failed' in line.lower():
                        result.errors += 1
            except:
                pass

            time.sleep(0.1)

        # Kill the process
        print(f"[*] Stopping scanner...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

        result.end_time = time.time()
        result.duration = result.end_time - result.start_time
        result.output = '\n'.join(output_lines[-50:])  # Last 50 lines

        # Check how many stocks were updated
        final_update_count = Stock.objects.filter(last_updated__isnull=False).count()
        result.tickers_successful = final_update_count - initial_update_count
        result.tickers_attempted = result.tickers_successful + result.errors

        result.calculate_metrics()

        # Print summary
        print(f"\n[*] Results:")
        print(f"    Duration: {result.duration:.1f}s")
        print(f"    Tickers attempted: {result.tickers_attempted}")
        print(f"    Tickers successful: {result.tickers_successful}")
        print(f"    Rate limit hits: {result.rate_limit_hits}")
        print(f"    Errors: {result.errors}")
        print(f"    Throughput: {result.throughput:.2f} tickers/sec")
        print(f"    Success rate: {result.success_rate*100:.1f}%")

        return result

    except Exception as e:
        print(f"[ERROR] Benchmark failed: {e}")
        result.end_time = time.time()
        result.duration = result.end_time - result.start_time if result.start_time else 0
        return result


def main():
    """Run benchmarks on all scanner scripts"""

    print("="*70)
    print("STOCK SCANNER BENCHMARK SUITE")
    print("="*70)
    print(f"Test duration: {BENCHMARK_DURATION} seconds per scanner")
    print(f"Test ticker limit: {TEST_TICKER_COUNT} tickers")
    print("")

    # Define scanners to test
    scanners = [
        {
            'name': 'Ultra Fast 5373 Scanner (No Proxy)',
            'command': ['python', 'ultra_fast_5373_scanner.py', '--max-tickers', str(TEST_TICKER_COUNT)]
        },
        {
            'name': 'YFinance Optimized',
            'command': ['python', 'manage.py', 'update_stocks_yfinance_optimized', '--limit', str(TEST_TICKER_COUNT)]
        },
        {
            'name': 'YFinance V2',
            'command': ['python', 'manage.py', 'update_stocks_yfinance_v2', '--limit', str(TEST_TICKER_COUNT)]
        },
        {
            'name': 'YFinance Standard',
            'command': ['python', 'manage.py', 'update_stocks_yfinance', '--limit', str(TEST_TICKER_COUNT)]
        }
    ]

    results = []

    # Run each scanner
    for scanner in scanners:
        try:
            result = run_scanner_benchmark(scanner['name'], scanner['command'])
            results.append(result)

            # Verify data correctness
            print(f"\n[*] Verifying data correctness...")
            correctness = verify_data_correctness(limit=50)
            print(f"    Correctness: {correctness['correctness']*100:.1f}% ({correctness['correct']}/{correctness['total_checked']})")

            if correctness['issues']:
                print(f"    Issues found: {len(correctness['issues'])}")

            # Wait a bit between tests
            print(f"\n[*] Waiting 5 seconds before next test...")
            time.sleep(5)

        except Exception as e:
            print(f"[ERROR] Failed to benchmark {scanner['name']}: {e}")

    # Generate comparison report
    print("\n" + "="*70)
    print("BENCHMARK COMPARISON REPORT")
    print("="*70)

    print(f"\n{'Scanner':<40} {'Throughput':>12} {'Success':>8} {'Rate Limits':>12}")
    print("-"*70)

    for result in results:
        print(f"{result.scanner_name:<40} "
              f"{result.throughput:>11.2f}/s "
              f"{result.success_rate*100:>7.1f}% "
              f"{result.rate_limit_hits:>12}")

    # Find best performer
    if results:
        best_throughput = max(results, key=lambda x: x.throughput)
        best_success = max(results, key=lambda x: x.success_rate)
        least_rate_limits = min(results, key=lambda x: x.rate_limit_hits)

        print("\n" + "="*70)
        print("RECOMMENDATIONS")
        print("="*70)
        print(f"Best throughput: {best_throughput.scanner_name} ({best_throughput.throughput:.2f} tickers/sec)")
        print(f"Best success rate: {best_success.scanner_name} ({best_success.success_rate*100:.1f}%)")
        print(f"Fewest rate limits: {least_rate_limits.scanner_name} ({least_rate_limits.rate_limit_hits} hits)")

        # Estimate full run time
        total_tickers = 5193  # Based on what we saw
        estimated_time = total_tickers / best_throughput.throughput if best_throughput.throughput > 0 else float('inf')

        print(f"\nEstimated time for {total_tickers} tickers:")
        print(f"  Using {best_throughput.scanner_name}: {estimated_time:.1f} seconds ({estimated_time/60:.1f} minutes)")

        if estimated_time <= 180:
            print(f"  [OK] Target of 180 seconds is ACHIEVABLE!")
        else:
            shortfall = estimated_time - 180
            print(f"  [WARN] Target of 180 seconds is {shortfall:.1f}s too slow")

    # Save results
    report_file = f'benchmark_report_{int(time.time())}.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': time.time(),
            'benchmark_duration': BENCHMARK_DURATION,
            'test_ticker_count': TEST_TICKER_COUNT,
            'results': [r.to_dict() for r in results]
        }, f, indent=2)

    print(f"\n[OK] Full report saved to: {report_file}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user")
    except Exception as e:
        print(f"\nError during benchmark: {e}")
        import traceback
        traceback.print_exc()
