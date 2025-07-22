# ⚡ Quick Start Guide - Stock Scanner Platform

## 🚀 **Get Running in 5 Minutes**

### **Prerequisites:**
- Python 3.8+ installed
- Git installed
- Internet connection

---

## 📦 **Option 1: Automated Setup (Recommended)**

```bash
# 1. Clone the repository
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# 2. Run the automated setup script
./startup.sh

# 3. That's it! 🎉
# Django Admin: http://localhost:8000/admin
# Analytics API: http://localhost:8000/api/analytics/public/
# Stock API: http://localhost:8000/api/stocks/
```

---

## 🛠️ **Option 2: Manual Setup**

```bash
# 1. Clone and navigate
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env with your email settings (optional for testing)

# 5. Setup database
python manage.py migrate
python manage.py setup_memberships
python manage.py createsuperuser

# 6. Start the server
python manage.py runserver
```

---

## 🧪 **Testing Your Installation**

### **1. Test Django Admin:**
- Visit: http://localhost:8000/admin
- Login with your superuser credentials
- Check: Stocks → Memberships (should see user memberships)

### **2. Test Analytics API:**
```bash
curl http://localhost:8000/api/analytics/public/
# Should return JSON with member stats
```

### **3. Test Stock Data API:**
```bash
curl http://localhost:8000/api/stocks/
# Should return paginated stock data
```

### **4. Test Stock Lookup:**
```bash
curl http://localhost:8000/api/stocks/lookup/AAPL/
# Should return detailed Apple stock information
```

---

## 📊 **What's Included**

### **✅ Backend Features:**
- **4-Tier Membership System**: Free (15 lookups), Basic ($9.99), Professional ($29.99), Expert ($49.99)
- **Real-Time Analytics**: Live member counts and revenue calculations
- **Stock Data APIs**: Advanced filtering, lookup, news integration
- **Email System**: Subscription management and notifications
- **Admin Dashboard**: Complete membership and analytics management

### **✅ WordPress Integration:**
- **24 Professional Pages**: Complete website structure
- **Live Stock Widgets**: Real-time data from Django backend
- **Email Signup Forms**: Working backend integration
- **Modern Design**: Responsive CSS with professional styling

### **✅ Business Features:**
- **Sales Tax System**: Automatic calculation for all 50 US states + DC
- **Usage Tracking**: Monthly limits per membership tier
- **Revenue Analytics**: Real-time business intelligence
- **Stripe Ready**: Payment processing integration prepared

---

## 🔧 **Configuration Options**

### **Environment Variables (.env):**
```bash
# Core Settings
SECRET_KEY=your-secret-key
DEBUG=True

# Email Configuration (for notifications)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# API Settings
API_RATE_LIMIT=60
CACHE_TIMEOUT=300
MAX_STOCKS_PER_REQUEST=50
```

### **Membership System:**
- **Automatic Creation**: New users get free memberships automatically
- **Usage Limits**: API calls tracked per user per month
- **Admin Management**: Full CRUD via Django admin

---

## 🌐 **API Endpoints**

### **Analytics:**
- `GET /api/analytics/public/` - Public member statistics
- `GET /api/analytics/members/` - Admin-only detailed analytics

### **Stock Data:**
- `GET /api/stocks/` - List all stocks (paginated)
- `GET /api/stocks/filter/` - Advanced filtering
- `GET /api/stocks/lookup/<ticker>/` - Detailed stock information
- `GET /api/news/?ticker=<TICKER>` - Live news for specific stock

### **User Management:**
- `POST /api/email-signup/` - Email subscription
- `POST /api/wordpress/subscribe/` - WordPress integration

---

## 🎯 **Next Steps**

### **For Development:**
1. **Customize Settings**: Edit `stockscanner_django/settings.py`
2. **Add Features**: Extend models in `stocks/models.py`
3. **Create APIs**: Add views in `stocks/api_views.py`
4. **Test Changes**: Use Django admin and API endpoints

### **For Production:**
1. **Follow Production Guide**: See `PRODUCTION_DEPLOYMENT_GUIDE.md`
2. **Configure Domain**: Set up DNS for retailtradescanner.com
3. **SSL Certificates**: Install Let's Encrypt certificates
4. **Database**: Switch to PostgreSQL
5. **WordPress**: Deploy frontend with plugin and theme

### **For WordPress Integration:**
1. **Copy Plugin**: `wordpress_plugin/stock-scanner-integration/`
2. **Copy Theme**: `wordpress_theme/stock-scanner-theme/`
3. **Configure API**: Set Django API URL in WordPress settings
4. **Import Pages**: Use included XML export

---

## 🐛 **Troubleshooting**

### **Common Issues:**

**ImportError or ModuleNotFoundError:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**Database Errors:**
```bash
# Reset database (development only)
rm db.sqlite3
python manage.py migrate
python manage.py setup_memberships
```

**Permission Errors:**
```bash
# Make startup script executable
chmod +x startup.sh
```

**API Not Working:**
```bash
# Check Django server is running
python manage.py runserver
# Test with curl or browser
curl http://localhost:8000/api/analytics/public/
```

### **Email Issues:**
- **Gmail**: Use App Password, not regular password
- **SMTP**: Verify EMAIL_HOST settings in .env
- **Testing**: Email is optional for basic functionality

---

## 📚 **Additional Resources**

- **Complete Documentation**: `README.md`
- **Production Deployment**: `PRODUCTION_DEPLOYMENT_GUIDE.md`
- **Development Guide**: `DEVELOPMENT_GUIDE.md`
- **WordPress Integration**: `WORDPRESS_DJANGO_CONNECTION.md`
- **Analytics System**: `REAL_DATA_ANALYTICS.md`

---

## ✅ **Success Indicators**

You know everything is working when:

1. **Django Admin** loads and shows membership data
2. **Analytics API** returns real member statistics
3. **Stock APIs** return live stock data
4. **No errors** in terminal when running server
5. **Database migrations** complete successfully

---

## 🎉 **You're Ready!**

Your Stock Scanner platform is now running with:
- ✅ **Real member analytics** (no fake data)
- ✅ **4-tier membership system** with usage tracking
- ✅ **Live stock data** via yfinance integration
- ✅ **Professional APIs** for WordPress integration
- ✅ **Admin dashboard** for business management

**Start building your stock scanning business!** 🚀

Need help? Check the troubleshooting section above or review the detailed documentation files.
