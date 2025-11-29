"""
Document E-Signature Views
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Sum, Avg
from django.db import models
from datetime import timedelta
from django.shortcuts import get_object_or_404

from .models import (
    DocumentTemplate, Document, DocumentRecipient, DocumentAuditLog, SavedSignature, DocumentAnalytics
)
from .serializers import (
    DocumentTemplateSerializer, DocumentSerializer, DocumentCreateSerializer,
    SignatureFieldSerializer, DocumentAuditLogSerializer, SavedSignatureSerializer, DocumentAnalyticsSerializer,
    SignDocumentSerializer, DeclineDocumentSerializer, SendDocumentSerializer
)
from .services import DocumentService


class DocumentTemplateViewSet(viewsets.ModelViewSet):
    """Manage document templates"""
    serializer_class = DocumentTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DocumentTemplate.objects.filter(
            models.Q(created_by=self.request.user) | models.Q(is_shared=True),
            is_active=True
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a template"""
        template = self.get_object()
        new_template = DocumentTemplate.objects.create(
            name=f"{template.name} (Copy)",
            template_type=template.template_type,
            description=template.description,
            content_html=template.content_html,
            css_styles=template.css_styles,
            merge_fields=template.merge_fields,
            created_by=request.user,
            is_shared=False
        )
        serializer = self.get_serializer(new_template)
        return Response(serializer.data, status=201)
    
    @action(detail=True, methods=['post'])
    def preview(self, request, pk=None):
        """Preview template with sample data"""
        template = self.get_object()
        sample_data = request.data.get('merge_data', {})
        
        service = DocumentService()
        preview_html = service.render_template(template, sample_data)
        
        return Response({'preview_html': preview_html})


# Import models for Q object


class DocumentViewSet(viewsets.ModelViewSet):
    """Manage documents for signature"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentCreateSerializer
        return DocumentSerializer
    
    def get_queryset(self):
        return Document.objects.filter(
            created_by=self.request.user
        ).prefetch_related('recipients', 'fields')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send document for signature"""
        document = self.get_object()
        serializer = SendDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = DocumentService()
        success, message = service.send_document(
            document,
            message=serializer.validated_data.get('message', ''),
            expires_in_days=serializer.validated_data.get('expires_in_days', 30)
        )
        
        if success:
            return Response({'status': 'sent', 'message': message})
        return Response({'status': 'error', 'message': message}, status=400)
    
    @action(detail=True, methods=['post'])
    def void(self, request, pk=None):
        """Void a document"""
        document = self.get_object()
        reason = request.data.get('reason', '')
        
        service = DocumentService()
        success, message = service.void_document(document, reason)
        
        if success:
            return Response({'status': 'voided'})
        return Response({'status': 'error', 'message': message}, status=400)
    
    @action(detail=True, methods=['post'])
    def remind(self, request, pk=None):
        """Send reminder to pending signers"""
        document = self.get_object()
        service = DocumentService()
        count = service.send_reminders(document)
        return Response({'reminders_sent': count})
    
    @action(detail=True, methods=['get'])
    def audit_log(self, request, pk=None):
        """Get document audit log"""
        document = self.get_object()
        logs = document.audit_logs.all()
        serializer = DocumentAuditLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Get download URL for signed document"""
        document = self.get_object()
        
        if document.status != 'completed':
            return Response(
                {'error': 'Document not yet completed'},
                status=400
            )
        
        service = DocumentService()
        url = service.get_signed_document_url(document)
        return Response({'download_url': url})
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get document statistics"""
        documents = self.get_queryset()
        
        return Response({
            'total': documents.count(),
            'draft': documents.filter(status='draft').count(),
            'sent': documents.filter(status='sent').count(),
            'completed': documents.filter(status='completed').count(),
            'declined': documents.filter(status='declined').count(),
            'expired': documents.filter(status='expired').count(),
        })


class SigningViewSet(viewsets.ViewSet):
    """Public endpoints for document signing"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'], url_path='view/(?P<token>[^/.]+)')
    def view_document(self, request, token=None):
        """View document for signing"""
        recipient = get_object_or_404(DocumentRecipient, access_token=token)
        document = recipient.document
        
        # Check document is signable
        if document.status in ['completed', 'voided', 'expired']:
            return Response(
                {'error': f'Document is {document.status}'},
                status=400
            )
        
        # Check expiration
        if document.expires_at and document.expires_at < timezone.now():
            document.status = 'expired'
            document.save()
            return Response({'error': 'Document has expired'}, status=400)
        
        # Check signing order
        if document.signing_order:
            earlier_recipients = document.recipients.filter(
                signing_order__lt=recipient.signing_order,
                signed_at__isnull=True
            )
            if earlier_recipients.exists():
                return Response(
                    {'error': 'Waiting for previous signers'},
                    status=400
                )
        
        # Record view
        if not recipient.viewed_at:
            recipient.viewed_at = timezone.now()
            recipient.viewed_from_ip = request.META.get('REMOTE_ADDR')
            recipient.save()
            
            DocumentAuditLog.objects.create(
                document=document,
                recipient=recipient,
                action='viewed',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Update document status
            if document.status == 'sent':
                document.status = 'viewed'
                document.save()
        
        # Return document data
        return Response({
            'document': {
                'name': document.name,
                'content_html': document.content_html,
            },
            'recipient': {
                'name': recipient.name,
                'email': recipient.email,
                'type': recipient.recipient_type,
            },
            'fields': SignatureFieldSerializer(recipient.fields.all(), many=True).data,
            'requires_access_code': document.access_code_required and not recipient.access_code,
        })
    
    @action(detail=False, methods=['post'], url_path='sign/(?P<token>[^/.]+)')
    def sign_document(self, request, token=None):
        """Submit signatures"""
        recipient = get_object_or_404(DocumentRecipient, access_token=token)
        document = recipient.document
        
        serializer = SignDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verify access code if required
        if document.access_code_required and recipient.access_code:
            if serializer.validated_data.get('access_code') != recipient.access_code:
                return Response({'error': 'Invalid access code'}, status=403)
        
        service = DocumentService()
        success, message = service.process_signature(
            recipient,
            serializer.validated_data['fields'],
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        if success:
            return Response({'status': 'signed', 'message': message})
        return Response({'status': 'error', 'message': message}, status=400)
    
    @action(detail=False, methods=['post'], url_path='decline/(?P<token>[^/.]+)')
    def decline_document(self, request, token=None):
        """Decline to sign"""
        recipient = get_object_or_404(DocumentRecipient, access_token=token)
        
        serializer = DeclineDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = DocumentService()
        service.decline_signature(
            recipient,
            reason=serializer.validated_data.get('reason', '')
        )
        
        return Response({'status': 'declined'})


class SavedSignatureViewSet(viewsets.ModelViewSet):
    """Manage user's saved signatures"""
    serializer_class = SavedSignatureSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SavedSignature.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # If marking as default, unmark others
        if serializer.validated_data.get('is_default'):
            SavedSignature.objects.filter(
                user=self.request.user, is_default=True
            ).update(is_default=False)
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set signature as default"""
        signature = self.get_object()
        SavedSignature.objects.filter(user=request.user).update(is_default=False)
        signature.is_default = True
        signature.save()
        return Response({'status': 'set as default'})


class DocumentAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """View document analytics"""
    serializer_class = DocumentAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DocumentAnalytics.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get analytics dashboard"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        analytics = self.get_queryset().filter(date__gte=start_date)
        
        totals = analytics.aggregate(
            total_created=Sum('documents_created'),
            total_sent=Sum('documents_sent'),
            total_completed=Sum('documents_completed'),
            total_declined=Sum('documents_declined'),
            total_value_sent=Sum('total_value_sent'),
            total_value_signed=Sum('total_value_signed'),
            avg_completion_hours=Avg('avg_completion_hours'),
        )
        
        return Response({
            'summary': totals,
            'completion_rate': self._calc_completion_rate(totals),
            'period_days': days,
        })
    
    def _calc_completion_rate(self, totals):
        sent = totals.get('total_sent') or 0
        completed = totals.get('total_completed') or 0
        if sent > 0:
            return round((completed / sent) * 100, 1)
        return 0
