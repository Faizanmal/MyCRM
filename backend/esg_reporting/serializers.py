"""
ESG Reporting Serializers
"""

from rest_framework import serializers
from .models import (
    ESGFramework, ESGMetricCategory, ESGMetricDefinition,
    ESGDataEntry, ESGTarget, ESGReport, CarbonFootprint,
    SupplierESGAssessment
)


class ESGFrameworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ESGFramework
        fields = '__all__'


class ESGMetricCategorySerializer(serializers.ModelSerializer):
    metric_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ESGMetricCategory
        fields = ['id', 'name', 'pillar', 'description', 'icon', 'metric_count']

    def get_metric_count(self, obj):
        return obj.metrics.filter(is_active=True).count()


class ESGMetricDefinitionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    pillar = serializers.CharField(source='category.pillar', read_only=True)
    frameworks = ESGFrameworkSerializer(many=True, read_only=True)
    
    class Meta:
        model = ESGMetricDefinition
        fields = [
            'id', 'name', 'code', 'description', 'category', 'category_name',
            'pillar', 'frameworks', 'data_type', 'unit', 'collection_frequency',
            'min_value', 'max_value', 'benchmark_value', 'target_direction',
            'is_calculated', 'is_active'
        ]


class ESGDataEntrySerializer(serializers.ModelSerializer):
    metric_name = serializers.CharField(source='metric.name', read_only=True)
    metric_unit = serializers.CharField(source='metric.unit', read_only=True)
    entered_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ESGDataEntry
        fields = [
            'id', 'metric', 'metric_name', 'metric_unit', 'period_start',
            'period_end', 'fiscal_year', 'fiscal_quarter', 'value', 'text_value',
            'scope', 'location', 'business_unit', 'confidence_level', 'data_source',
            'methodology', 'notes', 'status', 'entered_by', 'entered_by_name',
            'approved_by', 'approved_at', 'created_at'
        ]
        read_only_fields = ['id', 'entered_by', 'approved_by', 'approved_at', 'created_at']

    def get_entered_by_name(self, obj):
        if obj.entered_by:
            return f"{obj.entered_by.first_name} {obj.entered_by.last_name}"
        return None


class ESGTargetSerializer(serializers.ModelSerializer):
    metric_name = serializers.CharField(source='metric.name', read_only=True)
    
    class Meta:
        model = ESGTarget
        fields = [
            'id', 'metric', 'metric_name', 'name', 'description', 'target_type',
            'baseline_value', 'baseline_year', 'target_value', 'target_year',
            'interim_targets', 'current_value', 'progress_percentage', 'status',
            'sdg_goals', 'science_based', 'net_zero_aligned', 'created_at'
        ]


class ESGReportSerializer(serializers.ModelSerializer):
    framework_name = serializers.CharField(source='framework.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ESGReport
        fields = [
            'id', 'name', 'report_type', 'framework', 'framework_name',
            'fiscal_year', 'period_start', 'period_end', 'executive_summary',
            'sections', 'pdf_url', 'xlsx_url', 'status', 'created_by',
            'created_by_name', 'published_at', 'created_at'
        ]

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None


class CarbonFootprintSerializer(serializers.ModelSerializer):
    scope_display = serializers.CharField(source='get_scope_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = CarbonFootprint
        fields = [
            'id', 'scope', 'scope_display', 'category', 'category_display',
            'period_start', 'period_end', 'location', 'facility',
            'activity_data', 'activity_unit', 'emission_factor',
            'co2_emissions', 'ch4_emissions', 'n2o_emissions', 'total_co2e',
            'data_source', 'methodology', 'notes', 'created_at'
        ]


class CarbonSummarySerializer(serializers.Serializer):
    """Carbon footprint summary"""
    total_co2e = serializers.FloatField()
    scope1_total = serializers.FloatField()
    scope2_total = serializers.FloatField()
    scope3_total = serializers.FloatField()
    by_category = serializers.DictField()
    year_over_year_change = serializers.FloatField()


class SupplierESGAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierESGAssessment
        fields = [
            'id', 'supplier_name', 'supplier_id', 'industry', 'country',
            'assessment_date', 'valid_until', 'environmental_score',
            'social_score', 'governance_score', 'overall_score',
            'environmental_rating', 'social_rating', 'governance_rating',
            'overall_rating', 'risk_level', 'risk_factors', 'certifications',
            'improvement_areas', 'notes', 'created_at'
        ]


class ESGDashboardSerializer(serializers.Serializer):
    """ESG dashboard summary"""
    overall_score = serializers.IntegerField()
    environmental_score = serializers.IntegerField()
    social_score = serializers.IntegerField()
    governance_score = serializers.IntegerField()
    carbon_footprint = CarbonSummarySerializer()
    targets_on_track = serializers.IntegerField()
    targets_at_risk = serializers.IntegerField()
    pending_data_entries = serializers.IntegerField()
    recent_reports = ESGReportSerializer(many=True)
