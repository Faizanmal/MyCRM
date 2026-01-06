"""
API & Developer Tools Models - GraphQL, webhooks, API analytics, and developer features.
"""

import uuid

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models


class APIKey(models.Model):
    """API keys for programmatic access."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Key identification
    name = models.CharField(max_length=200)
    key_prefix = models.CharField(max_length=10)  # First few chars for identification
    key_hash = models.CharField(max_length=255)  # Hashed key for verification

    # Ownership
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='api_keys'
    )
    organization = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='api_keys'
    )

    # Permissions and scopes
    scopes = ArrayField(models.CharField(max_length=100), default=list)
    # e.g., ['contacts:read', 'contacts:write', 'deals:read']

    # Rate limiting
    rate_limit_per_minute = models.PositiveIntegerField(default=60)
    rate_limit_per_hour = models.PositiveIntegerField(default=1000)
    rate_limit_per_day = models.PositiveIntegerField(default=10000)

    # IP restrictions
    allowed_ips = ArrayField(models.GenericIPAddressField(), default=list)
    allowed_origins = ArrayField(models.CharField(max_length=200), default=list)

    # Validity
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True)

    # Usage tracking
    total_requests = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_key'
        indexes = [
            models.Index(fields=['key_prefix']),
            models.Index(fields=['user', 'is_active']),
        ]


class APIRequest(models.Model):
    """Logs individual API requests for analytics."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Request identification
    request_id = models.CharField(max_length=100, unique=True)

    # Authentication
    api_key = models.ForeignKey(
        APIKey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requests'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Request details
    method = models.CharField(max_length=10)  # GET, POST, etc.
    path = models.CharField(max_length=500)
    query_params = models.JSONField(default=dict)
    request_headers = models.JSONField(default=dict)  # Sanitized
    request_body_size = models.PositiveIntegerField(default=0)

    # Response details
    status_code = models.PositiveIntegerField()
    response_time_ms = models.PositiveIntegerField()
    response_body_size = models.PositiveIntegerField(default=0)

    # Context
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)

    # Error tracking
    error_code = models.CharField(max_length=50, blank=True)
    error_message = models.TextField(blank=True)

    # GraphQL specific
    is_graphql = models.BooleanField(default=False)
    graphql_operation_name = models.CharField(max_length=200, blank=True)
    graphql_operation_type = models.CharField(max_length=20, blank=True)  # query, mutation, subscription

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_request'
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['api_key', 'created_at']),
            models.Index(fields=['path', 'created_at']),
            models.Index(fields=['status_code']),
        ]


class Webhook(models.Model):
    """Webhook endpoints for event notifications."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Owner
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='webhooks'
    )
    organization = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='webhooks'
    )

    # Endpoint configuration
    url = models.URLField()
    secret = models.CharField(max_length=255)  # For signing payloads

    # Events to subscribe to
    events = ArrayField(models.CharField(max_length=100), default=list)
    # e.g., ['contact.created', 'deal.updated', 'deal.won']

    # Headers to include
    custom_headers = models.JSONField(default=dict)

    # Retry configuration
    retry_enabled = models.BooleanField(default=True)
    max_retries = models.PositiveIntegerField(default=5)
    retry_delay_seconds = models.PositiveIntegerField(default=60)
    retry_backoff_multiplier = models.FloatField(default=2.0)

    # Status
    is_active = models.BooleanField(default=True)

    # Health tracking
    consecutive_failures = models.PositiveIntegerField(default=0)
    last_triggered_at = models.DateTimeField(null=True)
    last_success_at = models.DateTimeField(null=True)
    last_failure_at = models.DateTimeField(null=True)

    # Auto-disable settings
    auto_disable_after_failures = models.PositiveIntegerField(default=10)
    disabled_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_webhook'


class WebhookDelivery(models.Model):
    """Tracks individual webhook delivery attempts."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    webhook = models.ForeignKey(
        Webhook,
        on_delete=models.CASCADE,
        related_name='deliveries'
    )

    # Event information
    event_type = models.CharField(max_length=100)
    event_id = models.CharField(max_length=100)
    payload = models.JSONField()

    # Delivery status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('sending', 'Sending'),
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('retrying', 'Retrying'),
        ],
        default='pending'
    )

    # Attempt tracking
    attempt_count = models.PositiveIntegerField(default=0)
    next_retry_at = models.DateTimeField(null=True)

    # Response information
    response_status_code = models.PositiveIntegerField(null=True)
    response_body = models.TextField(blank=True)
    response_headers = models.JSONField(default=dict)
    response_time_ms = models.PositiveIntegerField(null=True)

    # Error information
    error_message = models.TextField(blank=True)

    # Timing
    triggered_at = models.DateTimeField()
    delivered_at = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_webhook_delivery'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['webhook', 'status']),
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['next_retry_at']),
        ]


class GraphQLSchema(models.Model):
    """Stores GraphQL schema versions for documentation."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    version = models.CharField(max_length=50)
    schema_sdl = models.TextField()  # Schema Definition Language

    # Metadata
    types_count = models.PositiveIntegerField(default=0)
    queries_count = models.PositiveIntegerField(default=0)
    mutations_count = models.PositiveIntegerField(default=0)
    subscriptions_count = models.PositiveIntegerField(default=0)

    # Change tracking
    changelog = models.TextField(blank=True)
    breaking_changes = models.JSONField(default=list)
    deprecations = models.JSONField(default=list)

    is_current = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_graphql_schema'
        ordering = ['-created_at']


class GraphQLPersistedQuery(models.Model):
    """Persisted GraphQL queries for performance optimization."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Query identification
    query_hash = models.CharField(max_length=64, unique=True)  # SHA256 hash
    query_name = models.CharField(max_length=200, blank=True)

    # Query content
    query = models.TextField()
    variables_schema = models.JSONField(default=dict)  # Expected variables structure

    # Ownership
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='persisted_queries'
    )

    # Usage
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    last_used_at = models.DateTimeField(null=True)

    # Performance
    avg_execution_time_ms = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_graphql_persisted_query'


class APIAnalytics(models.Model):
    """Aggregated API analytics for reporting."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Time period
    period_type = models.CharField(
        max_length=10,
        choices=[
            ('hour', 'Hourly'),
            ('day', 'Daily'),
            ('week', 'Weekly'),
            ('month', 'Monthly'),
        ]
    )
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()

    # Scope
    api_key = models.ForeignKey(
        APIKey,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='analytics'
    )
    endpoint = models.CharField(max_length=500, blank=True)

    # Request metrics
    total_requests = models.PositiveIntegerField(default=0)
    successful_requests = models.PositiveIntegerField(default=0)
    failed_requests = models.PositiveIntegerField(default=0)

    # Response codes
    status_2xx = models.PositiveIntegerField(default=0)
    status_3xx = models.PositiveIntegerField(default=0)
    status_4xx = models.PositiveIntegerField(default=0)
    status_5xx = models.PositiveIntegerField(default=0)

    # Performance metrics
    avg_response_time_ms = models.FloatField(default=0)
    p50_response_time_ms = models.FloatField(default=0)
    p95_response_time_ms = models.FloatField(default=0)
    p99_response_time_ms = models.FloatField(default=0)
    max_response_time_ms = models.FloatField(default=0)

    # Data transfer
    total_request_bytes = models.BigIntegerField(default=0)
    total_response_bytes = models.BigIntegerField(default=0)

    # Rate limiting
    rate_limited_requests = models.PositiveIntegerField(default=0)

    # Unique values
    unique_ips = models.PositiveIntegerField(default=0)
    unique_user_agents = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_analytics'
        indexes = [
            models.Index(fields=['period_type', 'period_start']),
            models.Index(fields=['api_key', 'period_start']),
            models.Index(fields=['endpoint', 'period_start']),
        ]


class APIDocumentation(models.Model):
    """Custom API documentation and guides."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Document identification
    slug = models.SlugField(max_length=200, unique=True)
    title = models.CharField(max_length=200)

    # Content
    content = models.TextField()  # Markdown content
    content_html = models.TextField(blank=True)  # Rendered HTML

    # Organization
    category = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    # Related endpoints
    related_endpoints = ArrayField(models.CharField(max_length=200), default=list)

    # Status
    is_published = models.BooleanField(default=False)

    # Versioning
    version = models.CharField(max_length=50, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_documentation'
        ordering = ['category', 'order']


class SDKDownload(models.Model):
    """Tracks SDK downloads for developer analytics."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # SDK information
    sdk_name = models.CharField(max_length=100)  # python, javascript, ruby, etc.
    sdk_version = models.CharField(max_length=50)

    # Download context
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)

    download_source = models.CharField(max_length=50)  # docs, npm, pypi, github

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_sdk_download'


class DeveloperApp(models.Model):
    """OAuth applications registered by developers."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    logo_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)

    # Owner
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='developer_apps'
    )

    # OAuth credentials
    client_id = models.CharField(max_length=100, unique=True)
    client_secret_hash = models.CharField(max_length=255)

    # OAuth configuration
    redirect_uris = ArrayField(models.URLField(), default=list)
    allowed_scopes = ArrayField(models.CharField(max_length=100), default=list)

    # App type
    app_type = models.CharField(
        max_length=20,
        choices=[
            ('web', 'Web Application'),
            ('native', 'Native Application'),
            ('spa', 'Single Page Application'),
            ('service', 'Service Account'),
        ]
    )

    # Status
    is_published = models.BooleanField(default=False)  # Listed in marketplace
    is_approved = models.BooleanField(default=False)  # Reviewed by admin
    is_active = models.BooleanField(default=True)

    # Usage tracking
    total_installs = models.PositiveIntegerField(default=0)
    active_installs = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_developer_app'


class AppInstallation(models.Model):
    """Tracks installations of developer apps."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    app = models.ForeignKey(
        DeveloperApp,
        on_delete=models.CASCADE,
        related_name='installations'
    )

    # Installer
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='app_installations'
    )
    organization = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # Granted scopes
    granted_scopes = ArrayField(models.CharField(max_length=100), default=list)

    # Status
    is_active = models.BooleanField(default=True)

    # OAuth tokens would be stored separately in a secure token store

    installed_at = models.DateTimeField(auto_now_add=True)
    uninstalled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'api_app_installation'
        unique_together = ['app', 'user', 'organization']
