from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from stocks.models import Stock
import csv
import os
from datetime import datetime
from typing import Set, Tuple


class Command(BaseCommand):
    help = (
        "Remove extra tickers from the database that are not present in the provided CSV. "
        "Dry-run by default; use --apply to perform deletions."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            type=str,
            default="flat-ui__data-Fri Aug 01 2025.csv",
            help="Path to CSV file containing allowed tickers (default: flat-ui__data-Fri Aug 01 2025.csv)",
        )
        parser.add_argument(
            "--column",
            type=str,
            default="Symbol",
            help="CSV column name that contains ticker symbols (default: Symbol)",
        )
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Apply deletions. Without this flag the command runs in dry-run mode.",
        )
        parser.add_argument(
            "--report",
            type=str,
            default=None,
            help=(
                "Optional path to save a CSV report of tickers that would be/were deleted. "
                "Defaults to deleted_tickers_<timestamp>.csv in the current directory."
            ),
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Optional limit on number of deletions to perform (useful for testing).",
        )

    def handle(self, *args, **options):
        csv_path: str = options["csv"]
        csv_column: str = options["column"]
        apply_changes: bool = options["apply"]
        report_path: str | None = options["report"]
        delete_limit: int | None = options["limit"]

        if not os.path.isabs(csv_path):
            # Resolve relative to project root (manage.py location)
            csv_path = os.path.abspath(csv_path)

        if not os.path.exists(csv_path):
            raise CommandError(f"CSV file not found: {csv_path}")

        allowed_tickers: Set[str] = self._load_allowed_tickers(csv_path, csv_column)
        if not allowed_tickers:
            raise CommandError(
                "No tickers were found in the CSV. Verify the file and --column option."
            )

        # Fetch tickers from DB
        stocks = Stock.objects.all().only("id", "ticker", "symbol")
        extras: list[Tuple[int, str, str]] = []

        for s in stocks:
            ticker_upper = (s.ticker or "").strip().upper()
            symbol_upper = (s.symbol or "").strip().upper()
            if ticker_upper not in allowed_tickers and symbol_upper not in allowed_tickers:
                extras.append((s.id, s.ticker, s.symbol))

        total_extras = len(extras)
        if total_extras == 0:
            self.stdout.write(self.style.SUCCESS("No extra tickers found. Database is in sync with CSV."))
            return

        self.stdout.write(
            self.style.WARNING(
                f"Found {total_extras} tickers in DB not present in CSV ({os.path.basename(csv_path)})."
            )
        )

        # Prepare report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not report_path:
            report_path = os.path.abspath(f"deleted_tickers_{timestamp}.csv")

        self._write_report(report_path, extras)
        self.stdout.write(f"Report written: {report_path}")

        if not apply_changes:
            preview = ", ".join([t[1] or t[2] or "" for t in extras[:20]])
            if preview:
                self.stdout.write(f"Preview (first 20): {preview}")
            self.stdout.write(self.style.NOTICE("Dry-run complete. Use --apply to delete."))
            return

        # Apply deletions
        ids_to_delete = [row[0] for row in extras]
        if delete_limit is not None:
            ids_to_delete = ids_to_delete[: max(0, delete_limit)]

        with transaction.atomic():
            deleted_count, _ = Stock.objects.filter(id__in=ids_to_delete).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {deleted_count} Stock rows (out of {total_extras} extras). Report: {report_path}"
            )
        )

    def _load_allowed_tickers(self, csv_path: str, csv_column: str) -> Set[str]:
        """
        Load allowed tickers from a CSV. If the specified column is missing, attempt
        to auto-detect from common alternatives.
        """
        alternatives = [csv_column, "Symbol", "Ticker", "SYMBOL", "ticker", "symbol"]
        fieldnames: list[str] | None = None
        allowed: Set[str] = set()

        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            column_name = None
            for candidate in alternatives:
                if candidate in fieldnames:
                    column_name = candidate
                    break

            if not column_name:
                raise CommandError(
                    f"None of the expected columns {alternatives} were found in CSV: {fieldnames}"
                )

            for row in reader:
                raw = (row.get(column_name) or "").strip()
                if not raw:
                    continue
                allowed.add(raw.upper())

        return allowed

    def _write_report(self, report_path: str, extras: list[Tuple[int, str, str]]):
        os.makedirs(os.path.dirname(report_path) or ".", exist_ok=True)
        with open(report_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "ticker", "symbol"])  # header
            for row in extras:
                writer.writerow(row)