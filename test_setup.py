#!/usr/bin/env python3
"""
Stock Scanner Platform - Setup Verification Script
Tests all critical components to ensure proper installation
"""

import os
import sys
import django
import subprocess
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

def test_django_setup():
    """Test Django configuration"""
    print("🔧 Testing Django setup...")
    
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'check'])
        print("✅ Django configuration is valid")
        return True
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

def test_database_connection():
    """Test database connectivity"""
    print("🗄️ Testing database connection...")
    
    try:
        from django.db import connection
        connection.ensure_connection()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_models():
    """Test model imports and basic functionality"""
    print("📊 Testing models...")
    
    try:
        from stocks.models import Membership, StockAlert
        from emails.models import EmailSubscription
        from django.contrib.auth.models import User
        
        # Count existing records
        user_count = User.objects.count()
        membership_count = Membership.objects.count()
        stock_count = StockAlert.objects.count()
        email_count = EmailSubscription.objects.count()
        
        # Test StockAlert model has required fields
        stock_fields = [field.name for field in StockAlert._meta.get_fields()]
        required_fields = ['price_change_today', 'price_change_percent']
        missing_fields = [field for field in required_fields if field not in stock_fields]
        
        if missing_fields:
            print(f"❌ StockAlert model missing fields: {missing_fields}")
            print("   Run: python manage.py migrate")
            return False
        
        print(f"✅ Models loaded successfully")
        print(f"   Users: {user_count}")
        print(f"   Memberships: {membership_count}")
        print(f"   Stock Alerts: {stock_count}")
        print(f"   Email Subscriptions: {email_count}")
        print("✅ All required model fields present")
        return True
    except Exception as e:
        print(f"❌ Model testing failed: {e}")
        return False

def test_api_views():
    """Test API view imports"""
    print("🌐 Testing API views...")
    
    try:
        from stocks import api_views, analytics_views
        from core import views
        
        # Check if key functions exist
        assert hasattr(api_views, 'stock_list_api')
        assert hasattr(analytics_views, 'public_stats_api')
        assert hasattr(views, 'home')
        
        print("✅ API views loaded successfully")
        return True
    except Exception as e:
        print(f"❌ API view testing failed: {e}")
        return False

def test_url_patterns():
    """Test URL configuration"""
    print("🔗 Testing URL patterns...")
    
    try:
        from django.urls import reverse
        from django.test import Client
        
        # Test that key URLs can be resolved
        admin_url = reverse('admin:index')
        
        print("✅ URL patterns configured correctly")
        return True
    except Exception as e:
        print(f"❌ URL pattern testing failed: {e}")
        return False

def test_requirements():
    """Test that key packages are installed"""
    print("📦 Testing package requirements...")
    
    required_packages = [
        'django',
        'djangorestframework',
        'corsheaders',
        'yfinance',
        'pandas',
        'requests',
        'celery'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        return False
    else:
        print("✅ All required packages installed")
        return True

def test_file_structure():
    """Test that key files exist"""
    print("📁 Testing file structure...")
    
    required_files = [
        'manage.py',
        'requirements.txt',
        'startup.sh',
        '.env.example',
        'stockscanner_django/settings.py',
        'stocks/models.py',
        'stocks/api_views.py',
        'emails/models.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_membership_system():
    """Test membership system functionality"""
    print("💰 Testing membership system...")
    
    try:
        from stocks.models import Membership
        
        # Test membership tier choices
        tier_choices = dict(Membership.TIER_CHOICES)
        expected_tiers = {'free', 'basic', 'professional', 'expert'}
        actual_tiers = set(tier_choices.keys())
        
        if expected_tiers != actual_tiers:
            print(f"❌ Membership tiers mismatch. Expected: {expected_tiers}, Got: {actual_tiers}")
            return False
        
        # Test membership methods exist
        assert hasattr(Membership, 'tier_limits')
        assert hasattr(Membership, 'pricing_info')
        assert hasattr(Membership, 'can_make_lookup')
        
        print("✅ Membership system configured correctly")
        return True
    except Exception as e:
        print(f"❌ Membership system testing failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("🚀 Stock Scanner Platform - Setup Verification")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_requirements,
        test_django_setup,
        test_database_connection,
        test_models,
        test_api_views,
        test_url_patterns,
        test_membership_system
    ]
    
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Stock Scanner platform is ready!")
        print()
        print("Next steps:")
        print("1. Start the server: python manage.py runserver")
        print("2. Visit Django Admin: http://localhost:8000/admin")
        print("3. Test Analytics API: http://localhost:8000/api/analytics/public/")
        return True
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
        print("Check the setup documentation for troubleshooting.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
