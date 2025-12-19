from django.contrib import admin
from django.urls import path, include
from core.views import homepage, health_check
from django.views.generic import TemplateView

urlpatterns = [
    path('', homepage, name='homepage'),
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    path('api/', include('stocks.urls')),
    path('api/billing/', include('billing.urls')),
    path('api/education/', include('education.urls')),
    path('', include('core.urls')),
    path('pricing/', TemplateView.as_view(template_name='core/pricing.html'), name='pricing'),
    path('login/', TemplateView.as_view(template_name='core/login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='core/register.html'), name='register'),
]
