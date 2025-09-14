import os
from .settings import *  # noqa

# Select production cache backend via env: CACHE_BACKEND=locmem|db|file
cache_backend = os.environ.get("CACHE_BACKEND", "db").lower()

if cache_backend == "locmem":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": os.environ.get("CACHE_LOCATION", "stock-scanner-cache"),
            "TIMEOUT": int(os.environ.get("CACHE_TIMEOUT", "300")),
        }
    }
elif cache_backend == "file":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
            "LOCATION": os.environ.get("CACHE_DIR", "/var/www/cache/stockscanner"),
            "TIMEOUT": int(os.environ.get("CACHE_TIMEOUT", "300")),
        }
    }
else:
    # Default to DatabaseCache
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": os.environ.get("CACHE_TABLE", "django_cache"),
            "TIMEOUT": int(os.environ.get("CACHE_TIMEOUT", "300")),
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

