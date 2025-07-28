"""
Django Management Command: Load All NASDAQ Ticker Symbols
Loads all 5,380+ NASDAQ ticker symbols into the database
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from stocks.models import Stock
import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Load all NASDAQ ticker symbols into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing stock records with new information'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS("LOADING ALL NASDAQ TICKER SYMBOLS"))
        self.stdout.write(self.style.SUCCESS("=" * 70))
        
        # Load NASDAQ tickers from CSV
        csv_file = Path(__file__).parent.parent.parent.parent / 'data' / 'complete_nasdaq' / 'complete_nasdaq_export_20250724_182723.csv'
        
        if not csv_file.exists():
            raise CommandError(f"CSV file not found: {csv_file}")
        
        nasdaq_tickers = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('Exchange', '').upper() == 'NASDAQ':
                        symbol = row.get('Symbol', '').strip()
                        name = row.get('Name', '').strip()
                        sector = row.get('Sector', '').strip() or 'Unknown'
                        
                        if symbol and len(symbol) <= 5:  # Filter out weird symbols
                            nasdaq_tickers.append({
                                'symbol': symbol,
                                'name': name,
                                'sector': sector,
                                'exchange': 'NASDAQ'
                            })
            
            self.stdout.write(f"[LOAD] Found {len(nasdaq_tickers):,} NASDAQ ticker symbols")
            
        except Exception as e:
            raise CommandError(f"Failed to load CSV file: {e}")
        
        if options['dry_run']:
            self.stdout.write(f"[DRY-RUN] Would create/update {len(nasdaq_tickers):,} NASDAQ stock records")
            self.stdout.write(f"[SAMPLE] First 10 tickers: {', '.join([t['symbol'] for t in nasdaq_tickers[:10]])}")
            return
        
        # Load tickers into database
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        self.stdout.write("[PROCESS] Loading tickers into database...")
        
        with transaction.atomic():
            for i, ticker_data in enumerate(nasdaq_tickers, 1):
                try:
                    stock, created = Stock.objects.get_or_create(
                        symbol=ticker_data['symbol'],
                        defaults={
                            'name': ticker_data['name'],
                            'sector': ticker_data['sector'],
                            'industry': 'Unknown',
                            'exchange': ticker_data['exchange'],
                            'is_active': True,
                            'created_at': timezone.now(),
                            'updated_at': timezone.now()
                        }
                    )
                    
                    if created:
                        created_count += 1
                        if created_count % 100 == 0:
                            self.stdout.write(f"[CREATE] Created {created_count} new stock records...")
                    else:
                        if options['update_existing']:
                            # Update existing record
                            stock.name = ticker_data['name']
                            stock.sector = ticker_data['sector']
                            stock.exchange = ticker_data['exchange']
                            stock.is_active = True
                            stock.updated_at = timezone.now()
                            stock.save()
                            updated_count += 1
                            if updated_count % 100 == 0:
                                self.stdout.write(f"[UPDATE] Updated {updated_count} existing stock records...")
                        else:
                            skipped_count += 1
                
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"[WARNING] Failed to process {ticker_data['symbol']}: {e}"))
                    continue
        
        # Results
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS("[RESULTS] NASDAQ TICKER LOADING COMPLETE"))
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(f"[SUCCESS] Created new stocks: {created_count:,}")
        if options['update_existing']:
            self.stdout.write(f"[SUCCESS] Updated existing stocks: {updated_count:,}")
        else:
            self.stdout.write(f"[INFO] Skipped existing stocks: {skipped_count:,}")
        self.stdout.write(f"[TOTAL] Total NASDAQ stocks in database: {Stock.objects.filter(exchange__iexact='NASDAQ').count():,}")
        
        # Verify database state
        total_stocks = Stock.objects.count()
        nasdaq_stocks = Stock.objects.filter(exchange__iexact='NASDAQ').count()
        
        self.stdout.write("=" * 70)
        self.stdout.write("[DATABASE STATUS]")
        self.stdout.write(f"[STATS] Total stocks in database: {total_stocks:,}")
        self.stdout.write(f"[STATS] NASDAQ stocks in database: {nasdaq_stocks:,}")
        self.stdout.write(f"[STATS] NASDAQ percentage: {(nasdaq_stocks/total_stocks*100):.1f}%")
        
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS("✅ NASDAQ TICKER LIST UPDATED TO MAXIMUM!"))
        self.stdout.write(self.style.SUCCESS("🎯 Ready to update stock data with:"))
        self.stdout.write(self.style.SUCCESS(f"   python3 manage.py update_stocks_yfinance --nasdaq-only --limit {nasdaq_stocks}"))
        self.stdout.write(self.style.SUCCESS("=" * 70))
