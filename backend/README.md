# Stock Scanner Backend (Django)

This backend serves the Trade Scan Pro React frontend hosted on a separate static webspace. Configure via `.env` and use MySQL in production.

## Quick Setup

1) Create `.env` from example
```
cp .env.example .env
# Edit with your values (hosts, PayPal, SMTP, etc.)
```

2) Install dependencies
```
pip install -r requirements.txt
```

3) Migrate databases (MySQL)

Default (single DB):
```
python manage.py migrate --database=default
```

Optional dual-DB (if DB2_* set):
- The router sends `stocks` and `news` apps to the `stocks` database.
```
python manage.py migrate --database=default
python manage.py migrate --database=stocks stocks
python manage.py migrate --database=stocks news
```

4) Create superuser
```
python manage.py createsuperuser --database=default
```

5) Run server
```
python manage.py runserver 0.0.0.0:8000
```

## Environment
See `.env.example` for all keys. Key values:
- DB_*, DB2_* for MySQL connection(s)
- DJANGO_ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, FRONTEND_URL
- PAYPAL_* (live)
- EMAIL_* (SMTP)

## CORS/CSRF
Ensure `FRONTEND_URL` includes your static site (e.g., https://tradescanpro.com). `DJANGO_ALLOWED_HOSTS` must include the API domain.

## Notes
- No Redis required. Cache can be locmem/db/file.
- Celery uses RabbitMQ in this environment; disable via `CELERY_ENABLED=false` if not used.