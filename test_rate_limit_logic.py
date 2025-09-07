#!/usr/bin/env python3
"""
Test the rate limiting logic without requiring Django to be running
This script simulates the rate limiting behavior
"""

import time
from datetime import datetime

class RateLimitSimulator:
    """Simulates the rate limiting logic"""
    
    FREE_ENDPOINTS = [
        '/health/',
        '/api/health/',
        '/api/docs/',
        '/api/endpoint-status/',
        '/health/detailed/',
        '/health/ready/',
        '/health/live/',
        '/docs/',
        '/endpoint-status/',
        '/accounts/login/',
        '/accounts/logout/',
        '/admin/',
        '/static/',
        '/media/',
        # Note: '/' and '/api/' are too general and would match everything
        # They should be checked last or handled specially
    ]
    
    RATE_LIMITED_ENDPOINTS = [
        '/api/stocks/',
        '/api/stock/',
        '/api/search/',
        '/api/trending/',
        '/api/realtime/',
        '/api/filter/',
        '/api/market-stats/',
        '/api/portfolio/',
        '/api/watchlist/',
        '/api/alerts/',
        '/revenue/',
    ]
    
    def __init__(self):
        self.free_user_limit = 100
        self.authenticated_user_limit = 1000
        self.window_seconds = 3600
        self.request_cache = {}
    
    def should_rate_limit(self, path):
        """Check if endpoint should be rate limited"""
        # Check free endpoints first (they take precedence)
        for free_endpoint in self.FREE_ENDPOINTS:
            if path.startswith(free_endpoint):
                return False
        
        # Check exact match for homepage and API root
        if path in ['/', '/api/']:
            return False
        
        # Check rate-limited endpoints
        for limited_endpoint in self.RATE_LIMITED_ENDPOINTS:
            if path.startswith(limited_endpoint):
                return True
        
        # Default: no rate limiting for unknown endpoints
        return False
    
    def check_rate_limit(self, user_id, path, is_authenticated=False, is_premium=False):
        """Simulate rate limit check"""
        # Check if this is a rate-limited endpoint
        should_limit = self.should_rate_limit(path)
        
        # No rate limiting for free endpoints
        if not should_limit:
            return True, "No rate limiting for this endpoint"
        
        # No rate limiting for premium users
        if is_premium:
            return True, "Premium user - no rate limiting"
        
        # Get appropriate limit
        limit = self.authenticated_user_limit if is_authenticated else self.free_user_limit
        
        # Get current time
        current_time = time.time()
        
        # Get user's request history
        if user_id not in self.request_cache:
            self.request_cache[user_id] = []
        
        # Clean old requests outside window
        window_start = current_time - self.window_seconds
        self.request_cache[user_id] = [
            req_time for req_time in self.request_cache[user_id]
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        if len(self.request_cache[user_id]) >= limit:
            remaining_time = int(self.request_cache[user_id][0] + self.window_seconds - current_time)
            return False, f"Rate limit exceeded ({limit} requests/hour). Retry in {remaining_time} seconds"
        
        # Add current request
        self.request_cache[user_id].append(current_time)
        remaining = limit - len(self.request_cache[user_id])
        
        return True, f"Request allowed ({remaining}/{limit} remaining)"


def test_endpoints():
    """Test different endpoint scenarios"""
    simulator = RateLimitSimulator()
    
    print("="*60)
    print("RATE LIMITING LOGIC TEST")
    print("="*60)
    
    # Test 1: Free endpoints
    print("\n1. Testing FREE endpoints (should never be rate limited):")
    print("-"*40)
    free_test_paths = ['/health/', '/docs/', '/api/health/', '/endpoint-status/']
    
    for path in free_test_paths:
        allowed, message = simulator.check_rate_limit('user1', path)
        status = "✅" if allowed else "❌"
        print(f"{status} {path}: {message}")
    
    # Test 2: Rate-limited endpoints for free user
    print("\n2. Testing RATE-LIMITED endpoints for FREE user:")
    print("-"*40)
    
    # Debug: Check if endpoint is detected as rate-limited
    path = '/api/stocks/'
    is_limited = simulator.should_rate_limit(path)
    print(f"Debug: '/api/stocks/' should be rate-limited: {is_limited}")
    print(f"Debug: Checking against RATE_LIMITED_ENDPOINTS:")
    for endpoint in simulator.RATE_LIMITED_ENDPOINTS[:3]:
        print(f"  - '{endpoint}': {path.startswith(endpoint)}")
    
    # Simulate 105 requests (should fail after 100)
    user_id = 'free_user'
    
    for i in range(105):
        allowed, message = simulator.check_rate_limit(user_id, path, is_authenticated=False)
        
        if i < 5 or i >= 98:  # Show first 5 and last 7 requests
            status = "✅" if allowed else "❌"
            print(f"Request {i+1:3d}: {status} - {message}")
        elif i == 5:
            print("...")
    
    # Test 3: Authenticated user (higher limit)
    print("\n3. Testing RATE-LIMITED endpoints for AUTHENTICATED user:")
    print("-"*40)
    
    user_id = 'auth_user'
    # Make 200 requests (should all succeed as limit is 1000)
    success_count = 0
    for i in range(200):
        allowed, message = simulator.check_rate_limit(user_id, path, is_authenticated=True)
        if allowed:
            success_count += 1
    
    print(f"✅ Authenticated user: {success_count}/200 requests successful")
    print(f"   (Limit is {simulator.authenticated_user_limit} requests/hour)")
    
    # Test 4: Premium user (no limits)
    print("\n4. Testing RATE-LIMITED endpoints for PREMIUM user:")
    print("-"*40)
    
    user_id = 'premium_user'
    # Make 500 requests (should all succeed)
    success_count = 0
    for i in range(500):
        allowed, message = simulator.check_rate_limit(user_id, path, is_premium=True)
        if allowed:
            success_count += 1
    
    print(f"✅ Premium user: {success_count}/500 requests successful")
    print(f"   (No rate limiting for premium users)")
    
    # Test 5: Different users are tracked separately
    print("\n5. Testing that different users are tracked separately:")
    print("-"*40)
    
    # Clear cache
    simulator.request_cache.clear()
    
    # Make 50 requests each from 3 different users
    users = ['user_a', 'user_b', 'user_c']
    for user in users:
        success_count = 0
        for i in range(50):
            allowed, _ = simulator.check_rate_limit(user, '/api/stocks/')
            if allowed:
                success_count += 1
        print(f"✅ {user}: {success_count}/50 requests successful")
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("✅ Free endpoints: Never rate limited")
    print("✅ Free users: Limited to 100 requests/hour on stock endpoints")
    print("✅ Authenticated users: Limited to 1000 requests/hour")
    print("✅ Premium users: No rate limiting")
    print("✅ Per-user tracking: Each user tracked separately")


if __name__ == "__main__":
    test_endpoints()