# Stock Scanner Git Bash Production Guide

This guide covers setting up and deploying the Stock Scanner Django application using Git Bash on Windows for both development and production workflows.

## Prerequisites

- **Windows 10/11** with Git Bash installed
- **Python 3.8+** accessible from Git Bash
- **Git** configured with your repository access
- **Domain/Hosting** (optional for production)

---

## Part 1: Git Bash Development Setup

### Step 1: Initial Setup

```bash
# Clone the repository in Git Bash
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# One-command setup and start
./start_django_gitbash.sh
```

This script will:
- Create virtual environment (`venv/Scripts/` on Windows)
- Install all dependencies
- Setup SQLite database
- Create superuser (admin/admin123)
- Load sample stock data
- Start Django development server

### Step 2: Verify Git Bash Setup

```bash
# Check Python version
python --version

# Check virtual environment activation
which python
# Should show: /c/path/to/your/project/venv/Scripts/python

# Test Django
python manage.py check

# Test API endpoints
curl http://127.0.0.1:8000/api/simple/status/
```

---

## Part 2: Git Bash Production Workflow

### Option A: Windows Server Production (Git Bash)

If you're deploying to a Windows server with Git Bash:

#### Step 1: Server Setup via Git Bash

```bash
# Connect to Windows server via SSH (if available)
ssh administrator@your-windows-server

# Or use RDP and open Git Bash on the server
# Install Git Bash on Windows Server if not available
```

#### Step 2: Production Deployment

```bash
# On the Windows server, using Git Bash
cd /c/inetpub/wwwroot/ # or your preferred directory
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git stockscanner
cd stockscanner

# Setup production environment
cp .env.gitbash .env

# Edit .env for production
nano .env # or use notepad .env
```

**Production .env settings:**
```bash
DEBUG=False
SECRET_KEY=your-super-secret-production-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip
DATABASE_URL=sqlite:///production.db # or MySQL if available
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

#### Step 3: Production Setup

```bash
# Create production virtual environment
python -m venv venv
source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn # for production server

# Setup database
python manage.py migrate
python manage.py createsuperuser
python manage.py load_nasdaq_only
python manage.py collectstatic --noinput

# Test production setup
python manage.py check --deploy
```

#### Step 4: Run Production Server

```bash
# Option 1: Simple production server
python manage.py runserver 0.0.0.0:8000

# Option 2: Gunicorn (recommended)
gunicorn --bind 0.0.0.0:8000 stockscanner_django.wsgi:application

# Option 3: Background service (Git Bash)
nohup gunicorn --bind 0.0.0.0:8000 stockscanner_django.wsgi:application &
```

### Option B: Cloud Hosting with Git Bash Deployment

#### Heroku Deployment

```bash
# Install Heroku CLI (if not installed)
# Download from: https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create Heroku app
heroku create your-stock-scanner-app

# Add environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ALLOWED_HOSTS=your-app.herokuapp.com

# Create Procfile
echo "web: gunicorn stockscanner_django.wsgi:application" > Procfile

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Run migrations on Heroku
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
heroku run python manage.py load_nasdaq_only
```

#### DigitalOcean/AWS with Git Bash

```bash
# Connect to your cloud server
ssh root@your-server-ip

# Install Git and Python (if needed)
apt update && apt install -y git python3 python3-pip python3-venv

# Clone and setup (same as local)
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete
./start_django_gitbash.sh

# Configure for production
cp .env.gitbash .env
# Edit .env for production settings
```

---

## Part 3: Git Bash Development Workflow

### Daily Development Routine

```bash
# Start your day
cd /c/path/to/stock-scanner-complete
source venv/Scripts/activate

# Pull latest changes
git pull origin main

# Start development server
python manage.py runserver

# Make changes, test, commit
git add .
git commit -m "Your changes"
git push origin main
```

### Testing Workflow

```bash
# Test API endpoints
curl http://127.0.0.1:8000/api/simple/status/
curl http://127.0.0.1:8000/api/simple/stocks/
curl http://127.0.0.1:8000/api/simple/news/

# Test Django admin
# Visit: http://127.0.0.1:8000/admin/
# Login: admin / admin123

# Test WordPress integration
# Follow examples in WORDPRESS_INTEGRATION_GUIDE.md
```

### Database Management (Git Bash)

```bash
# Backup database
cp db.sqlite3 backup_$(date +%Y%m%d_%H%M%S).db

# Reset database
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
python manage.py load_nasdaq_only

# Load sample data for testing
python manage.py shell -c "
from stocks.models import Stock
print(f'Total stocks: {Stock.objects.count()}')
"
```

---

## Part 4: Git Bash Production Tools

### Environment Management

```bash
# Create different environment files
cp .env.gitbash .env.development
cp .env.gitbash .env.staging 
cp .env.gitbash .env.production

# Switch environments
cp .env.development .env # for development
cp .env.production .env # for production
```

### Deployment Scripts

Create `deploy.sh` for easy deployment:

```bash
#!/bin/bash
echo " Deploying Stock Scanner..."

# Activate virtual environment
source venv/Scripts/activate

# Pull latest changes
git pull origin main

# Install/update dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Test deployment
python manage.py check --deploy

echo " Deployment complete!"
echo " Start server with: python manage.py runserver"
```

Make it executable:
```bash
chmod +x deploy.sh
./deploy.sh
```

### Monitoring Scripts

Create `monitor.sh`:

```bash
#!/bin/bash
echo " Stock Scanner Status"
echo "======================="

# Check if server is running
if curl -s http://127.0.0.1:8000/api/simple/status/ > /dev/null; then
echo " Server: Running"
else
echo " Server: Not running"
fi

# Check API endpoints
echo " Testing API endpoints:"
curl -s http://127.0.0.1:8000/api/simple/status/ | jq '.status' || echo " Status API failed"

# Check database
python manage.py shell -c "
from stocks.models import Stock
print(f' Stocks in database: {Stock.objects.count()}')
" 2>/dev/null || echo " Database connection failed"

echo "======================="
```

---

## Part 5: WordPress Integration (Git Bash)

### Local WordPress Testing

```bash
# If you have local WordPress installation
# Copy the integration code from WORDPRESS_INTEGRATION_GUIDE.md

# Test API connection from WordPress
curl -X POST -d "url=http://127.0.0.1:8000/api/simple/stocks/" \
http://your-wordpress-site/wp-admin/admin-ajax.php
```

### Production WordPress Integration

```bash
# Update WordPress integration URLs for production
# In your WordPress functions.php:

# Development
$api_url = 'http://127.0.0.1:8000/api/simple/';

# Production 
$api_url = 'https://yourdomain.com/api/simple/';
```

---

## Part 6: Git Bash Performance Optimization

### Windows-Specific Optimizations

```bash
# Use Windows performance monitoring
# In Git Bash:
powershell "Get-Process python"
powershell "Get-Counter '\Process(python)\% Processor Time'"

# Optimize Django for Windows
# Add to settings.py:
if os.name == 'nt': # Windows
DATABASES['default']['OPTIONS'] = {
'timeout': 20,
}
```

### Git Bash Memory Management

```bash
# Monitor memory usage
ps aux | grep python

# Optimize virtual environment
pip install --upgrade pip
pip install --upgrade setuptools wheel

# Clean up old files
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

---

## Part 7: Troubleshooting (Git Bash)

### Common Git Bash Issues

**1. Python Path Issues**
```bash
# Check Python location
which python
which pip

# Fix if needed
export PATH="/c/Python39:$PATH" # Adjust for your Python version
```

**2. Virtual Environment Issues**
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

**3. Port Already in Use**
```bash
# Find process using port 8000
netstat -ano | grep :8000

# Kill process (replace PID)
taskkill /PID 1234 /F

# Or use different port
python manage.py runserver 127.0.0.1:8001
```

**4. Git Bash Permissions**
```bash
# Fix file permissions
chmod +x *.sh
chmod 755 manage.py
```

### Database Issues

```bash
# SQLite locked
rm db.sqlite3-journal
rm db.sqlite3-wal

# Reset completely
rm db.sqlite3
python manage.py migrate
```

---

## Git Bash Production Checklist

### Development Ready
- [ ] Git Bash installed and configured
- [ ] Python 3.8+ accessible from Git Bash
- [ ] Virtual environment created (`venv/Scripts/`)
- [ ] Dependencies installed via pip
- [ ] SQLite database setup and migrated
- [ ] Superuser created (admin/admin123)
- [ ] Development server running on port 8000
- [ ] API endpoints tested and working

### Production Ready 
- [ ] Production environment file configured
- [ ] DEBUG=False in production
- [ ] SECRET_KEY generated for production
- [ ] ALLOWED_HOSTS configured for domain
- [ ] Static files collected
- [ ] Database migrated for production
- [ ] Production server (Gunicorn) tested
- [ ] WordPress integration tested
- [ ] Monitoring scripts setup

### Deployment Ready
- [ ] Repository access configured
- [ ] Deployment scripts created
- [ ] Environment switching setup
- [ ] Backup procedures established
- [ ] Monitoring tools configured
- [ ] Performance optimization applied

---

## Git Bash Advantages

### Why Git Bash for Stock Scanner?

1. **Consistent Environment**: Same commands work on Windows and Linux
2. **Easy Development**: Quick setup with `./start_django_gitbash.sh`
3. **Git Integration**: Native git commands and workflows
4. **Cross-Platform**: Easy transition to Linux servers
5. **Professional Tools**: Standard Unix tools available
6. **WordPress Friendly**: Easy API integration testing

### Git Bash Best Practices

```bash
# Always use forward slashes for paths
cd /c/projects/stock-scanner

# Use .gitbash environment files
cp .env.gitbash .env

# Activate virtual environment consistently
source venv/Scripts/activate

# Use Unix-style commands
ls -la
grep -r "pattern" .
find . -name "*.py"
```

---

## You're Ready for Git Bash Production!

Your Stock Scanner is now optimized for Git Bash development and production workflows:

- **Development**: One-command setup and testing
- **Production**: Multiple deployment options
- **WordPress**: Ready for integration
- **Monitoring**: Built-in health checks
- **Deployment**: Automated scripts and workflows

**Start developing**: `./start_django_gitbash.sh` 
**Deploy to production**: Follow the deployment section for your hosting choice 
**Integrate with WordPress**: Use the examples in `WORDPRESS_INTEGRATION_GUIDE.md`