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

"""
API Endpoints:

COURSES:
--------
GET    /api/education/courses/                      - List all courses
GET    /api/education/courses/{slug}/                - Get course details
GET    /api/education/courses/my-courses/           - Get user's courses
POST   /api/education/courses/{slug}/enroll/        - Enroll in course

LESSONS:
--------
GET    /api/education/lessons/                      - List lessons
GET    /api/education/lessons/{slug}/               - Get lesson details
POST   /api/education/lessons/{slug}/start/         - Start lesson
POST   /api/education/lessons/{slug}/complete/      - Mark complete
POST   /api/education/lessons/{slug}/submit-quiz/   - Submit quiz
PATCH  /api/education/lessons/{slug}/update-progress/ - Update progress

GLOSSARY:
---------
GET    /api/education/glossary/                     - List all terms
GET    /api/education/glossary/{slug}/              - Get term details
GET    /api/education/glossary/by-category/         - Group by category
POST   /api/education/glossary/{slug}/track-view/   - Track view
POST   /api/education/glossary/{slug}/track-tooltip/ - Track tooltip

USER STATS:
-----------
GET    /api/education/user-stats/overview/          - Overall stats
GET    /api/education/user-stats/streak/            - Learning streak
GET    /api/education/user-stats/certificates/      - Earned certificates
GET    /api/education/user-stats/progress/          - All progress records

Query Parameters:
-----------------
Courses: ?category={category}&difficulty={difficulty}&premium={true/false}
Lessons: ?course={course_slug}
Glossary: ?category={category}&difficulty={difficulty}&letter={A-Z}&search={query}
"""
