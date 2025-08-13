"""
User Management and Settings API for Stock Scanner
Handles user profiles, settings, subscription management, and user preferences
"""

import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta

logger = logging.getLogger(__name__)
User = get_user_model()

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_settings(request):
    """Get or update user settings"""
    try:
        user = request.user
        
        # Ensure user has settings
        if not hasattr(user, 'settings'):
            from .models import UserSettings
            UserSettings.objects.create(user=user)
        
        settings_obj = user.settings
        
        if request.method == 'GET':
            return Response({
                'status': 'success',
                'settings': {
                    'enable_virtual_scrolling': settings_obj.enable_virtual_scrolling,
                    'enable_fuzzy_search': settings_obj.enable_fuzzy_search,
                    'enable_real_time_charts': settings_obj.enable_real_time_charts,
                    'chart_theme': settings_obj.chart_theme,
                    'items_per_page': settings_obj.items_per_page,
                    'default_watchlist_view': settings_obj.default_watchlist_view,
                    'auto_refresh_interval': settings_obj.auto_refresh_interval,
                    'enable_notifications': settings_obj.enable_notifications,
                    'share_usage_analytics': settings_obj.share_usage_analytics,
                    'enable_performance_tracking': settings_obj.enable_performance_tracking,
                }
            })
        
        elif request.method == 'PUT':
            # Update settings
            data = request.data
            
            # Validate and update each setting
            if 'enable_virtual_scrolling' in data:
                settings_obj.enable_virtual_scrolling = bool(data['enable_virtual_scrolling'])
            
            if 'enable_fuzzy_search' in data:
                settings_obj.enable_fuzzy_search = bool(data['enable_fuzzy_search'])
            
            if 'enable_real_time_charts' in data:
                settings_obj.enable_real_time_charts = bool(data['enable_real_time_charts'])
            
            if 'chart_theme' in data and data['chart_theme'] in ['light', 'dark']:
                settings_obj.chart_theme = data['chart_theme']
            
            if 'items_per_page' in data:
                items_per_page = int(data['items_per_page'])
                if 10 <= items_per_page <= 200:
                    settings_obj.items_per_page = items_per_page
            
            if 'default_watchlist_view' in data and data['default_watchlist_view'] in ['grid', 'list', 'chart']:
                settings_obj.default_watchlist_view = data['default_watchlist_view']
            
            if 'auto_refresh_interval' in data:
                interval = int(data['auto_refresh_interval'])
                if 5 <= interval <= 300:  # 5 seconds to 5 minutes
                    settings_obj.auto_refresh_interval = interval
            
            if 'enable_notifications' in data:
                settings_obj.enable_notifications = bool(data['enable_notifications'])
            
            if 'share_usage_analytics' in data:
                settings_obj.share_usage_analytics = bool(data['share_usage_analytics'])
            
            if 'enable_performance_tracking' in data:
                settings_obj.enable_performance_tracking = bool(data['enable_performance_tracking'])
            
            settings_obj.save()
            
            return Response({
                'status': 'success',
                'message': 'Settings updated successfully'
            })
    
    except Exception as e:
        logger.error(f"Error handling user settings: {e}")
        return Response({'error': 'Internal server error'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get or update user profile"""
    try:
        user = request.user
        
        # Ensure user has profile
        if not hasattr(user, 'profile'):
            from .models import UserProfile
            UserProfile.objects.create(user=user)
        
        profile = user.profile
        
        if request.method == 'GET':
            return Response({
                'status': 'success',
                'profile': {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'tier': profile.tier,
                    'subscription_active': profile.is_subscription_active,
                    'subscription_start': profile.subscription_start,
                    'subscription_end': profile.subscription_end,
                    'created_at': profile.created_at,
                    'enable_frontend_optimization': profile.enable_frontend_optimization,
                    'enable_client_side_charts': profile.enable_client_side_charts,
                    'enable_progressive_loading': profile.enable_progressive_loading,
                    'max_cache_size_mb': profile.max_cache_size_mb,
                                         'api_calls_this_month': profile.api_calls_this_month,
                    'rate_limits': profile.get_rate_limits()
                }
            })
        
        elif request.method == 'PUT':
            # Update profile and user data
            data = request.data
            
            # Update User model fields
            if 'first_name' in data:
                user.first_name = data['first_name']
            
            if 'last_name' in data:
                user.last_name = data['last_name']
            
            if 'email' in data:
                # Check if email is already taken
                if User.objects.filter(email=data['email']).exclude(id=user.id).exists():
                    return Response({'error': 'Email already taken'}, 
                                  status=status.HTTP_400_BAD_REQUEST)
                user.email = data['email']
            
            user.save()
            
            # Update Profile model fields
            if 'enable_frontend_optimization' in data:
                profile.enable_frontend_optimization = bool(data['enable_frontend_optimization'])
            
            if 'enable_client_side_charts' in data:
                profile.enable_client_side_charts = bool(data['enable_client_side_charts'])
            
            if 'enable_progressive_loading' in data:
                profile.enable_progressive_loading = bool(data['enable_progressive_loading'])
            
            if 'max_cache_size_mb' in data:
                cache_size = int(data['max_cache_size_mb'])
                if 10 <= cache_size <= 500:  # 10MB to 500MB
                    profile.max_cache_size_mb = cache_size
            
            profile.save()
            
            return Response({
                'status': 'success',
                'message': 'Profile updated successfully'
            })
    
    except Exception as e:
        logger.error(f"Error handling user profile: {e}")
        return Response({'error': 'Internal server error'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_usage_stats(request):
    """Get detailed API usage statistics for the user"""
    try:
        user = request.user
        
        # Get usage from the last 30 days
        from .models import UserAPIUsage
        from datetime import datetime, timedelta
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Get usage statistics
        usage_data = UserAPIUsage.objects.filter(
            user=user,
            timestamp__gte=thirty_days_ago
        ).order_by('-timestamp')
        
        # Aggregate data
        total_calls = usage_data.count()
        successful_calls = usage_data.filter(status_code__lt=400).count()
        frontend_optimized_calls = usage_data.filter(frontend_optimized=True).count()
        
        # Average response time
        avg_response_time = 0
        if total_calls > 0:
            total_time = sum(item.response_time_ms for item in usage_data)
            avg_response_time = total_time / total_calls
        
        # Group by endpoint
        endpoint_stats = {}
        for usage in usage_data:
            endpoint = usage.endpoint
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {
                    'count': 0,
                    'avg_response_time': 0,
                    'total_time': 0,
                    'frontend_optimized': 0,
                    'errors': 0
                }
            
            endpoint_stats[endpoint]['count'] += 1
            endpoint_stats[endpoint]['total_time'] += usage.response_time_ms
            
            if usage.frontend_optimized:
                endpoint_stats[endpoint]['frontend_optimized'] += 1
            
            if usage.status_code >= 400:
                endpoint_stats[endpoint]['errors'] += 1
        
        # Calculate averages
        for endpoint, stats in endpoint_stats.items():
            if stats['count'] > 0:
                stats['avg_response_time'] = stats['total_time'] / stats['count']
            del stats['total_time']  # Remove total_time from response
        
        # Get rate limits
        profile = getattr(user, 'profile', None)
        rate_limits = profile.get_rate_limits() if profile else {}
        
        return Response({
            'status': 'success',
            'usage_stats': {
                'period_days': 30,
                'total_calls': total_calls,
                'successful_calls': successful_calls,
                'error_rate': (total_calls - successful_calls) / total_calls * 100 if total_calls > 0 else 0,
                'frontend_optimized_calls': frontend_optimized_calls,
                'optimization_rate': frontend_optimized_calls / total_calls * 100 if total_calls > 0 else 0,
                'avg_response_time_ms': avg_response_time,
                'endpoints': endpoint_stats,
                                 'rate_limits': rate_limits,
                 'current_usage': {
                     'this_month': profile.api_calls_this_month if profile else 0
                 }
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting API usage stats: {e}")
        return Response({'error': 'Internal server error'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscription_management(request):
    """Get comprehensive subscription management information"""
    try:
        user = request.user
        profile = getattr(user, 'profile', None)
        
        if not profile:
            return Response({
                'status': 'success',
                'subscription': {
                    'tier': 'free',
                    'active': False,
                    'can_upgrade': True,
                    'available_upgrades': ['basic', 'pro', 'enterprise']
                }
            })
        
        # Get recent transactions
        from .models import PaymentTransaction, PaymentPlan
        
        recent_transactions = PaymentTransaction.objects.filter(
            user=user
        ).order_by('-created_at')[:10]
        
        transaction_data = []
        for transaction in recent_transactions:
            transaction_data.append({
                'id': transaction.id,
                'plan_name': transaction.plan.name if transaction.plan else 'Recurring Payment',
                'amount': float(transaction.amount),
                'currency': transaction.currency,
                'status': transaction.status,
                'billing_cycle': transaction.billing_cycle,
                'created_at': transaction.created_at,
                'paypal_transaction_id': transaction.paypal_transaction_id
            })
        
        # Get available upgrade options
        available_plans = PaymentPlan.objects.filter(is_active=True)
        current_tier_index = ['free', 'basic', 'pro', 'enterprise'].index(profile.tier)
        
        upgrade_options = []
        for plan in available_plans:
            plan_tier_index = ['free', 'basic', 'pro', 'enterprise'].index(plan.tier)
            if plan_tier_index > current_tier_index:
                upgrade_options.append({
                    'id': plan.id,
                    'name': plan.name,
                    'tier': plan.tier,
                    'price_monthly': float(plan.price_monthly),
                    'price_yearly': float(plan.price_yearly),
                    'features': plan.features
                })
        
        # Calculate subscription value and savings
        subscription_value = {
            'monthly_value': 0,
            'yearly_savings': 0,
            'features_unlocked': []
        }
        
        if profile.tier != 'free':
            try:
                current_plan = PaymentPlan.objects.get(tier=profile.tier, is_active=True)
                subscription_value['monthly_value'] = float(current_plan.price_monthly)
                subscription_value['yearly_savings'] = float(current_plan.price_monthly * 12 - current_plan.price_yearly)
                subscription_value['features_unlocked'] = list(current_plan.features.keys()) if current_plan.features else []
            except PaymentPlan.DoesNotExist:
                pass
        
        return Response({
            'status': 'success',
            'subscription': {
                'tier': profile.tier,
                'active': profile.is_subscription_active,
                'start_date': profile.subscription_start,
                'end_date': profile.subscription_end,
                'paypal_subscription_id': profile.paypal_subscription_id,
                'auto_renewal': profile.subscription_active,
                'days_remaining': (profile.subscription_end - timezone.now()).days if profile.subscription_end else 0,
                'subscription_value': subscription_value,
                'upgrade_options': upgrade_options,
                'recent_transactions': transaction_data,
                'can_cancel': profile.subscription_active and profile.paypal_subscription_id,
                'cancellation_policy': 'You can cancel anytime. Access continues until the end of your billing period.'
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting subscription management: {e}")
        return Response({'error': 'Internal server error'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_api_usage(request):
    """Reset API usage counters (admin function or for testing)"""
    try:
        user = request.user
        profile = getattr(user, 'profile', None)
        
        if not profile:
            return Response({'error': 'User profile not found'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Only allow this for certain conditions (e.g., admin, or monthly reset)
        reset_type = request.data.get('type', 'daily')
        
        if reset_type == 'daily':
            profile.api_calls_today = 0
        elif reset_type == 'monthly':
            profile.api_calls_this_month = 0
        elif reset_type == 'all':
            profile.api_calls_today = 0
            profile.api_calls_this_month = 0
        
        profile.save()
        
        return Response({
            'status': 'success',
            'message': f'API usage counters reset ({reset_type})',
            'current_usage': {
                'today': profile.api_calls_today,
                'this_month': profile.api_calls_this_month
            }
        })
    
    except Exception as e:
        logger.error(f"Error resetting API usage: {e}")
        return Response({'error': 'Internal server error'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def frontend_optimization_config(request):
    """Get personalized frontend optimization configuration based on user settings and tier"""
    try:
        user = request.user
        profile = getattr(user, 'profile', None)
        settings_obj = getattr(user, 'settings', None)
        
        # Default configuration
        config = {
            'enabled': True,
            'features': {
                'virtual_scrolling': True,
                'fuzzy_search': True,
                'real_time_charts': False,
                'progressive_loading': True,
                'client_side_charts': False,
                'advanced_aggregation': False,
                'unlimited_watchlist': False
            },
            'limits': {
                'cache_size_mb': 50,
                'items_per_page': 50,
                'max_watchlist_items': 10,
                'chart_data_points': 100
            },
            'performance': {
                'debounce_ms': 300,
                'throttle_ms': 16,
                'lazy_loading_threshold': 0.1,
                'preload_pages': 1
            }
        }
        
        # Apply user settings
        if settings_obj:
            config['features']['virtual_scrolling'] = settings_obj.enable_virtual_scrolling
            config['features']['fuzzy_search'] = settings_obj.enable_fuzzy_search
            config['features']['real_time_charts'] = settings_obj.enable_real_time_charts
            config['limits']['items_per_page'] = settings_obj.items_per_page
        
        # Apply profile settings and tier-based features
        if profile:
            config['enabled'] = profile.enable_frontend_optimization
            config['features']['client_side_charts'] = profile.enable_client_side_charts
            config['features']['progressive_loading'] = profile.enable_progressive_loading
            config['limits']['cache_size_mb'] = profile.max_cache_size_mb
            
            # Tier-based feature unlocking
            rate_limits = profile.get_rate_limits()
            config['limits']['max_watchlist_items'] = rate_limits.get('max_watchlist_items', 10)
            config['features']['real_time_charts'] = rate_limits.get('real_time_data', False)
            config['features']['advanced_charts'] = rate_limits.get('advanced_charts', False)
            
            # Enhanced features for higher tiers
            if profile.tier in ['pro', 'enterprise']:
                config['features']['advanced_aggregation'] = True
                config['limits']['chart_data_points'] = 1000
                config['performance']['preload_pages'] = 3
            
            if profile.tier == 'enterprise':
                config['features']['unlimited_watchlist'] = True
                config['limits']['cache_size_mb'] = min(profile.max_cache_size_mb, 200)
                config['performance']['debounce_ms'] = 100  # Faster for enterprise
        
        return Response({
            'status': 'success',
            'config': config,
            'user_tier': profile.tier if profile else 'free',
            'timestamp': timezone.now()
        })
    
    except Exception as e:
        logger.error(f"Error getting frontend optimization config: {e}")
        return Response({'error': 'Internal server error'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_user_data(request):
    """Export user data for GDPR compliance"""
    try:
        user = request.user
        
        # Collect all user data
        user_data = {
            'user_info': {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined,
                'last_login': user.last_login
            },
            'profile': {},
            'settings': {},
            'transactions': [],
            'api_usage': [],
            'watchlist': []
        }
        
        # Get profile data
        if hasattr(user, 'profile'):
            profile = user.profile
            user_data['profile'] = {
                'tier': profile.tier,
                'subscription_active': profile.subscription_active,
                'subscription_start': profile.subscription_start,
                'subscription_end': profile.subscription_end,
                'created_at': profile.created_at,
                'updated_at': profile.updated_at,
                'api_calls_today': profile.api_calls_today,
                'api_calls_this_month': profile.api_calls_this_month
            }
        
        # Get settings data
        if hasattr(user, 'settings'):
            settings_obj = user.settings
            user_data['settings'] = {
                'enable_virtual_scrolling': settings_obj.enable_virtual_scrolling,
                'enable_fuzzy_search': settings_obj.enable_fuzzy_search,
                'enable_real_time_charts': settings_obj.enable_real_time_charts,
                'chart_theme': settings_obj.chart_theme,
                'items_per_page': settings_obj.items_per_page,
                'default_watchlist_view': settings_obj.default_watchlist_view,
                'auto_refresh_interval': settings_obj.auto_refresh_interval,
                'enable_notifications': settings_obj.enable_notifications
            }
        
        # Get transaction history
        from .models import PaymentTransaction
        transactions = PaymentTransaction.objects.filter(user=user)
        for transaction in transactions:
            user_data['transactions'].append({
                'id': transaction.id,
                'amount': float(transaction.amount),
                'currency': transaction.currency,
                'status': transaction.status,
                'billing_cycle': transaction.billing_cycle,
                'created_at': transaction.created_at
            })
        
        # Get API usage (last 90 days)
        from .models import UserAPIUsage
        from datetime import timedelta
        
        ninety_days_ago = timezone.now() - timedelta(days=90)
        api_usage = UserAPIUsage.objects.filter(
            user=user,
            timestamp__gte=ninety_days_ago
        )
        
        for usage in api_usage:
            user_data['api_usage'].append({
                'endpoint': usage.endpoint,
                'method': usage.method,
                'timestamp': usage.timestamp,
                'response_time_ms': usage.response_time_ms,
                'status_code': usage.status_code
            })
        
        # Get watchlist data if available
        try:
            from .models import UserWatchlist
            watchlists = UserWatchlist.objects.filter(user=user)
            for watchlist in watchlists:
                user_data['watchlist'].append({
                    'stock_symbol': watchlist.stock.ticker,
                    'added_date': watchlist.added_date,
                    'notes': getattr(watchlist, 'notes', '')
                })
        except:
            pass  # Watchlist model might not exist yet
        
        return Response({
            'status': 'success',
            'data': user_data,
            'export_date': timezone.now(),
            'format': 'json'
        })
    
    except Exception as e:
        logger.error(f"Error exporting user data: {e}")
        return Response({'error': 'Internal server error'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)