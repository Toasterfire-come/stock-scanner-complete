#!/usr/bin/env python3
"""
Stock Scanner Project Cleanup & Organization Script
Cleans up the project structure with clear separations and removes redundant files.

This script:
1. Creates organized directory structure
2. Moves files to appropriate locations
3. Removes redundant/obsolete files
4. Creates clean documentation structure
5. Maintains only essential files in root

Author: Stock Scanner Project
Version: 1.0.0
"""

import os
import shutil
import glob
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"🧹 {title}")
    print("=" * 70)

def print_step(message):
    """Print a formatted step message"""
    print(f"\n🔧 {message}")

def print_success(message):
    """Print a formatted success message"""
    print(f"✅ {message}")

def print_warning(message):
    """Print a formatted warning message"""
    print(f"⚠️  {message}")

def print_info(message):
    """Print a formatted info message"""
    print(f"💡 {message}")

def ensure_directory(path):
    """Ensure directory exists"""
    Path(path).mkdir(parents=True, exist_ok=True)
    return path

def move_file_safe(source, destination):
    """Safely move a file, creating destination directory if needed"""
    try:
        if os.path.exists(source):
            ensure_directory(os.path.dirname(destination))
            if os.path.exists(destination):
                os.remove(destination)
            shutil.move(source, destination)
            return True
    except Exception as e:
        print_warning(f"Failed to move {source} to {destination}: {e}")
    return False

def delete_file_safe(file_path):
    """Safely delete a file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print_warning(f"Failed to delete {file_path}: {e}")
    return False

def create_directory_structure():
    """Create the new organized directory structure"""
    print_step("Creating organized directory structure...")
    
    directories = [
        # Setup and Installation
        "setup/windows",
        "setup/mysql", 
        "setup/requirements",
        
        # Management Tools
        "tools/database",
        "tools/django",
        "tools/testing",
        "tools/monitoring",
        
        # Documentation
        "docs/setup",
        "docs/production",
        "docs/troubleshooting",
        "docs/api",
        
        # Utilities
        "utils/windows",
        "utils/database",
        "utils/common",
        
        # Backup location for removed files
        "cleanup_backup"
    ]
    
    for directory in directories:
        ensure_directory(directory)
        print_success(f"Created: {directory}/")

def organize_setup_files():
    """Move setup-related files to appropriate locations"""
    print_step("Organizing setup files...")
    
    # Windows setup files
    setup_moves = [
        ("SIMPLE_START.bat", "setup/SIMPLE_START.bat"),
        ("setup.bat", "setup/windows/setup.bat"),
        ("setup_mysql_windows.bat", "setup/mysql/setup_mysql_windows.bat"),
        ("emergency_setup_windows.bat", "setup/windows/emergency_setup_windows.bat"),
        ("windows_complete_setup.py", "setup/windows/windows_complete_setup.py"),
        ("setup_mysql_production_complete.py", "setup/mysql/setup_mysql_production_complete.py"),
        ("install_windows_safe.py", "setup/requirements/install_windows_safe.py"),
    ]
    
    for source, dest in setup_moves:
        if move_file_safe(source, dest):
            print_success(f"Moved: {source} → {dest}")

def organize_database_tools():
    """Move database-related tools"""
    print_step("Organizing database tools...")
    
    db_moves = [
        ("fix_django_settings_error.py", "tools/database/fix_django_settings_error.py"),
        ("fix_postgresql_permissions.py", "tools/database/fix_postgresql_permissions.py"),
        ("switch_to_sqlite.py", "tools/database/switch_to_sqlite.py"),
        ("update_env_database.py", "tools/database/update_env_database.py"),
        ("fix_migrations_windows.py", "tools/database/fix_migrations_windows.py"),
        ("fix_migrations.bat", "tools/database/fix_migrations.bat"),
        ("fix_database_issues.bat", "tools/database/fix_database_issues.bat"),
        ("setup_database.bat", "tools/database/setup_database.bat"),
    ]
    
    for source, dest in db_moves:
        if move_file_safe(source, dest):
            print_success(f"Moved: {source} → {dest}")

def organize_django_tools():
    """Move Django management tools"""
    print_step("Organizing Django tools...")
    
    django_moves = [
        ("start_app.bat", "tools/django/start_app.bat"),
        ("test_django_startup.py", "tools/django/test_django_startup.py"),
        ("run_migrations.py", "tools/django/run_migrations.py"),
    ]
    
    for source, dest in django_moves:
        if move_file_safe(source, dest):
            print_success(f"Moved: {source} → {dest}")

def organize_testing_tools():
    """Move testing and debugging tools"""
    print_step("Organizing testing tools...")
    
    test_moves = [
        ("test_system.bat", "tools/testing/test_system.bat"),
        ("windows_bug_check.py", "tools/testing/windows_bug_check.py"),
    ]
    
    for source, dest in test_moves:
        if move_file_safe(source, dest):
            print_success(f"Moved: {source} → {dest}")

def organize_windows_utilities():
    """Move Windows-specific utilities"""
    print_step("Organizing Windows utilities...")
    
    windows_moves = [
        ("fix_numpy_windows.bat", "utils/windows/fix_numpy_windows.bat"),
        ("fix_windows_compiler_issues.bat", "utils/windows/fix_windows_compiler_issues.bat"),
    ]
    
    for source, dest in windows_moves:
        if move_file_safe(source, dest):
            print_success(f"Moved: {source} → {dest}")

def organize_requirements():
    """Organize requirements files"""
    print_step("Organizing requirements files...")
    
    req_moves = [
        ("requirements-minimal.txt", "setup/requirements/requirements-minimal.txt"),
        ("requirements-windows.txt", "setup/requirements/requirements-windows.txt"),
    ]
    
    for source, dest in req_moves:
        if move_file_safe(source, dest):
            print_success(f"Moved: {source} → {dest}")

def organize_documentation():
    """Organize documentation files"""
    print_step("Organizing documentation...")
    
    # Move specific docs to appropriate folders
    doc_moves = [
        ("SIMPLE_SETUP_README.md", "docs/setup/SIMPLE_SETUP_README.md"),
        ("WINDOWS_SETUP_GUIDE.md", "docs/setup/WINDOWS_SETUP_GUIDE.md"),
        ("docs/MYSQL_PRODUCTION_GUIDE.md", "docs/production/MYSQL_PRODUCTION_GUIDE.md"),
        ("docs/WINDOWS_PRODUCTION_DEPLOYMENT_GUIDE.md", "docs/production/WINDOWS_PRODUCTION_DEPLOYMENT_GUIDE.md"),
        ("PROJECT_AUDIT_REPORT.md", "docs/troubleshooting/PROJECT_AUDIT_REPORT.md"),
        ("WINDOWS_CMD_SUMMARY.md", "docs/troubleshooting/WINDOWS_CMD_SUMMARY.md"),
    ]
    
    for source, dest in doc_moves:
        if move_file_safe(source, dest):
            print_success(f"Moved: {source} → {dest}")

def remove_redundant_files():
    """Remove redundant and obsolete files"""
    print_step("Removing redundant files...")
    
    # Files to remove (backup first)
    redundant_files = [
        # Obsolete documentation
        "docs/COMPLETE_START_GUIDE.md",  # Replaced by SIMPLE_SETUP_README.md
        "docs/YFINANCE_RATE_LIMIT_GUIDE.md",  # No longer needed
        "docs/INTEGRATION_SUMMARY.md",  # Redundant
        "docs/COMPLETE_INTEGRATION_SUMMARY.md",  # Redundant
        "docs/PACKAGE_MANIFEST.md",  # Redundant
        "docs/DJANGO_WORDPRESS_INTEGRATION.md",  # Separate from core
    ]
    
    backup_count = 0
    for file_path in redundant_files:
        if os.path.exists(file_path):
            backup_path = f"cleanup_backup/{os.path.basename(file_path)}"
            if move_file_safe(file_path, backup_path):
                print_success(f"Backed up and removed: {file_path}")
                backup_count += 1
    
    print_info(f"Backed up {backup_count} redundant files to cleanup_backup/")

def create_directory_readmes():
    """Create README files for each organized directory"""
    print_step("Creating directory documentation...")
    
    readmes = {
        "setup/README.md": """# Setup Scripts

This directory contains all installation and setup scripts.

## Quick Start
- **SIMPLE_START.bat** - One-command setup (RECOMMENDED)

## Windows Setup
- **windows/** - Windows-specific setup scripts
- **mysql/** - MySQL database setup scripts  
- **requirements/** - Python package installation scripts

## Usage
For first-time setup: `SIMPLE_START.bat`
""",
        
        "tools/README.md": """# Management Tools

This directory contains tools for managing the Stock Scanner application.

## Database Tools
- **database/** - Database setup, migration, and troubleshooting tools

## Django Tools  
- **django/** - Django application management scripts

## Testing Tools
- **testing/** - System testing and debugging utilities

## Monitoring Tools
- **monitoring/** - Health checks and performance monitoring
""",
        
        "docs/README.md": """# Documentation

Complete documentation for the Stock Scanner project.

## Quick Start
- **setup/** - Installation and setup guides
- **production/** - Production deployment guides
- **troubleshooting/** - Problem-solving guides
- **api/** - API documentation

## Main Guides
- **setup/SIMPLE_SETUP_README.md** - Easiest way to get started
- **production/MYSQL_PRODUCTION_GUIDE.md** - Production database setup
- **production/WINDOWS_PRODUCTION_DEPLOYMENT_GUIDE.md** - Complete production deployment
""",
        
        "utils/README.md": """# Utilities

Shared utility functions and platform-specific tools.

## Windows Utilities
- **windows/** - Windows-specific fixes and utilities

## Database Utilities
- **database/** - Database helper functions

## Common Utilities
- **common/** - Shared utility functions
"""
    }
    
    for readme_path, content in readmes.items():
        ensure_directory(os.path.dirname(readme_path))
        with open(readme_path, 'w') as f:
            f.write(content)
        print_success(f"Created: {readme_path}")

def create_main_launchers():
    """Create main launcher scripts in root"""
    print_step("Creating main launcher scripts...")
    
    # Simple launcher that points to the organized structure
    launcher_content = """@echo off
title Stock Scanner - Quick Start
echo.
echo 🚀 Stock Scanner Quick Start
echo ============================
echo.
echo Choose your setup option:
echo.
echo 1. 🚀 SIMPLE START (Recommended) - One command does everything
echo 2. 🔧 Advanced Setup - Full control over installation
echo 3. 🗄️  Database Only - Just setup/fix database
echo 4. 🧪 Test System - Check if everything works
echo 5. 📖 View Documentation
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo Starting simple setup...
    call setup\\SIMPLE_START.bat
) else if "%choice%"=="2" (
    echo Opening advanced setup...
    call setup\\windows\\setup.bat
) else if "%choice%"=="3" (
    echo Opening database tools...
    call tools\\database\\setup_database.bat
) else if "%choice%"=="4" (
    echo Running system tests...
    call tools\\testing\\test_system.bat
) else if "%choice%"=="5" (
    echo Opening documentation...
    start docs\\README.md
) else (
    echo Invalid choice. Please run again.
    pause
)
"""
    
    with open("START_HERE.bat", 'w') as f:
        f.write(launcher_content)
    print_success("Created: START_HERE.bat - Main launcher script")

def update_main_readme():
    """Update the main README with the new structure"""
    print_step("Updating main README...")
    
    new_readme_content = """# 📊 Stock Scanner - Complete Business Platform

A comprehensive stock monitoring and membership platform featuring real-time analytics, 4-tier membership system, automatic sales tax collection, and full WordPress integration.

## 🚀 SUPER QUICK START

### 🎯 **Just want it to work?**

**Double-click: `START_HERE.bat`**

Then choose option 1 (Simple Start) for one-command setup!

---

## 📁 Project Structure

```
stock-scanner-complete/
├── 🚀 START_HERE.bat           # Main launcher (START HERE!)
├── 📖 README.md                # This file
├── 📋 requirements.txt         # Main Python requirements
├── ⚙️  manage.py               # Django management script
│
├── 🔧 setup/                   # All setup scripts
│   ├── SIMPLE_START.bat        # One-command setup
│   ├── windows/                # Windows-specific setup
│   ├── mysql/                  # MySQL database setup
│   └── requirements/           # Python package tools
│
├── 🛠️  tools/                  # Management tools
│   ├── database/               # Database management
│   ├── django/                 # Django management
│   ├── testing/                # System testing
│   └── monitoring/             # Health monitoring
│
├── 📚 docs/                    # Documentation
│   ├── setup/                  # Installation guides
│   ├── production/             # Production deployment
│   ├── troubleshooting/        # Problem solving
│   └── api/                    # API documentation
│
├── 🧰 utils/                   # Utilities
│   ├── windows/                # Windows-specific tools
│   ├── database/               # Database utilities
│   └── common/                 # Shared functions
│
└── 🏗️  Application Code/       # Django application
    ├── stocks/                 # Stock scanning app
    ├── core/                   # Core functionality
    ├── emails/                 # Email management
    ├── news/                   # News integration
    └── stockscanner_django/    # Django project settings
```

---

## 🎯 Quick Navigation

### **First Time Setup:**
1. **`START_HERE.bat`** → Option 1 (Simple Start)
2. Wait 15-20 minutes
3. Application opens in browser
4. Done!

### **Daily Use:**
- **`start_stock_scanner.bat`** (created after first setup)

### **Need Help:**
- **`docs/setup/SIMPLE_SETUP_README.md`** - Simple setup guide
- **`docs/troubleshooting/`** - Problem solving
- **`START_HERE.bat`** → Option 4 (Test System)

---

## 🔧 What's Included

### **Core Features:**
- 📊 Real-time stock data monitoring
- 🚨 Automated price alerts
- 📈 Portfolio tracking and analytics
- 👥 4-tier membership system
- 💳 Stripe payment integration
- 🌐 WordPress integration
- 📧 Email notification system

### **Technical Stack:**
- **Backend:** Django 5.1+ with MySQL production database
- **Frontend:** Modern responsive web interface
- **Data:** Yahoo Finance API integration
- **Payments:** Stripe integration
- **Email:** SMTP email system
- **Deployment:** Production-ready Windows deployment

### **Membership Tiers:**
1. **Free** - Basic stock alerts
2. **Premium** ($10/month) - Advanced analytics
3. **Pro** ($25/month) - Portfolio management
4. **Enterprise** ($50/month) - Full platform access

---

## 📋 Prerequisites

**Only 2 things needed:**

1. **Python 3.8+** - [Download here](https://python.org/downloads/)
   - ⚠️ **IMPORTANT:** Check "Add Python to PATH" during installation

2. **MySQL Server 8.0+** - [Download here](https://dev.mysql.com/downloads/mysql/)
   - ⚠️ **IMPORTANT:** Set root password to `StockScannerRoot2024!` during installation

---

## 🆘 Support

### **Common Issues:**
- **Python not found** → Install Python and check "Add to PATH"
- **MySQL not found** → Install MySQL with password `StockScannerRoot2024!`
- **Setup fails** → Run `START_HERE.bat` → Option 4 (Test System)

### **Get Help:**
1. Check `docs/troubleshooting/`
2. Run system diagnostics: `START_HERE.bat` → Option 4
3. View setup logs in `logs/` directory
4. GitHub Issues: [Report problems here](https://github.com/Toasterfire-come/stock-scanner-complete/issues)

---

## 🏆 Production Ready

This platform is production-ready with:
- ✅ **Secure MySQL database** with connection pooling
- ✅ **Professional UI/UX** with responsive design
- ✅ **Payment processing** via Stripe
- ✅ **Email notifications** for alerts and updates
- ✅ **WordPress integration** for content management
- ✅ **Automated backups** and monitoring
- ✅ **Windows deployment** scripts and guides

---

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🚀 Ready to start? Double-click `START_HERE.bat` and choose Simple Start!**
"""
    
    with open("README.md", 'w') as f:
        f.write(new_readme_content)
    print_success("Updated main README.md with clean structure")

def main():
    """Main cleanup function"""
    print_header("STOCK SCANNER PROJECT CLEANUP & ORGANIZATION")
    print("🎯 Organizing project with clear separations")
    print("⏱️  Estimated time: 2-3 minutes")
    print("🔒 All removed files will be backed up")
    
    try:
        # Create organized structure
        create_directory_structure()
        
        # Move files to appropriate locations
        organize_setup_files()
        organize_database_tools() 
        organize_django_tools()
        organize_testing_tools()
        organize_windows_utilities()
        organize_requirements()
        organize_documentation()
        
        # Remove redundant files (with backup)
        remove_redundant_files()
        
        # Create documentation
        create_directory_readmes()
        create_main_launchers()
        update_main_readme()
        
        print_header("CLEANUP COMPLETE!")
        print_success("🎉 Project successfully organized!")
        print("")
        print("📁 New Structure:")
        print("   ✅ setup/ - All installation scripts")
        print("   ✅ tools/ - Management and utilities") 
        print("   ✅ docs/ - Organized documentation")
        print("   ✅ utils/ - Shared utilities")
        print("   ✅ cleanup_backup/ - Removed files backup")
        print("")
        print("🚀 Next Steps:")
        print("   1. Double-click START_HERE.bat")
        print("   2. Choose option 1 (Simple Start)")
        print("   3. Wait for setup to complete")
        print("   4. Application opens in browser")
        print("")
        print("💡 Main entry points:")
        print("   - START_HERE.bat - Main launcher")
        print("   - setup/SIMPLE_START.bat - Direct simple setup")
        print("   - docs/README.md - Complete documentation")
        
        return True
        
    except Exception as e:
        print_warning(f"Cleanup encountered an error: {e}")
        print_info("Check cleanup_backup/ directory for any moved files")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n{'✅ SUCCESS' if success else '❌ COMPLETED WITH ISSUES'}")
    input("\nPress Enter to continue...")