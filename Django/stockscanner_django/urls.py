from django.contrib import admin
from django.urls import path, include
from core.views import homepage, health_check, api_documentation, endpoint_status, endpoint_status_api, kill_switch, csrf

urlpatterns = [
    path('', homepage, name='homepage'),
    path('health/', health_check, name='health_check'),
    path('api/health/', health_check, name='api_health_check'),  # WordPress expects this
    path('docs/', api_documentation, name='api_documentation'),  # API Documentation
    path('endpoint-status/', endpoint_status, name='endpoint_status'),  # Endpoint status check
    path('api/endpoint-status/', endpoint_status_api, name='endpoint_status_api'),
    path('api/auth/csrf/', csrf, name='csrf'),
    path('kill', kill_switch, name='kill_switch'),  # Kill switch (GET/POST)
    path('kill/', kill_switch, name='kill_switch_slash'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Authentication URLs
    path('api/', include('stocks.urls')),
    path('revenue/', include('stocks.revenue_urls')),
]
