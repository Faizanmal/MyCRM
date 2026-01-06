"""
Signals for Email Sequence Automation
Handles automated triggers and event tracking
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import SequenceActivity, SequenceEnrollment
from .services import TriggerEvaluationService


@receiver(post_save, sender='lead_management.Lead')
def check_lead_score_triggers(sender, instance, created, **kwargs):
    """Check for lead score-based triggers when lead is updated"""
    if created:
        return

    service = TriggerEvaluationService()
    service.evaluate_triggers('lead_score', {
        'contact_id': getattr(instance, 'contact_id', None),
        'lead_id': instance.id,
        'lead_score': instance.lead_score,
        'old_score': getattr(instance, '_original_score', 0)
    })


@receiver(post_save, sender='contact_management.Contact')
def check_contact_triggers(sender, instance, created, **kwargs):
    """Check for contact-based triggers"""
    if created:
        return

    # Check for tag changes
    old_tags = getattr(instance, '_original_tags', [])
    new_tags = instance.tags or []

    added_tags = [t for t in new_tags if t not in old_tags]
    removed_tags = [t for t in old_tags if t not in new_tags]

    if added_tags or removed_tags:
        service = TriggerEvaluationService()
        service.evaluate_triggers('tag_change', {
            'contact_id': instance.id,
            'added_tags': added_tags,
            'removed_tags': removed_tags
        })


@receiver(pre_save, sender='lead_management.Lead')
def store_original_lead_values(sender, instance, **kwargs):
    """Store original values for comparison"""
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            instance._original_score = original.lead_score
        except sender.DoesNotExist:
            instance._original_score = 0


@receiver(pre_save, sender='contact_management.Contact')
def store_original_contact_values(sender, instance, **kwargs):
    """Store original values for comparison"""
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            instance._original_tags = original.tags or []
        except sender.DoesNotExist:
            instance._original_tags = []


def track_email_open(enrollment_id: str, email_id: str, metadata: dict = None):
    """Track email open event"""
    try:
        enrollment = SequenceEnrollment.objects.get(id=enrollment_id)
        enrollment.emails_opened += 1
        enrollment.save(update_fields=['emails_opened'])

        SequenceActivity.objects.create(
            enrollment=enrollment,
            activity_type='email_opened',
            description='Email opened',
            metadata=metadata or {}
        )
    except SequenceEnrollment.DoesNotExist:
        pass


def track_email_click(enrollment_id: str, email_id: str, url: str, metadata: dict = None):
    """Track email click event"""
    try:
        enrollment = SequenceEnrollment.objects.get(id=enrollment_id)
        enrollment.emails_clicked += 1
        enrollment.save(update_fields=['emails_clicked'])

        SequenceActivity.objects.create(
            enrollment=enrollment,
            activity_type='email_clicked',
            description=f'Clicked: {url}',
            metadata={'url': url, **(metadata or {})}
        )
    except SequenceEnrollment.DoesNotExist:
        pass


def track_email_reply(enrollment_id: str, email_id: str, metadata: dict = None):
    """Track email reply event"""
    try:
        enrollment = SequenceEnrollment.objects.get(id=enrollment_id)
        enrollment.emails_replied += 1
        enrollment.save(update_fields=['emails_replied'])

        SequenceActivity.objects.create(
            enrollment=enrollment,
            activity_type='email_replied',
            description='Email replied',
            metadata=metadata or {}
        )

        # Check if sequence should exit on reply
        if enrollment.sequence.exit_conditions.get('on_reply'):
            enrollment.status = 'converted'
            enrollment.exit_reason = 'Replied to email'
            enrollment.exited_at = timezone.now()
            enrollment.save(update_fields=['status', 'exit_reason', 'exited_at'])

            # Update sequence stats
            enrollment.sequence.total_converted += 1
            enrollment.sequence.save(update_fields=['total_converted'])

    except SequenceEnrollment.DoesNotExist:
        pass
