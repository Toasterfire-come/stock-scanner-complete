#!/usr/bin/env python
"""
Configuration Helper for Ultra-Fast Stock Updater
Easily adjust performance parameters without editing code
"""

import argparse
import re


def update_config(file_path, updates):
    """Update configuration values in the file"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Track changes
    changes_made = []

    for key, value in updates.items():
        # Pattern to match: KEY = VALUE
        pattern = rf'^{key}\s*=\s*.*$'
        replacement = f'{key} = {value}'

        new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)

        if count > 0:
            content = new_content
            changes_made.append(f'{key}: {value}')
            print(f"[OK] Updated {key} = {value}")
        else:
            print(f"[WARN] Could not find {key} in config")

    # Write back
    if changes_made:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n[SUCCESS] Configuration updated successfully!")
        print(f"Changed: {', '.join(changes_made)}")
    else:
        print("\n[WARNING] No changes made")


def main():
    parser = argparse.ArgumentParser(
        description='Configure Ultra-Fast Stock Updater performance parameters',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Presets:
  --preset balanced    : 150 threads, 3.5s timeout, 2 retries (75-85% success)
  --preset fast        : 200 threads, 2s timeout, 2 retries (44-60% success)
  --preset conservative: 100 threads, 5s timeout, 3 retries (90-95% success)
  --preset max-speed   : 300 threads, 1.5s timeout, 1 retry (30-40% success)

Examples:
  python configure_updater.py --preset balanced
  python configure_updater.py --threads 150 --timeout 3.5
  python configure_updater.py --threads 200 --timeout 2 --retries 3
        '''
    )

    # Preset configurations
    parser.add_argument(
        '--preset',
        choices=['balanced', 'fast', 'conservative', 'max-speed'],
        help='Use a preset configuration'
    )

    # Individual parameters
    parser.add_argument(
        '--threads',
        type=int,
        help='Number of concurrent threads (default: 200)'
    )
    parser.add_argument(
        '--timeout',
        type=float,
        help='Request timeout in seconds (default: 2)'
    )
    parser.add_argument(
        '--retries',
        type=int,
        help='Maximum retry attempts (default: 2)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        help='Stocks per batch (default: 100)'
    )
    parser.add_argument(
        '--retry-delay',
        type=float,
        help='Delay between retries in seconds (default: 0.3)'
    )

    args = parser.parse_args()

    # File to update
    config_file = 'ultra_fast_yfinance_v3.py'

    # Determine configuration
    updates = {}

    if args.preset:
        print(f"[PRESET] Applying preset: {args.preset}\n")

        if args.preset == 'balanced':
            updates = {
                'THREAD_COUNT': 150,
                'REQUEST_TIMEOUT': 3.5,
                'MAX_RETRIES': 2,
            }
            print("Target: 75-85% success rate, ~180 seconds")

        elif args.preset == 'fast':
            updates = {
                'THREAD_COUNT': 200,
                'REQUEST_TIMEOUT': 2,
                'MAX_RETRIES': 2,
            }
            print("Target: 44-60% success rate, ~125 seconds")

        elif args.preset == 'conservative':
            updates = {
                'THREAD_COUNT': 100,
                'REQUEST_TIMEOUT': 5,
                'MAX_RETRIES': 3,
            }
            print("Target: 90-95% success rate, ~240 seconds")

        elif args.preset == 'max-speed':
            updates = {
                'THREAD_COUNT': 300,
                'REQUEST_TIMEOUT': 1.5,
                'MAX_RETRIES': 1,
            }
            print("Target: 30-40% success rate, ~90 seconds")

    # Override with individual parameters
    if args.threads:
        updates['THREAD_COUNT'] = args.threads
    if args.timeout:
        updates['REQUEST_TIMEOUT'] = args.timeout
    if args.retries:
        updates['MAX_RETRIES'] = args.retries
    if args.batch_size:
        updates['BATCH_SIZE'] = args.batch_size
    if args.retry_delay:
        updates['RETRY_DELAY'] = args.retry_delay

    if not updates:
        parser.print_help()
        return

    print()
    update_config(config_file, updates)

    print("\n[NEXT STEPS]")
    print("1. Test with: python manage.py update_stocks_ultra_fast --test-mode")
    print("2. Run full update: python manage.py update_stocks_ultra_fast")
    print("3. Monitor ultra_fast_updater.log for results")


if __name__ == '__main__':
    main()
