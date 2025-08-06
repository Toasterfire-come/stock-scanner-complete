from django.urls import path
from . import views, api_views
from .wordpress_api import WordPressStockView, WordPressNewsView, WordPressAlertsView
from .simple_api import SimpleStockView, SimpleNewsView
from . import portfolio_api, watchlist_api

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
    
    # Portfolio Management APIs
    path('portfolio/create/', portfolio_api.create_portfolio, name='create_portfolio'),
    path('portfolio/add-holding/', portfolio_api.add_holding, name='add_holding'),
    path('portfolio/sell-holding/', portfolio_api.sell_holding, name='sell_holding'),
    path('portfolio/list/', portfolio_api.list_portfolios, name='list_portfolios'),
    path('portfolio/<int:portfolio_id>/performance/', portfolio_api.portfolio_performance, name='portfolio_performance'),
    path('portfolio/import-csv/', portfolio_api.import_csv, name='import_portfolio_csv'),
    path('portfolio/alert-roi/', portfolio_api.alert_roi, name='alert_roi'),
    path('portfolio/<int:portfolio_id>/', portfolio_api.delete_portfolio, name='delete_portfolio'),
    path('portfolio/<int:portfolio_id>/update/', portfolio_api.update_portfolio, name='update_portfolio'),
    
    # Watchlist Management APIs
    path('watchlist/create/', watchlist_api.create_watchlist, name='create_watchlist'),
    path('watchlist/add-stock/', watchlist_api.add_stock, name='add_stock_to_watchlist'),
    path('watchlist/remove-stock/', watchlist_api.remove_stock, name='remove_stock_from_watchlist'),
    path('watchlist/list/', watchlist_api.list_watchlists, name='list_watchlists'),
    path('watchlist/<int:watchlist_id>/performance/', watchlist_api.watchlist_performance, name='watchlist_performance'),
    path('watchlist/<int:watchlist_id>/export/csv/', watchlist_api.export_csv, name='export_watchlist_csv'),
    path('watchlist/<int:watchlist_id>/export/json/', watchlist_api.export_json, name='export_watchlist_json'),
    path('watchlist/import/csv/', watchlist_api.import_csv, name='import_watchlist_csv'),
    path('watchlist/import/json/', watchlist_api.import_json, name='import_watchlist_json'),
    path('watchlist/<int:watchlist_id>/', watchlist_api.update_watchlist, name='update_watchlist'),
    path('watchlist/item/<int:item_id>/', watchlist_api.update_watchlist_item, name='update_watchlist_item'),
    path('watchlist/<int:watchlist_id>/delete/', watchlist_api.delete_watchlist, name='delete_watchlist'),
    
    # WordPress Integration APIs
    path('wordpress/', WordPressStockView.as_view(), name='wordpress_stocks'),
    path('wordpress/stocks/', WordPressStockView.as_view(), name='wordpress_stocks_detailed'),
    path('wordpress/news/', WordPressNewsView.as_view(), name='wordpress_news'),
    path('wordpress/alerts/', WordPressAlertsView.as_view(), name='wordpress_alerts'),
    
    # Simple APIs (no database required)
    path('simple/stocks/', SimpleStockView.as_view(), name='simple_stocks'),
    path('simple/news/', SimpleNewsView.as_view(), name='simple_news'),
]
