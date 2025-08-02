# PayPal Integration Setup Guide

This guide will help you set up PayPal payments for your Stock Scanner application.

## 📋 **Prerequisites**

1. **PayPal Business Account** (required for API access)
2. **WordPress Admin Access**
3. **SSL Certificate** (required for production)

## 🔧 **Step 1: Create PayPal Business Account**

### 1.1 Sign Up for PayPal Business
- Go to [PayPal Business](https://www.paypal.com/business)
- Click "Sign Up" and choose "Business Account"
- Complete the registration process

### 1.2 Verify Your Business Account
- Provide business information
- Upload required documents
- Wait for verification (usually 1-3 business days)

## 🔑 **Step 2: Get PayPal API Credentials**

### 2.1 Access PayPal Developer Dashboard
- Go to [PayPal Developer Dashboard](https://developer.paypal.com/)
- Sign in with your PayPal Business account
- Navigate to "My Apps & Credentials"

### 2.2 Create a New App
1. Click "Create App"
2. Choose "Business" app type
3. Enter app name: "Stock Scanner"
4. Click "Create App"

### 2.3 Get API Credentials
- **Client ID**: Copy from the app details
- **Client Secret**: Copy from the app details
- **Note**: Keep these secure and never share them

## ⚙️ **Step 3: Configure Environment**

### 3.1 Copy Environment Template
```bash
cp .env.example .env
```

### 3.2 Update PayPal Settings
Edit your `.env` file with your PayPal credentials:

```env
# PayPal Configuration
PAYPAL_MODE=sandbox  # Change to 'live' for production
PAYPAL_CLIENT_ID=your_paypal_client_id_here
PAYPAL_CLIENT_SECRET=your_paypal_client_secret_here
PAYPAL_WEBHOOK_URL=https://yourdomain.com/wp-json/stock-scanner/v1/paypal-webhook
PAYPAL_RETURN_URL=https://yourdomain.com/membership-success/
PAYPAL_CANCEL_URL=https://yourdomain.com/membership-cancel/
```

## 🌐 **Step 4: Configure WordPress Settings**

### 4.1 Access PayPal Settings
1. Go to WordPress Admin
2. Navigate to **Stock Scanner → PayPal Settings**
3. Enter your PayPal credentials

### 4.2 Configure URLs
- **Webhook URL**: `https://yourdomain.com/wp-json/stock-scanner/v1/paypal-webhook`
- **Return URL**: `https://yourdomain.com/membership-success/`
- **Cancel URL**: `https://yourdomain.com/membership-cancel/`

## 🔗 **Step 5: Set Up PayPal Webhooks**

### 5.1 Configure Webhook in PayPal Dashboard
1. Go to PayPal Developer Dashboard
2. Navigate to **Webhooks**
3. Click **Add Webhook**
4. Enter your webhook URL
5. Select these events:
   - `PAYMENT.CAPTURE.COMPLETED`
   - `BILLING.SUBSCRIPTION.ACTIVATED`
   - `BILLING.SUBSCRIPTION.CANCELLED`
   - `BILLING.SUBSCRIPTION.EXPIRED`

### 5.2 Test Webhook
1. Click "Test Webhook" in PayPal Dashboard
2. Check your WordPress logs for webhook receipt
3. Verify payment processing works

## 🧪 **Step 6: Test the Integration**

### 6.1 Sandbox Testing
1. Use PayPal Sandbox mode
2. Create test payments with sandbox accounts
3. Verify membership activation
4. Test subscription management

### 6.2 Test Scenarios
- ✅ One-time payment
- ✅ Subscription creation
- ✅ Payment cancellation
- ✅ Subscription renewal
- ✅ Failed payment handling

## 🚀 **Step 7: Go Live**

### 7.1 Switch to Production
1. Change `PAYPAL_MODE` to `live`
2. Update PayPal settings in WordPress admin
3. Test with real payments

### 7.2 Production Checklist
- [ ] SSL certificate installed
- [ ] PayPal mode set to "live"
- [ ] Webhook URL updated
- [ ] Test payments completed
- [ ] Error logging configured
- [ ] Support team notified

## 📊 **Step 8: Monitor Payments**

### 8.1 Check Payment Logs
- Location: `wp-content/paypal_payments.log`
- Format: JSON entries with payment details
- Monitor for failed payments

### 8.2 Monitor Error Logs
- Location: `wp-content/paypal_errors.log`
- Check for API errors
- Monitor webhook failures

## 🔒 **Security Best Practices**

### 8.1 API Security
- ✅ Never commit API credentials to Git
- ✅ Use environment variables
- ✅ Rotate credentials regularly
- ✅ Monitor API usage

### 8.2 Webhook Security
- ✅ Verify webhook signatures
- ✅ Use HTTPS for all URLs
- ✅ Implement rate limiting
- ✅ Log all webhook events

## 🛠️ **Troubleshooting**

### Common Issues

#### 1. **"Failed to get PayPal access token"**
**Solution:**
- Verify Client ID and Secret
- Check PayPal account status
- Ensure correct API endpoint

#### 2. **"Webhook not receiving events"**
**Solution:**
- Verify webhook URL is accessible
- Check SSL certificate
- Test webhook in PayPal dashboard

#### 3. **"Payment completed but membership not activated"**
**Solution:**
- Check webhook processing
- Verify user meta updates
- Review payment logs

#### 4. **"PayPal button not loading"**
**Solution:**
- Check Client ID configuration
- Verify JavaScript loading
- Check browser console for errors

### Debug Commands

```bash
# Check PayPal logs
tail -f wp-content/paypal_payments.log

# Check error logs
tail -f wp-content/paypal_errors.log

# Test webhook endpoint
curl -X POST https://yourdomain.com/wp-json/stock-scanner/v1/paypal-webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "webhook"}'
```

## 📞 **Support**

### PayPal Support
- **Developer Support**: [PayPal Developer Support](https://developer.paypal.com/support/)
- **Business Support**: [PayPal Business Support](https://www.paypal.com/smarthelp/)

### Application Support
- **Email**: support@stockscanner.com
- **Documentation**: [Stock Scanner Docs](https://docs.stockscanner.com)
- **GitHub Issues**: [Report Issues](https://github.com/your-repo/issues)

## 📈 **Analytics & Reporting**

### Payment Analytics
- Monitor payment success rates
- Track subscription conversions
- Analyze revenue patterns
- Identify failed payment trends

### Integration Metrics
- Webhook delivery rates
- API response times
- Error frequency
- User experience metrics

## 🔄 **Maintenance**

### Regular Tasks
- [ ] Monitor payment logs weekly
- [ ] Review error logs monthly
- [ ] Update PayPal SDK quarterly
- [ ] Test webhook functionality monthly
- [ ] Backup payment data regularly

### Updates
- Keep PayPal SDK updated
- Monitor PayPal API changes
- Update integration code as needed
- Test after major updates

---

**🎉 Congratulations!** Your PayPal integration is now complete and ready to process payments for your Stock Scanner application.