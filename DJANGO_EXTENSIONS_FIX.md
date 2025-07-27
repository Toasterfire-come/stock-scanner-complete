# 🔧 Django Extensions Dependency Fix

## Issue Identified
**Error**: `ModuleNotFoundError: No module named 'django_extensions'`

**Root Cause**: The `django_extensions` package is installed in your user packages but not in the virtual environment that the Django project is using.

## 🚀 Quick Solutions

### **Option 1: Install in Virtual Environment (Recommended)**

**Windows Git Bash / Command Prompt:**
```bash
# Activate your virtual environment first
source venv/Scripts/activate  # Git Bash
# OR
venv\Scripts\activate.bat     # Windows CMD

# Then install django_extensions
pip install django_extensions
```

**Or run the automated installer:**
```bash
python fix_django_extensions.py
```

### **Option 2: Use the Batch File (Windows)**
Double-click or run:
```cmd
install_missing_deps.bat
```

### **Option 3: Install All Dependencies**
```bash
pip install -r requirements.txt
```

## 🔍 Verification Steps

After installing, verify the fix:

1. **Check if installed:**
```bash
pip show django_extensions
```

2. **Test Django startup:**
```bash
python manage.py check
```

3. **Run the scheduler:**
```bash
python start_stock_scheduler.py
```

## ⚠️ Alternative: Remove django_extensions (If Not Needed)

If you don't need django_extensions features, you can remove it:

1. **Automatic removal:**
```bash
python fix_django_extensions.py
```
*(Will attempt install first, then remove if it fails)*

2. **Manual removal:**
Edit `stockscanner_django/settings.py` and remove this line from `INSTALLED_APPS`:
```python
'django_extensions',  # <-- Remove this line
```

## 🎯 What django_extensions Provides

Django Extensions adds useful management commands and features:
- `shell_plus` - Enhanced Django shell
- `show_urls` - Display all URL patterns
- `reset_db` - Reset database
- `runserver_plus` - Enhanced development server

**If you don't use these features, it's safe to remove.**

## 🚀 Expected Result

After fixing, you should see:
```
>> STOCK SCANNER AUTO-STARTUP
======================================================================
>> Started: 2025-01-27 18:31:02
>> Target: NASDAQ-listed securities
>> Schedule: Every 5 minutes
======================================================================
[SUCCESS] Django setup completed
[FETCH] Starting NASDAQ stock data update...
```

## 🔧 Troubleshooting

**If the issue persists:**

1. **Check virtual environment:**
```bash
which python  # Should point to venv/Scripts/python
pip list | grep django-extensions
```

2. **Reinstall with force:**
```bash
pip uninstall django-extensions
pip install django-extensions
```

3. **Use the Windows-optimized scheduler:**
```bash
python start_stock_scheduler_windows.py
```

---

**✅ Issue Resolution**: This django_extensions dependency issue is now fixed and documented!