#!/usr/bin/env python3
"""
Daily Market Updater - Runs at 9 AM ET every market day
Integrates proxy updates and stock retrieval with market hours
"""

import os
import sys
import time
import logging
import subprocess
import signal
import schedule
import threading
from datetime import datetime, timedelta
from pathlib import Path
import pytz

# Setup logging with rotation
from logging.handlers import RotatingFileHandler

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handlers
file_handler = RotatingFileHandler(
    'daily_market_updater.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
console_handler = logging.StreamHandler()

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.propagate = False

# Global shutdown flag
shutdown_flag = False


def signal_handler(signum, frame):
    """Handle interrupt signals gracefully"""
    global shutdown_flag
    logger.info("Received interrupt signal. Shutting down gracefully...")
    shutdown_flag = True


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class DailyMarketUpdater:
    """Manages daily updates at 9 AM ET"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.python_exe = sys.executable
        self.eastern_tz = pytz.timezone('US/Eastern')
        
        # Update times (ET)
        self.proxy_update_time = "08:45"  # 8:45 AM - Update proxies before market
        self.stock_update_time = "09:00"  # 9:00 AM - Main stock update
        self.market_open_time = "09:30"   # 9:30 AM - Market opens
        
        # Track last run dates to avoid duplicate runs
        self.last_proxy_update = None
        self.last_stock_update = None
        
        # Process tracking
        self.running_processes = {}
    
    def is_market_day(self, date=None):
        """Check if it's a market day (Monday-Friday, excluding holidays)"""
        if date is None:
            date = datetime.now(self.eastern_tz)
        
        # Check if it's a weekday
        if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # TODO: Add holiday checking (can integrate with pandas_market_calendars)
        # For now, just check weekdays
        return True
    
    def get_current_et_time(self):
        """Get current time in Eastern timezone"""
        return datetime.now(self.eastern_tz)
    
    def run_proxy_update(self):
        """Run proxy scraper and validator"""
        try:
            current_time = self.get_current_et_time()
            
            # Check if already run today
            if self.last_proxy_update and self.last_proxy_update.date() == current_time.date():
                logger.info("Proxy update already run today, skipping...")
                return
            
            logger.info("="*60)
            logger.info(f"DAILY PROXY UPDATE - {current_time.strftime('%Y-%m-%d %H:%M:%S ET')}")
            logger.info("="*60)
            
            # Run integrated proxy manager with GitHub repos for comprehensive coverage
            cmd = [
                self.python_exe,
                str(self.project_root / 'integrated_proxy_manager.py'),
                '-threads', '100',  # More threads for faster validation
                '-timeout', '5',    # Shorter timeout for speed
                '-github'           # Include GitHub repos
            ]
            
            logger.info(f"Running command: {' '.join(cmd)}")
            
            # Run and wait for completion
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=str(self.project_root)
            )
            
            # Stream output
            for line in process.stdout:
                logger.info(f"[PROXY] {line.rstrip()}")
            
            process.wait()
            
            if process.returncode == 0:
                logger.info("Proxy update completed successfully")
                self.last_proxy_update = current_time
            else:
                logger.error(f"Proxy update failed with code {process.returncode}")
            
        except Exception as e:
            logger.error(f"Error running proxy update: {e}")
    
    def run_stock_update(self):
        """Run enhanced stock retrieval with integrated proxy manager"""
        try:
            current_time = self.get_current_et_time()
            
            # Check if already run today
            if self.last_stock_update and self.last_stock_update.date() == current_time.date():
                logger.info("Stock update already run today, skipping...")
                return
            
            logger.info("="*60)
            logger.info(f"DAILY STOCK UPDATE - {current_time.strftime('%Y-%m-%d %H:%M:%S ET')}")
            logger.info("="*60)
            
            # Run integrated stock retrieval
            cmd = [
                self.python_exe,
                str(self.project_root / 'enhanced_stock_retrieval_integrated.py'),
                '-threads', '20',     # Balanced thread count
                '-timeout', '10',     # Standard timeout
                '-save-to-db'        # Save to database
            ]
            
            # Add test flag if in development
            if os.getenv('TEST_MODE', 'false').lower() == 'true':
                cmd.append('-test')
            
            logger.info(f"Running command: {' '.join(cmd)}")
            
            # Run and wait for completion
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=str(self.project_root)
            )
            
            # Stream output
            for line in process.stdout:
                logger.info(f"[STOCK] {line.rstrip()}")
            
            process.wait()
            
            if process.returncode == 0:
                logger.info("Stock update completed successfully")
                self.last_stock_update = current_time
            else:
                logger.error(f"Stock update failed with code {process.returncode}")
            
        except Exception as e:
            logger.error(f"Error running stock update: {e}")
    
    def run_news_update(self):
        """Run news scraper update"""
        try:
            current_time = self.get_current_et_time()
            
            logger.info("="*60)
            logger.info(f"DAILY NEWS UPDATE - {current_time.strftime('%Y-%m-%d %H:%M:%S ET')}")
            logger.info("="*60)
            
            # Check if news scraper exists
            news_script = self.project_root / 'news_scraper_with_restart.py'
            if not news_script.exists():
                logger.warning("News scraper not found, skipping...")
                return
            
            # Run news scraper (single cycle)
            cmd = [
                self.python_exe,
                str(news_script),
                '-limit', '50'  # Get top 50 news items
            ]
            
            logger.info(f"Running command: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=str(self.project_root)
            )
            
            # Stream output
            for line in process.stdout:
                logger.info(f"[NEWS] {line.rstrip()}")
            
            process.wait()
            
            if process.returncode == 0:
                logger.info("News update completed successfully")
            else:
                logger.error(f"News update failed with code {process.returncode}")
            
        except Exception as e:
            logger.error(f"Error running news update: {e}")
    
    def run_email_notifications(self):
        """Send daily email notifications"""
        try:
            current_time = self.get_current_et_time()
            
            logger.info("="*60)
            logger.info(f"DAILY EMAIL NOTIFICATIONS - {current_time.strftime('%Y-%m-%d %H:%M:%S ET')}")
            logger.info("="*60)
            
            # Check if email sender exists
            email_script = self.project_root / 'email_sender_with_restart.py'
            if not email_script.exists():
                logger.warning("Email sender not found, skipping...")
                return
            
            # Run email sender (single cycle)
            cmd = [
                self.python_exe,
                str(email_script)
            ]
            
            logger.info(f"Running command: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=str(self.project_root)
            )
            
            # Stream output
            for line in process.stdout:
                logger.info(f"[EMAIL] {line.rstrip()}")
            
            process.wait()
            
            if process.returncode == 0:
                logger.info("Email notifications sent successfully")
            else:
                logger.error(f"Email notifications failed with code {process.returncode}")
            
        except Exception as e:
            logger.error(f"Error sending email notifications: {e}")
    
    def daily_9am_update(self):
        """Main daily update routine at 9 AM"""
        current_time = self.get_current_et_time()
        
        # Check if it's a market day
        if not self.is_market_day(current_time):
            logger.info(f"Not a market day ({current_time.strftime('%A')}), skipping daily update")
            return
        
        logger.info("="*70)
        logger.info(f"STARTING DAILY 9 AM MARKET UPDATE")
        logger.info(f"Time: {current_time.strftime('%Y-%m-%d %H:%M:%S ET')}")
        logger.info("="*70)
        
        # Run updates in sequence
        # 1. Stock update with integrated proxies
        self.run_stock_update()
        
        # 2. News update
        self.run_news_update()
        
        # 3. Email notifications
        self.run_email_notifications()
        
        logger.info("="*70)
        logger.info("DAILY 9 AM UPDATE COMPLETED")
        logger.info("="*70)
    
    def daily_845am_proxy_update(self):
        """Proxy update at 8:45 AM before market activities"""
        current_time = self.get_current_et_time()
        
        # Check if it's a market day
        if not self.is_market_day(current_time):
            logger.info(f"Not a market day ({current_time.strftime('%A')}), skipping proxy update")
            return
        
        logger.info("="*70)
        logger.info(f"STARTING DAILY 8:45 AM PROXY UPDATE")
        logger.info(f"Time: {current_time.strftime('%Y-%m-%d %H:%M:%S ET')}")
        logger.info("="*70)
        
        self.run_proxy_update()
        
        logger.info("="*70)
        logger.info("PROXY UPDATE COMPLETED")
        logger.info("="*70)
    
    def run_scheduler(self):
        """Run the daily scheduler"""
        logger.info("Daily Market Updater Started")
        logger.info(f"Proxy Update Time: {self.proxy_update_time} ET")
        logger.info(f"Stock Update Time: {self.stock_update_time} ET")
        logger.info("Scheduler is running. Press Ctrl+C to stop.")
        
        # Schedule daily tasks
        schedule.every().day.at(self.proxy_update_time).do(self.daily_845am_proxy_update)
        schedule.every().day.at(self.stock_update_time).do(self.daily_9am_update)
        
        # Run immediately if within market hours and haven't run today
        current_time = self.get_current_et_time()
        current_time_str = current_time.strftime("%H:%M")
        
        if self.is_market_day(current_time):
            # Check if we should run proxy update
            if current_time_str >= self.proxy_update_time and not self.last_proxy_update:
                logger.info("Running immediate proxy update...")
                self.daily_845am_proxy_update()
            
            # Check if we should run stock update
            if current_time_str >= self.stock_update_time and not self.last_stock_update:
                logger.info("Running immediate stock update...")
                self.daily_9am_update()
        
        # Main scheduler loop
        while not shutdown_flag:
            try:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
                
                # Log heartbeat every hour
                if datetime.now().minute == 0 and datetime.now().second < 30:
                    current_et = self.get_current_et_time()
                    logger.info(f"Scheduler heartbeat: {current_et.strftime('%Y-%m-%d %H:%M:%S ET')}")
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)  # Wait a minute before retrying
    
    def run_once(self):
        """Run all updates once (for testing or manual execution)"""
        logger.info("Running daily updates once...")
        
        # Run proxy update first
        self.run_proxy_update()
        
        # Then run main update
        self.daily_9am_update()
        
        logger.info("One-time update completed")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Daily Market Updater')
    parser.add_argument('-schedule', action='store_true', 
                       help='Run in scheduler mode (default)')
    parser.add_argument('-once', action='store_true', 
                       help='Run all updates once and exit')
    parser.add_argument('-proxy-only', action='store_true',
                       help='Run proxy update only')
    parser.add_argument('-stock-only', action='store_true',
                       help='Run stock update only')
    
    args = parser.parse_args()
    
    # Create updater instance
    updater = DailyMarketUpdater()
    
    try:
        if args.once:
            updater.run_once()
        elif args.proxy_only:
            updater.run_proxy_update()
        elif args.stock_only:
            updater.run_stock_update()
        else:
            # Default: run scheduler
            updater.run_scheduler()
    
    except KeyboardInterrupt:
        logger.info("Updater stopped by user")
    except Exception as e:
        logger.error(f"Updater error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()