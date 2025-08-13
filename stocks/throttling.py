"""
Advanced Rate Limiting and Throttling for Stock Scanner API
Provides production-ready API protection with intelligent throttling
"""

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging
import hashlib

logger = logging.getLogger(__name__)

class IntelligentRateThrottle:
    """
    Base class for intelligent rate throttling with adaptive limits
    """
    
    def get_cache_key(self, request, view):
        """Generate cache key for rate limiting"""
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        return f"{self.scope}_{ident}"
    
    def get_ident(self, request):
        """Identify client by IP and headers"""
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        remote_addr = request.META.get('REMOTE_ADDR')
        
        if xff:
            # Use first IP in X-Forwarded-For chain
            ip = xff.split(',')[0].strip()
        else:
            ip = remote_addr
            
        # Add user agent for better identification
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        combined = f"{ip}_{hashlib.md5(user_agent.encode()).hexdigest()[:8]}"
        
        return combined

class StockAPIThrottle(IntelligentRateThrottle, UserRateThrottle):
    """
    Rate limiting for authenticated stock API requests
    """
    scope = 'stock_api'
    
    def get_rate(self):
        """Dynamic rate based on user membership"""
        if hasattr(self, 'request') and self.request.user.is_authenticated:
            try:
                from .models import Membership
                membership = Membership.objects.get(user=self.request.user)
                
                # Different rates based on membership level
                rate_map = {
                    'free': '100/hour',
                    'basic': '500/hour', 
                    'pro': '2000/hour',
                    'enterprise': '10000/hour'
                }
                
                return rate_map.get(membership.plan, '100/hour')
                
            except (Membership.DoesNotExist, Exception):
                return '100/hour'  # Default for authenticated users
        
        return '50/hour'  # Default rate

class AnonymousAPIThrottle(IntelligentRateThrottle, AnonRateThrottle):
    """
    Rate limiting for anonymous API requests
    """
    scope = 'anon_api'
    rate = '30/hour'  # Stricter for anonymous users

class SearchThrottle(IntelligentRateThrottle, UserRateThrottle):
    """
    Specialized throttling for search endpoints
    """
    scope = 'search'
    rate = '100/hour'
    
    def allow_request(self, request, view):
        """Enhanced allow logic with search complexity detection"""
        # Check base rate limit first
        if not super().allow_request(request, view):
            return False
        
        # Additional throttling for complex searches
        query = request.GET.get('search', '')
        if len(query) < 2:  # Very short queries are expensive
            return self._check_short_query_limit(request)
        
        return True
    
    def _check_short_query_limit(self, request):
        """Limit very short queries that cause broad searches"""
        cache_key = f"short_search_{self.get_cache_key(request, None)}"
        current_time = timezone.now()
        
        # Allow max 10 short queries per 10 minutes
        requests = cache.get(cache_key, [])
        cutoff_time = current_time - timedelta(minutes=10)
        
        # Clean old requests
        requests = [req_time for req_time in requests if req_time > cutoff_time]
        
        if len(requests) >= 10:
            logger.warning(f"Short query limit exceeded for {self.get_ident(request)}")
            return False
        
        requests.append(current_time)
        cache.set(cache_key, requests, 600)  # 10 minutes
        
        return True

class BulkOperationThrottle(IntelligentRateThrottle, UserRateThrottle):
    """
    Throttling for bulk operations and data-intensive endpoints
    """
    scope = 'bulk_operation'
    rate = '10/hour'
    
    def allow_request(self, request, view):
        """Enhanced throttling for bulk operations"""
        if not super().allow_request(request, view):
            return False
        
        # Additional checks for bulk size
        if request.method == 'POST':
            return self._check_bulk_size(request)
        
        return True
    
    def _check_bulk_size(self, request):
        """Limit based on bulk operation size"""
        try:
            data = request.data
            if isinstance(data, dict):
                # Check for bulk indicators
                tickers = data.get('tickers', [])
                if len(tickers) > 50:  # Large bulk operations
                    cache_key = f"large_bulk_{self.get_cache_key(request, None)}"
                    
                    # Allow max 3 large bulk operations per hour
                    if cache.get(cache_key, 0) >= 3:
                        logger.warning(f"Large bulk operation limit exceeded for user {request.user}")
                        return False
                    
                    cache.set(cache_key, cache.get(cache_key, 0) + 1, 3600)
                    
        except Exception as e:
            logger.error(f"Error checking bulk size: {e}")
        
        return True

class RealtimeDataThrottle(IntelligentRateThrottle, UserRateThrottle):
    """
    Throttling for real-time data endpoints
    """
    scope = 'realtime'
    rate = '300/hour'  # More generous for real-time needs
    
    def allow_request(self, request, view):
        """Allow bursts but limit sustained usage"""
        if not super().allow_request(request, view):
            # Check if this is a burst request
            return self._check_burst_allowance(request)
        
        return True
    
    def _check_burst_allowance(self, request):
        """Allow short bursts of requests for real-time updates"""
        cache_key = f"burst_{self.get_cache_key(request, None)}"
        current_time = timezone.now()
        
        # Allow 20 requests in 1 minute burst
        burst_requests = cache.get(cache_key, [])
        cutoff_time = current_time - timedelta(minutes=1)
        
        # Clean old requests
        burst_requests = [req_time for req_time in burst_requests if req_time > cutoff_time]
        
        if len(burst_requests) >= 20:
            return False
        
        burst_requests.append(current_time)
        cache.set(cache_key, burst_requests, 60)
        
        return True

class AdminAPIThrottle(IntelligentRateThrottle, UserRateThrottle):
    """
    Throttling for admin API endpoints
    """
    scope = 'admin_api'
    rate = '1000/hour'  # Higher limits for admin users
    
    def allow_request(self, request, view):
        """Only apply to non-admin users"""
        if request.user.is_authenticated and request.user.is_staff:
            return True  # No limits for admin users
        
        return super().allow_request(request, view)

class DynamicThrottle(IntelligentRateThrottle, UserRateThrottle):
    """
    Dynamic throttling based on system load and user behavior
    """
    scope = 'dynamic'
    
    def get_rate(self):
        """Adjust rate based on system metrics"""
        base_rate = 200  # Base requests per hour
        
        # Check system load indicators
        load_factor = self._get_load_factor()
        adjusted_rate = int(base_rate * load_factor)
        
        return f"{adjusted_rate}/hour"
    
    def _get_load_factor(self):
        """Calculate load factor based on system metrics"""
        try:
            # Check cache hit ratio
            cache_stats = cache.get('system_stats', {})
            cache_hit_ratio = cache_stats.get('cache_hit_ratio', 0.8)
            
            # Check active connections
            active_connections = cache_stats.get('active_connections', 0)
            
            # Calculate load factor (0.5 to 1.5 range)
            if cache_hit_ratio > 0.9 and active_connections < 100:
                return 1.5  # System running smoothly - increase limits
            elif cache_hit_ratio < 0.5 or active_connections > 500:
                return 0.5  # System under stress - reduce limits
            else:
                return 1.0  # Normal operation
                
        except Exception as e:
            logger.error(f"Error calculating load factor: {e}")
            return 0.8  # Conservative fallback

class IPBasedThrottle(IntelligentRateThrottle, AnonRateThrottle):
    """
    IP-based throttling with subnet awareness
    """
    scope = 'ip_based'
    rate = '1000/hour'
    
    def get_cache_key(self, request, view):
        """Generate cache key based on IP subnet"""
        ip = self.get_ident(request)
        
        # Group by /24 subnet for IPv4
        if '.' in ip:
            ip_parts = ip.split('.')
            if len(ip_parts) >= 3:
                subnet = '.'.join(ip_parts[:3]) + '.0/24'
                return f"{self.scope}_{subnet}"
        
        return f"{self.scope}_{ip}"

class SmartThrottleMiddleware:
    """
    Middleware for intelligent throttle management
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Update system metrics before processing
        self._update_system_metrics(request)
        
        response = self.get_response(request)
        
        # Log throttle events
        if hasattr(response, 'status_code') and response.status_code == 429:
            self._log_throttle_event(request, response)
        
        return response
    
    def _update_system_metrics(self, request):
        """Update system metrics for dynamic throttling"""
        try:
            cache_key = 'system_stats'
            stats = cache.get(cache_key, {})
            
            # Update request count
            stats['total_requests'] = stats.get('total_requests', 0) + 1
            
            # Update timestamp
            stats['last_updated'] = timezone.now().isoformat()
            
            # Cache for 1 minute
            cache.set(cache_key, stats, 60)
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
    
    def _log_throttle_event(self, request, response):
        """Log throttle events for monitoring"""
        user_id = request.user.id if request.user.is_authenticated else 'anonymous'
        ip = request.META.get('REMOTE_ADDR', 'unknown')
        endpoint = request.path
        
        logger.warning(
            f"Rate limit exceeded - User: {user_id}, IP: {ip}, "
            f"Endpoint: {endpoint}, Method: {request.method}"
        )

# Rate limit configuration for settings.py
THROTTLE_RATES = {
    'stock_api': '200/hour',
    'anon_api': '30/hour', 
    'search': '100/hour',
    'bulk_operation': '10/hour',
    'realtime': '300/hour',
    'admin_api': '1000/hour',
    'dynamic': '200/hour',
    'ip_based': '1000/hour',
}