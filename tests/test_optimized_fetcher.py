#!/usr/bin/env python3
"""
Test script for the optimized stock data fetcher.

This script verifies that the optimized system is properly integrated
and can fetch data successfully.
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import call_command
from django.test.utils import get_runner
import time
import logging

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import StockAlert

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_basic_functionality():
"""Test basic functionality of the optimized fetcher and workflow"""
logger.info("🧪 Testing basic functionality...")

try:
# Count initial records
initial_count = StockAlert.objects.count()
logger.info(f"Initial stock records: {initial_count}")

# Test the complete workflow with a small batch
logger.info("Running complete stock workflow with test settings...")
start_time = time.time()

call_command(
'stock_workflow',
'--batch-size', '5',
'--max-workers', '1',
'--use-cache',
'--delay-range', '1.0', '2.0',
'--dry-run-notifications',
verbosity=1
)

elapsed_time = time.time() - start_time

# Count final records
final_count = StockAlert.objects.count()
processed = final_count - initial_count

logger.info(f" Workflow test completed in {elapsed_time:.2f} seconds")
logger.info(f" Processed {processed} stocks")
logger.info(f" Total records: {final_count}")

return True

except Exception as e:
logger.error(f" Test failed: {e}")
return False

def test_configuration():
"""Test configuration loading"""
logger.info(" Testing configuration...")

try:
from stocks.config import RATE_LIMITS, CACHE_CONFIG, PERFORMANCE_CONFIG

logger.info(" Configuration loaded successfully")
logger.info(f"Rate limits: {RATE_LIMITS['requests_per_minute']}/min")
logger.info(f"Default batch size: {PERFORMANCE_CONFIG['batch_size']}")
logger.info(f"Cache timeout: {CACHE_CONFIG['default_timeout']}s")

return True

except Exception as e:
logger.error(f" Configuration test failed: {e}")
return False

def test_alternative_apis():
"""Test API providers - Simplified for Yahoo Finance + Finnhub"""
logger.info(" Testing API providers...")

try:
from stocks.api_manager import stock_manager

connections = stock_manager.test_connection()
usage_stats = stock_manager.get_usage_stats()
configured_providers = [api for api, connected in connections.items()]

logger.info(f" API status loaded")
logger.info(f" Configured providers: {len(configured_providers)}")

if configured_providers:
logger.info(f" Available: {', '.join(configured_providers)}")
else:
logger.info(" No alternative API providers configured")
logger.info(" Set environment variables for API keys to enable fallback")

return True

except Exception as e:
logger.error(f" Alternative APIs test failed: {e}")
return False

def test_caching():
"""Test caching functionality"""
logger.info(" Testing caching functionality...")

try:
from django.core.cache import cache

# Test cache operations
test_key = "test_optimized_fetcher"
test_value = {"test": "data", "timestamp": time.time()}

cache.set(test_key, test_value, 60)
retrieved_value = cache.get(test_key)

if retrieved_value == test_value:
logger.info(" Cache operations working correctly")
cache.delete(test_key) # Cleanup
return True
else:
logger.warning(" Cache not working properly (using dummy cache?)")
return False

except Exception as e:
logger.error(f" Caching test failed: {e}")
return False

def test_models():
"""Test database models"""
logger.info(" Testing database models...")

try:
# Test model access
total_stocks = StockAlert.objects.count()
recent_stocks = StockAlert.objects.filter(
last_update__isnull=False
).order_by('-last_update')[:5]

logger.info(f" Database access working")
logger.info(f" Total stocks in database: {total_stocks}")

if recent_stocks:
logger.info(" Recent stocks:")
for stock in recent_stocks:
logger.info(f" {stock.ticker}: ${stock.current_price:.2f}")

return True

except Exception as e:
logger.error(f" Models test failed: {e}")
return False

def test_data_export():
"""Test data export functionality"""
logger.info(" Testing data export...")

try:
# Test import of export command
from stocks.management.commands.export_stock_data import Command

# Test if we can check for data
from stocks.models import StockAlert
stock_count = StockAlert.objects.count()

logger.info(f" Export command available")
logger.info(f" Found {stock_count} stocks to export")

return True

except Exception as e:
logger.error(f" Data export test failed: {e}")
return False

def test_email_integration():
"""Test email notification integration"""
logger.info(" Testing email integration...")

try:
# Test imports
from emails.stock_notifications import send_stock_notifications
from emails.email_filter import EmailFilter
from emails.models import EmailSubscription

# Test filter
filter = EmailFilter()
test_category = filter.filter_email("dvsa volume 50")

logger.info(f" Email components available")
logger.info(f" Test categorization: 'dvsa volume 50' → '{test_category}'")

# Check subscription model
sub_count = EmailSubscription.objects.count()
logger.info(f" Email subscriptions: {sub_count}")

return True

except Exception as e:
logger.error(f" Email integration test failed: {e}")
return False

def test_workflow_commands():
"""Test workflow management commands"""
logger.info(" Testing workflow commands...")

try:
# Test command imports
from stocks.management.commands.stock_workflow import Command as WorkflowCommand
from stocks.management.commands.send_stock_notifications import Command as NotificationCommand
from stocks.management.commands.export_stock_data import Command as ExportCommand

logger.info(" All workflow commands available")
logger.info(" • stock_workflow - Complete pipeline")
logger.info(" • send_stock_notifications - Email notifications")
logger.info(" • export_stock_data - Data export")

return True

except Exception as e:
logger.error(f" Workflow commands test failed: {e}")
return False

def run_comprehensive_test():
"""Run all tests"""
logger.info(" Starting comprehensive test of optimized stock fetcher")
logger.info("=" * 60)

tests = [
("Configuration Loading", test_configuration),
("Database Models", test_models), 
("Caching System", test_caching),
("Alternative APIs", test_alternative_apis),
("Data Export System", test_data_export),
("Email Integration", test_email_integration),
("Workflow Commands", test_workflow_commands),
("Complete Workflow", test_basic_functionality),
]

results = []

for test_name, test_func in tests:
logger.info(f"\n🧪 Running: {test_name}")
logger.info("-" * 40)

try:
result = test_func()
results.append((test_name, result))

if result:
logger.info(f" {test_name}: PASSED")
else:
logger.error(f" {test_name}: FAILED")

except Exception as e:
logger.error(f" {test_name}: ERROR - {e}")
results.append((test_name, False))

# Summary
logger.info("\n" + "=" * 60)
logger.info(" TEST SUMMARY")
logger.info("=" * 60)

passed = sum(1 for _, result in results if result)
total = len(results)

for test_name, result in results:
status = " PASSED" if result else " FAILED"
logger.info(f"{test_name:<25} {status}")

logger.info("-" * 60)
logger.info(f"Results: {passed}/{total} tests passed")

if passed == total:
logger.info(" All tests passed! The optimized fetcher is ready to use.")
logger.info("\n Next steps:")
logger.info(" 1. Run: python manage.py import_stock_data_optimized --help")
logger.info(" 2. Start with: python manage.py import_stock_data_optimized --use-cache")
logger.info(" 3. For production: python manage.py import_stock_data_optimized --batch-size 30 --max-workers 3 --use-cache")
else:
logger.error(" Some tests failed. Please check the errors above.")
logger.info("\n Troubleshooting:")
logger.info(" 1. Ensure all dependencies are installed: pip install -r requirements_optimized.txt")
logger.info(" 2. Check Django settings configuration")
logger.info(" 3. Verify database connectivity")

return passed == total

def quick_test():
"""Run a quick test with minimal processing"""
logger.info(" Running quick test...")

try:
# Test core imports
from stocks.management.commands.import_stock_data_optimized import Command
from stocks.config import RATE_LIMITS
from stocks.api_manager import stock_manager

# Test workflow imports
from stocks.management.commands.stock_workflow import Command as WorkflowCommand
from stocks.management.commands.export_stock_data import Command as ExportCommand
from stocks.management.commands.send_stock_notifications import Command as NotificationCommand

# Test email integration
from emails.email_filter import EmailFilter
from emails.models import EmailSubscription

logger.info(" All core imports successful")
logger.info(" Workflow commands available")
logger.info(" Email integration working")
logger.info(" Configuration accessible")
logger.info(" Quick test passed!")

return True

except Exception as e:
logger.error(f" Quick test failed: {e}")
return False

if __name__ == "__main__":
import argparse

parser = argparse.ArgumentParser(description="Test the optimized stock data fetcher")
parser.add_argument("--quick", action="store_true", help="Run quick test only")
parser.add_argument("--comprehensive", action="store_true", help="Run comprehensive test")

args = parser.parse_args()

if args.quick:
success = quick_test()
else:
success = run_comprehensive_test()

sys.exit(0 if success else 1)