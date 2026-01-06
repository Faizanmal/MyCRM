"""
Document E-Signature Serializers
"""

from rest_framework import serializers

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


class DocumentTemplateSerializer(serializers.ModelSerializer):
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)

    class Meta:
        model = DocumentTemplate
        fields = '__all__'
        read_only_fields = ['created_by', 'times_used', 'avg_completion_time']


class SignatureFieldSerializer(serializers.ModelSerializer):
    field_type_display = serializers.CharField(source='get_field_type_display', read_only=True)

    class Meta:
        model = SignatureField
        fields = '__all__'


class DocumentRecipientSerializer(serializers.ModelSerializer):
    recipient_type_display = serializers.CharField(source='get_recipient_type_display', read_only=True)
    fields = SignatureFieldSerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = DocumentRecipient
        fields = '__all__'
        read_only_fields = ['access_token', 'viewed_at', 'signed_at', 'declined_at']

    def get_status(self, obj):
        if obj.declined_at:
            return 'declined'
        if obj.signed_at:
            return 'signed'
        if obj.viewed_at:
            return 'viewed'
        return 'pending'


class DocumentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    recipients = DocumentRecipientSerializer(many=True, read_only=True)
    signing_progress = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['uuid', 'created_by', 'sent_at', 'completed_at']


class DocumentCreateSerializer(serializers.ModelSerializer):
    recipients = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    fields = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Document
        fields = ['name', 'template', 'opportunity', 'contact', 'content_html',
                  'expires_at', 'require_all_signatures', 'signing_order',
                  'send_reminders', 'document_value', 'recipients', 'fields']

    def create(self, validated_data):
        recipients_data = validated_data.pop('recipients', [])
        fields_data = validated_data.pop('fields', [])

        document = Document.objects.create(**validated_data)

        # Create recipients
        recipient_map = {}
        for i, recipient_data in enumerate(recipients_data):
            recipient = DocumentRecipient.objects.create(
                document=document,
                signing_order=i,
                **recipient_data
            )
            recipient_map[i] = recipient

        # Create fields
        for field_data in fields_data:
            recipient_index = field_data.pop('recipient_index', 0)
            recipient = recipient_map.get(recipient_index)
            if recipient:
                SignatureField.objects.create(
                    document=document,
                    recipient=recipient,
                    **field_data
                )

        return document


class SignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signature
        fields = '__all__'
        read_only_fields = ['created_at']


class DocumentAuditLogSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = DocumentAuditLog
        fields = '__all__'


class SavedSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedSignature
        fields = '__all__'
        read_only_fields = ['user']


class DocumentAnalyticsSerializer(serializers.ModelSerializer):
    completion_rate = serializers.SerializerMethodField()

    class Meta:
        model = DocumentAnalytics
        fields = '__all__'

    def get_completion_rate(self, obj):
        if obj.documents_sent > 0:
            return round((obj.documents_completed / obj.documents_sent) * 100, 1)
        return 0


# Action serializers
class SignDocumentSerializer(serializers.Serializer):
    """Serialize signature submission"""
    access_token = serializers.CharField()
    access_code = serializers.CharField(required=False, allow_blank=True)
    fields = serializers.ListField(child=serializers.DictField())
    ip_address = serializers.IPAddressField(required=False)
    user_agent = serializers.CharField(required=False, allow_blank=True)


class DeclineDocumentSerializer(serializers.Serializer):
    """Serialize decline submission"""
    access_token = serializers.CharField()
    reason = serializers.CharField(required=False, allow_blank=True)


class SendDocumentSerializer(serializers.Serializer):
    """Serialize send action"""
    message = serializers.CharField(required=False, allow_blank=True)
    expires_in_days = serializers.IntegerField(required=False, default=30)
