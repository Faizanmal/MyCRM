from django.apps import AppConfig


class LeadQualificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lead_qualification'
    verbose_name = 'Lead Qualification & Scoring'
    
    def ready(self):
        import lead_qualification.signals  # noqa: F401
