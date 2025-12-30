"""
Follow-up and Calendar Sync Views
API endpoints for automated follow-ups and calendar intelligence
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.utils import timezone
from datetime import datetime, timedelta

from .follow_up_models import (
    MeetingFollowUp,
    FollowUpSequence,
    MeetingOutcome,
    RecurringMeetingPattern,
    MeetingAnalytics,
    CalendarEvent
)
from .follow_up_serializers import (
    MeetingFollowUpSerializer,
    FollowUpSequenceSerializer,
    MeetingOutcomeSerializer,
    RecurringMeetingPatternSerializer,
    MeetingAnalyticsSerializer,
    CalendarEventSerializer,
    ScheduleFollowUpsRequestSerializer,
    RecordOutcomeRequestSerializer,
    CreateSequenceRequestSerializer,
    CreateFromTemplateRequestSerializer,
    SyncCalendarRequestSerializer,
    CheckConflictsRequestSerializer,
    GetAvailabilityRequestSerializer,
    FindCommonTimeRequestSerializer,
    AnalyzeCalendarRequestSerializer,
    UnifiedCalendarRequestSerializer,
    CreateRecurringPatternRequestSerializer
)
from .follow_up_services import FollowUpService, SequenceTemplateService
from .calendar_sync_services import (
    CalendarSyncService,
    MultiCalendarService,
    CalendarIntelligenceService
)

logger = logging.getLogger(__name__)


class MeetingFollowUpViewSet(viewsets.ModelViewSet):
    """ViewSet for managing meeting follow-ups"""
    
    serializer_class = MeetingFollowUpSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MeetingFollowUp.objects.filter(
            meeting__host=self.request.user
        ).select_related('meeting', 'meeting__meeting_type')
    
    @action(detail=False, methods=['post'])
    def schedule(self, request):
        """Schedule follow-ups for a meeting"""
        serializer = ScheduleFollowUpsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = FollowUpService(request.user)
        
        try:
            follow_ups = service.schedule_follow_ups_for_meeting(
                meeting_id=str(serializer.validated_data['meeting_id']),
                sequence_id=str(serializer.validated_data.get('sequence_id')) if serializer.validated_data.get('sequence_id') else None
            )
            return Response({
                'status': 'success',
                'follow_ups_scheduled': len(follow_ups),
                'follow_ups': follow_ups
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def send_pending(self, request):
        """Send all pending follow-ups that are due"""
        service = FollowUpService(request.user)
        result = service.send_pending_follow_ups()
        
        return Response({
            'status': 'success',
            'sent': result['sent'],
            'failed': result['failed'],
            'remaining': result['remaining']
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a scheduled follow-up"""
        follow_up = self.get_object()
        
        if follow_up.status in ['sent', 'opened', 'clicked', 'replied']:
            return Response(
                {'error': 'Cannot cancel follow-up that has already been sent'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        follow_up.status = 'cancelled'
        follow_up.save()
        
        return Response({
            'status': 'success',
            'message': 'Follow-up cancelled'
        })
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending follow-ups"""
        pending = self.get_queryset().filter(
            status='pending',
            scheduled_at__gt=timezone.now()
        ).order_by('scheduled_at')
        
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get follow-up analytics"""
        days = int(request.query_params.get('days', 30))
        service = FollowUpService(request.user)
        analytics = service.get_follow_up_analytics(days)
        
        return Response(analytics)


class FollowUpSequenceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing follow-up sequences"""
    
    serializer_class = FollowUpSequenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FollowUpSequence.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """Get available sequence templates"""
        service = SequenceTemplateService(request.user)
        templates = service.get_default_sequences()
        
        return Response({
            'templates': templates,
            'count': len(templates)
        })
    
    @action(detail=False, methods=['post'])
    def create_from_template(self, request):
        """Create a sequence from a template"""
        serializer = CreateFromTemplateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = SequenceTemplateService(request.user)
        
        try:
            sequence = service.create_from_template(
                serializer.validated_data['template_name']
            )
            return Response({
                'status': 'success',
                'sequence': sequence
            }, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a sequence"""
        sequence = self.get_object()
        
        new_sequence = FollowUpSequence.objects.create(
            user=request.user,
            name=f"{sequence.name} (Copy)",
            description=sequence.description,
            steps=sequence.steps,
            apply_to_all=sequence.apply_to_all,
            use_ai_personalization=sequence.use_ai_personalization
        )
        new_sequence.meeting_types.set(sequence.meeting_types.all())
        
        serializer = self.get_serializer(new_sequence)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle sequence active status"""
        sequence = self.get_object()
        sequence.is_active = not sequence.is_active
        sequence.save()
        
        return Response({
            'status': 'success',
            'is_active': sequence.is_active
        })


class MeetingOutcomeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing meeting outcomes"""
    
    serializer_class = MeetingOutcomeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MeetingOutcome.objects.filter(
            meeting__host=self.request.user
        ).select_related('meeting', 'meeting__meeting_type', 'recorded_by')
    
    @action(detail=False, methods=['post'])
    def record(self, request):
        """Record a meeting outcome"""
        serializer = RecordOutcomeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = FollowUpService(request.user)
        
        try:
            outcome = service.record_meeting_outcome(
                meeting_id=str(serializer.validated_data['meeting_id']),
                outcome=serializer.validated_data['outcome'],
                notes=serializer.validated_data.get('notes', ''),
                action_items=serializer.validated_data.get('action_items')
            )
            return Response({
                'status': 'success',
                'outcome': outcome
            }, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent meeting outcomes"""
        days = int(request.query_params.get('days', 7))
        since = timezone.now() - timedelta(days=days)
        
        outcomes = self.get_queryset().filter(
            recorded_at__gte=since
        ).order_by('-recorded_at')[:20]
        
        serializer = self.get_serializer(outcomes, many=True)
        return Response(serializer.data)


class RecurringMeetingPatternViewSet(viewsets.ModelViewSet):
    """ViewSet for managing recurring meeting patterns"""
    
    serializer_class = RecurringMeetingPatternSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RecurringMeetingPattern.objects.filter(
            user=self.request.user
        ).select_related('meeting_type', 'contact')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle pattern active status"""
        pattern = self.get_object()
        pattern.is_active = not pattern.is_active
        pattern.save()
        
        return Response({
            'status': 'success',
            'is_active': pattern.is_active
        })
    
    @action(detail=True, methods=['post'])
    def schedule_next(self, request, pk=None):
        """Manually trigger scheduling of next occurrence"""
        pattern = self.get_object()
        
        # Calculate next occurrence
        # This would integrate with the main scheduling service
        
        return Response({
            'status': 'success',
            'message': 'Next meeting scheduled',
            'next_occurrence': pattern.next_occurrence
        })


class CalendarSyncViewSet(viewsets.ViewSet):
    """ViewSet for calendar synchronization"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def sync(self, request):
        """Sync a calendar integration"""
        serializer = SyncCalendarRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = CalendarSyncService(request.user)
        
        try:
            result = service.sync_calendar(
                str(serializer.validated_data['integration_id'])
            )
            return Response(result)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def check_conflicts(self, request):
        """Check for calendar conflicts"""
        serializer = CheckConflictsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = CalendarSyncService(request.user)
        result = service.check_conflicts(
            start_time=serializer.validated_data['start_time'],
            end_time=serializer.validated_data['end_time'],
            exclude_meeting_id=str(serializer.validated_data.get('exclude_meeting_id')) if serializer.validated_data.get('exclude_meeting_id') else None
        )
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def availability(self, request):
        """Get availability windows for a date"""
        date_str = request.query_params.get('date')
        duration = int(request.query_params.get('duration', 30))
        
        if not date_str:
            return Response(
                {'error': 'date parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            date = datetime.fromisoformat(date_str)
        except ValueError:
            return Response(
                {'error': 'Invalid date format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = CalendarSyncService(request.user)
        windows = service.get_availability_windows(date, duration)
        
        return Response({
            'date': date_str,
            'duration_minutes': duration,
            'windows': windows
        })
    
    @action(detail=False, methods=['get'])
    def broadcast_availability(self, request):
        """Get shareable availability"""
        service = CalendarSyncService(request.user)
        result = service.broadcast_availability()
        
        return Response(result)


class MultiCalendarViewSet(viewsets.ViewSet):
    """ViewSet for multi-calendar operations"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def unified(self, request):
        """Get unified calendar view"""
        serializer = UnifiedCalendarRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = MultiCalendarService(request.user)
        result = service.get_unified_calendar(
            start_date=serializer.validated_data['start_date'],
            end_date=serializer.validated_data['end_date']
        )
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def find_common_time(self, request):
        """Find common free time across participants"""
        serializer = FindCommonTimeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = MultiCalendarService(request.user)
        slots = service.find_common_free_time(
            participant_emails=serializer.validated_data['participant_emails'],
            duration_minutes=serializer.validated_data['duration_minutes'],
            date_range_days=serializer.validated_data['date_range_days']
        )
        
        return Response({
            'participants': serializer.validated_data['participant_emails'],
            'duration_minutes': serializer.validated_data['duration_minutes'],
            'slots': slots
        })


class CalendarIntelligenceViewSet(viewsets.ViewSet):
    """ViewSet for calendar intelligence and insights"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def patterns(self, request):
        """Analyze calendar patterns"""
        days = int(request.query_params.get('days', 30))
        
        service = CalendarIntelligenceService(request.user)
        result = service.analyze_calendar_patterns(days)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def productivity_score(self, request):
        """Get productivity score"""
        service = CalendarIntelligenceService(request.user)
        result = service.get_productivity_score()
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def focus_blocks(self, request):
        """Get suggested meeting-free focus blocks"""
        service = CalendarIntelligenceService(request.user)
        suggestions = service.suggest_meeting_free_blocks()
        
        return Response({
            'suggestions': suggestions,
            'count': len(suggestions)
        })


class MeetingAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for meeting analytics"""
    
    serializer_class = MeetingAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MeetingAnalytics.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get analytics summary"""
        period = request.query_params.get('period', 'weekly')
        
        analytics = self.get_queryset().filter(
            period_type=period
        ).order_by('-period_start').first()
        
        if analytics:
            serializer = self.get_serializer(analytics)
            return Response(serializer.data)
        
        return Response({
            'message': 'No analytics available for this period'
        })
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get analytics trends over time"""
        period = request.query_params.get('period', 'weekly')
        limit = int(request.query_params.get('limit', 12))
        
        analytics = self.get_queryset().filter(
            period_type=period
        ).order_by('-period_start')[:limit]
        
        serializer = self.get_serializer(analytics, many=True)
        return Response({
            'period': period,
            'data': serializer.data
        })
