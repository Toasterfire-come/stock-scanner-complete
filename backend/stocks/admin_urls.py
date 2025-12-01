from django.urls import path
from .admin_api import admin_metrics_api

urlpatterns = [
    path('metrics/', admin_metrics_api, name='admin_metrics'),
]
