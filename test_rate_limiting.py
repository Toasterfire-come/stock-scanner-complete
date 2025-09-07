#!/usr/bin/env python
"""
Test script to verify rate limiting functionality
Tests that health checks and non-stock endpoints are unlimited for free users
while stock data endpoints are rate limited
"""

import requests
import time
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = ""  # Optional: Add API key for testing authenticated requests

# Test endpoints
FREE_ENDPOINTS = [
    "/health/",
    "/api/health/",
    "/health/detailed/",
    "/health/ready/",
    "/health/live/",
    "/docs/",
    "/endpoint-status/",
    "/api/endpoint-status/",
    "/",
]

RATE_LIMITED_ENDPOINTS = [
    "/api/stocks/",
    "/api/search/?search=AAPL",
    "/api/trending/",
]


def test_endpoint(url, headers=None):
    """Test a single endpoint"""
    try:
        response = requests.get(url, headers=headers, timeout=5)
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'content': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:100]
        }
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}


def test_free_endpoints():
    """Test that free endpoints have no rate limiting"""
    print("\n" + "="*60)
    print("Testing FREE endpoints (should have no rate limiting)")
    print("="*60)
    
    for endpoint in FREE_ENDPOINTS:
        url = BASE_URL + endpoint
        print(f"\nTesting: {url}")
        
        # Make multiple rapid requests
        success_count = 0
        for i in range(10):
            result = test_endpoint(url)
            if result.get('status_code') == 200:
                success_count += 1
            
            if i == 0:  # Print first response details
                print(f"  Response: {result.get('status_code', 'ERROR')}")
                if 'X-RateLimit-Limit' in result.get('headers', {}):
                    print(f"  Rate Limit Headers Found: {result['headers'].get('X-RateLimit-Limit')}")
        
        print(f"  Success rate: {success_count}/10 requests")
        
        if success_count < 10:
            print(f"  ⚠️  WARNING: Free endpoint might be rate limited!")
        else:
            print(f"  ✅ No rate limiting detected")


def test_rate_limited_endpoints():
    """Test that stock data endpoints are rate limited for anonymous users"""
    print("\n" + "="*60)
    print("Testing RATE LIMITED endpoints (should limit after ~100 requests/hour)")
    print("="*60)
    
    for endpoint in RATE_LIMITED_ENDPOINTS:
        url = BASE_URL + endpoint
        print(f"\nTesting: {url}")
        
        # Make requests until rate limited
        request_count = 0
        rate_limited = False
        
        for i in range(150):  # Try up to 150 requests
            result = test_endpoint(url)
            status = result.get('status_code', 0)
            
            if status == 200:
                request_count += 1
                if i == 0:  # Print first successful response
                    print(f"  First response: {status}")
                    if 'X-RateLimit-Limit' in result.get('headers', {}):
                        print(f"  Rate limit: {result['headers'].get('X-RateLimit-Limit')} requests")
                        print(f"  Remaining: {result['headers'].get('X-RateLimit-Remaining', 'N/A')}")
            elif status == 429:
                rate_limited = True
                print(f"  ✅ Rate limited after {request_count} requests")
                print(f"  Response: {result.get('content', {})}")
                if 'Retry-After' in result.get('headers', {}):
                    print(f"  Retry after: {result['headers']['Retry-After']} seconds")
                break
            else:
                print(f"  Unexpected status: {status}")
                break
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
        
        if not rate_limited and request_count > 100:
            print(f"  ⚠️  WARNING: Made {request_count} requests without rate limiting!")
        elif not rate_limited:
            print(f"  ℹ️  Made {request_count} requests (may already be rate limited from previous tests)")


def test_api_key_authentication():
    """Test that API key authentication bypasses rate limiting"""
    if not API_KEY:
        print("\n" + "="*60)
        print("Skipping API key test (no API_KEY configured)")
        print("="*60)
        return
    
    print("\n" + "="*60)
    print("Testing API key authentication (should bypass rate limiting)")
    print("="*60)
    
    headers = {'X-API-Key': API_KEY}
    
    for endpoint in RATE_LIMITED_ENDPOINTS[:1]:  # Test just one endpoint
        url = BASE_URL + endpoint
        print(f"\nTesting with API key: {url}")
        
        # Make many rapid requests
        success_count = 0
        for i in range(150):
            result = test_endpoint(url, headers=headers)
            if result.get('status_code') == 200:
                success_count += 1
            elif result.get('status_code') == 429:
                print(f"  ❌ Rate limited even with API key after {success_count} requests")
                break
            
            if i % 50 == 0:
                print(f"  Progress: {i} requests made, {success_count} successful")
        
        if success_count >= 150:
            print(f"  ✅ No rate limiting with API key ({success_count} successful requests)")


def main():
    """Run all tests"""
    print(f"\nRate Limiting Test Suite")
    print(f"Testing against: {BASE_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test free endpoints
    test_free_endpoints()
    
    # Test rate limited endpoints
    test_rate_limited_endpoints()
    
    # Test API key authentication
    test_api_key_authentication()
    
    print("\n" + "="*60)
    print("Test suite completed")
    print("="*60)


if __name__ == "__main__":
    main()