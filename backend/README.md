### Production env template (paste into your environment)

```
# =============================================================================
# STOCK SCANNER ENVIRONMENT CONFIGURATION (PRODUCTION)
# =============================================================================
DJANGO_SETTINGS_MODULE=stockscanner_django.settings
DJANGO_DEBUG=False
ENVIRONMENT=production

# Hosts / Frontend
DJANGO_SECRET_KEY="((#cx+mb@f-(8x*p@9mfnanqe%ha1@6-b%w)q##v@)lanop"
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,retailtradescanner.com,api.retailtradescanner.com,tradescanpro.com,www.tradescanpro.com
FRONTEND_URL=https://tradescanpro.com
WORDPRESS_URL=https://retailtradescanner.com
CSRF_TRUSTED_ORIGINS=https://api.retailtradescanner.com,https://tradescanpro.com,https://www.tradescanpro.com
PRIMARY_ORIGIN=https://tradescanpro.com

# Database
DB_ENGINE=django.db.backends.mysql
DB_HOST=127.0.0.1
DB_NAME=stockscanner
DB_USER=root
DB_PASSWORD=
DB_PORT=3306
CONN_MAX_AGE=0

# Cache (no Redis)
CACHE_BACKEND=locmem

# Celery (optional)
CELERY_ENABLED=false

# Security / throttling
LOG_FORMAT=default
LOG_LEVEL=INFO
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=None
CSRF_COOKIE_SECURE=True
CSRF_COOKIE_HTTPONLY=True
CSRF_COOKIE_SAMESITE=None
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY
RATE_LIMIT_FREE_USERS=100
RATE_LIMIT_AUTHENTICATED_USERS=1000
RATE_LIMIT_WINDOW=3600

# Observability (optional)
SENTRY_DSN=
SENTRY_TRACES_SAMPLE_RATE=0
```

## Backend (Django) Setup

### 1) Environment

Copy `.env.example` to `.env` and fill values. Ensure `DJANGO_ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and DB credentials are set. Single-DB (local MySQL) is the default. To enable a second DB for stocks/news, set the `DB2_*` variables.

### 2) Install

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 3) Migrations

Single-DB (default):
```
python manage.py migrate --database=default
```

Optional dual-DB:
```
python manage.py migrate --database=default
python manage.py migrate --database=stocks stocks
python manage.py migrate --database=stocks news
```

### 4) Superuser

```
python manage.py createsuperuser --database=default
```

### 5) Run

```
python manage.py runserver 0.0.0.0:8000
```

CORS/CSRF and ALLOWED_HOSTS are env-driven in `settings.py`. The optional router for the `stocks` DB is disabled in single-DB mode and only used if `DB2_*` is configured.
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

3) Migrate databases
```
# Single-DB (default)
python manage.py migrate --database=default

# Dual-DB (optional; only if DB2_* is set)
# python manage.py migrate --database=stocks stocks
# python manage.py migrate --database=stocks news
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
- DB_* for MySQL connection (single DB by default)
- DB2_* optional for secondary stocks DB
- DJANGO_ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, FRONTEND_URL
- PAYPAL_* (live)
- EMAIL_* (SMTP)

## CORS/CSRF
Ensure `FRONTEND_URL` includes your static site (e.g., https://tradescanpro.com). `DJANGO_ALLOWED_HOSTS` must include the API domain.

## Notes
- No Redis required. Cache can be locmem/db/file.
- Celery uses RabbitMQ in this environment; disable via `CELERY_ENABLED=false` if not used.

## Data transfer: local → server (both databases)

The script uses your existing `DB_*` as REMOTE targets automatically, and `LOCAL_DB_*` / `LOCAL_DB2_*` (or localhost defaults) as LOCAL sources. `DB2_*` is optional for single-DB mode.

```bash
cd backend
export DJANGO_SETTINGS_MODULE=stockscanner_django.settings_production

# Optional: set local sources if not using defaults (127.0.0.1/root)
# export LOCAL_DB_HOST=127.0.0.1
# export LOCAL_DB_NAME=stockscanner
# export LOCAL_DB_USER=root
# export LOCAL_DB_PASSWORD=...
# export LOCAL_DB_PORT=3306

# Dual-DB optional:
# export LOCAL_DB2_NAME=stocks

./scripts/transfer_data.sh
```

Notes:
- If `mysqldump`/`mysql` are available, the script performs a fast dump/import.
- Otherwise, it falls back to Django `dumpdata/loaddata` and handles env overrides internally.
