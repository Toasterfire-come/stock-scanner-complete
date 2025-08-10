"""
Performance-Optimized Cache Manager for Stock Scanner API
Implements multi-level caching strategy for maximum performance
"""

import hashlib
import json
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, Optional, Union

from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponse
from django.utils.cache import patch_response_headers
from django.views.decorators.cache import cache_control
from django.views.decorators.vary import vary_on_headers

class CacheManager:
    """
    Advanced caching manager with multiple strategies
    """
    
    # Cache timeouts (in seconds)
    TIMEOUTS = {
        'stock_data': 60,          # 1 minute for real-time data
        'market_hours': 3600,      # 1 hour for market hours
        'user_preferences': 1800,  # 30 minutes for user settings
        'api_responses': 300,      # 5 minutes for API responses
        'static_content': 86400,   # 24 hours for static content
        'analytics': 900,          # 15 minutes for analytics
        'trending': 180,           # 3 minutes for trending data
    }
    
    @staticmethod
    def generate_cache_key(prefix: str, *args, **kwargs) -> str:
        """
        Generate a consistent cache key from arguments
        """
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else None,
            'timestamp': int(time.time() / 300)  # 5-minute buckets
        }
        
        hash_input = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(hash_input.encode()).hexdigest()[:12]
        
        return f"{prefix}:{key_hash}"
    
    @staticmethod
    def cache_response(timeout: int = None, key_prefix: str = 'response'):
        """
        Decorator for caching Django view responses
        """
        def decorator(view_func):
            @wraps(view_func)
            def wrapper(request, *args, **kwargs):
                # Generate cache key based on request
                cache_key = CacheManager.generate_cache_key(
                    key_prefix,
                    request.path,
                    request.GET.urlencode(),
                    getattr(request.user, 'id', 'anonymous')
                )
                
                # Try to get from cache first
                cached_response = cache.get(cache_key)
                if cached_response and not settings.DEBUG:
                    return cached_response
                
                # Generate response
                response = view_func(request, *args, **kwargs)
                
                # Cache successful responses
                if response.status_code == 200:
                    cache_timeout = timeout or CacheManager.TIMEOUTS.get('api_responses', 300)
                    cache.set(cache_key, response, cache_timeout)
                
                return response
            return wrapper
        return decorator
    
    @staticmethod
    def cache_function_result(timeout: int = None, key_prefix: str = 'function'):
        """
        Decorator for caching function results
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = CacheManager.generate_cache_key(
                    key_prefix,
                    func.__name__,
                    *args,
                    **kwargs
                )
                
                # Try cache first
                result = cache.get(cache_key)
                if result is not None:
                    return result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                cache_timeout = timeout or CacheManager.TIMEOUTS.get('api_responses', 300)
                cache.set(cache_key, result, cache_timeout)
                
                return result
            return wrapper
        return decorator
    
    @staticmethod
    def invalidate_pattern(pattern: str):
        """
        Invalidate cache keys matching a pattern
        """
        try:
            # This requires Redis backend
            from django.core.cache.backends.redis import RedisCache
            if isinstance(cache, RedisCache):
                cache_instance = cache._cache
                keys = cache_instance.keys(f"*{pattern}*")
                if keys:
                    cache_instance.delete(*keys)
        except ImportError:
            # Fallback for other cache backends
            pass
    
    @staticmethod
    def get_or_set_json(key: str, callable_func, timeout: int = None) -> Any:
        """
        Get JSON data from cache or set it using a callable
        """
        result = cache.get(key)
        if result is None:
            result = callable_func()
            cache_timeout = timeout or CacheManager.TIMEOUTS.get('api_responses', 300)
            cache.set(key, result, cache_timeout)
        return result

class BrowserCacheOptimizer:
    """
    Optimize browser caching with proper headers
    """
    
    @staticmethod
    def set_cache_headers(response: HttpResponse, 
                         max_age: int = 3600, 
                         public: bool = True,
                         etag: bool = True) -> HttpResponse:
        """
        Set optimal cache headers for browser caching
        """
        # Set cache control headers
        if public:
            response['Cache-Control'] = f'public, max-age={max_age}'
        else:
            response['Cache-Control'] = f'private, max-age={max_age}'
        
        # Set expiration header
        expires = datetime.utcnow() + timedelta(seconds=max_age)
        response['Expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # Add ETag if requested
        if etag and hasattr(response, 'content'):
            etag_value = hashlib.md5(response.content).hexdigest()
            response['ETag'] = f'"{etag_value}"'
        
        return response
    
    @staticmethod
    def cache_static_response(max_age: int = 86400):
        """
        Decorator for static content caching
        """
        def decorator(view_func):
            @wraps(view_func)
            def wrapper(request, *args, **kwargs):
                response = view_func(request, *args, **kwargs)
                return BrowserCacheOptimizer.set_cache_headers(
                    response, max_age=max_age, public=True
                )
            return wrapper
        return decorator

class PerformanceMiddleware:
    """
    Middleware for automatic performance optimizations
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Pre-process request
        start_time = time.time()
        
        # Add performance headers to request
        request.META['HTTP_X_PERFORMANCE_START'] = str(start_time)
        
        response = self.get_response(request)
        
        # Post-process response
        self.add_performance_headers(request, response, start_time)
        self.optimize_response(response)
        
        return response
    
    def add_performance_headers(self, request, response, start_time):
        """
        Add performance timing headers
        """
        if settings.DEBUG:
            process_time = time.time() - start_time
            response['X-Process-Time'] = f"{process_time:.3f}s"
            response['X-Server-Time'] = datetime.utcnow().isoformat()
    
    def optimize_response(self, response):
        """
        Apply response optimizations
        """
        # Compress responses over 1KB
        if len(response.content) > 1024:
            response['Content-Encoding'] = 'gzip'
        
        # Add security headers that also help performance
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

# Decorator shortcuts for common caching patterns
def cache_stock_data(timeout: int = None):
    """Cache stock data with default timeout"""
    return CacheManager.cache_function_result(
        timeout or CacheManager.TIMEOUTS['stock_data'], 
        'stock_data'
    )

def cache_api_response(timeout: int = None):
    """Cache API responses with default timeout"""
    return CacheManager.cache_response(
        timeout or CacheManager.TIMEOUTS['api_responses'],
        'api_response'
    )

def cache_analytics(timeout: int = None):
    """Cache analytics data with default timeout"""
    return CacheManager.cache_function_result(
        timeout or CacheManager.TIMEOUTS['analytics'],
        'analytics'
    )

# Example usage in views:
"""
from utils.cache_manager import cache_api_response, CacheManager

@cache_api_response(timeout=300)
def stock_list_view(request):
    # This view will be cached for 5 minutes
    stocks = get_stock_data()
    return JsonResponse({'stocks': stocks})

@CacheManager.cache_function_result(timeout=60, key_prefix='trending')
def get_trending_stocks():
    # This function result will be cached for 1 minute
    return calculate_trending_stocks()
"""