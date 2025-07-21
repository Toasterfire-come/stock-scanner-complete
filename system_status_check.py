#!/usr/bin/env python3
"""
Stock Scanner System Status Check
Comprehensive verification of all system components
"""

import os
import sys
import sqlite3
import json
import subprocess
from pathlib import Path
from datetime import datetime

class SystemStatusCheck:
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0
        self.project_root = Path(__file__).parent
        
    def print_header(self):
        """Print system check header"""
        print("=" * 80)
        print("🔍 STOCK SCANNER SYSTEM STATUS CHECK")
        print("=" * 80)
        print(f"📅 Check Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📂 Project Root: {self.project_root}")
        print("=" * 80)
        
    def print_section(self, title):
        """Print section header"""
        print(f"\n📋 {title.upper()}")
        print("-" * 60)
        
    def print_check(self, check_name, status, details=""):
        """Print individual check result"""
        if status == "PASS":
            print(f"✅ {check_name}: {status}")
            self.checks_passed += 1
        elif status == "FAIL":
            print(f"❌ {check_name}: {status}")
            if details:
                print(f"   💡 {details}")
            self.checks_failed += 1
        elif status == "WARN":
            print(f"⚠️  {check_name}: WARNING")
            if details:
                print(f"   💡 {details}")
            self.warnings += 1
        else:
            print(f"ℹ️  {check_name}: {status}")
            
    def check_python_version(self):
        """Check Python version compatibility"""
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            self.print_check("Python Version", "PASS", f"Python {version.major}.{version.minor}.{version.micro}")
        else:
            self.print_check("Python Version", "FAIL", f"Python {version.major}.{version.minor}.{version.micro} - Need Python 3.8+")
            
    def check_essential_files(self):
        """Check for essential project files"""
        essential_files = [
            "manage.py",
            "requirements.txt",
            "requirements_updated.txt",
            ".env.sample",
            "database_settings_local.py",
            "setup_local.py",
            "README.md",
            "COMPLETE_SETUP_GUIDE.md"
        ]
        
        for file_path in essential_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.print_check(f"File: {file_path}", "PASS")
            else:
                self.print_check(f"File: {file_path}", "FAIL", "File missing")
                
    def check_directory_structure(self):
        """Check Django app directory structure"""
        required_dirs = [
            "stockscanner_django",
            "stocks",
            "emails", 
            "core",
            "news",
            "wordpress_integration",
            "wordpress_deployment_package"
        ]
        
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                self.print_check(f"Directory: {dir_name}", "PASS")
            else:
                self.print_check(f"Directory: {dir_name}", "FAIL", "Directory missing")
                
    def check_database_config(self):
        """Check database configuration"""
        try:
            # Import database settings
            sys.path.insert(0, str(self.project_root))
            from database_settings_local import DATABASES, test_database_connection
            
            # Check database configuration
            if 'default' in DATABASES:
                db_config = DATABASES['default']
                if db_config['ENGINE'] == 'django.db.backends.sqlite3':
                    self.print_check("Database Config", "PASS", "SQLite configured")
                    
                    # Test database connection
                    if test_database_connection():
                        self.print_check("Database Connection", "PASS")
                    else:
                        self.print_check("Database Connection", "FAIL", "Cannot connect to database")
                else:
                    self.print_check("Database Config", "WARN", f"Using {db_config['ENGINE']}")
            else:
                self.print_check("Database Config", "FAIL", "No default database configured")
                
        except Exception as e:
            self.print_check("Database Config", "FAIL", f"Error: {str(e)}")
            
    def check_email_config(self):
        """Check email configuration"""
        try:
            sys.path.insert(0, str(self.project_root / "emails"))
            from email_config import EMAIL_HOST, EMAIL_HOST_USER, test_email_connection
            
            if EMAIL_HOST == 'smtp.gmail.com':
                self.print_check("Email SMTP", "PASS", "Gmail SMTP configured")
            else:
                self.print_check("Email SMTP", "WARN", f"Using {EMAIL_HOST}")
                
            if EMAIL_HOST_USER:
                self.print_check("Email User", "PASS", f"User: {EMAIL_HOST_USER}")
            else:
                self.print_check("Email User", "FAIL", "No email user configured")
                
            # Test email connection (optional - requires valid credentials)
            try:
                if test_email_connection():
                    self.print_check("Email Connection", "PASS")
                else:
                    self.print_check("Email Connection", "WARN", "Cannot test connection (check credentials)")
            except:
                self.print_check("Email Connection", "WARN", "Cannot test connection (check credentials)")
                
        except Exception as e:
            self.print_check("Email Config", "FAIL", f"Error: {str(e)}")
            
    def check_stock_api(self):
        """Check stock API configuration"""
        try:
            # Check if yfinance can be imported
            import yfinance as yf
            self.print_check("yfinance Import", "PASS")
            
            # Try to fetch a simple stock quote
            try:
                ticker = yf.Ticker("AAPL")
                info = ticker.info
                if info:
                    self.print_check("Stock API Test", "PASS", "Successfully fetched AAPL data")
                else:
                    self.print_check("Stock API Test", "WARN", "Could not fetch stock data")
            except Exception as api_error:
                self.print_check("Stock API Test", "WARN", f"API test failed: {str(api_error)}")
                
        except ImportError:
            self.print_check("yfinance Import", "FAIL", "yfinance not installed")
            
    def check_virtual_environment(self):
        """Check if running in virtual environment"""
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            self.print_check("Virtual Environment", "PASS", "Running in virtual environment")
        else:
            self.print_check("Virtual Environment", "WARN", "Not running in virtual environment")
            
    def check_django_installation(self):
        """Check Django installation and version"""
        try:
            import django
            self.print_check("Django Import", "PASS", f"Django {django.get_version()}")
            
            # Check if Django apps can be imported
            try:
                os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
                django.setup()
                self.print_check("Django Setup", "PASS")
            except Exception as e:
                self.print_check("Django Setup", "WARN", f"Django setup issue: {str(e)}")
                
        except ImportError:
            self.print_check("Django Import", "FAIL", "Django not installed")
            
    def check_log_directories(self):
        """Check if log directories exist"""
        log_dir = self.project_root / "logs"
        if log_dir.exists():
            self.print_check("Log Directory", "PASS")
        else:
            try:
                log_dir.mkdir(exist_ok=True)
                self.print_check("Log Directory", "PASS", "Created log directory")
            except:
                self.print_check("Log Directory", "FAIL", "Cannot create log directory")
                
    def check_static_files(self):
        """Check static files configuration"""
        static_dir = self.project_root / "staticfiles"
        if static_dir.exists():
            self.print_check("Static Files", "PASS")
        else:
            self.print_check("Static Files", "WARN", "Static files not collected")
            
    def check_git_repository(self):
        """Check Git repository status"""
        git_dir = self.project_root / ".git"
        if git_dir.exists():
            try:
                # Check current branch
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    branch = result.stdout.strip()
                    self.print_check("Git Repository", "PASS", f"Branch: {branch}")
                else:
                    self.print_check("Git Repository", "WARN", "Git status unknown")
            except:
                self.print_check("Git Repository", "WARN", "Cannot check Git status")
        else:
            self.print_check("Git Repository", "WARN", "Not a Git repository")
            
    def generate_summary_report(self):
        """Generate and save summary report"""
        self.print_section("SYSTEM STATUS SUMMARY")
        
        total_checks = self.checks_passed + self.checks_failed + self.warnings
        
        print(f"📊 Total Checks: {total_checks}")
        print(f"✅ Passed: {self.checks_passed}")
        print(f"❌ Failed: {self.checks_failed}")
        print(f"⚠️  Warnings: {self.warnings}")
        
        if self.checks_failed == 0:
            if self.warnings == 0:
                print("\n🎉 ALL SYSTEMS OPERATIONAL!")
                status = "EXCELLENT"
            else:
                print("\n✅ SYSTEM READY (Minor warnings)")
                status = "GOOD"
        else:
            print("\n🔧 SYSTEM NEEDS ATTENTION")
            status = "NEEDS_ATTENTION"
            
        # Save report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "total_checks": total_checks,
            "passed": self.checks_passed,
            "failed": self.checks_failed,
            "warnings": self.warnings,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "project_root": str(self.project_root)
        }
        
        try:
            report_file = self.project_root / "system_status_report.json"
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"\n📄 Report saved to: {report_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save report: {e}")
            
        return status
        
    def run_all_checks(self):
        """Run all system checks"""
        self.print_header()
        
        self.print_section("Python Environment")
        self.check_python_version()
        self.check_virtual_environment()
        
        self.print_section("File Structure")
        self.check_essential_files()
        self.check_directory_structure()
        
        self.print_section("Django Framework")
        self.check_django_installation()
        
        self.print_section("Database Configuration")
        self.check_database_config()
        
        self.print_section("Email Configuration")
        self.check_email_config()
        
        self.print_section("Stock API")
        self.check_stock_api()
        
        self.print_section("System Configuration")
        self.check_log_directories()
        self.check_static_files()
        self.check_git_repository()
        
        return self.generate_summary_report()

def main():
    """Main function to run system status check"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Stock Scanner System Status Check")
        print("\nUsage:")
        print("  python3 system_status_check.py      # Run all checks")
        print("  python3 system_status_check.py --help  # Show this help")
        return
        
    checker = SystemStatusCheck()
    status = checker.run_all_checks()
    
    # Set exit code based on status
    if status == "NEEDS_ATTENTION":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()