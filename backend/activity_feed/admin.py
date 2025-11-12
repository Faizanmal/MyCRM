from django.contrib import admin
from .models import Activity, Comment, Mention, Notification, Follow


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['actor', 'action', 'content_type', 'object_id', 'created_at']
    list_filter = ['action', 'content_type', 'created_at']
    search_fields = ['description', 'actor__username']
    readonly_fields = ['created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'content_type', 'object_id', 'created_at', 'is_edited']
    list_filter = ['content_type', 'created_at', 'is_edited']
    search_fields = ['content', 'author__username']


@admin.register(Mention)
class MentionAdmin(admin.ModelAdmin):
    list_display = ['user', 'mentioned_by', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'context']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_type', 'object_id', 'created_at']
    list_filter = ['content_type', 'created_at']
    search_fields = ['user__username']
