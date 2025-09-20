"""
Authentication and User Management URL Configuration
"""

from django.urls import path
from . import auth_api, billing_api, notifications_api
from . import platform_views

app_name = 'auth'

urlpatterns = [
    # Authentication endpoints
    path('auth/csrf/', auth_api.csrf_token_api, name='csrf'),
    path('auth/login/', auth_api.login_api, name='login'),
    path('auth/register/', auth_api.register_api, name='register'),
    path('auth/logout/', auth_api.logout_api, name='logout'),
    # Compatibility alias expected by some clients
    path('auth/user/', auth_api.user_profile_api, name='auth_user_alias'),
    
    # User profile endpoints
    path('user/profile/', auth_api.user_profile_api, name='user_profile'),
    path('user/change-password/', auth_api.change_password_api, name='change_password'),
    
    # Billing and payment endpoints
    path('user/update-payment/', billing_api.update_payment_method_api, name='update_payment'),
    path('user/billing-history/', billing_api.billing_history_api, name='user_billing_history'),
    path('billing/history/', billing_api.billing_history_api, name='billing_history'),
    path('billing/download/<str:invoice_id>/', billing_api.download_invoice_api, name='download_invoice'),
    path('billing/current-plan/', billing_api.current_plan_api, name='current_plan'),
    path('billing/change-plan/', billing_api.change_plan_api, name='change_plan'),
    path('billing/stats/', billing_api.billing_stats_api, name='billing_stats'),
    path('billing/update-payment-method/', billing_api.update_payment_method_api, name='update_payment_method'),
    path('billing/create-paypal-order/', billing_api.create_paypal_order_api, name='create_paypal_order'),
    path('billing/capture-paypal-order/', billing_api.capture_paypal_order_api, name='capture_paypal_order'),
    path('billing/paypal-webhook/', billing_api.paypal_webhook_api, name='paypal_webhook'),
    path('billing/paypal-status/', billing_api.paypal_status_api, name='paypal_status'),
    
    # Notification endpoints
    path('user/notification-settings/', billing_api.notification_settings_api, name='user_notification_settings'),
    path('notifications/settings/', billing_api.notification_settings_api, name='notification_settings'),
    path('notifications/history/', notifications_api.notification_history_api, name='notification_history'),
    path('notifications/mark-read/', notifications_api.mark_notifications_read_api, name='mark_notifications_read'),
    
    # Usage statistics
    path('usage-stats/', billing_api.usage_stats_api, name='usage_stats'),
    path('usage/', billing_api.usage_summary_api, name='usage_summary'),
    path('usage/history/', billing_api.usage_history_api, name='usage_history'),
    path('usage/track/', billing_api.usage_track_api, name='usage_track'),
    path('usage/reconcile/', billing_api.usage_reconcile_api, name='usage_reconcile'),
    path('platform-stats', platform_views.platform_stats_api, name='platform_stats'),
    # API keys (feature-gated)
    path('user/api-keys/create/', auth_api.api_keys_create_api, name='api_keys_create'),
    path('user/api-keys/', auth_api.api_keys_list_api, name='api_keys_list'),
    path('user/api-keys/revoke/', auth_api.api_keys_revoke_api, name='api_keys_revoke'),
    
    # Market data
    path('market-data/', auth_api.market_data_api, name='market_data'),
]