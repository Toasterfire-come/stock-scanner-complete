from .settings import *
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Production settings
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.mysql'),
        'NAME': os.environ.get('DB_NAME', 'stockscanner_production'),
        'USER': os.environ.get('DB_USER', 'django_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '300')),
        'CONN_HEALTH_CHECKS': os.environ.get('DB_CONN_HEALTH_CHECKS', 'True').lower() == 'true',
    }
}

# Security
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable must be set")

SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True').lower() == 'true'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'True').lower() == 'true'
SECURE_BROWSER_XSS_FILTER = os.environ.get('SECURE_BROWSER_XSS_FILTER', 'True').lower() == 'true'
SECURE_CONTENT_TYPE_NOSNIFF = os.environ.get('SECURE_CONTENT_TYPE_NOSNIFF', 'True').lower() == 'true'
X_FRAME_OPTIONS = 'DENY'

# Static files
STATIC_URL = os.environ.get('STATIC_URL', '/static/')
STATIC_ROOT = os.environ.get('STATIC_ROOT', '/var/www/stockscanner/static/')
MEDIA_URL = os.environ.get('MEDIA_URL', '/media/')
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', '/var/www/stockscanner/media/')

# CDN Configuration (optional)
if os.environ.get('CDN_URL'):
    STATIC_URL = os.environ.get('CDN_URL') + STATIC_URL

# CORS for WordPress integration
cors_origins = os.environ.get('CORS_ALLOWED_ORIGINS', 'https://localhost').split(',')
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins]
CORS_ALLOW_CREDENTIALS = os.environ.get('CORS_ALLOW_CREDENTIALS', 'True').lower() == 'true'

# API Rate limiting
anon_rate = os.environ.get('API_RATE_LIMIT_ANON', '1000/day')
user_rate = os.environ.get('API_RATE_LIMIT_USER', '10000/day')

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': anon_rate,
        'user': user_rate
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100
}

# Logging
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
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/stockscanner/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'stocks': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'news': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Cache configuration (optional - requires Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Email configuration (for production notifications)
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com')

# Admin emails
ADMINS = [
    ('Admin', os.environ.get('ADMIN_EMAIL', 'admin@yourdomain.com')),
]
MANAGERS = ADMINS

# Time zone
USE_TZ = os.environ.get('USE_TZ', 'True').lower() == 'true'
TIME_ZONE = os.environ.get('TIME_ZONE', 'UTC')

# Internationalization
LANGUAGE_CODE = os.environ.get('LANGUAGE_CODE', 'en-us')
USE_I18N = os.environ.get('USE_I18N', 'True').lower() == 'true'
USE_L10N = os.environ.get('USE_L10N', 'True').lower() == 'true'

# WordPress Integration Settings
WORDPRESS_URL = os.environ.get('WORDPRESS_URL', 'https://yourdomain.com')
WORDPRESS_API_URL = os.environ.get('WORDPRESS_API_URL', 'https://yourdomain.com/wp-json/wp/v2')
DJANGO_API_URL = os.environ.get('DJANGO_API_URL', 'https://api.yourdomain.com')
DJANGO_API_KEY = os.environ.get('DJANGO_API_KEY', '')

# SEO & Analytics
GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', '')
GOOGLE_TAG_MANAGER_ID = os.environ.get('GOOGLE_TAG_MANAGER_ID', '')
GOOGLE_SITE_VERIFICATION = os.environ.get('GOOGLE_SITE_VERIFICATION', '')
BING_SITE_VERIFICATION = os.environ.get('BING_SITE_VERIFICATION', '')

# Social Media Integration
FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID', '')
TWITTER_SITE = os.environ.get('TWITTER_SITE', '')
LINKEDIN_COMPANY_ID = os.environ.get('LINKEDIN_COMPANY_ID', '')

# Organization Schema Data
ORGANIZATION_NAME = os.environ.get('ORGANIZATION_NAME', 'Stock Scanner')
ORGANIZATION_DESCRIPTION = os.environ.get('ORGANIZATION_DESCRIPTION', 'Professional stock market analysis platform')
ORGANIZATION_LOGO_URL = os.environ.get('ORGANIZATION_LOGO_URL', '')
ORGANIZATION_ADDRESS = os.environ.get('ORGANIZATION_ADDRESS', '')
ORGANIZATION_PHONE = os.environ.get('ORGANIZATION_PHONE', '')
ORGANIZATION_EMAIL = os.environ.get('ORGANIZATION_EMAIL', '')

# Feature Flags
ENABLE_AI_SENTIMENT_ANALYSIS = os.environ.get('ENABLE_AI_SENTIMENT_ANALYSIS', 'True').lower() == 'true'
ENABLE_ADVANCED_ANALYTICS = os.environ.get('ENABLE_ADVANCED_ANALYTICS', 'True').lower() == 'true'
ENABLE_PREDICTIVE_MODELS = os.environ.get('ENABLE_PREDICTIVE_MODELS', 'False').lower() == 'true'
ENABLE_REAL_TIME_UPDATES = os.environ.get('ENABLE_REAL_TIME_UPDATES', 'True').lower() == 'true'
ENABLE_MOBILE_APP_API = os.environ.get('ENABLE_MOBILE_APP_API', 'True').lower() == 'true'
ENABLE_WEBHOOK_NOTIFICATIONS = os.environ.get('ENABLE_WEBHOOK_NOTIFICATIONS', 'True').lower() == 'true'
ENABLE_ADVANCED_CHARTING = os.environ.get('ENABLE_ADVANCED_CHARTING', 'True').lower() == 'true'

# Stock Data Configuration
STOCK_UPDATE_INTERVAL = int(os.environ.get('STOCK_UPDATE_INTERVAL', '10'))
NEWS_UPDATE_INTERVAL = int(os.environ.get('NEWS_UPDATE_INTERVAL', '30'))
CLEANUP_INTERVAL = int(os.environ.get('CLEANUP_INTERVAL', '1440'))

# Data Retention
STOCK_DATA_RETENTION_DAYS = int(os.environ.get('STOCK_DATA_RETENTION_DAYS', '365'))
NEWS_DATA_RETENTION_DAYS = int(os.environ.get('NEWS_DATA_RETENTION_DAYS', '90'))
LOG_RETENTION_DAYS = int(os.environ.get('LOG_RETENTION_DAYS', '30'))

# Maintenance Mode
MAINTENANCE_MODE = os.environ.get('MAINTENANCE_MODE', 'False').lower() == 'true'
MAINTENANCE_MESSAGE = os.environ.get('MAINTENANCE_MESSAGE', 'Site temporarily unavailable for maintenance')
MAINTENANCE_ALLOWED_IPS = os.environ.get('MAINTENANCE_ALLOWED_IPS', '127.0.0.1').split(',')

# API Documentation
ENABLE_API_DOCS = os.environ.get('ENABLE_API_DOCS', 'True').lower() == 'true'
API_DOCS_URL = os.environ.get('API_DOCS_URL', '/api/docs/')
API_TITLE = os.environ.get('API_TITLE', 'Stock Scanner API')
API_VERSION = os.environ.get('API_VERSION', 'v1')
API_DESCRIPTION = os.environ.get('API_DESCRIPTION', 'Professional stock market data and analysis API')