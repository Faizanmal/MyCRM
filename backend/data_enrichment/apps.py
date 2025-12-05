"""
Data Enrichment App Configuration
"""

from django.apps import AppConfig


class DataEnrichmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data_enrichment'
    verbose_name = 'Data Enrichment & Lead Intelligence'
    
    def ready(self):
        import data_enrichment.signals  # noqa
