from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.apps import apps
from django.db import connection
from typing import List, Set


class Command(BaseCommand):
    help = (
        "Detect and fix missing DB tables for the 'stocks' app by running makemigrations/migrate. "
        "Optionally run the clean_extra_tickers cleanup with the provided CSV after fixing."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--app",
            type=str,
            default="stocks",
            help="App label to check/migrate (default: stocks)",
        )
        parser.add_argument(
            "--fake-initial",
            action="store_true",
            help="Use --fake-initial when applying migrations (helpful if tables exist but migration history does not)",
        )
        parser.add_argument(
            "--apply-cleanup",
            action="store_true",
            help="After fixing tables, run clean_extra_tickers with the provided CSV",
        )
        parser.add_argument(
            "--csv",
            type=str,
            default="flat-ui__data-Fri Aug 01 2025.csv",
            help="CSV file path for clean_extra_tickers (default: flat-ui__data-Fri Aug 01 2025.csv)",
        )
        parser.add_argument(
            "--column",
            type=str,
            default="Symbol",
            help="CSV column to read ticker symbols from (default: Symbol)",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Optional limit for deletions when running cleanup",
        )

    def handle(self, *args, **options):
        app_label: str = options["app"]
        fake_initial: bool = options["fake_initial"]
        apply_cleanup: bool = options["apply_cleanup"]
        csv_path: str = options["csv"]
        csv_column: str = options["column"]
        delete_limit = options["limit"]

        try:
            app_config = apps.get_app_config(app_label)
        except LookupError as exc:
            raise CommandError(f"App '{app_label}' not found: {exc}")

        expected_tables: Set[str] = self._get_expected_tables(app_config)
        existing_tables: Set[str] = set(connection.introspection.table_names())

        missing_tables = sorted(expected_tables - existing_tables)
        if missing_tables:
            self.stdout.write(self.style.WARNING(
                f"Detected {len(missing_tables)} missing tables for app '{app_label}':\n- " + "\n- ".join(missing_tables)
            ))

            self.stdout.write("Running makemigrations...")
            call_command("makemigrations", app_label)

            self.stdout.write("Applying migrations...")
            if fake_initial:
                call_command("migrate", app_label, fake_initial=True)
            else:
                call_command("migrate", app_label)

            # Verify again
            existing_tables = set(connection.introspection.table_names())
            still_missing = sorted(expected_tables - existing_tables)
            if still_missing:
                raise CommandError(
                    "Some tables are still missing after migrations: \n- " + "\n- ".join(still_missing)
                )

            self.stdout.write(self.style.SUCCESS(
                f"All required tables for '{app_label}' are present."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"No missing tables detected for '{app_label}'."
            ))

        if apply_cleanup:
            self.stdout.write("Running clean_extra_tickers to remove stale symbols...")
            cleanup_kwargs = {"csv": csv_path, "column": csv_column, "apply": True}
            if delete_limit is not None:
                cleanup_kwargs["limit"] = int(delete_limit)
            call_command("clean_extra_tickers", **cleanup_kwargs)
            self.stdout.write(self.style.SUCCESS("Cleanup completed."))

    def _get_expected_tables(self, app_config) -> Set[str]:
        """
        Collect expected DB table names for all models in the given app based on model _meta.db_table.
        """
        table_names: List[str] = []
        for model in app_config.get_models():
            table_names.append(model._meta.db_table)
        return set(table_names)