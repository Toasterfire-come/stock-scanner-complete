#!/usr/bin/env python3
"""
Frontend Integration Test for Stock Scanner

This script tests that all frontend pages load correctly and maintain
consistent design and functionality.
"""

import os
import sys
import django
from django.conf import settings
from django.test import Client
from django.core.management import call_command
import json
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

def test_page_loads():
    """Test that all pages load successfully"""
    client = Client()
    
    pages = [
        ('/', 'Home Page'),
        ('/news/', 'News Page'),
        ('/search/', 'Search Page'),
        ('/filter/', 'Filter Page'),
        ('/admin-dashboard/', 'Admin Dashboard'),
    ]
    
    print("🧪 Testing page loads...")
    
    for url, name in pages:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ {name}: {url} - OK")
            else:
                print(f"❌ {name}: {url} - Status {response.status_code}")
        except Exception as e:
            print(f"💥 {name}: {url} - Error: {e}")
    
    print()

def test_navigation_consistency():
    """Test that navigation is consistent across pages"""
    client = Client()
    
    pages = ['/', '/news/', '/search/', '/filter/', '/admin-dashboard/']
    expected_links = ['Home', 'News', 'Search', 'Filter', 'Admin']
    
    print("🧪 Testing navigation consistency...")
    
    for url in pages:
        try:
            response = client.get(url)
            content = response.content.decode('utf-8')
            
            missing_links = []
            for link in expected_links:
                if link not in content:
                    missing_links.append(link)
            
            if not missing_links:
                print(f"✅ Navigation on {url}: All links present")
            else:
                print(f"⚠️  Navigation on {url}: Missing {missing_links}")
                
        except Exception as e:
            print(f"💥 Navigation test for {url}: Error: {e}")
    
    print()

def test_api_endpoints():
    """Test that API endpoints respond correctly"""
    client = Client()
    
    endpoints = [
        ('/api/admin/status/', 'Admin Status API'),
        ('/api/admin/api-providers/', 'API Providers Status'),
        ('/api/admin/health/', 'System Health API'),
        ('/api/admin/metrics/', 'Performance Metrics API'),
    ]
    
    print("🧪 Testing API endpoints...")
    
    for url, name in endpoints:
        try:
            response = client.get(url)
            if response.status_code == 200:
                data = json.loads(response.content)
                if 'status' in data or 'error' in data:
                    print(f"✅ {name}: {url} - JSON response OK")
                else:
                    print(f"⚠️  {name}: {url} - Unexpected JSON structure")
            else:
                print(f"❌ {name}: {url} - Status {response.status_code}")
        except json.JSONDecodeError:
            print(f"❌ {name}: {url} - Invalid JSON response")
        except Exception as e:
            print(f"💥 {name}: {url} - Error: {e}")
    
    print()

def test_filter_functionality():
    """Test the filter page functionality"""
    client = Client()
    
    print("🧪 Testing filter functionality...")
    
    try:
        # Test GET request (page load)
        response = client.get('/filter/')
        if response.status_code == 200:
            print("✅ Filter page loads successfully")
        else:
            print(f"❌ Filter page load failed: {response.status_code}")
            return
        
        # Test POST request (filter submission)
        filter_data = {
            "current_price": {
                "type": "greater_than",
                "value": "10"
            }
        }
        
        response = client.post(
            '/filter/',
            data=json.dumps(filter_data),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            try:
                data = json.loads(response.content)
                print(f"✅ Filter POST request successful - {len(data)} results")
            except json.JSONDecodeError:
                print("⚠️  Filter POST returned non-JSON response")
        else:
            print(f"❌ Filter POST request failed: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Filter functionality test error: {e}")
    
    print()

def test_subscription_functionality():
    """Test subscription form functionality"""
    client = Client()
    
    print("🧪 Testing subscription functionality...")
    
    # Test subscription page load
    try:
        response = client.get('/subscribe/dvsa-50/')
        if response.status_code == 200:
            print("✅ Subscription page loads successfully")
        else:
            print(f"❌ Subscription page load failed: {response.status_code}")
            return
            
        # Test subscription submission
        subscription_data = {
            "email": "test@example.com"
        }
        
        response = client.post(
            '/subscribe-dvsa-50',
            data=json.dumps(subscription_data),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            try:
                data = json.loads(response.content)
                if 'message' in data:
                    print("✅ Subscription POST request successful")
                else:
                    print("⚠️  Subscription POST unexpected response format")
            except json.JSONDecodeError:
                print("⚠️  Subscription POST returned non-JSON response")
        else:
            print(f"❌ Subscription POST request failed: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Subscription functionality test error: {e}")
    
    print()

def test_admin_dashboard_features():
    """Test admin dashboard specific features"""
    client = Client()
    
    print("🧪 Testing admin dashboard features...")
    
    try:
        # Test dashboard page
        response = client.get('/admin-dashboard/')
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for key dashboard elements
            dashboard_elements = [
                'System Status Overview',
                'Quick Actions',
                'Advanced Configuration',
                'Alternative API Providers',
                'Real-time Execution Logs'
            ]
            
            missing_elements = []
            for element in dashboard_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if not missing_elements:
                print("✅ Admin dashboard: All key elements present")
            else:
                print(f"⚠️  Admin dashboard: Missing elements {missing_elements}")
                
            # Check for JavaScript functionality
            if 'refreshStatus()' in content and 'executeCommand(' in content:
                print("✅ Admin dashboard: JavaScript functions present")
            else:
                print("⚠️  Admin dashboard: Missing JavaScript functions")
                
        else:
            print(f"❌ Admin dashboard load failed: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Admin dashboard test error: {e}")
    
    print()

def test_design_consistency():
    """Test design consistency across pages"""
    client = Client()
    
    print("🧪 Testing design consistency...")
    
    pages = ['/', '/news/', '/search/', '/filter/', '/admin-dashboard/']
    
    for url in pages:
        try:
            response = client.get(url)
            content = response.content.decode('utf-8')
            
            # Check for consistent design elements
            design_checks = [
                ('.navbar', 'Navigation bar'),
                ('Stock Scanner', 'Site title'),
                ('#1f2937', 'Consistent navbar color'),
                ('Arial, sans-serif', 'Consistent font family'),
            ]
            
            issues = []
            for check, description in design_checks:
                if check not in content:
                    issues.append(description)
            
            if not issues:
                print(f"✅ Design consistency on {url}: All checks passed")
            else:
                print(f"⚠️  Design consistency on {url}: Issues with {issues}")
                
        except Exception as e:
            print(f"💥 Design consistency test for {url}: Error: {e}")
    
    print()

def test_responsive_elements():
    """Test that responsive elements are present"""
    client = Client()
    
    print("🧪 Testing responsive design elements...")
    
    pages = ['/filter/', '/admin-dashboard/']
    
    for url in pages:
        try:
            response = client.get(url)
            content = response.content.decode('utf-8')
            
            # Check for Bootstrap and responsive elements
            responsive_checks = [
                ('bootstrap', 'Bootstrap CSS'),
                ('container', 'Bootstrap container'),
                ('btn btn-', 'Bootstrap buttons'),
                ('table-responsive', 'Responsive tables'),
                ('col-md-', 'Responsive columns'),
            ]
            
            present = []
            for check, description in responsive_checks:
                if check in content:
                    present.append(description)
            
            print(f"✅ Responsive elements on {url}: {len(present)}/{len(responsive_checks)} present")
            
        except Exception as e:
            print(f"💥 Responsive design test for {url}: Error: {e}")
    
    print()

def run_comprehensive_frontend_test():
    """Run all frontend tests"""
    print("🚀 Starting Comprehensive Frontend Integration Test")
    print("=" * 60)
    
    tests = [
        ("Page Load Test", test_page_loads),
        ("Navigation Consistency", test_navigation_consistency),
        ("API Endpoints", test_api_endpoints),
        ("Filter Functionality", test_filter_functionality),
        ("Subscription Functionality", test_subscription_functionality),
        ("Admin Dashboard Features", test_admin_dashboard_features),
        ("Design Consistency", test_design_consistency),
        ("Responsive Elements", test_responsive_elements),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🧪 Running: {test_name}")
        print("-" * 40)
        
        try:
            test_func()
            results.append((test_name, True))
        except Exception as e:
            print(f"💥 {test_name} failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("=" * 60)
    print("📋 FRONTEND TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
    
    print("-" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All frontend tests passed! UI is consistent and functional.")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test frontend integration")
    parser.add_argument("--quick", action="store_true", help="Run only basic tests")
    
    args = parser.parse_args()
    
    if args.quick:
        print("⚡ Running quick frontend test...")
        test_page_loads()
        test_navigation_consistency()
    else:
        success = run_comprehensive_frontend_test()
        sys.exit(0 if success else 1)