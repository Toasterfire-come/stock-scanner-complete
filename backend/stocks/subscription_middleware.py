"""
Subscription Enforcement Middleware

Ensures users have active paid subscriptions before accessing premium features.
Prevents old free accounts from bypassing payment requirements.
"""

from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


# Endpoints that require active subscription (not free)
SUBSCRIPTION_REQUIRED_ENDPOINTS = [
    '/api/stocks/backtest/',
    '/api/stocks/advanced-screener/',
    '/api/stocks/ai-analysis/',
    '/api/stocks/portfolio/advanced/',
    '/api/stocks/alerts/custom/',
    '/api/stocks/value-hunter/',
]

# Endpoints that are always accessible (free tier)
FREE_TIER_ENDPOINTS = [
    '/api/auth/',
    '/api/billing/',
    '/api/stocks/list/',
    '/api/stocks/search/',
    '/api/stocks/basic-screener/',
    '/api/education/',
]


class SubscriptionEnforcementMiddleware:
    """
    Middleware to enforce subscription requirements
    
    - Checks if user has active paid subscription for premium endpoints
    - Allows free tier access to basic features
    - Handles expired subscriptions gracefully
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if this endpoint requires subscription
        if self._requires_subscription(request.path):
            # Only check authenticated users
            if request.user.is_authenticated:
                subscription_status = self._get_subscription_status(request.user)
                
                if not subscription_status['has_active_subscription']:
                    return JsonResponse({
                        'success': False,
                        'error': 'Active subscription required',
                        'error_code': 'SUBSCRIPTION_REQUIRED',
                        'message': subscription_status['message'],
                        'current_plan': subscription_status['plan'],
                        'upgrade_url': '/pricing'
                    }, status=403)
            else:
                # Unauthenticated users accessing premium features
                return JsonResponse({
                    'success': False,
                    'error': 'Authentication required',
                    'error_code': 'AUTH_REQUIRED',
                    'message': 'Please sign in to access this feature',
                    'login_url': '/signin'
                }, status=401)
        
        response = self.get_response(request)
        return response
    
    def _requires_subscription(self, path):
        """Check if the endpoint requires an active subscription"""
        # Allow free tier endpoints
        for free_endpoint in FREE_TIER_ENDPOINTS:
            if path.startswith(free_endpoint):
                return False
        
        # Check if premium endpoint
        for premium_endpoint in SUBSCRIPTION_REQUIRED_ENDPOINTS:
            if path.startswith(premium_endpoint):
                return True
        
        return False
    
    def _get_subscription_status(self, user):
        """
        Get user's subscription status
        
        Returns:
            dict with has_active_subscription, plan, message
        """
        try:
            from billing.models import Subscription
            
            subscription = Subscription.objects.get(user=user)
            
            # Check if subscription is active
            if subscription.status == 'active':
                # Check if not expired
                if subscription.current_period_end and subscription.current_period_end > timezone.now():
                    return {
                        'has_active_subscription': True,
                        'plan': subscription.plan_tier,
                        'message': 'Active subscription'
                    }
                else:
                    # Expired subscription
                    return {
                        'has_active_subscription': False,
                        'plan': subscription.plan_tier,
                        'message': 'Your subscription has expired. Please renew to continue accessing premium features.'
                    }
            elif subscription.status == 'cancelled':
                return {
                    'has_active_subscription': False,
                    'plan': subscription.plan_tier,
                    'message': 'Your subscription has been cancelled. Reactivate to access premium features.'
                }
            elif subscription.status == 'suspended':
                return {
                    'has_active_subscription': False,
                    'plan': subscription.plan_tier,
                    'message': 'Your subscription is suspended due to payment issues. Please update your payment method.'
                }
            else:
                return {
                    'has_active_subscription': False,
                    'plan': subscription.plan_tier,
                    'message': 'No active subscription found. Please subscribe to access premium features.'
                }
        
        except Subscription.DoesNotExist:
            # No subscription = free tier
            return {
                'has_active_subscription': False,
                'plan': 'free',
                'message': 'Subscribe to access premium features and unlock unlimited potential.'
            }
        except Exception as e:
            logger.exception(f\"Error checking subscription status: {e}\")
            # Fail open in case of errors (don't block users)
            return {
                'has_active_subscription': True,
                'plan': 'unknown',
                'message': 'Unable to verify subscription status'
            }
