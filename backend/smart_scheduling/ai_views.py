"""
Smart Scheduling AI Views
API endpoints for AI-enhanced scheduling features
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from .ai_models import (
    AISchedulingPreference,
    AITimeSuggestion,
    NoShowPrediction,
    MeetingPrepAI,
    SmartReschedule,
    SmartReminder,
    ScheduleOptimization,
    AttendeeIntelligence
)
from .ai_serializers import (
    AISchedulingPreferenceSerializer,
    AITimeSuggestionSerializer,
    NoShowPredictionSerializer,
    MeetingPrepAISerializer,
    SmartRescheduleSerializer,
    SmartReminderSerializer,
    ScheduleOptimizationSerializer,
    AttendeeIntelligenceSerializer,
    FindOptimalTimesRequestSerializer,
    PredictNoShowRequestSerializer,
    GenerateMeetingPrepRequestSerializer,
    SetupSmartRemindersRequestSerializer,
    SuggestRescheduleRequestSerializer,
    OptimizeScheduleRequestSerializer,
    MeetingPrepFeedbackSerializer
)
from .ai_services import AISchedulingService, AttendeeIntelligenceService

logger = logging.getLogger(__name__)


class AISchedulingPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for AI scheduling preferences"""
    
    serializer_class = AISchedulingPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AISchedulingPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_preferences(self, request):
        """Get current user's AI scheduling preferences"""
        try:
            prefs = AISchedulingPreference.objects.get(user=request.user)
            serializer = self.get_serializer(prefs)
            return Response(serializer.data)
        except AISchedulingPreference.DoesNotExist:
            return Response(
                {'message': 'No preferences set yet. Use learn-preferences to auto-generate.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def learn_preferences(self, request):
        """Learn preferences from historical data"""
        service = AISchedulingService(request.user)
        result = service.learn_preferences()
        return Response(result)


class AITimeSuggestionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AI time suggestions"""
    
    serializer_class = AITimeSuggestionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AITimeSuggestion.objects.filter(
            user=self.request.user,
            expires_at__gt=timezone.now()
        ).order_by('-overall_score')
    
    @action(detail=False, methods=['post'])
    def find_optimal(self, request):
        """Find optimal meeting times using AI"""
        serializer = FindOptimalTimesRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = AISchedulingService(request.user)
        
        try:
            suggestions = service.find_optimal_times(
                meeting_type_id=str(serializer.validated_data['meeting_type_id']),
                duration_minutes=serializer.validated_data['duration_minutes'],
                date_range_days=serializer.validated_data.get('date_range_days', 14),
                participant_email=serializer.validated_data.get('participant_email'),
                num_suggestions=serializer.validated_data.get('num_suggestions', 5)
            )
            return Response(suggestions)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Mark a suggestion as accepted"""
        suggestion = self.get_object()
        suggestion.was_accepted = True
        suggestion.save()
        return Response({'message': 'Suggestion accepted'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Mark a suggestion as rejected with optional feedback"""
        suggestion = self.get_object()
        suggestion.was_accepted = False
        suggestion.feedback = request.data.get('feedback', '')
        suggestion.save()
        return Response({'message': 'Feedback recorded'})


class NoShowPredictionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for no-show predictions"""
    
    serializer_class = NoShowPredictionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return NoShowPrediction.objects.filter(
            meeting__host=self.request.user
        ).order_by('-risk_score')
    
    @action(detail=False, methods=['post'])
    def predict(self, request):
        """Predict no-show probability for a meeting"""
        serializer = PredictNoShowRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = AISchedulingService(request.user)
        
        try:
            prediction = service.predict_no_show(
                meeting_id=str(serializer.validated_data['meeting_id'])
            )
            return Response(prediction)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def high_risk(self, request):
        """Get high-risk meetings (no-show score > 50)"""
        predictions = self.get_queryset().filter(risk_score__gt=50)
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def record_outcome(self, request, pk=None):
        """Record actual meeting outcome for prediction accuracy"""
        prediction = self.get_object()
        outcome = request.data.get('outcome')
        
        if outcome not in ['completed', 'no_show', 'cancelled', 'rescheduled']:
            return Response(
                {'error': 'Invalid outcome. Must be: completed, no_show, cancelled, or rescheduled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        prediction.actual_outcome = outcome
        prediction.prediction_was_correct = (
            (outcome == 'no_show' and prediction.no_show_probability > 0.5) or
            (outcome != 'no_show' and prediction.no_show_probability <= 0.5)
        )
        prediction.save()
        
        # Update attendee intelligence
        AttendeeIntelligenceService.update_attendee_intelligence(
            email=prediction.meeting.guest_email,
            meeting_outcome=outcome
        )
        
        return Response({'message': 'Outcome recorded', 'prediction_correct': prediction.prediction_was_correct})


class MeetingPrepAIViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AI meeting prep materials"""
    
    serializer_class = MeetingPrepAISerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MeetingPrepAI.objects.filter(
            meeting__host=self.request.user
        ).order_by('-prep_generated_at')
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate AI meeting prep materials"""
        serializer = GenerateMeetingPrepRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = AISchedulingService(request.user)
        
        try:
            prep = service.generate_meeting_prep(
                meeting_id=str(serializer.validated_data['meeting_id'])
            )
            return Response(prep)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get prep materials for upcoming meetings"""
        # Get meetings in the next 7 days
        upcoming_cutoff = timezone.now() + timedelta(days=7)
        preps = self.get_queryset().filter(
            meeting__start_time__gt=timezone.now(),
            meeting__start_time__lte=upcoming_cutoff
        )
        serializer = self.get_serializer(preps, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def feedback(self, request, pk=None):
        """Submit feedback on prep materials"""
        prep = self.get_object()
        
        feedback_serializer = MeetingPrepFeedbackSerializer(data={
            'meeting_prep_id': pk,
            'was_helpful': request.data.get('was_helpful'),
            'feedback': request.data.get('feedback', '')
        })
        feedback_serializer.is_valid(raise_exception=True)
        
        prep.was_helpful = feedback_serializer.validated_data['was_helpful']
        prep.feedback = feedback_serializer.validated_data.get('feedback', '')
        prep.save()
        
        return Response({'message': 'Feedback recorded'})


class SmartRescheduleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for smart reschedule suggestions"""
    
    serializer_class = SmartRescheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SmartReschedule.objects.filter(
            meeting__host=self.request.user
        ).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def suggest(self, request):
        """Generate reschedule suggestions for a meeting"""
        serializer = SuggestRescheduleRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = AISchedulingService(request.user)
        
        try:
            suggestion = service.suggest_reschedule(
                meeting_id=str(serializer.validated_data['meeting_id']),
                trigger_type=serializer.validated_data.get('trigger_type', 'optimization'),
                trigger_reason=serializer.validated_data.get('trigger_reason', '')
            )
            return Response(suggestion)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a reschedule suggestion"""
        reschedule = self.get_object()
        
        # Get selected alternative or use best suggestion
        selected = request.data.get('selected_alternative')
        
        reschedule.status = 'accepted'
        reschedule.response_by = 'host'
        reschedule.selected_alternative = selected or {
            'start': reschedule.suggested_start.isoformat() if reschedule.suggested_start else None,
            'end': reschedule.suggested_end.isoformat() if reschedule.suggested_end else None
        }
        reschedule.response_at = timezone.now()
        reschedule.save()
        
        return Response({'message': 'Reschedule accepted', 'selected': reschedule.selected_alternative})
    
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        """Decline a reschedule suggestion"""
        reschedule = self.get_object()
        
        reschedule.status = 'declined'
        reschedule.response_by = 'host'
        reschedule.response_at = timezone.now()
        reschedule.save()
        
        return Response({'message': 'Reschedule declined'})


class SmartReminderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for smart reminders"""
    
    serializer_class = SmartReminderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SmartReminder.objects.filter(
            meeting__host=self.request.user
        ).order_by('scheduled_at')
    
    @action(detail=False, methods=['post'])
    def setup(self, request):
        """Setup smart reminders for a meeting"""
        serializer = SetupSmartRemindersRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = AISchedulingService(request.user)
        
        try:
            reminders = service.setup_smart_reminders(
                meeting_id=str(serializer.validated_data['meeting_id'])
            )
            return Response(reminders)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending (not yet sent) reminders"""
        reminders = self.get_queryset().filter(
            sent=False,
            scheduled_at__gt=timezone.now()
        )
        serializer = self.get_serializer(reminders, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_opened(self, request, pk=None):
        """Mark a reminder as opened (for tracking)"""
        reminder = self.get_object()
        reminder.opened = True
        reminder.opened_at = timezone.now()
        reminder.save()
        return Response({'message': 'Marked as opened'})


class ScheduleOptimizationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for schedule optimizations"""
    
    serializer_class = ScheduleOptimizationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ScheduleOptimization.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def optimize(self, request):
        """Generate schedule optimization suggestions"""
        serializer = OptimizeScheduleRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = AISchedulingService(request.user)
        
        try:
            optimization = service.optimize_schedule(
                start_date=serializer.validated_data['start_date'],
                end_date=serializer.validated_data['end_date'],
                optimization_type=serializer.validated_data.get('optimization_type', 'create_focus_time')
            )
            return Response(optimization)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Apply an optimization (mark as applied)"""
        optimization = self.get_object()
        optimization.applied = True
        optimization.applied_at = timezone.now()
        optimization.status = 'applied'
        optimization.save()
        return Response({'message': 'Optimization marked as applied'})
    
    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """Get pending optimization suggestions"""
        optimizations = self.get_queryset().filter(
            applied=False,
            status='pending'
        )
        serializer = self.get_serializer(optimizations, many=True)
        return Response(serializer.data)


class AttendeeIntelligenceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for attendee intelligence"""
    
    serializer_class = AttendeeIntelligenceSerializer
    permission_classes = [IsAuthenticated]
    queryset = AttendeeIntelligence.objects.all()
    
    @action(detail=False, methods=['get'])
    def lookup(self, request):
        """Look up intelligence for a specific email"""
        email = request.query_params.get('email')
        
        if not email:
            return Response(
                {'error': 'Email parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        insights = AttendeeIntelligenceService.get_attendee_insights(email)
        
        if insights:
            return Response(insights)
        else:
            return Response(
                {'message': 'No intelligence data for this attendee'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def high_risk(self, request):
        """Get attendees with high no-show risk"""
        high_risk = self.queryset.filter(
            reliability_score__lt=0.6,
            total_meetings_scheduled__gte=3
        ).order_by('reliability_score')
        serializer = self.get_serializer(high_risk, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def top_attendees(self, request):
        """Get most reliable attendees"""
        top = self.queryset.filter(
            reliability_score__gte=0.9,
            total_meetings_scheduled__gte=3
        ).order_by('-reliability_score', '-total_meetings_scheduled')[:20]
        serializer = self.get_serializer(top, many=True)
        return Response(serializer.data)
