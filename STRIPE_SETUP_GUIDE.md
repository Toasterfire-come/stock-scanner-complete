# 💳 Complete Stripe + Paid Membership Pro Setup Guide

## 🎯 **Updated Membership Levels**

| Level | Price | Monthly Stocks | Daily Limit | Features |
|-------|-------|---------------|-------------|----------|
| **Free** | $0 | **15 stocks** | 5 stocks | Basic prices, limited data |
| **Basic** | $9.99 | 1,500 stocks | 50 stocks | Real-time data, volume, charts |
| **Premium** | $29.99 | 6,000 stocks | 200 stocks | Technical indicators, alerts, portfolio |
| **Pro** | $99.99 | ∞ Unlimited | ∞ Unlimited | AI analysis, API access, white-label |

## 🚀 **Step 1: Stripe Account Setup**

### 1.1 Create Stripe Account
1. Go to [stripe.com](https://stripe.com) and sign up
2. Complete business verification
3. Add bank account for payouts

### 1.2 Get API Keys
1. **Dashboard** → **Developers** → **API Keys**
2. Copy your:
   - **Publishable Key** (pk_live_... or pk_test_...)
   - **Secret Key** (sk_live_... or sk_test_...)

### 1.3 Enable Webhooks
1. **Dashboard** → **Developers** → **Webhooks**
2. **Add endpoint**: `https://yoursite.com/wp-json/pmpro/v1/stripe-webhook/`
3. Select events:
   - `customer.subscription.created`
   - `customer.subscription.updated` 
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
4. Copy **Webhook Secret** (whsec_...)

## 🔧 **Step 2: WordPress Configuration**

### 2.1 Install Required Plugins
```bash
# Install Paid Membership Pro
wp plugin install paid-memberships-pro --activate

# Install Stripe Gateway (if not included)
wp plugin install pmpro-stripe --activate
```

### 2.2 Add Stripe Keys to wp-config.php
```php
// Add to wp-config.php (above "/* That's all, stop editing! */" line)

// Stripe Live Keys (Production)
define('STRIPE_PUBLISHABLE_KEY', 'pk_live_your_publishable_key_here');
define('STRIPE_SECRET_KEY', 'sk_live_your_secret_key_here');
define('STRIPE_WEBHOOK_SECRET', 'whsec_your_webhook_secret_here');

// For testing, use these instead:
// define('STRIPE_PUBLISHABLE_KEY', 'pk_test_your_test_publishable_key_here');
// define('STRIPE_SECRET_KEY', 'sk_test_your_test_secret_key_here');
// define('STRIPE_WEBHOOK_SECRET', 'whsec_your_test_webhook_secret_here');
```

### 2.3 Upload Configuration Files
```bash
# Upload the Stripe configuration
cp stripe-pmp-config.php /wp-content/themes/your-theme/
cp plugin/stock-scanner-pmp-integration.php /wp-content/plugins/stock-scanner-pmp/
```

## ⚙️ **Step 3: Automated Setup**

### 3.1 Run Setup Commands
```bash
# Setup membership levels
wp stock-scanner setup-memberships

# Configure Stripe settings  
wp stock-scanner setup-stripe

# Create Stripe products and prices
wp stock-scanner create-products

# Setup webhooks
wp stock-scanner setup-webhooks
```

### 3.2 Manual Setup (Alternative)
If WP-CLI isn't available:

1. **WordPress Admin** → **Memberships** → **Membership Levels**
2. **Add New Level** for each tier:

**Basic Stock Access (Level 1)**
- Name: `Basic Stock Access`
- Price: `$9.99`
- Billing Cycle: `1 Month`
- Description: `Access to 1,500 stocks per month with real-time data`

**Premium Stock Analysis (Level 2)**
- Name: `Premium Stock Analysis` 
- Price: `$29.99`
- Billing Cycle: `1 Month`
- Description: `6,000 stocks per month with advanced features`

**Pro Trading Suite (Level 3)**
- Name: `Pro Trading Suite`
- Price: `$99.99`
- Billing Cycle: `1 Month`
- Description: `Unlimited access with AI analysis and API`

## 💰 **Step 4: Stripe Products Configuration**

### 4.1 Create Products in Stripe Dashboard
Go to **Stripe Dashboard** → **Products** → **Add Product**

**Product 1: Basic Stock Access**
- Name: `Basic Stock Access`
- Price: `$9.99/month`
- Billing: `Recurring monthly`
- Metadata: `pmp_level = 1`

**Product 2: Premium Stock Analysis**
- Name: `Premium Stock Analysis`
- Price: `$29.99/month`
- Billing: `Recurring monthly`
- Metadata: `pmp_level = 2`

**Product 3: Pro Trading Suite**
- Name: `Pro Trading Suite`
- Price: `$99.99/month`
- Billing: `Recurring monthly`
- Metadata: `pmp_level = 3`

### 4.2 Copy Price IDs
1. For each product, copy the **Price ID** (price_...)
2. **WordPress Admin** → **Memberships** → **Payment Settings**
3. Set **Stripe Price ID** for each level

## 🎨 **Step 5: Checkout Customization**

### 5.1 Checkout Page Features
Your checkout now includes:
- ✅ **Stripe Payment Form** (credit cards, digital wallets)
- ✅ **Trading Experience** selection
- ✅ **Interested Sectors** input
- ✅ **Referral Source** tracking
- ✅ **SSL Security** indicators
- ✅ **Mobile Responsive** design

### 5.2 Payment Methods Supported
- 💳 **Credit/Debit Cards** (Visa, Mastercard, Amex)
- 🍎 **Apple Pay** (on supported devices)
- 🤖 **Google Pay** (on supported devices)
- 🌍 **International Cards** (global coverage)

## 📊 **Step 6: Testing & Verification**

### 6.1 Test Mode Setup
Use test keys in wp-config.php:
```php
define('STRIPE_PUBLISHABLE_KEY', 'pk_test_...');
define('STRIPE_SECRET_KEY', 'sk_test_...');
```

### 6.2 Test Card Numbers
- **Success**: `4242 4242 4242 4242`
- **Declined**: `4000 0000 0000 0002`
- **Authentication**: `4000 0025 0000 3155`
- Any future expiry date and any 3-digit CVC

### 6.3 Test Scenarios
1. **Successful Signup** → Check user gets correct membership level
2. **Failed Payment** → Verify user stays at free level
3. **Subscription Changes** → Test upgrades/downgrades
4. **Cancellations** → Verify access revocation

## 🔄 **Step 7: Go Live**

### 7.1 Switch to Live Mode
1. Replace test keys with live keys in wp-config.php
2. **Stripe Dashboard** → **Activate Account**
3. Complete business verification if required

### 7.2 Launch Checklist
- ✅ Live Stripe keys configured
- ✅ Webhooks pointing to live site
- ✅ SSL certificate installed
- ✅ Membership levels created
- ✅ Checkout page tested
- ✅ Email notifications working
- ✅ Member dashboard functional

## 📈 **Step 8: Revenue Analytics**

### 8.1 Stripe Dashboard
Monitor in **Stripe Dashboard**:
- Monthly Recurring Revenue (MRR)
- Customer lifetime value
- Churn rates
- Payment success rates

### 8.2 WordPress Analytics
Track in **WordPress Admin**:
- New member signups per level
- Member engagement metrics
- Stock viewing patterns
- Upgrade conversion rates

## 🛠️ **Step 9: Advanced Features**

### 9.1 Promo Codes & Coupons
```bash
# Create discount codes in Stripe
wp pmpro-coupon add --code="SAVE20" --discount-type="percent" --amount="20"
```

### 9.2 Trial Periods
Modify membership levels to include:
- 7-day free trial for Basic
- 14-day free trial for Premium
- 30-day money-back guarantee

### 9.3 Annual Billing
Add yearly options:
- Basic: $99/year (2 months free)
- Premium: $299/year (2 months free)  
- Pro: $999/year (2 months free)

## 🔒 **Security & Compliance**

### 9.1 PCI Compliance
- ✅ **Stripe handles PCI compliance** (you don't store cards)
- ✅ **SSL required** for checkout pages
- ✅ **Webhooks secured** with endpoint secrets

### 9.2 Data Protection
- Customer payment data stored securely in Stripe
- User metadata stored in WordPress
- GDPR compliance tools available

## 📞 **Support & Troubleshooting**

### Common Issues:
1. **"Payment failed"** → Check Stripe keys and webhook URL
2. **"Level not updated"** → Verify webhook events are firing
3. **"Checkout broken"** → Check SSL certificate and keys

### Debug Tools:
- **Stripe Dashboard** → **Events** (webhook logs)
- **WordPress** → **PMPro** → **Orders** (payment history)
- **PMPro** → **Settings** → **Advanced** (debug mode)

## 🎉 **Success! Your Stock Scanner Paywall is Live**

Your users can now:
- 🆓 **Start with 15 free stock views** per month
- 💳 **Upgrade with Stripe** (secure, professional payments)
- 📱 **Pay via mobile** (Apple Pay, Google Pay)
- 📊 **Track usage** in member dashboard
- 🔄 **Cancel anytime** (customer-friendly)

**Revenue-optimized pricing that encourages upgrades while providing value at every tier!** 💰📈