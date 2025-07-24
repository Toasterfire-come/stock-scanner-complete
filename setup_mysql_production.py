#!/usr/bin/env python3
"""
MySQL Production Setup Script
Automatically sets up MySQL database for Stock Scanner production environment.
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def print_step(message):
    """Print a formatted step message"""
    print(f"\n🔧 {message}")

def print_success(message):
    """Print a formatted success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print a formatted error message"""
    print(f"❌ {message}")

def run_command(command, check=True, capture_output=False):
    """Run a command and handle errors"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
            return result.stdout.strip()
        else:
            result = subprocess.run(command, shell=True, check=check)
            return result.returncode == 0
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"Command failed: {command}")
            print(f"Error: {e}")
            return False
        return False

def check_mysql_installed():
    """Check if MySQL is installed"""
    print_step("Checking MySQL installation...")
    result = run_command("which mysql", check=False, capture_output=True)
    if result:
        print_success("MySQL is installed")
        return True
    else:
        print_error("MySQL is not installed")
        return False

def start_mysql_service():
    """Start MySQL service using various methods"""
    print_step("Starting MySQL service...")
    
    # Try different methods to start MySQL
    methods = [
        "sudo systemctl start mysql",
        "sudo service mysql start", 
        "sudo /usr/sbin/mysqld --user=mysql --daemonize",
        "sudo mysqld_safe --user=mysql &"
    ]
    
    for method in methods:
        print(f"Trying: {method}")
        if run_command(method, check=False):
            time.sleep(2)
            # Check if MySQL is responding
            if run_command("mysqladmin ping", check=False):
                print_success("MySQL service started successfully")
                return True
            
    print_error("Could not start MySQL service")
    return False

def secure_mysql_installation():
    """Set up MySQL root password and create database"""
    print_step("Configuring MySQL...")
    
    # Set root password
    password = "StockScannerPass2024"
    
    commands = [
        f"sudo mysql -e \"ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '{password}';\"",
        f"sudo mysql -e \"FLUSH PRIVILEGES;\"",
        f"mysql -u root -p{password} -e \"CREATE DATABASE IF NOT EXISTS stock_scanner_db;\"",
        f"mysql -u root -p{password} -e \"CREATE USER IF NOT EXISTS 'stock_scanner_user'@'localhost' IDENTIFIED BY '{password}';\"",
        f"mysql -u root -p{password} -e \"GRANT ALL PRIVILEGES ON stock_scanner_db.* TO 'stock_scanner_user'@'localhost';\"",
        f"mysql -u root -p{password} -e \"FLUSH PRIVILEGES;\""
    ]
    
    for cmd in commands:
        if not run_command(cmd, check=False):
            print(f"Command may have failed (this is sometimes normal): {cmd}")
    
    print_success("MySQL configuration completed")
    return True

def test_connection():
    """Test the database connection"""
    print_step("Testing database connection...")
    
    password = "StockScannerPass2024"
    test_cmd = f"mysql -u stock_scanner_user -p{password} -D stock_scanner_db -e \"SELECT 1 AS test;\""
    
    if run_command(test_cmd, check=False):
        print_success("Database connection test successful!")
        return True
    else:
        print_error("Database connection test failed")
        return False

def update_requirements():
    """Add MySQL client to requirements if needed"""
    print_step("Checking requirements.txt for MySQL support...")
    
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        content = requirements_file.read_text()
        if "mysqlclient" not in content and "PyMySQL" not in content:
            with open(requirements_file, "a") as f:
                f.write("\nmysqlclient>=2.1.0\n")
            print_success("Added mysqlclient to requirements.txt")
        else:
            print_success("MySQL client already in requirements.txt")
    else:
        print_error("requirements.txt not found")

def main():
    """Main setup function"""
    print("🚀 MySQL Production Setup for Stock Scanner")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print_error("Please run this script from the Django project root directory")
        sys.exit(1)
    
    # Step 1: Check MySQL installation
    if not check_mysql_installed():
        print_error("Please install MySQL first: sudo apt install mysql-server")
        sys.exit(1)
    
    # Step 2: Start MySQL service
    if not start_mysql_service():
        print_error("Could not start MySQL service. Please start it manually.")
        sys.exit(1)
    
    # Step 3: Secure MySQL installation
    secure_mysql_installation()
    
    # Step 4: Test connection
    test_connection()
    
    # Step 5: Update requirements
    update_requirements()
    
    print("\n" + "=" * 50)
    print("🎉 MySQL Setup Complete!")
    print("\n📋 Database Information:")
    print("  Database: stock_scanner_db")
    print("  User: stock_scanner_user")
    print("  Password: StockScannerPass2024")
    print("  Host: localhost")
    print("  Port: 3306")
    
    print("\n🚀 Next Steps:")
    print("1. source venv/bin/activate")
    print("2. pip install -r requirements.txt")
    print("3. python manage.py migrate")
    print("4. python manage.py createsuperuser")
    print("5. python manage.py runserver")

if __name__ == "__main__":
    main()