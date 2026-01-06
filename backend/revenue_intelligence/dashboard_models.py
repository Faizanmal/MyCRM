"""
Revenue Intelligence Dashboard Models
"""

import uuid

from django.conf import settings
from django.db import models


class RevenueForecast(models.Model):
    """AI-powered revenue forecasting"""

    FORECAST_TYPES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
    ]

    CONFIDENCE_LEVELS = [
        ('commit', 'Commit'),
        ('best_case', 'Best Case'),
        ('worst_case', 'Worst Case'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='revenue_forecasts'
    )

    # Forecast period
    forecast_type = models.CharField(max_length=20, choices=FORECAST_TYPES)
    period_start = models.DateField()
    period_end = models.DateField()

    # Forecast values
    committed_revenue = models.DecimalField(max_digits=15, decimal_places=2)
    best_case_revenue = models.DecimalField(max_digits=15, decimal_places=2)
    worst_case_revenue = models.DecimalField(max_digits=15, decimal_places=2)

    # AI predictions
    predicted_revenue = models.DecimalField(max_digits=15, decimal_places=2)
    prediction_confidence = models.DecimalField(max_digits=5, decimal_places=2)

    # Pipeline breakdown
    pipeline_by_stage = models.JSONField(default=dict)
    weighted_pipeline = models.DecimalField(max_digits=15, decimal_places=2)

    # Factors
    positive_factors = models.JSONField(default=list)
    risk_factors = models.JSONField(default=list)

    # Historical comparison
    previous_period_actual = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    yoy_growth_rate = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )

    # Tracking
    actual_revenue = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    accuracy_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'revenue_forecasts'
        ordering = ['-period_start']
        unique_together = ['user', 'forecast_type', 'period_start']

    def __str__(self):
        return f"{self.forecast_type} forecast: {self.period_start}"


class CohortAnalysis(models.Model):
    """Customer cohort analysis"""

    COHORT_TYPES = [
        ('acquisition_month', 'Acquisition Month'),
        ('acquisition_quarter', 'Acquisition Quarter'),
        ('product', 'Product'),
        ('industry', 'Industry'),
        ('size', 'Company Size'),
        ('source', 'Lead Source'),
    ]

    METRIC_TYPES = [
        ('retention', 'Retention Rate'),
        ('revenue', 'Revenue'),
        ('ltv', 'Lifetime Value'),
        ('churn', 'Churn Rate'),
        ('expansion', 'Expansion Revenue'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cohort_analyses'
    )

    # Cohort definition
    cohort_type = models.CharField(max_length=30, choices=COHORT_TYPES)
    cohort_name = models.CharField(max_length=200)
    cohort_date = models.DateField()

    # Metric being tracked
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES)

    # Cohort data
    cohort_size = models.IntegerField()

    # Periodic values (month 0, 1, 2, etc.)
    periodic_values = models.JSONField(default=list)

    # Aggregate metrics
    avg_value = models.DecimalField(max_digits=15, decimal_places=2)
    total_value = models.DecimalField(max_digits=15, decimal_places=2)

    # Comparison
    benchmark_avg = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    vs_benchmark = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cohort_analyses'
        ordering = ['-cohort_date']

    def __str__(self):
        return f"{self.cohort_type}: {self.cohort_name} - {self.metric_type}"


class RevenueAttribution(models.Model):
    """Multi-touch revenue attribution"""

    ATTRIBUTION_MODELS = [
        ('first_touch', 'First Touch'),
        ('last_touch', 'Last Touch'),
        ('linear', 'Linear'),
        ('time_decay', 'Time Decay'),
        ('position_based', 'Position Based'),
        ('data_driven', 'Data Driven'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='revenue_attributions'
    )

    # Deal reference
    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.CASCADE,
        related_name='attributions'
    )

    # Attribution model
    model = models.CharField(max_length=30, choices=ATTRIBUTION_MODELS)

    # Revenue
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2)

    # Touchpoints with attribution
    touchpoints = models.JSONField(default=list)
    """
    [
        {
            'channel': 'organic_search',
            'source': 'google',
            'campaign': null,
            'timestamp': '2024-01-15T10:00:00Z',
            'is_first_touch': true,
            'is_last_touch': false,
            'attributed_revenue': 5000.00,
            'attribution_weight': 0.4
        },
        ...
    ]
    """

    # Channel summary
    channel_attribution = models.JSONField(default=dict)
    """
    {
        'organic_search': 5000.00,
        'email': 3000.00,
        'paid_social': 2000.00
    }
    """

    # Campaign summary
    campaign_attribution = models.JSONField(default=dict)

    # Time to conversion
    days_to_conversion = models.IntegerField()
    touchpoint_count = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'revenue_attributions'
        unique_together = ['opportunity', 'model']

    def __str__(self):
        return f"{self.model}: {self.opportunity}"


class SalesVelocity(models.Model):
    """Track sales velocity metrics"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sales_velocities'
    )

    # Period
    period_start = models.DateField()
    period_end = models.DateField()

    # Core velocity metrics
    num_opportunities = models.IntegerField()
    avg_deal_value = models.DecimalField(max_digits=15, decimal_places=2)
    win_rate = models.DecimalField(max_digits=5, decimal_places=2)
    avg_sales_cycle_days = models.IntegerField()

    # Calculated velocity
    # Velocity = (Opportunities × Deal Value × Win Rate) / Sales Cycle
    sales_velocity = models.DecimalField(max_digits=15, decimal_places=2)

    # Breakdown by stage
    stage_metrics = models.JSONField(default=dict)
    """
    {
        'qualification': {
            'count': 50,
            'avg_days': 5,
            'conversion_rate': 0.8
        },
        ...
    }
    """

    # Trends
    velocity_change = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    velocity_trend = models.CharField(max_length=20, blank=True)  # up, down, stable

    # Bottlenecks
    bottleneck_stage = models.CharField(max_length=100, blank=True)
    bottleneck_impact = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sales_velocities'
        ordering = ['-period_start']

    def __str__(self):
        return f"Velocity: {self.period_start} - {self.period_end}"


class RevenueLeakage(models.Model):
    """Track revenue leakage and optimization opportunities"""

    LEAKAGE_TYPES = [
        ('discount_overuse', 'Discount Overuse'),
        ('pricing_inconsistency', 'Pricing Inconsistency'),
        ('stalled_deals', 'Stalled Deals'),
        ('lost_upsells', 'Lost Upsells'),
        ('churn', 'Churn'),
        ('late_renewals', 'Late Renewals'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='revenue_leakages'
    )

    # Period
    period_start = models.DateField()
    period_end = models.DateField()

    # Leakage type
    leakage_type = models.CharField(max_length=30, choices=LEAKAGE_TYPES)

    # Impact
    potential_revenue = models.DecimalField(max_digits=15, decimal_places=2)
    lost_revenue = models.DecimalField(max_digits=15, decimal_places=2)
    recoverable_revenue = models.DecimalField(max_digits=15, decimal_places=2)

    # Details
    affected_deals = models.JSONField(default=list)
    root_causes = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)

    # Trend
    vs_previous_period = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'revenue_leakages'
        ordering = ['-lost_revenue']

    def __str__(self):
        return f"{self.leakage_type}: ${self.lost_revenue}"


class WinLossAnalysis(models.Model):
    """Analyze win/loss patterns"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='win_loss_analyses'
    )

    # Period
    period_start = models.DateField()
    period_end = models.DateField()

    # Overall metrics
    total_opportunities = models.IntegerField()
    total_won = models.IntegerField()
    total_lost = models.IntegerField()
    total_open = models.IntegerField()

    win_rate = models.DecimalField(max_digits=5, decimal_places=2)

    won_value = models.DecimalField(max_digits=15, decimal_places=2)
    lost_value = models.DecimalField(max_digits=15, decimal_places=2)

    # Win patterns
    win_factors = models.JSONField(default=list)
    """
    [
        {'factor': 'Champion identified', 'correlation': 0.85, 'count': 45},
        ...
    ]
    """

    # Loss patterns
    loss_reasons = models.JSONField(default=list)
    """
    [
        {'reason': 'Price too high', 'count': 20, 'percentage': 0.35, 'value': 500000},
        ...
    ]
    """

    # Competitor analysis
    competitor_wins = models.JSONField(default=dict)
    """
    {
        'Competitor A': {'losses': 10, 'value': 200000},
        ...
    }
    """

    # Segment analysis
    by_segment = models.JSONField(default=dict)
    by_industry = models.JSONField(default=dict)
    by_deal_size = models.JSONField(default=dict)
    by_rep = models.JSONField(default=dict)

    # Insights
    key_insights = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'win_loss_analyses'
        ordering = ['-period_start']

    def __str__(self):
        return f"Win/Loss: {self.period_start} - {self.period_end}"


class ARRMovement(models.Model):
    """Track ARR movements (SaaS metrics)"""

    MOVEMENT_TYPES = [
        ('new', 'New Business'),
        ('expansion', 'Expansion'),
        ('contraction', 'Contraction'),
        ('churn', 'Churn'),
        ('reactivation', 'Reactivation'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='arr_movements'
    )

    # Period
    period = models.DateField()  # First day of month

    # Opening ARR
    opening_arr = models.DecimalField(max_digits=15, decimal_places=2)

    # Movements
    new_business = models.DecimalField(max_digits=15, decimal_places=2)
    expansion = models.DecimalField(max_digits=15, decimal_places=2)
    contraction = models.DecimalField(max_digits=15, decimal_places=2)
    churn = models.DecimalField(max_digits=15, decimal_places=2)
    reactivation = models.DecimalField(max_digits=15, decimal_places=2)

    # Closing ARR
    closing_arr = models.DecimalField(max_digits=15, decimal_places=2)

    # Net movement
    net_movement = models.DecimalField(max_digits=15, decimal_places=2)

    # Growth rates
    gross_retention = models.DecimalField(max_digits=5, decimal_places=2)
    net_retention = models.DecimalField(max_digits=5, decimal_places=2)

    # Details
    movement_details = models.JSONField(default=dict)
    """
    {
        'new': [{'customer': 'Acme', 'arr': 50000}, ...],
        'churn': [{'customer': 'Beta', 'arr': 20000, 'reason': 'Budget'}, ...],
        ...
    }
    """

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'arr_movements'
        ordering = ['-period']
        unique_together = ['user', 'period']

    def __str__(self):
        return f"ARR: {self.period}"


class RevenueIntelligenceSnapshot(models.Model):
    """Daily snapshot of revenue intelligence metrics"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='revenue_snapshots'
    )

    snapshot_date = models.DateField()

    # Pipeline metrics
    total_pipeline = models.DecimalField(max_digits=15, decimal_places=2)
    weighted_pipeline = models.DecimalField(max_digits=15, decimal_places=2)
    pipeline_coverage = models.DecimalField(max_digits=5, decimal_places=2)

    # Forecast
    current_quarter_forecast = models.DecimalField(max_digits=15, decimal_places=2)
    current_quarter_closed = models.DecimalField(max_digits=15, decimal_places=2)
    current_quarter_target = models.DecimalField(max_digits=15, decimal_places=2)

    # Velocity
    current_velocity = models.DecimalField(max_digits=15, decimal_places=2)
    avg_deal_size = models.DecimalField(max_digits=15, decimal_places=2)
    avg_sales_cycle = models.IntegerField()
    win_rate = models.DecimalField(max_digits=5, decimal_places=2)

    # Health indicators
    at_risk_deals_count = models.IntegerField()
    at_risk_deals_value = models.DecimalField(max_digits=15, decimal_places=2)
    stalled_deals_count = models.IntegerField()
    stalled_deals_value = models.DecimalField(max_digits=15, decimal_places=2)

    # Trends
    pipeline_trend_7d = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    forecast_trend_7d = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'revenue_intelligence_snapshots'
        ordering = ['-snapshot_date']
        unique_together = ['user', 'snapshot_date']

    def __str__(self):
        return f"Revenue Snapshot: {self.snapshot_date}"
