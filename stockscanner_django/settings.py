"""
Django settings for stockscanner_django project.

For production deployment on retailtradescanner.com
"""

import os
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', "django-insecure-3o(csaf*^k*d41wf+k#tt$jcu13wo*o^*41*h&)18b1r-^7krg")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '10.6.200.155', 'retailtradescanner.com', 'www.retailtradescanner.com', 'api.retailtradescanner.com']

# Add additional hosts from environment
additional_hosts = os.environ.get('ADDITIONAL_HOSTS', '')
if additional_hosts:
    ALLOWED_HOSTS.extend([host.strip() for host in additional_hosts.split(',') if host.strip()])


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "core",
    "emails",
    "news",
    "stocks",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "stockscanner_django.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'core/templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "stockscanner_django.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Default to SQLite for development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# MySQL setup - using mysqlclient (native MySQL driver)
print("Linux/Windows MySQL setup - using native mysqlclient driver")

# Use DATABASE_URL environment variable for production
if os.environ.get('DATABASE_URL'):
    try:
        import dj_database_url
        from urllib.parse import quote_plus
        
        database_url = os.environ.get('DATABASE_URL')
        
        # Parse the database URL and detect the database type
        DATABASES['default'] = dj_database_url.parse(database_url)
        
        # Auto-detect database engine from URL
        if database_url.startswith('postgresql://'):
            DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
            # PostgreSQL Windows/Git Bash optimizations
            DATABASES['default']['OPTIONS'] = {
                'connect_timeout': 10,
                'options': '-c default_transaction_isolation=read_committed'
            }
            # Ensure password authentication works on Windows
            if 'HOST' not in DATABASES['default'] or DATABASES['default']['HOST'] in ['localhost', '127.0.0.1']:
                DATABASES['default']['HOST'] = '127.0.0.1'
            print(f"SUCCESS: Using PostgreSQL database")
        elif database_url.startswith('mysql://'):
            DATABASES['default']['ENGINE'] = 'django.db.backends.mysql'
            # MySQL production optimizations
            DATABASES['default']['OPTIONS'] = {
                'charset': 'utf8mb4',
                'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO',
                'isolation_level': 'READ COMMITTED',
            }
            # Connection pooling for production
            DATABASES['default']['CONN_MAX_AGE'] = int(os.environ.get('DB_CONN_MAX_AGE', 300))
            DATABASES['default']['CONN_HEALTH_CHECKS'] = os.environ.get('DB_CONN_HEALTH_CHECKS', 'true').lower() == 'true'
            print(f"SUCCESS: Using MySQL database with production optimizations (Linux optimized)")
        else:
            # Default to PostgreSQL for backward compatibility
            DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
            print(f"SUCCESS: Using PostgreSQL database (default)")
            
    except ImportError:
        print("Warning: dj_database_url not installed. Using SQLite for development.")

# Alternative database configuration for Windows/Git Bash
if os.environ.get('DB_ENGINE') and not os.environ.get('DATABASE_URL'):
    DATABASES['default'] = {
        'ENGINE': os.environ.get('DB_ENGINE'),
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
    print(f"SUCCESS: Using {os.environ.get('DB_ENGINE')} with explicit settings")


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Celery Configuration - Optional for development
celery_broker_url = os.environ.get('CELERY_BROKER_URL')

# Check if Redis is available for Celery
CELERY_ENABLED = os.environ.get('CELERY_ENABLED', 'false').lower() == 'true'

if CELERY_ENABLED and celery_broker_url:
    CELERY_BROKER_URL = celery_broker_url
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_BACKEND = celery_broker_url
else:
    # Development mode - disable Celery
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True
    CELERY_BROKER_URL = None


# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'noreply.retailtradescanner@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'mzqmvhsjqeqrjmjv')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'stockscanner_django', 'static'),
]

# Create static directories if they don't exist
os.makedirs(STATIC_ROOT, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'stockscanner_django', 'static'), exist_ok=True)

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50
}

# CORS Configuration for WordPress Integration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://retailtradescanner.com",
    "https://www.retailtradescanner.com",
    "http://retailtradescanner.com",
    "http://www.retailtradescanner.com",
    # Add your WordPress domain here
]

CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only in development

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
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Cache Configuration for API responses
redis_url = os.environ.get('REDIS_URL')
if redis_url and ('://' in redis_url):
    # Production Redis cache
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': redis_url,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
    # Development local memory cache
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'stock-scanner-cache',
            'TIMEOUT': 300,  # 5 minutes default
            'OPTIONS': {
                'MAX_ENTRIES': 1000,
                'CULL_FREQUENCY': 3,
            }
        }
    }

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Production Security Settings
if not DEBUG:
    # SSL/HTTPS settings for production
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    
    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Additional security headers
    X_FRAME_OPTIONS = 'DENY'

# Ensure logs directory exists and handle errors gracefully
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
try:
    os.makedirs(LOGS_DIR, exist_ok=True)
    USE_FILE_LOGGING = True
except (OSError, PermissionError):
    # If we can't create logs directory, only use console logging
    USE_FILE_LOGGING = False

# Logging Configuration
LOGGING_HANDLERS = {
    'console': {
        'level': 'INFO',
        'class': 'logging.StreamHandler',
        'formatter': 'simple',
    },
}

# Add file handler only if we can write to logs directory
if USE_FILE_LOGGING:
    LOGGING_HANDLERS['file'] = {
        'level': 'INFO',
        'class': 'logging.FileHandler',
        'filename': os.path.join(LOGS_DIR, 'django.log'),
        'formatter': 'verbose',
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': LOGGING_HANDLERS,
    'root': {
        'handlers': ['console'] + (['file'] if USE_FILE_LOGGING else []),
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'stocks': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ===== STOCK DATA API CONFIGURATION =====
# Primary: Yahoo Finance (yfinance) - Unlimited and Free
YFINANCE_RATE_LIMIT = float(os.environ.get('YFINANCE_RATE_LIMIT', '1.0'))
YFINANCE_TIMEOUT = int(os.environ.get('YFINANCE_TIMEOUT', '15'))
YFINANCE_RETRIES = int(os.environ.get('YFINANCE_RETRIES', '3'))

# Backup APIs - Simplified
FINNHUB_KEYS = []
for i in range(1, 3):
    key = os.environ.get(f'FINNHUB_API_KEY_{i}')
    if key:
        FINNHUB_KEYS.append(key)

# WordPress Integration
WORDPRESS_URL = os.environ.get('WORDPRESS_URL', '')
WORDPRESS_USERNAME = os.environ.get('WORDPRESS_USERNAME', '')
WORDPRESS_APP_PASSWORD = os.environ.get('WORDPRESS_APP_PASSWORD', '')

# Windows Git Bash PyMySQL compatibility
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    print("SUCCESS: PyMySQL configured for Windows compatibility")
except ImportError:
    print("WARNING: PyMySQL not available, using default MySQL driver")