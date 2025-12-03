"""
Django Management Command: Ultra-Fast Stock Update
Wrapper for ultra_fast_yfinance_v3.py

Usage:
    python manage.py update_stocks_ultra_fast
    python manage.py update_stocks_ultra_fast --limit 1000
    python manage.py update_stocks_ultra_fast --test-mode
    python manage.py update_stocks_ultra_fast --symbols AAPL,GOOGL,MSFT
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from stocks.models import Stock
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

# Import the updater
from ultra_fast_yfinance_v3 import UltraFastStockUpdater, logger


class Command(BaseCommand):
    help = 'Ultra-fast stock data update (9,394 stocks in <180 seconds)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--symbols',
            type=str,
            help='Comma-separated list of stock symbols to update'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Maximum number of stocks to update'
        )
        parser.add_argument(
            '--test-mode',
            action='store_true',
            help='Test mode with 10 stocks (no time limit)'
        )
        parser.add_argument(
            '--exchange',
            type=str,
            choices=['NYSE', 'NASDAQ', 'ALL'],
            default='ALL',
            help='Filter by exchange (default: ALL)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )

    def handle(self, *args, **options):
        """Main command handler"""
        self.stdout.write("=" * 70)
        self.stdout.write("ULTRA-FAST STOCK UPDATE")
        self.stdout.write("=" * 70)

        # Get symbols to update
        symbols = self.get_symbols(options)

        if not symbols:
            raise CommandError("No symbols to update")

        self.stdout.write(f"Updating {len(symbols)} stocks...")

        # Create updater
        updater = UltraFastStockUpdater()

        # Run update
        try:
            updater.run_update(symbols=symbols)
            self.stdout.write(self.style.SUCCESS("[SUCCESS] Update complete!"))
        except Exception as e:
            raise CommandError(f"Update failed: {e}")

    def get_symbols(self, options) -> list:
        """Get list of symbols to update based on options"""

        # Test mode - just 10 stocks
        if options['test_mode']:
            self.stdout.write(self.style.WARNING("TEST MODE: Updating 10 stocks only"))
            return list(Stock.objects.all()[:10].values_list('ticker', flat=True))

        # Specific symbols provided
        if options['symbols']:
            symbols = [s.strip().upper() for s in options['symbols'].split(',')]
            self.stdout.write(f"Updating specific symbols: {', '.join(symbols)}")
            return symbols

        # Filter by exchange
        queryset = Stock.objects.all()

        if options['exchange'] and options['exchange'] != 'ALL':
            queryset = queryset.filter(exchange=options['exchange'])
            self.stdout.write(f"Filtering by exchange: {options['exchange']}")

        # Apply limit
        if options['limit']:
            queryset = queryset[:options['limit']]
            self.stdout.write(f"Limiting to {options['limit']} stocks")

        return list(queryset.values_list('ticker', flat=True))
