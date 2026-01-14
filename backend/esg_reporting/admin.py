from django.contrib import admin

from .models import (
    CarbonFootprint,
    ESGDataEntry,
    ESGFramework,
    ESGMetricCategory,
    ESGMetricDefinition,
    ESGReport,
    ESGTarget,
    SupplierESGAssessment,
)


@admin.register(ESGFramework)
class ESGFrameworkAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'version', 'is_active']
    list_filter = ['is_active']


@admin.register(ESGMetricCategory)
class ESGMetricCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'pillar', 'order']
    list_filter = ['pillar']


@admin.register(ESGMetricDefinition)
class ESGMetricDefinitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'data_type', 'unit', 'is_active']
    list_filter = ['category', 'data_type', 'is_active']
    search_fields = ['name', 'code']


@admin.register(ESGDataEntry)
class ESGDataEntryAdmin(admin.ModelAdmin):
    list_display = ['metric', 'fiscal_year', 'value', 'status', 'entered_by', 'created_at']
    list_filter = ['status', 'fiscal_year', 'metric__category__pillar']
    date_hierarchy = 'period_end'


@admin.register(ESGTarget)
class ESGTargetAdmin(admin.ModelAdmin):
    list_display = ['name', 'metric', 'target_value', 'target_year', 'status']
    list_filter = ['status', 'target_type']


@admin.register(ESGReport)
class ESGReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'fiscal_year', 'status', 'created_at']
    list_filter = ['report_type', 'status', 'fiscal_year']


@admin.register(CarbonFootprint)
class CarbonFootprintAdmin(admin.ModelAdmin):
    list_display = ['scope', 'category', 'total_co2e', 'period_start', 'period_end']
    list_filter = ['scope', 'category']
    date_hierarchy = 'period_end'


@admin.register(SupplierESGAssessment)
class SupplierESGAssessmentAdmin(admin.ModelAdmin):
    list_display = ['supplier_name', 'overall_rating', 'risk_level', 'assessment_date']
    list_filter = ['overall_rating', 'risk_level']
    search_fields = ['supplier_name']
