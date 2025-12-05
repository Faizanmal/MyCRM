"""
Voice Intelligence App Configuration
"""

from django.apps import AppConfig


class VoiceIntelligenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'voice_intelligence'
    verbose_name = 'Voice Intelligence & AI Transcription'
    
    def ready(self):
        import voice_intelligence.signals  # noqa
