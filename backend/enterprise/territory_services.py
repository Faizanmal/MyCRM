"""
Territory & Quota Management Services
AI-powered territory balancing and quota planning
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Avg, Count, Q
from django.contrib.auth import get_user_model

from .territory_models import (
    Territory, TerritoryAssignmentRule, TerritoryRebalanceRequest,
    QuotaPeriod, Quota, QuotaAdjustment, TerritoryPerformance
)

logger = logging.getLogger(__name__)
User = get_user_model()


class TerritoryService:
    """Service for territory management"""
    
    def get_territory_hierarchy(self) -> List[Dict]:
        """Get complete territory hierarchy"""
        
        def build_tree(parent_id=None) -> List[Dict]:
            territories = Territory.objects.filter(
                parent_id=parent_id,
                is_active=True
            ).select_related('owner')
            
            return [
                {
                    'id': str(t.id),
                    'name': t.name,
                    'code': t.code,
                    'type': t.territory_type,
                    'owner': t.owner.username if t.owner else None,
                    'current_accounts': t.current_accounts,
                    'max_accounts': t.max_accounts,
                    'total_revenue': float(t.total_revenue),
                    'total_pipeline': float(t.total_pipeline),
                    'children': build_tree(t.id)
                }
                for t in territories
            ]
        
        return build_tree()
    
    @transaction.atomic
    def assign_account_to_territory(
        self,
        account_data: Dict,
        force_territory_id: Optional[str] = None
    ) -> Dict:
        """Assign an account to a territory based on rules"""
        
        if force_territory_id:
            territory = Territory.objects.get(id=force_territory_id)
        else:
            territory = self._match_territory(account_data)
        
        if not territory:
            return {
                'assigned': False,
                'reason': 'No matching territory found'
            }
        
        # Check capacity
        if territory.max_accounts and territory.current_accounts >= territory.max_accounts:
            return {
                'assigned': False,
                'reason': 'Territory at capacity',
                'territory_id': str(territory.id)
            }
        
        # Update territory counts
        territory.current_accounts += 1
        territory.save(update_fields=['current_accounts'])
        
        return {
            'assigned': True,
            'territory_id': str(territory.id),
            'territory_name': territory.name,
            'owner': territory.owner.username if territory.owner else None
        }
    
    def _match_territory(self, account_data: Dict) -> Optional[Territory]:
        """Match account to territory using rules"""
        
        rules = TerritoryAssignmentRule.objects.filter(
            is_active=True
        ).select_related('territory').order_by('-priority')
        
        for rule in rules:
            if self._evaluate_rule(rule, account_data):
                rule.matches_count += 1
                rule.last_matched_at = timezone.now()
                rule.save(update_fields=['matches_count', 'last_matched_at'])
                return rule.territory
        
        return None
    
    def _evaluate_rule(self, rule: TerritoryAssignmentRule, data: Dict) -> bool:
        """Evaluate assignment rule conditions"""
        
        conditions = rule.conditions
        results = []
        
        for condition in conditions:
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            
            account_value = data.get(field)
            
            if operator == 'equals':
                results.append(account_value == value)
            elif operator == 'in':
                results.append(account_value in value)
            elif operator == 'not_in':
                results.append(account_value not in value)
            elif operator == 'contains':
                results.append(value in str(account_value))
            elif operator == 'greater_than':
                results.append(account_value > value)
            elif operator == 'less_than':
                results.append(account_value < value)
            elif operator == 'between':
                results.append(value[0] <= account_value <= value[1])
        
        if rule.match_type == 'all':
            return all(results)
        else:  # any
            return any(results)
    
    def analyze_territory_balance(self, territory_ids: List[str] = None) -> Dict:
        """Analyze territory workload balance"""
        
        queryset = Territory.objects.filter(is_active=True)
        if territory_ids:
            queryset = queryset.filter(id__in=territory_ids)
        
        territories = list(queryset)
        
        if not territories:
            return {'territories': [], 'analysis': {}}
        
        # Calculate metrics
        metrics = []
        total_accounts = sum(t.current_accounts for t in territories)
        total_pipeline = sum(float(t.total_pipeline) for t in territories)
        avg_accounts = total_accounts / len(territories) if territories else 0
        avg_pipeline = total_pipeline / len(territories) if territories else 0
        
        for territory in territories:
            accounts_variance = (territory.current_accounts - avg_accounts) / avg_accounts * 100 if avg_accounts else 0
            pipeline_variance = (float(territory.total_pipeline) - avg_pipeline) / avg_pipeline * 100 if avg_pipeline else 0
            
            # Calculate capacity utilization
            capacity_util = territory.current_accounts / territory.max_accounts * 100 if territory.max_accounts else 0
            
            metrics.append({
                'territory_id': str(territory.id),
                'territory_name': territory.name,
                'current_accounts': territory.current_accounts,
                'accounts_variance': round(accounts_variance, 1),
                'pipeline': float(territory.total_pipeline),
                'pipeline_variance': round(pipeline_variance, 1),
                'capacity_utilization': round(capacity_util, 1),
                'is_overloaded': capacity_util > 90,
                'is_underutilized': capacity_util < 50
            })
        
        # Overall analysis
        overloaded = [m for m in metrics if m['is_overloaded']]
        underutilized = [m for m in metrics if m['is_underutilized']]
        
        return {
            'territories': metrics,
            'analysis': {
                'total_territories': len(territories),
                'total_accounts': total_accounts,
                'avg_accounts_per_territory': round(avg_accounts, 1),
                'total_pipeline': total_pipeline,
                'overloaded_count': len(overloaded),
                'underutilized_count': len(underutilized),
                'balance_score': self._calculate_balance_score(metrics)
            }
        }
    
    def _calculate_balance_score(self, metrics: List[Dict]) -> int:
        """Calculate overall balance score (0-100)"""
        
        if not metrics:
            return 100
        
        variances = [abs(m['accounts_variance']) for m in metrics]
        avg_variance = sum(variances) / len(variances)
        
        # Score decreases as variance increases
        score = max(0, 100 - avg_variance)
        return round(score)
    
    @transaction.atomic
    def request_rebalance(
        self,
        user,
        territory_ids: List[str],
        reason: str,
        optimization_goals: List[str]
    ) -> Dict:
        """Request territory rebalancing"""
        
        territories = Territory.objects.filter(id__in=territory_ids)
        
        # Get current state
        current_state = self.analyze_territory_balance(territory_ids)
        
        # Create request
        request = TerritoryRebalanceRequest.objects.create(
            requested_by=user,
            reason=reason,
            optimization_goals=optimization_goals,
            current_state=current_state,
            status='analyzing'
        )
        request.territories.set(territories)
        
        # Generate proposed changes (AI-powered in production)
        proposed_changes = self._generate_rebalance_proposal(territories, optimization_goals)
        
        request.proposed_changes = proposed_changes
        request.status = 'ready'
        request.save()
        
        return {
            'request_id': str(request.id),
            'status': request.status,
            'current_state': current_state,
            'proposed_changes': proposed_changes
        }
    
    def _generate_rebalance_proposal(
        self,
        territories,
        goals: List[str]
    ) -> List[Dict]:
        """Generate rebalancing proposal"""
        
        proposals = []
        territories_list = list(territories)
        
        # Simple algorithm - in production use ML/optimization
        avg_accounts = sum(t.current_accounts for t in territories_list) / len(territories_list)
        
        overloaded = [t for t in territories_list if t.current_accounts > avg_accounts * 1.2]
        underloaded = [t for t in territories_list if t.current_accounts < avg_accounts * 0.8]
        
        for over in overloaded:
            excess = int(over.current_accounts - avg_accounts)
            if underloaded and excess > 0:
                target = underloaded[0]
                proposals.append({
                    'type': 'transfer',
                    'from_territory': str(over.id),
                    'from_territory_name': over.name,
                    'to_territory': str(target.id),
                    'to_territory_name': target.name,
                    'accounts_to_move': min(excess, int(avg_accounts - target.current_accounts)),
                    'reason': 'Balance workload'
                })
        
        return proposals


class QuotaService:
    """Service for quota management"""
    
    def __init__(self, user=None):
        self.user = user
    
    def get_quota_summary(self, period_id: str = None) -> Dict:
        """Get quota summary for current period"""
        
        if period_id:
            period = QuotaPeriod.objects.get(id=period_id)
        else:
            period = QuotaPeriod.objects.filter(is_active=True).first()
        
        if not period:
            return {'error': 'No active quota period'}
        
        quotas = Quota.objects.filter(period=period)
        
        total_target = quotas.aggregate(Sum('target'))['target__sum'] or 0
        total_achieved = quotas.aggregate(Sum('achieved'))['achieved__sum'] or 0
        total_forecast = quotas.aggregate(Sum('forecast'))['forecast__sum'] or 0
        
        attainment = (total_achieved / total_target * 100) if total_target else 0
        forecast_attainment = (total_forecast / total_target * 100) if total_target else 0
        
        # By user
        user_quotas = quotas.filter(user__isnull=False).select_related('user')
        by_user = [
            {
                'user_id': str(q.user.id),
                'username': q.user.username,
                'target': float(q.target),
                'achieved': float(q.achieved),
                'attainment': q.attainment_percentage,
                'forecast': float(q.forecast)
            }
            for q in user_quotas
        ]
        
        # By territory
        territory_quotas = quotas.filter(territory__isnull=False).select_related('territory')
        by_territory = [
            {
                'territory_id': str(q.territory.id),
                'territory_name': q.territory.name,
                'target': float(q.target),
                'achieved': float(q.achieved),
                'attainment': q.attainment_percentage,
                'forecast': float(q.forecast)
            }
            for q in territory_quotas
        ]
        
        return {
            'period': {
                'id': str(period.id),
                'name': period.name,
                'start_date': period.start_date.isoformat(),
                'end_date': period.end_date.isoformat()
            },
            'summary': {
                'total_target': float(total_target),
                'total_achieved': float(total_achieved),
                'total_forecast': float(total_forecast),
                'attainment': round(attainment, 1),
                'forecast_attainment': round(forecast_attainment, 1),
                'quota_count': quotas.count()
            },
            'by_user': sorted(by_user, key=lambda x: x['attainment'], reverse=True),
            'by_territory': sorted(by_territory, key=lambda x: x['attainment'], reverse=True)
        }
    
    @transaction.atomic
    def set_quota(
        self,
        period_id: str,
        user_id: Optional[str] = None,
        territory_id: Optional[str] = None,
        quota_type: str = 'revenue',
        target: Decimal = 0,
        stretch_target: Optional[Decimal] = None
    ) -> Dict:
        """Set or update a quota"""
        
        period = QuotaPeriod.objects.get(id=period_id)
        
        if period.is_locked:
            raise ValueError("Quota period is locked")
        
        lookup = {'period': period, 'quota_type': quota_type}
        
        if user_id:
            lookup['user_id'] = user_id
        if territory_id:
            lookup['territory_id'] = territory_id
        
        quota, created = Quota.objects.update_or_create(
            **lookup,
            defaults={
                'target': target,
                'stretch_target': stretch_target
            }
        )
        
        # Get AI recommendation
        ai_recommendation = self._get_ai_quota_recommendation(quota)
        quota.ai_recommended_target = ai_recommendation.get('recommended_target')
        quota.ai_confidence = ai_recommendation.get('confidence')
        quota.ai_factors = ai_recommendation.get('factors', [])
        quota.save()
        
        return {
            'quota_id': str(quota.id),
            'target': float(quota.target),
            'stretch_target': float(quota.stretch_target) if quota.stretch_target else None,
            'ai_recommendation': ai_recommendation,
            'created': created
        }
    
    def _get_ai_quota_recommendation(self, quota: Quota) -> Dict:
        """Get AI-powered quota recommendation"""
        
        # In production, use ML model based on:
        # - Historical performance
        # - Market conditions
        # - Pipeline data
        # - Seasonal patterns
        
        # Simple heuristic for demo
        historical_achievement = self._get_historical_performance(quota)
        
        if historical_achievement:
            # Suggest 10-20% growth
            recommended = historical_achievement * Decimal('1.15')
            
            factors = [
                {'factor': 'Historical Performance', 'weight': 0.4},
                {'factor': 'Market Growth', 'weight': 0.3},
                {'factor': 'Pipeline Quality', 'weight': 0.3}
            ]
            
            return {
                'recommended_target': float(recommended),
                'confidence': 0.75,
                'factors': factors,
                'comparison_to_set': {
                    'difference': float(quota.target - recommended),
                    'percentage': float((quota.target / recommended - 1) * 100) if recommended else 0
                }
            }
        
        return {
            'recommended_target': None,
            'confidence': 0,
            'factors': [],
            'message': 'Insufficient historical data'
        }
    
    def _get_historical_performance(self, quota: Quota) -> Optional[Decimal]:
        """Get historical performance for quota entity"""
        
        # Get previous period quota
        previous = Quota.objects.filter(
            user=quota.user,
            territory=quota.territory,
            quota_type=quota.quota_type
        ).exclude(
            period=quota.period
        ).order_by('-period__end_date').first()
        
        return previous.achieved if previous else None
    
    @transaction.atomic
    def request_adjustment(
        self,
        quota_id: str,
        new_target: Decimal,
        reason: str,
        requester
    ) -> Dict:
        """Request quota adjustment"""
        
        quota = Quota.objects.get(id=quota_id)
        
        adjustment = QuotaAdjustment.objects.create(
            quota=quota,
            adjustment_type='increase' if new_target > quota.target else 'decrease',
            old_target=quota.target,
            new_target=new_target,
            difference=new_target - quota.target,
            reason=reason,
            requested_by=requester
        )
        
        return {
            'adjustment_id': str(adjustment.id),
            'old_target': float(adjustment.old_target),
            'new_target': float(adjustment.new_target),
            'difference': float(adjustment.difference),
            'status': 'pending_approval'
        }
    
    @transaction.atomic
    def approve_adjustment(
        self,
        adjustment_id: str,
        approver,
        approved: bool,
        notes: str = ''
    ) -> Dict:
        """Approve or reject quota adjustment"""
        
        adjustment = QuotaAdjustment.objects.get(id=adjustment_id)
        
        adjustment.approved_by = approver
        adjustment.approved_at = timezone.now()
        adjustment.is_approved = approved
        
        if approved:
            # Apply the adjustment
            quota = adjustment.quota
            quota.target = adjustment.new_target
            quota.save(update_fields=['target'])
        
        adjustment.save()
        
        return {
            'adjustment_id': str(adjustment.id),
            'approved': approved,
            'new_target': float(adjustment.new_target) if approved else float(adjustment.old_target)
        }
    
    def get_quota_forecast(self, quota_id: str) -> Dict:
        """Get quota forecast with AI insights"""
        
        quota = Quota.objects.get(id=quota_id)
        
        # Calculate days remaining
        today = timezone.now().date()
        days_remaining = (quota.period.end_date - today).days
        total_days = (quota.period.end_date - quota.period.start_date).days
        days_elapsed = total_days - days_remaining
        
        # Current run rate
        if days_elapsed > 0:
            daily_rate = float(quota.achieved) / days_elapsed
            projected = daily_rate * total_days
        else:
            daily_rate = 0
            projected = 0
        
        # Gap analysis
        remaining_target = float(quota.target) - float(quota.achieved)
        required_daily = remaining_target / days_remaining if days_remaining > 0 else 0
        
        return {
            'quota_id': str(quota.id),
            'target': float(quota.target),
            'achieved': float(quota.achieved),
            'attainment': quota.attainment_percentage,
            'forecast': {
                'projected_total': round(projected, 2),
                'projected_attainment': round(projected / float(quota.target) * 100, 1) if quota.target else 0,
                'days_remaining': days_remaining,
                'daily_run_rate': round(daily_rate, 2),
                'required_daily_rate': round(required_daily, 2)
            },
            'gap_analysis': {
                'remaining_target': round(remaining_target, 2),
                'on_track': projected >= float(quota.target),
                'variance': round(projected - float(quota.target), 2)
            }
        }


class TerritoryPerformanceService:
    """Service for territory performance analytics"""
    
    def capture_performance_snapshot(self, territory_id: str, period_id: str) -> Dict:
        """Capture territory performance snapshot"""
        
        territory = Territory.objects.get(id=territory_id)
        period = QuotaPeriod.objects.get(id=period_id)
        
        # Calculate metrics (in production, aggregate from opportunities)
        performance, created = TerritoryPerformance.objects.update_or_create(
            territory=territory,
            period=period,
            snapshot_date=timezone.now().date(),
            defaults={
                'total_revenue': territory.total_revenue,
                'total_pipeline': territory.total_pipeline,
                'accounts_count': territory.current_accounts,
                'win_rate': territory.win_rate,
                'health_score': self._calculate_health_score(territory)
            }
        )
        
        return {
            'snapshot_id': str(performance.id),
            'territory': territory.name,
            'health_score': performance.health_score,
            'created': created
        }
    
    def _calculate_health_score(self, territory: Territory) -> int:
        """Calculate territory health score"""
        
        score = 50  # Base score
        
        # Pipeline coverage
        if territory.total_pipeline > 0 and territory.total_revenue > 0:
            coverage = float(territory.total_pipeline) / float(territory.total_revenue)
            if coverage >= 3:
                score += 20
            elif coverage >= 2:
                score += 10
            elif coverage < 1:
                score -= 20
        
        # Win rate
        if territory.win_rate >= 0.3:
            score += 15
        elif territory.win_rate >= 0.2:
            score += 5
        elif territory.win_rate < 0.1:
            score -= 15
        
        # Capacity utilization
        if territory.max_accounts:
            util = territory.current_accounts / territory.max_accounts
            if 0.7 <= util <= 0.9:
                score += 15
            elif util > 0.95:
                score -= 10  # Overloaded
            elif util < 0.3:
                score -= 10  # Underutilized
        
        return max(0, min(100, score))
    
    def get_performance_trends(
        self,
        territory_id: str,
        periods: int = 4
    ) -> Dict:
        """Get territory performance trends"""
        
        territory = Territory.objects.get(id=territory_id)
        
        snapshots = TerritoryPerformance.objects.filter(
            territory=territory
        ).order_by('-snapshot_date')[:periods * 10]  # Get enough for grouping
        
        # Group by period
        by_period = {}
        for snap in snapshots:
            period_name = snap.period.name
            if period_name not in by_period:
                by_period[period_name] = snap
        
        trends = [
            {
                'period': snap.period.name,
                'revenue': float(snap.total_revenue),
                'pipeline': float(snap.total_pipeline),
                'win_rate': snap.win_rate,
                'health_score': snap.health_score,
                'quota_attainment': snap.quota_attainment
            }
            for snap in by_period.values()
        ]
        
        return {
            'territory_id': str(territory.id),
            'territory_name': territory.name,
            'trends': sorted(trends, key=lambda x: x['period'])
        }
    
    def get_optimization_recommendations(self, territory_id: str) -> List[Dict]:
        """Get AI-powered optimization recommendations"""
        
        territory = Territory.objects.get(id=territory_id)
        
        recommendations = []
        
        # Check capacity
        if territory.max_accounts:
            util = territory.current_accounts / territory.max_accounts
            if util > 0.9:
                recommendations.append({
                    'type': 'capacity',
                    'priority': 'high',
                    'title': 'Territory Overloaded',
                    'description': f'Territory is at {util*100:.0f}% capacity. Consider splitting or reassigning accounts.',
                    'impact': 'Prevents rep burnout and ensures quality coverage'
                })
            elif util < 0.4:
                recommendations.append({
                    'type': 'capacity',
                    'priority': 'medium',
                    'title': 'Underutilized Territory',
                    'description': f'Territory is at only {util*100:.0f}% capacity. Consider merging or adding accounts.',
                    'impact': 'Improves rep productivity'
                })
        
        # Check win rate
        if territory.win_rate < 0.15:
            recommendations.append({
                'type': 'performance',
                'priority': 'high',
                'title': 'Low Win Rate',
                'description': f'Win rate of {territory.win_rate*100:.1f}% is below target. Review deal qualification.',
                'impact': 'Improve close rates and revenue'
            })
        
        # Check pipeline coverage
        if float(territory.total_revenue) > 0:
            coverage = float(territory.total_pipeline) / float(territory.total_revenue)
            if coverage < 2:
                recommendations.append({
                    'type': 'pipeline',
                    'priority': 'high',
                    'title': 'Insufficient Pipeline Coverage',
                    'description': f'Pipeline coverage of {coverage:.1f}x is below the 3x target.',
                    'impact': 'Risk of missing quota'
                })
        
        return recommendations
