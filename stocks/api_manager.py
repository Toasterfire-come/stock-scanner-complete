"""
Stock Data API Manager - Simplified Two-API System
Primary: Yahoo Finance (yfinance) - Unlimited and Free  
Backup: Finnhub (2 accounts × 1000 calls/day)
"""

import os
import time
import logging
import requests
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

class YFinanceStockManager:
    """Primary stock data manager using yfinance with smart fallback"""
    
    def __init__(self):
        # Load configuration from Django settings
        self.yfinance_rate_limit = getattr(settings, 'YFINANCE_RATE_LIMIT', 1.0)
        self.yfinance_timeout = getattr(settings, 'YFINANCE_TIMEOUT', 15)
        self.yfinance_retries = getattr(settings, 'YFINANCE_RETRIES', 3)
        
        # Backup API keys - Simplified
        self.finnhub_keys = getattr(settings, 'FINNHUB_KEYS', [])
        
        # Usage tracking - Simplified
        self.current_finnhub_index = 0
        self.daily_usage = self._load_daily_usage()
        self.last_yfinance_request = 0
        
        logger.info(f"YFinance Stock Manager initialized:")
        logger.info(f"   • Yahoo Finance: Primary (unlimited)")
        logger.info(f"   • Finnhub backup: {len(self.finnhub_keys)} accounts")
        logger.info(f"   • Rate limit: {self.yfinance_rate_limit}s delay")

    def _load_daily_usage(self) -> Dict:
        """Load daily API usage from cache"""
        today = datetime.now().strftime('%Y-%m-%d')
        return cache.get(f'api_usage_{today}', {
            'finnhub': [0] * len(self.finnhub_keys),
            'yfinance_requests': 0
        })

    def _save_daily_usage(self):
        """Save daily API usage to cache"""
        today = datetime.now().strftime('%Y-%m-%d')
        cache.set(f'api_usage_{today}', self.daily_usage, 86400)  # 24 hours

    def _rate_limit_yfinance(self):
        """Apply rate limiting for yfinance requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_yfinance_request
        
        if time_since_last < self.yfinance_rate_limit:
            sleep_time = self.yfinance_rate_limit - time_since_last
            time.sleep(sleep_time)
        
        self.last_yfinance_request = time.time()

    def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """Get stock quote - yfinance primary with smart fallback"""
        symbol = symbol.upper()
        
        # Primary: Yahoo Finance (yfinance) - try multiple times with retries
        for attempt in range(self.yfinance_retries):
            try:
                self._rate_limit_yfinance()
                quote = self._get_yfinance_quote(symbol)
                if quote:
                    self.daily_usage['yfinance_requests'] += 1
                    self._save_daily_usage()
                    logger.info(f"SUCCESS: {symbol} from Yahoo Finance (attempt {attempt + 1})")
                    return quote
                    
            except Exception as e:
                logger.warning(f"Yahoo Finance attempt {attempt + 1} failed for {symbol}: {e}")
                if attempt < self.yfinance_retries - 1:
                    time.sleep(1)  # Brief pause before retry
        
        logger.warning(f"WARNING: Yahoo Finance failed for {symbol} after {self.yfinance_retries} attempts")
        
        # Fallback to backup APIs
        return self._get_backup_quote(symbol)

    def _get_yfinance_quote(self, symbol: str) -> Optional[Dict]:
        """Get quote from Yahoo Finance using yfinance library"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get both info and historical data
            hist = ticker.history(period="2d")
            info = ticker.info
            
            if hist.empty or len(hist) < 1:
                return None
                
            current_price = hist['Close'].iloc[-1]
            
            # Calculate price change
            if len(hist) > 1:
                prev_close = hist['Close'].iloc[-2]
                price_change = current_price - prev_close
                price_change_percent = (price_change / prev_close * 100) if prev_close != 0 else 0
            else:
                price_change = 0
                price_change_percent = 0
            
            # Get additional info from ticker.info if available
            market_cap = info.get('marketCap', 0) if info else 0
            volume = int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0
            
            return {
                'symbol': symbol,
                'price': float(current_price),
                'change': float(price_change),
                'change_percent': float(price_change_percent),
                'volume': volume,
                'market_cap': market_cap,
                'source': 'yahoo_finance',
                'timestamp': datetime.now().isoformat(),
                'currency': info.get('currency', 'USD') if info else 'USD'
            }
            
        except Exception as e:
            logger.error(f"YFinance error for {symbol}: {e}")
            return None

    def _get_backup_quote(self, symbol: str) -> Optional[Dict]:
        """Try backup API - Simplified to Finnhub only"""
        
        # Try Finnhub backup
        if self.finnhub_keys:
            try:
                quote = self._get_finnhub_quote(symbol)
                if quote:
                    logger.info(f"SUCCESS: {symbol} from Finnhub (backup)")
                    return quote
            except Exception as e:
                logger.warning(f"Finnhub backup failed for {symbol}: {e}")
        else:
            logger.warning(f"No Finnhub API keys configured")
        
        logger.error(f"ERROR: All APIs failed for {symbol}")
        return None

    def _get_finnhub_quote(self, symbol: str) -> Optional[Dict]:
        """Get quote from Finnhub (backup API)"""
        if not self.finnhub_keys:
            return None
            
        # Check usage limits
        if self.daily_usage['finnhub'][self.current_finnhub_index % len(self.finnhub_keys)] >= 990:
            return None
            
        api_key = self.finnhub_keys[self.current_finnhub_index % len(self.finnhub_keys)]
        
        try:
            response = requests.get(
                f"https://finnhub.io/api/v1/quote",
                params={'symbol': symbol, 'token': api_key},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Update usage counter
                self.daily_usage['finnhub'][self.current_finnhub_index % len(self.finnhub_keys)] += 1
                self.current_finnhub_index += 1
                self._save_daily_usage()
                
                if 'c' in data and data['c'] is not None:
                    return {
                        'symbol': symbol,
                        'price': float(data['c']),
                        'change': float(data.get('d', 0)),
                        'change_percent': float(data.get('dp', 0)),
                        'volume': 0,
                        'market_cap': 0,
                        'source': 'finnhub',
                        'timestamp': datetime.now().isoformat(),
                        'currency': 'USD'
                    }
            return None
        except Exception as e:
            logger.error(f"Finnhub error for {symbol}: {e}")
            return None



    def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get quotes for multiple symbols efficiently"""
        results = {}
        
        for i, symbol in enumerate(symbols):
            quote = self.get_stock_quote(symbol)
            if quote:
                results[symbol] = quote
            
            # Progress logging for large batches
            if (i + 1) % 10 == 0:
                success_rate = (len(results) / (i + 1)) * 100
                logger.info(f"Batch progress: {i + 1}/{len(symbols)} | Success: {success_rate:.1f}%")
        
        return results

    def get_usage_stats(self) -> Dict:
        """Get current API usage statistics - Simplified"""
        return {
            'yahoo_finance': {
                'status': 'primary',
                'requests_today': self.daily_usage['yfinance_requests'],
                'rate_limit': f"{self.yfinance_rate_limit}s",
                'retries': self.yfinance_retries,
                'description': 'Unlimited, primary data source'
            },
            'finnhub': {
                'accounts': len(self.finnhub_keys),
                'usage': self.daily_usage['finnhub'] if self.finnhub_keys else [],
                'limits': [1000] * len(self.finnhub_keys),
                'total_available': 1000 * len(self.finnhub_keys),
                'status': 'backup'
            }
        }

    def test_connection(self) -> Dict:
        """Test connection to primary and backup APIs - Simplified"""
        results = {
            'yahoo_finance': False,
            'finnhub': False
        }
        
        # Test Yahoo Finance
        try:
            test_quote = self._get_yfinance_quote('AAPL')
            results['yahoo_finance'] = test_quote is not None
        except:
            pass
        
        # Test Finnhub backup
        if self.finnhub_keys:
            try:
                test_quote = self._get_finnhub_quote('AAPL')
                results['finnhub'] = test_quote is not None
            except:
                pass
        
        return results

# Global instance
stock_manager = YFinanceStockManager()