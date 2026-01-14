import uuid

from django.contrib.auth.models import User
from django.db import models


class CarbonFootprint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carbon_footprints')
    interaction_type = models.CharField(max_length=100, choices=[
        ('email', 'Email'), ('video_call', 'Video Call'),
        ('file_transfer', 'File Transfer'), ('api_call', 'API Call')
    ])
    carbon_grams = models.FloatField(help_text="Carbon footprint in grams of CO2")
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)
    offset_applied = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']
        indexes = [models.Index(fields=['user', '-timestamp'])]

class CarbonOffset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carbon_offsets')
    carbon_grams_offset = models.FloatField()
    cost_usd = models.DecimalField(max_digits=10, decimal_places=2)
    provider = models.CharField(max_length=255)
    certificate_url = models.URLField(blank=True)
    transaction_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class LowImpactAlternative(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    original_action = models.CharField(max_length=100)
    alternative_action = models.CharField(max_length=100)
    carbon_savings_grams = models.FloatField()
    description = models.TextField()
    usage_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
