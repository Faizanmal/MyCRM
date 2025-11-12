"""
Activity Feed Views
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils import timezone

from .models import Activity, Comment, Mention, Notification, Follow
from .serializers import (
    ActivitySerializer, CommentSerializer, MentionSerializer,
    NotificationSerializer, FollowSerializer
)


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing activity feed
    """
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['action', 'actor', 'content_type']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter activities based on user permissions"""
        queryset = Activity.objects.filter(is_public=True)
        
        # Add user's private activities
        queryset = queryset | Activity.objects.filter(actor=self.request.user)
        
        return queryset.distinct()
    
    @action(detail=False, methods=['get'])
    def my_feed(self, request):
        """Get personalized activity feed"""
        # Activities from followed entities
        follows = Follow.objects.filter(user=request.user)
        
        activities = Activity.objects.filter(
            Q(actor=request.user) |  # Own activities
            Q(is_public=True)  # Public activities
        )
        
        # Filter by followed entities
        for follow in follows[:50]:  # Limit for performance
            activities = activities | Activity.objects.filter(
                content_type=follow.content_type,
                object_id=follow.object_id
            )
        
        activities = activities.distinct().order_by('-created_at')[:100]
        
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def for_entity(self, request):
        """Get activities for a specific entity"""
        model_name = request.query_params.get('model')
        object_id = request.query_params.get('id')
        
        if not model_name or not object_id:
            return Response(
                {'error': 'model and id parameters required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            content_type = ContentType.objects.get(model=model_name.lower())
        except ContentType.DoesNotExist:
            return Response(
                {'error': 'Invalid model name'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        activities = Activity.objects.filter(
            content_type=content_type,
            object_id=object_id
        ).order_by('-created_at')
        
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing comments
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['author', 'content_type', 'object_id']
    ordering_fields = ['created_at']
    ordering = ['created_at']
    
    def perform_create(self, serializer):
        """Set the comment author"""
        comment = serializer.save(author=self.request.user)
        
        # Process mentions
        self.process_mentions(comment)
    
    def perform_update(self, serializer):
        """Mark comment as edited"""
        comment = serializer.save(is_edited=True)
        self.process_mentions(comment)
    
    def process_mentions(self, comment):
        """Extract and create mentions from comment content"""
        import re
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Find @username patterns
        mentions = re.findall(r'@(\w+)', comment.content)
        
        for username in mentions:
            try:
                user = User.objects.get(username=username)
                comment.mentions.add(user)
                
                # Create mention record
                Mention.objects.create(
                    user=user,
                    content_type=ContentType.objects.get_for_model(Comment),
                    object_id=str(comment.id),
                    mentioned_by=self.request.user,
                    context=comment.content[:200]
                )
                
                # Create notification
                Notification.objects.create(
                    user=user,
                    notification_type='mention',
                    title=f'{self.request.user.username} mentioned you',
                    message=comment.content[:200],
                    content_type=comment.content_type,
                    object_id=comment.object_id,
                    actor=self.request.user
                )
            except User.DoesNotExist:
                pass
    
    @action(detail=False, methods=['get'])
    def for_entity(self, request):
        """Get comments for a specific entity"""
        model_name = request.query_params.get('model')
        object_id = request.query_params.get('id')
        
        if not model_name or not object_id:
            return Response(
                {'error': 'model and id parameters required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            content_type = ContentType.objects.get(model=model_name.lower())
        except ContentType.DoesNotExist:
            return Response(
                {'error': 'Invalid model name'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        comments = Comment.objects.filter(
            content_type=content_type,
            object_id=object_id,
            parent__isnull=True  # Only root comments
        ).order_by('created_at')
        
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        """Get replies to a comment"""
        comment = self.get_object()
        replies = comment.replies.all().order_by('created_at')
        
        serializer = self.get_serializer(replies, many=True)
        return Response(serializer.data)


class MentionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing mentions
    """
    queryset = Mention.objects.all()
    serializer_class = MentionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Only show user's own mentions"""
        return Mention.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark mention as read"""
        mention = self.get_object()
        mention.mark_as_read()
        
        serializer = self.get_serializer(mention)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all mentions as read"""
        Mention.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        return Response({'message': 'All mentions marked as read'})


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing notifications
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'is_read']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Only show user's own notifications"""
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        from django.utils import timezone
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        return Response({'message': 'All notifications marked as read'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return Response({'count': count})


class FollowViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing follows
    """
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only show user's own follows"""
        return Follow.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the follower"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def follow_entity(self, request):
        """Follow an entity"""
        model_name = request.data.get('model')
        object_id = request.data.get('id')
        
        if not model_name or not object_id:
            return Response(
                {'error': 'model and id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            content_type = ContentType.objects.get(model=model_name.lower())
        except ContentType.DoesNotExist:
            return Response(
                {'error': 'Invalid model name'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        follow, created = Follow.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=object_id
        )
        
        serializer = self.get_serializer(follow)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'])
    def unfollow_entity(self, request):
        """Unfollow an entity"""
        model_name = request.data.get('model')
        object_id = request.data.get('id')
        
        if not model_name or not object_id:
            return Response(
                {'error': 'model and id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            content_type = ContentType.objects.get(model=model_name.lower())
        except ContentType.DoesNotExist:
            return Response(
                {'error': 'Invalid model name'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        Follow.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=object_id
        ).delete()
        
        return Response({'message': 'Unfollowed successfully'})
