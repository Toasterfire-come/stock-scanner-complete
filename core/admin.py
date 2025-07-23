from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'category', 'subscribed_at')
    list_filter = ('category', 'subscribed_at')
    search_fields = ('email', 'category')
    ordering = ('-subscribed_at',)

# Celery Beat task setup - only run when Celery Beat is available
def setup_periodic_tasks():
    """Setup periodic tasks for email sending - only call when Celery Beat is enabled"""
    try:
        from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
        import json
        
        # Crontab: 9:00 AM daily
        schedule, created = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='9',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )
        
        # Uncomment to create periodic task
        # PeriodicTask.objects.create(
        #     crontab=schedule,
        #     name='Send MC 10 IN Emails',
        #     task='emails.tasks.send_mc_10_in_email',
        #     kwargs=json.dumps({}),
        # )
        
        return True
    except ImportError:
        # Celery Beat not available
        return False

# Only setup tasks if django_celery_beat is in INSTALLED_APPS
try:
    from django.conf import settings
    if 'django_celery_beat' in settings.INSTALLED_APPS:
        # Only setup tasks after Django is fully ready
        from django.core.signals import request_finished
        def setup_tasks_signal(sender, **kwargs):
            setup_periodic_tasks()
        # Don't auto-setup for now to avoid issues
        # request_finished.connect(setup_tasks_signal)
except Exception:
    # If there's any issue, just skip the setup
    pass
