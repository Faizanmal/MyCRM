from django.apps import AppConfig


class EmailSequenceAutomationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'email_sequence_automation'
    verbose_name = 'Email Sequence Automation'

    def ready(self):
        import email_sequence_automation.signals  # noqa
