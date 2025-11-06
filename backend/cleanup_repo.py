#!/usr/bin/env python3
"""
Repository Cleanup Script
Identifies and removes bloating files to keep the repo lean
"""

import os
import glob
from pathlib import Path
from typing import List, Tuple


def get_file_size(filepath: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(filepath)
    except Exception:
        return 0


def format_size(bytes: int) -> str:
    """Format bytes to human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} TB"


def find_bloat_files() -> List[Tuple[str, int, str]]:
    """
    Find bloating files in the repository
    Returns: List of (filepath, size_bytes, category)
    """
    bloat_files = []

    # 1. Old test/scan CSV files (keep only latest combined_tickers)
    test_csvs = glob.glob('*.csv')
    for csv_file in test_csvs:
        if 'combined_tickers' not in csv_file:  # Keep fresh ticker lists
            size = get_file_size(csv_file)
            bloat_files.append((csv_file, size, 'test_csv'))

    # 2. Log files
    log_files = glob.glob('*.log')
    for log_file in log_files:
        size = get_file_size(log_file)
        bloat_files.append((log_file, size, 'log'))

    # 3. Python cache files
    pycache_dirs = []
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            # Calculate size of entire directory
            total_size = sum(
                os.path.getsize(os.path.join(dirpath, filename))
                for dirpath, _, filenames in os.walk(pycache_path)
                for filename in filenames
            )
            bloat_files.append((pycache_path, total_size, 'pycache'))

    # 4. Old ticker files in data/ (keep only latest)
    old_ticker_files = []
    old_ticker_files.extend(glob.glob('data/complete_nasdaq/*.csv'))
    old_ticker_files.extend(glob.glob('data/complete_nasdaq/*.txt'))
    old_ticker_files.extend(glob.glob('data/nasdaq_only/*.csv'))
    old_ticker_files.extend(glob.glob('data/nasdaq_only/*.txt'))

    for old_file in old_ticker_files:
        size = get_file_size(old_file)
        bloat_files.append((old_file, size, 'old_ticker_data'))

    # 5. Duplicate/old ticker Python files (keep only latest combined)
    old_ticker_py = glob.glob('data/**/nasdaq_*.py', recursive=True) + \
                    glob.glob('data/**/complete_nasdaq_*.py', recursive=True)
    for old_file in old_ticker_py:
        size = get_file_size(old_file)
        bloat_files.append((old_file, size, 'old_ticker_py'))

    return bloat_files


def analyze_bloat(bloat_files: List[Tuple[str, int, str]]):
    """Analyze and display bloat files"""
    if not bloat_files:
        print("✓ No bloat files found!")
        return

    # Group by category
    by_category = {}
    total_size = 0

    for filepath, size, category in bloat_files:
        if category not in by_category:
            by_category[category] = []
        by_category[category].append((filepath, size))
        total_size += size

    print("=" * 70)
    print("REPOSITORY BLOAT ANALYSIS")
    print("=" * 70)
    print(f"\nTotal bloat: {format_size(total_size)}")
    print(f"Total files: {len(bloat_files)}\n")

    for category, files in sorted(by_category.items()):
        cat_size = sum(size for _, size in files)
        print(f"\n{category.upper().replace('_', ' ')}:")
        print(f"  Count: {len(files)}")
        print(f"  Size: {format_size(cat_size)}")
        print(f"  Files:")
        # Show top 5 largest
        for filepath, size in sorted(files, key=lambda x: x[1], reverse=True)[:5]:
            print(f"    - {filepath:50s} ({format_size(size)})")
        if len(files) > 5:
            print(f"    ... and {len(files) - 5} more")


def cleanup_bloat(bloat_files: List[Tuple[str, int, str]], dry_run: bool = True):
    """Clean up bloat files"""
    if not bloat_files:
        print("✓ No files to clean!")
        return

    total_size = sum(size for _, size, _ in bloat_files)

    if dry_run:
        print(f"\n{'=' * 70}")
        print(f"DRY RUN MODE")
        print(f"Would remove {len(bloat_files)} files ({format_size(total_size)})")
        print(f"Run with --execute to actually remove files")
        print(f"{'=' * 70}")
        return

    print(f"\n{'=' * 70}")
    print(f"CLEANING UP BLOAT")
    print(f"{'=' * 70}")

    removed_count = 0
    removed_size = 0

    for filepath, size, category in bloat_files:
        try:
            if os.path.isdir(filepath):
                # Remove directory and contents
                import shutil
                shutil.rmtree(filepath)
            else:
                # Remove file
                os.remove(filepath)

            removed_count += 1
            removed_size += size
            print(f"✓ Removed: {filepath}")

        except Exception as e:
            print(f"✗ Failed to remove {filepath}: {e}")

    print(f"\n{'=' * 70}")
    print(f"CLEANUP COMPLETE")
    print(f"{'=' * 70}")
    print(f"Removed: {removed_count}/{len(bloat_files)} files")
    print(f"Freed: {format_size(removed_size)}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Clean up repository bloat')
    parser.add_argument('--execute', action='store_true',
                       help='Actually remove files (default is dry-run)')

    args = parser.parse_args()

    print("Scanning for bloat files...")
    bloat_files = find_bloat_files()

    analyze_bloat(bloat_files)
    cleanup_bloat(bloat_files, dry_run=not args.execute)
