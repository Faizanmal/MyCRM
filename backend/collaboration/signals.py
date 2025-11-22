from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import (
    Message, DealRoom, DealRoomParticipant,
    DocumentComment, CollaborativeDocument,
    ApprovalAction, ApprovalInstance
)


@receiver(post_save, sender=Message)
def update_message_counts(sender, instance, created, **kwargs):
    """Update message counts when a message is created."""
    if created and not instance.is_deleted:
        if instance.channel:
            instance.channel.message_count += 1
            instance.channel.save(update_fields=['message_count', 'updated_at'])
        elif instance.deal_room:
            instance.deal_room.message_count += 1
            instance.deal_room.save(update_fields=['message_count', 'updated_at'])
        
        # Update thread reply count
        if instance.parent_message:
            instance.parent_message.thread_reply_count += 1
            instance.parent_message.save(update_fields=['thread_reply_count'])


@receiver(post_delete, sender=Message)
def decrement_message_counts(sender, instance, **kwargs):
    """Decrement message counts when a message is deleted."""
    if instance.channel:
        instance.channel.message_count = max(0, instance.channel.message_count - 1)
        instance.channel.save(update_fields=['message_count'])
    elif instance.deal_room:
        instance.deal_room.message_count = max(0, instance.deal_room.message_count - 1)
        instance.deal_room.save(update_fields=['message_count'])


@receiver(post_save, sender=DealRoomParticipant)
def update_participant_count(sender, instance, created, **kwargs):
    """Update participant count when a participant is added."""
    if created:
        instance.deal_room.participant_count += 1
        instance.deal_room.save(update_fields=['participant_count'])


@receiver(post_delete, sender=DealRoomParticipant)
def decrement_participant_count(sender, instance, **kwargs):
    """Decrement participant count when a participant is removed."""
    instance.deal_room.participant_count = max(0, instance.deal_room.participant_count - 1)
    instance.deal_room.save(update_fields=['participant_count'])


@receiver(post_save, sender=DocumentComment)
def update_comment_count(sender, instance, created, **kwargs):
    """Update comment count when a comment is created."""
    if created:
        instance.document.comment_count += 1
        instance.document.save(update_fields=['comment_count'])


@receiver(post_delete, sender=DocumentComment)
def decrement_comment_count(sender, instance, **kwargs):
    """Decrement comment count when a comment is deleted."""
    instance.document.comment_count = max(0, instance.document.comment_count - 1)
    instance.document.save(update_fields=['comment_count'])


@receiver(post_save, sender=CollaborativeDocument)
def update_document_count_in_dealroom(sender, instance, created, **kwargs):
    """Update document count in deal room."""
    if created and instance.deal_room:
        instance.deal_room.document_count += 1
        instance.deal_room.save(update_fields=['document_count'])


@receiver(post_save, sender=ApprovalInstance)
def update_workflow_instance_count(sender, instance, created, **kwargs):
    """Update workflow instance counts."""
    if created:
        instance.workflow.total_instances += 1
        instance.workflow.save(update_fields=['total_instances'])
    elif instance.status in ['approved', 'rejected'] and instance.completed_at:
        if instance.status == 'approved':
            instance.workflow.completed_instances += 1
            instance.workflow.save(update_fields=['completed_instances'])
