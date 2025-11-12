"""
Core Django app configuration
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Enterprise Core'

    def ready(self):
        """Initialize the app when Django starts"""
        # Import signal handlers
        from . import signals