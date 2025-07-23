#!/usr/bin/env python3
"""
Enhanced Yahoo Finance Direct API Optimizer
Uses direct API requests as the foundation with advanced enhancements
"""

import time
import yfinance as yf
import requests
import random
import threading
import queue
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any
import json
import statistics
import concurrent.futures
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import hashlib
import uuid
from urllib.parse import urlencode, urlparse
import socket
import ssl
try:
    import fake_useragent
    FAKE_USERAGENT_AVAILABLE = True
except ImportError:
    FAKE_USERAGENT_AVAILABLE = False

class EnhancedDirectAPIOptimizer:
    """Enhanced direct API requests with advanced optimizations"""
    
    def __init__(self):
        self.test_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'AMD', 'INTC', 'ORCL', 'CRM', 'ADBE', 'PYPL', 'UBER', 'SHOP',
            'ZOOM', 'ROKU', 'SQ', 'HOOD', 'SNAP', 'PINS', 'COIN', 'RBLX',
            'TWTR', 'FB', 'SPOT', 'DIS', 'BABA', 'JNJ', 'V', 'JPM', 'PG'
        ]
        self.results = {}
        self.failed_requests = []
        if FAKE_USERAGENT_AVAILABLE:
            self.user_agent_rotator = fake_useragent.UserAgent()
        else:
            self.user_agent_rotator = None
        
    def print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'='*70}")
        print(f"🚀 {title}")
        print(f"{'='*70}")
        
    def print_step(self, step: str, description: str):
        """Print formatted step"""
        print(f"\n{'-'*50}")
        print(f"{step} {description}")
        print(f"{'-'*50}")
        
    def print_result(self, message: str, success: bool = True):
        """Print formatted result"""
        icon = "✅" if success else "❌"
        print(f"   {icon} {message}")
        
    def print_warning(self, message: str):
        """Print formatted warning"""
        print(f"   ⚠️ {message}")
        
    def test_isolation_delay(self, test_name: str):
        """Add delay between tests to prevent spillover effects"""
        self.print_step("🕐", f"ISOLATION DELAY FOR {test_name}")
        print("   ⏳ Waiting to prevent test interference...")
        for i in range(10, 0, -1):
            print(f"   ⏰ {i} seconds remaining...", end='\r')
            time.sleep(1)
        print("   ✅ Isolation delay completed              ")
    
    # ==================== CORE METHOD: DIRECT API REQUESTS ====================
    
    def test_direct_api_requests(self, delays: List[float] = None, num_requests: int = 30) -> Dict:
        """Test direct API requests with various delays - CORE METHOD"""
        if delays is None:
            delays = [0.5, 1.0, 1.5]
            
        self.print_step("🌐", "DIRECT API REQUESTS - CORE METHOD")
        
        all_delay_results = {}
        best_delay_result = None
        best_success_rate = 0
        
        for delay in delays:
            print(f"\n🌐 Testing direct requests with {delay}s delay, {num_requests} requests...")
            
            start_time = time.time()
            successes = 0
            failures = 0
            response_times = []
            error_types = {}
            
            for i in range(num_requests):
                symbol = random.choice(self.test_symbols)
                request_start = time.time()
                
                try:
                    # Pure direct yfinance request - no enhancements
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    hist = ticker.history(period="1d")
                    
                    if hist.empty or not info:
                        failures += 1
                        error_types['empty_data'] = error_types.get('empty_data', 0) + 1
                    else:
                        successes += 1
                        response_times.append(time.time() - request_start)
                        
                except Exception as e:
                    failures += 1
                    error_type = type(e).__name__
                    error_types[error_type] = error_types.get(error_type, 0) + 1
                    
                # Progress updates every 10 requests
                if (i + 1) % 10 == 0:
                    success_rate = (successes / (i + 1)) * 100
                    print(f"   Progress: {i+1}/{num_requests} | Success Rate: {success_rate:.1f}%")
                    
                # Apply delay
                if i < num_requests - 1:
                    time.sleep(delay)
                    
            total_time = time.time() - start_time
            success_rate = (successes / num_requests) * 100 if num_requests > 0 else 0
            avg_response_time = statistics.mean(response_times) if response_times else 0
            rps = num_requests / total_time if total_time > 0 else 0
            
            delay_result = {
                'delay': delay,
                'success_rate': success_rate,
                'total_requests': num_requests,
                'successes': successes,
                'failures': failures,
                'avg_response_time': avg_response_time,
                'total_time': total_time,
                'requests_per_second': rps,
                'error_types': error_types
            }
            
            all_delay_results[f"{delay}s"] = delay_result
            print(f"   Delay {delay}s: {success_rate:.1f}% success, {rps:.2f} RPS")
            
            # Track best performing delay
            if success_rate > best_success_rate:
                best_success_rate = success_rate
                best_delay_result = delay_result
                
            # Brief pause between delay tests
            if delay != delays[-1]:
                time.sleep(2.0)
        
        # Summary result
        result = {
            'method': 'direct_api_requests',
            'success_rate': best_delay_result['success_rate'] if best_delay_result else 0,
            'total_requests': num_requests * len(delays),
            'successes': sum(r['successes'] for r in all_delay_results.values()),
            'failures': sum(r['failures'] for r in all_delay_results.values()),
            'avg_response_time': best_delay_result['avg_response_time'] if best_delay_result else 0,
            'total_time': sum(r['total_time'] for r in all_delay_results.values()),
            'requests_per_second': best_delay_result['requests_per_second'] if best_delay_result else 0,
            'error_types': {},
            'best_delay': best_delay_result['delay'] if best_delay_result else 0,
            'delay_results': all_delay_results
        }
        
        # Combine error types
        for delay_result in all_delay_results.values():
            for error_type, count in delay_result['error_types'].items():
                result['error_types'][error_type] = result['error_types'].get(error_type, 0) + count
        
        self.print_result(f"Direct API Core: Best {best_success_rate:.1f}% success with {best_delay_result['delay']}s delay")
        return result
    
    # ==================== ENHANCEMENT 1: USER AGENT ROTATION ====================
    
    def test_direct_api_with_user_agents(self, optimal_delay: float = 1.0, num_requests: int = 30) -> Dict:
        """Enhance direct API with user agent rotation"""
        self.print_step("🎭", "DIRECT API + USER AGENT ROTATION")
        
        if not FAKE_USERAGENT_AVAILABLE:
            print("   ⚠️ fake-useragent not available, using default user agents")
            
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1'
        ]
        
        print(f"🌐 Testing direct requests with user agent rotation, {optimal_delay}s delay, {num_requests} requests...")
        
        start_time = time.time()
        successes = 0
        failures = 0
        response_times = []
        error_types = {}
        user_agent_success = {}
        
        for i in range(num_requests):
            symbol = random.choice(self.test_symbols)
            request_start = time.time()
            
            # Select user agent
            if FAKE_USERAGENT_AVAILABLE and self.user_agent_rotator:
                try:
                    user_agent = self.user_agent_rotator.random
                except:
                    user_agent = random.choice(user_agents)
            else:
                user_agent = random.choice(user_agents)
            
            try:
                # Create session with user agent
                session = requests.Session()
                session.headers.update({'User-Agent': user_agent})
                
                # Direct API request with custom session
                ticker = yf.Ticker(symbol, session=session)
                info = ticker.info
                hist = ticker.history(period="1d")
                
                if hist.empty or not info:
                    failures += 1
                    error_types['empty_data'] = error_types.get('empty_data', 0) + 1
                else:
                    successes += 1
                    response_times.append(time.time() - request_start)
                    # Track user agent success
                    ua_short = user_agent.split()[0] if user_agent else 'unknown'
                    user_agent_success[ua_short] = user_agent_success.get(ua_short, 0) + 1
                    
            except Exception as e:
                failures += 1
                error_type = type(e).__name__
                error_types[error_type] = error_types.get(error_type, 0) + 1
                
            # Progress updates
            if (i + 1) % 10 == 0:
                success_rate = (successes / (i + 1)) * 100
                print(f"   Progress: {i+1}/{num_requests} | Success Rate: {success_rate:.1f}%")
                
            # Apply delay
            if i < num_requests - 1:
                time.sleep(optimal_delay)
                
        total_time = time.time() - start_time
        success_rate = (successes / num_requests) * 100 if num_requests > 0 else 0
        avg_response_time = statistics.mean(response_times) if response_times else 0
        rps = num_requests / total_time if total_time > 0 else 0
        
        result = {
            'method': 'direct_api_user_agents',
            'success_rate': success_rate,
            'total_requests': num_requests,
            'successes': successes,
            'failures': failures,
            'avg_response_time': avg_response_time,
            'total_time': total_time,
            'requests_per_second': rps,
            'error_types': error_types,
            'delay_used': optimal_delay,
            'user_agent_success': user_agent_success
        }
        
        print(f"   User Agent Enhancement: {success_rate:.1f}% success, {rps:.2f} RPS")
        self.print_result(f"User agents used: {len(user_agent_success)} different agents")
        return result
    
    # ==================== ENHANCEMENT 2: HEADER OPTIMIZATION ====================
    
    def test_direct_api_with_headers(self, optimal_delay: float = 1.0, num_requests: int = 30) -> Dict:
        """Enhance direct API with optimized headers"""
        self.print_step("📋", "DIRECT API + OPTIMIZED HEADERS")
        
        print(f"🌐 Testing direct requests with optimized headers, {optimal_delay}s delay, {num_requests} requests...")
        
        start_time = time.time()
        successes = 0
        failures = 0
        response_times = []
        error_types = {}
        
        for i in range(num_requests):
            symbol = random.choice(self.test_symbols)
            request_start = time.time()
            
            try:
                # Create session with optimized headers
                session = requests.Session()
                
                # Randomize headers to appear more natural
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.8', 'en-CA,en;q=0.7']),
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': random.choice(['no-cache', 'max-age=0']),
                }
                
                session.headers.update(headers)
                
                # Direct API request with optimized headers
                ticker = yf.Ticker(symbol, session=session)
                info = ticker.info
                hist = ticker.history(period="1d")
                
                if hist.empty or not info:
                    failures += 1
                    error_types['empty_data'] = error_types.get('empty_data', 0) + 1
                else:
                    successes += 1
                    response_times.append(time.time() - request_start)
                    
            except Exception as e:
                failures += 1
                error_type = type(e).__name__
                error_types[error_type] = error_types.get(error_type, 0) + 1
                
            # Progress updates
            if (i + 1) % 10 == 0:
                success_rate = (successes / (i + 1)) * 100
                print(f"   Progress: {i+1}/{num_requests} | Success Rate: {success_rate:.1f}%")
                
            # Apply delay
            if i < num_requests - 1:
                time.sleep(optimal_delay)
                
        total_time = time.time() - start_time
        success_rate = (successes / num_requests) * 100 if num_requests > 0 else 0
        avg_response_time = statistics.mean(response_times) if response_times else 0
        rps = num_requests / total_time if total_time > 0 else 0
        
        result = {
            'method': 'direct_api_headers',
            'success_rate': success_rate,
            'total_requests': num_requests,
            'successes': successes,
            'failures': failures,
            'avg_response_time': avg_response_time,
            'total_time': total_time,
            'requests_per_second': rps,
            'error_types': error_types,
            'delay_used': optimal_delay
        }
        
        print(f"   Header Enhancement: {success_rate:.1f}% success, {rps:.2f} RPS")
        return result
    
    # ==================== ENHANCEMENT 3: SESSION PERSISTENCE ====================
    
    def test_direct_api_with_session_persistence(self, optimal_delay: float = 1.0, num_requests: int = 30) -> Dict:
        """Enhance direct API with persistent session"""
        self.print_step("🔗", "DIRECT API + SESSION PERSISTENCE")
        
        print(f"🌐 Testing direct requests with session persistence, {optimal_delay}s delay, {num_requests} requests...")
        
        # Create persistent session
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })
        
        start_time = time.time()
        successes = 0
        failures = 0
        response_times = []
        error_types = {}
        
        for i in range(num_requests):
            symbol = random.choice(self.test_symbols)
            request_start = time.time()
            
            try:
                # Direct API request with persistent session
                ticker = yf.Ticker(symbol, session=session)
                info = ticker.info
                hist = ticker.history(period="1d")
                
                if hist.empty or not info:
                    failures += 1
                    error_types['empty_data'] = error_types.get('empty_data', 0) + 1
                else:
                    successes += 1
                    response_times.append(time.time() - request_start)
                    
            except Exception as e:
                failures += 1
                error_type = type(e).__name__
                error_types[error_type] = error_types.get(error_type, 0) + 1
                
            # Progress updates
            if (i + 1) % 10 == 0:
                success_rate = (successes / (i + 1)) * 100
                print(f"   Progress: {i+1}/{num_requests} | Success Rate: {success_rate:.1f}%")
                
            # Apply delay
            if i < num_requests - 1:
                time.sleep(optimal_delay)
                
        total_time = time.time() - start_time
        success_rate = (successes / num_requests) * 100 if num_requests > 0 else 0
        avg_response_time = statistics.mean(response_times) if response_times else 0
        rps = num_requests / total_time if total_time > 0 else 0
        
        result = {
            'method': 'direct_api_session_persistence',
            'success_rate': success_rate,
            'total_requests': num_requests,
            'successes': successes,
            'failures': failures,
            'avg_response_time': avg_response_time,
            'total_time': total_time,
            'requests_per_second': rps,
            'error_types': error_types,
            'delay_used': optimal_delay
        }
        
        print(f"   Session Persistence: {success_rate:.1f}% success, {rps:.2f} RPS")
        return result
    
    # ==================== ENHANCEMENT 4: ADAPTIVE TIMING ====================
    
    def test_direct_api_with_adaptive_timing(self, base_delay: float = 1.0, num_requests: int = 30) -> Dict:
        """Enhance direct API with adaptive timing based on success/failure"""
        self.print_step("⏰", "DIRECT API + ADAPTIVE TIMING")
        
        print(f"🌐 Testing direct requests with adaptive timing, base {base_delay}s delay, {num_requests} requests...")
        
        start_time = time.time()
        successes = 0
        failures = 0
        response_times = []
        error_types = {}
        adaptive_delays = []
        current_delay = base_delay
        
        for i in range(num_requests):
            symbol = random.choice(self.test_symbols)
            request_start = time.time()
            
            try:
                # Direct API request
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="1d")
                
                if hist.empty or not info:
                    failures += 1
                    error_types['empty_data'] = error_types.get('empty_data', 0) + 1
                    # Increase delay on failure
                    current_delay = min(current_delay * 1.2, 3.0)
                else:
                    successes += 1
                    response_times.append(time.time() - request_start)
                    # Decrease delay on success
                    current_delay = max(current_delay * 0.95, 0.1)
                    
            except Exception as e:
                failures += 1
                error_type = type(e).__name__
                error_types[error_type] = error_types.get(error_type, 0) + 1
                # Increase delay on exception
                current_delay = min(current_delay * 1.5, 5.0)
                
            adaptive_delays.append(current_delay)
            
            # Progress updates
            if (i + 1) % 10 == 0:
                success_rate = (successes / (i + 1)) * 100
                avg_delay = statistics.mean(adaptive_delays[-10:])  # Last 10 delays
                print(f"   Progress: {i+1}/{num_requests} | Success Rate: {success_rate:.1f}% | Avg Delay: {avg_delay:.2f}s")
                
            # Apply adaptive delay
            if i < num_requests - 1:
                time.sleep(current_delay)
                
        total_time = time.time() - start_time
        success_rate = (successes / num_requests) * 100 if num_requests > 0 else 0
        avg_response_time = statistics.mean(response_times) if response_times else 0
        rps = num_requests / total_time if total_time > 0 else 0
        avg_adaptive_delay = statistics.mean(adaptive_delays) if adaptive_delays else base_delay
        
        result = {
            'method': 'direct_api_adaptive_timing',
            'success_rate': success_rate,
            'total_requests': num_requests,
            'successes': successes,
            'failures': failures,
            'avg_response_time': avg_response_time,
            'total_time': total_time,
            'requests_per_second': rps,
            'error_types': error_types,
            'base_delay': base_delay,
            'avg_adaptive_delay': avg_adaptive_delay,
            'final_delay': current_delay
        }
        
        print(f"   Adaptive Timing: {success_rate:.1f}% success, {rps:.2f} RPS")
        print(f"   Final delay: {current_delay:.2f}s (started at {base_delay}s)")
        return result
    
    # ==================== COMPREHENSIVE TEST RUNNER ====================
    
    def run_comprehensive_test(self) -> Dict:
        """Run all direct API enhancements with proper isolation"""
        self.print_header("ENHANCED DIRECT API TESTING")
        
        all_results = {}
        
        # Step 1: Core direct API test
        print(f"\n📋 Running Test 1/4: CORE DIRECT API")
        core_result = self.test_direct_api_requests()
        all_results['core_direct_api'] = core_result
        optimal_delay = core_result.get('best_delay', 1.0)
        
        # Show core results
        print(f"   📊 Core: {core_result['success_rate']:.1f}% success")
        print(f"   ⚡ Speed: {core_result['requests_per_second']:.2f} req/s")
        print(f"   🎯 Best delay: {optimal_delay}s")
        
        # Isolation delay
        self.test_isolation_delay("CORE DIRECT API")
        
        # Step 2: User agent enhancement
        print(f"\n📋 Running Test 2/4: + USER AGENT ROTATION")
        try:
            ua_result = self.test_direct_api_with_user_agents(optimal_delay, 30)
            all_results['direct_api_user_agents'] = ua_result
            print(f"   📊 +User Agents: {ua_result['success_rate']:.1f}% success")
            print(f"   ⚡ Speed: {ua_result['requests_per_second']:.2f} req/s")
        except Exception as e:
            print(f"   ❌ User agent test failed: {e}")
            all_results['direct_api_user_agents'] = {'error': str(e), 'success_rate': 0}
        
        self.test_isolation_delay("USER AGENT ROTATION")
        
        # Step 3: Header optimization
        print(f"\n📋 Running Test 3/4: + OPTIMIZED HEADERS")
        try:
            header_result = self.test_direct_api_with_headers(optimal_delay, 30)
            all_results['direct_api_headers'] = header_result
            print(f"   📊 +Headers: {header_result['success_rate']:.1f}% success")
            print(f"   ⚡ Speed: {header_result['requests_per_second']:.2f} req/s")
        except Exception as e:
            print(f"   ❌ Header test failed: {e}")
            all_results['direct_api_headers'] = {'error': str(e), 'success_rate': 0}
        
        self.test_isolation_delay("OPTIMIZED HEADERS")
        
        # Step 4: Session persistence
        print(f"\n📋 Running Test 4/4: + SESSION PERSISTENCE")
        try:
            session_result = self.test_direct_api_with_session_persistence(optimal_delay, 30)
            all_results['direct_api_session'] = session_result
            print(f"   📊 +Session: {session_result['success_rate']:.1f}% success")
            print(f"   ⚡ Speed: {session_result['requests_per_second']:.2f} req/s")
        except Exception as e:
            print(f"   ❌ Session test failed: {e}")
            all_results['direct_api_session'] = {'error': str(e), 'success_rate': 0}
        
        # Analyze and rank results
        return self.analyze_results(all_results, core_result)
    
    def analyze_results(self, results: Dict, core_result: Dict) -> Dict:
        """Analyze test results and determine best enhancements"""
        self.print_header("ENHANCEMENT ANALYSIS")
        
        valid_results = {k: v for k, v in results.items() if 'error' not in v}
        
        if not valid_results:
            self.print_result("No valid test results", success=False)
            return {}
        
        # Show core baseline
        print(f"\n📊 CORE DIRECT API BASELINE:")
        print(f"   🌐 Core Method: {core_result['success_rate']:.1f}% success, {core_result['requests_per_second']:.2f} RPS")
        print(f"   ⏰ Best delay: {core_result['best_delay']}s")
        
        # Rank enhancements by success rate
        enhancement_results = {k: v for k, v in valid_results.items() if k != 'core_direct_api'}
        
        if enhancement_results:
            ranked_by_success = sorted(enhancement_results.items(), 
                                     key=lambda x: x[1]['success_rate'], reverse=True)
            
            print("\n🏆 ENHANCEMENTS - RANKING BY SUCCESS RATE:")
            for i, (method, result) in enumerate(ranked_by_success, 1):
                improvement = result['success_rate'] - core_result['success_rate']
                improvement_str = f" ({improvement:+.1f}%)" if improvement != 0 else " (same)"
                print(f"   {i}. {method.replace('direct_api_', '+')}: {result['success_rate']:.1f}% success{improvement_str}")
                
            # Speed ranking
            ranked_by_speed = sorted(enhancement_results.items(), 
                                   key=lambda x: x[1]['requests_per_second'], reverse=True)
            
            print("\n⚡ ENHANCEMENTS - RANKING BY SPEED:")
            for i, (method, result) in enumerate(ranked_by_speed, 1):
                speed_diff = result['requests_per_second'] - core_result['requests_per_second']
                speed_str = f" ({speed_diff:+.2f} RPS)" if speed_diff != 0 else " (same)"
                print(f"   {i}. {method.replace('direct_api_', '+')}: {result['requests_per_second']:.2f} req/s{speed_str}")
                
            # Best enhancement
            best_enhancement = ranked_by_success[0]
            self.print_result(f"BEST ENHANCEMENT: {best_enhancement[0].replace('direct_api_', '+')} ({best_enhancement[1]['success_rate']:.1f}% success)")
        else:
            print("\n⚠️ No enhancement results available")
            best_enhancement = None
        
        # Generate recommendations
        recommendations = self.generate_recommendations(valid_results, core_result, best_enhancement)
        
        final_result = {
            'core_method': 'direct_api_requests',
            'core_success_rate': core_result['success_rate'],
            'best_enhancement': best_enhancement[0] if best_enhancement else None,
            'best_enhanced_success_rate': best_enhancement[1]['success_rate'] if best_enhancement else core_result['success_rate'],
            'all_results': results,
            'core_result': core_result,
            'recommendations': recommendations
        }
        
        return final_result
    
    def generate_recommendations(self, results: Dict, core_result: Dict, best_enhancement: Tuple = None) -> List[str]:
        """Generate implementation recommendations"""
        recommendations = []
        
        # Core method recommendation
        recommendations.append(f"🌐 Core Method: Direct API with {core_result['best_delay']}s delay ({core_result['success_rate']:.1f}% success)")
        
        if best_enhancement:
            enhancement_name, enhancement_result = best_enhancement
            improvement = enhancement_result['success_rate'] - core_result['success_rate']
            
            if improvement > 5:
                recommendations.append(f"✅ {enhancement_name.replace('direct_api_', '')} significantly improves success by {improvement:.1f}%")
            elif improvement > 1:
                recommendations.append(f"⚡ {enhancement_name.replace('direct_api_', '')} provides modest improvement of {improvement:.1f}%")
            elif improvement >= 0:
                recommendations.append(f"📊 {enhancement_name.replace('direct_api_', '')} maintains performance with potential stability benefits")
            else:
                recommendations.append(f"⚠️ Core method outperforms enhancements - stick with basic direct API")
                
            # Enhancement-specific recommendations
            if 'user_agents' in enhancement_name:
                recommendations.append("🎭 Implement user agent rotation for better anonymity")
            elif 'headers' in enhancement_name:
                recommendations.append("📋 Use optimized headers to mimic real browser requests")
            elif 'session' in enhancement_name:
                recommendations.append("🔗 Session persistence reduces connection overhead")
            elif 'adaptive' in enhancement_name:
                recommendations.append("⏰ Adaptive timing automatically adjusts to API response")
        else:
            recommendations.append("🎯 Core direct API method is sufficient - no enhancements needed")
            
        # Performance recommendations
        core_rps = core_result['requests_per_second']
        if core_rps >= 2.0:
            recommendations.append("🚀 High performance achieved - suitable for production")
        elif core_rps >= 1.0:
            recommendations.append("⚡ Good performance - suitable for regular use")
        else:
            recommendations.append("🐌 Consider increasing delays for better stability")
            
        return recommendations
    
    def save_results(self, results: Dict, filename: str = None):
        """Save test results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"enhanced_direct_api_results_{timestamp}.json"
            
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
            
        self.print_result(f"Results saved to {filename}")

def main():
    """Main execution function"""
    print("🚀 Enhanced Direct API Yahoo Finance Optimizer")
    print("=" * 70)
    print("📋 Tests: Core Direct API + 4 Enhancement Layers")
    print("=" * 70)
    
    optimizer = EnhancedDirectAPIOptimizer()
    
    try:
        # Run comprehensive tests
        results = optimizer.run_comprehensive_test()
        
        # Save results
        optimizer.save_results(results)
        
        # Final summary
        optimizer.print_header("TESTING COMPLETE")
        if results:
            print(f"🌐 Core Method: {results['core_method']} ({results['core_success_rate']:.1f}% success)")
            if results['best_enhancement']:
                enhancement_name = results['best_enhancement'].replace('direct_api_', '+')
                print(f"🏆 Best Enhancement: {enhancement_name} ({results['best_enhanced_success_rate']:.1f}% success)")
                improvement = results['best_enhanced_success_rate'] - results['core_success_rate']
                print(f"📈 Improvement: {improvement:+.1f}% over core method")
            else:
                print("📊 Core method performs best without enhancements")
                
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in results['recommendations']:
                print(f"   {rec}")
        else:
            print("❌ No successful tests completed")
            
        print(f"\n🎯 Next Steps:")
        print(f"   1. Review saved results file")
        print(f"   2. Implement recommended configuration")
        print(f"   3. Monitor performance in production")
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")

if __name__ == "__main__":
    main()