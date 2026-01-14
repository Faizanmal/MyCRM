import uuid

from django.contrib.auth.models import User
from django.db import models


class HolographicSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_holo_sessions')
    participants = models.ManyToManyField(User, related_name='holo_sessions')
    scheduled_at = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    hologram_quality = models.CharField(max_length=20, default='high')
    gesture_controls_enabled = models.BooleanField(default=True)
    bandwidth_requirement_mbps = models.IntegerField(default=50)
    recording_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scheduled_at']

class HolographicAvatar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='holographic_avatar')
    model_url = models.URLField()
    appearance_settings = models.JSONField(default=dict)
    gesture_library = models.JSONField(default=list)
    last_updated = models.DateTimeField(auto_now=True)
