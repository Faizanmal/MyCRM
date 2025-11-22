from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Organization, OrganizationMember, OrganizationInvitation

User = get_user_model()


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
        # TODO: Send invitation email
        # from django.core.mail import send_mail
        # send_mail(
        #     subject=f'Invitation to join {instance.organization.name}',
        #     message=f'You have been invited to join {instance.organization.name}...',
        #     from_email='noreply@mycrm.com',
        #     recipient_list=[instance.email],
        # )
        pass


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
