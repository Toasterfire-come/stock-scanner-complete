#!/usr/bin/env python3
"""
Market Manager - Launches the high-throughput stock retrieval system.
- This is the single entry point you will call directly.
- Delegates to high_throughput_stock_retrieval.py for optimal performance.
- Supports 6200+ tickers in <180s with 95%+ success rate.
"""

import os
import sys
import subprocess
from shutil import which

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable or which('python3') or 'python3'
SCANNER = os.path.join(THIS_DIR, 'high_throughput_stock_retrieval.py')


def main():
    """
    Main entry point for market manager.

    Environment Variables:
    - SCANNER_WORKERS: Number of parallel workers (default: 60)
    - SCANNER_BATCH_SIZE: Batch size for processing (default: 200)
    - SCANNER_NO_PROXY: Disable proxies (default: false)
    - SCANNER_LIMIT: Limit number of tickers (for testing)
    - SCANNER_OUTPUT: Output CSV filename
    """
    # Get configuration from environment
    workers = os.environ.get('SCANNER_WORKERS', '60')
    batch_size = os.environ.get('SCANNER_BATCH_SIZE', '200')
    no_proxies = os.environ.get('SCANNER_NO_PROXY', '0') in ('1', 'true', 'True')
    limit = os.environ.get('SCANNER_LIMIT')
    output = os.environ.get('SCANNER_OUTPUT')

    # Build command
    cmd = [
        PYTHON, SCANNER,
        '--workers', str(workers),
        '--batch-size', str(batch_size)
    ]

    if no_proxies:
        cmd.append('--no-proxies')

    if limit:
        cmd.extend(['--limit', str(limit)])

    if output:
        cmd.extend(['--output', output])

    # Execute the high-throughput scanner
    print(f"Launching high-throughput stock retrieval...")
    print(f"  Workers: {workers}")
    print(f"  Batch size: {batch_size}")
    print(f"  Proxies: {'DISABLED' if no_proxies else 'ENABLED'}")
    if limit:
        print(f"  Limit: {limit} tickers")

    proc = subprocess.run(cmd, check=False)
    sys.exit(proc.returncode)


if __name__ == '__main__':
    main()
