"""
Unified API V1 ViewSets
Comprehensive REST API endpoints for all CRM resources
"""
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from contact_management.models import Contact
from lead_management.models import Lead
from opportunity_management.models import Opportunity
from task_management.models import Task

from .serializers import (
    BulkOperationSerializer,
    ContactDetailSerializer,
    ContactListSerializer,
    LeadDetailSerializer,
    LeadListSerializer,
    OpportunityDetailSerializer,
    OpportunityListSerializer,
    TaskDetailSerializer,
    TaskListSerializer,
)


class LeadViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Lead management

    list: Get all leads with filtering and search
    retrieve: Get a specific lead by ID
    create: Create a new lead
    update: Update a lead (PUT)
    partial_update: Partially update a lead (PATCH)
    destroy: Delete a lead
    """
    queryset = Lead.objects.select_related('assigned_to', 'owner').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'lead_source', 'assigned_to', 'owner']
    search_fields = ['first_name', 'last_name', 'email', 'company_name', 'phone']
    ordering_fields = ['created_at', 'updated_at', 'lead_score', 'estimated_value']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return LeadListSerializer
        return LeadDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Filter by query params
        status_filter = self.request.query_params.get('status', None)
        priority = self.request.query_params.get('priority', None)
        assigned_to_me = self.request.query_params.get('assigned_to_me', None)

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority:
            queryset = queryset.filter(priority=priority)
        if assigned_to_me == 'true':
            queryset = queryset.filter(assigned_to=user)

        return queryset

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update multiple leads"""
        serializer = BulkOperationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ids = serializer.validated_data['ids']
        action_type = serializer.validated_data['action']
        data = serializer.validated_data.get('data', {})

        leads = Lead.objects.filter(id__in=ids)

        if action_type == 'update':
            leads.update(**data, updated_at=timezone.now())
            return Response({'success': True, 'updated': leads.count()})
        elif action_type == 'delete':
            count = leads.count()
            leads.delete()
            return Response({'success': True, 'deleted': count})

        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def convert(self, request, _pk=None):
        """Convert lead to contact and opportunity"""
        lead = self.get_object()

        # Create contact
        contact = Contact.objects.create(
            first_name=lead.first_name,
            last_name=lead.last_name,
            email=lead.email,
            phone=lead.phone,
            company_name=lead.company_name,
            job_title=lead.job_title,
            contact_type='customer',
            assigned_to=lead.assigned_to,
            created_by=request.user
        )

        # Create opportunity if estimated value exists
        opportunity = None
        if lead.estimated_value:
            opportunity = Opportunity.objects.create(
                name=f"{lead.company_name} - {lead.first_name} {lead.last_name}",
                contact=contact,
                company_name=lead.company_name,
                amount=lead.estimated_value,
                probability=lead.probability,
                expected_close_date=timezone.now().date() + timezone.timedelta(days=30),
                assigned_to=lead.assigned_to,
                owner=request.user
            )

        # Update lead
        lead.status = 'converted'
        lead.converted_at = timezone.now()
        lead.save()

        return Response({
            'success': True,
            'contact_id': contact.id,
            'opportunity_id': opportunity.id if opportunity else None
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get lead statistics"""
        user = request.user
        queryset = self.get_queryset()

        stats = {
            'total': queryset.count(),
            'by_status': {},
            'by_priority': {},
            'assigned_to_me': queryset.filter(assigned_to=user).count(),
            'high_score': queryset.filter(lead_score__gte=75).count()
        }

        # Count by status
        for status_choice in Lead.LEAD_STATUS_CHOICES:
            status_key = status_choice[0]
            stats['by_status'][status_key] = queryset.filter(status=status_key).count()

        # Count by priority
        for priority_choice in Lead.PRIORITY_CHOICES:
            priority_key = priority_choice[0]
            stats['by_priority'][priority_key] = queryset.filter(priority=priority_key).count()

        return Response(stats)


class ContactViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Contact management
    """
    queryset = Contact.objects.select_related('assigned_to', 'created_by').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['contact_type', 'status', 'assigned_to']
    search_fields = ['first_name', 'last_name', 'email', 'company_name', 'phone', 'mobile']
    ordering_fields = ['created_at', 'updated_at', 'last_name', 'first_name']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ContactListSerializer
        return ContactDetailSerializer

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update multiple contacts"""
        serializer = BulkOperationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ids = serializer.validated_data['ids']
        action_type = serializer.validated_data['action']
        data = serializer.validated_data.get('data', {})

        contacts = Contact.objects.filter(id__in=ids)

        if action_type == 'update':
            contacts.update(**data, updated_at=timezone.now())
            return Response({'success': True, 'updated': contacts.count()})
        elif action_type == 'delete':
            count = contacts.count()
            contacts.delete()
            return Response({'success': True, 'deleted': count})

        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get contact statistics"""
        queryset = self.get_queryset()

        stats = {
            'total': queryset.count(),
            'by_type': {},
            'by_status': {}
        }

        for contact_type in Contact.CONTACT_TYPE_CHOICES:
            type_key = contact_type[0]
            stats['by_type'][type_key] = queryset.filter(contact_type=type_key).count()

        return Response(stats)


class OpportunityViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Opportunity management
    """
    queryset = Opportunity.objects.select_related('contact', 'assigned_to', 'owner').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['stage', 'assigned_to', 'owner']
    search_fields = ['name', 'company_name', 'contact__first_name', 'contact__last_name']
    ordering_fields = ['created_at', 'updated_at', 'amount', 'expected_close_date']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return OpportunityListSerializer
        return OpportunityDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Filter options
        stage = self.request.query_params.get('stage', None)
        assigned_to_me = self.request.query_params.get('assigned_to_me', None)

        if stage:
            queryset = queryset.filter(stage=stage)
        if assigned_to_me == 'true':
            queryset = queryset.filter(assigned_to=user)

        return queryset

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update multiple opportunities"""
        serializer = BulkOperationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ids = serializer.validated_data['ids']
        action_type = serializer.validated_data['action']
        data = serializer.validated_data.get('data', {})

        opportunities = Opportunity.objects.filter(id__in=ids)

        if action_type == 'update':
            opportunities.update(**data, updated_at=timezone.now())
            return Response({'success': True, 'updated': opportunities.count()})
        elif action_type == 'delete':
            count = opportunities.count()
            opportunities.delete()
            return Response({'success': True, 'deleted': count})

        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def pipeline(self, request):
        """Get opportunity pipeline statistics"""
        queryset = self.get_queryset()

        pipeline = {
            'total_value': 0,
            'total_weighted_value': 0,
            'by_stage': {}
        }

        for stage_choice in Opportunity.STAGE_CHOICES:
            stage_key = stage_choice[0]
            stage_opps = queryset.filter(stage=stage_key)

            stage_total = sum([float(opp.amount) for opp in stage_opps])
            stage_weighted = sum([float(opp.weighted_amount) for opp in stage_opps])

            pipeline['by_stage'][stage_key] = {
                'count': stage_opps.count(),
                'total_value': stage_total,
                'weighted_value': stage_weighted
            }

            pipeline['total_value'] += stage_total
            pipeline['total_weighted_value'] += stage_weighted

        return Response(pipeline)


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Task management
    """
    queryset = Task.objects.select_related('assigned_to', 'created_by').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'task_type', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'due_date', 'priority']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return TaskDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Filter options
        assigned_to_me = self.request.query_params.get('assigned_to_me', None)
        overdue = self.request.query_params.get('overdue', None)

        if assigned_to_me == 'true':
            queryset = queryset.filter(assigned_to=user)
        if overdue == 'true':
            queryset = queryset.filter(
                due_date__lt=timezone.now(),
                status__in=['pending', 'in_progress']
            )

        return queryset

    @action(detail=True, methods=['post'])
    def complete(self, request, _pk=None):
        """Mark task as completed"""
        task = self.get_object()
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()

        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get task statistics"""
        user = request.user
        queryset = self.get_queryset()

        stats = {
            'total': queryset.count(),
            'by_status': {},
            'assigned_to_me': queryset.filter(assigned_to=user).count(),
            'overdue': queryset.filter(
                due_date__lt=timezone.now(),
                status__in=['pending', 'in_progress']
            ).count()
        }

        for status_choice in Task.STATUS_CHOICES:
            status_key = status_choice[0]
            stats['by_status'][status_key] = queryset.filter(status=status_key).count()

        return Response(stats)
