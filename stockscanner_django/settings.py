import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

# XAMPP Auto-Detection and Configuration
XAMPP_PATH = r"C:\xampp"
XAMPP_MYSQL_PATH = os.path.join(XAMPP_PATH, "mysql", "bin")
IS_XAMPP_AVAILABLE = os.path.exists(XAMPP_PATH) and os.path.exists(XAMPP_MYSQL_PATH)

if IS_XAMPP_AVAILABLE:
    print("INFO: XAMPP detected - configuring for XAMPP MySQL")
    # Add XAMPP MySQL to PATH
    if XAMPP_MYSQL_PATH not in os.environ.get('PATH', ''):
        os.environ['PATH'] = os.environ.get('PATH', '') + os.pathsep + XAMPP_MYSQL_PATH

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-development-key')

# Security: Default DEBUG to False for safety
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'django_extensions',
    'stocks',
    'emails',
    'core',
    'news',
    'billing',
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
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'stockscanner_django.wsgi.application'

# Database configuration - Auto-detect XAMPP or use environment settings
if IS_XAMPP_AVAILABLE:
    # XAMPP Configuration (no password by default)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'stockscanner'),
            'USER': os.environ.get('DB_USER', 'root'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),  # XAMPP default: no password
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'use_unicode': True,
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES',innodb_strict_mode=1",
                'autocommit': True,
                'connect_timeout': 60,
                'read_timeout': 300,
                'write_timeout': 300,
            },
            'CONN_MAX_AGE': 0,
            'ATOMIC_REQUESTS': True,
        }
    }
    print("INFO: Using XAMPP MySQL configuration")
else:
    # Standard MySQL configuration
    # Security: No default password - must be provided via environment
    DATABASES = {
        'default': {
            'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.mysql'),
            'NAME': os.environ.get('DB_NAME', 'stock_scanner_nasdaq'),
            'USER': os.environ.get('DB_USER', 'django_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),  # No default - required!
            'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
            # Performance: Connection pooling
            'CONN_MAX_AGE': 600,  # Keep connections alive for 10 minutes
        }
    }
    print("INFO: Using standard MySQL configuration")

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings - Security: Never allow all origins
CORS_ALLOW_ALL_ORIGINS = False

# Production origins (update with your actual domain)
CORS_ALLOWED_ORIGINS = [
    'https://tradescanpro.com',
    'https://www.tradescanpro.com',
    'https://app.tradescanpro.com',
]

# Add development origins only in DEBUG mode
if DEBUG:
    CORS_ALLOWED_ORIGINS += [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:8000',
        'http://127.0.0.1:8000',
    ]

CORS_ALLOW_CREDENTIALS = True

# REST Framework - Security: Require authentication by default
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Changed from AllowAny
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'MAX_PAGE_SIZE': 100,  # Performance: Limit max page size
    # Security: Rate limiting
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',  # Anonymous users: 100 requests per hour
        'user': '1000/hour',  # Authenticated users: 1000 requests per hour
        'burst': '60/minute',  # Burst protection: 60 per minute
    }
}

# API Configuration
API_CONFIG = {
    'DEFAULT_PAGE_SIZE': 50,
    'MAX_PAGE_SIZE': 100,
    'CACHE_TIMEOUT': 60,  # 60 seconds cache
    'MARKET_CAP_LARGE': 10_000_000_000,  # $10B
    'MARKET_CAP_SMALL': 2_000_000_000,   # $2B
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'stock-scanner-cache',
    }
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Stock API Configuration
YFINANCE_RATE_LIMIT = float(os.environ.get('YFINANCE_RATE_LIMIT', '0.5'))  # 0.5 second delay
YFINANCE_TIMEOUT = int(os.environ.get('YFINANCE_TIMEOUT', '15'))  # 15 seconds timeout
YFINANCE_RETRIES = int(os.environ.get('YFINANCE_RETRIES', '3'))  # 3 retries

# Backup API keys (optional)
FINNHUB_KEYS = [
    key.strip() for key in os.environ.get('FINNHUB_API_KEYS', '').split(',') 
    if key.strip()
]

# PayPal Configuration
PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'sandbox')  # 'sandbox' or 'live'
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', '')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET', '')

# PayPal Subscription Plan IDs (get these from PayPal dashboard)
PAYPAL_PLAN_BRONZE_MONTHLY = os.environ.get('PAYPAL_PLAN_BRONZE_MONTHLY', '')
PAYPAL_PLAN_BRONZE_ANNUAL = os.environ.get('PAYPAL_PLAN_BRONZE_ANNUAL', '')
PAYPAL_PLAN_SILVER_MONTHLY = os.environ.get('PAYPAL_PLAN_SILVER_MONTHLY', '')
PAYPAL_PLAN_SILVER_ANNUAL = os.environ.get('PAYPAL_PLAN_SILVER_ANNUAL', '')
PAYPAL_PLAN_GOLD_MONTHLY = os.environ.get('PAYPAL_PLAN_GOLD_MONTHLY', '')
PAYPAL_PLAN_GOLD_ANNUAL = os.environ.get('PAYPAL_PLAN_GOLD_ANNUAL', '')

# Frontend URL for PayPal redirects
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

# PayPal Webhook ID for signature verification
PAYPAL_WEBHOOK_ID = os.environ.get('PAYPAL_WEBHOOK_ID', '')

# Security Settings - HTTPS Enforcement (disabled in DEBUG mode)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Secure cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

    # HSTS - Tell browsers to always use HTTPS
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Logging with security filtering
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'billing': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'stocks': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Note: Sensitive data (passwords, tokens, etc.) should never be logged
# Filter request.POST data in production before logging