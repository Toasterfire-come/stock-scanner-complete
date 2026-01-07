import os
from pathlib import Path
from corsheaders.defaults import default_headers

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

# XAMPP Auto-Detection and Configuration (disabled by default unless USE_XAMPP=true)
USE_XAMPP = os.environ.get('USE_XAMPP', 'false').lower() == 'true'
XAMPP_PATH = r"C:\xampp"
XAMPP_MYSQL_PATH = os.path.join(XAMPP_PATH, "mysql", "bin")
IS_XAMPP_AVAILABLE = os.path.exists(XAMPP_PATH) and os.path.exists(XAMPP_MYSQL_PATH)

if USE_XAMPP and IS_XAMPP_AVAILABLE:
    print("INFO: XAMPP detected - configuring for XAMPP MySQL")
    # Add XAMPP MySQL to PATH
    if XAMPP_MYSQL_PATH not in os.environ.get('PATH', ''):
        os.environ['PATH'] = os.environ.get('PATH', '') + os.pathsep + XAMPP_MYSQL_PATH

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') or os.environ.get('SECRET_KEY') or 'django-insecure-development-key'
_debug_raw = os.environ.get('DEBUG', os.environ.get('DJANGO_DEBUG', 'True'))
DEBUG = str(_debug_raw).lower() == 'true'
print(f"DEBUG MODE: {DEBUG} (raw value: {_debug_raw})")

# Fail closed if someone tries to run non-debug without a real secret key.
if not DEBUG and (not SECRET_KEY or SECRET_KEY.startswith("django-insecure-") or SECRET_KEY == "django-insecure-development-key"):
    raise RuntimeError("DJANGO_SECRET_KEY (or SECRET_KEY) must be set when DEBUG is false.")

# Disable SSL redirect in DEBUG mode for local development
if DEBUG:
    SECURE_SSL_REDIRECT = False

# Allow configuration of ALLOWED_HOSTS via environment variables
# Prefer DJANGO_ALLOWED_HOSTS (comma-separated), fallback to ALLOWED_HOSTS, then defaults
_allowed_hosts_env = os.environ.get('DJANGO_ALLOWED_HOSTS') or os.environ.get('ALLOWED_HOSTS')
if _allowed_hosts_env:
    ALLOWED_HOSTS = [host.strip() for host in _allowed_hosts_env.split(',') if host.strip()]
    for fallback_host in (
        "api.retailtradescanner.com",
        "retailtradescanner.com",
        "www.retailtradescanner.com",
        "tradescanpro.com",
        "www.tradescanpro.com",
    ):
        if fallback_host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(fallback_host)
else:
    ALLOWED_HOSTS = [
        "127.0.0.1",
        "localhost",
        os.environ.get('PRIMARY_DOMAIN', 'api.retailtradescanner.com'),
        "api.retailtradescanner.com",
        "retailtradescanner.com",
        "www.retailtradescanner.com",
        "tradescanpro.com",
        "www.tradescanpro.com",
    ]
# API key for WordPress/backend-to-backend auth
WORDPRESS_API_KEY = os.environ.get('WORDPRESS_API_KEY', '')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',
    'rest_framework',
    'corsheaders',
    'django_extensions',
    'stocks',
    'billing',
    'emails',
    'core',
    'news',
    'education',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Third-party CORS as high as possible
    'stocks.middleware_security.SecurityHeadersMiddleware',  # Add safe security headers
    'stocks.middleware_error.CircuitBreakerMiddleware',  # Circuit breaker for stability
    'stocks.middleware_error.EnhancedErrorHandlingMiddleware',  # Enhanced error handling
    'stocks.middleware.APICompatibilityMiddleware',  # API/HTML detection (sets request.is_api_request)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Ensure request.user exists before rate limiting
    'stocks.plan_middleware.PlanLimitMiddleware',  # Plan limits and API call tracking
    'stocks.plan_middleware.PlanFeatureMiddleware',  # Feature access control
    'stocks.rate_limit_middleware.APIKeyAuthenticationMiddleware',  # API key auth for backend services
    'stocks.rate_limit_middleware.RateLimitMiddleware',  # Rate limiting with free endpoint whitelist
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'stockscanner_django.urls'

# Minimal template configuration - only for Django admin
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # No custom templates - API-only backend
        'APP_DIRS': True,  # Allow Django admin templates
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


# Optional Sentry error reporting (enabled when SENTRY_DSN is set)
try:
    _sentry_dsn = os.environ.get('SENTRY_DSN') or os.environ.get('DJANGO_SENTRY_DSN')
    if _sentry_dsn:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        sentry_sdk.init(
            dsn=_sentry_dsn,
            integrations=[DjangoIntegration()],
            traces_sample_rate=float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0')),
            send_default_pii=False,
            environment=os.environ.get('ENVIRONMENT', 'production' if not DEBUG else 'development'),
            release=os.environ.get('RELEASE')
        )
except Exception:
    # Sentry is optional; never block startup
    pass

"""
Single-database configuration for local MySQL (root, no password).
To use: ensure MySQL is running locally and database 'stockscanner' exists.
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'stockscanner'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'CONN_MAX_AGE': 0,
        'ATOMIC_REQUESTS': True,
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'autocommit': True,
        },
    }
}

# No database routers in single-DB mode

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
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cross-site cookies for embedded clients (dev-friendly)
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = 'Lax' if DEBUG else 'None'
CSRF_COOKIE_SAMESITE = 'Lax' if DEBUG else 'None'
SESSION_COOKIE_AGE = int(os.environ.get('SESSION_COOKIE_AGE', str(6 * 60 * 60)))

# PayPal configuration (env-driven)
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', '')
PAYPAL_SECRET = os.environ.get('PAYPAL_SECRET', '')
PAYPAL_WEBHOOK_URL = os.environ.get('PAYPAL_WEBHOOK_URL', '')
PAYPAL_WEBHOOK_ID = os.environ.get('PAYPAL_WEBHOOK_ID', '')

# Optional Google reCAPTCHA (enterprise-friendly: set per environment)
RECAPTCHA_SECRET = os.environ.get('RECAPTCHA_SECRET', '')

# CORS settings
# Always use explicit allow-list to avoid wildcard (*) with credentials
CORS_ALLOW_ALL_ORIGINS = False
_extra_cors = [o.strip() for o in os.environ.get('EXTRA_CORS_ORIGINS', '').split(',') if o.strip()]
if DEBUG:
    CORS_ALLOWED_ORIGINS = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:8000',
        'http://127.0.0.1:8000',
    ] + _extra_cors
else:
    CORS_ALLOWED_ORIGINS = list(filter(None, [
        os.environ.get('FRONTEND_URL'),
        os.environ.get('WORDPRESS_URL'),
        'https://tradescanpro.com',
        'https://www.tradescanpro.com',
        'https://retailtradescanner.com',
        'https://www.retailtradescanner.com',
        # Deployed static hosting domain(s)
        'https://access-5018544625.webspace-host.com',
    ] + _extra_cors))
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = list({
    'GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'
})
CORS_ALLOW_HEADERS = list(default_headers) + [
    'x-csrftoken',
    'X-CSRFToken',
    'X-Requested-With',
    'authorization',
    'Authorization',
    'x-api-key',
    'X-API-Key',
]

# Enterprise/Premium overrides
# Comma-separated list via ENTERPRISE_EMAILS, plus hardcoded important recipients
ENTERPRISE_EMAIL_WHITELIST = list(filter(None, [
    *(email.strip() for email in os.environ.get('ENTERPRISE_EMAILS', '').split(',') if email.strip()),
    'Carter.kiefer2010@outlook.com',
    'carter.kiefer2010@outlook.com',  # ensure case-insensitive match
]))

# Forced plan mapping by email (takes precedence over enterprise whitelist)
# Format: { 'email@example.com': 'gold' }
FORCED_PLAN_BY_EMAIL = {
    **{k.strip().lower(): v.strip().lower() for k, v in (
        # Load from env FORCED_PLAN_EMAILS as pairs email:plan separated by commas
        # Example: FORCED_PLAN_EMAILS="carter.kiefer2010@outlook.com:gold, vip@example.com:enterprise"
        [tuple(item.split(':', 1)) for item in os.environ.get('FORCED_PLAN_EMAILS', '').split(',') if ':' in item]
    )},
    'carter.kiefer2010@outlook.com': 'gold',
    'hamzashehata3000@gmail.com': 'gold',
}

# Partner code mapping for analytics gating
PARTNER_CODE_BY_EMAIL = {
    **{k.strip().lower(): v.strip().upper() for k, v in (
        [tuple(item.split(':', 1)) for item in os.environ.get('PARTNER_CODE_EMAILS', '').split(',') if ':' in item]
    )},
    'hamzashehata3000@gmail.com': 'ADAM50',
}

# Define which endpoints constitute stock market data for counting/limits
STOCK_DATA_ENDPOINT_PREFIXES = [
    '/api/stocks/',
    '/api/stock/',
    '/api/search/',
    '/api/trending/',
    '/api/realtime/',
    '/api/filter/',
    '/api/market-stats/',
]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Security: Require auth
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'stocks.authentication.BearerSessionAuthentication',  # Bearer token auth
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'MAX_PAGE_SIZE': 100,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'burst': '60/minute',
    }
}

# API Configuration
API_CONFIG = {
    'MAX_PAGE_SIZE': 100,
    'MARKET_CAP_LARGE': 10_000_000_000,  # $10B
    'MARKET_CAP_SMALL': 2_000_000_000,    # $2B
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'stock-scanner-cache',
    }
}

# Sessions in DB (avoid Redis)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Celery Configuration (using database broker instead of Redis)
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'db+sqlite:///celery.db')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'db+sqlite:///celery_results.db')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Email
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')

# Stock API Configuration
YFINANCE_RATE_LIMIT = float(os.environ.get('YFINANCE_RATE_LIMIT', '0.5'))  # 0.5 second delay
YFINANCE_TIMEOUT = int(os.environ.get('YFINANCE_TIMEOUT', '15'))  # 15 seconds timeout
YFINANCE_RETRIES = int(os.environ.get('YFINANCE_RETRIES', '3'))  # 3 retries

# Backup API keys (optional)
FINNHUB_KEYS = [
    key.strip() for key in os.environ.get('FINNHUB_API_KEYS', '').split(',') 
    if key.strip()
]

# Scanner run-window feature flags (pre/post disabled by default)
SCAN_PREMARKET = os.environ.get('SCAN_PREMARKET', 'false').lower() == 'true'
SCAN_POSTMARKET = os.environ.get('SCAN_POSTMARKET', 'false').lower() == 'true'


# Security Settings - HTTPS Enforcement (disabled in DEBUG mode)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Debug: Print final SECURE_SSL_REDIRECT value
print(f"SECURE_SSL_REDIRECT = {globals().get('SECURE_SSL_REDIRECT', 'NOT SET')}")

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'fmt': '%(asctime)s %(levelname)s %(name)s %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json' if (os.environ.get('LOG_FORMAT', '').lower() == 'json' or os.environ.get('JSON_LOGS', 'false').lower() == 'true') else 'default',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.environ.get('LOG_LEVEL', 'INFO'),
    },
}
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Allow configuration of CSRF_TRUSTED_ORIGINS via environment variable (comma-separated)
_csrf_trusted = os.environ.get('CSRF_TRUSTED_ORIGINS')
if _csrf_trusted:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in _csrf_trusted.split(',') if origin.strip()]
else:
    CSRF_TRUSTED_ORIGINS = list(filter(None, [
        os.environ.get('PRIMARY_ORIGIN', 'https://tradescanpro.com'),
        'https://tradescanpro.com',
        'https://www.tradescanpro.com',
        'https://api.retailtradescanner.com',
        'https://retailtradescanner.com',
        'https://www.retailtradescanner.com',
        # Deployed static hosting domain(s)
        'https://access-5018544625.webspace-host.com',
    ] + [o.strip() for o in os.environ.get('EXTRA_CSRF_ORIGINS', '').split(',') if o.strip()]))
KILL_SWITCH_ENABLED = os.environ.get('KILL_SWITCH_ENABLED', 'false').lower() == 'true'
KILL_SWITCH_PASSWORD = os.environ.get('KILL_SWITCH_PASSWORD', '')
KILL_SWITCH_DELAY_SECONDS = int(os.environ.get('KILL_SWITCH_DELAY_SECONDS', '5'))

# Rate Limiting Configuration
RATE_LIMIT_FREE_USERS = int(os.environ.get('RATE_LIMIT_FREE_USERS', os.environ.get('FREE_MONTHLY_API_LIMIT', '30')))  # requests per hour for free users (env-driven)
RATE_LIMIT_AUTHENTICATED_USERS = int(os.environ.get('RATE_LIMIT_AUTHENTICATED_USERS', '1000'))  # requests per hour for authenticated users
RATE_LIMIT_WINDOW = int(os.environ.get('RATE_LIMIT_WINDOW', '3600'))  # Window in seconds (default: 1 hour)
PREMIUM_USER_GROUPS = ['premium', 'pro', 'enterprise']  # User groups that have no rate limiting
