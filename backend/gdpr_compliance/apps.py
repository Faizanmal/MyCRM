from django.apps import AppConfig


class GdprComplianceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gdpr_compliance'
    verbose_name = 'GDPR Compliance'

    def ready(self):
        import gdpr_compliance.signals
