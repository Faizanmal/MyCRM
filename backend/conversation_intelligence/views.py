"""
Conversation Intelligence Views
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum, Avg, Q
from django.db import models
from datetime import timedelta

from .models import (
    CallRecording, TopicMention, CallCoaching, CallPlaylist, PlaylistClip,
    CallTracker, ConversationAnalytics
)
from .serializers import (
    CallRecordingListSerializer, CallRecordingDetailSerializer, CallRecordingCreateSerializer,
    CallTranscriptSerializer, CallAnalysisSerializer,
    TopicMentionSerializer, CallCoachingSerializer, CallPlaylistSerializer,
    PlaylistClipSerializer, CallTrackerSerializer, ConversationAnalyticsSerializer,
    AddCoachingSerializer, CreateClipSerializer
)
from .services import ConversationIntelligenceService


class CallRecordingViewSet(viewsets.ModelViewSet):
    """Manage call recordings"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CallRecordingCreateSerializer
        if self.action == 'retrieve':
            return CallRecordingDetailSerializer
        return CallRecordingListSerializer
    
    def get_queryset(self):
        qs = CallRecording.objects.filter(owner=self.request.user)
        
        # Include shared recordings
        qs = qs | CallRecording.objects.filter(shared_with=self.request.user)
        
        return qs.distinct().select_related('owner', 'opportunity', 'contact')
    
    def perform_create(self, serializer):
        recording = serializer.save(owner=self.request.user)
        
        # Trigger async processing
        service = ConversationIntelligenceService()
        service.process_recording_async(recording)
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """Reprocess a failed recording"""
        recording = self.get_object()
        
        if recording.status not in ['failed', 'ready']:
            return Response(
                {'error': 'Can only reprocess failed or completed recordings'},
                status=400
            )
        
        service = ConversationIntelligenceService()
        service.process_recording_async(recording)
        
        return Response({'status': 'processing started'})
    
    @action(detail=True, methods=['get'])
    def transcript(self, request, pk=None):
        """Get full transcript"""
        recording = self.get_object()
        
        if not hasattr(recording, 'transcript'):
            return Response({'error': 'Transcript not available'}, status=404)
        
        serializer = CallTranscriptSerializer(recording.transcript)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def analysis(self, request, pk=None):
        """Get call analysis"""
        recording = self.get_object()
        
        if not hasattr(recording, 'analysis'):
            return Response({'error': 'Analysis not available'}, status=404)
        
        serializer = CallAnalysisSerializer(recording.analysis)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def topics(self, request, pk=None):
        """Get topic mentions"""
        recording = self.get_object()
        topics = recording.topic_mentions.all()
        serializer = TopicMentionSerializer(topics, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_coaching(self, request, pk=None):
        """Add coaching feedback"""
        recording = self.get_object()
        serializer = AddCoachingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        coaching = CallCoaching.objects.create(
            recording=recording,
            coach=request.user,
            **serializer.validated_data
        )
        
        return Response(CallCoachingSerializer(coaching).data, status=201)
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share recording with team members"""
        recording = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        users = User.objects.filter(id__in=user_ids)
        recording.shared_with.add(*users)
        recording.is_shared = True
        recording.save()
        
        return Response({'shared_with': [u.email for u in users]})
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent recordings"""
        recent = self.get_queryset().filter(status='ready')[:10]
        serializer = CallRecordingListSerializer(recent, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def high_scoring(self, request):
        """Get high-scoring calls for learning"""
        high_scoring = self.get_queryset().filter(
            status='ready',
            analysis__call_score__gte=80
        ).order_by('-analysis__call_score')[:10]
        
        serializer = CallRecordingListSerializer(high_scoring, many=True)
        return Response(serializer.data)


class CallPlaylistViewSet(viewsets.ModelViewSet):
    """Manage call playlists"""
    serializer_class = CallPlaylistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CallPlaylist.objects.filter(
            models.Q(creator=self.request.user) | models.Q(is_public=True)
        ).prefetch_related('clips')
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_clip(self, request, pk=None):
        """Add clip to playlist"""
        playlist = self.get_object()
        serializer = CreateClipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        recording = CallRecording.objects.get(id=serializer.validated_data['recording_id'])
        
        clip = PlaylistClip.objects.create(
            playlist=playlist,
            recording=recording,
            title=serializer.validated_data['title'],
            description=serializer.validated_data.get('description', ''),
            start_time=serializer.validated_data['start_time'],
            end_time=serializer.validated_data['end_time'],
            order=playlist.clips.count()
        )
        
        return Response(PlaylistClipSerializer(clip).data, status=201)
    
    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        """Reorder clips"""
        playlist = self.get_object()
        clip_order = request.data.get('clip_order', [])  # List of clip IDs in order
        
        for i, clip_id in enumerate(clip_order):
            PlaylistClip.objects.filter(
                id=clip_id, playlist=playlist
            ).update(order=i)
        
        return Response({'status': 'reordered'})


class CallTrackerViewSet(viewsets.ModelViewSet):
    """Manage keyword trackers"""
    serializer_class = CallTrackerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CallTracker.objects.filter(
            Q(created_by=self.request.user) | Q(is_shared=True)
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def mentions(self, request, pk=None):
        """Get all mentions of tracker keywords"""
        tracker = self.get_object()
        
        mentions = TopicMention.objects.filter(
            topic_name__in=tracker.keywords
        ).select_related('recording')[:100]
        
        serializer = TopicMentionSerializer(mentions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def trends(self, request, pk=None):
        """Get mention trends over time"""
        tracker = self.get_object()
        days = int(request.query_params.get('days', 30))
        
        service = ConversationIntelligenceService()
        trends = service.get_tracker_trends(tracker, days)
        
        return Response(trends)


class ConversationAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """View conversation analytics"""
    serializer_class = ConversationAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ConversationAnalytics.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get analytics dashboard"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        analytics = self.get_queryset().filter(date__gte=start_date)
        
        totals = analytics.aggregate(
            total_calls=Sum('calls_recorded'),
            total_minutes=Sum('total_duration_minutes'),
            avg_talk_ratio=Avg('avg_talk_ratio'),
            avg_call_score=Avg('avg_call_score'),
            avg_engagement=Avg('avg_engagement_score'),
        )
        
        # Daily breakdown
        daily = list(analytics.values('date').annotate(
            calls=Sum('calls_recorded'),
            avg_score=Avg('avg_call_score'),
            minutes=Sum('total_duration_minutes'),
        ).order_by('date'))
        
        return Response({
            'summary': totals,
            'daily': daily,
            'period_days': days,
        })
    
    @action(detail=False, methods=['get'])
    def team_comparison(self, request):
        """Compare performance across team"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        comparison = ConversationAnalytics.objects.filter(
            date__gte=start_date
        ).values('user__email', 'user__first_name', 'user__last_name').annotate(
            total_calls=Sum('calls_recorded'),
            avg_score=Avg('avg_call_score'),
            avg_talk_ratio=Avg('avg_talk_ratio'),
        ).order_by('-avg_score')
        
        return Response(list(comparison))
