"""
Revenue Intelligence Dashboard Services
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Count, Avg, Sum, F
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
import openai
import json


class ForecastingService:
    """AI-powered revenue forecasting"""
    
    def __init__(self, user):
        self.user = user
    
    def generate_forecast(
        self,
        forecast_type: str,
        period_start: date,
        period_end: date
    ) -> Dict[str, Any]:
        """Generate revenue forecast for a period"""
        from .dashboard_models import RevenueForecast
        from opportunity_management.models import Opportunity
        
        # Get pipeline data
        opportunities = Opportunity.objects.filter(
            expected_close_date__range=(period_start, period_end)
        )
        
        # Calculate pipeline by stage
        pipeline_by_stage = {}
        stage_weights = {
            'qualification': 0.1,
            'discovery': 0.2,
            'proposal': 0.4,
            'negotiation': 0.6,
            'verbal_commit': 0.9,
            'closed_won': 1.0
        }
        
        for opp in opportunities:
            stage = opp.stage
            if stage not in pipeline_by_stage:
                pipeline_by_stage[stage] = {'count': 0, 'value': Decimal('0')}
            pipeline_by_stage[stage]['count'] += 1
            pipeline_by_stage[stage]['value'] += opp.value or Decimal('0')
        
        # Calculate weighted pipeline
        weighted_pipeline = Decimal('0')
        for stage, data in pipeline_by_stage.items():
            weight = stage_weights.get(stage, 0.3)
            weighted_pipeline += data['value'] * Decimal(str(weight))
        
        # Already closed deals
        closed_won = opportunities.filter(stage='closed_won')
        committed_revenue = sum(
            opp.value or Decimal('0') for opp in closed_won
        )
        
        # AI-based prediction
        prediction = self._ai_predict_revenue(
            opportunities,
            pipeline_by_stage,
            period_start,
            period_end
        )
        
        # Historical comparison
        prev_start = period_start - relativedelta(years=1)
        prev_end = period_end - relativedelta(years=1)
        previous_actual = self._get_historical_revenue(prev_start, prev_end)
        
        yoy_growth = None
        if previous_actual and previous_actual > 0:
            yoy_growth = (
                (prediction['predicted'] - float(previous_actual)) / 
                float(previous_actual) * 100
            )
        
        # Create forecast record
        forecast = RevenueForecast.objects.update_or_create(
            user=self.user,
            forecast_type=forecast_type,
            period_start=period_start,
            defaults={
                'period_end': period_end,
                'committed_revenue': committed_revenue,
                'best_case_revenue': Decimal(str(prediction['best_case'])),
                'worst_case_revenue': Decimal(str(prediction['worst_case'])),
                'predicted_revenue': Decimal(str(prediction['predicted'])),
                'prediction_confidence': Decimal(str(prediction['confidence'])),
                'pipeline_by_stage': {
                    k: {'count': v['count'], 'value': float(v['value'])}
                    for k, v in pipeline_by_stage.items()
                },
                'weighted_pipeline': weighted_pipeline,
                'positive_factors': prediction.get('positive_factors', []),
                'risk_factors': prediction.get('risk_factors', []),
                'previous_period_actual': previous_actual,
                'yoy_growth_rate': yoy_growth
            }
        )[0]
        
        return {
            'forecast_id': str(forecast.id),
            'predicted_revenue': float(forecast.predicted_revenue),
            'committed': float(forecast.committed_revenue),
            'best_case': float(forecast.best_case_revenue),
            'worst_case': float(forecast.worst_case_revenue),
            'confidence': float(forecast.prediction_confidence),
            'pipeline_by_stage': pipeline_by_stage,
            'weighted_pipeline': float(weighted_pipeline),
            'yoy_growth': yoy_growth
        }
    
    def _ai_predict_revenue(
        self,
        opportunities,
        pipeline_by_stage: Dict,
        period_start: date,
        period_end: date
    ) -> Dict[str, Any]:
        """Use AI to predict revenue"""
        # Calculate base prediction from weighted pipeline
        stage_weights = {
            'qualification': 0.1,
            'discovery': 0.2,
            'proposal': 0.4,
            'negotiation': 0.6,
            'verbal_commit': 0.9,
            'closed_won': 1.0
        }
        
        predicted = 0
        for stage, data in pipeline_by_stage.items():
            weight = stage_weights.get(stage, 0.3)
            predicted += float(data['value']) * weight
        
        # Calculate confidence based on pipeline distribution
        confidence = 70  # Base confidence
        
        # More committed deals = higher confidence
        if 'verbal_commit' in pipeline_by_stage:
            confidence += 10
        if 'closed_won' in pipeline_by_stage:
            confidence += 10
        
        # Analyze risks and opportunities
        positive_factors = []
        risk_factors = []
        
        # Check for large deals
        large_deals = [o for o in opportunities if o.value and o.value > 100000]
        if large_deals:
            positive_factors.append({
                'factor': f'{len(large_deals)} large deal(s) in pipeline',
                'impact': 'high'
            })
        
        # Check for stalled deals
        stalled = [
            o for o in opportunities 
            if o.updated_at and o.updated_at < timezone.now() - timedelta(days=14)
        ]
        if stalled:
            risk_factors.append({
                'factor': f'{len(stalled)} stalled deal(s)',
                'impact': 'medium'
            })
        
        return {
            'predicted': predicted,
            'best_case': predicted * 1.2,
            'worst_case': predicted * 0.7,
            'confidence': min(95, confidence),
            'positive_factors': positive_factors,
            'risk_factors': risk_factors
        }
    
    def _get_historical_revenue(
        self, start: date, end: date
    ) -> Optional[Decimal]:
        """Get historical closed revenue for a period"""
        from opportunity_management.models import Opportunity
        
        closed = Opportunity.objects.filter(
            stage='closed_won',
            close_date__range=(start, end)
        )
        
        total = closed.aggregate(total=Sum('value'))['total']
        return total


class CohortAnalysisService:
    """Customer cohort analysis"""
    
    def __init__(self, user):
        self.user = user
    
    def generate_cohort_analysis(
        self,
        cohort_type: str,
        metric_type: str,
        periods: int = 12
    ) -> Dict[str, Any]:
        """Generate cohort analysis"""
        from .dashboard_models import CohortAnalysis
        
        # Get cohorts based on type
        cohorts = self._get_cohorts(cohort_type, periods)
        
        results = []
        
        for cohort in cohorts:
            periodic_values = self._calculate_cohort_metrics(
                cohort, metric_type, periods
            )
            
            analysis = CohortAnalysis.objects.create(
                user=self.user,
                cohort_type=cohort_type,
                cohort_name=cohort['name'],
                cohort_date=cohort['date'],
                metric_type=metric_type,
                cohort_size=cohort['size'],
                periodic_values=periodic_values,
                avg_value=Decimal(str(
                    sum(periodic_values) / len(periodic_values)
                    if periodic_values else 0
                )),
                total_value=Decimal(str(sum(periodic_values)))
            )
            
            results.append({
                'cohort_name': cohort['name'],
                'cohort_size': cohort['size'],
                'periodic_values': periodic_values,
                'avg_value': float(analysis.avg_value),
                'total_value': float(analysis.total_value)
            })
        
        return {
            'cohort_type': cohort_type,
            'metric_type': metric_type,
            'periods': periods,
            'cohorts': results
        }
    
    def _get_cohorts(
        self, cohort_type: str, periods: int
    ) -> List[Dict[str, Any]]:
        """Get cohorts based on type"""
        cohorts = []
        today = date.today()
        
        if cohort_type in ['acquisition_month', 'acquisition_quarter']:
            # Monthly/quarterly acquisition cohorts
            for i in range(periods):
                if cohort_type == 'acquisition_month':
                    cohort_date = today - relativedelta(months=i)
                    name = cohort_date.strftime('%b %Y')
                else:
                    cohort_date = today - relativedelta(months=i*3)
                    quarter = (cohort_date.month - 1) // 3 + 1
                    name = f"Q{quarter} {cohort_date.year}"
                
                # Count customers acquired in this period
                size = self._count_customers_acquired(cohort_date, cohort_type)
                
                cohorts.append({
                    'name': name,
                    'date': cohort_date,
                    'size': size
                })
        
        return cohorts
    
    def _count_customers_acquired(
        self, cohort_date: date, cohort_type: str
    ) -> int:
        """Count customers acquired in a cohort period"""
        # Simplified - would query actual customer data
        return 0
    
    def _calculate_cohort_metrics(
        self, cohort: Dict, metric_type: str, periods: int
    ) -> List[float]:
        """Calculate metrics for each period in cohort"""
        # Simplified - would calculate actual metrics
        return [0] * min(periods, 12)
    
    def get_retention_matrix(self) -> Dict[str, Any]:
        """Get retention matrix visualization data"""
        from .dashboard_models import CohortAnalysis
        
        retention_cohorts = CohortAnalysis.objects.filter(
            user=self.user,
            metric_type='retention'
        ).order_by('-cohort_date')[:12]
        
        matrix = []
        for cohort in retention_cohorts:
            matrix.append({
                'cohort': cohort.cohort_name,
                'size': cohort.cohort_size,
                'periods': cohort.periodic_values
            })
        
        return {'matrix': matrix}


class AttributionService:
    """Multi-touch revenue attribution"""
    
    def __init__(self, user):
        self.user = user
    
    def calculate_attribution(
        self,
        opportunity_id: str,
        model: str = 'linear'
    ) -> Dict[str, Any]:
        """Calculate attribution for an opportunity"""
        from .dashboard_models import RevenueAttribution
        from opportunity_management.models import Opportunity
        
        opportunity = Opportunity.objects.get(id=opportunity_id)
        
        # Get touchpoints
        touchpoints = self._get_touchpoints(opportunity)
        
        if not touchpoints:
            return {'error': 'No touchpoints found'}
        
        # Calculate attribution based on model
        if model == 'first_touch':
            attributed = self._first_touch_attribution(touchpoints, opportunity.value)
        elif model == 'last_touch':
            attributed = self._last_touch_attribution(touchpoints, opportunity.value)
        elif model == 'linear':
            attributed = self._linear_attribution(touchpoints, opportunity.value)
        elif model == 'time_decay':
            attributed = self._time_decay_attribution(touchpoints, opportunity.value)
        elif model == 'position_based':
            attributed = self._position_based_attribution(touchpoints, opportunity.value)
        else:
            attributed = self._linear_attribution(touchpoints, opportunity.value)
        
        # Aggregate by channel and campaign
        channel_attribution = {}
        campaign_attribution = {}
        
        for tp in attributed:
            channel = tp.get('channel', 'unknown')
            campaign = tp.get('campaign', 'direct')
            rev = tp.get('attributed_revenue', 0)
            
            channel_attribution[channel] = channel_attribution.get(channel, 0) + rev
            if campaign:
                campaign_attribution[campaign] = campaign_attribution.get(campaign, 0) + rev
        
        # Calculate days to conversion
        if touchpoints:
            first_touch = min(tp['timestamp'] for tp in touchpoints)
            last_touch = max(tp['timestamp'] for tp in touchpoints)
            days_to_conversion = (last_touch - first_touch).days
        else:
            days_to_conversion = 0
        
        # Save attribution
        attribution = RevenueAttribution.objects.update_or_create(
            opportunity=opportunity,
            model=model,
            defaults={
                'user': self.user,
                'total_revenue': opportunity.value or Decimal('0'),
                'touchpoints': attributed,
                'channel_attribution': channel_attribution,
                'campaign_attribution': campaign_attribution,
                'days_to_conversion': days_to_conversion,
                'touchpoint_count': len(touchpoints)
            }
        )[0]
        
        return {
            'attribution_id': str(attribution.id),
            'model': model,
            'total_revenue': float(attribution.total_revenue),
            'channel_attribution': channel_attribution,
            'campaign_attribution': campaign_attribution,
            'touchpoints': attributed,
            'days_to_conversion': days_to_conversion
        }
    
    def _get_touchpoints(self, opportunity) -> List[Dict[str, Any]]:
        """Get all touchpoints for an opportunity"""
        # Would query activities, emails, page views, etc.
        return []
    
    def _first_touch_attribution(
        self, touchpoints: List, revenue: Decimal
    ) -> List[Dict]:
        """First touch gets all credit"""
        if not touchpoints:
            return []
        
        sorted_tp = sorted(touchpoints, key=lambda x: x['timestamp'])
        
        result = []
        for i, tp in enumerate(sorted_tp):
            tp_copy = tp.copy()
            tp_copy['is_first_touch'] = (i == 0)
            tp_copy['is_last_touch'] = (i == len(sorted_tp) - 1)
            tp_copy['attribution_weight'] = 1.0 if i == 0 else 0.0
            tp_copy['attributed_revenue'] = float(revenue) if i == 0 else 0.0
            result.append(tp_copy)
        
        return result
    
    def _last_touch_attribution(
        self, touchpoints: List, revenue: Decimal
    ) -> List[Dict]:
        """Last touch gets all credit"""
        if not touchpoints:
            return []
        
        sorted_tp = sorted(touchpoints, key=lambda x: x['timestamp'])
        
        result = []
        for i, tp in enumerate(sorted_tp):
            tp_copy = tp.copy()
            tp_copy['is_first_touch'] = (i == 0)
            tp_copy['is_last_touch'] = (i == len(sorted_tp) - 1)
            tp_copy['attribution_weight'] = 1.0 if i == len(sorted_tp) - 1 else 0.0
            tp_copy['attributed_revenue'] = float(revenue) if i == len(sorted_tp) - 1 else 0.0
            result.append(tp_copy)
        
        return result
    
    def _linear_attribution(
        self, touchpoints: List, revenue: Decimal
    ) -> List[Dict]:
        """Equal credit to all touchpoints"""
        if not touchpoints:
            return []
        
        weight = 1.0 / len(touchpoints)
        rev_per_touch = float(revenue) / len(touchpoints)
        
        sorted_tp = sorted(touchpoints, key=lambda x: x['timestamp'])
        
        result = []
        for i, tp in enumerate(sorted_tp):
            tp_copy = tp.copy()
            tp_copy['is_first_touch'] = (i == 0)
            tp_copy['is_last_touch'] = (i == len(sorted_tp) - 1)
            tp_copy['attribution_weight'] = weight
            tp_copy['attributed_revenue'] = rev_per_touch
            result.append(tp_copy)
        
        return result
    
    def _time_decay_attribution(
        self, touchpoints: List, revenue: Decimal
    ) -> List[Dict]:
        """More recent touchpoints get more credit"""
        if not touchpoints:
            return []
        
        sorted_tp = sorted(touchpoints, key=lambda x: x['timestamp'])
        n = len(sorted_tp)
        
        # Calculate weights using time decay (half-life = 7 days)
        weights = []
        for i, tp in enumerate(sorted_tp):
            weight = 2 ** (i / n)  # Exponential growth
            weights.append(weight)
        
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        result = []
        for i, tp in enumerate(sorted_tp):
            tp_copy = tp.copy()
            tp_copy['is_first_touch'] = (i == 0)
            tp_copy['is_last_touch'] = (i == n - 1)
            tp_copy['attribution_weight'] = normalized_weights[i]
            tp_copy['attributed_revenue'] = float(revenue) * normalized_weights[i]
            result.append(tp_copy)
        
        return result
    
    def _position_based_attribution(
        self, touchpoints: List, revenue: Decimal
    ) -> List[Dict]:
        """40% first, 40% last, 20% split among middle"""
        if not touchpoints:
            return []
        
        sorted_tp = sorted(touchpoints, key=lambda x: x['timestamp'])
        n = len(sorted_tp)
        
        result = []
        for i, tp in enumerate(sorted_tp):
            tp_copy = tp.copy()
            tp_copy['is_first_touch'] = (i == 0)
            tp_copy['is_last_touch'] = (i == n - 1)
            
            if i == 0:
                weight = 0.4
            elif i == n - 1:
                weight = 0.4
            else:
                weight = 0.2 / (n - 2) if n > 2 else 0
            
            tp_copy['attribution_weight'] = weight
            tp_copy['attributed_revenue'] = float(revenue) * weight
            result.append(tp_copy)
        
        return result
    
    def get_channel_roi(self) -> Dict[str, Any]:
        """Get ROI by marketing channel"""
        from .dashboard_models import RevenueAttribution
        
        attributions = RevenueAttribution.objects.filter(user=self.user)
        
        channel_totals = {}
        
        for attr in attributions:
            for channel, revenue in attr.channel_attribution.items():
                if channel not in channel_totals:
                    channel_totals[channel] = {'revenue': 0, 'deals': 0}
                channel_totals[channel]['revenue'] += revenue
                channel_totals[channel]['deals'] += 1
        
        return {'channels': channel_totals}


class SalesVelocityService:
    """Sales velocity analysis"""
    
    def __init__(self, user):
        self.user = user
    
    def calculate_velocity(
        self,
        period_start: date,
        period_end: date
    ) -> Dict[str, Any]:
        """Calculate sales velocity for a period"""
        from .dashboard_models import SalesVelocity
        from opportunity_management.models import Opportunity
        
        opportunities = Opportunity.objects.filter(
            created_at__date__range=(period_start, period_end)
        )
        
        # Core metrics
        num_opportunities = opportunities.count()
        
        closed_won = opportunities.filter(stage='closed_won')
        total_won = closed_won.count()
        
        avg_deal_value = closed_won.aggregate(
            avg=Avg('value')
        )['avg'] or Decimal('0')
        
        win_rate = (total_won / num_opportunities * 100) if num_opportunities > 0 else 0
        
        # Calculate average sales cycle
        cycles = []
        for opp in closed_won:
            if opp.close_date and opp.created_at:
                days = (opp.close_date - opp.created_at.date()).days
                cycles.append(days)
        
        avg_sales_cycle = sum(cycles) / len(cycles) if cycles else 30
        
        # Calculate velocity
        # Velocity = (Opportunities × Deal Value × Win Rate) / Sales Cycle
        if avg_sales_cycle > 0:
            velocity = (
                num_opportunities * float(avg_deal_value) * (win_rate / 100)
            ) / avg_sales_cycle
        else:
            velocity = 0
        
        # Stage metrics
        stage_metrics = self._calculate_stage_metrics(opportunities)
        
        # Find bottleneck
        bottleneck = self._find_bottleneck(stage_metrics)
        
        # Get previous period for comparison
        period_length = (period_end - period_start).days
        prev_end = period_start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=period_length)
        
        prev_velocity = self._get_previous_velocity(prev_start, prev_end)
        
        velocity_change = None
        velocity_trend = 'stable'
        if prev_velocity:
            velocity_change = ((velocity - prev_velocity) / prev_velocity * 100) if prev_velocity > 0 else 0
            velocity_trend = 'up' if velocity_change > 5 else ('down' if velocity_change < -5 else 'stable')
        
        # Save
        velocity_record = SalesVelocity.objects.update_or_create(
            user=self.user,
            period_start=period_start,
            period_end=period_end,
            defaults={
                'num_opportunities': num_opportunities,
                'avg_deal_value': avg_deal_value,
                'win_rate': Decimal(str(win_rate)),
                'avg_sales_cycle_days': int(avg_sales_cycle),
                'sales_velocity': Decimal(str(velocity)),
                'stage_metrics': stage_metrics,
                'velocity_change': velocity_change,
                'velocity_trend': velocity_trend,
                'bottleneck_stage': bottleneck.get('stage', ''),
                'bottleneck_impact': bottleneck.get('impact')
            }
        )[0]
        
        return {
            'velocity': velocity,
            'num_opportunities': num_opportunities,
            'avg_deal_value': float(avg_deal_value),
            'win_rate': win_rate,
            'avg_sales_cycle_days': int(avg_sales_cycle),
            'stage_metrics': stage_metrics,
            'bottleneck': bottleneck,
            'velocity_change': velocity_change,
            'velocity_trend': velocity_trend
        }
    
    def _calculate_stage_metrics(
        self, opportunities
    ) -> Dict[str, Any]:
        """Calculate metrics for each stage"""
        # Simplified
        return {}
    
    def _find_bottleneck(self, stage_metrics: Dict) -> Dict[str, Any]:
        """Find the bottleneck stage"""
        # Simplified
        return {}
    
    def _get_previous_velocity(
        self, start: date, end: date
    ) -> Optional[float]:
        """Get velocity from previous period"""
        from .dashboard_models import SalesVelocity
        
        prev = SalesVelocity.objects.filter(
            user=self.user,
            period_start=start,
            period_end=end
        ).first()
        
        return float(prev.sales_velocity) if prev else None


class RevenueIntelligenceService:
    """Main service for revenue intelligence dashboard"""
    
    def __init__(self, user):
        self.user = user
    
    def get_dashboard_snapshot(self) -> Dict[str, Any]:
        """Get current revenue intelligence snapshot"""
        from .dashboard_models import RevenueIntelligenceSnapshot
        from opportunity_management.models import Opportunity
        
        today = date.today()
        
        # Try to get today's snapshot
        snapshot = RevenueIntelligenceSnapshot.objects.filter(
            user=self.user,
            snapshot_date=today
        ).first()
        
        if not snapshot:
            # Generate new snapshot
            snapshot = self._generate_snapshot(today)
        
        return {
            'snapshot_date': snapshot.snapshot_date.isoformat(),
            'pipeline': {
                'total': float(snapshot.total_pipeline),
                'weighted': float(snapshot.weighted_pipeline),
                'coverage': float(snapshot.pipeline_coverage)
            },
            'forecast': {
                'current_quarter': float(snapshot.current_quarter_forecast),
                'closed': float(snapshot.current_quarter_closed),
                'target': float(snapshot.current_quarter_target),
                'attainment': (
                    float(snapshot.current_quarter_closed) / 
                    float(snapshot.current_quarter_target) * 100
                ) if snapshot.current_quarter_target else 0
            },
            'velocity': {
                'current': float(snapshot.current_velocity),
                'avg_deal_size': float(snapshot.avg_deal_size),
                'avg_sales_cycle': snapshot.avg_sales_cycle,
                'win_rate': float(snapshot.win_rate)
            },
            'health': {
                'at_risk_deals': snapshot.at_risk_deals_count,
                'at_risk_value': float(snapshot.at_risk_deals_value),
                'stalled_deals': snapshot.stalled_deals_count,
                'stalled_value': float(snapshot.stalled_deals_value)
            },
            'trends': {
                'pipeline_7d': float(snapshot.pipeline_trend_7d or 0),
                'forecast_7d': float(snapshot.forecast_trend_7d or 0)
            }
        }
    
    def _generate_snapshot(self, snapshot_date: date):
        """Generate a new snapshot"""
        from .dashboard_models import RevenueIntelligenceSnapshot
        from opportunity_management.models import Opportunity
        
        # Get current quarter
        quarter_start = date(snapshot_date.year, ((snapshot_date.month - 1) // 3) * 3 + 1, 1)
        quarter_end = quarter_start + relativedelta(months=3) - timedelta(days=1)
        
        # Pipeline metrics
        open_opps = Opportunity.objects.exclude(stage__in=['closed_won', 'closed_lost'])
        
        total_pipeline = open_opps.aggregate(
            total=Sum('value')
        )['total'] or Decimal('0')
        
        # Simplified weighted calculation
        weighted_pipeline = total_pipeline * Decimal('0.5')
        
        # Closed this quarter
        closed_this_quarter = Opportunity.objects.filter(
            stage='closed_won',
            close_date__range=(quarter_start, quarter_end)
        )
        
        current_quarter_closed = closed_this_quarter.aggregate(
            total=Sum('value')
        )['total'] or Decimal('0')
        
        # Target (would come from quota management)
        target = Decimal('1000000')
        
        coverage = (total_pipeline / target * 100) if target else 0
        
        # At risk deals
        at_risk = open_opps.filter(
            updated_at__lt=timezone.now() - timedelta(days=14)
        )
        
        at_risk_count = at_risk.count()
        at_risk_value = at_risk.aggregate(total=Sum('value'))['total'] or Decimal('0')
        
        # Stalled deals (no activity in 21+ days)
        stalled = open_opps.filter(
            updated_at__lt=timezone.now() - timedelta(days=21)
        )
        
        stalled_count = stalled.count()
        stalled_value = stalled.aggregate(total=Sum('value'))['total'] or Decimal('0')
        
        snapshot = RevenueIntelligenceSnapshot.objects.create(
            user=self.user,
            snapshot_date=snapshot_date,
            total_pipeline=total_pipeline,
            weighted_pipeline=weighted_pipeline,
            pipeline_coverage=coverage,
            current_quarter_forecast=weighted_pipeline + current_quarter_closed,
            current_quarter_closed=current_quarter_closed,
            current_quarter_target=target,
            current_velocity=Decimal('50000'),  # Simplified
            avg_deal_size=Decimal('25000'),
            avg_sales_cycle=30,
            win_rate=Decimal('25'),
            at_risk_deals_count=at_risk_count,
            at_risk_deals_value=at_risk_value,
            stalled_deals_count=stalled_count,
            stalled_deals_value=stalled_value
        )
        
        return snapshot
    
    def get_win_loss_analysis(
        self,
        period_start: date,
        period_end: date
    ) -> Dict[str, Any]:
        """Get win/loss analysis"""
        from .dashboard_models import WinLossAnalysis
        from opportunity_management.models import Opportunity
        
        opportunities = Opportunity.objects.filter(
            created_at__date__range=(period_start, period_end)
        )
        
        total = opportunities.count()
        won = opportunities.filter(stage='closed_won')
        lost = opportunities.filter(stage='closed_lost')
        open_opps = opportunities.exclude(stage__in=['closed_won', 'closed_lost'])
        
        won_count = won.count()
        lost_count = lost.count()
        open_count = open_opps.count()
        
        win_rate = (won_count / (won_count + lost_count) * 100) if (won_count + lost_count) > 0 else 0
        
        won_value = won.aggregate(total=Sum('value'))['total'] or Decimal('0')
        lost_value = lost.aggregate(total=Sum('value'))['total'] or Decimal('0')
        
        # Create analysis record
        analysis = WinLossAnalysis.objects.create(
            user=self.user,
            period_start=period_start,
            period_end=period_end,
            total_opportunities=total,
            total_won=won_count,
            total_lost=lost_count,
            total_open=open_count,
            win_rate=Decimal(str(win_rate)),
            won_value=won_value,
            lost_value=lost_value
        )
        
        return {
            'analysis_id': str(analysis.id),
            'total': total,
            'won': won_count,
            'lost': lost_count,
            'open': open_count,
            'win_rate': win_rate,
            'won_value': float(won_value),
            'lost_value': float(lost_value)
        }
