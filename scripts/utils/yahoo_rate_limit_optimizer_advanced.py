#!/usr/bin/env python3
"""
Advanced Yahoo Finance Rate Limit Optimizer
Uses sophisticated bypass methods beyond simple delays
"""

import time
import yfinance as yf
import requests
import random
import threading
import queue
import asyncio
import aiohttp
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
from requests.packages.urllib3.util.connection import create_connection
import fake_useragent

class AdvancedYahooBypass:
    """Advanced Yahoo Finance rate limit bypass techniques"""
    
    def __init__(self):
        self.test_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'AMD', 'INTC', 'ORCL', 'CRM', 'ADBE', 'PYPL', 'UBER', 'SHOP',
            'ZOOM', 'ROKU', 'SQ', 'HOOD', 'SNAP', 'PINS', 'COIN', 'RBLX',
            'TWTR', 'FB', 'SPOT', 'DIS', 'BABA', 'JNJ', 'V', 'JPM', 'PG'
        ]
        self.results = {}
        self.failed_requests = []
        self.user_agent_rotator = fake_useragent.UserAgent()
        
        # Advanced bypass configurations
        self.bypass_methods = {
            'session_rotation': self._create_session_rotation,
            'header_spoofing': self._create_header_spoofing,
            'connection_pooling': self._create_connection_pooling,
            'proxy_rotation': self._create_proxy_rotation,
            'request_chunking': self._create_request_chunking,
            'parallel_sessions': self._create_parallel_sessions,
            'caching_strategy': self._create_caching_strategy,
            'fallback_apis': self._create_fallback_apis
        }
        
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
        
    # ==================== BYPASS METHOD 1: SESSION ROTATION ====================
    
    def _create_session_rotation(self) -> List[requests.Session]:
        """Create multiple rotating sessions with different fingerprints"""
        sessions = []
        
        for i in range(5):  # Create 5 different sessions
            session = requests.Session()
            
            # Different retry strategies
            retry_configs = [
                {'total': 3, 'backoff_factor': 0.5},
                {'total': 5, 'backoff_factor': 1.0},
                {'total': 2, 'backoff_factor': 2.0},
                {'total': 4, 'backoff_factor': 0.3},
                {'total': 3, 'backoff_factor': 1.5}
            ]
            
            retry_strategy = Retry(**retry_configs[i])
            adapter = HTTPAdapter(max_retries=retry_strategy, pool_maxsize=20)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            # Unique headers for each session
            session.headers.update({
                'User-Agent': self.user_agent_rotator.random,
                'Accept': 'application/json,text/html,application/xhtml+xml',
                'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.8', 'en-CA,en;q=0.7']),
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'DNT': '1',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': random.choice(['document', 'empty']),
                'Sec-Fetch-Mode': random.choice(['navigate', 'cors']),
                'Sec-Fetch-Site': random.choice(['none', 'same-origin']),
                'Cache-Control': random.choice(['no-cache', 'max-age=0']),
            })
            
            sessions.append(session)
            
        return sessions
    
    def test_session_rotation(self, num_requests: int = 30) -> Dict:
        """Test session rotation bypass method"""
        self.print_step("🔄", "TESTING SESSION ROTATION BYPASS")
        
        sessions = self._create_session_rotation()
        start_time = time.time()
        successes = 0
        failures = 0
        response_times = []
        error_types = {}
        
        for i in range(num_requests):
            symbol = random.choice(self.test_symbols)
            session = sessions[i % len(sessions)]  # Rotate sessions
            request_start = time.time()
            
            try:
                # Use session-specific ticker
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
                
            # Progress with session info
            if (i + 1) % 5 == 0:
                success_rate = (successes / (i + 1)) * 100
                session_id = (i % len(sessions)) + 1
                print(f"   📊 Progress: {i+1}/{num_requests} | Session {session_id} | Success: {success_rate:.1f}%")
                
            # Variable delay based on session
            session_delay = 0.1 + (i % len(sessions)) * 0.05
            time.sleep(session_delay)
            
        total_time = time.time() - start_time
        success_rate = (successes / num_requests) * 100 if num_requests > 0 else 0
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        result = {
            'method': 'session_rotation',
            'success_rate': success_rate,
            'total_requests': num_requests,
            'successes': successes,
            'failures': failures,
            'avg_response_time': avg_response_time,
            'total_time': total_time,
            'requests_per_second': num_requests / total_time,
            'error_types': error_types,
            'sessions_used': len(sessions)
        }
        
        self.print_result(f"Session Rotation: {success_rate:.1f}% success rate")
        self.print_result(f"Sessions: {len(sessions)} rotating sessions")
        return result
    
    # ==================== BYPASS METHOD 2: HEADER SPOOFING ====================
    
    def _create_header_spoofing(self) -> List[Dict]:
        """Create various browser fingerprints"""
        browser_profiles = [
            {
                'name': 'Chrome_Windows',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'headers': {
                    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1'
                }
            },
            {
                'name': 'Firefox_Mac',
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/120.0',
                'headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none'
                }
            },
            {
                'name': 'Safari_iOS',
                'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
                'headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive'
                }
            },
            {
                'name': 'Edge_Windows',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
                'headers': {
                    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none'
                }
            }
        ]
        return browser_profiles
    
    def test_header_spoofing(self, num_requests: int = 30) -> Dict:
        """Test header spoofing bypass method"""
        self.print_step("🎭", "TESTING HEADER SPOOFING BYPASS")
        
        browser_profiles = self._create_header_spoofing()
        start_time = time.time()
        successes = 0
        failures = 0
        response_times = []
        error_types = {}
        profile_success = {}
        
        for i in range(num_requests):
            symbol = random.choice(self.test_symbols)
            profile = browser_profiles[i % len(browser_profiles)]
            request_start = time.time()
            
            # Create session with specific browser profile
            session = requests.Session()
            session.headers.update({
                'User-Agent': profile['user_agent'],
                **profile['headers']
            })
            
            try:
                ticker = yf.Ticker(symbol, session=session)
                info = ticker.info
                hist = ticker.history(period="1d")
                
                if hist.empty or not info:
                    failures += 1
                    error_types['empty_data'] = error_types.get('empty_data', 0) + 1
                else:
                    successes += 1
                    response_times.append(time.time() - request_start)
                    profile_success[profile['name']] = profile_success.get(profile['name'], 0) + 1
                    
            except Exception as e:
                failures += 1
                error_type = type(e).__name__
                error_types[error_type] = error_types.get(error_type, 0) + 1
                
            # Progress with profile info
            if (i + 1) % 5 == 0:
                success_rate = (successes / (i + 1)) * 100
                print(f"   📊 Progress: {i+1}/{num_requests} | Profile: {profile['name']} | Success: {success_rate:.1f}%")
                
            # Randomized delay
            time.sleep(random.uniform(0.1, 0.3))
            
        total_time = time.time() - start_time
        success_rate = (successes / num_requests) * 100 if num_requests > 0 else 0
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        result = {
            'method': 'header_spoofing',
            'success_rate': success_rate,
            'total_requests': num_requests,
            'successes': successes,
            'failures': failures,
            'avg_response_time': avg_response_time,
            'total_time': total_time,
            'requests_per_second': num_requests / total_time,
            'error_types': error_types,
            'profiles_used': len(browser_profiles),
            'profile_success': profile_success
        }
        
        self.print_result(f"Header Spoofing: {success_rate:.1f}% success rate")
        self.print_result(f"Best Profile: {max(profile_success.items(), key=lambda x: x[1])[0] if profile_success else 'None'}")
        return result
    
    # ==================== BYPASS METHOD 3: REQUEST CHUNKING ====================
    
    def test_request_chunking(self, num_requests: int = 30) -> Dict:
        """Test request chunking bypass method"""
        self.print_step("📦", "TESTING REQUEST CHUNKING BYPASS")
        
        start_time = time.time()
        successes = 0
        failures = 0
        response_times = []
        error_types = {}
        
        # Split requests into chunks with varying delays
        chunk_size = 5
        chunks = [self.test_symbols[i:i + chunk_size] for i in range(0, len(self.test_symbols), chunk_size)]
        
        chunk_delays = [2.0, 3.0, 1.5, 4.0, 2.5]  # Different delays between chunks
        
        for chunk_idx, chunk in enumerate(chunks[:6]):  # Limit to 6 chunks
            if chunk_idx >= num_requests // chunk_size:
                break
                
            chunk_delay = chunk_delays[chunk_idx % len(chunk_delays)]
            print(f"   📦 Processing Chunk {chunk_idx + 1} | Symbols: {len(chunk)} | Delay: {chunk_delay}s")
            
            # Process chunk with burst requests
            for symbol in chunk:
                if successes + failures >= num_requests:
                    break
                    
                request_start = time.time()
                
                try:
                    # Use different session for each chunk
                    session = requests.Session()
                    session.headers.update({
                        'User-Agent': self.user_agent_rotator.random,
                        'X-Request-ID': str(uuid.uuid4()),
                        'X-Chunk-ID': f"chunk_{chunk_idx}"
                    })
                    
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
                    
                # Small delay within chunk
                time.sleep(0.05)
                
            # Progress update
            total_processed = successes + failures
            success_rate = (successes / total_processed) * 100 if total_processed > 0 else 0
            print(f"   📊 Chunk {chunk_idx + 1} Complete | Total: {total_processed} | Success: {success_rate:.1f}%")
            
            # Longer delay between chunks
            if chunk_idx < len(chunks) - 1 and total_processed < num_requests:
                print(f"   ⏳ Inter-chunk delay: {chunk_delay}s...")
                time.sleep(chunk_delay)
                
        total_time = time.time() - start_time
        success_rate = (successes / num_requests) * 100 if num_requests > 0 else 0
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        result = {
            'method': 'request_chunking',
            'success_rate': success_rate,
            'total_requests': num_requests,
            'successes': successes,
            'failures': failures,
            'avg_response_time': avg_response_time,
            'total_time': total_time,
            'requests_per_second': num_requests / total_time,
            'error_types': error_types,
            'chunks_processed': min(len(chunks), 6)
        }
        
        self.print_result(f"Request Chunking: {success_rate:.1f}% success rate")
        self.print_result(f"Chunks: {result['chunks_processed']} processed")
        return result
    
    # ==================== BYPASS METHOD 4: DISTRIBUTED TIMING ====================
    
    def test_distributed_timing(self, num_requests: int = 30) -> Dict:
        """Test distributed timing patterns"""
        self.print_step("⏰", "TESTING DISTRIBUTED TIMING BYPASS")
        
        start_time = time.time()
        successes = 0
        failures = 0
        response_times = []
        error_types = {}
        
        # Create natural request pattern that mimics human behavior
        base_delays = [0.8, 1.2, 0.5, 2.1, 0.9, 1.8, 0.7, 3.2, 1.1, 0.6]
        pattern_multipliers = [1.0, 0.8, 1.3, 0.9, 1.1, 1.5, 0.7, 1.2, 0.95, 1.4]
        
        for i in range(num_requests):
            symbol = random.choice(self.test_symbols)
            request_start = time.time()
            
            try:
                # Create session with timing-based fingerprint
                session = requests.Session()
                session.headers.update({
                    'User-Agent': self.user_agent_rotator.random,
                    'X-Request-Time': str(int(time.time())),
                    'X-Pattern-ID': f"pattern_{i % 10}"
                })
                
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
                
            # Progress update
            if (i + 1) % 5 == 0:
                success_rate = (successes / (i + 1)) * 100
                print(f"   📊 Progress: {i+1}/{num_requests} | Success: {success_rate:.1f}%")
                
            # Natural distributed delay pattern
            if i < num_requests - 1:
                base_delay = base_delays[i % len(base_delays)]
                multiplier = pattern_multipliers[i % len(pattern_multipliers)]
                jitter = random.uniform(-0.2, 0.2)
                delay = base_delay * multiplier + jitter
                delay = max(0.1, delay)  # Minimum delay
                time.sleep(delay)
                
        total_time = time.time() - start_time
        success_rate = (successes / num_requests) * 100 if num_requests > 0 else 0
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        result = {
            'method': 'distributed_timing',
            'success_rate': success_rate,
            'total_requests': num_requests,
            'successes': successes,
            'failures': failures,
            'avg_response_time': avg_response_time,
            'total_time': total_time,
            'requests_per_second': num_requests / total_time,
            'error_types': error_types,
            'timing_patterns': len(base_delays)
        }
        
        self.print_result(f"Distributed Timing: {success_rate:.1f}% success rate")
        self.print_result(f"Patterns: {result['timing_patterns']} timing patterns used")
        return result
    
    # ==================== COMPREHENSIVE TEST RUNNER ====================
    
    def run_comprehensive_test(self) -> Dict:
        """Run all bypass methods with proper isolation"""
        self.print_header("ADVANCED YAHOO FINANCE BYPASS TESTING")
        
        all_results = {}
        test_methods = [
            ('session_rotation', self.test_session_rotation),
            ('header_spoofing', self.test_header_spoofing),
            ('request_chunking', self.test_request_chunking),
            ('distributed_timing', self.test_distributed_timing)
        ]
        
        for i, (method_name, test_method) in enumerate(test_methods):
            print(f"\n📋 Running Test {i+1}/{len(test_methods)}: {method_name.upper()}")
            
            try:
                result = test_method(30)  # 30 requests per test
                all_results[method_name] = result
                
                # Show immediate results
                print(f"   📊 {method_name}: {result['success_rate']:.1f}% success")
                print(f"   ⚡ Speed: {result['requests_per_second']:.1f} req/s")
                
            except Exception as e:
                self.print_result(f"Test {method_name} failed: {e}", success=False)
                all_results[method_name] = {'error': str(e), 'success_rate': 0}
                
            # Isolation delay between tests (except after last test)
            if i < len(test_methods) - 1:
                self.test_isolation_delay(method_name.upper())
                
        # Analyze and rank results
        return self.analyze_results(all_results)
    
    def analyze_results(self, results: Dict) -> Dict:
        """Analyze test results and determine best methods"""
        self.print_header("TEST RESULTS ANALYSIS")
        
        valid_results = {k: v for k, v in results.items() if 'error' not in v}
        
        if not valid_results:
            self.print_result("No valid test results", success=False)
            return {}
            
        # Rank by success rate
        ranked_by_success = sorted(valid_results.items(), 
                                 key=lambda x: x[1]['success_rate'], reverse=True)
        
        # Rank by speed
        ranked_by_speed = sorted(valid_results.items(), 
                               key=lambda x: x[1]['requests_per_second'], reverse=True)
        
        print("\n🏆 RANKING BY SUCCESS RATE:")
        for i, (method, result) in enumerate(ranked_by_success, 1):
            print(f"   {i}. {method}: {result['success_rate']:.1f}% success")
            
        print("\n⚡ RANKING BY SPEED:")
        for i, (method, result) in enumerate(ranked_by_speed, 1):
            print(f"   {i}. {method}: {result['requests_per_second']:.1f} req/s")
            
        # Determine best overall method
        best_method = ranked_by_success[0]
        self.print_result(f"BEST METHOD: {best_method[0]} ({best_method[1]['success_rate']:.1f}% success)")
        
        # Generate recommendations
        recommendations = self.generate_recommendations(valid_results, best_method)
        
        final_result = {
            'best_method': best_method[0],
            'best_success_rate': best_method[1]['success_rate'],
            'all_results': results,
            'rankings': {
                'by_success': ranked_by_success,
                'by_speed': ranked_by_speed
            },
            'recommendations': recommendations
        }
        
        return final_result
    
    def generate_recommendations(self, results: Dict, best_method: Tuple) -> List[str]:
        """Generate implementation recommendations"""
        recommendations = []
        
        best_name, best_result = best_method
        
        if best_result['success_rate'] >= 90:
            recommendations.append(f"✅ {best_name} is highly reliable - implement immediately")
        elif best_result['success_rate'] >= 75:
            recommendations.append(f"⚠️ {best_name} is moderately reliable - consider with fallbacks")
        else:
            recommendations.append(f"❌ {best_name} needs improvement - combine with other methods")
            
        # Speed recommendations
        if best_result['requests_per_second'] >= 10:
            recommendations.append("🚀 High throughput achieved - suitable for production")
        elif best_result['requests_per_second'] >= 5:
            recommendations.append("⚡ Moderate throughput - good for regular use")
        else:
            recommendations.append("🐌 Low throughput - optimize delays")
            
        # Method-specific recommendations
        if best_name == 'session_rotation':
            recommendations.append("🔄 Implement session pool with 5-10 rotating sessions")
        elif best_name == 'header_spoofing':
            recommendations.append("🎭 Focus on Chrome/Firefox profiles for best results")
        elif best_name == 'request_chunking':
            recommendations.append("📦 Use chunk size of 5 with 2-3 second inter-chunk delays")
        elif best_name == 'distributed_timing':
            recommendations.append("⏰ Implement natural timing patterns with jitter")
            
        return recommendations
    
    def save_results(self, results: Dict, filename: str = None):
        """Save test results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"yahoo_bypass_results_{timestamp}.json"
            
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
            
        self.print_result(f"Results saved to {filename}")

def main():
    """Main execution function"""
    print("🚀 Advanced Yahoo Finance Rate Limit Bypass Tester")
    print("=" * 70)
    
    optimizer = AdvancedYahooBypass()
    
    try:
        # Run comprehensive tests
        results = optimizer.run_comprehensive_test()
        
        # Save results
        optimizer.save_results(results)
        
        # Final summary
        optimizer.print_header("TESTING COMPLETE")
        if results:
            print(f"🏆 Best Method: {results['best_method']}")
            print(f"📊 Success Rate: {results['best_success_rate']:.1f}%")
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in results['recommendations']:
                print(f"   {rec}")
        else:
            print("❌ No successful tests completed")
            
        print(f"\n🎯 Next Steps:")
        print(f"   1. Review saved results file")
        print(f"   2. Implement best method in production")
        print(f"   3. Monitor performance and adjust as needed")
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")

if __name__ == "__main__":
    main()