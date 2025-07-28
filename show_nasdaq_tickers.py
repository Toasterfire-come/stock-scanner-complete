#!/usr/bin/env python3
"""
Show NASDAQ Ticker List (No Database Required)
Display all 5,380 NASDAQ ticker symbols available for updating
"""

import csv
import os
from pathlib import Path

def show_nasdaq_tickers():
    """Show all available NASDAQ ticker symbols"""
    print("🎯 NASDAQ TICKER LIST (NO DATABASE REQUIRED)")
    print("=" * 70)
    
    csv_file = "data/complete_nasdaq/complete_nasdaq_export_20250724_182723.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return False
    
    print(f"✅ Loading from: {csv_file}")
    
    # Load NASDAQ-only tickers
    nasdaq_tickers = []
    all_exchanges = {}
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                exchange = row.get('Exchange', '').upper()
                symbol = row.get('Symbol', '').strip()
                name = row.get('Name', '').strip()
                
                # Count all exchanges
                all_exchanges[exchange] = all_exchanges.get(exchange, 0) + 1
                
                # Collect NASDAQ only
                if exchange == 'NASDAQ':
                    if symbol and len(symbol) <= 5:  # Filter out weird symbols
                        nasdaq_tickers.append({
                            'symbol': symbol,
                            'name': name,
                            'exchange': exchange
                        })
        
        print(f"\n📊 EXCHANGE BREAKDOWN:")
        for exchange, count in sorted(all_exchanges.items()):
            emoji = "🎯" if exchange == "NASDAQ" else "📈"
            print(f"   {emoji} {exchange}: {count:,} tickers")
        
        print(f"\n🎯 NASDAQ TICKER LIST READY:")
        print(f"   ✅ Total NASDAQ tickers: {len(nasdaq_tickers):,}")
        print(f"   📋 First 20 tickers: {', '.join([t['symbol'] for t in nasdaq_tickers[:20]])}")
        print(f"   📋 Sample companies: {nasdaq_tickers[0]['name']}, {nasdaq_tickers[1]['name']}")
        
        return len(nasdaq_tickers)
        
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return False

def show_database_commands():
    """Show commands to set up database and load tickers"""
    print(f"\n🚀 COMMANDS TO UPDATE NASDAQ TICKER LIST:")
    print("=" * 70)
    
    print("1️⃣  START MYSQL (if not running):")
    print("   # On Linux:")
    print("   sudo systemctl start mysql")
    print("   sudo systemctl status mysql")
    print()
    print("   # Or check if MySQL is running:")
    print("   ps aux | grep mysql")
    print()
    
    print("2️⃣  CREATE DATABASE (if needed):")
    print("   mysql -u root -p -e \"CREATE DATABASE IF NOT EXISTS stockscanner;\"")
    print("   mysql -u root -p -e \"SHOW DATABASES;\"")
    print()
    
    print("3️⃣  RUN DJANGO MIGRATIONS:")
    print("   python3 manage.py makemigrations")
    print("   python3 manage.py migrate")
    print()
    
    print("4️⃣  LOAD ALL NASDAQ TICKERS INTO DATABASE:")
    print("   python3 manage.py load_nasdaq_tickers --update-existing")
    print()
    
    print("5️⃣  UPDATE STOCK DATA FOR ALL NASDAQ TICKERS:")
    print("   python3 manage.py update_stocks_yfinance --nasdaq-only --limit 5380 --threads 20")
    print()
    
    print("6️⃣  TEST WITH SMALLER BATCH FIRST:")
    print("   python3 manage.py update_stocks_yfinance --nasdaq-only --limit 100 --test-mode")
    print("   python3 manage.py update_stocks_yfinance --nasdaq-only --limit 500 --threads 10")

def show_mysql_troubleshooting():
    """Show MySQL troubleshooting commands"""
    print(f"\n🔧 MYSQL TROUBLESHOOTING:")
    print("=" * 70)
    
    print("💡 CHECK MYSQL STATUS:")
    print("   sudo systemctl status mysql")
    print("   ps aux | grep mysql")
    print("   netstat -tlnp | grep 3306")
    print()
    
    print("💡 START MYSQL:")
    print("   sudo systemctl start mysql")
    print("   sudo systemctl enable mysql  # Auto-start on boot")
    print()
    
    print("💡 INSTALL MYSQL (if not installed):")
    print("   sudo apt update")
    print("   sudo apt install mysql-server")
    print("   sudo mysql_secure_installation")
    print()
    
    print("💡 CHECK MYSQL CONNECTION:")
    print("   mysql -u root -p")
    print("   mysql -u root -p -e \"SELECT VERSION();\"")

def main():
    print("🎯 NASDAQ TICKER LIST STATUS")
    print()
    
    # Show ticker count
    ticker_count = show_nasdaq_tickers()
    
    if ticker_count:
        print(f"\n✅ SUCCESS: {ticker_count:,} NASDAQ tickers ready for loading!")
        show_database_commands()
        show_mysql_troubleshooting()
        
        print(f"\n🎯 SUMMARY:")
        print(f"   📊 NASDAQ tickers available: {ticker_count:,}")
        print(f"   💾 Database required: MySQL")
        print(f"   🚀 Ready to process once MySQL is running")
        
    else:
        print("\n❌ FAILED: Could not load NASDAQ ticker list")

if __name__ == "__main__":
    main()