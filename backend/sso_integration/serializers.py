from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import SSOLoginAttempt, SSOProvider, SSOSession

User = get_user_model()


class SSOProviderSerializer(serializers.ModelSerializer):
    """Serializer for SSO Provider with sensitive data protection."""

    is_oauth2 = serializers.ReadOnlyField()
    is_saml = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    redirect_uri = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = SSOProvider
        fields = [
            'id', 'organization', 'provider_type', 'provider_name', 'status',
            'client_id', 'authorization_url', 'token_url', 'user_info_url', 'scope',
            'entity_id', 'sso_url', 'slo_url', 'x509_cert',
            'attribute_mapping', 'auto_create_users', 'auto_update_user_info',
            'default_role', 'required_domains', 'created_at', 'updated_at',
            'created_by', 'created_by_name', 'total_logins', 'last_used_at',
            'is_oauth2', 'is_saml', 'is_active', 'redirect_uri'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by',
                           'total_logins', 'last_used_at']
        extra_kwargs = {
            'client_secret': {'write_only': True},  # Never expose secret in responses
        }

    def get_redirect_uri(self, obj):
        return obj.get_redirect_uri()

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.email
        return None

    def validate_provider_name(self, value):
        """Ensure provider name is unique within organization."""
        organization = self.context['request'].user.organization
        if self.instance:
            # Update case
            if SSOProvider.objects.filter(
                organization=organization,
                provider_name=value
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(
                    "A provider with this name already exists in your organization."
                )
        else:
            # Create case
            if SSOProvider.objects.filter(
                organization=organization,
                provider_name=value
            ).exists():
                raise serializers.ValidationError(
                    "A provider with this name already exists in your organization."
                )
        return value

    def validate(self, data):
        """Validate OAuth2 and SAML configuration."""
        provider_type = data.get('provider_type')

        if provider_type and provider_type.startswith('oauth2_'):
            # OAuth2 validation
            required_fields = ['client_id', 'client_secret', 'authorization_url',
                             'token_url', 'user_info_url']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({
                        field: "This field is required for OAuth2 providers."
                    })

        elif provider_type and provider_type.startswith('saml_'):
            # SAML validation
            required_fields = ['entity_id', 'sso_url', 'x509_cert']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({
                        field: "This field is required for SAML providers."
                    })

        return data


class SSOProviderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing providers."""

    is_active = serializers.ReadOnlyField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = SSOProvider
        fields = [
            'id', 'provider_type', 'provider_name', 'status', 'is_active',
            'total_logins', 'last_used_at', 'created_at', 'created_by_name'
        ]

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.email
        return None


class SSOSessionSerializer(serializers.ModelSerializer):
    """Serializer for SSO sessions."""

    provider_name = serializers.CharField(source='provider.provider_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = SSOSession
        fields = [
            'id', 'provider', 'provider_name', 'user', 'user_email',
            'created_at', 'ip_address', 'user_agent', 'is_active',
            'ended_at', 'expires_at'
        ]
        read_only_fields = ['id', 'created_at']


class SSOLoginAttemptSerializer(serializers.ModelSerializer):
    """Serializer for SSO login attempts."""

    provider_name = serializers.CharField(source='provider.provider_name', read_only=True)
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = SSOLoginAttempt
        fields = [
            'id', 'provider', 'provider_name', 'user', 'user_email',
            'email', 'status', 'error_message', 'ip_address',
            'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_user_email(self, obj):
        return obj.user.email if obj.user else obj.email


class SSOProviderTestSerializer(serializers.Serializer):
    """Serializer for testing SSO provider connection."""

    test_email = serializers.EmailField(
        required=False,
        help_text="Test email address (for validation only)"
    )

    def validate_test_email(self, value):
        """Validate test email against required domains if configured."""
        provider = self.context.get('provider')
        if provider and provider.required_domains:
            domain = value.split('@')[1]
            if domain not in provider.required_domains:
                raise serializers.ValidationError(
                    f"Email domain must be one of: {', '.join(provider.required_domains)}"
                )
        return value


class SSOProviderStatisticsSerializer(serializers.Serializer):
    """Serializer for SSO provider statistics."""

    total_logins = serializers.IntegerField()
    successful_logins = serializers.IntegerField()
    failed_logins = serializers.IntegerField()
    unique_users = serializers.IntegerField()
    last_login_at = serializers.DateTimeField(allow_null=True)
    avg_logins_per_day = serializers.FloatField()
    recent_attempts = SSOLoginAttemptSerializer(many=True)
