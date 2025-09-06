from django.urls import path, include
from . import views, api_views, views_health
from .wordpress_api import WordPressStockView, WordPressNewsView, WordPressAlertsView
from .simple_api import SimpleStockView, SimpleNewsView
from .api_views_fixed import trigger_stock_update, trigger_news_update
from . import logs_api
from django.http import JsonResponse

urlpatterns = [
    # Health check endpoints (must be first for monitoring)
    path('health/', views_health.health_check, name='health_check'),
    path('health/detailed/', views_health.health_check_detailed, name='health_check_detailed'),
    path('health/ready/', views_health.readiness_check, name='readiness_check'),
    path('health/live/', views_health.liveness_check, name='liveness_check'),
    
    # Basic API endpoint
    path('', views.index, name='index'),
    
    # Include authentication and user management endpoints
    path('', include('stocks.auth_urls')),
    
    # Stock data endpoints - using available api_views functions
    path('stock/<str:ticker>/', api_views.stock_detail_api, name='stock_detail'),
    # WordPress and search aliases should come BEFORE the generic stocks/<ticker> route
    path('stocks/search/', api_views.stock_search_api, name='stock_search_wp'),
    path('search/', api_views.stock_search_api, name='stock_search'),
    path('stocks/<str:ticker>/', api_views.stock_detail_api, name='stock_detail_alias'),
    path('realtime/<str:ticker>/', api_views.realtime_stock_api, name='realtime_stock'),
    path('trending/', api_views.trending_stocks_api, name='trending_stocks'),
    path('market-stats/', api_views.market_stats_api, name='market_stats'),
    # Aliases for platform/frontend compatibility
    path('platform-stats/', api_views.market_stats_api, name='platform_stats_alias'),
    # path('nasdaq/', api_views.nasdaq_stocks_api, name='nasdaq_stocks'),  # Removed: only NYSE in DB
    path('stocks/', api_views.stock_list_api, name='stock_list'),
    path('stocks/<str:symbol>/quote/', api_views.stock_detail_api, name='stock_quote'),
    path('filter/', api_views.filter_stocks_api, name='filter_stocks'),
    path('statistics/', api_views.stock_statistics_api, name='stock_statistics'),
    
    # WordPress-friendly endpoints
    path('wordpress/stocks/', WordPressStockView.as_view(), name='wp_stocks'),
    path('wordpress/news/', WordPressNewsView.as_view(), name='wp_news'),
    path('wordpress/alerts/', WordPressAlertsView.as_view(), name='wp_alerts'),
    # Simple API (no DB)
    path('simple/stocks/', SimpleStockView.as_view(), name='simple_stocks'),
    
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

    # Logging & monitoring endpoints
    path('logs/client/', logs_api.client_logs_api, name='client_logs'),
    path('logs/metrics/', logs_api.metrics_logs_api, name='metrics_logs'),
    path('logs/security/', logs_api.security_logs_api, name='security_logs'),
]
