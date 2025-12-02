#!/usr/bin/env python
"""
Daily Data Scheduler - Runs daily fundamental updates at a scheduled time.

This script should be run as a daemon or via cron job.
Recommended: Run once per day at market close (e.g., 5:00 PM ET)

Cron example (run at 5 PM ET daily):
    0 17 * * * cd /app/backend && python daily_data_scheduler.py
"""
import os
import sys
import django
import logging
from datetime import datetime, time
import schedule
import time as time_module

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from stocks.services.daily_update_service import DailyUpdateService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/backend/logs/daily_update.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def run_daily_update():
    """Execute the daily update task."""
    logger.info("="*60)
    logger.info("Starting scheduled daily data update")
    logger.info(f"Time: {datetime.now().isoformat()}")
    logger.info("="*60)
    
    try:
        service = DailyUpdateService()
        summary = service.update_all_stocks()
        
        logger.info("Daily update completed successfully")
        logger.info(f"Summary: {summary['updated']} updated, {summary['failed']} failed")
        logger.info(f"Duration: {summary['duration_seconds']:.2f} seconds")
        
        if summary['errors']:
            logger.warning(f"Errors encountered: {len(summary['errors'])}")
            for error in summary['errors'][:5]:
                logger.warning(f"  {error}")
    
    except Exception as e:
        logger.error(f"Daily update failed with error: {str(e)}")
        raise


def run_scheduler():
    """Run the scheduler daemon."""
    logger.info("Daily data scheduler started")
    logger.info("Scheduled to run daily at 5:00 PM ET (market close)")
    
    # Schedule daily at 5:00 PM (17:00)
    schedule.every().day.at("17:00").do(run_daily_update)
    
    # Also run immediately on startup if it's after 5 PM
    now = datetime.now().time()
    if now > time(17, 0):
        logger.info("Running initial update (after 5 PM)")
        run_daily_update()
    
    # Keep running
    while True:
        schedule.run_pending()
        time_module.sleep(60)  # Check every minute


if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    os.makedirs('/app/backend/logs', exist_ok=True)
    
    # Check if running as one-time execution or daemon
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        logger.info("Running one-time update")
        run_daily_update()
    else:
        logger.info("Running as daemon")
        run_scheduler()
