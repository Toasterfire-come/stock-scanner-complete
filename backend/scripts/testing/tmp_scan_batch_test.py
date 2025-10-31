import time
from fast_stock_scanner import load_combined_tickers, StockScanner

symbols = load_combined_tickers()[:1000]
scanner = StockScanner(threads=10, timeout=8, use_proxies=False, db_enabled=False)
start = time.time()
stats = scanner.scan_batch(symbols, csv_out=None, chunk_size=250)
print('duration', time.time()-start)
print(stats)
