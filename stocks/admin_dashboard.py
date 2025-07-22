"""
Admin Dashboard for Stock Scanner Analytics
"""

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from emails.models import EmailSubscription
from .models import StockAlert
from django.utils import timezone
from datetime import timedelta

@staff_member_required
def dashboard_data(request):
    """
    Get dashboard data for admin
    """
    # Calculate member statistics
    total_users = User.objects.count()
    active_email_subs = EmailSubscription.objects.filter(is_active=True).count()
    
    # Simulate membership distribution for demo
    membership_data = {
        'free': 67,
        'basic': 35,      # $9.99/month
        'professional': 28,  # $29.99/month  
        'expert': 12      # $49.99/month
    }
    
    total_members = sum(membership_data.values())
    
    # Calculate revenue
    revenue_calculation = {
        'free': membership_data['free'] * 0,
        'basic': membership_data['basic'] * 9.99,
        'professional': membership_data['professional'] * 29.99,
        'expert': membership_data['expert'] * 49.99
    }
    
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
