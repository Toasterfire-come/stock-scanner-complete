#!/usr/bin/env python3
"""
Enhanced Stock Retrieval with Integrated Proxy Manager
Combines proxy scraping, validation, and stock retrieval
Designed to work with market hours manager
"""

import os
import sys
import time
import random
import json
import argparse
import logging
import signal
import schedule
import threading
from datetime import datetime, timedelta
import pytz

# Import the original enhanced stock retrieval functions
from enhanced_stock_retrieval_working import (
    parse_arguments as parse_stock_arguments,
    load_nyse_symbols,
    process_symbol_with_retry,
    shutdown_flag,
    signal_handler
)

# Import proxy management
from integrated_proxy_manager import IntegratedProxyManager
from utils.proxy_utils import ProxyManager

# Setup logging with rotation
from logging.handlers import RotatingFileHandler

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handlers
file_handler = RotatingFileHandler(
    'enhanced_stock_retrieval_integrated.log',
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

# Prevent propagation
logger.propagate = False

# Market window configuration
EASTERN_TZ = pytz.timezone('US/Eastern')
PREMARKET_START = os.getenv('PREMARKET_START', "04:00")
MARKET_OPEN = os.getenv('MARKET_OPEN', "09:30")
POSTMARKET_END = os.getenv('POSTMARKET_END', "20:00")

# Global proxy manager instance
proxy_manager_instance = None


class IntegratedStockRetriever:
    """Integrated stock retriever with automatic proxy management"""
    
    def __init__(self, args):
        self.args = args
        self.proxy_manager = None
        self.last_proxy_update = None
        self.proxy_update_interval = 60  # Update proxies every 60 minutes
        
        # Initialize proxy manager if not in noproxy mode
        if not args.noproxy:
            self.initialize_proxy_manager()
    
    def initialize_proxy_manager(self):
        """Initialize the integrated proxy manager"""
        try:
            logger.info("Initializing integrated proxy manager...")
            self.proxy_manager = IntegratedProxyManager(
                output_file=self.args.proxy_file,
                threads=50,
                timeout=10,
                max_response_time=5.0,
                include_github=True
            )
            
            # Load existing proxies or scrape new ones
            if not os.path.exists(self.args.proxy_file):
                logger.info("No existing proxies found. Starting initial scrape...")
                self.update_proxies()
            else:
                # Check age of proxy file
                file_age = time.time() - os.path.getmtime(self.args.proxy_file)
                if file_age > 3600:  # Older than 1 hour
                    logger.info("Proxy file is old. Updating...")
                    self.update_proxies()
                else:
                    self.proxy_manager.proxy_manager.load_proxies()
                    logger.info(f"Loaded {len(self.proxy_manager.proxy_manager.proxies)} existing proxies")
            
            self.last_proxy_update = datetime.now()
            
        except Exception as e:
            logger.error(f"Failed to initialize proxy manager: {e}")
            self.proxy_manager = None
    
    def update_proxies(self):
        """Update proxy list by scraping and validating"""
        if not self.proxy_manager:
            return
        
        try:
            logger.info("="*60)
            logger.info("UPDATING PROXY LIST")
            logger.info("="*60)
            
            result = self.proxy_manager.scrape_and_validate()
            
            if result['success']:
                logger.info(f"Proxy update successful: {result['total_working']} working proxies")
                self.last_proxy_update = datetime.now()
            else:
                logger.error("Proxy update failed")
                
        except Exception as e:
            logger.error(f"Error updating proxies: {e}")
    
    def check_proxy_update_needed(self):
        """Check if proxies need updating"""
        if not self.proxy_manager or not self.last_proxy_update:
            return False
        
        time_since_update = (datetime.now() - self.last_proxy_update).total_seconds() / 60
        return time_since_update >= self.proxy_update_interval
    
    def get_proxies_for_stock_scraper(self):
        """Get proxy list for stock scraper"""
        if not self.proxy_manager:
            return []
        
        # Check if update needed
        if self.check_proxy_update_needed():
            logger.info("Proxy update interval reached. Refreshing proxies...")
            self.update_proxies()
        
        return self.proxy_manager.proxy_manager.proxies
    
    def run_stock_update_cycle(self):
        """Run a single stock update cycle with integrated proxy management"""
        logger.info(f"{'='*60}")
        logger.info(f"INTEGRATED STOCK UPDATE CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*60}")
        
        # Get proxies
        proxies = []
        if not self.args.noproxy:
            proxies = self.get_proxies_for_stock_scraper()
            if proxies:
                logger.info(f"Using {len(proxies)} proxies for stock retrieval")
                
                # Show proxy stats
                stats = self.proxy_manager.proxy_manager.get_proxy_stats()
                logger.info(f"Proxy health: {stats['healthy_proxies']} healthy, "
                          f"{stats['blocked_proxies']} blocked, "
                          f"{stats['success_rate']:.1f}% success rate")
            else:
                logger.warning("No proxies available, continuing without proxies")
        
        # Load NYSE symbols
        logger.info(f"Loading NYSE symbols from {self.args.csv}...")
        symbols = load_nyse_symbols(self.args.csv, self.args.test, self.args.max_symbols)
        
        if not symbols:
            logger.error("No symbols loaded. Skipping cycle.")
            return
        
        logger.info(f"Processing {len(symbols)} symbols...")
        
        # Process stocks
        start_time = time.time()
        successful = 0
        failed = 0
        results = []
        
        # Use ThreadPoolExecutor for parallel processing
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        try:
            with ThreadPoolExecutor(max_workers=self.args.threads) as executor:
                future_to_symbol = {}
                
                for i, symbol in enumerate(symbols, 1):
                    if shutdown_flag:
                        break
                    
                    # Submit task with proxy manager integration
                    future = executor.submit(
                        self.process_symbol_with_proxy_tracking,
                        symbol, i, proxies, self.args.timeout, 
                        self.args.test, self.args.save_to_db
                    )
                    future_to_symbol[future] = symbol
                
                logger.info(f"Submitted {len(future_to_symbol)} tasks. Processing...")
                completed = 0
                
                for future in as_completed(future_to_symbol):
                    if shutdown_flag:
                        logger.info("Shutdown requested. Cancelling remaining tasks...")
                        break
                    
                    symbol = future_to_symbol[future]
                    completed += 1
                    
                    try:
                        result = future.result(timeout=self.args.timeout + 2)
                        if result:
                            successful += 1
                            results.append(result)
                        else:
                            failed += 1
                    except Exception as e:
                        logger.error(f"ERROR {symbol}: {e}")
                        failed += 1
                    
                    # Progress update
                    if completed % 10 == 0 or completed == len(symbols):
                        logger.info(f"[PROGRESS] {completed}/{len(symbols)} completed "
                                  f"({successful} successful, {failed} failed)")
                    
                    time.sleep(0.01)
        
        except KeyboardInterrupt:
            logger.info("Interrupted by user. Shutting down gracefully...")
        except Exception as e:
            logger.error(f"Thread pool execution failed: {e}")
        
        elapsed = time.time() - start_time
        
        # Results summary
        logger.info("=" * 60)
        logger.info("CYCLE RESULTS")
        logger.info("=" * 60)
        logger.info(f"SUCCESSFUL: {successful}")
        logger.info(f"FAILED: {failed}")
        if len(symbols) > 0:
            logger.info(f"SUCCESS RATE: {(successful/len(symbols)*100):.1f}%")
        logger.info(f"TIME: {elapsed:.2f}s")
        if elapsed > 0:
            logger.info(f"RATE: {len(symbols)/elapsed:.2f} symbols/sec")
        
        # Update proxy stats if using proxy manager
        if self.proxy_manager and proxies:
            stats = self.proxy_manager.proxy_manager.get_proxy_stats()
            logger.info(f"PROXY PERFORMANCE: {stats['success_rate']:.1f}% success rate, "
                      f"{stats['avg_response_time']:.2f}s avg response")
            
            # Save proxy stats
            self.proxy_manager.save_stats()
        
        logger.info(f"CYCLE COMPLETED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
    
    def process_symbol_with_proxy_tracking(self, symbol, ticker_number, proxies, 
                                          timeout, test_mode, save_to_db):
        """Process symbol with proxy tracking"""
        # Use the original process function
        result = process_symbol_with_retry(
            symbol, ticker_number, proxies, timeout, test_mode, save_to_db
        )
        
        # Track proxy performance if using proxy manager
        # (The original function already handles proxy health tracking)
        
        return result


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Enhanced Stock Retrieval with Integrated Proxy Manager')
    parser.add_argument('-noproxy', action='store_true', help='Disable proxy usage')
    parser.add_argument('-test', action='store_true', help='Test mode - process only first 100 tickers')
    parser.add_argument('-threads', type=int, default=15, help='Number of threads (default: 15)')
    parser.add_argument('-timeout', type=int, default=10, help='Request timeout in seconds (default: 10)')
    parser.add_argument('-csv', type=str, default=os.getenv('NYSE_CSV_PATH', 'flat-ui__data-Fri Aug 01 2025.csv'), 
                       help='NYSE CSV file path')
    parser.add_argument('-max-symbols', type=int, default=None, help='Maximum number of symbols to process')
    parser.add_argument('-proxy-file', type=str, default='working_proxies.json', help='Proxy JSON file path')
    parser.add_argument('-schedule', action='store_true', help='Run in scheduler mode')
    parser.add_argument('-save-to-db', action='store_true', default=True, help='Save results to database')
    parser.add_argument('-update-proxies', action='store_true', help='Force proxy update before starting')
    parser.add_argument('-proxy-update-interval', type=int, default=60, 
                       help='Proxy update interval in minutes (default: 60)')
    return parser.parse_args()


def run_daily_update(args):
    """Run the daily 9 AM update with proxy refresh"""
    logger.info("="*60)
    logger.info("DAILY 9 AM UPDATE STARTING")
    logger.info("="*60)
    
    # Initialize retriever
    retriever = IntegratedStockRetriever(args)
    
    # Force proxy update at start of day
    if not args.noproxy:
        logger.info("Performing daily proxy refresh...")
        retriever.update_proxies()
    
    # Run stock update
    retriever.run_stock_update_cycle()
    
    logger.info("Daily update completed")


def main():
    """Main function"""
    global shutdown_flag
    
    args = parse_arguments()
    
    logger.info("ENHANCED STOCK RETRIEVAL WITH INTEGRATED PROXY MANAGER")
    logger.info("=" * 60)
    logger.info(f"Configuration:")
    logger.info(f"  CSV File: {args.csv}")
    logger.info(f"  Test Mode: {args.test}")
    logger.info(f"  Use Proxies: {not args.noproxy}")
    logger.info(f"  Proxy File: {args.proxy_file}")
    logger.info(f"  Threads: {args.threads}")
    logger.info(f"  Timeout: {args.timeout}s")
    logger.info(f"  Max Symbols: {args.max_symbols or 'All'}")
    logger.info(f"  Save to DB: {args.save_to_db}")
    logger.info(f"  Schedule Mode: {args.schedule}")
    logger.info(f"  Proxy Update Interval: {args.proxy_update_interval} minutes")
    logger.info("=" * 60)
    
    # Initialize retriever
    retriever = IntegratedStockRetriever(args)
    
    # Force proxy update if requested
    if args.update_proxies and not args.noproxy:
        retriever.update_proxies()
    
    if args.schedule:
        logger.info("SCHEDULER MODE: Running every 3 minutes with proxy management")
        logger.info("Press Ctrl+C to stop the scheduler")
        logger.info("=" * 60)
        
        # Schedule regular runs every 3 minutes
        schedule.every(3).minutes.do(retriever.run_stock_update_cycle)
        
        # Schedule proxy updates every hour
        if not args.noproxy:
            schedule.every(args.proxy_update_interval).minutes.do(retriever.update_proxies)
        
        # Run immediately
        retriever.run_stock_update_cycle()
        
        try:
            while not shutdown_flag:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            shutdown_flag = True
    else:
        # Run single update
        retriever.run_stock_update_cycle()
    
    logger.info("Script completed!")


if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    main()