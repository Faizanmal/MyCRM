"""
Revenue Intelligence Dashboard Serializers
"""

from rest_framework import serializers

from .dashboard_models import (
    ARRMovement,
    CohortAnalysis,
    RevenueAttribution,
    RevenueForecast,
    RevenueIntelligenceSnapshot,
    RevenueLeakage,
    SalesVelocity,
    WinLossAnalysis,
)


class RevenueForecastSerializer(serializers.ModelSerializer):
    """Serializer for RevenueForecast"""

    attainment_percentage = serializers.SerializerMethodField()
    gap_to_committed = serializers.SerializerMethodField()

    class Meta:
        model = RevenueForecast
        fields = [
            'id', 'forecast_type', 'period_start', 'period_end',
            'committed_revenue', 'best_case_revenue', 'worst_case_revenue',
            'predicted_revenue', 'prediction_confidence',
            'pipeline_by_stage', 'weighted_pipeline',
            'positive_factors', 'risk_factors',
            'previous_period_actual', 'yoy_growth_rate',
            'attainment_percentage', 'gap_to_committed',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_attainment_percentage(self, obj):
        if obj.predicted_revenue and obj.committed_revenue:
            return float(obj.committed_revenue / obj.predicted_revenue * 100)
        return 0

    def get_gap_to_committed(self, obj):
        if obj.predicted_revenue and obj.committed_revenue:
            return float(obj.predicted_revenue - obj.committed_revenue)
        return 0


class CohortAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for CohortAnalysis"""

    retention_rate = serializers.SerializerMethodField()

    class Meta:
        model = CohortAnalysis
        fields = [
            'id', 'cohort_type', 'cohort_name', 'cohort_date',
            'metric_type', 'cohort_size', 'periodic_values',
            'avg_value', 'total_value', 'comparison_baseline',
            'insights', 'retention_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_retention_rate(self, obj):
        if obj.periodic_values and len(obj.periodic_values) >= 2:
            first = obj.periodic_values[0]
            last = obj.periodic_values[-1]
            if first > 0:
                return float(last / first * 100)
        return None


class RevenueAttributionSerializer(serializers.ModelSerializer):
    """Serializer for RevenueAttribution"""

    opportunity_name = serializers.SerializerMethodField()
    top_channels = serializers.SerializerMethodField()

    class Meta:
        model = RevenueAttribution
        fields = [
            'id', 'opportunity', 'opportunity_name', 'model',
            'total_revenue', 'touchpoints', 'channel_attribution',
            'campaign_attribution', 'days_to_conversion',
            'touchpoint_count', 'top_channels',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_opportunity_name(self, obj):
        return obj.opportunity.name if obj.opportunity else None

    def get_top_channels(self, obj):
        if obj.channel_attribution:
            sorted_channels = sorted(
                obj.channel_attribution.items(),
                key=lambda x: x[1],
                reverse=True
            )
            return [{'channel': k, 'revenue': v} for k, v in sorted_channels[:5]]
        return []


class SalesVelocitySerializer(serializers.ModelSerializer):
    """Serializer for SalesVelocity"""

    velocity_score = serializers.SerializerMethodField()

    class Meta:
        model = SalesVelocity
        fields = [
            'id', 'period_start', 'period_end',
            'num_opportunities', 'avg_deal_value', 'win_rate',
            'avg_sales_cycle_days', 'sales_velocity',
            'stage_metrics', 'velocity_change', 'velocity_trend',
            'bottleneck_stage', 'bottleneck_impact',
            'velocity_score',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_velocity_score(self, obj):
        """Calculate a normalized velocity score (0-100)"""
        # Simplified scoring
        if obj.sales_velocity:
            # Assume 100k/day is excellent
            score = min(100, float(obj.sales_velocity) / 1000)
            return round(score, 1)
        return 0


class RevenueLeakageSerializer(serializers.ModelSerializer):
    """Serializer for RevenueLeakage"""

    total_leakage = serializers.SerializerMethodField()

    class Meta:
        model = RevenueLeakage
        fields = [
            'id', 'period_start', 'period_end', 'leakage_type',
            'identified_amount', 'recovered_amount', 'recovery_rate',
            'affected_opportunities', 'root_causes',
            'recommendations', 'priority', 'total_leakage',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_leakage(self, obj):
        if obj.identified_amount and obj.recovered_amount:
            return float(obj.identified_amount - obj.recovered_amount)
        return float(obj.identified_amount or 0)


class WinLossAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for WinLossAnalysis"""

    win_loss_ratio = serializers.SerializerMethodField()
    avg_won_value = serializers.SerializerMethodField()
    avg_lost_value = serializers.SerializerMethodField()

    class Meta:
        model = WinLossAnalysis
        fields = [
            'id', 'period_start', 'period_end',
            'total_opportunities', 'total_won', 'total_lost', 'total_open',
            'win_rate', 'won_value', 'lost_value',
            'avg_won_cycle', 'avg_lost_cycle',
            'win_patterns', 'loss_patterns',
            'competitor_analysis', 'segment_breakdown',
            'win_loss_ratio', 'avg_won_value', 'avg_lost_value',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_win_loss_ratio(self, obj):
        if obj.total_lost and obj.total_lost > 0:
            return round(obj.total_won / obj.total_lost, 2)
        return obj.total_won if obj.total_won else 0

    def get_avg_won_value(self, obj):
        if obj.total_won and obj.total_won > 0:
            return float(obj.won_value / obj.total_won)
        return 0

    def get_avg_lost_value(self, obj):
        if obj.total_lost and obj.total_lost > 0:
            return float(obj.lost_value / obj.total_lost)
        return 0


class ARRMovementSerializer(serializers.ModelSerializer):
    """Serializer for ARRMovement"""

    net_arr_change = serializers.SerializerMethodField()
    growth_rate = serializers.SerializerMethodField()

    class Meta:
        model = ARRMovement
        fields = [
            'id', 'period_start', 'period_end', 'period_type',
            'starting_arr', 'ending_arr',
            'new_arr', 'expansion_arr', 'contraction_arr',
            'churn_arr', 'reactivation_arr',
            'net_arr_change', 'growth_rate',
            'new_customers', 'churned_customers',
            'expansion_customers', 'contraction_customers',
            'arr_by_segment', 'arr_by_product',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_net_arr_change(self, obj):
        return float(
            (obj.new_arr or 0) +
            (obj.expansion_arr or 0) +
            (obj.reactivation_arr or 0) -
            (obj.contraction_arr or 0) -
            (obj.churn_arr or 0)
        )

    def get_growth_rate(self, obj):
        if obj.starting_arr and obj.starting_arr > 0:
            net_change = self.get_net_arr_change(obj)
            return round(net_change / float(obj.starting_arr) * 100, 2)
        return 0


class RevenueIntelligenceSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for RevenueIntelligenceSnapshot"""

    quarter_attainment = serializers.SerializerMethodField()
    health_score = serializers.SerializerMethodField()

    class Meta:
        model = RevenueIntelligenceSnapshot
        fields = [
            'id', 'snapshot_date',
            'total_pipeline', 'weighted_pipeline', 'pipeline_coverage',
            'current_quarter_forecast', 'current_quarter_closed',
            'current_quarter_target',
            'current_velocity', 'avg_deal_size', 'avg_sales_cycle',
            'win_rate',
            'at_risk_deals_count', 'at_risk_deals_value',
            'stalled_deals_count', 'stalled_deals_value',
            'pipeline_trend_7d', 'forecast_trend_7d',
            'quarter_attainment', 'health_score',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_quarter_attainment(self, obj):
        if obj.current_quarter_target and obj.current_quarter_target > 0:
            return round(
                float(obj.current_quarter_closed / obj.current_quarter_target * 100),
                1
            )
        return 0

    def get_health_score(self, obj):
        """Calculate overall pipeline health score"""
        score = 100

        # Reduce for at-risk deals
        if obj.at_risk_deals_count and obj.at_risk_deals_count > 5:
            score -= 20
        elif obj.at_risk_deals_count and obj.at_risk_deals_count > 0:
            score -= 10

        # Reduce for stalled deals
        if obj.stalled_deals_count and obj.stalled_deals_count > 5:
            score -= 20
        elif obj.stalled_deals_count and obj.stalled_deals_count > 0:
            score -= 10

        # Reduce for low coverage
        if obj.pipeline_coverage and obj.pipeline_coverage < 200:
            score -= 15
        elif obj.pipeline_coverage and obj.pipeline_coverage < 300:
            score -= 5

        return max(0, score)


# Request Serializers
class GenerateForecastSerializer(serializers.Serializer):
    """Request serializer for generating forecast"""

    forecast_type = serializers.ChoiceField(
        choices=['monthly', 'quarterly', 'annual', 'rolling']
    )
    period_start = serializers.DateField()
    period_end = serializers.DateField()

    def validate(self, data):
        if data['period_start'] >= data['period_end']:
            raise serializers.ValidationError(
                "period_end must be after period_start"
            )
        return data


class CohortAnalysisRequestSerializer(serializers.Serializer):
    """Request serializer for cohort analysis"""

    cohort_type = serializers.ChoiceField(
        choices=[
            'acquisition_month',
            'acquisition_quarter',
            'product',
            'industry',
            'deal_size',
            'sales_rep'
        ]
    )
    metric_type = serializers.ChoiceField(
        choices=['revenue', 'retention', 'ltv', 'engagement', 'expansion']
    )
    periods = serializers.IntegerField(min_value=1, max_value=24, default=12)


class AttributionRequestSerializer(serializers.Serializer):
    """Request serializer for attribution calculation"""

    opportunity_id = serializers.UUIDField()
    model = serializers.ChoiceField(
        choices=['first_touch', 'last_touch', 'linear', 'time_decay', 'position_based', 'data_driven'],
        default='linear'
    )


class VelocityRequestSerializer(serializers.Serializer):
    """Request serializer for velocity calculation"""

    period_start = serializers.DateField()
    period_end = serializers.DateField()
    segment = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data['period_start'] >= data['period_end']:
            raise serializers.ValidationError(
                "period_end must be after period_start"
            )
        return data


class LeakageAnalysisRequestSerializer(serializers.Serializer):
    """Request serializer for leakage analysis"""

    period_start = serializers.DateField()
    period_end = serializers.DateField()
    leakage_types = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            'discount_overuse',
            'stalled_deals',
            'churn',
            'downgrade',
            'scope_creep',
            'delayed_renewal'
        ]),
        required=False
    )


class WinLossRequestSerializer(serializers.Serializer):
    """Request serializer for win/loss analysis"""

    period_start = serializers.DateField()
    period_end = serializers.DateField()
    segment = serializers.CharField(required=False, allow_blank=True)
    include_patterns = serializers.BooleanField(default=True)


class ARRMovementRequestSerializer(serializers.Serializer):
    """Request serializer for ARR movement analysis"""

    period_start = serializers.DateField()
    period_end = serializers.DateField()
    period_type = serializers.ChoiceField(
        choices=['monthly', 'quarterly', 'annual'],
        default='monthly'
    )
    breakdown_by = serializers.ChoiceField(
        choices=['segment', 'product', 'region', 'rep'],
        required=False
    )


class SnapshotComparisonSerializer(serializers.Serializer):
    """Request serializer for snapshot comparison"""

    snapshot_date_1 = serializers.DateField()
    snapshot_date_2 = serializers.DateField()
    metrics = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=['pipeline', 'forecast', 'velocity', 'health']
    )
