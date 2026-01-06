"""
White Label and Billing Admin Configuration
"""

from django.contrib import admin

from .models import (
    FeatureFlag,
    Invoice,
    InvoiceLineItem,
    Organization,
    OrganizationMember,
    PartnerPayout,
    PaymentMethod,
    SubscriptionPlan,
    UsageRecord,
    WhiteLabelPartner,
)


@admin.register(WhiteLabelPartner)
class WhiteLabelPartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'partner_type', 'subdomain', 'is_active', 'created_at']
    list_filter = ['partner_type', 'is_active']
    search_fields = ['name', 'subdomain', 'custom_domain']
    filter_horizontal = ['admin_users']


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'billing_period', 'max_users', 'max_contacts', 'is_active', 'is_featured']
    list_filter = ['billing_period', 'is_active', 'is_featured']
    search_fields = ['name', 'slug']


class OrganizationMemberInline(admin.TabularInline):
    model = OrganizationMember
    extra = 0


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'plan', 'subscription_status', 'current_users', 'created_at']
    list_filter = ['subscription_status', 'plan']
    search_fields = ['name', 'owner__email']
    inlines = [OrganizationMemberInline]
    readonly_fields = ['uuid', 'stripe_customer_id', 'stripe_subscription_id']


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'role', 'can_manage_billing', 'joined_at']
    list_filter = ['role']
    search_fields = ['user__email', 'organization__name']


class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'organization', 'total', 'status', 'issued_at', 'paid_at']
    list_filter = ['status', 'issued_at']
    search_fields = ['invoice_number', 'organization__name']
    inlines = [InvoiceLineItemInline]
    readonly_fields = ['uuid', 'stripe_invoice_id']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['organization', 'card_brand', 'card_last4', 'is_default', 'created_at']
    list_filter = ['card_brand', 'is_default']
    search_fields = ['organization__name']


@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = ['organization', 'usage_type', 'quantity', 'recorded_at']
    list_filter = ['usage_type', 'recorded_at']
    search_fields = ['organization__name']


@admin.register(PartnerPayout)
class PartnerPayoutAdmin(admin.ModelAdmin):
    list_display = ['partner', 'period_start', 'period_end', 'commission_amount', 'status', 'paid_at']
    list_filter = ['status', 'period_end']
    search_fields = ['partner__name']


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_enabled_by_default', 'created_at']
    filter_horizontal = ['enabled_for_plans', 'enabled_for_orgs', 'disabled_for_orgs']
