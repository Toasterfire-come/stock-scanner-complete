#!/usr/bin/env python3
"""
Standalone Financial News Scraper
Pulls news from multiple sources and saves to database
"""

import os
import sys
import django
import schedule
import time
import logging
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from news.scraper import NewsScraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_news_scrape():
    """Run the news scraper"""
    try:
        scraper = NewsScraper()
        
        print(f"\n{'='*60}")
        print(f"NEWS SCRAPING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Scrape articles
        articles = scraper.scrape_all_sources(limit_per_source=20)
        
        # Save to database
        saved_count = scraper.save_to_database(articles)
        
        print(f"\n{'='*60}")
        print("SCRAPING RESULTS")
        print(f"{'='*60}")
        print(f"Articles scraped: {len(articles)}")
        print(f"Articles saved: {saved_count}")
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        return saved_count
        
    except Exception as e:
        logger.error(f"Error in news scraping: {e}")
        return 0

def run_scheduler():
    """Run the news scraper on a schedule"""
    print("NEWS SCRAPER SCHEDULER")
    print("=" * 60)
    print("Schedule: Every 30 minutes")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    # Schedule news scraping every 30 minutes
    schedule.every(30).minutes.do(run_news_scrape)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nScheduler stopped by user")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Financial News Scraper')
    parser.add_argument('--schedule', action='store_true', help='Run on schedule (every 30 minutes)')
    parser.add_argument('--test', action='store_true', help='Test mode - scrape fewer articles')
    parser.add_argument('--limit', type=int, default=20, help='Articles per source (default: 20)')
    
    args = parser.parse_args()
    
    if args.schedule:
        run_scheduler()
    else:
        # Single run
        if args.test:
            # Test mode - reduce limits
            scraper = NewsScraper()
            articles = scraper.scrape_all_sources(limit_per_source=5)
            saved_count = scraper.save_to_database(articles)
            print(f"TEST MODE: Scraped {len(articles)} articles, saved {saved_count}")
        else:
            run_news_scrape()

if __name__ == "__main__":
    main()