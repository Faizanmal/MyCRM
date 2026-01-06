from django.apps import AppConfig


class DocumentEsignConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'document_esign'
    verbose_name = 'Document E-Signatures'

    def ready(self):
        import document_esign.signals  # noqa
