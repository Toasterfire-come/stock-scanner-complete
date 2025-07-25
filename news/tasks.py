import logging
from celery import shared_task
from . import scraper

logger = logging.getLogger(__name__)

@shared_task
def update_news_feed():
    logger.info("Running hourly news scrape...")
    scraper.main()
    logger.info("News feed updated.")
