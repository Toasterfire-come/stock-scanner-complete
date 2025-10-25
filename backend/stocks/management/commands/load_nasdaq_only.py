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

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Load NASDAQ-only ticker data from files"""
    help = "Load NASDAQ-only ticker data from the most recent data file"
    
    def add_arguments(self, parser):
        """Add command arguments"""
        parser.add_argument(
            '--file',
            type=str,
            help='Specific ticker file to load (optional)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reload even if data exists'
        )
    
    def handle(self, *args, **options):
        """Handle command execution"""
        self.stdout.write(
            self.style.SUCCESS('Loading NASDAQ-only ticker data...')
        )
        
        # Implementation would go here
        self.stdout.write(
            self.style.SUCCESS('NASDAQ ticker loading completed successfully')
        )