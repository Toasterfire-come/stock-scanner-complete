#!/usr/bin/env python3

import argparse
import csv
import os
import sys
import shutil
from typing import Set, List, Tuple
from datetime import datetime


def load_allowed_tickers(csv_path: str, column: str) -> Set[str]:
    alternatives = [column, "Symbol", "Ticker", "SYMBOL", "ticker", "symbol"]
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        column_name = None
        for candidate in alternatives:
            if candidate in fieldnames:
                column_name = candidate
                break
        if not column_name:
            raise ValueError(
                f"None of the expected columns {alternatives} were found in CSV: {fieldnames}"
            )
        allowed: Set[str] = set()
        for row in reader:
            raw = (row.get(column_name) or "").strip()
            if not raw:
                continue
            allowed.add(raw.upper())
    return allowed


def plan_deletions(target_dir: str, allowed: Set[str], mode: str) -> Tuple[List[str], List[str]]:
    files_to_delete: List[str] = []
    dirs_to_delete: List[str] = []

    with os.scandir(target_dir) as it:
        for entry in it:
            if entry.is_file() and mode in ("all", "files"):
                basename = os.path.splitext(entry.name)[0]
                candidate = basename.upper()
                if candidate not in allowed:
                    files_to_delete.append(entry.path)
            elif entry.is_dir() and mode in ("all", "dirs"):
                candidate = entry.name.upper()
                if candidate not in allowed:
                    dirs_to_delete.append(entry.path)
    return files_to_delete, dirs_to_delete


def write_report(path: str, files_to_delete: List[str], dirs_to_delete: List[str]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("type,path\n")
        for p in files_to_delete:
            f.write(f"file,{p}\n")
        for p in dirs_to_delete:
            f.write(f"dir,{p}\n")


def delete_paths(files_to_delete: List[str], dirs_to_delete: List[str]) -> Tuple[int, int]:
    deleted_files = 0
    deleted_dirs = 0
    for p in files_to_delete:
        try:
            os.unlink(p)
            deleted_files += 1
        except FileNotFoundError:
            pass
    for p in dirs_to_delete:
        try:
            shutil.rmtree(p)
            deleted_dirs += 1
        except FileNotFoundError:
            pass
    return deleted_files, deleted_dirs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Remove extra ticker files/directories not present in a CSV. "
            "Names are matched case-insensitively against the CSV ticker column (default: Symbol)."
        )
    )
    parser.add_argument("--csv", required=True, help="Path to CSV containing tickers")
    parser.add_argument(
        "--column", default="Symbol", help="CSV column name with tickers (default: Symbol)"
    )
    parser.add_argument(
        "--target-dir", required=True, help="Directory containing ticker-named files/directories"
    )
    parser.add_argument(
        "--mode",
        choices=["all", "files", "dirs"],
        default="all",
        help="Delete files, dirs, or both (default: all)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply deletions. Without this flag, runs as dry-run only.",
    )
    parser.add_argument(
        "--report",
        default=None,
        help=(
            "Optional CSV report path of items that would be/were deleted. "
            "Defaults to ticker_cleanup_<timestamp>.csv in current directory."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    target_dir = os.path.abspath(args.target_dir)
    csv_path = os.path.abspath(args.csv)

    if not os.path.isdir(target_dir):
        print(f"ERROR: Target directory not found: {target_dir}")
        return 2
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found: {csv_path}")
        return 2

    try:
        allowed = load_allowed_tickers(csv_path, args.column)
    except Exception as e:
        print(f"ERROR: Failed to read CSV: {e}")
        return 2

    files_to_delete, dirs_to_delete = plan_deletions(target_dir, allowed, args.mode)

    total = len(files_to_delete) + len(dirs_to_delete)
    print(
        f"Found {total} extra entries in {target_dir} (files: {len(files_to_delete)}, dirs: {len(dirs_to_delete)})."
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = args.report or os.path.abspath(
        f"ticker_cleanup_{timestamp}.csv"
    )
    write_report(report_path, files_to_delete, dirs_to_delete)
    print(f"Report written: {report_path}")

    # Preview first few items
    preview = [os.path.basename(p) for p in (files_to_delete[:10] + dirs_to_delete[:10])]
    if preview:
        print("Preview (first up to 10):", ", ".join(preview))

    if not args.apply:
        print("Dry-run complete. Re-run with --apply to delete.")
        return 0

    deleted_files, deleted_dirs = delete_paths(files_to_delete, dirs_to_delete)
    print(
        f"Deleted {deleted_files} files and {deleted_dirs} directories (of {total} planned)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())