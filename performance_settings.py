"""
Performance-Optimized Settings for Stock Scanner API
Add these to your settings.py or import this file for maximum performance
"""

import os
from pathlib import Path

# Performance-related settings
PERFORMANCE_SETTINGS = {
    
    # ===== CACHING CONFIGURATION =====
    'CACHES': {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/1',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 20,
                    'retry_on_timeout': True,
                },
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            },
            'TIMEOUT': 300,  # 5 minutes default timeout
            'KEY_PREFIX': 'stock_scanner',
            'VERSION': 1,
        },
        'sessions': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/2',
            'TIMEOUT': 3600,  # 1 hour for sessions
        },
        'static': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/3',
            'TIMEOUT': 86400,  # 24 hours for static content
        }
    },
    
    # Use Redis for sessions
    'SESSION_ENGINE': 'django.contrib.sessions.backends.cache',
    'SESSION_CACHE_ALIAS': 'sessions',
    'SESSION_COOKIE_AGE': 3600,  # 1 hour
    'SESSION_SAVE_EVERY_REQUEST': False,
    'SESSION_EXPIRE_AT_BROWSER_CLOSE': False,
    
    # ===== DATABASE OPTIMIZATION =====
    'DATABASE_OPTIONS': {
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        'charset': 'utf8mb4',
        'use_unicode': True,
        'autocommit': True,
        'conn_max_age': 3600,  # Keep connections alive for 1 hour
        'OPTIONS': {
            'MAX_CONNS': 20,
            'MIN_CONNS': 5,
            'CONN_HEALTH_CHECKS': True,
        }
    },
    
    # ===== MIDDLEWARE OPTIMIZATION =====
    'OPTIMIZED_MIDDLEWARE': [
        'django.middleware.cache.UpdateCacheMiddleware',
        'django.middleware.gzip.GZipMiddleware',
        'utils.compression_middleware.CompressionMiddleware',
        'utils.cache_manager.PerformanceMiddleware',
        'django.middleware.http.ConditionalGetMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'utils.compression_middleware.ResponseOptimizationMiddleware',
        'django.middleware.cache.FetchFromCacheMiddleware',
    ],
    
    # ===== STATIC FILES OPTIMIZATION =====
    'STATIC_URL': '/static/',
    'STATIC_ROOT': os.path.join(Path(__file__).parent, 'staticfiles'),
    'STATICFILES_STORAGE': 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage',
    
    'STATICFILES_FINDERS': [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    ],
    
    # ===== TEMPLATES OPTIMIZATION =====
    'TEMPLATE_OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
        'loaders': [
            ('django.template.loaders.cached.Loader', [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]),
        ],
        'builtins': [
            'django.templatetags.static',
        ],
    },
    
    # ===== SECURITY HEADERS FOR PERFORMANCE =====
    'SECURITY_HEADERS': {
        'SECURE_BROWSER_XSS_FILTER': True,
        'SECURE_CONTENT_TYPE_NOSNIFF': True,
        'SECURE_HSTS_SECONDS': 31536000,
        'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
        'SECURE_HSTS_PRELOAD': True,
        'X_FRAME_OPTIONS': 'DENY',
        'SECURE_REFERRER_POLICY': 'strict-origin-when-cross-origin',
    },
    
    # ===== COMPRESSION SETTINGS =====
    'ENABLE_COMPRESSION': True,
    'ENABLE_RESPONSE_OPTIMIZATION': True,
    'COMPRESSION_MIN_SIZE': 200,
    'COMPRESSION_LEVEL': 6,
    
    # ===== LOGGING OPTIMIZATION =====
    'LOGGING_CONFIG': {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'performance': {
                'format': '[{levelname}] {asctime} {name}: {message}',
                'style': '{',
            },
        },
        'handlers': {
            'performance_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/performance.log',
                'maxBytes': 1024*1024*10,  # 10MB
                'backupCount': 5,
                'formatter': 'performance',
            },
            'console': {
                'level': 'WARNING',
                'class': 'logging.StreamHandler',
                'formatter': 'performance',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
            'performance': {
                'handlers': ['performance_file'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    },
    
    # ===== EMAIL OPTIMIZATION =====
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_TIMEOUT': 10,
    
    # ===== FILE UPLOAD OPTIMIZATION =====
    'FILE_UPLOAD_MAX_MEMORY_SIZE': 5242880,  # 5MB
    'DATA_UPLOAD_MAX_MEMORY_SIZE': 5242880,  # 5MB
    'FILE_UPLOAD_PERMISSIONS': 0o644,
    
    # ===== INTERNATIONALIZATION OPTIMIZATION =====
    'USE_I18N': False,  # Disable if not needed for performance
    'USE_L10N': True,
    'USE_TZ': True,
    
    # ===== PERFORMANCE FLAGS =====
    'DEBUG': False,
    'ALLOWED_HOSTS': ['*'],  # Configure properly for production
    'INTERNAL_IPS': ['127.0.0.1', 'localhost'],
    
    # Custom performance settings
    'CACHE_MIDDLEWARE_SECONDS': 600,  # 10 minutes
    'CACHE_MIDDLEWARE_KEY_PREFIX': 'stock_scanner',
    
    # Database query optimization
    'DEFAULT_AUTO_FIELD': 'django.db.models.BigAutoField',
    
    # Timezone optimization
    'TIME_ZONE': 'UTC',
    
    # Message framework optimization
    'MESSAGE_STORAGE': 'django.contrib.messages.storage.cookie.CookieStorage',
}

# ===== PRODUCTION OPTIMIZATIONS =====
PRODUCTION_OPTIMIZATIONS = {
    'SECURE_SSL_REDIRECT': True,
    'SECURE_PROXY_SSL_HEADER': ('HTTP_X_FORWARDED_PROTO', 'https'),
    'SESSION_COOKIE_SECURE': True,
    'CSRF_COOKIE_SECURE': True,
    'SESSION_COOKIE_HTTPONLY': True,
    'CSRF_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SAMESITE': 'Lax',
    'CSRF_COOKIE_SAMESITE': 'Lax',
}

# ===== DEVELOPMENT OPTIMIZATIONS =====
DEVELOPMENT_OPTIMIZATIONS = {
    'INTERNAL_IPS': ['127.0.0.1', '10.0.2.2'],
    'DEBUG_TOOLBAR_CONFIG': {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
        'SHOW_COLLAPSED': True,
        'PROFILER_MAX_DEPTH': 10,
    },
}

# ===== API RATE LIMITING =====
API_RATE_LIMITING = {
    'RATELIMIT_ENABLE': True,
    'RATELIMIT_USE_CACHE': 'default',
    'RATELIMIT_VIEW': 'core.views.ratelimited',
    
    # Rate limits by endpoint
    'STOCK_API_RATE': '100/h',  # 100 requests per hour for stock data
    'TRENDING_API_RATE': '50/h',  # 50 requests per hour for trending
    'ANALYTICS_API_RATE': '30/h',  # 30 requests per hour for analytics
    'SEARCH_API_RATE': '200/h',  # 200 requests per hour for search
}

# ===== MONITORING SETTINGS =====
MONITORING_SETTINGS = {
    'ENABLE_PERFORMANCE_MONITORING': True,
    'SLOW_QUERY_THRESHOLD': 0.1,  # Log queries taking > 100ms
    'MEMORY_USAGE_THRESHOLD': 80,  # Alert at 80% memory usage
    'RESPONSE_TIME_THRESHOLD': 1.0,  # Alert if response > 1 second
}

def apply_performance_settings(settings_dict):
    """
    Apply all performance optimizations to Django settings
    """
    settings_dict.update(PERFORMANCE_SETTINGS)
    
    # Apply production optimizations if not in debug mode
    if not settings_dict.get('DEBUG', False):
        settings_dict.update(PRODUCTION_OPTIMIZATIONS)
    else:
        settings_dict.update(DEVELOPMENT_OPTIMIZATIONS)
    
    return settings_dict

# Usage example:
"""
# In your settings.py:
from performance_settings import apply_performance_settings

# Apply all performance optimizations
globals().update(apply_performance_settings(globals()))

# Or apply selectively:
CACHES = PERFORMANCE_SETTINGS['CACHES']
MIDDLEWARE = PERFORMANCE_SETTINGS['OPTIMIZED_MIDDLEWARE']
"""