"""
Rate limiting middleware for controlling API access
Allows unlimited access to health checks and non-stock-data endpoints for free users
"""
import time
import json
import logging
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.db.models import Sum
from .models import UsageStats, UserProfile

logger = logging.getLogger(__name__)


class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware that allows unlimited access to certain endpoints
    while limiting access to stock data endpoints for free users
    """
    
    # Endpoints that are always free (no rate limiting)
    # NOTE: More specific paths must come before general paths
    FREE_ENDPOINTS = [
        # Health check endpoints
        '/health/',
        '/api/health/',
        '/health/detailed/',
        '/health/ready/',
        '/health/live/',
        
        # Documentation and status endpoints
        '/docs/',
        '/api/docs/',
        '/endpoint-status/',
        '/api/endpoint-status/',
        
        # Authentication endpoints
        '/accounts/login/',
        '/accounts/logout/',
        '/accounts/signup/',
        '/accounts/password_reset/',
        '/api/auth/',
        
        # Admin (handled separately by Django auth)
        '/admin/',
        
        # Static files
        '/static/',
        '/media/',
    ]
    
    # Special endpoints that need exact match (not prefix)
    EXACT_FREE_ENDPOINTS = [
        '/',  # Homepage only
        '/api/',  # API root only
    ]
    
    # Endpoints that require rate limiting for free users
    RATE_LIMITED_ENDPOINTS = getattr(settings, 'STOCK_DATA_ENDPOINT_PREFIXES', [
        '/api/stocks/',
        '/api/stock/',
        '/api/search/',
        '/api/trending/',
        '/api/realtime/',
        '/api/filter/',
        '/api/market-stats/',
    ])
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Rate limit configuration
        # Free users per-hour limit derives from env and supports marketing requirement of 30 if set
        self.free_user_limit = int(getattr(settings, 'RATE_LIMIT_FREE_USERS', 100))
        self.free_user_window = getattr(settings, 'RATE_LIMIT_WINDOW', 3600)  # 1 hour in seconds
        self.authenticated_user_limit = getattr(settings, 'RATE_LIMIT_AUTHENTICATED_USERS', 1000)  # requests per hour
        
        # Premium user settings (no rate limiting)
        self.premium_user_groups = getattr(settings, 'PREMIUM_USER_GROUPS', ['premium', 'pro', 'enterprise'])
    
    def __call__(self, request):
        # Always skip CORS preflight and non-mutating methods that should not be rate limited
        if request.method in ("OPTIONS", "HEAD"):
            return self.get_response(request)

        # Check if rate limiting should be applied
        if not self.should_rate_limit(request):
            return self.get_response(request)
        
        # Get user identifier
        user_id = self.get_user_identifier(request)
        
        # Check if user is premium (no rate limiting)
        if self.is_premium_user(request):
            # Track usage for enterprise/premium for display purposes only
            response = self.get_response(request)
            try:
                self._increment_monthly_usage(request)
            except Exception:
                pass
            return response
        
        # Get rate limit for this user
        rate_limit = self.get_rate_limit(request)
        
        # Check rate limit
        if not self.check_rate_limit(user_id, rate_limit):
            return self.rate_limit_exceeded_response(user_id, rate_limit)

        # Strict monthly enforcement for authenticated users based on plan tier
        if getattr(getattr(request, 'user', None), 'is_authenticated', False):
            try:
                profile = getattr(request.user, 'profile', None)
                api_monthly_limit = int(getattr(profile, 'api_calls_limit', 100)) if profile else 100
                plan_type = (getattr(profile, 'plan_type', 'free') if profile else 'free') or 'free'

                # Enterprise has unlimited monthly, but we still track usage
                is_enterprise = str(plan_type).lower() == 'enterprise'
                if not is_enterprise and api_monthly_limit >= 0:
                    month_start = timezone.now().replace(day=1).date()
                    used = UsageStats.objects.filter(user=request.user, date__gte=month_start).aggregate(total=Sum('api_calls')).get('total') or 0
                    if used >= api_monthly_limit:
                        # Monthly quota exceeded
                        return self.monthly_limit_exceeded_response(api_monthly_limit, used)
                # Mark for post-response increment
                request._count_usage_after_response = True
            except Exception:
                # Fail-open on usage calculation errors
                request._count_usage_after_response = True
        else:
            request._count_usage_after_response = False
        
        # Process request
        response = self.get_response(request)
        # Increment usage after successful response
        try:
            if getattr(request, '_count_usage_after_response', False) and (200 <= getattr(response, 'status_code', 200) < 500):
                self._increment_monthly_usage(request)
        except Exception:
            pass
        return response
    
    def should_rate_limit(self, request):
        """
        Determine if this request should be rate limited
        """
        path = request.path
        method = request.method

        # Never rate limit preflight or HEAD requests
        if method in ("OPTIONS", "HEAD"):
            return False
        
        # Check if endpoint is in free list (no rate limiting)
        for free_endpoint in self.FREE_ENDPOINTS:
            if path.startswith(free_endpoint):
                logger.debug(f"Endpoint {path} is free, no rate limiting")
                return False
        
        # Check exact match endpoints
        if path in self.EXACT_FREE_ENDPOINTS:
            logger.debug(f"Endpoint {path} is free (exact match), no rate limiting")
            return False
        
        # Check if endpoint is in rate-limited list
        for limited_endpoint in self.RATE_LIMITED_ENDPOINTS:
            if path.startswith(limited_endpoint):
                logger.debug(f"Endpoint {path} requires rate limiting")
                return True
        
        # Default: don't rate limit unknown endpoints
        logger.debug(f"Endpoint {path} not in rate limit lists, allowing free access")
        return False
    
    def get_user_identifier(self, request):
        """
        Get a unique identifier for the user
        """
        user = getattr(request, 'user', None)
        is_authenticated = getattr(user, 'is_authenticated', False)

        if is_authenticated:
            user_id = getattr(user, 'id', None)
            # Fallback to session key if user id is somehow missing
            if user_id is not None:
                return f"user_{user_id}"

        # Use IP address (or a generic fallback) for anonymous/missing user
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return f"ip_{ip}"
    
    def is_premium_user(self, request):
        """
        Check if user is a premium user (no rate limiting)
        """
        user = getattr(request, 'user', None)
        if not getattr(user, 'is_authenticated', False):
            return False
        
        # Enterprise email whitelist override
        try:
            from django.conf import settings as django_settings
            enterprise_emails = set(email.lower() for email in getattr(django_settings, 'ENTERPRISE_EMAIL_WHITELIST', []))
            user_email = (getattr(user, 'email', '') or '').lower()
            if user_email and user_email in enterprise_emails:
                return True
        except Exception:
            pass

        # Profile-based premium/enterprise check
        try:
            profile = getattr(user, 'profile', None)
            if profile and getattr(profile, 'plan_type', 'free') in ('pro', 'enterprise'):
                return True
            if profile and getattr(profile, 'is_premium', False):
                return True
        except Exception:
            pass

        # Check if user is in premium groups
        user_groups = getattr(user, 'groups', None)
        if user_groups is not None:
            user_groups = user_groups.values_list('name', flat=True)
        else:
            user_groups = []
        for group in self.premium_user_groups:
            if group in user_groups:
                username = getattr(user, 'username', 'unknown')
                logger.debug(f"User {username} is premium, no rate limiting")
                return True
        
        # Check if user is staff or superuser
        if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
            username = getattr(user, 'username', 'unknown')
            logger.debug(f"User {username} is staff/superuser, no rate limiting")
            return True
        
        return False
    
    def get_rate_limit(self, request):
        """
        Get the rate limit for this user
        """
        if getattr(getattr(request, 'user', None), 'is_authenticated', False):
            return self.authenticated_user_limit
        else:
            return self.free_user_limit
    
    def check_rate_limit(self, user_id, limit):
        """
        Check if user has exceeded rate limit
        """
        cache_key = f"rate_limit_{user_id}"
        current_time = time.time()
        
        # Get current request data from cache
        try:
            request_data = cache.get(cache_key)
        except Exception:
            # Fail-open if cache backend is unavailable
            request_data = None
        
        if request_data is None:
            # First request, initialize
            cache.set(cache_key, {
                'count': 1,
                'window_start': current_time,
                'requests': [current_time]
            }, self.free_user_window)
            return True
        
        # Clean old requests outside the window
        window_start = current_time - self.free_user_window
        request_data['requests'] = [
            req_time for req_time in request_data['requests']
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        if len(request_data['requests']) >= limit:
            logger.warning(f"Rate limit exceeded for {user_id}: {len(request_data['requests'])} requests in window")
            return False
        
        # Add current request
        request_data['requests'].append(current_time)
        request_data['count'] = len(request_data['requests'])
        
        # Update cache
        try:
            cache.set(cache_key, request_data, self.free_user_window)
        except Exception:
            pass
        
        return True
    
    def rate_limit_exceeded_response(self, user_id, limit):
        """
        Return response when rate limit is exceeded
        """
        cache_key = f"rate_limit_{user_id}"
        try:
            request_data = cache.get(cache_key, {})
        except Exception:
            # Fail-open if cache backend is unavailable
            request_data = {}
        
        # Calculate when the oldest request will expire
        if request_data and request_data.get('requests'):
            oldest_request = min(request_data['requests'])
            retry_after = int(oldest_request + self.free_user_window - time.time())
            retry_after = max(retry_after, 1)  # At least 1 second
        else:
            retry_after = 60  # Default to 60 seconds
        
        response = JsonResponse({
            'error': 'Rate limit exceeded',
            'message': f'You have exceeded the rate limit of {limit} requests per hour.',
            'retry_after': retry_after,
            'limit': limit,
            'window': self.free_user_window,
            'upgrade_message': 'Upgrade to a premium account for higher limits or unlimited access.'
        }, status=429)
        
        response['Retry-After'] = str(retry_after)
        response['X-RateLimit-Limit'] = str(limit)
        response['X-RateLimit-Remaining'] = '0'
        response['X-RateLimit-Reset'] = str(int(time.time() + retry_after))
        
        return response

    def monthly_limit_exceeded_response(self, limit, used):
        """
        Return response when monthly quota is exceeded
        """
        remaining = max(0, int(limit) - int(used))
        response = JsonResponse({
            'error': 'Monthly quota exceeded',
            'message': f'You have reached your monthly limit of {limit} API calls.',
            'period': 'month',
            'limit': int(limit),
            'used': int(used),
            'remaining': remaining,
            'upgrade_message': 'Upgrade your plan for a higher monthly quota or unlimited access.'
        }, status=429)
        # Provide generic headers for clients
        response['X-RateLimit-Period'] = 'month'
        response['X-RateLimit-Limit'] = str(limit)
        response['X-RateLimit-Remaining'] = str(remaining)
        return response

    def _increment_monthly_usage(self, request):
        """
        Increment daily and monthly usage counters for authenticated user.
        Only counts requests to rate-limited endpoints.
        """
        if not getattr(getattr(request, 'user', None), 'is_authenticated', False):
            return
        if not self.should_rate_limit(request):
            return
        today = timezone.now().date()
        stats, _ = UsageStats.objects.get_or_create(user=request.user, date=today)
        stats.api_calls = (stats.api_calls or 0) + 1
        stats.requests = (stats.requests or 0) + 1
        stats.save()


class APIKeyAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to handle API key authentication for backend services
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.api_key = getattr(settings, 'WORDPRESS_API_KEY', '')
    
    def __call__(self, request):
        # Check for API key in headers
        provided_api_key = request.META.get('HTTP_X_API_KEY', '')
        
        if provided_api_key and provided_api_key == self.api_key:
            # Mark request as authenticated via API key
            request.api_key_authenticated = True
            logger.debug(f"API key authentication successful for {request.path}")
        else:
            request.api_key_authenticated = False
        
        return self.get_response(request)