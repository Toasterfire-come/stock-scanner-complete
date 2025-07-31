#!/usr/bin/env python3
"""
Standalone Stock Scanner
Works without database connection - saves results to JSON
"""

import os
import sys
import time
import random
import json
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from proxy_manager import ProxyManager
from datetime import datetime

def patch_yfinance_proxy(proxy):
    """Patch yfinance to use proxy"""
    if not proxy:
        return
        
    try:
        session = requests.Session()
        session.proxies = {
            'http': proxy,
            'https': proxy
        }
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        yfinance.shared._requests = session
    except Exception as e:
        print(f"[PROXY ERROR] Failed to set proxy {proxy}: {e}")

def process_symbol(symbol, ticker_number, proxy_manager):
    """Process a single symbol with comprehensive data collection"""
    try:
        # Get proxy for this ticker
        proxy = None
        if proxy_manager:
            proxy = proxy_manager.get_proxy_for_ticker(ticker_number)
            if proxy and ticker_number <= 5:  # Show proxy info for first 5 tickers
                print(f"[PROXY] {symbol}: Using proxy {proxy}")
        
        patch_yfinance_proxy(proxy)
        
        # Minimal delay
        time.sleep(random.uniform(0.01, 0.02))
        
        # Try multiple approaches to get data
        ticker_obj = yf.Ticker(symbol)
        info = None
        hist = None
        current_price = None
        
        # Approach 1: Try to get basic info
        try:
            info = ticker_obj.info
        except:
            pass
        
        # Approach 2: Try to get historical data with multiple periods
        for period in ["1d", "5d", "1mo"]:
            try:
                hist = ticker_obj.history(period=period, timeout=8)
                if hist is not None and not hist.empty and len(hist) > 0:
                    try:
                        current_price = hist['Close'].iloc[-1]
                        if current_price is not None and not pd.isna(current_price):
                            break
                    except:
                        continue
            except Exception as e:
                continue
        
        # Approach 3: Try to get current price from info if historical failed
        if current_price is None and info:
            try:
                current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('regularMarketOpen')
            except:
                pass
        
        # Approach 4: Try a simple quote request
        if current_price is None:
            try:
                quote = ticker_obj.quote_type
                if quote:
                    # If we can get quote type, symbol exists
                    pass
            except:
                pass
        
        # Determine if we have enough data to process
        has_data = hist is not None and not hist.empty
        has_info = info and isinstance(info, dict) and len(info) > 3
        has_price = current_price is not None and not pd.isna(current_price)
        
        if not has_data and not has_info:
            print(f"[FAILED] {symbol}: No data at all - Proxy: {proxy}")
            return None
        
        # Calculate price changes
        price_change_today = None
        change_percent = None
        if has_data and len(hist) > 1:
            try:
                prev_price = hist['Close'].iloc[-2]
                if not pd.isna(prev_price) and prev_price > 0 and current_price:
                    price_change_today = current_price - prev_price
                    change_percent = (price_change_today / prev_price) * 100
            except:
                pass
        
        # Extract comprehensive data
        stock_data = {
            'ticker': symbol,
            'symbol': symbol,
            'company_name': info.get('longName') if info else '' or info.get('shortName') if info else '' or symbol,
            'name': info.get('longName') if info else '' or info.get('shortName') if info else '' or symbol,
            'exchange': info.get('exchange', 'NASDAQ') if info else 'NASDAQ',
            
            # Price data
            'current_price': current_price,
            'price_change_today': price_change_today,
            'change_percent': change_percent,
            
            # Bid/Ask data
            'bid_price': info.get('bid') if info else None,
            'ask_price': info.get('ask') if info else None,
            'days_low': info.get('dayLow') if info else None,
            'days_high': info.get('dayHigh') if info else None,
            
            # Volume data
            'volume': info.get('volume') if info else None,
            'volume_today': info.get('volume') if info else None,
            'avg_volume_3mon': info.get('averageVolume') if info else None,
            'shares_available': info.get('sharesOutstanding') if info else None,
            
            # Market data
            'market_cap': info.get('marketCap') if info else None,
            
            # Financial ratios
            'pe_ratio': info.get('trailingPE') if info else None,
            'dividend_yield': info.get('dividendYield') if info else None,
            'earnings_per_share': info.get('trailingEps') if info else None,
            'book_value': info.get('bookValue') if info else None,
            'price_to_book': info.get('priceToBook') if info else None,
            
            # 52-week range
            'week_52_low': info.get('fiftyTwoWeekLow') if info else None,
            'week_52_high': info.get('fiftyTwoWeekHigh') if info else None,
            
            # Target
            'one_year_target': info.get('targetMeanPrice') if info else None,
            
            # Metadata
            'proxy_used': proxy,
            'timestamp': datetime.now().isoformat(),
        }
        
        # Calculate DVAV (Day Volume over Average Volume)
        if stock_data['volume'] and stock_data['avg_volume_3mon']:
            try:
                dvav_val = stock_data['volume'] / stock_data['avg_volume_3mon']
                if not (pd.isna(dvav_val) or pd.isinf(dvav_val)):
                    stock_data['dvav'] = dvav_val
                else:
                    stock_data['dvav'] = None
            except Exception:
                stock_data['dvav'] = None
        
        # Success - show summary
        change_str = f"{change_percent:+.2f}%" if change_percent else "N/A"
        data_count = len([v for v in stock_data.values() if v is not None and v != ''])
        print(f"[SUCCESS] {symbol}: ${current_price:.2f} ({change_str}) - {data_count} fields - Proxy: {proxy}")
        
        return stock_data
        
    except Exception as e:
        err_str = str(e).lower()
        if 'too many requests' in err_str or 'rate limit' in err_str or '401' in err_str:
            if proxy and proxy_manager:
                proxy_manager.mark_proxy_failed(proxy)
            print(f"[RATE LIMIT] {symbol}: {e}")
            time.sleep(random.uniform(0.5, 1.0))
        elif any(x in err_str for x in ['no data found', 'delisted', 'not found', '404']):
            print(f"[DELISTED] {symbol}: {e}")
        else:
            print(f"[ERROR] {symbol}: {e}")
        return None

def get_nasdaq_symbols(limit=100):
    """Get NASDAQ symbols - using a predefined list for standalone mode"""
    # Popular NASDAQ symbols
    nasdaq_symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'ADBE', 'CRM',
        'ORCL', 'CSCO', 'INTC', 'QCOM', 'AMD', 'PYPL', 'NKE', 'DIS', 'WMT', 'JPM',
        'V', 'JNJ', 'PG', 'UNH', 'HD', 'MA', 'BAC', 'ABT', 'KO', 'PEP',
        'TMO', 'COST', 'AVGO', 'DHR', 'ABBV', 'WFC', 'MRK', 'ACN', 'VZ', 'CMCSA',
        'ADP', 'TXN', 'BMY', 'PM', 'RTX', 'QCOM', 'UNP', 'UPS', 'MS', 'SPGI',
        'CAT', 'DE', 'LOW', 'ISRG', 'GILD', 'AMGN', 'T', 'CVS', 'SCHW', 'BA',
        'MDLZ', 'CI', 'SO', 'DUK', 'PLD', 'REGN', 'BDX', 'TJX', 'CME', 'ADI',
        'NEE', 'ITW', 'SYK', 'ZTS', 'MMC', 'ETN', 'KLAC', 'AON', 'SHW', 'ICE',
        'APD', 'GE', 'SLB', 'EOG', 'PXD', 'COP', 'OXY', 'VLO', 'PSX', 'MPC',
        'HAL', 'BKR', 'DVN', 'FANG', 'CTRA', 'MRO', 'APA', 'NOV', 'FTI', 'WMB'
    ]
    
    return nasdaq_symbols[:limit]

def main():
    """Main function"""
    print("STANDALONE STOCK SCANNER")
    print("=" * 50)
    
    # Configuration
    limit = 50  # Number of stocks to process
    num_threads = 10
    use_proxies = True
    
    print(f"Configuration:")
    print(f"  Stocks to process: {limit}")
    print(f"  Threads: {num_threads}")
    print(f"  Use proxies: {use_proxies}")
    
    # Get symbols
    symbols = get_nasdaq_symbols(limit)
    print(f"\nProcessing {len(symbols)} NASDAQ symbols")
    
    # Initialize proxy manager
    proxy_manager = None
    if use_proxies:
        try:
            proxy_manager = ProxyManager()
            stats = proxy_manager.get_proxy_stats()
            if stats['total_working'] > 0:
                print(f"SUCCESS: Loaded {stats['total_working']} proxies")
            else:
                print("No proxies available - trying to refresh...")
                count = proxy_manager.refresh_proxy_pool(force=True)
                if count > 0:
                    stats = proxy_manager.get_proxy_stats()
                    print(f"SUCCESS: Refreshed pool - {stats['total_working']} proxies")
                else:
                    print("WARNING: No proxies available - continuing without proxies")
                    proxy_manager = None
        except Exception as e:
            print(f"ERROR: Proxy manager failed: {e}")
            proxy_manager = None
    
    # Test connectivity
    print("\nTesting yfinance connectivity...")
    try:
        test_ticker = yf.Ticker("AAPL")
        test_info = test_ticker.info
        if test_info:
            print("SUCCESS: yfinance connectivity test passed")
        else:
            print("WARNING: yfinance connectivity test failed")
    except Exception as e:
        print(f"ERROR: yfinance connectivity error: {e}")
    
    # Process stocks
    print(f"\nStarting to process {len(symbols)} symbols...")
    print("=" * 50)
    
    start_time = time.time()
    successful = 0
    failed = 0
    results = []
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_symbol = {}
        for i, symbol in enumerate(symbols, 1):
            future = executor.submit(process_symbol, symbol, i, proxy_manager)
            future_to_symbol[future] = symbol
        
        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                result = future.result(timeout=15)
                if result:
                    successful += 1
                    results.append(result)
                else:
                    failed += 1
            except Exception as e:
                print(f"[TIMEOUT] {symbol}: {e}")
                failed += 1
    
    elapsed = time.time() - start_time
    
    # Results
    print("\n" + "=" * 50)
    print("SCAN RESULTS")
    print("=" * 50)
    print(f"SUCCESSFUL: {successful}")
    print(f"FAILED: {failed}")
    print(f"SUCCESS RATE: {(successful/len(symbols)*100):.1f}%")
    print(f"TIME: {elapsed:.2f}s")
    print(f"RATE: {len(symbols)/elapsed:.2f} symbols/sec")
    
    if proxy_manager:
        final_stats = proxy_manager.get_proxy_stats()
        print(f"PROXY STATS: {final_stats}")
    
    # Save results
    if results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stock_scan_results_{timestamp}.json"
        
        output_data = {
            'scan_info': {
                'timestamp': datetime.now().isoformat(),
                'total_symbols': len(symbols),
                'successful': successful,
                'failed': failed,
                'success_rate': f"{(successful/len(symbols)*100):.1f}%",
                'elapsed_time': f"{elapsed:.2f}s",
                'rate': f"{len(symbols)/elapsed:.2f} symbols/sec"
            },
            'stocks': results
        }
        
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        print(f"\nSUCCESS: Results saved to {filename}")
        print(f"Total stocks processed: {len(results)}")
    else:
        print("\nWARNING: No results to save")
    
    print("\nScan completed!")

if __name__ == "__main__":
    main()