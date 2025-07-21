"""
yfinance-only Stock Data Configuration
Optimized for IONOS hosting with rate limiting and error handling
"""

import os
import time
import yfinance as yf
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logger = logging.getLogger(__name__)

class YFinanceConfig:
    """Configuration for yfinance API with rate limiting and optimization"""
    
    def __init__(self):
        # Rate limiting settings
        self.rate_limit = float(os.getenv('STOCK_API_RATE_LIMIT', '1.0'))  # seconds between requests
        self.max_retries = int(os.getenv('YFINANCE_MAX_RETRIES', '3'))
        self.retry_delay = float(os.getenv('YFINANCE_RETRY_DELAY', '2.0'))
        
        # Batch processing settings
        self.batch_size = int(os.getenv('YFINANCE_BATCH_SIZE', '10'))
        self.max_concurrent_requests = int(os.getenv('YFINANCE_MAX_CONCURRENT', '5'))
        
        # Timeout settings
        self.request_timeout = int(os.getenv('YFINANCE_TIMEOUT', '30'))
        
        # User agent rotation to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        # Setup session with retry strategy
        self.session = self._create_session()
        
        # Last request time for rate limiting
        self.last_request_time = 0
        
        # Cache settings
        self.cache_duration = int(os.getenv('YFINANCE_CACHE_DURATION', '300'))  # 5 minutes
        self.cache = {}

    def _create_session(self) -> requests.Session:
        """Create optimized requests session with retry strategy"""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session

    def _wait_for_rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

    def _get_user_agent(self) -> str:
        """Get rotating user agent"""
        import random
        return random.choice(self.user_agents)

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key]['timestamp']
        return (datetime.now() - cached_time).seconds < self.cache_duration

    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Get data from cache if valid"""
        if self._is_cache_valid(cache_key):
            logger.debug(f"Cache hit for {cache_key}")
            return self.cache[cache_key]['data']
        return None

    def _store_in_cache(self, cache_key: str, data: Dict):
        """Store data in cache with timestamp"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now()
        }
        logger.debug(f"Cached data for {cache_key}")

    def get_stock_data(self, ticker: str) -> Optional[Dict]:
        """
        Get comprehensive stock data for a single ticker
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dict with stock data or None if failed
        """
        cache_key = f"stock_data_{ticker.upper()}"
        
        # Check cache first
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # Apply rate limiting
        self._wait_for_rate_limit()
        
        try:
            # Create ticker object with custom session
            stock = yf.Ticker(ticker, session=self.session)
            
            # Set user agent
            stock._base_url = stock._base_url
            stock.session.headers.update({'User-Agent': self._get_user_agent()})
            
            # Get basic info
            info = stock.info
            history = stock.history(period="5d")  # Last 5 days for calculations
            
            if history.empty or not info:
                logger.warning(f"No data found for ticker {ticker}")
                return None
            
            # Extract current data
            current_price = history['Close'].iloc[-1] if not history.empty else None
            previous_close = history['Close'].iloc[-2] if len(history) > 1 else current_price
            
            # Calculate changes
            price_change = current_price - previous_close if current_price and previous_close else 0
            price_change_percent = (price_change / previous_close * 100) if previous_close else 0
            
            # Get volume data
            current_volume = history['Volume'].iloc[-1] if not history.empty else 0
            avg_volume = history['Volume'].mean() if not history.empty else 0
            
            # Calculate DVAV and DVSA (simplified)
            dvav = (current_volume / avg_volume * 100) if avg_volume > 0 else 0
            dvsa = dvav  # Simplified - you can implement more complex calculation
            
            # Compile stock data
            stock_data = {
                'ticker': ticker.upper(),
                'company_name': info.get('longName', info.get('shortName', ticker.upper())),
                'current_price': float(current_price) if current_price else 0,
                'previous_close': float(previous_close) if previous_close else 0,
                'price_change_today': float(price_change),
                'price_change_percent': round(price_change_percent, 2),
                'volume_today': int(current_volume),
                'average_volume': int(avg_volume),
                'dvav': round(dvav, 2),
                'dvsa': round(dvsa, 2),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'country': info.get('country', 'Unknown'),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'Unknown'),
                'last_update': datetime.now(),
                'data_source': 'yfinance',
                'note': self._generate_note(ticker, price_change_percent, dvav)
            }
            
            # Store in cache
            self._store_in_cache(cache_key, stock_data)
            
            logger.info(f"Successfully fetched data for {ticker}")
            return stock_data
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {str(e)}")
            return None

    def get_multiple_stocks(self, tickers: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Get stock data for multiple tickers with batching
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            Dict mapping ticker to stock data (or None if failed)
        """
        results = {}
        
        # Process in batches
        for i in range(0, len(tickers), self.batch_size):
            batch = tickers[i:i + self.batch_size]
            logger.info(f"Processing batch {i//self.batch_size + 1}: {batch}")
            
            for ticker in batch:
                results[ticker] = self.get_stock_data(ticker)
                
            # Pause between batches
            if i + self.batch_size < len(tickers):
                time.sleep(self.rate_limit * 2)  # Extra pause between batches
        
        return results

    def validate_ticker(self, ticker: str) -> bool:
        """
        Validate if a ticker exists and has data
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            True if ticker is valid, False otherwise
        """
        try:
            stock = yf.Ticker(ticker, session=self.session)
            info = stock.info
            
            # Check if we got meaningful data
            if not info or 'regularMarketPrice' not in info:
                return False
                
            return True
            
        except Exception as e:
            logger.warning(f"Ticker validation failed for {ticker}: {str(e)}")
            return False

    def get_market_summary(self) -> Dict:
        """
        Get market summary data
        
        Returns:
            Dict with market indices data
        """
        cache_key = "market_summary"
        
        # Check cache first
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        indices = ['^GSPC', '^DJI', '^IXIC', '^RUT']  # S&P 500, Dow, NASDAQ, Russell 2000
        index_names = ['S&P 500', 'Dow Jones', 'NASDAQ', 'Russell 2000']
        
        market_data = {}
        
        for ticker, name in zip(indices, index_names):
            data = self.get_stock_data(ticker)
            if data:
                market_data[name] = {
                    'ticker': ticker,
                    'price': data['current_price'],
                    'change': data['price_change_today'],
                    'change_percent': data['price_change_percent']
                }
        
        # Store in cache
        self._store_in_cache(cache_key, market_data)
        
        return market_data

    def _generate_note(self, ticker: str, price_change_percent: float, dvav: float) -> str:
        """Generate descriptive note for stock alert"""
        notes = []
        
        if abs(price_change_percent) >= 10:
            direction = "up" if price_change_percent > 0 else "down"
            notes.append(f"Large move {direction} ({price_change_percent:+.1f}%)")
        
        if dvav >= 150:
            notes.append(f"High volume ({dvav:.0f}% of avg)")
        elif dvav >= 50:
            notes.append(f"Above avg volume ({dvav:.0f}%)")
        
        if abs(price_change_percent) >= 5:
            notes.append("Price alert")
        
        return " | ".join(notes) if notes else f"{ticker} update"

    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        logger.info("Cache cleared")

    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        total_entries = len(self.cache)
        valid_entries = sum(1 for key in self.cache if self._is_cache_valid(key))
        
        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'hit_rate': f"{(valid_entries/total_entries*100):.1f}%" if total_entries > 0 else "0%",
            'cache_duration': self.cache_duration
        }

# Global instance
yfinance_config = YFinanceConfig()

def get_stock_data(ticker: str) -> Optional[Dict]:
    """Convenience function to get stock data"""
    return yfinance_config.get_stock_data(ticker)

def get_multiple_stocks(tickers: List[str]) -> Dict[str, Optional[Dict]]:
    """Convenience function to get multiple stocks"""
    return yfinance_config.get_multiple_stocks(tickers)

def validate_ticker(ticker: str) -> bool:
    """Convenience function to validate ticker"""
    return yfinance_config.validate_ticker(ticker)

def get_market_summary() -> Dict:
    """Convenience function to get market summary"""
    return yfinance_config.get_market_summary()

# Configuration validation
def validate_yfinance_config() -> List[str]:
    """Validate yfinance configuration"""
    errors = []
    
    try:
        import yfinance
    except ImportError:
        errors.append("yfinance not installed. Run: pip install yfinance")
    
    rate_limit = float(os.getenv('STOCK_API_RATE_LIMIT', '1.0'))
    if rate_limit < 0.5:
        errors.append("Rate limit too low - minimum 0.5 seconds recommended")
    
    return errors

# Test function
def test_yfinance_connection() -> Tuple[bool, str]:
    """Test yfinance connection with a sample ticker"""
    try:
        test_ticker = "AAPL"
        data = get_stock_data(test_ticker)
        
        if data and data.get('current_price', 0) > 0:
            return True, f"yfinance connection successful - {test_ticker}: ${data['current_price']}"
        else:
            return False, f"Failed to get valid data for {test_ticker}"
            
    except Exception as e:
        return False, f"yfinance connection failed: {str(e)}"

# Rate limiting decorator
def rate_limited(func):
    """Decorator to apply rate limiting to functions"""
    def wrapper(*args, **kwargs):
        yfinance_config._wait_for_rate_limit()
        return func(*args, **kwargs)
    return wrapper