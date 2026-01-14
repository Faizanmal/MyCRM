"""
Mobile App Enhancement Models - Backend APIs for Mobile Features
"""

import uuid

from django.conf import settings
from django.db import models


class OfflineSyncQueue(models.Model):
    """Queue for offline sync operations"""

    OPERATION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]

    SYNC_STATUS = [
        ('pending', 'Pending'),
        ('syncing', 'Syncing'),
        ('synced', 'Synced'),
        ('conflict', 'Conflict'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sync_queue'
    )

    # Device info
    device_id = models.CharField(max_length=200)
    device_name = models.CharField(max_length=200, blank=True)
    platform = models.CharField(max_length=50)  # ios, android, web

    # Operation
    operation = models.CharField(max_length=20, choices=OPERATION_TYPES)
    entity_type = models.CharField(max_length=100)  # Contact, Lead, Task, etc.
    entity_id = models.CharField(max_length=200)

    # Data
    payload = models.JSONField()
    local_timestamp = models.DateTimeField()
    server_timestamp = models.DateTimeField(blank=True)

    # Sync status
    status = models.CharField(max_length=20, choices=SYNC_STATUS, default='pending')
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)

    # Conflict resolution
    conflict_data = models.JSONField(blank=True)
    resolution = models.CharField(max_length=50, blank=True)  # client_wins, server_wins, merged

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'offline_sync_queue'
        ordering = ['local_timestamp']
        indexes = [
            models.Index(fields=['user', 'device_id', 'status']),
            models.Index(fields=['entity_type', 'entity_id']),
        ]

    def __str__(self):
        return f"{self.operation} {self.entity_type}/{self.entity_id}"


class DeviceRegistration(models.Model):
    """Track registered mobile devices"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='devices'
    )

    device_id = models.CharField(max_length=200, unique=True)
    device_name = models.CharField(max_length=200)
    platform = models.CharField(max_length=50)  # ios, android
    os_version = models.CharField(max_length=50, blank=True)
    app_version = models.CharField(max_length=50, blank=True)

    # Push notifications
    push_token = models.TextField(blank=True)
    push_enabled = models.BooleanField(default=True)
    push_provider = models.CharField(max_length=50, blank=True)  # fcm, apns

    # Sync settings
    last_sync_at = models.DateTimeField(blank=True)
    sync_enabled = models.BooleanField(default=True)
    sync_interval_minutes = models.IntegerField(default=15)

    # Status
    is_active = models.BooleanField(default=True)
    last_active_at = models.DateTimeField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'device_registrations'

    def __str__(self):
        return f"{self.device_name} ({self.platform})"


class BusinessCardScan(models.Model):
    """Scanned business cards from mobile camera"""

    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('review', 'Needs Review'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='business_card_scans'
    )

    # Image
    image_url = models.URLField()
    image_key = models.CharField(max_length=500, blank=True)

    # OCR Results
    raw_text = models.TextField(blank=True)

    # Extracted data
    extracted_data = models.JSONField(default=dict)
    name = models.CharField(max_length=200, blank=True)
    title = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    mobile = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)

    # Confidence scores
    confidence_scores = models.JSONField(default=dict)
    overall_confidence = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')

    # Created contact/lead
    created_contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.SET_NULL,
        blank=True
    )
    created_lead = models.ForeignKey(
        'lead_management.Lead',
        on_delete=models.SET_NULL,
        blank=True
    )

    # Location where scanned
    scan_location = models.JSONField(blank=True)
    event_name = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'business_card_scans'
        ordering = ['-created_at']

    def __str__(self):
        return f"Card: {self.name or 'Unknown'} - {self.company or 'Unknown'}"


class LocationCheckIn(models.Model):
    """Track user check-ins at customer locations"""

    CHECK_IN_TYPES = [
        ('meeting', 'Meeting'),
        ('site_visit', 'Site Visit'),
        ('delivery', 'Delivery'),
        ('service_call', 'Service Call'),
        ('prospecting', 'Prospecting'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='location_checkins'
    )

    # Location
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    accuracy_meters = models.IntegerField(blank=True)

    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    # Check-in details
    check_in_type = models.CharField(max_length=30, choices=CHECK_IN_TYPES)
    notes = models.TextField(blank=True)

    # Photo documentation
    photos = models.JSONField(default=list)

    # Duration tracking
    check_in_time = models.DateTimeField()
    check_out_time = models.DateTimeField(blank=True)
    duration_minutes = models.IntegerField(blank=True)

    # Linked CRM objects
    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.SET_NULL,
        blank=True
    )
    lead = models.ForeignKey(
        'lead_management.Lead',
        on_delete=models.SET_NULL,
        blank=True
    )
    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.SET_NULL,
        blank=True
    )

    # Auto-created activity
    activity = models.ForeignKey(
        'activity_feed.Activity',
        on_delete=models.SET_NULL,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'location_checkins'
        ordering = ['-check_in_time']

    def __str__(self):
        return f"Check-in: {self.city or 'Unknown'} - {self.check_in_type}"


class NearbyCustomer(models.Model):
    """Cache of nearby customers for location-based features"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nearby_customers_cache'
    )

    # Reference location
    center_latitude = models.DecimalField(max_digits=10, decimal_places=8)
    center_longitude = models.DecimalField(max_digits=11, decimal_places=8)
    radius_km = models.DecimalField(max_digits=6, decimal_places=2)

    # Cached results
    customers = models.JSONField(default=list)
    leads = models.JSONField(default=list)

    # Cache metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'nearby_customers_cache'

    def __str__(self):
        return f"Nearby cache at ({self.center_latitude}, {self.center_longitude})"


class MobileActivityLog(models.Model):
    """Log of mobile app activities for analytics"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mobile_activity_logs'
    )

    device_id = models.CharField(max_length=200)

    # Activity
    action = models.CharField(max_length=100)
    screen = models.CharField(max_length=100, blank=True)
    entity_type = models.CharField(max_length=100, blank=True)
    entity_id = models.CharField(max_length=200, blank=True)

    # Context
    metadata = models.JSONField(default=dict)

    # Location (optional)
    latitude = models.DecimalField(
        max_digits=10, decimal_places=8, blank=True
    )
    longitude = models.DecimalField(
        max_digits=11, decimal_places=8, blank=True
    )

    # Connection status
    is_offline = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mobile_activity_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} by {self.user}"


class VoiceNote(models.Model):
    """Voice notes recorded on mobile"""

    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('transcribed', 'Transcribed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='voice_notes'
    )

    # Audio file
    audio_url = models.URLField()
    audio_key = models.CharField(max_length=500, blank=True)
    duration_seconds = models.IntegerField()
    format = models.CharField(max_length=20, default='m4a')

    # Transcription
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    transcription = models.TextField(blank=True)

    # AI Analysis
    summary = models.TextField(blank=True)
    action_items = models.JSONField(default=list)
    entities = models.JSONField(default=list)  # Extracted entities

    # Context
    title = models.CharField(max_length=200, blank=True)

    # Linked CRM objects
    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.SET_NULL,
        blank=True
    )
    lead = models.ForeignKey(
        'lead_management.Lead',
        on_delete=models.SET_NULL,
        blank=True
    )
    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.SET_NULL,
        blank=True
    )

    # Created tasks
    created_tasks = models.JSONField(default=list)

    # Location
    recorded_location = models.JSONField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'voice_notes'
        ordering = ['-created_at']

    def __str__(self):
        return f"Voice Note: {self.title or 'Untitled'}"
