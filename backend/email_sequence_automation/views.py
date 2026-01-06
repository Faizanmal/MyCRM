from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .ai_content_generator import AIEmailContentGenerator
from .models import (
    ABTest,
    AutomatedTrigger,
    EmailPersonalizationToken,
    EmailSequence,
    SequenceActivity,
    SequenceAnalytics,
    SequenceEmail,
    SequenceEnrollment,
    SequenceStep,
)
from .serializers import (
    ABTestSerializer,
    AnalyzeEmailQualitySerializer,
    AutomatedTriggerSerializer,
    EmailPersonalizationTokenSerializer,
    EmailSequenceCreateSerializer,
    EmailSequenceSerializer,
    EnrollContactSerializer,
    GenerateEmailContentSerializer,
    GenerateSubjectVariantsSerializer,
    OptimizeSendTimeSerializer,
    SequenceActivitySerializer,
    SequenceAnalyticsSerializer,
    SequenceEmailSerializer,
    SequenceEnrollmentSerializer,
    SequenceStepCreateSerializer,
    SequenceStepSerializer,
)
from .services import (
    ABTestingService,
    AnalyticsService,
    SequenceExecutionService,
    TriggerEvaluationService,
)


class EmailSequenceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing email sequences"""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return EmailSequence.objects.filter(
            Q(owner=user) | Q(shared_with_team=True)
        ).prefetch_related('steps', 'steps__emails')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EmailSequenceCreateSerializer
        return EmailSequenceSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def activate(self, request, _pk=None):
        """Activate a sequence"""
        sequence = self.get_object()

        if sequence.status == 'active':
            return Response({'detail': 'Sequence already active'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate sequence has at least one step
        if not sequence.steps.filter(is_active=True).exists():
            return Response(
                {'detail': 'Sequence must have at least one active step'},
                status=status.HTTP_400_BAD_REQUEST
            )

        sequence.status = 'active'
        sequence.activated_at = timezone.now()
        sequence.save(update_fields=['status', 'activated_at'])

        return Response({'status': 'activated'})

    @action(detail=True, methods=['post'])
    def pause(self, request, _pk=None):
        """Pause a sequence"""
        sequence = self.get_object()
        sequence.status = 'paused'
        sequence.save(update_fields=['status'])
        return Response({'status': 'paused'})

    @action(detail=True, methods=['post'])
    def archive(self, request, _pk=None):
        """Archive a sequence"""
        sequence = self.get_object()
        sequence.status = 'archived'
        sequence.save(update_fields=['status'])
        return Response({'status': 'archived'})

    @action(detail=True, methods=['post'])
    def duplicate(self, request, _pk=None):
        """Duplicate a sequence"""
        sequence = self.get_object()

        # Clone sequence
        new_sequence = EmailSequence.objects.create(
            name=f"{sequence.name} (Copy)",
            description=sequence.description,
            owner=request.user,
            trigger_type=sequence.trigger_type,
            trigger_config=sequence.trigger_config,
            settings=sequence.settings,
            exit_conditions=sequence.exit_conditions,
            personalization_enabled=sequence.personalization_enabled,
            ai_optimization_enabled=sequence.ai_optimization_enabled,
            status='draft'
        )

        # Clone steps and emails
        for step in sequence.steps.all():
            new_step = SequenceStep.objects.create(
                sequence=new_sequence,
                step_type=step.step_type,
                step_number=step.step_number,
                name=step.name,
                wait_days=step.wait_days,
                wait_hours=step.wait_hours,
                wait_minutes=step.wait_minutes,
                condition_type=step.condition_type,
                condition_config=step.condition_config,
                config=step.config,
                ab_test_enabled=step.ab_test_enabled,
                is_active=step.is_active
            )

            for email in step.emails.all():
                SequenceEmail.objects.create(
                    step=new_step,
                    subject=email.subject,
                    preview_text=email.preview_text,
                    body_html=email.body_html,
                    body_text=email.body_text,
                    variant_name=email.variant_name,
                    variant_weight=email.variant_weight,
                    personalization_tokens=email.personalization_tokens
                )

        serializer = EmailSequenceSerializer(new_sequence)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def enroll_contact(self, request, _pk=None):
        """Enroll a contact in this sequence"""
        sequence = self.get_object()
        serializer = EnrollContactSerializer(data={
            'sequence_id': pk,
            **request.data
        })
        serializer.is_valid(raise_exception=True)

        service = SequenceExecutionService()
        enrollment, created = service.enroll_contact(
            sequence_id=str(sequence.id),
            contact_id=serializer.validated_data['contact_id'],
            enrolled_by_id=request.user.id,
            trigger='manual',
            lead_id=serializer.validated_data.get('lead_id'),
            personalization_data=serializer.validated_data.get('personalization_data')
        )

        if not created:
            return Response(
                {'detail': 'Contact already enrolled in this sequence'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            SequenceEnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'])
    def analytics(self, request, _pk=None):
        """Get sequence analytics"""
        sequence = self.get_object()
        service = AnalyticsService()
        stats = service.get_sequence_stats(str(sequence.id))
        return Response(stats)

    @action(detail=True, methods=['get'])
    def enrollments(self, request, _pk=None):
        """Get enrollments for this sequence"""
        sequence = self.get_object()
        enrollments = SequenceEnrollment.objects.filter(
            sequence=sequence
        ).select_related('contact', 'current_step')

        status_filter = request.query_params.get('status')
        if status_filter:
            enrollments = enrollments.filter(status=status_filter)

        serializer = SequenceEnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)


class SequenceStepViewSet(viewsets.ModelViewSet):
    """ViewSet for managing sequence steps"""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SequenceStep.objects.filter(
            sequence__owner=self.request.user
        ).prefetch_related('emails')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SequenceStepCreateSerializer
        return SequenceStepSerializer

    @action(detail=True, methods=['post'])
    def reorder(self, request, _pk=None):
        """Reorder step in sequence"""
        step = self.get_object()
        new_position = request.data.get('position')

        if new_position is None:
            return Response(
                {'detail': 'Position required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update other steps
        if new_position < step.step_number:
            SequenceStep.objects.filter(
                sequence=step.sequence,
                step_number__gte=new_position,
                step_number__lt=step.step_number
            ).update(step_number=models.F('step_number') + 1)
        else:
            SequenceStep.objects.filter(
                sequence=step.sequence,
                step_number__gt=step.step_number,
                step_number__lte=new_position
            ).update(step_number=models.F('step_number') - 1)

        step.step_number = new_position
        step.save(update_fields=['step_number'])

        return Response({'status': 'reordered'})


class SequenceEmailViewSet(viewsets.ModelViewSet):
    """ViewSet for managing sequence emails"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SequenceEmailSerializer

    def get_queryset(self):
        return SequenceEmail.objects.filter(
            step__sequence__owner=self.request.user
        )

    @action(detail=False, methods=['post'])
    def generate_content(self, request):
        """Generate AI email content"""
        serializer = GenerateEmailContentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        generator = AIEmailContentGenerator()
        content = generator.generate_email(
            template_type=serializer.validated_data['template_type'],
            template_subtype=serializer.validated_data['template_subtype'],
            context=serializer.validated_data['context'],
            tone=serializer.validated_data['tone'],
            length=serializer.validated_data['length'],
            personalization_data=serializer.validated_data.get('personalization_data')
        )

        return Response(content)

    @action(detail=False, methods=['post'])
    def generate_subject_variants(self, request):
        """Generate A/B test subject line variants"""
        serializer = GenerateSubjectVariantsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        generator = AIEmailContentGenerator()
        variants = generator.generate_subject_variants(
            base_context=serializer.validated_data['context'],
            num_variants=serializer.validated_data['num_variants']
        )

        return Response(variants)

    @action(detail=False, methods=['post'])
    def analyze_quality(self, request):
        """Analyze email content quality"""
        serializer = AnalyzeEmailQualitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        generator = AIEmailContentGenerator()
        analysis = generator.analyze_email_quality(
            subject=serializer.validated_data['subject'],
            body=serializer.validated_data['body']
        )

        return Response(analysis)

    @action(detail=False, methods=['post'])
    def optimize_send_time(self, request):
        """Get optimal send time for a contact"""
        serializer = OptimizeSendTimeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from contact_management.models import Contact
        contact = Contact.objects.get(id=serializer.validated_data['contact_id'])

        generator = AIEmailContentGenerator()
        optimal_time = generator.optimize_send_time(
            contact_id=contact.id,
            contact_data={
                'timezone': contact.custom_fields.get('timezone', 'UTC'),
                'timezone_offset': contact.custom_fields.get('timezone_offset', 0)
            }
        )

        return Response(optimal_time)


class SequenceEnrollmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing sequence enrollments"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SequenceEnrollmentSerializer
    http_method_names = ['get', 'delete', 'patch']

    def get_queryset(self):
        return SequenceEnrollment.objects.filter(
            sequence__owner=self.request.user
        ).select_related('contact', 'sequence', 'current_step')

    @action(detail=True, methods=['post'])
    def pause(self, request, _pk=None):
        """Pause enrollment"""
        enrollment = self.get_object()
        enrollment.status = 'paused'
        enrollment.save(update_fields=['status'])

        SequenceActivity.objects.create(
            enrollment=enrollment,
            activity_type='paused',
            description='Enrollment paused manually'
        )

        return Response({'status': 'paused'})

    @action(detail=True, methods=['post'])
    def resume(self, request, _pk=None):
        """Resume paused enrollment"""
        enrollment = self.get_object()

        if enrollment.status != 'paused':
            return Response(
                {'detail': 'Enrollment is not paused'},
                status=status.HTTP_400_BAD_REQUEST
            )

        enrollment.status = 'active'
        enrollment.save(update_fields=['status'])

        SequenceActivity.objects.create(
            enrollment=enrollment,
            activity_type='resumed',
            description='Enrollment resumed manually'
        )

        return Response({'status': 'resumed'})

    @action(detail=True, methods=['post'])
    def skip_step(self, request, _pk=None):
        """Skip current step and advance"""
        enrollment = self.get_object()

        service = SequenceExecutionService()
        service._advance_to_next_step(enrollment)

        return Response(SequenceEnrollmentSerializer(enrollment).data)

    @action(detail=True, methods=['get'])
    def activities(self, request, _pk=None):
        """Get enrollment activities"""
        enrollment = self.get_object()
        activities = SequenceActivity.objects.filter(
            enrollment=enrollment
        ).select_related('step')

        serializer = SequenceActivitySerializer(activities, many=True)
        return Response(serializer.data)


class ABTestViewSet(viewsets.ModelViewSet):
    """ViewSet for managing A/B tests"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ABTestSerializer

    def get_queryset(self):
        return ABTest.objects.filter(
            step__sequence__owner=self.request.user
        )

    @action(detail=True, methods=['post'])
    def start(self, request, _pk=None):
        """Start A/B test"""
        test = self.get_object()
        test.status = 'running'
        test.started_at = timezone.now()
        test.save(update_fields=['status', 'started_at'])
        return Response({'status': 'started'})

    @action(detail=True, methods=['get'])
    def evaluate(self, request, _pk=None):
        """Evaluate A/B test results"""
        test = self.get_object()
        service = ABTestingService()
        results = service.evaluate_test(test)
        return Response(results)

    @action(detail=True, methods=['post'])
    def select_winner(self, request, _pk=None):
        """Manually select winner"""
        test = self.get_object()
        email_id = request.data.get('email_id')

        if not email_id:
            return Response(
                {'detail': 'email_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = ABTestingService()
        email = SequenceEmail.objects.get(id=email_id)

        service._select_winner(test, {
            'email_id': str(email.id),
            'variant': email.variant_name,
            'metric_value': 0
        })

        return Response({'status': 'winner_selected'})


class AutomatedTriggerViewSet(viewsets.ModelViewSet):
    """ViewSet for managing automated triggers"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AutomatedTriggerSerializer

    def get_queryset(self):
        return AutomatedTrigger.objects.filter(
            sequence__owner=self.request.user
        )

    @action(detail=True, methods=['post'])
    def toggle(self, request, _pk=None):
        """Toggle trigger active status"""
        trigger = self.get_object()
        trigger.is_active = not trigger.is_active
        trigger.save(update_fields=['is_active'])
        return Response({'is_active': trigger.is_active})

    @action(detail=True, methods=['post'])
    def test(self, request, _pk=None):
        """Test trigger with sample data"""
        trigger = self.get_object()
        test_data = request.data.get('test_data', {})

        service = TriggerEvaluationService()
        matches = service._matches_trigger(trigger, test_data)

        return Response({
            'would_trigger': matches,
            'test_data': test_data
        })


class EmailPersonalizationTokenViewSet(viewsets.ModelViewSet):
    """ViewSet for managing personalization tokens"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmailPersonalizationTokenSerializer

    def get_queryset(self):
        return EmailPersonalizationToken.objects.filter(
            Q(owner=self.request.user) | Q(is_system=True)
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def system_tokens(self, request):
        """Get all system tokens"""
        tokens = EmailPersonalizationToken.objects.filter(is_system=True)
        serializer = self.get_serializer(tokens, many=True)
        return Response(serializer.data)


class SequenceAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing sequence analytics"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SequenceAnalyticsSerializer

    def get_queryset(self):
        return SequenceAnalytics.objects.filter(
            sequence__owner=self.request.user
        )

    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Get analytics overview across all sequences"""
        from django.db.models import Avg, Sum

        sequences = EmailSequence.objects.filter(owner=request.user, status='active')

        totals = sequences.aggregate(
            total_enrolled=Sum('total_enrolled'),
            total_completed=Sum('total_completed'),
            total_converted=Sum('total_converted'),
            avg_open_rate=Avg('avg_open_rate'),
            avg_click_rate=Avg('avg_click_rate'),
            avg_reply_rate=Avg('avg_reply_rate')
        )

        return Response({
            'active_sequences': sequences.count(),
            'total_active_enrollments': SequenceEnrollment.objects.filter(
                sequence__owner=request.user,
                status='active'
            ).count(),
            **totals
        })
