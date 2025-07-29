#!/usr/bin/env python3
"""
Standalone Stock Scanner Test
Tests the stock scanner functionality without database requirements
Exports results as JSON
"""

import yfinance as yf
import time
import random
import json
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading

class StandaloneStockScanner:
    def __init__(self, test_symbols=None):
        self.test_symbols = test_symbols or [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 
            'META', 'NVDA', 'NFLX', 'AMD', 'INTC',
            'AAPGV', 'ABST', 'ACHL', 'ACST', 'ADAL'  # Some potentially problematic ones
        ]
        self.results = {
            'start_time': datetime.now().isoformat(),
            'symbols_processed': 0,
            'successful': 0,
            'failed': 0,
            'timeouts': 0,
            'delisted': 0,
            'errors': 0,
            'stock_data': [],
            'processing_times': [],
            'errors_list': []
        }
        self.lock = threading.Lock()
        
    def test_yfinance_connectivity(self):
        """Test yfinance API connectivity"""
        try:
            test_ticker = yf.Ticker("AAPL")
            test_info = test_ticker.info
            if test_info:
                print("[SUCCESS] yfinance connectivity test passed")
                return True
            else:
                print("[WARNING] yfinance connectivity test failed")
                return False
        except Exception as e:
            print(f"[ERROR] yfinance connectivity error: {e}")
            return False
    
    def process_symbol(self, symbol, timeout=15):
        """Process a single symbol with timeout"""
        start_time = time.time()
        
        try:
            # Add minimal delay
            time.sleep(random.uniform(0.1, 0.3))
            
            # Get stock data
            ticker_obj = yf.Ticker(symbol)
            info = ticker_obj.info
            hist = ticker_obj.history(period="5d")
            
            processing_time = time.time() - start_time
            
            if hist.empty or not info:
                with self.lock:
                    self.results['delisted'] += 1
                    self.results['errors_list'].append({
                        'symbol': symbol,
                        'error': 'No data found, possibly delisted',
                        'processing_time': processing_time
                    })
                print(f"[DELISTED] {symbol}: No data found")
                return False
            
            # Extract key data
            current_price = hist['Close'].iloc[-1] if len(hist) > 0 else None
            if current_price is None or str(current_price) == 'nan':
                with self.lock:
                    self.results['delisted'] += 1
                    self.results['errors_list'].append({
                        'symbol': symbol,
                        'error': 'No price data available',
                        'processing_time': processing_time
                    })
                print(f"[DELISTED] {symbol}: No price data")
                return False
            
            # Calculate price changes
            price_change_today = None
            change_percent = None
            if len(hist) > 1:
                prev_price = hist['Close'].iloc[-2]
                if not str(prev_price) == 'nan' and prev_price > 0:
                    price_change_today = current_price - prev_price
                    change_percent = (price_change_today / prev_price) * 100
            
            # Create stock data object
            stock_data = {
                'symbol': symbol,
                'company_name': info.get('longName') or info.get('shortName', ''),
                'current_price': float(current_price) if current_price else None,
                'price_change_today': float(price_change_today) if price_change_today else None,
                'change_percent': float(change_percent) if change_percent else None,
                'volume': info.get('volume'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'exchange': info.get('exchange', 'NASDAQ'),
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat()
            }
            
            with self.lock:
                self.results['successful'] += 1
                self.results['stock_data'].append(stock_data)
                self.results['processing_times'].append(processing_time)
            
            change_str = f"{change_percent:+.2f}%" if change_percent else "N/A"
            print(f"[SUCCESS] {symbol}: ${current_price:.2f} ({change_str}) - {processing_time:.2f}s")
            return True
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = str(e).lower()
            
            with self.lock:
                self.results['failed'] += 1
                self.results['errors_list'].append({
                    'symbol': symbol,
                    'error': str(e),
                    'processing_time': processing_time
                })
            
            if 'timeout' in error_msg or 'timed out' in error_msg:
                self.results['timeouts'] += 1
                print(f"[TIMEOUT] {symbol}: Timed out after {processing_time:.2f}s")
            elif any(x in error_msg for x in ['no data found', 'delisted', '404', 'not found']):
                self.results['delisted'] += 1
                print(f"[DELISTED] {symbol}: {e}")
            else:
                self.results['errors'] += 1
                print(f"[ERROR] {symbol}: {e}")
            
            return False
    
    def process_symbol_with_timeout(self, symbol, timeout=15):
        """Process symbol with timeout using ThreadPoolExecutor"""
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self.process_symbol, symbol, timeout)
                return future.result(timeout=timeout)
        except Exception as e:
            with self.lock:
                self.results['timeouts'] += 1
                self.results['errors_list'].append({
                    'symbol': symbol,
                    'error': f'Timeout error: {e}',
                    'processing_time': timeout
                })
            print(f"[TIMEOUT] {symbol} timed out after {timeout}s")
            return False
    
    def run_test(self, limit=None):
        """Run the stock scanner test"""
        print("=" * 70)
        print("[TEST] STANDALONE STOCK SCANNER TEST")
        print("=" * 70)
        
        # Test connectivity
        if not self.test_yfinance_connectivity():
            print("[ERROR] Cannot proceed without yfinance connectivity")
            return
        
        symbols = self.test_symbols[:limit] if limit else self.test_symbols
        total_symbols = len(symbols)
        
        print(f"[SETTINGS] Testing {total_symbols} symbols")
        print(f"[SETTINGS] Timeout: 15s per symbol")
        print(f"[SETTINGS] Test mode: ON")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Progress tracking
        progress = {'current': 0}
        stop_flag = threading.Event()
        
        def print_progress():
            while not stop_flag.is_set():
                try:
                    percent = (progress['current'] / total_symbols) * 100
                    elapsed = time.time() - start_time
                    print(f"[PROGRESS] {progress['current']}/{total_symbols} ({percent:.1f}%) - {elapsed:.1f}s elapsed")
                    stop_flag.wait(5)
                except Exception as e:
                    print(f"[PROGRESS ERROR] {e}")
                    break
        
        start_time = time.time()
        progress_thread = threading.Thread(target=print_progress, daemon=True)
        progress_thread.start()
        
        print(f"[READY] Starting to process {total_symbols} symbols...")
        print(f"[FIRST] First 5 symbols: {', '.join(symbols[:5])}")
        print()
        
        try:
            for i, symbol in enumerate(symbols, 1):
                try:
                    if i <= 5:
                        print(f"[PROCESSING] {i}/{total_symbols}: {symbol}")
                    
                    print(f"[DEBUG] Before processing {symbol}")
                    result = self.process_symbol_with_timeout(symbol, timeout=15)
                    print(f"[DEBUG] After processing {symbol} - Result: {result}")
                    
                    progress['current'] = i
                    self.results['symbols_processed'] = i
                    
                    # Show progress every 5 tickers
                    if i % 5 == 0 or i == total_symbols:
                        progress_percent = (i / total_symbols) * 100
                        elapsed = time.time() - start_time
                        print(f"[STATS] Progress: {i}/{total_symbols} ({progress_percent:.1f}%) - {elapsed:.1f}s elapsed")
                        
                except Exception as e:
                    print(f"[LOOP ERROR] Error processing symbol {symbol} (iteration {i}): {e}")
                    continue
                    
        except KeyboardInterrupt:
            print("\n[STOP] Keyboard interrupt detected. Stopping gracefully...")
            print(f"[STOP] Processed {progress['current']} out of {total_symbols} symbols")
            stop_flag.set()
            if progress_thread.is_alive():
                progress_thread.join(timeout=2)
        
        stop_flag.set()
        if progress_thread.is_alive():
            progress_thread.join(timeout=2)
        
        # Calculate final statistics
        total_time = time.time() - start_time
        self.results['end_time'] = datetime.now().isoformat()
        self.results['total_duration'] = total_time
        self.results['average_processing_time'] = sum(self.results['processing_times']) / len(self.results['processing_times']) if self.results['processing_times'] else 0
        self.results['success_rate'] = (self.results['successful'] / self.results['symbols_processed']) * 100 if self.results['symbols_processed'] > 0 else 0
        self.results['stocks_per_minute'] = (self.results['symbols_processed'] / total_time) * 60 if total_time > 0 else 0
        
        # Display final results
        self.display_final_results()
        
        # Export to JSON
        self.export_to_json()
        
        return self.results
    
    def display_final_results(self):
        """Display comprehensive final results"""
        results = self.results
        duration = results['total_duration']
        success_rate = results['success_rate']
        
        print("\n" + "="*70)
        print("[STATS] TEST COMPLETED")
        print("="*70)
        print(f"[SUCCESS] Successful: {results['successful']}")
        print(f"[ERROR] Failed: {results['failed']}")
        print(f"[DELISTED] Delisted: {results['delisted']}")
        print(f"[TIMEOUT] Timeouts: {results['timeouts']}")
        print(f"[UP] Total processed: {results['symbols_processed']}")
        print(f"[STATS] Success rate: {success_rate:.1f}%")
        print(f"[TIME] Duration: {duration:.1f} seconds")
        print(f"[SPEED] Rate: {results['stocks_per_minute']:.1f} stocks/minute")
        print(f"[AVG] Average processing time: {results['average_processing_time']:.2f}s")
        print(f"[COMPLETE] Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if success_rate < 80:
            print(f"[WARNING] Low success rate: {success_rate:.1f}%")
        
        print("="*70)
    
    def export_to_json(self, filename="stock_scanner_test_results.json"):
        """Export results to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"[EXPORT] Results exported to {filename}")
        except Exception as e:
            print(f"[EXPORT ERROR] Failed to export results: {e}")

def main():
    """Main test function"""
    # Test with different symbol sets
    test_cases = [
        {
            'name': 'Popular Stocks Test',
            'symbols': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'AMD', 'INTC'],
            'limit': 10
        },
        {
            'name': 'Problematic Symbols Test',
            'symbols': ['AAPGV', 'ABST', 'ACHL', 'ACST', 'ADAL', 'AAPL', 'MSFT', 'GOOGL'],
            'limit': 8
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*70}")
        print(f"[TEST CASE] {test_case['name']}")
        print(f"{'='*70}")
        
        scanner = StandaloneStockScanner(test_case['symbols'])
        results = scanner.run_test(test_case['limit'])
        
        # Export with unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"stock_scanner_test_{test_case['name'].replace(' ', '_').lower()}_{timestamp}.json"
        scanner.export_to_json(filename)

if __name__ == "__main__":
    main()