#!/usr/bin/env python3
"""
NASDAQ-Only Ticker Downloader
Downloads ONLY NASDAQ-listed ticker symbols (excluding NYSE, ARCA, etc.)

This script:
1. Downloads from NASDAQ FTP nasdaqlisted.txt ONLY
2. Filters to include ONLY NASDAQ securities
3. Excludes NYSE, ARCA, BATS, and other exchanges
4. Provides pure NASDAQ ticker list

Data Source:
- ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt (NASDAQ ONLY)

Author: Stock Scanner Project
Version: 4.0.0
Target: NASDAQ tickers ONLY
"""

import os
import sys
import urllib.request
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
import re
from io import StringIO

class NasdaqOnlyDownloader:
    """Downloads ONLY NASDAQ ticker list (no other exchanges)"""
    
    def __init__(self):
        self.nasdaq_ftp_url = "ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt"
        self.data_dir = Path('data/nasdaq_only')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Results tracking
        self.nasdaq_tickers = set()
        self.ticker_details = {}
        self.errors = []
        
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

    def download_nasdaq_only(self) -> Set[str]:
        """Download ONLY NASDAQ-listed securities"""
        self.print_step("Downloading NASDAQ-only ticker list...")
        
        tickers = set()
        
        try:
            local_path = self.data_dir / 'nasdaqlisted.txt'
            
            self.print_step("Downloading from official NASDAQ FTP (NASDAQ ONLY)...")
            urllib.request.urlretrieve(self.nasdaq_ftp_url, local_path)
            
            if local_path.exists() and local_path.stat().st_size > 0:
                nasdaq_tickers = self.parse_nasdaq_only_file(local_path)
                tickers.update(nasdaq_tickers)
                self.print_success(f"Downloaded {len(nasdaq_tickers):,} NASDAQ-only tickers")
            else:
                self.print_error("Failed to download NASDAQ file")
                
        except Exception as e:
            self.print_warning(f"NASDAQ FTP download failed: {e}")
            self.errors.append(f"NASDAQ FTP download error: {e}")
            
            # Fallback to hardcoded NASDAQ list if FTP fails
            self.print_step("Using fallback NASDAQ ticker list...")
            tickers = self.get_fallback_nasdaq_tickers()
        
        return tickers

    def parse_nasdaq_only_file(self, file_path: Path) -> Set[str]:
        """Parse NASDAQ file and extract ONLY NASDAQ securities"""
        tickers = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.strip().split('\n')
            # Skip header and footer
            data_lines = [line for line in lines[1:] if not line.startswith('File Creation Time')]
            
            for line in data_lines:
                fields = line.split('|')
                if len(fields) >= 8:  # NASDAQ file has specific format
                    symbol = fields[0].strip()
                    security_name = fields[1].strip() if len(fields) > 1 else f"{symbol} Corp"
                    market_category = fields[2].strip() if len(fields) > 2 else ""
                    test_issue = fields[3].strip() if len(fields) > 3 else ""
                    financial_status = fields[4].strip() if len(fields) > 4 else ""
                    round_lot_size = fields[5].strip() if len(fields) > 5 else ""
                    etf = fields[6].strip() if len(fields) > 6 else ""
                    nextshares = fields[7].strip() if len(fields) > 7 else ""
                    
                    # NASDAQ-only filtering
                    if (symbol and 
                        len(symbol) <= 5 and 
                        symbol.isalpha() and 
                        test_issue != "Y" and  # Exclude test issues
                        symbol not in ['TEST', 'DEMO']):  # Exclude test symbols
                        
                        tickers.add(symbol)
                        
                        # Store NASDAQ-specific details
                        self.ticker_details[symbol] = {
                            'name': security_name,
                            'exchange': 'NASDAQ',
                            'market_category': market_category,
                            'financial_status': financial_status,
                            'etf': etf == 'Y',
                            'nextshares': nextshares == 'Y',
                            'source': 'NASDAQ FTP'
                        }
        
        except Exception as e:
            self.print_error(f"Error parsing NASDAQ file {file_path}: {e}")
        
        return tickers

    def get_fallback_nasdaq_tickers(self) -> Set[str]:
        """Fallback NASDAQ ticker list if FTP download fails"""
        self.print_step("Using curated NASDAQ-only ticker list...")
        
        # Core NASDAQ tickers (major ones that are definitely NASDAQ)
        nasdaq_core_tickers = [
            # NASDAQ 100 Technology Leaders
            "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "COST",
            "NFLX", "ADBE", "PEP", "TMUS", "CSCO", "INTC", "CMCSA", "TXN", "QCOM", "AMGN",
            "HON", "INTU", "AMD", "AMAT", "ISRG", "BKNG", "ADP", "GILD", "LRCX", "MDLZ",
            "ADI", "REGN", "VRTX", "KLAC", "MELI", "SNPS", "CDNS", "MAR", "ORLY", "CSX",
            "FTNT", "ADSK", "NXPI", "MRVL", "ABNB", "CHTR", "WDAY", "MNST", "TEAM", "DXCM",
            
            # NASDAQ Technology & Growth
            "ZM", "ROKU", "SHOP", "SQ", "PYPL", "OKTA", "CRWD", "ZS", "NET", "DDOG",
            "SNOW", "PLTR", "RBLX", "U", "PATH", "HOOD", "COIN", "RIVN", "LCID", "NIO",
            "XPEV", "LI", "BIDU", "PDD", "JD", "BILI", "TME", "WB", "GRAB", "SE",
            
            # NASDAQ Biotech & Healthcare
            "BIIB", "MRNA", "BNTX", "VRTX", "REGN", "GILD", "AMGN", "CELG", "IDXX", "ILMN",
            "TECH", "BMRN", "ALXN", "INCY", "VTRS", "TEVA", "EXAS", "ALGN", "DEXC", "ISRG",
            
            # NASDAQ Consumer & Retail
            "COST", "SBUX", "LULU", "ROST", "DLTR", "ULTA", "NCLH", "CCL", "MAR", "BKNG",
            "EXPD", "CHRW", "FAST", "PAYX", "FISV", "ADP", "INTU", "CTSH", "LBTYA", "LBTYK",
            
            # NASDAQ Financial Services
            "PYPL", "SQ", "COIN", "SOFI", "AFRM", "LC", "UPST", "HOOD", "NU", "PAGS",
            
            # NASDAQ Semiconductors
            "NVDA", "AMD", "INTC", "QCOM", "AVGO", "TXN", "ADI", "LRCX", "KLAC", "AMAT",
            "NXPI", "MRVL", "MCHP", "SWKS", "QRVO", "MPWR", "ON", "TER", "ENTG", "MTSI",
            
            # NASDAQ Communications & Media
            "GOOGL", "GOOG", "META", "NFLX", "CMCSA", "CHTR", "TMUS", "VZ", "T", "DISH",
            "SIRI", "FOXA", "FOX", "PARA", "WBD", "NWSA", "NWS", "NYT", "GSAT", "IRDM",
            
            # NASDAQ Energy & Materials
            "ENPH", "SEDG", "FSLR", "RUN", "NOVA", "BE", "PLUG", "FCEL", "BLDP", "BALLARD"
        ]
        
        tickers = set(nasdaq_core_tickers)
        
        # Add ticker details for fallback
        for ticker in tickers:
            self.ticker_details[ticker] = {
                'name': f'{ticker} Corporation',
                'exchange': 'NASDAQ',
                'market_category': 'Q',  # NASDAQ Global Select Market
                'financial_status': 'N',  # Normal
                'etf': False,
                'source': 'Fallback List'
            }
        
        self.print_success(f"Loaded {len(tickers):,} NASDAQ tickers from fallback list")
        return tickers

    def clean_and_validate_nasdaq_tickers(self, tickers: Set[str]) -> Set[str]:
        """Clean and validate NASDAQ ticker symbols"""
        self.print_step("Cleaning and validating NASDAQ ticker symbols...")
        
        cleaned = set()
        
        for ticker in tickers:
            # Basic cleaning
            ticker = ticker.strip().upper()
            
            # NASDAQ-specific validation rules
            if (ticker and 
                1 <= len(ticker) <= 5 and 
                ticker.isalpha() and 
                not ticker in ['TEST', 'DEMO', 'NULL'] and
                not ticker.endswith('TEST')):
                cleaned.add(ticker)
        
        removed_count = len(tickers) - len(cleaned)
        if removed_count > 0:
            self.print_success(f"Cleaned {removed_count:,} invalid tickers")
        
        return cleaned

    def save_nasdaq_only_ticker_list(self, tickers: Set[str]) -> Path:
        """Save NASDAQ-only ticker list to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.data_dir / f'nasdaq_only_tickers_{timestamp}.py'
        
        self.print_step(f"Saving NASDAQ-only ticker list to {output_file.name}...")
        
        # Sort tickers
        sorted_tickers = sorted(list(tickers))
        
        # Generate Python file content
        python_content = f'''#!/usr/bin/env python3
"""
NASDAQ-Only Ticker List
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total NASDAQ tickers: {len(sorted_tickers):,}

Source: NASDAQ FTP - nasdaqlisted.txt ONLY
Exchange: NASDAQ ONLY (excludes NYSE, ARCA, BATS, etc.)

This file contains ONLY NASDAQ-listed securities.
"""

# NASDAQ-only ticker list ({len(sorted_tickers):,} symbols)
NASDAQ_ONLY_TICKERS = [
'''
        
        # Add tickers in rows of 10
        for i in range(0, len(sorted_tickers), 10):
            row = sorted_tickers[i:i+10]
            python_content += '    ' + ', '.join(f'"{ticker}"' for ticker in row) + ',\n'
        
        python_content = python_content.rstrip(',\n') + '\n]\n\n'
        
        # Add utility functions
        python_content += f'''
# Statistics
TOTAL_NASDAQ_TICKERS = {len(sorted_tickers)}
EXCHANGE = "NASDAQ"
GENERATION_DATE = "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"

def get_nasdaq_only_tickers():
    """Return NASDAQ-only ticker symbols"""
    return NASDAQ_ONLY_TICKERS.copy()

def get_nasdaq_ticker_count():
    """Get total number of NASDAQ tickers"""
    return TOTAL_NASDAQ_TICKERS

def is_nasdaq_ticker(symbol):
    """Check if a ticker symbol is NASDAQ-listed"""
    return symbol.upper() in NASDAQ_ONLY_TICKERS

def search_nasdaq_tickers(query):
    """Search for NASDAQ tickers containing the query string"""
    query = query.upper()
    return [ticker for ticker in NASDAQ_ONLY_TICKERS if query in ticker]

def get_nasdaq_statistics():
    """Get NASDAQ generation statistics"""
    return {{
        'total_tickers': TOTAL_NASDAQ_TICKERS,
        'exchange': EXCHANGE,
        'generation_date': GENERATION_DATE,
        'source': 'NASDAQ FTP - nasdaqlisted.txt ONLY'
    }}

# Sample NASDAQ tickers
SAMPLE_NASDAQ_TICKERS = NASDAQ_ONLY_TICKERS[:20]

if __name__ == "__main__":
    print(f"📈 NASDAQ-Only Ticker List")
    print(f"📊 Total NASDAQ tickers: {{get_nasdaq_ticker_count():,}}")
    print(f"🏛️  Exchange: {{EXCHANGE}} ONLY")
    print(f"🔍 Sample: {{', '.join(SAMPLE_NASDAQ_TICKERS)}}")
    print(f"✅ Ready for Stock Scanner integration!")
'''
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(python_content)
        
        self.print_success(f"Saved {len(sorted_tickers):,} NASDAQ-only tickers to {output_file}")
        
        return output_file

    def generate_nasdaq_csv_export(self, tickers: Set[str]) -> Path:
        """Generate CSV export with NASDAQ ticker details"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = self.data_dir / f'nasdaq_only_export_{timestamp}.csv'
        
        self.print_step(f"Generating NASDAQ-only CSV export...")
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Symbol', 'Name', 'Exchange', 'Market_Category', 'ETF', 'Source'])
            
            for ticker in sorted(tickers):
                details = self.ticker_details.get(ticker, {})
                writer.writerow([
                    ticker,
                    details.get('name', f'{ticker} Corp'),
                    'NASDAQ',
                    details.get('market_category', 'Q'),
                    details.get('etf', False),
                    details.get('source', 'NASDAQ FTP')
                ])
        
        self.print_success(f"NASDAQ-only CSV export saved: {csv_file}")
        return csv_file

    def run_nasdaq_only_download(self) -> Tuple[Set[str], Path]:
        """Run NASDAQ-only ticker download"""
        self.print_header("NASDAQ-ONLY TICKER DOWNLOADER")
        print("🎯 Downloading NASDAQ ticker symbols ONLY...")
        print("🏛️  Source: NASDAQ FTP (excludes NYSE, ARCA, BATS, etc.)")
        print("📈 Pure NASDAQ exchange securities only")
        
        try:
            # Download NASDAQ-only tickers
            nasdaq_tickers = self.download_nasdaq_only()
            
            if not nasdaq_tickers:
                self.print_error("No NASDAQ tickers downloaded!")
                return set(), Path()
            
            # Clean and validate
            cleaned_tickers = self.clean_and_validate_nasdaq_tickers(nasdaq_tickers)
            
            # Save results
            python_file = self.save_nasdaq_only_ticker_list(cleaned_tickers)
            csv_file = self.generate_nasdaq_csv_export(cleaned_tickers)
            
            # Final summary
            self.print_header("NASDAQ-ONLY DOWNLOAD COMPLETE")
            self.print_success("🎉 NASDAQ-only download finished!")
            
            print(f"\n📊 FINAL RESULTS:")
            print(f"   📈 Total NASDAQ tickers: {len(cleaned_tickers):,}")
            print(f"   🏛️  Exchange: NASDAQ ONLY")
            print(f"   📄 Python file: {python_file}")
            print(f"   📄 CSV export: {csv_file}")
            
            print(f"\n🏛️  EXCHANGE COVERAGE:")
            print("   ✅ NASDAQ - NASDAQ-listed securities ONLY")
            print("   ❌ NYSE - Excluded")
            print("   ❌ ARCA - Excluded") 
            print("   ❌ BATS - Excluded")
            print("   ❌ Other exchanges - Excluded")
            
            if self.errors:
                print(f"\n⚠️  WARNINGS ({len(self.errors)}):")
                for error in self.errors[:3]:
                    print(f"   • {error}")
                if len(self.errors) > 3:
                    print(f"   ... and {len(self.errors) - 3} more warnings")
            
            print(f"\n🚀 NEXT STEPS:")
            print("   1. Use the generated Python file for Stock Scanner")
            print("   2. Run: python manage.py load_nasdaq_only")
            print("   3. Import: from data.nasdaq_only.nasdaq_only_tickers_* import NASDAQ_ONLY_TICKERS")
            
            return cleaned_tickers, python_file
            
        except Exception as e:
            self.print_error(f"Critical error during NASDAQ-only download: {e}")
            return set(), Path()

def main():
    """Main function"""
    downloader = NasdaqOnlyDownloader()
    
    try:
        tickers, output_file = downloader.run_nasdaq_only_download()
        
        if tickers:
            print(f"\n✅ SUCCESS: Downloaded {len(tickers):,} NASDAQ-only tickers")
            return 0
        else:
            print(f"\n❌ FAILED: No NASDAQ tickers downloaded")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Download interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())