#!/usr/bin/env python3
"""
Test NASDAQ Full Dataset Retrieval
Test script to retrieve stock data for the complete NASDAQ dataset (11,658+ tickers)
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
    print("INFO: Continuing with basic test...")

# Import the NASDAQ ticker list
try:
    sys.path.append('data/complete_nasdaq')
    from complete_nasdaq_tickers_20250724_182723 import COMPLETE_NASDAQ_TICKERS
    print(f"SUCCESS: Loaded {len(COMPLETE_NASDAQ_TICKERS):,} NASDAQ tickers")
except ImportError:
    print("WARNING: Could not load NASDAQ ticker list, using fallback")
    COMPLETE_NASDAQ_TICKERS = [
        "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META", "NFLX", "ADBE", "CRM",
        "INTC", "AMD", "ORCL", "CSCO", "AVGO", "TXN", "QCOM", "IBM", "UBER", "PYPL"
    ]

import yfinance as yf
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from datetime import datetime

def test_nasdaq_sample(sample_size=50):
    """Test a sample of NASDAQ stocks"""
    print(f"\n=== TESTING NASDAQ SAMPLE ({sample_size} stocks) ===")
    
    # Get sample of tickers
    sample_tickers = COMPLETE_NASDAQ_TICKERS[:sample_size]
    print(f"Testing first {len(sample_tickers)} tickers: {', '.join(sample_tickers[:10])}{'...' if len(sample_tickers) > 10 else ''}")
    
    successful = 0
    failed = 0
    start_time = time.time()
    
    for i, ticker in enumerate(sample_tickers, 1):
        try:
            print(f"({i}/{len(sample_tickers)}) Testing {ticker}...", end=" ")
            
            # Quick test
            yf_ticker = yf.Ticker(ticker)
            info = yf_ticker.info
            
            if info and info.get('currentPrice'):
                price = info.get('currentPrice')
                print(f"OK - ${price}")
                successful += 1
            else:
                print("FAILED - No price data")
                failed += 1
                
        except Exception as e:
            print(f"ERROR - {e}")
            failed += 1
            
        # Rate limiting
        time.sleep(0.1)
    
    elapsed = time.time() - start_time
    success_rate = (successful / (successful + failed)) * 100 if (successful + failed) > 0 else 0
    
    print(f"\n📊 SAMPLE TEST RESULTS:")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    print(f"⏱️  Time: {elapsed:.1f} seconds")
    print(f"🚀 Rate: {(successful + failed) / elapsed:.1f} stocks/second")
    
    return successful, failed

def test_nasdaq_multithreaded(sample_size=100, num_threads=10):
    """Test NASDAQ stocks with multithreading"""
    print(f"\n=== MULTITHREADED NASDAQ TEST ===")
    print(f"📊 Sample Size: {sample_size}")
    print(f"🧵 Threads: {num_threads}")
    
    sample_tickers = COMPLETE_NASDAQ_TICKERS[:sample_size]
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
            if processed % 10 == 0:
                elapsed = time.time() - start_time
                rate = processed / elapsed if elapsed > 0 else 0
                print(f"Progress: {processed}/{len(sample_tickers)} ({processed/len(sample_tickers)*100:.1f}%) - {rate:.1f}/sec")
    
    def test_ticker(ticker):
        try:
            time.sleep(0.05)  # Rate limiting
            yf_ticker = yf.Ticker(ticker)
            info = yf_ticker.info
            
            if info and (info.get('currentPrice') or info.get('regularMarketPrice')):
                update_counters(True)
                return True
            else:
                update_counters(False)
                return False
                
        except Exception:
            update_counters(False)
            return False
    
    # Execute with thread pool
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(test_ticker, ticker) for ticker in sample_tickers]
        
        # Wait for completion
        for future in as_completed(futures):
            future.result()
    
    elapsed = time.time() - start_time
    success_rate = (successful / (successful + failed)) * 100 if (successful + failed) > 0 else 0
    
    print(f"\n🎯 MULTITHREADED TEST RESULTS:")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    print(f"⏱️  Total Time: {elapsed:.1f} seconds")
    print(f"🚀 Average Rate: {processed / elapsed:.1f} stocks/second")
    
    return successful, failed

def estimate_full_nasdaq_time():
    """Estimate time needed for full NASDAQ dataset"""
    print(f"\n=== FULL NASDAQ ESTIMATION ===")
    
    total_tickers = len(COMPLETE_NASDAQ_TICKERS)
    print(f"📊 Total NASDAQ Tickers: {total_tickers:,}")
    
    # Test small sample to estimate rate
    print("🧪 Running speed test with 20 tickers...")
    start_time = time.time()
    
    test_successful = 0
    for ticker in COMPLETE_NASDAQ_TICKERS[:20]:
        try:
            yf_ticker = yf.Ticker(ticker)
            info = yf_ticker.info
            if info:
                test_successful += 1
            time.sleep(0.05)  # Rate limiting
        except:
            pass
    
    test_time = time.time() - start_time
    rate = 20 / test_time
    
    # Estimate full dataset
    estimated_time_single = total_tickers / rate
    estimated_time_multi = estimated_time_single / 10  # Assume 10 threads
    
    print(f"⚡ Test Rate: {rate:.1f} stocks/second")
    print(f"⏱️  Estimated Time (Single Thread): {estimated_time_single/60:.1f} minutes")
    print(f"⏱️  Estimated Time (10 Threads): {estimated_time_multi/60:.1f} minutes")
    print(f"📈 Success Rate in Test: {(test_successful/20)*100:.1f}%")

def run_django_command_examples():
    """Show Django management command examples for NASDAQ testing"""
    print(f"\n=== DJANGO MANAGEMENT COMMAND EXAMPLES ===")
    print("🎯 Here are the recommended commands to test with NASDAQ data:")
    print()
    
    print("1️⃣  TEST MODE (NO DATABASE SAVE):")
    print("   python3 manage.py update_stocks_yfinance --limit 100 --test-mode --verbose")
    print("   python3 manage.py update_stocks_yfinance --limit 500 --test-mode --threads 10")
    print()
    
    print("2️⃣  SMALL BATCHES (SAVE TO DATABASE):")
    print("   python3 manage.py update_stocks_yfinance --limit 50")
    print("   python3 manage.py update_stocks_yfinance --limit 200 --threads 5")
    print()
    
    print("3️⃣  MEDIUM BATCHES:")
    print("   python3 manage.py update_stocks_yfinance --limit 1000 --threads 10")
    print("   python3 manage.py update_stocks_yfinance --limit 2000 --threads 15")
    print()
    
    print("4️⃣  FULL NASDAQ (3500+ DEFAULT):")
    print("   python3 manage.py update_stocks_yfinance --limit 3500 --threads 20")
    print("   python3 manage.py update_stocks_yfinance --nasdaq-only --threads 15")
    print()
    
    print("5️⃣  VERY LARGE BATCHES:")
    print("   python3 manage.py update_stocks_yfinance --limit 5000 --threads 25")
    print("   python3 manage.py update_stocks_yfinance --limit 10000 --threads 30")
    print()
    
    print("⚠️  NOTES:")
    print("   - Start with --test-mode to verify API connectivity")
    print("   - Use --threads 10-30 for faster processing")
    print("   - Default limit is 3500 (good for most use cases)")
    print("   - Add --verbose for detailed progress logging")

def main():
    print("📈 NASDAQ FULL DATASET TEST")
    print("=" * 60)
    print(f"📊 Available NASDAQ Tickers: {len(COMPLETE_NASDAQ_TICKERS):,}")
    print(f"🎯 Ready to test with full dataset")
    print()
    
    while True:
        print("\n🎯 CHOOSE TEST TYPE:")
        print("1️⃣  Quick Sample Test (50 stocks)")
        print("2️⃣  Medium Sample Test (200 stocks)")
        print("3️⃣  Large Sample Test (500 stocks)")
        print("4️⃣  Multithreaded Test (100 stocks, 10 threads)")
        print("5️⃣  Speed Estimation for Full NASDAQ")
        print("6️⃣  Show Django Command Examples")
        print("7️⃣  Exit")
        
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice == "1":
            test_nasdaq_sample(50)
        elif choice == "2":
            test_nasdaq_sample(200)
        elif choice == "3":
            test_nasdaq_sample(500)
        elif choice == "4":
            test_nasdaq_multithreaded(100, 10)
        elif choice == "5":
            estimate_full_nasdaq_time()
        elif choice == "6":
            run_django_command_examples()
        elif choice == "7":
            print("👋 Exiting...")
            break
        else:
            print("❌ Invalid choice, please enter 1-7")

if __name__ == "__main__":
    main()