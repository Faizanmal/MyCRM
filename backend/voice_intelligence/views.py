"""
Voice Intelligence Views
DRF views for voice intelligence endpoints
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
import logging

from .models import (
    VoiceRecording, Transcription, ConversationSummary,
    ActionItem, SentimentAnalysis, KeyMoment, CallScore,
    VoiceNote, ConversationCategory, RecordingCategory,
    TranscriptionSettings
)
from .serializers import (
    VoiceRecordingListSerializer, VoiceRecordingDetailSerializer,
    VoiceRecordingCreateSerializer, TranscriptionSerializer,
    ConversationSummarySerializer, ActionItemSerializer,
    SentimentAnalysisSerializer, KeyMomentSerializer,
    CallScoreSerializer, VoiceNoteSerializer, VoiceNoteCreateSerializer,
    ConversationCategorySerializer, TranscriptionSettingsSerializer,
    TranscriptionEditSerializer, ProcessRecordingSerializer,
    BulkActionItemUpdateSerializer, SearchRecordingsSerializer,
    RecordingAnalyticsSerializer
)
from .services import (
    VoiceRecordingService, TranscriptionService,
    AnalysisService, VoiceNoteService, ProcessingOrchestrator
)

logger = logging.getLogger(__name__)


class VoiceRecordingViewSet(viewsets.ModelViewSet):
    """ViewSet for voice recordings"""
    
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        return VoiceRecording.objects.filter(
            owner=self.request.user
        ).select_related(
            'transcription', 'sentiment_analysis', 'call_score'
        ).prefetch_related(
            'summaries', 'action_items', 'key_moments', 'categories'
        )
    
    def get_serializer_class(self):
        if self.action == 'list':
            return VoiceRecordingListSerializer
        elif self.action == 'create':
            return VoiceRecordingCreateSerializer
        return VoiceRecordingDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Trigger full processing pipeline for a recording"""
        recording = self.get_object()
        
        serializer = ProcessRecordingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Queue processing task
        from .tasks import process_recording_task
        process_recording_task.delay(str(recording.id))
        
        return Response({
            'status': 'processing',
            'message': 'Recording processing started',
            'recording_id': str(recording.id)
        })
    
    @action(detail=True, methods=['post'])
    def transcribe(self, request, pk=None):
        """Transcribe a recording"""
        recording = self.get_object()
        
        if hasattr(recording, 'transcription'):
            return Response(
                {'error': 'Recording already has a transcription'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Queue transcription task
        from .tasks import transcribe_recording_task
        transcribe_recording_task.delay(str(recording.id))
        
        return Response({
            'status': 'transcribing',
            'message': 'Transcription started',
            'recording_id': str(recording.id)
        })
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """Run AI analysis on a recording"""
        recording = self.get_object()
        
        if not hasattr(recording, 'transcription'):
            return Response(
                {'error': 'Recording must be transcribed first'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Queue analysis task
        from .tasks import analyze_recording_task
        analyze_recording_task.delay(str(recording.id))
        
        return Response({
            'status': 'analyzing',
            'message': 'Analysis started',
            'recording_id': str(recording.id)
        })
    
    @action(detail=True, methods=['get'])
    def transcription(self, request, pk=None):
        """Get transcription for a recording"""
        recording = self.get_object()
        
        if not hasattr(recording, 'transcription'):
            return Response(
                {'error': 'No transcription available'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TranscriptionSerializer(recording.transcription)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def edit_transcription(self, request, pk=None):
        """Edit transcription text"""
        recording = self.get_object()
        
        if not hasattr(recording, 'transcription'):
            return Response(
                {'error': 'No transcription available'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TranscriptionEditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        transcription = recording.transcription
        transcription.full_text = serializer.validated_data['full_text']
        if 'segments' in serializer.validated_data:
            transcription.speaker_segments = serializer.validated_data['segments']
        transcription.was_edited = True
        transcription.edited_by = request.user
        transcription.edited_at = timezone.now()
        transcription.save()
        
        return Response(TranscriptionSerializer(transcription).data)
    
    @action(detail=True, methods=['get'])
    def summaries(self, request, pk=None):
        """Get all summaries for a recording"""
        recording = self.get_object()
        serializer = ConversationSummarySerializer(
            recording.summaries.all(), many=True
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def generate_summary(self, request, pk=None):
        """Generate a new summary"""
        recording = self.get_object()
        summary_type = request.data.get('summary_type', 'executive')
        
        if not hasattr(recording, 'transcription'):
            return Response(
                {'error': 'Recording must be transcribed first'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from .tasks import generate_summary_task
        generate_summary_task.delay(str(recording.id), summary_type)
        
        return Response({
            'status': 'generating',
            'message': f'{summary_type} summary generation started'
        })
    
    @action(detail=True, methods=['get'])
    def action_items(self, request, pk=None):
        """Get action items for a recording"""
        recording = self.get_object()
        serializer = ActionItemSerializer(
            recording.action_items.all(), many=True
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def key_moments(self, request, pk=None):
        """Get key moments for a recording"""
        recording = self.get_object()
        serializer = KeyMomentSerializer(
            recording.key_moments.all(), many=True
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_key_moment(self, request, pk=None):
        """Manually add a key moment"""
        recording = self.get_object()
        
        moment = KeyMoment.objects.create(
            recording=recording,
            moment_type=request.data.get('moment_type', 'highlight'),
            start_timestamp=request.data.get('start_timestamp', 0),
            end_timestamp=request.data.get('end_timestamp', 0),
            transcript_excerpt=request.data.get('transcript_excerpt', ''),
            speaker=request.data.get('speaker', ''),
            summary=request.data.get('summary', ''),
            notes=request.data.get('notes', ''),
            is_ai_detected=False,
            marked_by=request.user
        )
        
        return Response(
            KeyMomentSerializer(moment).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def call_score(self, request, pk=None):
        """Get call score for a recording"""
        recording = self.get_object()
        
        if not hasattr(recording, 'call_score'):
            return Response(
                {'error': 'No call score available'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = CallScoreSerializer(recording.call_score)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def categorize(self, request, pk=None):
        """Add categories to a recording"""
        recording = self.get_object()
        category_ids = request.data.get('category_ids', [])
        
        for cat_id in category_ids:
            try:
                category = ConversationCategory.objects.get(id=cat_id)
                RecordingCategory.objects.get_or_create(
                    recording=recording,
                    category=category,
                    defaults={'is_auto_classified': False}
                )
            except ConversationCategory.DoesNotExist:
                pass
        
        return Response({'status': 'success'})
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search recordings with filters"""
        serializer = SearchRecordingsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        queryset = self.get_queryset()
        
        # Apply filters
        if data.get('query'):
            queryset = queryset.filter(
                Q(title__icontains=data['query']) |
                Q(transcription__full_text__icontains=data['query'])
            )
        if data.get('source_type'):
            queryset = queryset.filter(source_type=data['source_type'])
        if data.get('status'):
            queryset = queryset.filter(status=data['status'])
        if data.get('date_from'):
            queryset = queryset.filter(recorded_at__gte=data['date_from'])
        if data.get('date_to'):
            queryset = queryset.filter(recorded_at__lte=data['date_to'])
        if data.get('contact_id'):
            queryset = queryset.filter(contact_id=data['contact_id'])
        if data.get('lead_id'):
            queryset = queryset.filter(lead_id=data['lead_id'])
        if data.get('opportunity_id'):
            queryset = queryset.filter(opportunity_id=data['opportunity_id'])
        if data.get('category_id'):
            queryset = queryset.filter(categories__category_id=data['category_id'])
        if data.get('has_action_items'):
            queryset = queryset.filter(action_items__isnull=False).distinct()
        if data.get('min_duration'):
            queryset = queryset.filter(duration_seconds__gte=data['min_duration'])
        if data.get('max_duration'):
            queryset = queryset.filter(duration_seconds__lte=data['max_duration'])
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = VoiceRecordingListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = VoiceRecordingListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get recording analytics"""
        queryset = self.get_queryset()
        
        # Date range filter
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(recorded_at__gte=start_date)
        
        # Aggregate stats
        total_recordings = queryset.count()
        total_duration = queryset.aggregate(
            total=Sum('duration_seconds')
        )['total'] or 0
        
        # Format duration
        hours = total_duration // 3600
        minutes = (total_duration % 3600) // 60
        duration_formatted = f"{hours}h {minutes}m"
        
        # By status
        by_status = dict(queryset.values_list('status').annotate(count=Count('id')))
        
        # By source
        by_source = dict(queryset.values_list('source_type').annotate(count=Count('id')))
        
        # By category
        by_category = list(
            RecordingCategory.objects.filter(
                recording__in=queryset
            ).values(
                'category__name', 'category__color'
            ).annotate(count=Count('id'))
        )
        
        # Average call score
        avg_score = CallScore.objects.filter(
            recording__in=queryset
        ).aggregate(avg=Avg('overall_score'))['avg'] or 0
        
        # Top coaching tips
        all_tips = []
        for score in CallScore.objects.filter(recording__in=queryset):
            all_tips.extend(score.coaching_tips)
        tip_counts = {}
        for tip in all_tips:
            tip_counts[tip] = tip_counts.get(tip, 0) + 1
        top_tips = sorted(tip_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Action items summary
        action_stats = ActionItem.objects.filter(
            recording__in=queryset
        ).aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            completed=Count('id', filter=Q(status='completed'))
        )
        
        # Sentiment distribution
        sentiment_dist = dict(
            SentimentAnalysis.objects.filter(
                recording__in=queryset
            ).values_list('overall_sentiment').annotate(count=Count('id'))
        )
        
        # Recent activity
        recent = queryset.order_by('-recorded_at')[:5]
        recent_data = VoiceRecordingListSerializer(recent, many=True).data
        
        return Response({
            'total_recordings': total_recordings,
            'total_duration_seconds': total_duration,
            'total_duration_formatted': duration_formatted,
            'recordings_by_status': by_status,
            'recordings_by_source': by_source,
            'recordings_by_category': by_category,
            'average_call_score': round(avg_score, 1),
            'top_coaching_tips': [{'tip': t[0], 'count': t[1]} for t in top_tips],
            'action_items_summary': action_stats,
            'sentiment_distribution': sentiment_dist,
            'recent_activity': recent_data
        })


class ActionItemViewSet(viewsets.ModelViewSet):
    """ViewSet for action items"""
    
    serializer_class = ActionItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ActionItem.objects.filter(
            recording__owner=self.request.user
        ).select_related('recording', 'assigned_to')
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update action items"""
        serializer = BulkActionItemUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        items = self.get_queryset().filter(
            id__in=data['action_item_ids']
        )
        
        update_fields = {}
        if 'status' in data:
            update_fields['status'] = data['status']
        if 'priority' in data:
            update_fields['priority'] = data['priority']
        if 'assigned_to' in data:
            update_fields['assigned_to_id'] = data['assigned_to']
        
        items.update(**update_fields)
        
        return Response({
            'status': 'success',
            'updated_count': items.count()
        })
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm an AI-extracted action item"""
        item = self.get_object()
        item.was_confirmed = True
        item.save()
        
        return Response(self.get_serializer(item).data)
    
    @action(detail=True, methods=['post'])
    def create_task(self, request, pk=None):
        """Create a task from an action item"""
        item = self.get_object()
        
        # Import Task model
        try:
            from task_management.models import Task
            
            task = Task.objects.create(
                title=item.title,
                description=item.description,
                assigned_to=item.assigned_to or request.user,
                due_date=item.due_date,
                priority=item.priority,
                created_by=request.user
            )
            
            item.linked_task = task
            item.save()
            
            return Response({
                'status': 'success',
                'task_id': str(task.id)
            })
            
        except ImportError:
            return Response(
                {'error': 'Task management module not available'},
                status=status.HTTP_400_BAD_REQUEST
            )


class VoiceNoteViewSet(viewsets.ModelViewSet):
    """ViewSet for voice notes"""
    
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        return VoiceNote.objects.filter(owner=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return VoiceNoteCreateSerializer
        return VoiceNoteSerializer
    
    @action(detail=False, methods=['get'])
    def for_contact(self, request):
        """Get voice notes for a contact"""
        contact_id = request.query_params.get('contact_id')
        if not contact_id:
            return Response(
                {'error': 'contact_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notes = self.get_queryset().filter(contact_id=contact_id)
        return Response(VoiceNoteSerializer(notes, many=True).data)
    
    @action(detail=False, methods=['get'])
    def for_lead(self, request):
        """Get voice notes for a lead"""
        lead_id = request.query_params.get('lead_id')
        if not lead_id:
            return Response(
                {'error': 'lead_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notes = self.get_queryset().filter(lead_id=lead_id)
        return Response(VoiceNoteSerializer(notes, many=True).data)
    
    @action(detail=False, methods=['get'])
    def for_opportunity(self, request):
        """Get voice notes for an opportunity"""
        opportunity_id = request.query_params.get('opportunity_id')
        if not opportunity_id:
            return Response(
                {'error': 'opportunity_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notes = self.get_queryset().filter(opportunity_id=opportunity_id)
        return Response(VoiceNoteSerializer(notes, many=True).data)


class ConversationCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for conversation categories"""
    
    serializer_class = ConversationCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ConversationCategory.objects.all()
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get categories as a tree structure"""
        root_categories = ConversationCategory.objects.filter(parent=None)
        serializer = ConversationCategorySerializer(root_categories, many=True)
        return Response(serializer.data)


class TranscriptionSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for user transcription settings"""
    
    serializer_class = TranscriptionSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return TranscriptionSettings.objects.filter(user=self.request.user)
    
    def get_object(self):
        obj, _ = TranscriptionSettings.objects.get_or_create(
            user=self.request.user
        )
        return obj
    
    def list(self, request, *args, **kwargs):
        # Return single settings object
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
