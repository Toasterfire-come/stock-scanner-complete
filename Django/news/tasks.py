import logging
from celery import shared_task
from .scraper import YahooFinanceNewsScraper

logger = logging.getLogger(__name__)

@shared_task
def update_news_feed():
    logger.info("Running Yahoo Finance news scrape...")
    scraper = YahooFinanceNewsScraper()
    articles = scraper.scrape_all_yahoo_feeds(limit_per_feed=50)
    saved_count = scraper.save_to_database(articles)
    logger.info(f"News feed updated. Scraped {len(articles)} articles, saved {saved_count}.")
