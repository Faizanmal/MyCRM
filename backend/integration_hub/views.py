"""
Integration Hub Views
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Webhook, WebhookDelivery, ThirdPartyIntegration, IntegrationLog, APIEndpoint
from .serializers import (
    WebhookSerializer, WebhookDeliverySerializer, ThirdPartyIntegrationSerializer,
    IntegrationLogSerializer, APIEndpointSerializer
)
from .tasks import trigger_webhook, deliver_webhook, sync_third_party_integration


class WebhookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing webhooks
    """
    queryset = Webhook.objects.all()
    serializer_class = WebhookSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'is_active']
    search_fields = ['name', 'url']
    
    def perform_create(self, serializer):
        """Set the creator"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test a webhook with sample payload"""
        webhook = self.get_object()
        
        test_payload = {
            'event': 'test.webhook',
            'test': True,
            'timestamp': str(timezone.now())
        }
        
        # Trigger test delivery
        trigger_webhook.delay('test.webhook', test_payload)
        
        return Response({
            'message': 'Test webhook queued',
            'payload': test_payload
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def deliveries(self, request, pk=None):
        """Get delivery history for a webhook"""
        webhook = self.get_object()
        deliveries = webhook.deliveries.all()[:50]  # Last 50 deliveries
        
        serializer = WebhookDeliverySerializer(deliveries, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a webhook"""
        webhook = self.get_object()
        webhook.is_active = True
        webhook.status = 'active'
        webhook.save()
        
        return Response({'message': 'Webhook activated'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a webhook"""
        webhook = self.get_object()
        webhook.is_active = False
        webhook.status = 'inactive'
        webhook.save()
        
        return Response({'message': 'Webhook deactivated'})


class WebhookDeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing webhook deliveries
    """
    queryset = WebhookDelivery.objects.all()
    serializer_class = WebhookDeliverySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['webhook', 'status', 'event']
    ordering_fields = ['created_at', 'delivered_at']
    ordering = ['-created_at']


class ThirdPartyIntegrationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing third-party integrations
    """
    queryset = ThirdPartyIntegration.objects.all()
    serializer_class = ThirdPartyIntegrationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['provider', 'status', 'is_active']
    search_fields = ['name']
    
    def perform_create(self, serializer):
        """Set the creator"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Trigger sync with third-party service"""
        integration = self.get_object()
        
        # Queue sync task
        sync_third_party_integration.delay(str(integration.id))
        
        return Response({
            'message': 'Sync queued',
            'integration': integration.name
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test integration connection"""
        integration = self.get_object()
        
        # Test based on provider
        try:
            if integration.provider == 'slack':
                # Test Slack connection
                result = test_slack_connection(integration)
            elif integration.provider == 'google_calendar':
                # Test Google Calendar connection
                result = test_google_calendar_connection(integration)
            else:
                return Response({
                    'error': f'Test not implemented for {integration.provider}'
                }, status=status.HTTP_501_NOT_IMPLEMENTED)
            
            return Response({
                'message': 'Connection test successful',
                'result': result
            })
        
        except Exception as e:
            return Response({
                'error': f'Connection test failed: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get integration activity logs"""
        integration = self.get_object()
        logs = integration.logs.all()[:50]
        
        serializer = IntegrationLogSerializer(logs, many=True)
        return Response(serializer.data)


class IntegrationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing integration logs
    """
    queryset = IntegrationLog.objects.all()
    serializer_class = IntegrationLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['integration', 'action', 'success']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class APIEndpointViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing custom API endpoints
    """
    queryset = APIEndpoint.objects.all()
    serializer_class = APIEndpointSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'path']
    
    def perform_create(self, serializer):
        """Set the creator"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test custom endpoint"""
        endpoint = self.get_object()
        
        # Execute endpoint handler
        try:
            if endpoint.handler_type == 'webhook':
                # Forward to webhook URL
                import requests
                response = requests.post(
                    endpoint.handler_url,
                    json=request.data,
                    timeout=30
                )
                return Response({
                    'status_code': response.status_code,
                    'response': response.text[:500]
                })
            
            elif endpoint.handler_type == 'function':
                # Execute Python code (DANGEROUS - need sandboxing in production)
                return Response({
                    'error': 'Function execution not yet implemented'
                }, status=status.HTTP_501_NOT_IMPLEMENTED)
        
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


def test_slack_connection(integration):
    """Test Slack integration"""
    # Placeholder
    return {'status': 'ok', 'message': 'Slack connection test not implemented'}


def test_google_calendar_connection(integration):
    """Test Google Calendar integration"""
    # Placeholder
    return {'status': 'ok', 'message': 'Google Calendar connection test not implemented'}
