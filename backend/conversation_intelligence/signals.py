"""
Conversation Intelligence Signals
"""

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='conversation_intelligence.CallRecording')
def handle_recording_status_change(sender, instance, **kwargs):
    """Handle recording status changes"""
    if instance.status == 'ready':
        # Could notify owner, create activity, etc.
        pass


@receiver(post_save, sender='conversation_intelligence.CallAnalysis')
def handle_analysis_complete(sender, instance, **kwargs):
    """Handle analysis completion"""
    # Could update opportunity, create tasks for low scores, etc.
    recording = instance.recording

    if instance.call_score < 50 and recording.owner:
        # Could create a coaching task
        pass
