#!/usr/bin/env python3
"""
Complete NASDAQ Ticker Downloader
Downloads comprehensive NASDAQ ticker list from multiple sources
"""

import requests
import csv
import json
import time
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
import re
from io import StringIO

class CompleteNasdaqDownloader:
    """Downloads complete NASDAQ ticker list from multiple sources"""

    def __init__(self):
        """Initialize the complete NASDAQ downloader"""
        self.base_url = "https://api.nasdaq.com/api/screener/stocks"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.data_dir = Path(__file__).parent.parent / 'data' / 'complete_nasdaq'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Results tracking
        self.nasdaq_tickers = set()
        self.ticker_details = {}
        self.errors = []

    def print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'='*80}")
        print(f" {title}")
        print(f"{'='*80}")

    def print_success(self, message: str):
        """Print success message"""
        print(f"✅ {message}")

    def print_error(self, message: str):
        """Print error message"""
        print(f"❌ {message}")

    def print_info(self, message: str):
        """Print info message"""
        print(f"ℹ️  {message}")

    def download_nasdaq_tickers(self) -> bool:
        """Download complete NASDAQ ticker list"""
        self.print_header("Downloading Complete NASDAQ Tickers")
        
        try:
            # NASDAQ API endpoint for all exchanges
            params = {
                'tableonly': 'true',
                'limit': '25000',  # Higher limit for complete list
                'offset': '0'
            }
            
            self.print_info("Fetching complete NASDAQ ticker data from API...")
            response = requests.get(self.base_url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code != 200:
                self.print_error(f"API request failed: {response.status_code}")
                return False
            
            data = response.json()
            
            if 'data' not in data or 'rows' not in data['data']:
                self.print_error("Unexpected API response format")
                return False
            
            rows = data['data']['rows']
            
            for row in rows:
                if 'symbol' in row:
                    ticker = row['symbol'].strip().upper()
                    if self.is_valid_ticker(ticker):
                        self.nasdaq_tickers.add(ticker)
                        self.ticker_details[ticker] = {
                            'name': row.get('name', ''),
                            'sector': row.get('sector', ''),
                            'industry': row.get('industry', ''),
                            'market_cap': row.get('marketCap', ''),
                            'exchange': row.get('exchange', 'NASDAQ')
                        }
            
            self.print_success(f"Downloaded {len(self.nasdaq_tickers)} complete NASDAQ tickers")
            return True
            
        except Exception as e:
            self.print_error(f"Failed to download NASDAQ tickers: {e}")
            return False

    def is_valid_ticker(self, ticker: str) -> bool:
        """Check if ticker is valid"""
        if not ticker or len(ticker) < 1 or len(ticker) > 6:
            return False
        
        # Must be alphanumeric with possible dots/hyphens
        if not re.match(r'^[A-Z0-9\.\-]+$', ticker):
            return False
        
        # Exclude test patterns
        excluded_patterns = ['TEST', 'TEMP', 'DEMO']
        for pattern in excluded_patterns:
            if pattern in ticker:
                return False
        
        return True

    def save_complete_tickers(self) -> bool:
        """Save complete NASDAQ tickers to Python file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"complete_nasdaq_tickers_{timestamp}.py"
            filepath = self.data_dir / filename
            
            # Sort tickers for consistency
            sorted_tickers = sorted(list(self.nasdaq_tickers))
            
            # Generate Python file content
            content = f'''#!/usr/bin/env python3
"""
Complete NASDAQ Ticker List
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Source: NASDAQ API (All Exchanges)
Total Tickers: {len(sorted_tickers):,}
"""

# Complete NASDAQ ticker list
COMPLETE_NASDAQ_TICKERS = {sorted_tickers}

def get_complete_tickers():
    """Get list of complete NASDAQ tickers"""
    return COMPLETE_NASDAQ_TICKERS

def get_ticker_count():
    """Get count of tickers"""
    return len(COMPLETE_NASDAQ_TICKERS)

if __name__ == "__main__":
    print(f"Complete NASDAQ Tickers: {{get_ticker_count():,}}")
    print("Sample tickers:", COMPLETE_NASDAQ_TICKERS[:10])
'''
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.print_success(f"Complete NASDAQ tickers saved to: {filename}")
            self.print_info(f"File location: {filepath}")
            return True
            
        except Exception as e:
            self.print_error(f"Failed to save tickers: {e}")
            return False

    def generate_summary(self):
        """Generate download summary"""
        self.print_header("Complete NASDAQ Download Summary")
        
        print(f"📊 Total Tickers: {len(self.nasdaq_tickers):,}")
        print(f"🕐 Downloaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Data Directory: {self.data_dir}")
        
        if self.errors:
            print(f"⚠️  Errors: {len(self.errors)}")
            for error in self.errors[:5]:
                print(f"   • {error}")
        
        # Show sample tickers
        if self.nasdaq_tickers:
            sample_tickers = sorted(list(self.nasdaq_tickers))[:20]
            print(f"\n📄 Sample Tickers:")
            print(f"   {', '.join(sample_tickers)}...")

    def run(self) -> bool:
        """Run the complete download process"""
        try:
            self.print_header("Complete NASDAQ Ticker Downloader")
            self.print_info("Target: All NASDAQ-listed securities")
            
            # Download tickers
            if not self.download_nasdaq_tickers():
                self.print_error("Failed to download tickers")
                return False
            
            if not self.nasdaq_tickers:
                self.print_error("No tickers found")
                return False
            
            # Save to file
            if not self.save_complete_tickers():
                self.print_error("Failed to save tickers")
                return False
            
            # Generate summary
            self.generate_summary()
            
            self.print_success("Complete NASDAQ download completed successfully!")
            return True
            
        except Exception as e:
            self.print_error(f"Download process failed: {e}")
            return False

def main():
    """Main execution function"""
    downloader = CompleteNasdaqDownloader()
    
    try:
        success = downloader.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Download interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()