"""
Territory & Quota Management Models
Dynamic territory assignment and quota planning
"""

import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Territory(models.Model):
    """Sales territory definitions"""

    TERRITORY_TYPES = [
        ('geographic', 'Geographic'),
        ('industry', 'Industry'),
        ('company_size', 'Company Size'),
        ('account_based', 'Account Based'),
        ('hybrid', 'Hybrid'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    territory_type = models.CharField(max_length=20, choices=TERRITORY_TYPES, default='geographic')

    # Hierarchy
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='sub_territories'
    )
    level = models.IntegerField(default=0)  # 0 = top level

    # Geographic boundaries
    regions = models.JSONField(default=list)  # ['US-CA', 'US-NV']
    countries = models.JSONField(default=list)
    zip_codes = models.JSONField(default=list)

    # Industry criteria
    industries = models.JSONField(default=list)

    # Company size criteria
    min_employees = models.IntegerField(null=True, blank=True)
    max_employees = models.IntegerField(null=True, blank=True)
    min_revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    max_revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    # Assignment
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='owned_territories'
    )
    team_members = models.ManyToManyField(User, blank=True, related_name='territories')

    # Capacity
    max_accounts = models.IntegerField(null=True, blank=True)
    current_accounts = models.IntegerField(default=0)
    max_opportunities = models.IntegerField(null=True, blank=True)
    current_opportunities = models.IntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)

    # Metrics
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_pipeline = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    win_rate = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'territories'
        ordering = ['level', 'name']
        verbose_name_plural = 'territories'

    def __str__(self):
        return f"{self.name} ({self.code})"


class TerritoryAssignmentRule(models.Model):
    """Rules for automatic territory assignment"""

    MATCH_TYPE = [
        ('all', 'Match All Conditions'),
        ('any', 'Match Any Condition'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    territory = models.ForeignKey(Territory, on_delete=models.CASCADE, related_name='assignment_rules')

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    match_type = models.CharField(max_length=10, choices=MATCH_TYPE, default='all')

    # Conditions
    conditions = models.JSONField(default=list, help_text="""
        [
            {"field": "country", "operator": "equals", "value": "US"},
            {"field": "industry", "operator": "in", "value": ["Technology", "SaaS"]},
            {"field": "employees", "operator": "between", "value": [100, 500]}
        ]
    """)

    # Priority
    priority = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    # Stats
    matches_count = models.IntegerField(default=0)
    last_matched_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'territory_assignment_rules'
        ordering = ['-priority']

    def __str__(self):
        return f"{self.name} -> {self.territory.name}"


class TerritoryRebalanceRequest(models.Model):
    """Requests for territory rebalancing"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('analyzing', 'Analyzing'),
        ('ready', 'Ready for Review'),
        ('approved', 'Approved'),
        ('applied', 'Applied'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='rebalance_requests')

    # Scope
    territories = models.ManyToManyField(Territory, related_name='rebalance_requests')

    # Reason
    reason = models.TextField()
    optimization_goals = models.JSONField(default=list)  # ['balance_workload', 'maximize_coverage', 'minimize_travel']

    # Analysis results
    current_state = models.JSONField(default=dict)
    proposed_changes = models.JSONField(default=list)
    impact_analysis = models.JSONField(default=dict)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Approval
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reviewed_rebalance_requests'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    applied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'territory_rebalance_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"Rebalance Request {self.id} - {self.status}"


class QuotaPeriod(models.Model):
    """Quota periods (fiscal quarters, years)"""

    PERIOD_TYPES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200)
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPES, default='quarterly')

    start_date = models.DateField()
    end_date = models.DateField()

    # Settings
    is_active = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'quota_periods'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"


class Quota(models.Model):
    """Individual quota assignments"""

    QUOTA_TYPES = [
        ('revenue', 'Revenue'),
        ('bookings', 'Bookings'),
        ('arr', 'Annual Recurring Revenue'),
        ('units', 'Units'),
        ('deals', 'Deal Count'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    period = models.ForeignKey(QuotaPeriod, on_delete=models.CASCADE, related_name='quotas')

    # Assignment (can be user, territory, or team)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='quotas'
    )
    territory = models.ForeignKey(
        Territory, on_delete=models.CASCADE, null=True, blank=True,
        related_name='quotas'
    )

    quota_type = models.CharField(max_length=20, choices=QUOTA_TYPES, default='revenue')

    # Quota values
    target = models.DecimalField(max_digits=15, decimal_places=2)
    stretch_target = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    # Achievement
    achieved = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    attainment_percentage = models.FloatField(default=0)

    # Forecasting
    forecast = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    forecast_attainment = models.FloatField(default=0)

    # Historical context
    previous_period_achieved = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    yoy_growth_target = models.FloatField(null=True)

    # AI recommendations
    ai_recommended_target = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    ai_confidence = models.FloatField(null=True)
    ai_factors = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quotas'
        ordering = ['-period__start_date']

    def __str__(self):
        assignee = self.user.username if self.user else self.territory.name
        return f"{assignee} - {self.period.name}: {self.target}"


class QuotaAdjustment(models.Model):
    """Quota adjustments and changes"""

    ADJUSTMENT_TYPES = [
        ('increase', 'Increase'),
        ('decrease', 'Decrease'),
        ('reallocation', 'Reallocation'),
        ('correction', 'Correction'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    quota = models.ForeignKey(Quota, on_delete=models.CASCADE, related_name='adjustments')

    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPES)

    # Values
    old_target = models.DecimalField(max_digits=15, decimal_places=2)
    new_target = models.DecimalField(max_digits=15, decimal_places=2)
    difference = models.DecimalField(max_digits=15, decimal_places=2)

    # Reason
    reason = models.TextField()

    # Approval
    requested_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='quota_adjustment_requests'
    )
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_quota_adjustments'
    )
    is_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'quota_adjustments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Adjustment for {self.quota}: {self.difference}"


class TerritoryPerformance(models.Model):
    """Territory performance snapshots"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    territory = models.ForeignKey(Territory, on_delete=models.CASCADE, related_name='performance_records')
    period = models.ForeignKey(QuotaPeriod, on_delete=models.CASCADE, related_name='territory_performance')

    # Metrics
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_pipeline = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    new_opportunities = models.IntegerField(default=0)
    closed_won = models.IntegerField(default=0)
    closed_lost = models.IntegerField(default=0)

    # Rates
    win_rate = models.FloatField(default=0)
    conversion_rate = models.FloatField(default=0)
    avg_deal_size = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    avg_sales_cycle = models.IntegerField(default=0)  # days

    # Capacity
    accounts_count = models.IntegerField(default=0)
    active_opportunities = models.IntegerField(default=0)
    rep_count = models.IntegerField(default=0)

    # Quota
    quota_target = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    quota_achieved = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    quota_attainment = models.FloatField(default=0)

    # AI insights
    health_score = models.IntegerField(default=0)  # 0-100
    risk_factors = models.JSONField(default=list)
    opportunities_at_risk = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)

    snapshot_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'territory_performance'
        ordering = ['-snapshot_date']
        unique_together = ['territory', 'period', 'snapshot_date']

    def __str__(self):
        return f"{self.territory.name} - {self.period.name}"
