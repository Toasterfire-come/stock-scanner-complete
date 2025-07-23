# 🪟 Stock Scanner - Windows Setup Guide

**Complete setup guide for Windows users with all common issues resolved.**

---

## 📋 **REQUIREMENTS**

- **Windows 10/11**
- **Python 3.8+** (we recommend Python 3.11 or 3.12)
- **Git** (for cloning the repository)
- **Visual Studio Code** (recommended)

---

## 🚀 **QUICK START (5 Minutes)**

### **Step 1: Clone Repository**
```cmd
# Open Command Prompt or PowerShell
cd Desktop
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete
```

### **Step 2: Create Virtual Environment**
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation (should show (venv) in prompt)
```

### **Step 3: Run Windows Installer**
```cmd
# Run the Windows-specific installer
python windows_fix_install.py
```

### **Step 4: Test Django**
```cmd
# Test Django configuration
python test_django_startup.py

# Run migrations (use our migration runner for best results)
python run_migrations.py

# Start development server
python manage.py runserver
```

### **Step 5: Access Your Platform**
Open browser: **http://localhost:8000**

---

## 🔧 **DETAILED SETUP**

### **1. Prerequisites Installation**

#### **Install Python:**
1. Download from: https://python.org/downloads/
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

#### **Install Git:**
1. Download from: https://git-scm.com/download/windows
2. Use default settings during installation
3. Verify: `git --version`

### **2. Project Setup**

#### **Clone Repository:**
```cmd
# Navigate to desired directory
cd C:\Users\%USERNAME%\Desktop

# Clone the project
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete
```

#### **Virtual Environment:**
```cmd
# Create virtual environment
python -m venv venv

# Activate (IMPORTANT: Run this every time you work on the project)
venv\Scripts\activate

# Verify activation - prompt should show (venv)
```

### **3. Package Installation**

#### **Option A: Automated Windows Installer (RECOMMENDED)**
```cmd
python windows_fix_install.py
```

**Features:**
- ✅ Handles Windows compilation issues
- ✅ Uses binary wheels for data packages
- ✅ Multiple fallback strategies
- ✅ Automatic error recovery

#### **Option B: Manual Installation**
```cmd
# Install essential packages first
pip install --upgrade pip setuptools wheel

# Install Windows-specific requirements
pip install -r requirements-windows.txt

# If NumPy/Pandas fail, install separately:
pip install --only-binary=all numpy pandas
```

### **4. Django Configuration**

#### **Test Django Setup:**
```cmd
# Test Django configuration step-by-step
python test_django_startup.py
```

**Expected output:**
```
🔍 Django Startup Test
==============================
1️⃣ Checking environment...
   Python: 3.11.x
   ✅ Environment OK

2️⃣ Setting Django settings module...
   ✅ Settings module set

3️⃣ Creating logs directory...
   ✅ Logs directory created

4️⃣ Testing Django import...
   ✅ Django version: 5.1.x

5️⃣ Testing settings import...
   ✅ Settings imported
   Debug mode: True

6️⃣ Testing Django setup...
   ✅ Django setup completed

7️⃣ Testing management commands...
   ✅ System check passed

8️⃣ Testing database connection...
   ✅ Database connection successful

🎉 Django startup test completed successfully!
```

#### **Run Database Migrations:**
```cmd
# Use our migration runner (handles Celery Beat dependency issues)
python run_migrations.py

# Or run manually:
python manage.py makemigrations
python manage.py migrate
```

#### **Create Superuser (Optional):**
```cmd
python manage.py createsuperuser
```

### **5. Start Development Server**

```cmd
# Start the Django development server
python manage.py runserver

# Server will start at: http://localhost:8000
# Admin panel: http://localhost:8000/admin
```

---

## 🛠️ **TROUBLESHOOTING**

### **Common Issues & Solutions**

#### **❌ "ModuleNotFoundError: No module named 'pkg_resources'"**
**Solution:**
```cmd
pip install setuptools wheel
python windows_fix_install.py
```

#### **❌ NumPy compilation errors (C compiler not found)**
**Solution:**
```cmd
# Use binary wheels only
pip install --only-binary=all numpy pandas
```

#### **❌ "Unable to configure handler 'file'"**
**Solution:** Fixed automatically by our logging configuration

#### **❌ Virtual environment not activating**
**Solution:**
```cmd
# Try PowerShell instead of Command Prompt
# Or use full path:
C:\path\to\project\venv\Scripts\activate
```

#### **❌ Permission errors during installation**
**Solution:**
```cmd
# Run as administrator or use user install
pip install --user -r requirements-windows.txt
```

#### **❌ Django migration errors (Celery Beat tables)**
**Solution:**
```cmd
# Use our migration runner (handles order correctly)
python run_migrations.py

# Or run manually in order:
python manage.py migrate contenttypes
python manage.py migrate auth
python manage.py migrate django_celery_beat
python manage.py migrate
```

### **Windows-Specific Notes**

#### **File Paths:**
- Use forward slashes `/` or double backslashes `\\` in settings
- Avoid spaces in directory names

#### **Antivirus:**
- Add project folder to antivirus exclusions
- Windows Defender might slow down pip installs

#### **PowerShell vs Command Prompt:**
- Both work, but PowerShell is recommended
- Some commands might need different syntax

---

## 📁 **PROJECT STRUCTURE**

```
stock-scanner-complete/
├── 📁 core/                 # Main Django app
├── 📁 stocks/               # Stock data management
├── 📁 emails/               # Email notifications
├── 📁 news/                 # News scraping
├── 📁 stockscanner_django/  # Django project settings
├── 📄 manage.py             # Django management script
├── 📄 requirements.txt      # Python packages
├── 📄 requirements-windows.txt  # Windows-safe packages
├── 📄 windows_fix_install.py   # Windows installer
├── 📄 test_django_startup.py   # Django test script
├── 📄 run_migrations.py        # Migration runner (fixes Celery Beat)
└── 📄 .env.example         # Environment variables template
```

---

## ⚙️ **CONFIGURATION**

### **Environment Variables**

1. **Copy environment template:**
   ```cmd
   copy .env.example .env
   ```

2. **Edit .env file** with your API keys:
   ```
   # Yahoo Finance (Primary - Free)
   YFINANCE_RATE_LIMIT=1.0
   
   # Finnhub (Backup)
   FINNHUB_API_KEY_1=your_finnhub_key_here
   FINNHUB_API_KEY_2=your_second_finnhub_key_here
   
   # Database (Development uses SQLite by default)
   # DATABASE_URL=postgresql://user:pass@localhost/dbname
   
   # WordPress Integration (Optional)
   WORDPRESS_SITE_URL=https://yoursite.com
   WORDPRESS_USERNAME=your_username
   WORDPRESS_PASSWORD=your_app_password
   ```

### **API Keys Setup**

#### **Finnhub (Free Backup API):**
1. Register at: https://finnhub.io/
2. Get free API key (1000 calls/day)
3. Add to .env file

#### **WordPress (Optional):**
1. Generate application password in WordPress
2. Add credentials to .env file

---

## 🧪 **TESTING**

### **Run System Tests**
```cmd
# Test stock data system
python test_yfinance_system.py

# Test Django functionality
python test_django_startup.py

# Run Django's built-in tests
python manage.py test
```

### **Verify Installation**
```cmd
# Check Django configuration
python manage.py check

# Verify database
python manage.py dbshell

# Test API manager
python -c "from stocks.api_manager import stock_manager; print(stock_manager.get_usage_stats())"
```

---

## 🚀 **DEVELOPMENT WORKFLOW**

### **Daily Development**
```cmd
# 1. Navigate to project
cd C:\path\to\stock-scanner-complete

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Pull latest changes
git pull origin main

# 4. Install any new packages
pip install -r requirements-windows.txt

# 5. Run migrations if needed
python manage.py migrate

# 6. Start development server
python manage.py runserver
```

### **Making Changes**
```cmd
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files for production
python manage.py collectstatic
```

---

## 📊 **PERFORMANCE OPTIMIZATION**

### **Rate Limiting Optimization**
```cmd
# Test and optimize Yahoo Finance rate limits
python yahoo_rate_limit_optimizer.py
```

### **Database Optimization**
```cmd
# Apply database migrations
python apply_yfinance_migrations.py
```

---

## 🔒 **SECURITY NOTES**

- Never commit `.env` file to Git
- Use strong passwords for database and admin accounts
- Keep API keys secure
- Use HTTPS in production
- Regular security updates: `pip install --upgrade django`

---

## 📞 **SUPPORT**

### **Getting Help**

1. **Check logs:** Look in `logs/django.log`
2. **Run diagnostics:** `python test_django_startup.py`
3. **Check Django:** `python manage.py check`
4. **Verify packages:** Check if imports work

### **Common Commands Reference**

```cmd
# Virtual Environment
venv\Scripts\activate              # Activate
venv\Scripts\deactivate           # Deactivate

# Django Management
python manage.py runserver         # Start development server
python manage.py migrate          # Apply database migrations
python manage.py createsuperuser  # Create admin user
python manage.py collectstatic    # Collect static files
python manage.py shell           # Django shell

# Package Management
pip install package_name          # Install package
pip install -r requirements.txt   # Install from requirements
pip freeze > requirements.txt     # Save current packages
pip list                          # List installed packages
```

---

## 🎉 **SUCCESS!**

If you've followed this guide, you should now have:

✅ **Working Django development server**  
✅ **Stock data API integration**  
✅ **Database connectivity**  
✅ **Web interface accessible**  
✅ **All Windows compatibility issues resolved**  

**🌐 Access your platform at: http://localhost:8000**

---

**Happy coding! 🚀**