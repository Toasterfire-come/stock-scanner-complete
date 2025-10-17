#!/usr/bin/env python3
"""
Market Manager - Launches the new high-speed stock scanner.
- This is the single entry point you will call directly.
- Delegates to fast_stock_scanner.py and supports passing CLI options through env vars.
"""

import os
import sys
import subprocess
from shutil import which

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable or which('python3') or 'python3'
SCANNER = os.path.join(THIS_DIR, 'fast_stock_scanner.py')


def main():
    threads = os.environ.get('SCANNER_THREADS', '10')
    timeout = os.environ.get('SCANNER_TIMEOUT', '8')
    proxy_file = os.environ.get('SCANNER_PROXY_FILE', os.path.join(THIS_DIR, 'working_proxies.json'))
    no_proxy = os.environ.get('SCANNER_NO_PROXY', '0') in ('1', 'true', 'True')
    limit = os.environ.get('SCANNER_LIMIT')
    symbols = os.environ.get('SCANNER_SYMBOLS')

    cmd = [PYTHON, SCANNER, '--threads', str(threads), '--timeout', str(timeout), '--proxy-file', proxy_file]
    if no_proxy:
        cmd.append('--no-proxy')
    if limit:
        cmd.extend(['--limit', str(limit)])
    if symbols:
        cmd.extend(['--symbols', symbols])

    # Execute the scanner as a child process so it can leverage its own arg parsing
    proc = subprocess.run(cmd, check=False)
    sys.exit(proc.returncode)


if __name__ == '__main__':
    main()
