# PayPal Webhook Setup Guide

## 🎯 **What Are Webhooks?**

Webhooks are automated messages sent from PayPal to your WordPress site when payment events occur (like successful payments, subscription activations, etc.).

## 📋 **Webhook Events You Need**

### **Essential Events:**
- ✅ `PAYMENT.CAPTURE.COMPLETED` - One-time payments completed
- ✅ `BILLING.SUBSCRIPTION.ACTIVATED` - Subscription started
- ✅ `BILLING.SUBSCRIPTION.CANCELLED` - Subscription cancelled
- ✅ `BILLING.SUBSCRIPTION.EXPIRED` - Subscription expired
- ✅ `BILLING.SUBSCRIPTION.SUSPENDED` - Subscription suspended

## 🚀 **Step-by-Step Webhook Setup**

### **Step 1: Get Your Webhook URL**

**In WordPress Admin → Settings → Stock Scanner:**
1. Look for the **Webhook URL** field
2. Copy the URL shown in the description
3. It will look like: `https://yourdomain.com/wp-json/stock-scanner/v1/paypal-webhook`

### **Step 2: Configure PayPal Developer Dashboard**

#### **For Sandbox (Testing):**
1. Go to [PayPal Developer Dashboard](https://developer.paypal.com/)
2. Click **"Sandbox"** tab
3. Go to **"Webhooks"** in the left menu
4. Click **"Add Webhook"**

#### **For Live (Production):**
1. Go to [PayPal Developer Dashboard](https://developer.paypal.com/)
2. Click **"Live"** tab
3. Go to **"Webhooks"** in the left menu
4. Click **"Add Webhook"**

### **Step 3: Add Webhook Details**

**Fill in the webhook form:**

| Field | Value |
|-------|-------|
| **Webhook URL** | `https://yourdomain.com/wp-json/stock-scanner/v1/paypal-webhook` |
| **Event Types** | Select these events: |

**Select These Events:**
- ✅ `PAYMENT.CAPTURE.COMPLETED`
- ✅ `BILLING.SUBSCRIPTION.ACTIVATED`
- ✅ `BILLING.SUBSCRIPTION.CANCELLED`
- ✅ `BILLING.SUBSCRIPTION.EXPIRED`
- ✅ `BILLING.SUBSCRIPTION.SUSPENDED`

### **Step 4: Test Your Webhook**

1. **In PayPal Dashboard:**
   - Click on your webhook
   - Click **"Test Webhook"**
   - Select an event type
   - Click **"Send Test Notification"**

2. **Check WordPress Logs:**
   ```bash
   # Check webhook logs
   tail -f wp-content/paypal_payments.log
   tail -f wp-content/paypal_errors.log
   ```

## 🔧 **Manual Webhook Setup (Alternative)**

### **If Auto-Generated URL Doesn't Work:**

1. **Create Custom Webhook URL:**
   ```php
   // Add this to your theme's functions.php or plugin
   add_action('rest_api_init', function () {
       register_rest_route('stock-scanner/v1', '/paypal-webhook', array(
           'methods' => 'POST',
           'callback' => 'handle_paypal_webhook',
           'permission_callback' => '__return_true'
       ));
   });
   ```

2. **Your webhook URL becomes:**
   ```
   https://yourdomain.com/wp-json/stock-scanner/v1/paypal-webhook
   ```

## 🛡️ **Webhook Security**

### **Verification Headers:**
PayPal sends verification headers that your plugin validates:
- `PAYPAL-TRANSMISSION-ID`
- `PAYPAL-CERT-URL`
- `PAYPAL-AUTH-ALGO`
- `PAYPAL-TRANSMISSION-SIG`
- `PAYPAL-TRANSMISSION-TIME`

### **Security Best Practices:**
1. ✅ **Always verify webhook signatures**
2. ✅ **Use HTTPS only**
3. ✅ **Log all webhook events**
4. ✅ **Handle webhook failures gracefully**

## 📊 **Webhook Event Handling**

### **What Happens When Webhooks Are Received:**

#### **Payment Completed (`PAYMENT.CAPTURE.COMPLETED`):**
1. ✅ Verify payment signature
2. ✅ Update user membership status
3. ✅ Log payment details
4. ✅ Send confirmation email

#### **Subscription Activated (`BILLING.SUBSCRIPTION.ACTIVATED`):**
1. ✅ Activate user membership
2. ✅ Set subscription end date
3. ✅ Update user meta data
4. ✅ Send welcome email

#### **Subscription Cancelled (`BILLING.SUBSCRIPTION.CANCELLED`):**
1. ✅ Mark subscription as cancelled
2. ✅ Update user access level
3. ✅ Send cancellation email
4. ✅ Log cancellation reason

## 🔍 **Testing Webhooks**

### **Sandbox Testing:**
```bash
# 1. Set PayPal Mode to "Sandbox" in WordPress
# 2. Use PayPal sandbox accounts
# 3. Make test payments
# 4. Check webhook logs
tail -f wp-content/paypal_payments.log
```

### **Live Testing:**
```bash
# 1. Set PayPal Mode to "Live" in WordPress
# 2. Use real PayPal accounts
# 3. Make small test payments
# 4. Monitor webhook delivery
```

## 📋 **Webhook Configuration Checklist**

### **PayPal Developer Dashboard:**
- [ ] Webhook URL added correctly
- [ ] All required events selected
- [ ] Webhook status shows "Active"
- [ ] Test notification sent successfully

### **WordPress Settings:**
- [ ] PayPal Mode set correctly (Sandbox/Live)
- [ ] Client ID and Secret entered
- [ ] Webhook URL matches PayPal Dashboard
- [ ] Return and Cancel URLs set

### **Testing:**
- [ ] Test payment completed
- [ ] Webhook received and processed
- [ ] User membership updated
- [ ] Logs show successful processing

## 🚨 **Common Webhook Issues**

### **1. "Webhook Not Received"**
**Solutions:**
- Check webhook URL is correct
- Verify HTTPS is enabled
- Check server firewall settings
- Test webhook delivery in PayPal Dashboard

### **2. "Webhook Verification Failed"**
**Solutions:**
- Ensure PayPal certificates are accessible
- Check webhook signature verification
- Verify webhook URL matches exactly

### **3. "User Not Updated"**
**Solutions:**
- Check webhook event type
- Verify user exists in WordPress
- Check database permissions
- Review webhook processing logs

## 🔧 **Debugging Webhooks**

### **Enable Debug Logging:**
```php
// Add to wp-config.php for debugging
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
```

### **Check Webhook Logs:**
```bash
# PayPal payment logs
tail -f wp-content/paypal_payments.log

# PayPal error logs
tail -f wp-content/paypal_errors.log

# WordPress debug logs
tail -f wp-content/debug.log
```

### **Test Webhook Manually:**
```bash
# Simulate webhook (for testing)
curl -X POST https://yourdomain.com/wp-json/stock-scanner/v1/paypal-webhook \
  -H "Content-Type: application/json" \
  -d '{"event_type":"PAYMENT.CAPTURE.COMPLETED","data":{}}'
```

## 📊 **Webhook Monitoring**

### **Monitor These Metrics:**
- ✅ Webhook delivery success rate
- ✅ Payment processing time
- ✅ Error frequency
- ✅ User activation success rate

### **Set Up Alerts:**
- Monitor webhook failure rates
- Alert on payment processing errors
- Track subscription activation success

## ✅ **Success Indicators**

### **When Webhooks Are Working:**
- ✅ Payments are processed automatically
- ✅ User memberships are activated immediately
- ✅ Subscription changes are reflected instantly
- ✅ No manual intervention needed
- ✅ Logs show successful processing

Your PayPal webhooks are now properly configured for automated payment processing! 🎉

## 🚀 **Next Steps:**

1. **Test with sandbox accounts first**
2. **Verify all webhook events work**
3. **Monitor logs for any issues**
4. **Switch to live mode when ready**
5. **Set up monitoring and alerts**