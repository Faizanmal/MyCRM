from django.contrib import admin
from .models import ChatSession, ChatMessage, ChatIntent, QuickAction, EmailTemplate


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'message_count', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'user__username']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'role', 'message_type', 'is_helpful', 'created_at']
    list_filter = ['role', 'message_type', 'is_helpful']


@admin.register(QuickAction)
class QuickActionAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'requires_context', 'is_active']
    list_filter = ['category', 'is_active']


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'purpose', 'tone', 'usage_count', 'is_active']
    list_filter = ['purpose', 'tone', 'is_active']
