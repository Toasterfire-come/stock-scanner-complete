#!/usr/bin/env python3
"""
Enhanced Production-Ready Yahoo Finance Direct API Optimizer v2.0
Implements direct Yahoo Finance API calls with advanced rate limit optimization

Features:
- Direct Yahoo Finance API integration with full data extraction
- Advanced User Agent Rotation (20+ realistic agents)
- Dynamic Optimized Headers with randomization
- Adaptive timing based on response patterns
- Session persistence with connection pooling
- Comprehensive error handling and logging
- Real-time success rate monitoring
- Automatic result saving and analysis
- Production-ready architecture

Author: Stock Scanner Project
Version: 2.0.0
"""

import time
import requests
import random
import json
import statistics
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from concurrent.futures import ThreadPoolExecutor
import threading

# Configure production logging
def setup_logging():
    """Setup production-grade logging configuration"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(
        f'{log_dir}/yahoo_api_optimizer_{datetime.now().strftime("%Y%m%d")}.log'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Setup logger
    logger = logging.getLogger('YahooAPIOptimizer')
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

class EnhancedYahooAPIOptimizer:
    """
    Enhanced production-ready Yahoo Finance API optimizer
    """
    
    def __init__(self, timeout: int = 15, max_retries: int = 3, pool_size: int = 10):
        """
        Initialize the enhanced optimizer
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            pool_size: Connection pool size
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.pool_size = pool_size
        
        # Comprehensive stock symbol pool
        self.test_symbols = [
            # Large Cap Tech
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            # Mid Cap Tech
            'AMD', 'INTC', 'ORCL', 'CRM', 'ADBE', 'PYPL', 'UBER', 'SHOP',
            # Growth Stocks
            'ZOOM', 'ROKU', 'SQ', 'HOOD', 'SNAP', 'PINS', 'COIN', 'RBLX',
            # Traditional Stocks
            'JNJ', 'V', 'JPM', 'PG', 'DIS', 'KO', 'WMT', 'PFE',
            # International
            'BABA', 'TSM', 'ASML', 'NVO', 'TM', 'NESN'
        ]
        
        # Enhanced user agent pool (20+ realistic agents)
        self.user_agents = [
            # Chrome Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            
            # Chrome macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            
            # Firefox Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 11.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0',
            
            # Firefox macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.2; rv:120.0) Gecko/20100101 Firefox/120.0',
            
            # Safari macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            
            # Edge Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
            'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            
            # Chrome Linux
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
            
            # Mobile
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 14; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0'
        ]
        
        # Accept language variations
        self.accept_languages = [
            'en-US,en;q=0.9',
            'en-GB,en;q=0.8',
            'en-CA,en;q=0.7',
            'en-AU,en;q=0.6',
            'en-US,en;q=0.9,es;q=0.8',
            'en-GB,en;q=0.9,fr;q=0.8'
        ]
        
        # Results storage
        self.results = {}
        self.session = self._create_optimized_session()
        self.lock = threading.Lock()
        
        logger.info(f"Enhanced Yahoo API Optimizer v2.0 initialized - Pool Size: {pool_size}")
    
    def _create_optimized_session(self) -> requests.Session:
        """
        Create an optimized requests session with advanced configuration
        
        Returns:
            Configured requests session with connection pooling
        """
        session = requests.Session()
        
        # Advanced retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1.5,
            status_forcelist=[429, 500, 502, 503, 504, 520, 521, 522, 524],
            allowed_methods=["GET"],
            raise_on_status=False
        )
        
        # HTTP adapter with connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=self.pool_size,
            pool_maxsize=self.pool_size * 2,
            pool_block=False
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set initial headers
        session.headers.update(self._get_dynamic_headers())
        
        return session
    
    def _get_dynamic_headers(self) -> Dict[str, str]:
        """
        Generate dynamic optimized headers with randomization
        
        Returns:
            Dictionary of randomized optimized headers
        """
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': random.choice(self.accept_languages),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Pragma': 'no-cache',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': f'"{random.choice(["Windows", "macOS", "Linux"])}"'
        }
    
    def test_direct_requests_method(self, delay: float, num_requests: int = 50) -> Dict:
        """
        Test direct requests to Yahoo Finance API with full data extraction
        
        Args:
            delay: Delay between requests in seconds
            num_requests: Number of test requests
            
        Returns:
            Dictionary containing test results and metrics
        """
        logger.info(f"Testing direct requests with {delay}s delay, {num_requests} requests...")
        print(f"🌐 Testing direct requests with {delay}s delay, {num_requests} requests...")
        
        start_time = time.time()
        successes = 0
        failures = 0
        response_times = []
        error_types = {}
        data_quality_scores = []
        
        for i in range(num_requests):
            symbol = random.choice(self.test_symbols)
            request_start = time.time()
            
            try:
                # Rotate headers for each request
                self.session.headers.update(self._get_dynamic_headers())
                
                # Direct Yahoo Finance API call
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                response = self.session.get(url, timeout=self.timeout)
                
                request_time = time.time() - request_start
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if 'chart' in data and data['chart']['result']:
                            result = data['chart']['result'][0]
                            
                            # Validate data quality
                            quality_score = self._assess_data_quality(result)
                            data_quality_scores.append(quality_score)
                            
                            if quality_score > 0.7:  # High quality data threshold
                                successes += 1
                                response_times.append(request_time)
                                
                                # Log successful data extraction
                                if i < 5:  # Log first few for verification
                                    logger.debug(f"Successfully extracted data for {symbol}: Quality Score {quality_score:.2f}")
                            else:
                                failures += 1
                                error_types['low_quality_data'] = error_types.get('low_quality_data', 0) + 1
                        else:
                            failures += 1
                            error_types['invalid_data_structure'] = error_types.get('invalid_data_structure', 0) + 1
                    except json.JSONDecodeError:
                        failures += 1
                        error_types['json_decode_error'] = error_types.get('json_decode_error', 0) + 1
                else:
                    failures += 1
                    error_types[f'http_{response.status_code}'] = error_types.get(f'http_{response.status_code}', 0) + 1
                    
            except requests.exceptions.Timeout:
                failures += 1
                error_types['timeout'] = error_types.get('timeout', 0) + 1
            except requests.exceptions.ConnectionError:
                failures += 1
                error_types['connection_error'] = error_types.get('connection_error', 0) + 1
            except Exception as e:
                failures += 1
                error_type = type(e).__name__
                error_types[error_type] = error_types.get(error_type, 0) + 1
                logger.warning(f"Unexpected error for {symbol}: {e}")
            
            # Progress indicator
            if (i + 1) % 10 == 0 or i == 0:
                success_rate = (successes / (i + 1)) * 100
                print(f"   Progress: {i+1}/{num_requests} | Success Rate: {success_rate:.1f}%")
            
            # Add delay between requests
            if i < num_requests - 1:
                time.sleep(delay)
        
        total_time = time.time() - start_time
        success_rate = (successes / num_requests) * 100
        avg_response_time = statistics.mean(response_times) if response_times else 0
        requests_per_second = num_requests / total_time if total_time > 0 else 0
        avg_quality_score = statistics.mean(data_quality_scores) if data_quality_scores else 0
        
        result = {
            'method': 'direct_api_requests',
            'delay': delay,
            'num_requests': num_requests,
            'successes': successes,
            'failures': failures,
            'success_rate': success_rate,
            'total_time': total_time,
            'avg_response_time': avg_response_time,
            'requests_per_second': requests_per_second,
            'avg_data_quality': avg_quality_score,
            'error_types': error_types,
            'timestamp': datetime.now().isoformat()
        }
        
        # Log detailed results
        logger.info(f"Test completed - Success Rate: {success_rate:.1f}%, RPS: {requests_per_second:.2f}, Quality: {avg_quality_score:.2f}")
        
        print(f"   Delay {delay}s: {success_rate:.1f}% success, {requests_per_second:.2f} RPS, Quality: {avg_quality_score:.2f}")
        
        return result
    
    def _assess_data_quality(self, result: Dict) -> float:
        """
        Assess the quality of extracted Yahoo Finance data
        
        Args:
            result: Yahoo Finance API result data
            
        Returns:
            Quality score between 0 and 1
        """
        score = 0.0
        checks = 0
        
        # Check for essential fields
        if 'meta' in result:
            score += 0.3
            meta = result['meta']
            
            # Check meta fields
            if 'symbol' in meta: score += 0.1
            if 'regularMarketPrice' in meta: score += 0.1
            if 'currency' in meta: score += 0.05
            
        checks += 1
        
        # Check for timestamp data
        if 'timestamp' in result and result['timestamp']:
            score += 0.2
            if len(result['timestamp']) > 10:  # Sufficient data points
                score += 0.1
        checks += 1
        
        # Check for indicators (OHLCV data)
        if 'indicators' in result:
            indicators = result['indicators']
            if 'quote' in indicators and indicators['quote']:
                quote = indicators['quote'][0]
                if 'close' in quote and quote['close']: score += 0.15
                if 'volume' in quote and quote['volume']: score += 0.1
                if 'open' in quote and quote['open']: score += 0.05
                if 'high' in quote and quote['high']: score += 0.05
                if 'low' in quote and quote['low']: score += 0.05
        checks += 1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def run_comprehensive_test(self, delays: List[float] = None, num_requests: int = 50) -> Dict:
        """
        Run comprehensive testing with multiple delay configurations
        
        Args:
            delays: List of delays to test
            num_requests: Number of requests per test
            
        Returns:
            Complete test results
        """
        if delays is None:
            delays = [0.5, 1.0, 1.5, 2.0]
        
        print("\n" + "="*70)
        print("🚀 ENHANCED YAHOO FINANCE API OPTIMIZER v2.0")
        print("="*70)
        print(f"Testing {len(delays)} delay configurations with {num_requests} requests each")
        print(f"User Agents: {len(self.user_agents)} rotating agents")
        print(f"Test Symbols: {len(self.test_symbols)} symbols")
        print("="*70)
        
        all_results = []
        best_result = None
        best_score = 0
        
        for i, delay in enumerate(delays, 1):
            print(f"\n📊 TEST {i}/{len(delays)}: Delay {delay}s")
            print("-" * 50)
            
            result = self.test_direct_requests_method(delay, num_requests)
            all_results.append(result)
            
            # Calculate composite score (success rate + quality - response time penalty)
            composite_score = (
                result['success_rate'] * 0.5 +
                result['avg_data_quality'] * 30 * 0.3 +
                result['requests_per_second'] * 10 * 0.2
            )
            
            if composite_score > best_score:
                best_score = composite_score
                best_result = result
            
            print(f"   Composite Score: {composite_score:.2f}")
            
            # Small delay between tests
            if i < len(delays):
                time.sleep(2)
        
        # Generate final report
        self._generate_comprehensive_report(all_results, best_result)
        
        # Save results
        self._save_results({
            'test_configuration': {
                'delays_tested': delays,
                'requests_per_test': num_requests,
                'total_requests': len(delays) * num_requests,
                'test_timestamp': datetime.now().isoformat()
            },
            'all_results': all_results,
            'best_configuration': best_result,
            'optimizer_version': '2.0.0'
        })
        
        return {
            'all_results': all_results,
            'best_configuration': best_result,
            'summary': self._create_summary(all_results, best_result)
        }
    
    def _generate_comprehensive_report(self, all_results: List[Dict], best_result: Dict):
        """
        Generate and display comprehensive test report
        """
        print("\n" + "="*70)
        print("📈 COMPREHENSIVE TEST RESULTS")
        print("="*70)
        
        for result in all_results:
            print(f"Delay {result['delay']:>4}s: {result['success_rate']:>6.1f}% success | "
                  f"{result['requests_per_second']:>5.2f} RPS | "
                  f"Quality: {result['avg_data_quality']:>4.2f} | "
                  f"Avg Time: {result['avg_response_time']*1000:>6.0f}ms")
        
        print("\n" + "🏆 OPTIMAL CONFIGURATION")
        print("-" * 50)
        print(f"Best Delay: {best_result['delay']}s")
        print(f"Success Rate: {best_result['success_rate']:.1f}%")
        print(f"Requests/Second: {best_result['requests_per_second']:.2f}")
        print(f"Data Quality: {best_result['avg_data_quality']:.2f}")
        print(f"Average Response Time: {best_result['avg_response_time']*1000:.0f}ms")
        
        if best_result['error_types']:
            print("\n🔍 Error Analysis:")
            for error, count in best_result['error_types'].items():
                print(f"   {error}: {count} occurrences")
        
        print("\n" + "="*70)
        print("✅ PRODUCTION RECOMMENDATIONS")
        print("="*70)
        print(f"• Use {best_result['delay']}s delay between requests")
        print(f"• Expected success rate: {best_result['success_rate']:.1f}%")
        print(f"• Recommended batch size: {int(3600 / (best_result['delay'] + best_result['avg_response_time']))} requests/hour")
        print("• User agent rotation: ✅ Active")
        print("• Dynamic headers: ✅ Active")
        print("• Session persistence: ✅ Active")
        print("="*70)
    
    def _create_summary(self, all_results: List[Dict], best_result: Dict) -> Dict:
        """
        Create a summary of test results
        """
        return {
            'total_tests': len(all_results),
            'optimal_delay': best_result['delay'],
            'best_success_rate': best_result['success_rate'],
            'best_rps': best_result['requests_per_second'],
            'best_quality': best_result['avg_data_quality'],
            'recommendation': f"Use {best_result['delay']}s delay for optimal balance of speed and reliability"
        }
    
    def _save_results(self, results: Dict):
        """
        Save test results to JSON file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"yahoo_finance_api_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to {filename}")
            print(f"\n💾 Results saved to: {filename}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")

def main():
    """
    Main execution function
    """
    try:
        optimizer = EnhancedYahooAPIOptimizer()
        results = optimizer.run_comprehensive_test()
        
        print("\n🎉 Testing completed successfully!")
        print("Check the generated JSON file for detailed results.")
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        logger.info("Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        logger.error(f"Error during testing: {e}")

if __name__ == "__main__":
    main()