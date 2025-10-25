"""
URL patterns for discount codes and revenue tracking
"""

from django.urls import path
from . import revenue_views

urlpatterns = [
    # Discount code endpoints
    path('validate-discount/', revenue_views.validate_discount_code, name='validate_discount_code'),
    path('apply-discount/', revenue_views.apply_discount_code, name='apply_discount_code'),
    
    # Revenue tracking endpoints
    path('record-payment/', revenue_views.record_payment, name='record_payment'),
    path('revenue-analytics/', revenue_views.get_revenue_analytics, name='revenue_analytics'),
    path('revenue-analytics/<str:month_year>/', revenue_views.get_revenue_analytics, name='revenue_analytics_month'),
    
    # Admin endpoints
    path('initialize-codes/', revenue_views.initialize_discount_codes, name='initialize_discount_codes'),
    path('monthly-summary/<str:month_year>/', revenue_views.get_monthly_summary, name='monthly_summary'),
]