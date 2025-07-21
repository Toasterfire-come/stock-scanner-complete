# WordPress Production Settings for Stock Scanner
import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'your-production-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Production domains
ALLOWED_HOSTS = [
    'your-domain.com',  # Replace with your actual domain
    'www.your-domain.com',
    'api.your-domain.com',  # If using subdomain for API
    'localhost',  # For local testing
    '127.0.0.1',
]

# WordPress Integration Settings
CORS_ALLOWED_ORIGINS = [
    "https://your-wordpress-site.com",  # Replace with your WordPress URL
    "https://www.your-wordpress-site.com",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False  # Set to False for production security

# WordPress API Authentication
WORDPRESS_API_SECRET = os.getenv('WORDPRESS_API_SECRET', 'shared-secret-key')
WORDPRESS_SITE_URL = os.getenv('WORDPRESS_SITE_URL', 'https://your-wordpress-site.com')

# Stock Usage Limits (per month)
STOCK_LIMITS = {
    'free': 15,
    'premium': 1000,
    'professional': 10000,
}

# Paid Membership Pro Integration
PMP_API_KEY = os.getenv('PMP_API_KEY', 'your-pmp-api-key')
PMP_WEBHOOK_SECRET = os.getenv('PMP_WEBHOOK_SECRET', 'webhook-secret')

# Email Configuration (Gmail)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'noreply.retailtradescanner@gmail.com'
EMAIL_HOST_PASSWORD = 'mzqmvhsjqeqrjmjv'

# Database (SQLite for simplicity)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'stock_scanner_production.db',
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
        'wordpress': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'wordpress.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'wordpress_integration': {
            'handlers': ['wordpress'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session Security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True