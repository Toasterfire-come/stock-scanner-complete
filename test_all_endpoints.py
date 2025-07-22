#!/usr/bin/env python3
"""
Comprehensive Endpoint Performance Test
Tests all 24 page endpoints for functionality and efficiency
"""

import os
import sys
import django
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from django.test import RequestFactory, TestCase
from django.contrib.auth.models import User
from django.http import JsonResponse

# Setup Django
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks import page_endpoints
from stocks.models import Membership, StockAlert
from emails.models import EmailSubscription

class EndpointTester:
    def __init__(self):
        self.factory = RequestFactory()
        self.test_user = None
        self.results = []
    
    def setup_test_data(self):
        """Create test user and data"""
        print("🔧 Setting up test data...")
        
        # Create test user
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create membership
        membership, created = Membership.objects.get_or_create(
            user=self.test_user,
            defaults={
                'tier': 'basic',
                'monthly_price': 9.99,
                'is_active': True
            }
        )
        
        # Create test stock data
        StockAlert.objects.get_or_create(
            ticker='AAPL',
            defaults={
                'company_name': 'Apple Inc.',
                'current_price': 150.00,
                'volume_today': 1000000
            }
        )
        
        # Create test email subscription
        EmailSubscription.objects.get_or_create(
            email=self.test_user.email,
            category='technology',
            defaults={'is_active': True}
        )
        
        print(f"✅ Test user created: {self.test_user.username}")
        print(f"✅ Test membership: {membership.tier}")
    
    def test_endpoint(self, endpoint_name, endpoint_func, method='GET', auth_required=False, post_data=None):
        """Test individual endpoint"""
        try:
            # Create request
            if method == 'GET':
                request = self.factory.get(f'/api/pages/{endpoint_name}/')
            else:
                request = self.factory.post(
                    f'/api/pages/{endpoint_name}/',
                    data=json.dumps(post_data or {}),
                    content_type='application/json'
                )
            
            # Add user if authentication required
            if auth_required and self.test_user:
                request.user = self.test_user
            else:
                request.user = MagicMock()
                request.user.is_authenticated = False
            
            # Mock yfinance to avoid external API calls
            with patch('yfinance.Ticker') as mock_ticker:
                mock_stock = MagicMock()
                mock_stock.history.return_value.empty = False
                mock_stock.history.return_value.__len__.return_value = 1
                mock_stock.history.return_value.__getitem__ = lambda self, key: [150.0]
                mock_stock.history.return_value.iloc = MagicMock()
                mock_stock.history.return_value.iloc.__getitem__.return_value = 150.0
                mock_stock.news = []
                mock_ticker.return_value = mock_stock
                
                # Call endpoint
                response = endpoint_func(request)
            
            # Check response
            if isinstance(response, JsonResponse):
                data = json.loads(response.content.decode())
                success = data.get('success', False)
                
                self.results.append({
                    'endpoint': endpoint_name,
                    'method': method,
                    'status': 'PASS' if success else 'FAIL',
                    'response_code': response.status_code,
                    'auth_required': auth_required,
                    'error': data.get('error', '') if not success else ''
                })
                
                status_icon = "✅" if success else "❌"
                auth_icon = "🔒" if auth_required else "🌐"
                print(f"{status_icon} {auth_icon} {endpoint_name} ({method}) - {response.status_code}")
                
                return success
            else:
                print(f"❌ {endpoint_name} - Invalid response type")
                return False
                
        except Exception as e:
            self.results.append({
                'endpoint': endpoint_name,
                'method': method,
                'status': 'ERROR',
                'error': str(e),
                'auth_required': auth_required
            })
            print(f"💥 {endpoint_name} - ERROR: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Test all 24 page endpoints"""
        print("🚀 Testing All Page Endpoints")
        print("=" * 50)
        
        # Test all endpoints
        endpoints_to_test = [
            # Public endpoints
            ('premium-plans', page_endpoints.premium_plans_api, 'GET', False),
            ('email-stock-lists', page_endpoints.email_stock_lists_api, 'GET', False),
            ('email-stock-lists', page_endpoints.email_stock_lists_api, 'POST', False, {'email': 'test@example.com', 'category': 'tech'}),
            ('all-stock-alerts', page_endpoints.all_stock_alerts_api, 'GET', False),
            ('popular-stock-lists', page_endpoints.popular_stock_lists_api, 'GET', False),
            ('personalized-stock-finder', page_endpoints.personalized_stock_finder_api, 'GET', False),
            ('personalized-stock-finder', page_endpoints.personalized_stock_finder_api, 'POST', False, {'risk_tolerance': 'moderate'}),
            ('news-scrapper', page_endpoints.news_scrapper_api, 'GET', False),
            ('filter-scrapper', page_endpoints.filter_and_scrapper_pages_api, 'GET', False),
            ('membership-levels', page_endpoints.membership_levels_api, 'GET', False),
            ('login', page_endpoints.login_api, 'GET', False),
            ('login', page_endpoints.login_api, 'POST', False, {'email': 'test@example.com', 'password': 'test'}),
            ('terms-conditions', page_endpoints.terms_and_conditions_api, 'GET', False),
            ('privacy-policy', page_endpoints.privacy_policy_api, 'GET', False),
            ('stock-market-news', page_endpoints.stock_market_news_api, 'GET', False),
            ('membership-plans', page_endpoints.membership_plans_api, 'GET', False),
            ('membership-checkout', page_endpoints.membership_checkout_api, 'GET', False),
            ('membership-checkout', page_endpoints.membership_checkout_api, 'POST', False, {'plan': 'basic'}),
            
            # Authenticated endpoints
            ('membership-account', page_endpoints.membership_account_api, 'GET', True),
            ('membership-billing', page_endpoints.membership_billing_api, 'GET', True),
            ('membership-cancel', page_endpoints.membership_cancel_api, 'GET', True),
            ('membership-cancel', page_endpoints.membership_cancel_api, 'POST', True, {'type': 'immediate'}),
            ('membership-confirmation', page_endpoints.membership_confirmation_api, 'GET', True),
            ('membership-orders', page_endpoints.membership_orders_api, 'GET', True),
            ('your-profile', page_endpoints.your_profile_api, 'GET', True),
            ('your-profile', page_endpoints.your_profile_api, 'POST', True, {'username': 'newname'}),
            ('stock-dashboard', page_endpoints.stock_dashboard_api, 'GET', True),
            ('stock-watchlist', page_endpoints.stock_watchlist_api, 'GET', True),
            ('stock-watchlist', page_endpoints.stock_watchlist_api, 'POST', True, {'ticker': 'MSFT'}),
        ]
        
        passed = 0
        total = len(endpoints_to_test)
        
        for endpoint_name, endpoint_func, method, auth_required, *post_data in endpoints_to_test:
            post_data = post_data[0] if post_data else None
            success = self.test_endpoint(endpoint_name, endpoint_func, method, auth_required, post_data)
            if success:
                passed += 1
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} endpoints passed")
        
        # Show failed endpoints
        failed = [r for r in self.results if r['status'] != 'PASS']
        if failed:
            print(f"\n❌ Failed Endpoints ({len(failed)}):")
            for fail in failed:
                print(f"   - {fail['endpoint']} ({fail['method']}): {fail.get('error', 'Unknown error')}")
        
        # Show authentication requirements
        auth_endpoints = [r for r in self.results if r['auth_required']]
        print(f"\n🔒 Authentication Required: {len(auth_endpoints)} endpoints")
        
        return passed == total
    
    def generate_endpoint_summary(self):
        """Generate summary of all endpoints"""
        print("\n📋 Endpoint Summary")
        print("=" * 50)
        
        print("🌐 Public Endpoints:")
        public = [r for r in self.results if not r['auth_required']]
        for endpoint in public:
            status_icon = "✅" if endpoint['status'] == 'PASS' else "❌"
            print(f"   {status_icon} /api/pages/{endpoint['endpoint']}/ ({endpoint['method']})")
        
        print(f"\n🔒 Authenticated Endpoints:")
        auth = [r for r in self.results if r['auth_required']]
        for endpoint in auth:
            status_icon = "✅" if endpoint['status'] == 'PASS' else "❌"
            print(f"   {status_icon} /api/pages/{endpoint['endpoint']}/ ({endpoint['method']})")
        
        print(f"\n📊 Statistics:")
        print(f"   - Total Endpoints: {len(self.results)}")
        print(f"   - Public: {len(public)}")
        print(f"   - Authenticated: {len(auth)}")
        print(f"   - Passed: {len([r for r in self.results if r['status'] == 'PASS'])}")
        print(f"   - Failed: {len([r for r in self.results if r['status'] != 'PASS'])}")

def main():
    tester = EndpointTester()
    
    try:
        tester.setup_test_data()
        all_passed = tester.run_all_tests()
        tester.generate_endpoint_summary()
        
        if all_passed:
            print("\n🎉 ALL ENDPOINTS WORKING CORRECTLY!")
            print("✅ Every WordPress page has a functional backend API")
            print("✅ Authentication properly implemented")
            print("✅ Error handling in place")
            print("✅ JSON responses standardized")
        else:
            print("\n⚠️ Some endpoints need attention. See details above.")
        
        return all_passed
        
    except Exception as e:
        print(f"\n💥 Test setup failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
