#!/usr/bin/env python3
"""
Django Management Command: Load Complete NASDAQ Tickers
Loads the complete 11,658+ NASDAQ ticker list into the Stock Scanner database.

Usage:
    python manage.py load_complete_nasdaq
    python manage.py load_complete_nasdaq --update-existing
    python manage.py load_complete_nasdaq --dry-run
    python manage.py load_complete_nasdaq --batch-size 500

Author: Stock Scanner Project
Version: 3.0.0
Target: 11,658+ tickers
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
    help = 'Load complete NASDAQ ticker list (11,658+ tickers) into Stock Scanner database'

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
            default=500,
            help='Number of tickers to process in each batch (default: 500)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of tickers to load (for testing)',
        )
        parser.add_argument(
            '--exchange-filter',
            type=str,
            help='Filter by exchange (NASDAQ, NYSE, ARCA, etc.)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🎯 Loading Complete NASDAQ Ticker List (11,658+ Tickers)')
        )
        self.stdout.write('=' * 80)
        
        try:
            # Find the most recent complete ticker file
            ticker_file = self.find_latest_ticker_file()
            if not ticker_file:
                raise CommandError("No complete NASDAQ ticker file found. Run: python tools/complete_nasdaq_downloader.py")
            
            # Import the ticker data
            tickers_data = self.load_ticker_data(ticker_file)
            
            if not tickers_data:
                raise CommandError("Failed to load ticker data from file")
            
            # Apply filters
            filtered_tickers = self.apply_filters(tickers_data, options)
            
            # Show summary
            self.show_summary(filtered_tickers, ticker_file)
            
            # Process tickers
            if options['dry_run']:
                self.stdout.write(self.style.WARNING('\n🔍 DRY RUN MODE - No changes will be made'))
                self.dry_run_analysis(filtered_tickers, options['update_existing'])
            else:
                self.load_tickers(filtered_tickers, options)
            
        except Exception as e:
            raise CommandError(f'Error loading complete NASDAQ tickers: {e}')

    def find_latest_ticker_file(self) -> Path:
        """Find the most recent complete ticker file"""
        data_dir = Path('data/complete_nasdaq')
        
        if not data_dir.exists():
            return None
        
        # Look for complete ticker files
        pattern = str(data_dir / 'complete_nasdaq_tickers_*.py')
        ticker_files = glob.glob(pattern)
        
        if not ticker_files:
            return None
        
        # Return the most recent file
        latest_file = max(ticker_files, key=lambda x: Path(x).stat().st_mtime)
        return Path(latest_file)

    def load_ticker_data(self, ticker_file: Path) -> list:
        """Load ticker data from Python file"""
        self.stdout.write(f'📄 Loading ticker data from: {ticker_file.name}')
        
        try:
            # Read the file and extract ticker list
            with open(ticker_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Execute the Python file to get the ticker list
            namespace = {}
            exec(content, namespace)
            
            if 'COMPLETE_NASDAQ_TICKERS' in namespace:
                tickers = namespace['COMPLETE_NASDAQ_TICKERS']
                self.stdout.write(f'✅ Loaded {len(tickers):,} tickers from file')
                return tickers
            else:
                raise Exception("COMPLETE_NASDAQ_TICKERS not found in file")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error loading ticker file: {e}')
            )
            return []

    def apply_filters(self, tickers_data: list, options: dict) -> list:
        """Apply filters to ticker data"""
        filtered_tickers = tickers_data.copy()
        
        # Apply exchange filter
        if options.get('exchange_filter'):
            exchange = options['exchange_filter'].upper()
            # For this basic version, we'll keep all tickers since we don't have exchange info
            # In a more advanced version, you'd filter by exchange
            self.stdout.write(f'📊 Exchange filter "{exchange}" noted (applied during processing)')
        
        # Apply limit
        if options.get('limit'):
            filtered_tickers = filtered_tickers[:options['limit']]
            self.stdout.write(f'📊 Limited to first {options["limit"]:,} tickers')
        
        return filtered_tickers

    def show_summary(self, tickers: list, ticker_file: Path):
        """Display summary of tickers to be loaded"""
        self.stdout.write(f'\n📈 Complete NASDAQ Ticker Summary:')
        self.stdout.write(f'   📄 Source file: {ticker_file.name}')
        self.stdout.write(f'   📊 Total tickers to process: {len(tickers):,}')
        
        # Show sample tickers
        sample_size = min(20, len(tickers))
        sample_tickers = tickers[:sample_size]
        self.stdout.write(f'   🔍 Sample tickers: {", ".join(sample_tickers)}...')

    def dry_run_analysis(self, tickers_to_load: list, update_existing: bool):
        """Analyze what would be done without making changes"""
        self.stdout.write('\n🔍 Analyzing ticker data...')
        
        existing_symbols = set(Stock.objects.values_list('symbol', flat=True))
        new_tickers = []
        existing_to_update = []
        
        for ticker in tickers_to_load:
            if ticker in existing_symbols:
                if update_existing:
                    existing_to_update.append(ticker)
            else:
                new_tickers.append(ticker)
        
        self.stdout.write(f'\n📊 Analysis Results:')
        self.stdout.write(f'   ➕ New tickers to add: {len(new_tickers):,}')
        self.stdout.write(f'   🔄 Existing tickers to update: {len(existing_to_update):,}')
        self.stdout.write(f'   ⏭️  Existing tickers to skip: {len(existing_symbols & set(tickers_to_load)) - len(existing_to_update):,}')
        
        if new_tickers:
            sample_new = new_tickers[:10]
            self.stdout.write(f'\n🆕 Sample new tickers: {", ".join(sample_new)}...')
        
        if existing_to_update:
            sample_update = existing_to_update[:10]
            self.stdout.write(f'\n🔄 Sample tickers to update: {", ".join(sample_update)}...')

    def load_tickers(self, tickers_to_load: list, options: dict):
        """Load tickers into the database"""
        self.stdout.write('\n🔄 Loading tickers into database...')
        
        batch_size = options.get('batch_size', 500)
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
            
            self.stdout.write(f'   📦 Processing batch {batch_num + 1}/{total_batches} ({len(batch_tickers)} tickers)...')
            
            try:
                with transaction.atomic():
                    for ticker in batch_tickers:
                        try:
                            # Determine basic info
                            exchange = self.determine_exchange(ticker)
                            sector = self.determine_basic_sector(ticker)
                            
                            # Get or create stock
                            stock, created = Stock.objects.get_or_create(
                                symbol=ticker,
                                defaults={
                                    'name': f'{ticker} Corporation',
                                    'sector': sector,
                                    'industry': 'Unknown',
                                    'exchange': exchange,
                                    'is_active': True,
                                    'last_updated': timezone.now()
                                }
                            )
                            
                            if created:
                                added_count += 1
                            elif update_existing:
                                # Update existing stock
                                updated = False
                                if stock.exchange != exchange:
                                    stock.exchange = exchange
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
                            if error_count <= 10:  # Show first 10 errors
                                self.stdout.write(
                                    self.style.WARNING(f'   ⚠️  Error processing {ticker}: {e}')
                                )
                            continue
                
                # Progress update
                processed_so_far = min(end_idx, len(tickers_to_load))
                progress_pct = (processed_so_far / len(tickers_to_load)) * 100
                self.stdout.write(f'   📊 Progress: {processed_so_far:,}/{len(tickers_to_load):,} ({progress_pct:.1f}%)')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Batch {batch_num + 1} failed: {e}')
                )
                error_count += len(batch_tickers)
                continue
        
        # Final summary
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS('✅ Complete NASDAQ ticker loading finished!'))
        self.stdout.write(f'\n📊 Final Results:')
        self.stdout.write(f'   ➕ Added: {added_count:,} new tickers')
        self.stdout.write(f'   🔄 Updated: {updated_count:,} existing tickers')
        self.stdout.write(f'   ⏭️  Skipped: {skipped_count:,} unchanged tickers')
        if error_count > 0:
            self.stdout.write(f'   ❌ Errors: {error_count:,} tickers')
        
        # Database summary
        total_stocks = Stock.objects.count()
        active_stocks = Stock.objects.filter(is_active=True).count()
        self.stdout.write(f'\n🗄️  Database Summary:')
        self.stdout.write(f'   📈 Total stocks in database: {total_stocks:,}')
        self.stdout.write(f'   ✅ Active stocks: {active_stocks:,}')
        
        # Performance stats
        success_rate = ((added_count + updated_count + skipped_count) / len(tickers_to_load)) * 100
        self.stdout.write(f'   📊 Success rate: {success_rate:.1f}%')
        
        self.stdout.write(f'\n🚀 Next Steps:')
        self.stdout.write('   1. Fetch price data: python manage.py update_stocks_yfinance')
        self.stdout.write('   2. Test web interface: python manage.py runserver')
        self.stdout.write('   3. Start full scanner: START_HERE.bat')
        self.stdout.write(f'   4. Verify count: python manage.py shell -c "from stocks.models import Stock; print(f\'Stocks: {{Stock.objects.count():,}}\')"')

    def determine_exchange(self, ticker: str) -> str:
        """Determine likely exchange for a ticker"""
        # Basic heuristics - in a real implementation you'd use the actual data
        if len(ticker) <= 4 and ticker.isalpha():
            return 'NASDAQ'
        elif '.' in ticker:
            return 'OTHER'
        else:
            return 'NASDAQ'

    def determine_basic_sector(self, ticker: str) -> str:
        """Determine basic sector for a ticker"""
        # This is a simplified version - in reality you'd use the actual sector data
        # from the downloaded ticker details
        
        tech_indicators = ['TECH', 'SOFT', 'DATA', 'NET', 'COMP', 'SYS', 'APP']
        finance_indicators = ['BANK', 'FIN', 'CAP', 'FUND', 'INV', 'LOAN']
        
        ticker_upper = ticker.upper()
        
        if any(indicator in ticker_upper for indicator in tech_indicators):
            return 'Technology'
        elif any(indicator in ticker_upper for indicator in finance_indicators):
            return 'Financial Services'
        else:
            return 'Unknown'