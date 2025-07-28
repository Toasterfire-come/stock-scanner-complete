#!/usr/bin/env python3
"""
Fix Database Connection Issues
Creates the django_user or sets up root access for MySQL
"""

import os
import sys
import subprocess
import pymysql
from pathlib import Path

def test_mysql_connection(host='localhost', port=3306, user='root', password=''):
    """Test MySQL connection"""
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4'
        )
        print(f"✅ Successfully connected to MySQL as {user}")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ Failed to connect as {user}: {e}")
        return False

def create_django_user(host='localhost', port=3306, user='root', password=''):
    """Create django_user with proper permissions"""
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✅ Database 'stockscanner' created/verified")
        
        # Create django_user if it doesn't exist
        cursor.execute("SELECT User FROM mysql.user WHERE User = 'django_user'")
        if not cursor.fetchone():
            cursor.execute("CREATE USER 'django_user'@'localhost' IDENTIFIED BY 'StockScanner2010'")
            print("✅ Created django_user")
        else:
            print("✅ django_user already exists")
        
        # Grant permissions
        cursor.execute("GRANT ALL PRIVILEGES ON stockscanner.* TO 'django_user'@'localhost'")
        cursor.execute("FLUSH PRIVILEGES")
        print("✅ Granted permissions to django_user")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create django_user: {e}")
        return False

def main():
    print("🔧 Database Connection Fix Tool")
    print("=" * 50)
    
    # Test root connection first
    print("\n1. Testing root connection...")
    if test_mysql_connection(user='root', password=''):
        print("✅ Root connection works - using XAMPP MySQL")
        print("\n📝 To use root user, set these environment variables:")
        print("export DB_USER=root")
        print("export DB_PASSWORD=")
        print("export DB_NAME=stockscanner")
        
        # Create database with root
        try:
            connection = pymysql.connect(
                host='localhost',
                port=3306,
                user='root',
                password='',
                charset='utf8mb4'
            )
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            connection.close()
            print("✅ Database 'stockscanner' created with root user")
        except Exception as e:
            print(f"❌ Failed to create database: {e}")
        
    elif test_mysql_connection(user='root', password='root'):
        print("✅ Root connection works with password 'root'")
        print("\n📝 To use root user, set these environment variables:")
        print("export DB_USER=root")
        print("export DB_PASSWORD=root")
        print("export DB_NAME=stockscanner")
        
    else:
        print("❌ Root connection failed")
        print("\n2. Trying to create django_user...")
        if create_django_user():
            print("\n✅ django_user created successfully")
            print("\n📝 Using default django_user credentials:")
            print("export DB_USER=django_user")
            print("export DB_PASSWORD=StockScanner2010")
            print("export DB_NAME=stockscanner")
        else:
            print("❌ Failed to create django_user")
            print("\n🔧 Manual steps required:")
            print("1. Start MySQL service")
            print("2. Connect as root")
            print("3. Create database: CREATE DATABASE stockscanner;")
            print("4. Create user: CREATE USER 'django_user'@'localhost' IDENTIFIED BY 'StockScanner2010';")
            print("5. Grant permissions: GRANT ALL PRIVILEGES ON stockscanner.* TO 'django_user'@'localhost';")
    
    print("\n" + "=" * 50)
    print("🎯 Next steps:")
    print("1. Set the environment variables shown above")
    print("2. Install Django: pip install django pymysql")
    print("3. Run migrations: python manage.py migrate")
    print("4. Test your command again")

if __name__ == "__main__":
    main()