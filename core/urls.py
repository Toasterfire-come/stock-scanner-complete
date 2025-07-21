from django.urls import path
from . import views, admin_api_views

urlpatterns = [
    path('', views.home, name='home'),
    path('news/', views.news_view, name='news_view'),
    path('search/', views.stock_search, name='stock_search'),
    path('filter/', views.filter_view, name='filter_view'),
    path('filter/download/', views.download_csv_view, name='download_csv'),
    path('email-filter/', views.email_filter_view, name='email_filter'),
    path('subscribe/<slug:category>/', views.subscription_form, name='subscription_form'),
    path('subscribe-<slug:route_name>', views.generic_subscribe),
    
    # Admin dashboard and API endpoints
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('api/admin/status/', admin_api_views.admin_status, name='admin_status'),
    path('api/admin/api-providers/', admin_api_views.api_providers_status, name='api_providers_status'),
    path('api/admin/execute/', admin_api_views.AdminExecuteView.as_view(), name='admin_execute'),
    path('api/admin/health/', admin_api_views.system_health, name='system_health'),
    path('api/admin/metrics/', admin_api_views.performance_metrics, name='performance_metrics'),
    path('api/admin/config/', admin_api_views.update_configuration, name='update_configuration'),
]
