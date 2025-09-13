from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='core_homepage'),
    path('readiness/', views.health_check, name='readiness'),
]
