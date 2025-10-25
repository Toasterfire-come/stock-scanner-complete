## Deployment Notes

### Frontend (Static Hosting)

1) Build with backend URL
```
cd frontend
REACT_APP_BACKEND_URL=https://api.retailtradescannet.com npm run build
```

2) Upload `frontend/build/` to your static webspace. The app uses HashRouter, so deep links are `/#/path` and do not require server rewrites.

### Backend (Django)

1) `.env`
Copy `backend/.env.example` to `backend/.env` and fill credentials.

2) Install and migrate
```
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --database=default
python manage.py migrate --database=stocks stocks
# Optional news in stocks DB
python manage.py migrate --database=stocks news
```

3) Create superuser
```
python manage.py createsuperuser --database=default
```

4) Run
```
python manage.py runserver 0.0.0.0:8000
```

Ensure CORS and CSRF envs allow `https://tradescanpro.com`.
# Deployment Notes

Frontend (React)
- Build with env set (example):
  - REACT_APP_BACKEND_URL=https://api.retailtradescannet.com
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