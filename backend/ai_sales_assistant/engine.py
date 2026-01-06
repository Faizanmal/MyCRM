"""
AI Sales Assistant Engine
The brain behind all AI-powered sales features
"""

import json
import os

from django.utils import timezone


class AIEmailGenerator:
    """Generate personalized sales emails using AI"""

    EMAIL_TEMPLATES = {
        'cold_outreach': {
            'structure': ['hook', 'value_prop', 'social_proof', 'cta'],
            'max_length': 150,
            'tone_guide': 'Direct but friendly, focus on their pain points'
        },
        'follow_up': {
            'structure': ['reference_previous', 'new_value', 'urgency', 'cta'],
            'max_length': 100,
            'tone_guide': 'Persistent but respectful'
        },
        'proposal': {
            'structure': ['summary', 'solution_overview', 'benefits', 'next_steps'],
            'max_length': 300,
            'tone_guide': 'Professional and comprehensive'
        },
        'meeting_request': {
            'structure': ['context', 'value_proposition', 'specific_ask', 'flexibility'],
            'max_length': 100,
            'tone_guide': 'Respectful of their time'
        },
        'thank_you': {
            'structure': ['gratitude', 'recap_value', 'next_steps', 'availability'],
            'max_length': 100,
            'tone_guide': 'Warm and professional'
        },
        'objection_handling': {
            'structure': ['acknowledge', 'reframe', 'evidence', 'bridge'],
            'max_length': 150,
            'tone_guide': 'Empathetic but confident'
        },
    }

    def __init__(self):
        self.openai_available = bool(os.environ.get('OPENAI_API_KEY'))

    def generate_email(self, email_type, contact, opportunity=None, context='',
                       key_points=None, tone='professional'):
        """Generate a personalized email"""
        from .models import AIEmailDraft

        # Build context from CRM data
        crm_context = self._build_context(contact, opportunity)

        # Generate email using AI or fallback templates
        if self.openai_available:
            subject, body, variations = self._generate_with_ai(
                email_type, crm_context, context, key_points, tone
            )
        else:
            subject, body, variations = self._generate_with_templates(
                email_type, crm_context, context, key_points, tone
            )

        # Save draft
        draft = AIEmailDraft.objects.create(
            user=contact.assigned_to or contact.created_by,
            contact=contact,
            opportunity=opportunity,
            email_type=email_type,
            tone=tone,
            context=context,
            key_points=key_points or [],
            subject=subject,
            body=body,
            variations=variations
        )

        return draft

    def _build_context(self, contact, opportunity):
        """Build context dictionary from CRM data"""
        context = {
            'contact': {
                'first_name': contact.first_name,
                'last_name': contact.last_name,
                'full_name': contact.full_name,
                'company': contact.company_name or 'your company',
                'title': contact.job_title or '',
                'email': contact.email,
            }
        }

        if opportunity:
            context['opportunity'] = {
                'name': opportunity.name,
                'value': float(opportunity.amount),
                'stage': opportunity.stage,
                'days_in_pipeline': (timezone.now().date() - opportunity.created_at.date()).days,
            }

        # Add activity history
        recent_activities = []
        if hasattr(contact, 'tracked_emails'):
            recent_emails = contact.tracked_emails.order_by('-sent_at')[:3]
            for email in recent_emails:
                recent_activities.append({
                    'type': 'email',
                    'subject': email.subject,
                    'opened': email.open_count > 0,
                    'clicked': email.click_count > 0,
                })

        context['recent_activities'] = recent_activities

        return context

    def _generate_with_ai(self, email_type, crm_context, user_context, key_points, tone):
        """Generate using OpenAI API"""
        try:
            import openai

            template_info = self.EMAIL_TEMPLATES.get(email_type, self.EMAIL_TEMPLATES['cold_outreach'])

            prompt = f"""Generate a sales email with the following parameters:

Type: {email_type}
Tone: {tone}
Tone Guide: {template_info['tone_guide']}
Max Length: {template_info['max_length']} words

Contact Info:
- Name: {crm_context['contact']['full_name']}
- Company: {crm_context['contact']['company']}
- Title: {crm_context['contact']['title']}

{'Opportunity: ' + crm_context.get('opportunity', {}).get('name', '') if crm_context.get('opportunity') else ''}

Additional Context: {user_context}

Key Points to Include: {', '.join(key_points) if key_points else 'None specified'}

Structure: {' → '.join(template_info['structure'])}

Return a JSON object with:
- subject: Email subject line
- body: Email body (use {{first_name}} for personalization)
- variations: Array of 2 alternative subject lines
"""

            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert sales copywriter. Generate compelling, personalized sales emails."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            return (
                result.get('subject', 'Follow up'),
                result.get('body', ''),
                result.get('variations', [])
            )

        except Exception:
            # Fallback to templates
            return self._generate_with_templates(email_type, crm_context, user_context, key_points, tone)

    def _generate_with_templates(self, email_type, crm_context, user_context, key_points, tone):
        """Generate using pre-built templates"""
        contact = crm_context['contact']
        first_name = contact['first_name']
        company = contact['company']

        templates = {
            'cold_outreach': {
                'subject': f"Quick question for {company}",
                'body': f"""Hi {first_name},

I noticed {company} is growing rapidly, and I wanted to reach out because we've helped similar companies streamline their sales processes.

Would you be open to a quick 15-minute call to explore if we might be able to help?

Best regards"""
            },
            'follow_up': {
                'subject': f"Following up - {company}",
                'body': f"""Hi {first_name},

I wanted to follow up on my previous message. I understand you're busy, but I believe we could provide significant value to {company}.

Do you have 10 minutes this week for a quick chat?

Best regards"""
            },
            'meeting_request': {
                'subject': "Can we schedule 15 minutes?",
                'body': f"""Hi {first_name},

I'd love to learn more about {company}'s current challenges and share how we've helped similar organizations.

Would you have 15 minutes this week or next for a brief call? I'm flexible on timing.

Looking forward to connecting,"""
            },
            'thank_you': {
                'subject': f"Thank you, {first_name}!",
                'body': f"""Hi {first_name},

Thank you for taking the time to speak with me today. I really enjoyed learning more about {company} and your goals.

As discussed, I'll follow up with [next steps].

Please don't hesitate to reach out if you have any questions.

Best regards"""
            },
            'proposal': {
                'subject': f"Proposal for {company}",
                'body': f"""Hi {first_name},

Thank you for the opportunity to propose our solution for {company}.

Based on our discussions, I've put together a comprehensive proposal that addresses your key requirements:

[Key points would go here]

I'd love to schedule a call to walk you through the details and answer any questions.

Best regards"""
            },
        }

        template = templates.get(email_type, templates['cold_outreach'])

        # Add key points if provided
        body = template['body']
        if key_points:
            points_text = '\n'.join([f"• {point}" for point in key_points])
            body = body.replace('[Key points would go here]', points_text)

        variations = [
            f"Connecting with {first_name} at {company}",
            f"A quick idea for {company}",
        ]

        return template['subject'], body, variations


class SalesCoachEngine:
    """AI-powered sales coaching and advice"""

    def analyze_deal(self, opportunity):
        """Analyze a deal and provide coaching advice"""
        from .models import SalesCoachAdvice

        advice_items = []

        # Check deal age and stage progression
        deal_age = (timezone.now().date() - opportunity.created_at.date()).days

        if opportunity.stage == 'prospecting' and deal_age > 14:
            advice_items.append({
                'advice_type': 'deal_strategy',
                'title': 'Deal stuck in prospecting',
                'advice': f'This deal has been in prospecting for {deal_age} days. Consider scheduling a discovery call to move it forward.',
                'reasoning': 'Deals that stay in prospecting too long often go cold. Average time in prospecting should be 7-10 days.',
                'priority': 'high',
                'action_items': [
                    'Schedule a discovery call within 48 hours',
                    'Prepare qualification questions',
                    'Research the company before the call'
                ]
            })

        # Check for missing decision maker
        contact = opportunity.contact
        title = (contact.job_title or '').lower()
        is_decision_maker = any(t in title for t in ['ceo', 'cfo', 'cto', 'vp', 'director', 'head'])

        if not is_decision_maker and opportunity.amount >= 25000:
            advice_items.append({
                'advice_type': 'stakeholder_engagement',
                'title': 'Get executive buy-in',
                'advice': 'For a deal of this size, you likely need executive sponsorship. Consider asking for an introduction to the decision maker.',
                'reasoning': 'Deals over $25k typically require C-level or VP approval. Having a champion but no executive sponsor is risky.',
                'priority': 'high',
                'action_items': [
                    f'Ask {contact.first_name} who else needs to be involved in the decision',
                    'Request an introduction to the budget owner',
                    'Prepare executive-level value proposition'
                ]
            })

        # Check for stale activity
        if opportunity.last_activity_date:
            days_since_activity = (timezone.now() - opportunity.last_activity_date).days

            if days_since_activity >= 7:
                advice_items.append({
                    'advice_type': 'timing_suggestion',
                    'title': 'Re-engage this deal',
                    'advice': f'No activity in {days_since_activity} days. Reach out with new value to prevent the deal from going cold.',
                    'reasoning': 'Deals with gaps longer than 7 days have significantly lower close rates.',
                    'priority': 'critical' if days_since_activity >= 14 else 'high',
                    'action_items': [
                        'Send a value-add email (case study, relevant article)',
                        'Propose a quick check-in call',
                        'Share a new feature or update relevant to their needs'
                    ]
                })

        # Check close date
        if opportunity.expected_close_date:
            days_to_close = (opportunity.expected_close_date - timezone.now().date()).days

            if days_to_close < 0:
                advice_items.append({
                    'advice_type': 'timing_suggestion',
                    'title': 'Overdue close date',
                    'advice': 'This deal has passed its expected close date. Have an honest conversation about the timeline.',
                    'reasoning': 'Accurate forecasting requires realistic close dates. Understanding the real timeline helps with pipeline planning.',
                    'priority': 'high',
                    'action_items': [
                        'Schedule a call to discuss next steps',
                        'Ask directly what needs to happen to close',
                        'Update the close date based on their feedback'
                    ]
                })
            elif days_to_close <= 7 and opportunity.stage in ['prospecting', 'qualification']:
                advice_items.append({
                    'advice_type': 'risk_mitigation',
                    'title': 'Timeline at risk',
                    'advice': f'Close date is in {days_to_close} days but deal is still in {opportunity.stage}. This timeline may be unrealistic.',
                    'reasoning': 'Deals typically need 2+ weeks in proposal/negotiation stages before closing.',
                    'priority': 'medium',
                    'action_items': [
                        'Reassess the close date',
                        'Identify what is needed to accelerate',
                        'Consider if there are blockers you have not identified'
                    ]
                })

        # Save advice items
        for item_data in advice_items:
            SalesCoachAdvice.objects.create(
                user=opportunity.owner or opportunity.assigned_to,
                opportunity=opportunity,
                **item_data
            )

        return advice_items

    def get_objection_response(self, objection_text, contact=None, opportunity=None):
        """Get suggested response to an objection"""
        from .models import ObjectionResponse

        # Simple keyword matching (could be enhanced with NLP)
        objection_lower = objection_text.lower()

        # Find matching objection responses
        responses = ObjectionResponse.objects.filter(is_system=True)

        for response in responses:
            for keyword in response.keywords:
                if keyword.lower() in objection_lower:
                    response.times_used += 1
                    response.save()
                    return response

        # Generate generic response if no match
        if 'price' in objection_lower or 'expensive' in objection_lower or 'budget' in objection_lower:
            return {
                'category': 'price',
                'best_response': "I understand budget is a concern. Let's focus on the ROI - based on what you've shared, our customers typically see a 3x return within the first year. Would it help if we looked at the numbers together?",
                'follow_up_questions': [
                    "What would the ideal ROI look like for you?",
                    "What's the cost of not solving this problem?"
                ]
            }

        if 'time' in objection_lower or 'busy' in objection_lower or 'later' in objection_lower:
            return {
                'category': 'timing',
                'best_response': "I completely understand. Quick question - if timing weren't a constraint, is this something you'd want to move forward with? I ask because many of our customers felt the same way, but found that starting now actually saved them time in the long run.",
                'follow_up_questions': [
                    "What would need to change for this to become a priority?",
                    "When would be a better time to revisit this?"
                ]
            }

        if 'competitor' in objection_lower or 'alternative' in objection_lower:
            return {
                'category': 'competitor',
                'best_response': "That's great that you're doing your due diligence. What specific criteria are you using to evaluate options? I'd love to understand what matters most to you so I can show you how we compare.",
                'follow_up_questions': [
                    "What do you like most about the alternative you're considering?",
                    "What would make this an easy decision for you?"
                ]
            }

        return {
            'category': 'other',
            'best_response': "That's a fair point. Help me understand more - what's driving that concern?",
            'follow_up_questions': [
                "What would need to be true for you to feel confident moving forward?",
                "Is there anything else holding you back?"
            ]
        }


class PersonaMatchingEngine:
    """Match contacts to buyer personas"""

    def match_contact_to_personas(self, contact):
        """Find best matching personas for a contact"""
        from .models import ContactPersonaMatch, PersonaProfile

        personas = PersonaProfile.objects.all()
        matches = []

        for persona in personas:
            score, factors = self._calculate_match_score(contact, persona)

            if score >= 30:  # Minimum threshold
                matches.append({
                    'persona': persona,
                    'score': score,
                    'factors': factors
                })

        # Sort by score
        matches.sort(key=lambda x: x['score'], reverse=True)

        # Save top matches
        for match in matches[:3]:  # Top 3
            ContactPersonaMatch.objects.update_or_create(
                contact=contact,
                persona=match['persona'],
                defaults={
                    'confidence_score': match['score'],
                    'matching_factors': match['factors'],
                    'recommended_approach': self._generate_approach(match['persona']),
                    'talking_points': match['persona'].key_value_props[:5]
                }
            )

            # Update persona stats
            match['persona'].contacts_matched += 1
            match['persona'].save()

        return matches

    def _calculate_match_score(self, contact, persona):
        """Calculate how well a contact matches a persona"""
        score = 0
        factors = []

        # Title match
        if contact.job_title:
            title_lower = contact.job_title.lower()
            for typical_title in persona.typical_titles:
                if typical_title.lower() in title_lower:
                    score += 30
                    factors.append(f"Title match: {typical_title}")
                    break

        # Industry match (if we had industry on contact)
        # For now, use company name heuristics

        # Seniority indicators
        title = (contact.job_title or '').lower()
        if any(t in title for t in ['ceo', 'cfo', 'cto', 'president', 'founder']):
            if 'C-Level' in str(persona.typical_titles):
                score += 25
                factors.append("Executive level match")
        elif any(t in title for t in ['vp', 'vice president', 'director']):
            if 'VP' in str(persona.typical_titles) or 'Director' in str(persona.typical_titles):
                score += 20
                factors.append("Senior management match")
        elif 'manager' in title and 'Manager' in str(persona.typical_titles):
            score += 15
            factors.append("Management level match")

        # Department indicators
        if 'sales' in title and 'sales' in persona.name.lower():
            score += 20
            factors.append("Department match: Sales")
        elif 'marketing' in title and 'marketing' in persona.name.lower():
            score += 20
            factors.append("Department match: Marketing")
        elif 'technical' in title or 'engineer' in title or 'developer' in title:
            if 'technical' in persona.name.lower():
                score += 20
                factors.append("Department match: Technical")

        return min(score, 100), factors

    def _generate_approach(self, persona):
        """Generate recommended approach based on persona"""
        approach_parts = []

        if persona.communication_style:
            approach_parts.append(f"Communication: {persona.communication_style}")

        if persona.motivations:
            approach_parts.append(f"Focus on: {', '.join(persona.motivations[:2])}")

        if persona.things_to_avoid:
            approach_parts.append(f"Avoid: {', '.join(persona.things_to_avoid[:2])}")

        return ' | '.join(approach_parts) if approach_parts else "Use standard professional approach"
