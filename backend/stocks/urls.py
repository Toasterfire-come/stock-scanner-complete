from django.urls import path, include
from . import views, api_views, views_health
from . import alerts_api
from .wordpress_api import WordPressStockView, WordPressNewsView, WordPressAlertsView
from .simple_api import SimpleStockView, SimpleNewsView, simple_status_api
from .api_views_fixed import trigger_stock_update, trigger_news_update
from . import logs_api
from .billing_api import cancel_subscription_api
from django.http import JsonResponse

urlpatterns = [
    # Health check endpoints (must be first for monitoring)
    path('health/', views_health.health_check, name='health_check'),
    path('health/detailed/', views_health.health_check_detailed, name='health_check_detailed'),
    path('health/ready/', views_health.readiness_check, name='readiness_check'),
    path('health/live/', views_health.liveness_check, name='liveness_check'),
    
    # Status endpoint (required by problem statement)  
    path('status/', simple_status_api, name='api_status'),
    
    # Basic API endpoint
    path('', views.index, name='index'),
    
    # Include authentication and user management endpoints
    path('', include('stocks.auth_urls')),
    
    # Stock data endpoints - using available api_views functions
    path('stock/<str:ticker>/', api_views.stock_detail_api, name='stock_detail'),
    # WordPress and search aliases should come BEFORE the generic stocks/<ticker> route
    path('stocks/search/', api_views.stock_search_api, name='stock_search_wp'),
    path('search/', api_views.stock_search_api, name='stock_search'),
    
    # NEW STOCK CATEGORY ENDPOINTS (must come before stocks/<ticker>/)
    path('stocks/top-gainers/', api_views.top_gainers_api, name='top_gainers'),
    path('stocks/top-losers/', api_views.top_losers_api, name='top_losers'),
    path('stocks/most-active/', api_views.most_active_api, name='most_active'),
    
    # Screener endpoints (backed by filter API)
    path('screeners/', api_views.screeners_list_api, name='screeners_list'),
    path('screeners/create/', api_views.screeners_create_api, name='screeners_create'),
    path('screeners/<str:screener_id>/', api_views.screeners_detail_api, name='screeners_detail'),
    path('screeners/<str:screener_id>/update/', api_views.screeners_update_api, name='screeners_update'),
    path('screeners/<str:screener_id>/results/', api_views.screeners_results_api, name='screeners_results'),
    path('screeners/templates/', api_views.screeners_templates_api, name='screeners_templates'),

    # Generic stock endpoints (after specific routes)
    path('stocks/<str:ticker>/', api_views.stock_detail_api, name='stock_detail_alias'),
    path('realtime/<str:ticker>/', api_views.realtime_stock_api, name='realtime_stock'),
    path('trending/', api_views.trending_stocks_api, name='trending_stocks'),
    path('market-stats/', api_views.market_stats_api, name='market_stats'),
    # Aliases for platform/frontend compatibility
    path('platform-stats/', api_views.market_stats_api, name='platform_stats_alias'),
    # path('nasdaq/', api_views.nasdaq_stocks_api, name='nasdaq_stocks'),  # Removed: only NYSE in DB
    path('stocks/', api_views.stock_list_api, name='stock_list'),
    path('stocks/<str:ticker>/quote/', api_views.stock_detail_api, name='stock_quote'),
    path('filter/', api_views.filter_stocks_api, name='filter_stocks'),
    path('statistics/', api_views.stock_statistics_api, name='stock_statistics'),
    
    # NEW ENDPOINTS REQUESTED BY USER
    # Stats endpoints
    path('stats/total-tickers/', api_views.total_tickers_api, name='total_tickers'),
    path('stats/gainers-losers/', api_views.gainers_losers_stats_api, name='gainers_losers_stats'),
    path('stats/total-alerts/', api_views.total_alerts_api, name='total_alerts'),
    
    # Portfolio endpoints
    path('portfolio/value/', api_views.portfolio_value_api, name='portfolio_value'),
    path('portfolio/pnl/', api_views.portfolio_pnl_api, name='portfolio_pnl'),
    path('portfolio/return/', api_views.portfolio_return_api, name='portfolio_return'),
    path('portfolio/holdings-count/', api_views.portfolio_holdings_count_api, name='portfolio_holdings_count'),
    
    # WordPress-friendly endpoints
    path('wordpress/stocks/', WordPressStockView.as_view(), name='wp_stocks'),
    path('wordpress/news/', WordPressNewsView.as_view(), name='wp_news'),
    path('wordpress/alerts/', WordPressAlertsView.as_view(), name='wp_alerts'),
    # Simple API (no DB)
    path('simple/stocks/', SimpleStockView.as_view(), name='simple_stocks'),
    
    # Hosted WP workflow triggers
    path('stocks/update/', trigger_stock_update, name='stocks_update_trigger'),
    path('news/update/', trigger_news_update, name='news_update_trigger'),
    
    # Alerts endpoints (auth required)
    path('alerts/', alerts_api.alerts_list_api, name='alerts_list'),
    path('alerts/create/', alerts_api.alerts_create_api, name='create_alert'),
    path('alerts/<int:alert_id>/toggle/', alerts_api.alerts_toggle_api, name='toggle_alert'),
    path('alerts/<int:alert_id>/delete/', alerts_api.alerts_delete_api, name='delete_alert'),
    path('alerts/unread-count/', alerts_api.alerts_unread_count_api, name='alerts_unread_count'),
    
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

    # Billing management
    path('billing/cancel', cancel_subscription_api, name='cancel_subscription'),

    # Logging & monitoring endpoints
    path('logs/client/', logs_api.client_logs_api, name='client_logs'),
    path('logs/metrics/', logs_api.metrics_logs_api, name='metrics_logs'),
    path('logs/security/', logs_api.security_logs_api, name='security_logs'),
]
