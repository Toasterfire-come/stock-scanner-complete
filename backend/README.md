## Backend (Django) Setup

### 1) Environment

Copy `.env.example` to `.env` and fill values. Ensure `DJANGO_ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and DB credentials are set. To enable a second DB for stocks/news, set the `DB2_*` variables.

### 2) Install

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 3) Migrations

```
python manage.py migrate --database=default
python manage.py migrate --database=stocks stocks
# Optional if news app is stored in stocks DB
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

CORS/CSRF and ALLOWED_HOSTS are env-driven in `settings.py`. The optional router for the `stocks` DB is enabled only if `DB2_NAME` is set.
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

## Data transfer: local → server (both databases)

Fast path (MySQL tools):

```bash
cd backend
export DJANGO_SETTINGS_MODULE=stockscanner_django.settings_production

# Remote targets
export REMOTE_DB_HOST=your.mysql.host
export REMOTE_DB_NAME=stockscanner
export REMOTE_DB_USER=youruser
export REMOTE_DB_PASSWORD=yourpass
export REMOTE_DB_PORT=3306

export REMOTE_DB2_HOST=your.mysql.host
export REMOTE_DB2_NAME=stocks
export REMOTE_DB2_USER=youruser
export REMOTE_DB2_PASSWORD=yourpass
export REMOTE_DB2_PORT=3306

./scripts/transfer_data.sh
```

Fallback (no mysqldump): the script automatically uses Django fixtures (dumpdata/loaddata) and loads them into the remote DBs by overriding `DB_*` and `DB2_*` in a subshell.