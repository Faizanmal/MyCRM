from rest_framework import serializers
from .models import (
    DealRoom, DealRoomParticipant, Channel, ChannelMembership,
    Message, CollaborativeDocument, DocumentComment,
    ApprovalWorkflow, ApprovalStep, ApprovalInstance, ApprovalAction
)
from django.contrib.auth import get_user_model

User = get_user_model()


class DealRoomParticipantSerializer(serializers.ModelSerializer):
    """Serializer for deal room participants."""
    user_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = DealRoomParticipant
        fields = [
            'id', 'deal_room', 'user', 'user_name', 'user_email', 'role',
            'can_invite', 'can_edit_room', 'can_upload_documents', 'can_delete_messages',
            'joined_at', 'last_seen_at', 'is_active',
            'email_notifications', 'push_notifications'
        ]
        read_only_fields = ['id', 'joined_at']
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email


class DealRoomSerializer(serializers.ModelSerializer):
    """Serializer for deal rooms."""
    owner_name = serializers.SerializerMethodField()
    participants = DealRoomParticipantSerializer(many=True, read_only=True)
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True, allow_null=True)
    
    class Meta:
        model = DealRoom
        fields = [
            'id', 'name', 'description', 'opportunity', 'opportunity_name',
            'status', 'privacy', 'owner', 'owner_name',
            'created_at', 'updated_at', 'archived_at',
            'message_count', 'document_count', 'participant_count',
            'participants'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'message_count', 
                           'document_count', 'participant_count']
    
    def get_owner_name(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}".strip() or obj.owner.email


class DealRoomListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing deal rooms."""
    owner_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DealRoom
        fields = [
            'id', 'name', 'status', 'privacy', 'owner_name',
            'created_at', 'updated_at',
            'message_count', 'document_count', 'participant_count'
        ]
    
    def get_owner_name(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}".strip() or obj.owner.email


class ChannelMembershipSerializer(serializers.ModelSerializer):
    """Serializer for channel membership."""
    user_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = ChannelMembership
        fields = [
            'id', 'channel', 'user', 'user_name', 'user_email',
            'joined_at', 'last_read_at', 'is_muted', 'is_pinned',
            'is_admin', 'can_post', 'can_invite'
        ]
        read_only_fields = ['id', 'joined_at']
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email


class ChannelSerializer(serializers.ModelSerializer):
    """Serializer for channels."""
    created_by_name = serializers.SerializerMethodField()
    memberships = ChannelMembershipSerializer(source='channelmembership_set', many=True, read_only=True)
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Channel
        fields = [
            'id', 'name', 'description', 'channel_type',
            'created_by', 'created_by_name',
            'is_archived', 'is_read_only', 'allow_threads', 'allow_file_sharing',
            'created_at', 'updated_at', 'archived_at',
            'message_count', 'member_count',
            'memberships', 'unread_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'message_count', 'member_count']
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.email
        return None
    
    def get_unread_count(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user:
            membership = obj.channelmembership_set.filter(user=user).first()
            if membership:
                return obj.messages.filter(created_at__gt=membership.last_read_at).count()
        return 0


class ChannelListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing channels."""
    created_by_name = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Channel
        fields = [
            'id', 'name', 'channel_type', 'created_by_name',
            'is_archived', 'created_at', 'updated_at',
            'message_count', 'member_count', 'unread_count'
        ]
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.email
        return None
    
    def get_unread_count(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user:
            membership = obj.channelmembership_set.filter(user=user).first()
            if membership:
                return obj.messages.filter(created_at__gt=membership.last_read_at).count()
        return 0


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for messages."""
    sender_name = serializers.SerializerMethodField()
    sender_email = serializers.EmailField(source='sender.email', read_only=True, allow_null=True)
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'channel', 'deal_room', 'sender', 'sender_name', 'sender_email',
            'message_type', 'content', 'parent_message', 'thread_reply_count',
            'attachments', 'reactions', 'mentioned_users',
            'created_at', 'updated_at', 'edited_at', 'deleted_at',
            'is_pinned', 'is_edited', 'is_deleted', 'reply_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'thread_reply_count']
    
    def get_sender_name(self, obj):
        if obj.sender:
            return f"{obj.sender.first_name} {obj.sender.last_name}".strip() or obj.sender.email
        return "System"
    
    def get_reply_count(self, obj):
        return obj.replies.count()


class CollaborativeDocumentSerializer(serializers.ModelSerializer):
    """Serializer for collaborative documents."""
    owner_name = serializers.SerializerMethodField()
    locked_by_name = serializers.SerializerMethodField()
    deal_room_name = serializers.CharField(source='deal_room.name', read_only=True, allow_null=True)
    
    class Meta:
        model = CollaborativeDocument
        fields = [
            'id', 'title', 'description', 'doc_type', 'status',
            'file_path', 'file_size', 'mime_type',
            'owner', 'owner_name', 'deal_room', 'deal_room_name',
            'version', 'parent_version',
            'allow_comments', 'allow_downloads', 'is_locked', 'locked_by', 'locked_by_name',
            'created_at', 'updated_at',
            'view_count', 'download_count', 'comment_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'view_count', 
                           'download_count', 'comment_count', 'version']
    
    def get_owner_name(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}".strip() or obj.owner.email
    
    def get_locked_by_name(self, obj):
        if obj.locked_by:
            return f"{obj.locked_by.first_name} {obj.locked_by.last_name}".strip() or obj.locked_by.email
        return None


class DocumentCommentSerializer(serializers.ModelSerializer):
    """Serializer for document comments."""
    author_name = serializers.SerializerMethodField()
    resolved_by_name = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentComment
        fields = [
            'id', 'document', 'author', 'author_name', 'content',
            'page_number', 'position', 'highlighted_text',
            'parent_comment', 'is_resolved', 'resolved_by', 'resolved_by_name', 'resolved_at',
            'created_at', 'updated_at', 'reply_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_author_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.email
    
    def get_resolved_by_name(self, obj):
        if obj.resolved_by:
            return f"{obj.resolved_by.first_name} {obj.resolved_by.last_name}".strip() or obj.resolved_by.email
        return None
    
    def get_reply_count(self, obj):
        return obj.replies.count()


class ApprovalStepSerializer(serializers.ModelSerializer):
    """Serializer for approval steps."""
    approver_names = serializers.SerializerMethodField()
    
    class Meta:
        model = ApprovalStep
        fields = [
            'id', 'workflow', 'name', 'description', 'step_type', 'order',
            'approvers', 'approver_names', 'approver_count_required',
            'conditions', 'allow_delegate', 'allow_comments',
            'timeout_hours', 'timeout_action'
        ]
        read_only_fields = ['id']
    
    def get_approver_names(self, obj):
        return [
            f"{user.first_name} {user.last_name}".strip() or user.email
            for user in obj.approvers.all()
        ]


class ApprovalWorkflowSerializer(serializers.ModelSerializer):
    """Serializer for approval workflows."""
    created_by_name = serializers.SerializerMethodField()
    steps = ApprovalStepSerializer(many=True, read_only=True)
    
    class Meta:
        model = ApprovalWorkflow
        fields = [
            'id', 'name', 'description', 'is_active', 'is_sequential',
            'auto_start_on_create', 'trigger_conditions',
            'created_by', 'created_by_name',
            'created_at', 'updated_at',
            'total_instances', 'completed_instances',
            'steps'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_instances', 'completed_instances']
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.email
        return None


class ApprovalActionSerializer(serializers.ModelSerializer):
    """Serializer for approval actions."""
    actor_name = serializers.SerializerMethodField()
    delegated_to_name = serializers.SerializerMethodField()
    step_name = serializers.CharField(source='step.name', read_only=True)
    
    class Meta:
        model = ApprovalAction
        fields = [
            'id', 'instance', 'step', 'step_name',
            'actor', 'actor_name', 'action', 'comment',
            'delegated_to', 'delegated_to_name',
            'created_at', 'ip_address'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_actor_name(self, obj):
        return f"{obj.actor.first_name} {obj.actor.last_name}".strip() or obj.actor.email
    
    def get_delegated_to_name(self, obj):
        if obj.delegated_to:
            return f"{obj.delegated_to.first_name} {obj.delegated_to.last_name}".strip() or obj.delegated_to.email
        return None


class ApprovalInstanceSerializer(serializers.ModelSerializer):
    """Serializer for approval instances."""
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    requested_by_name = serializers.SerializerMethodField()
    current_step_name = serializers.CharField(source='current_step.name', read_only=True, allow_null=True)
    actions = ApprovalActionSerializer(many=True, read_only=True)
    pending_approvers = serializers.SerializerMethodField()
    
    class Meta:
        model = ApprovalInstance
        fields = [
            'id', 'workflow', 'workflow_name', 'content_type', 'object_id',
            'requested_by', 'requested_by_name', 'title', 'description',
            'status', 'current_step', 'current_step_name',
            'created_at', 'updated_at', 'completed_at',
            'attachments', 'metadata',
            'actions', 'pending_approvers'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_requested_by_name(self, obj):
        return f"{obj.requested_by.first_name} {obj.requested_by.last_name}".strip() or obj.requested_by.email
    
    def get_pending_approvers(self, obj):
        if obj.current_step:
            approved_users = obj.actions.filter(
                step=obj.current_step,
                action='approved'
            ).values_list('actor_id', flat=True)
            
            pending = obj.current_step.approvers.exclude(id__in=approved_users)
            return [
                {
                    'id': str(user.id),
                    'name': f"{user.first_name} {user.last_name}".strip() or user.email,
                    'email': user.email
                }
                for user in pending
            ]
        return []


class ApprovalInstanceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing approval instances."""
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    requested_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ApprovalInstance
        fields = [
            'id', 'workflow_name', 'requested_by_name', 'title',
            'status', 'created_at', 'updated_at', 'completed_at'
        ]
    
    def get_requested_by_name(self, obj):
        return f"{obj.requested_by.first_name} {obj.requested_by.last_name}".strip() or obj.requested_by.email
