# Deployment Notes

Frontend (React)
- Build with env set (example):
  - REACT_APP_BACKEND_URL=https://api.retailtradescanner.com
  - REACT_APP_PAYPAL_CLIENT_ID=... (if payments enabled)
- Run: `yarn build` (or `npm run build`).
- Upload `frontend/build/` to the static webspace for tradescanpro.com.
- Uses HashRouter, so deep links work without server rewrites.

Backend (Django)
- Place `.env` on server (see `backend/.env.example`).
- Ensure MySQL credentials are correct; optionally configure DB2_* for a secondary stocks DB.
- Migrations:
  - Single DB: `python manage.py migrate --database=default`
  - Dual DB: `python manage.py migrate --database=default` then `python manage.py migrate --database=stocks stocks` and `news`.
- Start on 127.0.0.1:8000 (matches tunnel):
  - Example: `gunicorn stockscanner_django.wsgi:application -b 127.0.0.1:8000 --workers 3`
- Tunnel remains unchanged (Cloudflare config points to http://127.0.0.1:8000).

CORS/CSRF
- Set `DJANGO_ALLOWED_HOSTS`, `FRONTEND_URL`, and `CSRF_TRUSTED_ORIGINS` in `.env`.
- Avoid wildcard origins when using cookies.

Optional switch to FastAPI (no frontend changes)
- Keep the same domain and port; replace WSGI with ASGI behind the same service name.
- Mirror route paths and JSON shapes.
- Use SQLAlchemy + Alembic with the same MySQL credentials.