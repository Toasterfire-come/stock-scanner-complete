#!/usr/bin/env python3
"""
Django Management Command: Load NASDAQ Tickers
Loads the comprehensive NASDAQ ticker list into the Stock Scanner database.

Usage:
    python manage.py load_nasdaq_tickers
    python manage.py load_nasdaq_tickers --update-existing
    python manage.py load_nasdaq_tickers --dry-run

Author: Stock Scanner Project
Version: 2.0.0
"""

import sys
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from stocks.models import Stock

# Add project root to path to import ticker data
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

try:
    from data.nasdaq_tickers_comprehensive import (
        get_all_tickers, 
        get_stock_scanner_format,
        get_sector_summary,
        NASDAQ_100_TICKERS,
        NYSE_BLUE_CHIPS,
        TECH_GROWTH_TICKERS,
        MAJOR_ETFS,
        CRYPTO_FINTECH_TICKERS,
        MEME_RETAIL_TICKERS,
        EV_CLEAN_ENERGY_TICKERS,
        BIOTECH_HEALTHCARE_TICKERS,
        FINANCIAL_TICKERS,
        ENERGY_TICKERS,
        REIT_TICKERS,
        CONSUMER_TICKERS
    )
except ImportError as e:
    print(f"Error importing ticker data: {e}")
    sys.exit(1)

class Command(BaseCommand):
    help = 'Load comprehensive NASDAQ ticker list into Stock Scanner database'

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
            '--sector',
            type=str,
            help='Only load tickers from specific sector (technology, finance, healthcare, etc.)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of tickers to load (for testing)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🎯 Loading Comprehensive NASDAQ Ticker List')
        )
        self.stdout.write('=' * 70)
        
        try:
            # Get ticker data
            if options['sector']:
                sector_map = {
                    'nasdaq100': NASDAQ_100_TICKERS,
                    'nyse': NYSE_BLUE_CHIPS,
                    'technology': TECH_GROWTH_TICKERS,
                    'etfs': MAJOR_ETFS,
                    'crypto': CRYPTO_FINTECH_TICKERS,
                    'meme': MEME_RETAIL_TICKERS,
                    'ev': EV_CLEAN_ENERGY_TICKERS,
                    'healthcare': BIOTECH_HEALTHCARE_TICKERS,
                    'finance': FINANCIAL_TICKERS,
                    'energy': ENERGY_TICKERS,
                    'reits': REIT_TICKERS,
                    'consumer': CONSUMER_TICKERS
                }
                
                sector_key = options['sector'].lower()
                if sector_key not in sector_map:
                    raise CommandError(f"Unknown sector: {options['sector']}. Available: {', '.join(sector_map.keys())}")
                
                tickers_to_load = sector_map[sector_key]
                self.stdout.write(f"📊 Loading {options['sector']} sector: {len(tickers_to_load)} tickers")
            else:
                tickers_to_load = get_all_tickers()
                self.stdout.write(f"📊 Loading all tickers: {len(tickers_to_load)} total")
            
            # Apply limit if specified
            if options['limit']:
                tickers_to_load = tickers_to_load[:options['limit']]
                self.stdout.write(f"📊 Limited to first {options['limit']} tickers")
            
            # Show summary
            self.show_summary()
            
            # Process tickers
            if options['dry_run']:
                self.stdout.write(self.style.WARNING('\n🔍 DRY RUN MODE - No changes will be made'))
                self.dry_run_analysis(tickers_to_load, options['update_existing'])
            else:
                self.load_tickers(tickers_to_load, options['update_existing'])
            
        except Exception as e:
            raise CommandError(f'Error loading tickers: {e}')

    def show_summary(self):
        """Display summary of available tickers"""
        self.stdout.write('\n📈 Ticker Summary:')
        
        summary = get_sector_summary()
        for category, count in summary.items():
            if category == 'Total Unique':
                self.stdout.write(f'   🎯 {category}: {count:,}')
            else:
                self.stdout.write(f'   • {category}: {count:,}')

    def dry_run_analysis(self, tickers_to_load, update_existing):
        """Analyze what would be done without making changes"""
        self.stdout.write('\n🔍 Analyzing ticker data...')
        
        existing_tickers = set(Stock.objects.values_list('symbol', flat=True))
        new_tickers = []
        existing_to_update = []
        
        for ticker in tickers_to_load:
            if ticker in existing_tickers:
                if update_existing:
                    existing_to_update.append(ticker)
            else:
                new_tickers.append(ticker)
        
        self.stdout.write(f'\n📊 Analysis Results:')
        self.stdout.write(f'   ➕ New tickers to add: {len(new_tickers):,}')
        self.stdout.write(f'   🔄 Existing tickers to update: {len(existing_to_update):,}')
        self.stdout.write(f'   ⏭️  Existing tickers to skip: {len(existing_tickers & set(tickers_to_load)) - len(existing_to_update):,}')
        
        if new_tickers:
            self.stdout.write(f'\n🆕 Sample new tickers:')
            sample_new = new_tickers[:10]
            self.stdout.write(f'   {", ".join(sample_new)}...')
        
        if existing_to_update:
            self.stdout.write(f'\n🔄 Sample tickers to update:')
            sample_update = existing_to_update[:10]
            self.stdout.write(f'   {", ".join(sample_update)}...')

    def load_tickers(self, tickers_to_load, update_existing):
        """Load tickers into the database"""
        self.stdout.write('\n🔄 Loading tickers into database...')
        
        added_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        with transaction.atomic():
            for i, ticker in enumerate(tickers_to_load):
                try:
                    # Determine sector and exchange
                    sector, exchange = self.determine_sector_exchange(ticker)
                    
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
                        if added_count % 50 == 0:
                            self.stdout.write(f'   📊 Added {added_count} tickers...')
                    elif update_existing:
                        # Update existing stock
                        updated = False
                        if stock.sector != sector:
                            stock.sector = sector
                            updated = True
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
                    self.stdout.write(
                        self.style.WARNING(f'   ⚠️  Error processing {ticker}: {e}')
                    )
                    continue
        
        # Final summary
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('✅ Ticker loading completed!'))
        self.stdout.write(f'\n📊 Results:')
        self.stdout.write(f'   ➕ Added: {added_count:,} new tickers')
        self.stdout.write(f'   🔄 Updated: {updated_count:,} existing tickers')
        self.stdout.write(f'   ⏭️  Skipped: {skipped_count:,} unchanged tickers')
        if error_count > 0:
            self.stdout.write(f'   ❌ Errors: {error_count:,} tickers')
        
        # Database summary
        total_stocks = Stock.objects.count()
        active_stocks = Stock.objects.filter(is_active=True).count()
        self.stdout.write(f'\n🗄️  Database totals:')
        self.stdout.write(f'   📈 Total stocks: {total_stocks:,}')
        self.stdout.write(f'   ✅ Active stocks: {active_stocks:,}')
        
        self.stdout.write(f'\n🚀 Next steps:')
        self.stdout.write('   1. Run: python manage.py update_stocks_yfinance')
        self.stdout.write('   2. Test: python manage.py shell -c "from stocks.models import Stock; print(Stock.objects.count())"')
        self.stdout.write('   3. Start scanner: ./start_stock_scanner.sh')

    def determine_sector_exchange(self, ticker):
        """Determine sector and exchange for a ticker"""
        sector = 'Unknown'
        exchange = 'NASDAQ'
        
        # Check sector based on which lists the ticker appears in
        if ticker in TECH_GROWTH_TICKERS or ticker in NASDAQ_100_TICKERS:
            if ticker in ['AAPL', 'MSFT', 'GOOGL', 'GOOG', 'META', 'NVDA', 'AMD', 'INTC']:
                sector = 'Technology'
            elif ticker in ['AMZN', 'COST', 'SBUX', 'HD', 'LOW']:
                sector = 'Consumer Discretionary'
            else:
                sector = 'Technology'
        elif ticker in FINANCIAL_TICKERS:
            sector = 'Financial Services'
        elif ticker in BIOTECH_HEALTHCARE_TICKERS:
            sector = 'Healthcare'
        elif ticker in ENERGY_TICKERS:
            sector = 'Energy'
        elif ticker in CONSUMER_TICKERS:
            sector = 'Consumer Goods'
        elif ticker in REIT_TICKERS:
            sector = 'Real Estate'
        elif ticker in EV_CLEAN_ENERGY_TICKERS:
            sector = 'Clean Energy'
        elif ticker in CRYPTO_FINTECH_TICKERS:
            if ticker in ['COIN', 'MSTR', 'RIOT', 'MARA']:
                sector = 'Cryptocurrency'
            else:
                sector = 'Financial Technology'
        elif ticker in MAJOR_ETFS:
            sector = 'ETF'
        
        # Determine exchange
        if ticker in NYSE_BLUE_CHIPS:
            exchange = 'NYSE'
        elif ticker in MAJOR_ETFS:
            exchange = 'ARCA'
        elif ticker.startswith('BTC') or ticker.startswith('ETH'):
            exchange = 'CRYPTO'
        
        return sector, exchange