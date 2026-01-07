# Installation & Development

This repo contains:
- **Backend**: Django (REST API) in `backend/`
- **Frontend**: React (CRA + CRACO) in `frontend/`

## Quickstart (Makefile)

If you have `make` installed, you can use:

```bash
make install
make test
```

See `make help` for more targets (build, e2e, security audit).

## Option A — Docker (recommended)

### Prereqs
- Docker + Docker Compose

### 1) Create `.env` for docker-compose

Create a file at the repo root named `.env`:

```bash
DB_ROOT_PASSWORD=change-me
DB_NAME=stockscanner
DB_USER=stockscanner
DB_PASSWORD=change-me

SECRET_KEY=change-me-super-long-random
DJANGO_SECRET_KEY=change-me-super-long-random
DEBUG=False
DJANGO_DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Optional: payments / oauth
PAYPAL_CLIENT_ID=
PAYPAL_SECRET=
GOOGLE_OAUTH_CLIENT_ID=
GOOGLE_OAUTH_CLIENT_SECRET=

```

### 2) Start everything

```bash
docker compose up --build
```

- **Frontend**: `http://localhost`
- **Backend**: `http://localhost:8000/api/health/`

## Option B — Local development (no Docker)

### Prereqs
- Python 3.12+
- Node.js 18+
- Yarn 1.x
- A database (MySQL recommended for parity; SQLite works for tests)

### Backend

```bash
python3 -m venv backend/venv
backend/venv/bin/pip install -r backend/requirements.txt

# Use SQLite for local dev (recommended unless you need MySQL parity)
export DJANGO_SETTINGS_MODULE=stockscanner_django.settings_local_sqlite
export DJANGO_DEBUG=True
export DJANGO_SECRET_KEY="dev-only-change-me"

cd backend
./venv/bin/python manage.py migrate
./venv/bin/python manage.py runserver 127.0.0.1:8000
```

### Frontend

```bash
yarn --cwd frontend install
cp frontend/.env.example frontend/.env.local
# edit frontend/.env.local as needed (REACT_APP_BACKEND_URL)
yarn --cwd frontend start
```

Frontend runs on `http://localhost:3000`.

## Tests

### Frontend

```bash
# unit
CI=true yarn --cwd frontend test --watchAll=false

# e2e (starts dev server automatically)
yarn --cwd frontend test:e2e
```

### Backend

Backend tests use SQLite + auth enabled:

```bash
cd backend
DJANGO_SETTINGS_MODULE=stockscanner_django.settings_ci ./venv/bin/python manage.py test
```

## Security note (important)

The backtesting engine executes AI-generated strategy code. It includes basic restrictions and timeouts, but **it is not a true sandbox**.
For production deployments, run strategy execution in an **isolated worker/container** with strict resource limits.

## Backtester market data providers (yfinance vs Stooq)

By default, backtests fetch market data via **yfinance**.

You can switch to **Stooq** (and/or local Stooq files) using environment variables on the backend:

```bash
# Default:
BACKTEST_DATA_PROVIDER=yfinance

# Use Stooq instead:
BACKTEST_DATA_PROVIDER=stooq

# Optional: point to a combined CSV produced by scripts/stooq_combine.py
STOOQ_COMBINED_CSV=/absolute/path/to/stooq_combined.csv

# Optional: filter interval when using a combined CSV (e.g. 60=hourly, 5=5-min)
BACKTEST_DATA_INTERVAL=60
```

To generate `STOOQ_COMBINED_CSV`, use:

```bash
python3 scripts/stooq_combine.py --input /path/to/h_us_txt.zip --output /path/to/stooq_hourly_combined.csv --interval 60 --sqlite
```

