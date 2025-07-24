#!/usr/bin/env python3
"""
Complete NASDAQ Ticker Downloader
Downloads ALL 3,300+ NASDAQ ticker symbols from multiple sources.

This script:
1. Downloads from official NASDAQ FTP (primary source)
2. Uses Yahoo Finance screener for backup
3. Web scrapes NASDAQ.com for complete list
4. Merges and deduplicates all sources
5. Formats for Stock Scanner integration

Data Sources:
- ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt
- ftp://ftp.nasdaqtrader.com/symboldirectory/otherlisted.txt
- Yahoo Finance stock screener
- NASDAQ.com official stock listings
- Alpha Vantage API (if available)

Author: Stock Scanner Project
Version: 3.0.0
Target: 3,300+ tickers
"""

import os
import sys
import urllib.request
import urllib.parse
import requests
import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
import re
from io import StringIO

class CompleteNasdaqDownloader:
    """Downloads complete NASDAQ ticker list from multiple sources"""
    
    def __init__(self):
        self.base_ftp_url = "ftp://ftp.nasdaqtrader.com/symboldirectory/"
        self.data_dir = Path('data/complete_nasdaq')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Results tracking
        self.all_tickers = set()
        self.ticker_details = {}
        self.sources_used = []
        self.errors = []
        
        # Headers for web requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'='*80}")
        print(f"📈 {title}")
        print('='*80)
        
    def print_step(self, message: str):
        """Print step message"""
        print(f"\n🔧 {message}")
        
    def print_success(self, message: str):
        """Print success message"""
        print(f"✅ {message}")
        
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"⚠️  {message}")
        
    def print_error(self, message: str):
        """Print error message"""
        print(f"❌ {message}")

    def download_nasdaq_ftp(self) -> Set[str]:
        """Download from official NASDAQ FTP - Primary source"""
        self.print_step("Downloading from official NASDAQ FTP...")
        
        tickers = set()
        files_to_download = {
            'nasdaqlisted.txt': 'NASDAQ-listed securities',
            'otherlisted.txt': 'Other exchange-listed securities'
        }
        
        for filename, description in files_to_download.items():
            try:
                url = self.base_ftp_url + filename
                local_path = self.data_dir / filename
                
                self.print_step(f"Downloading {description}...")
                urllib.request.urlretrieve(url, local_path)
                
                if local_path.exists() and local_path.stat().st_size > 0:
                    file_tickers = self.parse_nasdaq_file(local_path)
                    tickers.update(file_tickers)
                    self.print_success(f"Downloaded {len(file_tickers):,} tickers from {filename}")
                else:
                    self.print_error(f"Failed to download {filename}")
                    
            except Exception as e:
                self.print_warning(f"FTP download failed for {filename}: {e}")
                self.errors.append(f"FTP download error: {e}")
        
        if tickers:
            self.sources_used.append("NASDAQ FTP")
            self.print_success(f"FTP source: {len(tickers):,} total tickers")
        
        return tickers

    def parse_nasdaq_file(self, file_path: Path) -> Set[str]:
        """Parse NASDAQ file format"""
        tickers = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.strip().split('\n')
            data_lines = [line for line in lines[1:] if not line.startswith('File Creation Time')]
            
            for line in data_lines:
                fields = line.split('|')
                if len(fields) >= 1:
                    symbol = fields[0].strip()
                    
                    # Basic validation
                    if symbol and len(symbol) <= 5 and symbol.isalpha():
                        tickers.add(symbol)
                        
                        # Store additional details
                        if len(fields) >= 2:
                            name = fields[1].strip() if len(fields) > 1 else f"{symbol} Corp"
                            exchange = "NASDAQ" if "nasdaqlisted" in str(file_path) else "OTHER"
                            
                            self.ticker_details[symbol] = {
                                'name': name,
                                'exchange': exchange,
                                'source': 'FTP'
                            }
        
        except Exception as e:
            self.print_error(f"Error parsing {file_path}: {e}")
        
        return tickers

    def download_yahoo_finance_screener(self) -> Set[str]:
        """Download from Yahoo Finance stock screener"""
        self.print_step("Downloading from Yahoo Finance screener...")
        
        tickers = set()
        
        try:
            # Yahoo Finance screener API endpoints
            screener_urls = [
                # NASDAQ stocks
                "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?formatted=true&lang=en-US&region=US&scrIds=day_gainers%2Cday_losers%2Cmost_actives%2Cundervalued_large_caps%2Cundervalued_growth_stocks%2Cgrowth_technology_stocks",
                # Additional endpoints for comprehensive coverage
                "https://query2.finance.yahoo.com/v1/finance/screener"
            ]
            
            # Use a more comprehensive approach - get all US stocks
            url = "https://query1.finance.yahoo.com/v1/finance/screener"
            
            # Payload for all US stocks
            payload = {
                "size": 2500,  # Maximum allowed
                "offset": 0,
                "sortField": "ticker",
                "sortType": "ASC",
                "quoteType": "EQUITY",
                "topOperator": "AND",
                "query": {
                    "operator": "AND",
                    "operands": [
                        {
                            "operator": "eq",
                            "operands": ["region", "us"]
                        }
                    ]
                }
            }
            
            headers = {
                **self.headers,
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                quotes = data.get('finance', {}).get('result', [{}])[0].get('quotes', [])
                
                for quote in quotes:
                    symbol = quote.get('symbol', '').replace('.', '-')  # Handle special symbols
                    if symbol and len(symbol) <= 6:
                        tickers.add(symbol)
                        
                        # Store details
                        self.ticker_details[symbol] = {
                            'name': quote.get('longName', quote.get('shortName', f"{symbol} Corp")),
                            'exchange': quote.get('exchange', 'NASDAQ'),
                            'market_cap': quote.get('marketCap'),
                            'sector': quote.get('sector'),
                            'source': 'Yahoo Finance'
                        }
                
                self.print_success(f"Yahoo Finance: {len(tickers):,} tickers downloaded")
                self.sources_used.append("Yahoo Finance")
                
            else:
                self.print_warning(f"Yahoo Finance API returned status {response.status_code}")
                
        except Exception as e:
            self.print_warning(f"Yahoo Finance download failed: {e}")
            self.errors.append(f"Yahoo Finance error: {e}")
        
        return tickers

    def download_alpha_vantage_listings(self) -> Set[str]:
        """Download from Alpha Vantage API if available"""
        self.print_step("Attempting Alpha Vantage download...")
        
        tickers = set()
        
        try:
            # Try with free API key (limited)
            api_keys = [
                "demo",  # Demo key
                "ALPHA_VANTAGE_API_KEY"  # Environment variable
            ]
            
            for api_key in api_keys:
                if api_key == "ALPHA_VANTAGE_API_KEY":
                    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY", "")
                    if not api_key:
                        continue
                
                url = f"https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}"
                
                try:
                    response = requests.get(url, headers=self.headers, timeout=30)
                    
                    if response.status_code == 200:
                        content = response.text
                        
                        # Parse CSV content
                        csv_reader = csv.DictReader(StringIO(content))
                        for row in csv_reader:
                            symbol = row.get('symbol', '').strip()
                            if symbol and len(symbol) <= 5:
                                tickers.add(symbol)
                                
                                self.ticker_details[symbol] = {
                                    'name': row.get('name', f"{symbol} Corp"),
                                    'exchange': row.get('exchange', 'NASDAQ'),
                                    'asset_type': row.get('assetType', 'Stock'),
                                    'status': row.get('status', 'Active'),
                                    'source': 'Alpha Vantage'
                                }
                        
                        if tickers:
                            self.print_success(f"Alpha Vantage: {len(tickers):,} tickers downloaded")
                            self.sources_used.append("Alpha Vantage")
                            break
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.print_warning(f"Alpha Vantage download failed: {e}")
        
        return tickers

    def scrape_nasdaq_website(self) -> Set[str]:
        """Scrape NASDAQ.com for stock listings"""
        self.print_step("Scraping NASDAQ.com stock listings...")
        
        tickers = set()
        
        try:
            # NASDAQ stock screener API
            nasdaq_api_url = "https://api.nasdaq.com/api/screener/stocks"
            
            params = {
                'tableonly': 'true',
                'limit': 25,
                'offset': 0,
                'download': 'true'
            }
            
            # Get total count first
            response = requests.get(nasdaq_api_url, params=params, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                total_records = data.get('data', {}).get('totalrecords', 0)
                
                if total_records > 0:
                    # Download in batches
                    batch_size = 100
                    for offset in range(0, min(total_records, 5000), batch_size):
                        try:
                            params['offset'] = offset
                            params['limit'] = batch_size
                            
                            batch_response = requests.get(nasdaq_api_url, params=params, headers=self.headers, timeout=30)
                            
                            if batch_response.status_code == 200:
                                batch_data = batch_response.json()
                                rows = batch_data.get('data', {}).get('rows', [])
                                
                                for row in rows:
                                    symbol = row.get('symbol', '').strip()
                                    if symbol:
                                        tickers.add(symbol)
                                        
                                        self.ticker_details[symbol] = {
                                            'name': row.get('name', f"{symbol} Corp"),
                                            'exchange': 'NASDAQ',
                                            'sector': row.get('sector', 'Unknown'),
                                            'industry': row.get('industry', 'Unknown'),
                                            'market_cap': row.get('marketCap'),
                                            'source': 'NASDAQ.com'
                                        }
                                
                                if offset % 500 == 0:
                                    print(f"   📊 Downloaded {len(tickers):,} tickers so far...")
                                
                                time.sleep(0.1)  # Rate limiting
                            
                        except Exception as e:
                            self.print_warning(f"Batch download error at offset {offset}: {e}")
                            continue
                    
                    self.print_success(f"NASDAQ.com: {len(tickers):,} tickers scraped")
                    self.sources_used.append("NASDAQ.com")
            
        except Exception as e:
            self.print_warning(f"NASDAQ website scraping failed: {e}")
            self.errors.append(f"NASDAQ scraping error: {e}")
        
        return tickers

    def download_finviz_screener(self) -> Set[str]:
        """Download from Finviz stock screener"""
        self.print_step("Downloading from Finviz screener...")
        
        tickers = set()
        
        try:
            # Finviz screener URLs for different market caps
            finviz_urls = [
                "https://finviz.com/screener.ashx?v=111&f=cap_large&r=1",  # Large cap
                "https://finviz.com/screener.ashx?v=111&f=cap_mid&r=1",    # Mid cap
                "https://finviz.com/screener.ashx?v=111&f=cap_small&r=1",  # Small cap
                "https://finviz.com/screener.ashx?v=111&f=cap_micro&r=1"   # Micro cap
            ]
            
            for url in finviz_urls:
                try:
                    response = requests.get(url, headers=self.headers, timeout=30)
                    
                    if response.status_code == 200:
                        # Parse HTML for ticker symbols
                        content = response.text
                        
                        # Extract ticker symbols from the table
                        ticker_pattern = r'<a[^>]*class="tab-link"[^>]*>([A-Z]{1,5})</a>'
                        matches = re.findall(ticker_pattern, content)
                        
                        for symbol in matches:
                            if symbol and len(symbol) <= 5:
                                tickers.add(symbol)
                                
                                if symbol not in self.ticker_details:
                                    self.ticker_details[symbol] = {
                                        'name': f"{symbol} Corp",
                                        'exchange': 'NASDAQ',
                                        'source': 'Finviz'
                                    }
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    self.print_warning(f"Finviz URL failed: {url} - {e}")
                    continue
            
            if tickers:
                self.print_success(f"Finviz: {len(tickers):,} tickers found")
                self.sources_used.append("Finviz")
                
        except Exception as e:
            self.print_warning(f"Finviz download failed: {e}")
        
        return tickers

    def merge_all_sources(self) -> Set[str]:
        """Merge tickers from all sources and deduplicate"""
        self.print_step("Merging tickers from all sources...")
        
        all_sources = []
        
        # Try each source
        sources = [
            ("NASDAQ FTP", self.download_nasdaq_ftp),
            ("Yahoo Finance", self.download_yahoo_finance_screener),
            ("Alpha Vantage", self.download_alpha_vantage_listings),
            ("NASDAQ.com", self.scrape_nasdaq_website),
            ("Finviz", self.download_finviz_screener)
        ]
        
        for source_name, download_func in sources:
            try:
                source_tickers = download_func()
                all_sources.append((source_name, source_tickers))
                self.all_tickers.update(source_tickers)
                
                if source_tickers:
                    self.print_success(f"{source_name}: {len(source_tickers):,} tickers")
                else:
                    self.print_warning(f"{source_name}: No tickers obtained")
                    
            except Exception as e:
                self.print_error(f"{source_name} failed: {e}")
                self.errors.append(f"{source_name} error: {e}")
        
        # Clean and validate
        cleaned_tickers = self.clean_and_validate_tickers(self.all_tickers)
        
        self.print_success(f"Total unique tickers after merge: {len(cleaned_tickers):,}")
        
        return cleaned_tickers

    def clean_and_validate_tickers(self, tickers: Set[str]) -> Set[str]:
        """Clean and validate ticker symbols"""
        self.print_step("Cleaning and validating ticker symbols...")
        
        cleaned = set()
        
        for ticker in tickers:
            # Basic cleaning
            ticker = ticker.strip().upper()
            
            # Validation rules
            if (ticker and 
                1 <= len(ticker) <= 5 and 
                ticker.isalpha() and 
                not ticker in ['TEST', 'DEMO', 'NULL']):
                cleaned.add(ticker)
        
        removed_count = len(tickers) - len(cleaned)
        if removed_count > 0:
            self.print_success(f"Cleaned {removed_count:,} invalid tickers")
        
        return cleaned

    def save_complete_ticker_list(self, tickers: Set[str]) -> Path:
        """Save complete ticker list to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.data_dir / f'complete_nasdaq_tickers_{timestamp}.py'
        
        self.print_step(f"Saving complete ticker list to {output_file.name}...")
        
        # Sort tickers
        sorted_tickers = sorted(list(tickers))
        
        # Generate Python file content
        python_content = f'''#!/usr/bin/env python3
"""
Complete NASDAQ Ticker List
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total tickers: {len(sorted_tickers):,}

Sources used: {", ".join(self.sources_used)}
Data coverage: All NASDAQ and major exchange listed securities

This file contains the complete list of ticker symbols.
"""

# Complete NASDAQ ticker list ({len(sorted_tickers):,} symbols)
COMPLETE_NASDAQ_TICKERS = [
'''
        
        # Add tickers in rows of 10
        for i in range(0, len(sorted_tickers), 10):
            row = sorted_tickers[i:i+10]
            python_content += '    ' + ', '.join(f'"{ticker}"' for ticker in row) + ',\n'
        
        python_content = python_content.rstrip(',\n') + '\n]\n\n'
        
        # Add utility functions
        python_content += f'''
# Statistics
TOTAL_TICKERS = {len(sorted_tickers)}
SOURCES_USED = {self.sources_used}
GENERATION_DATE = "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"

def get_all_nasdaq_tickers():
    """Return all NASDAQ ticker symbols"""
    return COMPLETE_NASDAQ_TICKERS.copy()

def get_ticker_count():
    """Get total number of tickers"""
    return TOTAL_TICKERS

def is_valid_nasdaq_ticker(symbol):
    """Check if a ticker symbol is in the NASDAQ list"""
    return symbol.upper() in COMPLETE_NASDAQ_TICKERS

def search_nasdaq_tickers(query):
    """Search for tickers containing the query string"""
    query = query.upper()
    return [ticker for ticker in COMPLETE_NASDAQ_TICKERS if query in ticker]

def get_statistics():
    """Get generation statistics"""
    return {{
        'total_tickers': TOTAL_TICKERS,
        'sources_used': SOURCES_USED,
        'generation_date': GENERATION_DATE
    }}

# Sample tickers
SAMPLE_TICKERS = COMPLETE_NASDAQ_TICKERS[:20]

if __name__ == "__main__":
    print(f"🎯 Complete NASDAQ Ticker List")
    print(f"📊 Total tickers: {{get_ticker_count():,}}")
    print(f"📡 Sources: {{', '.join(SOURCES_USED)}}")
    print(f"🔍 Sample: {{', '.join(SAMPLE_TICKERS)}}")
    print(f"✅ Ready for Stock Scanner integration!")
'''
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(python_content)
        
        self.print_success(f"Saved {len(sorted_tickers):,} tickers to {output_file}")
        
        return output_file

    def generate_csv_export(self, tickers: Set[str]) -> Path:
        """Generate CSV export with ticker details"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = self.data_dir / f'complete_nasdaq_export_{timestamp}.csv'
        
        self.print_step(f"Generating CSV export...")
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Symbol', 'Name', 'Exchange', 'Sector', 'Source'])
            
            for ticker in sorted(tickers):
                details = self.ticker_details.get(ticker, {})
                writer.writerow([
                    ticker,
                    details.get('name', f'{ticker} Corp'),
                    details.get('exchange', 'NASDAQ'),
                    details.get('sector', 'Unknown'),
                    details.get('source', 'Multiple')
                ])
        
        self.print_success(f"CSV export saved: {csv_file}")
        return csv_file

    def run_complete_download(self) -> Tuple[Set[str], Path]:
        """Run complete NASDAQ ticker download"""
        self.print_header("COMPLETE NASDAQ TICKER DOWNLOADER")
        print("🎯 Downloading ALL 3,300+ NASDAQ ticker symbols...")
        print("📡 Using multiple sources for comprehensive coverage")
        print("⏱️  This may take several minutes...")
        
        try:
            # Download from all sources
            complete_tickers = self.merge_all_sources()
            
            if not complete_tickers:
                self.print_error("No tickers downloaded from any source!")
                return set(), Path()
            
            # Save results
            python_file = self.save_complete_ticker_list(complete_tickers)
            csv_file = self.generate_csv_export(complete_tickers)
            
            # Final summary
            self.print_header("DOWNLOAD COMPLETE")
            self.print_success("🎉 Complete NASDAQ download finished!")
            
            print(f"\n📊 FINAL RESULTS:")
            print(f"   📈 Total tickers downloaded: {len(complete_tickers):,}")
            print(f"   📡 Sources used: {len(self.sources_used)}")
            print(f"   📄 Python file: {python_file}")
            print(f"   📄 CSV export: {csv_file}")
            
            if self.sources_used:
                print(f"\n📡 DATA SOURCES:")
                for source in self.sources_used:
                    print(f"   ✅ {source}")
            
            if self.errors:
                print(f"\n⚠️  WARNINGS ({len(self.errors)}):")
                for error in self.errors[:3]:
                    print(f"   • {error}")
                if len(self.errors) > 3:
                    print(f"   ... and {len(self.errors) - 3} more warnings")
            
            print(f"\n🚀 NEXT STEPS:")
            print("   1. Use the generated Python file for Stock Scanner")
            print("   2. Run: python manage.py load_nasdaq_tickers")
            print("   3. Import: from data.complete_nasdaq.complete_nasdaq_tickers_* import COMPLETE_NASDAQ_TICKERS")
            
            return complete_tickers, python_file
            
        except Exception as e:
            self.print_error(f"Critical error during download: {e}")
            return set(), Path()

def main():
    """Main function"""
    downloader = CompleteNasdaqDownloader()
    
    try:
        tickers, output_file = downloader.run_complete_download()
        
        if tickers:
            print(f"\n✅ SUCCESS: Downloaded {len(tickers):,} NASDAQ tickers")
            return 0
        else:
            print(f"\n❌ FAILED: No tickers downloaded")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Download interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())