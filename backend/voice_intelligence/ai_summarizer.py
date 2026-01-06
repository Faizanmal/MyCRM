"""
AI Summarizer
AI-powered conversation summarization and analysis
"""

import json
import logging
from typing import Any

import openai
from django.conf import settings

logger = logging.getLogger(__name__)


class ConversationSummarizer:
    """AI-powered conversation summarization"""

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_summary(
        self,
        transcript: str,
        summary_type: str = 'executive',
        context: dict | None = None
    ) -> dict[str, Any]:
        """Generate a summary of the conversation"""
        try:
            prompt = self._build_summary_prompt(transcript, summary_type, context)

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert at summarizing business conversations.
Your summaries are concise, actionable, and capture all important details.
Focus on business outcomes, decisions, and next steps."""
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            return {
                'success': True,
                'summary_text': result.get('summary', ''),
                'key_points': result.get('key_points', []),
                'topics': result.get('topics', []),
                'decisions': result.get('decisions', []),
                'questions_asked': result.get('questions_asked', []),
                'questions_unanswered': result.get('questions_unanswered', []),
                'next_steps': result.get('next_steps', []),
                'keywords': result.get('keywords', []),
                'entities_mentioned': result.get('entities', {})
            }

        except Exception as e:
            logger.error(f"Summary generation error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _build_summary_prompt(
        self,
        transcript: str,
        summary_type: str,
        context: dict | None
    ) -> str:
        """Build the appropriate prompt based on summary type"""

        context_str = ""
        if context:
            if context.get('contact_name'):
                context_str += f"\nContact: {context['contact_name']}"
            if context.get('company'):
                context_str += f"\nCompany: {context['company']}"
            if context.get('opportunity'):
                context_str += f"\nOpportunity: {context['opportunity']}"

        if summary_type == 'executive':
            return f"""Create an executive summary of this business conversation.
{context_str}

Transcript:
{transcript[:15000]}

Return JSON with:
{{
    "summary": "2-3 paragraph executive summary",
    "key_points": ["list of 3-5 main points"],
    "topics": ["main topics discussed"],
    "decisions": ["any decisions made"],
    "questions_asked": ["important questions raised"],
    "questions_unanswered": ["questions that weren't answered"],
    "next_steps": ["agreed next steps"],
    "keywords": ["important keywords/terms"],
    "entities": {{
        "people": ["names mentioned"],
        "companies": ["companies mentioned"],
        "products": ["products mentioned"],
        "dates": ["dates/deadlines mentioned"]
    }}
}}"""

        elif summary_type == 'bullet_points':
            return f"""Summarize this conversation as bullet points.
{context_str}

Transcript:
{transcript[:15000]}

Return JSON with:
{{
    "summary": "• Bullet point 1\\n• Bullet point 2\\n• etc",
    "key_points": ["each key point as separate item"],
    "topics": ["topics covered"],
    "decisions": ["decisions made"],
    "questions_asked": [],
    "questions_unanswered": [],
    "next_steps": ["action items"],
    "keywords": ["keywords"],
    "entities": {{"people": [], "companies": [], "products": [], "dates": []}}
}}"""

        elif summary_type == 'action_items':
            return f"""Extract all action items from this conversation.
{context_str}

Transcript:
{transcript[:15000]}

Return JSON with:
{{
    "summary": "Brief overview of commitments made",
    "key_points": ["each commitment as a point"],
    "topics": [],
    "decisions": ["decisions that led to action items"],
    "questions_asked": [],
    "questions_unanswered": [],
    "next_steps": ["detailed action items with owners if mentioned"],
    "keywords": [],
    "entities": {{"people": ["people assigned tasks"], "companies": [], "products": [], "dates": ["due dates mentioned"]}}
}}"""

        else:  # detailed
            return f"""Create a detailed summary of this conversation.
{context_str}

Transcript:
{transcript[:15000]}

Return JSON with:
{{
    "summary": "Comprehensive 3-5 paragraph summary covering all important points",
    "key_points": ["list of 5-10 key points"],
    "topics": ["all topics discussed with brief descriptions"],
    "decisions": ["all decisions made"],
    "questions_asked": ["all questions raised"],
    "questions_unanswered": ["questions without clear answers"],
    "next_steps": ["all next steps and action items"],
    "keywords": ["important keywords and industry terms"],
    "entities": {{
        "people": ["all people mentioned"],
        "companies": ["all companies mentioned"],
        "products": ["all products/services mentioned"],
        "dates": ["all dates and deadlines"]
    }}
}}"""


class ActionItemExtractor:
    """Extract action items from conversations"""

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def extract_action_items(
        self,
        transcript: str,
        speaker_labels: dict | None = None
    ) -> list[dict[str, Any]]:
        """Extract action items from transcript"""
        try:
            prompt = f"""Analyze this conversation and extract all action items, tasks, and commitments.

Transcript:
{transcript[:15000]}

For each action item, identify:
1. What needs to be done
2. Who is responsible (if mentioned)
3. Due date/timeline (if mentioned)
4. Priority (infer from context: critical, high, medium, low)
5. The exact quote where this was mentioned

Return JSON:
{{
    "action_items": [
        {{
            "title": "Brief action item title",
            "description": "Detailed description",
            "assigned_to_name": "Person's name or 'Unassigned'",
            "due_date_mentioned": "Date string or null",
            "priority": "high/medium/low/critical",
            "context_quote": "Exact quote from transcript",
            "speaker": "Who mentioned/committed to this",
            "confidence": 0.9
        }}
    ]
}}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert at identifying action items in business conversations.
Look for explicit commitments, tasks, and follow-ups.
Distinguish between suggestions and firm commitments."""
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result.get('action_items', [])

        except Exception as e:
            logger.error(f"Action item extraction error: {str(e)}")
            return []


class SentimentAnalyzer:
    """Analyze sentiment and emotions in conversations"""

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def analyze_sentiment(
        self,
        transcript: str,
        segments: list[dict] | None = None
    ) -> dict[str, Any]:
        """Analyze overall and segment-level sentiment"""
        try:
            # For segment-level analysis, we'll sample key segments
            if segments:
                # Sample up to 20 segments evenly distributed
                sample_size = min(20, len(segments))
                step = max(1, len(segments) // sample_size)
                sampled = segments[::step][:sample_size]

                segment_texts = "\n".join([
                    f"[{s.get('start', 0):.1f}s] {s.get('text', '')}"
                    for s in sampled
                ])
            else:
                segment_texts = transcript[:5000]

            prompt = f"""Analyze the sentiment and emotions in this conversation.

Transcript/Segments:
{segment_texts}

Analyze:
1. Overall sentiment (-1 to 1 scale)
2. Sentiment progression over time
3. Emotions detected (with confidence scores)
4. Key positive and negative moments
5. Engagement level

Return JSON:
{{
    "overall_sentiment": "positive/negative/neutral/very_positive/very_negative",
    "overall_score": 0.5,
    "sentiment_timeline": [
        {{"timestamp": 0, "score": 0.0, "label": "neutral"}},
        {{"timestamp": 60, "score": 0.3, "label": "positive"}}
    ],
    "emotions_detected": {{
        "enthusiasm": 0.7,
        "concern": 0.3,
        "frustration": 0.1,
        "interest": 0.8,
        "confidence": 0.6
    }},
    "dominant_emotion": "interest",
    "positive_moments": [
        {{"timestamp": 120, "description": "Customer expressed interest in features"}}
    ],
    "negative_moments": [
        {{"timestamp": 240, "description": "Pricing objection raised"}}
    ],
    "engagement_score": 0.75,
    "tone_analysis": {{
        "formality": "professional",
        "warmth": "friendly",
        "assertiveness": "moderate"
    }}
}}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert at analyzing emotions and sentiment in business conversations.
Focus on business-relevant emotional cues and engagement signals."""
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return {
                'overall_sentiment': 'neutral',
                'overall_score': 0.0,
                'error': str(e)
            }


class KeyMomentDetector:
    """Detect key moments in conversations"""

    MOMENT_TYPES = [
        'objection', 'agreement', 'question', 'commitment',
        'concern', 'interest', 'pricing', 'competitor', 'next_step', 'highlight'
    ]

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def detect_key_moments(
        self,
        transcript: str,
        segments: list[dict]
    ) -> list[dict[str, Any]]:
        """Detect key moments in the conversation"""
        try:
            # Build transcript with timestamps
            timestamped_transcript = "\n".join([
                f"[{s.get('start', 0):.1f}s - {s.get('end', 0):.1f}s] {s.get('speaker', 'Speaker')}: {s.get('text', '')}"
                for s in segments
            ])

            prompt = f"""Identify key moments in this sales/business conversation.

Transcript:
{timestamped_transcript[:12000]}

Key moment types to look for:
- objection: Customer raises concern or pushback
- agreement: Explicit agreement or buy-in
- question: Important questions asked
- commitment: Commitment to action or next step
- concern: Expression of worry or hesitation
- interest: Strong interest shown
- pricing: Pricing discussion
- competitor: Competitor mention
- next_step: Discussion of next steps
- highlight: Notable positive moment

Return JSON:
{{
    "key_moments": [
        {{
            "moment_type": "objection",
            "start_timestamp": 120,
            "end_timestamp": 145,
            "transcript_excerpt": "Exact quote from transcript",
            "speaker": "Customer",
            "summary": "Brief description of the moment",
            "importance_score": 0.8
        }}
    ]
}}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert sales coach analyzing conversations.
Identify moments that are significant for sales outcomes and coaching."""
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result.get('key_moments', [])

        except Exception as e:
            logger.error(f"Key moment detection error: {str(e)}")
            return []


class CallScorer:
    """Score sales calls based on best practices"""

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def score_call(
        self,
        transcript: str,
        call_type: str = 'sales'
    ) -> dict[str, Any]:
        """Score a sales call"""
        try:
            prompt = f"""Score this {call_type} call based on best practices.

Transcript:
{transcript[:15000]}

Evaluate and score (0-100) these areas:
1. Opening - Did they establish rapport and set agenda?
2. Discovery - Did they ask good discovery questions?
3. Presentation - Did they present solutions effectively?
4. Objection Handling - Did they address concerns well?
5. Closing - Did they establish clear next steps?

Also analyze:
- Talk to listen ratio (ideal is 40-60 rep to 60-40 customer)
- Question count
- Filler words used
- Best practices followed

Return JSON:
{{
    "overall_score": 75,
    "opening_score": 80,
    "discovery_score": 70,
    "presentation_score": 75,
    "objection_handling_score": 65,
    "closing_score": 85,
    "talk_to_listen_ratio": 0.45,
    "question_count": 12,
    "filler_words_used": ["um", "uh", "like"],
    "filler_word_count": 8,
    "mentioned_value_prop": true,
    "asked_discovery_questions": true,
    "handled_objections": true,
    "established_next_steps": true,
    "personalized_conversation": true,
    "coaching_tips": [
        "Try to ask more open-ended questions",
        "Reduce use of filler words"
    ],
    "areas_for_improvement": [
        "Objection handling - consider acknowledging concerns before responding"
    ],
    "strengths": [
        "Strong opening that established rapport",
        "Clear next steps established"
    ]
}}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert sales coach with years of experience training top performers.
Score calls fairly but constructively, providing actionable feedback."""
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"Call scoring error: {str(e)}")
            return {
                'overall_score': 0,
                'error': str(e)
            }


class TopicExtractor:
    """Extract and categorize topics from conversations"""

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def extract_topics(
        self,
        transcript: str,
        segments: list[dict]
    ) -> dict[str, Any]:
        """Extract topics with time ranges"""
        try:
            timestamped_transcript = "\n".join([
                f"[{s.get('start', 0):.1f}s] {s.get('text', '')}"
                for s in segments
            ])

            prompt = f"""Identify distinct topics discussed in this conversation with their time ranges.

Transcript:
{timestamped_transcript[:12000]}

Return JSON:
{{
    "topics": [
        {{
            "name": "Product Demo",
            "description": "Discussion of product features and capabilities",
            "start_timestamp": 60,
            "end_timestamp": 300,
            "subtopics": ["feature A", "integration"]
        }}
    ],
    "topic_transitions": [
        {{"from": "Introduction", "to": "Product Demo", "timestamp": 60}}
    ]
}}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"Topic extraction error: {str(e)}")
            return {'topics': [], 'error': str(e)}


class VoiceNoteProcessor:
    """Process quick voice notes"""

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def process_voice_note(
        self,
        transcript: str,
        context: dict | None = None
    ) -> dict[str, Any]:
        """Process a voice note and extract key information"""
        try:
            context_str = ""
            if context:
                context_str = f"\nContext: Related to {context.get('contact_name', 'contact')} at {context.get('company', 'company')}"

            prompt = f"""Process this voice note and extract key information.
{context_str}

Voice note transcript:
{transcript}

Return JSON:
{{
    "ai_title": "Brief descriptive title for the note",
    "ai_summary": "1-2 sentence summary",
    "action_items": [
        {{"task": "Task description", "priority": "high/medium/low"}}
    ],
    "tags": ["relevant", "tags"],
    "sentiment": "positive/negative/neutral",
    "follow_up_needed": true/false,
    "follow_up_date_mentioned": "date string or null"
}}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"Voice note processing error: {str(e)}")
            return {
                'ai_title': 'Voice Note',
                'ai_summary': transcript[:200],
                'error': str(e)
            }
