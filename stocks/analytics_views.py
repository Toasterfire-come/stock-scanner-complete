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
from .models import StockAlert, Membership

def is_admin_user(user):
    """Check if user is admin/staff"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@require_http_methods(["GET"])
@user_passes_test(is_admin_user)
def member_analytics_api(request):
    """
    Get comprehensive member analytics from real database
    """
    try:
        # Get actual membership data from database
        total_users = User.objects.count()
        active_email_subscribers = EmailSubscription.objects.filter(is_active=True).count()
        
        # Real membership distribution from database
        membership_stats = {}
        total_members = 0
        monthly_revenue = 0
        
        # Count memberships by tier
        for tier_code, tier_name in Membership.TIER_CHOICES:
            count = Membership.objects.filter(tier=tier_code, is_active=True).count()
            membership_stats[tier_code] = count
            total_members += count
            
            # Calculate revenue for this tier
            tier_pricing = {
                'free': 0.00,
                'basic': 9.99,
                'professional': 29.99,
                'expert': 49.99
            }
            monthly_revenue += count * tier_pricing.get(tier_code, 0.00)
        
        # If no memberships exist yet, count all users as free
        if total_members == 0:
            total_members = total_users
            membership_stats = {
                'free': total_users,
                'basic': 0,
                'professional': 0,
                'expert': 0
            }
            monthly_revenue = 0.00
        
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
                'pricing_tiers': {
                    'free': 0.00,
                    'basic': 9.99,
                    'professional': 29.99,
                    'expert': 49.99
                },
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
    Get public statistics for displaying on website using real data
    """
    try:
        # Get real data from database
        total_subscribers = EmailSubscription.objects.filter(is_active=True).count()
        total_stocks_tracked = StockAlert.objects.count()
        total_users = User.objects.count()
        
        # Calculate real membership stats
        total_members = Membership.objects.filter(is_active=True).count()
        
        # If no memberships exist, count all users as members
        if total_members == 0:
            total_members = total_users
        
        # Calculate real monthly revenue
        monthly_revenue = 0.00
        tier_pricing = {
            'free': 0.00,
            'basic': 9.99,
            'professional': 29.99,
            'expert': 49.99
        }
        
        for tier_code, price in tier_pricing.items():
            tier_count = Membership.objects.filter(tier=tier_code, is_active=True).count()
            monthly_revenue += tier_count * price
        
        # Calculate real average spending
        avg_spending = round(monthly_revenue / total_members, 2) if total_members > 0 else 0.00
        
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
