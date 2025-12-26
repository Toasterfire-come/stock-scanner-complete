"""
Billing URL Configuration
"""

from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Subscription management
    path('subscription/', views.get_subscription, name='get_subscription'),
    path('subscription/upgrade/', views.upgrade_plan, name='upgrade_plan'),
    path('subscription/cancel/', views.cancel_subscription, name='cancel_subscription'),

    # Payment history
    path('payments/', views.get_payment_history, name='payment_history'),

    # Pricing (includes sales tax)
    path('pricing/', views.get_pricing, name='get_pricing'),
    path('pricing/<str:plan>/', views.get_plan_pricing, name='get_plan_pricing'),
]
