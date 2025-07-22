#!/usr/bin/env python3
"""
Production Readiness Validation Script
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

def check_database_models():
    """Validate database models and required fields"""
    print("🗄️ Checking Database Models...")
    
    try:
        from stocks.models import StockAlert, Membership
        
        # Check StockAlert has required fields
        stock_fields = [field.name for field in StockAlert._meta.get_fields()]
        required_fields = ['price_change_today', 'price_change_percent']
        
        missing = [field for field in required_fields if field not in stock_fields]
        if missing:
            print(f"❌ Missing fields: {missing}")
            return False
        
        print("✅ All database models valid")
        return True
        
    except Exception as e:
        print(f"❌ Database model validation failed: {e}")
        return False

def check_api_endpoints():
    """Test critical API endpoints"""
    print("🌐 Checking API Endpoints...")
    
    try:
        from django.test import Client
        
        client = Client()
        
        # Test analytics endpoint
        response = client.get('/api/analytics/public/')
        if response.status_code != 200:
            print(f"❌ Analytics API failed: HTTP {response.status_code}")
            return False
        
        print("✅ API endpoints responding")
        return True
        
    except Exception as e:
        print(f"❌ API endpoint testing failed: {e}")
        return False

def run_validation():
    """Run validation checks"""
    print("🚀 Production Readiness Validation")
    print("=" * 40)
    
    checks = [check_database_models, check_api_endpoints]
    results = [check() for check in checks]
    
    passed = sum(results)
    total = len(results)
    
    print("=" * 40)
    print(f"📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 VALIDATION PASSED!")
        return True
    else:
        print("⚠️ Some validations failed.")
        return False

if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
