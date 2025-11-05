# PayPal Integration Setup Guide

This guide will help you set up the PayPal payment system for Trade Scan Pro.

## Prerequisites

- Python 3.8+
- Django 3.2+
- React frontend
- PayPal Business Account

---

## Step 1: PayPal Account Setup

### 1.1 Create PayPal Developer Account

1. Go to [https://developer.paypal.com/](https://developer.paypal.com/)
2. Sign in with your PayPal business account
3. Navigate to **Dashboard** → **Apps & Credentials**

### 1.2 Create REST API App

1. Click **Create App** under REST API apps
2. App Name: "Trade Scan Pro"
3. Select account type: **Merchant**
4. Click **Create App**

### 1.3 Get API Credentials

From your app page, copy:
- **Client ID** (visible by default)
- **Secret** (click "Show" to reveal)

**Save these credentials - you'll need them for configuration!**

---

## Step 2: Create Subscription Plans

You need to create 6 subscription plans in PayPal (3 tiers × 2 billing cycles).

### 2.1 Navigate to Subscriptions

1. Go to [PayPal Dashboard](https://www.paypal.com/businessprofile/settings)
2. Click **Products & Services**
3. Click **Create Subscription Button**

### 2.2 Create Each Plan

Create the following 6 plans:

#### Bronze Monthly
- Product Name: **Trade Scan Pro - Bronze Monthly**
- Price: **$24.99 USD**
- Billing Cycle: **Monthly**
- Free Trial: **Until next 1st** (optional)

#### Bronze Annual
- Product Name: **Trade Scan Pro - Bronze Annual**
- Price: **$254.99 USD** (15% discount from $299.88)
- Billing Cycle: **Yearly**

#### Silver Monthly
- Product Name: **Trade Scan Pro - Silver Monthly**
- Price: **$49.99 USD**
- Billing Cycle: **Monthly**

#### Silver Annual
- Product Name: **Trade Scan Pro - Silver Annual**
- Price: **$509.99 USD** (15% discount from $599.88)
- Billing Cycle: **Yearly**

#### Gold Monthly
- Product Name: **Trade Scan Pro - Gold Monthly**
- Price: **$79.99 USD**
- Billing Cycle: **Monthly**

#### Gold Annual
- Product Name: **Trade Scan Pro - Gold Annual**
- Price: **$815.99 USD** (15% discount from $959.88)
- Billing Cycle: **Yearly**

### 2.3 Save Plan IDs

After creating each plan, PayPal will give you a **Plan ID** (looks like `P-XXXXXXXXXXXXXXXXXX`).

**Save all 6 Plan IDs - you'll add them to your .env file!**

---

## Step 3: Backend Configuration

### 3.1 Install Required Packages

```bash
pip install requests
```

### 3.2 Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and add your PayPal credentials:

```env
# PayPal Configuration
PAYPAL_MODE=sandbox  # Change to 'live' for production
PAYPAL_CLIENT_ID=your-client-id-here
PAYPAL_CLIENT_SECRET=your-client-secret-here

# PayPal Subscription Plan IDs
PAYPAL_PLAN_BRONZE_MONTHLY=P-XXXXXXXXXXXXXXXXXXXX
PAYPAL_PLAN_BRONZE_ANNUAL=P-XXXXXXXXXXXXXXXXXXXX
PAYPAL_PLAN_SILVER_MONTHLY=P-XXXXXXXXXXXXXXXXXXXX
PAYPAL_PLAN_SILVER_ANNUAL=P-XXXXXXXXXXXXXXXXXXXX
PAYPAL_PLAN_GOLD_MONTHLY=P-XXXXXXXXXXXXXXXXXXXX
PAYPAL_PLAN_GOLD_ANNUAL=P-XXXXXXXXXXXXXXXXXXXX

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### 3.3 Run Database Migrations

```bash
python manage.py makemigrations billing
python manage.py migrate billing
```

### 3.4 Create Django Superuser (if not done already)

```bash
python manage.py createsuperuser
```

---

## Step 4: Frontend Configuration

### 4.1 Configure React Environment

Edit `frontend/.env`:

```env
REACT_APP_PAYPAL_CLIENT_ID=your-client-id-here
REACT_APP_BACKEND_URL=http://localhost:8000
```

**Note**: Use the same Client ID from Step 1.3.

### 4.2 Install Frontend Dependencies

```bash
cd frontend
npm install
```

---

## Step 5: Testing

### 5.1 Start Backend Server

```bash
python manage.py runserver
```

### 5.2 Start Frontend Server

```bash
cd frontend
npm start
```

### 5.3 Test Payment Flow

1. Navigate to [http://localhost:3000/pricing](http://localhost:3000/pricing)
2. Click "Try for free" on any plan
3. Complete PayPal checkout using **sandbox test account**
4. Verify payment in Django admin: [http://localhost:8000/admin/billing/payment/](http://localhost:8000/admin/billing/payment/)

### 5.4 PayPal Sandbox Test Accounts

**Test Credit Card** (use in PayPal sandbox):
- Card Number: `4032 0353 2923 4227`
- Expiry: Any future date
- CVV: Any 3 digits

**Or create test accounts**:
1. Go to [https://developer.paypal.com/dashboard/accounts](https://developer.paypal.com/dashboard/accounts)
2. Create **Business** and **Personal** test accounts
3. Use personal test account to make test purchases

---

## Step 6: Webhook Setup (Important!)

Webhooks allow PayPal to notify your server about subscription events (cancelled, suspended, etc.)

### 6.1 Add Webhook in PayPal Dashboard

1. Go to [PayPal Developer Dashboard](https://developer.paypal.com/dashboard/)
2. Select your app
3. Click **Add Webhook**
4. Webhook URL: `https://yourdomain.com/api/billing/webhooks/paypal/`
5. Select these event types:
   - ✅ `PAYMENT.CAPTURE.COMPLETED`
   - ✅ `BILLING.SUBSCRIPTION.ACTIVATED`
   - ✅ `BILLING.SUBSCRIPTION.CANCELLED`
   - ✅ `BILLING.SUBSCRIPTION.SUSPENDED`
   - ✅ `BILLING.SUBSCRIPTION.EXPIRED`
   - ✅ `PAYMENT.SALE.REFUNDED`

6. Click **Save**

### 6.2 Test Webhooks

Use PayPal webhook simulator:
1. Go to **Webhooks** → **Simulate events**
2. Select event type
3. Send test event
4. Check Django logs for webhook processing

---

## Step 7: Go Live (Production)

### 7.1 Switch to Live Mode

1. Get **Live** credentials from PayPal dashboard (not sandbox)
2. Update `.env`:
   ```env
   PAYPAL_MODE=live
   PAYPAL_CLIENT_ID=your-live-client-id
   PAYPAL_CLIENT_SECRET=your-live-client-secret
   ```
3. Update frontend `.env`:
   ```env
   REACT_APP_PAYPAL_CLIENT_ID=your-live-client-id
   ```

### 7.2 Create Live Subscription Plans

Repeat Step 2 but in **Live** mode, not sandbox.

### 7.3 Update Webhook URL

Update webhook URL to your production domain:
`https://yourdomain.com/api/billing/webhooks/paypal/`

### 7.4 Test Live Payments

**Use real credit cards carefully!**
- Start with small test purchase
- Verify in PayPal dashboard
- Check Django admin for payment records
- Test cancellation flow
- Verify webhooks are received

---

## Troubleshooting

### Issue: "Payment unavailable: PayPal not configured"

**Solution**: Check that `REACT_APP_PAYPAL_CLIENT_ID` is set in `frontend/.env`

### Issue: "Failed to create PayPal order" (500 error)

**Check**:
1. Backend `.env` has correct `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET`
2. Backend server is running
3. Check Django logs for detailed error
4. Verify `PAYPAL_MODE` matches your credentials (sandbox vs live)

### Issue: "Payment capture failed"

**Check**:
1. User completed PayPal checkout (approved payment)
2. Check Django logs for API response
3. Verify PayPal subscription plan IDs are correct
4. Check PayPal developer dashboard for transaction details

### Issue: "No sales tax collected"

**Solution**: Sales tax is automatically calculated based on user's IP address. For testing:
1. Check billing/views.py `calculate_sales_tax()` function
2. Verify IP geolocation is working (uses ipapi.co)
3. Check Django logs for tax calculation

### Issue: Webhooks not received

**Check**:
1. Webhook URL is publicly accessible (not localhost)
2. Webhook URL in PayPal matches your server
3. SSL certificate is valid
4. Firewall allows PayPal IPs
5. Check Django logs for webhook processing errors

---

## API Endpoints Reference

### Public Endpoints

- `GET /api/billing/plans-meta/` - Get plan pricing (no auth required)

### Authenticated Endpoints

- `POST /api/billing/create-paypal-order/` - Create PayPal order
- `POST /api/billing/capture-paypal-order/` - Capture payment
- `POST /api/billing/change-plan/` - Change subscription plan
- `GET /api/billing/current-plan/` - Get user's current plan
- `GET /api/billing/history/` - Get billing history
- `GET /api/billing/stats/` - Get billing statistics
- `POST /api/billing/apply-discount/` - Apply discount code

### Webhook Endpoint

- `POST /api/billing/webhooks/paypal/` - PayPal webhook handler (no auth)

---

## Plan Pricing Structure

| Plan   | Monthly | Annual (15% off) |
|--------|---------|------------------|
| Bronze | $24.99  | $254.99          |
| Silver | $49.99  | $509.99          |
| Gold   | $79.99  | $815.99          |

**Sales Tax**: Automatically calculated based on user's state (US only)

**Referral Discounts**: Codes starting with `REF_` get 50% off first month (monthly plans only)

---

## Security Checklist

Before going live:

- [ ] Change `SECRET_KEY` in production
- [ ] Set `DEBUG=False` in production
- [ ] Use HTTPS for all endpoints
- [ ] Enable CSRF protection
- [ ] Implement webhook signature verification
- [ ] Store PayPal credentials securely (environment variables, not code)
- [ ] Limit `ALLOWED_HOSTS` to your domain
- [ ] Set up proper logging and monitoring
- [ ] Test all error scenarios
- [ ] Set up backup payment method (if needed)

---

## Support

For issues:
1. Check Django logs: `python manage.py runserver` output
2. Check browser console for frontend errors
3. Check PayPal developer dashboard for transaction details
4. Review this setup guide
5. Contact PayPal support for API issues

---

## Additional Resources

- [PayPal Subscriptions API](https://developer.paypal.com/docs/subscriptions/)
- [PayPal Orders API](https://developer.paypal.com/docs/api/orders/v2/)
- [PayPal Webhooks](https://developer.paypal.com/api/rest/webhooks/)
- [Django Documentation](https://docs.djangoproject.com/)
- [React PayPal SDK](https://paypal.github.io/react-paypal-js/)

