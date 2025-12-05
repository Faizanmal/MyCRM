"""
Voice Intelligence Signals
Django signals for voice intelligence events
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
import logging

from .models import (
    VoiceRecording, Transcription, ActionItem,
    ConversationCategory, RecordingCategory
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=VoiceRecording)
def on_recording_created(sender, instance, created, **kwargs):
    """Handle new recording creation"""
    if created:
        logger.info(f"New voice recording created: {instance.id}")
        
        # Auto-start processing if uploaded
        if instance.status == 'uploaded':
            # Import here to avoid circular imports
            from .tasks import process_recording_task
            
            # Queue processing with slight delay
            process_recording_task.apply_async(
                args=[str(instance.id)],
                countdown=2  # Start after 2 seconds
            )


@receiver(post_save, sender=VoiceRecording)
def on_recording_status_change(sender, instance, created, **kwargs):
    """Handle recording status changes"""
    if not created:
        # Check if status changed to completed
        if instance.status == 'completed':
            logger.info(f"Recording processing completed: {instance.id}")
            
            # Send notification if enabled
            try:
                from .models import TranscriptionSettings
                settings = TranscriptionSettings.objects.filter(
                    user=instance.owner
                ).first()
                
                if settings and settings.notify_on_completion:
                    # TODO: Send notification
                    pass
                    
            except Exception as e:
                logger.error(f"Error sending completion notification: {str(e)}")


@receiver(post_save, sender=Transcription)
def on_transcription_created(sender, instance, created, **kwargs):
    """Handle new transcription"""
    if created:
        logger.info(f"Transcription created for recording: {instance.recording_id}")
        
        # Update recording status
        recording = instance.recording
        if recording.status == 'transcribing':
            recording.status = 'transcribed'
            recording.save(update_fields=['status'])


@receiver(post_save, sender=ActionItem)
def on_action_item_created(sender, instance, created, **kwargs):
    """Handle new action item"""
    if created:
        logger.info(f"Action item created: {instance.title}")
        
        # Check for high priority notification
        if instance.priority in ['high', 'critical']:
            try:
                from .models import TranscriptionSettings
                settings = TranscriptionSettings.objects.filter(
                    user=instance.recording.owner
                ).first()
                
                if settings and settings.notify_on_high_priority_action:
                    # TODO: Send notification
                    pass
                    
            except Exception as e:
                logger.error(f"Error sending action item notification: {str(e)}")


@receiver(post_save, sender=ActionItem)
def on_action_item_status_change(sender, instance, created, **kwargs):
    """Track action item status changes"""
    if not created:
        # Log status changes for analytics
        logger.info(
            f"Action item {instance.id} status changed to {instance.status}"
        )


@receiver(post_save, sender=RecordingCategory)
def on_category_assigned(sender, instance, created, **kwargs):
    """Update category count when assigned"""
    if created:
        category = instance.category
        category.recording_count = category.recordings.count()
        category.save(update_fields=['recording_count'])


@receiver(pre_delete, sender=RecordingCategory)
def on_category_removed(sender, instance, **kwargs):
    """Update category count when removed"""
    category = instance.category
    # Will be one less after delete
    category.recording_count = max(0, category.recordings.count() - 1)
    category.save(update_fields=['recording_count'])


@receiver(pre_delete, sender=VoiceRecording)
def on_recording_deleted(sender, instance, **kwargs):
    """Handle recording deletion"""
    logger.info(f"Voice recording deleted: {instance.id}")
    
    # TODO: Delete associated files from storage
    # if instance.file_path:
    #     delete_file_from_storage(instance.file_path)


@receiver(post_save, sender=ConversationCategory)
def on_category_created(sender, instance, created, **kwargs):
    """Handle new category creation"""
    if created:
        logger.info(f"New conversation category created: {instance.name}")


# Activity feed integration
def create_activity_for_recording(recording, action):
    """Create activity feed entry for recording events"""
    try:
        from activity_feed.models import Activity
        
        Activity.objects.create(
            user=recording.owner,
            action=action,
            content_type='voice_recording',
            object_id=str(recording.id),
            metadata={
                'title': recording.title,
                'duration': recording.duration_seconds,
                'source_type': recording.source_type
            }
        )
    except ImportError:
        pass  # Activity feed module not available
    except Exception as e:
        logger.error(f"Error creating activity: {str(e)}")


@receiver(post_save, sender=VoiceRecording)
def create_recording_activity(sender, instance, created, **kwargs):
    """Create activity for recording events"""
    if created:
        create_activity_for_recording(instance, 'created')
    elif instance.status == 'completed':
        create_activity_for_recording(instance, 'processed')
