from django.contrib import admin

from .models import (
    CollaborativeDocument,
    DocumentCollaborator,
    DocumentComment,
    DocumentOperation,
    DocumentTemplate,
    DocumentVersion,
    EditingSession,
)


@admin.register(CollaborativeDocument)
class CollaborativeDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'status', 'owner', 'version', 'updated_at']
    list_filter = ['document_type', 'status', 'is_locked']
    search_fields = ['title', 'content_text']
    date_hierarchy = 'created_at'


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ['document', 'version', 'created_by', 'created_at', 'is_restored']
    list_filter = ['is_restored']


@admin.register(DocumentCollaborator)
class DocumentCollaboratorAdmin(admin.ModelAdmin):
    list_display = ['document', 'user', 'permission', 'added_at']
    list_filter = ['permission']


@admin.register(DocumentComment)
class DocumentCommentAdmin(admin.ModelAdmin):
    list_display = ['document', 'author', 'comment_type', 'is_resolved', 'created_at']
    list_filter = ['comment_type', 'is_resolved']


@admin.register(EditingSession)
class EditingSessionAdmin(admin.ModelAdmin):
    list_display = ['document', 'user', 'is_active', 'connected_at', 'last_activity']
    list_filter = ['is_active']


@admin.register(DocumentOperation)
class DocumentOperationAdmin(admin.ModelAdmin):
    list_display = ['document', 'user', 'operation_type', 'position', 'created_at']
    list_filter = ['operation_type']


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'is_system', 'use_count', 'created_at']
    list_filter = ['template_type', 'is_system']
