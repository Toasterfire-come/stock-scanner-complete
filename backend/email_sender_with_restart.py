#!/usr/bin/env python3
"""
Email Sender with Restart Capability - WORKING VERSION
Stock notifications email sender with scheduling and restart functionality
Command line options: -schedule, -test, -interval
Runs every 10 minutes in background with database integration
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
from collections import defaultdict

# Django imports for database integration
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings_production'))
django.setup()

from django.utils import timezone
from stocks.models import StockAlert
from emails.models import EmailSubscription
from emails.email_filter import EmailFilter
from emails.tasks import send_personalized_email

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_sender_with_restart.log'),
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
    parser = argparse.ArgumentParser(description='Email Sender with Restart Capability')
    parser.add_argument('-schedule', action='store_true', help='Run in scheduler mode (every 10 minutes)')
    parser.add_argument('-test', action='store_true', help='Test mode - process only a few alerts')
    parser.add_argument('-interval', type=int, default=10, help='Schedule interval in minutes (default: 10)')
    parser.add_argument('-max-alerts', type=int, default=None, help='Maximum number of alerts to process (for testing)')
    return parser.parse_args()

def send_stock_notifications_improved(args):
    """Enhanced version of send_stock_notifications with better error handling"""
    global shutdown_flag
    
    if shutdown_flag:
        return False
    
    try:
        logger.info("="*60)
        logger.info("STOCK EMAIL NOTIFICATIONS SENDER")
        logger.info("="*60)
        logger.info(f"Started: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Test mode: {'ON' if args.test else 'OFF'}")
        logger.info(f"Max alerts: {args.max_alerts or 'All'}")
        
        # Get new alerts
        new_alerts_query = StockAlert.objects.filter(sent=False)
        
        if args.max_alerts:
            new_alerts_query = new_alerts_query[:args.max_alerts]
            
        new_alerts = list(new_alerts_query)
        
        if not new_alerts:
            logger.info("No new stock alerts to send.")
            logger.info("="*60)
            return True
        
        logger.info(f"Found {len(new_alerts)} new alerts to process")
        
        # Initialize email filter
        email_filter = EmailFilter()
        category_map = defaultdict(list)
        processed_count = 0
        
        # Categorize alerts
        for alert in new_alerts:
            if shutdown_flag:
                break
                
            try:
                category = email_filter.filter_email(alert.note.lower() if alert.note else "")
                logger.debug(f"Category result: '{category}' from note: '{alert.note}'")
                
                if category != "Uncategorized":
                    category_map[category].append(alert)
                    processed_count += 1
                    
                    # Mark as sent
                    alert.sent = True
                    alert.save()
                    
            except Exception as e:
                logger.error(f"Error processing alert {alert.id}: {e}")
                continue
        
        logger.info(f"Categorized {processed_count} alerts into {len(category_map)} categories")
        
        # Send emails for each category
        total_emails_queued = 0
        
        for category, alerts in category_map.items():
            if shutdown_flag:
                break
                
            try:
                logger.info(f"Processing category: {category} ({len(alerts)} alerts)")
                
                # Get subscribers for this category
                subscribers = EmailSubscription.objects.filter(category=category, is_active=True)
                
                if not subscribers.exists():
                    logger.warning(f"No subscribers for category {category}")
                    continue
                
                logger.info(f"Found {subscribers.count()} subscribers for {category}")
                
                # Prepare stock list for email
                stock_list = []
                for alert in alerts:
                    try:
                        stock_data = {
                            "stock_symbol": alert.ticker,
                            "PRICE": str(alert.current_price),
                            "VOLUME": str(alert.volume_today),
                            "DVAV": str(alert.dvav or 0),
                            "DVSA": str(alert.dvsa or 0),
                        }
                        stock_list.append(stock_data)
                    except Exception as e:
                        logger.error(f"Error preparing stock data for alert {alert.id}: {e}")
                        continue
                
                if not stock_list:
                    logger.warning(f"No valid stock data for category {category}")
                    continue
                
                # Queue emails for subscribers
                for subscriber in subscribers:
                    if shutdown_flag:
                        break
                        
                    try:
                        if args.test and total_emails_queued >= 3:  # Limit in test mode
                            logger.info("Test mode: stopping after 3 emails")
                            break
                            
                        # Queue email
                        send_personalized_email.delay(
                            user_email=subscriber.email,
                            user_name=subscriber.email.split("@")[0],
                            category=category,
                            stock_list=stock_list
                        )
                        
                        total_emails_queued += 1
                        logger.info(f"Queued email for {subscriber.email} in category {category}")
                        
                    except Exception as e:
                        logger.error(f"Error queuing email for {subscriber.email}: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"Error processing category {category}: {e}")
                continue
        
        # Results
        logger.info("="*60)
        logger.info("EMAIL SENDING RESULTS")
        logger.info("="*60)
        logger.info(f"Alerts processed: {processed_count}")
        logger.info(f"Categories: {len(category_map)}")
        logger.info(f"Emails queued: {total_emails_queued}")
        
        for category, alerts in category_map.items():
            logger.info(f"  {category}: {len(alerts)} alerts")
        
        logger.info(f"Completed: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"Critical error in email sender: {e}")
        return False

def run_email_sender(args):
    """Run email sender with error handling"""
    try:
        return send_stock_notifications_improved(args)
    except Exception as e:
        logger.error(f"Error in email sender: {e}")
        return False

def main():
    """Main entry point"""
    args = parse_arguments()
    
    print("="*60)
    print("EMAIL SENDER WITH RESTART CAPABILITY")
    print("="*60)
    print(f"  Test Mode: {args.test}")
    print(f"  Max Alerts: {args.max_alerts or 'All'}")
    print(f"  Schedule Mode: {args.schedule}")
    print(f"  Interval: {args.interval} minutes")
    print("="*60)
    
    if args.schedule:
        print(f"\nSCHEDULER MODE: Running every {args.interval} minutes")
        print(f"Press Ctrl+C to stop the scheduler")
        print("="*60)
        
        # Schedule the job to run every N minutes
        schedule.every(args.interval).minutes.do(run_email_sender, args)
        
        # Run immediately on start
        logger.info("Running initial email sender...")
        run_email_sender(args)
        
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
        run_email_sender(args)
    
    print("\nEmail sender completed!")

if __name__ == "__main__":
    main()