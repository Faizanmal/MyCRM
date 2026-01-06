"""
Data Enrichment Signals
Django signals for automatic enrichment triggers
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender='contact_management.Contact')
def enrich_new_contact(sender, instance, created, **kwargs):
    """Automatically enrich new contacts"""
    if created and instance.email:
        # Check if there's an active rule for new contacts
        from .models import EnrichmentRule
        from .tasks import enrich_contact_async
        rules = EnrichmentRule.objects.filter(
            trigger_type='new_contact',
            is_active=True
        )

        if rules.exists():
            logger.info(f"Triggering enrichment for new contact: {instance.email}")
            enrich_contact_async.delay(str(instance.id), 'contact')


@receiver(post_save, sender='lead_management.Lead')
def enrich_new_lead(sender, instance, created, **kwargs):
    """Automatically enrich new leads"""
    if created and instance.email:
        # Check if there's an active rule for new leads
        from .models import EnrichmentRule
        from .tasks import enrich_contact_async
        rules = EnrichmentRule.objects.filter(
            trigger_type='new_lead',
            is_active=True
        )

        if rules.exists():
            logger.info(f"Triggering enrichment for new lead: {instance.email}")
            enrich_contact_async.delay(str(instance.id), 'lead')


@receiver(post_save, sender='data_enrichment.EnrichmentProfile')
def update_contact_from_enrichment(sender, instance, created, **kwargs):
    """Update linked contact/lead when enrichment profile is updated"""

    if instance.status != 'enriched':
        return

    # Update linked contact
    if instance.contact:
        contact = instance.contact

        if instance.first_name and not contact.first_name:
            contact.first_name = instance.first_name
        if instance.last_name and not contact.last_name:
            contact.last_name = instance.last_name
        if instance.phone and not contact.phone:
            contact.phone = instance.phone
        if instance.title and hasattr(contact, 'title') and not contact.title:
            contact.title = instance.title
        if instance.city and hasattr(contact, 'city') and not contact.city:
            contact.city = instance.city
        if instance.country and hasattr(contact, 'country') and not contact.country:
            contact.country = instance.country

        contact.save()

    # Update linked lead
    if instance.lead:
        lead = instance.lead

        if instance.first_name and not lead.first_name:
            lead.first_name = instance.first_name
        if instance.last_name and not lead.last_name:
            lead.last_name = instance.last_name
        if instance.phone and not lead.phone:
            lead.phone = instance.phone

        lead.save()


@receiver(post_save, sender='data_enrichment.IntentSignal')
def notify_strong_intent(sender, instance, created, **kwargs):
    """Notify sales team of strong intent signals"""

    if created and instance.strength in ['strong', 'very_strong']:
        from .tasks import notify_intent_signal

        logger.info(f"Strong intent signal detected: {instance.topic}")
        notify_intent_signal.delay(str(instance.id))


@receiver(post_save, sender='data_enrichment.NewsAlert')
def process_sales_trigger(sender, instance, created, **kwargs):
    """Process news alerts that are sales triggers"""

    if created and instance.is_sales_trigger:
        from .tasks import process_sales_trigger_alert

        logger.info(f"Sales trigger detected: {instance.title}")
        process_sales_trigger_alert.delay(str(instance.id))
