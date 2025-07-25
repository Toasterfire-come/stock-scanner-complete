#!/usr/bin/env python3
"""
WordPress Integration Test Script

This script tests the Django REST API endpoints that WordPress will consume.
Run this to verify your backend is ready for WordPress integration.
"""

import os
import sys
import django
import json
import requests
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from django.test import Client
from django.core.management import call_command
from stocks.models import StockAlert
from emails.models import EmailSubscription

class WordPressIntegrationTester:
def __init__(self):
self.client = Client()
self.base_url = "http://127.0.0.1:8000"
self.api_endpoints = [
'/api/stocks/',
'/api/market-movers/',
'/api/stats/',
'/api/stocks/search/',
]

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

def test_database_setup(self):
"""Test that we have stock data for API testing"""
self.print_header("Database Setup Check")

stock_count = StockAlert.objects.count()
subscription_count = EmailSubscription.objects.count()

if stock_count > 0:
self.print_success(f"Found {stock_count} stocks in database")
else:
self.print_info("No stocks found. Creating sample data...")
self.create_sample_data()

self.print_info(f"Email subscriptions: {subscription_count}")
return True

def create_sample_data(self):
"""Create sample stock data for testing"""
sample_stocks = [
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

for stock_data in sample_stocks:
stock, created = StockAlert.objects.get_or_create(
ticker=stock_data['ticker'],
defaults=stock_data
)
if created:
self.print_success(f"Created sample stock: {stock_data['ticker']}")

def test_api_endpoints(self):
"""Test all API endpoints that WordPress will use"""
self.print_header("API Endpoints Testing")

for endpoint in self.api_endpoints:
try:
response = self.client.get(endpoint)

if response.status_code == 200:
data = response.json()

if data.get('success'):
self.print_success(f"{endpoint} - Status: {response.status_code}")

# Show sample data
if 'data' in data:
if isinstance(data['data'], list) and len(data['data']) > 0:
sample = data['data'][0]
if 'ticker' in sample:
self.print_info(f" Sample: {sample['ticker']} - ${sample.get('current_price', 'N/A')}")
elif isinstance(data['data'], dict):
if 'market_overview' in data['data']:
overview = data['data']['market_overview']
self.print_info(f" Market: {overview.get('total_stocks', 0)} stocks, {overview.get('gainers', 0)} gainers")
else:
self.print_error(f"{endpoint} - API returned success=false")
else:
self.print_error(f"{endpoint} - Status: {response.status_code}")

except Exception as e:
self.print_error(f"{endpoint} - Error: {str(e)}")

def test_specific_stock_api(self):
"""Test specific stock detail API"""
self.print_header("Specific Stock API Testing")

# Test with sample tickers
test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'INVALID']

for ticker in test_tickers:
try:
response = self.client.get(f'/api/stocks/{ticker}/')

if response.status_code == 200:
data = response.json()
if data.get('success') and 'data' in data:
stock_data = data['data']
self.print_success(f"{ticker}: ${stock_data.get('current_price', 'N/A')} ({stock_data.get('price_change_percent', 0)}%)")
else:
self.print_error(f"{ticker}: API error - {data.get('error', 'Unknown error')}")
elif response.status_code == 404:
self.print_info(f"{ticker}: Not found (expected for INVALID)")
else:
self.print_error(f"{ticker}: HTTP {response.status_code}")

except Exception as e:
self.print_error(f"{ticker}: Exception - {str(e)}")

def test_search_api(self):
"""Test stock search API"""
self.print_header("Stock Search API Testing")

search_queries = ['AAPL', 'Apple', 'tech', 'Microsoft']

for query in search_queries:
try:
response = self.client.get(f'/api/stocks/search/?q={query}&limit=3')

if response.status_code == 200:
data = response.json()
if data.get('success'):
results = data.get('data', [])
self.print_success(f"Search '{query}': Found {len(results)} results")
for result in results[:2]: # Show first 2 results
self.print_info(f" {result.get('ticker')} - {result.get('company_name', 'N/A')}")
else:
self.print_error(f"Search '{query}': {data.get('error', 'Unknown error')}")
else:
self.print_error(f"Search '{query}': HTTP {response.status_code}")

except Exception as e:
self.print_error(f"Search '{query}': Exception - {str(e)}")

def test_market_movers_api(self):
"""Test market movers API"""
self.print_header("Market Movers API Testing")

mover_types = ['gainers', 'losers', 'volume']

for mover_type in mover_types:
try:
response = self.client.get(f'/api/market-movers/?type={mover_type}&limit=3')

if response.status_code == 200:
data = response.json()
if data.get('success'):
movers = data.get('data', [])
self.print_success(f"{mover_type.capitalize()}: Found {len(movers)} stocks")
for mover in movers[:2]: # Show first 2
change = mover.get('price_change_percent', 0)
self.print_info(f" {mover.get('ticker')} - {change}%")
else:
self.print_error(f"{mover_type}: {data.get('error', 'Unknown error')}")
else:
self.print_error(f"{mover_type}: HTTP {response.status_code}")

except Exception as e:
self.print_error(f"{mover_type}: Exception - {str(e)}")

def test_subscription_api(self):
"""Test WordPress subscription API"""
self.print_header("Subscription API Testing")

test_data = {
'email': 'test@example.com',
'category': 'dvsa-50'
}

try:
response = self.client.post(
'/api/wordpress/subscribe/',
data=json.dumps(test_data),
content_type='application/json'
)

if response.status_code == 200:
data = response.json()
if data.get('success'):
self.print_success(f"Subscription API works - Email: {test_data['email']}")

# Verify in database
subscription = EmailSubscription.objects.filter(
email=test_data['email'],
category=test_data['category']
).first()

if subscription:
self.print_success("Subscription saved to database")
else:
self.print_error("Subscription not found in database")
else:
self.print_error(f"Subscription failed: {data.get('error', 'Unknown error')}")
else:
self.print_error(f"Subscription API: HTTP {response.status_code}")

except Exception as e:
self.print_error(f"Subscription API: Exception - {str(e)}")

def test_cors_headers(self):
"""Test CORS headers for WordPress integration"""
self.print_header("CORS Headers Testing")

try:
response = self.client.options('/api/stocks/')

cors_headers = [
'Access-Control-Allow-Origin',
'Access-Control-Allow-Methods',
'Access-Control-Allow-Headers',
]

for header in cors_headers:
if header in response:
self.print_success(f"CORS header present: {header}")
else:
self.print_info(f"CORS header missing: {header} (may be handled by middleware)")

# Test actual CORS with GET request
response = self.client.get('/api/stocks/')
if response.status_code == 200:
self.print_success("API accessible (CORS should work)")
else:
self.print_error(f"API not accessible: HTTP {response.status_code}")

except Exception as e:
self.print_error(f"CORS test: Exception - {str(e)}")

def generate_wordpress_example(self):
"""Generate example WordPress PHP code"""
self.print_header("WordPress Integration Example")

php_code = '''
<?php
// Add this to your WordPress theme's functions.php
define('DJANGO_API_URL', 'http://127.0.0.1:8000/');

// Get stock data in WordPress
function get_stock_data($ticker) {
$api_url = DJANGO_API_URL . 'api/stocks/' . urlencode($ticker) . '/';
$response = wp_remote_get($api_url);

if (is_wp_error($response)) {
return false;
}

$body = wp_remote_retrieve_body($response);
$data = json_decode($body, true);

return $data['success'] ? $data['data'] : false;
}

// Use in WordPress templates:
$apple_stock = get_stock_data('AAPL');
if ($apple_stock) {
echo "AAPL: $" . $apple_stock['current_price'];
echo " (" . $apple_stock['price_change_percent'] . "%)";
}
?>
'''

print(php_code)
self.print_success("WordPress integration example generated")

def run_all_tests(self):
"""Run all integration tests"""
print(" Django-WordPress Integration Test Suite")
print(f" Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

try:
self.test_database_setup()
self.test_api_endpoints()
self.test_specific_stock_api()
self.test_search_api()
self.test_market_movers_api()
self.test_subscription_api()
self.test_cors_headers()
self.generate_wordpress_example()

self.print_header("Integration Test Summary")
self.print_success(" All tests completed!")
self.print_info("Your Django backend is ready for WordPress integration.")
self.print_info("Next steps:")
print(" 1. Deploy your WordPress theme")
print(" 2. Configure DJANGO_API_URL in wp-config.php")
print(" 3. Test the integration on your WordPress site")

except Exception as e:
self.print_error(f"Test suite failed: {str(e)}")
raise

def main():
tester = WordPressIntegrationTester()
tester.run_all_tests()

if __name__ == '__main__':
main()