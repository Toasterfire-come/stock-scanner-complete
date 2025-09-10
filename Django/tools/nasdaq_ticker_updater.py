#!/usr/bin/env python3
"""
NASDAQ Ticker Updater
Updates NASDAQ ticker database with latest ticker information
"""

import os
import sys
import django
from pathlib import Path

# Set up Django environment
sys.path.append(str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')

try:
    import django
    if hasattr(django, 'setup'):
        django.setup()
except Exception as e:
    print(f"Django setup failed: {e}")
    sys.exit(1)

from django.core.management import call_command
from stocks.models import Stock
import requests
import json
import time
from datetime import datetime
from proxy_manager import ProxyManager  # Add this import

class NasdaqTickerUpdater:
    """Updates NASDAQ ticker information in the database"""

    def __init__(self):
        """Initialize the updater"""
        self.base_url = "https://api.nasdaq.com/api/screener/stocks"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.updated_count = 0
        self.errors = []
        self.proxy_manager = ProxyManager(min_proxies=50, max_proxies=200)

    def print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'='*80}")
        print(f" {title}")
        print(f"{'='*80}")

    def print_success(self, message: str):
        """Print success message"""
        print(f"[SUCCESS] {message}")

    def print_error(self, message: str):
        """Print error message"""
        print(f"[ERROR] {message}")

    def print_info(self, message: str):
        """Print info message"""
        print(f"[INFO]  {message}")

    def update_nasdaq_tickers(self) -> bool:
        """Update NASDAQ tickers in database"""
        self.print_header("Updating NASDAQ Tickers")
        try:
            # Get current tickers from database
            existing_tickers = set(Stock.objects.values_list('ticker', flat=True))
            self.print_info(f"Found {len(existing_tickers)} existing tickers in database")
            params = {
                'tableonly': 'true',
                'limit': '10000',
                'offset': '0',
                'exchange': 'NASDAQ'
            }
            self.print_info("Fetching latest NASDAQ data...")
            attempt = 0
            max_attempts = 5
            ticker_number = 0  # For proxy rotation
            while attempt < max_attempts:
                proxy = self.proxy_manager.get_proxy_for_ticker(ticker_number)
                proxies = {'http': proxy, 'https': proxy} if proxy else None
                try:
                    response = requests.get(self.base_url, headers=self.headers, params=params, timeout=30, proxies=proxies)
                    if response.status_code == 200:
                        break
                    else:
                        self.print_error(f"API request failed: {response.status_code}")
                        if proxy:
                            self.proxy_manager.mark_proxy_failed(proxy)
                        attempt += 1
                        ticker_number += 1
                except Exception as e:
                    self.print_error(f"Request error: {e}")
                    if proxy:
                        self.proxy_manager.mark_proxy_failed(proxy)
                    attempt += 1
                    ticker_number += 1
            else:
                self.print_error("All proxy attempts failed.")
                return False
            data = response.json()
            if 'data' not in data or 'rows' not in data['data']:
                self.print_error("Unexpected API response format")
                return False
            rows = data['data']['rows']
            # Update existing tickers
            for row in rows:
                if 'symbol' in row:
                    ticker = row['symbol'].strip().upper()
                    if ticker in existing_tickers:
                        try:
                            stock = Stock.objects.get(ticker=ticker)
                            stock.company_name = row.get('name', stock.company_name)
                            stock.sector = row.get('sector', stock.sector)
                            stock.industry = row.get('industry', stock.industry)
                            stock.exchange = 'NASDAQ'
                            stock.last_updated = datetime.now()
                            stock.save()
                            self.updated_count += 1
                        except Stock.DoesNotExist:
                            continue
                        except Exception as e:
                            self.errors.append(f"Error updating {ticker}: {e}")
            self.print_success(f"Updated {self.updated_count} NASDAQ tickers")
            return True
        except Exception as e:
            self.print_error(f"Failed to update NASDAQ tickers: {e}")
            return False

    def generate_summary(self):
        """Generate update summary"""
        self.print_header("Update Summary")
        
        print(f"[STATS] Tickers Updated: {self.updated_count}")
        print(f" Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.errors:
            print(f"[WARNING]  Errors: {len(self.errors)}")
            for error in self.errors[:5]:
                print(f"   - {error}")

    def run(self) -> bool:
        """Run the update process"""
        try:
            self.print_header("NASDAQ Ticker Updater")
            self.print_info("Updating NASDAQ ticker information in database")
            
            # Update tickers
            if not self.update_nasdaq_tickers():
                self.print_error("Failed to update tickers")
                return False
            
            # Generate summary
            self.generate_summary()
            
            self.print_success("NASDAQ ticker update completed successfully!")
            return True
            
        except Exception as e:
            self.print_error(f"Update process failed: {e}")
            return False

def main():
    """Main execution function"""
    updater = NasdaqTickerUpdater()
    
    try:
        success = updater.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[STOP]  Update interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Update failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()