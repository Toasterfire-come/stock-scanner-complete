#!/usr/bin/env python3
"""
Django Server Startup with Interactive Password Input
Prompts for database password and starts the server
"""

import os
import sys
import getpass
import subprocess
import time
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"DJANGO SERVER - {title}")
    print(f"{'='*60}")

def get_database_credentials():
    """Get database credentials from user"""
    print("\nDATABASE CONFIGURATION")
    print("-" * 30)
    
    db_type = input("Database type (mysql/postgresql/sqlite) [mysql]: ").strip().lower() or "mysql"
    
    if db_type == "sqlite":
        return {
            'engine': 'django.db.backends.sqlite3',
            'name': 'db.sqlite3',
            'user': '',
            'password': '',
            'host': '',
            'port': ''
        }
    
    print(f"\nEnter {db_type.upper()} database credentials:")
    
    if db_type == "mysql":
        default_port = "3306"
        engine = "django.db.backends.mysql"
    else:  # postgresql
        default_port = "5432"
        engine = "django.db.backends.postgresql"
    
    host = input(f"Database host [127.0.0.1]: ").strip() or "127.0.0.1"
    port = input(f"Database port [{default_port}]: ").strip() or default_port
    database = input(f"Database name [stockscanner_db]: ").strip() or "stockscanner_db"
    username = input(f"Database username [root]: ").strip() or "root"
    
    # Get password securely
    password = getpass.getpass("Database password: ")
    
    if not password:
        print("ERROR: Password is required!")
        return None
    
    return {
        'engine': engine,
        'name': database,
        'user': username,
        'password': password,
        'host': host,
        'port': port
    }

def test_database_connection(db_config):
    """Test database connection"""
    print("\nTesting database connection...")
    
    try:
        if 'sqlite' in db_config['engine']:
            # SQLite doesn't need connection testing
            print("SUCCESS: SQLite database ready")
            return True
        
        if 'mysql' in db_config['engine']:
            import MySQLdb
            conn = MySQLdb.connect(
                host=db_config['host'],
                port=int(db_config['port']),
                user=db_config['user'],
                passwd=db_config['password'],
                db=db_config['name'],
                connect_timeout=10
            )
        else:  # postgresql
            import psycopg2
            conn = psycopg2.connect(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['name'],
                user=db_config['user'],
                password=db_config['password'],
                connect_timeout=10
            )
        
        conn.close()
        print("SUCCESS: Database connection successful!")
        return True
        
    except ImportError as e:
        print(f"ERROR: Required database driver not installed: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        print("\nTroubleshooting:")
        print("- Make sure the database server is running")
        print("- Check if the database exists")
        print("- Verify username and password")
        print("- Check host and port settings")
        return False

def create_env_file(db_config):
    """Create .env file with database configuration"""
    
    if 'sqlite' in db_config['engine']:
        database_url = f"sqlite:///{db_config['name']}"
    elif 'mysql' in db_config['engine']:
        database_url = f"mysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['name']}"
    else:  # postgresql
        database_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['name']}"
    
    env_content = f"""# Stock Scanner Environment Configuration
DEBUG=True
SECRET_KEY=django-insecure-development-key-change-in-production
ALLOWED_HOSTS=127.0.0.1,localhost,0.0.0.0

# Database Configuration
DATABASE_URL={database_url}
DB_ENGINE={db_config['engine']}
DB_NAME={db_config['name']}
DB_USER={db_config['user']}
DB_PASSWORD={db_config['password']}
DB_HOST={db_config['host']}
DB_PORT={db_config['port']}

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Stock Data API Configuration
YFINANCE_TIMEOUT=30
YFINANCE_RETRY_COUNT=3

# News Scraping Configuration
NEWS_SCRAPER_ENABLED=True
NEWS_SCRAPER_TIMEOUT=30
NEWS_SCRAPER_USER_AGENT=Mozilla/5.0 (compatible; StockScanner/1.0)

# Scheduler Configuration
NASDAQ_UPDATE_INTERVAL=10
SCHEDULER_ENABLED=True
SCHEDULER_TIMEZONE=America/New_York

# Performance & Scaling
API_RATE_LIMIT_PER_MINUTE=60
API_RATE_LIMIT_PER_HOUR=1000

# WordPress Integration
WORDPRESS_API_KEY=your-wordpress-api-key
WORDPRESS_SITE_URL=http://localhost

# Monitoring & Health Checks
HEALTH_CHECK_ENABLED=True
MONITORING_ENABLED=True
"""

    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("SUCCESS: Created .env file with database configuration")

def run_django_setup():
    """Run Django migrations and setup"""
    print("\nRUNNING DJANGO SETUP")
    print("-" * 30)
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
    
    commands = [
        ("Making migrations", "python manage.py makemigrations"),
        ("Applying migrations", "python manage.py migrate"),
        ("Collecting static files", "python manage.py collectstatic --noinput")
    ]
    
    for description, command in commands:
        print(f"\n{description}...")
        try:
            result = subprocess.run(command.split(), capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print(f"SUCCESS: {description} completed")
            else:
                print(f"WARNING: {description} had issues: {result.stderr}")
        except Exception as e:
            print(f"ERROR: {description} failed: {e}")
            return False
    
    return True

def start_django_server():
    """Start Django development server"""
    print("\nSTARTING DJANGO SERVER")
    print("-" * 30)
    
    print("Starting Django development server...")
    print("Server will be available at: http://127.0.0.1:8000")
    print("Admin panel: http://127.0.0.1:8000/admin/")
    print("API status: http://127.0.0.1:8000/api/simple/status/")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        # Start server in foreground
        subprocess.run(["python", "manage.py", "runserver", "0.0.0.0:8000"])
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"ERROR: Server failed to start: {e}")

def main():
    """Main server startup routine"""
    print_header("INTERACTIVE STARTUP")
    
    # Check if .env already exists
    if Path(".env").exists():
        use_existing = input("\n.env file already exists. Use existing configuration? (y/n): ").strip().lower()
        if use_existing != 'y':
            # Get new database credentials
            db_config = get_database_credentials()
            if not db_config:
                print("ERROR: Invalid database configuration")
                return
            
            # Test connection
            if not test_database_connection(db_config):
                retry = input("Database connection failed. Continue anyway? (y/n): ").strip().lower()
                if retry != 'y':
                    return
            
            # Create .env file
            create_env_file(db_config)
    else:
        # Get database credentials
        db_config = get_database_credentials()
        if not db_config:
            print("ERROR: Invalid database configuration")
            return
        
        # Test connection
        if not test_database_connection(db_config):
            retry = input("Database connection failed. Continue anyway? (y/n): ").strip().lower()
            if retry != 'y':
                return
        
        # Create .env file
        create_env_file(db_config)
    
    # Run Django setup
    if not run_django_setup():
        print("WARNING: Django setup had issues, but continuing...")
    
    # Start server
    start_django_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nServer startup cancelled by user")
    except Exception as e:
        print(f"\nERROR: Server startup failed: {e}")
        import traceback
        traceback.print_exc()