"""
Production settings for external API access
"""

import os
from .settings import *

# Security settings for external access
DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') or os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY (or SECRET_KEY) must be set in production.")

# Inherit ALLOWED_HOSTS and CORS from base settings.py which reads environment variables
# Do not override here; ensure DJANGO_ALLOWED_HOSTS and CSRF/CORS envs are set in .env

# CORS is configured in base settings using env vars

# Rate limiting - use safe throttles that tolerate cache outages
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        # Security: require auth by default in production.
        # Public endpoints must explicitly opt into AllowAny at the view level.
        'rest_framework.permissions.IsAuthenticated',
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

# Celery Configuration (using database broker instead of Redis)
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'db+sqlite:///celery.db')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'db+sqlite:///celery_results.db')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

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