# Celery task registration - simplified to avoid startup issues
try:
from . import tasks
except Exception:
# Skip task import if there are any issues
pass
