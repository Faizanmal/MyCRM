"""
Integration Hub Models
"""

import hashlib
import hmac
import uuid

from django.contrib.auth import get_user_model
from django.core.validators import URLValidator
from django.db import models
from django.utils import timezone

User = get_user_model()


class Webhook(models.Model):
    """Outgoing webhooks to notify external systems"""

    EVENT_CHOICES = [
        ('lead.created', 'Lead Created'),
        ('lead.updated', 'Lead Updated'),
        ('lead.deleted', 'Lead Deleted'),
        ('contact.created', 'Contact Created'),
        ('contact.updated', 'Contact Updated'),
        ('opportunity.created', 'Opportunity Created'),
        ('opportunity.updated', 'Opportunity Updated'),
        ('opportunity.won', 'Opportunity Won'),
        ('opportunity.lost', 'Opportunity Lost'),
        ('task.created', 'Task Created'),
        ('task.completed', 'Task Completed'),
        ('campaign.completed', 'Campaign Completed'),
        ('document.uploaded', 'Document Uploaded'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Target URL
    url = models.URLField(validators=[URLValidator()])

    # Events to trigger on
    events = models.JSONField(
        default=list,
        help_text="List of events to trigger webhook"
    )

    # Authentication
    secret_key = models.CharField(
        max_length=64,
        help_text="Secret key for HMAC signature verification"
    )

    # Headers
    custom_headers = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom HTTP headers to include"
    )

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)

    # Retry configuration
    max_retries = models.IntegerField(default=3)
    retry_delay = models.IntegerField(default=60, help_text="Delay in seconds between retries")

    # Statistics
    total_deliveries = models.IntegerField(default=0)
    successful_deliveries = models.IntegerField(default=0)
    failed_deliveries = models.IntegerField(default=0)
    last_delivery_at = models.DateTimeField(blank=True)

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crm_webhooks'
        verbose_name = 'Webhook'
        verbose_name_plural = 'Webhooks'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.url})"

    def generate_signature(self, payload):
        """Generate HMAC signature for payload"""
        return hmac.new(
            self.secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()


class WebhookDelivery(models.Model):
    """Log of webhook delivery attempts"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name='deliveries')

    event = models.CharField(max_length=50)
    payload = models.JSONField()

    # Delivery status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    status_code = models.IntegerField(blank=True)
    response_body = models.TextField(blank=True)
    error_message = models.TextField(blank=True)

    # Retry info
    attempts = models.IntegerField(default=0)
    next_retry_at = models.DateTimeField(blank=True)

    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(blank=True)
    duration_ms = models.IntegerField(blank=True, help_text="Response time in milliseconds")

    class Meta:
        db_table = 'crm_webhook_deliveries'
        verbose_name = 'Webhook Delivery'
        verbose_name_plural = 'Webhook Deliveries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['webhook', 'status']),
            models.Index(fields=['event', 'created_at']),
        ]

    def __str__(self):
        return f"{self.webhook.name} - {self.event} ({self.status})"


class ThirdPartyIntegration(models.Model):
    """Third-party service integrations"""

    PROVIDER_CHOICES = [
        ('slack', 'Slack'),
        ('microsoft_teams', 'Microsoft Teams'),
        ('google_calendar', 'Google Calendar'),
        ('zoom', 'Zoom'),
        ('salesforce', 'Salesforce'),
        ('hubspot', 'HubSpot'),
        ('mailchimp', 'Mailchimp'),
        ('zapier', 'Zapier'),
        ('custom', 'Custom'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
        ('expired', 'Expired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)

    # OAuth credentials
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)

    # API credentials
    api_key = models.CharField(max_length=255, blank=True)
    api_secret = models.CharField(max_length=255, blank=True)

    # Configuration
    config = models.JSONField(
        default=dict,
        help_text="Provider-specific configuration"
    )

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)

    # Error tracking
    error_message = models.TextField(blank=True)
    error_count = models.IntegerField(default=0)

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='hub_integrations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crm_hub_integrations'
        verbose_name = 'Third Party Integration'
        verbose_name_plural = 'Third Party Integrations'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.provider})"

    @property
    def is_token_expired(self):
        """Check if OAuth token is expired"""
        if self.token_expires_at:
            return timezone.now() > self.token_expires_at
        return False

    def save(self, *args, **kwargs):
        """Encrypt API secrets and OAuth tokens before persisting to database"""
        from core.encryption import encrypt_value, is_encrypted
        # If credentials look unencrypted (plain text), encrypt them
        if self.api_key and not is_encrypted(self.api_key):
            self.api_key = encrypt_value(self.api_key)
        if self.api_secret and not is_encrypted(self.api_secret):
            self.api_secret = encrypt_value(self.api_secret)
        if self.access_token and not is_encrypted(self.access_token):
            self.access_token = encrypt_value(self.access_token)
        if self.refresh_token and not is_encrypted(self.refresh_token):
            self.refresh_token = encrypt_value(self.refresh_token)
        super().save(*args, **kwargs)

    def get_decrypted_credentials(self) -> dict:
        """Helper to safely retrieve decrypted credentials at runtime"""
        from core.encryption import decrypt_value, is_encrypted
        return {
            'api_key': decrypt_value(self.api_key) if is_encrypted(self.api_key) else (self.api_key or ''),
            'api_secret': decrypt_value(self.api_secret) if is_encrypted(self.api_secret) else (self.api_secret or ''),
            'access_token': decrypt_value(self.access_token) if is_encrypted(self.access_token) else (self.access_token or ''),
            'refresh_token': decrypt_value(self.refresh_token) if is_encrypted(self.refresh_token) else (self.refresh_token or ''),
        }


class IntegrationLog(models.Model):
    """Log of integration activities"""

    ACTION_CHOICES = [
        ('sync', 'Sync'),
        ('send', 'Send'),
        ('receive', 'Receive'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('error', 'Error'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    integration = models.ForeignKey(
        ThirdPartyIntegration,
        on_delete=models.CASCADE,
        related_name='logs'
    )

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()

    # Request/Response data
    request_data = models.JSONField(blank=True)
    response_data = models.JSONField(blank=True)

    # Status
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'crm_integration_logs'
        verbose_name = 'Integration Log'
        verbose_name_plural = 'Integration Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['integration', 'created_at']),
            models.Index(fields=['action', 'success']),
        ]

    def __str__(self):
        return f"{self.integration.name} - {self.action} ({self.created_at})"


class APIEndpoint(models.Model):
    """Custom API endpoints for extensions"""

    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Endpoint configuration
    path = models.CharField(max_length=255, unique=True, help_text="API path (e.g., /custom/my-endpoint)")
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, default='POST')

    # Handler (Python code or webhook URL)
    handler_type = models.CharField(
        max_length=20,
        choices=[('webhook', 'Webhook'), ('function', 'Python Function')],
        default='webhook'
    )
    handler_url = models.URLField(blank=True)
    handler_code = models.TextField(blank=True, help_text="Python code to execute")

    # Authentication
    requires_auth = models.BooleanField(default=True)
    allowed_roles = models.JSONField(
        default=list,
        help_text="List of roles allowed to access this endpoint"
    )

    # Rate limiting
    rate_limit = models.IntegerField(
        default=100,
        help_text="Max requests per hour"
    )

    # Status
    is_active = models.BooleanField(default=True)

    # Statistics
    total_calls = models.IntegerField(default=0)
    successful_calls = models.IntegerField(default=0)
    failed_calls = models.IntegerField(default=0)

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crm_api_endpoints'
        verbose_name = 'API Endpoint'
        verbose_name_plural = 'API Endpoints'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.method} {self.path}"


class InboundWebhookEndpoint(models.Model):
    """
    Secure Inbound Webhook Endpoint.
    Rigidly bound to an Organization (tenant).
    Requires HMAC signature verification and timestamp replay defense.
    Untrusted payload tenant fields are strictly ignored to prevent forged tenant injection.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        related_name='inbound_webhooks'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    provider = models.CharField(max_length=50, default='generic')
    secret_key = models.CharField(max_length=128, help_text="Shared secret for HMAC verification")
    tolerance_seconds = models.IntegerField(default=300, help_text="Max acceptable timestamp drift in seconds")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crm_inbound_webhook_endpoints'
        verbose_name = 'Inbound Webhook Endpoint'
        verbose_name_plural = 'Inbound Webhook Endpoints'

    def __str__(self):
        return f"{self.name} ({self.organization.name})"

    @property
    def tenant(self):
        return self.organization


class InboundWebhookDelivery(models.Model):
    """
    Delivery history for inbound webhooks with replay prevention tracking.
    """
    STATUS_CHOICES = [
        ('processed', 'Processed'),
        ('duplicate', 'Duplicate / Replay'),
        ('invalid_signature', 'Invalid Signature'),
        ('expired', 'Expired Timestamp'),
        ('failed', 'Processing Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    endpoint = models.ForeignKey(
        InboundWebhookEndpoint,
        on_delete=models.CASCADE,
        related_name='deliveries'
    )
    event_id = models.CharField(max_length=255, db_index=True, blank=True, help_text="Unique event nonce/id from sender")
    event_type = models.CharField(max_length=100, blank=True)
    payload = models.JSONField(default=dict)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='processed')
    received_at = models.DateTimeField(auto_now_add=True)
    forged_tenant_detected = models.BooleanField(default=False)

    class Meta:
        db_table = 'crm_inbound_webhook_deliveries'
        verbose_name = 'Inbound Webhook Delivery'
        verbose_name_plural = 'Inbound Webhook Deliveries'
        indexes = [
            models.Index(fields=['endpoint', 'event_id']),
            models.Index(fields=['received_at']),
        ]

