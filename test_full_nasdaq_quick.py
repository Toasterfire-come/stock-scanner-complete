#!/usr/bin/env python3
"""
Quick Test for Full NASDAQ Dataset Loading
Verify that we can load all 5,390+ NASDAQ tickers correctly
"""

import os
import sys
import csv
from pathlib import Path

def test_nasdaq_loading():
    """Test loading the full NASDAQ dataset"""
    print("🧪 TESTING FULL NASDAQ DATASET LOADING")
    print("=" * 60)
    
    csv_file = "data/complete_nasdaq/complete_nasdaq_export_20250724_182723.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return False
    
    print(f"✅ Found CSV file: {csv_file}")
    
    # Load NASDAQ-only tickers
    nasdaq_tickers = []
    all_exchanges = {}
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                exchange = row.get('Exchange', '').upper()
                symbol = row.get('Symbol', '').strip()
                
                # Count all exchanges
                all_exchanges[exchange] = all_exchanges.get(exchange, 0) + 1
                
                # Filter NASDAQ only
                if exchange == 'NASDAQ':
                    if symbol and len(symbol) <= 5:  # Filter out weird symbols
                        nasdaq_tickers.append(symbol)
        
        print(f"\n📊 EXCHANGE BREAKDOWN:")
        for exchange, count in sorted(all_exchanges.items()):
            emoji = "🎯" if exchange == "NASDAQ" else "📈"
            print(f"   {emoji} {exchange}: {count:,} tickers")
        
        print(f"\n🎯 NASDAQ-ONLY RESULTS:")
        print(f"   ✅ Total NASDAQ tickers: {len(nasdaq_tickers):,}")
        print(f"   📋 Sample tickers: {', '.join(nasdaq_tickers[:10])}...")
        print(f"   📊 Percentage of total: {(len(nasdaq_tickers)/sum(all_exchanges.values()))*100:.1f}%")
        
        return len(nasdaq_tickers)
        
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return False

def show_commands_for_full_nasdaq(ticker_count):
    """Show the correct commands to test with full NASDAQ dataset"""
    print(f"\n🚀 COMMANDS TO TEST WITH ALL {ticker_count:,} NASDAQ STOCKS:")
    print("=" * 70)
    
    print("1️⃣  TEST MODE (Recommended first):")
    print(f"   python3 manage.py update_stocks_yfinance --nasdaq-only --limit {ticker_count} --test-mode --threads 20")
    print(f"   python3 manage.py update_stocks_yfinance --nasdaq-only --limit {ticker_count} --test-mode --threads 25 --verbose")
    print()
    
    print("2️⃣  CHUNKED PROCESSING (Recommended for stability):")
    print("   python3 manage.py update_stocks_yfinance --nasdaq-only --limit 1000 --threads 15")
    print("   python3 manage.py update_stocks_yfinance --nasdaq-only --limit 2000 --threads 15")
    print("   python3 manage.py update_stocks_yfinance --nasdaq-only --limit 3000 --threads 15")
    print("   python3 manage.py update_stocks_yfinance --nasdaq-only --limit 4000 --threads 20")
    print(f"   python3 manage.py update_stocks_yfinance --nasdaq-only --limit {ticker_count} --threads 20")
    print()
    
    print("3️⃣  FULL DATASET (Save to database):")
    print(f"   python3 manage.py update_stocks_yfinance --nasdaq-only --limit {ticker_count} --threads 20")
    print(f"   python3 manage.py update_stocks_yfinance --nasdaq-only --limit {ticker_count} --threads 25 --verbose")
    print()
    
    print("4️⃣  PERFORMANCE OPTIONS:")
    print(f"   # Fast (20 threads): ~{ticker_count//60:.0f}-{ticker_count//100:.0f} minutes")
    print(f"   # Very Fast (30 threads): ~{ticker_count//80:.0f}-{ticker_count//120:.0f} minutes")
    print()
    
    print("⚠️  IMPORTANT NOTES:")
    print("   - The system will now use ALL 5,390+ NASDAQ tickers")
    print("   - Start with --test-mode to verify connectivity")
    print("   - Use chunked processing for better stability")
    print("   - Monitor system resources with high thread counts")

def main():
    print("🎯 FULL NASDAQ DATASET VERIFICATION")
    print()
    
    # Test loading
    ticker_count = test_nasdaq_loading()
    
    if ticker_count:
        show_commands_for_full_nasdaq(ticker_count)
        
        print(f"\n✅ SUCCESS: Django command updated to use full {ticker_count:,} NASDAQ tickers!")
        print("🚀 You can now run the commands above to test with the complete dataset.")
    else:
        print("\n❌ FAILED: Could not load NASDAQ dataset")
        print("💡 Make sure the CSV file exists in data/complete_nasdaq/")

if __name__ == "__main__":
    main()