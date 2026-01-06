import logging

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import Organization, OrganizationInvitation, OrganizationMember

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Organization)
def create_owner_membership(sender, instance, created, **kwargs):
    """
    When a new organization is created, automatically create an owner membership
    for the user who created it.
    """
    if created and instance.created_by:
        OrganizationMember.objects.get_or_create(
            organization=instance,
            user=instance.created_by,
            defaults={
                'role': 'owner',
                'can_invite_users': True,
                'can_manage_billing': True,
                'can_manage_settings': True,
            }
        )


@receiver(post_save, sender=OrganizationInvitation)
def send_invitation_email(sender, instance, created, **kwargs):
    """
    Send an email when a new invitation is created.
    """
    if created and instance.status == 'pending':
        try:
            from core.email_notifications import EmailNotificationService
            EmailNotificationService.send_organization_invitation(instance)
            logger.info(f"Invitation email sent to {instance.email} for org {instance.organization.name}")
        except Exception as e:
            logger.error(f"Failed to send invitation email to {instance.email}: {e}")


@receiver(pre_delete, sender=OrganizationMember)
def prevent_last_owner_deletion(sender, instance, **kwargs):
    """
    Prevent deletion of the last owner in an organization.
    """
    if instance.role == 'owner':
        owner_count = OrganizationMember.objects.filter(
            organization=instance.organization,
            role='owner',
            is_active=True
        ).count()

        if owner_count <= 1:
            raise ValueError("Cannot remove the last owner from an organization.")
