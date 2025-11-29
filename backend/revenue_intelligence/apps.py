from django.apps import AppConfig


class RevenueIntelligenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'revenue_intelligence'
    verbose_name = 'Revenue Intelligence'

    def ready(self):
        import revenue_intelligence.signals  # noqa
