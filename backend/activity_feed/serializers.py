"""
Activity Feed Serializers
"""

from rest_framework import serializers
from .models import Activity, Comment, Mention, Notification, Follow


class ActivitySerializer(serializers.ModelSerializer):
    """Serializer for Activities"""
    
    actor_name = serializers.CharField(source='actor.username', read_only=True)
    actor_email = serializers.CharField(source='actor.email', read_only=True)
    target_type = serializers.CharField(source='content_type.model', read_only=True)
    
    class Meta:
        model = Activity
        fields = [
            'id', 'actor', 'actor_name', 'actor_email', 'action',
            'content_type', 'object_id', 'target_type',
            'description', 'metadata', 'is_public', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comments"""
    
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_email = serializers.CharField(source='author.email', read_only=True)
    target_type = serializers.CharField(source='content_type.model', read_only=True)
    replies_count = serializers.SerializerMethodField()
    mentions_list = serializers.PrimaryKeyRelatedField(source='mentions', many=True, read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'author_name', 'author_email',
            'content_type', 'object_id', 'target_type',
            'content', 'parent', 'mentions', 'mentions_list',
            'created_at', 'updated_at', 'is_edited', 'replies_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_edited']
    
    def get_replies_count(self, obj):
        return obj.replies.count()


class MentionSerializer(serializers.ModelSerializer):
    """Serializer for Mentions"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    mentioned_by_name = serializers.CharField(source='mentioned_by.username', read_only=True)
    source_type = serializers.CharField(source='content_type.model', read_only=True)
    
    class Meta:
        model = Mention
        fields = [
            'id', 'user', 'user_name', 'mentioned_by', 'mentioned_by_name',
            'content_type', 'object_id', 'source_type',
            'context', 'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notifications"""
    
    actor_name = serializers.CharField(source='actor.username', read_only=True)
    target_type = serializers.CharField(source='content_type.model', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'notification_type', 'title', 'message',
            'content_type', 'object_id', 'target_type',
            'actor', 'actor_name', 'is_read', 'read_at',
            'action_url', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for Follows"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    target_type = serializers.CharField(source='content_type.model', read_only=True)
    
    class Meta:
        model = Follow
        fields = [
            'id', 'user', 'user_name', 'content_type', 'object_id',
            'target_type', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
