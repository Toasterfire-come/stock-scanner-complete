"""
Django management command for scraping financial news
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from news.scraper import NewsScraper
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scrape financial news from multiple sources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Number of articles per source (default: 50)'
        )
        parser.add_argument(
            '--sources',
            type=str,
            help='Comma-separated list of sources to scrape (yahoo,reuters,marketwatch,cnbc)'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test mode - only scrape 5 articles per source'
        )

    def handle(self, *args, **options):
        """Main command handler"""
        self.stdout.write("=" * 60)
        self.stdout.write("FINANCIAL NEWS SCRAPER")
        self.stdout.write("=" * 60)
        
        limit = 5 if options['test'] else options['limit']
        self.stdout.write(f"Limit per source: {limit}")
        self.stdout.write(f"Test mode: {'ON' if options['test'] else 'OFF'}")
        self.stdout.write(f"Started: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Initialize scraper
        scraper = NewsScraper()
        
        # Scrape articles
        self.stdout.write("\nScraping news articles...")
        articles = scraper.scrape_all_sources(limit_per_source=limit)
        
        # Save to database
        self.stdout.write("Saving articles to database...")
        saved_count = scraper.save_to_database(articles)
        
        # Results
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("SCRAPING RESULTS")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Articles scraped: {len(articles)}")
        self.stdout.write(f"Articles saved: {saved_count}")
        self.stdout.write(f"Completed: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write("=" * 60)