#!/usr/bin/env python3
"""
Performance Tuning Helper for Ultra-Fast Scanner

This script helps you:
1. Measure actual call times for fast_info vs info
2. Calculate optimal worker count
3. Determine best batch size
4. Find ideal delay settings to avoid rate limits
5. Suggest configuration for <3 min runtime with >95% accuracy
"""

import os
import sys
import time
import json
import random
from statistics import mean, median, stdev
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stock_scanner_backend.settings")

import django
django.setup()

import yfinance as yf
from stock_retrieval.session_factory import create_session_with_proxy, ProxyPool
from stock_retrieval.ticker_loader import load_combined_tickers

# =====================================================
# TIMING TESTS
# =====================================================

def measure_fast_info_timing(sample_tickers, proxy=None, num_samples=20):
    """Measure fast_info call timing"""
    print(f"\n📊 Measuring fast_info timing ({num_samples} samples)...")

    times = []
    successes = 0

    session = create_session_with_proxy(proxy=proxy, timeout=10)

    for ticker in sample_tickers[:num_samples]:
        try:
            start = time.time()
            ticker_obj = yf.Ticker(ticker, session=session)
            _ = ticker_obj.fast_info.last_price
            duration = time.time() - start

            times.append(duration)
            successes += 1
            print(f"  {ticker}: {duration:.3f}s")

        except Exception as e:
            print(f"  {ticker}: FAILED - {e}")

    if times:
        return {
            'method': 'fast_info',
            'samples': len(times),
            'successes': successes,
            'min': min(times),
            'max': max(times),
            'mean': mean(times),
            'median': median(times),
            'stdev': stdev(times) if len(times) > 1 else 0,
            'success_rate': successes / num_samples
        }
    return None

def measure_info_timing(sample_tickers, proxy=None, num_samples=20):
    """Measure info call timing"""
    print(f"\n📊 Measuring info timing ({num_samples} samples)...")

    times = []
    successes = 0

    session = create_session_with_proxy(proxy=proxy, timeout=10)

    for ticker in sample_tickers[:num_samples]:
        try:
            start = time.time()
            ticker_obj = yf.Ticker(ticker, session=session)
            _ = ticker_obj.info
            duration = time.time() - start

            times.append(duration)
            successes += 1
            print(f"  {ticker}: {duration:.3f}s")

        except Exception as e:
            print(f"  {ticker}: FAILED - {e}")

    if times:
        return {
            'method': 'info',
            'samples': len(times),
            'successes': successes,
            'min': min(times),
            'max': max(times),
            'mean': mean(times),
            'median': median(times),
            'stdev': stdev(times) if len(times) > 1 else 0,
            'success_rate': successes / num_samples
        }
    return None

# =====================================================
# CONCURRENCY TESTS
# =====================================================

def test_concurrency_level(tickers, num_workers, proxy_pool, test_size=100):
    """Test throughput at different concurrency levels"""
    print(f"\n🔄 Testing {num_workers} workers with {test_size} tickers...")

    start_time = time.time()
    successes = 0
    rate_limits = 0

    test_tickers = tickers[:test_size]

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {}

        for idx, ticker in enumerate(test_tickers):
            worker_id = idx % num_workers
            proxy = proxy_pool.get_proxy_for_worker(worker_id) if hasattr(proxy_pool, 'get_proxy_for_worker') else None

            future = executor.submit(test_single_ticker, ticker, proxy)
            futures[future] = ticker

        for future in as_completed(futures):
            result = future.result()
            if result == 'success':
                successes += 1
            elif result == 'rate_limit':
                rate_limits += 1

    duration = time.time() - start_time
    throughput = test_size / duration

    return {
        'workers': num_workers,
        'test_size': test_size,
        'duration': duration,
        'successes': successes,
        'rate_limits': rate_limits,
        'throughput': throughput,
        'success_rate': successes / test_size
    }

def test_single_ticker(ticker, proxy):
    """Test fetching single ticker"""
    try:
        session = create_session_with_proxy(proxy=proxy, timeout=4)
        ticker_obj = yf.Ticker(ticker, session=session)

        # Try fast_info first
        try:
            _ = ticker_obj.fast_info.last_price
            return 'success'
        except:
            pass

        # Fall back to info
        try:
            _ = ticker_obj.info
            return 'success'
        except Exception as e:
            if '429' in str(e):
                return 'rate_limit'
            return 'failure'

    except Exception as e:
        if '429' in str(e):
            return 'rate_limit'
        return 'failure'

# =====================================================
# PROXY TESTING
# =====================================================

def test_proxy_pool(proxy_pool, num_tests=10):
    """Test proxy pool health"""
    print(f"\n🌐 Testing proxy pool ({num_tests} proxies)...")

    results = []
    test_ticker = "AAPL"

    for i in range(min(num_tests, len(proxy_pool.proxies))):
        proxy = proxy_pool.proxies[i]

        try:
            start = time.time()
            session = create_session_with_proxy(proxy=proxy, timeout=5)
            ticker_obj = yf.Ticker(test_ticker, session=session)
            _ = ticker_obj.fast_info.last_price
            duration = time.time() - start

            results.append({
                'proxy': proxy,
                'status': 'working',
                'duration': duration
            })
            print(f"  ✓ {proxy}: {duration:.3f}s")

        except Exception as e:
            results.append({
                'proxy': proxy,
                'status': 'failed',
                'error': str(e)
            })
            print(f"  ✗ {proxy}: {e}")

    working = [r for r in results if r['status'] == 'working']
    return {
        'total_tested': len(results),
        'working': len(working),
        'failed': len(results) - len(working),
        'working_rate': len(working) / len(results) if results else 0,
        'avg_response_time': mean([r['duration'] for r in working]) if working else 0
    }

# =====================================================
# OPTIMIZATION CALCULATOR
# =====================================================

def calculate_optimal_config(total_tickers, target_seconds, fast_info_stats, info_stats):
    """Calculate optimal configuration to meet targets"""

    print(f"\n🎯 Calculating optimal configuration...")
    print(f"   Target: {total_tickers} tickers in {target_seconds}s")

    # Use fast_info as primary (faster)
    avg_call_time = fast_info_stats['mean']
    success_rate = fast_info_stats['success_rate']

    # Account for info fallback (slower)
    fallback_rate = 1 - success_rate
    if info_stats:
        weighted_avg_time = (
            success_rate * fast_info_stats['mean'] +
            fallback_rate * info_stats['mean']
        )
    else:
        weighted_avg_time = avg_call_time

    print(f"   Weighted avg call time: {weighted_avg_time:.3f}s")

    # Calculate required throughput
    required_throughput = total_tickers / target_seconds
    print(f"   Required throughput: {required_throughput:.1f} tickers/sec")

    # Calculate workers needed
    # throughput = workers / avg_call_time
    # workers = throughput * avg_call_time
    ideal_workers = int(required_throughput * weighted_avg_time * 1.2)  # 20% buffer

    # Practical limits
    min_workers = 10
    max_workers = 50
    optimal_workers = max(min_workers, min(ideal_workers, max_workers))

    print(f"   Ideal workers: {ideal_workers}")
    print(f"   Optimal workers (capped): {optimal_workers}")

    # Calculate batch size
    # Larger batches = fewer HTTP requests but longer per-batch time
    # Smaller batches = more overhead but better progress visibility
    optimal_batch_size = max(100, min(1000, total_tickers // 10))

    print(f"   Optimal batch size: {optimal_batch_size}")

    # Calculate expected runtime
    expected_runtime = (total_tickers * weighted_avg_time) / optimal_workers
    print(f"   Expected runtime: {expected_runtime:.1f}s ({expected_runtime/60:.2f} min)")

    # Delay calculation
    # Want to stay under rate limits
    # Yahoo allows ~100-150 req/min per IP
    # With proxies, we can go faster
    # Rule of thumb: delay = avg_call_time * 0.05 (5%)
    optimal_min_delay = weighted_avg_time * 0.02
    optimal_max_delay = weighted_avg_time * 0.10

    print(f"   Optimal delay range: {optimal_min_delay:.4f}s - {optimal_max_delay:.4f}s")

    # Determine if targets are achievable
    achievable = expected_runtime <= target_seconds
    margin = ((target_seconds - expected_runtime) / target_seconds * 100) if achievable else 0

    print(f"   Target achievable: {'✓ YES' if achievable else '✗ NO'}")
    if achievable:
        print(f"   Margin: {margin:.1f}%")

    return {
        'optimal_workers': optimal_workers,
        'optimal_batch_size': optimal_batch_size,
        'optimal_min_delay': optimal_min_delay,
        'optimal_max_delay': optimal_max_delay,
        'expected_runtime_seconds': expected_runtime,
        'expected_runtime_minutes': expected_runtime / 60,
        'achievable': achievable,
        'margin_percent': margin,
        'required_throughput': required_throughput
    }

# =====================================================
# MAIN TUNING PROCESS
# =====================================================

def run_performance_tuning(target_tickers=5373, target_seconds=180):
    """Run complete performance tuning process"""

    print("=" * 70)
    print("PERFORMANCE TUNING FOR ULTRA-FAST SCANNER")
    print("=" * 70)
    print(f"Target: {target_tickers} tickers in {target_seconds}s ({target_seconds/60:.1f} min)")
    print("=" * 70)

    # Load sample tickers
    print("\n📦 Loading sample tickers...")
    all_tickers = load_combined_tickers()
    print(f"   Loaded {len(all_tickers)} tickers")

    # Random sample for testing
    sample_size = min(50, len(all_tickers))
    sample_tickers = random.sample(all_tickers, sample_size)
    print(f"   Using {sample_size} random samples for testing")

    # Load proxy pool
    print("\n🌐 Loading proxy pool...")
    proxy_pool = ProxyPool()
    print(f"   Loaded {len(proxy_pool.proxies)} proxies")

    # Test proxy health
    proxy_stats = test_proxy_pool(proxy_pool, num_tests=10)
    print(f"\n   Proxy Health:")
    print(f"     Working: {proxy_stats['working']}/{proxy_stats['total_tested']}")
    print(f"     Success rate: {proxy_stats['working_rate']*100:.1f}%")
    print(f"     Avg response time: {proxy_stats['avg_response_time']:.3f}s")

    # Get a working proxy for timing tests
    test_proxy = proxy_pool.proxies[0] if proxy_pool.proxies else None

    # Measure fast_info timing
    fast_info_stats = measure_fast_info_timing(sample_tickers, proxy=test_proxy, num_samples=20)

    if fast_info_stats:
        print(f"\n   Fast_info Results:")
        print(f"     Success rate: {fast_info_stats['success_rate']*100:.1f}%")
        print(f"     Mean time: {fast_info_stats['mean']:.3f}s")
        print(f"     Median time: {fast_info_stats['median']:.3f}s")
        print(f"     Range: {fast_info_stats['min']:.3f}s - {fast_info_stats['max']:.3f}s")
        print(f"     Std dev: {fast_info_stats['stdev']:.3f}s")

    # Measure info timing
    info_stats = measure_info_timing(sample_tickers, proxy=test_proxy, num_samples=20)

    if info_stats:
        print(f"\n   Info Results:")
        print(f"     Success rate: {info_stats['success_rate']*100:.1f}%")
        print(f"     Mean time: {info_stats['mean']:.3f}s")
        print(f"     Median time: {info_stats['median']:.3f}s")
        print(f"     Range: {info_stats['min']:.3f}s - {info_stats['max']:.3f}s")
        print(f"     Std dev: {info_stats['stdev']:.3f}s")

        # Compare
        speedup = info_stats['mean'] / fast_info_stats['mean'] if fast_info_stats else 1
        print(f"\n   Fast_info is {speedup:.1f}x faster than info")

    # Test different concurrency levels
    print("\n" + "=" * 70)
    print("CONCURRENCY TESTING")
    print("=" * 70)

    concurrency_results = []
    for workers in [10, 15, 20, 25, 30]:
        result = test_concurrency_level(sample_tickers, workers, proxy_pool, test_size=50)
        concurrency_results.append(result)

        print(f"\n   {workers} workers:")
        print(f"     Duration: {result['duration']:.1f}s")
        print(f"     Throughput: {result['throughput']:.1f} tickers/sec")
        print(f"     Success rate: {result['success_rate']*100:.1f}%")
        print(f"     Rate limits: {result['rate_limits']}")

    # Find best concurrency level
    best_concurrency = max(concurrency_results, key=lambda x: x['throughput'] * x['success_rate'])
    print(f"\n   Best performer: {best_concurrency['workers']} workers")
    print(f"     Throughput: {best_concurrency['throughput']:.1f} tickers/sec")
    print(f"     Success rate: {best_concurrency['success_rate']*100:.1f}%")

    # Calculate optimal configuration
    if fast_info_stats:
        optimal_config = calculate_optimal_config(
            target_tickers,
            target_seconds,
            fast_info_stats,
            info_stats
        )

        # Generate configuration recommendations
        print("\n" + "=" * 70)
        print("RECOMMENDED CONFIGURATION")
        print("=" * 70)

        config_code = f"""
# Recommended configuration for {target_tickers} tickers in {target_seconds}s

CONFIG = ScannerConfig(
    # Performance settings
    max_workers={optimal_config['optimal_workers']},  # Concurrent workers
    target_runtime_seconds={target_seconds},
    request_timeout=4,  # Seconds per request

    # Rate limiting strategy
    min_delay_between_calls={optimal_config['optimal_min_delay']:.4f},
    max_delay_between_calls={optimal_config['optimal_max_delay']:.4f},
    adaptive_delay_enabled=True,

    # Data retrieval strategy
    use_fast_info_first=True,  # Fast_info is {info_stats['mean']/fast_info_stats['mean']:.1f}x faster
    fallback_to_info=True,
    max_retries_per_ticker=2,

    # Proxy settings
    max_proxies={min(100, len(proxy_pool.proxies))},
    proxy_rotation_strategy="worker_based",

    # Quality thresholds
    min_success_rate=0.95,

    # Batching
    batch_size={optimal_config['optimal_batch_size']},
    inter_batch_delay=0.0,
)
"""

        print(config_code)

        # Save to file
        config_file = f"recommended_config_{target_tickers}tickers.py"
        with open(config_file, 'w') as f:
            f.write(config_code)

        print(f"\n✓ Configuration saved to: {config_file}")

        # Performance prediction
        print("\n" + "=" * 70)
        print("PERFORMANCE PREDICTION")
        print("=" * 70)
        print(f"Expected runtime: {optimal_config['expected_runtime_minutes']:.2f} minutes")
        print(f"Expected throughput: {optimal_config['required_throughput']:.1f} tickers/sec")

        if optimal_config['achievable']:
            print(f"✓ Target achievable with {optimal_config['margin_percent']:.1f}% margin")
        else:
            shortfall = optimal_config['expected_runtime_seconds'] - target_seconds
            print(f"✗ Target NOT achievable (need {shortfall:.1f}s improvement)")
            print("\nSuggestions:")
            print("  1. Increase max_workers further")
            print("  2. Reduce request_timeout")
            print("  3. Use more/faster proxies")
            print("  4. Accept lower success rate threshold")

        # Save full report
        report = {
            'target_tickers': target_tickers,
            'target_seconds': target_seconds,
            'proxy_stats': proxy_stats,
            'fast_info_stats': fast_info_stats,
            'info_stats': info_stats,
            'concurrency_results': concurrency_results,
            'best_concurrency': best_concurrency,
            'optimal_config': optimal_config,
            'timestamp': time.time()
        }

        report_file = f"tuning_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n✓ Full report saved to: {report_file}")

        print("\n" + "=" * 70)
        print("TUNING COMPLETE")
        print("=" * 70)

        return optimal_config

    else:
        print("\n✗ Could not measure timing stats - check proxy connectivity")
        return None

# =====================================================
# CLI ENTRY POINT
# =====================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Performance Tuning Helper")
    parser.add_argument('--target-tickers', type=int, default=5373,
                       help='Target number of tickers (default: 5373)')
    parser.add_argument('--target-seconds', type=int, default=180,
                       help='Target runtime in seconds (default: 180 = 3 minutes)')

    args = parser.parse_args()

    try:
        run_performance_tuning(
            target_tickers=args.target_tickers,
            target_seconds=args.target_seconds
        )
    except KeyboardInterrupt:
        print("\n\nTuning interrupted by user")
    except Exception as e:
        print(f"\nError during tuning: {e}")
        import traceback
        traceback.print_exc()
