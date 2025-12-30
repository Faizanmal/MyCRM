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
        try:
            from . import signals  # noqa: F401
        except ImportError:
            pass
        
        # Import notification signal handlers
        try:
            from . import notification_signals  # noqa: F401
        except ImportError:
            pass
