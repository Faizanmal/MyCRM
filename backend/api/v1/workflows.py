"""
Workflow Automation API Views
"""
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import NotificationTemplate, Workflow, WorkflowExecution
from core.tasks import execute_workflow


class WorkflowSerializer(serializers.ModelSerializer):
    """Workflow serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    execution_count = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = [
            'id', 'name', 'description', 'trigger_type', 'trigger_conditions',
            'actions', 'status', 'created_by', 'created_by_name', 'execution_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_execution_count(self, obj):
        return obj.executions.count()

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class WorkflowExecutionSerializer(serializers.ModelSerializer):
    """Workflow execution serializer"""
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)

    class Meta:
        model = WorkflowExecution
        fields = [
            'id', 'workflow', 'workflow_name', 'trigger_data', 'status',
            'steps_completed', 'total_steps', 'error_message', 'execution_log',
            'started_at', 'completed_at'
        ]
        read_only_fields = fields


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Notification template serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'notification_type', 'subject_template', 'body_template',
            'variables', 'is_active', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class WorkflowViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Workflow management
    """
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a workflow manually"""
        workflow = self.get_object()

        trigger_data = request.data.get('trigger_data', {})

        # Execute in background
        task = execute_workflow.delay(str(workflow.id), trigger_data)

        return Response({
            'success': True,
            'task_id': task.id,
            'message': 'Workflow execution started'
        })

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a workflow"""
        workflow = self.get_object()
        workflow.status = 'active'
        workflow.save()

        return Response({
            'success': True,
            'message': 'Workflow activated'
        })

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a workflow"""
        workflow = self.get_object()
        workflow.status = 'inactive'
        workflow.save()

        return Response({
            'success': True,
            'message': 'Workflow deactivated'
        })

    @action(detail=True, methods=['get'])
    def executions(self, request, pk=None):
        """Get execution history for a workflow"""
        workflow = self.get_object()
        executions = workflow.executions.all()[:50]  # Last 50 executions

        serializer = WorkflowExecutionSerializer(executions, many=True)
        return Response(serializer.data)


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Notification Template management
    """
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by type
        notification_type = self.request.query_params.get('type', None)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)

        # Only active templates
        active_only = self.request.query_params.get('active_only', None)
        if active_only == 'true':
            queryset = queryset.filter(is_active=True)

        return queryset
