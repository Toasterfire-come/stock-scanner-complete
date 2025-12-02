#!/usr/bin/env python3
"""
Market Manager with Fresh Proxy Pulling
========================================

Starts the market manager and pulls fresh proxies at startup.

Workflow:
1. Pull fresh elite proxies from GeoNode API
2. Save to working_proxies.json
3. Start ultra-optimized ticker puller
4. Target: <3 minutes, 100% correctness

Usage:
    python start_market_with_proxies.py
    python start_market_with_proxies.py --no-proxy-pull  # Skip proxy pulling
    python start_market_with_proxies.py --test  # Test mode
"""

import os
import sys
import subprocess
import time
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('market_manager.log')
    ]
)
logger = logging.getLogger(__name__)

class MarketManager:
    """Manages market startup with proxy pulling"""

    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.python = sys.executable

    def pull_fresh_proxies(self) -> bool:
        """Pull fresh proxies from GeoNode API"""
        logger.info("=" * 70)
        logger.info("PULLING FRESH PROXIES")
        logger.info("=" * 70)

        try:
            result = subprocess.run([
                str(self.python),
                'pull_fresh_proxies.py',
                '--pages', '2',  # Pull 2 pages (~500 proxies)
                '--no-validate'  # Skip validation for speed
            ], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                logger.info("Proxy pull successful")

                # Check output for proxy count
                if 'Total proxies:' in result.stderr:
                    for line in result.stderr.split('\n'):
                        if 'Total proxies:' in line:
                            logger.info(line.strip())
                            break

                return True
            else:
                logger.warning(f"Proxy pull failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.warning("Proxy pull timed out")
            return False
        except Exception as e:
            logger.error(f"Error pulling proxies: {e}")
            return False

    def run_ultra_optimized_puller(self, test_mode: bool = False) -> bool:
        """Run the ultra-optimized ticker puller"""
        logger.info("")
        logger.info("=" * 70)
        logger.info("STARTING ULTRA-OPTIMIZED TICKER PULLER")
        logger.info("=" * 70)

        cmd = [
            str(self.python),
            'ultra_optimized_puller.py',
            '--workers', '40',
            '--max-workers', '60',
            '--target-time', '180'
        ]

        if test_mode:
            cmd.append('--test')

        try:
            # Run with output streaming
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            logger.info(f"Puller started (PID: {process.pid})")

            # Stream output
            while True:
                output = process.stdout.readline()
                if output:
                    line = output.strip()
                    if line:
                        print(line)

                if process.poll() is not None:
                    break

            returncode = process.wait()

            if returncode == 0:
                logger.info("Puller completed successfully")
                return True
            else:
                logger.error(f"Puller failed with code {returncode}")
                return False

        except KeyboardInterrupt:
            logger.info("\nStopping puller...")
            process.terminate()
            process.wait()
            return False
        except Exception as e:
            logger.error(f"Error running puller: {e}")
            return False

    def check_environment(self) -> bool:
        """Check if environment is ready"""
        logger.info("Checking environment...")

        # Check required files
        required_files = [
            'pull_fresh_proxies.py',
            'ultra_optimized_puller.py',
            'stock_retrieval/session_factory.py',
            'stock_retrieval/config.py'
        ]

        for file in required_files:
            if not (self.project_root / file).exists():
                logger.error(f"Missing required file: {file}")
                return False

        logger.info("Environment check passed")
        return True

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Market Manager with Proxy Pulling")
    parser.add_argument('--no-proxy-pull', action='store_true',
                       help='Skip proxy pulling')
    parser.add_argument('--test', action='store_true',
                       help='Test mode (100 tickers)')
    parser.add_argument('--force-proxies', action='store_true',
                       help='Force proxy pulling even if fresh proxies exist')

    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("MARKET MANAGER WITH PROXY PULLING")
    logger.info("=" * 70)
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")

    manager = MarketManager()

    # Check environment
    if not manager.check_environment():
        logger.error("Environment check failed")
        sys.exit(1)

    # Pull proxies
    if not args.no_proxy_pull:
        # Check if we have recent proxies
        proxy_file = manager.project_root / 'working_proxies.json'

        if proxy_file.exists() and not args.force_proxies:
            age_seconds = time.time() - proxy_file.stat().st_mtime
            age_minutes = age_seconds / 60

            if age_minutes < 60:  # Less than 1 hour old
                logger.info(f"Using existing proxies (age: {age_minutes:.0f} minutes)")
                logger.info("Use --force-proxies to refresh")
            else:
                logger.info(f"Proxies are {age_minutes:.0f} minutes old, refreshing...")
                manager.pull_fresh_proxies()
        else:
            manager.pull_fresh_proxies()
    else:
        logger.info("Skipping proxy pull (--no-proxy-pull)")

    # Run ticker puller
    success = manager.run_ultra_optimized_puller(test_mode=args.test)

    if success:
        logger.info("")
        logger.info("=" * 70)
        logger.info("MARKET MANAGER COMPLETE")
        logger.info("=" * 70)
        sys.exit(0)
    else:
        logger.error("Market manager failed")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
