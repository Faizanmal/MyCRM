"""
Revenue Intelligence Serializers
"""

from rest_framework import serializers
from .models import (
    RevenueTarget, DealScore, DealVelocity, PipelineSnapshot,
    Competitor, DealCompetitor, RevenueForecast, DealRiskAlert
)


class RevenueTargetSerializer(serializers.ModelSerializer):
    attainment_percentage = serializers.ReadOnlyField()
    gap_to_target = serializers.ReadOnlyField()
    coverage_ratio = serializers.ReadOnlyField()
    forecast_attainment = serializers.ReadOnlyField()
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = RevenueTarget
        fields = '__all__'
        read_only_fields = ['id', 'achieved_amount', 'pipeline_amount', 'weighted_pipeline']


class DealScoreSerializer(serializers.ModelSerializer):
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    opportunity_amount = serializers.DecimalField(
        source='opportunity.amount', max_digits=12, decimal_places=2, read_only=True
    )
    opportunity_stage = serializers.CharField(source='opportunity.stage', read_only=True)
    
    class Meta:
        model = DealScore
        fields = '__all__'
        read_only_fields = ['id', 'calculated_at', 'created_at']


class DealScoreSummarySerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    
    class Meta:
        model = DealScore
        fields = ['id', 'opportunity', 'opportunity_name', 'score', 'win_probability', 
                  'risk_level', 'score_trend', 'calculated_at']


class DealVelocitySerializer(serializers.ModelSerializer):
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    
    class Meta:
        model = DealVelocity
        fields = '__all__'
        read_only_fields = ['id']


class PipelineSnapshotSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = PipelineSnapshot
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class CompetitorSerializer(serializers.ModelSerializer):
    win_rate_against = serializers.ReadOnlyField()
    deals_total = serializers.SerializerMethodField()
    
    class Meta:
        model = Competitor
        fields = '__all__'
        read_only_fields = ['id', 'deals_won_against', 'deals_lost_to', 'created_at', 'updated_at']
    
    def get_deals_total(self, obj):
        return obj.deals_won_against + obj.deals_lost_to


class DealCompetitorSerializer(serializers.ModelSerializer):
    competitor_name = serializers.CharField(source='competitor.name', read_only=True)
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    
    class Meta:
        model = DealCompetitor
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class RevenueForecastSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    forecast_type_display = serializers.CharField(source='get_forecast_type_display', read_only=True)
    
    class Meta:
        model = RevenueForecast
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class DealRiskAlertSerializer(serializers.ModelSerializer):
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    opportunity_amount = serializers.DecimalField(
        source='opportunity.amount', max_digits=12, decimal_places=2, read_only=True
    )
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    
    class Meta:
        model = DealRiskAlert
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


# Dashboard/Analytics Serializers

class PipelineHealthSerializer(serializers.Serializer):
    """Pipeline health metrics"""
    total_pipeline = serializers.DecimalField(max_digits=15, decimal_places=2)
    weighted_pipeline = serializers.DecimalField(max_digits=15, decimal_places=2)
    deal_count = serializers.IntegerField()
    avg_deal_size = serializers.DecimalField(max_digits=15, decimal_places=2)
    avg_days_to_close = serializers.IntegerField()
    win_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    stage_breakdown = serializers.JSONField()
    at_risk_deals = serializers.IntegerField()
    at_risk_value = serializers.DecimalField(max_digits=15, decimal_places=2)


class ForecastComparisonSerializer(serializers.Serializer):
    """Compare different forecast types"""
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    commit = serializers.DecimalField(max_digits=15, decimal_places=2)
    best_case = serializers.DecimalField(max_digits=15, decimal_places=2)
    pipeline = serializers.DecimalField(max_digits=15, decimal_places=2)
    ai_predicted = serializers.DecimalField(max_digits=15, decimal_places=2)
    target = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    closed_won = serializers.DecimalField(max_digits=15, decimal_places=2)


class QuotaAttainmentSerializer(serializers.Serializer):
    """Quota attainment dashboard"""
    user_id = serializers.IntegerField()
    user_name = serializers.CharField()
    target_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    achieved_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    attainment_percentage = serializers.DecimalField(max_digits=5, decimal_places=1)
    gap_to_target = serializers.DecimalField(max_digits=15, decimal_places=2)
    pipeline_coverage = serializers.DecimalField(max_digits=5, decimal_places=2)
    forecast_attainment = serializers.DecimalField(max_digits=5, decimal_places=1)
    days_remaining = serializers.IntegerField()
