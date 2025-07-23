#!/usr/bin/env python3
"""
Yahoo Finance Rate Limit Optimizer
Tests different strategies to find optimal rate limiting bypass
"""

import time
import yfinance as yf
import requests
import random
import threading
import queue
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import json
import statistics
import concurrent.futures
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class YahooRateLimitOptimizer:
    """Test different strategies to optimize Yahoo Finance rate limiting"""
    
    def __init__(self):
        self.test_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'AMD', 'INTC', 'ORCL', 'CRM', 'ADBE', 'PYPL', 'UBER', 'SHOP',
            'ZOOM', 'ROKU', 'SQ', 'TWTR', 'SNAP', 'PINS', 'COIN', 'RBLX'
        ]
        self.results = {}
        self.failed_requests = []
        self.session = self._create_session()
        
    def _create_session(self):
        """Create optimized requests session"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Rotate User-Agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101',
        ]
        session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        return session

    def test_yfinance_method(self, delay: float, num_requests: int = 50) -> Dict:
        """Test yfinance library with specific delay"""
        print(f"🔍 Testing yfinance with {delay}s delay, {num_requests} requests...")
        
        start_time = time.time()
        successes = 0
        failures = 0
        response_times = []
        error_types = {}
        
        for i in range(num_requests):
            symbol = random.choice(self.test_symbols)
            request_start = time.time()
            
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="1d")
                
                if hist.empty:
                    failures += 1
                    error_types['empty_data'] = error_types.get('empty_data', 0) + 1
                else:
                    successes += 1
                    response_times.append(time.time() - request_start)
                    
            except Exception as e:
                failures += 1
                error_type = type(e).__name__
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            # Progress indicator
            if (i + 1) % 10 == 0:
                success_rate = (successes / (i + 1)) * 100
                print(f"   Progress: {i+1}/{num_requests} | Success Rate: {success_rate:.1f}%")
            
            if i < num_requests - 1:  # Don't sleep after last request
                time.sleep(delay)
        
        total_time = time.time() - start_time
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        return {
            'method': 'yfinance',
            'delay': delay,
            'total_requests': num_requests,
            'successes': successes,
            'failures': failures,
            'success_rate': (successes / num_requests) * 100,
            'total_time': total_time,
            'avg_response_time': avg_response_time,
            'requests_per_second': num_requests / total_time,
            'error_types': error_types,
            'effective_rps': successes / total_time
        }

    def test_direct_requests_method(self, delay: float, num_requests: int = 50) -> Dict:
        """Test direct requests to Yahoo Finance API"""
        print(f"🌐 Testing direct requests with {delay}s delay, {num_requests} requests...")
        
        start_time = time.time()
        successes = 0
        failures = 0
        response_times = []
        error_types = {}
        
        for i in range(num_requests):
            symbol = random.choice(self.test_symbols)
            request_start = time.time()
            
            try:
                # Direct Yahoo Finance API call
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'chart' in data and data['chart']['result']:
                        successes += 1
                        response_times.append(time.time() - request_start)
                    else:
                        failures += 1
                        error_types['invalid_data'] = error_types.get('invalid_data', 0) + 1
                else:
                    failures += 1
                    error_types[f'http_{response.status_code}'] = error_types.get(f'http_{response.status_code}', 0) + 1
                    
            except Exception as e:
                failures += 1
                error_type = type(e).__name__
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            # Progress indicator
            if (i + 1) % 10 == 0:
                success_rate = (successes / (i + 1)) * 100
                print(f"   Progress: {i+1}/{num_requests} | Success Rate: {success_rate:.1f}%")
            
            if i < num_requests - 1:
                time.sleep(delay)
        
        total_time = time.time() - start_time
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        return {
            'method': 'direct_requests',
            'delay': delay,
            'total_requests': num_requests,
            'successes': successes,
            'failures': failures,
            'success_rate': (successes / num_requests) * 100,
            'total_time': total_time,
            'avg_response_time': avg_response_time,
            'requests_per_second': num_requests / total_time,
            'error_types': error_types,
            'effective_rps': successes / total_time
        }

    def test_concurrent_requests(self, delay: float, num_threads: int = 5, requests_per_thread: int = 10) -> Dict:
        """Test concurrent requests with threading"""
        print(f"⚡ Testing {num_threads} concurrent threads with {delay}s delay...")
        
        start_time = time.time()
        results_queue = queue.Queue()
        
        def worker_thread(thread_id: int):
            thread_successes = 0
            thread_failures = 0
            thread_errors = {}
            
            for i in range(requests_per_thread):
                symbol = random.choice(self.test_symbols)
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1d")
                    
                    if not hist.empty:
                        thread_successes += 1
                    else:
                        thread_failures += 1
                        thread_errors['empty_data'] = thread_errors.get('empty_data', 0) + 1
                        
                except Exception as e:
                    thread_failures += 1
                    error_type = type(e).__name__
                    thread_errors[error_type] = thread_errors.get(error_type, 0) + 1
                
                if i < requests_per_thread - 1:
                    time.sleep(delay)
            
            results_queue.put({
                'thread_id': thread_id,
                'successes': thread_successes,
                'failures': thread_failures,
                'errors': thread_errors
            })
        
        # Start all threads
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        total_successes = 0
        total_failures = 0
        combined_errors = {}
        
        while not results_queue.empty():
            result = results_queue.get()
            total_successes += result['successes']
            total_failures += result['failures']
            
            for error_type, count in result['errors'].items():
                combined_errors[error_type] = combined_errors.get(error_type, 0) + count
        
        total_time = time.time() - start_time
        total_requests = num_threads * requests_per_thread
        
        return {
            'method': 'concurrent',
            'delay': delay,
            'num_threads': num_threads,
            'requests_per_thread': requests_per_thread,
            'total_requests': total_requests,
            'successes': total_successes,
            'failures': total_failures,
            'success_rate': (total_successes / total_requests) * 100,
            'total_time': total_time,
            'requests_per_second': total_requests / total_time,
            'error_types': combined_errors,
            'effective_rps': total_successes / total_time
        }

    def test_burst_strategy(self, burst_size: int = 5, burst_delay: float = 0.1, pause_between_bursts: float = 2.0) -> Dict:
        """Test burst strategy - fast requests in bursts with longer pauses"""
        print(f"💥 Testing burst strategy: {burst_size} requests every {pause_between_bursts}s...")
        
        start_time = time.time()
        successes = 0
        failures = 0
        error_types = {}
        num_bursts = 10
        total_requests = num_bursts * burst_size
        
        for burst in range(num_bursts):
            print(f"   Burst {burst + 1}/{num_bursts}")
            
            # Rapid requests in burst
            for i in range(burst_size):
                symbol = random.choice(self.test_symbols)
                
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1d")
                    
                    if not hist.empty:
                        successes += 1
                    else:
                        failures += 1
                        error_types['empty_data'] = error_types.get('empty_data', 0) + 1
                        
                except Exception as e:
                    failures += 1
                    error_type = type(e).__name__
                    error_types[error_type] = error_types.get(error_type, 0) + 1
                
                if i < burst_size - 1:  # Short delay within burst
                    time.sleep(burst_delay)
            
            # Longer pause between bursts
            if burst < num_bursts - 1:
                time.sleep(pause_between_bursts)
        
        total_time = time.time() - start_time
        
        return {
            'method': 'burst',
            'burst_size': burst_size,
            'burst_delay': burst_delay,
            'pause_between_bursts': pause_between_bursts,
            'total_requests': total_requests,
            'successes': successes,
            'failures': failures,
            'success_rate': (successes / total_requests) * 100,
            'total_time': total_time,
            'requests_per_second': total_requests / total_time,
            'error_types': error_types,
            'effective_rps': successes / total_time
        }

    def test_random_delay_strategy(self, min_delay: float = 0.5, max_delay: float = 2.0, num_requests: int = 50) -> Dict:
        """Test random delay strategy to avoid pattern detection"""
        print(f"🎲 Testing random delays between {min_delay}s and {max_delay}s...")
        
        start_time = time.time()
        successes = 0
        failures = 0
        error_types = {}
        delays_used = []
        
        for i in range(num_requests):
            symbol = random.choice(self.test_symbols)
            
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                
                if not hist.empty:
                    successes += 1
                else:
                    failures += 1
                    error_types['empty_data'] = error_types.get('empty_data', 0) + 1
                    
            except Exception as e:
                failures += 1
                error_type = type(e).__name__
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            if i < num_requests - 1:
                delay = random.uniform(min_delay, max_delay)
                delays_used.append(delay)
                time.sleep(delay)
            
            # Progress indicator
            if (i + 1) % 10 == 0:
                success_rate = (successes / (i + 1)) * 100
                print(f"   Progress: {i+1}/{num_requests} | Success Rate: {success_rate:.1f}%")
        
        total_time = time.time() - start_time
        avg_delay = statistics.mean(delays_used) if delays_used else 0
        
        return {
            'method': 'random_delay',
            'min_delay': min_delay,
            'max_delay': max_delay,
            'avg_delay': avg_delay,
            'total_requests': num_requests,
            'successes': successes,
            'failures': failures,
            'success_rate': (successes / num_requests) * 100,
            'total_time': total_time,
            'requests_per_second': num_requests / total_time,
            'error_types': error_types,
            'effective_rps': successes / total_time
        }

    def run_comprehensive_test(self):
        """Run all optimization tests"""
        print("🚀 Starting Yahoo Finance Rate Limit Optimization Tests")
        print("=" * 60)
        
        all_results = []
        
        # Test 1: Different fixed delays with yfinance
        print("\n📊 TEST 1: Fixed Delays with yfinance")
        delays = [0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
        for delay in delays:
            result = self.test_yfinance_method(delay, 30)
            all_results.append(result)
            print(f"   Delay {delay}s: {result['success_rate']:.1f}% success, {result['effective_rps']:.2f} RPS")
        
        # Test 2: Direct requests method
        print("\n🌐 TEST 2: Direct API Requests")
        for delay in [0.5, 1.0, 1.5]:
            result = self.test_direct_requests_method(delay, 30)
            all_results.append(result)
            print(f"   Delay {delay}s: {result['success_rate']:.1f}% success, {result['effective_rps']:.2f} RPS")
        
        # Test 3: Concurrent requests
        print("\n⚡ TEST 3: Concurrent Requests")
        for delay in [1.0, 2.0]:
            for threads in [2, 3, 5]:
                result = self.test_concurrent_requests(delay, threads, 10)
                all_results.append(result)
                print(f"   {threads} threads, {delay}s: {result['success_rate']:.1f}% success, {result['effective_rps']:.2f} RPS")
        
        # Test 4: Burst strategy
        print("\n💥 TEST 4: Burst Strategy")
        burst_configs = [
            (3, 0.1, 2.0),
            (5, 0.1, 3.0),
            (5, 0.2, 2.0),
            (10, 0.1, 5.0)
        ]
        for burst_size, burst_delay, pause in burst_configs:
            result = self.test_burst_strategy(burst_size, burst_delay, pause)
            all_results.append(result)
            print(f"   Burst {burst_size}/{pause}s: {result['success_rate']:.1f}% success, {result['effective_rps']:.2f} RPS")
        
        # Test 5: Random delays
        print("\n🎲 TEST 5: Random Delay Strategy")
        random_configs = [
            (0.3, 1.0),
            (0.5, 1.5),
            (0.8, 2.0),
            (1.0, 3.0)
        ]
        for min_delay, max_delay in random_configs:
            result = self.test_random_delay_strategy(min_delay, max_delay, 30)
            all_results.append(result)
            print(f"   Random {min_delay}-{max_delay}s: {result['success_rate']:.1f}% success, {result['effective_rps']:.2f} RPS")
        
        return all_results

    def analyze_results(self, results: List[Dict]):
        """Analyze and rank all test results"""
        print("\n" + "=" * 60)
        print("📈 OPTIMIZATION ANALYSIS")
        print("=" * 60)
        
        # Sort by success rate first, then by effective RPS
        ranked_results = sorted(
            results,
            key=lambda x: (x['success_rate'], x['effective_rps']),
            reverse=True
        )
        
        print("\n🏆 TOP 10 STRATEGIES (by success rate + effective RPS):")
        print("-" * 60)
        
        for i, result in enumerate(ranked_results[:10], 1):
            method_info = self._format_method_info(result)
            print(f"{i:2d}. {method_info}")
            print(f"    Success: {result['success_rate']:5.1f}% | Effective RPS: {result['effective_rps']:5.2f}")
            if result['error_types']:
                main_error = max(result['error_types'], key=result['error_types'].get)
                print(f"    Main Error: {main_error} ({result['error_types'][main_error]} times)")
            print()
        
        # Find optimal configuration
        best_result = ranked_results[0]
        print("🎯 RECOMMENDED OPTIMAL CONFIGURATION:")
        print("-" * 40)
        self._print_optimal_config(best_result)
        
        return best_result

    def _format_method_info(self, result: Dict) -> str:
        """Format method information for display"""
        method = result['method']
        
        if method == 'yfinance':
            return f"yfinance with {result['delay']}s delay"
        elif method == 'direct_requests':
            return f"Direct requests with {result['delay']}s delay"
        elif method == 'concurrent':
            return f"Concurrent ({result['num_threads']} threads, {result['delay']}s delay)"
        elif method == 'burst':
            return f"Burst ({result['burst_size']} requests, {result['pause_between_bursts']}s pause)"
        elif method == 'random_delay':
            return f"Random delay ({result['min_delay']}-{result['max_delay']}s)"
        else:
            return method

    def _print_optimal_config(self, best_result: Dict):
        """Print the optimal configuration code"""
        method = best_result['method']
        
        print(f"Method: {method}")
        print(f"Success Rate: {best_result['success_rate']:.1f}%")
        print(f"Effective RPS: {best_result['effective_rps']:.2f}")
        print()
        
        print("💻 IMPLEMENTATION CODE:")
        print("-" * 30)
        
        if method == 'yfinance':
            print(f"""
import time
import yfinance as yf

# Optimal yfinance configuration
OPTIMAL_DELAY = {best_result['delay']}

def get_stock_data(symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1d")
    time.sleep(OPTIMAL_DELAY)  # Rate limiting
    return hist
""")
        
        elif method == 'burst':
            print(f"""
import time
import yfinance as yf

# Optimal burst configuration
BURST_SIZE = {best_result['burst_size']}
BURST_DELAY = {best_result['burst_delay']}
PAUSE_BETWEEN_BURSTS = {best_result['pause_between_bursts']}

def get_stocks_burst(symbols):
    results = []
    for i, symbol in enumerate(symbols):
        ticker = yf.Ticker(symbol)
        results.append(ticker.history(period="1d"))
        
        if (i + 1) % BURST_SIZE == 0:
            time.sleep(PAUSE_BETWEEN_BURSTS)
        else:
            time.sleep(BURST_DELAY)
    
    return results
""")
        
        elif method == 'random_delay':
            print(f"""
import time
import random
import yfinance as yf

# Optimal random delay configuration
MIN_DELAY = {best_result['min_delay']}
MAX_DELAY = {best_result['max_delay']}

def get_stock_data(symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1d")
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    time.sleep(delay)
    return hist
""")
        
        print("\n🔧 FOR DJANGO INTEGRATION:")
        print(f"Update your settings.py:")
        print(f"YFINANCE_RATE_LIMIT = {best_result.get('delay', best_result.get('avg_delay', 1.0))}")

    def save_results(self, results: List[Dict], filename: str = None):
        """Save results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'yahoo_rate_limit_test_results_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {filename}")

def main():
    """Run the complete optimization test suite"""
    optimizer = YahooRateLimitOptimizer()
    
    try:
        print("⚡ Yahoo Finance Rate Limit Optimizer")
        print("🎯 Finding the perfect balance to bypass rate limits")
        print("📊 This will take approximately 10-15 minutes...")
        print()
        
        # Run comprehensive tests
        results = optimizer.run_comprehensive_test()
        
        # Analyze and find optimal strategy
        best_config = optimizer.analyze_results(results)
        
        # Save results
        optimizer.save_results(results)
        
        print("\n✅ Optimization complete!")
        print("📧 Share the results and we'll implement the optimal strategy!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")

if __name__ == "__main__":
    main()