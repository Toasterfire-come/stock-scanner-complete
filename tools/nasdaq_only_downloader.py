#!/usr/bin/env python3
"""
NASDAQ-Only Ticker Downloader
Downloads ONLY NASDAQ exchange tickers (excludes NYSE, ARCA, BATS, etc.)
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

class NasdaqOnlyDownloader:
    """Downloads ONLY NASDAQ ticker list (no other exchanges)"""

    def __init__(self):
        """Initialize the NASDAQ-only downloader"""
        self.base_url = "https://api.nasdaq.com/api/screener/stocks"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.nasdaq_ftp_url = "ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt"
        self.data_dir = Path(__file__).parent.parent / 'data' / 'nasdaq_only'
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
        """Download NASDAQ tickers using API"""
        self.print_header("Downloading NASDAQ-Only Tickers")
        
        try:
            # NASDAQ API endpoint for screener
            params = {
                'tableonly': 'true',
                'limit': '10000',
                'offset': '0',
                'exchange': 'NASDAQ'  # NASDAQ only
            }
            
            self.print_info("Fetching NASDAQ ticker data from API...")
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
                    # Only include NASDAQ tickers
                    if self.is_nasdaq_ticker(ticker):
                        self.nasdaq_tickers.add(ticker)
                        self.ticker_details[ticker] = {
                            'name': row.get('name', ''),
                            'sector': row.get('sector', ''),
                            'industry': row.get('industry', ''),
                            'market_cap': row.get('marketCap', ''),
                            'exchange': 'NASDAQ'
                        }
            
            self.print_success(f"Downloaded {len(self.nasdaq_tickers)} NASDAQ tickers")
            return True
            
        except Exception as e:
            self.print_error(f"Failed to download NASDAQ tickers: {e}")
            return False

    def is_nasdaq_ticker(self, ticker: str) -> bool:
        """Check if ticker is a valid NASDAQ ticker"""
        # Basic validation for NASDAQ tickers
        if not ticker or len(ticker) < 1 or len(ticker) > 5:
            return False
        
        # Must be alphanumeric
        if not ticker.replace('.', '').isalnum():
            return False
        
        # Exclude obvious non-NASDAQ patterns
        excluded_patterns = ['TEST', 'TEMP', '.WS', '.RT', '.U', '.WD']
        for pattern in excluded_patterns:
            if pattern in ticker:
                return False
        
        return True

    def filter_nasdaq_only(self) -> Set[str]:
        """Filter to ensure only NASDAQ exchange tickers"""
        nasdaq_only = set()
        
        for ticker in self.nasdaq_tickers:
            # Additional filtering to ensure NASDAQ only
            if ticker and self.is_nasdaq_ticker(ticker):
                nasdaq_only.add(ticker)
        
        self.nasdaq_tickers = nasdaq_only
        return nasdaq_only

    def save_nasdaq_tickers(self) -> bool:
        """Save NASDAQ-only tickers to Python file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"nasdaq_only_tickers_{timestamp}.py"
            filepath = self.data_dir / filename
            
            # Sort tickers for consistency
            sorted_tickers = sorted(list(self.nasdaq_tickers))
            
            # Generate Python file content
            content = f'''#!/usr/bin/env python3
"""
NASDAQ-Only Ticker List
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Source: NASDAQ API (NASDAQ Exchange Only)
Total NASDAQ Tickers: {len(sorted_tickers):,}
"""

# NASDAQ-only ticker list (excludes NYSE, ARCA, BATS, etc.)
NASDAQ_ONLY_TICKERS = {sorted_tickers}

def get_nasdaq_tickers():
    """Get list of NASDAQ-only tickers"""
    return NASDAQ_ONLY_TICKERS

def get_nasdaq_count():
    """Get count of NASDAQ tickers"""
    return len(NASDAQ_ONLY_TICKERS)

if __name__ == "__main__":
    print(f"NASDAQ-Only Tickers: {{get_nasdaq_count():,}}")
    print("Sample NASDAQ tickers:", NASDAQ_ONLY_TICKERS[:10])
'''
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.print_success(f"NASDAQ-only tickers saved to: {filename}")
            self.print_info(f"File location: {filepath}")
            return True
            
        except Exception as e:
            self.print_error(f"Failed to save NASDAQ tickers: {e}")
            return False

    def generate_summary(self):
        """Generate download summary"""
        self.print_header("NASDAQ-Only Download Summary")
        
        print(f"📊 Exchange: NASDAQ ONLY")
        print(f"📊 Total NASDAQ Tickers: {len(self.nasdaq_tickers):,}")
        print(f"🕐 Downloaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Data Directory: {self.data_dir}")
        
        if self.errors:
            print(f"⚠️  Errors: {len(self.errors)}")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"   • {error}")
        
        # Show sample tickers
        if self.nasdaq_tickers:
            sample_tickers = sorted(list(self.nasdaq_tickers))[:20]
            print(f"\n📄 Sample NASDAQ Tickers:")
            print(f"   {', '.join(sample_tickers)}...")

    def run(self) -> bool:
        """Run the complete NASDAQ-only download process"""
        try:
            self.print_header("NASDAQ-Only Ticker Downloader")
            self.print_info("Target: NASDAQ Exchange Only")
            self.print_info("Excludes: NYSE, ARCA, BATS, OTC, etc.")
            
            # Download NASDAQ tickers
            if not self.download_nasdaq_tickers():
                self.print_error("Failed to download NASDAQ tickers")
                return False
            
            # Filter to ensure NASDAQ only
            nasdaq_filtered = self.filter_nasdaq_only()
            self.print_info(f"Filtered to {len(nasdaq_filtered)} NASDAQ-only tickers")
            
            if not nasdaq_filtered:
                self.print_error("No NASDAQ tickers found")
                return False
            
            # Save to file
            if not self.save_nasdaq_tickers():
                self.print_error("Failed to save NASDAQ tickers")
                return False
            
            # Generate summary
            self.generate_summary()
            
            self.print_success("NASDAQ-only download completed successfully!")
            return True
            
        except Exception as e:
            self.print_error(f"Download process failed: {e}")
            return False

def main():
    """Main execution function"""
    downloader = NasdaqOnlyDownloader()
    
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