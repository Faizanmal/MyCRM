"""
Document Management Serializers
"""

from rest_framework import serializers
from .models import Document, DocumentTemplate, DocumentShare, DocumentComment, DocumentApproval


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Documents"""
    
    file_extension = serializers.CharField(read_only=True)
    is_image = serializers.BooleanField(read_only=True)
    is_pdf = serializers.BooleanField(read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'name', 'description', 'category', 'file', 'file_size', 'mime_type',
            'version', 'parent_document', 'lead', 'contact', 'opportunity',
            'access_level', 'extracted_text', 'ocr_processed', 'tags',
            'uploaded_by', 'uploaded_by_name', 'uploaded_at', 'updated_at',
            'download_count', 'last_accessed',
            'file_extension', 'is_image', 'is_pdf'
        ]
        read_only_fields = [
            'id', 'version', 'file_size', 'mime_type', 'extracted_text', 'ocr_processed',
            'uploaded_at', 'updated_at', 'download_count', 'last_accessed'
        ]
    
    def create(self, validated_data):
        """Set file metadata on creation"""
        file_obj = validated_data.get('file')
        if file_obj:
            validated_data['file_size'] = file_obj.size
            validated_data['mime_type'] = file_obj.content_type
        
        return super().create(validated_data)


class DocumentTemplateSerializer(serializers.ModelSerializer):
    """Serializer for Document Templates"""
    
    class Meta:
        model = DocumentTemplate
        fields = [
            'id', 'name', 'description', 'template_type', 'file',
            'variables', 'thumbnail', 'is_active',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DocumentShareSerializer(serializers.ModelSerializer):
    """Serializer for Document Shares"""
    
    is_expired = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    document_name = serializers.CharField(source='document.name', read_only=True)
    
    class Meta:
        model = DocumentShare
        fields = [
            'id', 'document', 'document_name', 'shared_with_email',
            'access_token', 'can_download', 'can_view', 'expires_at',
            'view_count', 'download_count', 'last_accessed',
            'shared_by', 'shared_at', 'is_expired', 'is_active'
        ]
        read_only_fields = [
            'id', 'access_token', 'view_count', 'download_count',
            'last_accessed', 'shared_at'
        ]


class DocumentCommentSerializer(serializers.ModelSerializer):
    """Serializer for Document Comments"""
    
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = DocumentComment
        fields = [
            'id', 'document', 'comment', 'page_number',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DocumentApprovalSerializer(serializers.ModelSerializer):
    """Serializer for Document Approvals"""
    
    approver_name = serializers.CharField(source='approver.username', read_only=True)
    document_name = serializers.CharField(source='document.name', read_only=True)
    
    class Meta:
        model = DocumentApproval
        fields = [
            'id', 'document', 'document_name', 'approver', 'approver_name',
            'status', 'comments', 'requested_by', 'requested_at', 'responded_at'
        ]
        read_only_fields = ['id', 'requested_at', 'responded_at']
