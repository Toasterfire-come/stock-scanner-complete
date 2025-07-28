#!/usr/bin/env python3
"""
Test NASDAQ-Only Tickers (5,101+ stocks)
Test script specifically for NASDAQ-listed stocks from the complete dataset
"""

import os
import sys
import django
import csv
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
    print("INFO: Continuing with basic test...")

def load_nasdaq_only_tickers():
    """Load only NASDAQ-listed tickers from the complete dataset"""
    nasdaq_tickers = []
    csv_file = "data/complete_nasdaq/complete_nasdaq_export_20250724_182723.csv"
    
    if not os.path.exists(csv_file):
        print(f"WARNING: CSV file not found: {csv_file}")
        print("Using fallback ticker list...")
        return [
            "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META", "NFLX", 
            "ADBE", "CRM", "INTC", "AMD", "ORCL", "CSCO", "AVGO", "TXN", 
            "QCOM", "IBM", "UBER", "PYPL", "ZOOM", "SQ", "SHOP", "ROKU"
        ]
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Exchange', '').upper() == 'NASDAQ':
                    symbol = row.get('Symbol', '').strip()
                    if symbol and len(symbol) <= 5:  # Filter out weird symbols
                        nasdaq_tickers.append(symbol)
        
        print(f"SUCCESS: Loaded {len(nasdaq_tickers):,} NASDAQ-only tickers")
        return nasdaq_tickers
        
    except Exception as e:
        print(f"ERROR: Failed to load CSV: {e}")
        return []

# Load NASDAQ tickers
NASDAQ_ONLY_TICKERS = load_nasdaq_only_tickers()

import yfinance as yf
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from datetime import datetime

def test_nasdaq_sample(sample_size=100):
    """Test a sample of NASDAQ-only stocks"""
    print(f"\n=== TESTING NASDAQ-ONLY SAMPLE ({sample_size} stocks) ===")
    
    if not NASDAQ_ONLY_TICKERS:
        print("❌ No NASDAQ tickers loaded!")
        return 0, 0
    
    # Get sample of tickers
    sample_tickers = NASDAQ_ONLY_TICKERS[:sample_size]
    print(f"Testing first {len(sample_tickers)} NASDAQ tickers: {', '.join(sample_tickers[:10])}{'...' if len(sample_tickers) > 10 else ''}")
    
    successful = 0
    failed = 0
    start_time = time.time()
    
    for i, ticker in enumerate(sample_tickers, 1):
        try:
            print(f"({i}/{len(sample_tickers)}) Testing {ticker}...", end=" ")
            
            # Quick test
            yf_ticker = yf.Ticker(ticker)
            info = yf_ticker.info
            
            if info and (info.get('currentPrice') or info.get('regularMarketPrice')):
                price = info.get('currentPrice') or info.get('regularMarketPrice')
                print(f"✅ ${price}")
                successful += 1
            else:
                print("❌ No price")
                failed += 1
                
        except Exception as e:
            print(f"❌ {str(e)[:30]}...")
            failed += 1
            
        # Rate limiting
        time.sleep(0.1)
    
    elapsed = time.time() - start_time
    success_rate = (successful / (successful + failed)) * 100 if (successful + failed) > 0 else 0
    
    print(f"\n📊 NASDAQ-ONLY SAMPLE RESULTS:")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    print(f"⏱️  Time: {elapsed:.1f} seconds")
    print(f"🚀 Rate: {(successful + failed) / elapsed:.1f} stocks/second")
    
    return successful, failed

def test_nasdaq_multithreaded(sample_size=500, num_threads=15):
    """Test NASDAQ stocks with multithreading"""
    print(f"\n=== MULTITHREADED NASDAQ-ONLY TEST ===")
    print(f"📊 Sample Size: {sample_size}")
    print(f"🧵 Threads: {num_threads}")
    print(f"🎯 Exchange: NASDAQ ONLY")
    
    if not NASDAQ_ONLY_TICKERS:
        print("❌ No NASDAQ tickers loaded!")
        return 0, 0
    
    sample_tickers = NASDAQ_ONLY_TICKERS[:sample_size]
    successful = 0
    failed = 0
    processed = 0
    lock = threading.Lock()
    start_time = time.time()
    
    def update_counters(success):
        nonlocal successful, failed, processed
        with lock:
            processed += 1
            if success:
                successful += 1
            else:
                failed += 1
            
            # Progress update
            if processed % 25 == 0:
                elapsed = time.time() - start_time
                rate = processed / elapsed if elapsed > 0 else 0
                progress = processed / len(sample_tickers) * 100
                print(f"📈 Progress: {processed}/{len(sample_tickers)} ({progress:.1f}%) - {rate:.1f}/sec - Success: {(successful/processed*100):.1f}%")
    
    def test_ticker(ticker):
        try:
            time.sleep(0.05)  # Rate limiting
            yf_ticker = yf.Ticker(ticker)
            info = yf_ticker.info
            
            if info and (info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')):
                update_counters(True)
                return True
            else:
                update_counters(False)
                return False
                
        except Exception:
            update_counters(False)
            return False
    
    print(f"🚀 Starting test with {len(sample_tickers)} NASDAQ tickers...")
    
    # Execute with thread pool
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(test_ticker, ticker) for ticker in sample_tickers]
        
        # Wait for completion
        for future in as_completed(futures):
            future.result()
    
    elapsed = time.time() - start_time
    success_rate = (successful / (successful + failed)) * 100 if (successful + failed) > 0 else 0
    
    print(f"\n🎯 NASDAQ-ONLY MULTITHREADED RESULTS:")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    print(f"⏱️  Total Time: {elapsed:.1f} seconds")
    print(f"🚀 Average Rate: {processed / elapsed:.1f} stocks/second")
    print(f"💾 Data Retrieved: {successful} NASDAQ stocks")
    
    return successful, failed

def estimate_full_nasdaq_5101():
    """Estimate time needed for all 5,101+ NASDAQ stocks"""
    print(f"\n=== FULL 5,101+ NASDAQ ESTIMATION ===")
    
    total_nasdaq = len(NASDAQ_ONLY_TICKERS)
    print(f"📊 Total NASDAQ-Only Tickers Available: {total_nasdaq:,}")
    
    if total_nasdaq == 0:
        print("❌ No NASDAQ tickers loaded for estimation")
        return
    
    # Test small sample to estimate rate
    print("🧪 Running speed test with 30 NASDAQ tickers...")
    start_time = time.time()
    
    test_successful = 0
    test_count = min(30, len(NASDAQ_ONLY_TICKERS))
    
    for ticker in NASDAQ_ONLY_TICKERS[:test_count]:
        try:
            yf_ticker = yf.Ticker(ticker)
            info = yf_ticker.info
            if info and (info.get('currentPrice') or info.get('regularMarketPrice')):
                test_successful += 1
            time.sleep(0.05)  # Rate limiting
        except:
            pass
    
    test_time = time.time() - start_time
    rate = test_count / test_time
    
    # Estimate full dataset
    estimated_time_single = total_nasdaq / rate
    estimated_time_10_threads = estimated_time_single / 10
    estimated_time_20_threads = estimated_time_single / 20
    
    print(f"⚡ Test Rate: {rate:.1f} stocks/second")
    print(f"📈 Success Rate in Test: {(test_successful/test_count)*100:.1f}%")
    print()
    print(f"⏱️  ESTIMATED TIME FOR ALL {total_nasdaq:,} NASDAQ STOCKS:")
    print(f"   Single Thread: {estimated_time_single/60:.1f} minutes ({estimated_time_single/3600:.1f} hours)")
    print(f"   10 Threads: {estimated_time_10_threads/60:.1f} minutes")
    print(f"   20 Threads: {estimated_time_20_threads/60:.1f} minutes")
    print()
    print(f"💡 RECOMMENDED: Use 15-20 threads for optimal performance")

def show_nasdaq_django_commands():
    """Show Django management command examples for NASDAQ testing"""
    print(f"\n=== DJANGO COMMANDS FOR 5,101+ NASDAQ STOCKS ===")
    
    total_nasdaq = len(NASDAQ_ONLY_TICKERS)
    print(f"🎯 Available NASDAQ tickers: {total_nasdaq:,}")
    print()
    
    print("1️⃣  TEST MODE (NO DATABASE SAVE):")
    print("   python3 manage.py update_stocks_yfinance --nasdaq-only --limit 100 --test-mode")
    print("   python3 manage.py update_stocks_yfinance --nasdaq-only --limit 500 --test-mode --threads 10")
    print("   python3 manage.py update_stocks_yfinance --nasdaq-only --limit 1000 --test-mode --threads 15")
    print()
    
    print("2️⃣  PROGRESSIVE TESTING (SAVE TO DATABASE):")
    print("   python3 manage.py update_stocks_yfinance --nasdaq-only --limit 200 --threads 5")
    print("   python3 manage.py update_stocks_yfinance --nasdaq-only --limit 1000 --threads 10")
    print("   python3 manage.py update_stocks_yfinance --nasdaq-only --limit 2500 --threads 15")
    print()
    
    print("3️⃣  FULL NASDAQ DATASET:")
    print(f"   python3 manage.py update_stocks_yfinance --nasdaq-only --limit {total_nasdaq} --threads 20")
    print(f"   python3 manage.py update_stocks_yfinance --nasdaq-only --limit {total_nasdaq} --threads 25 --verbose")
    print()
    
    print("4️⃣  CHUNKED PROCESSING (RECOMMENDED FOR 5K+ STOCKS):")
    print("   python3 manage.py update_stocks_yfinance --nasdaq-only --limit 1000 --threads 15")
    print("   python3 manage.py update_stocks_yfinance --nasdaq-only --limit 2000 --threads 15")
    print("   python3 manage.py update_stocks_yfinance --nasdaq-only --limit 3000 --threads 15")
    print("   python3 manage.py update_stocks_yfinance --nasdaq-only --limit 5000 --threads 20")
    print()
    
    print("⚠️  PERFORMANCE NOTES:")
    print("   - --nasdaq-only flag filters to NASDAQ exchange only")
    print("   - Use --test-mode first to verify API connectivity")
    print("   - 15-20 threads optimal for 5K+ stocks")
    print("   - Add --verbose for detailed progress logging")
    print("   - Consider chunking large datasets for stability")

def main():
    print("📈 NASDAQ-ONLY DATASET TEST (5,101+ STOCKS)")
    print("=" * 70)
    
    if not NASDAQ_ONLY_TICKERS:
        print("❌ Failed to load NASDAQ ticker data!")
        print("💡 Make sure data/complete_nasdaq/complete_nasdaq_export_20250724_182723.csv exists")
        return
    
    print(f"📊 Loaded NASDAQ Tickers: {len(NASDAQ_ONLY_TICKERS):,}")
    print(f"🎯 Ready to test NASDAQ-only stocks")
    print()
    
    while True:
        print("\n🎯 CHOOSE NASDAQ TEST TYPE:")
        print("1️⃣  Quick NASDAQ Sample (100 stocks)")
        print("2️⃣  Medium NASDAQ Sample (500 stocks)")
        print("3️⃣  Large NASDAQ Sample (1000 stocks)")
        print("4️⃣  Multithreaded NASDAQ Test (500 stocks, 15 threads)")
        print("5️⃣  Large Multithreaded Test (1500 stocks, 20 threads)")
        print("6️⃣  Speed Estimation for Full 5,101+ NASDAQ")
        print("7️⃣  Show Django Command Examples")
        print("8️⃣  Exit")
        
        choice = input("\nEnter choice (1-8): ").strip()
        
        if choice == "1":
            test_nasdaq_sample(100)
        elif choice == "2":
            test_nasdaq_sample(500)
        elif choice == "3":
            test_nasdaq_sample(1000)
        elif choice == "4":
            test_nasdaq_multithreaded(500, 15)
        elif choice == "5":
            test_nasdaq_multithreaded(1500, 20)
        elif choice == "6":
            estimate_full_nasdaq_5101()
        elif choice == "7":
            show_nasdaq_django_commands()
        elif choice == "8":
            print("👋 Exiting...")
            break
        else:
            print("❌ Invalid choice, please enter 1-8")

if __name__ == "__main__":
    main()