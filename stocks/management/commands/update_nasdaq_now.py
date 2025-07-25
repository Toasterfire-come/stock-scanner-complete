#!/usr/bin/env python3
"""
Django Management Command: Update NASDAQ Data Now
Manually trigger a NASDAQ data update (same as the scheduled updates)

Usage:
    python manage.py update_nasdaq_now

Author: Stock Scanner Project
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
import time


class Command(BaseCommand):
    help = 'Manually update NASDAQ stock data and news (same as scheduled updates)'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔄 Starting manual NASDAQ data update...')
        )
        
        start_time = time.time()
        
        try:
            # Update NASDAQ stock prices
            self.stdout.write('📈 Updating NASDAQ stock prices...')
            call_command('update_stocks_yfinance')
            
            # Update news data
            self.stdout.write('📰 Updating news data...')
            from news.scraper import update_news_data
            success = update_news_data()
            
            if success:
                self.stdout.write('✅ News data updated successfully')
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️ News data updated with warnings')
                )
            
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ NASDAQ data update completed in {elapsed_time:.2f} seconds'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error updating NASDAQ data: {e}')
            )
            raise