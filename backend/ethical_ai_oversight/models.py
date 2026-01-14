import uuid

from django.contrib.auth.models import User
from django.db import models


class AIBiasDetection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    model_name = models.CharField(max_length=255)
    detection_date = models.DateTimeField(auto_now_add=True)
    bias_type = models.CharField(max_length=100, choices=[
        ('demographic', 'Demographic Bias'),
        ('geographic', 'Geographic Bias'),
        ('temporal', 'Temporal Bias'),
        ('confirmation', 'Confirmation Bias')
    ])
    severity = models.CharField(max_length=20, choices=[
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')
    ])
    affected_groups = models.JSONField(default=list)
    confidence_score = models.FloatField()
    mitigation_recommendations = models.JSONField(default=list)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-detection_date']

class AIDecisionAudit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    model_name = models.CharField(max_length=255)
    decision_type = models.CharField(max_length=100)
    input_data = models.JSONField(default=dict)
    output = models.JSONField(default=dict)
    explanation = models.TextField()
    confidence_score = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL)
    flagged_for_review = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']
        indexes = [models.Index(fields=['model_name', '-timestamp'])]

class EthicsConfiguration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ethics_configs')
    model_name = models.CharField(max_length=255)
    fairness_threshold = models.FloatField(default=0.8)
    bias_sensitivity = models.FloatField(default=0.5)
    explanation_detail_level = models.CharField(max_length=20, default='medium')
    auto_flag_threshold = models.FloatField(default=0.7)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'model_name']
