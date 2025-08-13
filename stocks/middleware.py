"""
Stock Scanner Middleware for User Management and Frontend Optimization
Handles authentication, rate limiting, auto-optimization, and usage tracking
"""

import time
import json
import logging
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class UserTierRateLimitMiddleware(MiddlewareMixin):
    """
    Middleware to enforce rate limiting based on user subscription tier
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        # Skip rate limiting for admin, static files, and health checks
        if self._should_skip_rate_limiting(request):
            return None
        
        # Only apply to API endpoints
        if not request.path.startswith('/api/'):
            return None
        
        user = request.user
        if isinstance(user, AnonymousUser):
            return self._handle_anonymous_rate_limit(request)
        
        # Get or create user profile
        try:
            profile = user.profile
        except AttributeError:
            from .models import UserProfile, UserSettings
            profile = UserProfile.objects.create(user=user)
            UserSettings.objects.create(user=user)
        
        # Check rate limits
        can_proceed, message = profile.can_make_api_call()
        if not can_proceed:
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': message,
                'tier': profile.tier,
                'limits': profile.get_rate_limits(),
                'upgrade_url': '/premium-plans/',
                'calls_used': profile.api_calls_this_month,
                'calls_limit': profile.get_rate_limits().get('api_calls_per_month', 15)
            }, status=429)
        
        # Store user info for later processing
        request.user_profile = profile
        return None
    
    def process_response(self, request, response):
        # Track API usage if this was an API call
        if (hasattr(request, 'user_profile') and 
            request.path.startswith('/api/') and 
            response.status_code < 500):
            
            try:
                request.user_profile.increment_api_usage()
                self._track_detailed_usage(request, response)
            except Exception as e:
                logger.error(f"Error tracking API usage: {e}")
        
        return response
    
    def _should_skip_rate_limiting(self, request):
        """Check if request should skip rate limiting"""
        skip_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/health/',
            '/api/health/',
            '/favicon.ico'
        ]
        return any(request.path.startswith(path) for path in skip_paths)
    
    def _handle_anonymous_rate_limit(self, request):
        """Handle rate limiting for anonymous users"""
        ip_address = self._get_client_ip(request)
        cache_key = f"anon_rate_limit_{ip_address}"
        
        current_count = cache.get(cache_key, 0)
        max_anonymous_requests = 5  # per month for anonymous users
        
        if current_count >= max_anonymous_requests:
            return JsonResponse({
                'error': 'Anonymous rate limit exceeded',
                'message': 'Please sign up for a free account to get higher rate limits',
                'max_requests': max_anonymous_requests,
                'signup_url': '/signup/'
            }, status=429)
        
        # Increment counter (30 day TTL for monthly limit)
        cache.set(cache_key, current_count + 1, 2592000)  # 30 days
        return None
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _track_detailed_usage(self, request, response):
        """Track detailed API usage for analytics"""
        try:
            from .models import UserAPIUsage
            
            # Calculate response time (if available)
            response_time_ms = getattr(request, '_start_time', None)
            if response_time_ms:
                response_time_ms = int((time.time() - response_time_ms) * 1000)
            else:
                response_time_ms = 0
            
            # Check if this was a frontend-optimized request
            frontend_optimized = any([
                '/frontend/' in request.path,
                '/charts/' in request.path,
                '/client/' in request.path,
                request.GET.get('frontend_optimized') == 'true'
            ])
            
            # Estimate response size
            data_size_bytes = len(response.content) if hasattr(response, 'content') else 0
            
            UserAPIUsage.objects.create(
                user=request.user,
                endpoint=request.path,
                method=request.method,
                response_time_ms=response_time_ms,
                status_code=response.status_code,
                user_tier=request.user_profile.tier,
                frontend_optimized=frontend_optimized,
                data_size_bytes=data_size_bytes,
                cache_hit=getattr(response, '_cache_hit', False)
            )
        except Exception as e:
            logger.error(f"Error tracking detailed usage: {e}")

class FrontendOptimizationMiddleware(MiddlewareMixin):
    """
    Middleware to automatically apply frontend optimization based on user settings
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        # Record start time for performance tracking
        request._start_time = time.time()
        
        # Skip for non-API requests
        if not request.path.startswith('/api/'):
            return None
        
        # Auto-detect if frontend optimization should be applied
        if self._should_apply_frontend_optimization(request):
            request.META['HTTP_X_FRONTEND_OPTIMIZED'] = 'true'
            request.frontend_optimized = True
        else:
            request.frontend_optimized = False
        
        return None
    
    def process_response(self, request, response):
        # Add frontend optimization headers
        if hasattr(request, 'frontend_optimized') and request.frontend_optimized:
            response['X-Frontend-Optimized'] = 'true'
            response['X-Cache-Control'] = 'public, max-age=300'  # 5 minutes
            
            # Add CORS headers for frontend optimization
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Frontend-Optimized'
        
        # Add performance headers
        if hasattr(request, '_start_time'):
            processing_time = time.time() - request._start_time
            response['X-Processing-Time'] = f"{processing_time:.3f}s"
        
        return response
    
    def _should_apply_frontend_optimization(self, request):
        """Determine if frontend optimization should be applied"""
        # Check user preferences
        user = request.user
        if not isinstance(user, AnonymousUser):
            try:
                if hasattr(user, 'profile') and not user.profile.enable_frontend_optimization:
                    return False
            except AttributeError:
                pass
        
        # Check for explicit frontend optimization request
        if request.GET.get('frontend_optimized') == 'true':
            return True
        
        # Check for frontend optimization endpoints
        frontend_endpoints = [
            '/frontend/',
            '/charts/',
            '/client/',
            '/minimal-stocks/',
            '/chart-data/',
            '/bulk-data/'
        ]
        
        if any(endpoint in request.path for endpoint in frontend_endpoints):
            return True
        
        # Check Accept header for frontend optimization
        accept_header = request.META.get('HTTP_ACCEPT', '')
        if 'application/frontend-optimized' in accept_header:
            return True
        
        # Default to frontend optimization for modern browsers
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        modern_browsers = ['Chrome/', 'Firefox/', 'Safari/', 'Edge/']
        if any(browser in user_agent for browser in modern_browsers):
            return True
        
        return False

class UserSettingsAutoSetupMiddleware(MiddlewareMixin):
    """
    Middleware to automatically set up user profiles and settings
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        user = request.user
        
        # Skip for anonymous users
        if isinstance(user, AnonymousUser):
            return None
        
        # Ensure user has profile and settings
        self._ensure_user_setup(user)
        
        return None
    
    def _ensure_user_setup(self, user):
        """Ensure user has profile and settings configured"""
        try:
            from .models import UserProfile, UserSettings
            
            # Create profile if it doesn't exist
            if not hasattr(user, 'profile'):
                profile = UserProfile.objects.create(user=user)
                logger.info(f"Created profile for user {user.username}")
            else:
                profile = user.profile
            
            # Create settings if they don't exist
            if not hasattr(user, 'settings'):
                settings = UserSettings.objects.create(user=user)
                logger.info(f"Created settings for user {user.username}")
            
            # Auto-upgrade tier based on payment status (simplified logic)
            if profile.subscription_active and profile.tier == 'free':
                self._auto_upgrade_tier(profile)
                
        except Exception as e:
            logger.error(f"Error setting up user {user.username}: {e}")
    
    def _auto_upgrade_tier(self, profile):
        """Auto-upgrade user tier based on active subscription"""
        try:
            from .models import PaymentTransaction
            
            # Check for recent successful transactions
            recent_transaction = PaymentTransaction.objects.filter(
                user=profile.user,
                status='completed'
            ).order_by('-created_at').first()
            
            if recent_transaction:
                # Upgrade to the tier associated with their payment plan
                profile.tier = recent_transaction.plan.tier
                profile.save()
                logger.info(f"Auto-upgraded user {profile.user.username} to {profile.tier}")
                
        except Exception as e:
            logger.error(f"Error auto-upgrading tier for {profile.user.username}: {e}")

class APIResponseOptimizationMiddleware(MiddlewareMixin):
    """
    Middleware to optimize API responses based on user tier and frontend capabilities
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_response(self, request, response):
        # Only optimize API responses
        if not request.path.startswith('/api/'):
            return response
        
        # Check if response should be optimized
        if hasattr(request, 'frontend_optimized') and request.frontend_optimized:
            response = self._optimize_response(request, response)
        
        # Add compression hint
        if hasattr(response, '_content') and len(response.content) > 1024:
            response['X-Compression-Recommended'] = 'true'
        
        return response
    
    def _optimize_response(self, request, response):
        """Optimize response for frontend processing"""
        try:
            # Add optimization metadata
            if hasattr(response, 'data') and isinstance(response.data, dict):
                response.data['_optimization'] = {
                    'frontend_processing': True,
                    'cache_ttl': 300,
                    'compression': True,
                    'minimal_payload': True
                }
            
            # Add caching headers
            response['Cache-Control'] = 'public, max-age=300'
            response['X-Optimized-Response'] = 'true'
            
        except Exception as e:
            logger.error(f"Error optimizing response: {e}")
        
        return response

class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Add HSTS for HTTPS
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # CSP for API endpoints
        if request.path.startswith('/api/'):
            response['Content-Security-Policy'] = "default-src 'self'"
        
        return response

class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor and log performance metrics
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            processing_time = time.time() - request._start_time
            
            # Log slow requests
            if processing_time > 1.0:  # Slower than 1 second
                logger.warning(f"Slow request: {request.path} took {processing_time:.3f}s")
            
            # Store performance metrics in cache for monitoring
            if request.path.startswith('/api/'):
                cache_key = f"perf_metrics_{request.path.replace('/', '_')}"
                metrics = cache.get(cache_key, [])
                metrics.append(processing_time)
                
                # Keep only last 100 measurements
                if len(metrics) > 100:
                    metrics = metrics[-100:]
                
                cache.set(cache_key, metrics, 3600)  # 1 hour
        
        return response