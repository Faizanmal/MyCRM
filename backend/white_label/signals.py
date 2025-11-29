"""
White Label and Billing Signals
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver(post_save, sender='white_label.OrganizationMember')
def update_user_count_on_add(sender, instance, created, **kwargs):
    """Update user count when member added"""
    if created:
        org = instance.organization
        org.current_users = org.members.count()
        org.save(update_fields=['current_users'])


@receiver(post_delete, sender='white_label.OrganizationMember')
def update_user_count_on_remove(sender, instance, **kwargs):
    """Update user count when member removed"""
    try:
        org = instance.organization
        org.current_users = org.members.count()
        org.save(update_fields=['current_users'])
    except Exception:
        pass


@receiver(post_save, sender='white_label.Organization')
def handle_subscription_changes(sender, instance, **kwargs):
    """Handle subscription status changes"""
    if instance.subscription_status == 'expired':
        # Could disable certain features, send notification, etc.
        pass
