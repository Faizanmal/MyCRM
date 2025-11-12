"""
Integration Hub Signals
Connect to Django signals to trigger webhooks
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from lead_management.models import Lead
from contact_management.models import Contact
from opportunity_management.models import Opportunity
from task_management.models import Task
from campaign_management.models import Campaign
from document_management.models import Document

from .tasks import trigger_webhook


@receiver(post_save, sender=Lead)
def lead_saved(sender, instance, created, **kwargs):
    """Trigger webhook when lead is created or updated"""
    event = 'lead.created' if created else 'lead.updated'
    payload = {
        'event': event,
        'lead_id': str(instance.id),
        'name': instance.name,
        'email': instance.email,
        'status': instance.status,
    }
    trigger_webhook.delay(event, payload)


@receiver(post_delete, sender=Lead)
def lead_deleted(sender, instance, **kwargs):
    """Trigger webhook when lead is deleted"""
    payload = {
        'event': 'lead.deleted',
        'lead_id': str(instance.id),
        'name': instance.name,
    }
    trigger_webhook.delay('lead.deleted', payload)


@receiver(post_save, sender=Contact)
def contact_saved(sender, instance, created, **kwargs):
    """Trigger webhook when contact is created or updated"""
    event = 'contact.created' if created else 'contact.updated'
    payload = {
        'event': event,
        'contact_id': str(instance.id),
        'first_name': instance.first_name,
        'last_name': instance.last_name,
        'email': instance.email,
    }
    trigger_webhook.delay(event, payload)


@receiver(post_save, sender=Opportunity)
def opportunity_saved(sender, instance, created, **kwargs):
    """Trigger webhook when opportunity is created or updated"""
    if created:
        event = 'opportunity.created'
    elif instance.stage == 'closed_won':
        event = 'opportunity.won'
    elif instance.stage == 'closed_lost':
        event = 'opportunity.lost'
    else:
        event = 'opportunity.updated'
    
    payload = {
        'event': event,
        'opportunity_id': str(instance.id),
        'name': instance.name,
        'amount': float(instance.amount),
        'stage': instance.stage,
    }
    trigger_webhook.delay(event, payload)


@receiver(post_save, sender=Task)
def task_saved(sender, instance, created, **kwargs):
    """Trigger webhook when task is created or completed"""
    if created:
        event = 'task.created'
    elif instance.status == 'completed':
        event = 'task.completed'
    else:
        return  # Don't trigger for regular updates
    
    payload = {
        'event': event,
        'task_id': str(instance.id),
        'title': instance.title,
        'status': instance.status,
    }
    trigger_webhook.delay(event, payload)


@receiver(post_save, sender=Campaign)
def campaign_completed(sender, instance, created, **kwargs):
    """Trigger webhook when campaign is completed"""
    if instance.status == 'completed' and not created:
        payload = {
            'event': 'campaign.completed',
            'campaign_id': str(instance.id),
            'name': instance.name,
            'sent_count': instance.sent_count,
            'open_rate': instance.open_rate,
            'click_rate': instance.click_rate,
        }
        trigger_webhook.delay('campaign.completed', payload)


@receiver(post_save, sender=Document)
def document_uploaded(sender, instance, created, **kwargs):
    """Trigger webhook when document is uploaded"""
    if created:
        payload = {
            'event': 'document.uploaded',
            'document_id': str(instance.id),
            'name': instance.name,
            'category': instance.category,
        }
        trigger_webhook.delay('document.uploaded', payload)
