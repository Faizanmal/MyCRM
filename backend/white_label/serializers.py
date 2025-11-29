"""
White Label and Billing Serializers
"""

from rest_framework import serializers
from .models import (
    WhiteLabelPartner, SubscriptionPlan, Organization, OrganizationMember,
    Invoice, InvoiceLineItem, PaymentMethod, UsageRecord, PartnerPayout, FeatureFlag
)


class WhiteLabelPartnerSerializer(serializers.ModelSerializer):
    partner_type_display = serializers.CharField(source='get_partner_type_display', read_only=True)
    organizations_count = serializers.IntegerField(source='organizations.count', read_only=True)
    
    class Meta:
        model = WhiteLabelPartner
        fields = '__all__'


class WhiteLabelBrandingSerializer(serializers.ModelSerializer):
    """Public branding info for login pages, etc."""
    class Meta:
        model = WhiteLabelPartner
        fields = [
            'brand_name', 'logo', 'logo_dark', 'favicon',
            'primary_color', 'secondary_color', 'accent_color',
            'custom_css', 'support_email', 'support_url'
        ]


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    billing_period_display = serializers.CharField(source='get_billing_period_display', read_only=True)
    
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'


class SubscriptionPlanPublicSerializer(serializers.ModelSerializer):
    """Public plan info for pricing pages"""
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'billing_period',
            'price_per_user', 'included_users', 'trial_days', 'features',
            'max_users', 'max_contacts', 'max_storage_gb', 'max_emails_per_month',
            'is_featured', 'display_order'
        ]


class OrganizationMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = OrganizationMember
        fields = '__all__'
        read_only_fields = ['organization', 'user', 'invited_by', 'joined_at']


class OrganizationSerializer(serializers.ModelSerializer):
    subscription_status_display = serializers.CharField(source='get_subscription_status_display', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    is_on_trial = serializers.ReadOnlyField()
    days_remaining_trial = serializers.ReadOnlyField()
    members = OrganizationMemberSerializer(many=True, read_only=True)
    
    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = [
            'uuid', 'owner', 'subscription_status', 'stripe_customer_id',
            'stripe_subscription_id', 'current_users', 'current_contacts',
            'current_storage_bytes'
        ]


class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['name', 'slug', 'plan', 'timezone', 'currency']


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLineItem
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    line_items = InvoiceLineItemSerializer(many=True, read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = Invoice
        fields = '__all__'


class PaymentMethodSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'card_brand', 'card_last4', 'card_exp_month',
            'card_exp_year', 'is_default', 'display_name', 'created_at'
        ]
    
    def get_display_name(self, obj):
        return f"{obj.card_brand.title()} ****{obj.card_last4}"


class UsageRecordSerializer(serializers.ModelSerializer):
    usage_type_display = serializers.CharField(source='get_usage_type_display', read_only=True)
    
    class Meta:
        model = UsageRecord
        fields = '__all__'


class PartnerPayoutSerializer(serializers.ModelSerializer):
    partner_name = serializers.CharField(source='partner.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PartnerPayout
        fields = '__all__'


class FeatureFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureFlag
        fields = '__all__'


# Action serializers
class InviteMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=OrganizationMember.ROLES, default='user')
    can_manage_users = serializers.BooleanField(default=False)
    can_manage_billing = serializers.BooleanField(default=False)


class ChangePlanSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()


class AddPaymentMethodSerializer(serializers.Serializer):
    payment_method_id = serializers.CharField()  # Stripe payment method ID
    set_as_default = serializers.BooleanField(default=True)


class CreateCheckoutSessionSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()


class UsageSummarySerializer(serializers.Serializer):
    """Summary of organization usage"""
    users = serializers.IntegerField()
    users_limit = serializers.IntegerField()
    users_percent = serializers.DecimalField(max_digits=5, decimal_places=1)
    contacts = serializers.IntegerField()
    contacts_limit = serializers.IntegerField()
    contacts_percent = serializers.DecimalField(max_digits=5, decimal_places=1)
    storage_bytes = serializers.IntegerField()
    storage_limit_bytes = serializers.IntegerField()
    storage_percent = serializers.DecimalField(max_digits=5, decimal_places=1)
