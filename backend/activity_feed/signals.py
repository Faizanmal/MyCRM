"""
Activity Feed Signals
Automatically create activity records for CRM actions
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Activity


@receiver(post_save, sender='lead_management.Lead')
def lead_activity(sender, instance, created, **kwargs):
    """Create activity for lead actions"""
    if created:
        Activity.objects.create(
            actor=instance.assigned_to if hasattr(instance, 'assigned_to') and instance.assigned_to else instance.created_by,
            action='created',
            content_type=ContentType.objects.get_for_model(sender),
            object_id=str(instance.id),
            description=f"Created lead: {instance.name}"
        )
    else:
        # Check if status changed
        if hasattr(instance, '_state') and not instance._state.adding:
            Activity.objects.create(
                actor=instance.assigned_to if hasattr(instance, 'assigned_to') and instance.assigned_to else instance.created_by,
                action='updated',
                content_type=ContentType.objects.get_for_model(sender),
                object_id=str(instance.id),
                description=f"Updated lead: {instance.name}"
            )


@receiver(post_save, sender='contact_management.Contact')
def contact_activity(sender, instance, created, **kwargs):
    """Create activity for contact actions"""
    if created:
        Activity.objects.create(
            actor=instance.created_by if hasattr(instance, 'created_by') and instance.created_by else instance.owner,
            action='created',
            content_type=ContentType.objects.get_for_model(sender),
            object_id=str(instance.id),
            description=f"Created contact: {instance.first_name} {instance.last_name}"
        )


@receiver(post_save, sender='opportunity_management.Opportunity')
def opportunity_activity(sender, instance, created, **kwargs):
    """Create activity for opportunity actions"""
    if created:
        Activity.objects.create(
            actor=instance.owner if hasattr(instance, 'owner') and instance.owner else instance.created_by,
            action='created',
            content_type=ContentType.objects.get_for_model(sender),
            object_id=str(instance.id),
            description=f"Created opportunity: {instance.name}"
        )
    else:
        # Check if status changed
        if hasattr(instance, 'stage'):
            Activity.objects.create(
                actor=instance.owner if hasattr(instance, 'owner') and instance.owner else instance.created_by,
                action='status_changed',
                content_type=ContentType.objects.get_for_model(sender),
                object_id=str(instance.id),
                description=f"Moved opportunity to {instance.stage}: {instance.name}"
            )


@receiver(post_save, sender='task_management.Task')
def task_activity(sender, instance, created, **kwargs):
    """Create activity for task actions"""
    if created:
        Activity.objects.create(
            actor=instance.created_by if hasattr(instance, 'created_by') and instance.created_by else instance.assigned_to,
            action='created',
            content_type=ContentType.objects.get_for_model(sender),
            object_id=str(instance.id),
            description=f"Created task: {instance.title}"
        )
    elif hasattr(instance, 'status') and instance.status == 'completed':
        Activity.objects.create(
            actor=instance.assigned_to if hasattr(instance, 'assigned_to') and instance.assigned_to else instance.created_by,
            action='completed',
            content_type=ContentType.objects.get_for_model(sender),
            object_id=str(instance.id),
            description=f"Completed task: {instance.title}"
        )


@receiver(post_save, sender='document_management.Document')
def document_activity(sender, instance, created, **kwargs):
    """Create activity for document upload"""
    if created:
        Activity.objects.create(
            actor=instance.uploaded_by,
            action='uploaded',
            content_type=ContentType.objects.get_for_model(sender),
            object_id=str(instance.id),
            description=f"Uploaded document: {instance.name}"
        )


@receiver(post_save, sender='campaign_management.Campaign')
def campaign_activity(sender, instance, created, **kwargs):
    """Create activity for campaign actions"""
    if instance.status == 'completed':
        Activity.objects.create(
            actor=instance.created_by,
            action='completed',
            content_type=ContentType.objects.get_for_model(sender),
            object_id=str(instance.id),
            description=f"Completed campaign: {instance.name}"
        )
