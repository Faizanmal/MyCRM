from django.apps import AppConfig


class PredictiveLeadRoutingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'predictive_lead_routing'
    verbose_name = 'Predictive Lead Routing'
    
    def ready(self):
        import predictive_lead_routing.signals  # noqa
