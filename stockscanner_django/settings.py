import os
import platform
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

# Cross-platform XAMPP Auto-Detection and Configuration
if platform.system() == 'Windows':
    XAMPP_PATH = r"C:\xampp"
elif platform.system() == 'Darwin':  # macOS
    XAMPP_PATH = "/Applications/XAMPP"
else:  # Linux
    XAMPP_PATH = "/opt/lampp"

XAMPP_MYSQL_PATH = os.path.join(XAMPP_PATH, "mysql", "bin")
IS_XAMPP_AVAILABLE = os.path.exists(XAMPP_PATH) and os.path.exists(XAMPP_MYSQL_PATH)

if IS_XAMPP_AVAILABLE:
    print("INFO: XAMPP detected - configuring for XAMPP MySQL")
    # Add XAMPP MySQL to PATH
    if XAMPP_MYSQL_PATH not in os.environ.get('PATH', ''):
        os.environ['PATH'] = os.environ.get('PATH', '') + os.pathsep + XAMPP_MYSQL_PATH

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-development-key')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver').split(',')
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

# ===== MIDDLEWARE CONFIGURATION =====
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Custom Stock Scanner middleware
    'stocks.middleware.UserTierRateLimitMiddleware',
    'stocks.middleware.FrontendOptimizationMiddleware',
    'stocks.middleware.UserSettingsAutoSetupMiddleware',
    'stocks.middleware.APIResponseOptimizationMiddleware',
    'stocks.middleware.SecurityHeadersMiddleware',
    'stocks.middleware.PerformanceMonitoringMiddleware',
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

# ===== REST FRAMEWORK CONFIGURATION =====
REST_FRAMEWORK = {
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
    },
    'DEFAULT_RENDERER_CLASSES': [
        'stocks.compression_optimization.CompressedJSONRenderer',
        'rest_framework.renderers.JSONRenderer',
    ],
    'EXCEPTION_HANDLER': 'stocks.enhanced_error_handling.custom_exception_handler',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# ===== ENHANCED CACHING CONFIGURATION =====
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
        } if 'REDIS_URL' in os.environ else {
            'MAX_ENTRIES': 1000,
        },
        'KEY_PREFIX': 'stock_scanner',
        'TIMEOUT': 300,  # 5 minutes default
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

# ===== ENHANCED LOGGING CONFIGURATION =====
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
        'stocks': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'stocks.performance': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Create logs directory if it doesn't exist
import os
os.makedirs('logs', exist_ok=True)

# ===== PERFORMANCE MONITORING CONFIGURATION =====
PERFORMANCE_MONITORING = {
    'ENABLE_QUERY_MONITORING': True,
    'SLOW_QUERY_THRESHOLD': 0.1,  # 100ms
    'ENABLE_CACHE_MONITORING': True,
    'ENABLE_REQUEST_MONITORING': True,
    'LOG_SLOW_REQUESTS': True,
    'SLOW_REQUEST_THRESHOLD': 2.0,  # 2 seconds
}

# ===== OPTIMIZATION SYSTEM CONFIGURATION =====
OPTIMIZATION_SETTINGS = {
    'DATABASE_RESILIENCE': {
        'ENABLED': True,
        'MAX_RETRIES': 3,
        'CIRCUIT_BREAKER_THRESHOLD': 5,
        'CIRCUIT_BREAKER_TIMEOUT': 300,  # 5 minutes
    },
    'MEMORY_OPTIMIZATION': {
        'ENABLED': True,
        'MEMORY_THRESHOLD': 500 * 1024 * 1024,  # 500MB
        'CLEANUP_INTERVAL': 600,  # 10 minutes
        'ENABLE_PROFILING': DEBUG,
    },
    'ERROR_HANDLING': {
        'ENABLED': True,
        'ENABLE_CIRCUIT_BREAKER': True,
        'ENABLE_AUTO_RECOVERY': True,
        'ERROR_TRACKING': True,
    },
    'COMPRESSION': {
        'ENABLED': True,
        'MIN_COMPRESSION_SIZE': 500,  # bytes
        'COMPRESSION_RATIO_THRESHOLD': 0.1,  # 10%
        'ENABLE_CONDITIONAL_REQUESTS': True,
    },
    'GRACEFUL_SHUTDOWN': {
        'ENABLED': True,
        'SHUTDOWN_TIMEOUT': 30,  # seconds
        'THREAD_WAIT_TIMEOUT': 15,  # seconds
    },
}

# ===== HEALTH CHECK ENDPOINTS =====
HEALTH_CHECK_ENDPOINTS = {
    'simple': '/health/',
    'detailed': '/health/detailed/',
    'metrics': '/health/metrics/',
    'performance': '/health/performance/',
}

# ===== PRODUCTION SECURITY HEADERS =====
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ===== SESSION CONFIGURATION =====
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ===== CSRF PROTECTION =====
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    'https://*.yourdomain.com',  # Replace with your actual domain
    'https://yourdomain.com',
] if not DEBUG else []

# ===== ADDITIONAL SECURITY SETTINGS =====
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'

# ===== PAYPAL CONFIGURATION =====
PAYPAL_BASE_URL = os.environ.get('PAYPAL_BASE_URL', 'https://api.sandbox.paypal.com')  # Use sandbox for development
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', '')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET', '')
PAYPAL_WEBHOOK_ID = os.environ.get('PAYPAL_WEBHOOK_ID', '')

# ===== AUTO-SETUP CONFIGURATION =====
# Automatically create user profiles and settings
AUTO_CREATE_USER_PROFILES = True
AUTO_OPTIMIZE_FRONTEND = True
AUTO_APPLY_RATE_LIMITS = True

# ===== FRONTEND OPTIMIZATION DEFAULTS =====
FRONTEND_OPTIMIZATION_DEFAULTS = {
    'enabled': True,
    'virtual_scrolling': True,
    'fuzzy_search': True,
    'progressive_loading': True,
    'client_side_charts': True,
    'cache_size_mb': 50,
    'items_per_page': 50
}