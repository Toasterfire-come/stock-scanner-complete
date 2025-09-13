from django.contrib import admin
from django.urls import path, include
from core.views import homepage, health_check
from stocks.auth_api import login_api, user_api, logout_api
from stocks.usage_api import usage_track_api
from stocks.billing_api import paypal_status_api, create_paypal_order_api, capture_paypal_order_api
from stocks.revenue_api import validate_discount_api

urlpatterns = [
    path('', homepage, name='homepage'),
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    path('api/', include('stocks.urls')),
]
