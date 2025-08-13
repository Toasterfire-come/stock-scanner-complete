"""
URL Configuration for Stock Scanner Django Project
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.utils import timezone

# Import health check views
from stocks.monitoring import health_check_detailed, health_check_simple, system_metrics, performance_metrics

def api_root(request):
    """API root endpoint with available endpoints"""
    return JsonResponse({
        'message': 'Stock Scanner API',
        'version': '1.0.0',
        'timestamp': timezone.now().isoformat(),
        'endpoints': {
            'stocks': '/api/stocks/',
            'search': '/api/search/',
            'health': '/health/',
            'admin': '/admin/',
        },
        'status': 'operational'
    })

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API root
    path('api/', api_root, name='api_root'),
    
    # Stock API endpoints
    path('api/', include('stocks.urls')),
    
    # Health check and monitoring endpoints
    path('health/', health_check_simple, name='health_check_simple'),
    path('health/detailed/', health_check_detailed, name='health_check_detailed'),
    path('health/metrics/', system_metrics, name='system_metrics'),
    path('health/performance/', performance_metrics, name='performance_metrics'),
    
    # WordPress-compatible API endpoints (alternative paths)
    path('wp-json/stock-scanner/v1/', include('stocks.urls')),
    
    # Legacy compatibility
    path('', api_root, name='home'),
]

# Add debug toolbar in development
import os
if os.environ.get('DEBUG', 'False').lower() == 'true':
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
