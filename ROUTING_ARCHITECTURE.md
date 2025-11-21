# Routing Architecture Guide

## Overview

This application uses a **decoupled architecture** with:
- **Frontend**: React SPA (Single Page Application)
- **Backend**: Django REST API

## Routing Responsibilities

### Django Backend (API Only)

Django serves **ONLY** JSON API endpoints and the Django admin panel:

```
✅ /api/*              → Stock data, market stats, portfolio, watchlist
✅ /api/billing/*      → Payment processing, subscriptions, billing history
✅ /admin/*            → Django admin panel (staff only)
✅ /health/            → Health check endpoint (monitoring)
```

**Django does NOT handle:**
- ❌ User-facing pages (login, signup, pricing, features)
- ❌ Protected app pages (dashboard, stocks, portfolio)
- ❌ Marketing pages (home, about, contact)

### React Frontend (UI Only)

React handles **ALL** user-facing routes via React Router:

```
✅ /                   → Homepage
✅ /features           → Features page
✅ /pricing            → Pricing page
✅ /about              → About page
✅ /contact            → Contact page

✅ /auth/sign-in       → Login page
✅ /auth/sign-up       → Registration page
✅ /auth/*             → All auth-related pages

✅ /app/dashboard      → User dashboard
✅ /app/stocks         → Stocks list
✅ /app/stocks/:symbol → Stock detail
✅ /app/portfolio      → Portfolio management
✅ /app/watchlist      → Watchlist management
✅ /app/*              → All protected app pages

✅ /enterprise/*       → Enterprise pages
✅ /help/*             → Help and documentation
✅ /checkout/*         → Billing checkout pages
```

## How It Works

### Development Mode

**Frontend (React Dev Server - Port 3000)**
```bash
cd frontend
npm start
# Runs on http://localhost:3000
# Proxies API calls to Django backend
```

**Backend (Django Dev Server - Port 8000)**
```bash
cd backend
python manage.py runserver 0.0.0.0:8000
# Runs on http://localhost:8000
# Serves API endpoints only
```

**Flow:**
1. User visits `http://localhost:3000/pricing`
2. React Router handles the route → Shows Pricing component
3. Pricing component fetches data from `http://localhost:8000/api/billing/plans-meta/`
4. Django responds with JSON data
5. React renders the pricing page

### Production Mode

**Frontend (Built & Deployed to SFTP)**
```bash
cd frontend
npm run build
# Creates optimized production build in frontend/build/

# Deploy to SFTP
python deploy_sftp_complete.py
# Uploads frontend/build/* to SFTP server
```

**Backend (Django Server - Port 8000)**
```bash
cd backend
python manage.py runserver 0.0.0.0:8000
# Or use gunicorn/uwsgi
# Serves API endpoints only
```

**Flow:**
1. User visits `https://tradescanpro.com/pricing`
2. SFTP server serves React's `index.html`
3. React loads and React Router handles `/pricing` route
4. React fetches data from `https://api.tradescanpro.com/api/billing/plans-meta/`
5. Django API responds with JSON
6. React renders pricing page

## Common Issues & Solutions

### Issue 1: TemplateDoesNotExist Errors

**Error:**
```
django.template.exceptions.TemplateDoesNotExist: core/register.html
```

**Cause:**
Django has routes that try to render templates for pages that should be handled by React.

**Solution:**
Remove Django TemplateView routes from `backend/stockscanner_django/urls.py`:

```python
# ❌ WRONG - Don't do this
path('register/', TemplateView.as_view(template_name='core/register.html'))

# ✅ CORRECT - Let React handle it (no Django route needed)
# React Router automatically handles /register route
```

### Issue 2: 404 Errors on React Routes

**Error:**
Visiting `https://yourdomain.com/pricing` shows Django 404 page.

**Cause:**
React's `index.html` is not being served for unmatched routes.

**Solution:**
Ensure `.htaccess` has SPA fallback:

```apache
# In frontend/public/.htaccess
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} -f
RewriteRule ^ - [L]
RewriteRule ^ /index.html [L]
```

### Issue 3: API Calls Failing

**Error:**
```
Failed to fetch: http://localhost:3000/api/stocks/
```

**Cause:**
React is trying to call API on port 3000 instead of Django's port 8000.

**Solution:**
Configure proxy in `frontend/package.json`:

```json
{
  "proxy": "http://localhost:8000"
}
```

Or use environment variable:

```bash
# frontend/.env.development
REACT_APP_BACKEND_URL=http://localhost:8000
```

### Issue 4: CORS Errors

**Error:**
```
Access to fetch at 'http://localhost:8000/api/stocks/' blocked by CORS policy
```

**Solution:**
Install and configure `django-cors-headers`:

```python
# backend/stockscanner_django/settings.py
INSTALLED_APPS = [
    'corsheaders',
    ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://tradescanpro.com",
]
```

## URL Pattern Examples

### API Endpoints (Django)

```python
# backend/stocks/urls.py
urlpatterns = [
    path('stocks/', stock_list_view, name='stock_list'),
    path('stocks/<str:ticker>/', stock_detail_view, name='stock_detail'),
    path('screeners/', screeners_list_view, name='screeners_list'),
]

# Usage:
# GET /api/stocks/ → Returns JSON list of stocks
# GET /api/stocks/AAPL/ → Returns JSON data for AAPL
```

### Frontend Routes (React)

```jsx
// frontend/src/App.js
<Routes>
  <Route path="/pricing" element={<Pricing />} />
  <Route path="/app/stocks" element={<ProtectedRoute><Stocks /></ProtectedRoute>} />
  <Route path="/app/stocks/:symbol" element={<ProtectedRoute><StockDetail /></ProtectedRoute>} />
</Routes>

// Usage:
// Visit /pricing → React shows Pricing component
// Visit /app/stocks/AAPL → React shows StockDetail component for AAPL
```

## Testing Routes

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health/

# Stock data
curl http://localhost:8000/api/stocks/

# Stock detail
curl http://localhost:8000/api/stocks/AAPL/

# Billing plans
curl http://localhost:8000/api/billing/plans-meta/
```

### Test Frontend Routes

```bash
# Development
Visit http://localhost:3000/pricing
Visit http://localhost:3000/app/dashboard
Visit http://localhost:3000/auth/sign-in

# Production
Visit https://tradescanpro.com/pricing
Visit https://tradescanpro.com/app/dashboard
Visit https://tradescanpro.com/auth/sign-in
```

## Deployment Checklist

- [ ] **Frontend Build**
  ```bash
  cd frontend && npm run build
  ```

- [ ] **Deploy Frontend to SFTP**
  ```bash
  python deploy_sftp_complete.py
  ```

- [ ] **Verify .htaccess** (SPA fallback configured)
  ```apache
  RewriteRule ^ /index.html [L]
  ```

- [ ] **Backend Running**
  ```bash
  python manage.py runserver 0.0.0.0:8000
  ```

- [ ] **Test API Endpoints**
  ```bash
  curl https://api.tradescanpro.com/health/
  ```

- [ ] **Test Frontend Routes**
  - Visit https://tradescanpro.com/
  - Visit https://tradescanpro.com/pricing
  - Visit https://tradescanpro.com/auth/sign-in
  - Check browser console for errors

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                        USER                              │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   tradescanpro.com  │
              │   (SFTP Server)     │
              └──────────┬──────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────┐            ┌──────────────────┐
│  React SPA      │            │  Django API      │
│  (Frontend)     │            │  (Backend)       │
├─────────────────┤            ├──────────────────┤
│ /pricing        │            │ /api/stocks/     │
│ /auth/sign-in   │───────────▶│ /api/billing/    │
│ /app/dashboard  │   HTTP     │ /api/portfolio/  │
│ /app/stocks     │   Requests │ /health/         │
└─────────────────┘            └──────────────────┘
     │                                  │
     │                                  ▼
     │                         ┌─────────────────┐
     │                         │   PostgreSQL    │
     └────────────────────────▶│   Database      │
        API Calls              └─────────────────┘
        (fetch/axios)
```

## Summary

**Key Principle**:
- **Django = API Server** (JSON only)
- **React = UI Client** (HTML/CSS/JS)
- **Complete separation of concerns**

**Never Mix**:
- ❌ Don't create Django templates for user-facing pages
- ❌ Don't handle React routes in Django
- ❌ Don't render HTML from Django for frontend features

**Always Follow**:
- ✅ Django serves JSON API responses
- ✅ React handles all UI rendering
- ✅ React Router manages frontend navigation
- ✅ Clear API contracts between frontend and backend
