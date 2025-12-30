"""
Progressive Web App (PWA) Views
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .pwa_models import (
    PushSubscription,
    PushNotification,
    BackgroundSyncJob,
    CacheManifest,
    OfflineAction,
    InstallationAnalytics
)
from .pwa_serializers import (
    PushSubscriptionSerializer,
    PushNotificationSerializer,
    PushNotificationListSerializer,
    BackgroundSyncJobSerializer,
    CacheManifestSerializer,
    OfflineActionSerializer,
    InstallationAnalyticsSerializer,
    SubscribePushSerializer,
    UpdatePreferencesSerializer,
    SendNotificationSerializer,
    RequestSyncSerializer,
    QueueOfflineActionSerializer,
    TrackInstallationSerializer
)
from .pwa_services import (
    PushNotificationService,
    BackgroundSyncService,
    OfflineActionService,
    PWAAnalyticsService,
    CacheManagementService
)


class PushSubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for push subscriptions"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = PushSubscriptionSerializer
    
    def get_queryset(self):
        return PushSubscription.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        """Subscribe to push notifications"""
        serializer = SubscribePushSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = PushNotificationService(request.user)
        result = service.subscribe(**serializer.validated_data)
        
        return Response(result, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def unsubscribe(self, request):
        """Unsubscribe from push notifications"""
        endpoint = request.data.get('endpoint')
        
        if not endpoint:
            return Response(
                {'error': 'endpoint required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = PushNotificationService(request.user)
        result = service.unsubscribe(endpoint)
        
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def update_preferences(self, request, pk=None):
        """Update notification preferences"""
        serializer = UpdatePreferencesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = PushNotificationService(request.user)
        result = service.update_preferences(
            subscription_id=pk,
            preferences=serializer.validated_data
        )
        
        return Response(result)


class PushNotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for push notifications"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PushNotification.objects.filter(
            subscription__user=self.request.user
        )
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PushNotificationListSerializer
        return PushNotificationSerializer
    
    @action(detail=False, methods=['post'])
    def send(self, request):
        """Send a push notification"""
        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get target user (self or specified)
        target_user_id = request.data.get('user_id')
        if target_user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            target_user = User.objects.get(id=target_user_id)
        else:
            target_user = request.user
        
        service = PushNotificationService()
        result = service.send_notification(
            user=target_user,
            **serializer.validated_data
        )
        
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def delivered(self, request, pk=None):
        """Mark notification as delivered"""
        service = PushNotificationService()
        result = service.track_delivery(pk)
        
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def clicked(self, request, pk=None):
        """Mark notification as clicked"""
        service = PushNotificationService()
        result = service.track_click(pk)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get notification history"""
        queryset = self.get_queryset().order_by('-created_at')[:100]
        serializer = PushNotificationListSerializer(queryset, many=True)
        return Response(serializer.data)


class BackgroundSyncViewSet(viewsets.ModelViewSet):
    """ViewSet for background sync jobs"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = BackgroundSyncJobSerializer
    
    def get_queryset(self):
        return BackgroundSyncJob.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def request_sync(self, request):
        """Request a background sync"""
        serializer = RequestSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = BackgroundSyncService(request.user)
        result = service.request_sync(**serializer.validated_data)
        
        return Response(result, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process a sync job"""
        service = BackgroundSyncService(request.user)
        result = service.process_sync_job(pk)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending sync jobs"""
        service = BackgroundSyncService(request.user)
        jobs = service.get_pending_jobs()
        
        return Response(jobs)
    
    @action(detail=False, methods=['post'])
    def process_all(self, request):
        """Process all pending sync jobs"""
        service = BackgroundSyncService(request.user)
        pending = service.get_pending_jobs()
        
        results = []
        for job in pending:
            result = service.process_sync_job(job['job_id'])
            results.append(result)
        
        return Response({
            'processed': len(results),
            'results': results
        })


class OfflineActionViewSet(viewsets.ModelViewSet):
    """ViewSet for offline actions"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = OfflineActionSerializer
    
    def get_queryset(self):
        return OfflineAction.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def queue(self, request):
        """Queue an offline action"""
        serializer = QueueOfflineActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = OfflineActionService(request.user)
        result = service.queue_action(**serializer.validated_data)
        
        return Response(result, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def queue_batch(self, request):
        """Queue multiple offline actions"""
        actions = request.data.get('actions', [])
        
        service = OfflineActionService(request.user)
        results = []
        
        for action_data in actions:
            serializer = QueueOfflineActionSerializer(data=action_data)
            serializer.is_valid(raise_exception=True)
            result = service.queue_action(**serializer.validated_data)
            results.append(result)
        
        return Response({
            'queued': len(results),
            'results': results
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def process(self, request):
        """Process all queued actions"""
        service = OfflineActionService(request.user)
        result = service.process_queued_actions()
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending actions"""
        service = OfflineActionService(request.user)
        actions = service.get_pending_actions()
        
        return Response(actions)
    
    @action(detail=False, methods=['get'])
    def conflicts(self, request):
        """Get actions with conflicts"""
        queryset = self.get_queryset().filter(status='conflict')
        serializer = OfflineActionSerializer(queryset, many=True)
        
        return Response(serializer.data)


class PWAAnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for PWA analytics"""
    
    permission_classes = [AllowAny]  # Some endpoints need to work without auth
    
    @action(detail=False, methods=['post'])
    def track(self, request):
        """Track PWA installation events"""
        serializer = TrackInstallationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        user = request.user if request.user.is_authenticated else None
        
        service = PWAAnalyticsService()
        event = data['event']
        
        if event == 'prompt_shown':
            result = service.track_prompt_shown(
                platform=data['platform'],
                browser=data['browser'],
                user=user
            )
        elif event in ['prompt_accepted', 'prompt_dismissed']:
            result = service.track_prompt_response(
                platform=data['platform'],
                browser=data['browser'],
                accepted=(event == 'prompt_accepted'),
                user=user
            )
        elif event == 'installed':
            result = service.track_installation(
                platform=data['platform'],
                browser=data['browser'],
                install_source=data.get('install_source', 'browser_prompt'),
                user=user
            )
        elif event == 'standalone_launch':
            result = service.track_standalone_launch(
                platform=data['platform'],
                browser=data['browser'],
                user=user
            )
        else:
            result = {'tracked': False}
        
        return Response(result)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def stats(self, request):
        """Get installation statistics"""
        service = PWAAnalyticsService()
        stats = service.get_installation_stats()
        
        return Response(stats)


class CacheManifestViewSet(viewsets.ModelViewSet):
    """ViewSet for cache manifest management"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = CacheManifestSerializer
    queryset = CacheManifest.objects.all()
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def manifest(self, request):
        """Get cache manifest for service worker"""
        service = CacheManagementService()
        manifest = service.get_cache_manifest()
        
        return Response(manifest)
    
    @action(detail=False, methods=['post'])
    def update_version(self, request):
        """Update cache version"""
        version = request.data.get('version')
        
        if not version:
            return Response(
                {'error': 'version required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = CacheManagementService()
        result = service.update_cache_version(version)
        
        return Response(result)


class ServiceWorkerConfigView(viewsets.ViewSet):
    """Endpoint for service worker configuration"""
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def config(self, request):
        """Get service worker configuration"""
        from django.conf import settings
        
        config = {
            'vapid_public_key': getattr(settings, 'VAPID_PUBLIC_KEY', ''),
            'cache_version': self._get_cache_version(),
            'api_base_url': '/api/',
            'offline_page': '/offline',
            'precache_urls': [
                '/',
                '/dashboard',
                '/contacts',
                '/leads',
                '/opportunities',
                '/tasks',
            ],
            'cache_strategies': {
                '/api/': 'network-first',
                '/static/': 'cache-first',
                '/media/': 'stale-while-revalidate',
            }
        }
        
        return Response(config)
    
    def _get_cache_version(self) -> str:
        """Get current cache version"""
        service = CacheManagementService()
        manifest = service.get_cache_manifest()
        return manifest.get('version', '1.0.0')
