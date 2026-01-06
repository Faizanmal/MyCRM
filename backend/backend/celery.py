"""
Celery Configuration for MyCRM
Background task processing setup
"""
import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('mycrm')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'retrain-lead-scoring-model': {
        'task': 'core.tasks.retrain_lead_scoring_model',
        'schedule': crontab(hour=2, minute=0, day_of_week=1),  # Every Monday at 2 AM
    },
    'send-daily-digest': {
        'task': 'activity_feed.tasks.send_daily_digest',
        'schedule': crontab(hour=8, minute=0),  # Every day at 8 AM
    },
    'check-overdue-tasks': {
        'task': 'task_management.tasks.check_overdue_tasks',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
