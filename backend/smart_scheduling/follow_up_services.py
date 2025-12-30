"""
Automated Meeting Follow-up Services
AI-powered follow-up sequences after meetings
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction, models
from django.contrib.auth import get_user_model
from django.conf import settings

from .follow_up_models import MeetingFollowUp, FollowUpSequence, MeetingOutcome

logger = logging.getLogger(__name__)
User = get_user_model()


class FollowUpService:
    """Service for managing automated follow-ups"""
    
    def __init__(self, user):
        self.user = user
    
    @transaction.atomic
    def schedule_follow_ups_for_meeting(
        self,
        meeting_id: str,
        sequence_id: Optional[str] = None
    ) -> List[Dict]:
        """Schedule follow-up sequence for a meeting"""
        from .models import Meeting
        
        try:
            meeting = Meeting.objects.get(id=meeting_id, host=self.user)
        except Meeting.DoesNotExist:
            raise ValueError(f"Meeting {meeting_id} not found")
        
        # Get sequence
        if sequence_id:
            try:
                sequence = FollowUpSequence.objects.get(id=sequence_id, user=self.user)
            except FollowUpSequence.DoesNotExist:
                raise ValueError(f"Sequence {sequence_id} not found")
        else:
            # Find applicable sequence
            sequence = FollowUpSequence.objects.filter(
                user=self.user,
                is_active=True
            ).filter(
                models.Q(apply_to_all=True) |
                models.Q(meeting_types=meeting.meeting_type)
            ).first()
        
        if not sequence:
            # Use default follow-up
            return self._create_default_follow_ups(meeting)
        
        return self._apply_sequence(meeting, sequence)
    
    def _create_default_follow_ups(self, meeting) -> List[Dict]:
        """Create default follow-up sequence"""
        follow_ups = []
        
        # Thank you email - 1 hour after meeting
        thank_you = MeetingFollowUp.objects.create(
            meeting=meeting,
            follow_up_type='thank_you',
            scheduled_at=meeting.end_time + timedelta(hours=1),
            delay_hours=1,
            subject=f"Great connecting today - {meeting.meeting_type.name}",
            body=self._generate_thank_you_email(meeting),
            is_ai_generated=True
        )
        follow_ups.append(self._serialize_follow_up(thank_you))
        
        # Summary email - 2 hours after meeting
        summary = MeetingFollowUp.objects.create(
            meeting=meeting,
            follow_up_type='summary',
            scheduled_at=meeting.end_time + timedelta(hours=2),
            delay_hours=2,
            subject=f"Meeting Summary - {meeting.meeting_type.name}",
            body="[AI will generate summary based on meeting notes]",
            is_ai_generated=True
        )
        follow_ups.append(self._serialize_follow_up(summary))
        
        return follow_ups
    
    def _apply_sequence(self, meeting, sequence: FollowUpSequence) -> List[Dict]:
        """Apply a follow-up sequence to a meeting"""
        follow_ups = []
        
        for step in sequence.steps:
            delay_hours = step.get('delay_hours', 0) + step.get('delay_days', 0) * 24
            scheduled_at = meeting.end_time + timedelta(hours=delay_hours)
            
            # Skip if scheduled in the past
            if scheduled_at <= timezone.now():
                scheduled_at = timezone.now() + timedelta(minutes=5)
            
            # Generate content
            subject, body = self._generate_step_content(meeting, step, sequence)
            
            follow_up = MeetingFollowUp.objects.create(
                meeting=meeting,
                follow_up_type=step.get('type', 'custom'),
                scheduled_at=scheduled_at,
                delay_hours=delay_hours,
                subject=subject,
                body=body,
                is_ai_generated=sequence.use_ai_personalization,
                personalization_context={
                    'sequence_id': str(sequence.id),
                    'step_index': sequence.steps.index(step),
                    'condition': step.get('condition')
                }
            )
            follow_ups.append(self._serialize_follow_up(follow_up))
        
        # Update sequence usage
        sequence.times_used += 1
        sequence.save(update_fields=['times_used'])
        
        return follow_ups
    
    def _generate_step_content(
        self,
        meeting,
        step: Dict,
        sequence: FollowUpSequence
    ) -> tuple:
        """Generate content for a sequence step"""
        
        # Use templates if provided
        if step.get('subject_template') and step.get('body_template'):
            subject = self._render_template(step['subject_template'], meeting)
            body = self._render_template(step['body_template'], meeting)
            return subject, body
        
        # Generate based on type
        follow_up_type = step.get('type', 'custom')
        
        if follow_up_type == 'thank_you':
            return self._generate_thank_you_content(meeting)
        elif follow_up_type == 'summary':
            return self._generate_summary_content(meeting)
        elif follow_up_type == 'action_items':
            return self._generate_action_items_content(meeting)
        elif follow_up_type == 'check_in':
            return self._generate_check_in_content(meeting)
        elif follow_up_type == 'proposal':
            return self._generate_proposal_content(meeting)
        elif follow_up_type == 'feedback':
            return self._generate_feedback_content(meeting)
        else:
            return "Follow-up", "Custom follow-up content"
    
    def _generate_thank_you_content(self, meeting) -> tuple:
        """Generate thank you email content"""
        subject = f"Great connecting today - {meeting.meeting_type.name}"
        
        body = f"""Hi {meeting.guest_name},

Thank you for taking the time to meet with me today. I really enjoyed our conversation and learning more about your needs.

{self._get_personalized_line(meeting)}

I'll follow up shortly with a summary of what we discussed and the next steps.

Looking forward to connecting again soon!

Best regards,
{meeting.host.get_full_name() or meeting.host.username}
"""
        return subject, body
    
    def _generate_summary_content(self, meeting) -> tuple:
        """Generate meeting summary content"""
        subject = f"Meeting Summary - {meeting.meeting_type.name}"
        
        body = f"""Hi {meeting.guest_name},

Here's a summary of our meeting today:

**Meeting Details:**
- Date: {meeting.start_time.strftime('%B %d, %Y at %I:%M %p')}
- Duration: {meeting.duration_minutes} minutes
- Type: {meeting.meeting_type.name}

**Key Discussion Points:**
[Summary will be generated from meeting notes]

**Action Items:**
[Action items will be listed here]

**Next Steps:**
[Next steps and follow-up timeline]

Please let me know if I missed anything or if you have any questions.

Best regards,
{meeting.host.get_full_name() or meeting.host.username}
"""
        return subject, body
    
    def _generate_action_items_content(self, meeting) -> tuple:
        """Generate action items reminder"""
        subject = f"Action Items from our meeting - {meeting.meeting_type.name}"
        
        body = f"""Hi {meeting.guest_name},

I wanted to follow up on the action items from our recent meeting:

**Your Action Items:**
[List of action items assigned to the guest]

**My Action Items:**
[List of action items assigned to the host]

**Deadlines:**
[Timeline for each item]

Let me know if you need any clarification or support on these items.

Best regards,
{meeting.host.get_full_name() or meeting.host.username}
"""
        return subject, body
    
    def _generate_check_in_content(self, meeting) -> tuple:
        """Generate check-in email"""
        subject = f"Checking in - {meeting.meeting_type.name}"
        
        body = f"""Hi {meeting.guest_name},

I hope this message finds you well! I wanted to check in following our meeting last week.

Have you had a chance to review the materials I sent over? I'd be happy to answer any questions or discuss next steps.

Would you like to schedule a follow-up call this week?

Best regards,
{meeting.host.get_full_name() or meeting.host.username}
"""
        return subject, body
    
    def _generate_proposal_content(self, meeting) -> tuple:
        """Generate proposal follow-up"""
        subject = f"Proposal Following Our Discussion - {meeting.meeting_type.name}"
        
        body = f"""Hi {meeting.guest_name},

As discussed in our meeting, I've prepared a proposal that addresses your needs:

[Proposal details or attachment reference]

Key highlights:
- [Highlight 1]
- [Highlight 2]
- [Highlight 3]

I'm available to walk through this in detail at your convenience.

Best regards,
{meeting.host.get_full_name() or meeting.host.username}
"""
        return subject, body
    
    def _generate_feedback_content(self, meeting) -> tuple:
        """Generate feedback request"""
        subject = f"Your feedback on our meeting"
        
        body = f"""Hi {meeting.guest_name},

I hope you found our recent meeting valuable. I'm always looking to improve, and your feedback would be greatly appreciated.

Would you mind taking a moment to share:
1. What worked well in our meeting?
2. Is there anything we could have done differently?
3. Any topics you'd like to explore further?

Thank you for your time!

Best regards,
{meeting.host.get_full_name() or meeting.host.username}
"""
        return subject, body
    
    def _generate_thank_you_email(self, meeting) -> str:
        """Generate full thank you email body"""
        _, body = self._generate_thank_you_content(meeting)
        return body
    
    def _render_template(self, template: str, meeting) -> str:
        """Render template with meeting context"""
        replacements = {
            '{{guest_name}}': meeting.guest_name,
            '{{guest_email}}': meeting.guest_email,
            '{{meeting_type}}': meeting.meeting_type.name,
            '{{meeting_date}}': meeting.start_time.strftime('%B %d, %Y'),
            '{{meeting_time}}': meeting.start_time.strftime('%I:%M %p'),
            '{{duration}}': str(meeting.duration_minutes),
            '{{host_name}}': meeting.host.get_full_name() or meeting.host.username,
            '{{host_email}}': meeting.host.email
        }
        
        result = template
        for key, value in replacements.items():
            result = result.replace(key, value)
        
        return result
    
    def _get_personalized_line(self, meeting) -> str:
        """Get a personalized line based on meeting context"""
        if meeting.contact:
            return f"It was great to continue building our relationship and discussing how we can help {meeting.contact.company_name or 'your team'}."
        return "I look forward to exploring how we can work together."
    
    def _serialize_follow_up(self, follow_up: MeetingFollowUp) -> Dict:
        """Serialize follow-up to dict"""
        return {
            'id': str(follow_up.id),
            'meeting_id': str(follow_up.meeting_id),
            'type': follow_up.follow_up_type,
            'scheduled_at': follow_up.scheduled_at.isoformat(),
            'delay_hours': follow_up.delay_hours,
            'subject': follow_up.subject,
            'status': follow_up.status,
            'is_ai_generated': follow_up.is_ai_generated
        }
    
    def send_pending_follow_ups(self) -> Dict:
        """Send all pending follow-ups that are due"""
        now = timezone.now()
        
        pending = MeetingFollowUp.objects.filter(
            meeting__host=self.user,
            status='pending',
            scheduled_at__lte=now
        )
        
        sent_count = 0
        failed_count = 0
        
        for follow_up in pending:
            try:
                self._send_follow_up(follow_up)
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send follow-up {follow_up.id}: {e}")
                follow_up.status = 'failed'
                follow_up.last_error = str(e)
                follow_up.retry_count += 1
                follow_up.save()
                failed_count += 1
        
        return {
            'sent': sent_count,
            'failed': failed_count,
            'remaining': pending.count() - sent_count - failed_count
        }
    
    def _send_follow_up(self, follow_up: MeetingFollowUp):
        """Send a single follow-up email"""
        from django.core.mail import send_mail
        
        # Check conditions if set
        if follow_up.personalization_context.get('condition') == 'no_reply':
            # Check if guest has replied to any previous follow-up
            previous_replied = MeetingFollowUp.objects.filter(
                meeting=follow_up.meeting,
                status='replied',
                scheduled_at__lt=follow_up.scheduled_at
            ).exists()
            
            if previous_replied:
                follow_up.status = 'cancelled'
                follow_up.save()
                return
        
        # Send email
        send_mail(
            subject=follow_up.subject,
            message=follow_up.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[follow_up.meeting.guest_email],
            fail_silently=False
        )
        
        follow_up.status = 'sent'
        follow_up.sent_at = timezone.now()
        follow_up.save()
    
    @transaction.atomic
    def record_meeting_outcome(
        self,
        meeting_id: str,
        outcome: str,
        notes: str = '',
        action_items: Optional[List[Dict]] = None
    ) -> Dict:
        """Record meeting outcome and generate AI summary"""
        from .models import Meeting
        
        try:
            meeting = Meeting.objects.get(id=meeting_id, host=self.user)
        except Meeting.DoesNotExist:
            raise ValueError(f"Meeting {meeting_id} not found")
        
        # Create or update outcome
        meeting_outcome, created = MeetingOutcome.objects.update_or_create(
            meeting=meeting,
            defaults={
                'outcome': outcome,
                'notes': notes,
                'action_items': action_items or [],
                'recorded_by': self.user
            }
        )
        
        # Generate AI summary if notes provided
        if notes:
            ai_summary = self._generate_ai_summary(notes)
            meeting_outcome.ai_summary = ai_summary.get('summary', '')
            meeting_outcome.key_points = ai_summary.get('key_points', [])
            meeting_outcome.sentiment_score = ai_summary.get('sentiment', 0)
            meeting_outcome.save()
        
        # Update meeting status
        if outcome == 'no_show':
            meeting.status = 'no_show'
        elif outcome == 'rescheduled':
            meeting.status = 'rescheduled'
        else:
            meeting.status = 'completed'
        meeting.save()
        
        return {
            'id': str(meeting_outcome.id),
            'meeting_id': str(meeting.id),
            'outcome': meeting_outcome.outcome,
            'notes': meeting_outcome.notes,
            'action_items': meeting_outcome.action_items,
            'ai_summary': meeting_outcome.ai_summary,
            'key_points': meeting_outcome.key_points,
            'sentiment_score': meeting_outcome.sentiment_score
        }
    
    def _generate_ai_summary(self, notes: str) -> Dict:
        """Generate AI summary from meeting notes"""
        
        try:
            import openai
            
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze these meeting notes and provide:
1. A brief summary (2-3 sentences)
2. Key points (3-5 bullet points)
3. Sentiment score (-1 to 1, where -1 is negative, 0 is neutral, 1 is positive)

Return as JSON: {"summary": "...", "key_points": [...], "sentiment": 0.5}"""
                    },
                    {
                        "role": "user",
                        "content": notes
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            import json
            return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            logger.error(f"AI summary generation failed: {e}")
            return {
                'summary': '',
                'key_points': [],
                'sentiment': 0
            }
    
    def get_follow_up_analytics(self, days: int = 30) -> Dict:
        """Get analytics on follow-up performance"""
        
        start_date = timezone.now() - timedelta(days=days)
        
        follow_ups = MeetingFollowUp.objects.filter(
            meeting__host=self.user,
            created_at__gte=start_date
        )
        
        total = follow_ups.count()
        sent = follow_ups.filter(status='sent').count()
        opened = follow_ups.filter(status='opened').count()
        clicked = follow_ups.filter(status='clicked').count()
        replied = follow_ups.filter(status='replied').count()
        
        return {
            'period_days': days,
            'total_follow_ups': total,
            'sent': sent,
            'opened': opened,
            'clicked': clicked,
            'replied': replied,
            'open_rate': (opened / sent * 100) if sent > 0 else 0,
            'click_rate': (clicked / sent * 100) if sent > 0 else 0,
            'reply_rate': (replied / sent * 100) if sent > 0 else 0,
            'by_type': self._get_follow_up_by_type(follow_ups)
        }
    
    def _get_follow_up_by_type(self, follow_ups) -> Dict:
        """Get follow-up stats by type"""
        types = {}
        
        for follow_up in follow_ups:
            type_name = follow_up.follow_up_type
            if type_name not in types:
                types[type_name] = {'total': 0, 'sent': 0, 'replied': 0}
            
            types[type_name]['total'] += 1
            if follow_up.status in ['sent', 'opened', 'clicked', 'replied']:
                types[type_name]['sent'] += 1
            if follow_up.status == 'replied':
                types[type_name]['replied'] += 1
        
        return types


class SequenceTemplateService:
    """Service for managing follow-up sequence templates"""
    
    def __init__(self, user):
        self.user = user
    
    def get_default_sequences(self) -> List[Dict]:
        """Get default sequence templates"""
        
        return [
            {
                'name': 'Standard Sales Meeting',
                'description': 'Best for initial sales calls and demos',
                'steps': [
                    {
                        'delay_hours': 1,
                        'type': 'thank_you',
                        'subject_template': 'Great connecting today, {{guest_name}}!',
                        'body_template': 'Thank you email template...'
                    },
                    {
                        'delay_hours': 24,
                        'type': 'summary',
                        'include_action_items': True
                    },
                    {
                        'delay_days': 3,
                        'type': 'proposal'
                    },
                    {
                        'delay_days': 7,
                        'type': 'check_in',
                        'condition': 'no_reply'
                    }
                ]
            },
            {
                'name': 'Discovery Call',
                'description': 'For initial discovery and qualification calls',
                'steps': [
                    {
                        'delay_hours': 1,
                        'type': 'thank_you'
                    },
                    {
                        'delay_hours': 4,
                        'type': 'summary'
                    },
                    {
                        'delay_days': 2,
                        'type': 'check_in',
                        'condition': 'no_reply'
                    }
                ]
            },
            {
                'name': 'Customer Success',
                'description': 'For customer onboarding and success meetings',
                'steps': [
                    {
                        'delay_hours': 1,
                        'type': 'summary'
                    },
                    {
                        'delay_hours': 24,
                        'type': 'action_items'
                    },
                    {
                        'delay_days': 14,
                        'type': 'check_in'
                    },
                    {
                        'delay_days': 30,
                        'type': 'feedback'
                    }
                ]
            },
            {
                'name': 'Demo Follow-up',
                'description': 'For product demo meetings',
                'steps': [
                    {
                        'delay_hours': 1,
                        'type': 'thank_you'
                    },
                    {
                        'delay_hours': 2,
                        'type': 'summary'
                    },
                    {
                        'delay_days': 1,
                        'type': 'proposal'
                    },
                    {
                        'delay_days': 5,
                        'type': 'check_in',
                        'condition': 'no_reply'
                    },
                    {
                        'delay_days': 10,
                        'type': 'check_in',
                        'condition': 'no_reply'
                    }
                ]
            }
        ]
    
    @transaction.atomic
    def create_from_template(self, template_name: str) -> Dict:
        """Create a sequence from a template"""
        
        templates = {t['name']: t for t in self.get_default_sequences()}
        
        if template_name not in templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = templates[template_name]
        
        sequence = FollowUpSequence.objects.create(
            user=self.user,
            name=template['name'],
            description=template['description'],
            steps=template['steps'],
            use_ai_personalization=True
        )
        
        return {
            'id': str(sequence.id),
            'name': sequence.name,
            'description': sequence.description,
            'steps_count': len(sequence.steps)
        }
