from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User
from .models import UserProfile, APICallLog
import time
import json


class PlanLimitMiddleware:
    """Middleware to enforce plan limits and track API usage"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Define API call counts for different endpoint types
        self.endpoint_call_counts = {
            '/api/stocks/': ('stocks_list', 5),
            '/api/stock/': ('stock_detail', 1),
            '/api/search/': ('stock_detail', 1),
            '/api/trending/': ('stock_detail', 1),
            '/api/filter/': ('screener_run', 2),
            '/api/alerts/create/': ('alert_create', 2),
            '/api/market-stats/': ('market_data', 2),
            '/api/watchlist/add/': ('watchlist_create', 2),
            '/api/portfolio/add/': ('other', 1),
            '/api/screeners/': ('screener_run', 2),
        }
    
    def __call__(self, request):
        # Start timing the request
        start_time = time.time()
        
        # Process the request
        response = self.get_response(request)
        
        # Only track API endpoints
        if request.path.startswith('/api/') and response.status_code < 500:
            self.track_api_call(request, response, start_time)
        
        return response
    
    def track_api_call(self, request, response, start_time):
        """Track API call and enforce limits"""
        # Skip certain endpoints that shouldn't count towards limits
        skip_endpoints = ['/api/health/', '/api/auth/csrf/', '/api/endpoint-status/']
        if any(request.path.startswith(endpoint) for endpoint in skip_endpoints):
            return
        
        # Determine endpoint type and call count
        endpoint_type, call_count = self.get_endpoint_info(request.path)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Track for authenticated users
        user = request.user if request.user.is_authenticated else None
        
        if user:
            # Get or create user profile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'plan_type': 'free',
                    'api_calls_limit': 30,
                    'screeners_limit': 1,
                    'alerts_limit': 0,
                    'watchlists_limit': 1,
                    'portfolios_limit': 1,
                }
            )
            
            # Check if user can make this API call (before incrementing)
            if not profile.can_make_api_call():
                # User has exceeded their limit
                limits = profile.get_plan_limits()
                return JsonResponse({
                    'error': 'API limit exceeded',
                    'message': f'You have reached your monthly limit of {limits["api_calls"]} API calls. Please upgrade your plan to continue.',
                    'current_plan': profile.plan_type,
                    'calls_used': profile.api_calls_used,
                    'calls_limit': limits['api_calls'],
                    'upgrade_url': '/pricing'
                }, status=429)
            
            # Reset monthly usage if needed (first day of month)
            now = timezone.now()
            if (not profile.usage_reset_date or 
                profile.usage_reset_date.month != now.month or 
                profile.usage_reset_date.year != now.year):
                profile.reset_monthly_usage()
            
            # Increment usage
            profile.increment_api_usage(call_count)
        
        # Log the API call
        APICallLog.objects.create(
            user=user,
            endpoint=request.path,
            endpoint_type=endpoint_type,
            call_count=call_count,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            request_method=request.method,
            response_status=response.status_code,
            response_time_ms=response_time_ms
        )
    
    def get_endpoint_info(self, path):
        """Determine endpoint type and call count based on path"""
        for endpoint_prefix, (endpoint_type, call_count) in self.endpoint_call_counts.items():
            if path.startswith(endpoint_prefix):
                return endpoint_type, call_count
        return 'other', 1
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PlanFeatureMiddleware:
    """Middleware to check feature access based on user plan"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Define feature requirements for different endpoints
        self.feature_requirements = {
            '/api/alerts/': ['email_alerts'],
            '/api/screeners/': ['basic_screener'],
            '/api/portfolio/': ['portfolio_tracking'],
            '/api/watchlist/': ['custom_watchlists'],
            '/api/news/': ['news_sentiment'],
        }
    
    def __call__(self, request):
        # Check feature access for authenticated users
        if request.user.is_authenticated and request.path.startswith('/api/'):
            response = self.check_feature_access(request)
            if response:
                return response
        
        return self.get_response(request)
    
    def check_feature_access(self, request):
        """Check if user has access to requested feature"""
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            # Create default profile for user
            profile = UserProfile.objects.create(
                user=request.user,
                plan_type='free'
            )
        
        # Get user's plan features
        plan_limits = profile.get_plan_limits()
        user_features = plan_limits.get('features', [])
        
        # Check if endpoint requires specific features
        for endpoint_prefix, required_features in self.feature_requirements.items():
            if request.path.startswith(endpoint_prefix):
                # Check if user has all required features
                if not all(feature in user_features for feature in required_features):
                    missing_features = [f for f in required_features if f not in user_features]
                    return JsonResponse({
                        'error': 'Feature not available',
                        'message': f'This feature requires a higher plan. Missing features: {", ".join(missing_features)}',
                        'current_plan': profile.plan_type,
                        'required_features': required_features,
                        'upgrade_url': '/pricing'
                    }, status=403)
        
        return None