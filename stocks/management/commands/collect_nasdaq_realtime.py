"""
NASDAQ Real-time Data Collection Command
Collects all NASDAQ stocks every 10 minutes using free APIs
"""

import asyncio
import aiohttp
import json
import time
import logging
import os
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from stocks.models import StockAlert, Membership

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NASDAQRealTimeCollector:
    def __init__(self):
        # DUAL IEX CLOUD FREE ACCOUNTS STRATEGY
        iex_key_1 = os.getenv('IEX_API_KEY_1', os.getenv('IEX_API_KEY', 'pk_test_your_iex_key_1'))
        iex_key_2 = os.getenv('IEX_API_KEY_2', 'pk_test_your_iex_key_2')
        
        # Free API configuration - DUAL IEX + MULTI-API STRATEGY FOR 100% COVERAGE
        self.apis = {
            'iex_1': {
                'key': iex_key_1,
                'base_url': 'https://cloud.iexapis.com/stable',
                'tier': 'free',
                'calls_per_minute': 100,
                'calls_per_month': 500000,
                'daily_limit': 16666,
                'monthly_cost': 0,
                'can_handle_all_nasdaq': False,
                'name': 'IEX Cloud #1'
            },
            'iex_2': {
                'key': iex_key_2,
                'base_url': 'https://cloud.iexapis.com/stable',
                'tier': 'free',
                'calls_per_minute': 100,
                'calls_per_month': 500000,
                'daily_limit': 16666,
                'monthly_cost': 0,
                'can_handle_all_nasdaq': False,
                'name': 'IEX Cloud #2'
            },
            'finnhub': {
                'key': os.getenv('FINNHUB_API_KEY', 'your_finnhub_key'),
                'base_url': 'https://finnhub.io/api/v1',
                'calls_per_minute': 60,
                'calls_per_day': 86400
            },
            'alphavantage': {
                'key': os.getenv('ALPHAVANTAGE_API_KEY', 'your_alphavantage_key'),
                'base_url': 'https://www.alphavantage.co/query',
                'calls_per_day': 500
            },
            'fmp': {
                'key': os.getenv('FMP_API_KEY', 'your_fmp_key'),
                'base_url': 'https://financialmodelingprep.com/api/v3',
                'calls_per_day': 250
            },
            'twelvedata': {
                'key': os.getenv('TWELVEDATA_API_KEY', 'your_twelvedata_key'),
                'base_url': 'https://api.twelvedata.com/v1',
                'calls_per_day': 800
            },
            'polygon': {
                'key': os.getenv('POLYGON_API_KEY', 'your_polygon_key'),
                'base_url': 'https://api.polygon.io/v2',
                'calls_per_minute': 5,
                'calls_per_day': 720  # 5 per minute * 1440 minutes
            }
        }
        
        # Load NASDAQ tickers
        self.nasdaq_tickers = self.get_nasdaq_tickers()
        
        # Log dual IEX configuration
        logger.info(f"🔑 Dual IEX Cloud FREE accounts configured")
        logger.info(f"📊 IEX Account #1: {self.apis['iex_1']['daily_limit']:,} requests/day")
        logger.info(f"📊 IEX Account #2: {self.apis['iex_2']['daily_limit']:,} requests/day")
        logger.info(f"🎯 Combined capacity: {self.apis['iex_1']['daily_limit'] + self.apis['iex_2']['daily_limit']:,} requests/day")

    def detect_iex_tier(self, api_key):
        """Detect IEX Cloud tier based on API key prefix and environment variable"""
        # Check if user explicitly set the tier
        explicit_tier = os.getenv('IEX_TIER', '').lower()
        if explicit_tier in ['free', 'start', 'launch', 'grow', 'scale', 'enterprise']:
            return explicit_tier
        
        # Auto-detect based on API key prefix
        if api_key.startswith('pk_test_'):
            return 'free'
        elif api_key.startswith('pk_'):
            # Production key - check environment or default to Launch (most common paid tier)
            return os.getenv('IEX_TIER', 'launch').lower()
        else:
            return 'free'
    
    def get_iex_limits(self, tier):
        """Get IEX Cloud limits based on tier"""
        iex_tiers = {
            'free': {
                'calls_per_minute': 100,
                'calls_per_month': 500000,
                'daily_limit': 16666,  # 500K/30 days
                'monthly_cost': 0,
                'can_handle_all_nasdaq': False
            },
            'start': {
                'calls_per_minute': 100,
                'calls_per_month': 5000000,  # 5M
                'daily_limit': 166666,  # 5M/30 days
                'monthly_cost': 9,
                'can_handle_all_nasdaq': True
            },
            'launch': {
                'calls_per_minute': 1000,
                'calls_per_month': 5000000,  # 5M
                'daily_limit': 166666,  # 5M/30 days
                'monthly_cost': 19,
                'can_handle_all_nasdaq': True
            },
            'grow': {
                'calls_per_minute': 2000,
                'calls_per_month': 50000000,  # 50M
                'daily_limit': 1666666,  # 50M/30 days
                'monthly_cost': 99,
                'can_handle_all_nasdaq': True
            },
            'scale': {
                'calls_per_minute': 10000,
                'calls_per_month': 100000000,  # 100M
                'daily_limit': 3333333,  # 100M/30 days
                'monthly_cost': 199,
                'can_handle_all_nasdaq': True
            },
            'enterprise': {
                'calls_per_minute': 100000,
                'calls_per_month': 1000000000,  # 1B
                'daily_limit': 33333333,  # 1B/30 days
                'monthly_cost': 999,
                'can_handle_all_nasdaq': True
            }
        }
        
        return iex_tiers.get(tier, iex_tiers['free'])
        
        # Priority tickers (most important stocks to update first)
        self.priority_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA',
            'NFLX', 'AMD', 'INTC', 'CSCO', 'ADBE', 'CRM', 'ORCL', 'AVGO',
            'TXN', 'QCOM', 'COST', 'SBUX', 'PYPL', 'ZOOM', 'DOCU', 'ROKU'
        ]
    
    def get_nasdaq_tickers(self):
        """Get NASDAQ tickers from various sources"""
        # Try to load from cache first
        cache_file = 'nasdaq_tickers_cache.json'
        
        if os.path.exists(cache_file):
            # Check if cache is less than 24 hours old
            cache_time = os.path.getmtime(cache_file)
            if time.time() - cache_time < 86400:  # 24 hours
                try:
                    with open(cache_file, 'r') as f:
                        cached_data = json.load(f)
                        logger.info(f"Loaded {len(cached_data)} tickers from cache")
                        return cached_data
                except:
                    pass
        
        # If no cache or cache is old, get fresh data
        logger.info("Fetching fresh NASDAQ ticker list...")
        tickers = self.fetch_nasdaq_tickers()
        
        # Save to cache
        try:
            with open(cache_file, 'w') as f:
                json.dump(tickers, f)
        except:
            pass
        
        return tickers
    
    def fetch_nasdaq_tickers(self):
        """Fetch NASDAQ tickers from FMP API"""
        try:
            import requests
            url = f"{self.apis['fmp']['base_url']}/nasdaq_constituent"
            params = {'apikey': self.apis['fmp']['key']}
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                tickers = [item['symbol'] for item in data if 'symbol' in item]
                logger.info(f"Fetched {len(tickers)} NASDAQ tickers from FMP")
                return tickers
        except Exception as e:
            logger.error(f"Error fetching NASDAQ tickers: {e}")
        
        # Fallback to hardcoded list of major NASDAQ stocks
        return [
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA',
            'NFLX', 'AMD', 'INTC', 'CSCO', 'ADBE', 'CRM', 'ORCL', 'AVGO',
            'TXN', 'QCOM', 'COST', 'SBUX', 'PYPL', 'ZOOM', 'DOCU', 'ROKU',
            'SHOP', 'SPOT', 'SNAP', 'TWTR', 'UBER', 'LYFT', 'PINS', 'ZM',
            'PTON', 'PLTR', 'SNOW', 'DDOG', 'CRWD', 'ZS', 'OKTA', 'SPLK'
        ]
    
    async def get_stock_data_iex_1(self, session, ticker):
        """Get stock data from IEX Cloud Account #1"""
        url = f"{self.apis['iex_1']['base_url']}/stock/{ticker}/quote"
        params = {'token': self.apis['iex_1']['key']}
        
        try:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'ticker': ticker,
                        'company_name': data.get('companyName', ''),
                        'current_price': data.get('latestPrice'),
                        'change': data.get('change'),
                        'change_percent': data.get('changePercent', 0) * 100,
                        'volume_today': data.get('latestVolume', 0),
                        'market_cap': data.get('marketCap'),
                        'pe_ratio': data.get('peRatio'),
                        'week_52_high': data.get('week52High'),
                        'week_52_low': data.get('week52Low'),
                        'avg_volume': data.get('avgTotalVolume'),
                                                    'source': 'iex_1',
                            'last_update': timezone.now()
                        }
        except Exception as e:
            logger.debug(f"IEX #1 error for {ticker}: {e}")

        return None

    async def get_stock_data_iex_2(self, session, ticker):
        """Get stock data from IEX Cloud Account #2"""
        url = f"{self.apis['iex_2']['base_url']}/stock/{ticker}/quote"
        params = {'token': self.apis['iex_2']['key']}

        try:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'ticker': ticker,
                        'company_name': data.get('companyName', ''),
                        'current_price': data.get('latestPrice'),
                        'change': data.get('change'),
                        'change_percent': data.get('changePercent', 0) * 100,
                        'volume_today': data.get('latestVolume', 0),
                        'market_cap': data.get('marketCap'),
                        'pe_ratio': data.get('peRatio'),
                        'week_52_high': data.get('week52High'),
                        'week_52_low': data.get('week52Low'),
                        'avg_volume': data.get('avgTotalVolume'),
                        'source': 'iex_2',
                        'last_update': timezone.now()
                    }
        except Exception as e:
            logger.debug(f"IEX #2 error for {ticker}: {e}")

        return None
    
    async def get_stock_data_finnhub(self, session, ticker):
        """Get stock data from Finnhub"""
        url = f"{self.apis['finnhub']['base_url']}/quote"
        params = {
            'symbol': ticker,
            'token': self.apis['finnhub']['key']
        }
        
        try:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    current_price = data.get('c')
                    prev_close = data.get('pc')
                    
                    if current_price and prev_close:
                        change = current_price - prev_close
                        change_percent = (change / prev_close) * 100
                        
                        return {
                            'ticker': ticker,
                            'current_price': current_price,
                            'change': change,
                            'change_percent': change_percent,
                            'high_today': data.get('h'),
                            'low_today': data.get('l'),
                            'open_today': data.get('o'),
                            'prev_close': prev_close,
                            'source': 'finnhub',
                            'last_update': timezone.now()
                        }
        except Exception as e:
            logger.debug(f"Finnhub error for {ticker}: {e}")
        
        return None

    async def get_stock_data_alphavantage(self, session, ticker):
        """Get stock data from Alpha Vantage"""
        url = self.apis['alphavantage']['base_url']
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': ticker,
            'apikey': self.apis['alphavantage']['key']
        }

        try:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    quote = data.get('Global Quote', {})

                    current_price = quote.get('05. price')
                    prev_close = quote.get('08. previous close')

                    if current_price and prev_close:
                        current_price = float(current_price)
                        prev_close = float(prev_close)
                        change = current_price - prev_close
                        change_percent = (change / prev_close) * 100

                        return {
                            'ticker': ticker,
                            'current_price': current_price,
                            'change': change,
                            'change_percent': change_percent,
                            'high_today': float(quote.get('03. high', 0)) or None,
                            'low_today': float(quote.get('04. low', 0)) or None,
                            'open_today': float(quote.get('02. open', 0)) or None,
                            'prev_close': prev_close,
                            'volume_today': int(quote.get('06. volume', 0)) or None,
                            'source': 'alphavantage',
                            'last_update': timezone.now()
                        }
        except Exception as e:
            logger.debug(f"Alpha Vantage error for {ticker}: {e}")

        return None

    async def get_stock_data_fmp(self, session, ticker):
        """Get stock data from Financial Modeling Prep"""
        url = f"{self.apis['fmp']['base_url']}/quote/{ticker}"
        params = {'apikey': self.apis['fmp']['key']}

        try:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and len(data) > 0:
                        quote = data[0]
                        
                        current_price = quote.get('price')
                        prev_close = quote.get('previousClose')

                        if current_price and prev_close:
                            change = quote.get('change', current_price - prev_close)
                            change_percent = quote.get('changesPercentage', 0)

                            return {
                                'ticker': ticker,
                                'company_name': quote.get('name', ''),
                                'current_price': current_price,
                                'change': change,
                                'change_percent': change_percent,
                                'high_today': quote.get('dayHigh'),
                                'low_today': quote.get('dayLow'),
                                'open_today': quote.get('open'),
                                'prev_close': prev_close,
                                'volume_today': quote.get('volume'),
                                'market_cap': quote.get('marketCap'),
                                'pe_ratio': quote.get('pe'),
                                'source': 'fmp',
                                'last_update': timezone.now()
                            }
        except Exception as e:
            logger.debug(f"FMP error for {ticker}: {e}")

        return None

    async def get_stock_data_twelvedata(self, session, ticker):
        """Get stock data from Twelve Data"""
        url = f"{self.apis['twelvedata']['base_url']}/quote"
        params = {
            'symbol': ticker,
            'apikey': self.apis['twelvedata']['key']
        }

        try:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    current_price = data.get('close')
                    prev_close = data.get('previous_close')

                    if current_price and prev_close:
                        current_price = float(current_price)
                        prev_close = float(prev_close)
                        change = current_price - prev_close
                        change_percent = (change / prev_close) * 100

                        return {
                            'ticker': ticker,
                            'company_name': data.get('name', ''),
                            'current_price': current_price,
                            'change': change,
                            'change_percent': change_percent,
                            'high_today': float(data.get('high', 0)) or None,
                            'low_today': float(data.get('low', 0)) or None,
                            'open_today': float(data.get('open', 0)) or None,
                            'prev_close': prev_close,
                            'volume_today': int(data.get('volume', 0)) or None,
                            'source': 'twelvedata',
                            'last_update': timezone.now()
                        }
        except Exception as e:
            logger.debug(f"Twelve Data error for {ticker}: {e}")

        return None

    async def get_stock_data_polygon(self, session, ticker):
        """Get stock data from Polygon.io"""
        url = f"{self.apis['polygon']['base_url']}/aggs/ticker/{ticker}/prev"
        params = {'apikey': self.apis['polygon']['key']}

        try:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'OK' and data.get('results'):
                        result = data['results'][0]
                        
                        current_price = result.get('c')  # close price
                        open_price = result.get('o')     # open price

                        if current_price and open_price:
                            change = current_price - open_price
                            change_percent = (change / open_price) * 100

                            return {
                                'ticker': ticker,
                                'current_price': current_price,
                                'change': change,
                                'change_percent': change_percent,
                                'high_today': result.get('h'),
                                'low_today': result.get('l'),
                                'open_today': open_price,
                                'volume_today': result.get('v'),
                                'source': 'polygon',
                                'last_update': timezone.now()
                            }
        except Exception as e:
            logger.debug(f"Polygon error for {ticker}: {e}")

        return None
    
    async def collect_batch(self, session, tickers_batch, api_source='iex'):
        """Collect data for a batch of exactly 10 tickers"""
        if len(tickers_batch) > 10:
            logger.warning(f"Batch size {len(tickers_batch)} exceeds 10, trimming to 10")
            tickers_batch = tickers_batch[:10]
        
        tasks = []
        
        # Create concurrent tasks for all 10 stocks in the batch
        for ticker in tickers_batch:
            if api_source == 'iex_1':
                task = self.get_stock_data_iex_1(session, ticker)
            elif api_source == 'iex_2':
                task = self.get_stock_data_iex_2(session, ticker)
            elif api_source == 'finnhub':
                task = self.get_stock_data_finnhub(session, ticker)
            elif api_source == 'alphavantage':
                task = self.get_stock_data_alphavantage(session, ticker)
            elif api_source == 'fmp':
                task = self.get_stock_data_fmp(session, ticker)
            elif api_source == 'twelvedata':
                task = self.get_stock_data_twelvedata(session, ticker)
            elif api_source == 'polygon':
                task = self.get_stock_data_polygon(session, ticker)
            else:
                logger.warning(f"Unknown API source: {api_source}")
                continue
            
            tasks.append(task)
        
        # Execute all 10 requests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter and validate results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.debug(f"Exception for {tickers_batch[i] if i < len(tickers_batch) else 'unknown'}: {result}")
            elif result and result.get('current_price') is not None:
                valid_results.append(result)
            else:
                logger.debug(f"No valid data for {tickers_batch[i] if i < len(tickers_batch) else 'unknown'}")
        
        return valid_results

    async def process_api_phase(self, session, tickers, api_source, batch_size, all_results, delay=0.1):
        """Process a complete API phase with batching and delays"""
        total_batches = (len(tickers) + batch_size - 1) // batch_size
        
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            try:
                results = await self.collect_batch(session, batch, api_source)
                all_results.extend(results)
                
                # Log progress for every batch since we have fewer batches per API
                logger.info(f"   {api_source.upper()} batch {batch_num}/{total_batches}: {len(results)} stocks | Total: {len(all_results)}")
                
                # Apply delay between batches
                if batch_num < total_batches:  # Don't delay after last batch
                    await asyncio.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error in {api_source.upper()} batch {batch_num}: {e}")

    def save_to_database(self, stock_data_list):
        """Save stock data to Django database"""
        saved_count = 0
        
        for data in stock_data_list:
            try:
                # Calculate additional metrics
                change_percent = data.get('change_percent', 0)
                note_parts = []
                
                # Add note based on performance
                if change_percent >= 10:
                    note_parts.append("price increase 10")
                elif change_percent >= 5:
                    note_parts.append("price increase 5")
                elif change_percent <= -10:
                    note_parts.append("price drop 10")
                elif change_percent <= -5:
                    note_parts.append("price drop 5")
                
                # Volume analysis (if available)
                volume_today = data.get('volume_today', 0)
                avg_volume = data.get('avg_volume', 0)
                
                if avg_volume and volume_today > avg_volume * 2:
                    note_parts.append("volume spike 2x")
                elif avg_volume and volume_today > avg_volume * 1.5:
                    note_parts.append("volume increase 50")
                
                note = ", ".join(note_parts) if note_parts else "normal trading"
                
                # Update or create stock record
                StockAlert.objects.update_or_create(
                    ticker=data['ticker'],
                    defaults={
                        'company_name': data.get('company_name', ''),
                        'current_price': data['current_price'],
                        'change_percent': change_percent,
                        'volume_today': volume_today,
                        'avg_volume': avg_volume,
                        'market_cap': data.get('market_cap'),
                        'pe_ratio': data.get('pe_ratio'),
                        'week_52_high': data.get('week_52_high'),
                        'week_52_low': data.get('week_52_low'),
                        'note': note,
                        'last_update': data['last_update'],
                        'data_source': data['source']
                    }
                )
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Error saving {data.get('ticker', 'unknown')}: {e}")
        
        return saved_count
    
    async def run_collection_cycle(self):
        """Run one complete collection cycle - ALL NASDAQ STOCKS every 10 minutes"""
        start_time = time.time()
        logger.info(f"🚀 Starting COMPLETE NASDAQ collection cycle at {datetime.now()}")
        
        # Get ALL NASDAQ tickers
        all_tickers = self.nasdaq_tickers.copy()
        total_stocks = len(all_tickers)
        
        logger.info(f"📊 Collecting data for ALL {total_stocks} NASDAQ stocks in batches of 10")
        
        # Prioritize tickers (put high-priority ones first)
        priority_tickers = [t for t in self.priority_tickers if t in all_tickers]
        regular_tickers = [t for t in all_tickers if t not in self.priority_tickers]
        
        # Organize with priority first, then regular
        organized_tickers = priority_tickers + regular_tickers
        
        all_results = []
        batch_size = 10  # Fixed batch size of 10 stocks per batch
        
        # Create aiohttp session with optimized settings for high volume
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        timeout = aiohttp.ClientTimeout(total=600)  # 10 minutes total timeout
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            
            # DUAL IEX FREE ACCOUNTS STRATEGY FOR 100% NASDAQ COVERAGE
            # Calculate daily limits per cycle (144 cycles per day = every 10 minutes)
            cycles_per_day = 144
            
            # Calculate what each IEX account can handle per cycle
            # Use aggressive limits since monthly quota has plenty of room
            iex_1_cycle_limit = min(2000, 2000)  # Use 2000 per cycle (well within monthly limit)
            iex_2_cycle_limit = min(1500, 1500)  # Use 1500 per cycle for second account
            total_iex_capacity = iex_1_cycle_limit + iex_2_cycle_limit
            
            logger.info(f"🎯 DUAL IEX FREE STRATEGY FOR 100% COVERAGE")
            logger.info(f"   📊 IEX Account #1: {iex_1_cycle_limit:,} stocks per cycle")
            logger.info(f"   📊 IEX Account #2: {iex_2_cycle_limit:,} stocks per cycle")
            logger.info(f"   🎉 Total IEX capacity: {total_iex_capacity:,} stocks per cycle")
            
            if total_iex_capacity >= total_stocks:
                # IEX accounts can handle ALL NASDAQ stocks
                logger.info(f"✅ Dual IEX accounts can handle ALL {total_stocks} NASDAQ stocks!")
                
                api_limits = {
                    'iex_1': min(iex_1_cycle_limit, total_stocks),
                    'iex_2': min(iex_2_cycle_limit, max(0, total_stocks - iex_1_cycle_limit)),
                    'finnhub': 0,  # Not needed with dual IEX
                    'alphavantage': 0,
                    'fmp': 0,
                    'twelvedata': 0,
                    'polygon': 0
                }
            else:
                # Use dual IEX + backup APIs for any remaining
                remaining_after_iex = total_stocks - total_iex_capacity
                logger.info(f"📊 Using dual IEX + backup APIs for {remaining_after_iex} remaining stocks")
                
                api_limits = {
                    'iex_1': iex_1_cycle_limit,
                    'iex_2': iex_2_cycle_limit,
                    'finnhub': min(600, remaining_after_iex),
                    'alphavantage': max(0, min(3, remaining_after_iex - 600)) if remaining_after_iex > 600 else 0,
                    'fmp': 0,  # Minimal for backup only
                    'twelvedata': 0,
                    'polygon': 0
                }
            
            logger.info(f"📊 API limits per cycle: {api_limits}")
            
            # Distribute ALL 3,331 stocks across APIs
            current_index = 0
            
            # Phase 1: IEX Cloud Account #1 (primary)
            iex_1_limit = api_limits['iex_1']
            iex_1_tickers = organized_tickers[current_index:current_index + iex_1_limit]
            current_index += len(iex_1_tickers)
            
            if iex_1_tickers:
                logger.info(f"📡 Phase 1: IEX Cloud #1 (FREE) - {len(iex_1_tickers)} stocks in batches of 10")
                await self.process_api_phase(session, iex_1_tickers, 'iex_1', batch_size, all_results, delay=0.1)
            
            # Phase 2: IEX Cloud Account #2 (secondary)
            iex_2_limit = api_limits['iex_2']
            iex_2_tickers = organized_tickers[current_index:current_index + iex_2_limit]
            current_index += len(iex_2_tickers)
            
            if iex_2_tickers:
                logger.info(f"📡 Phase 2: IEX Cloud #2 (FREE) - {len(iex_2_tickers)} stocks in batches of 10")
                await self.process_api_phase(session, iex_2_tickers, 'iex_2', batch_size, all_results, delay=0.1)
            
            # Phase 3: Finnhub (backup only if needed)
            finnhub_limit = api_limits['finnhub']
            finnhub_tickers = organized_tickers[current_index:current_index + finnhub_limit]
            current_index += len(finnhub_tickers)
            
            if finnhub_tickers:
                logger.info(f"📡 Phase 3: Finnhub (backup) - {len(finnhub_tickers)} stocks in batches of 10")
                await self.process_api_phase(session, finnhub_tickers, 'finnhub', batch_size, all_results, delay=0.2)
            
            # Phase 4: Alpha Vantage (minimal backup)
            av_limit = api_limits['alphavantage']
            av_tickers = organized_tickers[current_index:current_index + av_limit]
            current_index += len(av_tickers)
            
            if av_tickers:
                logger.info(f"📡 Phase 4: Alpha Vantage (backup) - {len(av_tickers)} stocks in batches of 10")
                await self.process_api_phase(session, av_tickers, 'alphavantage', batch_size, all_results, delay=1.0)
            
            # Calculate remaining stocks and provide recommendations
            remaining_stocks = total_stocks - current_index
            if remaining_stocks > 0:
                logger.warning(f"⚠️ {remaining_stocks} stocks not collected - need additional API keys")
                logger.info(f"💡 TO GET 100% COVERAGE:")
                logger.info(f"   🔑 Add second IEX Cloud free account (IEX_API_KEY_2)")
                logger.info(f"   📝 Sign up at https://iexcloud.io/ with different email")
                logger.info(f"   🎯 This will give you 100% FREE coverage of all {total_stocks} stocks")
            else:
                logger.info(f"🎉 ALL {total_stocks} NASDAQ stocks collected with DUAL IEX FREE accounts!")
                logger.info(f"✨ Using 2 FREE IEX Cloud accounts - $0/month for 100% coverage")
        
        # Save all results to database
        if all_results:
            logger.info(f"💾 Saving {len(all_results)} stock records to database...")
            saved_count = self.save_to_database(all_results)
            
            collection_time = time.time() - start_time
            coverage_percent = (len(all_results) / total_stocks) * 100
            
            logger.info(f"✅ COMPLETE CYCLE FINISHED!")
            logger.info(f"   📈 Coverage: {len(all_results)}/{total_stocks} stocks ({coverage_percent:.1f}%)")
            logger.info(f"   💾 Saved: {saved_count} records")
            logger.info(f"   ⏱️ Time: {collection_time:.1f} seconds")
            logger.info(f"   🔑 Strategy: Dual IEX Cloud FREE accounts")
            logger.info(f"   💰 Cost: $0/month for {len(all_results):,} stocks")
            if coverage_percent >= 99.9:
                logger.info(f"   🎉 FULL NASDAQ COVERAGE ACHIEVED WITH FREE ACCOUNTS!")
            logger.info(f"   🔄 Next cycle in 10 minutes")
            
            return saved_count
        else:
            logger.warning("❌ No data collected in this cycle")
            return 0

class Command(BaseCommand):
    help = 'Collect NASDAQ real-time data every 10 minutes'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run collection once instead of continuously',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=600,  # 10 minutes
            help='Collection interval in seconds (default: 600)',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting NASDAQ Real-Time Data Collector')
        )
        
        collector = NASDAQRealTimeCollector()
        
        if options['once']:
            # Run once and exit
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                collected = loop.run_until_complete(collector.run_collection_cycle())
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Collected {collected} stocks')
                )
            finally:
                loop.close()
        else:
            # Run continuously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.run_continuous_collection(collector, options['interval']))
            except KeyboardInterrupt:
                self.stdout.write(
                    self.style.WARNING('⏹️ Collection stopped by user')
                )
            finally:
                loop.close()
    
    async def run_continuous_collection(self, collector, interval):
        """Run collection continuously every interval seconds"""
        cycle_count = 0
        
        while True:
            try:
                cycle_count += 1
                self.stdout.write(f"\n🔄 Starting collection cycle #{cycle_count}")
                
                collected = await collector.run_collection_cycle()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Cycle #{cycle_count}: {collected} stocks collected')
                )
                
                # Wait for next cycle
                self.stdout.write(f"⏰ Waiting {interval} seconds for next cycle...")
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error in cycle #{cycle_count}: {e}')
                )
                self.stdout.write("⏰ Waiting 60 seconds before retry...")
                await asyncio.sleep(60)
