#!/usr/bin/env python3
"""
Production-Ready Yahoo Finance Direct API Optimizer
Implements direct Yahoo Finance API calls with advanced rate limit optimization

Features:
- Direct Yahoo Finance API integration
- User Agent Rotation
- Optimized Headers
- Adaptive timing based on response patterns
- Comprehensive error handling and logging
- Production-ready architecture

Author: Stock Scanner Project
Version: 1.0.0
"""

import time
import requests
import random
import json
import statistics
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('yahoo_api_optimizer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionYahooAPIOptimizer:
    """
    Production-ready Yahoo Finance API optimizer with advanced features
    """
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """
        Initialize the optimizer with production settings
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Test symbols for optimization
        self.test_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'AMD', 'INTC', 'ORCL', 'CRM', 'ADBE', 'PYPL', 'UBER', 'SHOP',
            'ZOOM', 'ROKU', 'SQ', 'HOOD', 'SNAP', 'PINS', 'COIN', 'RBLX'
        ]
        
        # User agent pool for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1'
        ]
        
        # Results storage
        self.results = {}
        self.session = self._create_optimized_session()
        
        logger.info("Production Yahoo API Optimizer initialized")
    
    def _create_optimized_session(self) -> requests.Session:
        """
        Create an optimized requests session with retry strategy
        
        Returns:
            Configured requests session
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set base headers
        session.headers.update(self._get_optimized_headers())
        
        return session
    
    def _get_optimized_headers(self) -> Dict[str, str]:
        """
        Generate optimized headers for Yahoo Finance API
        
        Returns:
            Dictionary of optimized headers
        """
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.8', 'en-CA,en;q=0.7']),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': random.choice(['document', 'empty']),
            'Sec-Fetch-Mode': random.choice(['navigate', 'cors']),
            'Sec-Fetch-Site': 'none',
            'Cache-Control': random.choice(['no-cache', 'max-age=0']),
            'Pragma': 'no-cache',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
    
    def _rotate_user_agent(self):
        """Rotate user agent for the session"""
        self.session.headers.update({'User-Agent': random.choice(self.user_agents)})
    
    def fetch_stock_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch stock data for a single symbol using direct Yahoo Finance API
        
        Args:
            symbol: Stock symbol to fetch
            
        Returns:
            Dictionary containing response data and metadata
        """
        start_time = time.time()
        
        try:
            # Rotate headers for this request
            self._rotate_user_agent()
            self.session.headers.update(self._get_optimized_headers())
            
            # Make API request
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            response = self.session.get(url, timeout=self.timeout)
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'chart' in data and data['chart']['result']:
                        logger.debug(f"Successfully fetched data for {symbol}")
                        return {
                            'symbol': symbol,
                            'success': True,
                            'data': data,
                            'response_time': response_time,
                            'status_code': response.status_code
                        }
                    else:
                        logger.warning(f"Invalid data structure for {symbol}")
                        return {
                            'symbol': symbol,
                            'success': False,
                            'error': 'invalid_data_structure',
                            'response_time': response_time,
                            'status_code': response.status_code
                        }
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error for {symbol}: {e}")
                    return {
                        'symbol': symbol,
                        'success': False,
                        'error': 'json_decode_error',
                        'response_time': response_time,
                        'status_code': response.status_code
                    }
            else:
                logger.warning(f"HTTP {response.status_code} for {symbol}")
                return {
                    'symbol': symbol,
                    'success': False,
                    'error': f'http_{response.status_code}',
                    'response_time': response_time,
                    'status_code': response.status_code
                }
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout error for {symbol}")
            return {
                'symbol': symbol,
                'success': False,
                'error': 'timeout',
                'response_time': time.time() - start_time
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {symbol}: {e}")
            return {
                'symbol': symbol,
                'success': False,
                'error': str(e),
                'response_time': time.time() - start_time
            }
    
    def test_rate_limits(self, delays: List[float] = None, requests_per_delay: int = 30) -> Dict[str, Any]:
        """
        Test different delay intervals to find optimal rate limiting
        
        Args:
            delays: List of delays to test in seconds
            requests_per_delay: Number of requests to make per delay test
            
        Returns:
            Dictionary containing test results and recommendations
        """
        if delays is None:
            delays = [0.5, 1.0, 1.5, 2.0]
        
        logger.info(f"Testing rate limits with delays: {delays}")
        
        all_results = {}
        best_performance = {'delay': 0, 'success_rate': 0, 'rps': 0}
        
        for delay in delays:
            logger.info(f"Testing delay: {delay}s with {requests_per_delay} requests")
            
            delay_results = self._test_single_delay(delay, requests_per_delay)
            all_results[f"{delay}s"] = delay_results
            
            # Track best performance
            if delay_results['success_rate'] > best_performance['success_rate']:
                best_performance = {
                    'delay': delay,
                    'success_rate': delay_results['success_rate'],
                    'rps': delay_results['requests_per_second']
                }
            
            # Brief pause between tests
            if delay != delays[-1]:
                time.sleep(2.0)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(all_results, best_performance)
        
        return {
            'test_results': all_results,
            'best_performance': best_performance,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
    
    def _test_single_delay(self, delay: float, num_requests: int) -> Dict[str, Any]:
        """
        Test a single delay configuration
        
        Args:
            delay: Delay between requests in seconds
            num_requests: Number of requests to make
            
        Returns:
            Dictionary containing test results
        """
        start_time = time.time()
        successes = 0
        failures = 0
        response_times = []
        error_counts = {}
        
        for i in range(num_requests):
            symbol = random.choice(self.test_symbols)
            result = self.fetch_stock_data(symbol)
            
            if result['success']:
                successes += 1
                response_times.append(result['response_time'])
            else:
                failures += 1
                error_type = result.get('error', 'unknown')
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
            # Progress logging
            if (i + 1) % 10 == 0:
                success_rate = (successes / (i + 1)) * 100
                logger.info(f"   Progress: {i+1}/{num_requests} | Success Rate: {success_rate:.1f}%")
            
            # Apply delay
            if i < num_requests - 1:
                time.sleep(delay)
        
        total_time = time.time() - start_time
        success_rate = (successes / num_requests) * 100 if num_requests > 0 else 0
        avg_response_time = statistics.mean(response_times) if response_times else 0
        rps = num_requests / total_time if total_time > 0 else 0
        
        return {
            'delay': delay,
            'success_rate': success_rate,
            'total_requests': num_requests,
            'successes': successes,
            'failures': failures,
            'avg_response_time': avg_response_time,
            'total_time': total_time,
            'requests_per_second': rps,
            'error_counts': error_counts
        }
    
    def _generate_recommendations(self, all_results: Dict, best_performance: Dict) -> Dict[str, str]:
        """
        Generate recommendations based on test results
        
        Args:
            all_results: All test results
            best_performance: Best performing configuration
            
        Returns:
            Dictionary containing recommendations
        """
        recommendations = {}
        
        # Basic recommendation
        if best_performance['success_rate'] >= 95:
            recommendations['primary'] = f"Excellent! Use {best_performance['delay']}s delay for {best_performance['success_rate']:.1f}% success rate"
        elif best_performance['success_rate'] >= 85:
            recommendations['primary'] = f"Good performance with {best_performance['delay']}s delay ({best_performance['success_rate']:.1f}% success)"
        else:
            recommendations['primary'] = f"Consider increasing delay beyond {best_performance['delay']}s (current: {best_performance['success_rate']:.1f}% success)"
        
        # Performance analysis
        if best_performance['rps'] > 1.0:
            recommendations['performance'] = "High throughput achieved - suitable for real-time applications"
        elif best_performance['rps'] > 0.5:
            recommendations['performance'] = "Moderate throughput - good for regular data collection"
        else:
            recommendations['performance'] = "Low throughput - suitable for background processing only"
        
        # Error analysis
        error_patterns = []
        for delay_key, results in all_results.items():
            if results['failures'] > 0:
                main_errors = [error for error, count in results['error_counts'].items() if count > 2]
                if main_errors:
                    error_patterns.extend(main_errors)
        
        if 'http_429' in error_patterns:
            recommendations['rate_limiting'] = "Rate limiting detected - consider increasing delays further"
        elif 'timeout' in error_patterns:
            recommendations['timeout'] = "Timeout issues detected - consider increasing timeout duration"
        
        return recommendations
    
    def save_results(self, results: Dict, filename: str = None):
        """
        Save test results to JSON file
        
        Args:
            results: Results dictionary to save
            filename: Optional filename (defaults to timestamped file)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"yahoo_api_optimization_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Results saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    
    def print_summary(self, results: Dict):
        """
        Print a formatted summary of test results
        
        Args:
            results: Results dictionary from test_rate_limits
        """
        print("\n" + "="*70)
        print("🚀 YAHOO FINANCE API OPTIMIZATION SUMMARY")
        print("="*70)
        
        best = results['best_performance']
        print(f"✅ Best Configuration:")
        print(f"   Delay: {best['delay']}s")
        print(f"   Success Rate: {best['success_rate']:.1f}%")
        print(f"   Requests/Second: {best['rps']:.2f}")
        
        print(f"\n📊 All Test Results:")
        for delay_key, delay_results in results['test_results'].items():
            print(f"   {delay_key}: {delay_results['success_rate']:.1f}% success, {delay_results['requests_per_second']:.2f} RPS")
        
        print(f"\n💡 Recommendations:")
        for rec_type, recommendation in results['recommendations'].items():
            print(f"   • {recommendation}")
        
        print("="*70)

def main():
    """Main function for testing the optimizer"""
    print("🚀 Starting Production Yahoo Finance API Optimizer")
    print("=" * 60)
    
    # Initialize optimizer
    optimizer = ProductionYahooAPIOptimizer()
    
    # Test rate limits
    results = optimizer.test_rate_limits(
        delays=[0.5, 1.0, 1.5, 2.0],
        requests_per_delay=20  # Reduced for faster testing
    )
    
    # Print summary
    optimizer.print_summary(results)
    
    # Save results
    optimizer.save_results(results)
    
    print("\n✅ Optimization complete! Check the generated JSON file for detailed results.")

if __name__ == "__main__":
    main()