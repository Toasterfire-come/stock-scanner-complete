"""
Admin Dashboard for Stock Scanner Analytics
"""

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from emails.models import EmailSubscription
from .models import StockAlert, Membership
from django.utils import timezone
from datetime import timedelta

@staff_member_required
def dashboard_data(request):
    """
    Get dashboard data for admin
    """
# Calculate real member statistics from database
    total_users = User.objects.count()
    active_email_subs = EmailSubscription.objects.filter(is_active=True).count()

# Get real membership distribution from database
    membership_data = {}
    total_members = 0

# Count actual memberships by tier
    for tier_code, tier_name in Membership.TIER_CHOICES:
        count = Membership.objects.filter(tier=tier_code, is_active=True).count()
        membership_data[tier_code] = count
        total_members += count

# If no memberships exist, count all users as free
        if total_members == 0:
            total_members = total_users
            membership_data = {
            'free': total_users,
            'basic': 0,
            'professional': 0,
            'expert': 0
            }

# Calculate real revenue
            tier_pricing = {
            'free': 0.00,
            'basic': 9.99,
            'professional': 29.99,
            'expert': 49.99
            }

            revenue_calculation = {}
            for tier_code, price in tier_pricing.items():
                count = membership_data.get(tier_code, 0)
                revenue_calculation[tier_code] = count * price

                total_monthly_revenue = sum(revenue_calculation.values())
                avg_spending_per_person = total_monthly_revenue / total_members if total_members > 0 else 0

                dashboard_stats = {
                'membership_overview': {
                'total_members': total_members,
                'monthly_revenue': round(total_monthly_revenue, 2),
                'avg_spending_per_person': round(avg_spending_per_person, 2),
                'projected_annual': round(total_monthly_revenue * 12, 2)
                },
                'membership_breakdown': membership_data,
                'revenue_breakdown': revenue_calculation,
                'last_updated': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                return JsonResponse({
                'success': True,
                'data': dashboard_stats
                })
