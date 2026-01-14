"""
Customer Portal Admin Configuration
"""

from django.contrib import admin

from .models import (
    CustomerAccount,
    CustomerOrder,
    KnowledgeBaseArticle,
    PortalNotification,
    PortalSession,
    SupportTicket,
    TicketComment,
)


@admin.register(CustomerAccount)
class CustomerAccountAdmin(admin.ModelAdmin):
    list_display = ['email', 'contact', 'is_active', 'is_verified', 'last_login', 'created_at']
    list_filter = ['is_active', 'is_verified', 'two_factor_enabled']
    search_fields = ['email', 'contact__first_name', 'contact__last_name']
    readonly_fields = ['last_login', 'login_count', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 0
    readonly_fields = ['created_at']


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'subject', 'customer', 'category', 'priority', 'status', 'created_at']
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = ['ticket_number', 'subject', 'customer__email']
    readonly_fields = ['ticket_number', 'first_response_at', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    inlines = [TicketCommentInline]

    fieldsets = (
        (None, {
            'fields': ('ticket_number', 'customer', 'subject', 'description')
        }),
        ('Classification', {
            'fields': ('category', 'priority', 'status', 'assigned_to')
        }),
        ('Resolution', {
            'fields': ('resolution', 'resolved_at', 'resolved_by', 'satisfaction_rating', 'satisfaction_feedback')
        }),
        ('SLA', {
            'fields': ('sla_response_due', 'sla_resolution_due', 'first_response_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CustomerOrder)
class CustomerOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'status', 'total', 'currency', 'ordered_at']
    list_filter = ['status', 'currency', 'ordered_at']
    search_fields = ['order_number', 'customer__email']
    readonly_fields = ['ordered_at', 'created_at', 'updated_at']
    date_hierarchy = 'ordered_at'


@admin.register(KnowledgeBaseArticle)
class KnowledgeBaseArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'is_featured', 'view_count', 'published_at']
    list_filter = ['status', 'is_featured', 'category']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'helpful_count', 'not_helpful_count', 'created_at', 'updated_at']
    date_hierarchy = 'published_at'


@admin.register(PortalNotification)
class PortalNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'customer', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'customer__email']
    readonly_fields = ['created_at']


@admin.register(PortalSession)
class PortalSessionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'ip_address', 'is_active', 'created_at', 'expires_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['customer__email', 'ip_address']
    readonly_fields = ['session_token', 'refresh_token', 'created_at', 'last_activity']
