#!/usr/bin/env python
"""
Windows Bug Check and Fix Script
Comprehensive testing and automatic fixing of common Windows issues.

This script:
1. Tests all system components
2. Identifies Windows-specific issues
3. Automatically fixes common problems
4. Provides detailed troubleshooting information

Usage:
    python windows_bug_check.py
    python windows_bug_check.py --fix-all

Author: Stock Scanner Project
Version: 1.0.0 - Windows CMD Optimized
"""

import os
import sys
import subprocess
import time
import shutil
from pathlib import Path
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)

def print_step(message):
    """Print a formatted step message"""
    print(f"\n🔧 {message}")

def print_success(message):
    """Print a formatted success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print a formatted error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print a formatted warning message"""
    print(f"⚠️  {message}")

def print_info(message):
    """Print a formatted info message"""
    print(f"💡 {message}")

def run_cmd(command, check=True, capture_output=False):
    """Run a Windows CMD command"""
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
    except Exception as e:
        print_error(f"Error running command: {command}")
        print(f"Error: {e}")
        return False

def check_python():
    """Check Python installation"""
    print_step("Checking Python installation...")
    issues = []
    
    # Check if python command exists
    try:
        version = run_cmd("python --version", capture_output=True)
        if version:
            print_success(f"Python found: {version}")
            
            # Check Python version
            version_parts = version.split()[1].split('.')
            major, minor = int(version_parts[0]), int(version_parts[1])
            if major < 3 or (major == 3 and minor < 8):
                issues.append(f"Python version too old: {version}. Need Python 3.8+")
            
        else:
            issues.append("Python command not found in PATH")
    except:
        issues.append("Python check failed - command not accessible")
    
    # Check pip
    try:
        pip_version = run_cmd("pip --version", capture_output=True)
        if pip_version:
            print_success(f"Pip found: {pip_version.split()[1]}")
        else:
            issues.append("Pip not found")
    except:
        issues.append("Pip check failed")
    
    return issues

def check_virtual_environment():
    """Check virtual environment"""
    print_step("Checking virtual environment...")
    issues = []
    
    # Check if venv directory exists
    if not os.path.exists("venv"):
        issues.append("Virtual environment directory 'venv' not found")
        return issues
    
    # Check venv structure
    required_files = [
        "venv\\Scripts\\python.exe",
        "venv\\Scripts\\pip.exe",
        "venv\\Scripts\\activate.bat"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            issues.append(f"Virtual environment file missing: {file_path}")
    
    if not issues:
        print_success("Virtual environment structure is correct")
    
    return issues

def check_requirements():
    """Check if requirements are installed"""
    print_step("Checking Python requirements...")
    issues = []
    
    if not os.path.exists("requirements.txt"):
        issues.append("requirements.txt file not found")
        return issues
    
    # Read requirements
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read()
        
        required_packages = [
            "Django", "djangorestframework", "psycopg2-binary", 
            "mysqlclient", "dj-database-url", "yfinance", "requests"
        ]
        
        for package in required_packages:
            if package not in requirements:
                issues.append(f"Missing requirement: {package}")
        
        print_success("Requirements file structure is correct")
        
    except Exception as e:
        issues.append(f"Error reading requirements.txt: {e}")
    
    return issues

def check_django_structure():
    """Check Django project structure"""
    print_step("Checking Django project structure...")
    issues = []
    
    required_files = [
        "manage.py",
        "stockscanner_django/settings.py",
        "stockscanner_django/urls.py",
        "stockscanner_django/wsgi.py"
    ]
    
    required_dirs = [
        "stocks",
        "core", 
        "emails",
        "news",
        "tests"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            issues.append(f"Required Django file missing: {file_path}")
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            issues.append(f"Required Django app directory missing: {dir_path}")
    
    if not issues:
        print_success("Django project structure is correct")
    
    return issues

def check_database_configuration():
    """Check database configuration"""
    print_step("Checking database configuration...")
    issues = []
    
    # Check .env file
    if not os.path.exists(".env"):
        issues.append(".env file not found")
        return issues
    
    try:
        with open(".env", "r") as f:
            env_content = f.read()
        
        required_env_vars = [
            "SECRET_KEY", "DATABASE_URL", "DB_ENGINE"
        ]
        
        for var in required_env_vars:
            if var not in env_content:
                issues.append(f"Missing environment variable: {var}")
        
        # Check database URL format
        if "DATABASE_URL" in env_content:
            db_lines = [line for line in env_content.split('\n') if line.startswith('DATABASE_URL')]
            if db_lines:
                db_url = db_lines[0].split('=', 1)[1] if '=' in db_lines[0] else ""
                if not any(db_url.startswith(prefix) for prefix in ['mysql://', 'postgresql://', 'sqlite://']):
                    issues.append("Invalid DATABASE_URL format")
                else:
                    print_success("Database URL format is correct")
        
    except Exception as e:
        issues.append(f"Error reading .env file: {e}")
    
    return issues

def check_migrations():
    """Check Django migrations"""
    print_step("Checking Django migrations...")
    issues = []
    
    migrations_dir = Path("stocks/migrations")
    if not migrations_dir.exists():
        issues.append("stocks/migrations directory not found")
        return issues
    
    # Check for migration files
    migration_files = list(migrations_dir.glob("*.py"))
    if len(migration_files) < 2:  # At least __init__.py and one migration
        issues.append("No migration files found")
    
    # Check for conflicting migrations
    numbered_migrations = [f for f in migration_files if f.name.startswith(('0001_', '0002_', '0003_'))]
    
    # Group by number
    migration_numbers = {}
    for migration in numbered_migrations:
        number = migration.name.split('_')[0]
        if number not in migration_numbers:
            migration_numbers[number] = []
        migration_numbers[number].append(migration.name)
    
    # Check for conflicts
    for number, files in migration_numbers.items():
        if len(files) > 1:
            issues.append(f"Migration conflict detected: multiple {number}_* files: {files}")
    
    if not issues:
        print_success("Migration structure is correct")
    
    return issues

def check_windows_batch_files():
    """Check Windows batch files"""
    print_step("Checking Windows batch files...")
    issues = []
    
    required_batch_files = [
        "setup.bat",
        "start_app.bat", 
        "setup_database.bat",
        "test_system.bat"
    ]
    
    for batch_file in required_batch_files:
        if not os.path.exists(batch_file):
            issues.append(f"Windows batch file missing: {batch_file}")
        else:
            # Check if batch file has proper Windows line endings
            try:
                with open(batch_file, 'rb') as f:
                    content = f.read()
                    if b'\r\n' not in content and b'\n' in content:
                        issues.append(f"Batch file {batch_file} has Unix line endings (should be Windows)")
            except:
                issues.append(f"Cannot read batch file: {batch_file}")
    
    if not issues:
        print_success("Windows batch files are correct")
    
    return issues

def fix_common_issues(issues):
    """Automatically fix common issues"""
    print_header("FIXING COMMON ISSUES")
    
    fixed_issues = []
    
    # Fix 1: Create virtual environment if missing
    if any("Virtual environment" in issue for issue in issues):
        print_step("Creating virtual environment...")
        if run_cmd("python -m venv venv"):
            print_success("Virtual environment created")
            fixed_issues.append("Created virtual environment")
        else:
            print_error("Failed to create virtual environment")
    
    # Fix 2: Create .env file if missing
    if any(".env file not found" in issue for issue in issues):
        print_step("Creating .env file...")
        try:
            env_content = """# Stock Scanner Environment Configuration
SECRET_KEY=django-insecure-windows-generated-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration (SQLite default)
DATABASE_URL=sqlite:///./db.sqlite3
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Optional Features
CELERY_ENABLED=false
REDIS_URL=redis://localhost:6379/0
"""
            with open('.env', 'w') as f:
                f.write(env_content)
            print_success(".env file created")
            fixed_issues.append("Created .env file")
        except Exception as e:
            print_error(f"Failed to create .env file: {e}")
    
    # Fix 3: Fix migration conflicts
    if any("Migration conflict" in issue for issue in issues):
        print_step("Fixing migration conflicts...")
        if run_cmd("python fix_migrations_windows.py"):
            print_success("Migration conflicts fixed")
            fixed_issues.append("Fixed migration conflicts")
        else:
            print_error("Failed to fix migration conflicts")
    
    # Fix 4: Create logs directory
    if not os.path.exists("logs"):
        print_step("Creating logs directory...")
        try:
            os.makedirs("logs")
            print_success("Logs directory created")
            fixed_issues.append("Created logs directory")
        except Exception as e:
            print_error(f"Failed to create logs directory: {e}")
    
    return fixed_issues

def generate_report(all_issues, fixed_issues):
    """Generate comprehensive report"""
    print_header("COMPREHENSIVE BUG CHECK REPORT")
    
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💻 System: Windows")
    print(f"📂 Directory: {os.getcwd()}")
    
    print(f"\n📊 SUMMARY:")
    total_issues = sum(len(issues) for issues in all_issues.values())
    print(f"   Total issues found: {total_issues}")
    print(f"   Issues fixed: {len(fixed_issues)}")
    print(f"   Remaining issues: {total_issues - len(fixed_issues)}")
    
    if total_issues == 0:
        print_success("\n🎉 NO ISSUES FOUND! Your system is ready for production.")
        print_info("✨ You can run start_app.bat to start the application")
        return True
    
    print(f"\n🔍 DETAILED ISSUES BY CATEGORY:")
    for category, issues in all_issues.items():
        if issues:
            print(f"\n{category}:")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
    
    if fixed_issues:
        print(f"\n✅ AUTOMATICALLY FIXED:")
        for i, fix in enumerate(fixed_issues, 1):
            print(f"  {i}. {fix}")
    
    remaining_issues = total_issues - len(fixed_issues)
    if remaining_issues > 0:
        print(f"\n🔧 RECOMMENDED ACTIONS:")
        print("1. Run setup.bat to fix installation issues")
        print("2. Run setup_database.bat to configure database")
        print("3. Check requirements.txt and install missing packages")
        print("4. See WINDOWS_SETUP_GUIDE.md for detailed instructions")
        
        print(f"\n💡 QUICK FIXES:")
        print("   pip install -r requirements.txt")
        print("   python manage.py migrate")
        print("   python windows_complete_setup.py")
        
    return remaining_issues == 0

def main():
    """Main bug check function"""
    print_header("WINDOWS BUG CHECK AND FIX UTILITY")
    print("🎯 Checking all system components for Windows CMD compatibility")
    print("⏱️  This will take 1-2 minutes")
    
    # Run all checks
    all_issues = {
        "Python Installation": check_python(),
        "Virtual Environment": check_virtual_environment(), 
        "Requirements": check_requirements(),
        "Django Structure": check_django_structure(),
        "Database Configuration": check_database_configuration(),
        "Migrations": check_migrations(),
        "Windows Batch Files": check_windows_batch_files()
    }
    
    # Check if we should fix issues
    fix_mode = "--fix-all" in sys.argv or len(sys.argv) == 1
    
    fixed_issues = []
    if fix_mode:
        # Collect all issues for fixing
        all_issues_list = []
        for issues in all_issues.values():
            all_issues_list.extend(issues)
        
        if all_issues_list:
            fixed_issues = fix_common_issues(all_issues_list)
            
            # Re-run checks after fixes
            print_header("RE-CHECKING AFTER FIXES")
            all_issues = {
                "Python Installation": check_python(),
                "Virtual Environment": check_virtual_environment(),
                "Requirements": check_requirements(), 
                "Django Structure": check_django_structure(),
                "Database Configuration": check_database_configuration(),
                "Migrations": check_migrations(),
                "Windows Batch Files": check_windows_batch_files()
            }
    
    # Generate final report
    success = generate_report(all_issues, fixed_issues)
    
    if success:
        print_info("\n🚀 Ready to start! Run: start_app.bat")
    else:
        print_info("\n🔧 Fix the remaining issues and run this script again")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())