from django.apps import AppConfig


class InterplanetarySyncConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'interplanetary_sync'
    verbose_name = 'Interplanetary Data Synchronization'
