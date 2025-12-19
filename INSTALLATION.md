# TradeScanPro Installation Guide

Complete setup guide for production deployment.

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- MySQL 8.0 or PostgreSQL 14+
- Git

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete
```

### 2. Backend Setup

#### Install Dependencies
```bash
cd backend
pip install -r ../requirements.txt
```

#### Configure Environment
Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
- Database credentials
- API keys
- Payment processor keys (Stripe)
- Secret keys

#### Setup Database
Follow [SETUP_DATABASE.md](./SETUP_DATABASE.md)

#### Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 3. Frontend Setup

```bash
cd ../frontend
npm install
```

Configure `.env.production`:
```
REACT_APP_API_URL=https://api.tradescanpro.com
```

### 4. Setup Cloudflare Tunnel (Production)

Follow [SETUP_CLOUDFLARE.md](./SETUP_CLOUDFLARE.md)

### 5. Start Services

#### Development
```bash
# Terminal 1 - Backend
cd backend
python manage.py runserver

# Terminal 2 - Frontend
cd frontend
npm start

# Terminal 3 - Scanners (optional)
cd backend
python scanner_orchestrator.py
```

#### Production
```bash
# Backend
cd backend
gunicorn stockscanner_django.wsgi:application --bind 0.0.0.0:8000

# Frontend
cd frontend
npm run build
# Serve build folder with nginx or similar

# Scanners
cd backend
python scanner_orchestrator.py
```

## Initial Data Population

Populate stock database (takes 2-3 hours):
```bash
cd backend
python realtime_daily_yfinance.py
```

## Verify Installation

1. Backend API: `http://localhost:8000/api/stocks/`
2. Frontend: `http://localhost:3000`
3. Admin Panel: `http://localhost:8000/admin`

## Production Checklist

- [ ] Database configured and migrated
- [ ] Environment variables set
- [ ] Cloudflare tunnel running
- [ ] SSL certificate active
- [ ] Payment processing configured
- [ ] Stock data populated
- [ ] Scanners running via orchestrator
- [ ] Frontend built and deployed
- [ ] Admin account created

## Troubleshooting

See individual setup guides:
- Database issues: [SETUP_DATABASE.md](./SETUP_DATABASE.md)
- Tunnel issues: [SETUP_CLOUDFLARE.md](./SETUP_CLOUDFLARE.md)
- Project overview: [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md)

## Support

For issues, contact: carter.kiefer2010@outlook.com
