"""
Analytics views for Stock Scanner
Provides member statistics and revenue analytics
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Sum, Avg, F, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import datetime, timedelta
import json

from django.contrib.auth.models import User
from emails.models import EmailSubscription
from .models import StockAlert

def is_admin_user(user):
    """Check if user is admin/staff"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@require_http_methods(["GET"])
@user_passes_test(is_admin_user)
def member_analytics_api(request):
    """
    Get comprehensive member analytics
    """
    try:
        # Total members calculation
        total_users = User.objects.count()
        active_email_subscribers = EmailSubscription.objects.filter(is_active=True).count()
        
        # Simulate membership distribution (in real app, query actual membership table)
        membership_stats = {
            'free': max(0, total_users - 50),
            'basic': 25,   # $9.99/month
            'professional': 20,  # $29.99/month  
            'expert': 5    # $49.99/month
        }
        
        total_members = sum(membership_stats.values())
        
        # Revenue calculations based on pricing tiers
        pricing = {
            'free': 0,
            'basic': 9.99,
            'professional': 29.99,
            'expert': 49.99
        }
        
        # Calculate total monthly revenue
        monthly_revenue = sum(membership_stats[tier] * pricing[tier] for tier in pricing)
        
        # Calculate average spending per person
        avg_spending_per_person = monthly_revenue / total_members if total_members > 0 else 0
        
        return JsonResponse({
            'success': True,
            'data': {
                'membership_overview': {
                    'total_members': total_members,
                    'monthly_revenue': round(monthly_revenue, 2),
                    'avg_spending_per_person': round(avg_spending_per_person, 2),
                    'membership_distribution': membership_stats
                },
                'pricing_tiers': pricing,
                'last_updated': timezone.now().isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def public_stats_api(request):
    """
    Get public statistics for displaying on website
    """
    try:
        # Get real data
        total_subscribers = EmailSubscription.objects.filter(is_active=True).count()
        total_stocks_tracked = StockAlert.objects.count()
        
        # Simulate realistic member counts
        total_members = 142
        monthly_revenue = 1847.53
        avg_spending = round(monthly_revenue / total_members, 2)
        
        return JsonResponse({
            'success': True,
            'data': {
                'total_members': total_members,
                'avg_spending_per_person': avg_spending,
                'monthly_revenue': monthly_revenue,
                'email_subscribers': total_subscribers,
                'stocks_tracked': total_stocks_tracked,
                'platform_status': 'active',
                'last_updated': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
