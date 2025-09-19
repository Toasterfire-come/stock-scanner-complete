#!/usr/bin/env python3
"""
News Scraper with Restart Capability - WORKING VERSION
Yahoo Finance News Scraper with scheduling and restart functionality
Command line options: -schedule, -test, -limit
Runs every 5 minutes in background with database integration
"""

import os
import sys
import time
import logging
import signal
import schedule
import threading
import argparse
from datetime import datetime

# Django imports for database integration
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings_production'))
django.setup()

from django.utils import timezone
from news.scraper import YahooFinanceNewsScraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_scraper_with_restart.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_flag = False

def signal_handler(signum, frame):
    """Handle interrupt signals gracefully"""
    global shutdown_flag
    print("\nReceived interrupt signal. Shutting down gracefully...")
    shutdown_flag = True

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='News Scraper with Restart Capability')
    parser.add_argument('-schedule', action='store_true', help='Run in scheduler mode (every 5 minutes)')
    parser.add_argument('-test', action='store_true', help='Test mode - only scrape 10 articles per feed')
    parser.add_argument('-limit', type=int, default=50, help='Number of articles per feed (default: 50)')
    parser.add_argument('-interval', type=int, default=5, help='Schedule interval in minutes (default: 5)')
    return parser.parse_args()

def run_news_scraper(args):
    """Run news scraper with error handling"""
    global shutdown_flag
    
    if shutdown_flag:
        return
    
    try:
        logger.info("="*60)
        logger.info("YAHOO FINANCE NEWS SCRAPER")
        logger.info("="*60)
        
        limit = 10 if args.test else args.limit
        logger.info(f"Limit per feed: {limit}")
        logger.info(f"Test mode: {'ON' if args.test else 'OFF'}")
        logger.info(f"Started: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Initialize scraper
        scraper = YahooFinanceNewsScraper()
        
        # Scrape articles
        logger.info("Scraping Yahoo Finance news...")
        articles = scraper.scrape_all_yahoo_feeds(limit_per_feed=limit)
        
        # Save to database
        logger.info("Saving articles to database...")
        saved_count = scraper.save_to_database(articles)
        
        # Results
        logger.info("="*60)
        logger.info("SCRAPING RESULTS")
        logger.info("="*60)
        logger.info(f"Articles scraped: {len(articles)}")
        logger.info(f"Articles saved: {saved_count}")
        
        # Show sentiment distribution
        grade_counts = {}
        for article in articles:
            grade = article.get('sentiment_grade', 'C')
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        logger.info("Sentiment Distribution:")
        for grade in ['A', 'B', 'C', 'D', 'F']:
            count = grade_counts.get(grade, 0)
            percentage = (count / len(articles) * 100) if articles else 0
            logger.info(f"Grade {grade}: {count} articles ({percentage:.1f}%)")
        
        # Show high impact articles
        high_impact = [a for a in articles if a.get('impact_score', 0) >= 8]
        logger.info(f"High Impact Articles (Score 8+): {len(high_impact)}")
        
        # Show major ticker articles
        major_ticker_articles = [a for a in articles if any(ticker in a.get('mentioned_tickers', '') for ticker in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'])]
        logger.info(f"Articles mentioning major stocks: {len(major_ticker_articles)}")
        
        logger.info(f"Completed: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"Error in news scraper: {e}")
        return False

def main():
    """Main entry point"""
    args = parse_arguments()
    
    print("="*60)
    print("NEWS SCRAPER WITH RESTART CAPABILITY")
    print("="*60)
    print(f"  Test Mode: {args.test}")
    print(f"  Limit per feed: {args.limit}")
    print(f"  Schedule Mode: {args.schedule}")
    print(f"  Interval: {args.interval} minutes")
    print("="*60)
    
    if args.schedule:
        print(f"\nSCHEDULER MODE: Running every {args.interval} minutes")
        print(f"Press Ctrl+C to stop the scheduler")
        print("="*60)
        
        # Schedule the job to run every N minutes
        schedule.every(args.interval).minutes.do(run_news_scraper, args)
        
        # Run immediately on start
        logger.info("Running initial news scraper...")
        run_news_scraper(args)
        
        try:
            while True:
                if shutdown_flag:
                    break
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nScheduler stopped by user")
            shutdown_flag = True
    else:
        # Run single update
        run_news_scraper(args)
    
    print("\nNews scraper completed!")

if __name__ == "__main__":
    main()