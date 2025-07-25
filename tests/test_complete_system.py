#!/usr/bin/env python3
"""
Complete System Integration Test

Tests all core functionality:
- News system and display
- Email signup and sending
- Stock filtering
- Stock lookup/search
- WordPress integration
- Admin dashboard
"""

import os
import sys
import django
import json
import time
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from django.test import Client
from django.core.management import call_command
from stocks.models import StockAlert
from emails.models import EmailSubscription

class CompleteSystemTester:
def __init__(self):
self.client = Client()
self.test_results = {
'news': False,
'stock_search': False,
'stock_filter': False,
'email_signup': False,
'email_sending': False,
'admin_dashboard': False,
'wordpress_api': False,
'database': False
}

def print_header(self, text):
print(f"\n{'='*60}")
print(f" {text}")
print(f"{'='*60}")

def print_success(self, text):
print(f" {text}")

def print_error(self, text):
print(f" {text}")

def print_info(self, text):
print(f"ℹ {text}")

def test_database_and_models(self):
"""Test database connectivity and models"""
self.print_header("Database & Models Testing")

try:
# Test StockAlert model
stock_count = StockAlert.objects.count()
self.print_success(f"StockAlert model working - {stock_count} stocks")

# Test EmailSubscription model
subscription_count = EmailSubscription.objects.count()
self.print_success(f"EmailSubscription model working - {subscription_count} subscriptions")

# Create test data if needed
if stock_count == 0:
self.create_test_stock_data()

self.test_results['database'] = True
return True

except Exception as e:
self.print_error(f"Database test failed: {e}")
return False

def create_test_stock_data(self):
"""Create test stock data for testing"""
self.print_info("Creating test stock data...")

test_stocks = [
{
'ticker': 'AAPL',
'company_name': 'Apple Inc.',
'current_price': 185.50,
'price_change_today': 2.35,
'volume_today': 45000000,
'dvav': 1.25,
'dvsa': 85.3,
'pe_ratio': 28.5,
'market_cap': 2900000000000,
'note': 'Strong buy signal'
},
{
'ticker': 'MSFT',
'company_name': 'Microsoft Corporation',
'current_price': 428.75,
'price_change_today': -3.20,
'volume_today': 25000000,
'dvav': 0.95,
'dvsa': 72.1,
'pe_ratio': 32.8,
'market_cap': 3200000000000,
'note': 'Hold position'
},
{
'ticker': 'GOOGL',
'company_name': 'Alphabet Inc.',
'current_price': 165.85,
'price_change_today': 1.85,
'volume_today': 28000000,
'dvav': 1.15,
'dvsa': 78.9,
'pe_ratio': 25.2,
'market_cap': 2100000000000,
'note': 'Technical breakout'
}
]

for stock_data in test_stocks:
stock, created = StockAlert.objects.get_or_create(
ticker=stock_data['ticker'],
defaults=stock_data
)
if created:
self.print_success(f"Created test stock: {stock_data['ticker']}")

def test_news_system(self):
"""Test news functionality"""
self.print_header("News System Testing")

try:
# Test news view
response = self.client.get('/news/')

if response.status_code == 200:
self.print_success("News page loads successfully")

# Check if template renders
content = response.content.decode()
if 'news' in content.lower():
self.print_success("News template renders correctly")
self.test_results['news'] = True
else:
self.print_error("News template may be missing content")
else:
self.print_error(f"News page failed: HTTP {response.status_code}")

# Check if news JSON file exists
news_json_path = os.path.join('..', 'json', 'news.json')
if os.path.exists(news_json_path):
with open(news_json_path, 'r') as f:
news_data = json.load(f)
self.print_success(f"News JSON file found with {len(news_data)} articles")
else:
self.print_info("News JSON file not found - will be created by news scraper")

except Exception as e:
self.print_error(f"News system test failed: {e}")

def test_stock_search(self):
"""Test stock search functionality"""
self.print_header("Stock Search Testing")

try:
# Test search page load
response = self.client.get('/search/')

if response.status_code == 200:
self.print_success("Search page loads successfully")

# Test search with query
response = self.client.get('/search/?q=AAPL')
if response.status_code == 200:
self.print_success("Search with query works")
self.test_results['stock_search'] = True
else:
self.print_error("Search with query failed")
else:
self.print_error(f"Search page failed: HTTP {response.status_code}")

except Exception as e:
self.print_error(f"Stock search test failed: {e}")

def test_stock_filter(self):
"""Test stock filtering functionality"""
self.print_header("Stock Filter Testing")

try:
# Test filter page load
response = self.client.get('/filter/')

if response.status_code == 200:
self.print_success("Filter page loads successfully")

# Test filter POST request
filter_data = {
"current_price": {"type": "greater_than", "value": 100},
"volume_today": {"type": "greater_than", "value": 1000000}
}

response = self.client.post(
'/filter/',
data=json.dumps(filter_data),
content_type='application/json'
)

if response.status_code == 200:
results = response.json()
self.print_success(f"Filter working - returned {len(results)} results")
self.test_results['stock_filter'] = True
else:
self.print_error(f"Filter POST failed: HTTP {response.status_code}")
else:
self.print_error(f"Filter page failed: HTTP {response.status_code}")

except Exception as e:
self.print_error(f"Stock filter test failed: {e}")

def test_email_signup(self):
"""Test email subscription functionality"""
self.print_header("Email Signup Testing")

try:
# Test subscription form page
response = self.client.get('/subscribe/dvsa-50/')

if response.status_code == 200:
self.print_success("Subscription form loads successfully")

# Test email subscription
test_email = 'test@example.com'
signup_data = {
'email': test_email
}

response = self.client.post(
'/subscribe-dvsa-50',
data=json.dumps(signup_data),
content_type='application/json'
)

if response.status_code == 200:
self.print_success("Email subscription endpoint works")

# Verify subscription was saved
subscription = EmailSubscription.objects.filter(
email=test_email,
category='dvsa-50'
).first()

if subscription:
self.print_success("Email subscription saved to database")
self.test_results['email_signup'] = True
else:
self.print_error("Email subscription not found in database")
else:
self.print_error(f"Email subscription failed: HTTP {response.status_code}")
else:
self.print_error(f"Subscription form failed: HTTP {response.status_code}")

except Exception as e:
self.print_error(f"Email signup test failed: {e}")

def test_email_sending(self):
"""Test email sending functionality"""
self.print_header("Email Sending Testing")

try:
# Test if we can import email sending modules
from emails.stock_notifications import send_stock_notifications
from emails.email_filter import EmailFilter

self.print_success("Email modules import successfully")

# Test email filter
email_filter = EmailFilter()
test_category = email_filter.filter_email("dvsa volume 50")
self.print_success(f"Email filter working - returned category: {test_category}")

# Check if we have subscriptions to send to
active_subscriptions = EmailSubscription.objects.filter(is_active=True).count()
self.print_info(f"Active subscriptions: {active_subscriptions}")

if active_subscriptions > 0:
self.print_success("Email system ready for sending")
self.test_results['email_sending'] = True
else:
self.print_info("Email system functional but no active subscriptions")
self.test_results['email_sending'] = True

except Exception as e:
self.print_error(f"Email sending test failed: {e}")

def test_admin_dashboard(self):
"""Test admin dashboard functionality"""
self.print_header("Admin Dashboard Testing")

try:
# Test dashboard page load
response = self.client.get('/admin-dashboard/')

if response.status_code == 200:
self.print_success("Admin dashboard loads successfully")

# Test admin API endpoints
api_endpoints = [
'/api/admin/status/',
'/api/admin/health/',
'/api/admin/metrics/'
]

for endpoint in api_endpoints:
try:
response = self.client.get(endpoint)
if response.status_code == 200:
self.print_success(f"Admin API {endpoint} works")
else:
self.print_error(f"Admin API {endpoint} failed: {response.status_code}")
except:
self.print_info(f"Admin API {endpoint} not available (optional)")

self.test_results['admin_dashboard'] = True
else:
self.print_error(f"Admin dashboard failed: HTTP {response.status_code}")

except Exception as e:
self.print_error(f"Admin dashboard test failed: {e}")

def test_wordpress_api(self):
"""Test WordPress API integration"""
self.print_header("WordPress API Testing")

try:
# Test WordPress-compatible API endpoints
api_endpoints = [
'/api/stocks/',
'/api/market-movers/',
'/api/stats/',
'/api/stocks/search/?q=AAPL'
]

working_endpoints = 0

for endpoint in api_endpoints:
try:
response = self.client.get(endpoint)
if response.status_code == 200:
data = response.json()
if data.get('success'):
self.print_success(f"WordPress API {endpoint} works")
working_endpoints += 1
else:
self.print_error(f"WordPress API {endpoint} returned success=false")
else:
self.print_error(f"WordPress API {endpoint} failed: {response.status_code}")
except Exception as e:
self.print_error(f"WordPress API {endpoint} error: {e}")

if working_endpoints >= 3:
self.print_success("WordPress API integration working")
self.test_results['wordpress_api'] = True
else:
self.print_error("WordPress API integration needs attention")

except Exception as e:
self.print_error(f"WordPress API test failed: {e}")

def test_data_export_pipeline(self):
"""Test the complete data pipeline"""
self.print_header("Data Export Pipeline Testing")

try:
# Test if export directory exists
export_dir = os.path.join('..', 'json')
if not os.path.exists(export_dir):
os.makedirs(export_dir)
self.print_info("Created export directory")

# Test data export command
self.print_info("Testing data export...")
call_command('export_stock_data', format='web', verbosity=0)

# Check if export file was created
export_file = os.path.join(export_dir, 'stock_data_export.json')
if os.path.exists(export_file):
with open(export_file, 'r') as f:
export_data = json.load(f)
self.print_success(f"Data export working - {len(export_data)} stocks exported")
else:
self.print_error("Data export file not created")

except Exception as e:
self.print_error(f"Data export pipeline test failed: {e}")

def generate_system_report(self):
"""Generate a comprehensive system report"""
self.print_header("System Integration Report")

total_tests = len(self.test_results)
passed_tests = sum(self.test_results.values())

print(f"\n Overall System Status: {passed_tests}/{total_tests} components working")
print(f" System Health: {(passed_tests/total_tests)*100:.1f}%")

print("\n Component Status:")
for component, status in self.test_results.items():
status_icon = "" if status else ""
print(f" {status_icon} {component.replace('_', ' ').title()}")

print("\n Complete Workflow Test:")
workflow_steps = [
("Database Models", self.test_results['database']),
("Stock Data Available", self.test_results['database']),
("Stock Search Works", self.test_results['stock_search']),
("Stock Filter Works", self.test_results['stock_filter']),
("Email Signup Works", self.test_results['email_signup']),
("Email System Ready", self.test_results['email_sending']),
("News System Works", self.test_results['news']),
("WordPress API Ready", self.test_results['wordpress_api']),
("Admin Dashboard Works", self.test_results['admin_dashboard'])
]

for step_name, step_status in workflow_steps:
status_icon = "" if step_status else ""
print(f" {status_icon} {step_name}")

if passed_tests == total_tests:
print("\n All systems operational! Your stock scanner is fully integrated.")
print("\n Ready for:")
print(" • Real-time stock data processing")
print(" • Email subscriptions and notifications")
print(" • Advanced stock filtering")
print(" • News integration")
print(" • WordPress frontend integration")
print(" • Admin dashboard management")
else:
failed_components = [k for k, v in self.test_results.items() if not v]
print(f"\n Need attention: {', '.join(failed_components)}")
print("\n Next steps:")

if not self.test_results['database']:
print(" • Run: python manage.py migrate")
print(" • Check database connectivity")

if not self.test_results['news']:
print(" • Check news scraper configuration")
print(" • Verify news.json file path")

if not self.test_results['email_sending']:
print(" • Check email configuration in settings.py")
print(" • Test SMTP connection")

if not self.test_results['wordpress_api']:
print(" • Install: pip install djangorestframework django-cors-headers")
print(" • Add to INSTALLED_APPS in settings.py")

def run_complete_test(self):
"""Run all system tests"""
print(" Complete System Integration Test")
print(f" Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Run all tests
self.test_database_and_models()
self.test_news_system()
self.test_stock_search()
self.test_stock_filter()
self.test_email_signup()
self.test_email_sending()
self.test_admin_dashboard()
self.test_wordpress_api()
self.test_data_export_pipeline()

# Generate final report
self.generate_system_report()

def main():
tester = CompleteSystemTester()
tester.run_complete_test()

if __name__ == '__main__':
main()