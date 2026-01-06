"""
AI Content Generator for Email Sequences
Generates personalized email content using AI
"""

import json
import re
from datetime import datetime, timedelta
from typing import Any

from django.conf import settings
from django.utils import timezone


class AIEmailContentGenerator:
    """AI-powered email content generation"""

    EMAIL_TEMPLATES = {
        'outreach': {
            'intro': "Generate a personalized outreach email introducing {company} to {contact_name}",
            'value_prop': "Generate an email highlighting key value propositions for {industry} companies",
            'case_study': "Generate an email sharing relevant case study for {contact_role} at {company}",
        },
        'follow_up': {
            'first': "Generate a friendly first follow-up email after initial outreach",
            'second': "Generate a value-added second follow-up email",
            'final': "Generate a breakup/final attempt email",
        },
        'nurture': {
            'educational': "Generate an educational content email about {topic}",
            'product_update': "Generate a product update announcement email",
            'event_invite': "Generate an event invitation email for {event_name}",
        },
        'deal': {
            'proposal_follow': "Generate a proposal follow-up email",
            'negotiation': "Generate a negotiation/pricing discussion email",
            'closing': "Generate a closing/decision-time email",
        }
    }

    TONES = ['professional', 'friendly', 'casual', 'urgent', 'empathetic', 'authoritative']

    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)

    def generate_email(
        self,
        template_type: str,
        template_subtype: str,
        context: dict[str, Any],
        tone: str = 'professional',
        length: str = 'medium',
        personalization_data: dict | None = None
    ) -> dict[str, str]:
        """
        Generate personalized email content

        Args:
            template_type: outreach, follow_up, nurture, deal
            template_subtype: Specific template variant
            context: Context data for personalization
            tone: Email tone
            length: short, medium, long
            personalization_data: Contact-specific data

        Returns:
            Dict with subject, body_html, body_text, preview_text
        """
        prompt = self._build_prompt(
            template_type, template_subtype, context, tone, length, personalization_data
        )

        # For now, return a template-based response
        # In production, this would call OpenAI/Claude API
        generated = self._generate_with_ai(prompt, context)

        return {
            'subject': generated['subject'],
            'preview_text': generated['preview_text'],
            'body_html': generated['body_html'],
            'body_text': generated['body_text'],
            'ai_prompt': prompt,
            'tokens_used': generated.get('tokens_used', 0)
        }

    def generate_subject_variants(
        self,
        base_context: dict[str, Any],
        num_variants: int = 3
    ) -> list[dict[str, str]]:
        """Generate multiple subject line variants for A/B testing"""
        variants = []

        styles = ['question', 'curiosity', 'benefit', 'personalized', 'urgency']

        for i in range(min(num_variants, len(styles))):
            variant = self._generate_subject_variant(base_context, styles[i])
            variants.append({
                'variant_name': chr(65 + i),  # A, B, C...
                'subject': variant['subject'],
                'style': styles[i],
                'preview_text': variant.get('preview_text', '')
            })

        return variants

    def personalize_content(
        self,
        content: str,
        personalization_data: dict[str, Any],
        tokens: list[str]
    ) -> str:
        """Replace personalization tokens with actual values"""
        result = content

        for token in tokens:
            token_key = token.strip('{}')
            if token_key in personalization_data:
                value = personalization_data[token_key]
                if value:
                    result = result.replace(f'{{{token_key}}}', str(value))
                else:
                    # Use fallback
                    result = result.replace(f'{{{token_key}}}', self._get_fallback(token_key))

        return result

    def generate_dynamic_content(
        self,
        content_type: str,
        context: dict[str, Any]
    ) -> str:
        """Generate dynamic content blocks based on context"""
        generators = {
            'recent_interaction_summary': self._generate_interaction_summary,
            'personalized_recommendation': self._generate_recommendation,
            'industry_insight': self._generate_industry_insight,
            'social_proof': self._generate_social_proof,
            'call_to_action': self._generate_cta,
        }

        generator = generators.get(content_type)
        if generator:
            return generator(context)
        return ''

    def analyze_email_quality(self, subject: str, body: str) -> dict[str, Any]:
        """Analyze email content quality and provide suggestions"""
        analysis = {
            'overall_score': 0,
            'spam_score': 0,
            'readability_score': 0,
            'personalization_score': 0,
            'engagement_prediction': 0,
            'suggestions': [],
            'spam_triggers': [],
            'sentiment': 'neutral'
        }

        # Subject line analysis
        subject_analysis = self._analyze_subject(subject)
        analysis['subject_analysis'] = subject_analysis

        # Body analysis
        body_analysis = self._analyze_body(body)
        analysis['body_analysis'] = body_analysis

        # Calculate overall scores
        analysis['readability_score'] = body_analysis['readability']
        analysis['personalization_score'] = body_analysis['personalization']
        analysis['spam_score'] = self._calculate_spam_score(subject, body)
        analysis['spam_triggers'] = self._find_spam_triggers(subject, body)

        # Engagement prediction based on historical data patterns
        analysis['engagement_prediction'] = self._predict_engagement(subject, body)

        # Overall quality score
        analysis['overall_score'] = round(
            (subject_analysis['score'] * 0.3) +
            (body_analysis['score'] * 0.4) +
            ((100 - analysis['spam_score']) * 0.3),
            1
        )

        # Generate suggestions
        analysis['suggestions'] = self._generate_suggestions(analysis)

        return analysis

    def optimize_send_time(
        self,
        contact_id: int,
        contact_data: dict[str, Any],
        historical_data: list[dict] | None = None
    ) -> dict[str, Any]:
        """Predict optimal send time for a contact"""
        # Default optimal times by day
        default_optimal = {
            'monday': {'hour': 10, 'confidence': 0.7},
            'tuesday': {'hour': 10, 'confidence': 0.8},
            'wednesday': {'hour': 10, 'confidence': 0.8},
            'thursday': {'hour': 10, 'confidence': 0.75},
            'friday': {'hour': 9, 'confidence': 0.65},
            'saturday': {'hour': 10, 'confidence': 0.3},
            'sunday': {'hour': 10, 'confidence': 0.3},
        }

        # Adjust based on timezone
        timezone_offset = contact_data.get('timezone_offset', 0)

        # Adjust based on historical engagement
        if historical_data:
            optimal = self._calculate_optimal_from_history(historical_data)
        else:
            optimal = default_optimal

        # Find next optimal send window
        now = timezone.now()
        next_optimal = self._find_next_optimal_window(now, optimal, timezone_offset)

        return {
            'recommended_time': next_optimal,
            'confidence': optimal.get(now.strftime('%A').lower(), {}).get('confidence', 0.5),
            'timezone': contact_data.get('timezone', 'UTC'),
            'reasoning': f"Based on {'historical engagement patterns' if historical_data else 'industry best practices'}"
        }

    def _build_prompt(
        self,
        template_type: str,
        template_subtype: str,
        context: dict[str, Any],
        tone: str,
        length: str,
        personalization_data: dict | None
    ) -> str:
        """Build AI prompt for email generation"""
        base_prompt = self.EMAIL_TEMPLATES.get(template_type, {}).get(template_subtype, '')

        # Format base prompt with context
        try:
            formatted_prompt = base_prompt.format(**context)
        except KeyError:
            formatted_prompt = base_prompt

        length_guide = {
            'short': '2-3 short paragraphs, under 100 words',
            'medium': '3-4 paragraphs, 100-200 words',
            'long': '4-5 paragraphs, 200-300 words'
        }

        full_prompt = f"""
        Generate a {tone} sales email.

        Context: {formatted_prompt}

        Requirements:
        - Tone: {tone}
        - Length: {length_guide.get(length, length_guide['medium'])}
        - Include a clear call-to-action
        - Use personalization where appropriate
        - Avoid spam trigger words
        - Write for easy scanning (short paragraphs, bullet points if needed)

        Contact Information:
        {json.dumps(personalization_data or {}, indent=2)}

        Additional Context:
        {json.dumps(context, indent=2)}

        Generate:
        1. Subject line (compelling, under 60 characters)
        2. Preview text (under 100 characters)
        3. Email body (HTML format)
        4. Plain text version
        """

        return full_prompt

    def _generate_with_ai(self, prompt: str, context: dict[str, Any]) -> dict[str, str]:
        """
        Generate email content using AI
        In production, this would call OpenAI/Claude API
        """
        # Template-based generation for demonstration
        contact_name = context.get('contact_name', context.get('first_name', 'there'))
        company = context.get('company', context.get('company_name', 'your company'))
        sender_name = context.get('sender_name', 'John')
        sender_company = context.get('sender_company', 'Our Company')

        subject = f"Quick question about {company}'s growth strategy"
        preview_text = f"Hi {contact_name}, I noticed something interesting..."

        body_html = f"""
        <p>Hi {contact_name},</p>

        <p>I've been following {company}'s recent developments and noticed you're expanding into new markets.
        Congratulations on the growth!</p>

        <p>I'm reaching out because many companies at your stage face challenges with:</p>
        <ul>
            <li>Scaling customer relationships efficiently</li>
            <li>Maintaining personalized communication at scale</li>
            <li>Tracking deal progress across growing teams</li>
        </ul>

        <p>We've helped companies like {company} increase their sales efficiency by 40% using our AI-powered CRM platform.</p>

        <p>Would you be open to a 15-minute call this week to explore if this could help {company}?</p>

        <p>Best regards,<br>
        {sender_name}<br>
        {sender_company}</p>
        """

        body_text = f"""
        Hi {contact_name},

        I've been following {company}'s recent developments and noticed you're expanding into new markets. Congratulations on the growth!

        I'm reaching out because many companies at your stage face challenges with:
        - Scaling customer relationships efficiently
        - Maintaining personalized communication at scale
        - Tracking deal progress across growing teams

        We've helped companies like {company} increase their sales efficiency by 40% using our AI-powered CRM platform.

        Would you be open to a 15-minute call this week to explore if this could help {company}?

        Best regards,
        {sender_name}
        {sender_company}
        """

        return {
            'subject': subject,
            'preview_text': preview_text,
            'body_html': body_html,
            'body_text': body_text.strip(),
            'tokens_used': len(prompt.split()) + len(body_html.split())
        }

    def _generate_subject_variant(self, context: dict[str, Any], style: str) -> dict[str, str]:
        """Generate subject line variant based on style"""
        company = context.get('company', 'your company')
        name = context.get('first_name', 'there')

        variants = {
            'question': {
                'subject': f"{name}, is {company} ready for the next level?",
                'preview_text': "I have a quick question about your growth strategy"
            },
            'curiosity': {
                'subject': f"Something interesting about {company}...",
                'preview_text': "I noticed this while researching your company"
            },
            'benefit': {
                'subject': f"40% more efficient sales for {company}",
                'preview_text': "Here's how similar companies achieved this"
            },
            'personalized': {
                'subject': f"{name} - quick idea for {company}",
                'preview_text': "Based on what I've seen, this could help"
            },
            'urgency': {
                'subject': f"Time-sensitive opportunity for {company}",
                'preview_text': "Don't miss this window"
            }
        }

        return variants.get(style, variants['benefit'])

    def _get_fallback(self, token_key: str) -> str:
        """Get fallback value for empty tokens"""
        fallbacks = {
            'first_name': 'there',
            'last_name': '',
            'company': 'your company',
            'company_name': 'your company',
            'job_title': 'professional',
            'industry': 'your industry',
        }
        return fallbacks.get(token_key, '')

    def _generate_interaction_summary(self, context: dict[str, Any]) -> str:
        """Generate summary of recent interactions"""
        interactions = context.get('recent_interactions', [])
        if not interactions:
            return "We haven't connected in a while."

        last = interactions[0]
        return f"Following up on our {last.get('type', 'conversation')} from {last.get('date', 'recently')}..."

    def _generate_recommendation(self, context: dict[str, Any]) -> str:
        """Generate personalized recommendation"""
        industry = context.get('industry', '')
        company_size = context.get('company_size', '')

        if industry and company_size:
            return f"Based on our work with {company_size} companies in {industry}, I recommend starting with..."
        return "Based on your profile, I recommend..."

    def _generate_industry_insight(self, context: dict[str, Any]) -> str:
        """Generate industry-specific insight"""
        industry = context.get('industry', 'technology')
        return f"Recent trends in {industry} show that companies are increasingly focused on..."

    def _generate_social_proof(self, context: dict[str, Any]) -> str:
        """Generate social proof content"""
        context.get('industry', '')
        return "Companies like yours have seen an average of 35% improvement in..."

    def _generate_cta(self, context: dict[str, Any]) -> str:
        """Generate call-to-action"""
        stage = context.get('deal_stage', 'discovery')

        ctas = {
            'discovery': "Would you be open to a 15-minute discovery call?",
            'proposal': "Can we schedule time to walk through the proposal?",
            'negotiation': "Let's find a time to discuss the details.",
            'closing': "Ready to move forward? Let me know and I'll send over the paperwork."
        }

        return ctas.get(stage, ctas['discovery'])

    def _analyze_subject(self, subject: str) -> dict[str, Any]:
        """Analyze subject line quality"""
        analysis = {
            'length': len(subject),
            'word_count': len(subject.split()),
            'has_personalization': '{' in subject,
            'has_emoji': bool(re.search(r'[\U0001F600-\U0001F64F]', subject)),
            'is_question': subject.strip().endswith('?'),
            'has_numbers': bool(re.search(r'\d', subject)),
            'score': 70  # Base score
        }

        # Adjust score based on factors
        if 30 <= analysis['length'] <= 50:
            analysis['score'] += 10
        elif analysis['length'] > 70:
            analysis['score'] -= 15

        if analysis['has_personalization']:
            analysis['score'] += 10

        if analysis['is_question']:
            analysis['score'] += 5

        if analysis['word_count'] <= 7:
            analysis['score'] += 5

        return analysis

    def _analyze_body(self, body: str) -> dict[str, Any]:
        """Analyze email body quality"""
        # Remove HTML tags for analysis
        clean_text = re.sub(r'<[^>]+>', '', body)

        word_count = len(clean_text.split())
        sentences = re.split(r'[.!?]+', clean_text)
        avg_sentence_length = word_count / max(len(sentences), 1)

        analysis = {
            'word_count': word_count,
            'sentence_count': len(sentences),
            'avg_sentence_length': round(avg_sentence_length, 1),
            'has_bullet_points': '<li>' in body or '•' in body,
            'has_cta': any(cta in body.lower() for cta in ['schedule', 'call', 'book', 'reply', 'click']),
            'paragraph_count': body.count('<p>') or body.count('\n\n') + 1,
            'readability': 70,  # Base readability score
            'personalization': 50,  # Base personalization score
            'score': 70  # Base score
        }

        # Readability adjustments
        if avg_sentence_length <= 20:
            analysis['readability'] += 15
        elif avg_sentence_length > 30:
            analysis['readability'] -= 20

        if analysis['has_bullet_points']:
            analysis['readability'] += 10

        # Personalization check
        personalization_tokens = re.findall(r'\{[^}]+\}', body)
        analysis['personalization_tokens'] = len(personalization_tokens)
        analysis['personalization'] += len(personalization_tokens) * 10

        # Score adjustments
        if 100 <= word_count <= 250:
            analysis['score'] += 15
        elif word_count < 50 or word_count > 400:
            analysis['score'] -= 10

        if analysis['has_cta']:
            analysis['score'] += 15

        return analysis

    def _calculate_spam_score(self, subject: str, body: str) -> int:
        """Calculate spam likelihood score (0-100)"""
        spam_score = 0
        (subject + ' ' + body).lower()

        # Check for spam triggers
        spam_triggers = self._find_spam_triggers(subject, body)
        spam_score += len(spam_triggers) * 10

        # Check for all caps
        if sum(1 for c in subject if c.isupper()) / max(len(subject), 1) > 0.3:
            spam_score += 15

        # Check for excessive punctuation
        if subject.count('!') > 1 or subject.count('?') > 2:
            spam_score += 10

        return min(spam_score, 100)

    def _find_spam_triggers(self, subject: str, body: str) -> list[str]:
        """Find spam trigger words"""
        text = (subject + ' ' + body).lower()

        spam_words = [
            'free', 'guarantee', 'limited time', 'act now', 'urgent',
            'winner', 'congratulations', 'click here', 'unsubscribe',
            'buy now', 'order now', 'special offer', 'exclusive deal',
            'make money', 'earn extra', 'no obligation', 'risk-free'
        ]

        found = []
        for word in spam_words:
            if word in text:
                found.append(word)

        return found

    def _predict_engagement(self, subject: str, body: str) -> float:
        """Predict engagement likelihood (0-100)"""
        subject_analysis = self._analyze_subject(subject)
        body_analysis = self._analyze_body(body)
        spam_score = self._calculate_spam_score(subject, body)

        # Base prediction
        prediction = 50.0

        # Subject factors
        prediction += (subject_analysis['score'] - 70) * 0.3

        # Body factors
        prediction += (body_analysis['score'] - 70) * 0.4

        # Spam penalty
        prediction -= spam_score * 0.3

        # CTA bonus
        if body_analysis['has_cta']:
            prediction += 10

        return round(max(0, min(100, prediction)), 1)

    def _generate_suggestions(self, analysis: dict[str, Any]) -> list[str]:
        """Generate improvement suggestions"""
        suggestions = []

        subject_analysis = analysis.get('subject_analysis', {})
        body_analysis = analysis.get('body_analysis', {})

        if subject_analysis.get('length', 0) > 60:
            suggestions.append("Shorten your subject line to under 60 characters for better mobile display")

        if not subject_analysis.get('has_personalization'):
            suggestions.append("Add personalization (like first name) to increase open rates")

        if body_analysis.get('word_count', 0) > 300:
            suggestions.append("Consider shortening your email - shorter emails typically get better responses")

        if not body_analysis.get('has_bullet_points') and body_analysis.get('word_count', 0) > 150:
            suggestions.append("Add bullet points to improve readability and scannability")

        if not body_analysis.get('has_cta'):
            suggestions.append("Add a clear call-to-action to guide the recipient")

        if analysis.get('spam_triggers'):
            suggestions.append(f"Remove spam trigger words: {', '.join(analysis['spam_triggers'][:3])}")

        return suggestions

    def _calculate_optimal_from_history(self, historical_data: list[dict]) -> dict:
        """Calculate optimal send times from historical engagement"""
        # Analyze when emails were opened/clicked
        engagement_by_hour = {}

        for record in historical_data:
            if record.get('opened'):
                hour = record.get('hour', 10)
                day = record.get('day', 'tuesday')
                key = f"{day}_{hour}"
                engagement_by_hour[key] = engagement_by_hour.get(key, 0) + 1

        # Find best times per day
        optimal = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        for day in days:
            best_hour = 10
            best_count = 0

            for hour in range(6, 22):
                key = f"{day}_{hour}"
                count = engagement_by_hour.get(key, 0)
                if count > best_count:
                    best_count = count
                    best_hour = hour

            optimal[day] = {
                'hour': best_hour,
                'confidence': min(0.5 + (best_count * 0.1), 0.95)
            }

        return optimal

    def _find_next_optimal_window(
        self,
        now: datetime,
        optimal: dict,
        timezone_offset: int
    ) -> datetime:
        """Find next optimal send window"""
        for days_ahead in range(7):
            check_date = now + timedelta(days=days_ahead)
            day_name = check_date.strftime('%A').lower()

            day_optimal = optimal.get(day_name, {'hour': 10})
            optimal_hour = day_optimal['hour']

            # Adjust for timezone
            local_hour = optimal_hour - timezone_offset

            candidate = check_date.replace(
                hour=local_hour,
                minute=0,
                second=0,
                microsecond=0
            )

            if candidate > now:
                return candidate

        # Fallback to tomorrow 10 AM
        return (now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
