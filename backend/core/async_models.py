"""
Async Task Execution and Poison Pill Quarantine Models
"""
import uuid
from django.db import models


class TaskExecutionRecord(models.Model):
    """
    Tracks task execution for distributed idempotency.
    Prevents duplicate background jobs from duplicating external side-effects
    (e.g., duplicate emails, double billing, duplicate notifications).
    """
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_name = models.CharField(max_length=255, db_index=True)
    idempotency_key = models.CharField(max_length=255, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'crm_task_execution_records'
        verbose_name = 'Task Execution Record'
        verbose_name_plural = 'Task Execution Records'
        indexes = [
            models.Index(fields=['task_name', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.task_name} - {self.idempotency_key} ({self.status})"


class PoisonPillQuarantine(models.Model):
    """
    Quarantines malformed, poisoned, or unrecoverable background jobs.
    Prevents infinite crash loops in Celery workers and maintains a complete audit trail.
    """
    STATUS_CHOICES = [
        ('quarantined', 'Quarantined'),
        ('reviewed', 'Reviewed'),
        ('replayed', 'Replayed'),
        ('discarded', 'Discarded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_name = models.CharField(max_length=255, db_index=True)
    task_id = models.CharField(max_length=255, blank=True)
    payload = models.JSONField(default=dict)
    error_type = models.CharField(max_length=255)
    error_message = models.TextField()
    traceback = models.TextField(blank=True)
    tenant = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quarantined_tasks'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='quarantined')
    quarantined_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    class Meta:
        db_table = 'crm_poison_pill_quarantines'
        verbose_name = 'Poison Pill Quarantine'
        verbose_name_plural = 'Poison Pill Quarantines'
        indexes = [
            models.Index(fields=['task_name', 'status']),
            models.Index(fields=['quarantined_at']),
            models.Index(fields=['tenant']),
        ]

    def __str__(self):
        return f"Quarantine: {self.task_name} ({self.error_type}) at {self.quarantined_at}"
