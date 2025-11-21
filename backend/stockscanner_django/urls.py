from django.contrib import admin
from django.urls import path, include
from core.views import homepage, health_check

urlpatterns = [
    path('', homepage, name='homepage'),
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    path('api/', include('stocks.urls')),
    path('api/billing/', include('billing.urls')),
    path('', include('core.urls')),
    # Note: /login/, /register/, /pricing/ are handled by React frontend SPA
]
