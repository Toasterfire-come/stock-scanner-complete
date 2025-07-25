# Stock Scanner Stripe Payment Setup Instructions

## Overview

This guide will help you set up Stripe payments for the Stock Scanner platform with the correct membership tiers and pricing.

## Prerequisites

1. **WordPress** with admin access
2. **Paid Memberships Pro (PMPro)** plugin installed and activated
3. **Stripe account** (live or test mode)
4. **Stock Scanner WordPress plugin** installed

## Membership Tiers & Pricing

- **Free**: $0/month - 50 API calls, 10 searches, 25 news articles per day
- **Basic**: $15/month - 1,000 API calls, 200 searches, 500 news articles per day
- **Pro**: $30/month - 5,000 API calls, 1,000 searches, 2,500 news articles per day
- **Enterprise**: $100/month - 20,000 API calls, 5,000 searches, 10,000 news articles per day

## Step 1: Install Required Plugins

### 1.1 Install Paid Memberships Pro
```bash
# Via WordPress admin
1. Go to Plugins > Add New
2. Search for "Paid Memberships Pro"
3. Install and activate the plugin
4. Follow the setup wizard
```

### 1.2 Install PMPro Stripe Add-on (if needed)
The Stripe gateway is included in PMPro core, but you may want additional features:
- PMPro - Stripe Webhook Handler
- PMPro - PayPal Express Add On (alternative payment method)

## Step 2: Configure Stripe Account

### 2.1 Create Stripe Account
1. Go to [stripe.com](https://stripe.com) and create an account
2. Complete business verification (for live payments)
3. Note your API keys from the Stripe dashboard

### 2.2 Get Stripe API Keys
```bash
# Test Mode Keys (for development)
Publishable key: pk_test_...
Secret key: sk_test_...

# Live Mode Keys (for production)
Publishable key: pk_live_...
Secret key: sk_live_...
```

### 2.3 Set Up Webhook Endpoint
1. In Stripe dashboard, go to Developers > Webhooks
2. Click "Add endpoint"
3. Use URL: `https://yourdomain.com/stock-scanner/webhook/stripe/`
4. Select events to listen for:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy the webhook signing secret

## Step 3: Configure WordPress Environment

### 3.1 Update .env File
Add these variables to your `.env` file:
```bash
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key
STRIPE_SECRET_KEY=sk_live_your_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# For testing, use test keys:
# STRIPE_PUBLISHABLE_KEY=pk_test_your_test_publishable_key
# STRIPE_SECRET_KEY=sk_test_your_test_secret_key
```

### 3.2 Set WordPress Options
Add these to your `wp-config.php` or set via WordPress admin:
```php
// Stripe settings
define('STOCK_SCANNER_STRIPE_PUBLISHABLE_KEY', 'pk_live_...');
define('STOCK_SCANNER_STRIPE_SECRET_KEY', 'sk_live_...');
define('STOCK_SCANNER_STRIPE_WEBHOOK_SECRET', 'whsec_...');
```

## Step 4: Set Up Membership Levels

### 4.1 Run Setup Script
Include the setup script in your WordPress installation:
```php
// Add to functions.php or run as a one-time script
include_once 'wp-content/plugins/stock-scanner-integration/setup-pmp-levels.php';
run_stock_scanner_pmp_setup();
```

### 4.2 Manual Setup (Alternative)
If you prefer manual setup:

1. Go to **Memberships > Membership Levels** in WordPress admin
2. Add the following levels:

#### Basic Level (ID: 1)
- **Name**: Basic
- **Description**: Perfect for casual traders - 1,000 API calls per day
- **Initial Payment**: $15.00
- **Billing Amount**: $15.00
- **Cycle**: 1 Month
- **Billing Limit**: 0 (unlimited)
- **Trial**: None

#### Pro Level (ID: 2)
- **Name**: Pro
- **Description**: Ideal for active traders - 5,000 API calls per day with priority access
- **Initial Payment**: $30.00
- **Billing Amount**: $30.00
- **Cycle**: 1 Month
- **Billing Limit**: 0 (unlimited)
- **Trial**: None

#### Enterprise Level (ID: 3)
- **Name**: Enterprise
- **Description**: For professional traders - 20,000 API calls per day with guaranteed access
- **Initial Payment**: $100.00
- **Billing Amount**: $100.00
- **Cycle**: 1 Month
- **Billing Limit**: 0 (unlimited)
- **Trial**: None

## Step 5: Configure PMPro Settings

### 5.1 Payment Gateway Settings
1. Go to **Memberships > Payment Settings**
2. Select **Stripe** as the gateway
3. Enter your Stripe keys:
   - **Publishable Key**: `pk_live_...` (or `pk_test_...` for testing)
   - **Secret Key**: `sk_live_...` (or `sk_test_...` for testing)
4. Set **Currency** to USD
5. Configure **Accepted Credit Cards**: Visa, Mastercard, American Express, Discover

### 5.2 Checkout Settings
1. Go to **Memberships > Page Settings**
2. Ensure checkout page is set up
3. Customize checkout page content if needed

### 5.3 Email Settings
1. Go to **Memberships > Email Settings**
2. Configure email templates for:
   - Checkout confirmation
   - Payment confirmation
   - Payment failed
   - Membership cancelled

## Step 6: Test the Integration

### 6.1 Test Mode Setup
1. Use Stripe test keys initially
2. Test credit card numbers:
   - **Success**: 4242 4242 4242 4242
   - **Declined**: 4000 0000 0000 0002
   - **Insufficient funds**: 4000 0000 0000 9995

### 6.2 Test Checkout Process
1. Go to your membership checkout page
2. Select each membership level
3. Complete checkout with test card
4. Verify membership is assigned correctly
5. Check webhook events in Stripe dashboard

### 6.3 Test Webhook Integration
1. Complete a test purchase
2. Check Stripe dashboard for webhook delivery
3. Verify user membership level is updated
4. Test subscription cancellation

## Step 7: Go Live

### 7.1 Switch to Live Mode
1. Replace test keys with live keys in settings
2. Update webhook endpoint to use live URL
3. Test with real payment method (small amount)

### 7.2 Configure Tax Settings (if applicable)
1. Go to **Memberships > Payment Settings**
2. Set up tax rates for applicable regions
3. Configure tax collection settings

## Step 8: Advanced Configuration

### 8.1 Custom Checkout Fields
Add custom fields for different membership levels:
```php
// Add to functions.php
function stock_scanner_custom_checkout_fields() {
    $level_id = intval($_REQUEST['level']);
    
    if ($level_id >= 2) { // Pro and Enterprise
        ?>
        <div class="pmpro_checkout-field">
            <label for="company_name">Company Name (Optional)</label>
            <input type="text" id="company_name" name="company_name" value="" />
        </div>
        <?php
    }
    
    ?>
    <div class="pmpro_checkout-field">
        <label for="trading_experience">Trading Experience</label>
        <select id="trading_experience" name="trading_experience">
            <option value="beginner">Beginner (0-1 years)</option>
            <option value="intermediate">Intermediate (2-5 years)</option>
            <option value="advanced">Advanced (5+ years)</option>
            <option value="professional">Professional Trader</option>
        </select>
    </div>
    <?php
}
add_action('pmpro_checkout_after_billing_fields', 'stock_scanner_custom_checkout_fields');
```

### 8.2 Usage Tracking Integration
Ensure the usage tracker recognizes membership levels:
```php
// In your usage tracker
function get_user_membership_level($user_id) {
    if (function_exists('pmpro_getMembershipLevelForUser')) {
        $level = pmpro_getMembershipLevelForUser($user_id);
        if ($level) {
            switch ($level->id) {
                case 1: return 'basic';
                case 2: return 'pro';
                case 3: return 'enterprise';
                default: return 'free';
            }
        }
    }
    return 'free';
}
```

## Step 9: Monitoring & Maintenance

### 9.1 Monitor Payments
- Check Stripe dashboard regularly
- Set up email alerts for failed payments
- Monitor webhook delivery status

### 9.2 Handle Failed Payments
1. Set up automated retry logic
2. Configure dunning emails
3. Implement grace period for service access

### 9.3 Customer Support
- Set up billing support workflows
- Create cancellation/refund procedures
- Document common payment issues

## Troubleshooting

### Common Issues

#### 1. Webhook Not Working
- Verify webhook URL is accessible
- Check webhook signing secret
- Ensure SSL certificate is valid
- Check server logs for errors

#### 2. Payment Failing
- Verify Stripe keys are correct
- Check if in test/live mode mismatch
- Verify card details format
- Check Stripe dashboard for error details

#### 3. Membership Not Assigned
- Check PMPro membership level configuration
- Verify webhook is processing correctly
- Check user meta for stripe_customer_id
- Ensure level IDs match between Stripe and PMPro

#### 4. Usage Limits Not Working
- Verify membership level mapping
- Check API integration between WordPress and Django
- Ensure usage tracker is getting correct level
- Test API endpoint responses

### Debug Mode
Enable debug logging:
```php
// Add to wp-config.php
define('PMPRO_DEBUG', true);
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
```

## Security Considerations

1. **Use HTTPS** for all payment pages
2. **Validate webhook signatures** properly
3. **Store API keys securely** (environment variables)
4. **Implement rate limiting** on payment endpoints
5. **Regular security audits** of payment flow
6. **PCI compliance** considerations

## Support Resources

- [Paid Memberships Pro Documentation](https://www.paidmembershipspro.com/documentation/)
- [Stripe Documentation](https://stripe.com/docs)
- [WordPress Codex](https://codex.wordpress.org/)
- Stock Scanner support: support@yourdomain.com

## Testing Checklist

- [ ] Test membership signup for each tier
- [ ] Test payment processing
- [ ] Test webhook delivery
- [ ] Test membership level assignment
- [ ] Test usage limits enforcement
- [ ] Test subscription cancellation
- [ ] Test failed payment handling
- [ ] Test refund processing
- [ ] Test emergency access during system load
- [ ] Test upgrade/downgrade flows

## Production Deployment Checklist

- [ ] Switch to live Stripe keys
- [ ] Update webhook URLs
- [ ] Configure proper tax settings
- [ ] Set up monitoring and alerts
- [ ] Test with real payment methods
- [ ] Configure backup payment methods
- [ ] Set up customer support workflows
- [ ] Document admin procedures
- [ ] Train support staff
- [ ] Create user documentation

This setup ensures your Stock Scanner platform has a robust, secure payment system that properly enforces the progressive scaling based on membership tiers.