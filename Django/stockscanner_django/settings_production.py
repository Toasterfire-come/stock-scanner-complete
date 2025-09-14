"""
Production settings for external API access
"""

import os
from .settings import *

# Security settings for external access
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Allow external hosts
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'YOUR_COMPUTER_IP',  # Replace with your computer's IP
    'YOUR_DOMAIN.com',   # Replace with your WordPress domain
]

# CORS settings for WordPress
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://YOUR_WORDPRESS_DOMAIN.com',  # Replace with your WordPress domain
    'http://YOUR_WORDPRESS_DOMAIN.com',   # Replace with your WordPress domain
]

# For development, you can allow all origins (less secure)
# CORS_ALLOW_ALL_ORIGINS = True

# Rate limiting - use safe throttles that tolerate cache outages
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    # Disable DRF throttling in production since RateLimitMiddleware handles it
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {},
    'DEFAULT_THROTTLE_CACHE': 'default',
}

# Select production cache backend via env: CACHE_BACKEND=locmem|db|file
cache_backend = os.environ.get("CACHE_BACKEND", "locmem").lower()

if cache_backend == "locmem":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": os.environ.get("CACHE_LOCATION", "stock-scanner-cache"),
            "TIMEOUT": int(os.environ.get("CACHE_TIMEOUT", "300")),
        }
    }
elif cache_backend == "db":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": os.environ.get("CACHE_TABLE", "django_cache"),
            "TIMEOUT": int(os.environ.get("CACHE_TIMEOUT", "300")),
        }
    }
elif cache_backend == "file":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
            "LOCATION": os.environ.get("CACHE_DIR", "/tmp/django_cache"),
            "TIMEOUT": int(os.environ.get("CACHE_TIMEOUT", "300")),
        }
    }
else:
    # Default fallback to LocMem
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": os.environ.get("CACHE_LOCATION", "stock-scanner-cache"),
            "TIMEOUT": int(os.environ.get("CACHE_TIMEOUT", "300")),
        }
    }

# Optional: detect unexpected overrides at startup
print("Effective cache backend:", CACHES['default']['BACKEND'])

# Logging for debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'django_api.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
}

# Security hardening
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS = 'DENY'