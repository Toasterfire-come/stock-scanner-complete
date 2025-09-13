#!/usr/bin/env python
"""
Create Django Superuser Script
Works with Git Bash and non-TTY environments
"""
import os
import sys
import django
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

# Configure PyMySQL for MySQL compatibility
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    print("PyMySQL configured for MySQL compatibility")
except ImportError:
    print("PyMySQL not available")

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

def create_superuser():
    """Create a superuser account"""
    User = get_user_model()
    
    # Default credentials
    username = 'admin'
    email = 'admin@retailstockscanner.com'
    password = 'StockScanner2010'
    
    try:
        # Check if superuser already exists
        if User.objects.filter(username=username).exists():
            print(f"SUCCESS: Superuser '{username}' already exists!")
            user = User.objects.get(username=username)
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Is Active: {user.is_active}")
            print(f"   Is Superuser: {user.is_superuser}")
            return
        
        # Create new superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        print("SUCCESS: Superuser created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Admin URL: http://127.0.0.1:8000/admin/")
        
        return user
        
    except Exception as e:
        print(f"ERROR: Error creating superuser: {e}")
        return None

def show_login_info():
    """Display login information"""
    print("\n" + "="*60)
    print("DJANGO ADMIN LOGIN INFORMATION")
    print("="*60)
    print("Admin URL: http://127.0.0.1:8000/admin/")
    print("Username: admin")
    print("Password: StockScanner2010")
    print("Email: admin@retailstockscanner.com")
    print("="*60)
    print("Save these credentials for future use!")
    print("Start server: python manage.py runserver")

if __name__ == '__main__':
    print("Creating Django Superuser...")
    print("Database: MySQL (stock_scanner_nasdaq)")
    print("Environment: Git Bash Compatible")
    print()
    
    create_superuser()
    show_login_info()