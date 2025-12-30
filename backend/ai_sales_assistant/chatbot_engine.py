"""
AI Sales Assistant - Conversational Chatbot Engine
Handles natural language queries, CRM data analysis, and intelligent responses
"""

import os
import json
import re
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional, Tuple

from django.db.models import Sum, Avg, Count, Q, F
from django.utils import timezone


class ChatbotEngine:
    """Core chatbot engine for CRM assistant"""
    
    def __init__(self):
        self.openai_available = bool(os.environ.get('OPENAI_API_KEY'))
        self.intent_handlers = {
            'pipeline_query': self._handle_pipeline_query,
            'deal_status': self._handle_deal_status,
            'activity_summary': self._handle_activity_summary,
            'forecast_query': self._handle_forecast_query,
            'contact_lookup': self._handle_contact_lookup,
            'task_query': self._handle_task_query,
            'generate_content': self._handle_content_generation,
            'coaching_request': self._handle_coaching_request,
            'insight_request': self._handle_insight_request,
            'action_suggestion': self._handle_action_suggestion,
        }
    
    def process_message(self, session, message: str, user) -> Dict[str, Any]:
        """Process a user message and generate a response"""
        
        # Detect intent
        intent, entities = self._detect_intent(message)
        
        # Get CRM context
        crm_context = self._build_crm_context(user, entities)
        
        # Handle based on intent
        if intent in self.intent_handlers:
            response = self.intent_handlers[intent](message, entities, crm_context, user)
        else:
            response = self._handle_general_query(message, crm_context, user)
        
        return response
    
    def _detect_intent(self, message: str) -> Tuple[str, Dict]:
        """Detect user intent from message"""
        
        message_lower = message.lower()
        entities = {}
        
        # Pipeline queries
        pipeline_patterns = [
            r'pipeline|deals|opportunities',
            r'how many deals|deal count',
            r'pipeline value|total value',
            r'stages?|funnel',
        ]
        for pattern in pipeline_patterns:
            if re.search(pattern, message_lower):
                return 'pipeline_query', entities
        
        # Deal status
        deal_patterns = [
            r'deal\s+status|deal\s+update',
            r'how is.+deal|deal.+doing',
            r'risk.+deal|at.risk',
        ]
        for pattern in deal_patterns:
            if re.search(pattern, message_lower):
                return 'deal_status', entities
        
        # Activity summary
        activity_patterns = [
            r'activities?|what.+(done|completed)',
            r'my\s+(day|week|month)',
            r'calls?|emails?|meetings?',
        ]
        for pattern in activity_patterns:
            if re.search(pattern, message_lower):
                return 'activity_summary', entities
        
        # Forecast
        forecast_patterns = [
            r'forecast|prediction|quota',
            r'will\s+(i|we)\s+(hit|make|reach)',
            r'revenue|target',
        ]
        for pattern in forecast_patterns:
            if re.search(pattern, message_lower):
                return 'forecast_query', entities
        
        # Contact lookup
        contact_patterns = [
            r'contact|person|who\s+is',
            r'find\s+\w+|search\s+\w+',
        ]
        for pattern in contact_patterns:
            if re.search(pattern, message_lower):
                return 'contact_lookup', entities
        
        # Task queries
        task_patterns = [
            r'tasks?|to.?do|pending',
            r'what.+need|overdue',
        ]
        for pattern in task_patterns:
            if re.search(pattern, message_lower):
                return 'task_query', entities
        
        # Content generation
        content_patterns = [
            r'write|draft|compose|generate',
            r'email|script|message|post',
            r'help\s+me\s+write',
        ]
        for pattern in content_patterns:
            if re.search(pattern, message_lower):
                return 'generate_content', entities
        
        # Coaching
        coaching_patterns = [
            r'advice|suggest|recommend|help',
            r'how\s+(should|can|do)',
            r'objection|handle|overcome',
        ]
        for pattern in coaching_patterns:
            if re.search(pattern, message_lower):
                return 'coaching_request', entities
        
        # Insights
        insight_patterns = [
            r'insight|analysis|analyze|trend',
            r'what\s+should\s+i\s+know',
            r'important|priority',
        ]
        for pattern in insight_patterns:
            if re.search(pattern, message_lower):
                return 'insight_request', entities
        
        # Actions
        action_patterns = [
            r'what.+next|next.+action|should\s+i\s+do',
            r'priorit|focus|urgent',
        ]
        for pattern in action_patterns:
            if re.search(pattern, message_lower):
                return 'action_suggestion', entities
        
        return 'general', entities
    
    def _build_crm_context(self, user, entities: Dict) -> Dict[str, Any]:
        """Build CRM context for the response"""
        
        from opportunity_management.models import Opportunity
        from contact_management.models import Contact
        from task_management.models import Task
        from activity_feed.models import Activity
        
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        context = {
            'user': {
                'name': user.get_full_name() or user.email,
                'email': user.email,
            },
            'pipeline': {},
            'activities': {},
            'tasks': {},
        }
        
        # Pipeline summary
        opportunities = Opportunity.objects.filter(owner=user, is_closed=False)
        context['pipeline'] = {
            'total_deals': opportunities.count(),
            'total_value': float(opportunities.aggregate(Sum('amount'))['amount__sum'] or 0),
            'by_stage': list(opportunities.values('stage').annotate(
                count=Count('id'),
                value=Sum('amount')
            )),
            'closing_this_month': opportunities.filter(
                expected_close_date__month=today.month,
                expected_close_date__year=today.year
            ).count(),
        }
        
        # Recent activities
        try:
            recent_activities = Activity.objects.filter(
                user=user,
                created_at__gte=week_ago
            ).count()
            context['activities'] = {
                'this_week': recent_activities,
            }
        except Exception:
            context['activities'] = {'this_week': 0}
        
        # Tasks
        try:
            tasks = Task.objects.filter(assigned_to=user)
            context['tasks'] = {
                'pending': tasks.filter(status='pending').count(),
                'overdue': tasks.filter(
                    due_date__lt=today,
                    status__in=['pending', 'in_progress']
                ).count(),
                'due_today': tasks.filter(due_date=today).count(),
            }
        except Exception:
            context['tasks'] = {'pending': 0, 'overdue': 0, 'due_today': 0}
        
        return context
    
    def _handle_pipeline_query(self, message: str, entities: Dict, 
                                context: Dict, user) -> Dict[str, Any]:
        """Handle pipeline-related queries"""
        
        pipeline = context['pipeline']
        
        response_text = f"""📊 **Your Pipeline Overview**

**Total Active Deals:** {pipeline['total_deals']}
**Total Pipeline Value:** ${pipeline['total_value']:,.2f}
**Deals Closing This Month:** {pipeline['closing_this_month']}

**By Stage:**"""
        
        for stage in pipeline['by_stage']:
            stage_name = stage['stage'].replace('_', ' ').title()
            response_text += f"\n• {stage_name}: {stage['count']} deals (${float(stage['value'] or 0):,.0f})"
        
        # Generate insights
        insights = []
        if pipeline['closing_this_month'] > 0:
            insights.append({
                'type': 'info',
                'text': f"You have {pipeline['closing_this_month']} deals expected to close this month."
            })
        
        return {
            'message_type': 'insight',
            'content': response_text,
            'metadata': {
                'chart_type': 'pipeline_funnel',
                'data': pipeline,
                'insights': insights,
            },
            'attachments': [],
        }
    
    def _handle_deal_status(self, message: str, entities: Dict,
                            context: Dict, user) -> Dict[str, Any]:
        """Handle deal status queries"""
        
        from opportunity_management.models import Opportunity
        
        # Get at-risk deals
        at_risk_deals = Opportunity.objects.filter(
            owner=user,
            is_closed=False,
        ).order_by('-amount')[:5]
        
        response_text = "🎯 **Deal Status Summary**\n\n"
        
        if at_risk_deals.exists():
            response_text += "**Top Active Deals:**\n"
            for deal in at_risk_deals:
                response_text += f"• **{deal.name}**: ${float(deal.amount):,.0f} - {deal.stage}\n"
        else:
            response_text += "No active deals found."
        
        # Generate actions
        actions = []
        for deal in at_risk_deals[:3]:
            actions.append({
                'type': 'review',
                'title': f'Review {deal.name}',
                'entity_type': 'opportunity',
                'entity_id': str(deal.id),
            })
        
        return {
            'message_type': 'insight',
            'content': response_text,
            'metadata': {
                'actions': actions,
            },
            'attachments': [
                {'type': 'opportunity', 'id': str(d.id), 'name': d.name}
                for d in at_risk_deals
            ],
        }
    
    def _handle_activity_summary(self, message: str, entities: Dict,
                                  context: Dict, user) -> Dict[str, Any]:
        """Handle activity summary queries"""
        
        activities = context['activities']
        tasks = context['tasks']
        
        response_text = f"""📅 **Your Activity Summary**

**This Week:**
• Activities logged: {activities.get('this_week', 0)}

**Tasks:**
• Pending: {tasks['pending']}
• Due Today: {tasks['due_today']}
• Overdue: {tasks['overdue']}
"""
        
        if tasks['overdue'] > 0:
            response_text += f"\n⚠️ You have {tasks['overdue']} overdue tasks that need attention."
        
        return {
            'message_type': 'insight',
            'content': response_text,
            'metadata': {
                'activities': activities,
                'tasks': tasks,
            },
            'attachments': [],
        }
    
    def _handle_forecast_query(self, message: str, entities: Dict,
                               context: Dict, user) -> Dict[str, Any]:
        """Handle forecast and quota queries"""
        
        from revenue_intelligence.models import RevenueTarget
        from opportunity_management.models import Opportunity
        
        today = timezone.now().date()
        
        # Get current quota
        try:
            target = RevenueTarget.objects.filter(
                user=user,
                period='monthly',
                start_date__lte=today,
                end_date__gte=today
            ).first()
            
            if target:
                progress = (float(target.achieved_amount) / float(target.target_amount)) * 100
                response_text = f"""📈 **Forecast & Quota Status**

**Monthly Target:** ${float(target.target_amount):,.0f}
**Achieved:** ${float(target.achieved_amount):,.0f} ({progress:.1f}%)
**Remaining:** ${float(target.target_amount - target.achieved_amount):,.0f}

**Pipeline Coverage:** {float(target.weighted_pipeline / target.target_amount * 100) if target.target_amount else 0:.1f}%
"""
            else:
                # Calculate from pipeline
                pipeline_value = context['pipeline']['total_value']
                response_text = f"""📈 **Pipeline Forecast**

**Total Pipeline Value:** ${pipeline_value:,.0f}
**Deals in Pipeline:** {context['pipeline']['total_deals']}

💡 _Set up revenue targets for more detailed forecasting._
"""
        except Exception:
            response_text = "Unable to load forecast data. Please check your revenue targets."
        
        return {
            'message_type': 'insight',
            'content': response_text,
            'metadata': {
                'chart_type': 'forecast_gauge',
            },
            'attachments': [],
        }
    
    def _handle_contact_lookup(self, message: str, entities: Dict,
                               context: Dict, user) -> Dict[str, Any]:
        """Handle contact search and lookup"""
        
        from contact_management.models import Contact
        
        # Extract potential name from message
        # Simple extraction - in production would use NER
        words = message.lower().replace('find', '').replace('search', '').replace('contact', '').strip().split()
        search_term = ' '.join(words) if words else ''
        
        if search_term:
            contacts = Contact.objects.filter(
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(company__icontains=search_term) |
                Q(email__icontains=search_term)
            )[:5]
            
            if contacts.exists():
                response_text = f"🔍 **Found {contacts.count()} contacts:**\n\n"
                for contact in contacts:
                    response_text += f"• **{contact.first_name} {contact.last_name}**"
                    if contact.company:
                        response_text += f" - {contact.company}"
                    response_text += f"\n  📧 {contact.email}\n"
            else:
                response_text = f"No contacts found matching '{search_term}'."
        else:
            response_text = "Please specify a name, company, or email to search for."
        
        return {
            'message_type': 'text',
            'content': response_text,
            'metadata': {},
            'attachments': [],
        }
    
    def _handle_task_query(self, message: str, entities: Dict,
                           context: Dict, user) -> Dict[str, Any]:
        """Handle task-related queries"""
        
        from task_management.models import Task
        
        today = timezone.now().date()
        
        # Get upcoming tasks
        tasks = Task.objects.filter(
            assigned_to=user,
            status__in=['pending', 'in_progress']
        ).order_by('due_date')[:10]
        
        response_text = "✅ **Your Tasks**\n\n"
        
        overdue = []
        due_today = []
        upcoming = []
        
        for task in tasks:
            if task.due_date:
                if task.due_date < today:
                    overdue.append(task)
                elif task.due_date == today:
                    due_today.append(task)
                else:
                    upcoming.append(task)
            else:
                upcoming.append(task)
        
        if overdue:
            response_text += "**⚠️ Overdue:**\n"
            for task in overdue:
                response_text += f"• {task.title} (Due: {task.due_date})\n"
            response_text += "\n"
        
        if due_today:
            response_text += "**📅 Due Today:**\n"
            for task in due_today:
                response_text += f"• {task.title}\n"
            response_text += "\n"
        
        if upcoming:
            response_text += "**🔜 Upcoming:**\n"
            for task in upcoming[:5]:
                due = f" (Due: {task.due_date})" if task.due_date else ""
                response_text += f"• {task.title}{due}\n"
        
        if not tasks:
            response_text += "🎉 No pending tasks!"
        
        return {
            'message_type': 'insight',
            'content': response_text,
            'metadata': {
                'overdue_count': len(overdue),
                'due_today_count': len(due_today),
            },
            'attachments': [],
        }
    
    def _handle_content_generation(self, message: str, entities: Dict,
                                   context: Dict, user) -> Dict[str, Any]:
        """Handle content generation requests"""
        
        response_text = """✍️ **Content Generation**

I can help you create:
• **Email drafts** - Professional outreach and follow-ups
• **Call scripts** - Structured conversation guides
• **Social posts** - LinkedIn and social media content
• **Objection responses** - Handling common pushbacks

Please specify what you'd like to create and for which contact/deal.

_Example: "Write a follow-up email for the Acme Corp deal"_
"""
        
        return {
            'message_type': 'suggestion',
            'content': response_text,
            'metadata': {
                'quick_actions': [
                    {'label': 'Write Email', 'action': 'generate_email'},
                    {'label': 'Create Script', 'action': 'generate_script'},
                    {'label': 'Social Post', 'action': 'generate_social'},
                ],
            },
            'attachments': [],
        }
    
    def _handle_coaching_request(self, message: str, entities: Dict,
                                  context: Dict, user) -> Dict[str, Any]:
        """Handle sales coaching requests"""
        
        # In production, this would use GPT-4 for personalized advice
        coaching_tips = [
            "**Discovery Call Tips:**\n• Ask open-ended questions\n• Listen more than you talk\n• Identify pain points early",
            "**Closing Techniques:**\n• Create urgency with value, not pressure\n• Address objections proactively\n• Always confirm next steps",
            "**Objection Handling:**\n• Acknowledge the concern\n• Ask clarifying questions\n• Reframe around value",
        ]
        
        import random
        tip = random.choice(coaching_tips)
        
        response_text = f"""🎯 **Sales Coaching**

{tip}

💡 _For personalized coaching, tell me about a specific deal or situation you're facing._
"""
        
        return {
            'message_type': 'insight',
            'content': response_text,
            'metadata': {},
            'attachments': [],
        }
    
    def _handle_insight_request(self, message: str, entities: Dict,
                                 context: Dict, user) -> Dict[str, Any]:
        """Handle insight and analysis requests"""
        
        pipeline = context['pipeline']
        tasks = context['tasks']
        
        insights = []
        
        # Generate insights based on data
        if pipeline['total_deals'] > 0:
            avg_deal = pipeline['total_value'] / pipeline['total_deals']
            insights.append(f"Your average deal size is ${avg_deal:,.0f}")
        
        if tasks['overdue'] > 0:
            insights.append(f"⚠️ You have {tasks['overdue']} overdue tasks that may be impacting deals")
        
        if pipeline['closing_this_month'] > 0:
            insights.append(f"Focus on {pipeline['closing_this_month']} deals closing this month")
        
        response_text = "💡 **Key Insights**\n\n"
        for insight in insights:
            response_text += f"• {insight}\n"
        
        if not insights:
            response_text += "No significant insights at this time. Keep up the good work!"
        
        return {
            'message_type': 'insight',
            'content': response_text,
            'metadata': {
                'insights': insights,
            },
            'attachments': [],
        }
    
    def _handle_action_suggestion(self, message: str, entities: Dict,
                                   context: Dict, user) -> Dict[str, Any]:
        """Handle next action suggestions"""
        
        from opportunity_management.models import Opportunity
        from task_management.models import Task
        
        today = timezone.now().date()
        
        actions = []
        
        # Check for overdue tasks
        if context['tasks']['overdue'] > 0:
            actions.append({
                'priority': 'high',
                'action': f"Complete {context['tasks']['overdue']} overdue tasks",
                'reason': "Overdue tasks can impact deal momentum",
            })
        
        # Check for stale deals
        stale_deals = Opportunity.objects.filter(
            owner=user,
            is_closed=False,
            updated_at__lt=timezone.now() - timedelta(days=7)
        ).count()
        
        if stale_deals > 0:
            actions.append({
                'priority': 'medium',
                'action': f"Update {stale_deals} deals with no recent activity",
                'reason': "Regular updates keep deals on track",
            })
        
        # Check for deals closing soon
        if context['pipeline']['closing_this_month'] > 0:
            actions.append({
                'priority': 'high',
                'action': f"Review {context['pipeline']['closing_this_month']} deals closing this month",
                'reason': "Ensure close dates are accurate",
            })
        
        response_text = "🎯 **Recommended Actions**\n\n"
        
        for i, action in enumerate(actions, 1):
            priority_emoji = '🔴' if action['priority'] == 'high' else '🟡'
            response_text += f"{i}. {priority_emoji} **{action['action']}**\n   _{action['reason']}_\n\n"
        
        if not actions:
            response_text += "✅ You're all caught up! No urgent actions needed."
        
        return {
            'message_type': 'action',
            'content': response_text,
            'metadata': {
                'actions': actions,
            },
            'attachments': [],
        }
    
    def _handle_general_query(self, message: str, context: Dict, user) -> Dict[str, Any]:
        """Handle general queries using AI or fallback"""
        
        if self.openai_available:
            return self._generate_ai_response(message, context, user)
        else:
            return {
                'message_type': 'text',
                'content': """I can help you with:

• **Pipeline queries** - "Show me my pipeline" or "How many deals do I have?"
• **Deal status** - "What's the status of my deals?" or "Show at-risk deals"
• **Tasks** - "What are my tasks?" or "Show overdue tasks"
• **Forecasting** - "What's my forecast?" or "Will I hit quota?"
• **Content** - "Write an email" or "Help me with a call script"
• **Coaching** - "How should I handle this objection?"

What would you like to know?""",
                'metadata': {},
                'attachments': [],
            }
    
    def _generate_ai_response(self, message: str, context: Dict, user) -> Dict[str, Any]:
        """Generate response using OpenAI"""
        
        try:
            import openai
            
            system_prompt = f"""You are a helpful AI sales assistant for a CRM system.
You help sales professionals with their pipeline, deals, tasks, and provide coaching.

User context:
- Name: {context['user']['name']}
- Pipeline: {context['pipeline']['total_deals']} deals worth ${context['pipeline']['total_value']:,.0f}
- Tasks: {context['tasks']['pending']} pending, {context['tasks']['overdue']} overdue

Be concise, helpful, and actionable. Use emojis sparingly for emphasis."""
            
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
                temperature=0.7,
            )
            
            return {
                'message_type': 'text',
                'content': response.choices[0].message.content,
                'metadata': {},
                'attachments': [],
            }
        except Exception as e:
            return self._handle_general_query(message, context, user)


class PredictiveDealEngine:
    """ML engine for deal predictions and risk assessment"""
    
    def __init__(self):
        self.model_version = "1.0.0"
    
    def analyze_deal(self, opportunity) -> Dict[str, Any]:
        """Analyze a deal and generate predictions"""
        
        from opportunity_management.models import Opportunity
        from activity_feed.models import Activity
        
        # Calculate win probability based on multiple factors
        factors = {}
        
        # Stage-based probability
        stage_probabilities = {
            'prospecting': 10,
            'qualification': 20,
            'needs_analysis': 40,
            'proposal': 60,
            'negotiation': 80,
            'closed_won': 100,
            'closed_lost': 0,
        }
        stage_prob = stage_probabilities.get(opportunity.stage, 30)
        factors['stage'] = stage_prob
        
        # Days in stage (negative if too long)
        days_in_stage = (timezone.now().date() - opportunity.updated_at.date()).days
        if days_in_stage > 30:
            factors['velocity'] = -10
        elif days_in_stage > 14:
            factors['velocity'] = -5
        else:
            factors['velocity'] = 5
        
        # Deal size factor (larger deals need more attention)
        avg_deal_size = Opportunity.objects.filter(
            owner=opportunity.owner,
            is_closed=True,
            stage='closed_won'
        ).aggregate(avg=Avg('amount'))['avg'] or opportunity.amount
        
        if opportunity.amount > float(avg_deal_size) * 2:
            factors['deal_size'] = -5
        else:
            factors['deal_size'] = 5
        
        # Activity level
        try:
            recent_activities = Activity.objects.filter(
                opportunity=opportunity,
                created_at__gte=timezone.now() - timedelta(days=14)
            ).count()
            if recent_activities >= 3:
                factors['engagement'] = 10
            elif recent_activities >= 1:
                factors['engagement'] = 5
            else:
                factors['engagement'] = -10
        except Exception:
            factors['engagement'] = 0
        
        # Calculate final probability
        base_prob = factors['stage']
        adjustments = sum(v for k, v in factors.items() if k != 'stage')
        win_probability = max(5, min(95, base_prob + adjustments))
        
        # Determine risk level
        if win_probability >= 70:
            risk_level = 'low'
        elif win_probability >= 50:
            risk_level = 'medium'
        elif win_probability >= 30:
            risk_level = 'high'
        else:
            risk_level = 'critical'
        
        # Generate risk factors
        risk_factors = []
        if factors['velocity'] < 0:
            risk_factors.append({
                'factor': 'Stalled Deal',
                'description': f'Deal has been in {opportunity.stage} for {days_in_stage} days',
                'impact': 'medium',
            })
        
        if factors.get('engagement', 0) < 0:
            risk_factors.append({
                'factor': 'Low Engagement',
                'description': 'No recent activities logged',
                'impact': 'high',
            })
        
        # Generate recommended actions
        recommended_actions = []
        if factors['velocity'] < 0:
            recommended_actions.append({
                'action': 'Schedule a check-in call',
                'priority': 'high',
                'reason': 'Re-engage the prospect and move the deal forward',
            })
        
        if factors.get('engagement', 0) < 0:
            recommended_actions.append({
                'action': 'Send a value-add email',
                'priority': 'medium',
                'reason': 'Maintain visibility and demonstrate ongoing value',
            })
        
        return {
            'win_probability': win_probability,
            'probability_factors': factors,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'recommended_actions': recommended_actions,
            'deal_health_score': int(win_probability * 0.7 + 30),
            'velocity_score': max(0, 100 + factors['velocity'] * 5),
            'engagement_score': max(0, 50 + factors.get('engagement', 0) * 5),
            'model_version': self.model_version,
            'confidence_score': 0.75,
        }
    
    def batch_analyze(self, opportunities) -> List[Dict[str, Any]]:
        """Analyze multiple deals"""
        return [self.analyze_deal(opp) for opp in opportunities]


class SmartContentGenerator:
    """AI-powered content generation for sales"""
    
    def __init__(self):
        self.openai_available = bool(os.environ.get('OPENAI_API_KEY'))
    
    def generate_content(self, content_type: str, context: Dict,
                        tone: str = 'professional') -> Dict[str, Any]:
        """Generate personalized content"""
        
        generators = {
            'email': self._generate_email,
            'call_script': self._generate_call_script,
            'objection_response': self._generate_objection_response,
            'social_post': self._generate_social_post,
            'linkedin_message': self._generate_linkedin_message,
            'sms': self._generate_sms,
        }
        
        generator = generators.get(content_type, self._generate_generic)
        return generator(context, tone)
    
    def _generate_email(self, context: Dict, tone: str) -> Dict[str, Any]:
        """Generate email content"""
        
        contact_name = context.get('contact_name', 'there')
        company = context.get('company', 'your company')
        
        if self.openai_available:
            return self._ai_generate('email', context, tone)
        
        # Template fallback
        subject = f"Following up on our conversation"
        body = f"""Hi {contact_name},

I hope this email finds you well. I wanted to follow up on our recent conversation about {company}.

[Your personalized message here]

Would you be available for a quick call this week to discuss next steps?

Best regards"""
        
        return {
            'title': subject,
            'content': body,
            'variations': [],
            'personalization_score': 0.3,
            'personalization_elements': ['contact_name', 'company'],
        }
    
    def _generate_call_script(self, context: Dict, tone: str) -> Dict[str, Any]:
        """Generate call script"""
        
        contact_name = context.get('contact_name', 'the prospect')
        
        script = f"""**Opening:**
"Hi, this is [Your Name] from [Company]. How are you today?"

**Purpose:**
"I'm calling because [reason]. Do you have a few minutes to chat?"

**Discovery Questions:**
1. "What challenges are you currently facing with [area]?"
2. "How is that impacting your business?"
3. "What would an ideal solution look like?"

**Value Proposition:**
"Based on what you've shared, I think we can help by [solution]"

**Objection Handling:**
- If busy: "I understand. When would be a better time?"
- If not interested: "I appreciate your honesty. May I ask what's working well for you currently?"

**Close:**
"Based on our conversation, I think it would be valuable to [next step]. Does [date/time] work for you?"
"""
        
        return {
            'title': f'Call Script for {contact_name}',
            'content': script,
            'variations': [],
            'personalization_score': 0.5,
            'personalization_elements': ['contact_name'],
        }
    
    def _generate_objection_response(self, context: Dict, tone: str) -> Dict[str, Any]:
        """Generate objection handling response"""
        
        objection = context.get('objection', 'price concern')
        
        responses = {
            'price': """**When they say "It's too expensive":**

1. **Acknowledge:** "I understand budget is a concern."

2. **Clarify:** "When you say it's too expensive, are you comparing it to something specific, or is it more about the overall investment?"

3. **Reframe:** "Let's look at the ROI. Our customers typically see [X] return within [timeframe]."

4. **Options:** "We do have flexible payment options. Would spreading the investment help?"
""",
            'timing': """**When they say "Not the right time":**

1. **Acknowledge:** "I appreciate you being upfront about timing."

2. **Probe:** "What would need to change for this to become a priority?"

3. **Create urgency:** "Many of our customers felt the same way, but found that [benefit] made it worth prioritizing."

4. **Stay connected:** "What if we schedule a check-in for [future date]?"
""",
        }
        
        # Find matching response
        content = responses.get('price', responses['price'])
        for key, response in responses.items():
            if key in objection.lower():
                content = response
                break
        
        return {
            'title': f'Response to: {objection}',
            'content': content,
            'variations': [],
            'personalization_score': 0.4,
            'personalization_elements': ['objection'],
        }
    
    def _generate_social_post(self, context: Dict, tone: str) -> Dict[str, Any]:
        """Generate social media post"""
        
        topic = context.get('topic', 'sales tips')
        
        post = f"""🚀 {topic.title()}

[Your insight or tip here]

The key takeaway? [Main point]

What's your experience with this? Drop a comment below! 👇

#Sales #SalesTips #B2B #GrowthMindset
"""
        
        return {
            'title': f'Social Post: {topic}',
            'content': post,
            'variations': [],
            'personalization_score': 0.2,
            'personalization_elements': ['topic'],
        }
    
    def _generate_linkedin_message(self, context: Dict, tone: str) -> Dict[str, Any]:
        """Generate LinkedIn message"""
        
        contact_name = context.get('contact_name', 'there')
        
        message = f"""Hi {contact_name},

I came across your profile and was impressed by [specific observation].

I work with [type of companies] to help them [benefit].

Would you be open to a brief conversation about [topic]?

Looking forward to connecting!
"""
        
        return {
            'title': f'LinkedIn Message to {contact_name}',
            'content': message,
            'variations': [],
            'personalization_score': 0.4,
            'personalization_elements': ['contact_name'],
        }
    
    def _generate_sms(self, context: Dict, tone: str) -> Dict[str, Any]:
        """Generate SMS message"""
        
        contact_name = context.get('contact_name', 'Hi')
        
        message = f"""Hi {contact_name}, this is [Your Name] from [Company]. Following up on [topic]. Do you have 5 min to chat today? Reply YES and I'll call you."""
        
        return {
            'title': f'SMS to {contact_name}',
            'content': message,
            'variations': [],
            'personalization_score': 0.3,
            'personalization_elements': ['contact_name'],
        }
    
    def _generate_generic(self, context: Dict, tone: str) -> Dict[str, Any]:
        """Generate generic content"""
        
        return {
            'title': 'Generated Content',
            'content': 'Please specify the content type you need.',
            'variations': [],
            'personalization_score': 0,
            'personalization_elements': [],
        }
    
    def _ai_generate(self, content_type: str, context: Dict, tone: str) -> Dict[str, Any]:
        """Generate content using AI"""
        
        try:
            import openai
            
            prompt = f"""Generate a {tone} {content_type} for a sales professional.

Context:
{json.dumps(context, indent=2)}

Requirements:
- Be concise and professional
- Include personalization where possible
- Focus on value and next steps
"""
            
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert sales copywriter."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7,
            )
            
            content = response.choices[0].message.content
            
            return {
                'title': f'{content_type.replace("_", " ").title()}',
                'content': content,
                'variations': [],
                'personalization_score': 0.8,
                'personalization_elements': list(context.keys()),
            }
        except Exception as e:
            # Fallback to template
            return self._generate_generic(context, tone)
