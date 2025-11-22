from rest_framework import serializers
from .models import Organization, OrganizationMember, OrganizationInvitation
from django.contrib.auth import get_user_model

User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):
    user_count = serializers.ReadOnlyField()
    storage_used_mb = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    is_trial = serializers.ReadOnlyField()

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'domain', 'logo', 'website',
            'email', 'phone', 'address', 'status', 'plan',
            'max_users', 'max_contacts', 'max_storage_mb',
            'billing_email', 'subscription_start', 'subscription_end',
            'trial_ends_at', 'user_count', 'storage_used_mb',
            'is_active', 'is_trial', 'settings', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'user_count', 'storage_used_mb']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class OrganizationMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    is_owner = serializers.ReadOnlyField()
    is_admin = serializers.ReadOnlyField()

    class Meta:
        model = OrganizationMember
        fields = [
            'id', 'organization', 'organization_name', 'user', 'user_email', 'user_name',
            'role', 'is_active', 'can_invite_users', 'can_manage_billing',
            'can_manage_settings', 'joined_at', 'invited_by', 'is_owner', 'is_admin'
        ]
        read_only_fields = ['id', 'joined_at']

    def get_user_name(self, obj):
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.user.username


class OrganizationInvitationSerializer(serializers.ModelSerializer):
    invited_by_email = serializers.EmailField(source='invited_by.email', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    is_expired = serializers.ReadOnlyField()
    is_pending = serializers.ReadOnlyField()

    class Meta:
        model = OrganizationInvitation
        fields = [
            'id', 'organization', 'organization_name', 'email', 'role',
            'token', 'status', 'invited_by', 'invited_by_email',
            'created_at', 'expires_at', 'accepted_at',
            'is_expired', 'is_pending'
        ]
        read_only_fields = ['id', 'token', 'status', 'created_at', 'accepted_at']

    def create(self, validated_data):
        from datetime import timedelta
        from django.utils import timezone
        
        validated_data['invited_by'] = self.context['request'].user
        validated_data['expires_at'] = timezone.now() + timedelta(days=7)
        return super().create(validated_data)


class SwitchOrganizationSerializer(serializers.Serializer):
    organization_id = serializers.UUIDField()

    def validate_organization_id(self, value):
        user = self.context['request'].user
        try:
            membership = OrganizationMember.objects.get(
                organization_id=value,
                user=user,
                is_active=True
            )
            if not membership.organization.is_active:
                raise serializers.ValidationError("This organization is not active.")
        except OrganizationMember.DoesNotExist:
            raise serializers.ValidationError("You are not a member of this organization.")
        return value
