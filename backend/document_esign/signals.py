"""
Document E-Signature Signals
"""

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='document_esign.Document')
def handle_document_completion(sender, instance, **kwargs):
    """Handle document completion events"""
    if instance.status == 'completed' and instance.opportunity:
        # Could update opportunity stage or create task
        pass


@receiver(post_save, sender='document_esign.DocumentRecipient')
def handle_signature_event(sender, instance, **kwargs):
    """Handle signature events"""
    if instance.signed_at:
        # Update analytics, create activity, etc.
        pass
