"""
Social Inbox Signals
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import SocialMessage


@receiver(post_save, sender=SocialMessage)
def update_conversation_on_message(sender, instance, created, **kwargs):
    """Update conversation metrics when a new message is added"""
    if created:
        conversation = instance.conversation
        conversation.message_count = conversation.messages.count()

        if instance.direction == 'inbound':
            conversation.unread_count += 1
            conversation.last_message_at = instance.platform_created_at

            # Auto-analyze sentiment for new inbound messages
            from .services import SentimentAnalyzer
            analyzer = SentimentAnalyzer()
            result = analyzer.analyze(instance.content)

            # Update conversation sentiment
            conversation.sentiment_score = result['score']
            conversation.sentiment_label = result['label']

        conversation.save()
