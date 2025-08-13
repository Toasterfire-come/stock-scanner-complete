from django.urls import path, include
from . import views, api_views
from .wordpress_api import WordPressStockView, WordPressNewsView, WordPressAlertsView
from .simple_api import SimpleStockView, SimpleNewsView
from .api_views_fixed import trigger_stock_update, trigger_news_update
from . import frontend_optimization, browser_charts, client_side_utilities, paypal_integration, user_management

urlpatterns = [
    # Basic API endpoint
    path('', views.index, name='index'),
    
    # Stock data endpoints - using available api_views functions
    path('stock/<str:ticker>/', api_views.stock_detail_api, name='stock_detail'),
    # WordPress and search aliases should come BEFORE the generic stocks/<ticker> route
    path('stocks/search/', api_views.stock_search_api, name='stock_search_wp'),
    path('search/', api_views.stock_search_api, name='stock_search'),
    path('stocks/<str:ticker>/', api_views.stock_detail_api, name='stock_detail_alias'),
    path('realtime/<str:ticker>/', api_views.realtime_stock_api, name='realtime_stock'),
    path('trending/', api_views.trending_stocks_api, name='trending_stocks'),
    path('market-stats/', api_views.market_stats_api, name='market_stats'),
    # path('nasdaq/', api_views.nasdaq_stocks_api, name='nasdaq_stocks'),  # Removed: only NYSE in DB
    path('stocks/', api_views.stock_list_api, name='stock_list'),
    path('filter/', api_views.filter_stocks_api, name='filter_stocks'),
    path('statistics/', api_views.stock_statistics_api, name='stock_statistics'),
    
    # WordPress-friendly endpoints
    path('wordpress/stocks/', WordPressStockView.as_view(), name='wp_stocks'),
    path('wordpress/news/', WordPressNewsView.as_view(), name='wp_news'),
    path('wordpress/alerts/', WordPressAlertsView.as_view(), name='wp_alerts'),
    
    # Hosted WP workflow triggers
    path('stocks/update/', trigger_stock_update, name='stocks_update_trigger'),
    path('news/update/', trigger_news_update, name='news_update_trigger'),
    
    # Alert endpoints
    path('alerts/create/', api_views.create_alert_api, name='create_alert'),
    
    # Subscription endpoints
    path('subscription/', api_views.wordpress_subscription_api, name='wordpress_subscription'),
    path('wordpress/subscribe/', api_views.wordpress_subscription_api, name='wp_subscribe'),
    
    # Portfolio endpoints
    path('portfolio/', include('stocks.portfolio_urls')),
    
    # Watchlist endpoints  
    path('watchlist/', include('stocks.watchlist_urls')),
    
    # News endpoints
    path('news/', include('stocks.news_urls')),
    
    # Revenue and discount endpoints
    path('revenue/', include('stocks.revenue_urls')),
    
    # Optimization and monitoring endpoints
    path('optimization/database/', api_views.database_optimization_status, name='db_optimization_status'),
    path('optimization/indexes/create/', api_views.create_indexes_endpoint, name='create_indexes'),
    path('optimization/memory/', api_views.memory_status_endpoint, name='memory_status'),
    path('optimization/overview/', api_views.system_optimization_overview, name='optimization_overview'),
    
    # Frontend optimization endpoints
    path('frontend/minimal-stocks/', frontend_optimization.get_minimal_stocks_api, name='minimal_stocks'),
    path('frontend/configuration/', frontend_optimization.get_frontend_configuration, name='frontend_config'),
    path('frontend/chart-data/', frontend_optimization.get_raw_chart_data, name='raw_chart_data'),
    path('frontend/bulk-data/', frontend_optimization.bulk_minimal_data, name='bulk_minimal_data'),
    path('frontend/scripts/', frontend_optimization.get_client_side_scripts, name='client_scripts'),
    
    # Browser chart system
    path('charts/library/', browser_charts.get_chart_library, name='chart_library'),
    path('charts/data-stream/', browser_charts.get_chart_data_stream, name='chart_stream'),
    
    # Client-side utilities
    path('client/utilities/', client_side_utilities.get_client_utilities, name='client_utilities'),
    path('client/performance-config/', client_side_utilities.get_performance_config, name='performance_config'),
    
    # PayPal integration endpoints
    path('payment/create-subscription/', paypal_integration.create_subscription, name='create_subscription'),
    path('payment/cancel-subscription/', paypal_integration.cancel_subscription, name='cancel_subscription'),
    path('payment/subscription-status/', paypal_integration.subscription_status, name='subscription_status'),
    path('payment/plans/', paypal_integration.available_plans, name='available_plans'),
    path('payment/webhook/', paypal_integration.paypal_webhook, name='paypal_webhook'),
    
    # User management endpoints
    path('user/settings/', user_management.user_settings, name='user_settings'),
    path('user/profile/', user_management.user_profile, name='user_profile'),
    path('user/api-usage/', user_management.api_usage_stats, name='api_usage_stats'),
    path('user/subscription/', user_management.subscription_management, name='subscription_management'),
    path('user/optimization-config/', user_management.frontend_optimization_config, name='optimization_config'),
    path('user/export-data/', user_management.export_user_data, name='export_user_data'),
    path('user/reset-usage/', user_management.reset_api_usage, name='reset_api_usage'),
]
