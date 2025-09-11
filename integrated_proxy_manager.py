#!/usr/bin/env python3
"""
Integrated Proxy Manager with Database Support
Manages proxy scraping, validation, and integration with stock retrieval
"""

import os
import sys
import time
import json
import argparse
import logging
import signal
import schedule
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from logging.handlers import RotatingFileHandler

# Import proxy scraper and utilities
from proxy_scraper_validator import (
    scrape_all_sources,
    validate_proxies,
    deduplicate_proxies,
    normalize_proxy_string
)
from utils.proxy_utils import ProxyManager, save_proxy_stats

# Django imports for database integration (optional)
try:
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
    django.setup()
    from django.db import models
    DJANGO_AVAILABLE = True
    
    # Define Proxy model if Django is available
    from django.apps import apps
    if not apps.is_installed('proxies'):
        DJANGO_AVAILABLE = False
except ImportError:
    DJANGO_AVAILABLE = False
    models = None

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(
    'integrated_proxy_manager.log',
    maxBytes=10*1024*1024,
    backupCount=5
)
console_handler = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

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

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class IntegratedProxyManager:
    """Integrated proxy manager with scraping, validation, and stock integration"""
    
    def __init__(self, 
                 output_file: str = 'working_proxies.json',
                 threads: int = 50,
                 timeout: int = 10,
                 max_response_time: float = 5.0,
                 min_success_rate: float = 0.6,
                 include_github: bool = True):
        """Initialize integrated proxy manager"""
        self.output_file = output_file
        self.threads = threads
        self.timeout = timeout
        self.max_response_time = max_response_time
        self.min_success_rate = min_success_rate
        self.include_github = include_github
        
        # Initialize proxy manager
        self.proxy_manager = ProxyManager(
            proxy_file=output_file,
            max_response_time=max_response_time
        )
        
        # Statistics
        self.stats = {
            'last_scrape': None,
            'last_validation': None,
            'total_scraped': 0,
            'total_validated': 0,
            'total_working': 0,
            'scrape_sources': {},
            'validation_history': []
        }
        
        # Load existing stats if available
        self.load_stats()
    
    def load_stats(self):
        """Load statistics from file"""
        stats_file = 'proxy_manager_stats.json'
        try:
            if os.path.exists(stats_file):
                with open(stats_file, 'r') as f:
                    self.stats.update(json.load(f))
                logger.info(f"Loaded stats from {stats_file}")
        except Exception as e:
            logger.warning(f"Error loading stats: {e}")
    
    def save_stats(self):
        """Save statistics to file"""
        stats_file = 'proxy_manager_stats.json'
        try:
            with open(stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
            logger.info(f"Saved stats to {stats_file}")
        except Exception as e:
            logger.error(f"Error saving stats: {e}")
    
    def scrape_and_validate(self) -> Dict:
        """Complete scrape and validation cycle"""
        logger.info("="*60)
        logger.info(f"PROXY SCRAPE & VALIDATE CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*60)
        
        # Scrape proxies
        logger.info("Phase 1: Scraping proxies from all sources...")
        all_proxies = scrape_all_sources(include_github=self.include_github)
        
        # Update stats
        self.stats['last_scrape'] = datetime.now().isoformat()
        self.stats['total_scraped'] = len(all_proxies)
        
        # Save all scraped proxies
        with open('all_scraped_proxies.json', 'w') as f:
            json.dump(all_proxies, f, indent=2)
        logger.info(f"Saved {len(all_proxies)} scraped proxies")
        
        if not all_proxies:
            logger.error("No proxies scraped!")
            return {'success': False, 'error': 'No proxies scraped'}
        
        # Validate proxies
        logger.info("Phase 2: Validating proxies...")
        
        # Create args object for validate_proxies function
        class Args:
            pass
        
        args = Args()
        args.threads = self.threads
        args.timeout = self.timeout
        args.max_response_time = self.max_response_time
        
        working_proxies = validate_proxies(all_proxies, args)
        
        # Update stats
        self.stats['last_validation'] = datetime.now().isoformat()
        self.stats['total_validated'] = len(all_proxies)
        self.stats['total_working'] = len(working_proxies)
        
        # Add to validation history
        validation_result = {
            'timestamp': datetime.now().isoformat(),
            'total_scraped': len(all_proxies),
            'total_working': len(working_proxies),
            'success_rate': (len(working_proxies) / len(all_proxies) * 100) if all_proxies else 0
        }
        self.stats['validation_history'].append(validation_result)
        
        # Keep only last 100 validation results
        if len(self.stats['validation_history']) > 100:
            self.stats['validation_history'] = self.stats['validation_history'][-100:]
        
        # Save working proxies
        self.save_working_proxies(working_proxies)
        
        # Save stats
        self.save_stats()
        
        # Update proxy manager with new proxies
        self.proxy_manager.load_proxies(reload=True)
        
        # Summary
        logger.info("="*60)
        logger.info("CYCLE RESULTS")
        logger.info("="*60)
        logger.info(f"Total Scraped: {len(all_proxies)}")
        logger.info(f"Working Proxies: {len(working_proxies)}")
        if all_proxies:
            logger.info(f"Success Rate: {validation_result['success_rate']:.1f}%")
        
        if working_proxies:
            avg_response = sum(p['response_time'] for p in working_proxies) / len(working_proxies)
            logger.info(f"Avg Response Time: {avg_response:.2f}s")
            logger.info(f"Best Proxy: {working_proxies[0]['proxy']} ({working_proxies[0]['response_time']:.2f}s)")
        
        logger.info("="*60)
        
        return {
            'success': True,
            'total_scraped': len(all_proxies),
            'total_working': len(working_proxies),
            'success_rate': validation_result['success_rate']
        }
    
    def save_working_proxies(self, working_proxies: List[Dict]):
        """Save working proxies in multiple formats"""
        # Save detailed format
        with open(self.output_file, 'w') as f:
            json.dump(working_proxies, f, indent=2)
        
        # Save simple list format (for compatibility with stock scraper)
        simple_list = [p['proxy'] for p in working_proxies]
        simple_file = self.output_file.replace('.json', '_simple.json')
        with open(simple_file, 'w') as f:
            json.dump(simple_list, f, indent=2)
        
        # Save as text file (one proxy per line)
        text_file = self.output_file.replace('.json', '.txt')
        with open(text_file, 'w') as f:
            for proxy in simple_list:
                f.write(f"{proxy}\n")
        
        logger.info(f"Saved {len(working_proxies)} working proxies in multiple formats")
        
        # Save to database if available
        if DJANGO_AVAILABLE:
            self.save_to_database(working_proxies)
    
    def save_to_database(self, working_proxies: List[Dict]):
        """Save proxies to Django database"""
        try:
            # Dynamic model creation if not exists
            from django.db import connection
            from django.db import models
            
            # Check if proxies app exists, if not, create a simple model
            cursor = connection.cursor()
            
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS proxy_list (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proxy VARCHAR(255) UNIQUE,
                    response_time FLOAT,
                    last_validated DATETIME,
                    success_rate FLOAT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert or update proxies
            for proxy_data in working_proxies:
                cursor.execute("""
                    INSERT OR REPLACE INTO proxy_list 
                    (proxy, response_time, last_validated, success_rate, is_active, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    proxy_data['proxy'],
                    proxy_data.get('response_time', 0),
                    proxy_data.get('last_validated', datetime.now()),
                    proxy_data.get('success_rate', 1.0),
                    True,
                    datetime.now()
                ))
            
            connection.commit()
            logger.info(f"Saved {len(working_proxies)} proxies to database")
        except Exception as e:
            logger.warning(f"Error saving to database: {e}")
    
    def get_proxy_for_stock_scraper(self) -> Optional[str]:
        """Get a healthy proxy for stock scraper"""
        return self.proxy_manager.get_healthy_proxy()
    
    def mark_proxy_result(self, proxy: str, success: bool, response_time: Optional[float] = None):
        """Mark proxy result from stock scraper"""
        if success:
            self.proxy_manager.mark_proxy_success(proxy, response_time)
        else:
            self.proxy_manager.mark_proxy_failure(proxy, "Stock scraper failure")
    
    def get_stats_summary(self) -> Dict:
        """Get summary of proxy statistics"""
        proxy_stats = self.proxy_manager.get_proxy_stats()
        
        return {
            'manager_stats': self.stats,
            'proxy_health': proxy_stats,
            'last_update': self.stats.get('last_validation'),
            'total_proxies': proxy_stats['total_proxies'],
            'healthy_proxies': proxy_stats['healthy_proxies'],
            'success_rate': proxy_stats['success_rate']
        }
    
    def run_maintenance(self):
        """Run maintenance tasks"""
        logger.info("Running proxy maintenance...")
        
        # Test all current proxies
        test_results = self.proxy_manager.batch_test_proxies(num_threads=20)
        
        # Filter out non-working proxies
        working = [proxy for proxy, result in test_results.items() if result['working']]
        
        logger.info(f"Maintenance: {len(working)}/{len(test_results)} proxies working")
        
        # Update proxy file if needed
        if len(working) < len(test_results) * 0.5:
            # Less than 50% working, trigger new scrape
            logger.warning("Less than 50% proxies working, triggering new scrape...")
            self.scrape_and_validate()
        else:
            # Just update the file with working proxies
            working_proxies = [
                {
                    'proxy': proxy,
                    'response_time': test_results[proxy]['response_time'],
                    'last_validated': test_results[proxy]['tested_at']
                }
                for proxy in working
            ]
            self.save_working_proxies(working_proxies)


def create_stock_integration_wrapper():
    """Create wrapper for stock scraper integration"""
    
    class ProxyProvider:
        """Proxy provider for stock scraper"""
        
        def __init__(self):
            self.manager = IntegratedProxyManager()
            self.manager.proxy_manager.load_proxies()
        
        def get_proxy(self, used_proxies: Optional[set] = None) -> Optional[str]:
            """Get a proxy for stock scraping"""
            return self.manager.get_proxy_for_stock_scraper()
        
        def mark_success(self, proxy: str, response_time: float = None):
            """Mark proxy as successful"""
            self.manager.mark_proxy_result(proxy, True, response_time)
        
        def mark_failure(self, proxy: str):
            """Mark proxy as failed"""
            self.manager.mark_proxy_result(proxy, False)
        
        def get_all_proxies(self) -> List[str]:
            """Get all available proxies"""
            return self.manager.proxy_manager.proxies
        
        def reload_proxies(self):
            """Reload proxies from file"""
            self.manager.proxy_manager.load_proxies(reload=True)
    
    return ProxyProvider()


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Integrated Proxy Manager')
    parser.add_argument('-threads', type=int, default=50, help='Number of validation threads')
    parser.add_argument('-timeout', type=int, default=10, help='Request timeout in seconds')
    parser.add_argument('-output', type=str, default='working_proxies.json', help='Output file')
    parser.add_argument('-schedule', action='store_true', help='Run in scheduler mode')
    parser.add_argument('-interval', type=int, default=30, help='Schedule interval in minutes')
    parser.add_argument('-maintenance', action='store_true', help='Run maintenance mode')
    parser.add_argument('-github', action='store_true', default=True, help='Include GitHub repos')
    parser.add_argument('-stats', action='store_true', help='Show statistics only')
    return parser.parse_args()


def main():
    """Main function"""
    global shutdown_flag
    
    args = parse_arguments()
    
    # Initialize manager
    manager = IntegratedProxyManager(
        output_file=args.output,
        threads=args.threads,
        timeout=args.timeout,
        include_github=args.github
    )
    
    logger.info("INTEGRATED PROXY MANAGER")
    logger.info("="*60)
    
    if args.stats:
        # Show statistics only
        stats = manager.get_stats_summary()
        logger.info("Proxy Statistics:")
        logger.info(f"  Total Proxies: {stats['total_proxies']}")
        logger.info(f"  Healthy Proxies: {stats['healthy_proxies']}")
        logger.info(f"  Success Rate: {stats['success_rate']:.1f}%")
        logger.info(f"  Last Update: {stats['last_update']}")
        
        # Show validation history
        if stats['manager_stats'].get('validation_history'):
            logger.info("\nRecent Validation History:")
            for entry in stats['manager_stats']['validation_history'][-5:]:
                logger.info(f"  {entry['timestamp']}: {entry['total_working']}/{entry['total_scraped']} ({entry['success_rate']:.1f}%)")
        
        return
    
    if args.maintenance:
        # Run maintenance mode
        manager.run_maintenance()
        return
    
    if args.schedule:
        # Scheduler mode
        logger.info(f"SCHEDULER MODE: Running every {args.interval} minutes")
        logger.info("Press Ctrl+C to stop")
        logger.info("="*60)
        
        # Initial run
        manager.scrape_and_validate()
        
        # Schedule subsequent runs
        schedule.every(args.interval).minutes.do(manager.scrape_and_validate)
        
        # Also schedule maintenance every 2 hours
        schedule.every(2).hours.do(manager.run_maintenance)
        
        try:
            while not shutdown_flag:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            shutdown_flag = True
    else:
        # Single run
        result = manager.scrape_and_validate()
        if result['success']:
            logger.info("Proxy update completed successfully")
        else:
            logger.error("Proxy update failed")
    
    logger.info("Script completed!")


if __name__ == "__main__":
    main()