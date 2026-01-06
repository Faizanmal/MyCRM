"""
Document E-Signature Admin Configuration
"""

from django.contrib import admin

from .models import (
    Document,
    DocumentAnalytics,
    DocumentAuditLog,
    DocumentRecipient,
    DocumentTemplate,
    SavedSignature,
    Signature,
    SignatureField,
)


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'created_by', 'is_active', 'times_used', 'created_at']
    list_filter = ['template_type', 'is_active', 'is_shared']
    search_fields = ['name', 'description']
    readonly_fields = ['times_used', 'avg_completion_time']


class DocumentRecipientInline(admin.TabularInline):
    model = DocumentRecipient
    extra = 0
    readonly_fields = ['access_token', 'viewed_at', 'signed_at', 'declined_at']


class SignatureFieldInline(admin.TabularInline):
    model = SignatureField
    extra = 0


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'created_by', 'signing_progress', 'sent_at', 'completed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'created_by__email']
    readonly_fields = ['uuid', 'sent_at', 'completed_at']
    inlines = [DocumentRecipientInline]
    raw_id_fields = ['opportunity', 'contact', 'template']


@admin.register(DocumentRecipient)
class DocumentRecipientAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'document', 'recipient_type', 'viewed_at', 'signed_at']
    list_filter = ['recipient_type']
    search_fields = ['name', 'email', 'document__name']
    readonly_fields = ['access_token', 'viewed_at', 'signed_at', 'declined_at']


@admin.register(Signature)
class SignatureAdmin(admin.ModelAdmin):
    list_display = ['signer_name', 'signer_email', 'signature_type', 'ip_address', 'created_at']
    list_filter = ['signature_type', 'created_at']
    search_fields = ['signer_name', 'signer_email']
    readonly_fields = ['created_at']


@admin.register(DocumentAuditLog)
class DocumentAuditLogAdmin(admin.ModelAdmin):
    list_display = ['document', 'action', 'recipient', 'ip_address', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['document__name']
    readonly_fields = ['created_at']


@admin.register(SavedSignature)
class SavedSignatureAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'is_default', 'created_at']
    list_filter = ['is_default']
    search_fields = ['user__email', 'name']


@admin.register(DocumentAnalytics)
class DocumentAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'documents_sent', 'documents_completed', 'total_value_signed']
    list_filter = ['date']
    search_fields = ['user__email']
    date_hierarchy = 'date'
