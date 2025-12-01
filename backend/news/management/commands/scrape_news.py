"""
Django management command for scraping Yahoo Finance news
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from news.scraper import YahooFinanceNewsScraper
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scrape Yahoo Finance news with comprehensive rating'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Number of articles per feed (default: 50)'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test mode - only scrape 10 articles per feed'
        )

    def handle(self, *args, **options):
        """Main command handler"""
        self.stdout.write("=" * 60)
        self.stdout.write("YAHOO FINANCE NEWS SCRAPER")
        self.stdout.write("=" * 60)
        
        limit = 10 if options['test'] else options['limit']
        self.stdout.write(f"Limit per feed: {limit}")
        self.stdout.write(f"Test mode: {'ON' if options['test'] else 'OFF'}")
        self.stdout.write(f"Started: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Initialize scraper
        scraper = YahooFinanceNewsScraper()
        
        # Scrape articles
        self.stdout.write("\nScraping Yahoo Finance news...")
        articles = scraper.scrape_all_yahoo_feeds(limit_per_feed=limit)
        
        # Save to database
        self.stdout.write("Saving articles to database...")
        saved_count = scraper.save_to_database(articles)
        
        # Results
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("SCRAPING RESULTS")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Articles scraped: {len(articles)}")
        self.stdout.write(f"Articles saved: {saved_count}")
        
        # Show sentiment distribution
        grade_counts = {}
        for article in articles:
            grade = article.get('sentiment_grade', 'C')
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        self.stdout.write(f"\nSentiment Distribution:")
        for grade in ['A', 'B', 'C', 'D', 'F']:
            count = grade_counts.get(grade, 0)
            percentage = (count / len(articles) * 100) if articles else 0
            self.stdout.write(f"Grade {grade}: {count} articles ({percentage:.1f}%)")
        
        # Show high impact articles
        high_impact = [a for a in articles if a.get('impact_score', 0) >= 8]
        self.stdout.write(f"\nHigh Impact Articles (Score 8+): {len(high_impact)}")
        
        # Show major ticker articles
        major_ticker_articles = [a for a in articles if any(ticker in a.get('mentioned_tickers', '') for ticker in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'])]
        self.stdout.write(f"Articles mentioning major stocks: {len(major_ticker_articles)}")
        
        self.stdout.write(f"Completed: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write("=" * 60)