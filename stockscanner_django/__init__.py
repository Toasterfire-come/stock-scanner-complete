# projectname/__init__.py
import os

# Only import Celery if explicitly enabled
if os.environ.get('CELERY_ENABLED', 'false').lower() == 'true':
try:
from .celery import app as celery_app
__all__ = ("celery_app",)
except Exception:
# If Celery import fails, continue without it
pass
else:
# Development mode - no Celery
pass
