#!/usr/bin/env python3
"""
NASDAQ Ticker List Updater
Downloads and integrates the complete NASDAQ ticker symbol list into Stock Scanner.

This script:
1. Downloads official NASDAQ ticker lists from nasdaqtrader.com FTP
2. Processes both NASDAQ-listed and other exchange-listed securities
3. Formats ticker data according to Stock Scanner database schema
4. Updates the database with comprehensive ticker information
5. Supports both development and production environments

Data Sources:
- ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt
- ftp://ftp.nasdaqtrader.com/symboldirectory/otherlisted.txt

Author: Stock Scanner Project
Version: 2.0.0
"""

import os
import sys
import urllib.request
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import django
from io import StringIO

# Set up Django environment
sys.path.append(str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')

try:
    import django
    if hasattr(django, 'setup'):
        django.setup()
    from stocks.models import Stock, StockPrice
    from django.db import transaction, connection
    from django.utils import timezone
    DJANGO_AVAILABLE = True
except (ImportError, AttributeError) as e:
    print(f"⚠️  Django not available: {e}")
    DJANGO_AVAILABLE = False

class NasdaqTickerUpdater:
    """Downloads and processes NASDAQ ticker lists"""
    
    def __init__(self):
        self.base_ftp_url = "ftp://ftp.nasdaqtrader.com/symboldirectory/"
        self.files_to_download = {
            'nasdaq_listed': 'nasdaqlisted.txt',
            'other_listed': 'otherlisted.txt'
        }
        self.data_dir = Path('data/nasdaq_tickers')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.tickers_processed = 0
        self.tickers_added = 0
        self.tickers_updated = 0
        self.errors = []
        
    def print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'='*70}")
        print(f"📈 {title}")
        print('='*70)
        
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

    def download_ticker_files(self) -> Dict[str, Path]:
        """Download ticker files from NASDAQ FTP"""
        self.print_step("Downloading NASDAQ ticker files...")
        
        downloaded_files = {}
        
        for file_type, filename in self.files_to_download.items():
            file_url = self.base_ftp_url + filename
            local_path = self.data_dir / filename
            
            try:
                self.print_step(f"Downloading {filename}...")
                urllib.request.urlretrieve(file_url, local_path)
                
                # Verify file was downloaded and has content
                if local_path.exists() and local_path.stat().st_size > 0:
                    downloaded_files[file_type] = local_path
                    self.print_success(f"Downloaded {filename} ({local_path.stat().st_size:,} bytes)")
                else:
                    self.print_error(f"Failed to download {filename} or file is empty")
                    
            except Exception as e:
                self.print_error(f"Error downloading {filename}: {e}")
                self.errors.append(f"Download failed for {filename}: {e}")
                
        return downloaded_files

    def parse_nasdaq_listed_file(self, file_path: Path) -> List[Dict]:
        """Parse NASDAQ-listed securities file"""
        self.print_step(f"Parsing NASDAQ-listed securities from {file_path.name}...")
        
        tickers = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into lines and process
            lines = content.strip().split('\n')
            
            # Skip header line and file creation time line
            data_lines = [line for line in lines[1:] if not line.startswith('File Creation Time')]
            
            for line_num, line in enumerate(data_lines, 2):
                try:
                    # Split by pipe delimiter
                    fields = line.split('|')
                    
                    if len(fields) >= 6:
                        symbol = fields[0].strip()
                        name = fields[1].strip()
                        market_category = fields[2].strip()
                        test_issue = fields[3].strip()
                        financial_status = fields[4].strip()
                        round_lot = fields[5].strip()
                        
                        # Skip test issues
                        if test_issue.upper() == 'Y':
                            continue
                            
                        # Skip if symbol is empty or invalid
                        if not symbol or len(symbol) > 5:
                            continue
                            
                        ticker_data = {
                            'symbol': symbol,
                            'name': name,
                            'exchange': 'NASDAQ',
                            'market_category': market_category,
                            'financial_status': financial_status,
                            'round_lot': round_lot,
                            'is_etf': False,  # Will be determined later
                            'source_file': 'nasdaq_listed',
                            'is_active': financial_status in ['N', 'D', 'E']  # Normal, Deficient, Delinquent
                        }
                        
                        tickers.append(ticker_data)
                        
                except Exception as e:
                    self.print_warning(f"Error parsing line {line_num}: {e}")
                    continue
            
            self.print_success(f"Parsed {len(tickers):,} NASDAQ-listed securities")
            
        except Exception as e:
            self.print_error(f"Error reading {file_path}: {e}")
            self.errors.append(f"Parse error for {file_path}: {e}")
            
        return tickers

    def parse_other_listed_file(self, file_path: Path) -> List[Dict]:
        """Parse other exchange-listed securities file"""
        self.print_step(f"Parsing other exchange-listed securities from {file_path.name}...")
        
        tickers = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into lines and process
            lines = content.strip().split('\n')
            
            # Skip header line and file creation time line
            data_lines = [line for line in lines[1:] if not line.startswith('File Creation Time')]
            
            for line_num, line in enumerate(data_lines, 2):
                try:
                    # Split by pipe delimiter
                    fields = line.split('|')
                    
                    if len(fields) >= 8:
                        act_symbol = fields[0].strip()
                        name = fields[1].strip()
                        exchange = fields[2].strip()
                        cqs_symbol = fields[3].strip()
                        etf_flag = fields[4].strip()
                        round_lot = fields[5].strip()
                        test_issue = fields[6].strip()
                        nasdaq_symbol = fields[7].strip() if len(fields) > 7 else act_symbol
                        
                        # Use the most appropriate symbol
                        symbol = nasdaq_symbol if nasdaq_symbol else act_symbol
                        
                        # Skip test issues
                        if test_issue.upper() == 'Y':
                            continue
                            
                        # Skip if symbol is empty or invalid
                        if not symbol or len(symbol) > 5:
                            continue
                            
                        # Map exchange codes
                        exchange_map = {
                            'A': 'NYSE MKT',
                            'N': 'NYSE',
                            'P': 'NYSE ARCA',
                            'Z': 'BATS',
                            'V': 'IEXG'
                        }
                        
                        exchange_name = exchange_map.get(exchange, exchange)
                        
                        ticker_data = {
                            'symbol': symbol,
                            'name': name,
                            'exchange': exchange_name,
                            'market_category': 'OTHER',
                            'financial_status': 'N',  # Assume normal for other exchanges
                            'round_lot': round_lot,
                            'is_etf': etf_flag.upper() == 'Y',
                            'source_file': 'other_listed',
                            'is_active': True
                        }
                        
                        tickers.append(ticker_data)
                        
                except Exception as e:
                    self.print_warning(f"Error parsing line {line_num}: {e}")
                    continue
            
            self.print_success(f"Parsed {len(tickers):,} other exchange-listed securities")
            
        except Exception as e:
            self.print_error(f"Error reading {file_path}: {e}")
            self.errors.append(f"Parse error for {file_path}: {e}")
            
        return tickers

    def deduplicate_tickers(self, all_tickers: List[Dict]) -> List[Dict]:
        """Remove duplicate tickers, preferring NASDAQ-listed over others"""
        self.print_step("Deduplicating ticker symbols...")
        
        # Create symbol map to handle duplicates
        symbol_map = {}
        
        for ticker in all_tickers:
            symbol = ticker['symbol']
            
            if symbol not in symbol_map:
                symbol_map[symbol] = ticker
            else:
                # Prefer NASDAQ-listed over other exchanges
                existing = symbol_map[symbol]
                if ticker['source_file'] == 'nasdaq_listed' and existing['source_file'] == 'other_listed':
                    symbol_map[symbol] = ticker
                # If both are from same source, prefer the active one
                elif ticker['is_active'] and not existing['is_active']:
                    symbol_map[symbol] = ticker
        
        deduplicated = list(symbol_map.values())
        
        self.print_success(f"Deduplicated to {len(deduplicated):,} unique ticker symbols")
        
        return deduplicated

    def save_to_csv(self, tickers: List[Dict]) -> Path:
        """Save ticker data to CSV file"""
        csv_path = self.data_dir / f'nasdaq_tickers_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        self.print_step(f"Saving ticker data to {csv_path.name}...")
        
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                if tickers:
                    fieldnames = tickers[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(tickers)
            
            self.print_success(f"Saved {len(tickers):,} tickers to {csv_path}")
            
        except Exception as e:
            self.print_error(f"Error saving CSV: {e}")
            self.errors.append(f"CSV save error: {e}")
            
        return csv_path

    def update_database(self, tickers: List[Dict]) -> bool:
        """Update Stock Scanner database with ticker data"""
        if not DJANGO_AVAILABLE:
            self.print_warning("Django not available, skipping database update")
            return False
            
        self.print_step("Updating Stock Scanner database...")
        
        try:
            with transaction.atomic():
                for ticker in tickers:
                    try:
                        # Check if stock already exists
                        stock, created = Stock.objects.get_or_create(
                            symbol=ticker['symbol'],
                            defaults={
                                'name': ticker['name'][:255],  # Limit name length
                                'exchange': ticker['exchange'],
                                'sector': 'Unknown',  # Will be updated later by other processes
                                'industry': 'Unknown',
                                'is_active': ticker['is_active'],
                                'last_updated': timezone.now()
                            }
                        )
                        
                        if created:
                            self.tickers_added += 1
                        else:
                            # Update existing stock information
                            updated = False
                            if stock.name != ticker['name'][:255]:
                                stock.name = ticker['name'][:255]
                                updated = True
                            if stock.exchange != ticker['exchange']:
                                stock.exchange = ticker['exchange']
                                updated = True
                            if stock.is_active != ticker['is_active']:
                                stock.is_active = ticker['is_active']
                                updated = True
                                
                            if updated:
                                stock.last_updated = timezone.now()
                                stock.save()
                                self.tickers_updated += 1
                        
                        self.tickers_processed += 1
                        
                        # Progress indicator
                        if self.tickers_processed % 500 == 0:
                            print(f"   📊 Processed {self.tickers_processed:,} tickers...")
                            
                    except Exception as e:
                        self.print_warning(f"Error processing ticker {ticker['symbol']}: {e}")
                        self.errors.append(f"Database error for {ticker['symbol']}: {e}")
                        continue
            
            self.print_success(f"Database update completed:")
            print(f"   📊 Total processed: {self.tickers_processed:,}")
            print(f"   ➕ Added: {self.tickers_added:,}")
            print(f"   🔄 Updated: {self.tickers_updated:,}")
            
            return True
            
        except Exception as e:
            self.print_error(f"Database transaction failed: {e}")
            self.errors.append(f"Database transaction error: {e}")
            return False

    def generate_ticker_python_list(self, tickers: List[Dict]) -> Path:
        """Generate Python list format for direct use in code"""
        py_path = self.data_dir / f'nasdaq_tickers_list_{datetime.now().strftime("%Y%m%d")}.py'
        
        self.print_step(f"Generating Python ticker list: {py_path.name}...")
        
        try:
            # Group tickers by exchange for better organization
            exchanges = {}
            for ticker in tickers:
                exchange = ticker['exchange']
                if exchange not in exchanges:
                    exchanges[exchange] = []
                exchanges[exchange].append(ticker['symbol'])
            
            # Sort symbols within each exchange
            for exchange in exchanges:
                exchanges[exchange].sort()
            
            # Generate Python code
            python_code = f'''#!/usr/bin/env python3
"""
NASDAQ Complete Ticker List
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total tickers: {len(tickers):,}

Source: Official NASDAQ FTP (ftp://ftp.nasdaqtrader.com/symboldirectory/)
Files: nasdaqlisted.txt, otherlisted.txt

This file contains the complete list of ticker symbols from NASDAQ and other major exchanges.
"""

# Complete ticker list (all exchanges)
ALL_TICKERS = [
'''
            
            # Add all symbols in a clean format
            symbols = [ticker['symbol'] for ticker in tickers]
            symbols.sort()
            
            # Format symbols in rows of 10 for readability
            for i in range(0, len(symbols), 10):
                row = symbols[i:i+10]
                python_code += '    ' + ', '.join(f'"{symbol}"' for symbol in row) + ',\n'
            
            python_code = python_code.rstrip(',\n') + '\n]\n\n'
            
            # Add exchange-specific lists
            for exchange, symbols in exchanges.items():
                var_name = exchange.replace(' ', '_').replace('-', '_').upper() + '_TICKERS'
                python_code += f'# {exchange} Exchange Tickers ({len(symbols):,} symbols)\n'
                python_code += f'{var_name} = [\n'
                
                for i in range(0, len(symbols), 10):
                    row = symbols[i:i+10]
                    python_code += '    ' + ', '.join(f'"{symbol}"' for symbol in row) + ',\n'
                
                python_code = python_code.rstrip(',\n') + '\n]\n\n'
            
            # Add utility functions
            python_code += '''
# Utility functions
def get_all_tickers():
    """Return all ticker symbols"""
    return ALL_TICKERS.copy()

def get_tickers_by_exchange(exchange_name):
    """Return tickers for a specific exchange"""
    exchange_map = {
'''
            
            for exchange in exchanges:
                var_name = exchange.replace(' ', '_').replace('-', '_').upper() + '_TICKERS'
                python_code += f'        "{exchange}": {var_name},\n'
            
            python_code += '''    }
    return exchange_map.get(exchange_name, [])

def is_valid_ticker(symbol):
    """Check if a ticker symbol is valid"""
    return symbol.upper() in ALL_TICKERS

def get_ticker_count():
    """Get total number of tickers"""
    return len(ALL_TICKERS)

def get_exchange_summary():
    """Get summary of tickers by exchange"""
    return {
'''
            
            for exchange, symbols in exchanges.items():
                python_code += f'        "{exchange}": {len(symbols)},\n'
                
            python_code += '''    }

if __name__ == "__main__":
    print(f"Total tickers available: {get_ticker_count():,}")
    print("\\nTickers by exchange:")
    for exchange, count in get_exchange_summary().items():
        print(f"  {exchange}: {count:,}")
'''
            
            # Write to file
            with open(py_path, 'w', encoding='utf-8') as f:
                f.write(python_code)
            
            self.print_success(f"Generated Python ticker list: {py_path}")
            
        except Exception as e:
            self.print_error(f"Error generating Python list: {e}")
            self.errors.append(f"Python list generation error: {e}")
            
        return py_path

    def update_stocks_models(self, tickers: List[Dict]) -> bool:
        """Update the stocks/models.py with new ticker choices"""
        
        models_file = Path('stocks/models.py')
        if not models_file.exists():
            self.print_warning("stocks/models.py not found, skipping model update")
            return False
            
        self.print_step("Updating stocks/models.py with ticker choices...")
        
        try:
            # Read current models.py
            with open(models_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate ticker choices for Django model
            symbols = sorted([ticker['symbol'] for ticker in tickers if ticker['is_active']])
            
            # Create choices tuple
            choices_lines = []
            choices_lines.append("# Auto-generated ticker choices")
            choices_lines.append(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            choices_lines.append(f"# Total active tickers: {len(symbols):,}")
            choices_lines.append("TICKER_CHOICES = (")
            
            for symbol in symbols:
                choices_lines.append(f'    ("{symbol}", "{symbol}"),')
            
            choices_lines.append(")")
            
            ticker_choices_code = '\n'.join(choices_lines)
            
            # Insert or replace ticker choices in models.py
            if 'TICKER_CHOICES' in content:
                # Replace existing choices
                import re
                pattern = r'TICKER_CHOICES = \([^)]*\)'
                content = re.sub(pattern, ticker_choices_code.replace('\n', '\n'), content, flags=re.MULTILINE | re.DOTALL)
            else:
                # Add before the first class definition
                class_match = re.search(r'^class\s+\w+', content, re.MULTILINE)
                if class_match:
                    insert_pos = class_match.start()
                    content = content[:insert_pos] + ticker_choices_code + '\n\n' + content[insert_pos:]
                else:
                    # Add at the end
                    content += '\n\n' + ticker_choices_code
            
            # Create backup
            backup_file = models_file.with_suffix('.py.backup')
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Write updated content
            with open(models_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.print_success(f"Updated stocks/models.py with {len(symbols):,} ticker choices")
            self.print_success(f"Backup saved to {backup_file}")
            
            return True
            
        except Exception as e:
            self.print_error(f"Error updating models.py: {e}")
            self.errors.append(f"Models update error: {e}")
            return False

    def run_complete_update(self) -> bool:
        """Run the complete ticker update process"""
        self.print_header("NASDAQ COMPLETE TICKER LIST UPDATER")
        print("🎯 Downloading and integrating complete NASDAQ ticker list...")
        print("📡 Source: Official NASDAQ FTP (ftp://ftp.nasdaqtrader.com/)")
        
        try:
            # Step 1: Download files
            downloaded_files = self.download_ticker_files()
            
            if not downloaded_files:
                self.print_error("No files downloaded successfully")
                return False
            
            # Step 2: Parse files
            all_tickers = []
            
            if 'nasdaq_listed' in downloaded_files:
                nasdaq_tickers = self.parse_nasdaq_listed_file(downloaded_files['nasdaq_listed'])
                all_tickers.extend(nasdaq_tickers)
            
            if 'other_listed' in downloaded_files:
                other_tickers = self.parse_other_listed_file(downloaded_files['other_listed'])
                all_tickers.extend(other_tickers)
            
            if not all_tickers:
                self.print_error("No tickers parsed from downloaded files")
                return False
            
            # Step 3: Deduplicate
            unique_tickers = self.deduplicate_tickers(all_tickers)
            
            # Step 4: Save to CSV
            csv_path = self.save_to_csv(unique_tickers)
            
            # Step 5: Generate Python list
            py_path = self.generate_ticker_python_list(unique_tickers)
            
            # Step 6: Update Django models
            self.update_stocks_models(unique_tickers)
            
            # Step 7: Update database
            if DJANGO_AVAILABLE:
                db_success = self.update_database(unique_tickers)
            else:
                db_success = False
                self.print_warning("Skipping database update (Django not available)")
            
            # Final summary
            self.print_header("UPDATE COMPLETE")
            self.print_success("🎉 NASDAQ ticker list update completed!")
            
            print(f"\n📊 SUMMARY:")
            print(f"   📈 Total unique tickers: {len(unique_tickers):,}")
            print(f"   📈 Active tickers: {sum(1 for t in unique_tickers if t['is_active']):,}")
            print(f"   📈 NASDAQ tickers: {sum(1 for t in unique_tickers if t['exchange'] == 'NASDAQ'):,}")
            print(f"   📈 Other exchanges: {sum(1 for t in unique_tickers if t['exchange'] != 'NASDAQ'):,}")
            print(f"   📈 ETFs identified: {sum(1 for t in unique_tickers if t['is_etf']):,}")
            
            print(f"\n📋 FILES CREATED:")
            print(f"   📄 CSV data: {csv_path}")
            print(f"   📄 Python list: {py_path}")
            if DJANGO_AVAILABLE:
                print(f"   📄 Database updated: {self.tickers_added:,} added, {self.tickers_updated:,} updated")
            
            if self.errors:
                print(f"\n⚠️  WARNINGS ({len(self.errors)}):")
                for error in self.errors[:5]:  # Show first 5 errors
                    print(f"   • {error}")
                if len(self.errors) > 5:
                    print(f"   ... and {len(self.errors) - 5} more warnings")
            
            print(f"\n🚀 NEXT STEPS:")
            print("   1. Import ticker list: from data.nasdaq_tickers.nasdaq_tickers_list_* import ALL_TICKERS")
            print("   2. Use in Stock Scanner: python manage.py update_stocks_yfinance")
            print("   3. Test ticker validation: python -c \"from stocks.models import Stock; print(Stock.objects.count())\"")
            
            return len(self.errors) == 0
            
        except Exception as e:
            self.print_error(f"Critical error during update: {e}")
            return False

def main():
    """Main function"""
    updater = NasdaqTickerUpdater()
    
    try:
        success = updater.run_complete_update()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Update interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())