"""
Advanced AI and Analytics Module for Enterprise CRM
Provides machine learning insights, predictive analytics, and automation
"""

from datetime import timedelta

import numpy as np
import pandas as pd
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, DecimalField, Sum
from django.utils import timezone

from communication_management.models import Communication
from contact_management.models import Contact
from lead_management.models import Lead
from opportunity_management.models import Opportunity
from task_management.models import Task

User = get_user_model()


class SalesForecasting:
    """Advanced sales forecasting using machine learning"""

    @staticmethod
    def forecast_revenue(period_months=3):
        """
        Forecast revenue for the next period based on historical data

        Args:
            period_months: Number of months to forecast

        Returns:
            dict: Forecast data with confidence intervals
        """
        # Get historical opportunity data
        end_date = timezone.now()
        start_date = end_date - timedelta(days=365)  # Last year

        opportunities = Opportunity.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).values('created_at', 'amount', 'probability', 'stage')

        if not opportunities:
            return {
                'forecast_amount': 0,
                'confidence_interval': [0, 0],
                'trend': 'insufficient_data',
                'recommendations': ['Need more historical data for accurate forecasting']
            }

        # Convert to DataFrame for analysis
        df = pd.DataFrame(opportunities)
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['month'] = df['created_at'].dt.to_period('M')

        # Calculate monthly revenue (weighted by probability)
        monthly_revenue = df.groupby('month').apply(
            lambda x: (x['amount'] * x['probability'] / 100).sum()
        )

        # Simple trend analysis
        if len(monthly_revenue) >= 3:
            recent_avg = monthly_revenue.tail(3).mean()
            previous_avg = monthly_revenue.head(-3).mean() if len(monthly_revenue) > 3 else recent_avg

            growth_rate = (recent_avg - previous_avg) / previous_avg if previous_avg > 0 else 0

            # Forecast based on trend
            base_forecast = recent_avg
            forecast_amount = base_forecast * (1 + growth_rate) ** period_months

            # Confidence interval (simplified)
            std_dev = monthly_revenue.std()
            confidence_lower = forecast_amount - (1.96 * std_dev)
            confidence_upper = forecast_amount + (1.96 * std_dev)

            trend = 'increasing' if growth_rate > 0.05 else ('decreasing' if growth_rate < -0.05 else 'stable')

            recommendations = SalesForecasting._generate_recommendations(
                growth_rate, monthly_revenue, df
            )

            return {
                'forecast_amount': round(forecast_amount, 2),
                'confidence_interval': [round(confidence_lower, 2), round(confidence_upper, 2)],
                'growth_rate': round(growth_rate * 100, 2),
                'trend': trend,
                'historical_average': round(recent_avg, 2),
                'recommendations': recommendations
            }

        return {
            'forecast_amount': monthly_revenue.mean(),
            'confidence_interval': [0, monthly_revenue.mean() * 2],
            'trend': 'insufficient_data',
            'recommendations': ['Need more historical data for accurate forecasting']
        }

    @staticmethod
    def _generate_recommendations(growth_rate, monthly_revenue, df):
        """Generate actionable recommendations based on forecast"""
        recommendations = []

        if growth_rate < -0.1:
            recommendations.extend([
                'Revenue declining - review sales strategy',
                'Focus on lead conversion optimization',
                'Consider additional marketing campaigns'
            ])
        elif growth_rate > 0.2:
            recommendations.extend([
                'Strong growth trend - maintain current strategy',
                'Consider scaling successful campaigns',
                'Prepare for increased demand'
            ])
        else:
            recommendations.extend([
                'Stable growth - look for optimization opportunities',
                'Analyze top-performing sales activities',
                'Consider A/B testing new approaches'
            ])

        # Stage-specific recommendations
        stage_distribution = df['stage'].value_counts()
        if 'prospecting' in stage_distribution and stage_distribution['prospecting'] > len(df) * 0.5:
            recommendations.append('High number of prospects - focus on qualification')

        return recommendations


class LeadScoring:
    """Advanced lead scoring using multiple factors"""

    @staticmethod
    def calculate_lead_score(lead):
        """
        Calculate comprehensive lead score

        Args:
            lead: Lead instance

        Returns:
            dict: Score breakdown and recommendations
        """
        score_components = {
            'demographic': LeadScoring._score_demographics(lead),
            'behavioral': LeadScoring._score_behavior(lead),
            'engagement': LeadScoring._score_engagement(lead),
            'firmographic': LeadScoring._score_firmographic(lead)
        }

        # Weighted total score
        weights = {
            'demographic': 0.3,
            'behavioral': 0.4,
            'engagement': 0.2,
            'firmographic': 0.1
        }

        total_score = sum(
            score_components[component] * weights[component]
            for component in score_components
        )

        # Determine lead quality
        if total_score >= 80:
            quality = 'hot'
            priority = 'high'
        elif total_score >= 60:
            quality = 'warm'
            priority = 'medium'
        else:
            quality = 'cold'
            priority = 'low'

        recommendations = LeadScoring._generate_lead_recommendations(
            lead, score_components, quality
        )

        return {
            'total_score': round(total_score, 1),
            'quality': quality,
            'priority': priority,
            'score_breakdown': score_components,
            'recommendations': recommendations
        }

    @staticmethod
    def _score_demographics(lead):
        """Score based on demographic information"""
        score = 50  # Base score

        # Job title scoring
        if lead.job_title:
            decision_maker_titles = [
                'ceo', 'cto', 'cfo', 'president', 'director', 'manager', 'head'
            ]
            if any(title in lead.job_title.lower() for title in decision_maker_titles):
                score += 20

        # Contact completeness
        if lead.email:
            score += 10
        if lead.phone:
            score += 10
        if lead.company_name:
            score += 10

        return min(score, 100)

    @staticmethod
    def _score_behavior(lead):
        """Score based on behavioral data"""
        score = 50

        # Communication frequency
        recent_communications = Communication.objects.filter(
            lead=lead,
            communication_date__gte=timezone.now() - timedelta(days=30)
        ).count()

        score += min(recent_communications * 5, 30)

        # Response time (if available in metadata)
        # This would be enhanced with actual tracking data

        return min(score, 100)

    @staticmethod
    def _score_engagement(lead):
        """Score based on engagement level"""
        score = 50

        # Last contact date
        if lead.last_contact_date:
            days_since_contact = (timezone.now().date() - lead.last_contact_date).days
            if days_since_contact <= 7:
                score += 20
            elif days_since_contact <= 30:
                score += 10
            elif days_since_contact > 90:
                score -= 20

        # Follow-up scheduling
        if lead.next_follow_up:
            score += 15

        return max(min(score, 100), 0)

    @staticmethod
    def _score_firmographic(lead):
        """Score based on company/firmographic data"""
        score = 50

        # Company size (if available)
        # This would be enhanced with company data integration

        # Industry fit (would require industry preferences configuration)

        # Geographic location (would require territory configuration)

        return score

    @staticmethod
    def _generate_lead_recommendations(lead, score_components, quality):
        """Generate recommendations for lead handling"""
        recommendations = []

        if quality == 'hot':
            recommendations.extend([
                'Contact immediately - high conversion potential',
                'Schedule demo or meeting within 24 hours',
                'Assign to senior sales representative'
            ])
        elif quality == 'warm':
            recommendations.extend([
                'Follow up within 2-3 business days',
                'Send relevant case studies or resources',
                'Schedule discovery call'
            ])
        else:
            recommendations.extend([
                'Add to nurturing campaign',
                'Send educational content',
                'Re-evaluate in 30 days'
            ])

        # Specific recommendations based on score components
        if score_components['engagement'] < 40:
            recommendations.append('Increase engagement through targeted content')

        if score_components['demographic'] < 40:
            recommendations.append('Gather more demographic information')

        return recommendations


class CustomerSegmentation:
    """Advanced customer segmentation analysis"""

    @staticmethod
    def segment_customers():
        """
        Segment customers based on multiple dimensions

        Returns:
            dict: Segmentation results with insights
        """
        contacts = Contact.objects.all()

        segments = {
            'high_value': [],
            'loyal': [],
            'at_risk': [],
            'new': [],
            'inactive': []
        }

        for contact in contacts:
            segment = CustomerSegmentation._classify_customer(contact)
            segments[segment].append(contact.id)

        # Generate insights for each segment
        insights = {}
        for segment_name, contact_ids in segments.items():
            insights[segment_name] = {
                'count': len(contact_ids),
                'percentage': round(len(contact_ids) / len(contacts) * 100, 1) if contacts else 0,
                'recommendations': CustomerSegmentation._get_segment_recommendations(segment_name)
            }

        return {
            'segments': segments,
            'insights': insights,
            'total_customers': len(contacts)
        }

    @staticmethod
    def _classify_customer(contact):
        """Classify a customer into a segment"""
        # Get related opportunities and communications
        opportunities = Opportunity.objects.filter(contact=contact)
        communications = Communication.objects.filter(contact=contact)

        # Calculate metrics
        total_value = opportunities.aggregate(total=Sum('amount'))['total'] or 0
        last_communication = communications.order_by('-communication_date').first()
        opportunity_count = opportunities.count()

        # Classification logic
        days_since_last_contact = 999
        if last_communication:
            days_since_last_contact = (
                timezone.now().date() - last_communication.communication_date.date()
            ).days

        # High value customers
        if total_value > 10000 or opportunity_count > 3:
            return 'high_value'

        # Loyal customers (regular engagement)
        if days_since_last_contact <= 30 and opportunity_count > 1:
            return 'loyal'

        # At risk (no recent contact)
        if days_since_last_contact > 90 and opportunity_count > 0:
            return 'at_risk'

        # New customers
        created_recently = (timezone.now().date() - contact.created_at.date()).days <= 30
        if created_recently:
            return 'new'

        # Default to inactive
        return 'inactive'

    @staticmethod
    def _get_segment_recommendations(segment_name):
        """Get recommendations for each segment"""
        recommendations = {
            'high_value': [
                'Provide premium support and services',
                'Offer exclusive deals and early access',
                'Assign dedicated account manager'
            ],
            'loyal': [
                'Continue regular engagement',
                'Request referrals and testimonials',
                'Offer loyalty rewards'
            ],
            'at_risk': [
                'Immediate re-engagement campaign',
                'Understand reasons for disengagement',
                'Offer special retention deals'
            ],
            'new': [
                'Provide onboarding support',
                'Share success stories and case studies',
                'Set up regular check-ins'
            ],
            'inactive': [
                'Re-activation campaign',
                'Survey for feedback',
                'Consider removing from active lists'
            ]
        }

        return recommendations.get(segment_name, [])


class PredictiveAnalytics:
    """Predictive analytics for various CRM metrics"""

    @staticmethod
    def predict_churn_risk():
        """Predict which customers are at risk of churning"""
        contacts = Contact.objects.all()
        risk_scores = []

        for contact in contacts:
            risk_score = PredictiveAnalytics._calculate_churn_risk(contact)
            if risk_score > 0.7:  # High risk threshold
                risk_scores.append({
                    'contact_id': contact.id,
                    'contact_name': contact.full_name,
                    'risk_score': risk_score,
                    'risk_level': 'high'
                })

        return {
            'high_risk_customers': risk_scores,
            'total_at_risk': len(risk_scores),
            'recommendations': [
                'Reach out to high-risk customers immediately',
                'Analyze common patterns in at-risk customers',
                'Implement retention campaigns'
            ]
        }

    @staticmethod
    def _calculate_churn_risk(contact):
        """Calculate churn risk score for a contact"""
        risk_factors = 0
        total_factors = 0

        # Factor 1: Days since last communication
        last_comm = Communication.objects.filter(contact=contact).order_by('-communication_date').first()
        if last_comm:
            days_since = (timezone.now().date() - last_comm.communication_date.date()).days
            if days_since > 90:
                risk_factors += 0.3
            elif days_since > 60:
                risk_factors += 0.2
            elif days_since > 30:
                risk_factors += 0.1
        else:
            risk_factors += 0.4  # No communication is high risk
        total_factors += 1

        # Factor 2: Opportunity activity
        recent_opportunities = Opportunity.objects.filter(
            contact=contact,
            created_at__gte=timezone.now() - timedelta(days=90)
        ).count()

        if recent_opportunities == 0:
            risk_factors += 0.3
        elif recent_opportunities == 1:
            risk_factors += 0.1
        total_factors += 1

        # Factor 3: Task completion rate
        contact_tasks = Task.objects.filter(contact=contact)
        if contact_tasks.exists():
            completed_tasks = contact_tasks.filter(status='completed').count()
            completion_rate = completed_tasks / contact_tasks.count()

            if completion_rate < 0.5:
                risk_factors += 0.2
            elif completion_rate < 0.7:
                risk_factors += 0.1
        else:
            risk_factors += 0.1  # No tasks is slightly risky
        total_factors += 1

        return risk_factors / total_factors if total_factors > 0 else 0.5


class WorkflowAutomation:
    """Intelligent workflow automation"""

    @staticmethod
    def suggest_next_actions(record_type, record_id):
        """
        Suggest next best actions for a record

        Args:
            record_type: 'lead', 'contact', 'opportunity'
            record_id: ID of the record

        Returns:
            list: Suggested actions with priorities
        """
        if record_type == 'lead':
            return WorkflowAutomation._suggest_lead_actions(record_id)
        elif record_type == 'contact':
            return WorkflowAutomation._suggest_contact_actions(record_id)
        elif record_type == 'opportunity':
            return WorkflowAutomation._suggest_opportunity_actions(record_id)

        return []

    @staticmethod
    def _suggest_lead_actions(lead_id):
        """Suggest next actions for a lead"""
        try:
            lead = Lead.objects.get(id=lead_id)
        except Lead.DoesNotExist:
            return []

        suggestions = []

        # Check last communication
        last_comm = Communication.objects.filter(lead=lead).order_by('-communication_date').first()
        if not last_comm:
            suggestions.append({
                'action': 'Initial outreach',
                'description': 'Make first contact with lead',
                'priority': 'high',
                'suggested_method': 'email'
            })
        else:
            days_since = (timezone.now().date() - last_comm.communication_date.date()).days
            if days_since > 7:
                suggestions.append({
                    'action': 'Follow-up communication',
                    'description': f'Follow up after {days_since} days of no contact',
                    'priority': 'medium',
                    'suggested_method': 'phone'
                })

        # Check lead score
        score_data = LeadScoring.calculate_lead_score(lead)
        if score_data['quality'] == 'hot':
            suggestions.append({
                'action': 'Schedule demo',
                'description': 'High-quality lead ready for demo',
                'priority': 'high',
                'suggested_method': 'meeting'
            })

        return suggestions


class PipelineAnalytics:
    """Advanced pipeline analytics and insights"""

    @staticmethod
    def get_pipeline_health():
        """
        Calculate overall pipeline health metrics

        Returns:
            dict: Pipeline health indicators
        """
        opportunities = Opportunity.objects.all()

        # Stage distribution
        stage_distribution = opportunities.values('stage').annotate(
            count=Count('id'),
            total_value=Sum('amount')
        ).order_by('stage')

        # Calculate velocity (average time in each stage)
        velocity_metrics = PipelineAnalytics._calculate_stage_velocity()

        # Identify bottlenecks
        bottlenecks = PipelineAnalytics._identify_bottlenecks(velocity_metrics)

        # Win rate analysis
        win_rate = PipelineAnalytics._calculate_win_rate()

        # Average deal size
        avg_deal_size = opportunities.aggregate(avg=Avg('amount'))['avg'] or 0

        # Pipeline coverage (pipeline value / quota)
        pipeline_value = opportunities.filter(
            stage__in=['qualification', 'proposal', 'negotiation']
        ).aggregate(total=Sum('amount'))['total'] or 0

        return {
            'overall_health_score': PipelineAnalytics._calculate_health_score(
                win_rate, velocity_metrics, bottlenecks
            ),
            'stage_distribution': list(stage_distribution),
            'velocity_metrics': velocity_metrics,
            'bottlenecks': bottlenecks,
            'win_rate': win_rate,
            'average_deal_size': round(avg_deal_size, 2),
            'pipeline_value': round(pipeline_value, 2),
            'recommendations': PipelineAnalytics._generate_health_recommendations(
                win_rate, bottlenecks, velocity_metrics
            )
        }

    @staticmethod
    def get_pipeline_forecast(months=3):
        """
        Forecast pipeline outcomes for next period

        Args:
            months: Number of months to forecast

        Returns:
            dict: Forecast data by stage and time period
        """
        opportunities = Opportunity.objects.all()

        forecast_by_stage = {}

        for stage in ['qualification', 'proposal', 'negotiation', 'closed_won']:
            stage_opps = opportunities.filter(stage=stage)

            expected_close = stage_opps.aggregate(
                total=Sum('amount'),
                weighted=Sum('amount') * Avg('probability') / 100
            )

            forecast_by_stage[stage] = {
                'count': stage_opps.count(),
                'total_value': expected_close['total'] or 0,
                'weighted_value': expected_close['weighted'] or 0,
                'expected_close_rate': PipelineAnalytics._get_stage_close_rate(stage)
            }

        # Time-based forecast
        monthly_forecast = []
        for month in range(1, months + 1):
            target_date = timezone.now() + timedelta(days=30 * month)

            expected_closes = opportunities.filter(
                expected_close_date__year=target_date.year,
                expected_close_date__month=target_date.month
            )

            monthly_forecast.append({
                'month': target_date.strftime('%Y-%m'),
                'expected_deals': expected_closes.count(),
                'expected_revenue': expected_closes.aggregate(
                    total=Sum('amount')
                )['total'] or 0
            })

        return {
            'by_stage': forecast_by_stage,
            'by_month': monthly_forecast,
            'total_pipeline_value': sum(s['total_value'] for s in forecast_by_stage.values()),
            'weighted_pipeline_value': sum(s['weighted_value'] for s in forecast_by_stage.values())
        }

    @staticmethod
    def get_conversion_funnel():
        """
        Analyze conversion rates through the sales funnel

        Returns:
            dict: Conversion metrics for each stage
        """

        # Get all opportunities with stage history
        opportunities = Opportunity.objects.all()
        total_opps = opportunities.count()

        stages = ['prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost']
        funnel_data = []

        for i, stage in enumerate(stages):
            stage_count = opportunities.filter(stage=stage).count()

            conversion_rate = (stage_count / total_opps * 100) if total_opps > 0 else 0

            # Calculate drop-off from previous stage
            if i > 0:
                prev_stage_count = opportunities.filter(stage=stages[i-1]).count()
                drop_off_rate = ((prev_stage_count - stage_count) / prev_stage_count * 100) if prev_stage_count > 0 else 0
            else:
                drop_off_rate = 0

            funnel_data.append({
                'stage': stage,
                'count': stage_count,
                'conversion_rate': round(conversion_rate, 2),
                'drop_off_rate': round(drop_off_rate, 2)
            })

        return {
            'funnel': funnel_data,
            'overall_conversion': round(
                opportunities.filter(stage='closed_won').count() / total_opps * 100, 2
            ) if total_opps > 0 else 0,
            'recommendations': PipelineAnalytics._generate_funnel_recommendations(funnel_data)
        }

    @staticmethod
    def get_deal_velocity():
        """
        Calculate average time to close deals

        Returns:
            dict: Velocity metrics
        """

        closed_deals = Opportunity.objects.filter(
            stage__in=['closed_won', 'closed_lost'],
            closed_at__isnull=False
        )

        # Calculate average time from creation to close
        velocities = []
        for deal in closed_deals:
            days_to_close = (deal.closed_at - deal.created_at).days
            velocities.append({
                'id': str(deal.id),
                'days': days_to_close,
                'amount': float(deal.amount),
                'stage': deal.stage
            })

        if not velocities:
            return {
                'average_days': 0,
                'median_days': 0,
                'fastest': None,
                'slowest': None
            }

        avg_days = np.mean([v['days'] for v in velocities])
        median_days = np.median([v['days'] for v in velocities])

        return {
            'average_days': round(avg_days, 1),
            'median_days': round(median_days, 1),
            'fastest': min(velocities, key=lambda x: x['days']),
            'slowest': max(velocities, key=lambda x: x['days']),
            'by_stage': PipelineAnalytics._velocity_by_stage(closed_deals)
        }

    @staticmethod
    def _calculate_stage_velocity():
        """Calculate average time spent in each stage"""
        # Simplified - in production, track stage transitions
        stages = ['prospecting', 'qualification', 'proposal', 'negotiation']
        velocity = {}

        for stage in stages:
            opps = Opportunity.objects.filter(stage=stage)
            if opps.exists():
                avg_age = np.mean([
                    (timezone.now() - opp.created_at).days
                    for opp in opps
                ])
                velocity[stage] = round(avg_age, 1)
            else:
                velocity[stage] = 0

        return velocity

    @staticmethod
    def _identify_bottlenecks(velocity_metrics):
        """Identify stages with unusually long durations"""
        bottlenecks = []

        if not velocity_metrics:
            return bottlenecks

        avg_velocity = np.mean(list(velocity_metrics.values()))

        for stage, days in velocity_metrics.items():
            if days > avg_velocity * 1.5:  # 50% longer than average
                bottlenecks.append({
                    'stage': stage,
                    'days': days,
                    'severity': 'high' if days > avg_velocity * 2 else 'medium'
                })

        return bottlenecks

    @staticmethod
    def _calculate_win_rate():
        """Calculate overall win rate"""
        closed_opps = Opportunity.objects.filter(
            stage__in=['closed_won', 'closed_lost']
        )

        total = closed_opps.count()
        won = closed_opps.filter(stage='closed_won').count()

        return round((won / total * 100), 2) if total > 0 else 0

    @staticmethod
    def _calculate_health_score(win_rate, velocity_metrics, bottlenecks):
        """Calculate overall pipeline health score (0-100)"""
        score = 100

        # Deduct for low win rate
        if win_rate < 20:
            score -= 30
        elif win_rate < 40:
            score -= 15

        # Deduct for bottlenecks
        score -= len(bottlenecks) * 10

        # Deduct for slow velocity
        if velocity_metrics:
            avg_velocity = np.mean(list(velocity_metrics.values()))
            if avg_velocity > 60:  # More than 60 days average
                score -= 20
            elif avg_velocity > 30:
                score -= 10

        return max(0, min(100, score))

    @staticmethod
    def _generate_health_recommendations(win_rate, bottlenecks, velocity_metrics):
        """Generate recommendations based on pipeline health"""
        recommendations = []

        if win_rate < 30:
            recommendations.append({
                'type': 'win_rate',
                'priority': 'high',
                'message': 'Win rate is below 30%. Focus on lead qualification and deal quality.'
            })

        for bottleneck in bottlenecks:
            recommendations.append({
                'type': 'bottleneck',
                'priority': bottleneck['severity'],
                'message': f"Bottleneck detected in {bottleneck['stage']} stage ({bottleneck['days']} days avg). Review processes."
            })

        if velocity_metrics and np.mean(list(velocity_metrics.values())) > 45:
            recommendations.append({
                'type': 'velocity',
                'priority': 'medium',
                'message': 'Sales cycle is longer than optimal. Consider streamlining approval processes.'
            })

        return recommendations

    @staticmethod
    def _generate_funnel_recommendations(funnel_data):
        """Generate recommendations based on funnel analysis"""
        recommendations = []

        for stage_data in funnel_data:
            if stage_data['drop_off_rate'] > 50:
                recommendations.append({
                    'stage': stage_data['stage'],
                    'priority': 'high',
                    'message': f"High drop-off rate ({stage_data['drop_off_rate']}%) in {stage_data['stage']}. Review qualification criteria."
                })

        return recommendations

    @staticmethod
    def _get_stage_close_rate(stage):
        """Get historical close rate for a stage"""
        stage_mapping = {
            'qualification': 0.20,
            'proposal': 0.40,
            'negotiation': 0.65,
            'closed_won': 1.0
        }
        return stage_mapping.get(stage, 0.10)

    @staticmethod
    def _velocity_by_stage(closed_deals):
        """Calculate velocity metrics by stage"""
        by_stage = {}

        for stage in ['closed_won', 'closed_lost']:
            stage_deals = closed_deals.filter(stage=stage)
            if stage_deals.exists():
                avg_days = np.mean([
                    (deal.closed_at - deal.created_at).days
                    for deal in stage_deals
                ])
                by_stage[stage] = round(avg_days, 1)
            else:
                by_stage[stage] = 0

        return by_stage

    @staticmethod
    def _suggest_contact_actions(contact_id):
        """Suggest next actions for a contact"""
        try:
            contact = Contact.objects.get(id=contact_id)
        except Contact.DoesNotExist:
            return []

        suggestions = []

        # Check for upcoming tasks
        upcoming_tasks = Task.objects.filter(
            contact=contact,
            due_date__gte=timezone.now(),
            status='pending'
        ).count()

        if upcoming_tasks == 0:
            suggestions.append({
                'action': 'Schedule check-in',
                'description': 'No upcoming tasks scheduled',
                'priority': 'medium',
                'suggested_method': 'task'
            })

        return suggestions

    @staticmethod
    def _suggest_opportunity_actions(opportunity_id):
        """Suggest next actions for an opportunity"""
        try:
            opportunity = Opportunity.objects.get(id=opportunity_id)
        except Opportunity.DoesNotExist:
            return []

        suggestions = []

        # Check stage progression
        if opportunity.stage == 'prospecting':
            suggestions.append({
                'action': 'Qualify opportunity',
                'description': 'Move from prospecting to qualification',
                'priority': 'high',
                'suggested_method': 'meeting'
            })
        elif opportunity.stage == 'proposal':
            suggestions.append({
                'action': 'Follow up on proposal',
                'description': 'Check status of submitted proposal',
                'priority': 'high',
                'suggested_method': 'email'
            })

        return suggestions


class PipelineAnalytics:
    """Advanced pipeline analytics and forecasting"""

    @staticmethod
    def get_pipeline_health():
        """Get overall pipeline health metrics"""
        from django.db.models import F, Sum

        from opportunity_management.models import Opportunity

        # Calculate pipeline value by stage
        pipeline_value = Opportunity.objects.values('stage').annotate(
            total_value=Sum('amount'),
            count=Count('id')
        ).order_by('stage')

        # Calculate weighted pipeline value (amount * probability / 100)
        total_weighted_value = Opportunity.objects.aggregate(
            weighted=Sum(F('amount') * F('probability') / 100, output_field=DecimalField())
        )['weighted'] or 0

        # Get conversion rates by stage
        stage_counts = {}
        for item in pipeline_value:
            stage_counts[item['stage']] = {
                'count': item['count'],
                'value': item['total_value'] or 0
            }

        return {
            'total_opportunities': sum(item['count'] for item in pipeline_value),
            'total_value': sum(item['total_value'] or 0 for item in pipeline_value),
            'weighted_value': float(total_weighted_value),
            'stage_breakdown': stage_counts,
            'health_score': PipelineAnalytics._calculate_health_score(stage_counts)
        }

    @staticmethod
    def get_pipeline_forecast(months=3):
        """Get pipeline forecast for next months"""
        from django.db.models import F, Sum

        from opportunity_management.models import Opportunity

        # Forecast based on current pipeline and historical conversion rates
        opportunities = Opportunity.objects.all()

        # Calculate expected close dates
        forecast_data = []
        for month_offset in range(months):
            target_date = timezone.now() + timedelta(days=30 * (month_offset + 1))

            # Opportunities expected to close in this month
            monthly_opportunities = opportunities.filter(
                expected_close_date__month=target_date.month,
                expected_close_date__year=target_date.year
            )

            weighted_value = monthly_opportunities.aggregate(
                weighted=Sum(F('amount') * F('probability') / 100, output_field=DecimalField())
            )['weighted'] or 0

            forecast_data.append({
                'month': target_date.strftime('%Y-%m'),
                'opportunities': monthly_opportunities.count(),
                'forecast_value': float(weighted_value),
                'confidence': 'medium'
            })

        return forecast_data

    @staticmethod
    def get_conversion_funnel():
        """Get conversion funnel analysis"""
        from opportunity_management.models import Opportunity

        # Define funnel stages
        stages = ['prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won']

        funnel_data = []
        previous_count = None

        for stage in stages:
            count = Opportunity.objects.filter(stage=stage).count()

            drop_off_rate = 0
            if previous_count and previous_count > 0:
                drop_off_rate = round(((previous_count - count) / previous_count) * 100, 1)

            funnel_data.append({
                'stage': stage,
                'count': count,
                'drop_off_rate': drop_off_rate
            })

            previous_count = count

        return funnel_data

    @staticmethod
    def get_deal_velocity():
        """Get deal velocity metrics"""
        from opportunity_management.models import Opportunity

        # Calculate average time in each stage
        closed_deals = Opportunity.objects.filter(
            stage='closed_won',
            actual_close_date__isnull=False
        )

        if not closed_deals.exists():
            return {
                'average_velocity_days': 0,
                'stage_velocity': {},
                'recommendations': ['No closed deals to analyze velocity']
            }

        # Calculate overall velocity
        total_days = sum(
            (deal.actual_close_date - deal.created_at).days
            for deal in closed_deals
        )
        average_velocity = total_days / closed_deals.count()

        # Velocity by stage (simplified)
        stage_velocity = PipelineAnalytics._calculate_stage_velocity(closed_deals)

        return {
            'average_velocity_days': round(average_velocity, 1),
            'stage_velocity': stage_velocity,
            'total_closed_deals': closed_deals.count(),
            'recommendations': PipelineAnalytics._generate_velocity_recommendations(average_velocity)
        }

    @staticmethod
    def _calculate_health_score(stage_breakdown):
        """Calculate pipeline health score"""
        # Simple scoring based on stage distribution
        total = sum(data['count'] for data in stage_breakdown.values())
        if total == 0:
            return 0

        # Ideal distribution weights
        ideal_weights = {
            'prospecting': 0.4,
            'qualification': 0.3,
            'proposal': 0.2,
            'negotiation': 0.08,
            'closed_won': 0.02
        }

        score = 0
        for stage, data in stage_breakdown.items():
            actual_weight = data['count'] / total
            ideal_weight = ideal_weights.get(stage, 0)
            score += min(actual_weight / ideal_weight, 1) if ideal_weight > 0 else 0

        return round((score / len(ideal_weights)) * 100, 1)

    @staticmethod
    def _calculate_stage_velocity(closed_deals):
        """Calculate velocity by stage"""
        # Simplified - in production, track stage transitions
        return {
            'prospecting': 7,  # days
            'qualification': 14,
            'proposal': 21,
            'negotiation': 30
        }

    @staticmethod
    def _generate_velocity_recommendations(avg_velocity):
        """Generate recommendations based on velocity"""
        if avg_velocity < 30:
            return ['Excellent velocity - maintain current processes']
        elif avg_velocity < 60:
            return ['Good velocity - look for minor optimizations']
        elif avg_velocity < 90:
            return ['Average velocity - review bottlenecks in qualification and proposal stages']
        else:
            return ['Slow velocity - focus on streamlining the sales process and removing obstacles']
