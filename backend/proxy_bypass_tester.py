#!/usr/bin/env python3
"""
Proxy Bypass Tester & Configuration Optimizer
==============================================

Comprehensive testing framework for proxy initialization methods,
session configurations, and rate limit bypass techniques.

Tests:
1. Proxy initialization methods (requests, curl_cffi, httpx, etc.)
2. Session configurations (headers, User-Agents, TLS)
3. Proxy types (datacenter, residential, SOCKS5)
4. Bypass techniques (rotation, timing, header randomization)
5. Rate limit detection and recovery

Usage:
    python proxy_bypass_tester.py --test-suite quick
    python proxy_bypass_tester.py --test-proxies proxies.json --sample-size 50
    python proxy_bypass_tester.py --compare-mode --output-report results.json
"""

import os
import sys
import time
import json
import random
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import statistics

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")

import django
django.setup()

import requests
import yfinance as yf

# Import infrastructure
from stock_retrieval.session_factory import ProxyPool, create_requests_session
from stock_retrieval.config import StockRetrievalConfig
from stock_retrieval.ticker_loader import load_combined_tickers

# Try optional dependencies
try:
    from curl_cffi import requests as curl_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

# =====================================================
# CONFIGURATION
# =====================================================

@dataclass
class TesterConfig:
    """Test configuration"""
    test_suite: str = "quick"  # quick, full, custom
    sample_size: int = 20
    proxy_file: Optional[str] = None
    output_report: str = "proxy_test_report.json"
    timeout: int = 10
    max_workers: int = 5
    verbose: bool = True

CONFIG = TesterConfig()

# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'proxy_tester_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

# =====================================================
# USER AGENT COLLECTION
# =====================================================

USER_AGENTS = [
    # Chrome Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",

    # Chrome Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",

    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",

    # Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",

    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",

    # Mobile
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
]

# =====================================================
# TEST RESULT TRACKING
# =====================================================

@dataclass
class TestResult:
    """Individual test result"""
    test_name: str
    method: str
    success: bool
    duration: float
    status_code: Optional[int] = None
    error: Optional[str] = None
    data_quality: float = 0.0  # 0-1 score
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class TestRunner:
    """Manages test execution and results"""

    def __init__(self):
        self.results: List[TestResult] = []
        self.test_tickers = []
        self.proxies: List[str] = []

    def add_result(self, result: TestResult):
        """Add test result"""
        self.results.append(result)

    def get_results_by_method(self, method: str) -> List[TestResult]:
        """Get results for specific method"""
        return [r for r in self.results if r.method == method]

    def get_success_rate(self, method: str) -> float:
        """Calculate success rate for method"""
        results = self.get_results_by_method(method)
        if not results:
            return 0.0
        successes = sum(1 for r in results if r.success)
        return successes / len(results)

    def get_avg_duration(self, method: str) -> float:
        """Get average duration for method"""
        results = self.get_results_by_method(method)
        if not results:
            return 0.0
        durations = [r.duration for r in results if r.success]
        return statistics.mean(durations) if durations else 0.0

    def get_summary(self) -> Dict:
        """Get comprehensive test summary"""
        methods = list(set(r.method for r in self.results))

        summary = {
            'total_tests': len(self.results),
            'methods_tested': len(methods),
            'timestamp': datetime.now().isoformat(),
            'methods': {}
        }

        for method in methods:
            results = self.get_results_by_method(method)
            successes = [r for r in results if r.success]
            failures = [r for r in results if not r.success]

            summary['methods'][method] = {
                'total_tests': len(results),
                'successes': len(successes),
                'failures': len(failures),
                'success_rate': len(successes) / len(results) if results else 0,
                'avg_duration': statistics.mean([r.duration for r in successes]) if successes else 0,
                'min_duration': min([r.duration for r in successes]) if successes else 0,
                'max_duration': max([r.duration for r in successes]) if successes else 0,
                'avg_data_quality': statistics.mean([r.data_quality for r in successes]) if successes else 0,
                'error_types': list(set(r.error for r in failures if r.error))
            }

        # Rank methods by performance
        ranked = sorted(
            summary['methods'].items(),
            key=lambda x: (x[1]['success_rate'], -x[1]['avg_duration']),
            reverse=True
        )

        summary['ranked_methods'] = [
            {
                'method': method,
                'score': data['success_rate'] * (1 / (data['avg_duration'] + 0.1)),
                **data
            }
            for method, data in ranked
        ]

        return summary

runner = TestRunner()

# =====================================================
# TEST IMPLEMENTATIONS
# =====================================================

def test_standard_requests(ticker: str, proxy: Optional[str] = None) -> TestResult:
    """Test standard requests library"""
    start = time.time()

    try:
        session = requests.Session()
        session.headers.update({'User-Agent': random.choice(USER_AGENTS)})

        if proxy:
            session.proxies = {'http': proxy, 'https': proxy}

        ticker_obj = yf.Ticker(ticker, session=session)
        price = ticker_obj.fast_info.last_price

        duration = time.time() - start

        return TestResult(
            test_name=f"standard_requests_{ticker}",
            method="standard_requests",
            success=True,
            duration=duration,
            status_code=200,
            data_quality=1.0 if price else 0.5,
            metadata={'proxy': proxy, 'ticker': ticker}
        )

    except Exception as e:
        duration = time.time() - start
        return TestResult(
            test_name=f"standard_requests_{ticker}",
            method="standard_requests",
            success=False,
            duration=duration,
            error=str(e),
            metadata={'proxy': proxy, 'ticker': ticker}
        )

def test_curl_cffi(ticker: str, proxy: Optional[str] = None) -> TestResult:
    """Test curl_cffi library (browser impersonation)"""
    if not HAS_CURL_CFFI:
        return TestResult(
            test_name=f"curl_cffi_{ticker}",
            method="curl_cffi",
            success=False,
            duration=0.0,
            error="curl_cffi not installed"
        )

    start = time.time()

    try:
        session = curl_requests.Session()
        session.headers.update({'User-Agent': random.choice(USER_AGENTS)})

        if proxy:
            session.proxies = {'http': proxy, 'https': proxy}

        ticker_obj = yf.Ticker(ticker, session=session)
        price = ticker_obj.fast_info.last_price

        duration = time.time() - start

        return TestResult(
            test_name=f"curl_cffi_{ticker}",
            method="curl_cffi",
            success=True,
            duration=duration,
            status_code=200,
            data_quality=1.0 if price else 0.5,
            metadata={'proxy': proxy, 'ticker': ticker}
        )

    except Exception as e:
        duration = time.time() - start
        return TestResult(
            test_name=f"curl_cffi_{ticker}",
            method="curl_cffi",
            success=False,
            duration=duration,
            error=str(e),
            metadata={'proxy': proxy, 'ticker': ticker}
        )

def test_httpx(ticker: str, proxy: Optional[str] = None) -> TestResult:
    """Test httpx library (HTTP/2 support)"""
    if not HAS_HTTPX:
        return TestResult(
            test_name=f"httpx_{ticker}",
            method="httpx",
            success=False,
            duration=0.0,
            error="httpx not installed"
        )

    start = time.time()

    try:
        # Note: yfinance doesn't directly support httpx, so we test the library capability
        # In practice, you'd need to implement custom yfinance requests

        headers = {'User-Agent': random.choice(USER_AGENTS)}
        proxies = {'http://': proxy, 'https://': proxy} if proxy else None

        with httpx.Client(headers=headers, proxies=proxies, timeout=CONFIG.timeout) as client:
            # Test basic connectivity
            response = client.get('https://finance.yahoo.com')

            duration = time.time() - start

            return TestResult(
                test_name=f"httpx_{ticker}",
                method="httpx",
                success=response.status_code == 200,
                duration=duration,
                status_code=response.status_code,
                data_quality=0.5,  # Can't get ticker data without yfinance integration
                metadata={'proxy': proxy, 'ticker': ticker}
            )

    except Exception as e:
        duration = time.time() - start
        return TestResult(
            test_name=f"httpx_{ticker}",
            method="httpx",
            success=False,
            duration=duration,
            error=str(e),
            metadata={'proxy': proxy, 'ticker': ticker}
        )

def test_custom_session_factory(ticker: str, proxy: Optional[str] = None) -> TestResult:
    """Test our custom session factory"""
    start = time.time()

    try:
        session = create_requests_session(proxy=proxy, timeout=CONFIG.timeout)
        ticker_obj = yf.Ticker(ticker, session=session)
        price = ticker_obj.fast_info.last_price

        duration = time.time() - start

        return TestResult(
            test_name=f"custom_factory_{ticker}",
            method="custom_session_factory",
            success=True,
            duration=duration,
            status_code=200,
            data_quality=1.0 if price else 0.5,
            metadata={'proxy': proxy, 'ticker': ticker}
        )

    except Exception as e:
        duration = time.time() - start
        return TestResult(
            test_name=f"custom_factory_{ticker}",
            method="custom_session_factory",
            success=False,
            duration=duration,
            error=str(e),
            metadata={'proxy': proxy, 'ticker': ticker}
        )

def test_no_proxy_baseline(ticker: str) -> TestResult:
    """Test without proxy (baseline)"""
    start = time.time()

    try:
        ticker_obj = yf.Ticker(ticker)
        price = ticker_obj.fast_info.last_price

        duration = time.time() - start

        return TestResult(
            test_name=f"no_proxy_{ticker}",
            method="no_proxy_baseline",
            success=True,
            duration=duration,
            status_code=200,
            data_quality=1.0 if price else 0.5,
            metadata={'ticker': ticker}
        )

    except Exception as e:
        duration = time.time() - start
        return TestResult(
            test_name=f"no_proxy_{ticker}",
            method="no_proxy_baseline",
            success=False,
            duration=duration,
            error=str(e),
            metadata={'ticker': ticker}
        )

def test_header_rotation(ticker: str, proxy: Optional[str] = None) -> TestResult:
    """Test with rotating headers"""
    start = time.time()

    try:
        session = requests.Session()

        # Randomized headers
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.9', 'en-CA,en;q=0.9']),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        session.headers.update(headers)

        if proxy:
            session.proxies = {'http': proxy, 'https': proxy}

        ticker_obj = yf.Ticker(ticker, session=session)
        price = ticker_obj.fast_info.last_price

        duration = time.time() - start

        return TestResult(
            test_name=f"header_rotation_{ticker}",
            method="header_rotation",
            success=True,
            duration=duration,
            status_code=200,
            data_quality=1.0 if price else 0.5,
            metadata={'proxy': proxy, 'ticker': ticker, 'user_agent': headers['User-Agent']}
        )

    except Exception as e:
        duration = time.time() - start
        return TestResult(
            test_name=f"header_rotation_{ticker}",
            method="header_rotation",
            success=False,
            duration=duration,
            error=str(e),
            metadata={'proxy': proxy, 'ticker': ticker}
        )

def test_variable_timing(ticker: str, proxy: Optional[str] = None) -> TestResult:
    """Test with variable request timing"""
    # Add random delay before request
    delay = random.uniform(0.1, 0.5)
    time.sleep(delay)

    start = time.time()

    try:
        session = requests.Session()
        session.headers.update({'User-Agent': random.choice(USER_AGENTS)})

        if proxy:
            session.proxies = {'http': proxy, 'https': proxy}

        ticker_obj = yf.Ticker(ticker, session=session)
        price = ticker_obj.fast_info.last_price

        duration = time.time() - start

        return TestResult(
            test_name=f"variable_timing_{ticker}",
            method="variable_timing",
            success=True,
            duration=duration,
            status_code=200,
            data_quality=1.0 if price else 0.5,
            metadata={'proxy': proxy, 'ticker': ticker, 'pre_delay': delay}
        )

    except Exception as e:
        duration = time.time() - start
        return TestResult(
            test_name=f"variable_timing_{ticker}",
            method="variable_timing",
            success=False,
            duration=duration,
            error=str(e),
            metadata={'proxy': proxy, 'ticker': ticker}
        )

# =====================================================
# ADVANCED TESTS
# =====================================================

def test_burst_requests(tickers: List[str], method_func, proxy: Optional[str] = None) -> Dict:
    """Test burst performance - how many requests before rate limit"""
    logger.info(f"Running burst test with {method_func.__name__}...")

    results = []
    rate_limit_hit = False
    requests_before_limit = 0

    start_time = time.time()

    for ticker in tickers:
        if rate_limit_hit:
            break

        result = method_func(ticker, proxy) if proxy else method_func(ticker)
        results.append(result)

        if not result.success and ("429" in str(result.error) or "Too Many Requests" in str(result.error)):
            rate_limit_hit = True
            requests_before_limit = len(results) - 1

        # Minimal delay
        time.sleep(0.01)

    total_time = time.time() - start_time

    return {
        'method': method_func.__name__,
        'total_requests': len(results),
        'successful_requests': sum(1 for r in results if r.success),
        'rate_limit_hit': rate_limit_hit,
        'requests_before_limit': requests_before_limit,
        'total_time': total_time,
        'avg_time_per_request': total_time / len(results) if results else 0,
        'throughput': len(results) / total_time if total_time > 0 else 0
    }

def test_sustained_load(tickers: List[str], method_func, duration_seconds: int = 60, proxy: Optional[str] = None) -> Dict:
    """Test sustained load over time"""
    logger.info(f"Running sustained load test ({duration_seconds}s) with {method_func.__name__}...")

    results = []
    start_time = time.time()

    ticker_idx = 0

    while time.time() - start_time < duration_seconds:
        ticker = tickers[ticker_idx % len(tickers)]

        result = method_func(ticker, proxy) if proxy else method_func(ticker)
        results.append(result)

        ticker_idx += 1

        # Controlled pacing
        time.sleep(0.1)

    total_time = time.time() - start_time
    successes = [r for r in results if r.success]

    return {
        'method': method_func.__name__,
        'duration': total_time,
        'total_requests': len(results),
        'successful_requests': len(successes),
        'success_rate': len(successes) / len(results) if results else 0,
        'avg_response_time': statistics.mean([r.duration for r in successes]) if successes else 0,
        'throughput': len(results) / total_time
    }

def test_proxy_health(proxies: List[str], test_ticker: str = "AAPL") -> List[Dict]:
    """Test health of each proxy"""
    logger.info(f"Testing {len(proxies)} proxies...")

    proxy_results = []

    with ThreadPoolExecutor(max_workers=CONFIG.max_workers) as executor:
        futures = {
            executor.submit(test_standard_requests, test_ticker, proxy): proxy
            for proxy in proxies[:50]  # Limit to first 50
        }

        for future in as_completed(futures):
            proxy = futures[future]
            try:
                result = future.result()
                proxy_results.append({
                    'proxy': proxy,
                    'success': result.success,
                    'duration': result.duration,
                    'error': result.error
                })
            except Exception as e:
                proxy_results.append({
                    'proxy': proxy,
                    'success': False,
                    'duration': 0,
                    'error': str(e)
                })

    # Sort by success and speed
    proxy_results.sort(key=lambda x: (x['success'], -x['duration']), reverse=True)

    return proxy_results

# =====================================================
# TEST SUITES
# =====================================================

def run_quick_suite(tickers: List[str], proxies: List[str]):
    """Quick test suite - basic functionality"""
    logger.info("=" * 70)
    logger.info("QUICK TEST SUITE")
    logger.info("=" * 70)

    test_methods = [
        test_no_proxy_baseline,
        test_standard_requests,
        test_custom_session_factory,
        test_header_rotation,
    ]

    sample_tickers = tickers[:10]
    sample_proxy = proxies[0] if proxies else None

    for method in test_methods:
        logger.info(f"\nTesting: {method.__name__}")

        for ticker in sample_tickers:
            if method == test_no_proxy_baseline:
                result = method(ticker)
            else:
                result = method(ticker, sample_proxy)

            runner.add_result(result)

            if CONFIG.verbose:
                status = "✓" if result.success else "✗"
                logger.info(f"  {status} {ticker}: {result.duration:.3f}s")

def run_full_suite(tickers: List[str], proxies: List[str]):
    """Full test suite - comprehensive testing"""
    logger.info("=" * 70)
    logger.info("FULL TEST SUITE")
    logger.info("=" * 70)

    # 1. Quick suite
    run_quick_suite(tickers, proxies)

    # 2. Additional methods
    if HAS_CURL_CFFI:
        logger.info("\n\nTesting: curl_cffi")
        sample_proxy = proxies[0] if proxies else None
        for ticker in tickers[:10]:
            result = test_curl_cffi(ticker, sample_proxy)
            runner.add_result(result)
            if CONFIG.verbose:
                status = "✓" if result.success else "✗"
                logger.info(f"  {status} {ticker}: {result.duration:.3f}s")

    # 3. Timing variations
    logger.info("\n\nTesting: variable_timing")
    sample_proxy = proxies[0] if proxies else None
    for ticker in tickers[:10]:
        result = test_variable_timing(ticker, sample_proxy)
        runner.add_result(result)
        if CONFIG.verbose:
            status = "✓" if result.success else "✗"
            logger.info(f"  {status} {ticker}: {result.duration:.3f}s")

    # 4. Burst test
    logger.info("\n\n" + "=" * 70)
    logger.info("BURST TESTS")
    logger.info("=" * 70)

    burst_result = test_burst_requests(tickers[:50], test_standard_requests, proxies[0] if proxies else None)
    logger.info(f"Burst test results: {json.dumps(burst_result, indent=2)}")

    # 5. Proxy health
    if proxies:
        logger.info("\n\n" + "=" * 70)
        logger.info("PROXY HEALTH TEST")
        logger.info("=" * 70)

        proxy_health = test_proxy_health(proxies[:20])
        working_proxies = sum(1 for p in proxy_health if p['success'])
        logger.info(f"Working proxies: {working_proxies}/{len(proxy_health)}")

def run_comparison_mode(tickers: List[str], proxies: List[str]):
    """Compare multiple configurations side-by-side"""
    logger.info("=" * 70)
    logger.info("COMPARISON MODE")
    logger.info("=" * 70)

    configurations = [
        ("No Proxy", lambda t: test_no_proxy_baseline(t)),
        ("Standard Requests", lambda t: test_standard_requests(t, proxies[0] if proxies else None)),
        ("Custom Factory", lambda t: test_custom_session_factory(t, proxies[0] if proxies else None)),
        ("Header Rotation", lambda t: test_header_rotation(t, proxies[0] if proxies else None)),
    ]

    if HAS_CURL_CFFI:
        configurations.append(("curl_cffi", lambda t: test_curl_cffi(t, proxies[0] if proxies else None)))

    sample_tickers = tickers[:CONFIG.sample_size]

    comparison_results = {}

    for config_name, test_func in configurations:
        logger.info(f"\nTesting configuration: {config_name}")

        config_results = []

        for ticker in sample_tickers:
            result = test_func(ticker)
            config_results.append(result)
            runner.add_result(result)

        successes = [r for r in config_results if r.success]

        comparison_results[config_name] = {
            'total': len(config_results),
            'successes': len(successes),
            'success_rate': len(successes) / len(config_results) if config_results else 0,
            'avg_duration': statistics.mean([r.duration for r in successes]) if successes else 0,
            'min_duration': min([r.duration for r in successes]) if successes else 0,
            'max_duration': max([r.duration for r in successes]) if successes else 0,
        }

        logger.info(f"  Success rate: {comparison_results[config_name]['success_rate']*100:.1f}%")
        logger.info(f"  Avg duration: {comparison_results[config_name]['avg_duration']:.3f}s")

    # Print comparison table
    logger.info("\n\n" + "=" * 70)
    logger.info("COMPARISON RESULTS")
    logger.info("=" * 70)

    # Sort by performance score
    ranked = sorted(
        comparison_results.items(),
        key=lambda x: x[1]['success_rate'] * (1 / (x[1]['avg_duration'] + 0.1)),
        reverse=True
    )

    logger.info(f"\n{'Rank':<6} {'Configuration':<25} {'Success Rate':<15} {'Avg Duration':<15} {'Score':<10}")
    logger.info("-" * 70)

    for idx, (name, data) in enumerate(ranked, 1):
        score = data['success_rate'] * (1 / (data['avg_duration'] + 0.1))
        logger.info(f"{idx:<6} {name:<25} {data['success_rate']*100:>6.1f}%        {data['avg_duration']:>6.3f}s         {score:>6.2f}")

# =====================================================
# MAIN RUNNER
# =====================================================

def run_tests():
    """Main test runner"""
    logger.info("=" * 70)
    logger.info("PROXY BYPASS TESTER")
    logger.info("=" * 70)

    # Load tickers
    logger.info("Loading test tickers...")
    config = StockRetrievalConfig()
    ticker_result = load_combined_tickers(config)
    tickers = ticker_result.tickers[:CONFIG.sample_size * 3]  # Load extra for testing
    logger.info(f"Loaded {len(tickers)} tickers for testing")

    # Load proxies
    proxies = []
    if CONFIG.proxy_file:
        try:
            with open(CONFIG.proxy_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    proxies = data
                elif isinstance(data, dict):
                    proxies = list(data.values())[0] if data.values() else []
            logger.info(f"Loaded {len(proxies)} proxies from {CONFIG.proxy_file}")
        except Exception as e:
            logger.warning(f"Could not load proxies: {e}")
    else:
        # Try to load from default location
        try:
            proxy_pool = ProxyPool.from_config(config)
            proxies = proxy_pool.proxies
            logger.info(f"Loaded {len(proxies)} proxies from default config")
        except:
            logger.info("No proxies loaded - will test without proxies")

    runner.test_tickers = tickers
    runner.proxies = proxies

    # Run appropriate test suite
    if CONFIG.test_suite == "quick":
        run_quick_suite(tickers, proxies)
    elif CONFIG.test_suite == "full":
        run_full_suite(tickers, proxies)
    elif CONFIG.test_suite == "compare":
        run_comparison_mode(tickers, proxies)
    else:
        logger.error(f"Unknown test suite: {CONFIG.test_suite}")
        return

    # Generate summary
    summary = runner.get_summary()

    logger.info("\n\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total tests: {summary['total_tests']}")
    logger.info(f"Methods tested: {summary['methods_tested']}")

    logger.info("\n\nMETHOD RANKINGS:")
    logger.info("-" * 70)

    for idx, method_data in enumerate(summary['ranked_methods'][:10], 1):
        logger.info(f"{idx}. {method_data['method']}")
        logger.info(f"   Success rate: {method_data['success_rate']*100:.1f}%")
        logger.info(f"   Avg duration: {method_data['avg_duration']:.3f}s")
        logger.info(f"   Performance score: {method_data['score']:.2f}")
        logger.info("")

    # Save report
    with open(CONFIG.output_report, 'w') as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Full report saved to: {CONFIG.output_report}")

    # Generate recommendations
    logger.info("\n\n" + "=" * 70)
    logger.info("RECOMMENDATIONS")
    logger.info("=" * 70)

    best_method = summary['ranked_methods'][0]
    logger.info(f"\nBest performing method: {best_method['method']}")
    logger.info(f"  - Success rate: {best_method['success_rate']*100:.1f}%")
    logger.info(f"  - Average response time: {best_method['avg_duration']:.3f}s")
    logger.info(f"  - Recommended for production use")

    if best_method['success_rate'] < 0.9:
        logger.warning("\nWARNING: Best method has <90% success rate")
        logger.warning("Consider:")
        logger.warning("  - Using better quality proxies")
        logger.warning("  - Implementing additional retry logic")
        logger.warning("  - Adding longer delays between requests")

    logger.info("\n" + "=" * 70)

# =====================================================
# CLI
# =====================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Proxy Bypass Tester")
    parser.add_argument('--test-suite', choices=['quick', 'full', 'compare'],
                       default='quick', help='Test suite to run')
    parser.add_argument('--sample-size', type=int, default=20,
                       help='Number of tickers to test per method')
    parser.add_argument('--test-proxies', type=str,
                       help='Path to proxy file (JSON)')
    parser.add_argument('--output-report', type=str,
                       default='proxy_test_report.json',
                       help='Output report file')
    parser.add_argument('--timeout', type=int, default=10,
                       help='Request timeout in seconds')
    parser.add_argument('--max-workers', type=int, default=5,
                       help='Max concurrent workers for proxy testing')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    # Apply config
    CONFIG.test_suite = args.test_suite
    CONFIG.sample_size = args.sample_size
    CONFIG.proxy_file = args.test_proxies
    CONFIG.output_report = args.output_report
    CONFIG.timeout = args.timeout
    CONFIG.max_workers = args.max_workers
    CONFIG.verbose = args.verbose

    try:
        run_tests()
    except KeyboardInterrupt:
        logger.info("\n\nInterrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
