from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Sum, Count
from .models import UserProfile, APICallLog, BillingHistory
import json
from datetime import datetime, timedelta


@login_required
@require_http_methods(["GET"])
def user_plan_info(request):
    """Get current user's plan information and usage stats"""
    try:
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'plan_type': 'free',
                'api_calls_limit': 30,
                'screeners_limit': 1,
                'alerts_limit': 0,
                'watchlists_limit': 1,
                'portfolios_limit': 1,
            }
        )
        
        # Get plan limits
        plan_limits = profile.get_plan_limits()
        
        # Calculate usage for current month
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get API usage stats
        api_usage = APICallLog.objects.filter(
            user=request.user,
            created_at__gte=month_start
        ).aggregate(
            total_calls=Sum('call_count'),
            total_requests=Count('id')
        )
        
        # Get usage by endpoint type
        usage_by_type = APICallLog.objects.filter(
            user=request.user,
            created_at__gte=month_start
        ).values('endpoint_type').annotate(
            call_count=Sum('call_count'),
            request_count=Count('id')
        ).order_by('-call_count')
        
        # Get recent API calls (last 10)
        recent_calls = APICallLog.objects.filter(
            user=request.user
        ).order_by('-created_at')[:10].values(
            'endpoint_type', 'call_count', 'created_at', 'response_status'
        )
        
        # Get user's current resources count
        resources_count = {
            'screeners': request.user.screeners.count(),
            'portfolios': request.user.portfolios.count(),
            'watchlists': request.user.watchlists.count(),
            'alerts': request.user.stockalert_set.filter(is_active=True).count(),
        }
        
        # Calculate usage percentages
        usage_percentages = {}
        for resource, count in resources_count.items():
            limit = plan_limits.get(f'{resource[:-1]}s_limit' if resource != 'alerts' else 'alerts', 0)
            if limit == -1:  # Unlimited
                usage_percentages[resource] = 0
            elif limit > 0:
                usage_percentages[resource] = min(100, (count / limit) * 100)
            else:
                usage_percentages[resource] = 100 if count > 0 else 0
        
        # API calls usage percentage
        api_calls_used = api_usage['total_calls'] or 0
        if plan_limits['api_calls'] == -1:  # Unlimited
            api_usage_percentage = 0
        else:
            api_usage_percentage = min(100, (api_calls_used / plan_limits['api_calls']) * 100)
        
        response_data = {
            'success': True,
            'user': {
                'username': request.user.username,
                'email': request.user.email,
                'is_premium': profile.is_premium,
            },
            'plan': {
                'type': profile.plan_type,
                'name': profile.plan_name,
                'features': plan_limits['features'],
                'limits': {
                    'api_calls': plan_limits['api_calls'],
                    'screeners': plan_limits['screeners'],
                    'alerts': plan_limits['alerts'],
                    'watchlists': plan_limits['watchlists'],
                    'portfolios': plan_limits.get('portfolios', 1),
                },
                'billing': {
                    'cycle': profile.billing_cycle,
                    'status': profile.subscription_status,
                    'next_billing_date': profile.next_billing_date.isoformat() if profile.next_billing_date else None,
                    'auto_renew': profile.auto_renew,
                }
            },
            'usage': {
                'current_month': now.strftime('%Y-%m'),
                'api_calls': {
                    'used': api_calls_used,
                    'limit': plan_limits['api_calls'],
                    'percentage': api_usage_percentage,
                    'unlimited': plan_limits['api_calls'] == -1
                },
                'resources': {
                    'screeners': {
                        'used': resources_count['screeners'],
                        'limit': plan_limits['screeners'],
                        'percentage': usage_percentages['screeners'],
                        'unlimited': plan_limits['screeners'] == -1
                    },
                    'portfolios': {
                        'used': resources_count['portfolios'],
                        'limit': plan_limits.get('portfolios', 1),
                        'percentage': usage_percentages['portfolios'],
                        'unlimited': plan_limits.get('portfolios', 1) == -1
                    },
                    'watchlists': {
                        'used': resources_count['watchlists'],
                        'limit': plan_limits['watchlists'],
                        'percentage': usage_percentages['watchlists'],
                        'unlimited': plan_limits['watchlists'] == -1
                    },
                    'alerts': {
                        'used': resources_count['alerts'],
                        'limit': plan_limits['alerts'],
                        'percentage': usage_percentages['alerts'],
                        'unlimited': plan_limits['alerts'] == -1
                    }
                },
                'alerts_sent': {
                    'used': profile.alerts_sent,
                    'limit': plan_limits['alerts'],
                    'unlimited': plan_limits['alerts'] == -1
                },
                'by_endpoint_type': list(usage_by_type),
                'recent_calls': [
                    {
                        **call,
                        'created_at': call['created_at'].isoformat()
                    }
                    for call in recent_calls
                ]
            },
            'recommendations': get_plan_recommendations(profile, plan_limits, api_calls_used, resources_count)
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def plan_comparison(request):
    """Get plan comparison data"""
    plans = {
        'free': {
            'name': 'Free Plan',
            'price': 0,
            'price_yearly': 0,
            'popular': False,
            'limits': {
                'api_calls': 30,
                'screeners': 1,
                'alerts': 0,
                'watchlists': 1,
                'portfolios': 1,
            },
            'features': [
                'Stock data access',
                '30 API calls per month',
                'Basic stock screener',
                '1 screener',
                '1 portfolio'
            ]
        },
        'bronze': {
            'name': 'Bronze Plan',
            'price': 15,
            'price_yearly': 150,
            'popular': False,
            'limits': {
                'api_calls': 1500,
                'screeners': 10,
                'alerts': 100,
                'watchlists': 2,
                'portfolios': 2,
            },
            'features': [
                'Professional stock data access',
                '1,500 API calls per month',
                '10 Screeners',
                '100 Email Alerts per month',
                '2 Watchlists',
                'Real-time market information', 
                'Basic stock screener',
                'Email alerts & notifications',
                'Portfolio tracking',
                'High Quality News and Sentiment Analysis',
                'Email support',
                'Advanced screener filters',
                'Custom watchlists',
                'Priority support'
            ]
        },
        'silver': {
            'name': 'Silver Plan',
            'price': 30,
            'price_yearly': 300,
            'popular': True,
            'limits': {
                'api_calls': 5000,
                'screeners': 20,
                'alerts': 500,
                'watchlists': 5,
                'portfolios': 5,
            },
            'features': [
                'Professional stock data access',
                '5,000 API calls per month',
                '20 Screeners',
                '500 Alerts per month',
                '5 Watchlists',
                'Portfolio Access',
                'Advanced Screener Tools (JSON input and CSV + JSON output)',
                'Advanced Watchlist Tools (JSON input and CSV + JSON output)',
                'Historical data access',
                'Custom Portfolios',
                'Higher Call limits',
                'Everything included in Bronze'
            ]
        },
        'gold': {
            'name': 'Gold Plan',
            'price': 100,
            'price_yearly': 1000,
            'popular': False,
            'limits': {
                'api_calls': -1,  # Unlimited
                'screeners': -1,
                'alerts': -1,
                'watchlists': -1,
                'portfolios': -1,
            },
            'features': [
                'Unlimited Everything',
                'Professional stock data access',
                'Highest Limits',
                'Portfolio tracking (unlimited)',
                'Complete documentation access',
                'All Screener and Watchlist Tools',
                'Unlimited watchlists',
                'API Key Access',
                'Real-time market data',
                'Professional reporting'
            ]
        }
    }
    
    # Get current user's plan
    try:
        profile = UserProfile.objects.get(user=request.user)
        current_plan = profile.plan_type
    except UserProfile.DoesNotExist:
        current_plan = 'free'
    
    return JsonResponse({
        'success': True,
        'plans': plans,
        'current_plan': current_plan
    })


def get_plan_recommendations(profile, plan_limits, api_calls_used, resources_count):
    """Get personalized plan recommendations"""
    recommendations = []
    
    # Check if user is close to limits
    if plan_limits['api_calls'] != -1:  # Not unlimited
        usage_percentage = (api_calls_used / plan_limits['api_calls']) * 100
        if usage_percentage > 80:
            recommendations.append({
                'type': 'upgrade_warning',
                'title': 'API Limit Warning',
                'message': f'You\'ve used {usage_percentage:.0f}% of your monthly API calls. Consider upgrading to avoid interruption.',
                'action': 'upgrade'
            })
        elif usage_percentage > 100:
            recommendations.append({
                'type': 'upgrade_required',
                'title': 'API Limit Exceeded',
                'message': 'You\'ve exceeded your monthly API limit. Upgrade to continue using the service.',
                'action': 'upgrade'
            })
    
    # Check resource limits
    for resource, count in resources_count.items():
        limit_key = f'{resource[:-1]}s' if resource != 'alerts' else 'alerts'
        limit = plan_limits.get(limit_key, 0)
        if limit != -1 and count >= limit:
            recommendations.append({
                'type': 'resource_limit',
                'title': f'{resource.title()} Limit Reached',
                'message': f'You\'ve reached your limit of {limit} {resource}. Upgrade to create more.',
                'action': 'upgrade'
            })
    
    # Suggest upgrades based on usage patterns
    if profile.plan_type == 'free' and api_calls_used > 20:
        recommendations.append({
            'type': 'usage_based',
            'title': 'High Usage Detected',
            'message': 'You\'re actively using the platform. Upgrade to Bronze for 50x more API calls and advanced features.',
            'action': 'upgrade_bronze'
        })
    
    return recommendations


@login_required
@require_http_methods(["GET"])
def billing_history(request):
    """Get user's billing history"""
    try:
        billing_records = BillingHistory.objects.filter(
            user=request.user
        ).order_by('-created_at')[:20]
        
        history = []
        for record in billing_records:
            history.append({
                'invoice_id': record.invoice_id,
                'amount': float(record.amount),
                'description': record.description,
                'status': record.status,
                'payment_method': record.payment_method,
                'date': record.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)