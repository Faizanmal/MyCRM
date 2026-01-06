"""
Advanced Workflow Engine Views
"""

from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .workflow_models import (
    WorkflowApprovalRequest,
    WorkflowConnection,
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowLog,
    WorkflowNode,
    WorkflowTemplate,
    WorkflowTrigger,
    WorkflowVariable,
)
from .workflow_serializers import (
    AddConnectionSerializer,
    AddNodeSerializer,
    AddTriggerSerializer,
    AddVariableSerializer,
    ApprovalResponseSerializer,
    CloneWorkflowSerializer,
    CreateFromTemplateSerializer,
    CreateWorkflowSerializer,
    DelegateApprovalSerializer,
    SaveCanvasSerializer,
    StartWorkflowSerializer,
    WorkflowApprovalRequestSerializer,
    WorkflowDefinitionListSerializer,
    WorkflowDefinitionSerializer,
    WorkflowInstanceListSerializer,
    WorkflowInstanceSerializer,
    WorkflowLogSerializer,
    WorkflowNodeExecutionSerializer,
    WorkflowNodeSerializer,
    WorkflowTemplateSerializer,
    WorkflowTriggerSerializer,
    WorkflowVariableSerializer,
)
from .workflow_services import ApprovalService, WorkflowDesignerService, WorkflowEngineService


class WorkflowDefinitionViewSet(viewsets.ModelViewSet):
    """ViewSet for workflow definitions"""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return WorkflowDefinitionListSerializer
        return WorkflowDefinitionSerializer

    def get_queryset(self):
        queryset = WorkflowDefinition.objects.filter(user=self.request.user)

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # Filter by trigger type
        trigger_type = self.request.query_params.get('trigger_type')
        if trigger_type:
            queryset = queryset.filter(trigger_type=trigger_type)

        return queryset.order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def create_workflow(self, request):
        """Create a new workflow"""
        serializer = CreateWorkflowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = WorkflowDesignerService(request.user)
        result = service.create_workflow(
            name=serializer.validated_data['name'],
            trigger_type=serializer.validated_data['trigger_type'],
            category=serializer.validated_data.get('category', 'custom'),
            config=serializer.validated_data
        )

        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_node(self, request, pk=None):
        """Add a node to workflow"""
        serializer = AddNodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = WorkflowDesignerService(request.user)
        result = service.add_node(pk, serializer.validated_data)

        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_connection(self, request, pk=None):
        """Add a connection between nodes"""
        serializer = AddConnectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = WorkflowDesignerService(request.user)
        result = service.add_connection(
            workflow_id=pk,
            source_node=serializer.validated_data['source_node'],
            target_node=serializer.validated_data['target_node'],
            condition=serializer.validated_data.get('condition'),
            label=serializer.validated_data.get('label', '')
        )

        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def save_canvas(self, request, pk=None):
        """Save complete canvas state"""
        serializer = SaveCanvasSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = WorkflowDesignerService(request.user)
        result = service.save_canvas(pk, serializer.validated_data)

        return Response(result)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate workflow"""
        service = WorkflowDesignerService(request.user)
        result = service.activate_workflow(pk)

        if result.get('error'):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(result)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate workflow"""
        workflow = self.get_object()
        workflow.status = 'paused'
        workflow.save(update_fields=['status', 'updated_at'])

        return Response({'status': 'paused'})

    @action(detail=True, methods=['get'])
    def validate(self, request, pk=None):
        """Validate workflow configuration"""
        service = WorkflowDesignerService(request.user)
        result = service.validate_workflow(pk)

        return Response(result)

    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        """Clone workflow"""
        serializer = CloneWorkflowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = WorkflowDesignerService(request.user)
        result = service.clone_workflow(
            pk, serializer.validated_data['new_name']
        )

        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_variable(self, request, pk=None):
        """Add a variable to workflow"""
        serializer = AddVariableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workflow = self.get_object()

        variable = WorkflowVariable.objects.create(
            workflow=workflow,
            **serializer.validated_data
        )

        return Response(
            WorkflowVariableSerializer(variable).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def add_trigger(self, request, pk=None):
        """Add a trigger to workflow"""
        serializer = AddTriggerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workflow = self.get_object()

        trigger = WorkflowTrigger.objects.create(
            workflow=workflow,
            **serializer.validated_data
        )

        return Response(
            WorkflowTriggerSerializer(trigger).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get workflow statistics"""
        workflow = self.get_object()

        instances = workflow.instances.all()

        return Response({
            'total_runs': workflow.run_count,
            'success_count': workflow.success_count,
            'failure_count': workflow.failure_count,
            'success_rate': round(
                workflow.success_count / workflow.run_count * 100, 1
            ) if workflow.run_count > 0 else None,
            'running': instances.filter(status='running').count(),
            'waiting': instances.filter(status='waiting').count(),
            'avg_duration': self._calculate_avg_duration(instances)
        })

    def _calculate_avg_duration(self, instances):
        """Calculate average duration"""
        completed = instances.filter(
            status='completed',
            completed_at__isnull=False
        )

        if not completed.exists():
            return None

        total_seconds = sum(
            (i.completed_at - i.started_at).total_seconds()
            for i in completed
            if i.completed_at and i.started_at
        )

        return int(total_seconds / completed.count())


class WorkflowNodeViewSet(viewsets.ModelViewSet):
    """ViewSet for workflow nodes"""

    serializer_class = WorkflowNodeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        workflow_id = self.request.query_params.get('workflow_id')
        if workflow_id:
            return WorkflowNode.objects.filter(workflow_id=workflow_id)
        return WorkflowNode.objects.filter(workflow__user=self.request.user)

    @action(detail=False, methods=['get'])
    def types(self, request):
        """Get available node types"""
        return Response({
            'actions': [
                {'type': 'action_email', 'label': 'Send Email', 'icon': 'email'},
                {'type': 'action_sms', 'label': 'Send SMS', 'icon': 'sms'},
                {'type': 'action_notification', 'label': 'Send Notification', 'icon': 'notification'},
                {'type': 'action_task', 'label': 'Create Task', 'icon': 'task'},
                {'type': 'action_update_record', 'label': 'Update Record', 'icon': 'edit'},
                {'type': 'action_create_record', 'label': 'Create Record', 'icon': 'add'},
                {'type': 'action_webhook', 'label': 'Call Webhook', 'icon': 'webhook'},
                {'type': 'action_slack', 'label': 'Send to Slack', 'icon': 'slack'},
            ],
            'control': [
                {'type': 'condition', 'label': 'Condition', 'icon': 'branch'},
                {'type': 'branch', 'label': 'Branch/Split', 'icon': 'fork'},
                {'type': 'merge', 'label': 'Merge', 'icon': 'merge'},
                {'type': 'delay', 'label': 'Delay/Wait', 'icon': 'timer'},
                {'type': 'schedule', 'label': 'Schedule', 'icon': 'schedule'},
            ],
            'approvals': [
                {'type': 'approval_single', 'label': 'Single Approval', 'icon': 'approval'},
                {'type': 'approval_multi', 'label': 'Multi-Person Approval', 'icon': 'group_approval'},
                {'type': 'approval_sequential', 'label': 'Sequential Approval', 'icon': 'sequence'},
            ],
            'ai': [
                {'type': 'ai_decision', 'label': 'AI Decision', 'icon': 'ai'},
                {'type': 'ai_enrich', 'label': 'AI Enrichment', 'icon': 'enhance'},
                {'type': 'ai_score', 'label': 'AI Scoring', 'icon': 'score'},
            ],
            'end': [
                {'type': 'end_success', 'label': 'End - Success', 'icon': 'success'},
                {'type': 'end_failure', 'label': 'End - Failure', 'icon': 'error'},
            ]
        })


class WorkflowInstanceViewSet(viewsets.ModelViewSet):
    """ViewSet for workflow instances"""

    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_serializer_class(self):
        if self.action == 'list':
            return WorkflowInstanceListSerializer
        return WorkflowInstanceSerializer

    def get_queryset(self):
        queryset = WorkflowInstance.objects.filter(
            workflow__user=self.request.user
        )

        # Filter by workflow
        workflow_id = self.request.query_params.get('workflow_id')
        if workflow_id:
            queryset = queryset.filter(workflow_id=workflow_id)

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by('-started_at')

    @action(detail=False, methods=['post'])
    def start(self, request):
        """Start a new workflow instance"""
        serializer = StartWorkflowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = WorkflowEngineService(request.user)

        target = None
        if serializer.validated_data.get('target_content_type'):
            target = (
                serializer.validated_data['target_content_type'],
                serializer.validated_data.get('target_object_id', '')
            )

        result = service.start_workflow(
            workflow_id=str(serializer.validated_data['workflow_id']),
            trigger_data=serializer.validated_data.get('trigger_data'),
            target_object=target
        )

        if result.get('error'):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause a running instance"""
        instance = self.get_object()

        if instance.status not in ['running', 'waiting']:
            return Response(
                {'error': f'Cannot pause instance with status {instance.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.status = 'paused'
        instance.save(update_fields=['status', 'last_activity_at'])

        return Response({'status': 'paused'})

    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Resume a paused/waiting instance"""
        instance = self.get_object()

        service = WorkflowEngineService(request.user)
        result = service.resume_workflow(
            str(instance.id),
            request.data.get('resume_data')
        )

        return Response(result)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an instance"""
        instance = self.get_object()

        if instance.status in ['completed', 'failed', 'cancelled']:
            return Response(
                {'error': f'Cannot cancel instance with status {instance.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.status = 'cancelled'
        instance.completed_at = timezone.now()
        instance.save(update_fields=['status', 'completed_at', 'last_activity_at'])

        WorkflowLog.objects.create(
            instance=instance,
            log_type='workflow_failed',
            message='Workflow cancelled by user'
        )

        return Response({'status': 'cancelled'})

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get instance logs"""
        instance = self.get_object()
        logs = instance.logs.all().order_by('created_at')

        return Response(WorkflowLogSerializer(logs, many=True).data)

    @action(detail=True, methods=['get'])
    def executions(self, request, pk=None):
        """Get node executions for instance"""
        instance = self.get_object()
        executions = instance.node_executions.all().order_by('created_at')

        return Response(WorkflowNodeExecutionSerializer(executions, many=True).data)


class WorkflowApprovalViewSet(viewsets.ModelViewSet):
    """ViewSet for workflow approvals"""

    serializer_class = WorkflowApprovalRequestSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return WorkflowApprovalRequest.objects.filter(
            approver=self.request.user
        ).order_by('-created_at')

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending approvals"""
        service = ApprovalService(request.user)
        approvals = service.get_pending_approvals()

        return Response(approvals)

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """Respond to an approval"""
        serializer = ApprovalResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ApprovalService(request.user)
        result = service.respond_to_approval(
            approval_id=pk,
            decision=serializer.validated_data['decision'],
            comment=serializer.validated_data.get('comment', '')
        )

        if result.get('error'):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(result)

    @action(detail=True, methods=['post'])
    def delegate(self, request, pk=None):
        """Delegate an approval"""
        serializer = DelegateApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ApprovalService(request.user)
        result = service.delegate_approval(
            approval_id=pk,
            delegate_to_id=str(serializer.validated_data['delegate_to_id']),
            reason=serializer.validated_data.get('reason', '')
        )

        return Response(result)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get approval history"""
        approvals = WorkflowApprovalRequest.objects.filter(
            Q(approver=request.user) |
            Q(delegated_to=request.user)
        ).exclude(status='pending').order_by('-responded_at')[:50]

        return Response(WorkflowApprovalRequestSerializer(approvals, many=True).data)


class WorkflowTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for workflow templates"""

    serializer_class = WorkflowTemplateSerializer
    permission_classes = [IsAuthenticated]
    queryset = WorkflowTemplate.objects.filter(is_active=True)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get templates grouped by category"""
        templates = self.get_queryset()

        by_category = {}
        for t in templates:
            if t.category not in by_category:
                by_category[t.category] = []
            by_category[t.category].append({
                'id': str(t.id),
                'name': t.name,
                'description': t.description,
                'use_count': t.use_count,
                'rating': float(t.rating)
            })

        return Response(by_category)

    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Create workflow from template"""
        serializer = CreateFromTemplateSerializer(data={
            'template_id': pk,
            **request.data
        })
        serializer.is_valid(raise_exception=True)

        template = self.get_object()

        # Create workflow from template
        workflow = WorkflowDefinition.objects.create(
            user=request.user,
            name=serializer.validated_data['name'],
            description=template.description,
            category=template.category,
            trigger_type=template.definition_data.get('trigger_type', 'manual'),
            trigger_config=template.definition_data.get('trigger_config', {}),
            entry_conditions=template.definition_data.get('entry_conditions', []),
            canvas_data=template.definition_data.get('canvas_data', {})
        )

        # Create nodes
        for node_data in template.definition_data.get('nodes', []):
            WorkflowNode.objects.create(
                workflow=workflow,
                node_id=node_data.get('node_id'),
                name=node_data.get('name'),
                node_type=node_data.get('node_type'),
                config=node_data.get('config', {}),
                position_x=node_data.get('position_x', 0),
                position_y=node_data.get('position_y', 0)
            )

        # Create connections
        for conn_data in template.definition_data.get('connections', []):
            WorkflowConnection.objects.create(
                workflow=workflow,
                source_node=conn_data.get('source_node'),
                target_node=conn_data.get('target_node'),
                condition=conn_data.get('condition', {}),
                label=conn_data.get('label', '')
            )

        # Update template usage
        template.use_count += 1
        template.save(update_fields=['use_count'])

        return Response({
            'workflow_id': str(workflow.id),
            'name': workflow.name,
            'from_template': template.name
        }, status=status.HTTP_201_CREATED)


class WorkflowTriggerView(APIView):
    """API endpoint for external workflow triggers"""

    permission_classes = [IsAuthenticated]

    def post(self, request, workflow_id):
        """Trigger a workflow via API"""
        service = WorkflowEngineService(request.user)

        result = service.start_workflow(
            workflow_id=workflow_id,
            trigger_data={
                'source': 'api',
                'data': request.data
            }
        )

        if result.get('error'):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_201_CREATED)
