"""
App Marketplace Serializers
"""

from rest_framework import serializers
from .models import (
    AppCategory, AppDeveloper, MarketplaceApp, AppVersion,
    AppInstallation, AppReview
)


class AppCategorySerializer(serializers.ModelSerializer):
    app_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AppCategory
        fields = ['id', 'name', 'slug', 'description', 'icon', 'app_count']

    def get_app_count(self, obj):
        return obj.apps.filter(status='approved').count()


class AppDeveloperSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppDeveloper
        fields = [
            'id', 'name', 'slug', 'description', 'website', 'logo_url',
            'verification_status', 'total_apps', 'total_installs'
        ]


class MarketplaceAppListSerializer(serializers.ModelSerializer):
    developer_name = serializers.CharField(source='developer.name')
    category_name = serializers.CharField(source='category.name', allow_null=True)
    
    class Meta:
        model = MarketplaceApp
        fields = [
            'id', 'name', 'slug', 'tagline', 'app_type', 'category_name',
            'developer_name', 'current_version', 'pricing_type', 'price',
            'icon_url', 'install_count', 'rating_average', 'rating_count',
            'is_featured', 'is_verified'
        ]


class MarketplaceAppDetailSerializer(serializers.ModelSerializer):
    developer = AppDeveloperSerializer(read_only=True)
    category = AppCategorySerializer(read_only=True)
    is_installed = serializers.SerializerMethodField()
    
    class Meta:
        model = MarketplaceApp
        fields = [
            'id', 'name', 'slug', 'tagline', 'description', 'app_type',
            'category', 'tags', 'developer', 'current_version', 'min_crm_version',
            'pricing_type', 'price', 'price_currency', 'subscription_period',
            'icon_url', 'screenshots', 'video_url', 'documentation_url',
            'support_url', 'privacy_policy_url', 'permissions',
            'install_count', 'rating_average', 'rating_count',
            'is_featured', 'is_verified', 'is_installed', 'published_at'
        ]

    def get_is_installed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return AppInstallation.objects.filter(
                app=obj,
                installed_by=request.user,
                status='active'
            ).exists()
        return False


class AppVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppVersion
        fields = [
            'id', 'version', 'changelog', 'min_crm_version',
            'is_approved', 'released_at'
        ]


class AppInstallationSerializer(serializers.ModelSerializer):
    app = MarketplaceAppListSerializer(read_only=True)
    
    class Meta:
        model = AppInstallation
        fields = [
            'id', 'app', 'installed_version', 'status', 'config',
            'last_used_at', 'usage_count', 'installed_at'
        ]


class AppInstallSerializer(serializers.Serializer):
    config = serializers.DictField(required=False, default=dict)


class AppReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AppReview
        fields = [
            'id', 'user_name', 'rating', 'title', 'review',
            'developer_response', 'developer_responded_at',
            'helpful_count', 'created_at'
        ]
        read_only_fields = ['id', 'user_name', 'developer_response', 'developer_responded_at', 'helpful_count', 'created_at']

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name[0]}." if obj.user.last_name else obj.user.username


class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppReview
        fields = ['rating', 'title', 'review']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
