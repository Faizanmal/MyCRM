import uuid

from django.contrib.auth.models import User
from django.db import models


class WearableDevice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wearable_devices')
    device_type = models.CharField(max_length=100, choices=[
        ('eeg_headband', 'EEG Headband'),
        ('smart_watch', 'Smart Watch'),
        ('fitness_tracker', 'Fitness Tracker')
    ])
    device_id = models.CharField(max_length=255, unique=True)
    is_connected = models.BooleanField(default=False)
    last_sync = models.DateTimeField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class EmotionalState(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emotional_states')
    device = models.ForeignKey(WearableDevice, on_delete=models.CASCADE)
    state = models.CharField(max_length=50, choices=[
        ('calm', 'Calm'), ('focused', 'Focused'), ('stressed', 'Stressed'),
        ('excited', 'Excited'), ('fatigued', 'Fatigued')
    ])
    confidence = models.FloatField()
    metrics = models.JSONField(default=dict)
    context = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [models.Index(fields=['user', '-timestamp'])]

class SentimentDrivenAction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    emotional_state = models.ForeignKey(EmotionalState, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=100)
    description = models.TextField()
    was_executed = models.BooleanField(default=False)
    user_feedback = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
