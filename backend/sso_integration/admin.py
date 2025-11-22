from django.contrib import admin
from .models import SSOProvider, SSOSession, SSOLoginAttempt


@admin.register(SSOProvider)
class SSOProviderAdmin(admin.ModelAdmin):
    list_display = [
        'provider_name', 'organization', 'provider_type', 'status',
        'total_logins', 'last_used_at', 'created_at'
    ]
    list_filter = ['provider_type', 'status', 'created_at']
    search_fields = ['provider_name', 'organization__name', 'entity_id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'total_logins', 'last_used_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'organization', 'provider_type', 'provider_name', 'status')
        }),
        ('OAuth2 Configuration', {
            'fields': (
                'client_id', 'client_secret', 'authorization_url',
                'token_url', 'user_info_url', 'scope'
            ),
            'classes': ('collapse',)
        }),
        ('SAML Configuration', {
            'fields': ('entity_id', 'sso_url', 'slo_url', 'x509_cert'),
            'classes': ('collapse',)
        }),
        ('User Management', {
            'fields': (
                'attribute_mapping', 'auto_create_users', 'auto_update_user_info',
                'default_role', 'required_domains'
            )
        }),
        ('Statistics', {
            'fields': ('total_logins', 'last_used_at', 'created_at', 'updated_at', 'created_by')
        }),
    )


@admin.register(SSOSession)
class SSOSessionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'provider', 'created_at', 'is_active', 'ended_at', 'ip_address'
    ]
    list_filter = ['is_active', 'provider', 'created_at']
    search_fields = ['user__email', 'provider__provider_name', 'ip_address']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Session Information', {
            'fields': ('id', 'provider', 'user', 'is_active', 'created_at', 'ended_at')
        }),
        ('Session Data', {
            'fields': ('session_index', 'name_id', 'expires_at'),
            'classes': ('collapse',)
        }),
        ('Request Metadata', {
            'fields': ('ip_address', 'user_agent')
        }),
    )


@admin.register(SSOLoginAttempt)
class SSOLoginAttemptAdmin(admin.ModelAdmin):
    list_display = [
        'email', 'provider', 'status', 'user', 'created_at', 'ip_address'
    ]
    list_filter = ['status', 'provider', 'created_at']
    search_fields = ['email', 'provider__provider_name', 'ip_address', 'error_message']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Attempt Information', {
            'fields': ('id', 'provider', 'email', 'user', 'status', 'created_at')
        }),
        ('Error Details', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('SSO Data', {
            'fields': ('sso_user_id', 'sso_attributes'),
            'classes': ('collapse',)
        }),
        ('Request Metadata', {
            'fields': ('ip_address', 'user_agent')
        }),
    )
