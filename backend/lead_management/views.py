from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from .models import Lead, LeadActivity, LeadAssignmentRule, LeadConversion
from .serializers import (
    LeadSerializer, LeadCreateSerializer, LeadActivitySerializer,
    LeadAssignmentRuleSerializer, LeadConversionSerializer, LeadBulkUpdateSerializer
)

User = get_user_model()


class LeadViewSet(viewsets.ModelViewSet):
    """Lead management viewset"""
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'company_name', 'phone']
    ordering_fields = ['first_name', 'last_name', 'email', 'company_name', 'created_at', 'lead_score']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LeadCreateSerializer
        return LeadSerializer
    
    def get_queryset(self):
        queryset = Lead.objects.all()
        
        # Filter by assigned user if not admin
        if self.request.user.role != 'admin':
            queryset = queryset.filter(
                Q(assigned_to=self.request.user) | Q(owner=self.request.user)
            )
        
        # Apply additional filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        priority_filter = self.request.query_params.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        source_filter = self.request.query_params.get('source')
        if source_filter:
            queryset = queryset.filter(lead_source=source_filter)
        
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def convert(self, request, pk=None):
        """Convert lead to opportunity"""
        lead = self.get_object()
        
        if lead.status == 'converted':
            return Response(
                {'error': 'Lead is already converted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create opportunity data from lead
        opportunity_data = {
            'name': f"{lead.first_name} {lead.last_name} - {lead.company_name}",
            'contact': None,  # Will be created or linked
            'company_name': lead.company_name,
            'stage': 'prospecting',
            'probability': lead.probability,
            'amount': lead.estimated_value or 0,
            'expected_close_date': timezone.now().date() + timezone.timedelta(days=30),
            'assigned_to': lead.assigned_to,
            'owner': lead.owner,
            'notes': f"Converted from lead: {lead.notes or ''}"
        }
        
        # Create opportunity (this would need to be implemented)
        # opportunity = Opportunity.objects.create(**opportunity_data)
        
        # Update lead status
        lead.status = 'converted'
        lead.converted_at = timezone.now()
        lead.save()
        
        # Create conversion record
        conversion = LeadConversion.objects.create(
            lead=lead,
            # opportunity=opportunity,
            converted_by=request.user,
            conversion_value=lead.estimated_value
        )
        
        return Response({
            'message': 'Lead converted successfully',
            'conversion_id': conversion.id
        })
    
    @action(detail=True, methods=['post'])
    def add_activity(self, request, pk=None):
        """Add activity to lead"""
        lead = self.get_object()
        
        serializer = LeadActivitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        activity = serializer.save(
            lead=lead,
            user=request.user
        )
        
        # Update last contact date if it's a contact activity
        if activity.activity_type in ['call', 'email', 'meeting']:
            lead.last_contact_date = timezone.now()
            lead.save()
        
        return Response(LeadActivitySerializer(activity).data)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update leads"""
        serializer = LeadBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        lead_ids = serializer.validated_data['lead_ids']
        updates = serializer.validated_data['updates']
        
        # Check permissions
        leads = Lead.objects.filter(id__in=lead_ids)
        if self.request.user.role != 'admin':
            leads = leads.filter(
                Q(assigned_to=self.request.user) | Q(owner=self.request.user)
            )
        
        updated_count = leads.update(**updates)
        
        return Response({
            'message': f'{updated_count} leads updated successfully',
            'updated_count': updated_count
        })
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """Bulk delete leads"""
        lead_ids = request.data.get('lead_ids', [])
        
        if not lead_ids:
            return Response(
                {'error': 'No lead IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check permissions
        leads = Lead.objects.filter(id__in=lead_ids)
        if self.request.user.role != 'admin':
            leads = leads.filter(
                Q(assigned_to=self.request.user) | Q(owner=self.request.user)
            )
        
        deleted_count = leads.count()
        leads.delete()
        
        return Response({
            'message': f'{deleted_count} leads deleted successfully',
            'deleted_count': deleted_count
        })


class LeadActivityViewSet(viewsets.ModelViewSet):
    """Lead activity management viewset"""
    queryset = LeadActivity.objects.all()
    serializer_class = LeadActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = LeadActivity.objects.all()
        
        # Filter by lead if specified
        lead_id = self.request.query_params.get('lead_id')
        if lead_id:
            queryset = queryset.filter(lead_id=lead_id)
        
        # Filter by user if not admin
        if self.request.user.role != 'admin':
            queryset = queryset.filter(
                Q(user=self.request.user) | Q(lead__assigned_to=self.request.user)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LeadAssignmentRuleViewSet(viewsets.ModelViewSet):
    """Lead assignment rule management viewset"""
    queryset = LeadAssignmentRule.objects.all()
    serializer_class = LeadAssignmentRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return LeadAssignmentRule.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class LeadConversionViewSet(viewsets.ReadOnlyModelViewSet):
    """Lead conversion tracking viewset"""
    queryset = LeadConversion.objects.all()
    serializer_class = LeadConversionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see conversions they made or for their leads
        if self.request.user.role == 'admin':
            return LeadConversion.objects.all()
        return LeadConversion.objects.filter(
            Q(converted_by=self.request.user) | 
            Q(lead__assigned_to=self.request.user)
        )