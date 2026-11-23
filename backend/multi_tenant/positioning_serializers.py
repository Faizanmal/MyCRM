"""
Serializers for Tenant Product Positioning & Onboarding Specs
"""
from rest_framework import serializers
from .models import ProductPositioningProfile


class ProductPositioningProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the tenant's Product Positioning & ICP profile.
    """
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    completion_percentage = serializers.SerializerMethodField()
    all_tasks = serializers.SerializerMethodField()

    class Meta:
        model = ProductPositioningProfile
        fields = [
            'id',
            'organization',
            'organization_name',
            'target_market',
            'ideal_customer_profile',
            'team_size_tier',
            'primary_jtbd',
            'buyer_tasks_completed',
            'all_tasks',
            'completion_percentage',
            'value_metrics',
            'onboarding_status',
            'activated_features',
            'completed_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'organization',
            'organization_name',
            'buyer_tasks_completed',
            'all_tasks',
            'completion_percentage',
            'completed_at',
            'created_at',
            'updated_at',
        ]

    def get_all_tasks(self, obj):
        return [
            {
                'key': 'eval_poc',
                'title': 'Evaluation & POC Setup',
                'description': 'Configure company profile, target market, and invite core team members.',
                'completed': 'eval_poc' in obj.buyer_tasks_completed
            },
            {
                'key': 'data_migration',
                'title': 'Data Migration & Schema Validation',
                'description': 'Import legacy CSV contacts/leads and verify zero duplicates or lost fields.',
                'completed': 'data_migration' in obj.buyer_tasks_completed
            },
            {
                'key': 'team_onboarding',
                'title': 'Team Onboarding & Alignment',
                'description': 'Complete product tour, configure RBAC role policies, and establish SLA rules.',
                'completed': 'team_onboarding' in obj.buyer_tasks_completed
            },
            {
                'key': 'pipeline_execution',
                'title': 'Operational Pipeline Execution',
                'description': 'Qualify incoming leads, progress deals through stages, and log customer activities.',
                'completed': 'pipeline_execution' in obj.buyer_tasks_completed
            },
            {
                'key': 'roi_measurement',
                'title': 'ROI & Value Measurement',
                'description': 'Review executive dashboard, verify win rate lift, and quantify administrative time saved.',
                'completed': 'roi_measurement' in obj.buyer_tasks_completed
            }
        ]

    def get_completion_percentage(self, obj):
        total_tasks = 5
        completed = len(obj.buyer_tasks_completed)
        return round((completed / total_tasks) * 100, 1)


class CompleteBuyerTaskSerializer(serializers.Serializer):
    """
    Serializer for marking one of the 5 buyer tasks as completed.
    """
    task_key = serializers.ChoiceField(
        choices=[
            'eval_poc',
            'data_migration',
            'team_onboarding',
            'pipeline_execution',
            'roi_measurement'
        ]
    )
    metadata = serializers.JSONField(required=False, default=dict)
