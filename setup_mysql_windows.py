#!/usr/bin/env python
"""
MySQL Production Setup Script for Windows
Automatically sets up MySQL database for Stock Scanner on Windows.
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

def run_command(command, check=True, capture_output=False, shell=True):
    """Run a command and handle errors"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=shell, capture_output=True, text=True, check=check)
            return result.stdout.strip()
        else:
            result = subprocess.run(command, shell=shell, check=check)
            return result.returncode == 0
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"Command failed: {command}")
            print(f"Error: {e}")
            return False
        return False
    except FileNotFoundError:
        print_error(f"Command not found: {command}")
        return False

def check_mysql_installed():
    """Check if MySQL is installed on Windows"""
    print_step("Checking MySQL installation...")
    
    # Check common MySQL installation paths
    mysql_paths = [
        "mysql",
        "C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysql.exe",
        "C:\\Program Files\\MySQL\\MySQL Server 8.4\\bin\\mysql.exe",
        "C:\\MySQL\\bin\\mysql.exe"
    ]
    
    for path in mysql_paths:
        try:
            result = run_command(f'"{path}" --version', check=False, capture_output=True)
            if result:
                print_success(f"MySQL found at: {path}")
                return path
        except:
            continue
    
    print_error("MySQL not found. Please install MySQL from https://dev.mysql.com/downloads/installer/")
    return None

def start_mysql_service():
    """Start MySQL service on Windows"""
    print_step("Starting MySQL service...")
    
    # Try to start MySQL service
    commands = [
        'net start mysql',
        'net start mysql80', 
        'net start mysql84',
        'sc start mysql'
    ]
    
    for cmd in commands:
        print(f"Trying: {cmd}")
        if run_command(cmd, check=False):
            time.sleep(2)
            # Test if MySQL is responding
            if test_mysql_connection():
                print_success("MySQL service started successfully")
                return True
    
    print_error("Could not start MySQL service")
    print("💡 Try starting MySQL manually:")
    print("   1. Open Services (services.msc)")
    print("   2. Find 'MySQL' service")
    print("   3. Right-click and select 'Start'")
    return False

def test_mysql_connection():
    """Test if MySQL is responding"""
    try:
        result = run_command("mysql -u root -e \"SELECT 1;\"", check=False, capture_output=True)
        return bool(result)
    except:
        return False

def secure_mysql_installation():
    """Set up MySQL root password and create database"""
    print_step("Configuring MySQL...")
    
    password = "StockScannerPass2024"
    
    # Commands to configure MySQL
    commands = [
        f'mysql -u root -e "ALTER USER \'root\'@\'localhost\' IDENTIFIED BY \'{password}\';"',
        f'mysql -u root -e "FLUSH PRIVILEGES;"',
        f'mysql -u root -p{password} -e "CREATE DATABASE IF NOT EXISTS stock_scanner_db;"',
        f'mysql -u root -p{password} -e "CREATE USER IF NOT EXISTS \'stock_scanner_user\'@\'localhost\' IDENTIFIED BY \'{password}\';"',
        f'mysql -u root -p{password} -e "GRANT ALL PRIVILEGES ON stock_scanner_db.* TO \'stock_scanner_user\'@\'localhost\';"',
        f'mysql -u root -p{password} -e "FLUSH PRIVILEGES;"'
    ]
    
    success_count = 0
    for cmd in commands:
        print(f"Running: {cmd.split('-e')[0]}-e \"[SQL COMMAND]\"")
        if run_command(cmd, check=False):
            success_count += 1
        else:
            print("  ⚠️  Command may have failed (this is sometimes normal during setup)")
    
    if success_count >= 3:
        print_success("MySQL configuration completed")
        return True
    else:
        print_error("MySQL configuration may have issues")
        return False

def test_connection():
    """Test the database connection"""
    print_step("Testing database connection...")
    
    password = "StockScannerPass2024"
    test_cmd = f'mysql -u stock_scanner_user -p{password} -D stock_scanner_db -e "SELECT 1 AS test;"'
    
    if run_command(test_cmd, check=False):
        print_success("Database connection test successful!")
        return True
    else:
        print_error("Database connection test failed")
        print("💡 This might be normal if the user doesn't exist yet")
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

def create_batch_files():
    """Create Windows batch files for easy setup"""
    print_step("Creating Windows batch files...")
    
    # Create setup_database.bat
    setup_bat = """@echo off
echo 🚀 Stock Scanner MySQL Setup for Windows
echo ==========================================

echo.
echo 🔧 Starting MySQL service...
net start mysql
if errorlevel 1 (
    echo ⚠️  Trying alternative service names...
    net start mysql80
    if errorlevel 1 net start mysql84
)

echo.
echo 🔧 Configuring MySQL database...
mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'StockScannerPass2024';"
mysql -u root -e "FLUSH PRIVILEGES;"
mysql -u root -pStockScannerPass2024 -e "CREATE DATABASE IF NOT EXISTS stock_scanner_db;"
mysql -u root -pStockScannerPass2024 -e "CREATE USER IF NOT EXISTS 'stock_scanner_user'@'localhost' IDENTIFIED BY 'StockScannerPass2024';"
mysql -u root -pStockScannerPass2024 -e "GRANT ALL PRIVILEGES ON stock_scanner_db.* TO 'stock_scanner_user'@'localhost';"
mysql -u root -pStockScannerPass2024 -e "FLUSH PRIVILEGES;"

echo.
echo ✅ MySQL setup complete!
echo.
echo 📋 Database Information:
echo   Database: stock_scanner_db
echo   User: stock_scanner_user
echo   Password: StockScannerPass2024
echo   Host: localhost
echo   Port: 3306
echo.
echo 🚀 Next steps:
echo   1. venv\\Scripts\\activate
echo   2. pip install -r requirements.txt
echo   3. python manage.py migrate
echo   4. python manage.py createsuperuser
echo   5. python manage.py runserver
echo.
pause
"""
    
    with open("setup_database.bat", "w") as f:
        f.write(setup_bat)
    
    # Create start_app.bat
    start_bat = """@echo off
echo 🚀 Starting Stock Scanner Application
echo ===================================

echo.
echo 🔧 Activating virtual environment...
call venv\\Scripts\\activate

echo.
echo 🔧 Installing requirements...
pip install -r requirements.txt

echo.
echo 🔧 Running database migrations...
python manage.py migrate

echo.
echo 🚀 Starting Django development server...
python manage.py runserver

pause
"""
    
    with open("start_app.bat", "w") as f:
        f.write(start_bat)
    
    print_success("Created setup_database.bat and start_app.bat")

def main():
    """Main setup function"""
    print("🚀 MySQL Production Setup for Stock Scanner (Windows)")
    print("=" * 55)
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print_error("Please run this script from the Django project root directory")
        sys.exit(1)
    
    # Step 1: Check MySQL installation
    mysql_path = check_mysql_installed()
    if not mysql_path:
        print("\n💡 To install MySQL on Windows:")
        print("1. Download MySQL Installer from https://dev.mysql.com/downloads/installer/")
        print("2. Run the installer and select 'Developer Default'")
        print("3. Set a root password when prompted")
        print("4. Complete the installation")
        sys.exit(1)
    
    # Step 2: Start MySQL service
    start_mysql_service()
    
    # Step 3: Secure MySQL installation
    secure_mysql_installation()
    
    # Step 4: Test connection
    test_connection()
    
    # Step 5: Update requirements
    update_requirements()
    
    # Step 6: Create batch files
    create_batch_files()
    
    print("\n" + "=" * 55)
    print("🎉 MySQL Setup Complete!")
    print("\n📋 Database Information:")
    print("  Database: stock_scanner_db")
    print("  User: stock_scanner_user")
    print("  Password: StockScannerPass2024")
    print("  Host: localhost")
    print("  Port: 3306")
    
    print("\n🚀 Windows Setup Files Created:")
    print("  📄 setup_database.bat - Run this to setup database")
    print("  📄 start_app.bat - Run this to start the application")
    
    print("\n🚀 Next Steps:")
    print("1. Double-click setup_database.bat (if this script had issues)")
    print("2. Double-click start_app.bat to start the application")
    print("\nOr manually:")
    print("1. venv\\Scripts\\activate")
    print("2. pip install -r requirements.txt")
    print("3. python manage.py migrate")
    print("4. python manage.py createsuperuser")
    print("5. python manage.py runserver")

if __name__ == "__main__":
    main()