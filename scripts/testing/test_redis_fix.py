#!/usr/bin/env python
"""
Test script to verify Django can start without Redis
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')

# Ensure Redis/Celery is disabled for this test
os.environ['CELERY_ENABLED'] = 'false'
os.environ.pop('REDIS_URL', None)
os.environ.pop('CELERY_BROKER_URL', None)

print("🧪 Testing Django startup without Redis...")

try:
    # Setup Django
    django.setup()
    print("✅ Django setup successful")
    
    # Test basic imports
    from django.conf import settings
    print(f"✅ Settings loaded - DEBUG: {settings.DEBUG}")
    
    # Test cache configuration
    cache_backend = settings.CACHES['default']['BACKEND']
    print(f"✅ Cache backend: {cache_backend}")
    
    if 'locmem' in cache_backend.lower():
        print("✅ Using local memory cache (no Redis required)")
    elif 'redis' in cache_backend.lower():
        print("⚠️ Still configured for Redis cache")
    
    # Test basic Django operations
    from django.core.management import call_command
    from io import StringIO
    
    print("\n🔍 Testing Django system check...")
    out = StringIO()
    try:
        call_command('check', stdout=out)
        output = out.getvalue()
        if 'System check identified no issues' in output:
            print("✅ Django system check passed")
        else:
            print(f"⚠️ System check output: {output}")
    except Exception as e:
        error_msg = str(e)
        if "6379" in error_msg or "redis" in error_msg.lower():
            print(f"❌ Still trying to connect to Redis: {e}")
        else:
            print(f"⚠️ System check issue (non-Redis): {e}")
    
    # Test model imports
    print("\n📊 Testing model imports...")
    from stocks.models import StockAlert, Membership
    from emails.models import EmailSubscription
    print("✅ All models imported successfully")
    
    print("\n🎉 Test completed successfully!")
    print("💡 Django can run without Redis!")
    
except Exception as e:
    error_msg = str(e)
    if "6379" in error_msg or "redis" in error_msg.lower():
        print(f"❌ Redis connection still required: {e}")
        print("\n🔧 Redis is still being accessed somewhere...")
    else:
        print(f"❌ Other Django error: {e}")
    
    sys.exit(1)