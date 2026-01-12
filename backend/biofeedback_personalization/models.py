from django.contrib.auth.models import User
from django.db import models
import uuid

class BiofeedbackProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='biofeedback_profile')
    baseline_heart_rate = models.IntegerField(null=True, blank=True)
    baseline_stress_level = models.FloatField(null=True, blank=True)
    preferences = models.JSONField(default=dict)
    calibrated = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

class BiometricReading(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    profile = models.ForeignKey(BiofeedbackProfile, on_delete=models.CASCADE, related_name='readings')
    reading_type = models.CharField(max_length=100)
    value = models.FloatField()
    unit = models.CharField(max_length=50)
    context = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [models.Index(fields=['profile', '-timestamp'])]

class PersonalizationRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    profile = models.ForeignKey(BiofeedbackProfile, on_delete=models.CASCADE, related_name='rules')
    condition = models.JSONField(default=dict)
    action = models.JSONField(default=dict)
    priority = models.IntegerField(default=5)
    is_active = models.BooleanField(default=True)
    activation_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
