"""
Stock Data API Manager - yfinance Primary with FREE Backup APIs
Primary: Yahoo Finance (yfinance) - Unlimited and Free  
Backup: Alpha Vantage, Finnhub, Twelve Data
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
        
        # Backup API keys
        self.alpha_vantage_keys = getattr(settings, 'ALPHA_VANTAGE_KEYS', [])
        self.finnhub_keys = getattr(settings, 'FINNHUB_KEYS', [])
        self.twelve_data_key = getattr(settings, 'TWELVE_DATA_API_KEY', '')
        
        # Usage tracking
        self.current_av_index = 0
        self.current_finnhub_index = 0
        self.daily_usage = self._load_daily_usage()
        self.last_yfinance_request = 0
        
        logger.info(f"🎯 YFinance Stock Manager initialized:")
        logger.info(f"   • Yahoo Finance: ✅ Primary (unlimited)")
        logger.info(f"   • Alpha Vantage backup: {len(self.alpha_vantage_keys)} accounts")
        logger.info(f"   • Finnhub backup: {len(self.finnhub_keys)} accounts")
        logger.info(f"   • Twelve Data backup: {'✅' if self.twelve_data_key else '❌'}")
        logger.info(f"   • Rate limit: {self.yfinance_rate_limit}s delay")

    def _load_daily_usage(self) -> Dict:
        """Load daily API usage from cache"""
        today = datetime.now().strftime('%Y-%m-%d')
        return cache.get(f'api_usage_{today}', {
            'alpha_vantage': [0] * len(self.alpha_vantage_keys),
            'finnhub': [0] * len(self.finnhub_keys),
            'twelve_data': 0,
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
                    logger.info(f"✅ {symbol} from Yahoo Finance (attempt {attempt + 1})")
                    return quote
                    
            except Exception as e:
                logger.warning(f"Yahoo Finance attempt {attempt + 1} failed for {symbol}: {e}")
                if attempt < self.yfinance_retries - 1:
                    time.sleep(1)  # Brief pause before retry
        
        logger.warning(f"⚠️ Yahoo Finance failed for {symbol} after {self.yfinance_retries} attempts")
        
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
        """Try backup APIs in order of preference"""
        
        # Try Finnhub first (highest daily limit)
        if self.finnhub_keys:
            try:
                quote = self._get_finnhub_quote(symbol)
                if quote:
                    logger.info(f"✅ {symbol} from Finnhub (backup)")
                    return quote
            except Exception as e:
                logger.warning(f"Finnhub backup failed for {symbol}: {e}")
        
        # Try Alpha Vantage
        if self.alpha_vantage_keys:
            try:
                quote = self._get_alpha_vantage_quote(symbol)
                if quote:
                    logger.info(f"✅ {symbol} from Alpha Vantage (backup)")
                    return quote
            except Exception as e:
                logger.warning(f"Alpha Vantage backup failed for {symbol}: {e}")
        
        # Try Twelve Data as last resort
        if self.twelve_data_key:
            try:
                quote = self._get_twelve_data_quote(symbol)
                if quote:
                    logger.info(f"✅ {symbol} from Twelve Data (backup)")
                    return quote
            except Exception as e:
                logger.warning(f"Twelve Data backup failed for {symbol}: {e}")
        
        logger.error(f"❌ All APIs failed for {symbol}")
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

    def _get_alpha_vantage_quote(self, symbol: str) -> Optional[Dict]:
        """Get quote from Alpha Vantage (backup API)"""
        if not self.alpha_vantage_keys:
            return None
            
        # Check usage limits
        if self.daily_usage['alpha_vantage'][self.current_av_index % len(self.alpha_vantage_keys)] >= 24:
            return None
            
        api_key = self.alpha_vantage_keys[self.current_av_index % len(self.alpha_vantage_keys)]
        
        try:
            response = requests.get(
                "https://www.alphavantage.co/query",
                params={
                    'function': 'GLOBAL_QUOTE',
                    'symbol': symbol,
                    'apikey': api_key
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Update usage counter
                self.daily_usage['alpha_vantage'][self.current_av_index % len(self.alpha_vantage_keys)] += 1
                self.current_av_index += 1
                self._save_daily_usage()
                
                if 'Global Quote' in data:
                    quote = data['Global Quote']
                    return {
                        'symbol': symbol,
                        'price': float(quote['05. price']),
                        'change': float(quote['09. change']),
                        'change_percent': float(quote['10. change percent'].replace('%', '')),
                        'volume': int(quote['06. volume']),
                        'market_cap': 0,
                        'source': 'alpha_vantage',
                        'timestamp': datetime.now().isoformat(),
                        'currency': 'USD'
                    }
            return None
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {e}")
            return None

    def _get_twelve_data_quote(self, symbol: str) -> Optional[Dict]:
        """Get quote from Twelve Data (backup API)"""
        if not self.twelve_data_key or self.daily_usage['twelve_data'] >= 790:
            return None

        try:
            response = requests.get(
                "https://api.twelvedata.com/quote",
                params={
                    'symbol': symbol,
                    'apikey': self.twelve_data_key
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Update usage counter
                self.daily_usage['twelve_data'] += 1
                self._save_daily_usage()
                
                if 'close' in data:
                    return {
                        'symbol': symbol,
                        'price': float(data['close']),
                        'change': float(data.get('change', 0)),
                        'change_percent': float(data.get('percent_change', 0)),
                        'volume': int(data.get('volume', 0)),
                        'market_cap': 0,
                        'source': 'twelve_data',
                        'timestamp': datetime.now().isoformat(),
                        'currency': 'USD'
                    }
            return None
        except Exception as e:
            logger.error(f"Twelve Data error for {symbol}: {e}")
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
        """Get current API usage statistics"""
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
            },
            'alpha_vantage': {
                'accounts': len(self.alpha_vantage_keys),
                'usage': self.daily_usage['alpha_vantage'] if self.alpha_vantage_keys else [],
                'limits': [25] * len(self.alpha_vantage_keys),
                'total_available': 25 * len(self.alpha_vantage_keys),
                'status': 'backup'
            },
            'twelve_data': {
                'usage': self.daily_usage['twelve_data'],
                'limit': 800,
                'available': 800 - self.daily_usage['twelve_data'],
                'status': 'backup'
            }
        }

    def test_connection(self) -> Dict:
        """Test connection to primary and backup APIs"""
        results = {
            'yahoo_finance': False,
            'finnhub': False,
            'alpha_vantage': False,
            'twelve_data': False
        }
        
        # Test Yahoo Finance
        try:
            test_quote = self._get_yfinance_quote('AAPL')
            results['yahoo_finance'] = test_quote is not None
        except:
            pass
        
        # Test backup APIs
        if self.finnhub_keys:
            try:
                test_quote = self._get_finnhub_quote('AAPL')
                results['finnhub'] = test_quote is not None
            except:
                pass
        
        if self.alpha_vantage_keys:
            try:
                test_quote = self._get_alpha_vantage_quote('AAPL')
                results['alpha_vantage'] = test_quote is not None
            except:
                pass
        
        if self.twelve_data_key:
            try:
                test_quote = self._get_twelve_data_quote('AAPL')
                results['twelve_data'] = test_quote is not None
            except:
                pass
        
        return results

# Global instance
stock_manager = YFinanceStockManager()