from django.contrib import admin
from django.urls import path, include
from core.views import homepage, health_check

urlpatterns = [
    path('', homepage, name='homepage'),
    path('health/', health_check, name='health_check'),
    path('api/health/', health_check, name='api_health_check'),  # WordPress expects this
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Authentication URLs
    path('api/', include('stocks.urls')),
    path('revenue/', include('stocks.revenue_urls')),
]
