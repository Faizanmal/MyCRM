"""
Mobile App Enhancement Views
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .mobile_models import (
    BusinessCardScan,
    DeviceRegistration,
    LocationCheckIn,
    MobileActivityLog,
    OfflineSyncQueue,
    VoiceNote,
)
from .mobile_serializers import (
    BusinessCardScanListSerializer,
    BusinessCardScanSerializer,
    CheckInSerializer,
    DeviceRegistrationSerializer,
    FindNearbySerializer,
    GetPendingChangesSerializer,
    LocationCheckInListSerializer,
    LocationCheckInSerializer,
    MobileActivityLogSerializer,
    OfflineSyncQueueSerializer,
    ProcessCardSerializer,
    ProcessVoiceNoteSerializer,
    QueueSyncOperationSerializer,
    RegisterDeviceSerializer,
    ResolveConflictSerializer,
    RouteOptimizationSerializer,
    VoiceNoteListSerializer,
    VoiceNoteSerializer,
)
from .mobile_services import (
    BusinessCardScanService,
    LocationService,
    OfflineSyncService,
    VoiceNoteService,
)


class DeviceRegistrationViewSet(viewsets.ModelViewSet):
    """ViewSet for device registration"""

    permission_classes = [IsAuthenticated]
    serializer_class = DeviceRegistrationSerializer

    def get_queryset(self):
        return DeviceRegistration.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new device"""
        serializer = RegisterDeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = OfflineSyncService(request.user)
        result = service.register_device(**serializer.validated_data)

        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def update_push_token(self, request, pk=None):
        """Update push notification token"""
        device = self.get_object()

        device.push_token = request.data.get('push_token', '')
        device.push_enabled = request.data.get('push_enabled', True)
        device.save(update_fields=['push_token', 'push_enabled'])

        return Response({'updated': True})


class OfflineSyncViewSet(viewsets.ModelViewSet):
    """ViewSet for offline sync operations"""

    permission_classes = [IsAuthenticated]
    serializer_class = OfflineSyncQueueSerializer

    def get_queryset(self):
        return OfflineSyncQueue.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def get_pending_changes(self, request):
        """Get changes since last sync"""
        serializer = GetPendingChangesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = OfflineSyncService(request.user)
        result = service.get_pending_changes(**serializer.validated_data)

        return Response(result)

    @action(detail=False, methods=['post'])
    def queue_operation(self, request):
        """Queue an offline operation for sync"""
        serializer = QueueSyncOperationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = OfflineSyncService(request.user)
        result = service.queue_sync_operation(**serializer.validated_data)

        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def process_queue(self, request):
        """Process pending sync operations"""
        device_id = request.data.get('device_id')

        if not device_id:
            return Response(
                {'error': 'device_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = OfflineSyncService(request.user)
        result = service.process_sync_queue(device_id)

        return Response(result)

    @action(detail=False, methods=['post'])
    def resolve_conflict(self, request):
        """Resolve a sync conflict"""
        serializer = ResolveConflictSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = OfflineSyncService(request.user)
        result = service.resolve_conflict(**serializer.validated_data)

        return Response(result)

    @action(detail=False, methods=['get'])
    def conflicts(self, request):
        """Get all conflicts for a device"""
        device_id = request.query_params.get('device_id')

        queryset = self.get_queryset().filter(status='conflict')

        if device_id:
            queryset = queryset.filter(device_id=device_id)

        serializer = OfflineSyncQueueSerializer(queryset, many=True)
        return Response(serializer.data)


class BusinessCardScanViewSet(viewsets.ModelViewSet):
    """ViewSet for business card scans"""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BusinessCardScan.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return BusinessCardScanListSerializer
        return BusinessCardScanSerializer

    @action(detail=False, methods=['post'])
    def scan(self, request):
        """Process a new business card scan"""
        serializer = ProcessCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = BusinessCardScanService(request.user)
        result = service.process_card(**serializer.validated_data)

        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def create_contact(self, request, pk=None):
        """Create a contact from a scan"""
        service = BusinessCardScanService(request.user)
        result = service.create_contact_from_scan(
            scan_id=pk,
            overrides=request.data.get('overrides')
        )

        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def update_extracted(self, request, pk=None):
        """Update extracted data before creating contact"""
        scan = self.get_object()

        for field in ['name', 'title', 'company', 'email', 'phone',
                      'mobile', 'address', 'website', 'linkedin']:
            if field in request.data:
                setattr(scan, field, request.data[field])

        scan.save()

        serializer = BusinessCardScanSerializer(scan)
        return Response(serializer.data)


class LocationCheckInViewSet(viewsets.ModelViewSet):
    """ViewSet for location check-ins"""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LocationCheckIn.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return LocationCheckInListSerializer
        return LocationCheckInSerializer

    @action(detail=False, methods=['post'])
    def check_in(self, request):
        """Record a new check-in"""
        serializer = CheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = LocationService(request.user)
        result = service.check_in(**serializer.validated_data)

        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def check_out(self, request, pk=None):
        """Record check-out"""
        service = LocationService(request.user)
        result = service.check_out(pk)

        return Response(result)

    @action(detail=False, methods=['post'])
    def find_nearby(self, request):
        """Find nearby customers"""
        serializer = FindNearbySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = LocationService(request.user)
        result = service.find_nearby_customers(**serializer.validated_data)

        return Response(result)

    @action(detail=False, methods=['post'])
    def optimize_route(self, request):
        """Optimize route for multiple visits"""
        serializer = RouteOptimizationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = LocationService(request.user)
        result = service.get_route_optimization(**serializer.validated_data)

        return Response(result)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get check-in history"""
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        check_in_type = request.query_params.get('type')

        queryset = self.get_queryset()

        if from_date:
            queryset = queryset.filter(check_in_time__gte=from_date)
        if to_date:
            queryset = queryset.filter(check_in_time__lte=to_date)
        if check_in_type:
            queryset = queryset.filter(check_in_type=check_in_type)

        serializer = LocationCheckInSerializer(queryset[:100], many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get check-in statistics"""
        from django.db.models import Avg, Count, Sum

        queryset = self.get_queryset()

        stats = queryset.aggregate(
            total_checkins=Count('id'),
            avg_duration=Avg('duration_minutes'),
            total_duration=Sum('duration_minutes')
        )

        by_type = queryset.values('check_in_type').annotate(
            count=Count('id')
        )

        return Response({
            'total_checkins': stats['total_checkins'],
            'avg_duration_minutes': float(stats['avg_duration'] or 0),
            'total_duration_hours': float((stats['total_duration'] or 0) / 60),
            'by_type': list(by_type)
        })


class VoiceNoteViewSet(viewsets.ModelViewSet):
    """ViewSet for voice notes"""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VoiceNote.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return VoiceNoteListSerializer
        return VoiceNoteSerializer

    @action(detail=False, methods=['post'])
    def process(self, request):
        """Process a new voice note"""
        serializer = ProcessVoiceNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = VoiceNoteService(request.user)
        result = service.process_voice_note(**serializer.validated_data)

        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def transcription(self, request, pk=None):
        """Get transcription for a voice note"""
        note = self.get_object()

        return Response({
            'id': str(note.id),
            'transcription': note.transcription,
            'status': note.status
        })

    @action(detail=True, methods=['get'])
    def action_items(self, request, pk=None):
        """Get action items from a voice note"""
        note = self.get_object()

        return Response({
            'id': str(note.id),
            'action_items': note.action_items,
            'created_tasks': note.created_tasks
        })

    @action(detail=True, methods=['post'])
    def link_to(self, request, pk=None):
        """Link voice note to CRM objects"""
        note = self.get_object()

        if 'contact_id' in request.data:
            note.contact_id = request.data['contact_id']
        if 'lead_id' in request.data:
            note.lead_id = request.data['lead_id']
        if 'opportunity_id' in request.data:
            note.opportunity_id = request.data['opportunity_id']

        note.save()

        return Response({'linked': True})


class MobileActivityLogViewSet(viewsets.ModelViewSet):
    """ViewSet for mobile activity logs"""

    permission_classes = [IsAuthenticated]
    serializer_class = MobileActivityLogSerializer

    def get_queryset(self):
        return MobileActivityLog.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def log_batch(self, request):
        """Log multiple activities at once"""
        activities = request.data.get('activities', [])

        created = []
        for activity_data in activities:
            activity = MobileActivityLog.objects.create(
                user=request.user,
                **activity_data
            )
            created.append(str(activity.id))

        return Response({
            'logged': len(created),
            'activity_ids': created
        })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get activity summary"""
        from django.db.models import Count

        queryset = self.get_queryset()

        device_id = request.query_params.get('device_id')
        if device_id:
            queryset = queryset.filter(device_id=device_id)

        by_action = queryset.values('action').annotate(
            count=Count('id')
        ).order_by('-count')[:20]

        by_screen = queryset.values('screen').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        return Response({
            'total_activities': queryset.count(),
            'by_action': list(by_action),
            'by_screen': list(by_screen)
        })
