"""
CI/test settings (SQLite + real auth enforced).

This is intended for automated test runs in CI where MySQL isn't available.
"""

import os

# Ensure base settings evaluate DEBUG correctly during import
os.environ.setdefault("DJANGO_DEBUG", "True")

from .settings import *  # noqa

DEBUG = True
TESTING_DISABLE_AUTH = False

ALLOWED_HOSTS = ["*"]

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

# Never redirect during tests
SECURE_SSL_REDIRECT = False

# Use SQLite for CI tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR / "db_ci.sqlite3"),
    }
}

# Avoid rate limiting + API key middleware noise in tests
MIDDLEWARE = [
    m for m in MIDDLEWARE
    if m not in (
        "stocks.rate_limit_middleware.APIKeyAuthenticationMiddleware",
        "stocks.rate_limit_middleware.RateLimitMiddleware",
    )
]

