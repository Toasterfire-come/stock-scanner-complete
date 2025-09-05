from django.urls import path
from . import views, api_views, auth_views, billing_views, usage_views, stock_quote_views
from .wordpress_api import WordPressStockView, WordPressNewsView, WordPressAlertsView
from .simple_api import SimpleStockView, SimpleNewsView

urlpatterns = [
    # Main API endpoints
    path('', views.index, name='api_index'),
    
    # Authentication endpoints
    path('auth/register/', auth_views.register_api, name='auth_register'),
    path('auth/login/', auth_views.login_api, name='auth_login'),
    
    # User management endpoints
    path('user/profile/', auth_views.user_profile_api, name='user_profile'),
    path('user/change-password/', auth_views.change_password_api, name='change_password'),
    
    # Billing endpoints
    path('billing/create-paypal-order/', billing_views.create_paypal_order_api, name='create_paypal_order'),
    path('billing/capture-paypal-order/', billing_views.capture_paypal_order_api, name='capture_paypal_order'),
    path('billing/current-plan/', billing_views.current_plan_api, name='current_plan'),
    path('billing/change-plan/', billing_views.change_plan_api, name='change_plan'),
    path('billing/history/', billing_views.billing_history_api, name='billing_history'),
    path('billing/stats/', billing_views.billing_stats_api, name='billing_stats'),
    
    # Usage and platform stats
    path('usage/', usage_views.usage_api, name='usage'),
    path('usage/track/', usage_views.track_usage_api, name='track_usage'),
    path('usage/history/', usage_views.user_usage_history_api, name='usage_history'),
    path('platform-stats/', usage_views.platform_stats_api, name='platform_stats'),
    
    # Stock quote endpoints
    path('stocks/<str:symbol>/quote/', stock_quote_views.stock_quote_api, name='stock_quote'),
    path('stocks/quotes/batch/', stock_quote_views.batch_quotes_api, name='batch_quotes'),
    path('realtime/<str:ticker>/', stock_quote_views.realtime_data_api, name='realtime_data'),
    
    # Comprehensive Stock API endpoints (order matters - specific before generic)
    path('stocks/', api_views.stock_list_api, name='stock_list_api'),
    path('stocks/nasdaq/', api_views.nasdaq_stocks_api, name='nasdaq_stocks_api'),
    path('stocks/search/', api_views.stock_search_api, name='stock_search_api'),
    path('stocks/<str:ticker>/', api_views.stock_detail_api, name='stock_detail_api'),
    
    # Market data endpoints
    path('market/stats/', api_views.market_stats_api, name='market_stats_api'),
    path('market/filter/', api_views.filter_stocks_api, name='filter_stocks_api'),
    
    # Alert management
    path('alerts/create/', api_views.create_alert_api, name='create_alert_api'),
    path('trending/', api_views.trending_stocks_api, name='trending_stocks_api'),
    
    # Portfolio and Watchlist (placeholder endpoints)
    path('portfolio/', views.placeholder_view, name='portfolio'),
    path('portfolio/add/', views.placeholder_view, name='portfolio_add'),
    path('watchlist/', views.placeholder_view, name='watchlist'),
    path('watchlist/add/', views.placeholder_view, name='watchlist_add'),
    
    # WordPress Integration APIs
    path('wordpress/', WordPressStockView.as_view(), name='wordpress_stocks'),
    path('wordpress/stocks/', WordPressStockView.as_view(), name='wordpress_stocks_detailed'),
    path('wordpress/news/', WordPressNewsView.as_view(), name='wordpress_news'),
    path('wordpress/alerts/', WordPressAlertsView.as_view(), name='wordpress_alerts'),
    
    # Simple APIs (no database required)
    path('simple/stocks/', SimpleStockView.as_view(), name='simple_stocks'),
    path('simple/news/', SimpleNewsView.as_view(), name='simple_news'),
]
