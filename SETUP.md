# Setup Guide

Complete setup instructions for TradeScanPro stock scanner platform.

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL or MySQL
- Git

## Backend Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd stock-scanner-complete
```

### 2. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment

Create `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/tradescanpro
# or
DATABASE_URL=mysql://user:pass@localhost:3306/tradescanpro

# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=api.tradescanpro.com,localhost

# PayPal (Production)
PAYPAL_CLIENT_ID=your_client_id
PAYPAL_SECRET=your_secret
PAYPAL_WEBHOOK_ID=your_webhook_id
PAYPAL_ENV=live

# PayPal Plan IDs
PAYPAL_PLAN_BRONZE_MONTHLY=P-xxx
PAYPAL_PLAN_BRONZE_ANNUAL=P-xxx
PAYPAL_PLAN_SILVER_MONTHLY=P-xxx
PAYPAL_PLAN_SILVER_ANNUAL=P-xxx
PAYPAL_PLAN_GOLD_MONTHLY=P-xxx
PAYPAL_PLAN_GOLD_ANNUAL=P-xxx

# Optional
REDIS_URL=redis://localhost:6379/0
RECAPTCHA_SECRET=your_recaptcha_secret
```

### 4. Setup Database

**PostgreSQL:**
```bash
createdb tradescanpro
python manage.py migrate
```

**MySQL:**
```sql
CREATE DATABASE tradescanpro CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

```bash
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 7. Start Backend

**Development:**
```bash
python manage.py runserver 0.0.0.0:8000
```

**Production (Gunicorn):**
```bash
gunicorn stockscanner_django.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create `frontend/.env`:

```bash
REACT_APP_API_URL=https://api.tradescanpro.com
REACT_APP_PAYPAL_CLIENT_ID=your_paypal_client_id
```

### 3. Build Frontend

**Development:**
```bash
npm start
```

**Production:**
```bash
npm run build
```

### 4. Deploy Build

Serve the `build/` directory with your web server (Nginx, Apache, or CDN).

## Cloudflare Tunnel Setup

### 1. Install Cloudflare Tunnel

```bash
# Windows
winget install --id Cloudflare.cloudflared

# macOS
brew install cloudflare/cloudflare/cloudflared

# Linux
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

### 2. Authenticate

```bash
cloudflared tunnel login
```

### 3. Create Tunnel

```bash
cloudflared tunnel create tradescanpro-api
```

### 4. Configure Tunnel

Create `~/.cloudflared/config.yml`:

```yaml
tunnel: <tunnel-id>
credentials-file: /path/to/credentials.json

ingress:
  - hostname: api.tradescanpro.com
    service: http://localhost:8000
  - service: http_status:404
```

### 5. Route DNS

```bash
cloudflared tunnel route dns tradescanpro-api api.tradescanpro.com
```

### 6. Start Tunnel

```bash
cloudflared tunnel run tradescanpro-api
```

**Windows Service (Production):**
```bash
cloudflared service install
cloudflared service start
```

## Database Migrations

Create and apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Initial Data

### Create Referral Discount Code

```python
python manage.py shell

from stocks.models import DiscountCode
DiscountCode.objects.create(
    code='REF50',
    discount_percentage=50.00,
    is_active=True,
    applies_to_first_payment_only=True
)
```

### Configure Partner Codes

In `backend/stockscanner_django/settings.py`:

```python
PARTNER_CODE_BY_EMAIL = {
    'partner@example.com': 'REF50',
}
```

## Running Scanners

### Historical Data Scanner

Collects historical price data for all NASDAQ stocks:

```bash
cd backend
python historical_data_scanner.py
```

Run daily via cron or Windows Task Scheduler.

### Real-time Scanner

Ultra-fast real-time data collection:

```bash
cd backend
python realtime_scanner_ultra_fast.py
```

Keep running continuously for real-time updates.

## Verification

### 1. Check Backend API

```bash
curl https://api.tradescanpro.com/health/
```

Should return:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

### 2. Check Frontend

Visit `https://tradescanpro.com` and verify homepage loads.

### 3. Test Checkout

1. Register new account
2. Go to pricing
3. Select plan
4. Complete PayPal checkout
5. Verify plan activation

## Troubleshooting

### Database Connection Issues
- Verify database credentials in `.env`
- Ensure database service is running
- Check firewall rules

### PayPal Webhook Issues
- Verify webhook URL is accessible: `https://api.tradescanpro.com/api/billing/paypal-webhook`
- Check `PAYPAL_WEBHOOK_ID` matches PayPal dashboard
- Review webhook signature verification logs

### Cloudflare Tunnel Issues
- Check tunnel status: `cloudflared tunnel info tradescanpro-api`
- View logs: `cloudflared tunnel logs tradescanpro-api`
- Verify DNS records in Cloudflare dashboard

### Scanner Issues
- Check proxy connectivity
- Verify API credentials
- Review scanner logs
- Ensure database write permissions

## Support

For setup assistance:
- Email: carter.kiefer2010@outlook.com
