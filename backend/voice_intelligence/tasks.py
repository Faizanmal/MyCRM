"""
Voice Intelligence Tasks
Celery tasks for async voice processing
"""

import contextlib
import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_recording_task(self, recording_id: str):
    """Full processing pipeline for a recording"""
    try:
        from .models import VoiceRecording
        from .services import ProcessingOrchestrator

        recording = VoiceRecording.objects.get(id=recording_id)

        orchestrator = ProcessingOrchestrator()
        result = orchestrator.process_recording(recording)

        logger.info(f"Recording {recording_id} processed: {result['status']}")
        return result

    except VoiceRecording.DoesNotExist:
        logger.error(f"Recording not found: {recording_id}")
        return {'status': 'error', 'message': 'Recording not found'}

    except Exception as e:
        logger.error(f"Processing error for {recording_id}: {str(e)}")

        # Retry on transient errors
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e) from e

        # Mark as failed on final retry
        with contextlib.suppress(Exception):
            recording = VoiceRecording.objects.get(id=recording_id)
            recording.status = 'failed'
            recording.processing_error = str(e)
            recording.save()

        return {'status': 'failed', 'error': str(e)}


@shared_task(bind=True, max_retries=3)
def transcribe_recording_task(self, recording_id: str):
    """Transcribe a recording"""
    try:
        from .models import VoiceRecording
        from .services import TranscriptionService

        recording = VoiceRecording.objects.get(id=recording_id)
        service = TranscriptionService()

        transcription = service.transcribe_recording(recording)

        logger.info(f"Recording {recording_id} transcribed")
        return {
            'status': 'success',
            'transcription_id': str(transcription.id),
            'word_count': transcription.word_count
        }

    except VoiceRecording.DoesNotExist:
        logger.error(f"Recording not found: {recording_id}")
        return {'status': 'error', 'message': 'Recording not found'}

    except Exception as e:
        logger.error(f"Transcription error for {recording_id}: {str(e)}")

        if self.request.retries < self.max_retries:
            raise self.retry(exc=e) from e

        return {'status': 'failed', 'error': str(e)}


@shared_task(bind=True, max_retries=2)
def analyze_recording_task(self, recording_id: str):
    """Run AI analysis on a recording"""
    try:
        from .models import VoiceRecording
        from .services import AnalysisService

        recording = VoiceRecording.objects.get(id=recording_id)
        service = AnalysisService()

        results = service.analyze_recording(recording)

        logger.info(f"Recording {recording_id} analyzed")
        return {
            'status': 'success',
            'has_summary': 'summary' in results,
            'action_items_count': len(results.get('action_items', []))
        }

    except VoiceRecording.DoesNotExist:
        logger.error(f"Recording not found: {recording_id}")
        return {'status': 'error', 'message': 'Recording not found'}

    except Exception as e:
        logger.error(f"Analysis error for {recording_id}: {str(e)}")

        if self.request.retries < self.max_retries:
            raise self.retry(exc=e) from e

        return {'status': 'failed', 'error': str(e)}


@shared_task
def generate_summary_task(recording_id: str, summary_type: str = 'executive'):
    """Generate a specific type of summary"""
    try:
        from .ai_summarizer import ConversationSummarizer
        from .models import ConversationSummary, VoiceRecording

        recording = VoiceRecording.objects.get(id=recording_id)

        if not hasattr(recording, 'transcription'):
            return {'status': 'error', 'message': 'No transcription available'}

        summarizer = ConversationSummarizer()

        # Build context
        context = {}
        if recording.contact:
            context['contact_name'] = f"{recording.contact.first_name} {recording.contact.last_name}"

        result = summarizer.generate_summary(
            recording.transcription.full_text,
            summary_type,
            context
        )

        if result.get('success'):
            summary = ConversationSummary.objects.create(
                recording=recording,
                summary_type=summary_type,
                summary_text=result.get('summary_text', ''),
                key_points=result.get('key_points', []),
                topics=result.get('topics', []),
                decisions=result.get('decisions', []),
                questions_asked=result.get('questions_asked', []),
                questions_unanswered=result.get('questions_unanswered', []),
                next_steps=result.get('next_steps', []),
                keywords=result.get('keywords', []),
                entities_mentioned=result.get('entities_mentioned', {}),
                model_used='gpt-4o'
            )

            return {
                'status': 'success',
                'summary_id': str(summary.id)
            }

        return {'status': 'failed', 'error': result.get('error')}

    except Exception as e:
        logger.error(f"Summary generation error: {str(e)}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def extract_action_items_task(recording_id: str):
    """Extract action items from a recording"""
    try:
        from .ai_summarizer import ActionItemExtractor
        from .models import ActionItem, VoiceRecording

        recording = VoiceRecording.objects.get(id=recording_id)

        if not hasattr(recording, 'transcription'):
            return {'status': 'error', 'message': 'No transcription available'}

        extractor = ActionItemExtractor()
        items = extractor.extract_action_items(recording.transcription.full_text)

        created_items = []
        for item in items:
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
            created_items.append(str(action.id))

        return {
            'status': 'success',
            'action_item_ids': created_items,
            'count': len(created_items)
        }

    except Exception as e:
        logger.error(f"Action item extraction error: {str(e)}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def score_call_task(recording_id: str):
    """Score a sales call"""
    try:
        from .ai_summarizer import CallScorer
        from .models import CallScore, VoiceRecording

        recording = VoiceRecording.objects.get(id=recording_id)

        if not hasattr(recording, 'transcription'):
            return {'status': 'error', 'message': 'No transcription available'}

        scorer = CallScorer()
        result = scorer.score_call(recording.transcription.full_text)

        # Delete existing score if any
        CallScore.objects.filter(recording=recording).delete()

        call_score = CallScore.objects.create(
            recording=recording,
            overall_score=result.get('overall_score', 0),
            opening_score=result.get('opening_score', 0),
            discovery_score=result.get('discovery_score', 0),
            presentation_score=result.get('presentation_score', 0),
            objection_handling_score=result.get('objection_handling_score', 0),
            closing_score=result.get('closing_score', 0),
            talk_to_listen_ratio=result.get('talk_to_listen_ratio'),
            question_count=result.get('question_count', 0),
            filler_word_count=result.get('filler_word_count', 0),
            filler_words_used=result.get('filler_words_used', []),
            mentioned_value_prop=result.get('mentioned_value_prop', False),
            asked_discovery_questions=result.get('asked_discovery_questions', False),
            handled_objections=result.get('handled_objections', False),
            established_next_steps=result.get('established_next_steps', False),
            personalized_conversation=result.get('personalized_conversation', False),
            coaching_tips=result.get('coaching_tips', []),
            areas_for_improvement=result.get('areas_for_improvement', []),
            strengths=result.get('strengths', [])
        )

        return {
            'status': 'success',
            'call_score_id': str(call_score.id),
            'overall_score': call_score.overall_score
        }

    except Exception as e:
        logger.error(f"Call scoring error: {str(e)}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def auto_categorize_task(recording_id: str):
    """Auto-categorize a recording"""
    try:
        from .models import VoiceRecording
        from .services import CategoryService

        recording = VoiceRecording.objects.get(id=recording_id)
        service = CategoryService()

        categories = service.auto_categorize(recording)

        return {
            'status': 'success',
            'categories': [c.name for c in categories]
        }

    except Exception as e:
        logger.error(f"Auto-categorization error: {str(e)}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def process_voice_note_task(voice_note_id: str):
    """Process a voice note"""
    try:
        from .ai_summarizer import VoiceNoteProcessor
        from .models import VoiceNote
        from .transcription_engine import TranscriptionEngine

        note = VoiceNote.objects.get(id=voice_note_id)

        # Transcribe if not already done
        if not note.is_transcribed:
            engine = TranscriptionEngine()
            result = engine.transcribe(note.audio_path)

            if result.get('success'):
                note.transcript = result.get('full_text', '')
                note.is_transcribed = True

        # Process with AI
        if note.transcript:
            processor = VoiceNoteProcessor()
            context = {}

            if note.contact:
                context['contact_name'] = f"{note.contact.first_name} {note.contact.last_name}"

            ai_result = processor.process_voice_note(note.transcript, context)

            note.ai_title = ai_result.get('ai_title', 'Voice Note')
            note.ai_summary = ai_result.get('ai_summary', '')
            note.action_items_extracted = ai_result.get('action_items', [])
            note.tags = ai_result.get('tags', [])

        note.save()

        return {
            'status': 'success',
            'voice_note_id': str(note.id),
            'title': note.ai_title
        }

    except Exception as e:
        logger.error(f"Voice note processing error: {str(e)}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def cleanup_failed_recordings():
    """Clean up recordings stuck in failed state"""
    from datetime import timedelta

    from .models import VoiceRecording

    # Find recordings failed more than 24 hours ago
    cutoff = timezone.now() - timedelta(hours=24)

    failed_recordings = VoiceRecording.objects.filter(
        status='failed',
        updated_at__lt=cutoff
    )

    count = failed_recordings.count()

    # Option 1: Retry processing
    for recording in failed_recordings[:10]:  # Limit batch size
        process_recording_task.delay(str(recording.id))

    logger.info(f"Queued {min(count, 10)} failed recordings for retry")

    return {'retried_count': min(count, 10), 'total_failed': count}


@shared_task
def generate_daily_analytics():
    """Generate daily analytics summary"""
    from datetime import timedelta

    from django.db.models import Avg, Sum

    from .models import ActionItem, CallScore, VoiceRecording

    yesterday = timezone.now().date() - timedelta(days=1)

    # Get stats for yesterday
    recordings = VoiceRecording.objects.filter(
        recorded_at__date=yesterday
    )

    stats = {
        'date': str(yesterday),
        'total_recordings': recordings.count(),
        'total_duration': recordings.aggregate(
            total=Sum('duration_seconds')
        )['total'] or 0,
        'completed': recordings.filter(status='completed').count(),
        'failed': recordings.filter(status='failed').count(),
        'avg_call_score': CallScore.objects.filter(
            recording__in=recordings
        ).aggregate(avg=Avg('overall_score'))['avg'] or 0,
        'action_items_created': ActionItem.objects.filter(
            created_at__date=yesterday
        ).count()
    }

    logger.info(f"Daily analytics for {yesterday}: {stats}")

    # TODO: Store in analytics table or send report
    return stats


@shared_task
def sync_action_items_to_tasks():
    """Sync confirmed action items to task management"""
    from .models import ActionItem

    # Find confirmed action items without linked tasks
    items = ActionItem.objects.filter(
        was_confirmed=True,
        linked_task__isnull=True,
        status='pending'
    )[:50]  # Batch size

    synced = 0
    for item in items:
        try:
            from task_management.models import Task

            task = Task.objects.create(
                title=item.title,
                description=item.description,
                assigned_to=item.assigned_to or item.recording.owner,
                due_date=item.due_date,
                priority=item.priority,
                created_by=item.recording.owner
            )

            item.linked_task = task
            item.save(update_fields=['linked_task'])
            synced += 1

        except Exception as e:
            logger.error(f"Error syncing action item {item.id}: {str(e)}")

    return {'synced_count': synced}
