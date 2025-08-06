# Cloudflare Tunnel Setup - Hide Your Home IP

## 🛡️ **Why Cloudflare Tunnel?**

- ✅ **No IP exposure** - Your home IP stays hidden
- ✅ **Automatic HTTPS** - Secure connections
- ✅ **DDoS protection** - Built-in security
- ✅ **Free tier available** - No cost for basic use
- ✅ **Custom domain** - Use your own domain name

## 🚀 **Step-by-Step Setup**

### **Step 1: Install Cloudflare Tunnel**

**Windows:**
```bash
# Download from: https://github.com/cloudflare/cloudflared/releases
# Extract to a folder and add to PATH
```

**Mac/Linux:**
```bash
# Using package manager
brew install cloudflare/cloudflare/cloudflared  # Mac
# or download from releases page
```

### **Step 2: Authenticate with Cloudflare**

```bash
cloudflared tunnel login
```

This opens your browser. Log in to Cloudflare and authorize the tunnel.

### **Step 3: Create Your Tunnel**

```bash
cloudflared tunnel create django-api
```

This creates a tunnel and gives you a tunnel ID.

### **Step 4: Configure the Tunnel**

Create a config file: `~/.cloudflared/config.yml`

```yaml
tunnel: YOUR_TUNNEL_ID_HERE
credentials-file: ~/.cloudflared/YOUR_TUNNEL_ID_HERE.json

ingress:
  # Your Django API
  - hostname: api.yourdomain.com
    service: http://localhost:8000
  
  # Catch-all rule
  - service: http_status:404
```

### **Step 5: Start the Tunnel**

```bash
cloudflared tunnel run django-api
```

### **Step 6: Update WordPress Settings**

**In WordPress Admin → Settings → Stock Scanner:**
```
API URL: https://api.yourdomain.com/api
```

## 🔧 **Alternative: ngrok (Easier but Less Secure)**

### **Step 1: Install ngrok**
Download from: https://ngrok.com/

### **Step 2: Start Django**
```bash
python manage.py runserver 127.0.0.1:8000
```

### **Step 3: Start ngrok**
```bash
ngrok http 8000
```

### **Step 4: Use ngrok URL**
Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`) and use it in WordPress.

## 🔧 **Alternative: VPS/Cloud Server**

### **Option A: Deploy Django to VPS**
1. **Rent a VPS** (DigitalOcean, AWS, etc.)
2. **Deploy Django** to the VPS
3. **Use VPS IP** in WordPress settings

### **Option B: Reverse Proxy**
1. **Set up nginx** on VPS
2. **Proxy requests** to your home server
3. **Use VPS domain** in WordPress

## 🛡️ **Security Best Practices**

### **1. Firewall Configuration**
```bash
# Only allow Cloudflare IPs (if using tunnel)
# Cloudflare IP ranges: https://www.cloudflare.com/ips/
```

### **2. Rate Limiting**
**In Django settings:**
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
    }
}
```

### **3. API Authentication (Optional)**
```python
# Add API key authentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}
```

### **4. CORS Restrictions**
```python
CORS_ALLOWED_ORIGINS = [
    'https://yourwordpress.com',
    'https://www.yourwordpress.com',
]
```

## 📋 **Quick Setup Commands**

### **For Cloudflare Tunnel:**
```bash
# 1. Install cloudflared
# 2. Login
cloudflared tunnel login

# 3. Create tunnel
cloudflared tunnel create django-api

# 4. Configure (edit config.yml)
# 5. Start tunnel
cloudflared tunnel run django-api

# 6. Update WordPress with tunnel URL
```

### **For ngrok:**
```bash
# 1. Start Django
python manage.py runserver 127.0.0.1:8000

# 2. Start ngrok
ngrok http 8000

# 3. Copy HTTPS URL to WordPress
```

## 🔍 **Testing Your Setup**

### **Test API Access:**
```bash
# Test locally
curl http://localhost:8000/api/simple/stocks/

# Test through tunnel
curl https://api.yourdomain.com/api/simple/stocks/
```

### **Test from WordPress:**
1. Go to WordPress admin
2. Settings → Stock Scanner
3. Click "Test Connection"
4. Check browser console for errors

## 📊 **Monitoring & Logs**

### **Cloudflare Tunnel Logs:**
```bash
# View tunnel logs
cloudflared tunnel info django-api

# Check tunnel status
cloudflared tunnel list
```

### **Django Logs:**
```bash
# View Django logs
tail -f django_api.log

# Check for errors
grep ERROR django_api.log
```

## 🎯 **Recommended Setup**

### **For Production:**
1. **Use Cloudflare Tunnel** - Most secure
2. **Custom domain** - Professional appearance
3. **HTTPS only** - Secure connections
4. **Rate limiting** - Prevent abuse
5. **Monitoring** - Track usage

### **For Development:**
1. **Use ngrok** - Quick and easy
2. **Test thoroughly** - Before production
3. **Update WordPress** - With tunnel URL

## ✅ **Security Checklist**

- [ ] Home IP not exposed
- [ ] HTTPS connections only
- [ ] Rate limiting enabled
- [ ] CORS restrictions set
- [ ] Firewall configured
- [ ] Logs being monitored
- [ ] API authentication (optional)
- [ ] Regular security updates

## 🚨 **Important Notes**

1. **Cloudflare Tunnel** is the most secure option
2. **ngrok** is easier but less secure
3. **VPS deployment** removes home IP entirely
4. **Always use HTTPS** for production
5. **Monitor logs** for suspicious activity
6. **Keep software updated** regularly

Your Django API will be secure and your home IP will stay hidden! 🛡️