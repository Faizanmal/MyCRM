"""
Celery Configuration for MyCRM
"""

import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('mycrm')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Configuration
app.conf.update(
    # Broker settings
    broker_url=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    result_backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),

    # Serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',

    # Timezone
    timezone='UTC',
    enable_utc=True,

    # Task settings
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes

    # Result settings
    result_expires=3600,  # 1 hour

    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,

    # Rate limiting
    task_default_rate_limit='100/m',

    # Error handling
    task_reject_on_worker_lost=True,
    task_acks_late=True,
)

# Celery Beat Schedule
app.conf.beat_schedule = {
    # Digest emails
    'send-daily-digests': {
        'task': 'core.celery_tasks.send_daily_digests',
        'schedule': crontab(hour=9, minute=0),  # 9:00 AM daily
        'options': {'queue': 'notifications'},
    },
    'send-weekly-digests': {
        'task': 'core.celery_tasks.send_weekly_digests',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),  # Monday 9:00 AM
        'options': {'queue': 'notifications'},
    },

    # Task reminders
    'check-overdue-tasks': {
        'task': 'core.celery_tasks.check_overdue_tasks',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {'queue': 'notifications'},
    },
    'check-due-soon-tasks': {
        'task': 'core.celery_tasks.check_due_soon_tasks',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {'queue': 'notifications'},
    },

    # Deal follow-ups
    'check-stale-deals': {
        'task': 'core.celery_tasks.check_stale_deals',
        'schedule': crontab(hour=10, minute=0),  # 10:00 AM daily
        'options': {'queue': 'notifications'},
    },

    # Cleanup tasks
    'cleanup-old-notifications': {
        'task': 'core.celery_tasks.cleanup_old_notifications',
        'schedule': crontab(hour=2, minute=0),  # 2:00 AM daily
        'options': {'queue': 'maintenance'},
    },
    'cleanup-expired-exports': {
        'task': 'core.celery_tasks.cleanup_expired_exports',
        'schedule': crontab(hour=3, minute=0),  # 3:00 AM daily
        'options': {'queue': 'maintenance'},
    },
    'cleanup-old-audit-logs': {
        'task': 'core.celery_tasks.cleanup_old_audit_logs',
        'schedule': crontab(hour=4, minute=0, day_of_week=0),  # Sunday 4:00 AM
        'options': {'queue': 'maintenance'},
    },

    # Analytics
    'calculate-daily-metrics': {
        'task': 'core.celery_tasks.calculate_daily_metrics',
        'schedule': crontab(hour=0, minute=5),  # 00:05 daily
        'options': {'queue': 'analytics'},
    },
    'generate-ai-recommendations': {
        'task': 'core.celery_tasks.generate_ai_recommendations',
        'schedule': crontab(hour=6, minute=0),  # 6:00 AM daily
        'options': {'queue': 'ai'},
    },

    # Analytics snapshots
    'generate-analytics-snapshot': {
        'task': 'core.export_tasks.generate_analytics_snapshot',
        'schedule': crontab(hour=1, minute=0),  # 1:00 AM daily
        'options': {'queue': 'analytics'},
    },
}

# Queue routing
app.conf.task_routes = {
    'core.celery_tasks.send_*': {'queue': 'notifications'},
    'core.celery_tasks.check_*': {'queue': 'notifications'},
    'core.celery_tasks.cleanup_*': {'queue': 'maintenance'},
    'core.celery_tasks.calculate_*': {'queue': 'analytics'},
    'core.celery_tasks.generate_*': {'queue': 'ai'},
    'core.export_tasks.*': {'queue': 'exports'},
}


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery configuration"""
    print(f'Request: {self.request!r}')
    return {'status': 'Celery is working!'}
