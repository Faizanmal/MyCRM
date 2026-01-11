"""
Customer Portal Serializers
"""

from rest_framework import serializers
from .models import (
    CustomerAccount, SupportTicket, TicketComment, 
    CustomerOrder, KnowledgeBaseArticle, PortalNotification
)


class CustomerAccountSerializer(serializers.ModelSerializer):
    """Serializer for customer account"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerAccount
        fields = [
            'id', 'email', 'is_active', 'is_verified', 
            'notification_preferences', 'timezone', 'language',
            'two_factor_enabled', 'last_login', 'created_at',
            'full_name'
        ]
        read_only_fields = ['id', 'email', 'is_verified', 'last_login', 'created_at']

    def get_full_name(self, obj):
        if obj.contact:
            return obj.contact.full_name
        return obj.email


class CustomerProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating customer profile"""
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    phone = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = CustomerAccount
        fields = [
            'notification_preferences', 'timezone', 'language',
            'first_name', 'last_name', 'phone'
        ]

    def update(self, instance, validated_data):
        # Update contact info
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)
        phone = validated_data.pop('phone', None)
        
        if instance.contact:
            if first_name:
                instance.contact.first_name = first_name
            if last_name:
                instance.contact.last_name = last_name
            if phone:
                instance.contact.phone = phone
            instance.contact.save()
        
        return super().update(instance, validated_data)


class TicketCommentSerializer(serializers.ModelSerializer):
    """Serializer for ticket comments"""
    author_name = serializers.SerializerMethodField()
    is_customer = serializers.SerializerMethodField()
    
    class Meta:
        model = TicketComment
        fields = [
            'id', 'content', 'is_internal', 'attachments',
            'author_name', 'is_customer', 'created_at'
        ]
        read_only_fields = ['id', 'is_internal', 'author_name', 'is_customer', 'created_at']

    def get_author_name(self, obj):
        if obj.customer:
            return obj.customer.contact.full_name if obj.customer.contact else obj.customer.email
        elif obj.internal_user:
            return f"{obj.internal_user.first_name} {obj.internal_user.last_name}"
        return "System"

    def get_is_customer(self, obj):
        return obj.customer is not None


class SupportTicketListSerializer(serializers.ModelSerializer):
    """Serializer for listing support tickets"""
    
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'ticket_number', 'subject', 'category', 
            'priority', 'status', 'created_at', 'updated_at'
        ]


class SupportTicketDetailSerializer(serializers.ModelSerializer):
    """Serializer for ticket details"""
    comments = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'ticket_number', 'subject', 'description', 
            'category', 'priority', 'status', 'resolution',
            'resolved_at', 'satisfaction_rating', 'satisfaction_feedback',
            'sla_response_due', 'sla_resolution_due', 'first_response_at',
            'assigned_to_name', 'comments', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'ticket_number', 'resolution', 'resolved_at',
            'first_response_at', 'assigned_to_name', 'comments'
        ]

    def get_comments(self, obj):
        # Only return non-internal comments to customers
        comments = obj.comments.filter(is_internal=False)
        return TicketCommentSerializer(comments, many=True).data

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
        return None


class SupportTicketCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating support tickets"""
    
    class Meta:
        model = SupportTicket
        fields = ['subject', 'description', 'category', 'priority']

    def create(self, validated_data):
        validated_data['customer'] = self.context['customer']
        return super().create(validated_data)


class CustomerOrderSerializer(serializers.ModelSerializer):
    """Serializer for customer orders"""
    
    class Meta:
        model = CustomerOrder
        fields = [
            'id', 'order_number', 'status', 'items', 
            'subtotal', 'tax', 'shipping', 'discount', 'total', 'currency',
            'shipping_address', 'tracking_number', 'tracking_url',
            'ordered_at', 'shipped_at', 'delivered_at', 'invoice_url'
        ]


class KnowledgeBaseArticleListSerializer(serializers.ModelSerializer):
    """Serializer for listing KB articles"""
    
    class Meta:
        model = KnowledgeBaseArticle
        fields = [
            'id', 'slug', 'title', 'excerpt', 'category', 
            'tags', 'is_featured', 'published_at'
        ]


class KnowledgeBaseArticleDetailSerializer(serializers.ModelSerializer):
    """Serializer for KB article details"""
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = KnowledgeBaseArticle
        fields = [
            'id', 'slug', 'title', 'content', 'excerpt', 
            'category', 'tags', 'is_featured',
            'view_count', 'helpful_count', 'not_helpful_count',
            'author_name', 'published_at', 'updated_at'
        ]

    def get_author_name(self, obj):
        if obj.author:
            return f"{obj.author.first_name} {obj.author.last_name}"
        return None


class PortalNotificationSerializer(serializers.ModelSerializer):
    """Serializer for portal notifications"""
    
    class Meta:
        model = PortalNotification
        fields = [
            'id', 'notification_type', 'title', 'message',
            'action_url', 'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'notification_type', 'title', 'message', 'action_url', 'created_at']


class PortalLoginSerializer(serializers.Serializer):
    """Serializer for portal login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class PortalPasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField()


class PortalPasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset"""
    token = serializers.CharField()
    password = serializers.CharField(min_length=8)
    password_confirm = serializers.CharField()

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data


class TicketFeedbackSerializer(serializers.Serializer):
    """Serializer for ticket satisfaction feedback"""
    rating = serializers.IntegerField(min_value=1, max_value=5)
    feedback = serializers.CharField(required=False, allow_blank=True)
