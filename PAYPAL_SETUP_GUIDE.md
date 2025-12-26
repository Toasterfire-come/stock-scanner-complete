# PayPal Integration Setup Guide

**Trade Scan Pro - Payment Processing Configuration**
**Date:** December 26, 2025
**Status:** Production Ready

---

## Overview

Trade Scan Pro now uses **PayPal** as the primary payment processor for subscription billing. The system supports:

- ✅ **Bronze, Silver, Gold** subscription tiers
- ✅ **Monthly and Yearly** billing cycles
- ✅ **Automatic recurring payments**
- ✅ **Webhook notifications** for payment events
- ✅ **Sandbox testing** before going live

---

## Prerequisites

1. **PayPal Business Account** - [Sign up here](https://www.paypal.com/us/webapps/mpp/merchant)
2. **Developer Account Access** - [PayPal Developer Portal](https://developer.paypal.com/)
3. **API Credentials** - Client ID and Secret

---

## Step 1: Create PayPal Developer App

### 1.1 Access Developer Dashboard

1. Go to [PayPal Developer Portal](https://developer.paypal.com/)
2. Log in with your PayPal Business account
3. Navigate to **Dashboard** → **My Apps & Credentials**

### 1.2 Create New App

1. Click **Create App**
2. Enter app name: `Trade Scan Pro`
3. Select **Merchant** as app type
4. Click **Create App**

### 1.3 Get API Credentials

**Sandbox Credentials (for testing):**
- Client ID: `AxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxR`
- Secret: `ExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxY`

**Live Credentials (for production):**
- Toggle to **Live** mode in the dashboard
- Client ID and Secret will be different from sandbox

---

## Step 2: Create Subscription Plans

You need to create 3 subscription plans in PayPal (one for each tier).

### 2.1 Access Subscriptions Dashboard

1. Go to [PayPal Developer Portal](https://developer.paypal.com/)
2. Click **Dashboard** → **Apps & Credentials**
3. Select your app (`Trade Scan Pro`)
4. Navigate to **Products** tab

### 2.2 Create Bronze Plan

1. Click **Create Product**
2. Fill in details:
   - **Product Name:** Trade Scan Pro - Bronze
   - **Product Type:** Service
   - **Category:** Software as a Service
   - **Description:** Bronze tier subscription with 1,500 API calls/month
3. Click **Save**

4. Click **Add Pricing Plan**
   - **Billing Plan Name:** Bronze Monthly
   - **Billing Cycle:** Monthly
   - **Pricing:** $9.99 USD (or your Bronze price)
   - **Setup Fee:** $0.00
   - **Free Trial:** 0 days (optional)
5. Click **Save**

6. **Copy the Plan ID** - Format: `P-XXXXXXXXXXXXXXXXXXXXXXXXXX`
   - This is your `PAYPAL_PLAN_ID_BRONZE`

### 2.3 Create Silver Plan

Repeat the process above with:
- **Product Name:** Trade Scan Pro - Silver
- **Description:** Silver tier subscription with 5,000 API calls/month
- **Pricing:** $29.99 USD (or your Silver price)
- Copy the **Plan ID** → `PAYPAL_PLAN_ID_SILVER`

### 2.4 Create Gold Plan

Repeat the process above with:
- **Product Name:** Trade Scan Pro - Gold
- **Description:** Gold tier subscription with unlimited API calls
- **Pricing:** $79.99 USD (or your Gold price)
- Copy the **Plan ID** → `PAYPAL_PLAN_ID_GOLD`

---

## Step 3: Set Up Webhooks

Webhooks notify your backend when subscription events occur (payment success, cancellation, etc.).

### 3.1 Create Webhook

1. In PayPal Developer Dashboard, go to your app
2. Navigate to **Webhooks** tab
3. Click **Add Webhook**
4. Enter webhook URL:
   - **Sandbox:** `https://your-domain.com/api/billing/webhook/` (or your ngrok URL for testing)
   - **Live:** `https://tradescanpro.com/api/billing/webhook/`

### 3.2 Select Events

Subscribe to these events:
- ✅ `BILLING.SUBSCRIPTION.ACTIVATED`
- ✅ `BILLING.SUBSCRIPTION.CANCELLED`
- ✅ `BILLING.SUBSCRIPTION.EXPIRED`
- ✅ `BILLING.SUBSCRIPTION.PAYMENT.FAILED`
- ✅ `BILLING.SUBSCRIPTION.SUSPENDED`
- ✅ `BILLING.SUBSCRIPTION.UPDATED`
- ✅ `PAYMENT.SALE.COMPLETED`
- ✅ `PAYMENT.SALE.REFUNDED`

### 3.3 Save and Copy Webhook ID

After creating the webhook:
- Click on the webhook to view details
- Copy the **Webhook ID** (format: `WH-XXXXXXXXXXXXXXXXXXXXX`)
- This is your `PAYPAL_WEBHOOK_ID`

---

## Step 4: Configure Backend Environment Variables

### 4.1 Update Django Settings

Add these to your `backend/.env` file or environment variables:

```bash
# PayPal Configuration
PAYPAL_MODE=sandbox  # Use 'sandbox' for testing, 'live' for production
PAYPAL_CLIENT_ID=AxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxR
PAYPAL_CLIENT_SECRET=ExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxY

# Subscription Plan IDs
PAYPAL_PLAN_ID_BRONZE=P-XXXXXXXXXXXXXXXXXXXXXXXXXX
PAYPAL_PLAN_ID_SILVER=P-YYYYYYYYYYYYYYYYYYYYYYYYYY
PAYPAL_PLAN_ID_GOLD=P-ZZZZZZZZZZZZZZZZZZZZZZZZZZ

# Webhook Configuration
PAYPAL_WEBHOOK_ID=WH-XXXXXXXXXXXXXXXXXXXXX

# Frontend URL (for return/cancel redirects)
FRONTEND_URL=https://tradescanpro.com
```

### 4.2 Verify Configuration

Test your configuration with Python:

```bash
cd backend
python manage.py shell
```

```python
from django.conf import settings

# Check all PayPal settings are loaded
print("Client ID:", settings.PAYPAL_CLIENT_ID[:10] + "...")
print("Mode:", settings.PAYPAL_MODE)
print("Bronze Plan ID:", settings.PAYPAL_PLAN_ID_BRONZE)
print("Silver Plan ID:", settings.PAYPAL_PLAN_ID_SILVER)
print("Gold Plan ID:", settings.PAYPAL_PLAN_ID_GOLD)
```

---

## Step 5: Test PayPal Integration

### 5.1 Create Test Subscription (Sandbox)

Use PayPal's sandbox test accounts:

1. Go to [PayPal Sandbox Accounts](https://developer.paypal.com/dashboard/accounts)
2. Create a **Personal Account** (buyer)
3. Note the test account email and password

### 5.2 Test Subscription Flow

```bash
# Start Django server
cd backend
python manage.py runserver
```

**Test API endpoint:**
```bash
curl -X POST http://localhost:8000/api/billing/subscription/upgrade/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan": "bronze"}'
```

**Expected response:**
```json
{
  "subscription_id": "I-XXXXXXXXXXXXXX",
  "approval_url": "https://www.sandbox.paypal.com/checkoutnow?token=XXXXX",
  "status": "APPROVAL_PENDING"
}
```

### 5.3 Complete Payment

1. Open the `approval_url` in a browser
2. Log in with your **sandbox personal account**
3. Approve the subscription
4. PayPal will redirect to `FRONTEND_URL/subscription/success`

### 5.4 Verify Webhook Events

Check Django logs for webhook events:
```bash
tail -f backend/logs/django.log
```

You should see:
```
INFO: PayPal webhook received: BILLING.SUBSCRIPTION.ACTIVATED
INFO: Subscription I-XXXXXXXXXXXXXX activated for user@example.com
```

---

## Step 6: Go Live (Production)

### 6.1 Switch to Live Mode

1. In PayPal Developer Dashboard, toggle to **Live** mode
2. Copy **Live** Client ID and Secret (different from sandbox)
3. Recreate subscription plans in **Live** mode
4. Recreate webhook with **Live** production URL

### 6.2 Update Environment Variables

```bash
# Production settings
PAYPAL_MODE=live
PAYPAL_CLIENT_ID=<LIVE_CLIENT_ID>
PAYPAL_CLIENT_SECRET=<LIVE_CLIENT_SECRET>
PAYPAL_PLAN_ID_BRONZE=<LIVE_BRONZE_PLAN_ID>
PAYPAL_PLAN_ID_SILVER=<LIVE_SILVER_PLAN_ID>
PAYPAL_PLAN_ID_GOLD=<LIVE_GOLD_PLAN_ID>
PAYPAL_WEBHOOK_ID=<LIVE_WEBHOOK_ID>
FRONTEND_URL=https://tradescanpro.com
```

### 6.3 Test with Real PayPal Account

- Use a **real PayPal account** (not sandbox)
- Test a small subscription ($1 test plan recommended)
- Verify webhook events are received
- Test cancellation flow

---

## PayPal Integration Code Reference

### Create Subscription (Python)

```python
from billing.paypal_integration import PayPalClient

client = PayPalClient()
subscription = client.create_subscription(
    plan_id=settings.PAYPAL_PLAN_ID_BRONZE,
    user_email="customer@example.com"
)

# Returns:
# {
#   "id": "I-XXXXXXXXXXXXXX",
#   "status": "APPROVAL_PENDING",
#   "links": [
#     {"rel": "approve", "href": "https://www.paypal.com/..."}
#   ]
# }
```

### Cancel Subscription (Python)

```python
client = PayPalClient()
success = client.cancel_subscription(
    subscription_id="I-XXXXXXXXXXXXXX",
    reason="User requested cancellation"
)
# Returns: True if successful
```

### Verify Webhook (Python)

```python
client = PayPalClient()
is_valid = client.verify_webhook_signature(
    headers=request.headers,
    body=request.body,
    webhook_id=settings.PAYPAL_WEBHOOK_ID
)

if is_valid:
    # Process webhook event
    event_type = request.data.get('event_type')
    if event_type == 'BILLING.SUBSCRIPTION.ACTIVATED':
        # Update user subscription status
        pass
```

---

## Frontend Integration (React)

### Subscription Upgrade Button

```jsx
import { useState } from 'react';
import client from '../api/client';

const UpgradePlan = () => {
  const [loading, setLoading] = useState(false);

  const handleUpgrade = async (plan) => {
    setLoading(true);
    try {
      const response = await client.post('/api/billing/subscription/upgrade/', {
        plan: plan  // 'bronze', 'silver', or 'gold'
      });

      // Redirect to PayPal approval page
      window.location.href = response.data.approval_url;
    } catch (error) {
      console.error('Upgrade failed:', error);
      alert('Failed to start subscription. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={() => handleUpgrade('bronze')} disabled={loading}>
        {loading ? 'Processing...' : 'Upgrade to Bronze'}
      </button>
      <button onClick={() => handleUpgrade('silver')} disabled={loading}>
        {loading ? 'Processing...' : 'Upgrade to Silver'}
      </button>
      <button onClick={() => handleUpgrade('gold')} disabled={loading}>
        {loading ? 'Processing...' : 'Upgrade to Gold'}
      </button>
    </div>
  );
};
```

### Success Page

```jsx
// src/pages/SubscriptionSuccess.jsx
import { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import client from '../api/client';

const SubscriptionSuccess = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const subscriptionId = searchParams.get('subscription_id');

    if (subscriptionId) {
      // Verify subscription with backend
      client.get(`/api/billing/subscription/`)
        .then((response) => {
          if (response.data.is_active) {
            alert('Subscription activated successfully!');
            navigate('/dashboard');
          }
        })
        .catch((error) => {
          console.error('Failed to verify subscription:', error);
        });
    }
  }, [searchParams, navigate]);

  return <div>Processing your subscription...</div>;
};
```

---

## Troubleshooting

### Issue: "Invalid Client ID"

**Solution:**
- Verify `PAYPAL_CLIENT_ID` is correct
- Check you're using sandbox credentials in sandbox mode
- Ensure no extra spaces in environment variables

### Issue: "Plan ID not found"

**Solution:**
- Verify plan IDs are correct
- Ensure plans are created in the correct mode (sandbox vs live)
- Check plan status is **Active** in PayPal dashboard

### Issue: Webhook not receiving events

**Solution:**
- Verify webhook URL is publicly accessible
- Check webhook URL has `/api/billing/webhook/` endpoint
- Test webhook with PayPal's **Webhook Simulator**
- Ensure SSL certificate is valid (https required)

### Issue: "Subscription approval failed"

**Solution:**
- Check sandbox account has sufficient funds (sandbox gives $5000)
- Verify return URL is correct
- Check PayPal developer logs for errors

---

## Security Best Practices

1. **Never commit API credentials** to git
   - Use environment variables
   - Add `.env` to `.gitignore`

2. **Always verify webhook signatures**
   - Use `verify_webhook_signature()` method
   - Reject unsigned webhooks

3. **Use HTTPS in production**
   - PayPal requires SSL for webhooks
   - Use valid SSL certificate (Let's Encrypt, Cloudflare)

4. **Validate subscription IDs**
   - Always verify subscription exists in PayPal
   - Don't trust client-side data

5. **Handle failed payments**
   - Set up email notifications
   - Implement grace period before disabling access
   - Allow users to update payment method

---

## Pricing Recommendations

**Bronze Tier:**
- **Monthly:** $9.99
- **Yearly:** $99.99 (2 months free)
- **Features:** 1,500 API calls/month

**Silver Tier:**
- **Monthly:** $29.99
- **Yearly:** $299.99 (2 months free)
- **Features:** 5,000 API calls/month

**Gold Tier:**
- **Monthly:** $79.99
- **Yearly:** $799.99 (2 months free)
- **Features:** Unlimited API calls

---

## PayPal Fees

PayPal charges standard processing fees:
- **Domestic:** 2.9% + $0.30 per transaction
- **International:** 4.4% + fixed fee
- **Monthly recurring:** Same as above

**Calculate net revenue:**
```
Bronze Monthly: $9.99 - ($9.99 × 0.029 + $0.30) = $9.40 net
Silver Monthly: $29.99 - ($29.99 × 0.029 + $0.30) = $28.82 net
Gold Monthly: $79.99 - ($79.99 × 0.029 + $0.30) = $77.37 net
```

---

## Support & Resources

- **PayPal Developer Docs:** [https://developer.paypal.com/docs/](https://developer.paypal.com/docs/)
- **Subscription API Reference:** [https://developer.paypal.com/docs/subscriptions/](https://developer.paypal.com/docs/subscriptions/)
- **Webhook Events:** [https://developer.paypal.com/api/rest/webhooks/event-names/](https://developer.paypal.com/api/rest/webhooks/event-names/)
- **PayPal Support:** [https://www.paypal.com/us/smarthelp/contact-us](https://www.paypal.com/us/smarthelp/contact-us)

---

## Next Steps

1. ✅ Create PayPal Business Account
2. ✅ Get API credentials (sandbox)
3. ✅ Create 3 subscription plans
4. ✅ Set up webhook
5. ✅ Configure environment variables
6. ✅ Test in sandbox mode
7. ✅ Switch to live mode
8. ✅ Test with real payment
9. ✅ Launch to production

---

**Trade Scan Pro - PayPal Integration**
**Status:** Ready for Production
**Last Updated:** December 26, 2025

🤖 Generated with [Claude Code](https://claude.com/claude-code)
