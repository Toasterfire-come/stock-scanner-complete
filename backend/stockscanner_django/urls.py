from django.contrib import admin
from django.urls import path, include
from core.views import homepage, health_check

"""
ROUTING ARCHITECTURE:
====================
This Django app serves as a REST API backend for a React SPA frontend.

Django URLs (Backend API):
- /api/*              → Stock data, market stats, screeners, etc.
- /api/billing/*      → Payment, subscriptions, billing
- /admin/*            → Django admin panel
- /health/            → Health check endpoint

React Routes (Frontend SPA - NOT handled by Django):
- /                   → Homepage
- /features           → Features page
- /pricing            → Pricing page
- /auth/sign-in       → Login page
- /auth/sign-up       → Registration page
- /app/*              → Protected app pages (dashboard, stocks, portfolio, etc.)
- /enterprise/*       → Enterprise pages
- /help/*             → Help/docs pages
- And all other frontend routes defined in React Router

IMPORTANT:
- Django should NEVER render templates for frontend routes
- Frontend routes are handled entirely by React (index.html)
- Django only serves JSON API responses
- All authentication UI is in React, Django provides API endpoints
"""

urlpatterns = [
    # Health check (required for monitoring)
    path('health/', health_check, name='health_check'),

    # Django admin panel
    path('admin/', admin.site.urls),

    # API endpoints (JSON responses only)
    path('api/', include('stocks.urls')),
    path('api/billing/', include('billing.urls')),

    # Legacy core URLs (for screeners/stocks server-rendered pages if needed)
    # These are distinct from React SPA routes
    path('', include('core.urls')),

    # Homepage - Serves React SPA entry point (index.html)
    # This MUST be last to catch all unmatched routes and serve the React app
    path('', homepage, name='homepage'),
]
