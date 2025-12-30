"""
Voice & Conversation Intelligence - Advanced Services
Real-time coaching engine, sentiment analyzer, and meeting summarizer
"""

import os
import json
import re
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional

from django.db.models import Sum, Avg, Count
from django.utils import timezone


class RealTimeCoachingEngine:
    """Engine for real-time call coaching"""
    
    def __init__(self):
        self.openai_available = bool(os.environ.get('OPENAI_API_KEY'))
        
        # Coaching rules
        self.talk_ratio_threshold = 60  # Alert if rep talks more than 60%
        self.question_interval = 300  # Suggest question every 5 minutes
        self.silence_threshold = 10  # Alert after 10 seconds silence
        
        # Objection patterns
        self.objection_patterns = [
            r'too expensive|price is high|budget|cost',
            r'not the right time|busy|later|next quarter',
            r'need to think|discuss with|check with',
            r'already have|using|competitor',
            r'not interested|not a priority',
        ]
    
    def start_coaching_session(self, recording) -> Dict[str, Any]:
        """Start a new coaching session for a call"""
        
        from .advanced_models import RealTimeCoachingSession
        
        session, created = RealTimeCoachingSession.objects.get_or_create(
            recording=recording,
            defaults={
                'status': 'active',
                'coaching_enabled': True,
                'suggestions_enabled': True,
            }
        )
        
        return {
            'session_id': str(session.id),
            'status': session.status,
            'created': created,
        }
    
    def process_audio_chunk(self, session, audio_data: bytes, 
                           timestamp: float) -> Dict[str, Any]:
        """Process an audio chunk and generate suggestions"""
        
        # In production, this would use real-time transcription
        # For now, we simulate the analysis
        
        suggestions = []
        metrics = {
            'talk_ratio': session.current_talk_ratio,
            'question_count': session.question_count,
            'sentiment': session.current_sentiment,
        }
        
        return {
            'suggestions': suggestions,
            'metrics': metrics,
        }
    
    def process_transcript_segment(self, session, segment: Dict) -> List[Dict]:
        """Process a transcript segment and generate suggestions"""
        
        suggestions = []
        text = segment.get('text', '').lower()
        speaker_type = segment.get('speaker_type', 'unknown')
        timestamp = segment.get('timestamp', 0)
        
        # Check for objections
        for pattern in self.objection_patterns:
            if re.search(pattern, text):
                suggestion = self._generate_objection_suggestion(
                    text, pattern, timestamp
                )
                if suggestion:
                    suggestions.append(suggestion)
                break
        
        # Check talk ratio
        if speaker_type == 'rep' and session.current_talk_ratio > self.talk_ratio_threshold:
            suggestions.append({
                'type': 'warning',
                'priority': 'medium',
                'title': 'Balance the conversation',
                'content': 'You\'ve been talking a lot. Try asking an open-ended question.',
                'timestamp': timestamp,
            })
        
        # Check for question opportunities
        question_words = ['how', 'what', 'why', 'when', 'who', 'which']
        if speaker_type == 'prospect':
            # Prospect is talking - good time to prepare follow-up
            if any(word in text for word in question_words):
                suggestions.append({
                    'type': 'technique',
                    'priority': 'low',
                    'title': 'Follow up on their question',
                    'content': 'They asked a question. Make sure to address it fully.',
                    'timestamp': timestamp,
                })
        
        return suggestions
    
    def _generate_objection_suggestion(self, text: str, pattern: str, 
                                        timestamp: float) -> Optional[Dict]:
        """Generate a suggestion for handling an objection"""
        
        if 'expensive' in pattern or 'price' in pattern or 'budget' in pattern:
            return {
                'type': 'objection',
                'priority': 'high',
                'title': 'Price objection detected',
                'content': (
                    '1. Acknowledge the concern\n'
                    '2. Ask: "When you say expensive, compared to what?"\n'
                    '3. Focus on ROI and value delivered'
                ),
                'timestamp': timestamp,
            }
        
        if 'not the right time' in pattern or 'busy' in pattern:
            return {
                'type': 'objection',
                'priority': 'medium',
                'title': 'Timing objection detected',
                'content': (
                    '1. Understand their timeline\n'
                    '2. Ask: "What would need to change for this to become a priority?"\n'
                    '3. Suggest a future check-in'
                ),
                'timestamp': timestamp,
            }
        
        if 'think about it' in pattern or 'discuss' in pattern:
            return {
                'type': 'objection',
                'priority': 'high',
                'title': 'Decision delay detected',
                'content': (
                    '1. Ask: "What specific concerns do you need to think through?"\n'
                    '2. Offer to address them now\n'
                    '3. Schedule a specific follow-up'
                ),
                'timestamp': timestamp,
            }
        
        return None
    
    def update_metrics(self, session, segment: Dict):
        """Update session metrics based on new segment"""
        
        speaker_type = segment.get('speaker_type', 'unknown')
        duration = segment.get('duration', 0)
        
        # Update talk ratio (simplified calculation)
        if speaker_type == 'rep':
            session.current_talk_ratio = min(
                100, float(session.current_talk_ratio) + 2
            )
        else:
            session.current_talk_ratio = max(
                0, float(session.current_talk_ratio) - 2
            )
        
        # Check for questions
        text = segment.get('text', '')
        if '?' in text and speaker_type == 'rep':
            session.question_count += 1
        
        session.save()
    
    def end_coaching_session(self, session) -> Dict[str, Any]:
        """End a coaching session and generate summary"""
        
        from .advanced_models import RealTimeCoachingSuggestion
        
        session.status = 'ended'
        session.ended_at = timezone.now()
        session.save()
        
        # Generate session summary
        suggestions = RealTimeCoachingSuggestion.objects.filter(session=session)
        
        summary = {
            'total_suggestions': suggestions.count(),
            'suggestions_viewed': suggestions.filter(was_viewed=True).count(),
            'suggestions_applied': suggestions.filter(was_applied=True).count(),
            'final_talk_ratio': float(session.current_talk_ratio),
            'total_questions': session.question_count,
            'objections_handled': session.objection_count,
        }
        
        return summary


class SentimentAnalyzer:
    """Analyze sentiment across conversations"""
    
    def __init__(self):
        self.openai_available = bool(os.environ.get('OPENAI_API_KEY'))
        
        # Simple sentiment keywords (production would use ML model)
        self.positive_words = [
            'great', 'excellent', 'love', 'amazing', 'perfect', 'fantastic',
            'wonderful', 'happy', 'excited', 'interested', 'yes', 'agree',
            'definitely', 'absolutely', 'impressed', 'valuable',
        ]
        self.negative_words = [
            'bad', 'terrible', 'hate', 'awful', 'problem', 'issue', 'concern',
            'worry', 'disappointed', 'frustrated', 'expensive', 'difficult',
            'no', 'never', 'wrong', 'poor', 'unfortunately',
        ]
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        
        text_lower = text.lower()
        words = text_lower.split()
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            sentiment = 'neutral'
            score = 0
        elif positive_count > negative_count:
            sentiment = 'positive'
            score = min(1, positive_count / max(len(words), 1))
        elif negative_count > positive_count:
            sentiment = 'negative'
            score = max(-1, -negative_count / max(len(words), 1))
        else:
            sentiment = 'neutral'
            score = 0
        
        # Detect emotions
        emotions = self._detect_emotions(text_lower)
        
        return {
            'sentiment': sentiment,
            'score': round(score, 2),
            'confidence': min(0.9, total_sentiment_words / max(len(words), 1) + 0.3),
            'emotions': emotions,
            'positive_words': positive_count,
            'negative_words': negative_count,
        }
    
    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect emotions in text"""
        
        emotion_patterns = {
            'happy': ['happy', 'glad', 'pleased', 'delighted', 'joy'],
            'excited': ['excited', 'thrilled', 'eager', 'enthusiastic'],
            'confident': ['sure', 'certain', 'confident', 'definitely'],
            'frustrated': ['frustrated', 'annoyed', 'irritated'],
            'concerned': ['worried', 'concerned', 'anxious', 'nervous'],
            'interested': ['interested', 'curious', 'intrigued'],
        }
        
        emotions = {}
        for emotion, keywords in emotion_patterns.items():
            count = sum(1 for word in keywords if word in text)
            if count > 0:
                emotions[emotion] = min(1.0, count * 0.3)
        
        return emotions
    
    def analyze_recording(self, recording) -> Dict[str, Any]:
        """Analyze sentiment for an entire recording"""
        
        from .models import TranscriptSegment
        from .advanced_models import SentimentTimeline
        
        if not hasattr(recording, 'transcript'):
            return {'error': 'No transcript available'}
        
        segments = TranscriptSegment.objects.filter(
            transcript=recording.transcript
        ).order_by('start_time')
        
        timeline = []
        overall_scores = []
        
        for segment in segments:
            analysis = self.analyze_text(segment.text)
            
            # Save to timeline
            SentimentTimeline.objects.create(
                recording=recording,
                timestamp_seconds=segment.start_time,
                sentiment=analysis['sentiment'],
                sentiment_score=analysis['score'],
                emotions=analysis['emotions'],
                speaker=segment.speaker,
                speaker_type=segment.speaker_type,
                text_snippet=segment.text[:200],
            )
            
            timeline.append({
                'timestamp': float(segment.start_time),
                'sentiment': analysis['sentiment'],
                'score': analysis['score'],
                'speaker': segment.speaker,
            })
            
            overall_scores.append(analysis['score'])
        
        # Calculate overall metrics
        avg_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0
        
        if avg_score > 0.2:
            overall_sentiment = 'positive'
        elif avg_score < -0.2:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        return {
            'overall_sentiment': overall_sentiment,
            'overall_score': round(avg_score, 2),
            'timeline': timeline,
            'total_segments': len(segments),
        }
    
    def generate_dashboard(self, user, period: str = 'weekly') -> Dict[str, Any]:
        """Generate sentiment dashboard for a user"""
        
        from .models import CallRecording
        from .advanced_models import SentimentDashboard, SentimentTimeline
        
        today = timezone.now().date()
        
        if period == 'daily':
            start_date = today
            end_date = today
        elif period == 'weekly':
            start_date = today - timedelta(days=7)
            end_date = today
        else:  # monthly
            start_date = today - timedelta(days=30)
            end_date = today
        
        # Get recordings in period
        recordings = CallRecording.objects.filter(
            owner=user,
            recorded_at__date__gte=start_date,
            recorded_at__date__lte=end_date,
            status='ready'
        )
        
        if not recordings.exists():
            return {
                'period': period,
                'total_calls': 0,
                'message': 'No calls in this period',
            }
        
        # Aggregate sentiment data
        sentiments = SentimentTimeline.objects.filter(
            recording__in=recordings
        )
        
        total = sentiments.count()
        if total == 0:
            return {
                'period': period,
                'total_calls': recordings.count(),
                'message': 'No sentiment data available',
            }
        
        positive = sentiments.filter(sentiment='positive').count()
        neutral = sentiments.filter(sentiment='neutral').count()
        negative = sentiments.filter(sentiment='negative').count()
        
        avg_score = sentiments.aggregate(avg=Avg('sentiment_score'))['avg'] or 0
        
        # Save dashboard
        dashboard, _ = SentimentDashboard.objects.update_or_create(
            user=user,
            period=period,
            start_date=start_date,
            end_date=end_date,
            defaults={
                'total_calls': recordings.count(),
                'avg_sentiment_score': avg_score,
                'positive_percentage': (positive / total) * 100,
                'neutral_percentage': (neutral / total) * 100,
                'negative_percentage': (negative / total) * 100,
                'sentiment_trend': 'stable' if abs(avg_score) < 0.1 else ('improving' if avg_score > 0 else 'declining'),
                'trend_percentage': abs(avg_score) * 100,
            }
        )
        
        return {
            'period': period,
            'start_date': str(start_date),
            'end_date': str(end_date),
            'total_calls': recordings.count(),
            'avg_sentiment_score': round(float(avg_score), 2),
            'positive_percentage': round((positive / total) * 100, 1),
            'neutral_percentage': round((neutral / total) * 100, 1),
            'negative_percentage': round((negative / total) * 100, 1),
            'sentiment_trend': dashboard.sentiment_trend,
        }


class MeetingSummarizer:
    """Generate AI-powered meeting summaries"""
    
    def __init__(self):
        self.openai_available = bool(os.environ.get('OPENAI_API_KEY'))
    
    def generate_summary(self, recording) -> Dict[str, Any]:
        """Generate a comprehensive meeting summary"""
        
        from .models import TranscriptSegment
        from .advanced_models import MeetingSummary, MeetingActionItem
        
        if not hasattr(recording, 'transcript'):
            return {'error': 'No transcript available'}
        
        segments = TranscriptSegment.objects.filter(
            transcript=recording.transcript
        ).order_by('start_time')
        
        if not segments.exists():
            return {'error': 'No transcript segments found'}
        
        # Extract full text
        full_text = '\n'.join([
            f"{s.speaker}: {s.text}" for s in segments
        ])
        
        if self.openai_available:
            return self._generate_with_ai(recording, full_text, segments)
        else:
            return self._generate_with_rules(recording, full_text, segments)
    
    def _generate_with_ai(self, recording, full_text: str, 
                          segments) -> Dict[str, Any]:
        """Generate summary using AI"""
        
        try:
            import openai
            
            prompt = f"""Analyze this sales call transcript and provide:
1. An executive summary (2-3 sentences)
2. Key discussion points (bullet points)
3. Decisions made
4. Action items with assignees and deadlines
5. Follow-up recommendations
6. Open questions

Transcript:
{full_text[:8000]}  # Limit for token constraints
"""
            
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at summarizing sales meetings."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3,
            )
            
            ai_summary = response.choices[0].message.content
            
            # Parse AI response into structured format
            return self._parse_ai_summary(recording, ai_summary, segments)
            
        except Exception as e:
            return self._generate_with_rules(recording, full_text, segments)
    
    def _generate_with_rules(self, recording, full_text: str,
                             segments) -> Dict[str, Any]:
        """Generate summary using rule-based extraction"""
        
        from .advanced_models import MeetingSummary, MeetingActionItem
        
        # Extract key information
        key_points = self._extract_key_points(segments)
        action_items = self._extract_action_items(full_text, segments)
        topics = self._extract_topics(full_text)
        
        # Generate executive summary
        duration = recording.duration_seconds // 60
        participants = list(set(s.speaker for s in segments))
        
        executive_summary = (
            f"A {duration}-minute {recording.get_call_type_display()} call with "
            f"{len(participants)} participants. "
            f"Key topics included: {', '.join(topics[:3]) if topics else 'general discussion'}."
        )
        
        # Create summary record
        summary, _ = MeetingSummary.objects.update_or_create(
            recording=recording,
            defaults={
                'executive_summary': executive_summary,
                'key_points': key_points,
                'decisions': [],
                'action_items': action_items,
                'follow_up_recommendations': [
                    'Schedule a follow-up call to discuss next steps',
                    'Send meeting summary to all participants',
                ],
                'open_questions': self._extract_questions(full_text),
                'topics_discussed': topics,
                'next_steps': 'Review action items and schedule follow-up.',
                'confidence_score': 0.6,
            }
        )
        
        # Create action item records
        for item in action_items:
            MeetingActionItem.objects.create(
                summary=summary,
                title=item.get('title', 'Action item'),
                description=item.get('description', ''),
                mentioned_assignee=item.get('assignee', ''),
                mentioned_deadline=item.get('deadline', ''),
                priority=item.get('priority', 'medium'),
            )
        
        return {
            'summary_id': str(summary.id),
            'executive_summary': executive_summary,
            'key_points': key_points,
            'action_items': action_items,
            'topics': topics,
        }
    
    def _extract_key_points(self, segments) -> List[str]:
        """Extract key discussion points from segments"""
        
        key_points = []
        
        # Look for important patterns
        important_patterns = [
            r'the main (issue|problem|concern|point)',
            r'important to (note|mention|remember)',
            r'key (takeaway|point|thing)',
            r'to summarize',
            r'in conclusion',
            r'the bottom line',
        ]
        
        for segment in segments:
            text = segment.text.lower()
            for pattern in important_patterns:
                if re.search(pattern, text):
                    key_points.append(segment.text[:200])
                    break
        
        # If no patterns found, use longest segments
        if not key_points:
            sorted_segments = sorted(segments, key=lambda s: len(s.text), reverse=True)
            key_points = [s.text[:200] for s in sorted_segments[:5]]
        
        return key_points[:10]
    
    def _extract_action_items(self, full_text: str, 
                              segments) -> List[Dict[str, str]]:
        """Extract action items from transcript"""
        
        action_items = []
        
        # Patterns indicating action items
        action_patterns = [
            r"(i'll|I will|we'll|we will) (send|schedule|follow up|prepare|create|set up)",
            r"(let's|let me) (send|schedule|follow up|prepare|create|set up)",
            r"(can you|could you|would you) (send|schedule|follow up|prepare|create)",
            r"action item[s]?:?\s*(.+)",
            r"next step[s]?:?\s*(.+)",
            r"(need to|should) (send|schedule|follow up|prepare|create)",
        ]
        
        for segment in segments:
            text = segment.text
            for pattern in action_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    action_items.append({
                        'title': text[:100],
                        'description': text,
                        'assignee': segment.speaker,
                        'timestamp': float(segment.start_time),
                        'priority': 'medium',
                    })
                    break
        
        return action_items[:10]
    
    def _extract_topics(self, full_text: str) -> List[str]:
        """Extract discussed topics"""
        
        # Common business topics
        topic_keywords = {
            'pricing': ['price', 'cost', 'budget', 'investment'],
            'implementation': ['implement', 'deploy', 'rollout', 'setup'],
            'timeline': ['timeline', 'deadline', 'schedule', 'when'],
            'features': ['feature', 'capability', 'functionality'],
            'integration': ['integrate', 'connect', 'api'],
            'support': ['support', 'help', 'assistance'],
            'security': ['security', 'compliance', 'privacy'],
            'roi': ['roi', 'return', 'value', 'benefit'],
        }
        
        text_lower = full_text.lower()
        found_topics = []
        
        for topic, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                found_topics.append(topic.title())
        
        return found_topics
    
    def _extract_questions(self, full_text: str) -> List[str]:
        """Extract open questions from transcript"""
        
        # Find sentences ending with ?
        questions = re.findall(r'[^.!?]*\?', full_text)
        
        # Filter to meaningful questions
        meaningful_questions = [
            q.strip() for q in questions
            if len(q.strip()) > 20 and len(q.strip()) < 200
        ]
        
        return meaningful_questions[:5]
    
    def _parse_ai_summary(self, recording, ai_summary: str,
                          segments) -> Dict[str, Any]:
        """Parse AI-generated summary into structured format"""
        
        from .advanced_models import MeetingSummary
        
        # Simple parsing - in production would use more robust parsing
        lines = ai_summary.split('\n')
        
        executive_summary = ''
        key_points = []
        action_items = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if 'executive summary' in line.lower():
                current_section = 'executive'
            elif 'key' in line.lower() and 'point' in line.lower():
                current_section = 'key_points'
            elif 'action' in line.lower():
                current_section = 'actions'
            elif line.startswith('-') or line.startswith('•'):
                content = line.lstrip('-•').strip()
                if current_section == 'key_points':
                    key_points.append(content)
                elif current_section == 'actions':
                    action_items.append({'title': content})
            elif current_section == 'executive':
                executive_summary += line + ' '
        
        # Create summary record
        summary, _ = MeetingSummary.objects.update_or_create(
            recording=recording,
            defaults={
                'executive_summary': executive_summary.strip() or ai_summary[:500],
                'key_points': key_points,
                'action_items': action_items,
                'confidence_score': 0.85,
            }
        )
        
        return {
            'summary_id': str(summary.id),
            'executive_summary': executive_summary.strip() or ai_summary[:500],
            'key_points': key_points,
            'action_items': action_items,
            'ai_generated': True,
        }
    
    def send_summary_email(self, summary, recipients: List[str]) -> bool:
        """Send meeting summary via email"""
        
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        
        try:
            subject = f"Meeting Summary: {summary.recording.title}"
            
            # Build email content
            content = f"""
Meeting Summary
===============

{summary.executive_summary}

Key Points:
{chr(10).join('• ' + p for p in summary.key_points)}

Action Items:
{chr(10).join('• ' + a.get('title', str(a)) for a in summary.action_items)}

Next Steps:
{summary.next_steps}
"""
            
            send_mail(
                subject=subject,
                message=content,
                from_email='noreply@mycrm.com',
                recipient_list=recipients,
                fail_silently=False,
            )
            
            summary.email_sent = True
            summary.email_sent_at = timezone.now()
            summary.save()
            
            return True
        except Exception as e:
            return False


class KeyMomentDetector:
    """Detect key moments in call recordings"""
    
    def __init__(self):
        self.moment_patterns = {
            'objection': [
                r'too expensive|price is (high|too much)',
                r'not the right time|busy right now',
                r"don't need|not interested",
            ],
            'buying_signal': [
                r'how (much|long)|when can (we|you)',
                r'sounds good|that would work',
                r'what are the next steps',
            ],
            'competitor_mention': [
                r'(salesforce|hubspot|zoho|pipedrive|microsoft)',
                r'other (vendor|solution|option)',
                r'currently using|already have',
            ],
            'pricing_discussion': [
                r'(price|pricing|cost|budget|investment)',
                r'how much|what.+cost',
                r'discount|deal|offer',
            ],
            'decision_maker': [
                r'(ceo|cfo|cto|vp|director|manager)',
                r'decision maker|final say',
                r'need to (check|talk|discuss) with',
            ],
            'pain_point': [
                r'(problem|issue|challenge|pain|frustrat)',
                r'struggling with|difficult to',
                r'wish we could|if only',
            ],
        }
    
    def detect_moments(self, recording) -> List[Dict[str, Any]]:
        """Detect key moments in a recording"""
        
        from .models import TranscriptSegment
        from .advanced_models import KeyMoment
        
        if not hasattr(recording, 'transcript'):
            return []
        
        segments = TranscriptSegment.objects.filter(
            transcript=recording.transcript
        ).order_by('start_time')
        
        moments = []
        
        for segment in segments:
            text = segment.text.lower()
            
            for moment_type, patterns in self.moment_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, text):
                        # Determine importance based on moment type
                        importance = 'medium'
                        if moment_type in ['buying_signal', 'objection']:
                            importance = 'high'
                        elif moment_type in ['competitor_mention', 'decision_maker']:
                            importance = 'high'
                        
                        moment = KeyMoment.objects.create(
                            recording=recording,
                            moment_type=moment_type,
                            importance=importance,
                            timestamp_seconds=segment.start_time,
                            title=f"{moment_type.replace('_', ' ').title()} detected",
                            description=f"Detected pattern: {pattern}",
                            quote=segment.text,
                            speaker=segment.speaker,
                            speaker_type=segment.speaker_type,
                        )
                        
                        moments.append({
                            'id': str(moment.id),
                            'type': moment_type,
                            'timestamp': float(segment.start_time),
                            'importance': importance,
                            'quote': segment.text[:200],
                        })
                        
                        break  # Only one moment type per segment
        
        return moments
