"""
Document Management Views
"""

from django.db.models import Q
from django.http import FileResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, parsers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Document, DocumentApproval, DocumentComment, DocumentShare, DocumentTemplate
from .serializers import (
    DocumentApprovalSerializer,
    DocumentCommentSerializer,
    DocumentSerializer,
    DocumentShareSerializer,
    DocumentTemplateSerializer,
)
from .tasks import generate_document_from_template, process_document_ocr


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing documents with multi-tenant isolation and signed URL access
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'access_level', 'lead', 'contact', 'opportunity']
    search_fields = ['name', 'description', 'extracted_text', 'tags']
    ordering_fields = ['uploaded_at', 'name', 'download_count']

    def get_permissions(self):
        if self.action in ['signed_download']:
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        """Strict multi-tenant organization boundary check preventing IDOR"""
        queryset = super().get_queryset()
        user = self.request.user
        if not user or not user.is_authenticated:
            return queryset.none()
        if user.is_superuser:
            return queryset

        from multi_tenant.middleware import get_current_organization
        org = get_current_organization() or getattr(self.request, 'organization', None) or getattr(self.request, 'tenant', None)
        if not org:
            org = getattr(user, 'organization', None)
        if not org and hasattr(user, 'organization_memberships'):
            membership = user.organization_memberships.filter(is_active=True).first()
            if membership:
                org = membership.organization

        if org:
            return queryset.filter(organization=org)
        return queryset.filter(uploaded_by=user)

    def perform_create(self, serializer):
        """Set the uploader and trigger OCR if applicable"""
        document = serializer.save(uploaded_by=self.request.user)

        # Queue OCR processing for PDFs and images
        if document.is_pdf or document.is_image:
            process_document_ocr.delay(str(document.id))

    @action(detail=True, methods=['get'])
    def signed_url(self, request, pk=None, _pk=None):
        """Generate a time-limited cryptographically signed download URL"""
        document = self.get_object()

        user_role = getattr(request.user, 'role', None)
        if document.access_level == 'restricted' and user_role not in ['admin', 'manager'] and not request.user.is_superuser:
            return Response(
                {'error': 'Insufficient permissions'},
                status=status.HTTP_403_FORBIDDEN
            )

        from core.signed_urls import generate_signed_download_token
        expires_in = int(request.query_params.get('expires_in', 300))
        token = generate_signed_download_token(document.id, request.user.id, expires_in_seconds=expires_in)
        return Response({
            'download_url': f"/api/documents/documents/signed-download/?token={token}",
            'token': token,
            'expires_in': expires_in
        })

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def signed_download(self, request):
        """Download document via cryptographically signed expirable token"""
        token = request.query_params.get('token')
        if not token:
            return Response({'error': 'Signed token is required'}, status=status.HTTP_400_BAD_REQUEST)

        from core.signed_urls import verify_signed_download_token
        from django.core.signing import BadSignature, SignatureExpired

        try:
            payload = verify_signed_download_token(token)
        except SignatureExpired:
            return Response({'error': 'Signed URL has expired'}, status=status.HTTP_403_FORBIDDEN)
        except BadSignature:
            return Response({'error': 'Invalid or tampered signed URL'}, status=status.HTTP_403_FORBIDDEN)

        doc_id = payload.get('doc_id')
        try:
            document = Document.objects.get(id=doc_id)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

        document.download_count += 1
        document.last_accessed = timezone.now()
        document.save(update_fields=['download_count', 'last_accessed'])

        return FileResponse(
            document.file.open('rb'),
            as_attachment=True,
            filename=document.name
        )

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None, _pk=None):
        """Download a document"""
        document = self.get_object()

        # Check permissions
        # Check permissions
        user_role = getattr(request.user, 'role', None)
        if document.access_level == 'restricted' and user_role not in ['admin', 'manager'] and not request.user.is_superuser:
            return Response(
                {'error': 'Insufficient permissions'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update download stats
        document.download_count += 1
        document.last_accessed = timezone.now()
        document.save()

        # Return file
        try:
            return FileResponse(
                document.file.open('rb'),
                as_attachment=True,
                filename=document.name
            )
        except Exception as e:
            return Response(
                {'error': f'Error downloading file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def create_version(self, request, _pk=None):
        """Create a new version of a document"""
        document = self.get_object()
        new_file = request.FILES.get('file')

        if not new_file:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_version = document.create_version(new_file, request.user)
        serializer = self.get_serializer(new_version)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def versions(self, request, _pk=None):
        """Get all versions of a document"""
        document = self.get_object()

        # Get all versions (including current)
        root = document.parent_document if document.parent_document else document

        versions = Document.objects.filter(
            Q(id=root.id) | Q(parent_document=root)
        ).order_by('-version')

        serializer = self.get_serializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def share(self, request, _pk=None):
        """Share a document with external email"""
        document = self.get_object()

        email = request.data.get('email')
        expires_in_days = request.data.get('expires_in_days', 7)

        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create share
        share = DocumentShare.objects.create(
            document=document,
            shared_with_email=email,
            can_download=request.data.get('can_download', True),
            can_view=request.data.get('can_view', True),
            expires_at=timezone.now() + timezone.timedelta(days=expires_in_days),
            shared_by=request.user
        )

        serializer = DocumentShareSerializer(share)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def request_approval(self, request, _pk=None):
        """Request approval for a document"""
        document = self.get_object()

        approver_id = request.data.get('approver_id')
        if not approver_id:
            return Response(
                {'error': 'approver_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            approver = User.objects.get(id=approver_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Approver not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        approval = DocumentApproval.objects.create(
            document=document,
            approver=approver,
            requested_by=request.user
        )

        serializer = DocumentApprovalSerializer(approval)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DocumentTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing document templates
    """
    queryset = DocumentTemplate.objects.all()
    serializer_class = DocumentTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['template_type', 'is_active']
    search_fields = ['name', 'description']

    def perform_create(self, serializer):
        """Set the creator"""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def generate(self, request, _pk=None):
        """Generate a document from template"""
        template = self.get_object()

        variables = request.data.get('variables', {})
        entity_type = request.data.get('entity_type')  # lead, contact, opportunity
        entity_id = request.data.get('entity_id')

        # Queue document generation
        task = generate_document_from_template.delay(
            str(template.id),
            variables,
            entity_type,
            entity_id,
            request.user.id
        )

        return Response({
            'message': 'Document generation queued',
            'task_id': task.id
        }, status=status.HTTP_202_ACCEPTED)


class DocumentShareViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing document shares
    """
    queryset = DocumentShare.objects.all()
    serializer_class = DocumentShareSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['document']

    def get_permissions(self):
        if self.action in ['access', 'download']:
            return [AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def access(self, request):
        """Access a shared document via token"""
        token = request.query_params.get('token')

        if not token:
            return Response(
                {'error': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            share = DocumentShare.objects.get(access_token=token)
        except DocumentShare.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired share link'},
                status=status.HTTP_404_NOT_FOUND
            )

        if share.is_expired:
            return Response(
                {'error': 'Share link has expired'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update access stats
        share.view_count += 1
        share.last_accessed = timezone.now()
        share.save()

        # Return document info
        document_data = DocumentSerializer(share.document).data

        return Response({
            'document': document_data,
            'can_download': share.can_download,
            'can_view': share.can_view
        })

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def download(self, request):
        """Download document from an active share token"""
        token = request.query_params.get('token')
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            share = DocumentShare.objects.get(access_token=token)
        except (DocumentShare.DoesNotExist, ValueError):
            return Response({'error': 'Invalid or expired share link'}, status=status.HTTP_404_NOT_FOUND)

        if share.is_expired:
            return Response({'error': 'Share link has expired'}, status=status.HTTP_403_FORBIDDEN)

        if not share.can_download:
            return Response({'error': 'Download is not permitted for this share link'}, status=status.HTTP_403_FORBIDDEN)

        share.download_count += 1
        share.last_accessed = timezone.now()
        share.save(update_fields=['download_count', 'last_accessed'])

        return FileResponse(
            share.document.file.open('rb'),
            as_attachment=True,
            filename=share.document.name
        )


class DocumentCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for document comments
    """
    queryset = DocumentComment.objects.all()
    serializer_class = DocumentCommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['document']

    def get_permissions(self):
        if self.action in ['access', 'download']:
            return [AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Set the comment author"""
        serializer.save(created_by=self.request.user)


class DocumentApprovalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for document approvals
    """
    queryset = DocumentApproval.objects.all()
    serializer_class = DocumentApprovalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['document', 'approver', 'status']

    def get_queryset(self):
        """Filter to show user's approval requests"""
        queryset = super().get_queryset()

        user_role = getattr(self.request.user, 'role', None)
        if user_role != 'admin' and not self.request.user.is_superuser:
            # Show approvals where user is approver or requester
            queryset = queryset.filter(
                Q(approver=self.request.user) |
                Q(requested_by=self.request.user)
            )

        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, _pk=None):
        """Approve a document"""
        approval = self.get_object()

        if approval.approver != request.user:
            return Response(
                {'error': 'Only the assigned approver can approve'},
                status=status.HTTP_403_FORBIDDEN
            )

        if approval.status != 'pending':
            return Response(
                {'error': 'Approval already processed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        approval.status = 'approved'
        approval.comments = request.data.get('comments', '')
        approval.responded_at = timezone.now()
        approval.save()

        serializer = self.get_serializer(approval)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, _pk=None):
        """Reject a document"""
        approval = self.get_object()

        if approval.approver != request.user:
            return Response(
                {'error': 'Only the assigned approver can reject'},
                status=status.HTTP_403_FORBIDDEN
            )

        if approval.status != 'pending':
            return Response(
                {'error': 'Approval already processed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        approval.status = 'rejected'
        approval.comments = request.data.get('comments', '')
        approval.responded_at = timezone.now()
        approval.save()

        serializer = self.get_serializer(approval)
        return Response(serializer.data)
