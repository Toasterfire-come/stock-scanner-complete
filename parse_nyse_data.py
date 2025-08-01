#!/usr/bin/env python3
"""
Parse NYSE Data - Extract tickers from otherlisted.txt
"""

import json
from pathlib import Path

def parse_nyse_data():
    """Parse NYSE data from otherlisted.txt"""
    print("PARSING NYSE DATA")
    print("=" * 50)
    
    # Read the NYSE data file
    nyse_file = Path('data/complete_nasdaq/otherlisted.txt')
    
    if not nyse_file.exists():
        print(f"❌ NYSE file not found: {nyse_file}")
        return []
    
    nyse_tickers = []
    etf_tickers = []
    
    print(f"Reading NYSE data from: {nyse_file}")
    
    with open(nyse_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total lines: {len(lines)}")
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('ACT Symbol'):
            continue  # Skip header and empty lines
        
        # Parse the pipe-separated format
        parts = line.split('|')
        if len(parts) >= 8:
            symbol = parts[0].strip()
            security_name = parts[1].strip()
            exchange = parts[2].strip()
            etf_flag = parts[4].strip()
            
            # Filter out test issues and invalid symbols
            if symbol and len(symbol) <= 5 and not symbol.endswith('.U') and not symbol.endswith('.W'):
                if etf_flag == 'Y':
                    etf_tickers.append({
                        'symbol': symbol,
                        'name': security_name,
                        'exchange': exchange
                    })
                else:
                    nyse_tickers.append({
                        'symbol': symbol,
                        'name': security_name,
                        'exchange': exchange
                    })
    
    print(f"NYSE Stocks: {len(nyse_tickers)}")
    print(f"NYSE ETFs: {len(etf_tickers)}")
    print(f"Total NYSE: {len(nyse_tickers) + len(etf_tickers)}")
    
    # Save NYSE stocks
    nyse_stocks_data = {
        'tickers': [t['symbol'] for t in nyse_tickers],
        'count': len(nyse_tickers),
        'source': 'nyse_otherlisted',
        'timestamp': '2025-01-27 12:00:00',
        'note': 'NYSE stocks extracted from otherlisted.txt'
    }
    
    with open('nyse_stocks.json', 'w') as f:
        json.dump(nyse_stocks_data, f, indent=2)
    
    # Save NYSE ETFs
    nyse_etfs_data = {
        'tickers': [t['symbol'] for t in etf_tickers],
        'count': len(etf_tickers),
        'source': 'nyse_otherlisted',
        'timestamp': '2025-01-27 12:00:00',
        'note': 'NYSE ETFs extracted from otherlisted.txt'
    }
    
    with open('nyse_etfs.json', 'w') as f:
        json.dump(nyse_etfs_data, f, indent=2)
    
    # Save combined NYSE data
    combined_data = {
        'tickers': [t['symbol'] for t in nyse_tickers + etf_tickers],
        'count': len(nyse_tickers) + len(etf_tickers),
        'source': 'nyse_otherlisted',
        'timestamp': '2025-01-27 12:00:00',
        'note': 'Combined NYSE stocks and ETFs from otherlisted.txt',
        'breakdown': {
            'stocks': len(nyse_tickers),
            'etfs': len(etf_tickers)
        }
    }
    
    with open('nyse_combined.json', 'w') as f:
        json.dump(combined_data, f, indent=2)
    
    print(f"\nSaved files:")
    print(f"  - nyse_stocks.json ({len(nyse_tickers)} stocks)")
    print(f"  - nyse_etfs.json ({len(etf_tickers)} ETFs)")
    print(f"  - nyse_combined.json ({len(nyse_tickers) + len(etf_tickers)} total)")
    
    # Show first 20 NYSE stocks
    print(f"\nFirst 20 NYSE stocks:")
    for i, ticker in enumerate(nyse_tickers[:20]):
        print(f"  {i+1:2d}. {ticker['symbol']} - {ticker['name']}")
    
    return nyse_tickers + etf_tickers

def main():
    """Main function"""
    tickers = parse_nyse_data()
    print(f"\n✅ Successfully parsed {len(tickers)} NYSE tickers")

if __name__ == "__main__":
    main()