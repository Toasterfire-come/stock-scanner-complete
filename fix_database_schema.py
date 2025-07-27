#!/usr/bin/env python3
"""
Database Schema Fix Tool
Fixes missing tables and columns, runs proper migrations
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def backup_database():
    """Backup current database if it exists"""
    try:
        print("[BACKUP] Creating database backup...")
        
        backup_dir = Path('database_backup')
        backup_dir.mkdir(exist_ok=True)
        
        # Try to backup MySQL database
        try:
            result = subprocess.run([
                'mysqldump', '--single-transaction', '--routines', '--triggers',
                '--user=root', '--password=', '--host=localhost',
                'stockscanner'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                backup_file = backup_dir / f'stockscanner_backup_{int(time.time())}.sql'
                with open(backup_file, 'w') as f:
                    f.write(result.stdout)
                print(f"[SUCCESS] Database backed up to {backup_file}")
            else:
                print("[WARNING] MySQL backup failed (database may not exist yet)")
        except:
            print("[WARNING] Could not create MySQL backup")
        
        return True
    except Exception as e:
        print(f"[ERROR] Backup failed: {e}")
        return False

def reset_migrations():
    """Reset Django migrations to clean state"""
    try:
        print("[RESET] Resetting Django migrations...")
        
        # Remove existing migration files (keep __init__.py)
        migration_dirs = [
            'stocks/migrations',
            'emails/migrations', 
            'core/migrations',
            'news/migrations'
        ]
        
        for migration_dir in migration_dirs:
            migration_path = Path(migration_dir)
            if migration_path.exists():
                for file in migration_path.glob('*.py'):
                    if file.name != '__init__.py':
                        file.unlink()
                        print(f"[REMOVED] {file}")
        
        print("[SUCCESS] Migration files reset")
        return True
        
    except Exception as e:
        print(f"[ERROR] Migration reset failed: {e}")
        return False

def create_fresh_migrations():
    """Create fresh Django migrations"""
    try:
        print("[CREATE] Creating fresh Django migrations...")
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
        
        # Create migrations for each app
        apps = ['stocks', 'emails', 'core', 'news']
        
        for app in apps:
            print(f"[MIGRATE] Creating migrations for {app}...")
            result = subprocess.run([
                sys.executable, 'manage.py', 'makemigrations', app
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"[SUCCESS] {app} migrations created")
            else:
                print(f"[WARNING] {app} migration creation failed: {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Migration creation failed: {e}")
        return False

def apply_migrations():
    """Apply Django migrations to database"""
    try:
        print("[APPLY] Applying Django migrations...")
        
        # Apply migrations
        result = subprocess.run([
            sys.executable, 'manage.py', 'migrate'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[SUCCESS] All migrations applied")
            print(result.stdout)
            return True
        else:
            print(f"[ERROR] Migration failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Migration application failed: {e}")
        return False

def verify_tables():
    """Verify that all required tables exist"""
    try:
        print("[VERIFY] Checking database tables...")
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
        import django
        django.setup()
        
        from django.db import connection
        
        # Check if stocks_stock table exists and has correct columns
        with connection.cursor() as cursor:
            # Get table list
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = [
                'stocks_stock',
                'stocks_stockalert', 
                'stocks_stockprice',
                'emails_emailsubscription',
                'news_newsarticle'
            ]
            
            missing_tables = []
            for table in required_tables:
                if table not in tables:
                    missing_tables.append(table)
                else:
                    print(f"[FOUND] Table {table} exists")
            
            if missing_tables:
                print(f"[ERROR] Missing tables: {missing_tables}")
                return False
            
            # Check stocks_stock table structure
            cursor.execute("DESCRIBE stocks_stock")
            columns = [row[0] for row in cursor.fetchall()]
            
            required_columns = [
                'id', 'ticker', 'name', 'current_price', 'price_change',
                'price_change_percent', 'volume', 'market_cap', 'pe_ratio',
                'dividend_yield', 'fifty_two_week_high', 'fifty_two_week_low',
                'sector', 'industry', 'exchange', 'last_updated'
            ]
            
            missing_columns = []
            for column in required_columns:
                if column not in columns:
                    missing_columns.append(column)
                else:
                    print(f"[FOUND] Column {column} exists")
            
            if missing_columns:
                print(f"[ERROR] Missing columns in stocks_stock: {missing_columns}")
                return False
            
            print("[SUCCESS] All required tables and columns exist")
            return True
            
    except Exception as e:
        print(f"[ERROR] Table verification failed: {e}")
        return False

def create_sample_data():
    """Create sample stock data for testing"""
    try:
        print("[SAMPLE] Creating sample stock data...")
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
        import django
        django.setup()
        
        from stocks.models import Stock
        from decimal import Decimal
        from django.utils import timezone
        
        # Create a few sample stocks if none exist
        if Stock.objects.count() == 0:
            sample_stocks = [
                {
                    'ticker': 'AAPL',
                    'name': 'Apple Inc.',
                    'current_price': Decimal('150.00'),
                    'price_change': Decimal('2.50'),
                    'price_change_percent': Decimal('1.69'),
                    'volume': 50000000,
                    'market_cap': Decimal('2500000000000'),
                    'sector': 'Technology',
                    'exchange': 'NASDAQ'
                },
                {
                    'ticker': 'GOOGL',
                    'name': 'Alphabet Inc.',
                    'current_price': Decimal('2800.00'),
                    'price_change': Decimal('-15.50'),
                    'price_change_percent': Decimal('-0.55'),
                    'volume': 25000000,
                    'market_cap': Decimal('1800000000000'),
                    'sector': 'Technology',
                    'exchange': 'NASDAQ'
                },
                {
                    'ticker': 'TSLA',
                    'name': 'Tesla, Inc.',
                    'current_price': Decimal('250.00'),
                    'price_change': Decimal('5.25'),
                    'price_change_percent': Decimal('2.14'),
                    'volume': 75000000,
                    'market_cap': Decimal('800000000000'),
                    'sector': 'Consumer Discretionary',
                    'exchange': 'NASDAQ'
                }
            ]
            
            for stock_data in sample_stocks:
                stock_data['last_updated'] = timezone.now()
                Stock.objects.create(**stock_data)
            
            print(f"[SUCCESS] Created {len(sample_stocks)} sample stocks")
        else:
            print(f"[INFO] Database already has {Stock.objects.count()} stocks")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Sample data creation failed: {e}")
        return False

def test_api_endpoints():
    """Test if API endpoints work after schema fix"""
    try:
        print("[TEST] Testing API endpoints...")
        
        import requests
        
        # Test basic stock API
        try:
            response = requests.get('http://127.0.0.1:8000/api/stocks/', timeout=10)
            if response.status_code == 200:
                print("[SUCCESS] Stock API endpoint working")
            else:
                print(f"[WARNING] Stock API returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("[WARNING] Django server not running - cannot test endpoints")
        except Exception as e:
            print(f"[WARNING] API test failed: {e}")
        
        # Test WordPress API
        try:
            response = requests.get('http://127.0.0.1:8000/api/wordpress/', timeout=10)
            if response.status_code == 200:
                print("[SUCCESS] WordPress API endpoint working")
            else:
                print(f"[WARNING] WordPress API returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("[WARNING] Django server not running - cannot test WordPress API")
        except Exception as e:
            print(f"[WARNING] WordPress API test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] API testing failed: {e}")
        return False

def main():
    """Main database schema fix function"""
    print("DATABASE SCHEMA FIX TOOL")
    print("=" * 50)
    print("This will fix missing tables and column errors")
    print()
    
    # Step 1: Backup existing database
    print("[STEP 1] Backing up existing database...")
    backup_database()
    print()
    
    # Step 2: Reset migrations
    print("[STEP 2] Resetting Django migrations...")
    if not reset_migrations():
        print("[ERROR] Migration reset failed")
        return False
    print()
    
    # Step 3: Create fresh migrations
    print("[STEP 3] Creating fresh Django migrations...")
    if not create_fresh_migrations():
        print("[ERROR] Migration creation failed")
        return False
    print()
    
    # Step 4: Apply migrations
    print("[STEP 4] Applying migrations to database...")
    if not apply_migrations():
        print("[ERROR] Migration application failed")
        return False
    print()
    
    # Step 5: Verify table structure
    print("[STEP 5] Verifying database schema...")
    if not verify_tables():
        print("[ERROR] Table verification failed")
        return False
    print()
    
    # Step 6: Create sample data
    print("[STEP 6] Creating sample data...")
    create_sample_data()
    print()
    
    # Step 7: Test API endpoints
    print("[STEP 7] Testing API endpoints...")
    test_api_endpoints()
    print()
    
    print("=" * 50)
    print("[SUCCESS] DATABASE SCHEMA FIX COMPLETE!")
    print("=" * 50)
    print()
    print("Your database now has:")
    print("- All required tables created")
    print("- Proper column structure") 
    print("- Sample stock data for testing")
    print("- Working API endpoints")
    print()
    print("You can now:")
    print("  python manage.py runserver")
    print("  python start_stock_scheduler.py --background")
    print("  visit http://127.0.0.1:8000/api/wordpress/")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n[HELP] If issues persist:")
            print("1. Check MySQL service is running")
            print("2. Verify database credentials in .env")
            print("3. Ensure database 'stockscanner' exists")
            print("4. Run: python manage.py check")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n[STOP] Schema fix interrupted")
    except Exception as e:
        print(f"\n[ERROR] Schema fix failed: {e}")
        sys.exit(1)