# PayPal Settings Integration

## ✅ **PayPal Settings Now in Main Stock Scanner Settings**

The PayPal configuration has been moved from a separate settings page to the main Stock Scanner settings page for better organization and easier access.

## 📍 **Where to Find PayPal Settings**

**WordPress Admin → Settings → Stock Scanner**

The settings page now has two sections:

### **1. API Configuration**
- Django API URL

### **2. PayPal Configuration**
- PayPal Mode (Sandbox/Live)
- Client ID
- Client Secret
- Webhook URL
- Return URL
- Cancel URL

## 🔧 **What Changed**

### **Before:**
- Separate "PayPal Settings" menu item
- PayPal settings in their own page
- Two different settings pages to manage

### **After:**
- All settings in one place
- Single settings page
- Better organization
- Easier to manage

## 📋 **PayPal Settings Fields**

| Field | Description | Required |
|-------|-------------|----------|
| **PayPal Mode** | Sandbox for testing, Live for production | ✅ Yes |
| **Client ID** | Your PayPal App Client ID from Developer Dashboard | ✅ Yes |
| **Client Secret** | Your PayPal App Client Secret from Developer Dashboard | ✅ Yes |
| **Webhook URL** | URL for PayPal webhooks (auto-generated) | ✅ Yes |
| **Return URL** | Where users return after successful payment | ✅ Yes |
| **Cancel URL** | Where users return after cancelled payment | ✅ Yes |

## 🚀 **How to Configure**

### **Step 1: Get PayPal Credentials**
1. Go to [PayPal Developer Dashboard](https://developer.paypal.com/)
2. Create a new app or use existing app
3. Copy Client ID and Client Secret

### **Step 2: Configure in WordPress**
1. Go to **WordPress Admin → Settings → Stock Scanner**
2. Fill in PayPal settings:
   - **Mode:** Sandbox (for testing) or Live (for production)
   - **Client ID:** Your PayPal App Client ID
   - **Client Secret:** Your PayPal App Client Secret
   - **Webhook URL:** Copy the URL shown in the description
   - **Return URL:** Your success page URL
   - **Cancel URL:** Your cancel page URL

### **Step 3: Configure PayPal Webhook**
1. Go to PayPal Developer Dashboard
2. Add the webhook URL shown in WordPress settings
3. Select events: `PAYMENT.CAPTURE.COMPLETED`, `BILLING.SUBSCRIPTION.ACTIVATED`

## 🔍 **Testing PayPal Integration**

### **Sandbox Testing:**
1. Set PayPal Mode to "Sandbox"
2. Use PayPal sandbox accounts for testing
3. Test payment flow end-to-end

### **Live Production:**
1. Set PayPal Mode to "Live"
2. Use real PayPal accounts
3. Ensure all URLs are correct

## 📊 **Membership Plans**

The plugin supports these membership tiers:

| Plan | Monthly | Annual |
|------|---------|--------|
| **Bronze** | $14.99 | $143.88 |
| **Silver** | $29.99 | $287.88 |
| **Gold** | $59.99 | $575.88 |

## 🛡️ **Security Notes**

- Client Secret is stored as password field (hidden)
- All URLs are sanitized before saving
- Webhook verification is implemented
- Payment logging is enabled

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **"Invalid Client ID"**
   - Check Client ID and Secret are correct
   - Ensure you're using the right mode (Sandbox/Live)

2. **"Webhook not working"**
   - Verify webhook URL in PayPal Dashboard
   - Check webhook events are selected

3. **"Payment not completing"**
   - Check Return URL and Cancel URL
   - Verify PayPal app permissions

### **Debug Commands:**
```bash
# Check PayPal logs
tail -f wp-content/paypal_payments.log
tail -f wp-content/paypal_errors.log
```

## ✅ **Success Checklist**

- [ ] PayPal Mode set correctly
- [ ] Client ID and Secret entered
- [ ] Webhook URL configured in PayPal Dashboard
- [ ] Return and Cancel URLs set
- [ ] Test payment completed successfully
- [ ] Webhook events working
- [ ] Membership activation working

Your PayPal integration is now centralized and easier to manage! 🎉