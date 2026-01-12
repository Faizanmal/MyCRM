from django.contrib.auth.models import User
from django.db import models
import uuid

class WorkflowVariant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    base_workflow = models.CharField(max_length=255)
    modifications = models.JSONField(default=dict)
    generation_method = models.CharField(max_length=100, default='generative_ai')
    status = models.CharField(max_length=20, default='testing')
    created_by_ai = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class ABTestResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    workflow_variant = models.ForeignKey(WorkflowVariant, on_delete=models.CASCADE, related_name='test_results')
    metric_name = models.CharField(max_length=100)
    control_value = models.FloatField()
    variant_value = models.FloatField()
    improvement_percentage = models.FloatField()
    statistical_significance = models.FloatField()
    sample_size = models.IntegerField()
    test_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-test_date']

class AIWorkflowProposal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    workflow_name = models.CharField(max_length=255)
    proposal_description = models.TextField()
    expected_improvement = models.FloatField()
    confidence_score = models.FloatField()
    reasoning = models.TextField()
    status = models.CharField(max_length=20, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
