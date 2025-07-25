#!/usr/bin/env python3
"""
Django Management Command: Load NASDAQ-Only Tickers
Loads ONLY NASDAQ-listed ticker symbols (excludes NYSE, ARCA, BATS, etc.)

Usage:
python manage.py load_nasdaq_only
python manage.py load_nasdaq_only --update-existing
python manage.py load_nasdaq_only --dry-run

Author: Stock Scanner Project
Version: 4.0.0
Target: NASDAQ tickers ONLY
"""

import sys
import glob
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from stocks.models import Stock

# Add project root to path to import ticker data
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

class Command(BaseCommand):
help = 'Load NASDAQ-only ticker list (excludes NYSE, ARCA, BATS, etc.)'

def add_arguments(self, parser):
parser.add_argument(
'--update-existing',
action='store_true',
help='Update existing stock records with new information',
)
parser.add_argument(
'--dry-run',
action='store_true',
help='Show what would be done without making changes',
)
parser.add_argument(
'--batch-size',
type=int,
default=100,
help='Number of tickers to process in each batch (default: 100)',
)

def handle(self, *args, **options):
self.stdout.write(
self.style.SUCCESS(' Loading NASDAQ-Only Ticker List')
)
self.stdout.write('=' * 80)

try:
# Find the most recent NASDAQ-only ticker file
ticker_file = self.find_latest_nasdaq_only_file()
if not ticker_file:
raise CommandError("No NASDAQ-only ticker file found. Run: python tools/nasdaq_only_downloader.py")

# Import the ticker data
tickers_data = self.load_nasdaq_only_data(ticker_file)

if not tickers_data:
raise CommandError("Failed to load NASDAQ-only ticker data from file")

# Show summary
self.show_nasdaq_summary(tickers_data, ticker_file)

# Process tickers
if options['dry_run']:
self.stdout.write(self.style.WARNING('\n DRY RUN MODE - No changes will be made'))
self.dry_run_analysis(tickers_data, options['update_existing'])
else:
self.load_nasdaq_tickers(tickers_data, options)

except Exception as e:
raise CommandError(f'Error loading NASDAQ-only tickers: {e}')

def find_latest_nasdaq_only_file(self) -> Path:
"""Find the most recent NASDAQ-only ticker file"""
data_dir = Path('data/nasdaq_only')

if not data_dir.exists():
return None

# Look for NASDAQ-only ticker files
pattern = str(data_dir / 'nasdaq_only_tickers_*.py')
ticker_files = glob.glob(pattern)

if not ticker_files:
return None

# Return the most recent file
latest_file = max(ticker_files, key=lambda x: Path(x).stat().st_mtime)
return Path(latest_file)

def load_nasdaq_only_data(self, ticker_file: Path) -> list:
"""Load NASDAQ-only ticker data from Python file"""
self.stdout.write(f' Loading NASDAQ-only data from: {ticker_file.name}')

try:
# Read the file and extract ticker list
with open(ticker_file, 'r', encoding='utf-8') as f:
content = f.read()

# Execute the Python file to get the ticker list
namespace = {}
exec(content, namespace)

if 'NASDAQ_ONLY_TICKERS' in namespace:
tickers = namespace['NASDAQ_ONLY_TICKERS']
self.stdout.write(f' Loaded {len(tickers):,} NASDAQ-only tickers from file')
return tickers
else:
raise Exception("NASDAQ_ONLY_TICKERS not found in file")

except Exception as e:
self.stdout.write(
self.style.ERROR(f' Error loading NASDAQ-only ticker file: {e}')
)
return []

def show_nasdaq_summary(self, tickers: list, ticker_file: Path):
"""Display summary of NASDAQ-only tickers to be loaded"""
self.stdout.write(f'\n NASDAQ-Only Ticker Summary:')
self.stdout.write(f' Source file: {ticker_file.name}')
self.stdout.write(f' Exchange: NASDAQ ONLY')
self.stdout.write(f' Total NASDAQ tickers: {len(tickers):,}')
self.stdout.write(f' Excludes: NYSE, ARCA, BATS, OTC, etc.')

# Show sample tickers
sample_size = min(20, len(tickers))
sample_tickers = tickers[:sample_size]
self.stdout.write(f' Sample NASDAQ tickers: {", ".join(sample_tickers)}...')

def dry_run_analysis(self, tickers_to_load: list, update_existing: bool):
"""Analyze what would be done without making changes"""
self.stdout.write('\n Analyzing NASDAQ-only ticker data...')

existing_symbols = set(Stock.objects.values_list('symbol', flat=True))
existing_nasdaq = set(Stock.objects.filter(exchange='NASDAQ').values_list('symbol', flat=True))

new_nasdaq_tickers = []
existing_to_update = []

for ticker in tickers_to_load:
if ticker in existing_symbols:
if update_existing:
existing_to_update.append(ticker)
else:
new_nasdaq_tickers.append(ticker)

self.stdout.write(f'\n NASDAQ-Only Analysis Results:')
self.stdout.write(f' New NASDAQ tickers to add: {len(new_nasdaq_tickers):,}')
self.stdout.write(f' Existing NASDAQ tickers to update: {len(existing_to_update):,}')
self.stdout.write(f' Currently in database (NASDAQ): {len(existing_nasdaq):,}')
self.stdout.write(f' ⏭ NASDAQ tickers to skip: {len(existing_nasdaq & set(tickers_to_load)) - len(existing_to_update):,}')

if new_nasdaq_tickers:
sample_new = new_nasdaq_tickers[:10]
self.stdout.write(f'\n Sample new NASDAQ tickers: {", ".join(sample_new)}...')

if existing_to_update:
sample_update = existing_to_update[:10]
self.stdout.write(f'\n Sample NASDAQ tickers to update: {", ".join(sample_update)}...')

def load_nasdaq_tickers(self, tickers_to_load: list, options: dict):
"""Load NASDAQ-only tickers into the database"""
self.stdout.write('\n Loading NASDAQ-only tickers into database...')

batch_size = options.get('batch_size', 100)
update_existing = options.get('update_existing', False)

added_count = 0
updated_count = 0
skipped_count = 0
error_count = 0

# Process in batches for better performance
total_batches = (len(tickers_to_load) + batch_size - 1) // batch_size

for batch_num in range(total_batches):
start_idx = batch_num * batch_size
end_idx = min(start_idx + batch_size, len(tickers_to_load))
batch_tickers = tickers_to_load[start_idx:end_idx]

self.stdout.write(f' Processing NASDAQ batch {batch_num + 1}/{total_batches} ({len(batch_tickers)} tickers)...')

try:
with transaction.atomic():
for ticker in batch_tickers:
try:
# Get or create NASDAQ stock
stock, created = Stock.objects.get_or_create(
symbol=ticker,
defaults={
'name': f'{ticker} Corporation',
'sector': self.determine_nasdaq_sector(ticker),
'industry': 'Unknown',
'exchange': 'NASDAQ', # NASDAQ ONLY
'is_active': True,
'last_updated': timezone.now()
}
)

if created:
added_count += 1
elif update_existing:
# Update existing stock to ensure it's marked as NASDAQ
updated = False
if stock.exchange != 'NASDAQ':
stock.exchange = 'NASDAQ' # Force NASDAQ exchange
updated = True
if not stock.is_active:
stock.is_active = True
updated = True

if updated:
stock.last_updated = timezone.now()
stock.save()
updated_count += 1
else:
skipped_count += 1
else:
skipped_count += 1

except Exception as e:
error_count += 1
if error_count <= 5: # Show first 5 errors
self.stdout.write(
self.style.WARNING(f' Error processing NASDAQ ticker {ticker}: {e}')
)
continue

# Progress update
processed_so_far = min(end_idx, len(tickers_to_load))
progress_pct = (processed_so_far / len(tickers_to_load)) * 100
self.stdout.write(f' NASDAQ Progress: {processed_so_far:,}/{len(tickers_to_load):,} ({progress_pct:.1f}%)')

except Exception as e:
self.stdout.write(
self.style.ERROR(f' NASDAQ batch {batch_num + 1} failed: {e}')
)
error_count += len(batch_tickers)
continue

# Final summary
self.stdout.write('\n' + '=' * 80)
self.stdout.write(self.style.SUCCESS(' NASDAQ-only ticker loading finished!'))
self.stdout.write(f'\n NASDAQ-Only Results:')
self.stdout.write(f' Added: {added_count:,} new NASDAQ tickers')
self.stdout.write(f' Updated: {updated_count:,} existing NASDAQ tickers')
self.stdout.write(f' ⏭ Skipped: {skipped_count:,} unchanged NASDAQ tickers')
if error_count > 0:
self.stdout.write(f' Errors: {error_count:,} tickers')

# Database summary
total_stocks = Stock.objects.count()
nasdaq_stocks = Stock.objects.filter(exchange='NASDAQ').count()
active_nasdaq = Stock.objects.filter(exchange='NASDAQ', is_active=True).count()

self.stdout.write(f'\n Database Summary:')
self.stdout.write(f' Total stocks in database: {total_stocks:,}')
self.stdout.write(f' NASDAQ stocks: {nasdaq_stocks:,}')
self.stdout.write(f' Active NASDAQ stocks: {active_nasdaq:,}')

# Show exchange breakdown
from django.db.models import Count
exchanges = Stock.objects.values('exchange').annotate(count=Count('exchange')).order_by('-count')
self.stdout.write(f'\n Exchange Breakdown:')
for ex in exchanges:
exchange_name = ex['exchange'] or 'Unknown'
is_nasdaq = '' if exchange_name == 'NASDAQ' else ' '
self.stdout.write(f' {is_nasdaq} {exchange_name}: {ex["count"]:,} stocks')

# Performance stats
success_rate = ((added_count + updated_count + skipped_count) / len(tickers_to_load)) * 100
self.stdout.write(f'\n NASDAQ Success rate: {success_rate:.1f}%')

self.stdout.write(f'\n Next Steps:')
self.stdout.write(' 1. Fetch NASDAQ price data: python manage.py update_stocks_yfinance --exchange NASDAQ')
self.stdout.write(' 2. Test NASDAQ scanning: python manage.py runserver')
self.stdout.write(' 3. Start NASDAQ-only scanner: ./start_stock_scanner.sh')
self.stdout.write(f' 4. Verify NASDAQ count: python manage.py shell -c "from stocks.models import Stock; print(f\'NASDAQ stocks: {{Stock.objects.filter(exchange=\\\"NASDAQ\\\").count():,}}\')"')

def determine_nasdaq_sector(self, ticker: str) -> str:
"""Determine sector for NASDAQ ticker"""
# NASDAQ-specific sector heuristics

tech_tickers = ['AAPL', 'MSFT', 'GOOGL', 'GOOG', 'META', 'NVDA', 'AMD', 'INTC', 'CSCO', 'ADBE', 'CRM', 'ORCL']
biotech_tickers = ['AMGN', 'GILD', 'BIIB', 'MRNA', 'BNTX', 'REGN', 'VRTX']
retail_tickers = ['AMZN', 'COST', 'SBUX', 'LULU', 'ROST']
auto_tickers = ['TSLA', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI']
fintech_tickers = ['PYPL', 'SQ', 'COIN', 'HOOD', 'AFRM']

ticker_upper = ticker.upper()

if ticker_upper in tech_tickers or any(tech in ticker_upper for tech in ['TECH', 'SOFT', 'DATA', 'NET', 'APP']):
return 'Technology'
elif ticker_upper in biotech_tickers or any(bio in ticker_upper for bio in ['BIO', 'GENE', 'THER', 'PHARM']):
return 'Biotechnology'
elif ticker_upper in retail_tickers:
return 'Consumer Discretionary'
elif ticker_upper in auto_tickers or 'AUTO' in ticker_upper:
return 'Automotive'
elif ticker_upper in fintech_tickers or any(fin in ticker_upper for fin in ['FIN', 'PAY', 'BANK']):
return 'Financial Services'
else:
return 'Unknown'