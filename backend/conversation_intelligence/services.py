"""
Conversation Intelligence Service Layer
"""

import os
from datetime import timedelta

from django.db import models
from django.utils import timezone


class ConversationIntelligenceService:
    """Service for conversation intelligence operations"""

    def __init__(self):
        self.openai_available = bool(os.environ.get('OPENAI_API_KEY'))

    def process_recording_async(self, recording):
        """Queue recording for async processing"""
        # In production, this would use Celery
        # For now, process synchronously (or mock)

        recording.status = 'processing'
        recording.save()

        try:
            self.process_recording(recording)
        except Exception as e:
            recording.status = 'failed'
            recording.processing_error = str(e)
            recording.save()

    def process_recording(self, recording):
        """Process a recording - transcribe and analyze"""
        from .models import CallAnalysis, CallTranscript, TranscriptSegment

        # Step 1: Transcribe
        recording.status = 'transcribing'
        recording.save()

        transcript_data = self._transcribe_audio(recording)

        # Create transcript
        transcript = CallTranscript.objects.create(
            recording=recording,
            full_text=transcript_data['full_text'],
            word_count=len(transcript_data['full_text'].split()),
            detected_language=transcript_data.get('language', 'en'),
            confidence_score=transcript_data.get('confidence', 0.9)
        )

        # Create segments
        for segment_data in transcript_data.get('segments', []):
            TranscriptSegment.objects.create(
                transcript=transcript,
                **segment_data
            )

        # Step 2: Analyze
        recording.status = 'analyzing'
        recording.save()

        analysis_data = self._analyze_transcript(recording, transcript)

        CallAnalysis.objects.create(
            recording=recording,
            **analysis_data
        )

        # Step 3: Extract topics
        self._extract_topics(recording, transcript)

        # Mark as ready
        recording.status = 'ready'
        recording.save()

        # Update analytics
        self._update_analytics(recording)

    def _transcribe_audio(self, recording):
        """Transcribe audio file"""
        # In production, use Whisper API or similar
        # For now, return mock data

        return {
            'full_text': 'This is a mock transcript of the sales call...',
            'language': 'en',
            'confidence': 0.95,
            'segments': [
                {
                    'speaker': 'Sales Rep',
                    'speaker_type': 'rep',
                    'text': 'Thank you for joining the call today.',
                    'start_time': 0,
                    'end_time': 3,
                    'sentiment': 'neutral',
                    'sentiment_score': 0.1
                },
                {
                    'speaker': 'Prospect',
                    'speaker_type': 'prospect',
                    'text': 'Thanks for having me. I am excited to learn more.',
                    'start_time': 3,
                    'end_time': 7,
                    'sentiment': 'positive',
                    'sentiment_score': 0.7
                },
            ]
        }

    def _analyze_transcript(self, recording, transcript):
        """Analyze transcript for insights"""
        segments = transcript.segments.all()

        # Calculate talk ratios
        rep_time = sum(
            float(s.end_time - s.start_time)
            for s in segments if s.speaker_type == 'rep'
        )
        prospect_time = sum(
            float(s.end_time - s.start_time)
            for s in segments if s.speaker_type == 'prospect'
        )
        total_time = rep_time + prospect_time

        rep_ratio = (rep_time / total_time * 100) if total_time > 0 else 50
        prospect_ratio = (prospect_time / total_time * 100) if total_time > 0 else 50

        # Count questions
        question_count = sum(
            1 for s in segments
            if s.speaker_type == 'rep' and '?' in s.text
        )

        # Analyze sentiment
        sentiments = [s.sentiment for s in segments]
        positive = sentiments.count('positive')
        negative = sentiments.count('negative')

        if positive > negative:
            overall_sentiment = 'positive'
        elif negative > positive:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'

        # Calculate engagement score
        engagement_score = min(100, int(
            (question_count * 5) +
            (prospect_ratio * 0.5) +
            (positive * 10)
        ))

        # Calculate call score
        call_score = self._calculate_call_score(
            rep_ratio, question_count, engagement_score, overall_sentiment
        )

        return {
            'rep_talk_ratio': round(rep_ratio, 2),
            'prospect_talk_ratio': round(prospect_ratio, 2),
            'longest_rep_monologue': 0,  # Would calculate from segments
            'longest_prospect_monologue': 0,
            'question_count': question_count,
            'engagement_score': engagement_score,
            'energy_level': 'medium',
            'overall_sentiment': overall_sentiment,
            'sentiment_trend': 'stable',
            'summary': self._generate_summary(transcript),
            'key_points': self._extract_key_points(transcript),
            'action_items': self._extract_action_items(transcript),
            'buying_signals': [],
            'objections_raised': [],
            'competitor_mentions': [],
            'call_score': call_score,
            'areas_for_improvement': self._get_improvement_areas(rep_ratio, question_count),
        }

    def _calculate_call_score(self, rep_ratio, question_count, engagement, sentiment):
        """Calculate overall call score"""
        score = 50  # Base score

        # Talk ratio (ideal: 40-60% rep)
        if 40 <= rep_ratio <= 60:
            score += 15
        elif 30 <= rep_ratio <= 70:
            score += 10

        # Questions (more is better, up to a point)
        score += min(question_count * 3, 15)

        # Engagement
        score += int(engagement * 0.1)

        # Sentiment
        if sentiment == 'positive':
            score += 10
        elif sentiment == 'negative':
            score -= 10

        return min(100, max(0, score))

    def _generate_summary(self, transcript):
        """Generate call summary"""
        # In production, use GPT for this
        return "This was a productive discovery call where the sales rep learned about the prospect's pain points and discussed potential solutions."

    def _extract_key_points(self, transcript):
        """Extract key points from transcript"""
        return [
            "Prospect is evaluating multiple solutions",
            "Budget decision expected by end of quarter",
            "Main pain point is team collaboration"
        ]

    def _extract_action_items(self, transcript):
        """Extract action items from transcript"""
        return [
            "Send pricing proposal by Friday",
            "Schedule technical demo with IT team",
            "Share case study from similar company"
        ]

    def _get_improvement_areas(self, rep_ratio, question_count):
        """Get areas for improvement"""
        areas = []

        if rep_ratio > 70:
            areas.append("Try to talk less and listen more - aim for 40-60% talk ratio")
        elif rep_ratio < 30:
            areas.append("Engage more in the conversation to build rapport")

        if question_count < 3:
            areas.append("Ask more discovery questions to understand customer needs")

        return areas

    def _extract_topics(self, recording, transcript):
        """Extract topic mentions from transcript"""
        from .models import TopicMention

        # Keywords to look for
        pricing_keywords = ['price', 'cost', 'budget', 'expensive', 'discount']
        competitor_keywords = ['competitor', 'alternative', 'versus', 'compared']

        for segment in transcript.segments.all():
            text_lower = segment.text.lower()

            for keyword in pricing_keywords:
                if keyword in text_lower:
                    TopicMention.objects.create(
                        recording=recording,
                        topic_type='pricing',
                        topic_name=keyword,
                        context=segment.text,
                        timestamp=segment.start_time,
                        sentiment=segment.sentiment
                    )
                    break

            for keyword in competitor_keywords:
                if keyword in text_lower:
                    TopicMention.objects.create(
                        recording=recording,
                        topic_type='competitor',
                        topic_name=keyword,
                        context=segment.text,
                        timestamp=segment.start_time,
                        sentiment=segment.sentiment
                    )
                    break

    def _update_analytics(self, recording):
        """Update user analytics"""
        from .models import ConversationAnalytics

        today = timezone.now().date()
        analytics, _ = ConversationAnalytics.objects.get_or_create(
            user=recording.owner,
            date=today
        )

        analytics.calls_recorded += 1
        analytics.total_duration_minutes += recording.duration_seconds // 60

        if hasattr(recording, 'analysis'):
            analysis = recording.analysis
            # Update averages
            total_calls = analytics.calls_recorded

            analytics.avg_talk_ratio = (
                (analytics.avg_talk_ratio * (total_calls - 1) + analysis.rep_talk_ratio) / total_calls
            )
            analytics.avg_call_score = (
                (analytics.avg_call_score * (total_calls - 1) + analysis.call_score) / total_calls
            )

            if analysis.overall_sentiment == 'positive':
                analytics.positive_sentiment_calls += 1
            if analysis.action_items:
                analytics.calls_with_action_items += 1

        analytics.save()

    def get_tracker_trends(self, tracker, days):
        """Get mention trends for a tracker"""
        from .models import TopicMention

        start_date = timezone.now() - timedelta(days=days)

        mentions = TopicMention.objects.filter(
            topic_name__in=tracker.keywords,
            recording__recorded_at__gte=start_date
        ).values('recording__recorded_at__date').annotate(
            count=models.Count('id')
        ).order_by('recording__recorded_at__date')

        return list(mentions)
