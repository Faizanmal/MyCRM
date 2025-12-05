"""
Predictive Lead Routing Services
Business logic for lead assignment, escalation, and rebalancing
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Q, F, Avg, Count
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import (
    SalesRepProfile, RoutingRule, LeadAssignment, EscalationRule,
    RebalancingEvent, RoutingAnalytics, TerritoryDefinition, LeadQualityScore
)
from .routing_engine import AILeadRouter, RoundRobinRouter, LeadRebalancer

logger = logging.getLogger(__name__)
User = get_user_model()


class LeadRoutingService:
    """Main service for lead routing operations"""
    
    def __init__(self):
        self.ai_router = AILeadRouter()
        self.round_robin = RoundRobinRouter()
        self.rebalancer = LeadRebalancer()
    
    def route_lead(
        self,
        lead,
        assigned_by: Optional[User] = None,
        force_rule: Optional[RoutingRule] = None
    ) -> Tuple[Optional[LeadAssignment], Dict[str, Any]]:
        """
        Route a lead to the best available rep
        
        Args:
            lead: Lead model instance
            assigned_by: User who initiated the routing
            force_rule: Optional specific rule to use
            
        Returns:
            Tuple of (assignment, routing_details)
        """
        # Build lead data for routing
        lead_data = self._build_lead_data(lead)
        
        # Calculate lead priority
        priority_info = self.ai_router.calculate_lead_priority(lead_data)
        lead_data['priority'] = priority_info
        
        # Find applicable routing rule
        if force_rule:
            rule = force_rule
        else:
            rule = self._find_matching_rule(lead_data)
        
        # Get available reps
        available_reps = self._get_available_reps(rule)
        
        if not available_reps:
            logger.warning(f"No available reps for lead {lead.id}")
            return None, {'error': 'No available reps', 'lead_data': lead_data}
        
        # Route based on rule type
        if rule:
            rep, match_details = self._route_by_rule(lead_data, available_reps, rule)
            method = rule.rule_type
        else:
            # Default to AI routing
            rep, match_details = self.ai_router.find_best_rep(lead_data, available_reps)
            method = 'ai_routing'
        
        if not rep:
            return None, {'error': 'Could not find suitable rep', 'lead_data': lead_data}
        
        # Create assignment
        with transaction.atomic():
            assignment = LeadAssignment.objects.create(
                lead=lead,
                assigned_to=rep.user,
                assigned_by=assigned_by,
                previous_assignee=lead.assigned_to,
                assignment_method=method,
                routing_rule=rule,
                match_score=Decimal(str(match_details.get('score', 0))),
                match_factors=match_details.get('factors', {})
            )
            
            # Update lead assignment
            lead.assigned_to = rep.user
            lead.save(update_fields=['assigned_to'])
            
            # Update rep stats
            rep.current_lead_count = F('current_lead_count') + 1
            rep.total_leads_assigned = F('total_leads_assigned') + 1
            rep.last_assignment_at = timezone.now()
            rep.save(update_fields=['current_lead_count', 'total_leads_assigned', 'last_assignment_at'])
            
            # Update rule stats if used
            if rule:
                rule.total_matches = F('total_matches') + 1
                rule.total_assignments = F('total_assignments') + 1
                rule.save(update_fields=['total_matches', 'total_assignments'])
        
        # Check for auto-escalation
        escalation_check = self._check_escalation(lead_data, assignment)
        
        return assignment, {
            'method': method,
            'rule_id': str(rule.id) if rule else None,
            'match_details': match_details,
            'priority': priority_info,
            'escalation': escalation_check
        }
    
    def reassign_lead(
        self,
        lead,
        new_assignee: User,
        reassigned_by: User,
        reason: str = ''
    ) -> LeadAssignment:
        """Manually reassign a lead"""
        with transaction.atomic():
            assignment = LeadAssignment.objects.create(
                lead=lead,
                assigned_to=new_assignee,
                assigned_by=reassigned_by,
                previous_assignee=lead.assigned_to,
                assignment_method='manual',
                status_reason=reason
            )
            
            # Update old rep's count
            if lead.assigned_to:
                old_profile = SalesRepProfile.objects.filter(user=lead.assigned_to).first()
                if old_profile:
                    old_profile.current_lead_count = F('current_lead_count') - 1
                    old_profile.save(update_fields=['current_lead_count'])
            
            # Update new rep's count
            new_profile = SalesRepProfile.objects.filter(user=new_assignee).first()
            if new_profile:
                new_profile.current_lead_count = F('current_lead_count') + 1
                new_profile.last_assignment_at = timezone.now()
                new_profile.save(update_fields=['current_lead_count', 'last_assignment_at'])
            
            # Update lead
            lead.assigned_to = new_assignee
            lead.save(update_fields=['assigned_to'])
        
        return assignment
    
    def escalate_lead(
        self,
        lead,
        rule: EscalationRule,
        escalated_by: Optional[User] = None
    ) -> LeadAssignment:
        """Escalate a lead based on rule"""
        # Determine escalation target
        if rule.escalate_to_manager:
            # Get current assignee's manager
            current_profile = SalesRepProfile.objects.filter(user=lead.assigned_to).first()
            if current_profile and hasattr(current_profile.user, 'manager'):
                target = current_profile.user.manager
            else:
                target = rule.escalate_to
        else:
            target = rule.escalate_to
        
        with transaction.atomic():
            assignment = LeadAssignment.objects.create(
                lead=lead,
                assigned_to=target,
                assigned_by=escalated_by,
                previous_assignee=lead.assigned_to,
                assignment_method='auto_escalation',
                status='escalated',
                status_reason=f"Escalated: {rule.trigger_type}"
            )
            
            # Update lead
            old_assignee = lead.assigned_to
            lead.assigned_to = target
            lead.save(update_fields=['assigned_to'])
            
            # Update rep counts
            self._update_rep_counts(old_assignee, target)
            
            # Update rule stats
            rule.total_escalations = F('total_escalations') + 1
            rule.save(update_fields=['total_escalations'])
        
        # Send notifications
        if rule.notify_original_rep and old_assignee:
            self._send_escalation_notification(old_assignee, lead, rule)
        
        if rule.notify_manager:
            self._send_manager_notification(target, lead, rule)
        
        return assignment
    
    def process_routing_queue(self) -> Dict[str, int]:
        """Process all unassigned leads in queue"""
        from lead_management.models import Lead
        
        results = {'processed': 0, 'assigned': 0, 'failed': 0}
        
        unassigned_leads = Lead.objects.filter(
            assigned_to__isnull=True,
            status__in=['new', 'contacted']
        ).order_by('-lead_score', '-created_at')
        
        for lead in unassigned_leads:
            try:
                assignment, details = self.route_lead(lead)
                results['processed'] += 1
                
                if assignment:
                    results['assigned'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                logger.error(f"Failed to route lead {lead.id}: {e}")
                results['failed'] += 1
        
        return results
    
    def check_and_process_escalations(self) -> Dict[str, int]:
        """Check and process all pending escalations"""
        results = {'checked': 0, 'escalated': 0}
        
        # Get all active escalation rules
        rules = EscalationRule.objects.filter(is_active=True)
        
        # Get pending assignments to check
        pending_assignments = LeadAssignment.objects.filter(
            status__in=['assigned', 'accepted'],
            first_response_at__isnull=True
        ).select_related('lead', 'assigned_to')
        
        for assignment in pending_assignments:
            results['checked'] += 1
            
            lead_data = self._build_lead_data(assignment.lead)
            assignment_data = {
                'assigned_at': assignment.assigned_at,
                'first_response_at': assignment.first_response_at
            }
            
            escalation = self.ai_router.recommend_escalation(
                lead_data, assignment_data, rules
            )
            
            if escalation.get('should_escalate'):
                rule = EscalationRule.objects.get(id=escalation['rule_id'])
                self.escalate_lead(assignment.lead, rule)
                results['escalated'] += 1
        
        return results
    
    def trigger_rebalancing(
        self,
        triggered_by: Optional[User] = None,
        reason: str = 'manual'
    ) -> Dict[str, Any]:
        """Trigger lead rebalancing across reps"""
        from lead_management.models import Lead
        
        # Get all active reps
        reps = list(SalesRepProfile.objects.filter(is_available=True))
        
        if not reps:
            return {'success': False, 'message': 'No available reps'}
        
        # Get leads that can be rebalanced
        leads = list(Lead.objects.filter(
            status__in=['new', 'contacted', 'qualified'],
            assigned_to__isnull=False
        ))
        
        # Calculate rebalancing plan
        plan = self.rebalancer.calculate_rebalancing_plan(reps, leads)
        
        if not plan.get('movements'):
            return {'success': True, 'message': 'No rebalancing needed'}
        
        # Execute plan
        result = self.rebalancer.execute_rebalancing(plan, triggered_by, reason)
        
        return result
    
    def get_rep_recommendations(
        self,
        lead
    ) -> List[Dict[str, Any]]:
        """Get recommended reps for a lead"""
        lead_data = self._build_lead_data(lead)
        available_reps = list(SalesRepProfile.objects.filter(is_available=True))
        
        recommendations = []
        
        for rep in available_reps:
            score, factors = self.ai_router._calculate_match_score(lead_data, rep)
            
            recommendations.append({
                'rep_id': str(rep.id),
                'user_id': rep.user_id,
                'name': rep.user.get_full_name(),
                'score': score,
                'factors': factors,
                'capacity_utilization': rep.capacity_utilization,
                'win_rate': float(rep.win_rate),
                'expertise_level': rep.expertise_level
            })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:10]  # Top 10
    
    def _build_lead_data(self, lead) -> Dict[str, Any]:
        """Build lead data dictionary for routing"""
        return {
            'id': lead.id,
            'lead_score': lead.lead_score,
            'estimated_value': float(lead.estimated_value) if lead.estimated_value else 0,
            'industry': getattr(lead, 'industry', ''),
            'company_name': lead.company_name or '',
            'source': lead.lead_source,
            'status': lead.status,
            'priority': lead.priority,
            'country': getattr(lead, 'country', ''),
            'region': getattr(lead, 'region', ''),
            'timezone': lead.custom_fields.get('timezone', '') if lead.custom_fields else '',
            'tags': lead.tags or [],
            'required_skills': lead.custom_fields.get('required_skills', []) if lead.custom_fields else [],
            'is_time_sensitive': lead.priority == 'urgent',
            'is_vip': 'vip' in (lead.tags or []),
        }
    
    def _find_matching_rule(self, lead_data: Dict) -> Optional[RoutingRule]:
        """Find the first matching routing rule"""
        rules = RoutingRule.objects.filter(is_active=True).order_by('priority')
        
        for rule in rules:
            if self._matches_rule_criteria(lead_data, rule):
                return rule
        
        return None
    
    def _matches_rule_criteria(self, lead_data: Dict, rule: RoutingRule) -> bool:
        """Check if lead matches rule criteria"""
        criteria = rule.criteria
        
        if not criteria:
            return True  # No criteria means match all
        
        # Check lead score range
        if 'min_lead_score' in criteria:
            if lead_data.get('lead_score', 0) < criteria['min_lead_score']:
                return False
        
        if 'max_lead_score' in criteria:
            if lead_data.get('lead_score', 0) > criteria['max_lead_score']:
                return False
        
        # Check industry
        if 'industries' in criteria:
            if lead_data.get('industry', '').lower() not in [i.lower() for i in criteria['industries']]:
                return False
        
        # Check source
        if 'sources' in criteria:
            if lead_data.get('source', '').lower() not in [s.lower() for s in criteria['sources']]:
                return False
        
        # Check deal size
        if 'min_deal_size' in criteria:
            if lead_data.get('estimated_value', 0) < criteria['min_deal_size']:
                return False
        
        if 'max_deal_size' in criteria:
            if lead_data.get('estimated_value', 0) > criteria['max_deal_size']:
                return False
        
        # Check country/region
        if 'countries' in criteria:
            if lead_data.get('country', '').lower() not in [c.lower() for c in criteria['countries']]:
                return False
        
        # Check tags
        if 'required_tags' in criteria:
            lead_tags = [t.lower() for t in lead_data.get('tags', [])]
            if not all(t.lower() in lead_tags for t in criteria['required_tags']):
                return False
        
        return True
    
    def _get_available_reps(self, rule: Optional[RoutingRule] = None) -> List[SalesRepProfile]:
        """Get list of available reps for routing"""
        queryset = SalesRepProfile.objects.filter(is_available=True)
        
        if rule:
            if rule.target_reps.exists():
                queryset = queryset.filter(user__in=rule.target_reps.all())
            
            if rule.respect_capacity:
                queryset = queryset.filter(
                    current_lead_count__lt=F('max_active_leads')
                )
        
        return list(queryset.select_related('user'))
    
    def _route_by_rule(
        self,
        lead_data: Dict,
        available_reps: List[SalesRepProfile],
        rule: RoutingRule
    ) -> Tuple[Optional[SalesRepProfile], Dict[str, Any]]:
        """Route lead based on rule type"""
        if rule.rule_type == 'round_robin':
            return self.round_robin.get_next_rep(available_reps, lead_data)
        
        elif rule.rule_type == 'skill_based':
            # Use AI router with emphasis on skills
            return self.ai_router.find_best_rep(lead_data, available_reps)
        
        elif rule.rule_type == 'territory':
            # Filter by territory first
            territory_reps = self._filter_by_territory(lead_data, available_reps)
            if territory_reps:
                return self.round_robin.get_next_rep(territory_reps, lead_data)
            elif rule.fallback_rep:
                fallback_profile = SalesRepProfile.objects.filter(user=rule.fallback_rep).first()
                return fallback_profile, {'method': 'fallback'}
            return None, {'error': 'No territory match'}
        
        elif rule.rule_type == 'performance':
            # Sort by performance and pick best
            sorted_reps = sorted(
                available_reps,
                key=lambda r: float(r.overall_performance_score),
                reverse=True
            )
            return sorted_reps[0], {'method': 'performance_based'}
        
        else:  # custom
            return self.ai_router.find_best_rep(lead_data, available_reps)
    
    def _filter_by_territory(
        self,
        lead_data: Dict,
        reps: List[SalesRepProfile]
    ) -> List[SalesRepProfile]:
        """Filter reps by territory match"""
        lead_country = lead_data.get('country', '').lower()
        lead_region = lead_data.get('region', '').lower()
        
        matching = []
        for rep in reps:
            rep_countries = [c.lower() for c in (rep.countries or [])]
            rep_regions = [r.lower() for r in (rep.regions or [])]
            
            if lead_country in rep_countries or lead_region in rep_regions:
                matching.append(rep)
        
        return matching
    
    def _check_escalation(
        self,
        lead_data: Dict,
        assignment: LeadAssignment
    ) -> Dict[str, Any]:
        """Check if lead should be immediately escalated"""
        # Check for immediate escalation triggers
        rules = EscalationRule.objects.filter(
            is_active=True,
            wait_hours=0  # Immediate escalation
        )
        
        assignment_data = {
            'assigned_at': assignment.assigned_at,
            'first_response_at': None
        }
        
        return self.ai_router.recommend_escalation(lead_data, assignment_data, rules)
    
    def _update_rep_counts(self, old_assignee: Optional[User], new_assignee: User):
        """Update rep lead counts"""
        if old_assignee:
            old_profile = SalesRepProfile.objects.filter(user=old_assignee).first()
            if old_profile:
                old_profile.current_lead_count = F('current_lead_count') - 1
                old_profile.save(update_fields=['current_lead_count'])
        
        new_profile = SalesRepProfile.objects.filter(user=new_assignee).first()
        if new_profile:
            new_profile.current_lead_count = F('current_lead_count') + 1
            new_profile.save(update_fields=['current_lead_count'])
    
    def _send_escalation_notification(self, user: User, lead, rule: EscalationRule):
        """Send escalation notification"""
        # Implementation would send email/in-app notification
        logger.info(f"Escalation notification sent to {user.email} for lead {lead.id}")
    
    def _send_manager_notification(self, manager: User, lead, rule: EscalationRule):
        """Send manager notification"""
        logger.info(f"Manager notification sent to {manager.email} for lead {lead.id}")


class RepPerformanceService:
    """Service for managing rep performance metrics"""
    
    def update_rep_performance(self, rep: SalesRepProfile):
        """Update rep's performance metrics"""
        from lead_management.models import Lead
        
        # Get rep's assignments
        assignments = LeadAssignment.objects.filter(assigned_to=rep.user)
        
        # Calculate metrics
        total = assignments.count()
        converted = assignments.filter(status='converted').count()
        
        if total > 0:
            rep.total_leads_assigned = total
            rep.total_leads_converted = converted
            rep.win_rate = Decimal(str(converted / total))
        
        # Average response time
        responded = assignments.filter(first_response_at__isnull=False)
        if responded.exists():
            avg_response = responded.aggregate(
                avg_response=Avg(
                    F('first_response_at') - F('assigned_at')
                )
            )['avg_response']
            if avg_response:
                rep.response_time_minutes = int(avg_response.total_seconds() / 60)
        
        # Average deal size (from converted leads)
        converted_leads = Lead.objects.filter(
            assigned_to=rep.user,
            status='converted'
        )
        if converted_leads.exists():
            avg_value = converted_leads.aggregate(
                avg=Avg('estimated_value')
            )['avg']
            if avg_value:
                rep.avg_deal_size = avg_value
        
        # Calculate overall score
        rep.overall_performance_score = self._calculate_performance_score(rep)
        rep.last_performance_update = timezone.now()
        
        rep.save()
        
        return rep
    
    def _calculate_performance_score(self, rep: SalesRepProfile) -> Decimal:
        """Calculate overall performance score"""
        score = Decimal('50')  # Base score
        
        # Win rate contribution (max 25 points)
        win_rate_points = float(rep.win_rate) * 25
        score += Decimal(str(win_rate_points))
        
        # Response time contribution (max 15 points, lower is better)
        if rep.response_time_minutes > 0:
            response_points = max(0, 15 - (rep.response_time_minutes / 60) * 5)
        else:
            response_points = 7.5  # Default
        score += Decimal(str(response_points))
        
        # Customer satisfaction contribution (max 10 points)
        satisfaction_points = float(rep.customer_satisfaction) * 2
        score += Decimal(str(satisfaction_points))
        
        return min(Decimal('100'), max(Decimal('0'), score))
    
    def get_performance_report(self, rep: SalesRepProfile) -> Dict[str, Any]:
        """Get detailed performance report for a rep"""
        assignments = LeadAssignment.objects.filter(assigned_to=rep.user)
        
        # Time-based metrics
        last_30_days = timezone.now() - timedelta(days=30)
        recent_assignments = assignments.filter(assigned_at__gte=last_30_days)
        
        return {
            'rep_id': str(rep.id),
            'user_id': rep.user_id,
            'name': rep.user.get_full_name(),
            'overall_score': float(rep.overall_performance_score),
            'metrics': {
                'total_leads': rep.total_leads_assigned,
                'converted': rep.total_leads_converted,
                'win_rate': float(rep.win_rate) * 100,
                'avg_response_time_minutes': rep.response_time_minutes,
                'avg_deal_size': float(rep.avg_deal_size),
                'customer_satisfaction': float(rep.customer_satisfaction)
            },
            'capacity': {
                'current_leads': rep.current_lead_count,
                'max_leads': rep.max_active_leads,
                'utilization': rep.capacity_utilization
            },
            'recent_30_days': {
                'assignments': recent_assignments.count(),
                'converted': recent_assignments.filter(status='converted').count(),
            },
            'expertise': {
                'level': rep.expertise_level,
                'industries': rep.industries,
                'regions': rep.regions
            }
        }


class AnalyticsService:
    """Service for routing analytics"""
    
    def record_daily_analytics(self):
        """Record daily routing analytics"""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        assignments = LeadAssignment.objects.filter(
            assigned_at__date=yesterday
        )
        
        analytics, _ = RoutingAnalytics.objects.update_or_create(
            date=yesterday,
            defaults={
                'total_leads_routed': assignments.count(),
                'auto_routed': assignments.exclude(assignment_method='manual').count(),
                'manual_routed': assignments.filter(assignment_method='manual').count(),
                'escalations': assignments.filter(assignment_method='auto_escalation').count(),
                'rebalanced': assignments.filter(assignment_method='rebalancing').count(),
                'avg_match_score': assignments.aggregate(avg=Avg('match_score'))['avg'] or 0,
                'routing_by_method': self._count_by_field(assignments, 'assignment_method'),
            }
        )
        
        return analytics
    
    def _count_by_field(self, queryset, field: str) -> Dict[str, int]:
        """Count queryset by field values"""
        counts = queryset.values(field).annotate(count=Count('id'))
        return {item[field]: item['count'] for item in counts}
    
    def get_routing_dashboard(self) -> Dict[str, Any]:
        """Get routing dashboard data"""
        today = timezone.now().date()
        last_7_days = today - timedelta(days=7)
        
        recent_analytics = RoutingAnalytics.objects.filter(
            date__gte=last_7_days
        ).order_by('date')
        
        # Today's stats
        today_assignments = LeadAssignment.objects.filter(
            assigned_at__date=today
        )
        
        return {
            'today': {
                'total_routed': today_assignments.count(),
                'auto_routed': today_assignments.exclude(assignment_method='manual').count(),
                'escalations': today_assignments.filter(assignment_method='auto_escalation').count(),
            },
            'trends': [
                {
                    'date': str(a.date),
                    'total': a.total_leads_routed,
                    'auto': a.auto_routed,
                    'avg_score': float(a.avg_match_score)
                }
                for a in recent_analytics
            ],
            'rep_utilization': self._get_rep_utilization(),
            'rule_performance': self._get_rule_performance()
        }
    
    def _get_rep_utilization(self) -> List[Dict]:
        """Get rep capacity utilization"""
        reps = SalesRepProfile.objects.all()
        return [
            {
                'name': rep.user.get_full_name(),
                'utilization': rep.capacity_utilization,
                'current': rep.current_lead_count,
                'max': rep.max_active_leads
            }
            for rep in reps
        ]
    
    def _get_rule_performance(self) -> List[Dict]:
        """Get routing rule performance"""
        rules = RoutingRule.objects.filter(is_active=True)
        return [
            {
                'name': rule.name,
                'type': rule.rule_type,
                'total_assignments': rule.total_assignments,
                'conversion_rate': 0  # Would calculate from actual data
            }
            for rule in rules
        ]
