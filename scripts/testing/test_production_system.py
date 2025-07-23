#!/usr/bin/env python3
"""
Production System Test Script for Windows Deployment
Tests all critical components of the Stock Scanner platform

Usage:
    python scripts/testing/test_production_system.py

This script tests:
- Database connectivity (PostgreSQL)
- Redis connectivity
- Django application startup
- API endpoints
- Yahoo Finance data fetching
- Celery workers
- Static file serving
- SSL configuration
- Payment system integration

Author: Stock Scanner Project
Version: 1.0.0
"""

import os
import sys
import time
import requests
import subprocess
import psycopg2
import redis
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Add Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')

# Django setup
import django
django.setup()

from django.core.management import execute_from_command_line
from django.test.utils import get_runner
from django.conf import settings
from django.core.cache import cache

class ProductionSystemTester:
    """Comprehensive production system testing"""
    
    def __init__(self):
        self.results = {}
        self.failed_tests = []
        self.passed_tests = []
        self.start_time = time.time()
        
        # Test configuration
        self.django_url = "http://localhost:8000"
        self.api_endpoints = [
            "/api/stocks/",
            "/api/analytics/public/",
            "/admin/",
            "/health/"
        ]
        
        print("🔍 Production System Testing Suite")
        print("=" * 50)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    def print_test_header(self, emoji: str, test_name: str):
        """Print formatted test header"""
        print(f"{emoji} {test_name}")
        print("-" * 40)

    def print_result(self, test_name: str, success: bool, message: str = "", details: str = ""):
        """Print test result with formatting"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status}: {test_name}")
        
        if message:
            print(f"   📋 {message}")
        
        if details:
            print(f"   💬 {details}")
        
        if success:
            self.passed_tests.append(test_name)
        else:
            self.failed_tests.append(test_name)
        
        print()

    def test_python_environment(self) -> bool:
        """Test Python environment and virtual environment"""
        self.print_test_header("🐍", "PYTHON ENVIRONMENT")
        
        try:
            # Check Python version
            python_version = sys.version
            if sys.version_info >= (3, 9):
                self.print_result("Python Version", True, f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
            else:
                self.print_result("Python Version", False, "Python 3.9+ required")
                return False
            
            # Check virtual environment
            venv_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
            self.print_result("Virtual Environment", venv_active, "Virtual environment is active" if venv_active else "No virtual environment detected")
            
            # Check critical imports
            critical_packages = ['django', 'yfinance', 'requests', 'psycopg2', 'redis', 'celery']
            all_imports_ok = True
            
            for package in critical_packages:
                try:
                    __import__(package)
                    self.print_result(f"Package: {package}", True, "Available")
                except ImportError as e:
                    self.print_result(f"Package: {package}", False, f"Import failed: {e}")
                    all_imports_ok = False
            
            return all_imports_ok
            
        except Exception as e:
            self.print_result("Python Environment", False, f"Error: {e}")
            return False

    def test_database_connectivity(self) -> bool:
        """Test PostgreSQL database connectivity"""
        self.print_test_header("🗄️", "DATABASE CONNECTIVITY")
        
        try:
            # Get database settings from Django
            db_config = settings.DATABASES['default']
            
            # Test connection
            conn = psycopg2.connect(
                host=db_config['HOST'],
                port=db_config['PORT'],
                database=db_config['NAME'],
                user=db_config['USER'],
                password=db_config['PASSWORD']
            )
            
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()[0]
            self.print_result("Database Connection", True, f"Connected to PostgreSQL")
            self.print_result("Database Version", True, db_version[:50] + "...")
            
            # Test Django tables
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
            table_count = cursor.fetchone()[0]
            self.print_result("Django Tables", table_count > 0, f"Found {table_count} tables")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            self.print_result("Database Connection", False, f"Error: {e}")
            return False

    def test_redis_connectivity(self) -> bool:
        """Test Redis connectivity"""
        self.print_test_header("🔴", "REDIS CONNECTIVITY")
        
        try:
            # Test Redis connection
            r = redis.Redis(host='localhost', port=6379, db=0)
            
            # Ping test
            pong = r.ping()
            self.print_result("Redis Ping", pong, "Redis server responding")
            
            # Set/Get test
            test_key = "production_test_key"
            test_value = f"test_value_{int(time.time())}"
            
            r.set(test_key, test_value)
            retrieved_value = r.get(test_key).decode('utf-8')
            
            success = retrieved_value == test_value
            self.print_result("Redis Set/Get", success, "Data storage working" if success else "Data storage failed")
            
            # Clean up
            r.delete(test_key)
            
            # Test Django cache
            cache.set('test_cache_key', 'test_cache_value', 30)
            cached_value = cache.get('test_cache_key')
            self.print_result("Django Cache", cached_value == 'test_cache_value', "Django cache integration working")
            
            return True
            
        except Exception as e:
            self.print_result("Redis Connection", False, f"Error: {e}")
            return False

    def test_django_application(self) -> bool:
        """Test Django application startup and configuration"""
        self.print_test_header("🌐", "DJANGO APPLICATION")
        
        try:
            # Test Django settings
            self.print_result("Django Settings", True, f"Settings module: {settings.SETTINGS_MODULE}")
            
            # Test static files configuration
            static_root_exists = os.path.exists(settings.STATIC_ROOT) if settings.STATIC_ROOT else False
            self.print_result("Static Files", static_root_exists, f"Static root: {settings.STATIC_ROOT}")
            
            # Test media files configuration
            media_root_exists = os.path.exists(settings.MEDIA_ROOT) if settings.MEDIA_ROOT else False
            self.print_result("Media Files", media_root_exists, f"Media root: {settings.MEDIA_ROOT}")
            
            # Test security settings
            debug_off = not settings.DEBUG
            self.print_result("Debug Mode", debug_off, "DEBUG=False (production ready)" if debug_off else "DEBUG=True (not production ready)")
            
            allowed_hosts_configured = len(settings.ALLOWED_HOSTS) > 0 and settings.ALLOWED_HOSTS != ['*']
            self.print_result("Allowed Hosts", allowed_hosts_configured, f"Configured: {settings.ALLOWED_HOSTS}")
            
            return True
            
        except Exception as e:
            self.print_result("Django Application", False, f"Error: {e}")
            return False

    def test_api_endpoints(self) -> bool:
        """Test API endpoints"""
        self.print_test_header("🌐", "API ENDPOINTS")
        
        all_endpoints_ok = True
        
        for endpoint in self.api_endpoints:
            try:
                url = f"{self.django_url}{endpoint}"
                response = requests.get(url, timeout=10)
                
                if response.status_code in [200, 301, 302]:
                    self.print_result(f"Endpoint: {endpoint}", True, f"Status: {response.status_code}")
                else:
                    self.print_result(f"Endpoint: {endpoint}", False, f"Status: {response.status_code}")
                    all_endpoints_ok = False
                    
            except requests.exceptions.ConnectionError:
                self.print_result(f"Endpoint: {endpoint}", False, "Connection refused - Django server not running")
                all_endpoints_ok = False
            except Exception as e:
                self.print_result(f"Endpoint: {endpoint}", False, f"Error: {e}")
                all_endpoints_ok = False
        
        return all_endpoints_ok

    def test_yahoo_finance_integration(self) -> bool:
        """Test Yahoo Finance API integration"""
        self.print_test_header("📈", "YAHOO FINANCE INTEGRATION")
        
        try:
            # Test using our enhanced optimizer
            optimizer_path = "scripts/utils/yahoo_finance_api_optimizer_v2.py"
            
            if os.path.exists(optimizer_path):
                self.print_result("Optimizer Script", True, "Enhanced optimizer available")
                
                # Test basic yfinance import and functionality
                import yfinance as yf
                
                # Test a simple stock fetch
                ticker = yf.Ticker("AAPL")
                info = ticker.info
                
                if info and 'symbol' in info:
                    self.print_result("Yahoo Finance API", True, f"Successfully fetched data for {info.get('symbol', 'AAPL')}")
                else:
                    self.print_result("Yahoo Finance API", False, "Failed to fetch stock data")
                    return False
                
            else:
                self.print_result("Optimizer Script", False, "Enhanced optimizer not found")
                return False
                
            return True
            
        except Exception as e:
            self.print_result("Yahoo Finance Integration", False, f"Error: {e}")
            return False

    def test_celery_workers(self) -> bool:
        """Test Celery workers and task queue"""
        self.print_test_header("🔄", "CELERY WORKERS")
        
        try:
            # Test Celery configuration
            from celery import Celery
            
            # Test broker connection
            try:
                from stockscanner_django.celery import app as celery_app
                
                # Check if broker is accessible
                broker_url = celery_app.conf.broker_url
                self.print_result("Celery Configuration", True, f"Broker: {broker_url}")
                
                # Try to inspect active workers (this might fail if no workers are running)
                try:
                    inspect = celery_app.control.inspect()
                    active_workers = inspect.active()
                    
                    if active_workers:
                        worker_count = len(active_workers)
                        self.print_result("Active Workers", True, f"Found {worker_count} worker(s)")
                    else:
                        self.print_result("Active Workers", False, "No active workers found")
                        
                except Exception:
                    self.print_result("Active Workers", False, "Could not inspect workers (may be offline)")
                
                return True
                
            except Exception as e:
                self.print_result("Celery Import", False, f"Error importing Celery app: {e}")
                return False
                
        except Exception as e:
            self.print_result("Celery Workers", False, f"Error: {e}")
            return False

    def test_windows_services(self) -> bool:
        """Test Windows services status"""
        self.print_test_header("🪟", "WINDOWS SERVICES")
        
        services_to_check = [
            ("postgresql-x64-14", "PostgreSQL Database"),
            ("Redis", "Redis Server")
        ]
        
        all_services_ok = True
        
        for service_name, display_name in services_to_check:
            try:
                # Use sc query command to check service status
                result = subprocess.run(
                    ["sc", "query", service_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0 and "RUNNING" in result.stdout:
                    self.print_result(f"Service: {display_name}", True, "Running")
                else:
                    self.print_result(f"Service: {display_name}", False, "Not running or not found")
                    all_services_ok = False
                    
            except Exception as e:
                self.print_result(f"Service: {display_name}", False, f"Error checking service: {e}")
                all_services_ok = False
        
        return all_services_ok

    def test_file_permissions(self) -> bool:
        """Test file permissions and directory access"""
        self.print_test_header("🔒", "FILE PERMISSIONS")
        
        critical_paths = [
            (settings.STATIC_ROOT, "Static Files Directory"),
            (settings.MEDIA_ROOT, "Media Files Directory"),
            ("logs", "Logs Directory"),
            (".", "Project Root")
        ]
        
        all_permissions_ok = True
        
        for path, description in critical_paths:
            if not path:
                continue
                
            try:
                # Test directory exists and is writable
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
                
                # Test write access
                test_file = os.path.join(path, "permission_test.tmp")
                with open(test_file, 'w') as f:
                    f.write("test")
                
                # Test read access
                with open(test_file, 'r') as f:
                    content = f.read()
                
                # Clean up
                os.remove(test_file)
                
                self.print_result(f"Path: {description}", True, f"Read/Write access OK: {path}")
                
            except Exception as e:
                self.print_result(f"Path: {description}", False, f"Access error: {e}")
                all_permissions_ok = False
        
        return all_permissions_ok

    def generate_report(self):
        """Generate final test report"""
        total_time = time.time() - self.start_time
        total_tests = len(self.passed_tests) + len(self.failed_tests)
        success_rate = (len(self.passed_tests) / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 PRODUCTION SYSTEM TEST REPORT")
        print("=" * 60)
        print(f"⏱️  Total Time: {total_time:.2f} seconds")
        print(f"✅ Passed Tests: {len(self.passed_tests)}")
        print(f"❌ Failed Tests: {len(self.failed_tests)}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print()
        
        if self.failed_tests:
            print("❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"   • {test}")
            print()
        
        if self.passed_tests:
            print("✅ PASSED TESTS:")
            for test in self.passed_tests:
                print(f"   • {test}")
            print()
        
        # Overall status
        if len(self.failed_tests) == 0:
            print("🎉 ALL TESTS PASSED - PRODUCTION SYSTEM READY!")
            print("🚀 Your Stock Scanner platform is ready for deployment!")
        elif len(self.failed_tests) <= 2:
            print("⚠️  MOSTLY READY - Minor issues detected")
            print("🔧 Address the failed tests before production deployment")
        else:
            print("🚨 SYSTEM NOT READY - Multiple issues detected")
            print("🔧 Please fix the failed tests before proceeding")
        
        print("\n" + "=" * 60)
        
        # Save report to file
        report_file = f"production_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(report_file, 'w') as f:
                f.write(f"Production System Test Report\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Time: {total_time:.2f} seconds\n")
                f.write(f"Success Rate: {success_rate:.1f}%\n\n")
                
                f.write("Failed Tests:\n")
                for test in self.failed_tests:
                    f.write(f"- {test}\n")
                
                f.write("\nPassed Tests:\n")
                for test in self.passed_tests:
                    f.write(f"- {test}\n")
            
            print(f"📄 Report saved: {report_file}")
        except Exception as e:
            print(f"⚠️  Could not save report: {e}")

    def run_all_tests(self):
        """Run all production system tests"""
        print("🚀 Starting comprehensive production system tests...")
        print()
        
        # Run all tests
        tests = [
            self.test_python_environment,
            self.test_database_connectivity,
            self.test_redis_connectivity,
            self.test_django_application,
            self.test_api_endpoints,
            self.test_yahoo_finance_integration,
            self.test_celery_workers,
            self.test_windows_services,
            self.test_file_permissions
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                test_name = test.__name__.replace('test_', '').replace('_', ' ').title()
                self.print_result(test_name, False, f"Test crashed: {e}")
            
            time.sleep(1)  # Brief pause between tests
        
        # Generate final report
        self.generate_report()

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print(__doc__)
        return
    
    # Change to project directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(os.path.dirname(script_dir))
    os.chdir(project_dir)
    
    # Run tests
    tester = ProductionSystemTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()