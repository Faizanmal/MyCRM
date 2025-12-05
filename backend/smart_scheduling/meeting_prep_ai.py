"""
AI Meeting Prep Generator
Generates intelligent meeting preparation materials
"""

import logging
from typing import Dict, List, Optional
from django.utils import timezone
from datetime import timedelta
import json

logger = logging.getLogger(__name__)


class MeetingPrepGenerator:
    """Generates AI-powered meeting preparation materials"""
    
    def __init__(self, meeting):
        self.meeting = meeting
        self.host = meeting.host
        self.contact = meeting.contact
        self.opportunity = meeting.opportunity
    
    def generate_prep_materials(self) -> Dict:
        """Generate comprehensive meeting prep materials"""
        
        prep_data = {
            'participant_summary': self._generate_participant_summary(),
            'company_info': self._gather_company_info(),
            'crm_context': self._gather_crm_context(),
            'meeting_history': self._gather_meeting_history(),
            'suggested_agenda': self._generate_agenda(),
            'talking_points': self._generate_talking_points(),
            'questions_to_ask': self._generate_questions(),
            'potential_objections': self._identify_objections(),
            'personalization_tips': self._generate_personalization_tips(),
            'ice_breakers': self._generate_ice_breakers(),
            'deal_context': self._gather_deal_context(),
            'recommended_next_steps': self._suggest_next_steps()
        }
        
        return prep_data
    
    def _generate_participant_summary(self) -> str:
        """Generate a summary of the participant"""
        
        summary_parts = []
        
        if self.contact:
            summary_parts.append(f"**{self.contact.first_name} {self.contact.last_name}**")
            
            if hasattr(self.contact, 'title') and self.contact.title:
                summary_parts.append(f"Title: {self.contact.title}")
            
            if hasattr(self.contact, 'company') and self.contact.company:
                summary_parts.append(f"Company: {self.contact.company}")
            
            if hasattr(self.contact, 'email') and self.contact.email:
                summary_parts.append(f"Email: {self.contact.email}")
        else:
            summary_parts.append(f"**{self.meeting.guest_name}**")
            summary_parts.append(f"Email: {self.meeting.guest_email}")
        
        return "\n".join(summary_parts)
    
    def _gather_company_info(self) -> Dict:
        """Gather information about the participant's company"""
        
        company_info = {
            'name': '',
            'industry': '',
            'size': '',
            'website': '',
            'description': '',
            'recent_news': []
        }
        
        if self.contact and hasattr(self.contact, 'company_name'):
            company_info['name'] = self.contact.company_name or ''
        
        # In production, this would integrate with data enrichment services
        # For now, return basic structure
        
        return company_info
    
    def _gather_crm_context(self) -> Dict:
        """Gather relevant CRM context"""
        
        context = {
            'contact_summary': '',
            'previous_interactions': [],
            'open_opportunities': [],
            'pending_tasks': [],
            'tags': [],
            'notes': []
        }
        
        if self.contact:
            # Get interaction history
            if hasattr(self.contact, 'interactions'):
                interactions = self.contact.interactions.order_by('-created_at')[:5]
                context['previous_interactions'] = [
                    {
                        'type': i.interaction_type if hasattr(i, 'interaction_type') else 'unknown',
                        'date': i.created_at.isoformat() if hasattr(i, 'created_at') else '',
                        'summary': i.notes[:200] if hasattr(i, 'notes') else ''
                    }
                    for i in interactions
                ]
            
            # Get opportunities
            if hasattr(self.contact, 'opportunities'):
                opportunities = self.contact.opportunities.filter(
                    status__in=['open', 'in_progress', 'negotiation']
                )
                context['open_opportunities'] = [
                    {
                        'name': o.name,
                        'value': float(o.value) if hasattr(o, 'value') else 0,
                        'stage': o.stage if hasattr(o, 'stage') else '',
                        'probability': o.probability if hasattr(o, 'probability') else 0
                    }
                    for o in opportunities
                ]
            
            # Get pending tasks
            if hasattr(self.contact, 'tasks'):
                tasks = self.contact.tasks.filter(status='pending')
                context['pending_tasks'] = [
                    {
                        'title': t.title,
                        'due_date': t.due_date.isoformat() if hasattr(t, 'due_date') and t.due_date else '',
                        'priority': t.priority if hasattr(t, 'priority') else 'normal'
                    }
                    for t in tasks
                ]
            
            # Get tags
            if hasattr(self.contact, 'tags'):
                context['tags'] = list(self.contact.tags.values_list('name', flat=True))
        
        return context
    
    def _gather_meeting_history(self) -> Dict:
        """Gather history of meetings with this participant"""
        from .models import Meeting
        
        history = {
            'total_meetings': 0,
            'last_meeting': None,
            'meetings_list': [],
            'common_topics': [],
            'outcomes': []
        }
        
        # Find previous meetings with same guest
        previous_meetings = Meeting.objects.filter(
            host=self.host,
            guest_email=self.meeting.guest_email,
            status='completed',
            end_time__lt=timezone.now()
        ).order_by('-start_time')[:10]
        
        history['total_meetings'] = previous_meetings.count()
        
        if previous_meetings.exists():
            last = previous_meetings.first()
            history['last_meeting'] = {
                'date': last.start_time.isoformat(),
                'type': last.meeting_type.name if last.meeting_type else '',
                'notes': last.notes[:500] if last.notes else ''
            }
            
            history['meetings_list'] = [
                {
                    'date': m.start_time.isoformat(),
                    'type': m.meeting_type.name if m.meeting_type else '',
                    'duration': m.duration_minutes,
                    'status': m.status
                }
                for m in previous_meetings[:5]
            ]
        
        return history
    
    def _generate_agenda(self) -> List[Dict]:
        """Generate a suggested meeting agenda"""
        
        agenda = []
        meeting_duration = self.meeting.duration_minutes
        
        # Opening (5 min)
        agenda.append({
            'item': 'Welcome & Introduction',
            'duration': 5,
            'notes': 'Brief introductions and rapport building'
        })
        
        # Main content depends on meeting type and context
        if self.opportunity:
            # Sales-focused agenda
            agenda.extend([
                {
                    'item': 'Review Current Situation',
                    'duration': min(10, meeting_duration // 4),
                    'notes': 'Understand current challenges and needs'
                },
                {
                    'item': 'Present Solution',
                    'duration': min(15, meeting_duration // 3),
                    'notes': 'Demonstrate value proposition'
                },
                {
                    'item': 'Address Questions & Concerns',
                    'duration': min(10, meeting_duration // 4),
                    'notes': 'Handle objections and clarify'
                },
                {
                    'item': 'Discuss Next Steps',
                    'duration': 5,
                    'notes': 'Define clear action items'
                }
            ])
        else:
            # General meeting agenda
            remaining = meeting_duration - 10  # Account for intro and closing
            agenda.extend([
                {
                    'item': 'Main Discussion',
                    'duration': remaining - 5,
                    'notes': 'Core meeting content'
                },
                {
                    'item': 'Summary & Action Items',
                    'duration': 5,
                    'notes': 'Recap key points and next steps'
                }
            ])
        
        return agenda
    
    def _generate_talking_points(self) -> List[Dict]:
        """Generate key talking points"""
        
        talking_points = []
        
        # Based on opportunity stage
        if self.opportunity:
            stage = getattr(self.opportunity, 'stage', '')
            
            if stage in ['discovery', 'qualification']:
                talking_points.extend([
                    {
                        'point': 'Understanding Their Challenges',
                        'details': 'Ask about current pain points and what prompted them to look for solutions'
                    },
                    {
                        'point': 'Budget & Timeline',
                        'details': 'Gauge budget expectations and implementation timeline'
                    },
                    {
                        'point': 'Decision Process',
                        'details': 'Understand who else is involved in the decision'
                    }
                ])
            elif stage in ['proposal', 'negotiation']:
                talking_points.extend([
                    {
                        'point': 'Address Previous Concerns',
                        'details': 'Follow up on any concerns raised in previous meetings'
                    },
                    {
                        'point': 'ROI & Value',
                        'details': 'Reinforce the return on investment and value proposition'
                    },
                    {
                        'point': 'Implementation Plan',
                        'details': 'Discuss onboarding and support process'
                    }
                ])
        else:
            # General talking points
            talking_points.append({
                'point': 'Meeting Objective',
                'details': 'Clarify the purpose and desired outcomes of the meeting'
            })
        
        return talking_points
    
    def _generate_questions(self) -> List[Dict]:
        """Generate questions to ask during the meeting"""
        
        questions = []
        
        # Discovery questions
        questions.extend([
            {
                'question': 'What are your top priorities for this quarter?',
                'purpose': 'Understand their current focus',
                'category': 'discovery'
            },
            {
                'question': 'What challenges have you faced with your current approach?',
                'purpose': 'Identify pain points',
                'category': 'discovery'
            },
            {
                'question': 'How would you measure success in this area?',
                'purpose': 'Understand success metrics',
                'category': 'qualification'
            }
        ])
        
        # Follow-up questions if we have history
        if self.contact:
            questions.append({
                'question': 'Since we last spoke, what progress has been made?',
                'purpose': 'Build on previous conversations',
                'category': 'follow-up'
            })
        
        # Closing questions
        questions.extend([
            {
                'question': 'What would you need to see to move forward?',
                'purpose': 'Identify next steps',
                'category': 'closing'
            },
            {
                'question': 'Who else should be involved in this conversation?',
                'purpose': 'Expand stakeholder map',
                'category': 'expansion'
            }
        ])
        
        return questions
    
    def _identify_objections(self) -> List[Dict]:
        """Identify potential objections and prepare responses"""
        
        objections = []
        
        # Common objections
        objections.extend([
            {
                'objection': 'Budget constraints',
                'response': 'Focus on ROI and potential cost savings. Offer flexible payment options if available.',
                'category': 'price'
            },
            {
                'objection': 'Not the right time',
                'response': 'Understand their timeline and discuss the cost of delay. Offer to start small.',
                'category': 'timing'
            },
            {
                'objection': 'Need to consult with others',
                'response': 'Offer to present to the broader team. Ask who else should be included.',
                'category': 'authority'
            },
            {
                'objection': 'Already using a competitor',
                'response': 'Ask about their experience and any gaps. Focus on differentiation.',
                'category': 'competition'
            }
        ])
        
        return objections
    
    def _generate_personalization_tips(self) -> List[Dict]:
        """Generate personalization tips for the meeting"""
        
        tips = []
        
        if self.contact:
            # Use contact info for personalization
            if hasattr(self.contact, 'notes') and self.contact.notes:
                tips.append({
                    'tip': 'Reference previous notes',
                    'detail': f'Review contact notes for context'
                })
        
        # Time-based tips
        meeting_hour = self.meeting.start_time.hour
        if meeting_hour < 10:
            tips.append({
                'tip': 'Early meeting',
                'detail': 'Keep introductions brief, they may have a busy day ahead'
            })
        elif meeting_hour >= 16:
            tips.append({
                'tip': 'Late day meeting',
                'detail': 'Be mindful of time, they may be wrapping up their day'
            })
        
        # Day-based tips
        day = self.meeting.start_time.weekday()
        if day == 0:
            tips.append({
                'tip': 'Monday meeting',
                'detail': 'Allow time for them to settle into the week'
            })
        elif day == 4:
            tips.append({
                'tip': 'Friday meeting',
                'detail': 'Keep it focused and action-oriented for weekend follow-up'
            })
        
        return tips
    
    def _generate_ice_breakers(self) -> List[str]:
        """Generate ice breaker suggestions"""
        
        ice_breakers = [
            "How's your week going so far?",
            "Have you had a chance to [reference recent shared event/news]?",
            "I noticed you're based in [location] - how's the weather there?"
        ]
        
        # Add contextual ice breakers
        if self.contact and hasattr(self.contact, 'linkedin_url') and self.contact.linkedin_url:
            ice_breakers.append("I saw on LinkedIn that you [recent activity] - that's impressive!")
        
        return ice_breakers
    
    def _gather_deal_context(self) -> Dict:
        """Gather context about the related deal/opportunity"""
        
        deal_context = {
            'stage': '',
            'value': 0,
            'probability': 0,
            'days_in_stage': 0,
            'competitors': [],
            'key_stakeholders': [],
            'decision_criteria': []
        }
        
        if self.opportunity:
            deal_context['stage'] = getattr(self.opportunity, 'stage', '')
            deal_context['value'] = float(getattr(self.opportunity, 'value', 0) or 0)
            deal_context['probability'] = getattr(self.opportunity, 'probability', 0)
            
            # Calculate days in stage
            if hasattr(self.opportunity, 'stage_changed_at') and self.opportunity.stage_changed_at:
                days = (timezone.now() - self.opportunity.stage_changed_at).days
                deal_context['days_in_stage'] = days
        
        return deal_context
    
    def _suggest_next_steps(self) -> List[Dict]:
        """Suggest next steps based on context"""
        
        next_steps = []
        
        if self.opportunity:
            stage = getattr(self.opportunity, 'stage', '')
            
            if stage in ['discovery', 'qualification']:
                next_steps.extend([
                    {
                        'step': 'Schedule follow-up demo',
                        'priority': 'high',
                        'timing': 'Within 1 week'
                    },
                    {
                        'step': 'Send relevant case studies',
                        'priority': 'medium',
                        'timing': 'Same day'
                    }
                ])
            elif stage == 'proposal':
                next_steps.extend([
                    {
                        'step': 'Review and refine proposal',
                        'priority': 'high',
                        'timing': 'Within 24 hours'
                    },
                    {
                        'step': 'Schedule decision-maker meeting',
                        'priority': 'high',
                        'timing': 'Within 1 week'
                    }
                ])
            elif stage == 'negotiation':
                next_steps.extend([
                    {
                        'step': 'Finalize contract terms',
                        'priority': 'high',
                        'timing': 'Within 48 hours'
                    },
                    {
                        'step': 'Prepare implementation timeline',
                        'priority': 'medium',
                        'timing': 'Before close'
                    }
                ])
        else:
            next_steps.append({
                'step': 'Send meeting summary',
                'priority': 'high',
                'timing': 'Same day'
            })
        
        return next_steps


class SmartReminderOptimizer:
    """Optimizes reminder timing and channel based on attendee behavior"""
    
    def __init__(self, meeting):
        self.meeting = meeting
    
    def get_optimal_reminders(self) -> List[Dict]:
        """Generate optimal reminder schedule"""
        from .ai_models import AttendeeIntelligence, NoShowPrediction
        
        reminders = []
        
        # Try to get attendee intelligence
        attendee_intel = None
        try:
            attendee_intel = AttendeeIntelligence.objects.get(email=self.meeting.guest_email)
        except AttendeeIntelligence.DoesNotExist:
            pass
        
        # Get no-show prediction if available
        no_show_risk = 0
        try:
            prediction = NoShowPrediction.objects.get(meeting=self.meeting)
            no_show_risk = prediction.risk_score
        except NoShowPrediction.DoesNotExist:
            pass
        
        # Determine best channel
        best_channel = self._determine_best_channel(attendee_intel)
        
        # Standard reminders
        reminder_times = [1440, 60]  # 24 hours and 1 hour before
        
        # Add extra reminder for high-risk meetings
        if no_show_risk > 50:
            reminder_times.insert(1, 180)  # 3 hours before
        
        if no_show_risk > 70:
            reminder_times.insert(0, 2880)  # 48 hours before
        
        for minutes_before in reminder_times:
            reminder_time = self.meeting.start_time - timedelta(minutes=minutes_before)
            
            if reminder_time > timezone.now():
                reminders.append({
                    'scheduled_at': reminder_time.isoformat(),
                    'minutes_before': minutes_before,
                    'channel': best_channel,
                    'include_prep_material': minutes_before == 1440,  # Include prep in 24h reminder
                    'include_agenda': True,
                    'optimization_reason': self._get_optimization_reason(
                        minutes_before, no_show_risk, attendee_intel
                    )
                })
        
        return reminders
    
    def _determine_best_channel(self, attendee_intel) -> str:
        """Determine the best communication channel"""
        
        if attendee_intel and attendee_intel.best_communication_channel:
            return attendee_intel.best_communication_channel
        
        # Default to email
        return 'email'
    
    def _get_optimization_reason(
        self,
        minutes_before: int,
        no_show_risk: int,
        attendee_intel
    ) -> str:
        """Generate explanation for reminder timing"""
        
        reasons = []
        
        if minutes_before == 2880 and no_show_risk > 70:
            reasons.append("48h reminder added due to high no-show risk")
        elif minutes_before == 180 and no_show_risk > 50:
            reasons.append("3h reminder added due to elevated no-show risk")
        
        if attendee_intel:
            if attendee_intel.best_reminder_timing:
                reasons.append(f"Channel optimized based on {attendee_intel.email}'s engagement history")
        
        if not reasons:
            reasons.append("Standard reminder timing")
        
        return "; ".join(reasons)
