"""
App Marketplace Models
Registry and management of third-party apps and extensions.
"""

import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class AppCategory(models.Model):
    """Categories for marketplace apps"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'marketplace_categories'
        verbose_name = 'App Category'
        verbose_name_plural = 'App Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class AppDeveloper(models.Model):
    """Developer/Publisher information"""
    
    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    
    # Contact
    email = models.EmailField()
    website = models.URLField(blank=True)
    support_url = models.URLField(blank=True)
    
    # Branding
    logo_url = models.URLField(blank=True)
    
    # Verification
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Stats
    total_apps = models.IntegerField(default=0)
    total_installs = models.IntegerField(default=0)
    
    # Linked user
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'marketplace_developers'
        verbose_name = 'App Developer'
        verbose_name_plural = 'App Developers'

    def __str__(self):
        return self.name


class MarketplaceApp(models.Model):
    """Apps available in the marketplace"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
        ('deprecated', 'Deprecated'),
    ]
    
    PRICING_TYPE = [
        ('free', 'Free'),
        ('freemium', 'Freemium'),
        ('paid', 'Paid'),
        ('subscription', 'Subscription'),
    ]
    
    APP_TYPE = [
        ('integration', 'Integration'),
        ('widget', 'Widget'),
        ('report', 'Report'),
        ('workflow', 'Workflow'),
        ('theme', 'Theme'),
        ('utility', 'Utility'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic info
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    tagline = models.CharField(max_length=200)
    description = models.TextField()
    
    # Classification
    app_type = models.CharField(max_length=20, choices=APP_TYPE)
    category = models.ForeignKey(AppCategory, on_delete=models.SET_NULL, null=True, related_name='apps')
    tags = models.JSONField(default=list, blank=True)
    
    # Developer
    developer = models.ForeignKey(AppDeveloper, on_delete=models.CASCADE, related_name='apps')
    
    # Versioning
    current_version = models.CharField(max_length=20)
    min_crm_version = models.CharField(max_length=20, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Pricing
    pricing_type = models.CharField(max_length=20, choices=PRICING_TYPE, default='free')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_currency = models.CharField(max_length=3, default='USD')
    subscription_period = models.CharField(max_length=20, blank=True)  # monthly, yearly
    
    # Media
    icon_url = models.URLField()
    screenshots = models.JSONField(default=list, blank=True)
    video_url = models.URLField(blank=True)
    
    # Links
    documentation_url = models.URLField(blank=True)
    support_url = models.URLField(blank=True)
    privacy_policy_url = models.URLField(blank=True)
    terms_url = models.URLField(blank=True)
    
    # Configuration
    manifest = models.JSONField(default=dict)  # App configuration/capabilities
    permissions = models.JSONField(default=list)  # Required permissions
    webhook_url = models.URLField(blank=True)
    oauth_settings = models.JSONField(default=dict, blank=True)
    
    # Stats
    install_count = models.IntegerField(default=0)
    rating_average = models.FloatField(default=0)
    rating_count = models.IntegerField(default=0)
    
    # Feature flags
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'marketplace_apps'
        verbose_name = 'Marketplace App'
        verbose_name_plural = 'Marketplace Apps'
        ordering = ['-is_featured', '-rating_average', '-install_count']

    def __str__(self):
        return self.name


class AppVersion(models.Model):
    """Version history for apps"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    app = models.ForeignKey(MarketplaceApp, on_delete=models.CASCADE, related_name='versions')
    version = models.CharField(max_length=20)
    
    # Changes
    changelog = models.TextField()
    
    # Package
    package_url = models.URLField(blank=True)
    package_hash = models.CharField(max_length=64, blank=True)
    
    # Compatibility
    min_crm_version = models.CharField(max_length=20, blank=True)
    max_crm_version = models.CharField(max_length=20, blank=True)
    
    # Review
    is_approved = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    released_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'marketplace_app_versions'
        verbose_name = 'App Version'
        verbose_name_plural = 'App Versions'
        unique_together = ['app', 'version']
        ordering = ['-released_at']

    def __str__(self):
        return f"{self.app.name} v{self.version}"


class AppInstallation(models.Model):
    """Installed apps for a tenant/user"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending_setup', 'Pending Setup'),
        ('error', 'Error'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    app = models.ForeignKey(MarketplaceApp, on_delete=models.CASCADE, related_name='installations')
    installed_version = models.CharField(max_length=20)
    
    # Installation scope
    tenant = models.ForeignKey(
        'multi_tenant.Tenant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='installed_apps'
    )
    installed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Configuration
    config = models.JSONField(default=dict, blank=True)
    
    # OAuth tokens if needed
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_setup')
    error_message = models.TextField(blank=True)
    
    # Usage
    last_used_at = models.DateTimeField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    
    installed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'marketplace_installations'
        verbose_name = 'App Installation'
        verbose_name_plural = 'App Installations'
        unique_together = ['app', 'tenant']

    def __str__(self):
        return f"{self.app.name} - {self.tenant}"


class AppReview(models.Model):
    """User reviews for apps"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    app = models.ForeignKey(MarketplaceApp, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='app_reviews')
    installation = models.ForeignKey(AppInstallation, on_delete=models.SET_NULL, null=True)
    
    rating = models.IntegerField()  # 1-5
    title = models.CharField(max_length=200)
    review = models.TextField()
    
    # Response from developer
    developer_response = models.TextField(blank=True)
    developer_responded_at = models.DateTimeField(null=True, blank=True)
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Helpful votes
    helpful_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'marketplace_reviews'
        verbose_name = 'App Review'
        verbose_name_plural = 'App Reviews'
        unique_together = ['app', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.app.name} - {self.rating}★ by {self.user.username}"


class AppWebhookEvent(models.Model):
    """Webhook events from installed apps"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    installation = models.ForeignKey(
        AppInstallation,
        on_delete=models.CASCADE,
        related_name='webhook_events'
    )
    
    event_type = models.CharField(max_length=100)
    payload = models.JSONField(default=dict)
    
    # Processing
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    response_status = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'marketplace_webhook_events'
        verbose_name = 'Webhook Event'
        verbose_name_plural = 'Webhook Events'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.installation.app.name} - {self.event_type}"
