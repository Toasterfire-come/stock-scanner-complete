#!/usr/bin/env python3
"""
Scheduled Stock Retrieval - Runs every 3 minutes
Optimized for 6200 tickers with high success rate using proxies
"""

import os
import sys
import time
import logging
import signal
from datetime import datetime
import schedule

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from high_throughput_stock_retrieval import (
    load_tickers, run_high_throughput_scan, save_csv, logger
)

# Global shutdown flag
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle interrupt signals"""
    global shutdown_requested
    logger.info("\nShutdown signal received. Completing current scan...")
    shutdown_requested = True


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def run_scheduled_scan():
    """Run a single scan iteration"""
    if shutdown_requested:
        return

    logger.info("\n" + "=" * 70)
    logger.info(f"SCHEDULED SCAN STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)

    try:
        # Load tickers
        symbols = load_tickers()
        logger.info(f"Loaded {len(symbols)} tickers")

        # Run high-throughput scan
        result = run_high_throughput_scan(
            symbols,
            batch_size=50,  # Optimal batch size
            max_workers=50,  # High parallelization
            session_pool_size=30  # Good proxy rotation
        )

        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"scheduled_scan_{timestamp}.csv"
        save_csv(result['results'], filename)

        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("SCAN COMPLETED")
        logger.info(f"Success Rate: {result['success_rate']}% "
                   f"({result['successful']}/{result['total']})")
        logger.info(f"Time: {result['elapsed']}s "
                   f"({result['rate_per_sec']} tickers/sec)")
        logger.info(f"Working Proxies: {result['working_proxies']}")
        logger.info("=" * 70)

        # Check if ready for next run
        if result['elapsed'] > 160:
            logger.warning(f"⚠️  Scan took {result['elapsed']}s - approaching 3-minute limit!")
        else:
            logger.info(f"✓ Ready for next scan in {180 - result['elapsed']:.0f}s")

    except Exception as e:
        logger.error(f"Scan failed: {e}")

    logger.info(f"\nNext scan at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    logger.info("=" * 70)
    logger.info("SCHEDULED STOCK RETRIEVAL SERVICE")
    logger.info("Running every 3 minutes with proxy rotation")
    logger.info("=" * 70)
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("Press Ctrl+C to stop gracefully\n")

    # Run immediately on start
    run_scheduled_scan()

    # Schedule to run every 3 minutes
    schedule.every(3).minutes.do(run_scheduled_scan)

    # Main loop
    while not shutdown_requested:
        schedule.run_pending()
        time.sleep(1)

    logger.info("\n✓ Scheduler stopped gracefully")


if __name__ == '__main__':
    main()
