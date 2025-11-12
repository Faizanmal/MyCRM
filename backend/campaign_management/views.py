"""
Campaign Management Views
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Avg, Count, Q
from django_filters.rest_framework import DjangoFilterBackend

from .models import Campaign, CampaignSegment, CampaignRecipient, CampaignClick, EmailTemplate
from .serializers import (
    CampaignSerializer, CampaignSegmentSerializer, CampaignRecipientSerializer,
    CampaignClickSerializer, EmailTemplateSerializer, CampaignStatsSerializer
)
from .tasks import send_campaign_emails, process_campaign_segment


class CampaignViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing email campaigns
    """
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'campaign_type']
    search_fields = ['name', 'description', 'subject']
    ordering_fields = ['created_at', 'scheduled_at', 'open_rate']
    
    def perform_create(self, serializer):
        """Set the creator"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """Schedule a campaign"""
        campaign = self.get_object()
        
        if campaign.status not in ['draft', 'paused']:
            return Response(
                {'error': 'Can only schedule draft or paused campaigns'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        scheduled_at = request.data.get('scheduled_at')
        if not scheduled_at:
            return Response(
                {'error': 'scheduled_at is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        campaign.scheduled_at = scheduled_at
        campaign.status = 'scheduled'
        campaign.save()
        
        # Queue the campaign for sending
        send_campaign_emails.apply_async(
            args=[str(campaign.id)],
            eta=campaign.scheduled_at
        )
        
        return Response(
            {'message': 'Campaign scheduled successfully'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def send_now(self, request, pk=None):
        """Send campaign immediately"""
        campaign = self.get_object()
        
        if campaign.status not in ['draft', 'scheduled']:
            return Response(
                {'error': 'Campaign already sent or cannot be sent'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        campaign.status = 'running'
        campaign.started_at = timezone.now()
        campaign.save()
        
        # Queue for immediate sending
        send_campaign_emails.delay(str(campaign.id))
        
        return Response(
            {'message': 'Campaign is being sent'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause a running campaign"""
        campaign = self.get_object()
        
        if campaign.status != 'running':
            return Response(
                {'error': 'Can only pause running campaigns'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        campaign.status = 'paused'
        campaign.save()
        
        return Response(
            {'message': 'Campaign paused'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a scheduled campaign"""
        campaign = self.get_object()
        
        if campaign.status not in ['scheduled', 'paused']:
            return Response(
                {'error': 'Can only cancel scheduled or paused campaigns'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        campaign.status = 'cancelled'
        campaign.save()
        
        return Response(
            {'message': 'Campaign cancelled'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get detailed campaign analytics"""
        campaign = self.get_object()
        
        # Time-series data for opens/clicks
        recipients = campaign.recipients.all()
        
        analytics = {
            'overview': {
                'total_recipients': campaign.total_recipients,
                'sent': campaign.sent_count,
                'delivered': campaign.delivered_count,
                'opened': campaign.opened_count,
                'clicked': campaign.clicked_count,
                'bounced': campaign.bounced_count,
                'unsubscribed': campaign.unsubscribed_count,
                'open_rate': campaign.open_rate,
                'click_rate': campaign.click_rate,
                'bounce_rate': campaign.bounce_rate,
            },
            'engagement_timeline': self._get_engagement_timeline(recipients),
            'top_links': self._get_top_links(campaign),
            'device_breakdown': self._get_device_breakdown(recipients),
        }
        
        return Response(analytics)
    
    def _get_engagement_timeline(self, recipients):
        """Get engagement over time"""
        # Simplified - in production, group by hour/day
        return {
            'opens': recipients.filter(opened_at__isnull=False).count(),
            'clicks': recipients.filter(first_clicked_at__isnull=False).count(),
        }
    
    def _get_top_links(self, campaign):
        """Get most clicked links"""
        from django.db.models import Count
        clicks = CampaignClick.objects.filter(
            recipient__campaign=campaign
        ).values('url').annotate(
            click_count=Count('id')
        ).order_by('-click_count')[:10]
        
        return list(clicks)
    
    def _get_device_breakdown(self, recipients):
        """Parse user agents for device types"""
        # Simplified - in production, use user-agent parser
        return {
            'desktop': 0,
            'mobile': 0,
            'tablet': 0,
            'unknown': recipients.count()
        }
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get overall campaign statistics"""
        campaigns = self.get_queryset()
        
        total_campaigns = campaigns.count()
        active_campaigns = campaigns.filter(
            status__in=['running', 'scheduled']
        ).count()
        
        total_sent = campaigns.aggregate(total=Count('sent_count'))['total'] or 0
        avg_open = campaigns.aggregate(avg=Avg('opened_count'))['avg'] or 0
        avg_click = campaigns.aggregate(avg=Avg('clicked_count'))['avg'] or 0
        
        top_performing = campaigns.filter(
            status='completed'
        ).order_by('-opened_count')[:5]
        
        stats = {
            'total_campaigns': total_campaigns,
            'active_campaigns': active_campaigns,
            'total_sent': total_sent,
            'average_open_rate': round(avg_open, 2),
            'average_click_rate': round(avg_click, 2),
            'top_performing': CampaignSerializer(top_performing, many=True).data
        }
        
        return Response(stats)


class CampaignSegmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing campaign segments
    """
    queryset = CampaignSegment.objects.all()
    serializer_class = CampaignSegmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'contact_count']
    
    def perform_create(self, serializer):
        """Set the creator and calculate contact count"""
        segment = serializer.save(created_by=self.request.user)
        # Queue segment processing
        process_campaign_segment.delay(str(segment.id))
    
    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        """Refresh segment contact count"""
        segment = self.get_object()
        process_campaign_segment.delay(str(segment.id))
        
        return Response(
            {'message': 'Segment refresh queued'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """Preview contacts in segment"""
        segment = self.get_object()
        
        # Apply filters to get contacts/leads
        from contact_management.models import Contact
        from lead_management.models import Lead
        
        contacts = Contact.objects.all()
        leads = Lead.objects.all()
        
        # Apply filters from segment.filters
        # Simplified - in production, build dynamic queries
        
        return Response({
            'contacts': contacts[:10].values('id', 'email', 'first_name', 'last_name'),
            'leads': leads[:10].values('id', 'email', 'name'),
            'total_count': contacts.count() + leads.count()
        })


class CampaignRecipientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing campaign recipients
    """
    queryset = CampaignRecipient.objects.all()
    serializer_class = CampaignRecipientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['campaign', 'status']
    ordering_fields = ['sent_at', 'opened_at', 'clicked_at']


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing email templates
    """
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    
    def perform_create(self, serializer):
        """Set the creator"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a template"""
        template = self.get_object()
        
        new_template = EmailTemplate.objects.create(
            name=f"{template.name} (Copy)",
            description=template.description,
            category=template.category,
            subject=template.subject,
            content_html=template.content_html,
            content_text=template.content_text,
            variables=template.variables,
            created_by=request.user
        )
        
        serializer = self.get_serializer(new_template)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
