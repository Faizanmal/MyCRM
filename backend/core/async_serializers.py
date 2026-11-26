"""
Serializers for Async Background Tasks and Poison Pill Quarantine
"""

from rest_framework import serializers

from core.async_models import PoisonPillQuarantine, TaskExecutionRecord


class PoisonPillQuarantineSerializer(serializers.ModelSerializer):
    """Serializer for reviewing and managing quarantined background jobs"""
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)

    class Meta:
        model = PoisonPillQuarantine
        fields = [
            'id',
            'task_name',
            'task_id',
            'payload',
            'error_type',
            'error_message',
            'traceback',
            'tenant',
            'tenant_name',
            'status',
            'quarantined_at',
            'resolved_at',
            'resolution_notes',
        ]
        read_only_fields = [
            'id',
            'task_name',
            'task_id',
            'error_type',
            'error_message',
            'traceback',
            'tenant',
            'quarantined_at',
        ]


class TaskExecutionRecordSerializer(serializers.ModelSerializer):
    """Serializer for inspecting task execution records and idempotency locks"""

    class Meta:
        model = TaskExecutionRecord
        fields = [
            'id',
            'task_name',
            'idempotency_key',
            'status',
            'result',
            'created_at',
            'completed_at',
        ]
        read_only_fields = [
            'id',
            'task_name',
            'idempotency_key',
            'status',
            'result',
            'created_at',
            'completed_at',
        ]
