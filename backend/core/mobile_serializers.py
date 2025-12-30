"""
Mobile App Enhancement Serializers
"""

from rest_framework import serializers
from .mobile_models import (
    OfflineSyncQueue,
    DeviceRegistration,
    BusinessCardScan,
    LocationCheckIn,
    NearbyCustomer,
    MobileActivityLog,
    VoiceNote
)


class OfflineSyncQueueSerializer(serializers.ModelSerializer):
    """Serializer for offline sync queue items"""
    
    class Meta:
        model = OfflineSyncQueue
        fields = [
            'id', 'user', 'device_id', 'device_name', 'platform',
            'operation', 'entity_type', 'entity_id',
            'payload', 'local_timestamp', 'server_timestamp',
            'status', 'error_message', 'retry_count',
            'conflict_data', 'resolution',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'server_timestamp', 'status',
            'error_message', 'retry_count', 'conflict_data', 'resolution',
            'created_at', 'updated_at'
        ]


class DeviceRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for device registration"""
    
    class Meta:
        model = DeviceRegistration
        fields = [
            'id', 'user', 'device_id', 'device_name', 'platform',
            'os_version', 'app_version',
            'push_token', 'push_enabled', 'push_provider',
            'last_sync_at', 'sync_enabled', 'sync_interval_minutes',
            'is_active', 'last_active_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'last_sync_at', 'last_active_at',
            'created_at', 'updated_at'
        ]


class BusinessCardScanSerializer(serializers.ModelSerializer):
    """Serializer for business card scans"""
    
    class Meta:
        model = BusinessCardScan
        fields = [
            'id', 'user', 'image_url', 'image_key',
            'raw_text', 'extracted_data',
            'name', 'title', 'company', 'email', 'phone', 'mobile',
            'address', 'website', 'linkedin',
            'confidence_scores', 'overall_confidence',
            'status', 'created_contact', 'created_lead',
            'scan_location', 'event_name', 'notes',
            'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'raw_text', 'extracted_data',
            'confidence_scores', 'overall_confidence',
            'status', 'created_contact', 'created_lead', 'created_at'
        ]


class BusinessCardScanListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for scan list"""
    
    class Meta:
        model = BusinessCardScan
        fields = [
            'id', 'name', 'company', 'email',
            'overall_confidence', 'status', 'created_at'
        ]


class LocationCheckInSerializer(serializers.ModelSerializer):
    """Serializer for location check-ins"""
    
    class Meta:
        model = LocationCheckIn
        fields = [
            'id', 'user', 'latitude', 'longitude', 'accuracy_meters',
            'address', 'city', 'state', 'country', 'postal_code',
            'check_in_type', 'notes', 'photos',
            'check_in_time', 'check_out_time', 'duration_minutes',
            'contact', 'lead', 'opportunity', 'activity',
            'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'address', 'city', 'state', 'country',
            'postal_code', 'duration_minutes', 'activity', 'created_at'
        ]


class LocationCheckInListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for check-in list"""
    
    class Meta:
        model = LocationCheckIn
        fields = [
            'id', 'city', 'check_in_type',
            'check_in_time', 'duration_minutes'
        ]


class NearbyCustomerSerializer(serializers.ModelSerializer):
    """Serializer for nearby customers cache"""
    
    class Meta:
        model = NearbyCustomer
        fields = [
            'id', 'center_latitude', 'center_longitude', 'radius_km',
            'customers', 'leads', 'generated_at', 'expires_at'
        ]


class MobileActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for mobile activity logs"""
    
    class Meta:
        model = MobileActivityLog
        fields = [
            'id', 'user', 'device_id',
            'action', 'screen', 'entity_type', 'entity_id',
            'metadata', 'latitude', 'longitude', 'is_offline',
            'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class VoiceNoteSerializer(serializers.ModelSerializer):
    """Serializer for voice notes"""
    
    class Meta:
        model = VoiceNote
        fields = [
            'id', 'user', 'audio_url', 'audio_key',
            'duration_seconds', 'format',
            'status', 'transcription',
            'summary', 'action_items', 'entities',
            'title', 'contact', 'lead', 'opportunity',
            'created_tasks', 'recorded_location',
            'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'transcription',
            'summary', 'action_items', 'entities',
            'created_tasks', 'created_at'
        ]


class VoiceNoteListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for voice note list"""
    
    class Meta:
        model = VoiceNote
        fields = [
            'id', 'title', 'duration_seconds', 'status',
            'summary', 'created_at'
        ]


# Request Serializers

class RegisterDeviceSerializer(serializers.Serializer):
    """Serializer for device registration request"""
    
    device_id = serializers.CharField(max_length=200)
    device_name = serializers.CharField(max_length=200)
    platform = serializers.ChoiceField(choices=['ios', 'android', 'web'])
    os_version = serializers.CharField(max_length=50, required=False, allow_blank=True)
    app_version = serializers.CharField(max_length=50, required=False, allow_blank=True)
    push_token = serializers.CharField(required=False, allow_blank=True)
    push_provider = serializers.CharField(max_length=50, required=False, allow_blank=True)


class GetPendingChangesSerializer(serializers.Serializer):
    """Serializer for getting pending changes"""
    
    device_id = serializers.CharField(max_length=200)
    since_timestamp = serializers.DateTimeField(required=False)
    entity_types = serializers.ListField(
        child=serializers.CharField(), required=False
    )


class QueueSyncOperationSerializer(serializers.Serializer):
    """Serializer for queueing sync operations"""
    
    device_id = serializers.CharField(max_length=200)
    operation = serializers.ChoiceField(choices=['create', 'update', 'delete'])
    entity_type = serializers.CharField(max_length=100)
    entity_id = serializers.CharField(max_length=200)
    payload = serializers.DictField()
    local_timestamp = serializers.DateTimeField()


class ResolveConflictSerializer(serializers.Serializer):
    """Serializer for conflict resolution"""
    
    sync_id = serializers.UUIDField()
    resolution = serializers.ChoiceField(
        choices=['client_wins', 'server_wins', 'merged']
    )
    merged_data = serializers.DictField(required=False)


class ProcessCardSerializer(serializers.Serializer):
    """Serializer for processing business card"""
    
    image_url = serializers.URLField()
    scan_location = serializers.DictField(required=False)
    event_name = serializers.CharField(max_length=200, required=False, allow_blank=True)


class CreateContactFromScanSerializer(serializers.Serializer):
    """Serializer for creating contact from scan"""
    
    scan_id = serializers.UUIDField()
    overrides = serializers.DictField(required=False)


class CheckInSerializer(serializers.Serializer):
    """Serializer for location check-in"""
    
    latitude = serializers.DecimalField(max_digits=10, decimal_places=8)
    longitude = serializers.DecimalField(max_digits=11, decimal_places=8)
    check_in_type = serializers.ChoiceField(choices=[
        'meeting', 'site_visit', 'delivery', 'service_call', 'prospecting', 'other'
    ])
    accuracy_meters = serializers.IntegerField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
    photos = serializers.ListField(
        child=serializers.URLField(), required=False
    )
    contact_id = serializers.UUIDField(required=False)
    lead_id = serializers.UUIDField(required=False)
    opportunity_id = serializers.UUIDField(required=False)


class FindNearbySerializer(serializers.Serializer):
    """Serializer for finding nearby customers"""
    
    latitude = serializers.DecimalField(max_digits=10, decimal_places=8)
    longitude = serializers.DecimalField(max_digits=11, decimal_places=8)
    radius_km = serializers.DecimalField(
        max_digits=6, decimal_places=2, default=10
    )
    use_cache = serializers.BooleanField(default=True)


class RouteOptimizationSerializer(serializers.Serializer):
    """Serializer for route optimization"""
    
    locations = serializers.ListField(
        child=serializers.DictField()
    )
    start_location = serializers.DictField(required=False)


class ProcessVoiceNoteSerializer(serializers.Serializer):
    """Serializer for processing voice note"""
    
    audio_url = serializers.URLField()
    duration_seconds = serializers.IntegerField()
    format = serializers.CharField(max_length=20, default='m4a')
    title = serializers.CharField(max_length=200, required=False, allow_blank=True)
    contact_id = serializers.UUIDField(required=False)
    lead_id = serializers.UUIDField(required=False)
    opportunity_id = serializers.UUIDField(required=False)
    recorded_location = serializers.DictField(required=False)
