"""
Integration Marketplace - Advanced Features
App marketplace, custom webhook builder, and API rate limiting
"""

from django.db import models
from django.conf import settings
import uuid


class MarketplaceApp(models.Model):
    """Third-party integrations available in the marketplace"""
    
    CATEGORIES = [
        ('communication', 'Communication'),
        ('productivity', 'Productivity'),
        ('analytics', 'Analytics'),
        ('marketing', 'Marketing'),
        ('sales', 'Sales Tools'),
        ('support', 'Customer Support'),
        ('finance', 'Finance & Billing'),
        ('hr', 'HR & Recruiting'),
        ('developer', 'Developer Tools'),
        ('storage', 'Storage & Files'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('published', 'Published'),
        ('deprecated', 'Deprecated'),
    ]
    
    PRICING_MODELS = [
        ('free', 'Free'),
        ('freemium', 'Freemium'),
        ('paid', 'Paid'),
        ('contact', 'Contact for Pricing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic info
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    tagline = models.CharField(max_length=300)
    description = models.TextField()
    
    # Categorization
    category = models.CharField(max_length=50, choices=CATEGORIES)
    tags = models.JSONField(default=list)
    
    # Developer info
    developer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='developed_apps'
    )
    developer_name = models.CharField(max_length=200)
    developer_email = models.EmailField()
    developer_website = models.URLField(blank=True)
    support_url = models.URLField(blank=True)
    documentation_url = models.URLField(blank=True)
    
    # Media
    icon = models.ImageField(upload_to='marketplace/icons/', blank=True)
    banner = models.ImageField(upload_to='marketplace/banners/', blank=True)
    screenshots = models.JSONField(default=list)  # List of URLs
    
    # Pricing
    pricing_model = models.CharField(max_length=20, choices=PRICING_MODELS, default='free')
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Integration details
    oauth_client_id = models.CharField(max_length=500, blank=True)
    oauth_client_secret = models.CharField(max_length=500, blank=True)
    oauth_authorize_url = models.URLField(blank=True)
    oauth_token_url = models.URLField(blank=True)
    oauth_scopes = models.JSONField(default=list)
    
    api_base_url = models.URLField(blank=True)
    webhook_url = models.URLField(blank=True)
    
    # Permissions
    required_permissions = models.JSONField(default=list)
    data_access = models.JSONField(default=list)  # What data the app can access
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    version = models.CharField(max_length=20, default='1.0.0')
    
    # Stats
    install_count = models.IntegerField(default=0)
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'marketplace_apps'
        ordering = ['-install_count', '-rating_avg']
    
    def __str__(self):
        return self.name


class AppInstallation(models.Model):
    """Track app installations by organizations/users"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('uninstalled', 'Uninstalled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    app = models.ForeignKey(
        MarketplaceApp,
        on_delete=models.CASCADE,
        related_name='installations'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='installed_apps'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # OAuth tokens
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Configuration
    config = models.JSONField(default=dict)
    permissions_granted = models.JSONField(default=list)
    
    # Usage
    last_used = models.DateTimeField(null=True, blank=True)
    api_calls_count = models.IntegerField(default=0)
    
    installed_at = models.DateTimeField(auto_now_add=True)
    uninstalled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'app_installations'
        unique_together = ['app', 'user']
    
    def __str__(self):
        return f"{self.user.email} - {self.app.name}"


class AppReview(models.Model):
    """User reviews for marketplace apps"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    app = models.ForeignKey(
        MarketplaceApp,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='app_reviews'
    )
    
    rating = models.IntegerField()  # 1-5
    title = models.CharField(max_length=200)
    review = models.TextField()
    
    # Helpfulness
    helpful_count = models.IntegerField(default=0)
    
    # Developer response
    developer_response = models.TextField(blank=True)
    developer_responded_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'app_reviews'
        unique_together = ['app', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.app.name}: {self.rating}/5"


class CustomWebhook(models.Model):
    """User-configured custom webhooks"""
    
    HTTP_METHODS = [
        ('POST', 'POST'),
        ('GET', 'GET'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
    ]
    
    AUTH_TYPES = [
        ('none', 'None'),
        ('basic', 'Basic Auth'),
        ('bearer', 'Bearer Token'),
        ('api_key', 'API Key'),
        ('oauth2', 'OAuth 2.0'),
        ('hmac', 'HMAC Signature'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='custom_webhooks'
    )
    
    # Basic config
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    url = models.URLField()
    method = models.CharField(max_length=10, choices=HTTP_METHODS, default='POST')
    
    # Events
    events = models.JSONField(default=list)  # List of event types to trigger on
    
    # Authentication
    auth_type = models.CharField(max_length=20, choices=AUTH_TYPES, default='none')
    auth_config = models.JSONField(default=dict)  # Encrypted credentials
    
    # Headers
    custom_headers = models.JSONField(default=dict)
    
    # Payload configuration
    payload_template = models.TextField(blank=True)  # JSON template with variables
    include_full_payload = models.BooleanField(default=True)
    
    # Conditions
    conditions = models.JSONField(default=list)  # Conditional logic for triggering
    
    # Rate limiting
    rate_limit_per_minute = models.IntegerField(default=60)
    
    # Retry configuration
    retry_enabled = models.BooleanField(default=True)
    max_retries = models.IntegerField(default=3)
    retry_delay_seconds = models.IntegerField(default=60)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Stats
    total_triggers = models.IntegerField(default=0)
    successful_deliveries = models.IntegerField(default=0)
    failed_deliveries = models.IntegerField(default=0)
    last_triggered = models.DateTimeField(null=True, blank=True)
    last_success = models.DateTimeField(null=True, blank=True)
    last_failure = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'custom_webhooks'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.url})"


class WebhookEvent(models.Model):
    """Available webhook events"""
    
    ENTITY_TYPES = [
        ('contact', 'Contact'),
        ('lead', 'Lead'),
        ('opportunity', 'Opportunity'),
        ('task', 'Task'),
        ('email', 'Email'),
        ('call', 'Call'),
        ('meeting', 'Meeting'),
        ('note', 'Note'),
        ('user', 'User'),
        ('organization', 'Organization'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200)
    description = models.TextField()
    
    entity_type = models.CharField(max_length=50, choices=ENTITY_TYPES)
    action = models.CharField(max_length=50)  # created, updated, deleted
    
    # Payload schema
    payload_schema = models.JSONField(default=dict)
    example_payload = models.JSONField(default=dict)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'webhook_events'
        ordering = ['entity_type', 'action']
    
    def __str__(self):
        return self.name


class WebhookDeliveryLog(models.Model):
    """Log of webhook deliveries"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    webhook = models.ForeignKey(
        CustomWebhook,
        on_delete=models.CASCADE,
        related_name='delivery_logs'
    )
    
    event = models.CharField(max_length=100)
    
    # Request
    request_url = models.URLField()
    request_method = models.CharField(max_length=10)
    request_headers = models.JSONField(default=dict)
    request_body = models.TextField()
    
    # Response
    response_status = models.IntegerField(null=True, blank=True)
    response_headers = models.JSONField(default=dict)
    response_body = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # Timing
    attempt_number = models.IntegerField(default=1)
    duration_ms = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'webhook_delivery_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.webhook.name} - {self.event} - {self.status}"


class APIRateLimit(models.Model):
    """API rate limiting configuration"""
    
    PERIOD_CHOICES = [
        ('second', 'Per Second'),
        ('minute', 'Per Minute'),
        ('hour', 'Per Hour'),
        ('day', 'Per Day'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Scope
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='rate_limits'
    )
    api_key = models.CharField(max_length=200, blank=True)
    app = models.ForeignKey(
        MarketplaceApp,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='rate_limits'
    )
    
    # Endpoint
    endpoint_pattern = models.CharField(max_length=500, default='*')  # Regex or wildcard
    
    # Limits
    requests_limit = models.IntegerField(default=1000)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='hour')
    
    # Burst handling
    burst_limit = models.IntegerField(default=50)  # Max concurrent requests
    
    # Current usage
    current_count = models.IntegerField(default=0)
    period_start = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_exceeded = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_rate_limits'
    
    def __str__(self):
        scope = self.user.email if self.user else self.api_key or 'Global'
        return f"{scope}: {self.requests_limit}/{self.period}"


class APIUsageLog(models.Model):
    """Log API usage for monitoring and rate limiting"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    api_key = models.CharField(max_length=200, blank=True)
    app = models.ForeignKey(
        MarketplaceApp,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    
    # Request details
    endpoint = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    
    # Response
    status_code = models.IntegerField()
    response_time_ms = models.IntegerField()
    
    # Client info
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    # Rate limiting
    rate_limit_remaining = models.IntegerField(null=True, blank=True)
    was_rate_limited = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'api_usage_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['endpoint', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"


class APIUsageMetrics(models.Model):
    """Aggregated API usage metrics"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    app = models.ForeignKey(
        MarketplaceApp,
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    
    # Period
    period = models.CharField(max_length=20)  # hourly, daily, weekly
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Metrics
    total_requests = models.IntegerField(default=0)
    successful_requests = models.IntegerField(default=0)
    failed_requests = models.IntegerField(default=0)
    rate_limited_requests = models.IntegerField(default=0)
    
    avg_response_time_ms = models.IntegerField(default=0)
    max_response_time_ms = models.IntegerField(default=0)
    min_response_time_ms = models.IntegerField(default=0)
    
    # By endpoint
    endpoint_breakdown = models.JSONField(default=dict)
    
    # By status code
    status_code_breakdown = models.JSONField(default=dict)
    
    calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_usage_metrics'
        ordering = ['-period_start']
    
    def __str__(self):
        scope = self.user.email if self.user else 'All'
        return f"{scope} - {self.period}: {self.total_requests} requests"
