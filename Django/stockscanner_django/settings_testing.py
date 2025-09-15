from .settings import *  # noqa

# Testing overrides: disable security/auth/CSRF for local endpoint validation
DEBUG = True

ALLOWED_HOSTS = ["*"]

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

# Disable DRF authentication/permissions for testing
REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = [
    'rest_framework.permissions.AllowAny',
]
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = []

# Remove rate limiting and API key middlewares for testing
MIDDLEWARE = [
    m for m in MIDDLEWARE
    if m not in (
        'stocks.rate_limit_middleware.APIKeyAuthenticationMiddleware',
        'stocks.rate_limit_middleware.RateLimitMiddleware',
    )
]
# Inject test user middleware to simulate authenticated requests locally
MIDDLEWARE.insert(0, 'stocks.testing_middleware.TestUserMiddleware')

# Force CORS allow all for local testing
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = []
CORS_ALLOW_CREDENTIALS = True

# Use SQLite for local testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(BASE_DIR / 'db_test.sqlite3'),
    }
}

