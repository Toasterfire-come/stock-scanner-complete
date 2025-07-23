# projectname/celery.py
import os
import sys
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")

app = Celery("stockscanner_django")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(['emails', 'news', 'stocks',])

# Only set database scheduler if not running migrations
# This prevents database access during Django startup before migrations
if 'migrate' not in sys.argv and 'makemigrations' not in sys.argv:
    try:
        # Try to set database scheduler, but don't fail if tables don't exist
        app.conf.beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'
    except Exception:
        # Fall back to default scheduler if database tables don't exist
        pass

