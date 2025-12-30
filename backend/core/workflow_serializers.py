"""
Advanced Workflow Engine Serializers
"""

from rest_framework import serializers
from .workflow_models import (
    WorkflowDefinition, WorkflowNode, WorkflowConnection,
    WorkflowInstance, WorkflowNodeExecution, WorkflowApprovalRequest,
    WorkflowTrigger, WorkflowVariable, WorkflowTemplate, WorkflowLog
)


class WorkflowNodeSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowNode"""
    
    class Meta:
        model = WorkflowNode
        fields = [
            'id', 'node_id', 'name', 'node_type',
            'config', 'position_x', 'position_y',
            'timeout_minutes', 'retry_count', 'retry_delay_minutes',
            'on_error', 'error_branch_node',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WorkflowConnectionSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowConnection"""
    
    class Meta:
        model = WorkflowConnection
        fields = [
            'id', 'source_node', 'source_port',
            'target_node', 'target_port',
            'condition', 'label', 'priority',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class WorkflowVariableSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowVariable"""
    
    class Meta:
        model = WorkflowVariable
        fields = [
            'id', 'name', 'display_name', 'variable_type',
            'default_value', 'is_required', 'validation_rules',
            'description', 'input_type', 'options',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class WorkflowTriggerSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowTrigger"""
    
    class Meta:
        model = WorkflowTrigger
        fields = [
            'id', 'event_type', 'entity_type',
            'conditions', 'schedule_expression', 'schedule_timezone',
            'watched_fields', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WorkflowDefinitionSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowDefinition"""
    
    nodes = WorkflowNodeSerializer(many=True, read_only=True)
    connections = WorkflowConnectionSerializer(many=True, read_only=True)
    variables = WorkflowVariableSerializer(many=True, read_only=True)
    triggers = WorkflowTriggerSerializer(many=True, read_only=True)
    
    node_count = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowDefinition
        fields = [
            'id', 'name', 'description', 'category',
            'status', 'trigger_type', 'trigger_config',
            'entry_conditions', 'canvas_data',
            'allow_multiple', 'max_concurrent', 'timeout_hours',
            'version', 'is_template', 'shared_with',
            'run_count', 'success_count', 'failure_count',
            'nodes', 'connections', 'variables', 'triggers',
            'node_count', 'success_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'run_count', 'success_count', 'failure_count',
            'created_at', 'updated_at'
        ]
    
    def get_node_count(self, obj):
        return obj.nodes.count()
    
    def get_success_rate(self, obj):
        if obj.run_count > 0:
            return round(obj.success_count / obj.run_count * 100, 1)
        return None


class WorkflowDefinitionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing workflows"""
    
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowDefinition
        fields = [
            'id', 'name', 'description', 'category',
            'status', 'trigger_type',
            'run_count', 'success_count', 'failure_count',
            'success_rate',
            'created_at', 'updated_at'
        ]
    
    def get_success_rate(self, obj):
        if obj.run_count > 0:
            return round(obj.success_count / obj.run_count * 100, 1)
        return None


class WorkflowNodeExecutionSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowNodeExecution"""
    
    node_name = serializers.SerializerMethodField()
    node_type = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowNodeExecution
        fields = [
            'id', 'node', 'node_name', 'node_type',
            'status', 'input_data', 'output_data',
            'started_at', 'completed_at', 'execution_time_ms',
            'attempt_number', 'error_message', 'error_details',
            'approval_status', 'approved_by', 'approval_comment',
            'created_at'
        ]
    
    def get_node_name(self, obj):
        return obj.node.name if obj.node else None
    
    def get_node_type(self, obj):
        return obj.node.node_type if obj.node else None


class WorkflowInstanceSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowInstance"""
    
    workflow_name = serializers.SerializerMethodField()
    node_executions = WorkflowNodeExecutionSerializer(many=True, read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowInstance
        fields = [
            'id', 'workflow', 'workflow_name',
            'triggered_by', 'trigger_event', 'trigger_data',
            'target_content_type', 'target_object_id',
            'status', 'current_node', 'context',
            'started_at', 'completed_at', 'last_activity_at',
            'error_message', 'error_node',
            'resume_at', 'resume_data',
            'node_executions', 'duration'
        ]
    
    def get_workflow_name(self, obj):
        return obj.workflow.name if obj.workflow else None
    
    def get_duration(self, obj):
        if obj.completed_at and obj.started_at:
            return int((obj.completed_at - obj.started_at).total_seconds())
        return None


class WorkflowInstanceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing instances"""
    
    workflow_name = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowInstance
        fields = [
            'id', 'workflow', 'workflow_name',
            'status', 'current_node',
            'started_at', 'completed_at',
            'error_message'
        ]
    
    def get_workflow_name(self, obj):
        return obj.workflow.name if obj.workflow else None


class WorkflowApprovalRequestSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowApprovalRequest"""
    
    workflow_name = serializers.SerializerMethodField()
    approver_email = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowApprovalRequest
        fields = [
            'id', 'node_execution',
            'approver', 'approver_email',
            'title', 'description', 'data_to_review',
            'approval_options', 'requires_comment',
            'status', 'decision', 'comment',
            'delegated_to', 'delegated_reason',
            'due_date', 'responded_at',
            'reminder_sent_count', 'last_reminder_at',
            'workflow_name',
            'created_at'
        ]
        read_only_fields = [
            'id', 'reminder_sent_count', 'last_reminder_at', 'created_at'
        ]
    
    def get_workflow_name(self, obj):
        if obj.node_execution and obj.node_execution.instance:
            return obj.node_execution.instance.workflow.name
        return None
    
    def get_approver_email(self, obj):
        return obj.approver.email if obj.approver else None


class WorkflowLogSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowLog"""
    
    class Meta:
        model = WorkflowLog
        fields = [
            'id', 'log_type', 'node_id',
            'message', 'details',
            'created_at'
        ]


class WorkflowTemplateSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowTemplate"""
    
    class Meta:
        model = WorkflowTemplate
        fields = [
            'id', 'name', 'description', 'category',
            'definition_data', 'preview_image',
            'use_count', 'rating', 'rating_count',
            'is_official', 'is_active',
            'created_at', 'updated_at'
        ]


# Request Serializers
class CreateWorkflowSerializer(serializers.Serializer):
    """Request serializer for creating a workflow"""
    
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    category = serializers.ChoiceField(
        choices=[
            'sales', 'marketing', 'support', 'onboarding',
            'approval', 'notification', 'data_management', 'custom'
        ],
        default='custom'
    )
    trigger_type = serializers.ChoiceField(
        choices=['event', 'schedule', 'manual', 'api', 'record_change']
    )
    trigger_config = serializers.DictField(required=False, default=dict)
    entry_conditions = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=[]
    )


class AddNodeSerializer(serializers.Serializer):
    """Request serializer for adding a node"""
    
    node_id = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=255)
    node_type = serializers.CharField(max_length=50)
    config = serializers.DictField(required=False, default=dict)
    position_x = serializers.IntegerField(default=0)
    position_y = serializers.IntegerField(default=0)
    timeout_minutes = serializers.IntegerField(required=False)
    retry_count = serializers.IntegerField(default=0)
    on_error = serializers.ChoiceField(
        choices=['stop', 'continue', 'branch'],
        default='stop'
    )


class AddConnectionSerializer(serializers.Serializer):
    """Request serializer for adding a connection"""
    
    source_node = serializers.CharField(max_length=100)
    target_node = serializers.CharField(max_length=100)
    source_port = serializers.CharField(max_length=50, default='output')
    target_port = serializers.CharField(max_length=50, default='input')
    condition = serializers.DictField(required=False, default=dict)
    label = serializers.CharField(max_length=100, required=False, allow_blank=True)


class SaveCanvasSerializer(serializers.Serializer):
    """Request serializer for saving canvas"""
    
    nodes = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=[]
    )
    connections = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=[]
    )
    viewport = serializers.DictField(required=False)


class StartWorkflowSerializer(serializers.Serializer):
    """Request serializer for starting a workflow"""
    
    workflow_id = serializers.UUIDField()
    trigger_data = serializers.DictField(required=False, default=dict)
    target_content_type = serializers.CharField(required=False, allow_blank=True)
    target_object_id = serializers.CharField(required=False, allow_blank=True)


class ApprovalResponseSerializer(serializers.Serializer):
    """Request serializer for approval response"""
    
    decision = serializers.CharField(max_length=50)
    comment = serializers.CharField(required=False, allow_blank=True)


class DelegateApprovalSerializer(serializers.Serializer):
    """Request serializer for delegating approval"""
    
    delegate_to_id = serializers.UUIDField()
    reason = serializers.CharField(required=False, allow_blank=True)


class AddVariableSerializer(serializers.Serializer):
    """Request serializer for adding a variable"""
    
    name = serializers.CharField(max_length=100)
    display_name = serializers.CharField(max_length=255)
    variable_type = serializers.ChoiceField(
        choices=['string', 'number', 'boolean', 'date', 'datetime', 'list', 'object']
    )
    default_value = serializers.JSONField(required=False)
    is_required = serializers.BooleanField(default=False)
    description = serializers.CharField(required=False, allow_blank=True)
    input_type = serializers.CharField(default='text')
    options = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=[]
    )


class AddTriggerSerializer(serializers.Serializer):
    """Request serializer for adding a trigger"""
    
    event_type = serializers.CharField(max_length=50)
    entity_type = serializers.CharField(required=False, allow_blank=True)
    conditions = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=[]
    )
    schedule_expression = serializers.CharField(required=False, allow_blank=True)
    schedule_timezone = serializers.CharField(default='UTC')
    watched_fields = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=[]
    )


class CloneWorkflowSerializer(serializers.Serializer):
    """Request serializer for cloning a workflow"""
    
    new_name = serializers.CharField(max_length=255)


class CreateFromTemplateSerializer(serializers.Serializer):
    """Request serializer for creating from template"""
    
    template_id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)
    customize = serializers.DictField(required=False, default=dict)
