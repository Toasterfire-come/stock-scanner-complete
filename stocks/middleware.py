"""
Authentication Middleware for API Token handling
"""

from django.contrib.auth.models import AnonymousUser, User
from django.utils import timezone
from .models import APIToken, UserProfile
import logging

logger = logging.getLogger(__name__)

class APITokenAuthenticationMiddleware:
    """
    Middleware to handle API token authentication
    Looks for Authorization: Bearer <token> or X-API-Token header
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request
        user = self.get_user_from_token(request)
        if user:
            request.user = user
        
        response = self.get_response(request)
        return response

    def get_user_from_token(self, request):
        """Extract user from API token"""
        token = None
        
        # Try Authorization header first
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        # Try X-API-Token header
        if not token:
            token = request.META.get('HTTP_X_API_TOKEN', '')
        
        # Try query parameter (less secure, but convenient for testing)
        if not token:
            token = request.GET.get('api_token', '')
        
        if not token:
            return None
        
        try:
            api_token = APIToken.objects.select_related('user').get(
                token=token,
                is_active=True
            )
            
            # Update last used timestamp
            api_token.last_used = timezone.now()
            api_token.save(update_fields=['last_used'])
            
            return api_token.user
            
        except APIToken.DoesNotExist:
            logger.warning(f"Invalid API token attempted: {token[:8]}...")
            return None
        except Exception as e:
            logger.error(f"Token authentication error: {e}")
            return None

class UsageTrackingMiddleware:
    """
    Middleware to track API usage for rate limiting
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip non-API requests
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        # Skip certain endpoints from usage tracking
        skip_endpoints = [
            '/api/health/',
            '/api/auth/register/',
            '/api/auth/login/',
            '/api/platform-stats/',
            '/api/usage/',
        ]
        
        if any(request.path.startswith(endpoint) for endpoint in skip_endpoints):
            return self.get_response(request)
        
        # Track usage for authenticated users
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            try:
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'plan': 'free', 'is_premium': False}
                )
                
                # Check if user can make API call
                if not profile.can_make_api_call():
                    from django.http import JsonResponse
                    return JsonResponse({
                        'success': False,
                        'error': 'API usage limit exceeded',
                        'current_usage': {
                            'daily': profile.daily_api_calls,
                            'monthly': profile.monthly_api_calls,
                            'limits': profile.get_plan_limits()
                        }
                    }, status=429)
                
                # Increment usage
                profile.increment_api_usage()
                
            except Exception as e:
                logger.error(f"Usage tracking middleware error: {e}")
        
        return self.get_response(request)