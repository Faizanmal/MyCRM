from django.apps import AppConfig


class WhiteLabelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'white_label'
    verbose_name = 'White Label & Billing'

    def ready(self):
        import white_label.signals  # noqa
