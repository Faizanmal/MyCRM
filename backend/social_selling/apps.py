from django.apps import AppConfig


class SocialSellingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'social_selling'
    verbose_name = 'Social Selling Tools'

    def ready(self):
        import social_selling.signals  # noqa
