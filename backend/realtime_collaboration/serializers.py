"""
Real-Time Collaboration Serializers
"""

from rest_framework import serializers
from .models import (
    CollaborativeDocument, DocumentVersion, DocumentCollaborator,
    DocumentComment, EditingSession, DocumentOperation, DocumentTemplate
)


class DocumentCollaboratorSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentCollaborator
        fields = [
            'id', 'user_id', 'username', 'full_name', 'email', 'avatar_url',
            'permission', 'notify_on_changes', 'notify_on_comments',
            'last_viewed_at', 'last_edited_at', 'added_at'
        ]
        read_only_fields = ['id', 'added_at']

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username

    def get_avatar_url(self, obj):
        return getattr(obj.user, 'avatar_url', None)


class AddCollaboratorSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    permission = serializers.ChoiceField(choices=['view', 'comment', 'edit', 'admin'], default='view')
    notify_on_changes = serializers.BooleanField(default=True)
    notify_on_comments = serializers.BooleanField(default=True)


class DocumentVersionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentVersion
        fields = [
            'id', 'version', 'content', 'changes_summary',
            'created_by', 'created_by_name', 'created_at',
            'is_restored', 'restored_from'
        ]

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None


class DocumentVersionListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentVersion
        fields = [
            'id', 'version', 'changes_summary', 'created_by_name', 'created_at'
        ]

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None


class DocumentCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    author_avatar = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentComment
        fields = [
            'id', 'document', 'comment_type', 'content',
            'anchor_id', 'selection_start', 'selection_end', 'selected_text',
            'parent', 'is_resolved', 'resolved_by', 'resolved_at',
            'author', 'author_name', 'author_avatar',
            'replies', 'reply_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_author_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.username

    def get_author_avatar(self, obj):
        return getattr(obj.author, 'avatar_url', None)

    def get_replies(self, obj):
        if obj.parent is None:
            replies = obj.replies.all()[:5]
            return DocumentCommentSerializer(replies, many=True).data
        return []

    def get_reply_count(self, obj):
        return obj.replies.count()


class EditingSessionSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = EditingSession
        fields = [
            'id', 'user', 'user_name', 'user_avatar',
            'cursor_position', 'selection', 'cursor_color',
            'is_active', 'last_activity', 'connected_at'
        ]

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username

    def get_user_avatar(self, obj):
        return getattr(obj.user, 'avatar_url', None)


class CollaborativeDocumentListSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    collaborator_count = serializers.SerializerMethodField()
    active_editors = serializers.SerializerMethodField()
    
    class Meta:
        model = CollaborativeDocument
        fields = [
            'id', 'title', 'description', 'document_type', 'status',
            'version', 'owner', 'owner_name', 'collaborator_count',
            'active_editors', 'is_locked', 'updated_at', 'created_at'
        ]

    def get_owner_name(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}".strip() or obj.owner.username

    def get_collaborator_count(self, obj):
        return obj.collaborators.count()

    def get_active_editors(self, obj):
        return obj.editing_sessions.filter(is_active=True).count()


class CollaborativeDocumentDetailSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    collaborators = DocumentCollaboratorSerializer(many=True, read_only=True)
    active_sessions = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    unresolved_comments = serializers.SerializerMethodField()
    
    class Meta:
        model = CollaborativeDocument
        fields = [
            'id', 'title', 'description', 'document_type', 'status',
            'content', 'version', 'owner', 'owner_name',
            'is_public', 'public_link_enabled', 'default_permission',
            'collaborators', 'active_sessions',
            'is_locked', 'locked_by', 'locked_at',
            'related_lead', 'related_opportunity', 'related_contact',
            'comment_count', 'unresolved_comments',
            'last_edited_by', 'updated_at', 'created_at'
        ]
        read_only_fields = ['id', 'version', 'created_at']

    def get_owner_name(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}".strip() or obj.owner.username

    def get_active_sessions(self, obj):
        sessions = obj.editing_sessions.filter(is_active=True)
        return EditingSessionSerializer(sessions, many=True).data

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_unresolved_comments(self, obj):
        return obj.comments.filter(is_resolved=False, parent=None).count()


class DocumentOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentOperation
        fields = [
            'id', 'operation_type', 'position', 'content', 'length',
            'attributes', 'base_version', 'user', 'created_at'
        ]


class ApplyOperationSerializer(serializers.Serializer):
    operation_type = serializers.ChoiceField(choices=['insert', 'delete', 'retain', 'format'])
    position = serializers.IntegerField(min_value=0)
    content = serializers.CharField(required=False, allow_blank=True)
    length = serializers.IntegerField(required=False, default=0)
    attributes = serializers.DictField(required=False, default=dict)
    base_version = serializers.IntegerField()


class DocumentTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentTemplate
        fields = [
            'id', 'name', 'description', 'template_type', 'content',
            'thumbnail_url', 'variables', 'is_system', 'use_count',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'is_system', 'use_count', 'created_by', 'created_at']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None


class CreateFromTemplateSerializer(serializers.Serializer):
    template_id = serializers.UUIDField()
    title = serializers.CharField(max_length=255)
    variables = serializers.DictField(required=False, default=dict)
