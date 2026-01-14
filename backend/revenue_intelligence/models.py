"""
Revenue Intelligence Models
Premium features that Salesforce/HubSpot charge $$$$ for:
- Deal scoring & win probability
- Revenue forecasting with ML
- Pipeline health analytics
- Quota tracking & attainment
- Competitive intelligence
- Deal risk alerts
"""

import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

User = get_user_model()


class RevenueTarget(models.Model):
    """Sales quota and revenue targets - what Salesforce charges extra for"""

    PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    TARGET_TYPE_CHOICES = [
        ('revenue', 'Revenue'),
        ('deals', 'Deal Count'),
        ('new_business', 'New Business'),
        ('expansion', 'Expansion/Upsell'),
        ('renewal', 'Renewals'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='revenue_targets')

    # Target configuration
    target_type = models.CharField(max_length=20, choices=TARGET_TYPE_CHOICES, default='revenue')
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='monthly')

    # Time range
    start_date = models.DateField()
    end_date = models.DateField()

    # Target values
    target_amount = models.DecimalField(max_digits=15, decimal_places=2)
    stretch_target = models.DecimalField(max_digits=15, decimal_places=2, blank=True)

    # Actuals (updated via signals/tasks)
    achieved_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    pipeline_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    weighted_pipeline = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'revenue_targets'
        ordering = ['-start_date']
        unique_together = ['user', 'target_type', 'period', 'start_date']

    def __str__(self):
        return f"{self.user.username} - {self.get_target_type_display()} ({self.start_date})"

    @property
    def attainment_percentage(self):
        """Calculate quota attainment"""
        if self.target_amount == 0:
            return 0
        return round((self.achieved_amount / self.target_amount) * 100, 1)

    @property
    def gap_to_target(self):
        """Calculate gap to target"""
        return self.target_amount - self.achieved_amount

    @property
    def coverage_ratio(self):
        """Pipeline coverage ratio (industry standard: 3x is healthy)"""
        gap = self.gap_to_target
        if gap <= 0:
            return float('inf')
        return round(float(self.pipeline_amount / gap), 2) if gap > 0 else 0

    @property
    def forecast_attainment(self):
        """Predicted attainment based on weighted pipeline"""
        predicted = self.achieved_amount + self.weighted_pipeline
        if self.target_amount == 0:
            return 0
        return round((predicted / self.target_amount) * 100, 1)


class DealScore(models.Model):
    """AI-powered deal scoring - like Salesforce Einstein but free"""

    RISK_LEVELS = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.OneToOneField(
        'opportunity_management.Opportunity',
        on_delete=models.CASCADE,
        related_name='deal_score'
    )

    # Overall score (0-100)
    score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall deal health score 0-100"
    )

    # Win probability (ML-predicted)
    win_probability = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Risk assessment
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default='medium')
    risk_factors = models.JSONField(default=list, help_text="List of identified risk factors")

    # Score breakdown
    engagement_score = models.IntegerField(default=0)  # Contact engagement level
    timing_score = models.IntegerField(default=0)  # Deal velocity/timing
    stakeholder_score = models.IntegerField(default=0)  # Decision maker involvement
    activity_score = models.IntegerField(default=0)  # Recent activity level
    competitive_score = models.IntegerField(default=0)  # Competitive positioning

    # Insights
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    recommended_actions = models.JSONField(default=list)

    # Trend tracking
    score_trend = models.CharField(max_length=20, default='stable')  # improving, declining, stable
    previous_score = models.IntegerField(blank=True)

    # Timestamps
    calculated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'deal_scores'
        ordering = ['-score']

    def __str__(self):
        return f"Deal Score: {self.opportunity.name} - {self.score}/100"


class DealVelocity(models.Model):
    """Track deal progression speed - premium analytics feature"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.CASCADE,
        related_name='velocity_records'
    )

    # Stage transition
    from_stage = models.CharField(max_length=50)
    to_stage = models.CharField(max_length=50)

    # Timing
    transition_date = models.DateTimeField(default=timezone.now)
    days_in_stage = models.IntegerField(help_text="Days spent in previous stage")

    # Benchmarks
    avg_days_for_stage = models.IntegerField(help_text="Average days in this stage")
    is_on_track = models.BooleanField(default=True)

    # Context
    triggered_by = models.ForeignKey(User, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'deal_velocity'
        ordering = ['-transition_date']

    def __str__(self):
        return f"{self.opportunity.name}: {self.from_stage} → {self.to_stage}"


class PipelineSnapshot(models.Model):
    """Daily pipeline snapshots for historical analysis"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Snapshot date
    snapshot_date = models.DateField(default=timezone.now)

    # User/Team level
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    team = models.CharField(max_length=100, blank=True)

    # Pipeline metrics
    total_pipeline = models.DecimalField(max_digits=15, decimal_places=2)
    weighted_pipeline = models.DecimalField(max_digits=15, decimal_places=2)
    deal_count = models.IntegerField()

    # Stage breakdown
    stage_breakdown = models.JSONField(default=dict)

    # Movement
    new_pipeline = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    moved_forward = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    moved_backward = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    closed_won = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    closed_lost = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Calculated metrics
    avg_deal_size = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    avg_days_to_close = models.IntegerField(default=0)
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pipeline_snapshots'
        ordering = ['-snapshot_date']
        unique_together = ['snapshot_date', 'user']

    def __str__(self):
        return f"Pipeline Snapshot: {self.snapshot_date}"


class Competitor(models.Model):
    """Competitive intelligence tracking"""

    THREAT_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)

    # Competitive analysis
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    pricing_info = models.TextField(blank=True)

    # Threat assessment
    threat_level = models.CharField(max_length=20, choices=THREAT_LEVELS, default='medium')
    market_share = models.DecimalField(max_digits=5, decimal_places=2)

    # Win/Loss against this competitor
    deals_won_against = models.IntegerField(default=0)
    deals_lost_to = models.IntegerField(default=0)

    # Battle cards
    differentiators = models.JSONField(default=list, help_text="Our advantages")
    objection_handlers = models.JSONField(default=list)

    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'competitors'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def win_rate_against(self):
        """Win rate against this competitor"""
        total = self.deals_won_against + self.deals_lost_to
        if total == 0:
            return 0
        return round((self.deals_won_against / total) * 100, 1)


class DealCompetitor(models.Model):
    """Track competitors in specific deals"""

    STATUS_CHOICES = [
        ('active', 'Actively Competing'),
        ('eliminated', 'Eliminated'),
        ('won', 'We Won'),
        ('lost', 'Lost to Them'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.CASCADE,
        related_name='competitors'
    )
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    threat_level = models.CharField(max_length=20, choices=Competitor.THREAT_LEVELS, default='medium')

    # Intelligence
    known_pricing = models.TextField(blank=True)
    strengths_in_deal = models.JSONField(default=list)
    weaknesses_in_deal = models.JSONField(default=list)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'deal_competitors'
        unique_together = ['opportunity', 'competitor']

    def __str__(self):
        return f"{self.opportunity.name} vs {self.competitor.name}"


class RevenueForecast(models.Model):
    """ML-powered revenue forecasting"""

    FORECAST_TYPES = [
        ('commit', 'Commit'),
        ('best_case', 'Best Case'),
        ('pipeline', 'Pipeline'),
        ('ai_predicted', 'AI Predicted'),
    ]

    CONFIDENCE_LEVELS = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Time period
    forecast_date = models.DateField()
    period_start = models.DateField()
    period_end = models.DateField()

    # User/Team
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    team = models.CharField(max_length=100, blank=True)

    # Forecast values
    forecast_type = models.CharField(max_length=20, choices=FORECAST_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    confidence = models.CharField(max_length=20, choices=CONFIDENCE_LEVELS, default='medium')

    # AI insights
    ai_adjustment = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    adjustment_reasons = models.JSONField(default=list)

    # Breakdown
    closed_won = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    expected_closes = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    at_risk_deals = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Accuracy tracking (for completed periods)
    actual_amount = models.DecimalField(max_digits=15, decimal_places=2)
    accuracy_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'revenue_forecasts'
        ordering = ['-forecast_date', '-period_start']

    def __str__(self):
        return f"Forecast: {self.get_forecast_type_display()} - {self.period_start} to {self.period_end}"


class DealRiskAlert(models.Model):
    """Automated deal risk alerts"""

    ALERT_TYPES = [
        ('stale_deal', 'Stale Deal - No Activity'),
        ('slipping_close', 'Close Date Slipping'),
        ('engagement_drop', 'Engagement Dropped'),
        ('competitor_threat', 'Competitor Threat'),
        ('stakeholder_change', 'Stakeholder Change'),
        ('budget_concern', 'Budget Concerns'),
        ('timeline_risk', 'Timeline at Risk'),
        ('champion_left', 'Champion Left Company'),
    ]

    SEVERITY_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.CASCADE,
        related_name='risk_alerts'
    )

    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='warning')

    title = models.CharField(max_length=200)
    description = models.TextField()
    recommended_action = models.TextField()

    # Status
    is_active = models.BooleanField(default=True)
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True)
    acknowledged_at = models.DateTimeField(blank=True)

    # Resolution
    is_resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'deal_risk_alerts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_alert_type_display()}: {self.opportunity.name}"
