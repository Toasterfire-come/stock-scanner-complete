import os
from .settings import *  # noqa

# Production cache: Database-backed cache table (default: django_cache)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": os.environ.get("CACHE_TABLE", "django_cache"),
        "TIMEOUT": 300,
        "OPTIONS": {},
    }
}

# If you use a separate cache alias anywhere (e.g., for DRF throttling),
# make sure it resolves to the same DB cache:
# CACHES["throttle"] = CACHES["default"]

# If you configured DRF to use a non-default cache alias, make sure it exists:
# REST_FRAMEWORK = {
#     ...
#     # "DEFAULT_THROTTLE_CACHE": "throttle",
# }

