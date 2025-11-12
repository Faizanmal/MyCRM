"""
Email Campaign Management Models
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class Campaign(models.Model):
    """Email Marketing Campaign"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('mixed', 'Mixed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    campaign_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='email')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Content
    subject = models.CharField(max_length=255, help_text="Email subject line")
    content_html = models.TextField(help_text="HTML email content")
    content_text = models.TextField(blank=True, help_text="Plain text fallback")
    
    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Targeting
    segment = models.ForeignKey('CampaignSegment', on_delete=models.SET_NULL, null=True, blank=True)
    
    # A/B Testing
    enable_ab_test = models.BooleanField(default=False)
    ab_test_variants = models.JSONField(default=dict, blank=True)
    
    # Tracking
    total_recipients = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    bounced_count = models.IntegerField(default=0)
    unsubscribed_count = models.IntegerField(default=0)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_campaigns')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_campaigns'
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['created_by', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.status})"
    
    @property
    def open_rate(self):
        """Calculate email open rate"""
        if self.sent_count > 0:
            return round((self.opened_count / self.sent_count) * 100, 2)
        return 0
    
    @property
    def click_rate(self):
        """Calculate click-through rate"""
        if self.sent_count > 0:
            return round((self.clicked_count / self.sent_count) * 100, 2)
        return 0
    
    @property
    def bounce_rate(self):
        """Calculate bounce rate"""
        if self.sent_count > 0:
            return round((self.bounced_count / self.sent_count) * 100, 2)
        return 0


class CampaignSegment(models.Model):
    """Contact/Lead segment for targeting"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Segment criteria (JSON)
    filters = models.JSONField(
        default=dict, 
        help_text="Filter criteria: {lead_status: 'qualified', industry: 'tech', etc.}"
    )
    
    # Cached count
    contact_count = models.IntegerField(default=0)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_campaign_segments'
        verbose_name = 'Campaign Segment'
        verbose_name_plural = 'Campaign Segments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.contact_count} contacts)"


class CampaignRecipient(models.Model):
    """Individual campaign recipient tracking"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
        ('bounced', 'Bounced'),
        ('unsubscribed', 'Unsubscribed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='recipients')
    
    # Recipient info
    contact = models.ForeignKey('contact_management.Contact', on_delete=models.SET_NULL, null=True, blank=True)
    lead = models.ForeignKey('lead_management.Lead', on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # A/B Test variant
    variant = models.CharField(max_length=50, blank=True, help_text="A/B test variant (A, B, etc.)")
    
    # Tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    first_clicked_at = models.DateTimeField(null=True, blank=True)
    bounced_at = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    # Engagement
    open_count = models.IntegerField(default=0)
    click_count = models.IntegerField(default=0)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_campaign_recipients'
        verbose_name = 'Campaign Recipient'
        verbose_name_plural = 'Campaign Recipients'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['campaign', 'status']),
            models.Index(fields=['email']),
            models.Index(fields=['contact']),
            models.Index(fields=['lead']),
        ]
        unique_together = ['campaign', 'email']
    
    def __str__(self):
        return f"{self.email} - {self.campaign.name} ({self.status})"


class CampaignClick(models.Model):
    """Track individual link clicks in campaigns"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(CampaignRecipient, on_delete=models.CASCADE, related_name='clicks')
    
    url = models.URLField()
    clicked_at = models.DateTimeField(default=timezone.now)
    
    # Tracking details
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        db_table = 'crm_campaign_clicks'
        verbose_name = 'Campaign Click'
        verbose_name_plural = 'Campaign Clicks'
        ordering = ['-clicked_at']
        indexes = [
            models.Index(fields=['recipient', 'clicked_at']),
            models.Index(fields=['url']),
        ]
    
    def __str__(self):
        return f"{self.recipient.email} clicked {self.url}"


class EmailTemplate(models.Model):
    """Reusable email templates"""
    
    CATEGORY_CHOICES = [
        ('welcome', 'Welcome'),
        ('nurture', 'Nurture'),
        ('promotion', 'Promotion'),
        ('newsletter', 'Newsletter'),
        ('transactional', 'Transactional'),
        ('followup', 'Follow-up'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='custom')
    
    # Template content
    subject = models.CharField(max_length=255)
    content_html = models.TextField()
    content_text = models.TextField(blank=True)
    
    # Template variables (for personalization)
    variables = models.JSONField(
        default=list,
        help_text="List of variables: ['first_name', 'company', 'custom_field']"
    )
    
    # Preview
    thumbnail = models.ImageField(upload_to='email_templates/', null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='campaign_email_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_campaign_email_templates'
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.category})"
