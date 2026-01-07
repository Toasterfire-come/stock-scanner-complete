#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Make manage.py runnable from any working directory.
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except Exception:
    pass

_suppress_startup_logs = (
    os.environ.get("DJANGO_SUPPRESS_STARTUP_LOGS", "").strip().lower() in ("1", "true", "yes")
    or "test" in sys.argv
)

# Add XAMPP MySQL to PATH if it exists
XAMPP_MYSQL_PATH = r"C:\xampp\mysql\bin"
if os.path.exists(XAMPP_MYSQL_PATH) and XAMPP_MYSQL_PATH not in os.environ.get('PATH', ''):
    os.environ['PATH'] = os.environ.get('PATH', '') + os.pathsep + XAMPP_MYSQL_PATH
    if not _suppress_startup_logs:
        print(f"INFO: Added XAMPP MySQL to PATH: {XAMPP_MYSQL_PATH}")

# Configure PyMySQL for MySQL compatibility
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    if not _suppress_startup_logs:
        print("PyMySQL configured for MySQL compatibility")
except ImportError:
    if not _suppress_startup_logs:
        print("PyMySQL not available")


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
