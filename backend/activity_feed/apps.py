from django.apps import AppConfig


class ActivityFeedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'activity_feed'
    verbose_name = 'Activity Feed'
    
    def ready(self):
        import activity_feed.signals
