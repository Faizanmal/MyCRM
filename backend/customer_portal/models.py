"""
Customer Portal Models
Enables self-service capabilities for customers including tickets, orders, and profile management.
"""

import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class CustomerAccount(models.Model):
    """
    Customer account for portal access - linked to Contact
    Provides separate authentication for customer portal
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.OneToOneField(
        'contact_management.Contact',
        on_delete=models.CASCADE,
        related_name='portal_account'
    )
    
    # Authentication
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Portal settings
    portal_access_enabled = models.BooleanField(default=True)
    notification_preferences = models.JSONField(default=dict, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    
    # Security
    last_login = models.DateTimeField(null=True, blank=True)
    login_count = models.IntegerField(default=0)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    password_reset_token = models.CharField(max_length=255, null=True, blank=True)
    password_reset_expires = models.DateTimeField(null=True, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, null=True, blank=True)
    
    # Branding (for white-label)
    tenant = models.ForeignKey(
        'multi_tenant.Tenant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='customer_accounts'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer_portal_accounts'
        verbose_name = 'Customer Account'
        verbose_name_plural = 'Customer Accounts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} - Portal Account"

    def is_locked(self):
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False

    def record_login(self):
        self.last_login = timezone.now()
        self.login_count += 1
        self.failed_login_attempts = 0
        self.save(update_fields=['last_login', 'login_count', 'failed_login_attempts'])


class SupportTicket(models.Model):
    """Customer support tickets submitted through the portal"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting_customer', 'Waiting on Customer'),
        ('waiting_internal', 'Waiting on Internal'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    CATEGORY_CHOICES = [
        ('general', 'General Inquiry'),
        ('billing', 'Billing'),
        ('technical', 'Technical Support'),
        ('feature_request', 'Feature Request'),
        ('bug_report', 'Bug Report'),
        ('account', 'Account Issues'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.CharField(max_length=20, unique=True)
    
    # Relationships
    customer = models.ForeignKey(
        CustomerAccount,
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_portal_tickets'
    )
    
    # Ticket details
    subject = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='open')
    
    # Related entities
    related_opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='support_tickets'
    )
    
    # Resolution
    resolution = models.TextField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_tickets'
    )
    
    # Satisfaction
    satisfaction_rating = models.IntegerField(null=True, blank=True, help_text="1-5 rating")
    satisfaction_feedback = models.TextField(null=True, blank=True)
    
    # SLA tracking
    sla_response_due = models.DateTimeField(null=True, blank=True)
    sla_resolution_due = models.DateTimeField(null=True, blank=True)
    first_response_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer_portal_tickets'
        verbose_name = 'Support Ticket'
        verbose_name_plural = 'Support Tickets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['customer', '-created_at']),
            models.Index(fields=['assigned_to', 'status']),
        ]

    def __str__(self):
        return f"#{self.ticket_number} - {self.subject}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            # Generate ticket number
            last_ticket = SupportTicket.objects.order_by('-created_at').first()
            if last_ticket and last_ticket.ticket_number:
                try:
                    last_num = int(last_ticket.ticket_number.replace('TKT-', ''))
                    self.ticket_number = f"TKT-{last_num + 1:06d}"
                except ValueError:
                    self.ticket_number = f"TKT-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            else:
                self.ticket_number = "TKT-000001"
        super().save(*args, **kwargs)


class TicketComment(models.Model):
    """Comments on support tickets"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    
    # Author can be customer or internal user
    customer = models.ForeignKey(
        CustomerAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ticket_comments'
    )
    internal_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ticket_comments'
    )
    
    content = models.TextField()
    is_internal = models.BooleanField(default=False, help_text="Internal note not visible to customer")
    
    # Attachments
    attachments = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer_portal_ticket_comments'
        verbose_name = 'Ticket Comment'
        verbose_name_plural = 'Ticket Comments'
        ordering = ['created_at']

    def __str__(self):
        return f"Comment on {self.ticket.ticket_number}"


class CustomerOrder(models.Model):
    """Customer orders visible in the portal"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True)
    
    customer = models.ForeignKey(
        CustomerAccount,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_orders'
    )
    
    # Order details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    items = models.JSONField(default=list)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Shipping
    shipping_address = models.JSONField(default=dict, blank=True)
    billing_address = models.JSONField(default=dict, blank=True)
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    tracking_url = models.URLField(null=True, blank=True)
    
    # Dates
    ordered_at = models.DateTimeField(auto_now_add=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Documents
    invoice_url = models.URLField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer_portal_orders'
        verbose_name = 'Customer Order'
        verbose_name_plural = 'Customer Orders'
        ordering = ['-ordered_at']

    def __str__(self):
        return f"Order #{self.order_number}"


class KnowledgeBaseArticle(models.Model):
    """Self-service knowledge base articles"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True)
    
    title = models.CharField(max_length=255)
    content = models.TextField()
    excerpt = models.TextField(max_length=500, blank=True)
    
    category = models.CharField(max_length=100)
    tags = models.JSONField(default=list, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    
    # Analytics
    view_count = models.IntegerField(default=0)
    helpful_count = models.IntegerField(default=0)
    not_helpful_count = models.IntegerField(default=0)
    
    # SEO
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Authorship
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='kb_articles'
    )
    
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer_portal_kb_articles'
        verbose_name = 'Knowledge Base Article'
        verbose_name_plural = 'Knowledge Base Articles'
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class PortalSession(models.Model):
    """Track customer portal sessions for security"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        CustomerAccount,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    
    session_token = models.CharField(max_length=255, unique=True)
    refresh_token = models.CharField(max_length=255, unique=True)
    
    # Device info
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_fingerprint = models.CharField(max_length=255, null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer_portal_sessions'
        verbose_name = 'Portal Session'
        verbose_name_plural = 'Portal Sessions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Session for {self.customer.email}"

    def is_expired(self):
        return timezone.now() > self.expires_at


class PortalNotification(models.Model):
    """Notifications for customer portal users"""
    
    TYPE_CHOICES = [
        ('ticket_update', 'Ticket Update'),
        ('order_update', 'Order Update'),
        ('new_article', 'New Article'),
        ('announcement', 'Announcement'),
        ('system', 'System'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        CustomerAccount,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    action_url = models.URLField(null=True, blank=True)
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'customer_portal_notifications'
        verbose_name = 'Portal Notification'
        verbose_name_plural = 'Portal Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type}: {self.title}"
