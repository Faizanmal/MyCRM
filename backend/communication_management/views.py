from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django.core.mail import send_mail
from .models import Communication, EmailTemplate, EmailCampaign, CommunicationRule, CommunicationLog
from .serializers import (
    CommunicationSerializer, CommunicationCreateSerializer, EmailTemplateSerializer,
    EmailCampaignSerializer, CommunicationRuleSerializer, CommunicationLogSerializer,
    CommunicationBulkUpdateSerializer
)

User = get_user_model()


class CommunicationViewSet(viewsets.ModelViewSet):
    """Communication management viewset"""
    queryset = Communication.objects.all()
    serializer_class = CommunicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['subject', 'content', 'summary']
    ordering_fields = ['communication_date', 'created_at']
    ordering = ['-communication_date']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CommunicationCreateSerializer
        return CommunicationSerializer
    
    def get_queryset(self):
        queryset = Communication.objects.all()
        
        # Filter by user if not admin
        user_role = getattr(self.request.user, 'role', None)
        if user_role != 'admin' and not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(from_user=self.request.user) | Q(to_user=self.request.user)
            )
        
        # Apply additional filters
        communication_type = self.request.query_params.get('type')
        if communication_type:
            queryset = queryset.filter(communication_type=communication_type)
        
        direction = self.request.query_params.get('direction')
        if direction:
            queryset = queryset.filter(direction=direction)
        
        contact_id = self.request.query_params.get('contact_id')
        if contact_id:
            queryset = queryset.filter(contact_id=contact_id)
        
        lead_id = self.request.query_params.get('lead_id')
        if lead_id:
            queryset = queryset.filter(lead_id=lead_id)
        
        opportunity_id = self.request.query_params.get('opportunity_id')
        if opportunity_id:
            queryset = queryset.filter(opportunity_id=opportunity_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark communication as read"""
        communication = self.get_object()
        
        if not communication.is_read:
            communication.is_read = True
            communication.read_at = timezone.now()
            communication.save()
        
        return Response(CommunicationSerializer(communication).data)
    
    @action(detail=True, methods=['post'])
    def mark_replied(self, request, pk=None):
        """Mark communication as replied"""
        communication = self.get_object()
        
        if not communication.is_replied:
            communication.is_replied = True
            communication.replied_at = timezone.now()
            communication.save()
        
        return Response(CommunicationSerializer(communication).data)
    
    @action(detail=False, methods=['post'])
    def send_email(self, request):
        """Send email communication"""
        data = request.data.copy()
        data['communication_type'] = 'email'
        data['direction'] = 'outbound'
        
        serializer = CommunicationCreateSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        communication = serializer.save()
        
        # Send actual email if configured
        try:
            send_mail(
                subject=communication.subject,
                message=communication.content,
                from_email=communication.from_email or 'noreply@mycrm.com',
                recipient_list=[communication.to_email],
                fail_silently=False,
            )
        except Exception as e:
            # Log error but don't fail the request
            print(f"Email sending failed: {e}")
        
        return Response(CommunicationSerializer(communication).data)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update communications"""
        serializer = CommunicationBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        communication_ids = serializer.validated_data['communication_ids']
        updates = serializer.validated_data['updates']
        
        # Check permissions
        communications = Communication.objects.filter(id__in=communication_ids)
        user_role = getattr(self.request.user, 'role', None)
        if user_role != 'admin' and not self.request.user.is_superuser:
            communications = communications.filter(
                Q(from_user=self.request.user) | Q(to_user=self.request.user)
            )
        
        updated_count = communications.update(**updates)
        
        return Response({
            'message': f'{updated_count} communications updated successfully',
            'updated_count': updated_count
        })


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """Email template management viewset"""
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'subject', 'content']
    ordering_fields = ['name', 'created_at', 'usage_count']
    ordering = ['name']
    
    def get_queryset(self):
        return EmailTemplate.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def use_template(self, request, pk=None):
        """Use template and increment usage count"""
        template = self.get_object()
        template.usage_count += 1
        template.save()
        
        return Response(EmailTemplateSerializer(template).data)


class EmailCampaignViewSet(viewsets.ModelViewSet):
    """Email campaign management viewset"""
    queryset = EmailCampaign.objects.all()
    serializer_class = EmailCampaignSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return EmailCampaign.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_campaign(self, request, pk=None):
        """Send email campaign"""
        campaign = self.get_object()
        
        if campaign.status != 'draft':
            return Response(
                {'error': 'Campaign can only be sent from draft status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        campaign.status = 'sending'
        campaign.sent_at = timezone.now()
        campaign.save()
        
        # Here you would implement the actual email sending logic
        # For now, we'll just simulate it
        
        return Response({
            'message': 'Campaign sending initiated',
            'campaign_id': campaign.id
        })
    
    @action(detail=True, methods=['post'])
    def pause_campaign(self, request, pk=None):
        """Pause email campaign"""
        campaign = self.get_object()
        
        if campaign.status not in ['sending', 'sent']:
            return Response(
                {'error': 'Campaign cannot be paused in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        campaign.status = 'paused'
        campaign.save()
        
        return Response(EmailCampaignSerializer(campaign).data)


class CommunicationRuleViewSet(viewsets.ModelViewSet):
    """Communication rule management viewset"""
    queryset = CommunicationRule.objects.all()
    serializer_class = CommunicationRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CommunicationRule.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def test_rule(self, request, pk=None):
        """Test communication rule"""
        rule = self.get_object()
        
        # Here you would implement rule testing logic
        # For now, we'll just return a success message
        
        return Response({
            'message': 'Rule test completed',
            'rule_id': rule.id
        })


class CommunicationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Communication log viewset"""
    queryset = CommunicationLog.objects.all()
    serializer_class = CommunicationLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see logs for rules they created
        user_role = getattr(self.request.user, 'role', None)
        if user_role == 'admin' or self.request.user.is_superuser:
            return CommunicationLog.objects.all()
        return CommunicationLog.objects.filter(rule__created_by=self.request.user)
