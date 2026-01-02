#!/usr/bin/env python3
"""
Daily Scanner Load Test
=======================
Tests proxy switching, rate limiting, and throughput under load

Test Parameters:
- Sample size: 500 tickers (representative of full load)
- Monitors: proxy switches, rate limit compliance, ticker/sec
- Duration: ~2-3 minutes for quick validation
- Extrapolates: 8.5hr completion time estimate
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")
import django
django.setup()

from stocks.models import Stock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("load_test")

# Import the scanner module
sys.path.insert(0, str(Path(__file__).parent / "stock_retrieval"))
import realtime_daily_with_proxies as scanner_module

class LoadTestMetrics:
    """Track detailed metrics during load test"""

    def __init__(self):
        self.start_time = None
        self.end_time = None

        self.total_tickers = 0
        self.successful_fetches = 0
        self.failed_fetches = 0

        self.proxy_switches = 0
        self.proxies_used = set()
        self.proxy_failures = defaultdict(int)

        self.request_times = []
        self.inter_request_delays = []

        self.rate_limit_violations = 0
        self.expected_delay = scanner_module.DELAY_PER_REQUEST

    def start(self):
        """Start timing"""
        self.start_time = time.time()
        self.last_request = time.time()

    def record_request(self, ticker, success, proxy_used, duration):
        """Record a single request"""
        if success:
            self.successful_fetches += 1
        else:
            self.failed_fetches += 1

        self.request_times.append(duration)

        # Track inter-request delay
        now = time.time()
        delay = now - self.last_request
        self.inter_request_delays.append(delay)

        # Check rate limit compliance
        if delay < self.expected_delay * 0.9:  # 10% tolerance
            self.rate_limit_violations += 1

        self.last_request = now

        # Track proxy usage
        if proxy_used:
            self.proxies_used.add(proxy_used)

    def record_proxy_switch(self, from_proxy, to_proxy):
        """Record a proxy switch"""
        self.proxy_switches += 1

    def record_proxy_failure(self, proxy):
        """Record a proxy failure"""
        self.proxy_failures[proxy] += 1

    def finish(self):
        """End timing"""
        self.end_time = time.time()

    def get_summary(self):
        """Get test summary"""
        if not self.start_time or not self.end_time:
            return {}

        total_time = self.end_time - self.start_time
        total_requests = self.successful_fetches + self.failed_fetches

        return {
            "duration_seconds": round(total_time, 2),
            "duration_minutes": round(total_time / 60, 2),

            "total_requests": total_requests,
            "successful": self.successful_fetches,
            "failed": self.failed_fetches,
            "success_rate": round(self.successful_fetches / total_requests * 100, 2) if total_requests > 0 else 0,

            "tickers_per_second": round(total_requests / total_time, 3) if total_time > 0 else 0,
            "target_rate": scanner_module.TARGET_RATE,

            "proxy_switches": self.proxy_switches,
            "unique_proxies_used": len(self.proxies_used),
            "proxy_failures": sum(self.proxy_failures.values()),
            "proxy_failure_rate": round(sum(self.proxy_failures.values()) / total_requests * 100, 2) if total_requests > 0 else 0,

            "avg_request_time": round(sum(self.request_times) / len(self.request_times), 3) if self.request_times else 0,
            "avg_inter_request_delay": round(sum(self.inter_request_delays) / len(self.inter_request_delays), 3) if self.inter_request_delays else 0,
            "expected_delay": round(self.expected_delay, 3),

            "rate_limit_violations": self.rate_limit_violations,
            "rate_limit_compliance": round((1 - self.rate_limit_violations / total_requests) * 100, 2) if total_requests > 0 else 0,
        }

    def extrapolate_full_scan(self, total_tickers):
        """Extrapolate metrics to full ticker set"""
        summary = self.get_summary()

        if summary["tickers_per_second"] == 0:
            return {}

        # Calculate full scan time
        full_scan_seconds = total_tickers / summary["tickers_per_second"]
        full_scan_hours = full_scan_seconds / 3600

        # Estimate success/failure for full scan
        success_rate = summary["success_rate"] / 100
        estimated_successful = int(total_tickers * success_rate)
        estimated_failed = total_tickers - estimated_successful

        return {
            "total_tickers": total_tickers,
            "estimated_duration_hours": round(full_scan_hours, 2),
            "estimated_duration_minutes": round(full_scan_hours * 60, 1),
            "meets_8_5hr_target": full_scan_hours <= 8.5,
            "estimated_successful": estimated_successful,
            "estimated_failed": estimated_failed,
        }


def test_proxy_switching():
    """Test that proxies are actually switching"""
    logger.info("="*80)
    logger.info("TEST 1: Proxy Switching")
    logger.info("="*80)

    # Load proxies
    proxies = scanner_module.load_proxies()

    if not scanner_module.USE_PROXIES or not proxies:
        logger.info("Proxies disabled (USE_PROXIES=False)")
        logger.info("Test skipped - proxies not in use")
        return {"proxy_switching_works": False, "reason": "Proxies disabled"}

    logger.info(f"Loaded {len(proxies)} proxies")

    # Get 20 consecutive proxies
    proxy_sequence = []
    for i in range(min(20, len(proxies) * 2)):
        proxy = scanner_module.get_next_proxy()
        proxy_sequence.append(proxy)

    unique_proxies = set(proxy_sequence)

    logger.info(f"Fetched 20 proxies, {len(unique_proxies)} unique")
    logger.info(f"Proxies: {', '.join(list(unique_proxies)[:5])}...")

    # Check if rotation is working
    is_rotating = len(unique_proxies) > 1

    result = {
        "proxy_switching_works": is_rotating,
        "total_proxies": len(proxies),
        "unique_in_sequence": len(unique_proxies),
        "rotation_detected": is_rotating,
    }

    logger.info("")
    if is_rotating:
        logger.info("[PASS] Proxy rotation is working")
    else:
        logger.warning("[FAIL] Proxy rotation not detected")

    return result


def test_rate_limiting():
    """Test that rate limiting is enforced"""
    logger.info("="*80)
    logger.info("TEST 2: Rate Limiting")
    logger.info("="*80)

    target_rate = scanner_module.TARGET_RATE
    expected_delay = scanner_module.DELAY_PER_REQUEST

    logger.info(f"Target rate: {target_rate} t/s")
    logger.info(f"Expected delay: {expected_delay:.3f}s between requests")

    # Get sample ticker
    sample_ticker = Stock.objects.first()
    if not sample_ticker:
        logger.error("No tickers in database!")
        return {"rate_limiting_works": False, "reason": "No tickers"}

    ticker = sample_ticker.ticker

    # Make 10 consecutive requests
    logger.info(f"Making 10 requests for {ticker}...")

    delays = []
    start = time.time()

    for i in range(10):
        req_start = time.time()
        scanner_module.fetch_stock_with_proxy(ticker)
        req_end = time.time()

        if i > 0:
            delay = req_start - prev_start
            delays.append(delay)
            logger.info(f"  Request {i}: delay={delay:.3f}s")

        prev_start = req_start

    avg_delay = sum(delays) / len(delays) if delays else 0
    total_time = time.time() - start
    actual_rate = 10 / total_time

    logger.info("")
    logger.info(f"Average delay: {avg_delay:.3f}s (expected: {expected_delay:.3f}s)")
    logger.info(f"Actual rate: {actual_rate:.3f} t/s (target: {target_rate} t/s)")

    # Check compliance (within 20% tolerance)
    delay_ok = abs(avg_delay - expected_delay) / expected_delay < 0.2
    rate_ok = abs(actual_rate - target_rate) / target_rate < 0.2

    result = {
        "rate_limiting_works": delay_ok and rate_ok,
        "expected_delay": expected_delay,
        "actual_delay": avg_delay,
        "target_rate": target_rate,
        "actual_rate": actual_rate,
        "within_tolerance": delay_ok and rate_ok,
    }

    logger.info("")
    if delay_ok and rate_ok:
        logger.info("[PASS] Rate limiting is working correctly")
    else:
        logger.warning("[FAIL] Rate limiting not within tolerance")

    return result


def test_throughput_under_load():
    """Test throughput with 500 ticker sample"""
    logger.info("="*80)
    logger.info("TEST 3: Throughput Under Load")
    logger.info("="*80)

    # Get total ticker count
    total_tickers = Stock.objects.count()
    logger.info(f"Total tickers in database: {total_tickers}")

    # Sample size for test
    sample_size = min(500, total_tickers)
    tickers = list(Stock.objects.values_list('ticker', flat=True)[:sample_size])

    logger.info(f"Test sample: {sample_size} tickers")
    logger.info(f"Target rate: {scanner_module.TARGET_RATE} t/s")
    logger.info(f"Expected test duration: {sample_size / scanner_module.TARGET_RATE / 60:.1f} minutes")
    logger.info("")

    # Initialize metrics
    metrics = LoadTestMetrics()
    metrics.total_tickers = sample_size
    metrics.start()

    # Track proxies used
    last_proxy = None

    logger.info("Starting load test...")
    logger.info("")

    for i, ticker in enumerate(tickers, 1):
        req_start = time.time()

        # Fetch data
        data = scanner_module.fetch_stock_with_proxy(ticker)

        req_end = time.time()
        duration = req_end - req_start

        # Get current proxy
        current_proxy = scanner_module.get_next_proxy() if scanner_module.USE_PROXIES else None

        # Track proxy switch
        if current_proxy and last_proxy and current_proxy != last_proxy:
            metrics.record_proxy_switch(last_proxy, current_proxy)

        last_proxy = current_proxy

        # Record request
        metrics.record_request(
            ticker=ticker,
            success=data is not None,
            proxy_used=current_proxy,
            duration=duration
        )

        # Progress update every 50 tickers
        if i % 50 == 0:
            elapsed = time.time() - metrics.start_time
            rate = i / elapsed if elapsed > 0 else 0
            remaining = sample_size - i
            eta = remaining / rate if rate > 0 else 0

            logger.info(
                f"Progress: {i}/{sample_size} ({i/sample_size*100:.0f}%) | "
                f"Rate: {rate:.3f} t/s | "
                f"Success: {metrics.successful_fetches} | "
                f"Failed: {metrics.failed_fetches} | "
                f"ETA: {eta/60:.1f}min"
            )

    metrics.finish()

    # Get summary
    summary = metrics.get_summary()
    extrapolation = metrics.extrapolate_full_scan(total_tickers)

    logger.info("")
    logger.info("="*80)
    logger.info("LOAD TEST RESULTS")
    logger.info("="*80)
    logger.info("")

    logger.info("Test Sample:")
    logger.info(f"  Tickers tested: {summary['total_requests']}")
    logger.info(f"  Duration: {summary['duration_minutes']} minutes")
    logger.info(f"  Success rate: {summary['success_rate']}%")
    logger.info("")

    logger.info("Throughput:")
    logger.info(f"  Actual rate: {summary['tickers_per_second']} t/s")
    logger.info(f"  Target rate: {summary['target_rate']} t/s")
    logger.info(f"  Performance: {summary['tickers_per_second']/summary['target_rate']*100:.1f}% of target")
    logger.info("")

    logger.info("Proxy Usage:")
    logger.info(f"  Proxies enabled: {scanner_module.USE_PROXIES}")
    logger.info(f"  Unique proxies used: {summary['unique_proxies_used']}")
    logger.info(f"  Proxy switches: {summary['proxy_switches']}")
    logger.info(f"  Proxy failures: {summary['proxy_failures']}")
    logger.info("")

    logger.info("Rate Limiting:")
    logger.info(f"  Expected delay: {summary['expected_delay']}s")
    logger.info(f"  Actual avg delay: {summary['avg_inter_request_delay']}s")
    logger.info(f"  Rate limit compliance: {summary['rate_limit_compliance']}%")
    logger.info(f"  Violations: {summary['rate_limit_violations']}")
    logger.info("")

    logger.info("="*80)
    logger.info("FULL SCAN EXTRAPOLATION")
    logger.info("="*80)
    logger.info("")
    logger.info(f"Total tickers: {extrapolation['total_tickers']}")
    logger.info(f"Estimated duration: {extrapolation['estimated_duration_hours']} hours ({extrapolation['estimated_duration_minutes']} minutes)")
    logger.info(f"Meets 8.5hr target: {'YES' if extrapolation['meets_8_5hr_target'] else 'NO'}")
    logger.info(f"Estimated successful: {extrapolation['estimated_successful']}")
    logger.info(f"Estimated failed: {extrapolation['estimated_failed']}")
    logger.info("")

    # Final verdict
    logger.info("="*80)
    logger.info("FINAL VERDICT")
    logger.info("="*80)

    all_tests_pass = True

    # Check success rate
    if summary['success_rate'] >= 95:
        logger.info(f"[PASS] Success rate: {summary['success_rate']}% >= 95%")
    else:
        logger.warning(f"[FAIL] Success rate: {summary['success_rate']}% < 95%")
        all_tests_pass = False

    # Check rate compliance
    if summary['rate_limit_compliance'] >= 90:
        logger.info(f"[PASS] Rate limit compliance: {summary['rate_limit_compliance']}% >= 90%")
    else:
        logger.warning(f"[FAIL] Rate limit compliance: {summary['rate_limit_compliance']}% < 90%")
        all_tests_pass = False

    # Check 8.5hr target
    if extrapolation['meets_8_5hr_target']:
        logger.info(f"[PASS] Can complete in 8.5 hours: {extrapolation['estimated_duration_hours']}h <= 8.5h")
    else:
        logger.warning(f"[FAIL] Cannot complete in 8.5 hours: {extrapolation['estimated_duration_hours']}h > 8.5h")
        all_tests_pass = False

    # Check throughput
    if summary['tickers_per_second'] >= summary['target_rate'] * 0.8:
        logger.info(f"[PASS] Throughput: {summary['tickers_per_second']} t/s >= 80% of target")
    else:
        logger.warning(f"[FAIL] Throughput: {summary['tickers_per_second']} t/s < 80% of target")
        all_tests_pass = False

    logger.info("")
    if all_tests_pass:
        logger.info("="*80)
        logger.info("[SUCCESS] ALL TESTS PASSED - NO OPTIMIZATION NEEDED")
        logger.info("="*80)
    else:
        logger.info("="*80)
        logger.warning("[WARNING] SOME TESTS FAILED - OPTIMIZATION RECOMMENDED")
        logger.info("="*80)

    return {
        "summary": summary,
        "extrapolation": extrapolation,
        "all_tests_pass": all_tests_pass,
    }


def main():
    """Run all load tests"""
    logger.info("")
    logger.info("="*80)
    logger.info("DAILY SCANNER LOAD TEST SUITE")
    logger.info("="*80)
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")

    results = {}

    # Test 1: Proxy switching
    try:
        results['proxy_switching'] = test_proxy_switching()
    except Exception as e:
        logger.error(f"Proxy switching test failed: {e}")
        results['proxy_switching'] = {"error": str(e)}

    logger.info("")
    time.sleep(2)

    # Test 2: Rate limiting
    try:
        results['rate_limiting'] = test_rate_limiting()
    except Exception as e:
        logger.error(f"Rate limiting test failed: {e}")
        results['rate_limiting'] = {"error": str(e)}

    logger.info("")
    time.sleep(2)

    # Test 3: Throughput under load
    try:
        results['throughput'] = test_throughput_under_load()
    except Exception as e:
        logger.error(f"Throughput test failed: {e}")
        results['throughput'] = {"error": str(e)}

    # Save results to file
    output_file = Path(__file__).parent / f"scanner_load_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info("")
    logger.info(f"Results saved to: {output_file}")
    logger.info("")
    logger.info("="*80)
    logger.info("LOAD TEST COMPLETE")
    logger.info("="*80)


if __name__ == "__main__":
    main()
