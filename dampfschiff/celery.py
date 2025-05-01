# celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dampfschiff.settings')


app = Celery('dampfschiff')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks from installed apps
app.autodiscover_tasks()

# Optional Celery beat configuration for scheduled tasks
app.conf.beat_schedule = {
    'daily-route-optimization': {
        'task': 'bookings.tasks.optimize_routes',
        'schedule': 86400,  # every 24 hours
    },
}
