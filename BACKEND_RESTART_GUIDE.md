# 🔧 Backend Restart Guide - api.tradescanpro.com

**Date:** November 7, 2025
**Critical:** Backend configuration updated to support `api.tradescanpro.com`

---

## 🎯 What Was Fixed

The backend was configured ONLY for `api.retailtradescanner.com`, causing 503 errors when the frontend tried to connect to `api.tradescanpro.com`.

### Files Updated:
1. ✅ **`backend/cloudflared_config.yml`** - Cloudflare tunnel ingress rules
2. ✅ **`backend/.env`** - Production Django configuration
3. ✅ **`backend/.env.example`** - Template configuration

### Changes Made:

**Cloudflare Tunnel:**
- Added `api.tradescanpro.com` as primary hostname
- Kept `api.retailtradescanner.com` for legacy support
- Both domains now route to `http://localhost:8000`

**Django Settings:**
```bash
# Before:
DJANGO_ALLOWED_HOSTS=...,tradescanpro.com,www.tradescanpro.com
CSRF_TRUSTED_ORIGINS=https://api.retailtradescanner.com,...

# After:
DJANGO_ALLOWED_HOSTS=...,api.tradescanpro.com,api.retailtradescanner.com
CSRF_TRUSTED_ORIGINS=...,https://api.tradescanpro.com
```

---

## 🚀 Restart Backend Services (REQUIRED)

You **MUST** restart the backend services for these changes to take effect:

### Step 1: Restart Cloudflare Tunnel

```bash
# Stop the tunnel
pkill cloudflared
# OR
sudo systemctl stop cloudflared

# Start with updated config
cd /home/user/stock-scanner-complete/backend
cloudflared tunnel --config cloudflared_config.yml run django-api

# OR if using systemd service:
sudo systemctl restart cloudflared
```

### Step 2: Restart Django Application

```bash
# If using gunicorn:
pkill gunicorn
cd /home/user/stock-scanner-complete/backend
gunicorn stockscanner_django.wsgi:application --bind 127.0.0.1:8000 --workers 4 --daemon

# If using systemd:
sudo systemctl restart stockscanner
# OR
sudo systemctl restart django

# If using manage.py runserver (dev):
pkill -f "manage.py runserver"
python manage.py runserver 8000
```

### Step 3: Verify Services Are Running

```bash
# Check if tunnel is running
ps aux | grep cloudflared

# Check if Django is running
ps aux | grep gunicorn
# OR
ps aux | grep "manage.py"

# Check if port 8000 is listening
netstat -tlnp | grep 8000
# OR
ss -tlnp | grep 8000
```

---

## ✅ Verify Backend Is Working

After restarting, test from your local machine:

### Test 1: Root Endpoint
```bash
curl https://api.tradescanpro.com/
# Should return: Django application response (NOT "DNS resolution failure")
```

### Test 2: Health Check
```bash
curl https://api.tradescanpro.com/api/health/
# Should return: {"status": "healthy"} or similar
```

### Test 3: Meta Endpoint
```bash
curl https://api.tradescanpro.com/api/meta/
# Should return: JSON with API metadata
```

### Test 4: Headers Check
```bash
curl -I https://api.tradescanpro.com/api/meta/
# Should return: HTTP 200 (NOT 503)
```

---

## 🔍 Troubleshooting

### Issue: Still getting "DNS resolution failure"

**Cause:** Cloudflare tunnel not restarted with new config

**Solution:**
```bash
# Force kill all cloudflared processes
sudo pkill -9 cloudflared

# Wait 5 seconds
sleep 5

# Restart with correct config
cd /home/user/stock-scanner-complete/backend
cloudflared tunnel --config cloudflared_config.yml run django-api
```

### Issue: 403 Forbidden

**Cause:** Django ALLOWED_HOSTS not updated or Django not restarted

**Solution:**
```bash
# Verify .env has correct ALLOWED_HOSTS
grep ALLOWED_HOSTS backend/.env

# Should include: api.tradescanpro.com

# Restart Django
sudo systemctl restart django
# OR kill and restart manually
```

### Issue: Connection refused

**Cause:** Django not running on port 8000

**Solution:**
```bash
# Check what's on port 8000
sudo lsof -i :8000

# If nothing, start Django:
cd /home/user/stock-scanner-complete/backend
python manage.py runserver 8000
```

### Issue: Tunnel not connecting

**Cause:** Cloudflare credentials or tunnel name mismatch

**Solution:**
```bash
# Check tunnel exists in Cloudflare
cloudflared tunnel list

# Should show: django-api tunnel

# If not, you may need to create CNAME record:
# api.tradescanpro.com -> <tunnel-id>.cfargotunnel.com
```

---

## 📋 Backend Service Scripts

Available scripts in `/home/user/stock-scanner-complete/backend/`:

- `start_tunnel.sh` - Start Cloudflare tunnel
- `start_complete_system.sh` - Start all services
- `run_production.sh` - Start Django in production mode
- `setup_cloudflare_tunnel.sh` - Setup tunnel (first time)

**Recommended: Use these scripts to start services**

```bash
cd /home/user/stock-scanner-complete/backend

# Start tunnel
./start_tunnel.sh

# In another terminal, start Django
./run_production.sh
```

---

## 🔒 Cloudflare DNS Configuration

Make sure your Cloudflare DNS has the correct records:

### Required DNS Records:

**For Cloudflare Tunnel:**
```
Type: CNAME
Name: api.tradescanpro.com
Target: <tunnel-id>.cfargotunnel.com
Proxied: Yes (orange cloud)
```

**Alternative (if not using tunnel):**
```
Type: A
Name: api.tradescanpro.com
Value: <your-server-ip>
Proxied: Yes
```

To get your tunnel ID:
```bash
cloudflared tunnel list
```

---

## 📊 Configuration Reference

### Current Tunnel Configuration

**File:** `backend/cloudflared_config.yml`

**Hostnames configured:**
- `api.tradescanpro.com` (primary)
- `api.retailtradescanner.com` (legacy)

**Backend service:** `http://localhost:8000` (Django)

### Current Django Configuration

**File:** `backend/.env`

**Allowed Hosts:**
- `localhost`, `127.0.0.1`
- `api.tradescanpro.com` ✅ NEW
- `api.retailtradescanner.com` ✅ NEW
- `api.retailtradescannet.com`
- `tradescanpro.com`, `www.tradescanpro.com`
- `retailtradescannet.com`

**CSRF Trusted Origins:**
- `https://api.tradescanpro.com` ✅ NEW
- `https://api.retailtradescanner.com`
- `https://tradescanpro.com`
- `https://www.tradescanpro.com`

---

## ⚡ Quick Restart Commands

If you're in a hurry, run these:

```bash
# Option 1: Kill and restart everything
sudo pkill cloudflared && sleep 2 && \
cd /home/user/stock-scanner-complete/backend && \
cloudflared tunnel --config cloudflared_config.yml run django-api &

sudo pkill gunicorn && sleep 2 && \
cd /home/user/stock-scanner-complete/backend && \
gunicorn stockscanner_django.wsgi:application --bind 127.0.0.1:8000 --workers 4 --daemon

# Option 2: Use systemd
sudo systemctl restart cloudflared && \
sudo systemctl restart django
```

---

## 🎯 Success Checklist

After restart, verify:

- [ ] Cloudflare tunnel is running (`ps aux | grep cloudflared`)
- [ ] Django is running on port 8000 (`netstat -tlnp | grep 8000`)
- [ ] `curl https://api.tradescanpro.com/` returns data (not 503)
- [ ] `curl https://api.tradescanpro.com/api/meta/` returns JSON
- [ ] No "DNS resolution failure" errors
- [ ] Frontend can connect (test at https://tradescanpro.com)

---

## 📝 Post-Restart: Deploy Frontend

Once backend is verified working:

```bash
cd /home/user/stock-scanner-complete
python3 deploy_sftp_complete.py --no-pull --no-build
```

This will deploy the frontend that's already configured for `api.tradescanpro.com`.

---

## 💡 Why This Was Needed

**Before:**
```
Frontend → api.tradescanpro.com → 503 DNS resolution failure
         (Tunnel not configured for this hostname)

Tunnel only accepted: api.retailtradescanner.com
```

**After:**
```
Frontend → api.tradescanpro.com → Tunnel accepts → Django → Success! ✅

Tunnel accepts both:
  - api.tradescanpro.com (primary)
  - api.retailtradescanner.com (legacy)
```

---

## 🆘 Getting Help

If backend still doesn't work after restart:

1. Check Cloudflare tunnel logs: `cloudflared tunnel info django-api`
2. Check Django logs: `tail -f /path/to/django.log`
3. Check systemd logs: `sudo journalctl -u cloudflared -f`
4. Verify Cloudflare DNS: Go to Cloudflare dashboard → DNS records
5. Test from server: `curl http://localhost:8000/api/meta/`

**Once backend returns 200 instead of 503, your website will work!** 🎉
