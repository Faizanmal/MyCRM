"""
Customer Success Hub Models
Post-sale customer management, health scoring, and retention
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class CustomerAccount(models.Model):
    """Customer accounts for post-sale management"""

    ACCOUNT_TIERS = [
        ('enterprise', 'Enterprise'),
        ('business', 'Business'),
        ('professional', 'Professional'),
        ('starter', 'Starter'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=200)

    # Linked contact (typically the primary business contact)
    primary_contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_accounts'
    )

    # Account details
    tier = models.CharField(max_length=20, choices=ACCOUNT_TIERS, default='professional')

    # Revenue
    arr = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Annual Recurring Revenue
    mrr = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Monthly
    contract_start = models.DateField(null=True, blank=True)
    contract_end = models.DateField(null=True, blank=True)

    # Ownership
    customer_success_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_accounts'
    )

    # Status
    is_active = models.BooleanField(default=True)

    # Onboarding
    onboarding_complete = models.BooleanField(default=False)
    onboarding_completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-arr']

    def __str__(self):
        return self.name

    @property
    def days_until_renewal(self):
        if not self.contract_end:
            return None
        delta = self.contract_end - timezone.now().date()
        return delta.days


class HealthScore(models.Model):
    """Customer health scores"""

    account = models.ForeignKey(
        CustomerAccount,
        on_delete=models.CASCADE,
        related_name='health_scores'
    )

    # Overall score (0-100)
    score = models.IntegerField()

    # Component scores
    usage_score = models.IntegerField(default=50)
    engagement_score = models.IntegerField(default=50)
    support_score = models.IntegerField(default=50)
    payment_score = models.IntegerField(default=100)
    sentiment_score = models.IntegerField(default=50)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('healthy', 'Healthy'),
            ('at_risk', 'At Risk'),
            ('critical', 'Critical'),
        ]
    )

    # Trends
    score_change_7d = models.IntegerField(default=0)
    score_change_30d = models.IntegerField(default=0)

    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-calculated_at']
        get_latest_by = 'calculated_at'

    def __str__(self):
        return f"{self.account.name}: {self.score} ({self.status})"


class HealthScoreConfig(models.Model):
    """Configuration for health score calculation"""

    name = models.CharField(max_length=100, default='Default')

    # Weights (should sum to 100)
    usage_weight = models.IntegerField(default=30)
    engagement_weight = models.IntegerField(default=25)
    support_weight = models.IntegerField(default=20)
    payment_weight = models.IntegerField(default=15)
    sentiment_weight = models.IntegerField(default=10)

    # Thresholds
    healthy_threshold = models.IntegerField(default=70)  # Score >= this is healthy
    critical_threshold = models.IntegerField(default=40)  # Score < this is critical

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CustomerMilestone(models.Model):
    """Track customer journey milestones"""

    MILESTONE_TYPES = [
        ('contract_signed', 'Contract Signed'),
        ('kickoff_complete', 'Kickoff Complete'),
        ('implementation_started', 'Implementation Started'),
        ('first_value', 'First Value Realized'),
        ('go_live', 'Go Live'),
        ('onboarding_complete', 'Onboarding Complete'),
        ('first_renewal', 'First Renewal'),
        ('expansion', 'Expansion'),
        ('reference', 'Became Reference'),
        ('advocate', 'Customer Advocate'),
        ('custom', 'Custom'),
    ]

    account = models.ForeignKey(
        CustomerAccount,
        on_delete=models.CASCADE,
        related_name='milestones'
    )

    milestone_type = models.CharField(max_length=30, choices=MILESTONE_TYPES)
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    target_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['target_date', 'created_at']

    def __str__(self):
        return f"{self.account.name}: {self.get_milestone_type_display()}"


class SuccessPlaybook(models.Model):
    """Playbooks for customer success scenarios"""

    TRIGGER_TYPES = [
        ('onboarding', 'New Customer Onboarding'),
        ('low_health', 'Low Health Score'),
        ('renewal_approaching', 'Renewal Approaching'),
        ('expansion_opportunity', 'Expansion Opportunity'),
        ('at_risk', 'At-Risk Customer'),
        ('champion_left', 'Champion Left'),
        ('no_engagement', 'No Recent Engagement'),
        ('manual', 'Manual Trigger'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    trigger_type = models.CharField(max_length=30, choices=TRIGGER_TYPES)

    # Trigger conditions
    trigger_conditions = models.JSONField(default=dict)

    # Target
    target_tiers = models.JSONField(default=list)  # Account tiers this applies to

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class PlaybookStep(models.Model):
    """Steps in a success playbook"""

    STEP_TYPES = [
        ('task', 'Create Task'),
        ('email', 'Send Email'),
        ('call', 'Schedule Call'),
        ('meeting', 'Schedule Meeting'),
        ('internal', 'Internal Action'),
        ('wait', 'Wait'),
    ]

    playbook = models.ForeignKey(
        SuccessPlaybook,
        on_delete=models.CASCADE,
        related_name='steps'
    )

    order = models.IntegerField(default=0)
    name = models.CharField(max_length=200)
    step_type = models.CharField(max_length=20, choices=STEP_TYPES)

    # Step details
    description = models.TextField(blank=True)
    email_template = models.TextField(blank=True)
    delay_days = models.IntegerField(default=0)  # Days after previous step

    is_required = models.BooleanField(default=True)

    class Meta:
        ordering = ['playbook', 'order']

    def __str__(self):
        return f"{self.playbook.name} - Step {self.order}: {self.name}"


class PlaybookExecution(models.Model):
    """Track playbook execution for an account"""

    account = models.ForeignKey(
        CustomerAccount,
        on_delete=models.CASCADE,
        related_name='playbook_executions'
    )
    playbook = models.ForeignKey(
        SuccessPlaybook,
        on_delete=models.CASCADE,
        related_name='executions'
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('paused', 'Paused'),
            ('canceled', 'Canceled'),
        ],
        default='active'
    )

    current_step = models.IntegerField(default=0)
    next_step_at = models.DateTimeField(null=True, blank=True)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.playbook.name} for {self.account.name}"


class CustomerNote(models.Model):
    """Notes about customer accounts"""

    NOTE_TYPES = [
        ('general', 'General'),
        ('meeting', 'Meeting Notes'),
        ('call', 'Call Notes'),
        ('risk', 'Risk Assessment'),
        ('feedback', 'Customer Feedback'),
        ('success', 'Success Story'),
    ]

    account = models.ForeignKey(
        CustomerAccount,
        on_delete=models.CASCADE,
        related_name='notes'
    )

    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default='general')
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()

    # Participants (for meetings/calls)
    participants = models.ManyToManyField(
        'contact_management.Contact',
        blank=True,
        related_name='customer_notes'
    )

    is_pinned = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"{self.account.name}: {self.title or self.get_note_type_display()}"


class RenewalOpportunity(models.Model):
    """Track renewals"""

    account = models.ForeignKey(
        CustomerAccount,
        on_delete=models.CASCADE,
        related_name='renewals'
    )

    # Dates
    renewal_date = models.DateField()

    # Values
    current_arr = models.DecimalField(max_digits=12, decimal_places=2)
    projected_arr = models.DecimalField(max_digits=12, decimal_places=2)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('upcoming', 'Upcoming'),
            ('in_progress', 'In Progress'),
            ('renewed', 'Renewed'),
            ('churned', 'Churned'),
            ('downgraded', 'Downgraded'),
        ],
        default='upcoming'
    )

    # Risk assessment
    risk_level = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='low'
    )
    risk_factors = models.JSONField(default=list)

    # Outcome
    final_arr = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    outcome_notes = models.TextField(blank=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='renewal_opportunities'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['renewal_date']

    def __str__(self):
        return f"{self.account.name} renewal - {self.renewal_date}"

    @property
    def projected_change(self):
        if self.current_arr:
            return self.projected_arr - self.current_arr
        return 0

    @property
    def projected_change_percent(self):
        if self.current_arr and self.current_arr > 0:
            return ((self.projected_arr - self.current_arr) / self.current_arr) * 100
        return 0


class ExpansionOpportunity(models.Model):
    """Track upsell/cross-sell opportunities"""

    EXPANSION_TYPES = [
        ('upsell', 'Upsell'),
        ('cross_sell', 'Cross-sell'),
        ('add_users', 'Add Users'),
        ('add_features', 'Add Features'),
        ('upgrade_tier', 'Upgrade Tier'),
    ]

    account = models.ForeignKey(
        CustomerAccount,
        on_delete=models.CASCADE,
        related_name='expansion_opportunities'
    )

    expansion_type = models.CharField(max_length=20, choices=EXPANSION_TYPES)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Value
    potential_arr_increase = models.DecimalField(max_digits=12, decimal_places=2)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('identified', 'Identified'),
            ('qualified', 'Qualified'),
            ('proposal', 'Proposal'),
            ('negotiation', 'Negotiation'),
            ('closed_won', 'Closed Won'),
            ('closed_lost', 'Closed Lost'),
        ],
        default='identified'
    )

    probability = models.IntegerField(default=50)  # 0-100
    target_close_date = models.DateField(null=True, blank=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='expansion_opportunities'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-potential_arr_increase']

    def __str__(self):
        return f"{self.account.name}: {self.name}"


class NPSSurvey(models.Model):
    """Net Promoter Score surveys"""

    account = models.ForeignKey(
        CustomerAccount,
        on_delete=models.CASCADE,
        related_name='nps_surveys'
    )
    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Score
    score = models.IntegerField(null=True, blank=True)  # 0-10
    feedback = models.TextField(blank=True)

    # Classification
    classification = models.CharField(
        max_length=10,
        choices=[
            ('promoter', 'Promoter'),  # 9-10
            ('passive', 'Passive'),  # 7-8
            ('detractor', 'Detractor'),  # 0-6
        ],
        blank=True
    )

    # Status
    sent_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.account.name}: NPS {self.score if self.score else 'pending'}"

    def save(self, *args, **kwargs):
        # Auto-classify based on score
        if self.score is not None:
            if self.score >= 9:
                self.classification = 'promoter'
            elif self.score >= 7:
                self.classification = 'passive'
            else:
                self.classification = 'detractor'
        super().save(*args, **kwargs)


class CustomerSuccessAnalytics(models.Model):
    """Aggregated CS metrics"""

    date = models.DateField()

    # Portfolio metrics
    total_accounts = models.IntegerField(default=0)
    total_arr = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Health distribution
    healthy_accounts = models.IntegerField(default=0)
    at_risk_accounts = models.IntegerField(default=0)
    critical_accounts = models.IntegerField(default=0)

    # NPS
    nps_score = models.IntegerField(null=True, blank=True)
    nps_responses = models.IntegerField(default=0)

    # Churn/Retention
    churned_accounts = models.IntegerField(default=0)
    churned_arr = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    retention_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    # Expansion
    expansion_arr = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ['date']
        ordering = ['-date']

    def __str__(self):
        return f"CS Analytics: {self.date}"
