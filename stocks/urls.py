from django.urls import path
from . import api_views
try:
    from . import paywall_api_views
    PAYWALL_AVAILABLE = True
except ImportError:
    PAYWALL_AVAILABLE = False

app_name = 'stocks_api'

urlpatterns = [
    # REST API endpoints for WordPress integration
    path('api/stocks/', api_views.stock_list_api, name='stock_list'),
    path('api/stocks/<str:ticker>/', api_views.stock_detail_api, name='stock_detail'),
    path('api/stocks/search/', api_views.stock_search_api, name='stock_search'),
    path('api/market-movers/', api_views.market_movers_api, name='market_movers'),
    path('api/stats/', api_views.stock_statistics_api, name='stock_statistics'),
    path('api/wordpress/subscribe/', api_views.wordpress_subscription_api, name='wordpress_subscribe'),
    
    # CORS handling
    path('api/cors/', api_views.cors_handler, name='cors_handler'),
]

# Add paywall-protected endpoints if available
if PAYWALL_AVAILABLE:
    urlpatterns += [
        # Paywall-protected endpoints
        path('api/protected/stocks/', paywall_api_views.protected_stock_list_api, name='protected_stock_list'),
        path('api/protected/stocks/<str:ticker>/', paywall_api_views.protected_stock_detail_api, name='protected_stock_detail'),
        path('api/premium/analytics/', paywall_api_views.premium_market_analytics_api, name='premium_analytics'),
        path('api/premium/alerts/', paywall_api_views.premium_stock_alerts_api, name='premium_alerts'),
    ]