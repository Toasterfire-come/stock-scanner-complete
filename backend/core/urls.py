from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='core_homepage'),
    path('readiness/', views.health_check, name='readiness'),
    path('legal/terms', views.terms_api, name='terms_api'),
    path('legal/privacy', views.privacy_api, name='privacy_api'),
]
