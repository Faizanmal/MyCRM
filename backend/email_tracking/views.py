"""
Email Tracking Views
Full email tracking with pixel tracking and link wrapping
"""

import base64
from datetime import timedelta

from django.db.models import Avg, Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    EmailEvent,
    EmailSequence,
    EmailTemplate,
    SequenceEnrollment,
    SequenceStep,
    TrackedEmail,
)
from .serializers import (
    EmailEventSerializer,
    EmailSequenceListSerializer,
    EmailSequenceSerializer,
    EmailTemplateSerializer,
    EnrollContactSerializer,
    SendEmailSerializer,
    SequenceEnrollmentSerializer,
    SequenceStepSerializer,
    TrackedEmailListSerializer,
    TrackedEmailSerializer,
)
from .services import EmailTrackingService


class TrackedEmailViewSet(viewsets.ModelViewSet):
    """Manage tracked emails"""
    serializer_class = TrackedEmailSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'contact', 'opportunity']
    search_fields = ['subject', 'to_email', 'to_name']
    ordering_fields = ['-sent_at', '-created_at', '-open_count']

    def get_queryset(self):
        return TrackedEmail.objects.filter(sender=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return TrackedEmailListSerializer
        return TrackedEmailSerializer

    @action(detail=False, methods=['post'])
    def send(self, request):
        """Send a tracked email"""
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = EmailTrackingService()
        email = service.send_email(
            sender=request.user,
            **serializer.validated_data
        )

        return Response(TrackedEmailSerializer(email).data, status=201)

    @action(detail=True, methods=['get'])
    def events(self, request, _pk=None):
        """Get all events for an email"""
        email = self.get_object()
        events = email.events.all()
        serializer = EmailEventSerializer(events, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def timeline(self, request, _pk=None):
        """Get email timeline with all events"""
        email = self.get_object()

        timeline = []

        timeline.append({
            'event': 'created',
            'timestamp': email.created_at,
            'description': 'Email created'
        })

        if email.sent_at:
            timeline.append({
                'event': 'sent',
                'timestamp': email.sent_at,
                'description': 'Email sent'
            })

        for event in email.events.all():
            timeline.append({
                'event': event.event_type,
                'timestamp': event.timestamp,
                'description': event.get_event_type_display(),
                'metadata': {
                    'device': event.device_type,
                    'location': f"{event.city}, {event.country}" if event.city else None,
                    'url': event.clicked_url if event.event_type == 'click' else None
                }
            })

        timeline.sort(key=lambda x: x['timestamp'])

        return Response(timeline)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get email statistics"""
        emails = self.get_queryset()

        # Time period
        days = int(request.query_params.get('days', 30))
        since = timezone.now() - timedelta(days=days)
        recent = emails.filter(sent_at__gte=since)

        sent_count = recent.filter(status__in=['sent', 'delivered', 'opened', 'clicked', 'replied']).count()

        return Response({
            'period_days': days,
            'total_sent': sent_count,
            'total_opened': recent.filter(open_count__gt=0).count(),
            'total_clicked': recent.filter(click_count__gt=0).count(),
            'total_replied': recent.filter(status='replied').count(),
            'open_rate': round(recent.filter(open_count__gt=0).count() / sent_count * 100, 1) if sent_count > 0 else 0,
            'click_rate': round(recent.filter(click_count__gt=0).count() / sent_count * 100, 1) if sent_count > 0 else 0,
            'reply_rate': round(recent.filter(status='replied').count() / sent_count * 100, 1) if sent_count > 0 else 0,
            'avg_engagement_score': recent.aggregate(avg=Avg('open_count'))['avg'] or 0,
        })


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """Manage email templates"""
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category', 'is_shared', 'is_active']
    search_fields = ['name', 'subject', 'description']
    ordering_fields = ['-times_used', 'name', '-avg_open_rate']

    def get_queryset(self):
        # Show own templates and shared templates
        return EmailTemplate.objects.filter(
            Q(owner=self.request.user) | Q(is_shared=True)
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, _pk=None):
        """Duplicate a template"""
        template = self.get_object()

        new_template = EmailTemplate.objects.create(
            name=f"{template.name} (Copy)",
            description=template.description,
            category=template.category,
            subject=template.subject,
            body_text=template.body_text,
            body_html=template.body_html,
            variables=template.variables,
            owner=request.user,
            is_shared=False,
        )

        serializer = self.get_serializer(new_template)
        return Response(serializer.data, status=201)

    @action(detail=False, methods=['get'])
    def top_performing(self, request):
        """Get top performing templates"""
        templates = self.get_queryset().filter(
            times_used__gt=0
        ).order_by('-avg_reply_rate', '-avg_open_rate')[:10]

        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)


class EmailSequenceViewSet(viewsets.ModelViewSet):
    """Manage email sequences"""
    serializer_class = EmailSequenceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status']
    search_fields = ['name', 'description']
    ordering_fields = ['-created_at', '-total_enrolled', 'name']

    def get_queryset(self):
        return EmailSequence.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return EmailSequenceListSerializer
        return EmailSequenceSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def activate(self, request, _pk=None):
        """Activate a sequence"""
        sequence = self.get_object()

        if not sequence.steps.exists():
            return Response(
                {'error': 'Sequence must have at least one step'},
                status=400
            )

        sequence.status = 'active'
        sequence.save()

        return Response({'status': 'activated'})

    @action(detail=True, methods=['post'])
    def pause(self, request, _pk=None):
        """Pause a sequence"""
        sequence = self.get_object()
        sequence.status = 'paused'
        sequence.save()

        return Response({'status': 'paused'})

    @action(detail=True, methods=['post'])
    def enroll(self, request, _pk=None):
        """Enroll contacts in sequence"""
        sequence = self.get_object()

        if sequence.status != 'active':
            return Response(
                {'error': 'Sequence must be active to enroll contacts'},
                status=400
            )

        serializer = EnrollContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from contact_management.models import Contact

        enrolled = []
        already_enrolled = []

        for contact_id in serializer.validated_data['contact_ids']:
            try:
                contact = Contact.objects.get(id=contact_id)

                # Check if already enrolled
                if SequenceEnrollment.objects.filter(
                    sequence=sequence,
                    contact=contact,
                    status='active'
                ).exists():
                    already_enrolled.append(contact_id)
                    continue

                # Calculate first action time
                first_step = sequence.steps.order_by('order').first()
                next_action = timezone.now()

                if first_step.step_type == 'wait':
                    next_action += timedelta(
                        days=first_step.delay_days,
                        hours=first_step.delay_hours
                    )

                SequenceEnrollment.objects.create(
                    sequence=sequence,
                    contact=contact,
                    enrolled_by=request.user,
                    next_action_at=next_action
                )

                enrolled.append(contact_id)
                sequence.total_enrolled += 1

            except Contact.DoesNotExist:
                continue

        sequence.save()

        return Response({
            'enrolled': enrolled,
            'already_enrolled': already_enrolled,
            'total_enrolled': len(enrolled)
        })

    @action(detail=True, methods=['get'])
    def enrollments(self, request, _pk=None):
        """Get all enrollments for a sequence"""
        sequence = self.get_object()
        enrollments = sequence.enrollments.all()

        status_filter = request.query_params.get('status')
        if status_filter:
            enrollments = enrollments.filter(status=status_filter)

        serializer = SequenceEnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def performance(self, request, _pk=None):
        """Get sequence performance metrics"""
        sequence = self.get_object()

        steps_data = []
        for step in sequence.steps.all():
            steps_data.append({
                'order': step.order,
                'type': step.step_type,
                'sent': step.sent_count,
                'opened': step.open_count,
                'clicked': step.click_count,
                'replied': step.reply_count,
                'open_rate': step.open_rate,
                'reply_rate': step.reply_rate,
            })

        return Response({
            'total_enrolled': sequence.total_enrolled,
            'total_completed': sequence.total_completed,
            'total_replied': sequence.total_replied,
            'reply_rate': sequence.reply_rate,
            'active_enrollments': sequence.enrollments.filter(status='active').count(),
            'steps': steps_data
        })


class SequenceStepViewSet(viewsets.ModelViewSet):
    """Manage sequence steps"""
    serializer_class = SequenceStepSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SequenceStep.objects.filter(
            sequence__owner=self.request.user
        )


class TrackingPixelView(APIView):
    """
    Handle email open tracking via 1x1 pixel
    This is the magic that enables open tracking!
    """
    permission_classes = [AllowAny]

    def get(self, request, tracking_id):
        """Return 1x1 transparent pixel and record open"""
        try:
            email = TrackedEmail.objects.get(tracking_id=tracking_id)

            # Record open event
            EmailEvent.objects.create(
                email=email,
                event_type='open',
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                device_type=self._detect_device(request),
                email_client=self._detect_email_client(request),
            )

            # Update email stats
            email.open_count += 1
            if not email.first_opened_at:
                email.first_opened_at = timezone.now()
                email.status = 'opened'
            email.last_opened_at = timezone.now()
            email.save()

        except TrackedEmail.DoesNotExist:
            pass

        # Return 1x1 transparent GIF
        pixel = base64.b64decode(
            'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
        )

        return HttpResponse(pixel, content_type='image/gif')

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def _detect_device(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if 'mobile' in user_agent or 'android' in user_agent:
            return 'mobile'
        elif 'tablet' in user_agent or 'ipad' in user_agent:
            return 'tablet'
        return 'desktop'

    def _detect_email_client(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if 'outlook' in user_agent:
            return 'Outlook'
        elif 'gmail' in user_agent or 'googleimageproxy' in user_agent:
            return 'Gmail'
        elif 'yahoo' in user_agent:
            return 'Yahoo Mail'
        elif 'apple' in user_agent:
            return 'Apple Mail'
        return 'Unknown'


class TrackingLinkView(APIView):
    """
    Handle link click tracking
    All links in emails are wrapped to go through this endpoint
    """
    permission_classes = [AllowAny]

    def get(self, request, tracking_id):
        """Record click and redirect to actual URL"""
        url = request.query_params.get('url', '')

        if not url:
            return HttpResponse('Invalid link', status=400)

        try:
            email = TrackedEmail.objects.get(tracking_id=tracking_id)

            # Record click event
            EmailEvent.objects.create(
                email=email,
                event_type='click',
                clicked_url=url,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                device_type=self._detect_device(request),
            )

            # Update email stats
            email.click_count += 1
            if not email.first_clicked_at:
                email.first_clicked_at = timezone.now()
                email.status = 'clicked'
            email.save()

        except TrackedEmail.DoesNotExist:
            pass

        return redirect(url)

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def _detect_device(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if 'mobile' in user_agent or 'android' in user_agent:
            return 'mobile'
        elif 'tablet' in user_agent or 'ipad' in user_agent:
            return 'tablet'
        return 'desktop'


class EmailAnalyticsDashboardView(APIView):
    """Email analytics dashboard"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get comprehensive email analytics"""
        user = request.user
        days = int(request.query_params.get('days', 30))
        since = timezone.now() - timedelta(days=days)

        emails = TrackedEmail.objects.filter(
            sender=user,
            sent_at__gte=since
        )

        sent_count = emails.count()
        opened_count = emails.filter(open_count__gt=0).count()
        clicked_count = emails.filter(click_count__gt=0).count()
        replied_count = emails.filter(status='replied').count()

        # Daily breakdown
        daily_stats = []
        for i in range(days):
            date = (timezone.now() - timedelta(days=i)).date()
            day_emails = emails.filter(sent_at__date=date)
            daily_stats.append({
                'date': date.isoformat(),
                'sent': day_emails.count(),
                'opened': day_emails.filter(open_count__gt=0).count(),
                'clicked': day_emails.filter(click_count__gt=0).count(),
            })

        # Best performing subjects
        top_subjects = emails.filter(
            open_count__gt=0
        ).order_by('-open_count')[:5].values('subject', 'open_count', 'click_count')

        # Best send times
        events = EmailEvent.objects.filter(
            email__sender=user,
            event_type='open',
            timestamp__gte=since
        )

        hour_performance = {}
        for event in events:
            hour = event.timestamp.hour
            hour_performance[hour] = hour_performance.get(hour, 0) + 1

        best_hour = max(hour_performance.items(), key=lambda x: x[1])[0] if hour_performance else 10

        return Response({
            'period_days': days,
            'summary': {
                'total_sent': sent_count,
                'total_opened': opened_count,
                'total_clicked': clicked_count,
                'total_replied': replied_count,
                'open_rate': round(opened_count / sent_count * 100, 1) if sent_count > 0 else 0,
                'click_rate': round(clicked_count / sent_count * 100, 1) if sent_count > 0 else 0,
                'reply_rate': round(replied_count / sent_count * 100, 1) if sent_count > 0 else 0,
            },
            'daily_stats': daily_stats,
            'top_subjects': list(top_subjects),
            'best_send_time': f"{best_hour:02d}:00",
            'device_breakdown': self._get_device_breakdown(user, since),
        })

    def _get_device_breakdown(self, user, since):
        events = EmailEvent.objects.filter(
            email__sender=user,
            event_type='open',
            timestamp__gte=since
        )

        breakdown = {
            'desktop': events.filter(device_type='desktop').count(),
            'mobile': events.filter(device_type='mobile').count(),
            'tablet': events.filter(device_type='tablet').count(),
        }

        total = sum(breakdown.values())
        if total > 0:
            return {k: round(v / total * 100, 1) for k, v in breakdown.items()}
        return breakdown
