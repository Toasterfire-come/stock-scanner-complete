#!/usr/bin/env python
"""
Create MySQL Database Script
Creates the database and runs migrations
"""
import os
import subprocess
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    import pymysql
except Exception:
    # Best-effort install in case it's missing in a fresh environment
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'PyMySQL==1.1.0', '--break-system-packages'])
    import pymysql


def get_env(name: str, default: str) -> str:
    value = os.environ.get(name, default)
    return value


def create_database() -> bool:
    """Create the MySQL database using admin credentials (root by default)."""
    # Read target app database credentials
    app_db_name = get_env('DB_NAME', 'stockscanner')
    app_db_user = get_env('DB_USER', 'stockscanner_user')
    app_db_password = get_env('DB_PASSWORD', 'StockScanner_2025!')
    db_host = get_env('DB_HOST', '127.0.0.1')
    db_port = int(get_env('DB_PORT', '3306'))

    # Admin for creating DB and granting permissions
    admin_user = get_env('MYSQL_ADMIN_USER', 'root')
    admin_password = os.environ.get('MYSQL_ADMIN_PASSWORD', '')

    try:
        connection = pymysql.connect(
            host=db_host,
            user=admin_user,
            password=admin_password,
            port=db_port,
            charset='utf8mb4',
            autocommit=True,
        )
        cursor = connection.cursor()

        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{app_db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        )
        cursor.execute(
            "FLUSH PRIVILEGES;"
        )

        # Create application user and grant privileges (safe if exists)
        cursor.execute(
            f"CREATE USER IF NOT EXISTS '{app_db_user}'@'localhost' IDENTIFIED BY %s;",
            (app_db_password,),
        )
        cursor.execute(
            f"GRANT ALL PRIVILEGES ON `{app_db_name}`.* TO '{app_db_user}'@'localhost';"
        )
        cursor.execute("FLUSH PRIVILEGES;")

        # Verify database exists
        cursor.execute("SHOW DATABASES LIKE %s", (app_db_name,))
        result = cursor.fetchone()
        if not result:
            print("ERROR: Database not found after creation")
            return False

        print(f"SUCCESS: Database '{app_db_name}' is ready and user '{app_db_user}' has privileges")
        cursor.close()
        connection.close()
        return True

    except Exception as exc:
        print(f"ERROR: Failed to create database or user: {exc}")
        return False


def run_migrations() -> bool:
    """Run Django migrations."""
    try:
        print("\nRunning Django migrations...")

        result = subprocess.run([sys.executable, 'manage.py', 'makemigrations'], capture_output=True, text=True)
        if result.returncode != 0:
            print("WARNING: makemigrations had issues:")
            print(result.stderr)

        result = subprocess.run([sys.executable, 'manage.py', 'migrate'], capture_output=True, text=True)
        if result.returncode == 0:
            print("SUCCESS: All migrations applied!")
            return True
        else:
            print("ERROR: Migration failed:")
            print(result.stderr)
            return False

    except Exception as exc:
        print(f"ERROR: Failed to run migrations: {exc}")
        return False


def main() -> None:
    # Summarize from env
    app_db_name = get_env('DB_NAME', 'stockscanner')
    app_db_user = get_env('DB_USER', 'stockscanner_user')
    _ = get_env('DB_PASSWORD', 'StockScanner_2025!')

    print("Creating MySQL Database for Stock Scanner")
    print("=" * 50)
    print(f"Database: {app_db_name}")
    print(f"User: {app_db_user}")
    print("Password: [hidden]")
    print()

    if create_database():
        print()
        if run_migrations():
            print()
            print("=" * 50)
            print("SUCCESS: Database setup complete!")
            print("You can now run: python manage.py runserver")
            print("Admin URL: http://127.0.0.1:8000/admin/")
        else:
            print("ERROR: Migration failed. Check the error messages above.")
    else:
        print("ERROR: Database creation failed.")
        print()
        print("TROUBLESHOOTING:")
        print("1. Make sure MySQL is running (XAMPP MySQL)")
        print("2. Provide admin credentials via MYSQL_ADMIN_USER / MYSQL_ADMIN_PASSWORD if root is protected")
        print("3. Try creating manually via phpMyAdmin")


if __name__ == '__main__':
    main()