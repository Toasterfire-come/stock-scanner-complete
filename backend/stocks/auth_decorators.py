"""
Authentication decorators and utilities for API endpoints
"""
from functools import wraps
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework import status


def require_authentication(view_func):
    """
    Decorator to require authentication on API views.
    
    Usage:
        @api_view(['GET'])
        @require_authentication
        def my_protected_view(request):
            return Response({'data': 'Protected'})
    """
    @wraps(view_func)
    @permission_classes([IsAuthenticated])
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)
    return wrapped_view


def allow_public_with_rate_limit(view_func):
    """
    Decorator for public endpoints with rate limiting.
    
    Usage:
        @api_view(['GET'])
        @allow_public_with_rate_limit
        def public_view(request):
            return Response({'data': 'Public'})
    """
    from rest_framework.throttling import AnonRateThrottle
    from rest_framework.decorators import throttle_classes
    
    @wraps(view_func)
    @permission_classes([AllowAny])
    @throttle_classes([AnonRateThrottle])
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)
    return wrapped_view


def get_client_ip(request):
    """
    Get client IP address from request.
    
    Args:
        request: Django request object
        
    Returns:
        Client IP address as string
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def check_user_permission(user, required_plan: str = None):
    """
    Check if user has required plan level.
    
    Args:
        user: User object
        required_plan: Required plan tier ('bronze', 'silver', 'gold')
        
    Returns:
        Boolean indicating if user has permission
        
    Example:
        if not check_user_permission(request.user, 'silver'):
            return Response({'error': 'Upgrade required'}, status=403)
    """
    if not user.is_authenticated:
        return False
    
    if required_plan is None:
        return True
    
    # Get user's plan
    try:
        from billing.models import Subscription
        subscription = Subscription.objects.get(user=user, status='active')
        
        # Plan hierarchy
        plan_levels = {
            'free': 0,
            'bronze': 1,
            'silver': 2,
            'gold': 3,
            'enterprise': 4,
        }
        
        user_level = plan_levels.get(subscription.plan_tier, 0)
        required_level = plan_levels.get(required_plan, 0)
        
        return user_level >= required_level
        
    except Exception:
        return False


def require_plan(required_plan: str):
    """
    Decorator to require specific plan tier.
    
    Args:
        required_plan: Plan tier required ('bronze', 'silver', 'gold')
        
    Usage:
        @api_view(['GET'])
        @require_plan('silver')
        def premium_view(request):
            return Response({'data': 'Premium content'})
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not check_user_permission(request.user, required_plan):
                return Response({
                    'error': f'This feature requires {required_plan.title()} plan or higher',
                    'required_plan': required_plan,
                    'upgrade_url': '/pricing'
                }, status=status.HTTP_403_FORBIDDEN)
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
