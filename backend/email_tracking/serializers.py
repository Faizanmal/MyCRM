"""
Email Tracking Serializers
"""

from rest_framework import serializers
from .models import (
    TrackedEmail, EmailEvent, EmailTemplate, EmailSequence,
    SequenceStep, SequenceEnrollment, EmailAnalytics
)


class EmailEventSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = EmailEvent
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']


class TrackedEmailSerializer(serializers.ModelSerializer):
    engagement_score = serializers.ReadOnlyField()
    is_opened = serializers.ReadOnlyField()
    is_clicked = serializers.ReadOnlyField()
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    events = EmailEventSerializer(many=True, read_only=True)
    
    class Meta:
        model = TrackedEmail
        fields = '__all__'
        read_only_fields = ['id', 'tracking_id', 'sent_at', 'delivered_at', 'first_opened_at', 
                           'last_opened_at', 'first_clicked_at', 'replied_at', 'open_count', 'click_count']


class TrackedEmailListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    engagement_score = serializers.ReadOnlyField()
    is_opened = serializers.ReadOnlyField()
    is_clicked = serializers.ReadOnlyField()
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    
    class Meta:
        model = TrackedEmail
        fields = ['id', 'subject', 'to_email', 'contact_name', 'status', 'sent_at', 
                  'open_count', 'click_count', 'engagement_score', 'is_opened', 'is_clicked']


class SendEmailSerializer(serializers.Serializer):
    """Serializer for sending tracked emails"""
    to_email = serializers.EmailField()
    to_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    contact_id = serializers.IntegerField(required=False, allow_null=True)
    opportunity_id = serializers.IntegerField(required=False, allow_null=True)
    subject = serializers.CharField(max_length=500)
    body_html = serializers.CharField()
    body_text = serializers.CharField(required=False, allow_blank=True)
    template_id = serializers.UUIDField(required=False, allow_null=True)
    schedule_at = serializers.DateTimeField(required=False, allow_null=True)


class EmailTemplateSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    
    class Meta:
        model = EmailTemplate
        fields = '__all__'
        read_only_fields = ['id', 'times_used', 'avg_open_rate', 'avg_click_rate', 
                           'avg_reply_rate', 'created_at', 'updated_at']


class SequenceStepSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    open_rate = serializers.ReadOnlyField()
    reply_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = SequenceStep
        fields = '__all__'
        read_only_fields = ['id', 'sent_count', 'open_count', 'click_count', 'reply_count']


class EmailSequenceSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    reply_rate = serializers.ReadOnlyField()
    steps = SequenceStepSerializer(many=True, read_only=True)
    
    class Meta:
        model = EmailSequence
        fields = '__all__'
        read_only_fields = ['id', 'total_enrolled', 'total_completed', 'total_replied', 
                           'created_at', 'updated_at']


class EmailSequenceListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    reply_rate = serializers.ReadOnlyField()
    step_count = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailSequence
        fields = ['id', 'name', 'status', 'total_enrolled', 'total_replied', 
                  'reply_rate', 'step_count', 'created_at']
    
    def get_step_count(self, obj):
        return obj.steps.count()


class SequenceEnrollmentSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    contact_email = serializers.EmailField(source='contact.email', read_only=True)
    sequence_name = serializers.CharField(source='sequence.name', read_only=True)
    
    class Meta:
        model = SequenceEnrollment
        fields = '__all__'
        read_only_fields = ['id', 'enrolled_at', 'completed_at', 'exited_at']


class EnrollContactSerializer(serializers.Serializer):
    """Serializer for enrolling contacts in sequences"""
    contact_ids = serializers.ListField(child=serializers.IntegerField())


class EmailAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAnalytics
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class EmailPerformanceSerializer(serializers.Serializer):
    """Email performance dashboard"""
    period = serializers.CharField()
    total_sent = serializers.IntegerField()
    total_delivered = serializers.IntegerField()
    total_opened = serializers.IntegerField()
    total_clicked = serializers.IntegerField()
    total_replied = serializers.IntegerField()
    open_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    click_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    reply_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    best_day = serializers.CharField()
    best_time = serializers.TimeField()
    top_templates = serializers.ListField()
