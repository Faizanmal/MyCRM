from django.apps import AppConfig


class CollaborationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'collaboration'
    verbose_name = 'Advanced Collaboration Tools'
    
    def ready(self):
        import collaboration.signals
