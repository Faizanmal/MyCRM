"""
Next Best Action recommendation engine
"""
import logging
from datetime import timedelta

from django.utils import timezone

from contact_management.models import Contact
from lead_management.models import Lead
from opportunity_management.models import Opportunity

from .models import NextBestAction

logger = logging.getLogger(__name__)


class NextBestActionEngine:
    """Generate AI-powered next best action recommendations"""

    def __init__(self):
        self.model_version = '1.0'

    def generate_recommendations(self, user, limit=10):
        """Generate personalized recommendations for a user"""
        recommendations = []

        # Get user's entities
        leads = Lead.objects.filter(assigned_to=user)
        contacts = Contact.objects.filter(assigned_to=user)
        opportunities = Opportunity.objects.filter(owner=user)

        # Generate recommendations for each entity type
        recommendations.extend(self._recommend_for_leads(user, leads))
        recommendations.extend(self._recommend_for_contacts(user, contacts))
        recommendations.extend(self._recommend_for_opportunities(user, opportunities))

        # Sort by priority and take top N
        recommendations.sort(key=lambda x: x['priority_score'], reverse=True)
        recommendations = recommendations[:limit]

        # Save to database
        saved_recommendations = []
        for rec in recommendations:
            action, created = NextBestAction.objects.get_or_create(
                user=user,
                entity_type=rec['entity_type'],
                entity_id=rec['entity_id'],
                action_type=rec['action_type'],
                defaults={
                    'title': rec['title'],
                    'description': rec['description'],
                    'reasoning': rec['reasoning'],
                    'priority_score': rec['priority_score'],
                    'expected_impact': rec['expected_impact'],
                    'suggested_timing': rec.get('suggested_timing'),
                    'model_version': self.model_version,
                }
            )
            saved_recommendations.append(action)

        return saved_recommendations

    def _recommend_for_leads(self, user, leads):
        """Generate recommendations for leads"""
        recommendations = []
        now = timezone.now()

        for lead in leads[:20]:  # Limit processing
            # Check for stale leads
            if lead.last_contacted_at:
                days_since_contact = (now - lead.last_contacted_at).days
            else:
                days_since_contact = (now - lead.created_at).days

            # Recommend follow-up for stale leads
            if days_since_contact > 7:
                priority = min(100, days_since_contact * 5)
                recommendations.append({
                    'entity_type': 'lead',
                    'entity_id': lead.id,
                    'action_type': 'follow_up',
                    'title': f'Follow up with {lead.first_name} {lead.last_name}',
                    'description': f'Last contact was {days_since_contact} days ago',
                    'reasoning': f'Lead has not been contacted in {days_since_contact} days. Regular follow-up is crucial for conversion.',
                    'priority_score': priority,
                    'expected_impact': 'high' if days_since_contact > 14 else 'medium',
                    'suggested_timing': now + timedelta(hours=2)
                })

            # Recommend qualification call for new leads
            if lead.status == 'new' and (now - lead.created_at).days < 3:
                recommendations.append({
                    'entity_type': 'lead',
                    'entity_id': lead.id,
                    'action_type': 'call',
                    'title': f'Qualification call with {lead.company_name or lead.first_name}',
                    'description': 'New lead requires qualification',
                    'reasoning': 'Fresh leads should be qualified quickly to maintain momentum.',
                    'priority_score': 80,
                    'expected_impact': 'high',
                    'suggested_timing': now + timedelta(hours=4)
                })

            # Recommend conversion for qualified leads
            if lead.status == 'qualified' and lead.lead_score > 70:
                recommendations.append({
                    'entity_type': 'lead',
                    'entity_id': lead.id,
                    'action_type': 'proposal',
                    'title': f'Send proposal to {lead.company_name}',
                    'description': f'High-score lead (score: {lead.lead_score}) ready for proposal',
                    'reasoning': f'Lead score of {lead.lead_score} indicates strong potential. Time to send proposal.',
                    'priority_score': 90,
                    'expected_impact': 'high',
                    'suggested_timing': now + timedelta(days=1)
                })

        return recommendations

    def _recommend_for_contacts(self, user, contacts):
        """Generate recommendations for contacts"""
        recommendations = []
        now = timezone.now()

        for contact in contacts[:20]:
            # Recommend check-in for customers with no recent activity
            days_since_activity = 999
            if contact.last_contacted_at:
                days_since_activity = (now - contact.last_contacted_at).days

            if contact.contact_type == 'customer' and days_since_activity > 30:
                priority = min(100, days_since_activity * 2)
                recommendations.append({
                    'entity_type': 'contact',
                    'entity_id': contact.id,
                    'action_type': 'check_in',
                    'title': f'Customer check-in: {contact.first_name} {contact.last_name}',
                    'description': f'No contact in {days_since_activity} days',
                    'reasoning': 'Regular customer check-ins improve retention and reveal upsell opportunities.',
                    'priority_score': priority,
                    'expected_impact': 'high' if days_since_activity > 60 else 'medium',
                    'suggested_timing': now + timedelta(days=1)
                })

            # Recommend upsell for customers with no recent opportunities
            if contact.contact_type == 'customer':
                recent_opps = contact.opportunities.filter(
                    created_at__gte=now - timedelta(days=90)
                ).count()

                if recent_opps == 0:
                    recommendations.append({
                        'entity_type': 'contact',
                        'entity_id': contact.id,
                        'action_type': 'upsell',
                        'title': f'Explore upsell with {contact.company_name}',
                        'description': 'No recent opportunities for existing customer',
                        'reasoning': 'Existing customers with no recent deals are prime for upsell/cross-sell.',
                        'priority_score': 75,
                        'expected_impact': 'high',
                        'suggested_timing': now + timedelta(days=2)
                    })

        return recommendations

    def _recommend_for_opportunities(self, user, opportunities):
        """Generate recommendations for opportunities"""
        recommendations = []
        now = timezone.now()

        for opp in opportunities.filter(stage__in=['prospecting', 'qualification', 'proposal']):
            # Calculate days in current stage
            days_in_stage = (now - opp.updated_at).days

            # Recommend action for stalled opportunities
            if days_in_stage > 14:
                priority = min(100, 50 + days_in_stage * 3)
                recommendations.append({
                    'entity_type': 'opportunity',
                    'entity_id': opp.id,
                    'action_type': 'follow_up',
                    'title': f'Follow up on stalled deal: {opp.name}',
                    'description': f'Deal has been in {opp.stage} stage for {days_in_stage} days',
                    'reasoning': f'Opportunity stagnating in {opp.stage}. Action needed to move forward or close.',
                    'priority_score': priority,
                    'expected_impact': 'high',
                    'suggested_timing': now + timedelta(hours=12)
                })

            # Recommend proposal for qualified opportunities
            if opp.stage == 'qualification' and opp.probability > 50:
                recommendations.append({
                    'entity_type': 'opportunity',
                    'entity_id': opp.id,
                    'action_type': 'proposal',
                    'title': f'Send proposal for {opp.name}',
                    'description': f'High probability deal ({opp.probability}%) ready for proposal',
                    'reasoning': 'Qualified opportunity with good probability. Time to send formal proposal.',
                    'priority_score': 85,
                    'expected_impact': 'high',
                    'suggested_timing': now + timedelta(days=1)
                })

            # Recommend discount for deals close to closing
            if opp.stage == 'proposal' and opp.close_date:
                days_to_close = (opp.close_date - now.date()).days
                if 0 < days_to_close < 7:
                    recommendations.append({
                        'entity_type': 'opportunity',
                        'entity_id': opp.id,
                        'action_type': 'discount',
                        'title': f'Consider incentive for {opp.name}',
                        'description': f'Deal closes in {days_to_close} days',
                        'reasoning': 'Deal approaching close date. Strategic discount might secure the win.',
                        'priority_score': 70,
                        'expected_impact': 'medium',
                        'suggested_timing': now + timedelta(hours=24)
                    })

        return recommendations

    def accept_recommendation(self, action_id):
        """Mark recommendation as accepted"""
        try:
            action = NextBestAction.objects.get(id=action_id)
            action.status = 'accepted'
            action.save()
            return action
        except NextBestAction.DoesNotExist:
            return None

    def complete_recommendation(self, action_id):
        """Mark recommendation as completed"""
        try:
            action = NextBestAction.objects.get(id=action_id)
            action.status = 'completed'
            action.completed_at = timezone.now()
            action.save()
            return action
        except NextBestAction.DoesNotExist:
            return None

    def dismiss_recommendation(self, action_id):
        """Dismiss a recommendation"""
        try:
            action = NextBestAction.objects.get(id=action_id)
            action.status = 'dismissed'
            action.save()
            return action
        except NextBestAction.DoesNotExist:
            return None
