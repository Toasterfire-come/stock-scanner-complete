from django.urls import path, include
from . import views, api_views
from .wordpress_api import WordPressStockView, WordPressNewsView, WordPressAlertsView
from .simple_api import SimpleStockView, SimpleNewsView
from .api_views_fixed import trigger_stock_update, trigger_news_update

urlpatterns = [
    # Basic API endpoint
    path('', views.index, name='index'),
    
    # Stock data endpoints - using available api_views functions
    path('stock/<str:ticker>/', api_views.stock_detail_api, name='stock_detail'),
    path('realtime/<str:ticker>/', api_views.realtime_stock_api, name='realtime_stock'),
    path('search/', api_views.stock_search_api, name='stock_search'),
    path('trending/', api_views.trending_stocks_api, name='trending_stocks'),
    path('market-stats/', api_views.market_stats_api, name='market_stats'),
    path('nasdaq/', api_views.nasdaq_stocks_api, name='nasdaq_stocks'),
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
    
    # Subscription endpoint
    path('subscription/', api_views.wordpress_subscription_api, name='wordpress_subscription'),
    
    # Portfolio endpoints
    path('portfolio/', include('stocks.portfolio_urls')),
    
    # Watchlist endpoints  
    path('watchlist/', include('stocks.watchlist_urls')),
    
    # News endpoints
    path('news/', include('stocks.news_urls')),
    
    # Revenue and discount endpoints
    path('revenue/', include('stocks.revenue_urls')),
]
