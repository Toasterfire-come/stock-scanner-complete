from django.contrib import admin
from django.urls import path, include
from core.views import homepage, health_check
from django.http import JsonResponse


def api_info(request):
    """Return API information for old template routes"""
    return JsonResponse({
        'name': 'TradeScanPro API',
        'version': '2.0',
        'endpoints': {
            'stocks': '/api/stocks/',
            'auth': '/api/auth/',
            'billing': '/api/billing/',
            'backtesting': '/api/backtesting/',
            'admin': '/admin/',
        },
        'frontend': 'https://tradescanpro.com'
    })


urlpatterns = [
    path('', homepage, name='homepage'),
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    path('api/', include('stocks.urls')),
    path('api/billing/', include('billing.urls')),
    path('', include('core.urls')),
    # Redirect old template routes to API info
    path('pricing/', api_info, name='pricing_redirect'),
    path('login/', api_info, name='login_redirect'),
    path('register/', api_info, name='register_redirect'),
]
