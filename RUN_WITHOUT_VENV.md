# 🚀 Running Stock Scanner Without Virtual Environment

## Your Situation
You want to run the Stock Scanner without a virtual environment, using your existing pandas 2.3.1 and numpy 2.3.1 packages.

## Option 1: Use Existing Virtual Environment (Recommended)

Since you already have a working virtual environment set up, you can simply activate it each time:

### Windows (Git Bash/Command Prompt):
```bash
# Activate the virtual environment
source venv/Scripts/activate  # Git Bash
# OR
venv\Scripts\activate.bat     # Command Prompt

# Then run normally
python manage.py runserver
```

### Linux/Mac:
```bash
# Activate the virtual environment
source venv/bin/activate

# Then run normally
python manage.py runserver
```

## Option 2: System-Wide Installation (Advanced Users)

If your system has PEP 668 protection (most modern Linux distributions), you can:

### Override System Protection (USE WITH CAUTION):
```bash
# Install packages with system override
python3 -m pip install --break-system-packages Django==4.2.11 djangorestframework django-cors-headers python-dotenv requests yfinance textblob beautifulsoup4

# Then run directly
python3 manage.py runserver
```

⚠️ **Warning**: `--break-system-packages` can potentially interfere with your system's Python packages.

## Option 3: Quick Start Script (Windows)

Create a simple batch file `start_scanner.bat`:

```batch
@echo off
echo Starting Stock Scanner...
call venv\Scripts\activate.bat
python manage.py runserver
pause
```

Then just double-click the file to start!

## Option 4: Quick Start Script (Linux/Mac)

Create a simple shell script `start_scanner.sh`:

```bash
#!/bin/bash
echo "Starting Stock Scanner..."
source venv/bin/activate
python manage.py runserver
```

Make it executable and run:
```bash
chmod +x start_scanner.sh
./start_scanner.sh
```

## Option 5: Using pipx (Application Isolation)

If you have pipx installed:
```bash
# Install Django in isolated environment
pipx install Django

# Then you can run Django commands directly
django-admin startproject myproject
```

## Your Package Compatibility ✅

Your existing packages are perfect:
- **pandas 2.3.1** → Fully compatible with Python 3.13
- **numpy 2.3.1** → Fully compatible with Python 3.13
- **Python 3.13** → Latest and greatest!

## Recommended Workflow

**For daily use, I recommend Option 1 (using the venv):**

1. **One-time setup**: Already done!
2. **Daily workflow**:
   ```bash
   # Windows Git Bash
   cd /c/path/to/stock-scanner-complete
   source venv/Scripts/activate
   python manage.py runserver
   
   # Windows Command Prompt
   cd C:\path\to\stock-scanner-complete
   venv\Scripts\activate.bat
   python manage.py runserver
   ```

## Why Virtual Environment is Actually Better

- ✅ **Isolated**: Won't affect other Python projects
- ✅ **Reproducible**: Same environment every time
- ✅ **Safe**: No system package conflicts
- ✅ **Portable**: Easy to share or recreate
- ✅ **Your packages**: Still uses your pandas/numpy when installed in venv

## Quick Commands Reference

### With Virtual Environment:
```bash
# Activate (do this once per session)
source venv/Scripts/activate      # Git Bash
venv\Scripts\activate.bat         # Windows CMD

# Then use normally
python manage.py runserver
python manage.py load_nasdaq_only
python manage.py createsuperuser
```

### Without Virtual Environment (if system allows):
```bash
# Direct execution (may require --break-system-packages)
python3 manage.py runserver
python3 manage.py load_nasdaq_only
python3 manage.py createsuperuser
```

## Access Your Application

Once running (either method):
- **Main App**: http://localhost:8000
- **API**: http://localhost:8000/api/stocks/
- **Admin**: http://localhost:8000/admin

## Troubleshooting

### "externally-managed-environment" Error:
- **Recommended**: Use the virtual environment (Option 1)
- **Advanced**: Use `--break-system-packages` flag (Option 2)
- **Alternative**: Use pipx for application isolation

### Virtual Environment "Not Found":
```bash
# Recreate if needed
python3 -m venv venv

# Install packages
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### Package Import Errors:
```bash
# Check which Python you're using
which python
python --version

# Check if packages are installed
pip list | grep -E "(Django|pandas|numpy)"
```

## Best Practice Recommendation

**Use the virtual environment** - it's actually easier once you get used to it:

1. Create a startup script that activates venv automatically
2. Your IDE can be configured to use the venv Python automatically
3. It's the Python community standard for good reason

The virtual environment doesn't prevent you from using your system's pandas/numpy - when you install pandas in the venv, it will use compatible versions that work with your Python 3.13!