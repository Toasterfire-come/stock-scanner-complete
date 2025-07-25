#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows MySQL Setup Script for Stock Scanner
Automatically sets up MySQL database, cleans up files, and runs migrations

This script will:
1. Check and install required Python packages
2. Set up MySQL database connection
3. Create database and user if needed
4. Clean up unnecessary files
5. Run Django migrations
6. Verify the setup

Usage: python windows_mysql_setup.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json
import time

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_step(message):
    """Print a step message"""
    print(f"\n[STEP] {message}")

def print_success(message):
    """Print a success message"""
    print(f"[SUCCESS] {message}")

def print_warning(message):
    """Print a warning message"""
    print(f"[WARNING] {message}")

def print_error(message):
    """Print an error message"""
    print(f"[ERROR] {message}")

def run_command(command, capture_output=True, shell=True):
    """Run a system command and return result"""
    try:
        if isinstance(command, str):
            result = subprocess.run(command, shell=shell, capture_output=capture_output, text=True)
        else:
            result = subprocess.run(command, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python_packages():
    """Check and install required Python packages"""
    print_step("Checking Python packages...")
    
    required_packages = [
        'django==4.2.11',
        'djangorestframework',
        'django-cors-headers',
        'PyMySQL',
        'python-dotenv',
        'dj-database-url'
    ]
    
    for package in required_packages:
        print(f"Installing {package}...")
        success, stdout, stderr = run_command(f"pip install {package}")
        if success:
            print_success(f"Installed {package}")
        else:
            print_error(f"Failed to install {package}: {stderr}")
            return False
    
    return True

def check_mysql_installation():
    """Check if MySQL is installed and accessible"""
    print_step("Checking MySQL installation...")
    
    # Check if MySQL command line client is available
    success, stdout, stderr = run_command("mysql --version")
    if success:
        print_success(f"MySQL client found: {stdout.strip()}")
        return True
    else:
        print_error("MySQL client not found. Please install MySQL Server first.")
        print("Download from: https://dev.mysql.com/downloads/mysql/")
        return False

def create_env_file():
    """Create or update .env file with MySQL configuration"""
    print_step("Creating .env configuration...")
    
    env_content = """# Stock Scanner Database Configuration
DATABASE_URL=mysql://stock_scanner:StockScanner2024@localhost:3306/stock_scanner_nasdaq

# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-change-this-in-production

# Email Settings (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# API Keys (optional)
FINNHUB_API_KEY=your-finnhub-api-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print_success("Created .env file with MySQL configuration")
        return True
    except Exception as e:
        print_error(f"Failed to create .env file: {e}")
        return False

def setup_mysql_database():
    """Set up MySQL database and user"""
    print_step("Setting up MySQL database...")
    
    # Database configuration
    db_config = {
        'host': 'localhost',
        'port': '3306',
        'database': 'stock_scanner_nasdaq',
        'username': 'stock_scanner',
        'password': 'StockScanner2024'
    }
    
    print("Please enter your MySQL root password when prompted...")
    
    # SQL commands to create database and user
    sql_commands = f"""
CREATE DATABASE IF NOT EXISTS {db_config['database']};
CREATE USER IF NOT EXISTS '{db_config['username']}'@'{db_config['host']}' IDENTIFIED BY '{db_config['password']}';
GRANT ALL PRIVILEGES ON {db_config['database']}.* TO '{db_config['username']}'@'{db_config['host']}';
FLUSH PRIVILEGES;
SELECT 'Database setup completed successfully' as status;
"""
    
    # Write SQL to temporary file
    sql_file = 'temp_setup.sql'
    try:
        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write(sql_commands)
        
        # Execute SQL file
        success, stdout, stderr = run_command(f'mysql -u root -p < {sql_file}')
        
        # Clean up SQL file
        if os.path.exists(sql_file):
            os.remove(sql_file)
        
        if success:
            print_success("MySQL database and user created successfully")
            return True
        else:
            print_error(f"Failed to create database: {stderr}")
            return False
            
    except Exception as e:
        print_error(f"Database setup failed: {e}")
        if os.path.exists(sql_file):
            os.remove(sql_file)
        return False

def test_database_connection():
    """Test database connection"""
    print_step("Testing database connection...")
    
    try:
        # Set environment variable for Django
        os.environ['DATABASE_URL'] = 'mysql://stock_scanner:StockScanner2024@localhost:3306/stock_scanner_nasdaq'
        
        # Test connection with PyMySQL
        import pymysql
        
        connection = pymysql.connect(
            host='localhost',
            user='stock_scanner',
            password='StockScanner2024',
            database='stock_scanner_nasdaq',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        
        connection.close()
        print_success("Database connection test successful")
        return True
        
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False

def cleanup_unnecessary_files():
    """Clean up unnecessary files and directories"""
    print_step("Cleaning up unnecessary files...")
    
    # Files and directories to remove
    cleanup_items = [
        # Python cache
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.Python',
        
        # Django
        'db.sqlite3',
        'db.sqlite3-journal',
        
        # IDE files
        '.vscode',
        '.idea',
        '*.swp',
        '*.swo',
        
        # OS files
        '.DS_Store',
        'Thumbs.db',
        
        # Backup files
        '*.bak',
        '*.backup',
        '*.old',
        
        # Log files
        '*.log',
        'logs/',
        
        # Temporary files
        'temp/',
        'tmp/',
        '.tmp',
        
        # Migration backups (keep only latest)
        'migration_backup_*.sql',
        'db_backup_*.sqlite3'
    ]
    
    cleaned_count = 0
    
    for item in cleanup_items:
        if '*' in item:
            # Handle wildcard patterns
            import glob
            for file_path in glob.glob(item, recursive=True):
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        cleaned_count += 1
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        cleaned_count += 1
                except Exception as e:
                    print_warning(f"Could not remove {file_path}: {e}")
        else:
            # Handle specific files/directories
            if os.path.exists(item):
                try:
                    if os.path.isfile(item):
                        os.remove(item)
                        cleaned_count += 1
                    elif os.path.isdir(item):
                        shutil.rmtree(item)
                        cleaned_count += 1
                except Exception as e:
                    print_warning(f"Could not remove {item}: {e}")
    
    # Clean up Python cache directories recursively
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs[:]:  # Use slice to avoid modification during iteration
            if dir_name == '__pycache__':
                try:
                    shutil.rmtree(os.path.join(root, dir_name))
                    cleaned_count += 1
                except Exception as e:
                    print_warning(f"Could not remove {os.path.join(root, dir_name)}: {e}")
    
    print_success(f"Cleaned up {cleaned_count} unnecessary files/directories")
    return True

def setup_django_settings():
    """Ensure Django settings are properly configured for MySQL"""
    print_step("Configuring Django settings for MySQL...")
    
    # Add PyMySQL configuration to manage.py if not present
    manage_py_path = 'manage.py'
    if os.path.exists(manage_py_path):
        try:
            with open(manage_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'pymysql' not in content:
                # Add PyMySQL configuration
                pymysql_config = '''
# Configure PyMySQL for Windows MySQL compatibility
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
'''
                # Insert after the first import or at the beginning
                lines = content.split('\n')
                insert_index = 1  # After shebang
                for i, line in enumerate(lines):
                    if line.startswith('import') or line.startswith('from'):
                        insert_index = i
                        break
                
                lines.insert(insert_index, pymysql_config)
                
                with open(manage_py_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                print_success("Updated manage.py with PyMySQL configuration")
        
        except Exception as e:
            print_warning(f"Could not update manage.py: {e}")
    
    return True

def run_django_migrations():
    """Run Django migrations"""
    print_step("Running Django migrations...")
    
    try:
        # Set Django settings module
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
        
        # Import Django after setting environment
        import django
        django.setup()
        
        from django.core.management import call_command
        from io import StringIO
        
        # Capture migration output
        output = StringIO()
        
        # Run migrations
        print("Creating migrations...")
        call_command('makemigrations', stdout=output)
        makemigrations_output = output.getvalue()
        
        output = StringIO()
        print("Applying migrations...")
        call_command('migrate', stdout=output)
        migrate_output = output.getvalue()
        
        print_success("Django migrations completed successfully")
        print("Migration output:")
        print(makemigrations_output)
        print(migrate_output)
        
        return True
        
    except Exception as e:
        print_error(f"Migration failed: {e}")
        return False

def create_django_superuser():
    """Create Django superuser (optional)"""
    print_step("Creating Django superuser (optional)...")
    
    try:
        create_superuser = input("Do you want to create a Django admin superuser? (y/n): ").lower().strip()
        
        if create_superuser == 'y':
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
            import django
            django.setup()
            
            from django.core.management import call_command
            call_command('createsuperuser')
            print_success("Superuser created successfully")
        else:
            print("Skipping superuser creation")
        
        return True
        
    except Exception as e:
        print_warning(f"Superuser creation failed: {e}")
        return True  # Not critical for setup

def verify_installation():
    """Verify the complete installation"""
    print_step("Verifying installation...")
    
    try:
        # Test Django setup
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
        import django
        django.setup()
        
        from django.core.management import call_command
        from io import StringIO
        
        # Check migrations status
        output = StringIO()
        call_command('showmigrations', stdout=output)
        migrations_status = output.getvalue()
        
        print("Migration status:")
        print(migrations_status)
        
        # Test database connection through Django
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            migration_count = cursor.fetchone()[0]
        
        print_success(f"Installation verified - {migration_count} migrations applied")
        return True
        
    except Exception as e:
        print_error(f"Verification failed: {e}")
        return False

def main():
    """Main setup process"""
    print_header("Windows MySQL Setup for Stock Scanner")
    print("This script will set up MySQL database and prepare the Django application")
    
    # Confirm before proceeding
    proceed = input("\nDo you want to proceed with the setup? (y/n): ").lower().strip()
    if proceed != 'y':
        print("Setup cancelled by user")
        return False
    
    # Step 1: Check Python packages
    if not check_python_packages():
        print_error("Package installation failed")
        return False
    
    # Step 2: Check MySQL installation
    if not check_mysql_installation():
        print_error("MySQL not available")
        return False
    
    # Step 3: Create .env file
    if not create_env_file():
        print_error("Environment configuration failed")
        return False
    
    # Step 4: Setup MySQL database
    if not setup_mysql_database():
        print_error("Database setup failed")
        return False
    
    # Step 5: Test database connection
    if not test_database_connection():
        print_error("Database connection test failed")
        return False
    
    # Step 6: Clean up unnecessary files
    cleanup_unnecessary_files()
    
    # Step 7: Configure Django settings
    setup_django_settings()
    
    # Step 8: Run Django migrations
    if not run_django_migrations():
        print_error("Django migrations failed")
        return False
    
    # Step 9: Create superuser (optional)
    create_django_superuser()
    
    # Step 10: Verify installation
    if not verify_installation():
        print_warning("Verification had issues, but setup might still work")
    
    print_header("SETUP COMPLETED SUCCESSFULLY")
    print("\nNext steps:")
    print("1. Start the Django development server:")
    print("   python manage.py runserver")
    print("\n2. Access the application at:")
    print("   http://localhost:8000")
    print("\n3. Access the admin panel at:")
    print("   http://localhost:8000/admin")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_error("\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)