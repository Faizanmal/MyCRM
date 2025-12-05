"""
Voice Intelligence Services
High-level service layer for voice processing workflows
"""

from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from typing import Dict, Any, Optional, List
import logging
import os
import tempfile
import uuid

from .models import (
    VoiceRecording, Transcription, ConversationSummary,
    ActionItem, SentimentAnalysis, KeyMoment, CallScore,
    VoiceNote, RecordingCategory, ConversationCategory,
    TranscriptionSettings
)
from .transcription_engine import (
    TranscriptionEngine, SpeakerDiarization, AudioPreprocessor
)
from .ai_summarizer import (
    ConversationSummarizer, ActionItemExtractor, SentimentAnalyzer,
    KeyMomentDetector, CallScorer, TopicExtractor, VoiceNoteProcessor
)

logger = logging.getLogger(__name__)
User = get_user_model()


class VoiceRecordingService:
    """Service for managing voice recordings"""
    
    def __init__(self):
        self.transcription_engine = TranscriptionEngine()
        self.diarization = SpeakerDiarization()
        self.audio_processor = AudioPreprocessor()
    
    def create_recording(
        self,
        user: User,
        audio_file,
        source_type: str = 'upload',
        title: str = '',
        metadata: Optional[Dict] = None
    ) -> VoiceRecording:
        """Create a new voice recording"""
        
        # Generate file path
        file_name = f"{uuid.uuid4()}.{audio_file.name.split('.')[-1]}"
        file_path = f"voice_recordings/{user.id}/{file_name}"
        
        # Get audio info
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_name.split('.')[-1]}") as tmp:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
        
        try:
            audio_info = self.audio_processor.get_audio_info(tmp_path)
            
            recording = VoiceRecording.objects.create(
                owner=user,
                title=title or f"Recording {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                source_type=source_type,
                status='uploaded',
                file_path=file_path,
                file_size_bytes=audio_file.size,
                file_format=file_name.split('.')[-1],
                duration_seconds=int(audio_info.get('duration', 0)),
                sample_rate=audio_info.get('sample_rate'),
                channels=audio_info.get('channels', 1),
                bitrate=audio_info.get('bitrate'),
                participants=metadata.get('participants', []) if metadata else [],
                participant_count=metadata.get('participant_count', 2) if metadata else 2,
                contact_id=metadata.get('contact_id') if metadata else None,
                lead_id=metadata.get('lead_id') if metadata else None,
                opportunity_id=metadata.get('opportunity_id') if metadata else None,
                meeting_id=metadata.get('meeting_id') if metadata else None,
            )
            
            # TODO: Upload file to storage (S3, etc.)
            # For now, keep local path
            
            return recording
            
        finally:
            os.unlink(tmp_path)
    
    def get_user_recordings(
        self,
        user: User,
        filters: Optional[Dict] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get recordings for a user with filters"""
        queryset = VoiceRecording.objects.filter(owner=user)
        
        if filters:
            if filters.get('status'):
                queryset = queryset.filter(status=filters['status'])
            if filters.get('source_type'):
                queryset = queryset.filter(source_type=filters['source_type'])
            if filters.get('contact_id'):
                queryset = queryset.filter(contact_id=filters['contact_id'])
            if filters.get('lead_id'):
                queryset = queryset.filter(lead_id=filters['lead_id'])
            if filters.get('date_from'):
                queryset = queryset.filter(recorded_at__gte=filters['date_from'])
            if filters.get('date_to'):
                queryset = queryset.filter(recorded_at__lte=filters['date_to'])
            if filters.get('search'):
                queryset = queryset.filter(title__icontains=filters['search'])
        
        total = queryset.count()
        offset = (page - 1) * page_size
        recordings = queryset[offset:offset + page_size]
        
        return {
            'recordings': recordings,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }


class TranscriptionService:
    """Service for transcribing recordings"""
    
    def __init__(self):
        self.engine = TranscriptionEngine()
        self.diarization = SpeakerDiarization()
    
    @transaction.atomic
    def transcribe_recording(
        self,
        recording: VoiceRecording,
        settings: Optional[TranscriptionSettings] = None
    ) -> Transcription:
        """Transcribe a recording"""
        
        recording.status = 'transcribing'
        recording.processing_started_at = timezone.now()
        recording.save()
        
        try:
            # Get user settings if not provided
            if not settings:
                settings, _ = TranscriptionSettings.objects.get_or_create(
                    user=recording.owner
                )
            
            # Transcribe
            result = self.engine.transcribe(
                audio_file_path=recording.file_path,
                provider=settings.preferred_provider,
                language=settings.default_language if not settings.auto_detect_language else None,
                enable_diarization=settings.enable_speaker_diarization,
                custom_vocabulary=settings.custom_vocabulary
            )
            
            if not result.get('success'):
                raise Exception(result.get('error', 'Transcription failed'))
            
            # Speaker diarization
            speaker_data = {}
            if settings.enable_speaker_diarization and result.get('segments'):
                speaker_result = self.diarization.identify_speakers(
                    result['segments'],
                    participant_hints=recording.participants
                )
                if speaker_result.get('success'):
                    # Merge speaker labels into segments
                    labeled_segments = self.diarization.merge_speaker_labels(
                        result['segments'],
                        speaker_result.get('segment_assignments', [])
                    )
                    speaker_data = {
                        'has_labels': True,
                        'speaker_count': speaker_result.get('speaker_count'),
                        'speakers': speaker_result.get('speakers', []),
                        'segments': labeled_segments
                    }
            
            # Create transcription record
            transcription = Transcription.objects.create(
                recording=recording,
                full_text=result.get('full_text', ''),
                words_with_timing=result.get('words', []),
                has_speaker_labels=speaker_data.get('has_labels', False),
                speaker_segments=speaker_data.get('segments', result.get('segments', [])),
                speaker_count=speaker_data.get('speaker_count'),
                speaker_mapping={
                    s['id']: s.get('description', s['id'])
                    for s in speaker_data.get('speakers', [])
                },
                confidence_score=result.get('confidence'),
                provider=settings.preferred_provider,
                detected_language=result.get('language', 'en'),
                processing_time_seconds=(timezone.now() - recording.processing_started_at).total_seconds()
            )
            
            recording.status = 'transcribed'
            recording.detected_language = result.get('language', 'en')
            recording.save()
            
            return transcription
            
        except Exception as e:
            recording.status = 'failed'
            recording.processing_error = str(e)
            recording.save()
            raise


class AnalysisService:
    """Service for AI analysis of recordings"""
    
    def __init__(self):
        self.summarizer = ConversationSummarizer()
        self.action_extractor = ActionItemExtractor()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.moment_detector = KeyMomentDetector()
        self.call_scorer = CallScorer()
        self.topic_extractor = TopicExtractor()
    
    def analyze_recording(
        self,
        recording: VoiceRecording,
        settings: Optional[TranscriptionSettings] = None
    ) -> Dict[str, Any]:
        """Perform full AI analysis on a recording"""
        
        recording.status = 'analyzing'
        recording.save()
        
        try:
            # Get settings
            if not settings:
                settings, _ = TranscriptionSettings.objects.get_or_create(
                    user=recording.owner
                )
            
            # Get transcription
            transcription = recording.transcription
            transcript = transcription.full_text
            segments = transcription.speaker_segments
            
            # Build context
            context = self._build_context(recording)
            
            results = {}
            
            # Generate summary
            if settings.auto_generate_summary:
                summary_result = self.summarizer.generate_summary(
                    transcript, 'executive', context
                )
                if summary_result.get('success'):
                    summary = ConversationSummary.objects.create(
                        recording=recording,
                        summary_type='executive',
                        summary_text=summary_result.get('summary_text', ''),
                        key_points=summary_result.get('key_points', []),
                        topics=summary_result.get('topics', []),
                        decisions=summary_result.get('decisions', []),
                        questions_asked=summary_result.get('questions_asked', []),
                        questions_unanswered=summary_result.get('questions_unanswered', []),
                        next_steps=summary_result.get('next_steps', []),
                        keywords=summary_result.get('keywords', []),
                        entities_mentioned=summary_result.get('entities_mentioned', {}),
                        model_used='gpt-4o'
                    )
                    results['summary'] = summary
            
            # Extract action items
            if settings.auto_extract_action_items:
                action_items = self.action_extractor.extract_action_items(transcript)
                created_items = []
                for item in action_items:
                    action = ActionItem.objects.create(
                        recording=recording,
                        title=item.get('title', 'Action Item'),
                        description=item.get('description', ''),
                        assigned_to_name=item.get('assigned_to_name', ''),
                        context_quote=item.get('context_quote', ''),
                        speaker=item.get('speaker', ''),
                        priority=item.get('priority', 'medium'),
                        confidence=item.get('confidence', 0.8)
                    )
                    # TODO: Parse due date if mentioned
                    created_items.append(action)
                results['action_items'] = created_items
            
            # Analyze sentiment
            if settings.auto_analyze_sentiment:
                sentiment_result = self.sentiment_analyzer.analyze_sentiment(
                    transcript, segments
                )
                sentiment = SentimentAnalysis.objects.create(
                    recording=recording,
                    overall_sentiment=sentiment_result.get('overall_sentiment', 'neutral'),
                    overall_score=sentiment_result.get('overall_score', 0.0),
                    sentiment_timeline=sentiment_result.get('sentiment_timeline', []),
                    emotions_detected=sentiment_result.get('emotions_detected', {}),
                    dominant_emotion=sentiment_result.get('dominant_emotion', ''),
                    positive_moments=sentiment_result.get('positive_moments', []),
                    negative_moments=sentiment_result.get('negative_moments', []),
                    engagement_score=sentiment_result.get('engagement_score'),
                    tone_analysis=sentiment_result.get('tone_analysis', {})
                )
                results['sentiment'] = sentiment
            
            # Detect key moments
            if segments:
                moments = self.moment_detector.detect_key_moments(transcript, segments)
                created_moments = []
                for moment in moments:
                    key_moment = KeyMoment.objects.create(
                        recording=recording,
                        moment_type=moment.get('moment_type', 'highlight'),
                        start_timestamp=moment.get('start_timestamp', 0),
                        end_timestamp=moment.get('end_timestamp', 0),
                        transcript_excerpt=moment.get('transcript_excerpt', ''),
                        speaker=moment.get('speaker', ''),
                        summary=moment.get('summary', ''),
                        importance_score=moment.get('importance_score', 0.5),
                        is_ai_detected=True
                    )
                    created_moments.append(key_moment)
                results['key_moments'] = created_moments
            
            # Score call if it's a sales call
            if settings.auto_score_calls and recording.source_type in ['phone_call', 'video_meeting']:
                score_result = self.call_scorer.score_call(transcript)
                call_score = CallScore.objects.create(
                    recording=recording,
                    overall_score=score_result.get('overall_score', 0),
                    opening_score=score_result.get('opening_score', 0),
                    discovery_score=score_result.get('discovery_score', 0),
                    presentation_score=score_result.get('presentation_score', 0),
                    objection_handling_score=score_result.get('objection_handling_score', 0),
                    closing_score=score_result.get('closing_score', 0),
                    talk_to_listen_ratio=score_result.get('talk_to_listen_ratio'),
                    question_count=score_result.get('question_count', 0),
                    filler_word_count=score_result.get('filler_word_count', 0),
                    filler_words_used=score_result.get('filler_words_used', []),
                    mentioned_value_prop=score_result.get('mentioned_value_prop', False),
                    asked_discovery_questions=score_result.get('asked_discovery_questions', False),
                    handled_objections=score_result.get('handled_objections', False),
                    established_next_steps=score_result.get('established_next_steps', False),
                    personalized_conversation=score_result.get('personalized_conversation', False),
                    coaching_tips=score_result.get('coaching_tips', []),
                    areas_for_improvement=score_result.get('areas_for_improvement', []),
                    strengths=score_result.get('strengths', [])
                )
                results['call_score'] = call_score
            
            recording.status = 'completed'
            recording.processing_completed_at = timezone.now()
            recording.save()
            
            return results
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            recording.status = 'completed'  # Mark as completed even if some analysis failed
            recording.processing_completed_at = timezone.now()
            recording.save()
            raise
    
    def _build_context(self, recording: VoiceRecording) -> Dict:
        """Build context from related records"""
        context = {}
        
        if recording.contact:
            context['contact_name'] = f"{recording.contact.first_name} {recording.contact.last_name}"
            context['company'] = getattr(recording.contact, 'company', '')
        
        if recording.lead:
            context['lead_name'] = getattr(recording.lead, 'name', str(recording.lead))
        
        if recording.opportunity:
            context['opportunity'] = getattr(recording.opportunity, 'name', str(recording.opportunity))
        
        return context


class VoiceNoteService:
    """Service for quick voice notes"""
    
    def __init__(self):
        self.transcription_engine = TranscriptionEngine()
        self.note_processor = VoiceNoteProcessor()
    
    @transaction.atomic
    def create_voice_note(
        self,
        user: User,
        audio_file,
        related_to: Optional[Dict] = None
    ) -> VoiceNote:
        """Create and process a voice note"""
        
        # Generate file path
        file_name = f"note_{uuid.uuid4()}.{audio_file.name.split('.')[-1]}"
        file_path = f"voice_notes/{user.id}/{file_name}"
        
        # Save file temporarily for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_name.split('.')[-1]}") as tmp:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
        
        try:
            # Get audio duration
            from .transcription_engine import AudioPreprocessor
            audio_info = AudioPreprocessor.get_audio_info(tmp_path)
            
            # Transcribe
            result = self.transcription_engine.transcribe(tmp_path, provider='whisper')
            transcript = result.get('full_text', '') if result.get('success') else ''
            
            # Build context for AI processing
            context = {}
            contact_id = None
            lead_id = None
            opportunity_id = None
            
            if related_to:
                contact_id = related_to.get('contact_id')
                lead_id = related_to.get('lead_id')
                opportunity_id = related_to.get('opportunity_id')
                context = {
                    'contact_name': related_to.get('contact_name', ''),
                    'company': related_to.get('company', '')
                }
            
            # Process with AI
            ai_result = self.note_processor.process_voice_note(transcript, context)
            
            # Create voice note
            voice_note = VoiceNote.objects.create(
                owner=user,
                audio_path=file_path,
                duration_seconds=int(audio_info.get('duration', 0)),
                transcript=transcript,
                is_transcribed=bool(transcript),
                ai_title=ai_result.get('ai_title', 'Voice Note'),
                ai_summary=ai_result.get('ai_summary', ''),
                action_items_extracted=ai_result.get('action_items', []),
                tags=ai_result.get('tags', []),
                contact_id=contact_id,
                lead_id=lead_id,
                opportunity_id=opportunity_id
            )
            
            # TODO: Upload file to storage
            
            return voice_note
            
        finally:
            os.unlink(tmp_path)
    
    def get_notes_for_record(
        self,
        record_type: str,
        record_id: str,
        user: User
    ) -> List[VoiceNote]:
        """Get voice notes for a related record"""
        queryset = VoiceNote.objects.filter(owner=user)
        
        if record_type == 'contact':
            queryset = queryset.filter(contact_id=record_id)
        elif record_type == 'lead':
            queryset = queryset.filter(lead_id=record_id)
        elif record_type == 'opportunity':
            queryset = queryset.filter(opportunity_id=record_id)
        
        return list(queryset.order_by('-created_at'))


class CategoryService:
    """Service for managing conversation categories"""
    
    def auto_categorize(self, recording: VoiceRecording) -> List[ConversationCategory]:
        """Auto-categorize a recording based on content"""
        try:
            transcription = recording.transcription
            if not transcription:
                return []
            
            transcript = transcription.full_text.lower()
            
            # Get all categories with keywords
            categories = ConversationCategory.objects.exclude(keywords=[])
            matched_categories = []
            
            for category in categories:
                keywords = category.keywords
                matches = sum(1 for kw in keywords if kw.lower() in transcript)
                
                if matches > 0:
                    confidence = min(1.0, matches / len(keywords))
                    if confidence >= 0.3:  # Threshold
                        RecordingCategory.objects.get_or_create(
                            recording=recording,
                            category=category,
                            defaults={
                                'is_auto_classified': True,
                                'confidence': confidence
                            }
                        )
                        # Update category count
                        category.recording_count = category.recordings.count()
                        category.save()
                        matched_categories.append(category)
            
            return matched_categories
            
        except Exception as e:
            logger.error(f"Auto-categorization error: {str(e)}")
            return []


class ProcessingOrchestrator:
    """Orchestrate the full processing pipeline"""
    
    def __init__(self):
        self.transcription_service = TranscriptionService()
        self.analysis_service = AnalysisService()
        self.category_service = CategoryService()
    
    def process_recording(
        self,
        recording: VoiceRecording,
        options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Run full processing pipeline"""
        results = {
            'recording_id': str(recording.id),
            'status': 'processing',
            'steps_completed': []
        }
        
        try:
            # Get user settings
            settings, _ = TranscriptionSettings.objects.get_or_create(
                user=recording.owner
            )
            
            # Step 1: Transcribe
            transcription = self.transcription_service.transcribe_recording(
                recording, settings
            )
            results['steps_completed'].append('transcription')
            results['transcription'] = {
                'word_count': transcription.word_count,
                'duration': recording.duration_seconds,
                'language': transcription.detected_language
            }
            
            # Step 2: AI Analysis
            analysis = self.analysis_service.analyze_recording(recording, settings)
            results['steps_completed'].append('analysis')
            results['analysis'] = {
                'has_summary': 'summary' in analysis,
                'action_items_count': len(analysis.get('action_items', [])),
                'key_moments_count': len(analysis.get('key_moments', [])),
                'call_score': analysis.get('call_score', {}).overall_score if analysis.get('call_score') else None
            }
            
            # Step 3: Auto-categorize
            categories = self.category_service.auto_categorize(recording)
            results['steps_completed'].append('categorization')
            results['categories'] = [c.name for c in categories]
            
            results['status'] = 'completed'
            
        except Exception as e:
            results['status'] = 'failed'
            results['error'] = str(e)
            logger.error(f"Processing pipeline error: {str(e)}")
        
        return results
