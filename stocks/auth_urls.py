"""
Authentication and User Management URL Configuration
"""

from django.urls import path
from . import auth_api, billing_api, notifications_api

app_name = 'auth'

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', auth_api.login_api, name='login'),
    path('auth/logout/', auth_api.logout_api, name='logout'),
    
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
    
    # Notification endpoints
    path('user/notification-settings/', billing_api.notification_settings_api, name='user_notification_settings'),
    path('notifications/settings/', billing_api.notification_settings_api, name='notification_settings'),
    path('notifications/history/', notifications_api.notification_history_api, name='notification_history'),
    path('notifications/mark-read/', notifications_api.mark_notifications_read_api, name='mark_notifications_read'),
    
    # Usage statistics
    path('usage-stats/', billing_api.usage_stats_api, name='usage_stats'),
    
    # Market data
    path('market-data/', auth_api.market_data_api, name='market_data'),
]