import uuid

from django.db import models


class SpaceEndpoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=100, choices=[
        ('earth', 'Earth'), ('moon', 'Moon'), ('mars', 'Mars'),
        ('iss', 'International Space Station'), ('satellite', 'Satellite')
    ])
    latency_seconds = models.IntegerField()
    connection_type = models.CharField(max_length=50)
    is_online = models.BooleanField(default=True)
    last_sync = models.DateTimeField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['latency_seconds']

class DelayTolerantMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    from_endpoint = models.ForeignKey(SpaceEndpoint, on_delete=models.CASCADE, related_name='sent_messages')
    to_endpoint = models.ForeignKey(SpaceEndpoint, on_delete=models.CASCADE, related_name='received_messages')
    message_type = models.CharField(max_length=100)
    payload = models.JSONField(default=dict)
    priority = models.IntegerField(default=5)
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(blank=True)
    status = models.CharField(max_length=20, default='queued')
    encryption_type = models.CharField(max_length=50, default='satellite_optimized')

    class Meta:
        ordering = ['-priority', 'sent_at']

class OfflineDataCache(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    endpoint = models.ForeignKey(SpaceEndpoint, on_delete=models.CASCADE)
    data_type = models.CharField(max_length=100)
    data = models.JSONField(default=dict)
    version = models.IntegerField(default=1)
    synced = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    synced_at = models.DateTimeField(blank=True)
