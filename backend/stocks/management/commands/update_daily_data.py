"""
Management command to update daily stock fundamentals and technicals.
Run this once per day via cron or scheduler.

Usage:
    python manage.py update_daily_data                    # Update all stocks
    python manage.py update_daily_data --limit 100        # Update first 100 stocks
    python manage.py update_daily_data --ticker AAPL MSFT # Update specific tickers
"""
from django.core.management.base import BaseCommand
from stocks.services.daily_update_service import DailyUpdateService
import json


class Command(BaseCommand):
    help = 'Update daily stock fundamentals and valuation data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of stocks to update'
        )
        parser.add_argument(
            '--ticker',
            nargs='+',
            type=str,
            help='Specific ticker(s) to update'
        )
    
    def handle(self, *args, **options):
        service = DailyUpdateService()
        
        self.stdout.write(self.style.SUCCESS('Starting daily data update...'))
        
        if options['ticker']:
            # Update specific tickers
            tickers = [t.upper().strip() for t in options['ticker']]
            self.stdout.write(f"Updating {len(tickers)} specified ticker(s): {', '.join(tickers)}")
            summary = service.update_stock_list(tickers)
        else:
            # Update all or limited stocks
            limit = options['limit']
            if limit:
                self.stdout.write(f"Updating first {limit} stocks...")
            else:
                self.stdout.write("Updating all stocks...")
            summary = service.update_all_stocks(limit=limit)
        
        # Print summary
        self.stdout.write(self.style.SUCCESS('\n=== Update Summary ==='))
        self.stdout.write(f"Duration: {summary['duration_seconds']:.2f} seconds")
        self.stdout.write(f"Total stocks: {summary['total_stocks']}")
        self.stdout.write(self.style.SUCCESS(f"Updated: {summary['updated']}"))
        
        if summary['failed'] > 0:
            self.stdout.write(self.style.ERROR(f"Failed: {summary['failed']}"))
            self.stdout.write(self.style.WARNING(f"Success rate: {summary['success_rate']}"))
            
            if summary['errors']:
                self.stdout.write(self.style.ERROR('\nFirst errors:'))
                for error in summary['errors']:
                    self.stdout.write(self.style.ERROR(f"  - {error}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Success rate: {summary['success_rate']}"))
        
        self.stdout.write(self.style.SUCCESS('\nDaily update completed!'))
