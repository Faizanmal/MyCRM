from django.contrib import admin

from .models import (
    ApprovalAction,
    ApprovalInstance,
    ApprovalStep,
    ApprovalWorkflow,
    Channel,
    ChannelMembership,
    CollaborativeDocument,
    DealRoom,
    DealRoomParticipant,
    DocumentComment,
    Message,
)


class DealRoomParticipantInline(admin.TabularInline):
    model = DealRoomParticipant
    extra = 1
    autocomplete_fields = ['user']


@admin.register(DealRoom)
class DealRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'opportunity', 'status', 'privacy', 'participant_count', 'created_at']
    list_filter = ['status', 'privacy', 'created_at']
    search_fields = ['name', 'description', 'opportunity__name']
    autocomplete_fields = ['opportunity', 'owner']
    inlines = [DealRoomParticipantInline]
    readonly_fields = ['participant_count', 'message_count', 'document_count', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'opportunity')
        }),
        ('Settings', {
            'fields': ('status', 'privacy_level')
        }),
        ('Metadata', {
            'fields': ('metadata',)
        }),
        ('Statistics', {
            'fields': ('participant_count', 'message_count', 'document_count'),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DealRoomParticipant)
class DealRoomParticipantAdmin(admin.ModelAdmin):
    list_display = ['deal_room', 'user', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['deal_room__name', 'user__username', 'user__email']
    autocomplete_fields = ['deal_room', 'user']


class ChannelMembershipInline(admin.TabularInline):
    model = ChannelMembership
    extra = 1
    autocomplete_fields = ['user']


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'channel_type', 'is_archived', 'member_count', 'created_at']
    list_filter = ['channel_type', 'is_archived', 'created_at']
    search_fields = ['name', 'description']
    autocomplete_fields = ['created_by']
    inlines = [ChannelMembershipInline]
    readonly_fields = ['member_count', 'message_count', 'created_at', 'updated_at']


@admin.register(ChannelMembership)
class ChannelMembershipAdmin(admin.ModelAdmin):
    list_display = ['channel', 'user', 'is_admin', 'joined_at', 'last_read_at']
    list_filter = ['is_admin', 'joined_at']
    search_fields = ['channel__name', 'user__username', 'user__email']
    autocomplete_fields = ['channel', 'user']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'channel', 'deal_room', 'parent_message', 'created_at', 'is_edited', 'is_deleted']
    list_filter = ['is_edited', 'is_deleted', 'created_at']
    search_fields = ['content', 'sender__username', 'channel__name']
    autocomplete_fields = ['sender', 'channel', 'deal_room', 'parent_message']
    readonly_fields = ['thread_reply_count', 'created_at', 'edited_at']

    fieldsets = (
        ('Message Details', {
            'fields': ('sender', 'content', 'channel', 'deal_room', 'parent_message')
        }),
        ('Attachments & Reactions', {
            'fields': ('attachments', 'reactions', 'mentions'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_edited', 'is_deleted', 'thread_reply_count')
        }),
        ('Tracking', {
            'fields': ('created_at', 'edited_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CollaborativeDocument)
class CollaborativeDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'doc_type', 'deal_room', 'version', 'is_locked', 'created_at']
    list_filter = ['doc_type', 'is_locked', 'created_at']
    search_fields = ['title', 'description', 'deal_room__name']
    autocomplete_fields = ['deal_room', 'owner', 'locked_by', 'parent_version']
    readonly_fields = ['version', 'comment_count', 'created_at', 'updated_at']

    fieldsets = (
        ('Document Information', {
            'fields': ('title', 'description', 'doc_type', 'deal_room')
        }),
        ('Content', {
            'fields': ('file_path', 'file_size', 'mime_type')
        }),
        ('Versioning', {
            'fields': ('version', 'parent_version'),
            'classes': ('collapse',)
        }),
        ('Lock Status', {
            'fields': ('is_locked', 'locked_by')
        }),
        ('Statistics', {
            'fields': ('comment_count',),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('owner', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DocumentComment)
class DocumentCommentAdmin(admin.ModelAdmin):
    list_display = ['document', 'author', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['content', 'document__title', 'author__username']
    autocomplete_fields = ['document', 'author', 'parent_comment', 'resolved_by']
    readonly_fields = ['created_at', 'resolved_at']


class ApprovalStepInline(admin.TabularInline):
    model = ApprovalStep
    extra = 1
    filter_horizontal = ['approvers']


@admin.register(ApprovalWorkflow)
class ApprovalWorkflowAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'total_instances', 'completed_instances', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    autocomplete_fields = ['created_by']
    inlines = [ApprovalStepInline]
    readonly_fields = ['total_instances', 'completed_instances', 'created_at', 'updated_at']

    fieldsets = (
        ('Workflow Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Trigger Conditions', {
            'fields': ('trigger_conditions',),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('total_instances', 'completed_instances'),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ApprovalStep)
class ApprovalStepAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'name', 'step_type', 'order', 'approver_count_required']
    list_filter = ['step_type']
    search_fields = ['name', 'workflow__name']
    autocomplete_fields = ['workflow']
    filter_horizontal = ['approvers']


@admin.register(ApprovalInstance)
class ApprovalInstanceAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'status', 'requested_by', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['workflow__name', 'requested_by__username']
    autocomplete_fields = ['workflow', 'requested_by']
    readonly_fields = ['created_at', 'completed_at']


@admin.register(ApprovalAction)
class ApprovalActionAdmin(admin.ModelAdmin):
    list_display = ['instance', 'step', 'actor', 'action', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['instance__workflow__name', 'actor__username', 'comment']
    autocomplete_fields = ['instance', 'step', 'actor', 'delegated_to']
    readonly_fields = ['created_at']
