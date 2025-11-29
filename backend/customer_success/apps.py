from django.apps import AppConfig


class CustomerSuccessConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customer_success'
    verbose_name = 'Customer Success Hub'
    
    def ready(self):
        import customer_success.signals  # noqa
