from django.contrib.auth.models import User
from django.db import models
import uuid

class VirtualShowroom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    platform = models.CharField(max_length=100, choices=[
        ('decentraland', 'Decentraland'), ('sandbox', 'The Sandbox'),
        ('horizon', 'Horizon Worlds'), ('spatial', 'Spatial')
    ])
    url = models.URLField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.JSONField(default=list)
    visitors_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class AvatarMeeting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=255)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    platform = models.CharField(max_length=100)
    meeting_url = models.URLField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_meetings')
    participants = models.ManyToManyField(User, related_name='avatar_meetings')
    spatial_audio_enabled = models.BooleanField(default=True)
    haptic_feedback_enabled = models.BooleanField(default=False)
    real_time_translation = models.BooleanField(default=True)
    recording_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-scheduled_at']

class MetaverseProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    description = models.TextField()
    model_3d_url = models.URLField()
    showroom = models.ForeignKey(VirtualShowroom, on_delete=models.CASCADE, related_name='products_detailed')
    interactions_count = models.IntegerField(default=0)
    demo_requests = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
