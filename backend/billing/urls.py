from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # PayPal order management
    path('create-paypal-order/', views.create_paypal_order, name='create_paypal_order'),
    path('capture-paypal-order/', views.capture_paypal_order, name='capture_paypal_order'),
    
    # Subscription management
    path('change-plan/', views.change_plan, name='change_plan'),
    path('current-plan/', views.get_current_plan, name='current_plan'),
    
    # Billing information
    path('plans-meta/', views.get_plans_meta, name='plans_meta'),
    path('history/', views.get_billing_history, name='billing_history'),
    path('stats/', views.get_billing_stats, name='billing_stats'),
    
    # Discount codes
    path('apply-discount/', views.apply_discount, name='apply_discount'),
    
    # Webhooks
    path('webhooks/paypal/', views.paypal_webhook, name='paypal_webhook'),
]
