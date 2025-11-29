"""
Social Selling Signals
"""

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='social_selling.SocialEngagement')
def track_engagement_completion(sender, instance, **kwargs):
    """Track when engagements are completed"""
    if instance.status == 'completed' and instance.completed_at:
        # Update profile engagement history
        pass


@receiver(post_save, sender='social_selling.ProspectInSequence')
def handle_sequence_response(sender, instance, **kwargs):
    """Handle when prospect responds"""
    if instance.status == 'responded':
        # Update sequence analytics
        # Potentially create a task for follow-up
        pass
