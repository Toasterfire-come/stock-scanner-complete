from django.urls import path
from . import views, api_views
from .wordpress_api import WordPressStockView, WordPressNewsView, WordPressAlertsView
from .simple_api import SimpleStockView, SimpleNewsView
from .portfolio_api import portfolio_list_api
from .watchlist_api import watchlist_list_api
from .news_api import news_feed_api

urlpatterns = [
    # Main API endpoints
    path('', views.index, name='api_index'),

    # Comprehensive Stock API endpoints (order matters - specific before generic)
    path('stocks/', api_views.stock_list_api, name='stock_list_api'),
    path('stocks/nasdaq/', api_views.nasdaq_stocks_api, name='nasdaq_stocks_api'),
    path('stocks/search/', api_views.stock_search_api, name='stock_search_api'),
    path('stocks/<str:ticker>/', api_views.stock_detail_api, name='stock_detail_api'),

    # Market data endpoints
    path('market/stats/', api_views.market_stats_api, name='market_stats_api'),
    path('market/filter/', api_views.filter_stocks_api, name='filter_stocks_api'),

    # Real-time data endpoints
    path('realtime/<str:ticker>/', api_views.realtime_stock_api, name='realtime_stock_api'),
    path('trending/', api_views.trending_stocks_api, name='trending_stocks_api'),

    # Alert management
    path('alerts/create/', api_views.create_alert_api, name='create_alert_api'),

    # Portfolio & Watchlist (bugfix: provide GET list endpoints)
    path('portfolio/list/', portfolio_list_api, name='portfolio_list_api'),
    path('watchlist/list/', watchlist_list_api, name='watchlist_list_api'),

    # News feed (bugfix: public feed endpoint)
    path('news/feed/', news_feed_api, name='news_feed_api'),

    # WordPress Integration APIs
    path('wordpress/', WordPressStockView.as_view(), name='wordpress_stocks'),
    path('wordpress/stocks/', WordPressStockView.as_view(), name='wordpress_stocks_detailed'),
    path('wordpress/news/', WordPressNewsView.as_view(), name='wordpress_news'),
    path('wordpress/alerts/', WordPressAlertsView.as_view(), name='wordpress_alerts'),

    # Simple APIs (no database required)
    path('simple/stocks/', SimpleStockView.as_view(), name='simple_stocks'),
    path('simple/news/', SimpleNewsView.as_view(), name='simple_news'),
]