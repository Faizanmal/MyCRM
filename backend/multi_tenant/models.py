import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify

User = get_user_model()


class Organization(models.Model):
    """
    Represents a tenant organization in the multi-tenant system.
    Each organization is completely isolated from others.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('trial', 'Trial'),
        ('cancelled', 'Cancelled'),
    ]

    PLAN_CHOICES = [
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)

    # Organization details
    domain = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text="Custom domain for this organization"
    )
    logo = models.ImageField(upload_to='organization_logos/', blank=True)
    website = models.URLField(max_length=500, blank=True)

    # Contact information
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    # Subscription details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    max_users = models.PositiveIntegerField(default=5)
    max_contacts = models.PositiveIntegerField(default=1000)
    max_storage_mb = models.PositiveIntegerField(default=500)

    # Billing
    billing_email = models.EmailField(blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    subscription_start = models.DateField(null=True, blank=True)
    subscription_end = models.DateField(null=True, blank=True)
    trial_ends_at = models.DateField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_organizations'
    )

    # Settings
    settings = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['domain']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status in ['active', 'trial']

    @property
    def is_trial(self):
        return self.status == 'trial'

    @property
    def user_count(self):
        return self.members.filter(is_active=True).count()

    @property
    def storage_used_mb(self):
        # Calculate storage used by this organization
        # This would need to be implemented based on your file storage
        return 0


class OrganizationMember(models.Model):
    """
    Represents a user's membership in an organization with specific roles and permissions.
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('member', 'Member'),
        ('guest', 'Guest'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organization_memberships'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')

    # Permissions
    is_active = models.BooleanField(default=True)
    can_invite_users = models.BooleanField(default=False)
    can_manage_billing = models.BooleanField(default=False)
    can_manage_settings = models.BooleanField(default=False)

    # Metadata
    joined_at = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invited_members'
    )

    class Meta:
        unique_together = ('organization', 'user')
        ordering = ['-joined_at']
        indexes = [
            models.Index(fields=['organization', 'user']),
            models.Index(fields=['organization', 'role']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.organization.name} ({self.role})"

    @property
    def is_owner(self):
        return self.role == 'owner'

    @property
    def is_admin(self):
        return self.role in ['owner', 'admin']


class OrganizationInvitation(models.Model):
    """
    Represents an invitation to join an organization.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    email = models.EmailField()
    role = models.CharField(
        max_length=20,
        choices=OrganizationMember.ROLE_CHOICES,
        default='member'
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Metadata
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_invitations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['email', 'status']),
        ]

    def __str__(self):
        return f"Invitation to {self.email} for {self.organization.name}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    @property
    def is_pending(self):
        return self.status == 'pending' and not self.is_expired


class TenantAwareModel(models.Model):
    """
    Abstract base model that adds organization/tenant awareness to any model.
    All tenant-aware models should inherit from this.
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
        db_index=True
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Ensure organization is set
        if not self.organization_id:
            from .middleware import get_current_organization
            org = get_current_organization()
            if not org:
                # For development/testing, create a default organization
                org, created = Organization.objects.get_or_create(
                    slug='default',
                    defaults={
                        'name': 'Default Organization',
                        'domain': '127.0.0.1',
                        'email': 'admin@example.com',
                        'status': 'active'
                    }
                )
            if org:
                self.organization = org
        super().save(*args, **kwargs)


class ProductPositioningProfile(models.Model):
    """
    Tracks tenant product positioning, Ideal Customer Profile (ICP),
    Jobs-To-Be-Done (JTBD), buyer task progression, and measurable value metrics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name='product_positioning'
    )

    # ICP & Market Positioning
    target_market = models.CharField(
        max_length=100,
        default='b2b_saas',
        help_text="Target vertical, e.g. b2b_saas, fintech, professional_services, healthtech"
    )
    ideal_customer_profile = models.CharField(
        max_length=100,
        default='mid_market',
        help_text="Company tier, e.g. smb, mid_market, enterprise"
    )
    team_size_tier = models.CharField(
        max_length=50,
        default='20_100',
        help_text="Sales team size tier, e.g. 1_10, 11_50, 51_200, 201_500, 500_plus"
    )
    primary_jtbd = models.CharField(
        max_length=100,
        default='pipeline_velocity',
        help_text="Primary job to be done: pipeline_velocity, data_consolidation, ai_sales_automation, forecasting_accuracy"
    )

    # 5 Real Buyer Tasks Tracking
    # Allowed tasks: 'eval_poc', 'data_migration', 'team_onboarding', 'pipeline_execution', 'roi_measurement'
    buyer_tasks_completed = models.JSONField(
        default=list,
        blank=True,
        help_text="List of completed buyer tasks"
    )

    # Measurable Value Metrics
    # Stores business impact metrics, e.g. {'hours_saved_weekly': 14.5, 'win_rate_lift': 28.0, 'pipeline_hygiene_score': 95}
    value_metrics = models.JSONField(
        default=dict,
        blank=True,
        help_text="Quantifiable business impact metrics"
    )

    # Onboarding Status & Milestones
    onboarding_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('skipped', 'Skipped')
        ],
        default='in_progress'
    )
    activated_features = models.JSONField(
        default=list,
        blank=True,
        help_text="List of activated platform features"
    )
    completed_at = models.DateTimeField(null=True, blank=True)

    # Auditing & Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_positioning_profiles'
    )

    class Meta:
        db_table = 'tenant_product_positioning'
        ordering = ['-created_at']
        verbose_name = 'Product Positioning Profile'
        verbose_name_plural = 'Product Positioning Profiles'

    def __str__(self):
        return f"Positioning for {self.organization.name} ({self.target_market})"

    def complete_buyer_task(self, task_key: str, updated_by=None):
        from django.utils import timezone
        valid_tasks = [
            'eval_poc',
            'data_migration',
            'team_onboarding',
            'pipeline_execution',
            'roi_measurement'
        ]
        if task_key not in valid_tasks:
            raise ValueError(f"Invalid buyer task '{task_key}'. Must be one of {valid_tasks}")

        if task_key not in self.buyer_tasks_completed:
            self.buyer_tasks_completed.append(task_key)
            if updated_by:
                self.last_updated_by = updated_by
            if len(self.buyer_tasks_completed) == len(valid_tasks):
                self.onboarding_status = 'completed'
                self.completed_at = timezone.now()
            self.save(update_fields=['buyer_tasks_completed', 'onboarding_status', 'completed_at', 'last_updated_by', 'updated_at'])
        return self.buyer_tasks_completed

