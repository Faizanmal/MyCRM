from django.contrib import admin

from .models import Document, DocumentApproval, DocumentComment, DocumentShare, DocumentTemplate


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'version', 'uploaded_by', 'uploaded_at', 'download_count']
    list_filter = ['category', 'access_level', 'ocr_processed']
    search_fields = ['name', 'description', 'extracted_text']
    readonly_fields = ['uploaded_at', 'updated_at', 'download_count']


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'is_active', 'created_at']
    list_filter = ['template_type', 'is_active']
    search_fields = ['name', 'description']


@admin.register(DocumentShare)
class DocumentShareAdmin(admin.ModelAdmin):
    list_display = ['document', 'shared_with_email', 'shared_by', 'expires_at', 'view_count']
    list_filter = ['shared_at', 'expires_at']
    search_fields = ['shared_with_email']


@admin.register(DocumentComment)
class DocumentCommentAdmin(admin.ModelAdmin):
    list_display = ['document', 'created_by', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['document__name', 'created_by__username', 'content']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DocumentApproval)
class DocumentApprovalAdmin(admin.ModelAdmin):
    list_display = ['document', 'approver', 'status', 'requested_at', 'responded_at']
    list_filter = ['status', 'requested_at']
    search_fields = ['document__name', 'approver__username']
