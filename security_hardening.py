#!/usr/bin/env python3
"""
Security Hardening Configuration for Stock Scanner
IONOS Hosting Compatible Security Settings
"""

import os
import secrets
import subprocess
import sys
from pathlib import Path

class SecurityHardening:
    """Security hardening configuration and utilities"""
    
    def __init__(self, django_project_path="."):
        self.project_path = Path(django_project_path)
        self.settings_file = self.project_path / "stockscanner_django" / "settings.py"
        
    def print_step(self, message):
        """Print setup step"""
        print(f"\n🔐 {message}")

    def print_success(self, message):
        """Print success message"""
        print(f"✅ {message}")

    def print_error(self, message):
        """Print error message"""
        print(f"❌ {message}")

    def print_warning(self, message):
        """Print warning message"""
        print(f"⚠️ {message}")

    def generate_secret_key(self) -> str:
        """Generate a secure Django secret key"""
        return secrets.token_urlsafe(50)

    def create_production_settings(self):
        """Create hardened production settings"""
        self.print_step("Creating production security settings...")
        
        secret_key = self.generate_secret_key()
        
        production_settings = f'''"""
Production Security Settings for Stock Scanner
Generated automatically - DO NOT EDIT MANUALLY
"""

import os
from pathlib import Path

# Import email configuration
from emails.email_config import get_email_settings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '{secret_key}'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# IONOS hosting configuration
ALLOWED_HOSTS = [
    'retailtradescan.net',
    'www.retailtradescan.net',
    '.retailtradescan.net',  # Allow subdomains
    'localhost',  # For development/testing
    '127.0.0.1',  # For development/testing
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    
    # Local apps
    'core',
    'stocks',
    'emails',
    'wordpress_integration',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'stockscanner_django.urls'

TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {{
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }},
    }},
]

WSGI_APPLICATION = 'stockscanner_django.wsgi.application'

# Database configuration (import from database_settings_local.py)
try:
    from .database_settings_local import DATABASES
except ImportError:
    # Fallback SQLite database configuration
    DATABASES = {{
        'default': {{
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'stock_scanner.db',
            'OPTIONS': {{
                'timeout': 20,
            }},
            'ATOMIC_REQUESTS': True,
        }}
    }}

# Email configuration
email_settings = get_email_settings()
for key, value in email_settings.items():
    globals()[key] = value

# Cache configuration (Local memory cache for simplicity)
CACHES = {{
    'default': {{
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'stock-scanner-cache',
        'TIMEOUT': 300,  # 5 minutes default timeout
        'OPTIONS': {{
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }}
    }}
}}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Use database for sessions
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {{
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    }},
    {{
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {{
            'min_length': 12,  # Increased from default 8
        }}
    }},
    {{
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    }},
    {{
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    }},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework configuration
REST_FRAMEWORK = {{
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {{
        'anon': '100/hour',
        'user': '500/hour'
    }},
    'PAGE_SIZE': 100,
}}

# CORS Configuration for WordPress Integration
CORS_ALLOWED_ORIGINS = [
    "https://retailtradescan.net",
    "https://www.retailtradescan.net",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-wp-token',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

# Content Security Policy (basic implementation)
CSP_DEFAULT_SRC = ["'self'"]
CSP_SCRIPT_SRC = ["'self'", "'unsafe-inline'", "cdnjs.cloudflare.com", "cdn.jsdelivr.net"]
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'", "cdnjs.cloudflare.com", "cdn.jsdelivr.net"]
CSP_IMG_SRC = ["'self'", "data:", "https:"]
CSP_FONT_SRC = ["'self'", "cdnjs.cloudflare.com", "cdn.jsdelivr.net"]

# Additional security headers
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS = 'DENY'

# File upload security
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5 MB
FILE_UPLOAD_PERMISSIONS = 0o644

# Logging configuration
LOGGING = {{
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {{
        'verbose': {{
            'format': '{{levelname}} {{asctime}} {{module}} {{process:d}} {{thread:d}} {{message}}',
            'style': '{{',
        }},
        'simple': {{
            'format': '{{levelname}} {{message}}',
            'style': '{{',
        }},
    }},
    'handlers': {{
        'file': {{
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/stock-scanner/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        }},
        'security_file': {{
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/stock-scanner/security.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        }},
        'console': {{
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        }},
        'mail_admins': {{
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        }},
    }},
    'root': {{
        'handlers': ['console', 'file'],
    }},
    'loggers': {{
        'django': {{
            'handlers': ['file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        }},
        'django.security': {{
            'handlers': ['security_file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': True,
        }},
        'stocks': {{
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        }},
        'emails': {{
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        }},
    }},
}}

# Site configuration
SITE_ID = 1

# Stock API Configuration (yfinance only)
STOCK_API_SETTINGS = {{
    'USE_YFINANCE_ONLY': True,
    'RATE_LIMIT': 1.0,  # 1 second between requests
    'CACHE_DURATION': 300,  # 5 minutes
    'MAX_RETRIES': 3,
    'TIMEOUT': 30,
}}

# WordPress integration settings
WORDPRESS_URL = 'https://retailtradescan.net'
WORDPRESS_API_TIMEOUT = 10

# Admin URL obfuscation (change 'admin' to something else)
ADMIN_URL = os.getenv('ADMIN_URL', 'secure-admin-{secret_key[:8]}')

# Rate limiting
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_ENABLE = True

# Additional security middleware (if installed)
try:
    import django_csp
    MIDDLEWARE.append('csp.middleware.CSPMiddleware')
except ImportError:
    pass

try:
    import django_ratelimit
    MIDDLEWARE.append('django_ratelimit.middleware.RatelimitMiddleware')
except ImportError:
    pass
'''
        
        # Write production settings
        production_settings_file = self.project_path / "stockscanner_django" / "production_settings.py"
        with open(production_settings_file, 'w') as f:
            f.write(production_settings)
        
        self.print_success(f"Production settings created: {production_settings_file}")
        return secret_key

    def create_security_middleware(self):
        """Create custom security middleware"""
        self.print_step("Creating custom security middleware...")
        
        middleware_content = '''"""
Custom Security Middleware for Stock Scanner
"""

import logging
from django.http import HttpResponseForbidden
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import time

logger = logging.getLogger('django.security')

class SecurityMiddleware(MiddlewareMixin):
    """Custom security middleware for additional protection"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.suspicious_paths = [
            '/wp-admin', '/admin.php', '/.env', '/config.php',
            '/phpmyadmin', '/wp-config.php', '/backup',
            '/xmlrpc.php', '/wp-login.php'
        ]
        self.rate_limit_cache = {}
        super().__init__(get_response)
    
    def process_request(self, request):
        """Process incoming requests for security"""
        
        # Block suspicious paths
        for path in self.suspicious_paths:
            if path in request.path.lower():
                logger.warning(f"Blocked suspicious path: {request.path} from {self.get_client_ip(request)}")
                return HttpResponseForbidden("Access denied")
        
        # Rate limiting by IP
        if self.is_rate_limited(request):
            logger.warning(f"Rate limited IP: {self.get_client_ip(request)}")
            return HttpResponseForbidden("Rate limit exceeded")
        
        # Log admin access attempts
        if '/admin' in request.path and request.method == 'POST':
            logger.info(f"Admin access attempt from {self.get_client_ip(request)}")
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_rate_limited(self, request):
        """Simple rate limiting implementation"""
        ip = self.get_client_ip(request)
        current_time = time.time()
        
        # Clean old entries
        self.rate_limit_cache = {
            k: v for k, v in self.rate_limit_cache.items() 
            if current_time - v['last_request'] < 3600  # 1 hour window
        }
        
        if ip not in self.rate_limit_cache:
            self.rate_limit_cache[ip] = {'count': 1, 'last_request': current_time}
            return False
        
        entry = self.rate_limit_cache[ip]
        
        # Reset count if more than 1 hour passed
        if current_time - entry['last_request'] > 3600:
            entry['count'] = 1
            entry['last_request'] = current_time
            return False
        
        # Increment count
        entry['count'] += 1
        entry['last_request'] = current_time
        
        # Check rate limit (100 requests per hour per IP)
        return entry['count'] > 100

class HeaderSecurityMiddleware(MiddlewareMixin):
    """Add additional security headers"""
    
    def process_response(self, request, response):
        """Add security headers to response"""
        
        # Remove server information
        if 'Server' in response:
            del response['Server']
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Remove potentially sensitive headers
        headers_to_remove = ['X-Powered-By', 'X-AspNet-Version', 'X-AspNetMvc-Version']
        for header in headers_to_remove:
            if header in response:
                del response[header]
        
        return response
'''
        
        # Create middleware directory
        middleware_dir = self.project_path / "stockscanner_django" / "middleware"
        middleware_dir.mkdir(exist_ok=True)
        
        # Create __init__.py
        with open(middleware_dir / "__init__.py", 'w') as f:
            f.write("")
        
        # Create security middleware
        with open(middleware_dir / "security.py", 'w') as f:
            f.write(middleware_content)
        
        self.print_success("Custom security middleware created")

    def create_environment_file(self, secret_key):
        """Create secure .env file"""
        self.print_step("Creating secure environment file...")
        
        env_content = f'''# Production Environment Variables for Stock Scanner
# SECURITY WARNING: Keep this file secure and never commit to version control

# Django Configuration
SECRET_KEY={secret_key}
DEBUG=False
ADMIN_URL=secure-admin-{secret_key[:8]}

# Database Configuration (Local SQLite - no password needed)
DB_TYPE=sqlite3
DB_NAME=stock_scanner.db
DB_PATH=./stock_scanner.db

# Email Configuration (Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply.retailtradescanner@gmail.com
EMAIL_HOST_PASSWORD=mzqmvhsjqeqrjmjv
ADMIN_EMAIL=noreply.retailtradescanner@gmail.com

# Site Configuration
SITE_URL=https://retailtradescan.net
ALLOWED_HOSTS=retailtradescan.net,www.retailtradescan.net

# Stock API Configuration (yfinance only)
USE_YFINANCE_ONLY=True
STOCK_API_RATE_LIMIT=1.0
YFINANCE_CACHE_DURATION=300
YFINANCE_MAX_RETRIES=3
YFINANCE_TIMEOUT=30

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000

# Cache Configuration (Local Memory Cache - no Redis needed)
CACHE_BACKEND=locmem

# WordPress Integration
WORDPRESS_URL=https://retailtradescan.net
WORDPRESS_API_TIMEOUT=10

# Stripe Configuration (from previous setup)
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_PUBLISHABLE_KEY
STRIPE_SECRET_KEY=sk_live_YOUR_SECRET_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET

# File Paths
LOG_DIR=/var/log/stock-scanner
STATIC_ROOT=/var/www/stock-scanner/static
MEDIA_ROOT=/var/www/stock-scanner/media
'''
        
        env_file = self.project_path / ".env"
        if not env_file.exists():
            with open(env_file, 'w') as f:
                f.write(env_content)
            
            # Set secure permissions
            os.chmod(env_file, 0o600)
            self.print_success(f"Secure .env file created: {env_file}")
        else:
            self.print_warning(".env file already exists - not overwriting")

    def create_log_directories(self):
        """Create secure log directories"""
        self.print_step("Creating log directories...")
        
        try:
            # Create log directory
            log_dir = Path("/var/log/stock-scanner")
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Set appropriate permissions
            os.chmod(log_dir, 0o755)
            
            # Create log files with appropriate permissions
            log_files = ["django.log", "security.log", "access.log", "error.log"]
            for log_file in log_files:
                log_path = log_dir / log_file
                log_path.touch(exist_ok=True)
                os.chmod(log_path, 0o644)
            
            self.print_success(f"Log directories created: {log_dir}")
            
        except PermissionError:
            self.print_warning("Cannot create system log directory - will use local logs")
            
            # Create local log directory as fallback
            local_log_dir = self.project_path / "logs"
            local_log_dir.mkdir(exist_ok=True)
            
            for log_file in ["django.log", "security.log"]:
                log_path = local_log_dir / log_file
                log_path.touch(exist_ok=True)
            
            self.print_success(f"Local log directory created: {local_log_dir}")

    def create_security_requirements(self):
        """Create requirements file with security packages"""
        self.print_step("Creating security requirements...")
        
        security_requirements = '''# Requirements for Stock Scanner (Local SQLite + Gmail)

# Core Django (SQLite included by default)
Django>=4.2.0,<5.0

# Stock data (yfinance only)
yfinance>=0.2.0
requests>=2.31.0
urllib3>=1.26.0
pandas>=2.0.0
numpy>=1.24.0

# REST API and CORS
djangorestframework>=3.14.0
django-cors-headers>=4.3.0

# Security packages
django-csp>=3.7  # Content Security Policy
django-ratelimit>=4.0.0  # Rate limiting
django-axes>=6.0.0  # Login attempt monitoring
cryptography>=41.0.0  # Strong cryptography

# Environment management
python-decouple>=3.8  # Environment variable management
python-dotenv>=1.0.0  # .env file support

# Monitoring and logging
django-extensions>=3.2.0  # Development tools

# Production server
gunicorn>=21.0.0
whitenoise>=6.5.0  # Static file serving

# Development and testing
pytest>=7.4.0
pytest-django>=4.5.0
coverage>=7.3.0

# Additional utilities
Pillow>=10.0.0  # Image processing
python-dateutil>=2.8.0  # Date utilities
'''
        
        requirements_file = self.project_path / "requirements_secure.txt"
        with open(requirements_file, 'w') as f:
            f.write(security_requirements)
        
        self.print_success(f"Security requirements created: {requirements_file}")

    def create_deployment_script(self):
        """Create secure deployment script"""
        self.print_step("Creating deployment script...")
        
        deploy_script = '''#!/bin/bash
# Secure Deployment Script for Stock Scanner on IONOS

set -e  # Exit on any error

echo "🚀 Starting secure deployment..."

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}❌ Do not run this script as root${NC}"
   exit 1
fi

# Backup existing deployment
if [ -d "/var/www/stock-scanner" ]; then
    echo -e "${YELLOW}📦 Creating backup...${NC}"
    sudo cp -r /var/www/stock-scanner /var/www/stock-scanner.backup.$(date +%Y%m%d_%H%M%S)
fi

# Update system packages
echo -e "${YELLOW}🔄 Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# Install required system packages
echo -e "${YELLOW}📦 Installing system dependencies...${NC}"
sudo apt install -y python3-pip python3-venv nginx postgresql redis-server supervisor ufw fail2ban

# Create application user if not exists
if ! id "stockscanner" &>/dev/null; then
    echo -e "${YELLOW}👤 Creating application user...${NC}"
    sudo useradd -m -d /home/stockscanner -s /bin/bash stockscanner
fi

# Create directory structure
echo -e "${YELLOW}📁 Creating directory structure...${NC}"
sudo mkdir -p /var/www/stock-scanner
sudo mkdir -p /var/log/stock-scanner
sudo mkdir -p /etc/stockscanner

# Set ownership
sudo chown -R stockscanner:www-data /var/www/stock-scanner
sudo chown -R stockscanner:adm /var/log/stock-scanner

# Copy application files
echo -e "${YELLOW}📂 Copying application files...${NC}"
sudo -u stockscanner cp -r . /var/www/stock-scanner/

# Create virtual environment
echo -e "${YELLOW}🐍 Setting up Python environment...${NC}"
cd /var/www/stock-scanner
sudo -u stockscanner python3 -m venv venv
sudo -u stockscanner ./venv/bin/pip install --upgrade pip
sudo -u stockscanner ./venv/bin/pip install -r requirements_secure.txt

# Set environment variables
echo -e "${YELLOW}⚙️ Configuring environment...${NC}"
if [ ! -f "/var/www/stock-scanner/.env" ]; then
    sudo -u stockscanner cp .env.example .env
    echo -e "${RED}⚠️ Please edit /var/www/stock-scanner/.env with your configuration${NC}"
fi

# Setup database
echo -e "${YELLOW}🗄️ Setting up database...${NC}"
sudo -u stockscanner ./venv/bin/python database_setup.py

# Run Django setup
echo -e "${YELLOW}🔧 Running Django setup...${NC}"
cd /var/www/stock-scanner
sudo -u stockscanner ./venv/bin/python manage.py collectstatic --noinput
sudo -u stockscanner ./venv/bin/python manage.py migrate

# Create Gunicorn configuration
echo -e "${YELLOW}🌐 Configuring Gunicorn...${NC}"
sudo tee /etc/stockscanner/gunicorn.conf.py > /dev/null <<EOF
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
user = "stockscanner"
group = "stockscanner"
tmp_upload_dir = None
errorlog = "/var/log/stock-scanner/gunicorn_error.log"
accesslog = "/var/log/stock-scanner/gunicorn_access.log"
access_log_format = '%%(h)s %%(l)s %%(u)s %%(t)s "%%(r)s" %%(s)s %%(b)s "%%(f)s" "%%(a)s"'
loglevel = "info"
EOF

# Create systemd service
echo -e "${YELLOW}🔧 Creating systemd service...${NC}"
sudo tee /etc/systemd/system/stockscanner.service > /dev/null <<EOF
[Unit]
Description=Stock Scanner Django Application
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=stockscanner
Group=stockscanner
WorkingDirectory=/var/www/stock-scanner
Environment=PATH=/var/www/stock-scanner/venv/bin
ExecStart=/var/www/stock-scanner/venv/bin/gunicorn --config /etc/stockscanner/gunicorn.conf.py stockscanner_django.wsgi:application
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
echo -e "${YELLOW}🌍 Configuring Nginx...${NC}"
sudo tee /etc/nginx/sites-available/stockscanner > /dev/null <<EOF
server {
    listen 80;
    server_name retailtradescan.net www.retailtradescan.net;
    return 301 https://\\$server_name\\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name retailtradescan.net www.retailtradescan.net;

    # SSL configuration (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/retailtradescan.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/retailtradescan.net/privkey.pem;
    
    # SSL security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Static files
    location /static/ {
        alias /var/www/stock-scanner/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /var/www/stock-scanner/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Django application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\$scheme;
        proxy_redirect off;
        
        # Security
        proxy_hide_header X-Powered-By;
        proxy_hide_header Server;
    }
    
    # Block common attack paths
    location ~ /\\.(ht|env|git) {
        deny all;
        return 404;
    }
    
    location ~ /(wp-admin|wp-login|phpmyadmin|admin\\.php) {
        deny all;
        return 404;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/stockscanner /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Configure firewall
echo -e "${YELLOW}🔥 Configuring firewall...${NC}"
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Configure fail2ban
echo -e "${YELLOW}🛡️ Configuring fail2ban...${NC}"
sudo tee /etc/fail2ban/jail.local > /dev/null <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 2
EOF

# Start services
echo -e "${YELLOW}🚀 Starting services...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable stockscanner redis-server postgresql nginx fail2ban
sudo systemctl start stockscanner redis-server postgresql nginx fail2ban

# Test configuration
echo -e "${YELLOW}🧪 Testing configuration...${NC}"
sudo nginx -t
sudo systemctl status stockscanner --no-pager

# Setup Let's Encrypt (optional)
if command -v certbot &> /dev/null; then
    echo -e "${YELLOW}🔒 Setting up SSL certificate...${NC}"
    sudo certbot --nginx -d retailtradescan.net -d www.retailtradescan.net --non-interactive --agree-tos --email admin@retailtradescan.net
fi

# Create maintenance script
sudo tee /usr/local/bin/stockscanner-maintenance > /dev/null <<EOF
#!/bin/bash
# Stock Scanner Maintenance Script

case "\\$1" in
    update)
        echo "Updating Stock Scanner..."
        cd /var/www/stock-scanner
        sudo -u stockscanner git pull
        sudo -u stockscanner ./venv/bin/pip install -r requirements_secure.txt
        sudo -u stockscanner ./venv/bin/python manage.py migrate
        sudo -u stockscanner ./venv/bin/python manage.py collectstatic --noinput
        sudo systemctl restart stockscanner
        echo "Update complete!"
        ;;
    restart)
        echo "Restarting Stock Scanner..."
        sudo systemctl restart stockscanner nginx
        echo "Restart complete!"
        ;;
    status)
        sudo systemctl status stockscanner nginx --no-pager
        ;;
    logs)
        sudo journalctl -u stockscanner -f
        ;;
    *)
        echo "Usage: \\$0 {update|restart|status|logs}"
        exit 1
        ;;
esac
EOF

sudo chmod +x /usr/local/bin/stockscanner-maintenance

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}📋 Next steps:${NC}"
echo -e "   1. Edit /var/www/stock-scanner/.env with your configuration"
echo -e "   2. Run: sudo -u stockscanner python manage.py createsuperuser"
echo -e "   3. Test the site: https://retailtradescan.net"
echo -e "   4. Use 'stockscanner-maintenance' command for maintenance"
'''
        
        deploy_script_file = self.project_path / "deploy_secure.sh"
        with open(deploy_script_file, 'w') as f:
            f.write(deploy_script)
        
        # Make executable
        os.chmod(deploy_script_file, 0o755)
        
        self.print_success(f"Deployment script created: {deploy_script_file}")

    def run_security_hardening(self):
        """Run complete security hardening process"""
        print("🔐 Stock Scanner Security Hardening for IONOS Hosting")
        print("=" * 60)
        
        # Create all security components
        secret_key = self.create_production_settings()
        self.create_security_middleware()
        self.create_environment_file(secret_key)
        self.create_log_directories()
        self.create_security_requirements()
        self.create_deployment_script()
        
        print("\n🎉 Security hardening completed successfully!")
        print("\n📋 Security checklist:")
        print("   ✅ Production settings with secure defaults")
        print("   ✅ Custom security middleware")
        print("   ✅ Secure environment configuration")
        print("   ✅ Logging and monitoring setup")
        print("   ✅ Security-focused requirements")
        print("   ✅ Automated deployment script")
        
        print("\n🔑 IMPORTANT:")
        print(f"   📄 Your Django secret key: {secret_key}")
        print("   📝 Edit .env file with your passwords")
        print("   🚀 Run ./deploy_secure.sh to deploy")
        print("   🔒 Change default passwords immediately")
        
        return True

def main():
    """Main execution function"""
    hardening = SecurityHardening()
    success = hardening.run_security_hardening()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()