# Windows Machine Setup Fix

**Your Django server is crashing due to outdated code on your Windows machine.**

## ✅ Quick Fix - Pull Latest Changes

Open **Command Prompt** or **PowerShell** in your project directory:

```bash
cd C:\Stock-scanner-project\stock-scanner-complete
```

Then run:

```bash
# Fetch all latest changes
git fetch origin

# Pull the fixed version
git pull origin claude/merged-improvements-to-main-011CUppkbEq5sZ5PEQDyqQ28
```

**That's it!** Your Django server should now start without errors.

---

## 🔧 Alternative: Manual Fix (if git pull doesn't work)

If you can't pull from git, manually apply these fixes:

### Fix 1: settings.py (Line 290-296)

**File:** `C:\Stock-scanner-project\stock-scanner-complete\backend\stockscanner_django\settings.py`

**Find this (around line 290-296):**
```python
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'burst': '60/minute',
    }
},
    'DEFAULT_THROTTLE_CACHE': 'default',
}
```

**Replace with:**
```python
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'burst': '60/minute',
    }
}
```

**Delete these two lines:**
- `},` (the extra closing brace with comma)
- `    'DEFAULT_THROTTLE_CACHE': 'default',`

---

### Fix 2: admin.py (Line 2-8 and 30-34)

**File:** `C:\Stock-scanner-project\stock-scanner-complete\backend\stocks\admin.py`

**Change line 2-8 from:**
```python
from .models import (
    Stock, StockPrice, StockAlert, Membership,
    UserProfile, UserPortfolio, PortfolioHolding, TradeTransaction,
    UserWatchlist, WatchlistItem, UserInterests, PersonalizedNews,
    PortfolioFollowing, DiscountCode, UserDiscountUsage,
    RevenueTracking, MonthlyRevenueSummary
)
```

**To:**
```python
from .models import (
    Stock, StockPrice, StockAlert,
    UserProfile, UserPortfolio, PortfolioHolding, TradeTransaction,
    UserWatchlist, WatchlistItem, UserInterests, PersonalizedNews,
    PortfolioFollowing, DiscountCode, UserDiscountUsage,
    RevenueTracking, MonthlyRevenueSummary
)
# Note: Membership model has been deprecated in favor of billing.models.Subscription
```

**Delete lines 30-34:**
```python
@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'is_active', 'created_at', 'expires_at']
    list_filter = ['plan', 'is_active', 'created_at']
    search_fields = ['user__username']
```

**Replace with:**
```python
# Membership model has been deprecated - use billing.models.Subscription instead
# To manage subscriptions, use the billing app admin interface
```

---

## 🎯 After Fixing

Restart your Django development server:

```bash
python manage.py runserver
```

You should see:
```
✅ System check identified no issues (0 silenced).
Django version X.X.X, using settings 'stockscanner_django.settings'
Starting development server at http://127.0.0.1:8000/
```

---

## 🐛 Errors Fixed

1. ✅ **IndentationError** at line 296 in settings.py
2. ✅ **SyntaxError** about missing comma in REST_FRAMEWORK
3. ✅ **ImportError** - cannot import 'Membership' from stocks.models

---

## 📦 What Changed

- **settings.py**: Fixed malformed REST_FRAMEWORK dictionary
- **admin.py**: Removed deprecated Membership model registration
- **models.py**: Membership model is now commented out (use billing.Subscription instead)

All security improvements and performance optimizations are included in these fixes!

---

## 🚀 Fix 3: Windows Deployment Script Issues

If you're running the deployment script (`deploy_sftp_complete.py`) and getting this error:

```
FileNotFoundError: [WinError 2] The system cannot find the file specified
```

This means **Node.js/npm is not properly installed or not in your PATH**.

### Solution A: Install Node.js (Recommended)

1. **Download Node.js** from: https://nodejs.org/
   - Download the **LTS version** (Long Term Support)
   - Use the Windows Installer (.msi file)

2. **Install with default options**
   - Make sure to check "Add to PATH" during installation
   - Restart your terminal after installation

3. **Verify installation:**
   ```bash
   node --version
   npm --version
   ```

### Solution B: Add Node.js to PATH (if already installed)

If Node.js is installed but not in PATH:

1. **Find Node.js location** (usually):
   - `C:\Program Files\nodejs\`
   - Or: `C:\Program Files (x86)\nodejs\`

2. **Add to PATH:**
   - Press `Win + X` → System
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find "Path"
   - Click "Edit" → "New"
   - Add the Node.js folder path
   - Click OK on all dialogs
   - **Restart your terminal**

3. **Test it works:**
   ```bash
   npm --version
   ```

### Solution C: Use the Fixed Deployment Script

The latest version of `deploy_sftp_complete.py` now includes **automatic Windows detection** and fixes the npm command issues.

**Pull the latest changes:**
```bash
git pull origin claude/review-main-changes-011CUrvWjx2Z336CikzF6865
```

The script now:
- Automatically detects Windows
- Uses `npm.cmd` instead of `npm`
- Provides better error messages
- Uses `shell=True` for Windows compatibility

### Troubleshooting npm issues:

**Error: "npm: command not found"**
- Node.js is not installed → Install from nodejs.org

**Error: "The system cannot find the file specified"**
- npm is not in PATH → Add to PATH (see Solution B)
- Terminal needs restart → Close and reopen terminal

**Error: "npm install fails with EPERM"**
- Run as Administrator: Right-click terminal → "Run as administrator"
- Or disable antivirus temporarily during install

---

## ❓ Need Help?

If you're still having issues:

1. Check you're in the correct directory: `C:\Stock-scanner-project\stock-scanner-complete\backend`
2. Make sure your Python virtual environment is activated
3. Verify Python version: `python --version` (should be 3.8+)
4. Check Django is installed: `pip show django`
5. For deployment issues, verify Node.js: `node --version` and `npm --version`

---

**Last Updated:** 2025-11-06
**Branch:** `claude/review-main-changes-011CUrvWjx2Z336CikzF6865`
