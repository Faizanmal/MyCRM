import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

logger = logging.getLogger(__name__)
User = get_user_model()


class Account(models.Model):
    """Company / Account entity for B2B relationships and multi-tenant organization hierarchy"""
    ACCOUNT_TYPE_CHOICES = [
        ('prospect', 'Prospect'),
        ('customer', 'Customer'),
        ('partner', 'Partner'),
        ('vendor', 'Vendor'),
    ]

    TIER_CHOICES = [
        ('enterprise', 'Enterprise'),
        ('mid_market', 'Mid-Market'),
        ('smb', 'SMB'),
        ('starter', 'Starter'),
    ]

    COMPANY_SIZE_CHOICES = [
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('501-1000', '501-1000 employees'),
        ('1000+', '1000+ employees'),
    ]

    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=50, choices=COMPANY_SIZE_CHOICES, blank=True)
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    founded_year = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    logo_url = models.URLField(max_length=500, blank=True)
    website = models.URLField(max_length=500, blank=True)
    linkedin_url = models.URLField(max_length=500, blank=True)

    # Address Details
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    employee_count = models.IntegerField(null=True, blank=True)

    # Status & Classification
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPE_CHOICES, default='prospect')
    tier = models.CharField(max_length=50, choices=TIER_CHOICES, default='starter')
    health_score = models.IntegerField(default=100)

    # Multi-tenant and Ownership
    organization = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        related_name='crm_accounts',
        db_index=True
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_crm_accounts'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_crm_accounts'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_crm_accounts'
    )

    # Operational lifecycle and merge tracking
    is_active = models.BooleanField(default=True)
    is_merged = models.BooleanField(default=False)
    merged_into = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='merged_accounts'
    )

    custom_fields = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crm_accounts'
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'name'],
                name='unique_tenant_account_name'
            ),
        ]
        indexes = [
            models.Index(fields=['organization', 'name']),
            models.Index(fields=['organization', 'domain']),
            models.Index(fields=['organization', 'account_type']),
            models.Index(fields=['organization', 'is_active', 'is_merged']),
        ]

    def __str__(self):
        return f"{self.name} ({self.domain or 'No Domain'})"

    def clean(self):
        super().clean()
        if self.organization_id:
            for user_obj, field_name in [(self.assigned_to, 'assigned_to'), (self.owner, 'owner')]:
                if user_obj and not user_obj.is_superuser:
                    user_org = getattr(user_obj, 'organization', None)
                    if user_org and user_org.id != self.organization_id:
                        raise ValidationError({field_name: "User belongs to a different organization."})
                    elif not user_org and hasattr(user_obj, 'organization_memberships'):
                        has_membership = user_obj.organization_memberships.filter(
                            organization_id=self.organization_id,
                            is_active=True
                        ).exists()
                        if not has_membership:
                            raise ValidationError({field_name: "User is not a member of this organization."})

    def save(self, *args, **kwargs):
        if not self.organization_id:
            from multi_tenant.middleware import get_current_organization
            org = get_current_organization()
            if not org:
                user = self.created_by or self.owner or self.assigned_to
                if user:
                    org = getattr(user, 'organization', None)
                    if not org and hasattr(user, 'organization_memberships'):
                        membership = user.organization_memberships.filter(is_active=True).first()
                        if membership:
                            org = membership.organization
            if org:
                self.organization = org

        # Sync owner and assigned_to if one is missing
        if self.owner and not self.assigned_to:
            self.assigned_to = self.owner
        elif self.assigned_to and not self.owner:
            self.owner = self.assigned_to

        self.clean()
        super().save(*args, **kwargs)


class Contact(models.Model):
    """Contact model for storing customer/contact information with tenant boundaries"""
    CONTACT_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('prospect', 'Prospect'),
        ('vendor', 'Vendor'),
        ('partner', 'Partner'),
    ]

    SALUTATION_CHOICES = [
        ('mr', 'Mr.'),
        ('mrs', 'Mrs.'),
        ('ms', 'Ms.'),
        ('dr', 'Dr.'),
        ('prof', 'Prof.'),
    ]

    # Basic Information
    salutation = models.CharField(max_length=10, choices=SALUTATION_CHOICES, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=False)
    phone = models.CharField(max_length=30, blank=True)
    mobile = models.CharField(max_length=30, blank=True)

    # Company / Account Association
    account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contacts'
    )
    company_name = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)

    # Address Information
    address_line_1 = models.CharField(max_length=200, blank=True)
    address_line_2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)

    # CRM Information & Multi-Tenancy
    organization = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='contacts',
        db_index=True
    )
    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPE_CHOICES, default='prospect')
    lifecycle_stage = models.CharField(max_length=50, default='lead', blank=True)
    source = models.CharField(max_length=100, blank=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_contacts'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_contacts'
    )
    status = models.CharField(max_length=50, default='active')
    score = models.IntegerField(default=0)

    # Operational lifecycle and merge tracking
    is_merged = models.BooleanField(default=False)
    merged_into = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='merged_contacts'
    )

    # Social Media
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.CharField(max_length=100, blank=True)

    # Additional Information
    notes = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_contacts')

    class Meta:
        db_table = 'crm_contacts'
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'email']),
            models.Index(fields=['organization', 'company_name']),
            models.Index(fields=['organization', 'status', 'is_merged']),
            models.Index(fields=['organization', 'created_at']),
        ]

    def __init__(self, *args, **kwargs):
        company_arg = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        if company_arg and not self.company_name:
            self.company_name = company_arg

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def company(self):
        if self.account:
            return self.account.name
        return self.company_name

    @company.setter
    def company(self, value):
        self.company_name = value or ''

    def clean(self):
        super().clean()
        if self.organization_id:
            # Prevent associating contact with an account from another organization
            if self.account_id and self.account.organization_id != self.organization_id:
                raise ValidationError({'account': "Linked account belongs to a different organization."})
            # Prevent assigning to a user in another organization
            for user_obj, field_name in [(self.assigned_to, 'assigned_to'), (self.owner, 'owner')]:
                if user_obj and not user_obj.is_superuser:
                    user_org = getattr(user_obj, 'organization', None)
                    if user_org and user_org.id != self.organization_id:
                        raise ValidationError({field_name: "Assigned user belongs to a different organization."})
                    elif not user_org and hasattr(user_obj, 'organization_memberships'):
                        has_membership = user_obj.organization_memberships.filter(
                            organization_id=self.organization_id,
                            is_active=True
                        ).exists()
                        if not has_membership:
                            raise ValidationError({field_name: "Assigned user is not a member of this organization."})

    def save(self, *args, **kwargs):
        if not self.organization_id:
            from multi_tenant.middleware import get_current_organization
            org = get_current_organization()
            if not org and self.account_id:
                org = self.account.organization
            if not org:
                user = self.created_by or self.assigned_to or self.owner
                if user:
                    org = getattr(user, 'organization', None)
                    if not org and hasattr(user, 'organization_memberships'):
                        membership = user.organization_memberships.filter(is_active=True).first()
                        if membership:
                            org = membership.organization
            if org:
                self.organization = org

        # Sync owner and assigned_to
        if self.owner and not self.assigned_to:
            self.assigned_to = self.owner
        elif self.assigned_to and not self.owner:
            self.owner = self.assigned_to

        # Sync company_name with account name if account present and company_name empty
        if self.account and not self.company_name:
            self.company_name = self.account.name

        self.clean()
        super().save(*args, **kwargs)


class ContactActivity(models.Model):
    """Activity logs specifically attached to a Contact"""
    ACTIVITY_TYPE_CHOICES = [
        ('note', 'Note'),
        ('call', 'Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('task', 'Task'),
    ]

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES, default='note')
    content = models.TextField()
    subject = models.CharField(max_length=255, blank=True)
    duration = models.IntegerField(null=True, blank=True, help_text="Duration in minutes")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contact_activities')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'crm_contact_activities'
        verbose_name = 'Contact Activity'
        verbose_name_plural = 'Contact Activities'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.activity_type.title()} on {self.contact} at {self.created_at}"


class ContactGroup(models.Model):
    """Groups for organizing contacts within an organization"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    organization = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='contact_groups'
    )
    contacts = models.ManyToManyField(Contact, blank=True, related_name='groups')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crm_contact_groups'
        verbose_name = 'Contact Group'
        verbose_name_plural = 'Contact Groups'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.organization_id and self.created_by:
            org = getattr(self.created_by, 'organization', None)
            if not org and hasattr(self.created_by, 'organization_memberships'):
                m = self.created_by.organization_memberships.filter(is_active=True).first()
                if m:
                    org = m.organization
            if org:
                self.organization = org
        super().save(*args, **kwargs)


class ContactImport(models.Model):
    """Track contact/account bulk imports"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    RESOURCE_CHOICES = [
        ('contacts', 'Contacts'),
        ('accounts', 'Accounts'),
    ]

    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500, blank=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_CHOICES, default='contacts')
    organization = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='crm_imports'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_records = models.IntegerField(default=0)
    processed_records = models.IntegerField(default=0)
    failed_records = models.IntegerField(default=0)
    error_log = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'crm_contact_imports'
        verbose_name = 'Contact Import'
        verbose_name_plural = 'Contact Imports'


class MergeAuditLog(models.Model):
    """Audit log tracking merge operations with rollback/unmerge capability"""
    ENTITY_CHOICES = [
        ('contact', 'Contact'),
        ('account', 'Account'),
    ]

    entity_type = models.CharField(max_length=20, choices=ENTITY_CHOICES)
    organization = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        related_name='crm_merge_logs',
        db_index=True
    )
    primary_id = models.IntegerField()
    secondary_id = models.IntegerField()
    secondary_snapshot = models.JSONField(
        default=dict,
        help_text="Snapshot of secondary entity prior to merge"
    )
    repointed_relations = models.JSONField(
        default=dict,
        help_text="Records repointed during merge (activities, opportunities, contacts)"
    )
    merged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performed_merges'
    )
    is_reverted = models.BooleanField(default=False)
    reverted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reverted_merges'
    )
    reverted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'crm_merge_audit_logs'
        verbose_name = 'Merge Audit Log'
        verbose_name_plural = 'Merge Audit Logs'
        ordering = ['-created_at']
