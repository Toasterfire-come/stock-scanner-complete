# Django API External Access Guide

## 🎯 **Making Your Django API Accessible from WordPress**

This guide shows you how to make your Django API accessible from your hosted WordPress site while keeping it secure.

## 🔧 **Option 1: Port Forwarding (Recommended for Development)**

### **Step 1: Find Your Computer's IP Address**

**Windows:**
```bash
ipconfig
```
Look for "IPv4 Address" (usually 192.168.x.x)

**Mac/Linux:**
```bash
ifconfig
# or
ip addr show
```

### **Step 2: Configure Django for External Access**

**Update `stockscanner_django/settings.py`:**
```python
# Add your computer's IP to ALLOWED_HOSTS
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'YOUR_COMPUTER_IP',  # Replace with your actual IP
    '0.0.0.0',  # Allow all IPs (less secure)
]

# Update CORS settings
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://YOUR_WORDPRESS_DOMAIN.com',  # Replace with your WordPress domain
    'http://YOUR_WORDPRESS_DOMAIN.com',   # Replace with your WordPress domain
]
```

### **Step 3: Start Django Server for External Access**

```bash
# Start Django on all interfaces
python3 manage.py runserver 0.0.0.0:8000
```

### **Step 4: Configure Port Forwarding**

**Router Configuration:**
1. Log into your router admin (usually 192.168.1.1)
2. Find "Port Forwarding" or "Virtual Server"
3. Add rule:
   - **External Port:** 8000
   - **Internal IP:** Your computer's IP
   - **Internal Port:** 8000
   - **Protocol:** TCP

### **Step 5: Update WordPress Plugin Settings**

**In WordPress Admin → Settings → Stock Scanner:**
```
API URL: http://YOUR_COMPUTER_IP:8000/api
```

## 🔧 **Option 2: ngrok (Easiest for Testing)**

### **Step 1: Install ngrok**
```bash
# Download from https://ngrok.com/
# or install via package manager
```

### **Step 2: Start Django Server**
```bash
python3 manage.py runserver 127.0.0.1:8000
```

### **Step 3: Create ngrok Tunnel**
```bash
ngrok http 8000
```

### **Step 4: Update WordPress Settings**
Use the ngrok URL (e.g., `https://abc123.ngrok.io/api`)

## 🔧 **Option 3: Cloudflare Tunnel (Production Ready)**

### **Step 1: Install Cloudflare Tunnel**
```bash
# Download cloudflared from https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
```

### **Step 2: Authenticate**
```bash
cloudflared tunnel login
```

### **Step 3: Create Tunnel**
```bash
cloudflared tunnel create django-api
```

### **Step 4: Configure Tunnel**
Create `~/.cloudflared/config.yml`:
```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: ~/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: api.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
```

### **Step 5: Start Tunnel**
```bash
cloudflared tunnel run django-api
```

## 🔒 **Security Considerations**

### **1. Firewall Configuration**
```bash
# Allow only specific IPs (your WordPress server)
sudo ufw allow from YOUR_WORDPRESS_SERVER_IP to any port 8000
```

### **2. API Rate Limiting**
**In `stockscanner_django/settings.py`:**
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

### **3. API Authentication (Optional)**
**Add API key authentication:**
```python
# In settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}
```

## 🚀 **Quick Setup Commands**

### **For Development (ngrok):**
```bash
# Terminal 1: Start Django
python3 manage.py runserver 127.0.0.1:8000

# Terminal 2: Start ngrok
ngrok http 8000

# Copy ngrok URL to WordPress settings
```

### **For Production (Port Forwarding):**
```bash
# 1. Find your IP
ipconfig  # Windows
ifconfig  # Mac/Linux

# 2. Start Django on all interfaces
python3 manage.py runserver 0.0.0.0:8000

# 3. Configure router port forwarding
# 4. Update WordPress API URL
```

## 📋 **WordPress Configuration**

### **Update WordPress Plugin Settings:**
1. Go to **WordPress Admin → Settings → Stock Scanner**
2. Update **Django API URL**:
   - **Development:** `https://abc123.ngrok.io/api`
   - **Production:** `http://YOUR_IP:8000/api`

### **Test Connection:**
1. Click "Test Connection" in WordPress admin
2. Check browser console for errors
3. Verify API responses

## 🔍 **Troubleshooting**

### **Common Issues:**

1. **"Connection refused"**
   - Check if Django is running on correct port
   - Verify firewall settings
   - Test with `curl http://localhost:8000/api/`

2. **"CORS error"**
   - Update CORS_ALLOWED_ORIGINS in Django settings
   - Add your WordPress domain to allowed origins

3. **"Timeout"**
   - Increase timeout in WordPress plugin settings
   - Check network connectivity
   - Verify port forwarding

### **Debug Commands:**
```bash
# Test Django API locally
curl http://localhost:8000/api/simple/stocks/

# Test from external IP
curl http://YOUR_IP:8000/api/simple/stocks/

# Check Django logs
tail -f django_api.log
```

## 📊 **Monitoring**

### **Django Logs:**
```bash
# View real-time logs
tail -f django_api.log

# Check for errors
grep ERROR django_api.log
```

### **Network Monitoring:**
```bash
# Check if port is open
netstat -tulpn | grep 8000

# Test connectivity
telnet YOUR_IP 8000
```

## 🎯 **Recommended Setup**

### **For Development:**
1. Use **ngrok** for easy testing
2. Update WordPress settings with ngrok URL
3. Test thoroughly before production

### **For Production:**
1. Use **Cloudflare Tunnel** for security
2. Set up proper firewall rules
3. Monitor logs and performance
4. Use HTTPS for all connections

## ✅ **Success Checklist**

- [ ] Django server running on external IP
- [ ] Port forwarding configured (if using router)
- [ ] CORS settings updated with WordPress domain
- [ ] WordPress plugin API URL updated
- [ ] Connection test successful
- [ ] Stock data loading in WordPress
- [ ] News feed working
- [ ] Error handling configured
- [ ] Logs being monitored

Your Django API will now be accessible from your WordPress site! 🚀