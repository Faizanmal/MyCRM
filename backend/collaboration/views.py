from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F, Count
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import (
    DealRoom, DealRoomParticipant, Channel, ChannelMembership,
    Message, CollaborativeDocument, DocumentComment,
    ApprovalWorkflow, ApprovalStep, ApprovalInstance, ApprovalAction
)
from .serializers import (
    DealRoomSerializer, DealRoomListSerializer, DealRoomParticipantSerializer,
    ChannelSerializer, ChannelListSerializer, ChannelMembershipSerializer,
    MessageSerializer, CollaborativeDocumentSerializer, DocumentCommentSerializer,
    ApprovalWorkflowSerializer, ApprovalStepSerializer,
    ApprovalInstanceSerializer, ApprovalInstanceListSerializer, ApprovalActionSerializer
)


class DealRoomViewSet(viewsets.ModelViewSet):
    """ViewSet for managing deal rooms."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'privacy_level', 'opportunity']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'name']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return DealRoomListSerializer
        return DealRoomSerializer

    def get_queryset(self):
        queryset = DealRoom.objects.all()
        
        # Filter by user's accessible rooms
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(participants__user=self.request.user) |
                Q(privacy_level='public') |
                Q(created_by=self.request.user)
            ).distinct()
        
        return queryset.select_related('opportunity', 'created_by').prefetch_related('participants__user')

    def perform_create(self, serializer):
        deal_room = serializer.save(created_by=self.request.user)
        # Auto-add creator as owner
        DealRoomParticipant.objects.create(
            deal_room=deal_room,
            user=self.request.user,
            role='owner',
            can_edit=True,
            can_invite=True,
            can_delete=True
        )

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a deal room."""
        deal_room = self.get_object()
        
        if deal_room.privacy_level == 'private':
            return Response(
                {'error': 'Cannot join private deal room without invitation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        participant, created = DealRoomParticipant.objects.get_or_create(
            deal_room=deal_room,
            user=request.user,
            defaults={'role': 'contributor'}
        )
        
        if not created:
            return Response({'message': 'Already a participant'}, status=status.HTTP_200_OK)
        
        return Response(
            DealRoomParticipantSerializer(participant).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a deal room."""
        deal_room = self.get_object()
        
        try:
            participant = DealRoomParticipant.objects.get(deal_room=deal_room, user=request.user)
            if participant.role == 'owner':
                return Response(
                    {'error': 'Owner cannot leave. Transfer ownership first.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            participant.delete()
            return Response({'message': 'Left deal room successfully'}, status=status.HTTP_204_NO_CONTENT)
        except DealRoomParticipant.DoesNotExist:
            return Response({'error': 'Not a participant'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Add a participant to the deal room."""
        deal_room = self.get_object()
        
        # Check permissions
        try:
            current_participant = DealRoomParticipant.objects.get(
                deal_room=deal_room,
                user=request.user
            )
            if not current_participant.can_invite:
                return Response(
                    {'error': 'No permission to invite participants'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except DealRoomParticipant.DoesNotExist:
            return Response({'error': 'Not a participant'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = DealRoomParticipantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(deal_room=deal_room)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        """Get all participants of a deal room."""
        deal_room = self.get_object()
        participants = deal_room.participants.select_related('user')
        serializer = DealRoomParticipantSerializer(participants, many=True)
        return Response(serializer.data)


class ChannelViewSet(viewsets.ModelViewSet):
    """ViewSet for managing channels."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['channel_type', 'is_archived']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'name']
    ordering = ['-updated_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ChannelListSerializer
        return ChannelSerializer

    def get_queryset(self):
        queryset = Channel.objects.all()
        
        # Filter by user's accessible channels
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(members__user=self.request.user) |
                Q(channel_type='public')
            ).distinct()
        
        # Filter by deal room if specified
        deal_room_id = self.request.query_params.get('deal_room')
        if deal_room_id:
            queryset = queryset.filter(deal_room_id=deal_room_id)
        
        return queryset.select_related('created_by', 'deal_room').prefetch_related('members__user')

    def perform_create(self, serializer):
        channel = serializer.save(created_by=self.request.user)
        # Auto-add creator as member
        ChannelMembership.objects.create(
            channel=channel,
            user=self.request.user,
            is_admin=True
        )

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a channel."""
        channel = self.get_object()
        
        if channel.channel_type == 'private':
            return Response(
                {'error': 'Cannot join private channel without invitation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        membership, created = ChannelMembership.objects.get_or_create(
            channel=channel,
            user=request.user
        )
        
        if not created:
            return Response({'message': 'Already a member'}, status=status.HTTP_200_OK)
        
        return Response(
            ChannelMembershipSerializer(membership).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a channel."""
        channel = self.get_object()
        
        try:
            membership = ChannelMembership.objects.get(channel=channel, user=request.user)
            membership.delete()
            return Response({'message': 'Left channel successfully'}, status=status.HTTP_204_NO_CONTENT)
        except ChannelMembership.DoesNotExist:
            return Response({'error': 'Not a member'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark channel as read up to a specific message."""
        channel = self.get_object()
        
        try:
            membership = ChannelMembership.objects.get(channel=channel, user=request.user)
            membership.last_read_at = timezone.now()
            membership.save(update_fields=['last_read_at'])
            return Response({'message': 'Marked as read'}, status=status.HTTP_200_OK)
        except ChannelMembership.DoesNotExist:
            return Response({'error': 'Not a member'}, status=status.HTTP_404_NOT_FOUND)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing messages."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['channel', 'deal_room', 'parent_message', 'is_edited', 'is_deleted']
    search_fields = ['content']
    ordering_fields = ['created_at']
    ordering = ['created_at']
    serializer_class = MessageSerializer

    def get_queryset(self):
        queryset = Message.objects.all()
        
        # Filter by user's accessible messages
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(channel__members__user=self.request.user) |
                Q(deal_room__participants__user=self.request.user) |
                Q(sender=self.request.user)
            ).distinct()
        
        # Optionally exclude deleted messages
        if not self.request.query_params.get('include_deleted'):
            queryset = queryset.filter(is_deleted=False)
        
        return queryset.select_related('sender', 'channel', 'deal_room', 'parent_message')

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        """Add or remove a reaction to a message."""
        message = self.get_object()
        emoji = request.data.get('emoji')
        
        if not emoji:
            return Response({'error': 'Emoji is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        reactions = message.reactions or {}
        
        if emoji in reactions:
            # Toggle reaction
            if request.user.id in reactions[emoji]:
                reactions[emoji].remove(request.user.id)
                if not reactions[emoji]:
                    del reactions[emoji]
            else:
                reactions[emoji].append(request.user.id)
        else:
            reactions[emoji] = [request.user.id]
        
        message.reactions = reactions
        message.save(update_fields=['reactions'])
        
        return Response(MessageSerializer(message).data)

    @action(detail=True, methods=['get'])
    def thread(self, request, pk=None):
        """Get all replies to a message."""
        message = self.get_object()
        replies = Message.objects.filter(parent_message=message, is_deleted=False).order_by('created_at')
        serializer = MessageSerializer(replies, many=True)
        return Response(serializer.data)


class CollaborativeDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing collaborative documents."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document_type', 'deal_room', 'is_locked']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'title', 'version']
    ordering = ['-updated_at']
    serializer_class = CollaborativeDocumentSerializer

    def get_queryset(self):
        queryset = CollaborativeDocument.objects.all()
        
        # Filter by user's accessible documents
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(deal_room__participants__user=self.request.user) |
                Q(created_by=self.request.user)
            ).distinct()
        
        # Optionally show only latest versions
        if self.request.query_params.get('latest_only') == 'true':
            queryset = queryset.filter(parent_version__isnull=True)
        
        return queryset.select_related('created_by', 'deal_room', 'locked_by', 'parent_version')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        """Lock a document for editing."""
        document = self.get_object()
        
        if document.is_locked and document.locked_by != request.user:
            return Response(
                {'error': f'Document is locked by {document.locked_by.get_full_name()}'},
                status=status.HTTP_409_CONFLICT
            )
        
        document.is_locked = True
        document.locked_by = request.user
        document.locked_at = timezone.now()
        document.save(update_fields=['is_locked', 'locked_by', 'locked_at'])
        
        return Response(CollaborativeDocumentSerializer(document).data)

    @action(detail=True, methods=['post'])
    def unlock(self, request, pk=None):
        """Unlock a document."""
        document = self.get_object()
        
        # Only the locker or admin can unlock
        if document.locked_by and document.locked_by != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Only the user who locked the document can unlock it'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        document.is_locked = False
        document.locked_by = None
        document.locked_at = None
        document.save(update_fields=['is_locked', 'locked_by', 'locked_at'])
        
        return Response(CollaborativeDocumentSerializer(document).data)

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """Get all versions of a document."""
        document = self.get_object()
        
        # Get all versions (both parent and children)
        versions = CollaborativeDocument.objects.filter(
            Q(id=document.id) | Q(parent_version=document)
        ).order_by('-version')
        
        serializer = CollaborativeDocumentSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create_version(self, request, pk=None):
        """Create a new version of the document."""
        parent_document = self.get_object()
        
        if parent_document.is_locked and parent_document.locked_by != request.user:
            return Response(
                {'error': 'Cannot create version of locked document'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create new version
        new_version = CollaborativeDocument.objects.create(
            deal_room=parent_document.deal_room,
            title=parent_document.title,
            description=request.data.get('description', parent_document.description),
            document_type=parent_document.document_type,
            file_url=request.data.get('file_url', parent_document.file_url),
            content=request.data.get('content', parent_document.content),
            version=parent_document.version + 1,
            parent_version=parent_document,
            created_by=request.user
        )
        
        return Response(
            CollaborativeDocumentSerializer(new_version).data,
            status=status.HTTP_201_CREATED
        )


class DocumentCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing document comments."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['document', 'parent_comment', 'is_resolved']
    ordering_fields = ['created_at']
    ordering = ['created_at']
    serializer_class = DocumentCommentSerializer

    def get_queryset(self):
        queryset = DocumentComment.objects.all()
        
        # Filter by user's accessible comments
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(document__deal_room__participants__user=self.request.user) |
                Q(created_by=self.request.user)
            ).distinct()
        
        return queryset.select_related('created_by', 'document', 'parent_comment')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve or unresolve a comment."""
        comment = self.get_object()
        is_resolved = request.data.get('is_resolved', True)
        
        comment.is_resolved = is_resolved
        comment.resolved_by = request.user if is_resolved else None
        comment.resolved_at = timezone.now() if is_resolved else None
        comment.save(update_fields=['is_resolved', 'resolved_by', 'resolved_at'])
        
        return Response(DocumentCommentSerializer(comment).data)


class ApprovalWorkflowViewSet(viewsets.ModelViewSet):
    """ViewSet for managing approval workflows."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    serializer_class = ApprovalWorkflowSerializer

    def get_queryset(self):
        return ApprovalWorkflow.objects.all().prefetch_related('steps__approvers')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ApprovalInstanceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing approval instances."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['workflow', 'status', 'initiated_by']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ApprovalInstanceListSerializer
        return ApprovalInstanceSerializer

    def get_queryset(self):
        queryset = ApprovalInstance.objects.all()
        
        # Filter by user's instances (initiated by or needs approval from)
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(initiated_by=self.request.user) |
                Q(workflow__steps__approvers=self.request.user)
            ).distinct()
        
        # Filter pending approvals
        if self.request.query_params.get('pending_only') == 'true':
            queryset = queryset.filter(
                status='pending',
                workflow__steps__approvers=self.request.user
            ).exclude(
                actions__actor=self.request.user,
                actions__step__approvers=self.request.user
            )
        
        return queryset.select_related('workflow', 'initiated_by')

    def perform_create(self, serializer):
        serializer.save(initiated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a step in the workflow."""
        instance = self.get_object()
        
        if instance.status != 'pending':
            return Response(
                {'error': 'Instance is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        step_id = request.data.get('step_id')
        comment = request.data.get('comment', '')
        
        try:
            step = ApprovalStep.objects.get(id=step_id, workflow=instance.workflow)
        except ApprovalStep.DoesNotExist:
            return Response({'error': 'Invalid step'}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user not in step.approvers.all():
            return Response(
                {'error': 'You are not an approver for this step'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if already actioned
        if ApprovalAction.objects.filter(instance=instance, step=step, actor=request.user).exists():
            return Response(
                {'error': 'You have already actioned this step'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create approval action
        ApprovalAction.objects.create(
            instance=instance,
            step=step,
            actor=request.user,
            action='approved',
            comment=comment
        )
        
        # Check if all required approvals are complete
        self._check_workflow_completion(instance)
        
        return Response(ApprovalInstanceSerializer(instance).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a step in the workflow."""
        instance = self.get_object()
        
        if instance.status != 'pending':
            return Response(
                {'error': 'Instance is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        step_id = request.data.get('step_id')
        comment = request.data.get('comment', '')
        
        try:
            step = ApprovalStep.objects.get(id=step_id, workflow=instance.workflow)
        except ApprovalStep.DoesNotExist:
            return Response({'error': 'Invalid step'}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user not in step.approvers.all():
            return Response(
                {'error': 'You are not an approver for this step'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create rejection action
        ApprovalAction.objects.create(
            instance=instance,
            step=step,
            actor=request.user,
            action='rejected',
            comment=comment
        )
        
        # Reject the entire workflow
        instance.status = 'rejected'
        instance.completed_at = timezone.now()
        instance.save(update_fields=['status', 'completed_at'])
        
        return Response(ApprovalInstanceSerializer(instance).data)

    def _check_workflow_completion(self, instance):
        """Check if workflow is complete and update status."""
        workflow = instance.workflow
        
        # Get all approval steps
        approval_steps = workflow.steps.filter(step_type='approval')
        
        for step in approval_steps:
            # Check if step has all required approvals
            approvals_count = ApprovalAction.objects.filter(
                instance=instance,
                step=step,
                action='approved'
            ).count()
            
            required_approvals = step.approvers.count()
            
            if approvals_count < required_approvals:
                return  # Not all steps approved yet
        
        # All steps approved
        instance.status = 'approved'
        instance.completed_at = timezone.now()
        instance.save(update_fields=['status', 'completed_at'])
