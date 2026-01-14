"""
Real-Time Collaboration Views
"""

import secrets

from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    CollaborativeDocument,
    DocumentCollaborator,
    DocumentComment,
    DocumentOperation,
    DocumentTemplate,
    DocumentVersion,
)
from .serializers import (
    AddCollaboratorSerializer,
    ApplyOperationSerializer,
    CollaborativeDocumentDetailSerializer,
    CollaborativeDocumentListSerializer,
    CreateFromTemplateSerializer,
    DocumentCollaboratorSerializer,
    DocumentCommentSerializer,
    DocumentTemplateSerializer,
    DocumentVersionListSerializer,
    EditingSessionSerializer,
)


class CollaborativeDocumentViewSet(viewsets.ModelViewSet):
    """CRUD and collaboration features for documents"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return CollaborativeDocument.objects.filter(
            Q(owner=user) |
            Q(collaborators__user=user) |
            Q(is_public=True)
        ).distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return CollaborativeDocumentListSerializer
        return CollaborativeDocumentDetailSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        # Save version before update
        doc = self.get_object()
        DocumentVersion.objects.create(
            document=doc,
            version=doc.version,
            content=doc.content,
            content_text=doc.content_text,
            created_by=self.request.user
        )

        serializer.save(
            version=doc.version + 1,
            last_edited_by=self.request.user
        )

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """Get version history"""
        doc = self.get_object()
        versions = DocumentVersion.objects.filter(document=doc)
        return Response(DocumentVersionListSerializer(versions, many=True).data)

    @action(detail=True, methods=['post'])
    def restore_version(self, request, pk=None):
        """Restore a previous version"""
        doc = self.get_object()
        version_number = request.data.get('version')

        try:
            version = DocumentVersion.objects.get(document=doc, version=version_number)
        except DocumentVersion.DoesNotExist:
            return Response(
                {"error": "Version not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Save current as new version
        DocumentVersion.objects.create(
            document=doc,
            version=doc.version,
            content=doc.content,
            content_text=doc.content_text,
            created_by=request.user
        )

        # Restore
        doc.content = version.content
        doc.content_text = version.content_text
        doc.version = doc.version + 1
        doc.last_edited_by = request.user
        doc.save()

        # Mark as restored
        new_version = DocumentVersion.objects.create(
            document=doc,
            version=doc.version,
            content=doc.content,
            content_text=doc.content_text,
            created_by=request.user,
            is_restored=True,
            restored_from=version_number
        )

        return Response(CollaborativeDocumentDetailSerializer(doc, context={'request': request}).data)

    @action(detail=True, methods=['get', 'post', 'delete'])
    def collaborators(self, request, pk=None):
        """Manage document collaborators"""
        doc = self.get_object()

        if request.method == 'GET':
            collaborators = doc.collaborators.all()
            return Response(DocumentCollaboratorSerializer(collaborators, many=True).data)

        elif request.method == 'POST':
            serializer = AddCollaboratorSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            collaborator, created = DocumentCollaborator.objects.update_or_create(
                document=doc,
                user_id=serializer.validated_data['user_id'],
                defaults={
                    'permission': serializer.validated_data['permission'],
                    'notify_on_changes': serializer.validated_data['notify_on_changes'],
                    'notify_on_comments': serializer.validated_data['notify_on_comments'],
                    'added_by': request.user
                }
            )

            return Response(
                DocumentCollaboratorSerializer(collaborator).data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )

        elif request.method == 'DELETE':
            user_id = request.data.get('user_id')
            DocumentCollaborator.objects.filter(document=doc, user_id=user_id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """Get/add comments"""
        doc = self.get_object()

        if request.method == 'GET':
            comments = doc.comments.filter(parent=None)
            resolved = request.query_params.get('resolved')
            if resolved == 'true':
                comments = comments.filter(is_resolved=True)
            elif resolved == 'false':
                comments = comments.filter(is_resolved=False)

            return Response(DocumentCommentSerializer(comments, many=True).data)

        elif request.method == 'POST':
            serializer = DocumentCommentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(document=doc, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='comments/(?P<comment_id>[^/.]+)/resolve')
    def resolve_comment(self, request, pk=None, comment_id=None):
        """Resolve a comment"""
        doc = self.get_object()
        try:
            comment = doc.comments.get(id=comment_id)
        except DocumentComment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        comment.is_resolved = True
        comment.resolved_by = request.user
        comment.resolved_at = timezone.now()
        comment.save()

        return Response(DocumentCommentSerializer(comment).data)

    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        """Lock document for exclusive editing"""
        doc = self.get_object()

        if doc.is_locked and doc.locked_by != request.user:
            return Response(
                {"error": f"Document is locked by {doc.locked_by.username}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        doc.is_locked = True
        doc.locked_by = request.user
        doc.locked_at = timezone.now()
        doc.save()

        return Response({"message": "Document locked"})

    @action(detail=True, methods=['post'])
    def unlock(self, request, pk=None):
        """Unlock document"""
        doc = self.get_object()

        if doc.is_locked and doc.locked_by != request.user:
            return Response(
                {"error": "Only the lock owner can unlock"},
                status=status.HTTP_403_FORBIDDEN
            )

        doc.is_locked = False
        doc.locked_by = None
        doc.locked_at = None
        doc.save()

        return Response({"message": "Document unlocked"})

    @action(detail=True, methods=['post'])
    def generate_share_link(self, request, pk=None):
        """Generate a public share link"""
        doc = self.get_object()

        if not doc.public_link_token:
            doc.public_link_token = secrets.token_urlsafe(32)

        doc.public_link_enabled = True
        doc.save()

        return Response({
            "share_link": f"/documents/shared/{doc.public_link_token}",
            "token": doc.public_link_token
        })

    @action(detail=True, methods=['get'])
    def active_editors(self, request, pk=None):
        """Get active editing sessions"""
        doc = self.get_object()
        sessions = doc.editing_sessions.filter(is_active=True)
        return Response(EditingSessionSerializer(sessions, many=True).data)

    @action(detail=True, methods=['post'])
    def apply_operation(self, request, pk=None):
        """Apply an operational transform operation"""
        doc = self.get_object()
        serializer = ApplyOperationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Verify version
        if data['base_version'] != doc.version:
            # Transform operation against concurrent changes
            return Response(
                {"error": "Version conflict", "current_version": doc.version},
                status=status.HTTP_409_CONFLICT
            )

        # Record operation
        operation = DocumentOperation.objects.create(
            document=doc,
            user=request.user,
            operation_type=data['operation_type'],
            position=data['position'],
            content=data.get('content', ''),
            length=data.get('length', 0),
            attributes=data.get('attributes', {}),
            base_version=data['base_version']
        )

        # Update document version
        doc.version += 1
        doc.last_edited_by = request.user
        doc.save()

        return Response({
            "operation_id": str(operation.id),
            "new_version": doc.version
        })


class DocumentTemplateViewSet(viewsets.ModelViewSet):
    """Document templates"""
    serializer_class = DocumentTemplateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DocumentTemplate.objects.filter(
            Q(is_system=True) |
            Q(created_by=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['post'])
    def create_from_template(self, request):
        """Create a document from template"""
        serializer = CreateFromTemplateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            template = DocumentTemplate.objects.get(id=data['template_id'])
        except DocumentTemplate.DoesNotExist:
            return Response({"error": "Template not found"}, status=status.HTTP_404_NOT_FOUND)

        # Create document from template
        doc = CollaborativeDocument.objects.create(
            title=data['title'],
            document_type=template.template_type,
            content=template.content,
            owner=request.user
        )

        # Increment template usage
        template.use_count += 1
        template.save()

        return Response(
            CollaborativeDocumentDetailSerializer(doc, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class SharedDocumentView(APIView):
    """Access shared documents via public link"""
    permission_classes = []

    def get(self, request, token):
        try:
            doc = CollaborativeDocument.objects.get(
                public_link_token=token,
                public_link_enabled=True
            )
        except CollaborativeDocument.DoesNotExist:
            return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(CollaborativeDocumentDetailSerializer(doc, context={'request': request}).data)


class MyCollaborationsView(APIView):
    """Get documents user is collaborating on"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        collaborations = DocumentCollaborator.objects.filter(
            user=request.user
        ).select_related('document')

        documents = [c.document for c in collaborations]

        return Response(
            CollaborativeDocumentListSerializer(documents, many=True).data
        )
