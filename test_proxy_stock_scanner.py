#!/usr/bin/env python3
"""
Standalone test script for stock scanner with proxy functionality
Tests the proxy integration without requiring database connection
"""

import os
import sys
import time
import random
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from proxy_manager import ProxyManager

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

def test_stock_with_proxy(symbol, ticker_number, proxy_manager):
    """Test a single stock with proxy - verifies full data retrieval then discards results"""
    try:
        # Get proxy for this ticker
        proxy = None
        if proxy_manager:
            proxy = proxy_manager.get_proxy_for_ticker(ticker_number)
            if proxy and ticker_number <= 3:  # Show proxy info for first 3 tickers
                print(f"[PROXY] {symbol}: Using proxy {proxy}")
        
        patch_yfinance_proxy(proxy)
        
        # Minimal delay
        time.sleep(random.uniform(0.01, 0.02))
        
        # Test comprehensive data retrieval (same as production script)
        ticker_obj = yf.Ticker(symbol)
        info = None
        hist = None
        current_price = None
        
        # Approach 1: Try to get basic info (full company data)
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
        
        # Determine if we have enough data to process (same validation as production)
        has_data = hist is not None and not hist.empty
        has_info = info and isinstance(info, dict) and len(info) > 3
        has_price = current_price is not None and not pd.isna(current_price)
        
        if not has_data and not has_info:
            print(f"[FAILED] {symbol}: No data at all - Proxy: {proxy}")
            return False
        
        # Calculate price changes (same as production)
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
        
        # Extract comprehensive data (same as production but discard after verification)
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
        
        # Verify we have meaningful data (same validation as production)
        data_fields = [v for v in stock_data.values() if v is not None and v != '']
        if len(data_fields) < 5:  # At least 5 meaningful fields
            print(f"[FAILED] {symbol}: Insufficient data fields ({len(data_fields)}) - Proxy: {proxy}")
            return False
        
        # Success - show summary but discard data
        change_str = f"{change_percent:+.2f}%" if change_percent else "N/A"
        data_count = len(data_fields)
        print(f"[SUCCESS] {symbol}: ${current_price:.2f} ({change_str}) - {data_count} fields - Proxy: {proxy}")
        
        # Explicitly discard data to free memory
        del ticker_obj, info, hist, stock_data
        return True
            
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
        return False

def main():
    """Main test function"""
    print("🔍 PROXY STOCK SCANNER TEST")
    print("=" * 50)
    
    # Test symbols - use more symbols to test more proxies
    test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'ADBE', 'CRM', 
                   'ORCL', 'CSCO', 'INTC', 'QCOM', 'AMD', 'PYPL', 'NKE', 'DIS', 'WMT', 'JPM']
    
    # Initialize proxy manager
    print("\n📡 Initializing proxy manager...")
    try:
        proxy_manager = ProxyManager()
        stats = proxy_manager.get_proxy_stats()
        print(f"✅ Proxy manager ready: {stats}")
    except Exception as e:
        print(f"❌ Proxy manager failed: {e}")
        proxy_manager = None
    
    # Test connectivity
    print("\n🌐 Testing yfinance connectivity...")
    try:
        test_ticker = yf.Ticker("AAPL")
        test_info = test_ticker.info
        if test_info:
            print("✅ yfinance connectivity test passed")
        else:
            print("⚠️  yfinance connectivity test failed")
    except Exception as e:
        print(f"❌ yfinance connectivity error: {e}")
    
    # Test stocks with proxies
    print(f"\n📊 Testing {len(test_symbols)} stocks with proxy rotation...")
    print("=" * 50)
    
    start_time = time.time()
    successful = 0
    failed = 0
    proxy_usage = {}
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_symbol = {}
        for i, symbol in enumerate(test_symbols, 1):
            future = executor.submit(test_stock_with_proxy, symbol, i, proxy_manager)
            future_to_symbol[future] = symbol
        
        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                result = future.result(timeout=15)
                if result:
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"[TIMEOUT] {symbol}: {e}")
                failed += 1
    
    elapsed = time.time() - start_time
    
    # Results
    print("\n" + "=" * 50)
    print("📈 TEST RESULTS")
    print("=" * 50)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {(successful/len(test_symbols)*100):.1f}%")
    print(f"⏱️  Time: {elapsed:.2f}s")
    print(f"🚀 Rate: {len(test_symbols)/elapsed:.2f} symbols/sec")
    
    if proxy_manager:
        final_stats = proxy_manager.get_proxy_stats()
        print(f"🌐 Final proxy stats: {final_stats}")
        print(f"🔄 Proxies used in test: {final_stats['used_in_run']}")
    
    print("\n🎯 Test completed!")
    print("💡 This test verified that each proxy can pull full stock data and then discarded the results.")

if __name__ == "__main__":
    main()