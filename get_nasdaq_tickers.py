#!/usr/bin/env python3
"""
Get Actual NASDAQ Tickers - Fetch real NASDAQ symbols from Yahoo Finance
"""

import yfinance as yf
import pandas as pd
import time
import json
from pathlib import Path

def get_nasdaq_tickers():
    """Get actual NASDAQ tickers from Yahoo Finance"""
    print("FETCHING ACTUAL NASDAQ TICKERS")
    print("=" * 50)
    
    # Get NASDAQ tickers from Yahoo Finance
    try:
        print("Fetching NASDAQ tickers from Yahoo Finance...")
        
        # Method 1: Try to get NASDAQ tickers from yfinance
        nasdaq_tickers = []
        
        # Get some known NASDAQ tickers to start with
        known_nasdaq = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'ADBE', 'CRM',
            'PYPL', 'INTC', 'AMD', 'ORCL', 'CSCO', 'QCOM', 'TXN', 'AVGO', 'MU', 'ADP',
            'INTU', 'ISRG', 'REGN', 'VRTX', 'GILD', 'AMGN', 'BIIB', 'ILMN', 'MELI', 'JD',
            'BIDU', 'NTES', 'PDD', 'TME', 'NIO', 'XPEV', 'LI', 'BABA', 'TCEHY', 'JD',
            'PDD', 'BIDU', 'NTES', 'TME', 'NIO', 'XPEV', 'LI', 'BABA', 'TCEHY', 'JD'
        ]
        
        print(f"Testing {len(known_nasdaq)} known NASDAQ tickers...")
        
        for i, symbol in enumerate(known_nasdaq, 1):
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if info and isinstance(info, dict):
                    exchange = info.get('exchange', '').upper()
                    if exchange == 'NASDAQ':
                        nasdaq_tickers.append(symbol)
                        print(f"✅ {symbol}: NASDAQ confirmed")
                    else:
                        print(f"❌ {symbol}: {exchange} (not NASDAQ)")
                else:
                    print(f"⚠️ {symbol}: No info available")
                    
            except Exception as e:
                print(f"❌ {symbol}: Error - {e}")
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
            
            # Show progress
            if i % 10 == 0:
                print(f"Progress: {i}/{len(known_nasdaq)} ({len(nasdaq_tickers)} NASDAQ confirmed)")
        
        print(f"\nFound {len(nasdaq_tickers)} confirmed NASDAQ tickers")
        
        # Method 2: Try to get more NASDAQ tickers using a broader approach
        print("\nTrying to get more NASDAQ tickers...")
        
        # Common NASDAQ patterns
        additional_symbols = []
        
        # Generate some common NASDAQ symbol patterns
        for i in range(1000, 2000):  # Test some 4-letter symbols
            symbol = f"TEST{i}"
            additional_symbols.append(symbol)
        
        # Test a smaller sample
        test_symbols = additional_symbols[:100]
        
        for symbol in test_symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if info and isinstance(info, dict):
                    exchange = info.get('exchange', '').upper()
                    if exchange == 'NASDAQ':
                        nasdaq_tickers.append(symbol)
                        print(f"✅ {symbol}: NASDAQ found")
                        
            except Exception:
                pass
            
            time.sleep(0.05)  # Very small delay
        
        # Remove duplicates
        nasdaq_tickers = list(set(nasdaq_tickers))
        
        print(f"\nTotal unique NASDAQ tickers found: {len(nasdaq_tickers)}")
        
        # Save to file
        data = {
            'tickers': nasdaq_tickers,
            'count': len(nasdaq_tickers),
            'source': 'yfinance',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        output_file = Path('actual_nasdaq_tickers.json')
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved {len(nasdaq_tickers)} NASDAQ tickers to {output_file}")
        
        return nasdaq_tickers
        
    except Exception as e:
        print(f"Error fetching NASDAQ tickers: {e}")
        return []

def create_nasdaq_list():
    """Create a comprehensive NASDAQ list using multiple sources"""
    print("CREATING COMPREHENSIVE NASDAQ LIST")
    print("=" * 50)
    
    # Common NASDAQ tickers (manually curated)
    nasdaq_tickers = [
        # Major Tech Companies
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'ADBE', 'CRM',
        'PYPL', 'INTC', 'AMD', 'ORCL', 'CSCO', 'QCOM', 'TXN', 'AVGO', 'MU', 'ADP',
        'INTU', 'ISRG', 'REGN', 'VRTX', 'GILD', 'AMGN', 'BIIB', 'ILMN', 'MELI', 'JD',
        
        # Chinese Tech
        'BIDU', 'NTES', 'PDD', 'TME', 'NIO', 'XPEV', 'LI', 'BABA', 'TCEHY', 'JD',
        
        # Biotech
        'REGN', 'VRTX', 'GILD', 'AMGN', 'BIIB', 'ILMN', 'MRNA', 'BNTX', 'VRTX', 'REGN',
        
        # Software
        'ADBE', 'CRM', 'ORCL', 'INTU', 'ADP', 'MSFT', 'GOOGL', 'META', 'NFLX', 'TSLA',
        
        # Semiconductor
        'NVDA', 'AMD', 'INTC', 'QCOM', 'TXN', 'AVGO', 'MU', 'AMAT', 'KLAC', 'LRCX',
        
        # E-commerce
        'AMZN', 'EBAY', 'ETSY', 'SHOP', 'BABA', 'JD', 'PDD', 'MELI', 'SE', 'MELI',
        
        # Gaming
        'ATVI', 'EA', 'TTWO', 'ZNGA', 'NTDOY', 'U', 'RBLX', 'SKLZ', 'PLTK', 'GME',
        
        # Streaming
        'NFLX', 'DIS', 'CMCSA', 'PARA', 'WBD', 'ROKU', 'SPOT', 'PINS', 'SNAP', 'TWTR',
        
        # Cloud/SaaS
        'CRM', 'ADBE', 'ORCL', 'INTU', 'ADP', 'WDAY', 'NOW', 'TEAM', 'ZM', 'DOCU',
        
        # Electric Vehicles
        'TSLA', 'NIO', 'XPEV', 'LI', 'RIVN', 'LCID', 'FSR', 'NKLA', 'WKHS', 'IDEX',
        
        # Fintech
        'PYPL', 'SQ', 'COIN', 'AFRM', 'UPST', 'SOFI', 'LC', 'OPRT', 'LDI', 'RKT',
        
        # Healthcare Tech
        'TDOC', 'CERN', 'VEEV', 'DDOG', 'CRWD', 'OKTA', 'ZS', 'NET', 'PLTR', 'SNOW',
        
        # Renewable Energy
        'ENPH', 'SEDG', 'RUN', 'SPWR', 'FSLR', 'JKS', 'CSIQ', 'DQ', 'SOL', 'MAXN',
        
        # Cannabis
        'TLRY', 'CGC', 'ACB', 'APHA', 'CRON', 'HEXO', 'OGI', 'SNDL', 'CURLF', 'GTBIF',
        
        # Space
        'SPCE', 'RKLB', 'ASTS', 'VORB', 'ASTR', 'MNTS', 'BKSY', 'LUNR', 'RDW', 'SPIR',
        
        # Crypto Related
        'COIN', 'MSTR', 'RIOT', 'MARA', 'HUT', 'BITF', 'CLSK', 'ARBK', 'WULF', 'CORZ',
        
        # AI/ML
        'NVDA', 'AMD', 'INTC', 'GOOGL', 'MSFT', 'META', 'TSLA', 'PLTR', 'AI', 'PATH',
        
        # Cybersecurity
        'CRWD', 'OKTA', 'ZS', 'NET', 'PLTR', 'SNOW', 'DDOG', 'S', 'PANW', 'FTNT',
        
        # 3D Printing
        'DDD', 'SSYS', 'XONE', 'PRLB', 'DM', 'NNDM', 'XONE', 'SSYS', 'DDD', 'PRLB',
        
        # Robotics
        'IRBT', 'ROK', 'ABB', 'FANUC', 'YASKAWA', 'KUKA', 'ABB', 'ROK', 'IRBT', 'FANUC'
    ]
    
    # Remove duplicates
    nasdaq_tickers = list(set(nasdaq_tickers))
    
    print(f"Created list with {len(nasdaq_tickers)} unique NASDAQ tickers")
    
    # Save to file
    data = {
        'tickers': nasdaq_tickers,
        'count': len(nasdaq_tickers),
        'source': 'curated_list',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'note': 'This is a curated list of major NASDAQ tickers. Actual NASDAQ has ~3,300 stocks.'
    }
    
    output_file = Path('curated_nasdaq_tickers.json')
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Saved to {output_file}")
    
    return nasdaq_tickers

def main():
    """Main function"""
    print("NASDAQ TICKER FETCHER")
    print("=" * 50)
    
    # Try to get actual NASDAQ tickers
    print("Method 1: Fetching from Yahoo Finance...")
    actual_tickers = get_nasdaq_tickers()
    
    print("\nMethod 2: Creating curated list...")
    curated_tickers = create_nasdaq_list()
    
    print(f"\nRESULTS:")
    print(f"Actual tickers found: {len(actual_tickers)}")
    print(f"Curated tickers: {len(curated_tickers)}")
    print(f"Total unique: {len(set(actual_tickers + curated_tickers))}")
    
    print(f"\nNote: NASDAQ typically has around 3,300 stocks, not 5,380+")

if __name__ == "__main__":
    main()