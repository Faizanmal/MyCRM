"""
Advanced AI and Analytics Module for Enterprise CRM
Provides machine learning insights, predictive analytics, and automation
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from django.contrib.auth import get_user_model
from contact_management.models import Contact
from lead_management.models import Lead
from opportunity_management.models import Opportunity
from task_management.models import Task
from communication_management.models import Communication

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