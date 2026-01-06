"""
AI Lead Routing Engine
Intelligent matching algorithm for optimal lead-to-rep assignment
"""

import logging
import random
from decimal import Decimal
from typing import Any, Optional

from django.utils import timezone

logger = logging.getLogger(__name__)


class AILeadRouter:
    """AI-powered lead routing engine"""

    # Scoring weights for different factors
    DEFAULT_WEIGHTS = {
        'skill_match': 25,
        'industry_match': 20,
        'performance': 20,
        'capacity': 15,
        'territory': 10,
        'deal_size_fit': 10,
    }

    def __init__(self, weights: dict[str, int] | None = None):
        self.weights = weights or self.DEFAULT_WEIGHTS

    def find_best_rep(
        self,
        lead_data: dict[str, Any],
        available_reps: list,
        routing_rule: Optional['RoutingRule'] = None
    ) -> tuple[Any | None, dict[str, Any]]:
        """
        Find the best rep for a lead using AI scoring

        Args:
            lead_data: Lead information for matching
            available_reps: List of SalesRepProfile objects
            routing_rule: Optional routing rule to apply

        Returns:
            Tuple of (best_rep, match_details)
        """
        if not available_reps:
            return None, {'error': 'No available reps'}

        scores = []

        for rep in available_reps:
            score, factors = self._calculate_match_score(lead_data, rep)
            scores.append({
                'rep': rep,
                'score': score,
                'factors': factors
            })

        # Sort by score descending
        scores.sort(key=lambda x: x['score'], reverse=True)

        best_match = scores[0]

        return best_match['rep'], {
            'score': best_match['score'],
            'factors': best_match['factors'],
            'alternatives': [
                {'rep_id': str(s['rep'].id), 'score': s['score']}
                for s in scores[1:4]  # Top 3 alternatives
            ]
        }

    def _calculate_match_score(
        self,
        lead_data: dict[str, Any],
        rep: 'SalesRepProfile'
    ) -> tuple[float, dict[str, float]]:
        """Calculate match score between lead and rep"""
        factors = {}

        # Skill match score
        factors['skill_match'] = self._score_skill_match(lead_data, rep)

        # Industry match score
        factors['industry_match'] = self._score_industry_match(lead_data, rep)

        # Performance score
        factors['performance'] = self._score_performance(rep)

        # Capacity score
        factors['capacity'] = self._score_capacity(rep)

        # Territory score
        factors['territory'] = self._score_territory_match(lead_data, rep)

        # Deal size fit score
        factors['deal_size_fit'] = self._score_deal_size_fit(lead_data, rep)

        # Calculate weighted total
        total_weight = sum(self.weights.values())
        total_score = sum(
            factors[key] * (self.weights.get(key, 0) / total_weight)
            for key in factors
        )

        return round(total_score, 2), factors

    def _score_skill_match(self, lead_data: dict, rep: 'SalesRepProfile') -> float:
        """Score based on skill/certification match"""
        score = 50.0  # Base score

        required_skills = lead_data.get('required_skills', [])
        rep_certifications = rep.certifications or []

        if required_skills:
            matched = sum(1 for skill in required_skills if skill in rep_certifications)
            score += (matched / len(required_skills)) * 50
        else:
            # No specific requirements, give bonus for expertise
            if rep.expertise_level == 'expert':
                score += 30
            elif rep.expertise_level == 'advanced':
                score += 20
            elif rep.expertise_level == 'intermediate':
                score += 10

        return min(score, 100)

    def _score_industry_match(self, lead_data: dict, rep: 'SalesRepProfile') -> float:
        """Score based on industry expertise"""
        score = 40.0  # Base score

        lead_industry = lead_data.get('industry', '').lower()
        rep_industries = [i.lower() for i in (rep.industries or [])]

        if lead_industry:
            if lead_industry in rep_industries:
                score = 100.0
            elif any(ind in lead_industry or lead_industry in ind for ind in rep_industries):
                score = 75.0

        return score

    def _score_performance(self, rep: 'SalesRepProfile') -> float:
        """Score based on historical performance"""
        # Weighted combination of metrics
        win_rate_score = float(rep.win_rate) * 100 if rep.win_rate else 50

        # Response time score (faster is better)
        if rep.response_time_minutes > 0:
            response_score = max(0, 100 - (rep.response_time_minutes / 60) * 10)
        else:
            response_score = 50

        # Customer satisfaction score
        satisfaction_score = float(rep.customer_satisfaction) * 20 if rep.customer_satisfaction else 50

        # Combined score
        score = (
            win_rate_score * 0.4 +
            response_score * 0.3 +
            satisfaction_score * 0.3
        )

        return min(max(score, 0), 100)

    def _score_capacity(self, rep: 'SalesRepProfile') -> float:
        """Score based on current capacity"""
        if rep.is_at_capacity:
            return 0

        if not rep.is_available:
            return 10

        # Higher score for more available capacity
        utilization = rep.capacity_utilization

        if utilization < 50:
            return 100
        elif utilization < 70:
            return 80
        elif utilization < 85:
            return 60
        elif utilization < 95:
            return 40
        else:
            return 20

    def _score_territory_match(self, lead_data: dict, rep: 'SalesRepProfile') -> float:
        """Score based on geographic territory match"""
        score = 50.0  # Base score

        lead_country = lead_data.get('country', '').lower()
        lead_region = lead_data.get('region', '').lower()

        rep_countries = [c.lower() for c in (rep.countries or [])]
        rep_regions = [r.lower() for r in (rep.regions or [])]

        if lead_country and lead_country in rep_countries:
            score += 30

        if lead_region and lead_region in rep_regions:
            score += 20

        # Timezone match
        lead_tz = lead_data.get('timezone', '')
        if lead_tz and lead_tz in (rep.timezones or []):
            score += 10

        return min(score, 100)

    def _score_deal_size_fit(self, lead_data: dict, rep: 'SalesRepProfile') -> float:
        """Score based on deal size fit"""
        estimated_value = lead_data.get('estimated_value', 0)

        if not estimated_value:
            return 60  # Default score when unknown

        # Check if within rep's range
        if rep.min_deal_size <= estimated_value <= rep.max_deal_size:
            # Closer to preferred deal size = higher score
            if rep.preferred_deal_size:
                diff_ratio = abs(estimated_value - float(rep.preferred_deal_size)) / float(rep.preferred_deal_size)
                return max(50, 100 - (diff_ratio * 50))
            return 80

        # Outside range
        if estimated_value < rep.min_deal_size:
            return 30
        else:  # Above max
            return 40

    def calculate_lead_priority(self, lead_data: dict[str, Any]) -> dict[str, Any]:
        """Calculate lead priority for routing order"""
        priority_score = 50.0
        factors = {}

        # Lead score
        lead_score = lead_data.get('lead_score', 0)
        if lead_score >= 80:
            factors['lead_score'] = 100
            priority_score += 20
        elif lead_score >= 60:
            factors['lead_score'] = 75
            priority_score += 10
        elif lead_score >= 40:
            factors['lead_score'] = 50
        else:
            factors['lead_score'] = 25
            priority_score -= 10

        # Deal size
        estimated_value = lead_data.get('estimated_value', 0)
        if estimated_value >= 100000:
            factors['deal_size'] = 100
            priority_score += 15
        elif estimated_value >= 50000:
            factors['deal_size'] = 75
            priority_score += 10
        elif estimated_value >= 10000:
            factors['deal_size'] = 50
        else:
            factors['deal_size'] = 25

        # Time sensitivity
        if lead_data.get('is_time_sensitive'):
            factors['urgency'] = 100
            priority_score += 15

        # Source quality
        high_quality_sources = ['referral', 'demo_request', 'inbound_qualified']
        if lead_data.get('source', '').lower() in high_quality_sources:
            factors['source_quality'] = 100
            priority_score += 10

        tier = 'hot' if priority_score >= 80 else ('warm' if priority_score >= 60 else 'standard')

        return {
            'priority_score': round(priority_score, 2),
            'tier': tier,
            'factors': factors
        }

    def recommend_escalation(
        self,
        lead_data: dict[str, Any],
        assignment_data: dict[str, Any],
        escalation_rules: list
    ) -> dict[str, Any] | None:
        """Determine if lead should be escalated"""
        for rule in escalation_rules:
            if self._should_escalate(lead_data, assignment_data, rule):
                return {
                    'should_escalate': True,
                    'rule_id': str(rule.id),
                    'rule_name': rule.name,
                    'reason': rule.trigger_type
                }

        return {'should_escalate': False}

    def _should_escalate(
        self,
        lead_data: dict,
        assignment_data: dict,
        rule: 'EscalationRule'
    ) -> bool:
        """Check if escalation rule applies"""
        config = rule.trigger_config

        if rule.trigger_type == 'lead_score':
            threshold = config.get('threshold', 80)
            return lead_data.get('lead_score', 0) >= threshold

        elif rule.trigger_type == 'no_response':
            hours = rule.wait_hours
            assigned_at = assignment_data.get('assigned_at')
            if assigned_at:
                elapsed = (timezone.now() - assigned_at).total_seconds() / 3600
                return elapsed >= hours and not assignment_data.get('first_response_at')

        elif rule.trigger_type == 'deal_size':
            threshold = config.get('threshold', 50000)
            return lead_data.get('estimated_value', 0) >= threshold

        elif rule.trigger_type == 'vip_customer':
            return lead_data.get('is_vip', False)

        elif rule.trigger_type == 'time_sensitive':
            return lead_data.get('is_time_sensitive', False)

        return False


class RoundRobinRouter:
    """Intelligent round-robin routing with weights"""

    def __init__(self):
        self.ai_router = AILeadRouter()

    def get_next_rep(
        self,
        available_reps: list['SalesRepProfile'],
        lead_data: dict | None = None,
        consider_weights: bool = True
    ) -> tuple[Optional['SalesRepProfile'], dict[str, Any]]:
        """Get next rep in round-robin rotation"""
        if not available_reps:
            return None, {'error': 'No available reps'}

        # Filter by availability and capacity
        eligible_reps = [
            rep for rep in available_reps
            if rep.is_available and not rep.is_at_capacity
        ]

        if not eligible_reps:
            # Fall back to any available rep
            eligible_reps = [rep for rep in available_reps if rep.is_available]

        if not eligible_reps:
            return None, {'error': 'No eligible reps'}

        if consider_weights:
            # Weighted round-robin
            selected = self._weighted_selection(eligible_reps)
        else:
            # Simple round-robin by last assignment
            selected = min(eligible_reps, key=lambda r: r.last_assignment_at or timezone.now())

        # Calculate match score if lead data provided
        match_details = {}
        if lead_data:
            _, match_details = self.ai_router._calculate_match_score(lead_data, selected)

        return selected, {
            'method': 'weighted_round_robin' if consider_weights else 'simple_round_robin',
            'factors': match_details
        }

    def _weighted_selection(self, reps: list['SalesRepProfile']) -> 'SalesRepProfile':
        """Select rep based on weights and last assignment"""
        # Calculate effective weights
        now = timezone.now()
        weights = []

        for rep in reps:
            base_weight = rep.assignment_weight

            # Reduce weight for recently assigned reps
            if rep.last_assignment_at:
                hours_since = (now - rep.last_assignment_at).total_seconds() / 3600
                recency_factor = min(1.0, hours_since / 24)  # Full weight after 24h
            else:
                recency_factor = 1.0

            # Reduce weight for reps at high capacity
            capacity_factor = 1.0 - (rep.capacity_utilization / 100) * 0.5

            effective_weight = base_weight * recency_factor * capacity_factor
            weights.append((rep, max(effective_weight, 1)))

        # Weighted random selection
        total = sum(w for _, w in weights)
        r = random.uniform(0, total)

        cumulative = 0
        for rep, weight in weights:
            cumulative += weight
            if r <= cumulative:
                return rep

        return reps[0]


class LeadRebalancer:
    """Service for rebalancing leads among reps"""

    def __init__(self):
        self.ai_router = AILeadRouter()

    def analyze_distribution(
        self,
        reps: list['SalesRepProfile']
    ) -> dict[str, Any]:
        """Analyze current lead distribution"""
        if not reps:
            return {'error': 'No reps provided'}

        lead_counts = [rep.current_lead_count for rep in reps]

        avg_leads = sum(lead_counts) / len(lead_counts) if lead_counts else 0
        max_leads = max(lead_counts) if lead_counts else 0
        min_leads = min(lead_counts) if lead_counts else 0

        # Calculate standard deviation
        if len(lead_counts) > 1:
            variance = sum((x - avg_leads) ** 2 for x in lead_counts) / len(lead_counts)
            std_dev = variance ** 0.5
        else:
            std_dev = 0

        # Identify imbalance
        imbalanced_reps = []
        for rep in reps:
            if rep.current_lead_count > avg_leads + std_dev:
                imbalanced_reps.append({
                    'rep_id': str(rep.id),
                    'rep_name': rep.user.get_full_name(),
                    'status': 'overloaded',
                    'current': rep.current_lead_count,
                    'target': round(avg_leads)
                })
            elif rep.current_lead_count < avg_leads - std_dev:
                imbalanced_reps.append({
                    'rep_id': str(rep.id),
                    'rep_name': rep.user.get_full_name(),
                    'status': 'underloaded',
                    'current': rep.current_lead_count,
                    'target': round(avg_leads)
                })

        return {
            'total_leads': sum(lead_counts),
            'total_reps': len(reps),
            'avg_leads_per_rep': round(avg_leads, 1),
            'max_leads': max_leads,
            'min_leads': min_leads,
            'std_deviation': round(std_dev, 2),
            'imbalance_ratio': round((max_leads - min_leads) / max(avg_leads, 1), 2),
            'imbalanced_reps': imbalanced_reps,
            'needs_rebalancing': len(imbalanced_reps) > 0
        }

    def calculate_rebalancing_plan(
        self,
        reps: list['SalesRepProfile'],
        leads: list
    ) -> dict[str, Any]:
        """Calculate optimal rebalancing plan"""
        analysis = self.analyze_distribution(reps)

        if not analysis.get('needs_rebalancing'):
            return {'movements': [], 'message': 'Distribution is balanced'}

        movements = []
        target_per_rep = analysis['avg_leads_per_rep']

        # Sort reps by current load
        overloaded = [r for r in reps if r.current_lead_count > target_per_rep + 1]
        underloaded = [r for r in reps if r.current_lead_count < target_per_rep - 1]

        # Match leads from overloaded to underloaded reps
        for source_rep in overloaded:
            excess = source_rep.current_lead_count - round(target_per_rep)
            source_leads = [l for l in leads if l.assigned_to_id == source_rep.user_id]

            for _i, lead in enumerate(source_leads[:excess]):
                if not underloaded:
                    break

                # Find best match among underloaded reps
                lead_data = {
                    'industry': getattr(lead, 'industry', ''),
                    'estimated_value': float(lead.estimated_value) if lead.estimated_value else 0,
                    'country': getattr(lead, 'country', ''),
                }

                best_target = None
                best_score = 0

                for target_rep in underloaded:
                    if target_rep.current_lead_count >= round(target_per_rep):
                        continue

                    score, _ = self.ai_router._calculate_match_score(lead_data, target_rep)
                    if score > best_score:
                        best_score = score
                        best_target = target_rep

                if best_target:
                    movements.append({
                        'lead_id': lead.id,
                        'from_rep_id': source_rep.user_id,
                        'from_rep_name': source_rep.user.get_full_name(),
                        'to_rep_id': best_target.user_id,
                        'to_rep_name': best_target.user.get_full_name(),
                        'match_score': best_score
                    })

                    # Update counts for next iteration
                    best_target.current_lead_count += 1

                    # Remove from underloaded if at target
                    if best_target.current_lead_count >= round(target_per_rep):
                        underloaded.remove(best_target)

        return {
            'movements': movements,
            'total_movements': len(movements),
            'before': {r.user.get_full_name(): r.current_lead_count for r in reps},
            'estimated_improvement': analysis['imbalance_ratio'] - (len(movements) * 0.1)
        }

    def execute_rebalancing(
        self,
        plan: dict[str, Any],
        triggered_by: Optional['User'] = None,
        reason: str = 'manual'
    ) -> dict[str, Any]:
        """Execute a rebalancing plan"""
        from django.contrib.auth import get_user_model

        from lead_management.models import Lead

        from .models import LeadAssignment, RebalancingEvent

        User = get_user_model()

        movements = plan.get('movements', [])
        if not movements:
            return {'success': False, 'message': 'No movements to execute'}

        # Create rebalancing event
        event = RebalancingEvent.objects.create(
            trigger_reason=reason,
            triggered_by=triggered_by,
            before_distribution=plan.get('before', {}),
            movements=movements
        )

        successful = 0
        failed = 0

        for movement in movements:
            try:
                lead = Lead.objects.get(id=movement['lead_id'])
                new_assignee = User.objects.get(id=movement['to_rep_id'])

                # Create assignment record
                LeadAssignment.objects.create(
                    lead=lead,
                    assigned_to=new_assignee,
                    previous_assignee_id=movement['from_rep_id'],
                    assignment_method='rebalancing',
                    match_score=Decimal(str(movement.get('match_score', 0)))
                )

                # Update lead assignment
                lead.assigned_to = new_assignee
                lead.save(update_fields=['assigned_to'])

                successful += 1

            except Exception as e:
                logger.error(f"Failed to move lead {movement['lead_id']}: {e}")
                failed += 1

        # Complete event
        event.leads_moved = successful
        event.completed_at = timezone.now()
        event.save(update_fields=['leads_moved', 'completed_at'])

        return {
            'success': True,
            'event_id': str(event.id),
            'moved': successful,
            'failed': failed
        }
