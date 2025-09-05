"""
Usage Tracking and Platform Stats API Views
Handles API usage monitoring and platform statistics
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Count, Sum
from datetime import datetime, timedelta
import logging

from .models import UserProfile, UsageStats, Stock
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

@api_view(['GET'])
def usage_api(request):
    """
    Get user's API usage statistics
    URL: /api/usage/
    Headers: X-User-ID, X-User-Plan (optional fallback)
    """
    try:
        # Get user from authentication or headers
        user = getattr(request, 'user', None)
        user_id = request.META.get('HTTP_X_USER_ID')
        user_plan = request.META.get('HTTP_X_USER_PLAN', 'free')
        
        if user and user.is_authenticated:
            # Use authenticated user
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'plan': 'free', 'is_premium': False}
            )
        elif user_id:
            # Try to get user by ID from header
            try:
                user = User.objects.get(id=user_id)
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'plan': user_plan, 'is_premium': user_plan != 'free'}
                )
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # Return anonymous usage info
            return Response({
                'success': True,
                'usage': {
                    'plan': 'free',
                    'monthly_used': 0,
                    'monthly_limit': 15,
                    'daily_used': 0,
                    'daily_limit': 15
                },
                'rate_limits': {
                    'requests_this_minute': 0,
                    'requests_this_hour': 0,
                    'requests_this_day': 0,
                    'rate_limited': False
                }
            })
        
        # Get plan limits
        limits = profile.get_plan_limits()
        
        # Check rate limiting status
        now = timezone.now()
        one_minute_ago = now - timedelta(minutes=1)
        one_hour_ago = now - timedelta(hours=1)
        today = now.date()
        
        # Get recent usage stats for rate limiting
        recent_usage = UsageStats.objects.filter(
            user=user,
            date=today
        ).aggregate(
            total_today=Sum('api_calls')
        )
        
        # Simple rate limiting check (can be enhanced with Redis for real-time tracking)
        requests_this_minute = 0  # Would need Redis for real-time tracking
        requests_this_hour = min(profile.daily_api_calls, 100)  # Approximate
        requests_this_day = profile.daily_api_calls
        
        # Determine if rate limited
        rate_limited = not profile.can_make_api_call()
        
        return Response({
            'success': True,
            'usage': {
                'plan': profile.plan,
                'monthly_used': profile.monthly_api_calls,
                'monthly_limit': limits['monthly'] if limits['monthly'] != -1 else 'unlimited',
                'daily_used': profile.daily_api_calls,
                'daily_limit': limits['daily'] if limits['daily'] != -1 else 'unlimited'
            },
            'rate_limits': {
                'requests_this_minute': requests_this_minute,
                'requests_this_hour': requests_this_hour,
                'requests_this_day': requests_this_day,
                'rate_limited': rate_limited
            },
            'subscription': {
                'active': profile.subscription_active,
                'end_date': profile.subscription_end_date.isoformat() if profile.subscription_end_date else None,
                'trial_used': profile.trial_used
            }
        })
        
    except Exception as e:
        logger.error(f"Usage API error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Failed to get usage information'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def platform_stats_api(request):
    """
    Get platform statistics
    URL: /api/platform-stats/
    """
    try:
        # Get stock statistics
        nyse_stocks = Stock.objects.filter(exchange__iexact='NYSE').count()
        nasdaq_stocks = Stock.objects.filter(exchange__iexact='NASDAQ').count()
        total_stocks = Stock.objects.count()
        
        # Calculate scanner combinations (indicators * stocks)
        total_indicators = 14  # As mentioned in requirements
        scanner_combinations = total_stocks * total_indicators if total_stocks > 0 else 1234
        
        # Get recent updates
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        recent_updates = Stock.objects.filter(
            last_updated__gte=twenty_four_hours_ago
        ).count()
        
        # Get user statistics
        total_users = User.objects.count()
        premium_users = UserProfile.objects.filter(is_premium=True).count()
        
        # Get usage statistics
        today = timezone.now().date()
        todays_api_calls = UsageStats.objects.filter(date=today).aggregate(
            total_calls=Sum('api_calls')
        )['total_calls'] or 0
        
        return Response({
            'success': True,
            'nyse_stocks': nyse_stocks,
            'nasdaq_stocks': nasdaq_stocks,
            'total_stocks': total_stocks,
            'total_indicators': total_indicators,
            'scanner_combinations': scanner_combinations,
            'platform_stats': {
                'total_users': total_users,
                'premium_users': premium_users,
                'recent_stock_updates': recent_updates,
                'api_calls_today': todays_api_calls
            },
            'market_stats': {
                'exchanges_supported': ['NYSE', 'NASDAQ'],
                'data_sources': ['yfinance', 'real-time feeds'],
                'update_frequency': 'Real-time'
            },
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Platform stats error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Failed to get platform statistics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def track_usage_api(request):
    """
    Internal endpoint to track API usage
    URL: /api/usage/track/
    """
    try:
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return Response({
                'success': False,
                'error': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        endpoint = request.data.get('endpoint', 'unknown')
        
        # Get or create usage stats for today
        today = timezone.now().date()
        usage_stat, created = UsageStats.objects.get_or_create(
            user=user,
            date=today,
            endpoint=endpoint,
            defaults={'api_calls': 0}
        )
        
        # Increment usage
        usage_stat.api_calls += 1
        usage_stat.save()
        
        # Update user profile usage
        profile, profile_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'plan': 'free', 'is_premium': False}
        )
        
        profile.increment_api_usage()
        
        return Response({
            'success': True,
            'message': 'Usage tracked',
            'current_usage': {
                'daily': profile.daily_api_calls,
                'monthly': profile.monthly_api_calls,
                'endpoint_today': usage_stat.api_calls
            }
        })
        
    except Exception as e:
        logger.error(f"Track usage error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Failed to track usage'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def user_usage_history_api(request):
    """
    Get detailed usage history for user
    URL: /api/usage/history/
    """
    try:
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return Response({
                'success': False,
                'error': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get usage history for last 30 days
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        usage_history = UsageStats.objects.filter(
            user=user,
            date__gte=thirty_days_ago
        ).order_by('-date', 'endpoint')
        
        # Group by date
        history_by_date = {}
        for usage in usage_history:
            date_str = usage.date.isoformat()
            if date_str not in history_by_date:
                history_by_date[date_str] = {
                    'date': date_str,
                    'total_calls': 0,
                    'endpoints': {}
                }
            
            history_by_date[date_str]['endpoints'][usage.endpoint] = usage.api_calls
            history_by_date[date_str]['total_calls'] += usage.api_calls
        
        # Convert to list sorted by date
        history_list = sorted(history_by_date.values(), key=lambda x: x['date'], reverse=True)
        
        return Response({
            'success': True,
            'data': {
                'usage_history': history_list,
                'total_days': len(history_list),
                'date_range': {
                    'from': thirty_days_ago.isoformat(),
                    'to': timezone.now().date().isoformat()
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Usage history error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Failed to get usage history'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)