"""
White Label and Subscription Billing Models
Enable agencies/partners to resell the CRM with their own branding
"""

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class WhiteLabelPartner(models.Model):
    """Partners who can white-label the CRM"""

    PARTNER_TYPES = [
        ('agency', 'Marketing Agency'),
        ('consultant', 'Consultant'),
        ('reseller', 'Reseller'),
        ('enterprise', 'Enterprise'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=200)
    partner_type = models.CharField(max_length=20, choices=PARTNER_TYPES)

    # Contact info
    contact_email = models.EmailField()
    contact_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)

    # Admin users for this partner
    admin_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='partner_admin_of'
    )

    # Branding
    brand_name = models.CharField(max_length=200)  # What to call the CRM
    subdomain = models.CharField(max_length=100, unique=True)  # partner.mycrm.com
    custom_domain = models.CharField(max_length=200, blank=True)  # crm.partner.com

    # Logo and colors
    logo = models.ImageField(upload_to='partners/logos/', blank=True)
    logo_dark = models.ImageField(upload_to='partners/logos/', blank=True)
    favicon = models.ImageField(upload_to='partners/favicons/', blank=True)
    primary_color = models.CharField(max_length=7, default='#2563eb')
    secondary_color = models.CharField(max_length=7, default='#1e40af')
    accent_color = models.CharField(max_length=7, default='#3b82f6')

    # Custom CSS
    custom_css = models.TextField(blank=True)

    # Email settings
    email_from_name = models.CharField(max_length=200, blank=True)
    email_from_address = models.EmailField(blank=True)
    email_footer_text = models.TextField(blank=True)

    # Support info shown to end users
    support_email = models.EmailField(blank=True)
    support_url = models.URLField(blank=True)

    # Features
    hide_powered_by = models.BooleanField(default=False)
    allow_custom_domain = models.BooleanField(default=False)

    # Commission settings
    revenue_share_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=20,
        validators=[MinValueValidator(Decimal('0'))]
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SubscriptionPlan(models.Model):
    """Available subscription plans"""

    BILLING_PERIODS = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('lifetime', 'Lifetime'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_period = models.CharField(max_length=10, choices=BILLING_PERIODS)

    # Per-user pricing (optional)
    price_per_user = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Additional cost per user beyond included users"
    )
    included_users = models.IntegerField(default=1)

    # Trial
    trial_days = models.IntegerField(default=14)

    # Features
    features = models.JSONField(default=dict)  # Feature flags

    # Limits
    max_users = models.IntegerField(default=5)
    max_contacts = models.IntegerField(default=1000)
    max_storage_gb = models.IntegerField(default=5)
    max_emails_per_month = models.IntegerField(default=1000)
    max_api_calls_per_day = models.IntegerField(default=5000)

    # Partner-specific plan
    partner = models.ForeignKey(
        WhiteLabelPartner,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='custom_plans'
    )

    # Stripe/Payment integration
    stripe_price_id = models.CharField(max_length=100, blank=True)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'price']

    def __str__(self):
        return f"{self.name} (${self.price}/{self.billing_period})"


class Organization(models.Model):
    """Customer organizations (tenants)"""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    # Ownership
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owned_organizations'
    )

    # White-label relationship
    partner = models.ForeignKey(
        WhiteLabelPartner,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organizations'
    )

    # Subscription
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='organizations'
    )
    subscription_status = models.CharField(
        max_length=20,
        choices=[
            ('trialing', 'Trialing'),
            ('active', 'Active'),
            ('past_due', 'Past Due'),
            ('canceled', 'Canceled'),
            ('expired', 'Expired'),
        ],
        default='trialing'
    )

    # Trial
    trial_ends_at = models.DateTimeField(blank=True)

    # Billing
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    current_period_ends_at = models.DateTimeField(blank=True)

    # Usage tracking
    current_users = models.IntegerField(default=1)
    current_contacts = models.IntegerField(default=0)
    current_storage_bytes = models.BigIntegerField(default=0)

    # Settings
    timezone = models.CharField(max_length=50, default='UTC')
    date_format = models.CharField(max_length=20, default='YYYY-MM-DD')
    currency = models.CharField(max_length=3, default='USD')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def is_on_trial(self):
        if self.subscription_status != 'trialing':
            return False
        if not self.trial_ends_at:
            return False
        return timezone.now() < self.trial_ends_at

    @property
    def days_remaining_trial(self):
        if not self.is_on_trial:
            return 0
        delta = self.trial_ends_at - timezone.now()
        return max(0, delta.days)


class OrganizationMember(models.Model):
    """Members of an organization"""

    ROLES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('user', 'User'),
        ('readonly', 'Read Only'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wl_organization_memberships'
    )
    role = models.CharField(max_length=20, choices=ROLES, default='user')

    # Permissions
    can_manage_users = models.BooleanField(default=False)
    can_manage_billing = models.BooleanField(default=False)
    can_export_data = models.BooleanField(default=False)
    can_delete_data = models.BooleanField(default=False)

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='wl_invitations_sent'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['organization', 'user']
        ordering = ['role', 'joined_at']

    def __str__(self):
        return f"{self.user.email} @ {self.organization.name}"


class Invoice(models.Model):
    """Invoices for organizations"""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('void', 'Void'),
        ('refunded', 'Refunded'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    invoice_number = models.CharField(max_length=50, unique=True)

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='invoices'
    )

    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    currency = models.CharField(max_length=3, default='USD')

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Dates
    issued_at = models.DateTimeField(blank=True)
    due_at = models.DateTimeField(blank=True)
    paid_at = models.DateTimeField(blank=True)

    # Period
    period_start = models.DateField()
    period_end = models.DateField()

    # Stripe
    stripe_invoice_id = models.CharField(max_length=100, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)

    # PDF
    pdf_url = models.URLField(blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issued_at']

    def __str__(self):
        return f"Invoice {self.invoice_number}"


class InvoiceLineItem(models.Model):
    """Line items on an invoice"""

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='line_items'
    )

    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Related plan
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.description


class PaymentMethod(models.Model):
    """Stored payment methods"""

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )

    # Stripe
    stripe_payment_method_id = models.CharField(max_length=100)

    # Card details (tokenized)
    card_brand = models.CharField(max_length=20)  # visa, mastercard, etc.
    card_last4 = models.CharField(max_length=4)
    card_exp_month = models.IntegerField()
    card_exp_year = models.IntegerField()

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.card_brand} ****{self.card_last4}"


class UsageRecord(models.Model):
    """Track usage for metered billing"""

    USAGE_TYPES = [
        ('users', 'Active Users'),
        ('contacts', 'Contacts'),
        ('storage', 'Storage (bytes)'),
        ('emails', 'Emails Sent'),
        ('api_calls', 'API Calls'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='usage_records'
    )

    usage_type = models.CharField(max_length=20, choices=USAGE_TYPES)
    quantity = models.BigIntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.organization.name} - {self.usage_type}: {self.quantity}"


class PartnerPayout(models.Model):
    """Track partner revenue share payouts"""

    partner = models.ForeignKey(
        WhiteLabelPartner,
        on_delete=models.CASCADE,
        related_name='payouts'
    )

    # Period
    period_start = models.DateField()
    period_end = models.DateField()

    # Amounts
    gross_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('paid', 'Paid'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )

    paid_at = models.DateTimeField(blank=True)
    stripe_transfer_id = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-period_end']

    def __str__(self):
        return f"{self.partner.name} - {self.period_start} to {self.period_end}"


class FeatureFlag(models.Model):
    """Feature flags for plans and organizations"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    # Default state
    is_enabled_by_default = models.BooleanField(default=False)

    # Which plans have this feature
    enabled_for_plans = models.ManyToManyField(
        SubscriptionPlan,
        blank=True,
        related_name='feature_flags'
    )

    # Override for specific organizations
    enabled_for_orgs = models.ManyToManyField(
        Organization,
        blank=True,
        related_name='enabled_features'
    )
    disabled_for_orgs = models.ManyToManyField(
        Organization,
        blank=True,
        related_name='disabled_features'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def is_enabled_for(self, organization):
        """Check if feature is enabled for an organization"""
        # Check org-level override
        if self.disabled_for_orgs.filter(id=organization.id).exists():
            return False
        if self.enabled_for_orgs.filter(id=organization.id).exists():
            return True

        # Check plan
        if self.enabled_for_plans.filter(id=organization.plan_id).exists():
            return True

        return self.is_enabled_by_default
