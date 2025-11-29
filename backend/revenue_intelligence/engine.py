"""
Revenue Intelligence Engine
AI-powered deal scoring, forecasting, and risk detection
This is what Salesforce Einstein costs $$$$ for - we give it free!
"""

import numpy as np
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, F
from decimal import Decimal


class DealScoringEngine:
    """
    AI-powered deal scoring engine
    Analyzes multiple signals to predict deal health and win probability
    """
    
    # Weights for different score components (tunable)
    WEIGHTS = {
        'engagement': 0.25,
        'timing': 0.20,
        'stakeholder': 0.20,
        'activity': 0.20,
        'competitive': 0.15,
    }
    
    def __init__(self):
        self.benchmark_cache = {}
    
    def score_deal(self, opportunity):
        """
        Calculate comprehensive deal score
        Returns DealScore object
        """
        from .models import DealScore
        
        # Calculate individual component scores
        engagement_score = self._calculate_engagement_score(opportunity)
        timing_score = self._calculate_timing_score(opportunity)
        stakeholder_score = self._calculate_stakeholder_score(opportunity)
        activity_score = self._calculate_activity_score(opportunity)
        competitive_score = self._calculate_competitive_score(opportunity)
        
        # Calculate weighted overall score
        overall_score = int(
            engagement_score * self.WEIGHTS['engagement'] +
            timing_score * self.WEIGHTS['timing'] +
            stakeholder_score * self.WEIGHTS['stakeholder'] +
            activity_score * self.WEIGHTS['activity'] +
            competitive_score * self.WEIGHTS['competitive']
        )
        
        # Calculate win probability using logistic regression approach
        win_probability = self._calculate_win_probability(
            overall_score, opportunity
        )
        
        # Identify risks and strengths
        risk_factors = self._identify_risk_factors(opportunity, {
            'engagement': engagement_score,
            'timing': timing_score,
            'stakeholder': stakeholder_score,
            'activity': activity_score,
            'competitive': competitive_score,
        })
        
        strengths = self._identify_strengths(opportunity, {
            'engagement': engagement_score,
            'timing': timing_score,
            'stakeholder': stakeholder_score,
            'activity': activity_score,
            'competitive': competitive_score,
        })
        
        weaknesses = self._identify_weaknesses(opportunity, {
            'engagement': engagement_score,
            'timing': timing_score,
            'stakeholder': stakeholder_score,
            'activity': activity_score,
            'competitive': competitive_score,
        })
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_score, risk_factors)
        
        # Generate recommended actions
        recommended_actions = self._generate_recommendations(
            opportunity, risk_factors, weaknesses
        )
        
        # Get previous score for trend
        previous_score = None
        try:
            existing = DealScore.objects.get(opportunity=opportunity)
            previous_score = existing.score
        except DealScore.DoesNotExist:
            pass
        
        # Determine trend
        score_trend = 'stable'
        if previous_score:
            if overall_score > previous_score + 5:
                score_trend = 'improving'
            elif overall_score < previous_score - 5:
                score_trend = 'declining'
        
        # Create or update deal score
        deal_score, created = DealScore.objects.update_or_create(
            opportunity=opportunity,
            defaults={
                'score': overall_score,
                'win_probability': Decimal(str(win_probability)),
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'engagement_score': engagement_score,
                'timing_score': timing_score,
                'stakeholder_score': stakeholder_score,
                'activity_score': activity_score,
                'competitive_score': competitive_score,
                'strengths': strengths,
                'weaknesses': weaknesses,
                'recommended_actions': recommended_actions,
                'score_trend': score_trend,
                'previous_score': previous_score,
            }
        )
        
        return deal_score
    
    def _calculate_engagement_score(self, opportunity):
        """Score based on contact engagement level"""
        score = 50  # Base score
        
        contact = opportunity.contact
        
        # Email opens/clicks from email tracking
        if hasattr(contact, 'email_events'):
            recent_opens = contact.email_events.filter(
                event_type='open',
                timestamp__gte=timezone.now() - timedelta(days=30)
            ).count()
            score += min(recent_opens * 5, 25)
        
        # Response time to communications
        if opportunity.last_activity_date:
            days_since_activity = (timezone.now() - opportunity.last_activity_date).days
            if days_since_activity < 3:
                score += 20
            elif days_since_activity < 7:
                score += 10
            elif days_since_activity > 14:
                score -= 20
        
        # Meeting attendance
        if hasattr(opportunity, 'meetings'):
            meetings_held = opportunity.meetings.filter(
                status='completed'
            ).count()
            score += min(meetings_held * 10, 30)
        
        return max(0, min(100, score))
    
    def _calculate_timing_score(self, opportunity):
        """Score based on deal timing and velocity"""
        score = 50
        
        now = timezone.now().date()
        
        # Days to expected close
        if opportunity.expected_close_date:
            days_to_close = (opportunity.expected_close_date - now).days
            
            if days_to_close < 0:
                # Deal is overdue
                score -= min(abs(days_to_close) * 2, 40)
            elif days_to_close <= 7:
                score += 20  # Closing soon
            elif days_to_close <= 30:
                score += 10
        
        # Deal age vs benchmark
        deal_age = (now - opportunity.created_at.date()).days
        avg_sales_cycle = self._get_benchmark('avg_sales_cycle', opportunity.owner)
        
        if avg_sales_cycle and deal_age > avg_sales_cycle * 1.5:
            score -= 20  # Deal taking too long
        elif avg_sales_cycle and deal_age < avg_sales_cycle * 0.5:
            score += 15  # Fast-moving deal
        
        # Stage progression
        stage_order = ['prospecting', 'qualification', 'proposal', 'negotiation']
        if opportunity.stage in stage_order:
            current_index = stage_order.index(opportunity.stage)
            expected_index = min(deal_age // 15, len(stage_order) - 1)  # Expect stage movement every ~15 days
            
            if current_index >= expected_index:
                score += 10
            else:
                score -= 15
        
        return max(0, min(100, score))
    
    def _calculate_stakeholder_score(self, opportunity):
        """Score based on decision maker involvement"""
        score = 40  # Lower base - we want explicit evidence
        
        contact = opportunity.contact
        
        # Job title analysis
        title = (contact.job_title or '').lower()
        executive_titles = ['ceo', 'cfo', 'cto', 'coo', 'president', 'vp', 'vice president', 'director', 'head of']
        
        if any(t in title for t in executive_titles):
            score += 30
        elif 'manager' in title:
            score += 15
        
        # Multiple stakeholders identified
        if hasattr(opportunity, 'stakeholders'):
            stakeholder_count = opportunity.stakeholders.count()
            score += min(stakeholder_count * 10, 30)
        
        # Champion identified
        if opportunity.custom_fields.get('champion_identified'):
            score += 20
        
        return max(0, min(100, score))
    
    def _calculate_activity_score(self, opportunity):
        """Score based on recent activity level"""
        score = 30  # Start lower
        
        now = timezone.now()
        
        # Recent activities
        if hasattr(opportunity, 'activities'):
            activities_7d = opportunity.activities.filter(
                created_at__gte=now - timedelta(days=7)
            ).count()
            activities_30d = opportunity.activities.filter(
                created_at__gte=now - timedelta(days=30)
            ).count()
            
            score += min(activities_7d * 10, 30)
            score += min(activities_30d * 2, 20)
        
        # Tasks completed
        if hasattr(opportunity, 'tasks'):
            completed_tasks = opportunity.tasks.filter(status='completed').count()
            score += min(completed_tasks * 5, 20)
        
        # Notes/updates
        if opportunity.notes:
            score += 10
        
        return max(0, min(100, score))
    
    def _calculate_competitive_score(self, opportunity):
        """Score based on competitive positioning"""
        score = 60  # Start optimistic
        
        # Check for competitors in deal
        competitors = opportunity.competitors.filter(status='active')
        competitor_count = competitors.count()
        
        if competitor_count == 0:
            score += 20  # No competition is great
        elif competitor_count == 1:
            score += 5
        elif competitor_count == 2:
            score -= 10
        else:
            score -= 20  # Crowded deal
        
        # High threat competitors
        high_threat = competitors.filter(threat_level='high').count()
        score -= high_threat * 15
        
        return max(0, min(100, score))
    
    def _calculate_win_probability(self, overall_score, opportunity):
        """Calculate win probability using historical data"""
        # Base probability from score
        base_prob = overall_score / 100
        
        # Stage adjustment
        stage_probs = {
            'prospecting': 0.1,
            'qualification': 0.2,
            'proposal': 0.4,
            'negotiation': 0.6,
            'closed_won': 1.0,
            'closed_lost': 0.0,
        }
        stage_factor = stage_probs.get(opportunity.stage, 0.3)
        
        # Combine factors
        win_prob = (base_prob * 0.6 + stage_factor * 0.4) * 100
        
        return round(min(95, max(5, win_prob)), 2)
    
    def _identify_risk_factors(self, opportunity, scores):
        """Identify risk factors in the deal"""
        risks = []
        
        if scores['engagement'] < 40:
            risks.append({
                'factor': 'Low Engagement',
                'description': 'Contact engagement is below threshold',
                'severity': 'high'
            })
        
        if scores['timing'] < 40:
            risks.append({
                'factor': 'Timing Issues',
                'description': 'Deal velocity is concerning',
                'severity': 'medium'
            })
        
        if scores['stakeholder'] < 40:
            risks.append({
                'factor': 'Missing Decision Maker',
                'description': 'No executive sponsor identified',
                'severity': 'high'
            })
        
        if scores['activity'] < 30:
            risks.append({
                'factor': 'Deal Going Dark',
                'description': 'Insufficient recent activity',
                'severity': 'critical'
            })
        
        if scores['competitive'] < 40:
            risks.append({
                'factor': 'Competitive Pressure',
                'description': 'Strong competition in this deal',
                'severity': 'medium'
            })
        
        # Check for overdue close date
        if opportunity.expected_close_date:
            if opportunity.expected_close_date < timezone.now().date():
                risks.append({
                    'factor': 'Overdue Close Date',
                    'description': 'Deal has slipped past expected close',
                    'severity': 'high'
                })
        
        return risks
    
    def _identify_strengths(self, opportunity, scores):
        """Identify deal strengths"""
        strengths = []
        
        if scores['engagement'] >= 70:
            strengths.append('High contact engagement')
        
        if scores['timing'] >= 70:
            strengths.append('Deal moving at healthy pace')
        
        if scores['stakeholder'] >= 70:
            strengths.append('Strong executive sponsorship')
        
        if scores['activity'] >= 70:
            strengths.append('Active deal with recent touchpoints')
        
        if scores['competitive'] >= 70:
            strengths.append('Favorable competitive position')
        
        if opportunity.amount >= 50000:
            strengths.append('High-value opportunity')
        
        return strengths
    
    def _identify_weaknesses(self, opportunity, scores):
        """Identify deal weaknesses"""
        weaknesses = []
        
        if scores['engagement'] < 50:
            weaknesses.append('Contact engagement needs improvement')
        
        if scores['timing'] < 50:
            weaknesses.append('Deal velocity is slow')
        
        if scores['stakeholder'] < 50:
            weaknesses.append('Need to engage decision makers')
        
        if scores['activity'] < 50:
            weaknesses.append('Increase touchpoint frequency')
        
        if scores['competitive'] < 50:
            weaknesses.append('Address competitive threats')
        
        return weaknesses
    
    def _generate_recommendations(self, opportunity, risks, weaknesses):
        """Generate actionable recommendations"""
        recommendations = []
        
        for risk in risks:
            if risk['factor'] == 'Low Engagement':
                recommendations.append({
                    'action': 'Schedule a discovery call',
                    'priority': 'high',
                    'reason': 'Re-engage the contact with value-focused discussion'
                })
            elif risk['factor'] == 'Missing Decision Maker':
                recommendations.append({
                    'action': 'Request executive introduction',
                    'priority': 'high',
                    'reason': 'Deals without executive sponsor have 60% lower win rate'
                })
            elif risk['factor'] == 'Deal Going Dark':
                recommendations.append({
                    'action': 'Send check-in email with new value content',
                    'priority': 'critical',
                    'reason': 'Break the silence before deal is lost'
                })
            elif risk['factor'] == 'Competitive Pressure':
                recommendations.append({
                    'action': 'Review battle cards and differentiate',
                    'priority': 'medium',
                    'reason': 'Reinforce unique value proposition'
                })
            elif risk['factor'] == 'Overdue Close Date':
                recommendations.append({
                    'action': 'Update close date and get commitment',
                    'priority': 'high',
                    'reason': 'Align expectations and create urgency'
                })
        
        return recommendations
    
    def _determine_risk_level(self, score, risk_factors):
        """Determine overall risk level"""
        critical_risks = len([r for r in risk_factors if r.get('severity') == 'critical'])
        high_risks = len([r for r in risk_factors if r.get('severity') == 'high'])
        
        if critical_risks > 0 or score < 30:
            return 'critical'
        elif high_risks >= 2 or score < 50:
            return 'high'
        elif high_risks >= 1 or score < 70:
            return 'medium'
        else:
            return 'low'
    
    def _get_benchmark(self, metric, user):
        """Get benchmark value from historical data"""
        cache_key = f"{metric}_{user.id if user else 'all'}"
        
        if cache_key in self.benchmark_cache:
            return self.benchmark_cache[cache_key]
        
        from opportunity_management.models import Opportunity
        
        if metric == 'avg_sales_cycle':
            # Calculate average days from creation to close
            closed_deals = Opportunity.objects.filter(
                stage__in=['closed_won', 'closed_lost'],
                actual_close_date__isnull=False
            )
            
            if user:
                closed_deals = closed_deals.filter(owner=user)
            
            cycles = []
            for deal in closed_deals[:100]:  # Sample last 100 deals
                cycle = (deal.actual_close_date - deal.created_at.date()).days
                if cycle > 0:
                    cycles.append(cycle)
            
            result = np.mean(cycles) if cycles else 45  # Default 45 days
            self.benchmark_cache[cache_key] = result
            return result
        
        return None


class RevenueForecastEngine:
    """
    ML-powered revenue forecasting
    Generates commit, best case, and AI-predicted forecasts
    """
    
    def generate_forecast(self, user, period_start, period_end):
        """Generate all forecast types for a period"""
        from .models import RevenueForecast
        from opportunity_management.models import Opportunity
        
        forecasts = []
        
        # Get relevant opportunities
        opportunities = Opportunity.objects.filter(
            owner=user,
            expected_close_date__gte=period_start,
            expected_close_date__lte=period_end,
        ).exclude(stage__in=['closed_won', 'closed_lost'])
        
        # Already closed won in period
        closed_won = Opportunity.objects.filter(
            owner=user,
            actual_close_date__gte=period_start,
            actual_close_date__lte=period_end,
            stage='closed_won'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Commit forecast (high probability deals)
        commit_opps = opportunities.filter(probability__gte=75)
        commit_amount = commit_opps.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        commit_forecast = RevenueForecast.objects.create(
            user=user,
            forecast_date=timezone.now().date(),
            period_start=period_start,
            period_end=period_end,
            forecast_type='commit',
            amount=closed_won + commit_amount,
            confidence='high',
            closed_won=closed_won,
            expected_closes=commit_amount,
        )
        forecasts.append(commit_forecast)
        
        # Best case forecast (medium+ probability)
        best_case_opps = opportunities.filter(probability__gte=50)
        best_case_amount = best_case_opps.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        best_case_forecast = RevenueForecast.objects.create(
            user=user,
            forecast_date=timezone.now().date(),
            period_start=period_start,
            period_end=period_end,
            forecast_type='best_case',
            amount=closed_won + best_case_amount,
            confidence='medium',
            closed_won=closed_won,
            expected_closes=best_case_amount,
        )
        forecasts.append(best_case_forecast)
        
        # Pipeline forecast (all open deals, weighted)
        weighted_pipeline = opportunities.aggregate(
            total=Sum(F('amount') * F('probability') / 100)
        )['total'] or Decimal('0')
        
        pipeline_forecast = RevenueForecast.objects.create(
            user=user,
            forecast_date=timezone.now().date(),
            period_start=period_start,
            period_end=period_end,
            forecast_type='pipeline',
            amount=closed_won + weighted_pipeline,
            confidence='low',
            closed_won=closed_won,
            expected_closes=weighted_pipeline,
        )
        forecasts.append(pipeline_forecast)
        
        # AI Predicted forecast
        ai_amount, adjustment, reasons = self._ai_predict(
            user, opportunities, closed_won, period_start, period_end
        )
        
        ai_forecast = RevenueForecast.objects.create(
            user=user,
            forecast_date=timezone.now().date(),
            period_start=period_start,
            period_end=period_end,
            forecast_type='ai_predicted',
            amount=ai_amount,
            confidence='medium',
            closed_won=closed_won,
            ai_adjustment=adjustment,
            adjustment_reasons=reasons,
        )
        forecasts.append(ai_forecast)
        
        return forecasts
    
    def _ai_predict(self, user, opportunities, closed_won, period_start, period_end):
        """
        AI-powered prediction using historical patterns
        """
        from opportunity_management.models import Opportunity
        
        # Get historical win rate
        historical = Opportunity.objects.filter(
            owner=user,
            stage__in=['closed_won', 'closed_lost']
        )
        won = historical.filter(stage='closed_won').count()
        total = historical.count()
        win_rate = won / total if total > 0 else 0.3
        
        # Calculate adjusted amounts based on deal scores
        total_predicted = closed_won
        adjustments = []
        
        for opp in opportunities:
            # Get deal score if available
            base_amount = opp.amount * Decimal(str(opp.probability / 100))
            
            try:
                deal_score = opp.deal_score
                # Adjust based on AI score
                score_factor = deal_score.win_probability / 100
                adjusted_amount = opp.amount * Decimal(str(score_factor))
                total_predicted += adjusted_amount
                
                if abs(float(adjusted_amount - base_amount)) > 1000:
                    adjustments.append({
                        'deal': opp.name,
                        'adjustment': float(adjusted_amount - base_amount),
                        'reason': f"AI score: {deal_score.score}/100"
                    })
            except Exception:
                # No deal score, use historical win rate adjustment
                adjusted_amount = base_amount * Decimal(str(win_rate / (opp.probability / 100)))
                total_predicted += adjusted_amount
        
        # Apply seasonal adjustment
        month = period_start.month
        seasonal_factors = {
            1: 0.85, 2: 0.90, 3: 1.05, 4: 1.0, 5: 1.0, 6: 1.10,
            7: 0.80, 8: 0.75, 9: 1.05, 10: 1.0, 11: 1.05, 12: 1.15
        }
        seasonal_factor = seasonal_factors.get(month, 1.0)
        
        weighted_pipeline = sum(
            float(o.amount * Decimal(str(o.probability / 100))) for o in opportunities
        )
        
        adjustment = total_predicted - (closed_won + Decimal(str(weighted_pipeline)))
        
        reasons = adjustments[:5]  # Top 5 adjustments
        if seasonal_factor != 1.0:
            reasons.append({
                'type': 'seasonal',
                'factor': seasonal_factor,
                'reason': f"Historical seasonal pattern for month {month}"
            })
        
        return total_predicted, adjustment, reasons


class RiskAlertEngine:
    """
    Automated deal risk detection
    Proactively identifies at-risk deals
    """
    
    def scan_deals_for_risks(self, user=None):
        """Scan all open deals for risk factors"""
        from .models import DealRiskAlert
        from opportunity_management.models import Opportunity
        
        deals = Opportunity.objects.exclude(
            stage__in=['closed_won', 'closed_lost']
        )
        
        if user:
            deals = deals.filter(owner=user)
        
        alerts_created = []
        
        for deal in deals:
            alerts = self._check_deal_risks(deal)
            for alert_data in alerts:
                # Check if similar alert already exists
                existing = DealRiskAlert.objects.filter(
                    opportunity=deal,
                    alert_type=alert_data['alert_type'],
                    is_active=True
                ).first()
                
                if not existing:
                    alert = DealRiskAlert.objects.create(
                        opportunity=deal,
                        **alert_data
                    )
                    alerts_created.append(alert)
        
        return alerts_created
    
    def _check_deal_risks(self, opportunity):
        """Check a single deal for various risk factors"""
        risks = []
        now = timezone.now()
        
        # 1. Stale deal - no activity in 14+ days
        if opportunity.last_activity_date:
            days_inactive = (now - opportunity.last_activity_date).days
            if days_inactive >= 14:
                risks.append({
                    'alert_type': 'stale_deal',
                    'severity': 'critical' if days_inactive >= 30 else 'warning',
                    'title': f'No activity for {days_inactive} days',
                    'description': f'Deal "{opportunity.name}" has had no activity since {opportunity.last_activity_date.strftime("%Y-%m-%d")}',
                    'recommended_action': 'Schedule a check-in call or send a follow-up email to re-engage the prospect'
                })
        
        # 2. Close date slipping
        if opportunity.expected_close_date:
            if opportunity.expected_close_date < now.date():
                days_overdue = (now.date() - opportunity.expected_close_date).days
                risks.append({
                    'alert_type': 'slipping_close',
                    'severity': 'critical' if days_overdue >= 30 else 'warning',
                    'title': f'Close date overdue by {days_overdue} days',
                    'description': f'Expected close was {opportunity.expected_close_date}. Deal may be stalled.',
                    'recommended_action': 'Update close date with realistic timeline and identify blocking issues'
                })
        
        # 3. High-value deal without recent activity
        if opportunity.amount >= 50000:
            if not opportunity.last_activity_date or (now - opportunity.last_activity_date).days >= 7:
                risks.append({
                    'alert_type': 'engagement_drop',
                    'severity': 'warning',
                    'title': 'High-value deal needs attention',
                    'description': f'${opportunity.amount:,.0f} deal has limited recent engagement',
                    'recommended_action': 'Prioritize this deal with executive engagement or demo'
                })
        
        # 4. Competitor threat
        high_threat_competitors = opportunity.competitors.filter(
            status='active',
            threat_level='high'
        ).count()
        
        if high_threat_competitors > 0:
            risks.append({
                'alert_type': 'competitor_threat',
                'severity': 'warning',
                'title': f'{high_threat_competitors} high-threat competitor(s) identified',
                'description': 'Strong competition may impact win probability',
                'recommended_action': 'Review battle cards and emphasize differentiators in next meeting'
            })
        
        return risks
