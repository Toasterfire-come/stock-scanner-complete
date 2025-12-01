"""
Billing and Subscription URL Configuration
All PayPal, billing history, and payment management endpoints
"""

from django.urls import path
from . import billing_api

urlpatterns = [
    # PayPal Integration Endpoints
    path('create-paypal-order/', billing_api.create_paypal_order_api, name='create_paypal_order'),
    path('capture-paypal-order/', billing_api.capture_paypal_order_api, name='capture_paypal_order'),
    path('paypal-webhook/', billing_api.paypal_webhook_api, name='paypal_webhook'),
    path('paypal-client-token/', billing_api.paypal_client_token_api, name='paypal_client_token'),
    path('paypal-status/', billing_api.paypal_status_api, name='paypal_status'),
    path('plans-meta/', billing_api.paypal_plans_meta_api, name='paypal_plans_meta'),

    # Billing Management
    path('current-plan/', billing_api.current_plan_api, name='current_plan'),
    path('change-plan/', billing_api.change_plan_api, name='change_plan'),
    path('cancel/', billing_api.cancel_subscription_api, name='cancel_subscription'),
    path('update-payment/', billing_api.update_payment_method_api, name='update_payment_method'),
    path('history/', billing_api.billing_history_api, name='billing_history'),
    path('stats/', billing_api.billing_stats_api, name='billing_stats'),
    path('download/<str:invoice_id>/', billing_api.download_invoice_api, name='download_invoice'),

    # Notification Settings
    path('notifications/settings/', billing_api.notification_settings_api, name='notification_settings'),

    # Usage Statistics
    path('usage-stats/', billing_api.usage_stats_api, name='usage_stats'),
    path('usage/', billing_api.usage_summary_api, name='usage_summary'),
    path('usage/history/', billing_api.usage_history_api, name='usage_history'),
    path('usage/track/', billing_api.usage_track_api, name='usage_track'),
    path('usage/reconcile/', billing_api.usage_reconcile_api, name='usage_reconcile'),

    # Developer API Stats
    path('developer/usage-stats/', billing_api.developer_usage_stats_api, name='developer_usage_stats'),
]
