"""
Email Campaign API Views
"""
from django.template import Context, Template
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from campaign_management.email_models import EmailCampaign, EmailRecipient
from campaign_management.models import EmailTemplate


class EmailTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'description', 'category', 'subject_template',
            'html_template', 'text_template', 'available_variables',
            'thumbnail_url', 'is_active', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class EmailCampaignSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    open_rate = serializers.FloatField(read_only=True)
    click_rate = serializers.FloatField(read_only=True)
    click_to_open_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = EmailCampaign
        fields = [
            'id', 'name', 'description', 'campaign_type', 'subject',
            'from_email', 'from_name', 'reply_to', 'template', 'template_name',
            'html_content', 'text_content', 'target_segment', 'exclude_segment',
            'status', 'scheduled_at', 'sent_at', 'drip_sequence',
            'track_opens', 'track_clicks', 'total_recipients', 'sent_count',
            'delivered_count', 'opened_count', 'clicked_count', 'bounced_count',
            'unsubscribed_count', 'open_rate', 'click_rate', 'click_to_open_rate',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'sent_at', 'total_recipients', 'sent_count',
            'delivered_count', 'opened_count', 'clicked_count', 'bounced_count',
            'unsubscribed_count', 'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class EmailRecipientSerializer(serializers.ModelSerializer):
    contact_name = serializers.SerializerMethodField()
    lead_name = serializers.SerializerMethodField()

    class Meta:
        model = EmailRecipient
        fields = [
            'id', 'campaign', 'email', 'contact', 'contact_name', 'lead', 'lead_name',
            'personalization_data', 'status', 'sent_at', 'delivered_at',
            'first_opened_at', 'last_opened_at', 'first_clicked_at', 'last_clicked_at',
            'open_count', 'click_count', 'error_message', 'bounce_reason', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_contact_name(self, obj):
        return obj.contact.full_name if obj.contact else None

    def get_lead_name(self, obj):
        return f"{obj.lead.first_name} {obj.lead.last_name}" if obj.lead else None


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """
    Email template management
    """
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'name']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def preview(self, request, pk=None):
        """Preview template with sample data"""
        template_obj = self.get_object()
        sample_data = request.data.get('sample_data', {})

        try:
            # Render subject
            subject_template = Template(template_obj.subject_template)
            subject = subject_template.render(Context(sample_data))

            # Render HTML
            html_template = Template(template_obj.html_template)
            html_content = html_template.render(Context(sample_data))

            # Render text
            text_content = ""
            if template_obj.text_template:
                text_template = Template(template_obj.text_template)
                text_content = text_template.render(Context(sample_data))

            return Response({
                'subject': subject,
                'html_content': html_content,
                'text_content': text_content
            })
        except Exception as e:
            return Response(
                {'error': f'Template rendering error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class EmailCampaignViewSet(viewsets.ModelViewSet):
    """
    Email campaign management
    """
    queryset = EmailCampaign.objects.select_related('template', 'created_by').all()
    serializer_class = EmailCampaignSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'campaign_type']
    search_fields = ['name', 'subject']
    ordering_fields = ['created_at', 'sent_at', 'scheduled_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send campaign immediately"""
        campaign = self.get_object()

        if campaign.status not in ['draft', 'scheduled']:
            return Response(
                {'error': 'Campaign cannot be sent in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update status
        campaign.status = 'sending'
        campaign.save()

        # Queue sending task (simplified - in production use Celery)
        # send_campaign_task.delay(campaign.id)

        return Response({
            'success': True,
            'message': 'Campaign queued for sending'
        })

    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """Schedule campaign for later"""
        campaign = self.get_object()
        scheduled_at = request.data.get('scheduled_at')

        if not scheduled_at:
            return Response(
                {'error': 'scheduled_at is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        campaign.scheduled_at = scheduled_at
        campaign.status = 'scheduled'
        campaign.save()

        return Response({
            'success': True,
            'scheduled_at': campaign.scheduled_at
        })

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause sending campaign"""
        campaign = self.get_object()

        if campaign.status != 'sending':
            return Response(
                {'error': 'Can only pause campaigns that are currently sending'},
                status=status.HTTP_400_BAD_REQUEST
            )

        campaign.status = 'paused'
        campaign.save()

        return Response({'success': True})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel campaign"""
        campaign = self.get_object()
        campaign.status = 'cancelled'
        campaign.save()

        return Response({'success': True})

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get detailed campaign statistics"""
        campaign = self.get_object()

        # Calculate additional stats
        recipients = campaign.recipients.all()

        status_breakdown = {}
        for status_choice in EmailRecipient.STATUS_CHOICES:
            status_key = status_choice[0]
            count = recipients.filter(status=status_key).count()
            status_breakdown[status_key] = count

        return Response({
            'campaign_id': str(campaign.id),
            'campaign_name': campaign.name,
            'status': campaign.status,
            'summary': {
                'total_recipients': campaign.total_recipients,
                'sent': campaign.sent_count,
                'delivered': campaign.delivered_count,
                'opened': campaign.opened_count,
                'clicked': campaign.clicked_count,
                'bounced': campaign.bounced_count,
                'unsubscribed': campaign.unsubscribed_count
            },
            'rates': {
                'open_rate': round(campaign.open_rate, 2),
                'click_rate': round(campaign.click_rate, 2),
                'click_to_open_rate': round(campaign.click_to_open_rate, 2),
                'bounce_rate': round((campaign.bounced_count / campaign.sent_count * 100) if campaign.sent_count > 0 else 0, 2)
            },
            'status_breakdown': status_breakdown,
            'sent_at': campaign.sent_at,
            'scheduled_at': campaign.scheduled_at
        })

    @action(detail=True, methods=['get'])
    def recipients(self, request, pk=None):
        """Get campaign recipients"""
        campaign = self.get_object()
        recipients = campaign.recipients.select_related('contact', 'lead').all()

        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            recipients = recipients.filter(status=status_filter)

        serializer = EmailRecipientSerializer(recipients, many=True)
        return Response(serializer.data)
