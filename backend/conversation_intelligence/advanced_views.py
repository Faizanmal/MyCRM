"""
Voice & Conversation Intelligence - Advanced Views
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Avg

from .models import CallRecording
from .advanced_models import (
    RealTimeCoachingSession, RealTimeCoachingSuggestion,
    SentimentTimeline, SentimentDashboard, MeetingSummary,
    MeetingActionItem, CallCoachingMetrics, KeyMoment
)
from .advanced_serializers import (
    RealTimeCoachingSessionSerializer, RealTimeCoachingSuggestionSerializer,
    SentimentTimelineSerializer, SentimentDashboardSerializer,
    MeetingSummarySerializer, MeetingActionItemSerializer,
    CallCoachingMetricsSerializer, KeyMomentSerializer,
    StartCoachingSessionSerializer, GenerateSummarySerializer,
    SendSummaryEmailSerializer, SentimentDashboardRequestSerializer
)
from .advanced_services import (
    RealTimeCoachingEngine, SentimentAnalyzer,
    MeetingSummarizer, KeyMomentDetector
)


class RealTimeCoachingViewSet(viewsets.ModelViewSet):
    """Manage real-time coaching sessions"""
    
    serializer_class = RealTimeCoachingSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RealTimeCoachingSession.objects.filter(
            recording__owner=self.request.user
        )
    
    @action(detail=False, methods=['post'])
    def start(self, request):
        """Start a new coaching session"""
        serializer = StartCoachingSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            recording = CallRecording.objects.get(
                id=serializer.validated_data['recording_id'],
                owner=request.user
            )
        except CallRecording.DoesNotExist:
            return Response(
                {'error': 'Recording not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        engine = RealTimeCoachingEngine()
        result = engine.start_coaching_session(recording)
        
        session = RealTimeCoachingSession.objects.get(id=result['session_id'])
        return Response(RealTimeCoachingSessionSerializer(session).data)
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End a coaching session"""
        session = self.get_object()
        
        engine = RealTimeCoachingEngine()
        summary = engine.end_coaching_session(session)
        
        return Response({
            'status': 'ended',
            'summary': summary,
        })
    
    @action(detail=True, methods=['post'])
    def process_segment(self, request, pk=None):
        """Process a transcript segment for real-time coaching"""
        session = self.get_object()
        
        segment = request.data.get('segment', {})
        
        engine = RealTimeCoachingEngine()
        suggestions = engine.process_transcript_segment(session, segment)
        engine.update_metrics(session, segment)
        
        # Save suggestions
        saved_suggestions = []
        for suggestion_data in suggestions:
            suggestion = RealTimeCoachingSuggestion.objects.create(
                session=session,
                suggestion_type=suggestion_data['type'],
                priority=suggestion_data.get('priority', 'medium'),
                title=suggestion_data['title'],
                content=suggestion_data['content'],
                timestamp_seconds=suggestion_data.get('timestamp', 0),
            )
            saved_suggestions.append(suggestion)
        
        return Response({
            'suggestions': RealTimeCoachingSuggestionSerializer(
                saved_suggestions, many=True
            ).data,
            'metrics': {
                'talk_ratio': float(session.current_talk_ratio),
                'question_count': session.question_count,
                'sentiment': session.current_sentiment,
            },
        })
    
    @action(detail=True, methods=['get'])
    def suggestions(self, request, pk=None):
        """Get all suggestions for a session"""
        session = self.get_object()
        suggestions = session.suggestions.all()
        return Response(
            RealTimeCoachingSuggestionSerializer(suggestions, many=True).data
        )


class CoachingSuggestionViewSet(viewsets.ModelViewSet):
    """Manage coaching suggestions"""
    
    serializer_class = RealTimeCoachingSuggestionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RealTimeCoachingSuggestion.objects.filter(
            session__recording__owner=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """Mark suggestion as viewed"""
        suggestion = self.get_object()
        suggestion.was_viewed = True
        suggestion.save()
        return Response({'status': 'viewed'})
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Mark suggestion as applied"""
        suggestion = self.get_object()
        suggestion.was_applied = True
        suggestion.save()
        return Response({'status': 'applied'})
    
    @action(detail=True, methods=['post'])
    def feedback(self, request, pk=None):
        """Provide feedback on suggestion"""
        suggestion = self.get_object()
        was_helpful = request.data.get('was_helpful')
        
        if was_helpful is not None:
            suggestion.was_helpful = was_helpful
            suggestion.save()
        
        return Response({'status': 'feedback recorded'})


class SentimentAnalysisViewSet(viewsets.ViewSet):
    """Sentiment analysis endpoints"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def analyze_recording(self, request):
        """Analyze sentiment for a recording"""
        recording_id = request.data.get('recording_id')
        
        try:
            recording = CallRecording.objects.get(
                id=recording_id,
                owner=request.user
            )
        except CallRecording.DoesNotExist:
            return Response(
                {'error': 'Recording not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_recording(recording)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def timeline(self, request):
        """Get sentiment timeline for a recording"""
        recording_id = request.query_params.get('recording_id')
        
        if not recording_id:
            return Response(
                {'error': 'recording_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        timeline = SentimentTimeline.objects.filter(
            recording_id=recording_id,
            recording__owner=request.user
        ).order_by('timestamp_seconds')
        
        return Response(
            SentimentTimelineSerializer(timeline, many=True).data
        )
    
    @action(detail=False, methods=['get', 'post'])
    def dashboard(self, request):
        """Get sentiment dashboard"""
        if request.method == 'POST':
            serializer = SentimentDashboardRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            period = serializer.validated_data['period']
        else:
            period = request.query_params.get('period', 'weekly')
        
        analyzer = SentimentAnalyzer()
        result = analyzer.generate_dashboard(request.user, period)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get sentiment trends over time"""
        dashboards = SentimentDashboard.objects.filter(
            user=request.user
        ).order_by('-start_date')[:12]
        
        return Response(
            SentimentDashboardSerializer(dashboards, many=True).data
        )


class MeetingSummaryViewSet(viewsets.ModelViewSet):
    """Manage meeting summaries"""
    
    serializer_class = MeetingSummarySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MeetingSummary.objects.filter(
            recording__owner=self.request.user
        )
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a meeting summary"""
        serializer = GenerateSummarySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            recording = CallRecording.objects.get(
                id=serializer.validated_data['recording_id'],
                owner=request.user
            )
        except CallRecording.DoesNotExist:
            return Response(
                {'error': 'Recording not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        summarizer = MeetingSummarizer()
        result = summarizer.generate_summary(recording)
        
        if 'error' in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the full summary object
        summary = MeetingSummary.objects.get(id=result['summary_id'])
        
        return Response(MeetingSummarySerializer(summary).data)
    
    @action(detail=True, methods=['post'])
    def send_email(self, request, pk=None):
        """Send summary via email"""
        summary = self.get_object()
        
        serializer = SendSummaryEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        summarizer = MeetingSummarizer()
        success = summarizer.send_summary_email(
            summary,
            serializer.validated_data['recipients']
        )
        
        if success:
            return Response({'status': 'email sent'})
        else:
            return Response(
                {'error': 'Failed to send email'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share summary with team members"""
        summary = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        users = User.objects.filter(id__in=user_ids)
        summary.shared_with.add(*users)
        summary.is_shared = True
        summary.save()
        
        return Response({'status': 'shared', 'shared_with': user_ids})


class MeetingActionItemViewSet(viewsets.ModelViewSet):
    """Manage meeting action items"""
    
    serializer_class = MeetingActionItemSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'priority', 'assigned_to']
    ordering_fields = ['due_date', 'priority', 'created_at']
    
    def get_queryset(self):
        return MeetingActionItem.objects.filter(
            summary__recording__owner=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark action item as completed"""
        item = self.get_object()
        item.status = 'completed'
        item.completed_at = timezone.now()
        item.save()
        return Response({'status': 'completed'})
    
    @action(detail=True, methods=['post'])
    def create_task(self, request, pk=None):
        """Create a task from action item"""
        item = self.get_object()
        
        from task_management.models import Task
        
        task = Task.objects.create(
            title=item.title,
            description=item.description,
            assigned_to=item.assigned_to or request.user,
            due_date=item.due_date,
            priority=item.priority,
            created_by=request.user,
        )
        
        item.linked_task = task
        item.save()
        
        return Response({
            'status': 'task created',
            'task_id': task.id,
        })
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending action items"""
        items = self.get_queryset().filter(status='pending')
        return Response(
            MeetingActionItemSerializer(items, many=True).data
        )


class KeyMomentViewSet(viewsets.ModelViewSet):
    """Manage key moments"""
    
    serializer_class = KeyMomentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['moment_type', 'importance', 'is_bookmarked']
    ordering_fields = ['timestamp_seconds', 'importance']
    
    def get_queryset(self):
        return KeyMoment.objects.filter(
            recording__owner=self.request.user
        )
    
    @action(detail=False, methods=['post'])
    def detect(self, request):
        """Detect key moments in a recording"""
        recording_id = request.data.get('recording_id')
        
        try:
            recording = CallRecording.objects.get(
                id=recording_id,
                owner=request.user
            )
        except CallRecording.DoesNotExist:
            return Response(
                {'error': 'Recording not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        detector = KeyMomentDetector()
        moments = detector.detect_moments(recording)
        
        return Response({
            'detected': len(moments),
            'moments': moments,
        })
    
    @action(detail=True, methods=['post'])
    def bookmark(self, request, pk=None):
        """Toggle bookmark on a moment"""
        moment = self.get_object()
        moment.is_bookmarked = not moment.is_bookmarked
        moment.save()
        return Response({'is_bookmarked': moment.is_bookmarked})
    
    @action(detail=False, methods=['get'])
    def bookmarked(self, request):
        """Get bookmarked moments"""
        moments = self.get_queryset().filter(is_bookmarked=True)
        return Response(
            KeyMomentSerializer(moments, many=True).data
        )
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get moments grouped by type"""
        moment_type = request.query_params.get('type')
        
        if moment_type:
            moments = self.get_queryset().filter(moment_type=moment_type)
        else:
            moments = self.get_queryset()
        
        # Group by type
        from django.db.models import Count
        grouped = moments.values('moment_type').annotate(
            count=Count('id')
        )
        
        return Response({
            'grouped': list(grouped),
            'moments': KeyMomentSerializer(moments, many=True).data,
        })


class CallCoachingMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """View coaching metrics"""
    
    serializer_class = CallCoachingMetricsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CallCoachingMetrics.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get', 'post'])
    def generate(self, request):
        """Generate coaching metrics"""
        period = request.data.get('period', 'weekly') if request.method == 'POST' \
            else request.query_params.get('period', 'weekly')
        
        from datetime import timedelta
        from .models import CallRecording, CallAnalysis
        
        today = timezone.now().date()
        
        if period == 'weekly':
            start_date = today - timedelta(days=7)
        else:
            start_date = today - timedelta(days=30)
        
        recordings = CallRecording.objects.filter(
            owner=request.user,
            recorded_at__date__gte=start_date,
            status='ready'
        )
        
        if not recordings.exists():
            return Response({
                'period': period,
                'message': 'No calls in this period',
            })
        
        # Calculate metrics
        total_calls = recordings.count()
        total_duration = sum(r.duration_seconds for r in recordings) // 60
        
        # Get analysis data
        analyses = []
        for recording in recordings:
            if hasattr(recording, 'analysis'):
                analyses.append(recording.analysis)
        
        if analyses:
            avg_talk_ratio = sum(float(a.rep_talk_ratio) for a in analyses) / len(analyses)
            avg_questions = sum(a.question_count for a in analyses) / len(analyses)
            avg_score = sum(float(a.call_score) for a in analyses) / len(analyses)
        else:
            avg_talk_ratio = 50
            avg_questions = 0
            avg_score = 0
        
        # Create/update metrics
        metrics, _ = CallCoachingMetrics.objects.update_or_create(
            user=request.user,
            period=period,
            start_date=start_date,
            end_date=today,
            defaults={
                'total_calls': total_calls,
                'total_duration_minutes': total_duration,
                'avg_talk_ratio': avg_talk_ratio,
                'avg_questions_per_call': avg_questions,
                'avg_call_score': avg_score,
                'improvement_areas': [],
                'strengths': [],
                'recommendations': [],
            }
        )
        
        return Response(CallCoachingMetricsSerializer(metrics).data)


class ConversationIntelligenceDashboardView(APIView):
    """Dashboard for conversation intelligence"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get comprehensive dashboard data"""
        
        user = request.user
        
        # Recent recordings
        recent_recordings = CallRecording.objects.filter(
            owner=user
        ).order_by('-recorded_at')[:5]
        
        # Coaching sessions
        active_sessions = RealTimeCoachingSession.objects.filter(
            recording__owner=user,
            status='active'
        ).count()
        
        # Sentiment summary
        analyzer = SentimentAnalyzer()
        sentiment_summary = analyzer.generate_dashboard(user, 'weekly')
        
        # Recent summaries
        recent_summaries = MeetingSummary.objects.filter(
            recording__owner=user
        ).order_by('-created_at')[:5]
        
        # Pending action items
        pending_actions = MeetingActionItem.objects.filter(
            summary__recording__owner=user,
            status='pending'
        ).count()
        
        # Key moments stats
        from django.db.models import Count
        moment_stats = KeyMoment.objects.filter(
            recording__owner=user
        ).values('moment_type').annotate(count=Count('id'))
        
        return Response({
            'overview': {
                'total_recordings': CallRecording.objects.filter(owner=user).count(),
                'active_coaching_sessions': active_sessions,
                'pending_action_items': pending_actions,
            },
            'sentiment': sentiment_summary,
            'recent_recordings': [{
                'id': r.id,
                'title': r.title,
                'call_type': r.call_type,
                'duration': r.duration_formatted,
                'status': r.status,
                'recorded_at': r.recorded_at,
            } for r in recent_recordings],
            'recent_summaries': MeetingSummarySerializer(
                recent_summaries, many=True
            ).data,
            'moment_stats': list(moment_stats),
        })
