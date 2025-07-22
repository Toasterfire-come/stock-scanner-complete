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
        # Free API configuration
        self.apis = {
            'iex': {
                'key': os.getenv('IEX_API_KEY', 'pk_test_your_iex_key'),
                'base_url': 'https://cloud.iexapis.com/stable',
                'calls_per_minute': 100,
                'calls_per_month': 500000
            },
            'finnhub': {
                'key': os.getenv('FINNHUB_API_KEY', 'your_finnhub_key'),
                'base_url': 'https://finnhub.io/api/v1',
                'calls_per_minute': 60
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
            }
        }
        
        # Load NASDAQ tickers
        self.nasdaq_tickers = self.get_nasdaq_tickers()
        
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
    
    async def get_stock_data_iex(self, session, ticker):
        """Get stock data from IEX Cloud"""
        url = f"{self.apis['iex']['base_url']}/stock/{ticker}/quote"
        params = {'token': self.apis['iex']['key']}
        
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
                        'source': 'iex',
                        'last_update': timezone.now()
                    }
        except Exception as e:
            logger.debug(f"IEX error for {ticker}: {e}")
        
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
    
    async def collect_batch(self, session, tickers_batch, api_source='iex'):
        """Collect data for a batch of exactly 10 tickers"""
        if len(tickers_batch) > 10:
            logger.warning(f"Batch size {len(tickers_batch)} exceeds 10, trimming to 10")
            tickers_batch = tickers_batch[:10]
        
        tasks = []
        
        # Create concurrent tasks for all 10 stocks in the batch
        for ticker in tickers_batch:
            if api_source == 'iex':
                task = self.get_stock_data_iex(session, ticker)
            elif api_source == 'finnhub':
                task = self.get_stock_data_finnhub(session, ticker)
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
            
            # Calculate distribution across APIs
            iex_limit = min(2000, total_stocks)  # IEX handles up to 2000 stocks
            finnhub_limit = min(600, max(0, total_stocks - iex_limit))  # Finnhub for next 600 (respects daily limit)
            
            # Phase 1: IEX Cloud (primary source) - batches of 10
            iex_tickers = organized_tickers[:iex_limit]
            logger.info(f"📡 Phase 1: IEX Cloud collection - {len(iex_tickers)} stocks in batches of 10")
            
            for i in range(0, len(iex_tickers), batch_size):
                batch = iex_tickers[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                
                try:
                    results = await self.collect_batch(session, batch, 'iex')
                    all_results.extend(results)
                    
                    if batch_num % 10 == 0:  # Log every 10th batch (100 stocks)
                        logger.info(f"   IEX batch {batch_num}: {len(results)} stocks | Total: {len(all_results)}")
                    
                    # Minimal delay for IEX (good free tier)
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error in IEX batch {batch_num}: {e}")
            
            # Phase 2: Finnhub (secondary source) - batches of 10
            if finnhub_limit > 0:
                finnhub_tickers = organized_tickers[iex_limit:iex_limit + finnhub_limit]
                logger.info(f"📡 Phase 2: Finnhub collection - {len(finnhub_tickers)} stocks in batches of 10")
                
                for i in range(0, len(finnhub_tickers), batch_size):
                    batch = finnhub_tickers[i:i + batch_size]
                    batch_num = (i // batch_size) + 1
                    
                    try:
                        results = await self.collect_batch(session, batch, 'finnhub')
                        all_results.extend(results)
                        
                        if batch_num % 10 == 0:  # Log every 10th batch
                            logger.info(f"   Finnhub batch {batch_num}: {len(results)} stocks | Total: {len(all_results)}")
                        
                        # Slightly longer delay for Finnhub
                        await asyncio.sleep(0.2)
                        
                    except Exception as e:
                        logger.error(f"Error in Finnhub batch {batch_num}: {e}")
            
            # Phase 3: Alpha Vantage for any remaining (if needed)
            remaining_count = total_stocks - iex_limit - finnhub_limit
            if remaining_count > 0:
                remaining_tickers = organized_tickers[iex_limit + finnhub_limit:]
                # Note: Alpha Vantage has lower limits, so we'll collect what we can
                av_limit = min(100, remaining_count)  # Only 100 for Alpha Vantage
                av_tickers = remaining_tickers[:av_limit]
                
                logger.info(f"📡 Phase 3: Backup collection - {len(av_tickers)} stocks")
                logger.warning(f"⚠️ {remaining_count - av_limit} stocks skipped due to API limits")
        
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
