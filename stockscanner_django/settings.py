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
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "api.retailtradescanner.com"]
# API key for WordPress/backend-to-backend auth
WORDPRESS_API_KEY = os.environ.get('WORDPRESS_API_KEY', '')

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
]

MIDDLEWARE = [
    'stocks.middleware.CORSMiddleware',  # Custom CORS for WordPress
    'stocks.middleware.APICompatibilityMiddleware',  # API/HTML detection
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
    DATABASES = {
        'default': {
            'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.mysql'),
            'NAME': os.environ.get('DB_NAME', 'stockscanner'),
            'USER': os.environ.get('DB_USER', 'stockscanner_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            }
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
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
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

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
}
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = ["https://api.retailtradescanner.com"]
