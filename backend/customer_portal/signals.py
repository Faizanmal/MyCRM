"""
Customer Portal Signals
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import SupportTicket, TicketComment, PortalNotification


@receiver(post_save, sender=TicketComment)
def notify_ticket_comment(sender, instance, created, **kwargs):
    """
    Send notification when a new comment is added to a ticket
    """
    if created and not instance.is_internal:
        ticket = instance.ticket
        
        # If comment is from internal user, notify customer
        if instance.internal_user and not instance.customer:
            PortalNotification.objects.create(
                customer=ticket.customer,
                notification_type='ticket_update',
                title=f'New reply on ticket #{ticket.ticket_number}',
                message=f'Your support ticket "{ticket.subject}" has a new response.',
                action_url=f'/portal/tickets/{ticket.id}'
            )
            
            # Update first response time if not set
            if not ticket.first_response_at:
                from django.utils import timezone
                ticket.first_response_at = timezone.now()
                ticket.save(update_fields=['first_response_at'])


@receiver(post_save, sender=SupportTicket)
def notify_ticket_status_change(sender, instance, created, **kwargs):
    """
    Send notification when ticket status changes
    """
    if not created:
        # Check if status changed to resolved
        if instance.status == 'resolved':
            PortalNotification.objects.create(
                customer=instance.customer,
                notification_type='ticket_update',
                title=f'Ticket #{instance.ticket_number} resolved',
                message=f'Your support ticket "{instance.subject}" has been resolved.',
                action_url=f'/portal/tickets/{instance.id}'
            )
