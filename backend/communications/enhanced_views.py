"""
Enhanced Communication Hub Views
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .enhanced_models import (
    UnifiedInboxMessage,
    InboxLabel,
    MultiChannelCampaign,
    CampaignStep,
    CampaignRecipient,
    AdvancedEmailTracking,
    EmailTrackingEvent,
    CommunicationPreference
)
from .enhanced_serializers import (
    UnifiedInboxMessageSerializer,
    UnifiedInboxMessageListSerializer,
    InboxLabelSerializer,
    MultiChannelCampaignSerializer,
    MultiChannelCampaignListSerializer,
    CampaignStepSerializer,
    CampaignRecipientSerializer,
    AdvancedEmailTrackingSerializer,
    AdvancedEmailTrackingListSerializer,
    EmailTrackingEventSerializer,
    CommunicationPreferenceSerializer,
    InboxSearchSerializer,
    BulkUpdateStatusSerializer,
    ApplyLabelSerializer,
    SnoozeMessageSerializer,
    CreateCampaignSerializer,
    AddCampaignStepSerializer,
    ABTestSerializer,
    CreateTrackingSerializer,
    RecordEventSerializer,
    UnsubscribeSerializer
)
from .enhanced_services import (
    UnifiedInboxService,
    MultiChannelCampaignService,
    EmailTrackingService,
    CommunicationPreferenceService
)


class UnifiedInboxViewSet(viewsets.ModelViewSet):
    """ViewSet for unified inbox messages"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UnifiedInboxMessage.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UnifiedInboxMessageListSerializer
        return UnifiedInboxMessageSerializer
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get inbox summary"""
        service = UnifiedInboxService(request.user)
        summary = service.get_inbox_summary()
        return Response(summary)
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Search inbox with filters"""
        serializer = InboxSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = UnifiedInboxService(request.user)
        results = service.search_inbox(**serializer.validated_data)
        
        return Response({
            'count': len(results),
            'results': results
        })
    
    @action(detail=False, methods=['post'])
    def bulk_update_status(self, request):
        """Bulk update message status"""
        serializer = BulkUpdateStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = UnifiedInboxService(request.user)
        result = service.bulk_update_status(
            message_ids=[str(m) for m in serializer.validated_data['message_ids']],
            status=serializer.validated_data['status']
        )
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def apply_label(self, request):
        """Apply or remove label from messages"""
        serializer = ApplyLabelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = UnifiedInboxService(request.user)
        result = service.apply_label(
            message_ids=[str(m) for m in serializer.validated_data['message_ids']],
            label=serializer.validated_data['label'],
            remove=serializer.validated_data.get('remove', False)
        )
        
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def snooze(self, request, pk=None):
        """Snooze a message"""
        serializer = SnoozeMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = UnifiedInboxService(request.user)
        result = service.snooze_message(
            message_id=pk,
            snooze_until=serializer.validated_data['snooze_until']
        )
        
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def thread(self, request, pk=None):
        """Get all messages in a thread"""
        message = self.get_object()
        
        if not message.thread_id:
            return Response([UnifiedInboxMessageSerializer(message).data])
        
        service = UnifiedInboxService(request.user)
        thread = service.get_thread(message.thread_id)
        
        return Response(thread)
    
    @action(detail=True, methods=['post'])
    def link_crm(self, request, pk=None):
        """Link message to CRM objects"""
        service = UnifiedInboxService(request.user)
        result = service.link_to_crm(
            message_id=pk,
            contact_id=request.data.get('contact_id'),
            lead_id=request.data.get('lead_id'),
            opportunity_id=request.data.get('opportunity_id')
        )
        
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def generate_reply(self, request, pk=None):
        """Generate AI-suggested reply"""
        service = UnifiedInboxService(request.user)
        result = service.generate_ai_reply(message_id=pk)
        
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def star(self, request, pk=None):
        """Toggle star status"""
        message = self.get_object()
        message.is_starred = not message.is_starred
        message.save(update_fields=['is_starred'])
        
        return Response({'is_starred': message.is_starred})


class InboxLabelViewSet(viewsets.ModelViewSet):
    """ViewSet for inbox labels"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = InboxLabelSerializer
    
    def get_queryset(self):
        return InboxLabel.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MultiChannelCampaignViewSet(viewsets.ModelViewSet):
    """ViewSet for multi-channel campaigns"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MultiChannelCampaign.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MultiChannelCampaignListSerializer
        return MultiChannelCampaignSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def create_campaign(self, request):
        """Create a new campaign with initial setup"""
        serializer = CreateCampaignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = MultiChannelCampaignService(request.user)
        result = service.create_campaign(**serializer.validated_data)
        
        return Response(result, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def add_step(self, request, pk=None):
        """Add a step to the campaign"""
        serializer = AddCampaignStepSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = MultiChannelCampaignService(request.user)
        result = service.add_campaign_step(
            campaign_id=pk,
            **serializer.validated_data
        )
        
        return Response(result, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def reorder_steps(self, request, pk=None):
        """Reorder campaign steps"""
        step_orders = request.data.get('step_orders', {})
        
        service = MultiChannelCampaignService(request.user)
        result = service.update_step_order(pk, step_orders)
        
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start the campaign"""
        service = MultiChannelCampaignService(request.user)
        result = service.start_campaign(pk)
        
        if 'error' in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause the campaign"""
        service = MultiChannelCampaignService(request.user)
        result = service.pause_campaign(pk)
        
        if 'error' in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get campaign analytics"""
        service = MultiChannelCampaignService(request.user)
        analytics = service.get_campaign_analytics(pk)
        
        return Response(analytics)
    
    @action(detail=True, methods=['post'], url_path='steps/(?P<step_id>[^/.]+)/ab-test')
    def setup_ab_test(self, request, pk=None, step_id=None):
        """Set up A/B test for a step"""
        serializer = ABTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = MultiChannelCampaignService(request.user)
        result = service.ab_test_step(
            campaign_id=pk,
            step_id=step_id,
            variants=serializer.validated_data['variants']
        )
        
        return Response(result)


class CampaignStepViewSet(viewsets.ModelViewSet):
    """ViewSet for campaign steps"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = CampaignStepSerializer
    
    def get_queryset(self):
        return CampaignStep.objects.filter(campaign__user=self.request.user)


class CampaignRecipientViewSet(viewsets.ModelViewSet):
    """ViewSet for campaign recipients"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = CampaignRecipientSerializer
    
    def get_queryset(self):
        return CampaignRecipient.objects.filter(campaign__user=self.request.user)
    
    def get_queryset(self):
        queryset = CampaignRecipient.objects.filter(
            campaign__user=self.request.user
        )
        
        campaign_id = self.request.query_params.get('campaign_id')
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset


class EmailTrackingViewSet(viewsets.ModelViewSet):
    """ViewSet for email tracking"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AdvancedEmailTracking.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AdvancedEmailTrackingListSerializer
        return AdvancedEmailTrackingSerializer
    
    @action(detail=False, methods=['post'])
    def create_tracking(self, request):
        """Create tracking for an email"""
        serializer = CreateTrackingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = EmailTrackingService(request.user)
        result = service.create_tracking(**serializer.validated_data)
        
        return Response(result, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def record_event(self, request, pk=None):
        """Record a tracking event"""
        tracking = self.get_object()
        
        serializer = RecordEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = EmailTrackingService(request.user)
        result = service.record_event(
            tracking_id=tracking.tracking_id,
            **serializer.validated_data
        )
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get email engagement analytics"""
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        
        from datetime import datetime
        
        if from_date:
            from_date = datetime.fromisoformat(from_date)
        if to_date:
            to_date = datetime.fromisoformat(to_date)
        
        service = EmailTrackingService(request.user)
        analytics = service.get_engagement_analytics(from_date, to_date)
        
        return Response(analytics)
    
    @action(detail=False, methods=['get'])
    def unsubscribe_risk(self, request):
        """Get unsubscribe risk for a contact"""
        contact_id = request.query_params.get('contact_id')
        
        if not contact_id:
            return Response(
                {'error': 'contact_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = EmailTrackingService(request.user)
        result = service.predict_unsubscribe_risk(contact_id)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def best_send_time(self, request):
        """Get best send time analysis"""
        contact_id = request.query_params.get('contact_id')
        
        service = EmailTrackingService(request.user)
        result = service.get_best_send_time(contact_id)
        
        return Response(result)


class TrackingPixelView(viewsets.ViewSet):
    """Public endpoint for tracking pixels"""
    
    permission_classes = []  # No auth required for tracking
    
    @action(detail=True, methods=['get'], url_path='open')
    def track_open(self, request, pk=None):
        """Track email open via pixel"""
        from .enhanced_models import AdvancedEmailTracking
        from .enhanced_services import EmailTrackingService
        from django.http import HttpResponse
        import base64
        
        # 1x1 transparent GIF
        PIXEL = base64.b64decode(
            'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
        )
        
        try:
            tracking = AdvancedEmailTracking.objects.get(tracking_id=pk)
            
            # Record event
            device_info = {
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'device_type': 'unknown',
                'browser': 'unknown',
                'os': 'unknown'
            }
            
            location_info = {
                'ip': request.META.get('REMOTE_ADDR')
            }
            
            service = EmailTrackingService(tracking.user)
            service.record_event(
                tracking_id=pk,
                event_type='opened',
                device_info=device_info,
                location_info=location_info
            )
        except AdvancedEmailTracking.DoesNotExist:
            pass
        
        return HttpResponse(PIXEL, content_type='image/gif')
    
    @action(detail=True, methods=['get'], url_path='click')
    def track_click(self, request, pk=None):
        """Track email click"""
        from .enhanced_models import AdvancedEmailTracking
        from .enhanced_services import EmailTrackingService
        from django.http import HttpResponseRedirect
        
        url = request.query_params.get('url', '/')
        
        try:
            tracking = AdvancedEmailTracking.objects.get(tracking_id=pk)
            
            device_info = {
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
            
            location_info = {
                'ip': request.META.get('REMOTE_ADDR')
            }
            
            service = EmailTrackingService(tracking.user)
            service.record_event(
                tracking_id=pk,
                event_type='clicked',
                url=url,
                device_info=device_info,
                location_info=location_info
            )
        except AdvancedEmailTracking.DoesNotExist:
            pass
        
        return HttpResponseRedirect(url)


class CommunicationPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for communication preferences"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = CommunicationPreferenceSerializer
    
    def get_queryset(self):
        return CommunicationPreference.objects.all()
    
    @action(detail=False, methods=['get'])
    def for_contact(self, request):
        """Get preferences for a contact"""
        contact_id = request.query_params.get('contact_id')
        
        if not contact_id:
            return Response(
                {'error': 'contact_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = CommunicationPreferenceService()
        result = service.get_or_create_preferences(contact_id)
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def unsubscribe(self, request):
        """Handle unsubscribe request"""
        serializer = UnsubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = CommunicationPreferenceService()
        result = service.handle_unsubscribe(**serializer.validated_data)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def engagement_patterns(self, request):
        """Get engagement patterns for a contact"""
        contact_id = request.query_params.get('contact_id')
        
        if not contact_id:
            return Response(
                {'error': 'contact_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = CommunicationPreferenceService()
        result = service.analyze_engagement_patterns(contact_id)
        
        return Response(result)
