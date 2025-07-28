#!/usr/bin/env python3
"""
Test Single Stock Data Retrieval
Quick test script to retrieve stock data for a few symbols without scheduler
"""

import os
import sys
import django
from pathlib import Path

# Setup Django environment
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')

# Set environment variables for correct MySQL configuration
os.environ['DB_ENGINE'] = 'django.db.backends.mysql'
os.environ['DB_NAME'] = 'stockscanner'
os.environ['DB_USER'] = 'root'
os.environ['DB_PASSWORD'] = ''
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '3306'

try:
    django.setup()
    print("SUCCESS: Django environment loaded successfully")
except Exception as e:
    print(f"ERROR: Failed to setup Django: {e}")
    sys.exit(1)

# Now import Django models
from stocks.models import Stock, StockPrice
from django.utils import timezone
import yfinance as yf
from decimal import Decimal

def test_single_stock(symbol="AAPL"):
    """Test retrieving data for a single stock symbol"""
    print(f"\n=== TESTING SINGLE STOCK RETRIEVAL: {symbol} ===")
    
    try:
        # Get stock data from Yahoo Finance
        print(f"📡 Fetching data for {symbol}...")
        ticker = yf.Ticker(symbol)
        
        # Get current info
        info = ticker.info
        if not info:
            print(f"❌ No data found for {symbol}")
            return False
            
        # Get current price
        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
        if not current_price:
            print(f"❌ No price data found for {symbol}")
            return False
            
        print(f"✅ Current Price: ${current_price}")
        print(f"✅ Company Name: {info.get('longName', 'N/A')}")
        print(f"✅ Market Cap: ${info.get('marketCap', 'N/A'):,}" if info.get('marketCap') else "✅ Market Cap: N/A")
        print(f"✅ Volume: {info.get('volume', 'N/A'):,}" if info.get('volume') else "✅ Volume: N/A")
        
        # Test database save (if you want to actually save)
        try:
            stock, created = Stock.objects.get_or_create(
                symbol=symbol,
                defaults={
                    'name': info.get('longName', symbol),
                    'sector': info.get('sector', 'Unknown'),
                    'industry': info.get('industry', 'Unknown'),
                    'market_cap': info.get('marketCap'),
                    'is_active': True
                }
            )
            
            if created:
                print(f"✅ Created new stock record for {symbol}")
            else:
                print(f"✅ Found existing stock record for {symbol}")
                
            # Create price record
            StockPrice.objects.create(
                stock=stock,
                price=Decimal(str(current_price)),
                volume=info.get('volume', 0),
                timestamp=timezone.now()
            )
            print(f"✅ Saved price data to database")
            
        except Exception as db_error:
            print(f"⚠️  Database save failed: {db_error}")
            print("💡 This is normal if database isn't set up yet")
            
        return True
        
    except Exception as e:
        print(f"❌ Error retrieving {symbol}: {e}")
        return False

def test_multiple_stocks(symbols=["AAPL", "GOOGL", "MSFT"]):
    """Test retrieving data for multiple stocks"""
    print(f"\n=== TESTING MULTIPLE STOCK RETRIEVAL ===")
    print(f"📊 Testing symbols: {', '.join(symbols)}")
    
    successful = 0
    failed = 0
    
    for symbol in symbols:
        if test_single_stock(symbol):
            successful += 1
        else:
            failed += 1
            
    print(f"\n📈 RESULTS:")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {(successful/(successful+failed)*100):.1f}%")

def main():
    print("🧪 STOCK DATA RETRIEVAL TEST")
    print("=" * 50)
    
    # Test single stock
    test_single_stock("AAPL")
    
    # Test multiple stocks
    test_multiple_stocks(["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"])
    
    print("\n🎯 TEST COMPLETE!")
    print("\nℹ️  To test with Django management command:")
    print("   python3 manage.py update_stocks_yfinance --symbols AAPL,GOOGL,MSFT --limit 3")
    print("   python3 manage.py update_stocks_yfinance --test-mode --limit 5")

if __name__ == "__main__":
    main()