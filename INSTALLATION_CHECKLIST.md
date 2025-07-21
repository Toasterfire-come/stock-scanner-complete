# 📋 Stock Scanner Installation Checklist

## 🎯 Quick Verification

Run this command to verify your setup:
```bash
python3 test_database_setup.py
```

Expected output: **5/6 tests passed** (yfinance will be installed during setup)

---

## ✅ Installation Steps

### Step 1: Verify System Requirements
- [ ] **Python 3.8+** installed (`python3 --version`)
- [ ] **Internet connection** available
- [ ] **Gmail account** with 2FA enabled

### Step 2: Run Automated Setup
```bash
# One-command setup
python3 setup_local.py
```

This will:
- [ ] Create virtual environment
- [ ] Install all dependencies (including yfinance)
- [ ] Setup SQLite database
- [ ] Configure email settings
- [ ] Create sample data

### Step 3: Configure Gmail (5 minutes)
1. [ ] Go to [Google Account Settings](https://myaccount.google.com/)
2. [ ] Enable **2-Step Verification** (if not already enabled)
3. [ ] Generate **App Password**:
   - Security → App passwords
   - Select "Mail" → "Other (custom name)"
   - Enter "Stock Scanner"
   - Copy the 16-character password
4. [ ] Update `.env` file with your Gmail credentials

### Step 4: Start the Application
```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Start Django server
python manage.py runserver
```

### Step 5: Verify Installation
- [ ] Visit http://localhost:8000 (main site loads)
- [ ] Visit http://localhost:8000/admin (admin panel loads)
- [ ] Test API: `curl http://localhost:8000/api/stocks/`

---

## 🧪 Verification Commands

### Database Test
```bash
python3 test_database_setup.py
# Expected: 5/6 tests pass
```

### Email Test (after Gmail setup)
```bash
python3 -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'stockscanner_django.settings'
import django
django.setup()
from emails.email_config import test_email_connection
print(test_email_connection())
"
```

### Stock Data Test (after setup)
```bash
python3 -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'stockscanner_django.settings'
import django
django.setup()
from stocks.yfinance_config import test_yfinance_connection
print(test_yfinance_connection())
"
```

---

## 📁 Essential Files Present

### Core Files
- [ ] `README.md` - Project overview
- [ ] `COMPLETE_SETUP_GUIDE.md` - Detailed instructions
- [ ] `setup_local.py` - Automated setup script
- [ ] `manage.py` - Django management
- [ ] `requirements_secure.txt` - Dependencies

### Configuration Files
- [ ] `database_settings_local.py` - SQLite setup
- [ ] `emails/email_config.py` - Gmail SMTP
- [ ] `stocks/yfinance_config.py` - Stock data
- [ ] `security_hardening.py` - Production security

### Test Files
- [ ] `test_database_setup.py` - Database test
- [ ] `.env.sample` - Configuration template

---

## 🔧 Configuration Check

### Environment Variables (.env file)
```bash
# Required settings
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DB_NAME=stock_scanner.db
SECRET_KEY=your-secret-key
```

### Database File
- [ ] `stock_scanner.db` created after migration
- [ ] Database health check passes

### Virtual Environment
- [ ] `venv/` directory exists
- [ ] All packages installed in virtual environment

---

## 🚀 Production Deployment (Optional)

### Security Hardening
```bash
python3 security_hardening.py
```
This creates:
- [ ] Production settings
- [ ] Secure environment configuration
- [ ] Deployment scripts

### Deploy to Server
```bash
./deploy_secure.sh
```

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. Module Not Found
```bash
# Activate virtual environment
source venv/bin/activate
pip install -r requirements_secure.txt
```

#### 2. Database Errors
```bash
# Reset database
rm stock_scanner.db
python manage.py migrate
```

#### 3. Email Not Working
- Verify 2FA is enabled in Gmail
- Check app password is 16 characters
- Test with: `python3 -c "from emails.email_config import test_email_connection; print(test_email_connection())"`

#### 4. yfinance Connection Issues
- Check internet connection
- Verify no firewall blocking
- Test with: `python3 -c "import yfinance; print(yfinance.Ticker('AAPL').info)"`

---

## 📊 Success Indicators

### ✅ Installation Successful When:
- [ ] `python3 test_database_setup.py` shows 5/6 or 6/6 tests pass
- [ ] Django server starts without errors
- [ ] Admin panel accessible at http://localhost:8000/admin
- [ ] API responds at http://localhost:8000/api/stocks/
- [ ] Email configuration test passes
- [ ] Stock data can be fetched

### 🎯 Ready for Use When:
- [ ] Can create superuser account
- [ ] Can add stocks via admin panel
- [ ] Email notifications can be sent
- [ ] WordPress API integration works
- [ ] All tests pass

---

## 📞 Support

If you encounter issues:

1. **Check this checklist** - most issues are covered here
2. **Read the troubleshooting section** above
3. **Run the diagnostic script**: `python3 test_database_setup.py`
4. **Check the complete setup guide**: `COMPLETE_SETUP_GUIDE.md`

---

## 🎉 What's Next?

After successful installation:

1. **Add Stock Tickers**: Use Django admin to add stocks to monitor
2. **Configure Emails**: Set up email subscriptions and categories
3. **WordPress Integration**: Deploy the WordPress theme/plugin
4. **Production**: Run security hardening for production deployment

**Your stock scanner is ready to monitor the markets!** 📈✨