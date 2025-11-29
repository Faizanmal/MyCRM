from django.apps import AppConfig


class ConversationIntelligenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'conversation_intelligence'
    verbose_name = 'Conversation Intelligence'
    
    def ready(self):
        import conversation_intelligence.signals  # noqa
