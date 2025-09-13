from django.contrib import admin
from django.urls import path, include
from core.views import homepage, health_check
from core.views_extra import docs_page, schema_page, redoc_page, openapi_json, endpoint_status
from stocks.auth_api import login_api, user_api, logout_api
from stocks.usage_api import usage_track_api
from stocks.billing_api import paypal_status_api, create_paypal_order_api, capture_paypal_order_api
from stocks.revenue_api import validate_discount_api

urlpatterns = [
    path('', homepage, name='homepage'),
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls),

    # Core API group
    path('api/', include('stocks.urls')),
    path('api/auth/login/', login_api, name='login_api'),
    path('api/auth/user/', user_api, name='user_api'),
    path('api/auth/logout/', logout_api, name='logout_api'),
    path('api/usage/track/', usage_track_api, name='usage_track_api'),
    path('api/billing/paypal-status/', paypal_status_api, name='paypal_status_api'),
    path('api/billing/create-paypal-order/', create_paypal_order_api, name='create_paypal_order_api'),
    path('api/billing/capture-paypal-order/', capture_paypal_order_api, name='capture_paypal_order_api'),
    path('api/revenue/validate-discount/', validate_discount_api, name='validate_discount_api'),
]
