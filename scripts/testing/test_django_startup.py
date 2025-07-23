#!/usr/bin/env python3
"""
Django Startup Test Script
Tests if Django application can start successfully with all components.

Usage:
    python scripts/testing/test_django_startup.py

This script tests:
- Python environment
- Django imports and settings
- Database connectivity
- Model imports
- Admin configuration
- URL routing
- Static file configuration

Author: Stock Scanner Project
Version: 1.0.0
"""

import os
import sys
import django
from pathlib import Path

def setup_django():
    """Setup Django environment"""
    # Add project root to Python path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
    
    try:
        django.setup()
        return True
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

def test_imports():
    """Test critical imports"""
    print("🔍 Testing Python imports...")
    
    tests = [
        ("Django", "django"),
        ("Django REST Framework", "rest_framework"),
        ("yfinance", "yfinance"),
        ("requests", "requests"),
    ]
    
    for name, module in tests:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError as e:
            print(f"❌ {name}: {e}")
            return False
    
    return True

def test_django_config():
    """Test Django configuration"""
    print("\n🌐 Testing Django configuration...")
    
    try:
        from django.conf import settings
        print(f"✅ Settings loaded: {settings.SETTINGS_MODULE}")
        
        # Test database configuration
        db_config = settings.DATABASES.get('default', {})
        if db_config:
            print(f"✅ Database configured: {db_config.get('ENGINE', 'Unknown')}")
        else:
            print("❌ No database configuration found")
            return False
        
        # Test static files
        if hasattr(settings, 'STATIC_URL'):
            print(f"✅ Static URL: {settings.STATIC_URL}")
        else:
            print("⚠️ No STATIC_URL configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Django configuration error: {e}")
        return False

def test_models():
    """Test model imports and basic functionality"""
    print("\n📊 Testing Django models...")
    
    try:
        from stocks.models import StockAlert, UserMembership
        print("✅ Stock models imported successfully")
        
        # Test model fields
        alert_fields = [f.name for f in StockAlert._meta.fields]
        required_fields = ['symbol', 'target_price', 'user']
        
        for field in required_fields:
            if field in alert_fields:
                print(f"✅ StockAlert.{field} field exists")
            else:
                print(f"❌ StockAlert.{field} field missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Model import error: {e}")
        return False

def test_admin():
    """Test Django admin configuration"""
    print("\n👨‍💼 Testing Django admin...")
    
    try:
        from django.contrib import admin
        from stocks.admin import StockAlertAdmin
        print("✅ Admin configuration loaded")
        
        # Check if models are registered
        from stocks.models import StockAlert
        if StockAlert in admin.site._registry:
            print("✅ StockAlert registered in admin")
        else:
            print("⚠️ StockAlert not registered in admin")
        
        return True
        
    except Exception as e:
        print(f"❌ Admin configuration error: {e}")
        return False

def test_urls():
    """Test URL configuration"""
    print("\n🔗 Testing URL configuration...")
    
    try:
        from django.urls import resolve
        from django.urls.exceptions import Resolver404
        
        # Test main URLs
        test_urls = [
            '/',
            '/admin/',
            '/api/stocks/',
        ]
        
        for url in test_urls:
            try:
                resolve(url)
                print(f"✅ URL resolves: {url}")
            except Resolver404:
                print(f"⚠️ URL not found: {url}")
        
        return True
        
    except Exception as e:
        print(f"❌ URL configuration error: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🗄️ Testing database connection...")
    
    try:
        from django.db import connection
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result and result[0] == 1:
                print("✅ Database connection successful")
                return True
            else:
                print("❌ Database query failed")
                return False
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        print("💡 Hint: Run 'python manage.py migrate' first")
        return False

def main():
    """Main test function"""
    print("🚀 Django Startup Test")
    print("=" * 50)
    
    # Track test results
    tests = []
    
    # Run tests
    tests.append(("Python Imports", test_imports()))
    
    if setup_django():
        print("✅ Django setup successful\n")
        tests.append(("Django Configuration", test_django_config()))
        tests.append(("Model Imports", test_models()))
        tests.append(("Admin Configuration", test_admin()))
        tests.append(("URL Configuration", test_urls()))
        tests.append(("Database Connection", test_database_connection()))
    else:
        print("❌ Django setup failed - cannot run further tests")
        return False
    
    # Show results
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📈 Success Rate: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Django is ready to run.")
        print("\n🚀 Next steps:")
        print("   python manage.py runserver")
        return True
    else:
        print(f"⚠️ {total-passed} tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)