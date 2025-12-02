# app/backend/education/urls.py
"""
Educational Platform URL Configuration
Phase 7 Implementation - TradeScanPro
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, LessonViewSet, GlossaryViewSet, UserStatsViewSet
)

app_name = 'education'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'glossary', GlossaryViewSet, basename='glossary')
router.register(r'user-stats', UserStatsViewSet, basename='user-stats')

urlpatterns = [
    path('', include(router.urls)),
]
