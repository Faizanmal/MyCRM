from django.contrib import admin
from .models import Organization, OrganizationMember, OrganizationInvitation


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'status', 'plan', 'user_count', 'created_at']
    list_filter = ['status', 'plan', 'created_at']
    search_fields = ['name', 'slug', 'email', 'domain']
    readonly_fields = ['id', 'created_at', 'updated_at', 'user_count', 'storage_used_mb']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'logo', 'website', 'domain')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Subscription', {
            'fields': ('status', 'plan', 'max_users', 'max_contacts', 'max_storage_mb', 
                      'subscription_start', 'subscription_end', 'trial_ends_at')
        }),
        ('Billing', {
            'fields': ('billing_email', 'stripe_customer_id')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at', 'created_by', 'user_count', 'storage_used_mb')
        }),
        ('Settings', {
            'fields': ('settings',),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'joined_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'organization__name']
    readonly_fields = ['id', 'joined_at']


@admin.register(OrganizationInvitation)
class OrganizationInvitationAdmin(admin.ModelAdmin):
    list_display = ['email', 'organization', 'role', 'status', 'invited_by', 'created_at', 'expires_at']
    list_filter = ['status', 'role', 'created_at']
    search_fields = ['email', 'organization__name', 'invited_by__email']
    readonly_fields = ['id', 'token', 'created_at', 'accepted_at']
