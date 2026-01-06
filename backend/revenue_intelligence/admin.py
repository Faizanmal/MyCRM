from django.contrib import admin

from .models import (
    Competitor,
    DealCompetitor,
    DealRiskAlert,
    DealScore,
    DealVelocity,
    PipelineSnapshot,
    RevenueForecast,
    RevenueTarget,
)


@admin.register(RevenueTarget)
class RevenueTargetAdmin(admin.ModelAdmin):
    list_display = ['user', 'target_type', 'period', 'target_amount', 'achieved_amount', 'attainment_percentage', 'start_date', 'end_date']
    list_filter = ['target_type', 'period', 'start_date']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['achieved_amount', 'pipeline_amount', 'weighted_pipeline']


@admin.register(DealScore)
class DealScoreAdmin(admin.ModelAdmin):
    list_display = ['opportunity', 'score', 'win_probability', 'risk_level', 'score_trend', 'calculated_at']
    list_filter = ['risk_level', 'score_trend']
    search_fields = ['opportunity__name']
    readonly_fields = ['score', 'win_probability', 'risk_level', 'engagement_score', 'timing_score',
                       'stakeholder_score', 'activity_score', 'competitive_score', 'calculated_at']


@admin.register(DealVelocity)
class DealVelocityAdmin(admin.ModelAdmin):
    list_display = ['opportunity', 'from_stage', 'to_stage', 'days_in_stage', 'transition_date']
    list_filter = ['from_stage', 'to_stage']
    search_fields = ['opportunity__name']


@admin.register(PipelineSnapshot)
class PipelineSnapshotAdmin(admin.ModelAdmin):
    list_display = ['snapshot_date', 'user', 'total_pipeline', 'weighted_pipeline', 'deal_count', 'win_rate']
    list_filter = ['snapshot_date', 'user']
    date_hierarchy = 'snapshot_date'


@admin.register(Competitor)
class CompetitorAdmin(admin.ModelAdmin):
    list_display = ['name', 'threat_level', 'deals_won_against', 'deals_lost_to', 'win_rate_against', 'is_active']
    list_filter = ['threat_level', 'is_active']
    search_fields = ['name', 'description']


@admin.register(DealCompetitor)
class DealCompetitorAdmin(admin.ModelAdmin):
    list_display = ['opportunity', 'competitor', 'status', 'threat_level']
    list_filter = ['status', 'threat_level']
    search_fields = ['opportunity__name', 'competitor__name']


@admin.register(RevenueForecast)
class RevenueForecastAdmin(admin.ModelAdmin):
    list_display = ['user', 'forecast_type', 'period_start', 'period_end', 'amount', 'confidence', 'forecast_date']
    list_filter = ['forecast_type', 'confidence', 'forecast_date']
    search_fields = ['user__username']
    date_hierarchy = 'forecast_date'


@admin.register(DealRiskAlert)
class DealRiskAlertAdmin(admin.ModelAdmin):
    list_display = ['opportunity', 'alert_type', 'severity', 'is_active', 'is_acknowledged', 'created_at']
    list_filter = ['alert_type', 'severity', 'is_active', 'is_acknowledged']
    search_fields = ['opportunity__name', 'title']
