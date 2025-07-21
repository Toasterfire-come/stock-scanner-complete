import asyncio
import aiohttp
import requests
import time
import logging
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class StockData:
    """Standardized stock data structure"""
    ticker: str
    current_price: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    avg_volume: Optional[int] = None
    previous_close: Optional[float] = None
    shares_outstanding: Optional[int] = None
    source: str = "unknown"

class BaseAPIProvider(ABC):
    """Base class for stock data providers"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def get_stock_data(self, ticker: str) -> Optional[StockData]:
        """Fetch stock data for a given ticker"""
        pass
    
    @abstractmethod
    def get_rate_limit(self) -> int:
        """Return requests per minute limit"""
        pass

class AlphaVantageProvider(BaseAPIProvider):
    """Alpha Vantage API provider - Good for free tier with 5 requests/minute"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://www.alphavantage.co/query"
    
    async def get_stock_data(self, ticker: str) -> Optional[StockData]:
        if not self.api_key:
            return None
            
        try:
            # Get quote data
            quote_params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': ticker,
                'apikey': self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=quote_params) as response:
                    data = await response.json()
                    
                    if 'Global Quote' in data:
                        quote = data['Global Quote']
                        return StockData(
                            ticker=ticker,
                            current_price=float(quote.get('05. price', 0)),
                            volume=int(quote.get('06. volume', 0)),
                            previous_close=float(quote.get('08. previous close', 0)),
                            source="AlphaVantage"
                        )
        except Exception as e:
            logger.error(f"AlphaVantage error for {ticker}: {e}")
        
        return None
    
    def get_rate_limit(self) -> int:
        return 5  # 5 requests per minute for free tier

class FinnhubProvider(BaseAPIProvider):
    """Finnhub API provider - 60 requests/minute free tier"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://finnhub.io/api/v1"
    
    async def get_stock_data(self, ticker: str) -> Optional[StockData]:
        if not self.api_key:
            return None
            
        try:
            headers = {'X-Finnhub-Token': self.api_key}
            
            async with aiohttp.ClientSession() as session:
                # Get quote
                quote_url = f"{self.base_url}/quote"
                async with session.get(quote_url, params={'symbol': ticker}, headers=headers) as response:
                    quote_data = await response.json()
                
                # Get profile for additional data
                profile_url = f"{self.base_url}/stock/profile2"
                async with session.get(profile_url, params={'symbol': ticker}, headers=headers) as response:
                    profile_data = await response.json()
                
                if quote_data.get('c'):  # Current price exists
                    return StockData(
                        ticker=ticker,
                        current_price=float(quote_data['c']),
                        volume=int(quote_data.get('v', 0)),
                        previous_close=float(quote_data.get('pc', 0)),
                        market_cap=profile_data.get('marketCapitalization'),
                        shares_outstanding=profile_data.get('shareOutstanding'),
                        source="Finnhub"
                    )
        except Exception as e:
            logger.error(f"Finnhub error for {ticker}: {e}")
        
        return None
    
    def get_rate_limit(self) -> int:
        return 60  # 60 requests per minute for free tier

class IEXCloudProvider(BaseAPIProvider):
    """IEX Cloud API provider - Varies by plan"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://cloud.iexapis.com/stable"
    
    async def get_stock_data(self, ticker: str) -> Optional[StockData]:
        if not self.api_key:
            return None
            
        try:
            params = {'token': self.api_key}
            
            async with aiohttp.ClientSession() as session:
                # Get quote
                quote_url = f"{self.base_url}/stock/{ticker}/quote"
                async with session.get(quote_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return StockData(
                            ticker=ticker,
                            current_price=float(data.get('latestPrice', 0)),
                            volume=int(data.get('latestVolume', 0)),
                            market_cap=data.get('marketCap'),
                            pe_ratio=data.get('peRatio'),
                            avg_volume=data.get('avgTotalVolume'),
                            previous_close=float(data.get('previousClose', 0)),
                            source="IEXCloud"
                        )
        except Exception as e:
            logger.error(f"IEXCloud error for {ticker}: {e}")
        
        return None
    
    def get_rate_limit(self) -> int:
        return 100  # Varies by plan

class PolygonProvider(BaseAPIProvider):
    """Polygon.io API provider - 5 requests/minute free tier"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://api.polygon.io"
    
    async def get_stock_data(self, ticker: str) -> Optional[StockData]:
        if not self.api_key:
            return None
            
        try:
            params = {'apikey': self.api_key}
            
            async with aiohttp.ClientSession() as session:
                # Get snapshot
                snapshot_url = f"{self.base_url}/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}"
                async with session.get(snapshot_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        ticker_data = data.get('results', {})
                        day_data = ticker_data.get('day', {})
                        
                        return StockData(
                            ticker=ticker,
                            current_price=float(day_data.get('c', 0)),
                            volume=int(day_data.get('v', 0)),
                            previous_close=float(ticker_data.get('prevDay', {}).get('c', 0)),
                            source="Polygon"
                        )
        except Exception as e:
            logger.error(f"Polygon error for {ticker}: {e}")
        
        return None
    
    def get_rate_limit(self) -> int:
        return 5  # 5 requests per minute for free tier

class TwelveDataProvider(BaseAPIProvider):
    """Twelve Data API provider - 8 requests/minute free tier"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://api.twelvedata.com"
    
    async def get_stock_data(self, ticker: str) -> Optional[StockData]:
        if not self.api_key:
            return None
            
        try:
            params = {
                'symbol': ticker,
                'apikey': self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                # Get real-time price
                price_url = f"{self.base_url}/price"
                async with session.get(price_url, params=params) as response:
                    if response.status == 200:
                        price_data = await response.json()
                        current_price = float(price_data.get('price', 0))
                        
                        if current_price > 0:
                            return StockData(
                                ticker=ticker,
                                current_price=current_price,
                                volume=0,  # Would need separate call
                                source="TwelveData"
                            )
        except Exception as e:
            logger.error(f"TwelveData error for {ticker}: {e}")
        
        return None
    
    def get_rate_limit(self) -> int:
        return 8  # 8 requests per minute for free tier

class MultiAPIStockFetcher:
    """Fetches stock data from multiple APIs with fallback support"""
    
    def __init__(self, providers: List[BaseAPIProvider]):
        self.providers = providers
        self.rate_limiters = {provider.name: {'requests': [], 'last_reset': time.time()} 
                            for provider in providers}
    
    def _can_make_request(self, provider: BaseAPIProvider) -> bool:
        """Check if provider can make a request within rate limits"""
        current_time = time.time()
        rate_limiter = self.rate_limiters[provider.name]
        
        # Reset counter every minute
        if current_time - rate_limiter['last_reset'] >= 60:
            rate_limiter['requests'] = []
            rate_limiter['last_reset'] = current_time
        
        # Remove old requests
        minute_ago = current_time - 60
        rate_limiter['requests'] = [req for req in rate_limiter['requests'] if req > minute_ago]
        
        return len(rate_limiter['requests']) < provider.get_rate_limit()
    
    def _record_request(self, provider: BaseAPIProvider):
        """Record a request for rate limiting"""
        self.rate_limiters[provider.name]['requests'].append(time.time())
    
    async def get_stock_data(self, ticker: str, preferred_provider: Optional[str] = None) -> Optional[StockData]:
        """Get stock data with fallback to multiple providers"""
        providers = self.providers.copy()
        
        # Move preferred provider to front if specified
        if preferred_provider:
            for i, provider in enumerate(providers):
                if provider.name.lower() == preferred_provider.lower():
                    providers.insert(0, providers.pop(i))
                    break
        
        for provider in providers:
            if not self._can_make_request(provider):
                logger.debug(f"Rate limit reached for {provider.name}, skipping")
                continue
            
            try:
                self._record_request(provider)
                data = await provider.get_stock_data(ticker)
                if data:
                    logger.info(f"Successfully fetched {ticker} from {provider.name}")
                    return data
                else:
                    logger.debug(f"No data returned from {provider.name} for {ticker}")
            except Exception as e:
                logger.error(f"Error fetching {ticker} from {provider.name}: {e}")
                continue
        
        logger.warning(f"Failed to fetch data for {ticker} from all providers")
        return None
    
    async def get_multiple_stocks(self, tickers: List[str], 
                                 max_concurrent: int = 5) -> Dict[str, Optional[StockData]]:
        """Fetch multiple stocks concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_semaphore(ticker):
            async with semaphore:
                return ticker, await self.get_stock_data(ticker)
        
        tasks = [fetch_with_semaphore(ticker) for ticker in tickers]
        results = await asyncio.gather(*tasks)
        
        return dict(results)

# Factory function to create API fetcher based on environment variables
def create_multi_api_fetcher() -> MultiAPIStockFetcher:
    """Create a multi-API fetcher with all available providers"""
    providers = []
    
    # Add providers based on available API keys from environment variables
    if os.getenv('ALPHAVANTAGE_API_KEY'):
        providers.append(AlphaVantageProvider(os.getenv('ALPHAVANTAGE_API_KEY')))
        logger.info("Added AlphaVantage provider")
    
    if os.getenv('FINNHUB_API_KEY'):
        providers.append(FinnhubProvider(os.getenv('FINNHUB_API_KEY')))
        logger.info("Added Finnhub provider")
    
    if os.getenv('IEXCLOUD_API_KEY'):
        providers.append(IEXCloudProvider(os.getenv('IEXCLOUD_API_KEY')))
        logger.info("Added IEXCloud provider")
    
    if os.getenv('POLYGON_API_KEY'):
        providers.append(PolygonProvider(os.getenv('POLYGON_API_KEY')))
        logger.info("Added Polygon provider")
    
    if os.getenv('TWELVEDATA_API_KEY'):
        providers.append(TwelveDataProvider(os.getenv('TWELVEDATA_API_KEY')))
        logger.info("Added TwelveData provider")
    
    if not providers:
        logger.warning("No alternative API providers configured. Set environment variables for API keys.")
        logger.info("Available providers: ALPHAVANTAGE_API_KEY, FINNHUB_API_KEY, IEXCLOUD_API_KEY, POLYGON_API_KEY, TWELVEDATA_API_KEY")
    else:
        logger.info(f"Configured {len(providers)} alternative API providers")
    
    return MultiAPIStockFetcher(providers)

# Utility function to convert StockData to Django model format
def stock_data_to_dict(stock_data: StockData, company_name: str = "") -> Dict:
    """Convert StockData to dictionary format for Django model"""
    return {
        'company_name': company_name,
        'current_price': stock_data.current_price,
        'volume_today': stock_data.volume,
        'avg_volume': stock_data.avg_volume,
        'pe_ratio': stock_data.pe_ratio,
        'market_cap': stock_data.market_cap,
        'dvav': None,  # Calculate separately if needed
        'dvsa': None,  # Calculate separately if needed
        'note': f"Data from {stock_data.source}",
    }

# Example usage and testing functions
async def test_providers():
    """Test all configured providers with a sample ticker"""
    fetcher = create_multi_api_fetcher()
    
    if not fetcher.providers:
        print("No API providers configured for testing")
        return
    
    test_ticker = "AAPL"
    print(f"Testing providers with {test_ticker}...")
    
    for provider in fetcher.providers:
        try:
            data = await provider.get_stock_data(test_ticker)
            if data:
                print(f"✅ {provider.name}: ${data.current_price:.2f}")
            else:
                print(f"❌ {provider.name}: No data")
        except Exception as e:
            print(f"❌ {provider.name}: Error - {e}")

def get_provider_status():
    """Get the status of all available providers"""
    providers_status = {}
    
    api_keys = {
        'AlphaVantage': os.getenv('ALPHAVANTAGE_API_KEY'),
        'Finnhub': os.getenv('FINNHUB_API_KEY'),
        'IEXCloud': os.getenv('IEXCLOUD_API_KEY'),
        'Polygon': os.getenv('POLYGON_API_KEY'),
        'TwelveData': os.getenv('TWELVEDATA_API_KEY'),
    }
    
    for provider, api_key in api_keys.items():
        providers_status[provider] = {
            'configured': bool(api_key),
            'api_key_set': bool(api_key),
            'rate_limit': {
                'AlphaVantage': '5/min',
                'Finnhub': '60/min', 
                'IEXCloud': 'Varies',
                'Polygon': '5/min',
                'TwelveData': '8/min'
            }.get(provider, 'Unknown')
        }
    
    return providers_status

if __name__ == "__main__":
    # Test the providers if run directly
    asyncio.run(test_providers())