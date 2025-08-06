from django.urls import path, include
from . import views, api_views
from .wordpress_api import WordPressStockView, WordPressNewsView, WordPressAlertsView
from .simple_api import SimpleStockView, SimpleNewsView

urlpatterns = [
    # Stock data endpoints
    path('api/stock/<str:symbol>/', views.get_stock_data, name='get_stock_data'),
    path('api/stock/<str:symbol>/price/', views.get_stock_price, name='get_stock_price'),
    path('api/search/', views.search_stocks, name='search_stocks'),
    path('api/trending/', views.get_trending_stocks, name='get_trending_stocks'),
    path('api/market-data/', views.get_market_data, name='get_market_data'),
    
    # User management endpoints
    path('api/user/profile/', views.get_user_profile, name='get_user_profile'),
    path('api/user/profile/update/', views.update_user_profile, name='update_user_profile'),
    path('api/user/membership/', views.get_user_membership, name='get_user_membership'),
    
    # Portfolio endpoints
    path('portfolio/', include('stocks.portfolio_urls')),
    
    # Watchlist endpoints  
    path('watchlist/', include('stocks.watchlist_urls')),
    
    # News endpoints
    path('news/', include('stocks.news_urls')),
    
    # Revenue and discount endpoints
    path('revenue/', include('stocks.revenue_urls')),
    
    # Alert endpoints
    path('api/alerts/', views.get_user_alerts, name='get_user_alerts'),
    path('api/alerts/create/', views.create_alert, name='create_alert'),
    path('api/alerts/<int:alert_id>/update/', views.update_alert, name='update_alert'),
    path('api/alerts/<int:alert_id>/delete/', views.delete_alert, name='delete_alert'),
]
