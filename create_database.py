#!/usr/bin/env python
"""
Create MySQL Database Script
Creates the stock_scanner_nasdaq database and runs migrations
"""
import pymysql
import os
import subprocess
import sys

def create_database():
    """Create the MySQL database"""
    try:
        # Connect to MySQL server (without specifying database)
        connection = pymysql.connect(
            host='127.0.0.1',
            user='django_user',
            password='StockScanner2010',
            port=3307
        )
        
        cursor = connection.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS stock_scanner_nasdaq")
        print("SUCCESS: Database 'stock_scanner_nasdaq' created!")
        
        # Verify database exists
        cursor.execute("SHOW DATABASES LIKE 'stock_scanner_nasdaq'")
        result = cursor.fetchone()
        if result:
            print("SUCCESS: Database verified!")
        else:
            print("ERROR: Database not found after creation")
            return False
            
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to create database: {e}")
        return False

def run_migrations():
    """Run Django migrations"""
    try:
        print("\nRunning Django migrations...")
        
        # Run makemigrations
        result = subprocess.run([sys.executable, 'manage.py', 'makemigrations'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("WARNING: makemigrations had issues:")
            print(result.stderr)
        
        # Run migrate
        result = subprocess.run([sys.executable, 'manage.py', 'migrate'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("SUCCESS: All migrations applied!")
            return True
        else:
            print("ERROR: Migration failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to run migrations: {e}")
        return False

def main():
    print("Creating MySQL Database for Stock Scanner")
    print("=" * 50)
    print("Database: stock_scanner_nasdaq")
    print("User: django_user")
    print("Password: StockScanner2010")
    print()
    
    # Step 1: Create database
    if create_database():
        print()
        # Step 2: Run migrations
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
        print("1. Make sure MySQL is running")
        print("2. Verify django_user exists with correct password")
        print("3. Try creating manually: CREATE DATABASE stock_scanner_nasdaq;")

if __name__ == '__main__':
    main()