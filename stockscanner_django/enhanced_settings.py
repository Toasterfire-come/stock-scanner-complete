"""
Enhanced Django Settings for Production-Ready Stock Scanner
Includes all optimizations, caching, throttling, and monitoring configurations
"""

import os
import platform
from pathlib import Path

# Import base settings
from .settings import *

# ===== PERFORMANCE OPTIMIZATIONS =====

# Enhanced REST Framework configuration with optimizations
REST_FRAMEWORK.update({
    'DEFAULT_PAGINATION_CLASS': 'stocks.pagination.OptimizedStockPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_THROTTLE_CLASSES': [
        'stocks.throttling.StockAPIThrottle',
        'stocks.throttling.AnonymousAPIThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'stock_api': '200/hour',
        'anon_api': '30/hour',
        'search': '100/hour',
        'bulk_operation': '10/hour',
        'realtime': '300/hour',
        'admin_api': '1000/hour',
        'dynamic': '200/hour',
        'ip_based': '1000/hour',
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'EXCEPTION_HANDLER': 'stocks.error_handlers.custom_exception_handler',
})

# ===== CACHING CONFIGURATION =====

# Enhanced caching with Redis support
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache' if 'REDIS_URL' in os.environ else 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 20,
                'retry_on_timeout': True,
            },
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'KEY_PREFIX': 'stock_scanner',
        'TIMEOUT': 300,  # 5 minutes default
    },
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache' if 'REDIS_URL' in os.environ else 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': os.environ.get('REDIS_URL', 'cache_sessions') if 'REDIS_URL' in os.environ else 'cache_sessions',
        'TIMEOUT': 86400,  # 24 hours
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        } if 'REDIS_URL' in os.environ else {},
    },
    'query_cache': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'query-cache',
        'TIMEOUT': 180,  # 3 minutes for query results
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Use Redis for sessions if available
if 'REDIS_URL' in os.environ:
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'sessions'

# Cache key prefixes
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 300
CACHE_MIDDLEWARE_KEY_PREFIX = 'stock_scanner'

# ===== DATABASE OPTIMIZATIONS =====

# Enhanced database configuration with connection pooling
DATABASES['default'].update({
    'CONN_MAX_AGE': 600,  # 10 minutes
    'ATOMIC_REQUESTS': True,
    'OPTIONS': {
        **DATABASES['default'].get('OPTIONS', {}),
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES',innodb_strict_mode=1",
        'charset': 'utf8mb4',
        'use_unicode': True,
        'autocommit': True,
        'connect_timeout': 60,
        'read_timeout': 300,
        'write_timeout': 300,
        # MySQL specific optimizations
        'init_command': (
            "SET sql_mode='STRICT_TRANS_TABLES';"
            "SET innodb_strict_mode=1;"
            "SET transaction_isolation='READ-COMMITTED';"
        ),
    }
})

# ===== MIDDLEWARE ENHANCEMENTS =====

# Add performance and monitoring middleware
MIDDLEWARE = [
    'stocks.middleware.PerformanceMonitoringMiddleware',
    'stocks.throttling.SmartThrottleMiddleware',
    'stocks.monitoring.HealthCheckMiddleware',
] + MIDDLEWARE + [
    'stocks.middleware.RequestLoggingMiddleware',
    'stocks.middleware.SecurityHeadersMiddleware',
]

# ===== LOGGING CONFIGURATION =====

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
        'json': {
            'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/stock_scanner.log',
            'maxBytes': 1024*1024*50,  # 50MB
            'backupCount': 5,
            'formatter': 'json',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/errors.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'performance_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/performance.log',
            'maxBytes': 1024*1024*25,  # 25MB
            'backupCount': 3,
            'formatter': 'json',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['performance_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'stocks': {
            'handlers': ['console', 'file', 'performance_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'stocks.performance': {
            'handlers': ['performance_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'stocks.security': {
            'handlers': ['error_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# ===== SECURITY ENHANCEMENTS =====

# Enhanced security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'

# CSRF and session security
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 86400  # 24 hours

# Additional security headers
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# ===== PERFORMANCE MONITORING =====

# Performance monitoring settings
PERFORMANCE_MONITORING = {
    'ENABLE_QUERY_MONITORING': True,
    'SLOW_QUERY_THRESHOLD': 0.1,  # 100ms
    'ENABLE_CACHE_MONITORING': True,
    'ENABLE_REQUEST_MONITORING': True,
    'LOG_SLOW_REQUESTS': True,
    'SLOW_REQUEST_THRESHOLD': 2.0,  # 2 seconds
}

# ===== CELERY CONFIGURATION (for background tasks) =====

if 'REDIS_URL' in os.environ:
    CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
else:
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'cache+memory://'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# Task routing
CELERY_TASK_ROUTES = {
    'stocks.tasks.update_stock_prices': {'queue': 'stock_updates'},
    'stocks.tasks.send_alerts': {'queue': 'notifications'},
    'stocks.tasks.generate_reports': {'queue': 'reports'},
}

# ===== API RATE LIMITING =====

# Throttle settings
DEFAULT_THROTTLE_RATES = {
    'anon': '30/hour',
    'user': '200/hour',
    'premium': '1000/hour',
}

# ===== CORS CONFIGURATION =====

# Enhanced CORS settings
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [
    'https://yourdomain.com',
    'https://www.yourdomain.com',
    'https://api.yourdomain.com',
] if not DEBUG else [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.yourdomain\.com$",
] if not DEBUG else []

CORS_ALLOW_CREDENTIALS = True
CORS_PREFLIGHT_MAX_AGE = 86400

# ===== STATIC AND MEDIA FILES =====

# Enhanced static files configuration
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Compression and optimization
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# ===== CUSTOM SETTINGS =====

# Stock data update intervals
STOCK_UPDATE_INTERVALS = {
    'real_time': 30,  # seconds
    'fast': 300,     # 5 minutes
    'normal': 900,   # 15 minutes
    'slow': 3600,    # 1 hour
}

# API versioning
API_VERSION = 'v1'
API_TITLE = 'Stock Scanner API'
API_DESCRIPTION = 'Comprehensive stock market data API with real-time updates'

# Feature flags
FEATURE_FLAGS = {
    'ENABLE_REAL_TIME_UPDATES': True,
    'ENABLE_PORTFOLIO_TRACKING': True,
    'ENABLE_SOCIAL_FEATURES': True,
    'ENABLE_ADVANCED_ANALYTICS': True,
    'ENABLE_NEWS_INTEGRATION': True,
    'ENABLE_PAYMENT_PROCESSING': True,
}

# Health check configuration
HEALTH_CHECK_ENDPOINTS = {
    'simple': '/health/',
    'detailed': '/health/detailed/',
    'metrics': '/health/metrics/',
    'performance': '/health/performance/',
}

# ===== EMAIL CONFIGURATION =====

# Enhanced email settings for production
if not DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@stockscanner.com')
    SERVER_EMAIL = DEFAULT_FROM_EMAIL

# ===== ERROR REPORTING =====

# Error reporting configuration
ADMINS = [
    ('Admin', os.environ.get('ADMIN_EMAIL', 'admin@stockscanner.com')),
]

MANAGERS = ADMINS

# ===== INTERNATIONALIZATION =====

# Enhanced i18n settings
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# ===== FILE UPLOADS =====

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# ===== CUSTOM VALIDATORS =====

# Custom password validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'stocks.validators.CustomPasswordValidator',
    },
]

# ===== MONITORING AND ALERTING =====

# Monitoring configuration
MONITORING = {
    'HEALTH_CHECK_INTERVAL': 60,  # seconds
    'PERFORMANCE_ALERT_THRESHOLD': {
        'cpu': 80,  # percent
        'memory': 85,  # percent
        'disk': 90,  # percent
        'response_time': 2000,  # milliseconds
    },
    'ENABLE_ALERTS': not DEBUG,
    'ALERT_CHANNELS': ['email', 'log'],
}

# ===== DEVELOPMENT OVERRIDES =====

if DEBUG:
    # Development-specific settings
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
    
    # Disable some security features in development
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0
    
    # Enable Django Debug Toolbar if available
    try:
        import debug_toolbar
        INSTALLED_APPS.append('debug_toolbar')
        MIDDLEWARE.insert(1, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
        }
    except ImportError:
        pass

# Print configuration summary
print(f"🚀 Stock Scanner Django Configuration Loaded")
print(f"📊 Environment: {'Development' if DEBUG else 'Production'}")
print(f"💾 Database: {DATABASES['default']['ENGINE'].split('.')[-1]}")
print(f"🔄 Cache Backend: {CACHES['default']['BACKEND'].split('.')[-1]}")
print(f"📈 Performance Monitoring: {'Enabled' if PERFORMANCE_MONITORING['ENABLE_QUERY_MONITORING'] else 'Disabled'}")
print(f"🔒 Security Headers: {'Enabled' if not DEBUG else 'Development Mode'}")
print(f"⚡ API Throttling: {'Enabled' if REST_FRAMEWORK.get('DEFAULT_THROTTLE_CLASSES') else 'Disabled'}")