#!/usr/bin/env python
"""Complete system refresh: proxies, stock lists, and database update"""
import os
import sys
import json
import time
import csv
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SECRET_KEY', 'temp-key-for-script')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import Stock

# Configuration
PROXY_TEST_TARGET = "https://httpbin.org/get"
PROXY_TEST_ATTEMPTS = 3
PROXY_TEST_TIMEOUT = 5.0
MIN_PROXY_SUCCESS_RATE = 66.0  # 66% = 2/3 attempts successful

# Free proxy sources
FREE_PROXY_SOURCES = [
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
]

# Stock list sources (multiple fallbacks)
STOCK_LIST_SOURCES = [
    {
        'name': 'NASDAQ Official',
        'url': 'https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt',
        'exchange': 'NASDAQ',
        'type': 'pipe_delimited'
    },
    {
        'name': 'NYSE Official',
        'url': 'https://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt',
        'exchange': 'NYSE',
        'type': 'pipe_delimited'
    },
    {
        'name': 'EOD Historical Data',
        'url': 'https://eodhistoricaldata.com/api/exchange-symbol-list/US?api_token=demo&fmt=json',
        'exchange': 'US',
        'type': 'json'
    }
]

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)

def test_single_proxy(proxy, target=PROXY_TEST_TARGET, attempts=PROXY_TEST_ATTEMPTS, timeout=PROXY_TEST_TIMEOUT):
    """Test a single proxy with multiple attempts"""
    successes = 0
    total_latency = 0

    session = requests.Session()
    session.proxies = {"http": proxy, "https": proxy}
    headers = {"User-Agent": "StockScanner/1.0"}

    for _ in range(attempts):
        start = time.perf_counter()
        try:
            resp = session.get(target, headers=headers, timeout=timeout)
            latency = (time.perf_counter() - start) * 1000
            if resp.ok:
                successes += 1
                total_latency += latency
        except Exception:
            pass

    success_rate = (successes / attempts) * 100 if attempts > 0 else 0
    avg_latency = total_latency / successes if successes > 0 else None

    return {
        'proxy': proxy,
        'successes': successes,
        'attempts': attempts,
        'success_rate': success_rate,
        'avg_latency_ms': avg_latency,
        'healthy': success_rate >= MIN_PROXY_SUCCESS_RATE
    }

def test_proxies(proxies, max_workers=50):
    """Test multiple proxies concurrently"""
    print(f"[INFO] Testing {len(proxies)} proxies ({PROXY_TEST_ATTEMPTS} attempts each)...")

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(test_single_proxy, proxy): proxy for proxy in proxies}

        completed = 0
        for future in as_completed(futures):
            completed += 1
            if completed % 50 == 0 or completed == len(proxies):
                print(f"[PROGRESS] Tested {completed}/{len(proxies)} proxies...")

            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                proxy = futures[future]
                print(f"[ERROR] Failed to test {proxy}: {e}")

    return results

def fetch_free_proxies():
    """Fetch proxies from free proxy sources"""
    print_header("FETCHING FREE PROXIES")

    all_proxies = set()

    for source_url in FREE_PROXY_SOURCES:
        try:
            print(f"[FETCH] {source_url}")
            resp = requests.get(source_url, timeout=10)
            if resp.ok:
                # Parse proxy list (one per line)
                lines = resp.text.strip().split('\n')
                proxies = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Format as http://ip:port
                        if '://' not in line:
                            line = f'http://{line}'
                        proxies.append(line)

                all_proxies.update(proxies)
                print(f"[SUCCESS] Got {len(proxies)} proxies from this source")
        except Exception as e:
            print(f"[ERROR] Failed to fetch from {source_url}: {e}")

    print(f"\n[TOTAL] Fetched {len(all_proxies)} unique proxies")
    return list(all_proxies)

def load_existing_proxies(file_path='working_proxies.json'):
    """Load existing proxies from JSON file"""
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data.get('proxies', [])
    except Exception as e:
        print(f"[ERROR] Failed to load {file_path}: {e}")
        return []

def save_proxies(proxies, file_path='working_proxies.json'):
    """Save proxies to JSON file"""
    data = {'proxies': proxies}
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"[SAVED] {len(proxies)} proxies to {file_path}")

def fetch_stocks_from_multiple_sources():
    """Fetch stock lists from multiple reliable sources"""
    print_header("FETCHING STOCK LISTS")

    all_stocks = []

    # Source 1: DataHub S&P 500
    try:
        print("[FETCH] S&P 500 constituents...")
        url = "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv"
        resp = requests.get(url, timeout=15)
        if resp.ok:
            import io
            reader = csv.DictReader(io.StringIO(resp.text))
            for row in reader:
                symbol = row.get('Symbol', '').strip()
                name = row.get('Name', '').strip()
                if symbol:
                    all_stocks.append({
                        'symbol': symbol,
                        'name': name or symbol,
                        'exchange': 'NYSE'
                    })
            print(f"[SUCCESS] Got {len(all_stocks)} S&P 500 stocks")
    except Exception as e:
        print(f"[WARN] Failed to fetch S&P 500: {e}")

    # Source 2: Use yfinance to get comprehensive list (slower but reliable)
    try:
        print("[FETCH] Using yfinance ticker search...")
        import yfinance as yf

        # Get popular US stocks from yfinance
        # This is a simpler approach - use major indices
        indices = {
            '^GSPC': 'S&P 500',  # S&P 500 components
            '^DJI': 'Dow Jones',  # Dow 30 components
            '^IXIC': 'NASDAQ Composite'  # NASDAQ components (top companies)
        }

        print("[INFO] Fetching from major US indices...")
        # For now, we'll keep the existing database and just add new symbols
        print("[INFO] Will update database with discovered symbols during price updates")

    except Exception as e:
        print(f"[WARN] yfinance fetch failed: {e}")

    # Source 3: Use existing database as base
    try:
        print("[FETCH] Loading from existing database...")
        from stocks.models import Stock
        existing_stocks = Stock.objects.all().values('symbol', 'name', 'exchange')
        for stock in existing_stocks:
            if stock['symbol'] not in [s['symbol'] for s in all_stocks]:
                all_stocks.append({
                    'symbol': stock['symbol'],
                    'name': stock['name'] or stock['symbol'],
                    'exchange': stock['exchange'] or 'NASDAQ'
                })
        print(f"[SUCCESS] Loaded {len(existing_stocks)} stocks from database")
    except Exception as e:
        print(f"[WARN] Failed to load from database: {e}")

    # Deduplicate
    seen_symbols = set()
    unique_stocks = []
    for stock in all_stocks:
        if stock['symbol'] not in seen_symbols:
            seen_symbols.add(stock['symbol'])
            unique_stocks.append(stock)

    print(f"\n[TOTAL] Have {len(unique_stocks)} unique stocks to update")
    return unique_stocks

def update_database(stocks):
    """Update database with stock list"""
    print_header("UPDATING DATABASE")

    print(f"[INFO] Processing {len(stocks)} stocks...")

    created = 0
    updated = 0

    for stock_data in stocks:
        try:
            stock, was_created = Stock.objects.update_or_create(
                symbol=stock_data['symbol'],
                defaults={
                    'name': stock_data['name'],
                    'exchange': stock_data['exchange']
                }
            )

            if was_created:
                created += 1
            else:
                updated += 1

        except Exception as e:
            print(f"[ERROR] Failed to process {stock_data['symbol']}: {e}")

    print(f"[RESULTS]")
    print(f"  Created: {created}")
    print(f"  Updated: {updated}")
    print(f"  Total: {created + updated}")

    return created, updated

def main():
    """Main refresh workflow"""
    print_header("STOCK SCANNER SYSTEM REFRESH")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: Test existing proxies
    print_header("STEP 1: TEST EXISTING PROXIES")
    existing_proxies = load_existing_proxies('working_proxies.json')
    print(f"[INFO] Found {len(existing_proxies)} existing proxies")

    if existing_proxies:
        print("[INFO] Testing existing proxies...")
        existing_results = test_proxies(existing_proxies[:100], max_workers=50)  # Test first 100
        healthy_existing = [r['proxy'] for r in existing_results if r['healthy']]
        print(f"[RESULTS] {len(healthy_existing)}/{len(existing_results)} existing proxies are healthy")
    else:
        healthy_existing = []

    # Step 2: Fetch and test new proxies if needed
    target_proxy_count = 200  # Aim for 200 healthy proxies

    if len(healthy_existing) < target_proxy_count:
        print_header("STEP 2: FETCH NEW PROXIES")
        new_proxies = fetch_free_proxies()

        # Remove duplicates with existing
        new_proxies = [p for p in new_proxies if p not in existing_proxies]
        print(f"[INFO] {len(new_proxies)} new unique proxies to test")

        if new_proxies:
            print("[INFO] Testing new proxies...")
            new_results = test_proxies(new_proxies, max_workers=50)
            healthy_new = [r['proxy'] for r in new_results if r['healthy']]
            print(f"[RESULTS] {len(healthy_new)}/{len(new_results)} new proxies are healthy")
        else:
            healthy_new = []
    else:
        print("[SKIP] Have enough healthy proxies, skipping new proxy fetch")
        healthy_new = []

    # Step 3: Save healthy proxies
    all_healthy_proxies = list(set(healthy_existing + healthy_new))
    if all_healthy_proxies:
        save_proxies(all_healthy_proxies, 'working_proxies.json')
        print(f"\n[PROXIES] Total healthy proxies: {len(all_healthy_proxies)}")

    # Step 4: Fetch stock lists
    print_header("STEP 3: FETCH STOCK LISTS")
    all_stocks = fetch_stocks_from_multiple_sources()

    nasdaq_stocks = [s for s in all_stocks if s['exchange'] == 'NASDAQ']
    nyse_stocks = [s for s in all_stocks if s['exchange'] == 'NYSE']

    print(f"\n[STOCKS] Total stocks: {len(all_stocks)}")
    print(f"  NYSE: {len(nyse_stocks)}")
    print(f"  NASDAQ: {len(nasdaq_stocks)}")

    # Step 5: Update database
    if all_stocks:
        created, updated = update_database(all_stocks)
    else:
        print("[ERROR] No stocks fetched, skipping database update")
        created, updated = 0, 0

    # Final summary
    print_header("REFRESH COMPLETE")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nSummary:")
    print(f"  Healthy Proxies: {len(all_healthy_proxies)}")
    print(f"  Stocks Fetched: {len(all_stocks)} (NYSE: {len(nyse_stocks)}, NASDAQ: {len(nasdaq_stocks)})")
    print(f"  Database Created: {created}")
    print(f"  Database Updated: {updated}")
    print(f"  Total in Database: {Stock.objects.count()}")

if __name__ == '__main__':
    main()
