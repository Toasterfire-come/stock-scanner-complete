#!/usr/bin/env python3
"""
Quick Scanner Test - 100 Tickers
================================
Fast test to verify both scanners work correctly
"""

import os
import sys
import time
import logging
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
import django
django.setup()

from stocks.models import Stock

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger('quick_test')
logging.getLogger('yfinance').setLevel(logging.ERROR)

# Import scanners
sys.path.insert(0, str(Path(__file__).parent))
import realtime_daily_with_proxies as daily
import scanner_10min_fast as fast

logger.info('='*80)
logger.info('QUICK SCANNER TEST - 100 TICKERS')
logger.info('='*80)

# Get 100 test tickers
tickers = list(Stock.objects.values_list('ticker', flat=True)[:100])
logger.info(f'Testing with {len(tickers)} tickers')
logger.info('')

# Load proxies
daily.proxy_list = daily.load_proxies()
fast.proxy_list = fast.proxy_list or daily.proxy_list
logger.info(f'Loaded {len(daily.proxy_list)} proxies')
logger.info('')

# Test Daily Scanner
logger.info('TEST 1: Daily Scanner (0.488 t/s)')
logger.info(f'Expected time: {len(tickers) / daily.TARGET_RATE:.1f}s')

start_time = time.time()
success = 0
failed = 0
proxy_used = 0

from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=daily.MAX_THREADS) as executor:
    future_to_ticker = {executor.submit(daily.fetch_stock_with_proxy, ticker): ticker for ticker in tickers}

    for future in as_completed(future_to_ticker):
        data = future.result()
        if data:
            success += 1
            if data.get('used_proxy'):
                proxy_used += 1
        else:
            failed += 1

elapsed = time.time() - start_time
rate = len(tickers) / elapsed

logger.info('')
logger.info('DAILY SCANNER RESULTS:')
logger.info(f'  Success: {success}/{len(tickers)} ({success/len(tickers)*100:.1f}%)')
logger.info(f'  Proxy usage: {proxy_used}/{success} ({proxy_used/success*100:.0f}%)' if success > 0 else '  Proxy usage: 0/0 (0%)')
logger.info(f'  Time: {elapsed:.1f}s')
logger.info(f'  Rate: {rate:.3f} t/s (target: {daily.TARGET_RATE} t/s)')
logger.info(f'  Status: {"PASS" if success >= 90 and (success == 0 or proxy_used/success >= 0.7) else "FAIL"}')
logger.info('')

# Test 10-Min Scanner
logger.info('TEST 2: 10-Min Scanner (15 t/s)')
logger.info(f'Expected time: {len(tickers) / fast.TARGET_RATE:.1f}s')

# Reset rate limiter
fast.last_request_time = [time.time()]
fast.failed_proxies = set()

start_time = time.time()
success2 = 0
failed2 = 0
proxy_used2 = 0

with ThreadPoolExecutor(max_workers=fast.MAX_THREADS) as executor:
    future_to_ticker = {executor.submit(fast.fetch_10min_fast, ticker): ticker for ticker in tickers}

    for future in as_completed(future_to_ticker):
        data = future.result()
        if data:
            success2 += 1
            if data.get('used_proxy'):
                proxy_used2 += 1
        else:
            failed2 += 1

elapsed2 = time.time() - start_time
rate2 = len(tickers) / elapsed2

logger.info('')
logger.info('10-MIN SCANNER RESULTS:')
logger.info(f'  Success: {success2}/{len(tickers)} ({success2/len(tickers)*100:.1f}%)')
logger.info(f'  Proxy usage: {proxy_used2}/{success2} ({proxy_used2/success2*100:.0f}%)' if success2 > 0 else '  Proxy usage: 0/0 (0%)')
logger.info(f'  Time: {elapsed2:.1f}s')
logger.info(f'  Rate: {rate2:.1f} t/s (target: {fast.TARGET_RATE} t/s)')
logger.info(f'  Status: {"PASS" if success2 >= 90 and (success2 == 0 or proxy_used2/success2 >= 0.7) else "FAIL"}')
logger.info('')

logger.info('='*80)
logger.info('SUMMARY')
logger.info('='*80)
logger.info(f'Daily: {"PASS" if success >= 90 else "FAIL"} ({success/len(tickers)*100:.0f}% success)')
logger.info(f'10-Min: {"PASS" if success2 >= 90 else "FAIL"} ({success2/len(tickers)*100:.0f}% success)')
logger.info('='*80)
