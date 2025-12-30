"""
Enhanced AI Recommendation Engine
Advanced recommendation logic with ML-like scoring and pattern detection
"""

from django.utils import timezone
from django.db.models import Count, Avg, Q, F, Sum, Max, Min
from django.db.models.functions import TruncDate, TruncWeek
from datetime import timedelta, datetime
from collections import defaultdict
import logging
import re

from .interactive_models import AIRecommendation

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Advanced recommendation engine that analyzes CRM data patterns
    and generates intelligent, actionable recommendations
    """
    
    def __init__(self, user):
        self.user = user
        self.recommendations = []
        self.max_recommendations = 10
        
    def generate_all(self):
        """Generate all types of recommendations"""
        # Clear expired recommendations first
        self._clear_expired()
        
        # Generate various recommendation types
        self._generate_follow_up_recommendations()
        self._generate_deal_velocity_recommendations()
        self._generate_churn_risk_recommendations()
        self._generate_upsell_opportunities()
        self._generate_best_time_recommendations()
        self._generate_pipeline_health_recommendations()
        self._generate_productivity_recommendations()
        self._generate_engagement_recommendations()
        self._generate_competitor_insights()
        self._generate_seasonal_recommendations()
        
        # Advanced recommendation types
        self._generate_win_probability_alerts()
        self._generate_relationship_mapping()
        self._generate_email_response_insights()
        self._generate_meeting_preparation()
        self._generate_deal_risk_scoring()
        
        return self.recommendations[:self.max_recommendations]
    
    def _clear_expired(self):
        """Clear expired recommendations"""
        AIRecommendation.objects.filter(
            user=self.user,
            expires_at__lt=timezone.now()
        ).update(status='expired')
    
    def _create_recommendation(self, **kwargs):
        """Create a new recommendation if it doesn't already exist"""
        # Check for similar existing recommendation
        title = kwargs.get('title', '')
        existing = AIRecommendation.objects.filter(
            user=self.user,
            status='active',
            title__icontains=title[:50]  # Match first 50 chars
        ).exists()
        
        if not existing:
            rec = AIRecommendation.objects.create(
                user=self.user,
                **kwargs
            )
            self.recommendations.append(rec)
            return rec
        return None
    
    def _generate_follow_up_recommendations(self):
        """Generate recommendations for leads/contacts needing follow-up"""
        try:
            from lead_management.models import Lead
            from activity_feed.models import Activity
            
            # Find leads with high scores but no recent activity
            high_value_stale = Lead.objects.filter(
                Q(owner=self.user) | Q(assigned_to=self.user),
                status__in=['new', 'contacted', 'qualified'],
            ).annotate(
                last_activity=Max('activities__created_at')
            ).filter(
                Q(last_activity__lt=timezone.now() - timedelta(days=5)) |
                Q(last_activity__isnull=True)
            ).order_by('-score', 'last_activity')[:5]
            
            for lead in high_value_stale:
                days_stale = 0
                if lead.last_activity:
                    days_stale = (timezone.now() - lead.last_activity).days
                else:
                    days_stale = (timezone.now() - lead.created_at).days
                
                urgency = 'high' if days_stale > 7 else 'medium'
                
                self._create_recommendation(
                    recommendation_type='action',
                    title=f'Follow up with {lead.first_name} {lead.last_name}',
                    description=f"This lead has a score of {getattr(lead, 'score', 'N/A')} "
                               f"but hasn't been contacted in {days_stale} days. "
                               f"High-potential leads need regular engagement to convert.",
                    impact=urgency,
                    action_label='Contact Now',
                    action_url=f'/leads/{lead.id}',
                    dismissable=False,
                    confidence_score=0.9,
                    reasoning=f"High-scoring lead stale for {days_stale} days",
                    expires_at=timezone.now() + timedelta(days=3)
                )
                
        except (ImportError, Exception) as e:
            logger.debug(f"Follow-up recommendations skipped: {e}")
    
    def _generate_deal_velocity_recommendations(self):
        """Analyze deal velocity and identify slow-moving opportunities"""
        try:
            from opportunity_management.models import Opportunity
            
            # Calculate average time per stage
            stage_avg_times = {}
            
            # Find deals that are significantly slower than average
            slow_deals = Opportunity.objects.filter(
                Q(owner=self.user) | Q(assigned_to=self.user),
                status='open'
            ).annotate(
                days_in_stage=F('updated_at') - F('stage_changed_at') if hasattr(Opportunity, 'stage_changed_at') else F('updated_at') - F('created_at')
            ).order_by('-value')[:10]
            
            for deal in slow_deals:
                days_in_stage = (timezone.now() - deal.updated_at).days
                
                if days_in_stage > 14:  # More than 2 weeks in same stage
                    self._create_recommendation(
                        recommendation_type='warning',
                        title=f'Deal stalled: {deal.name}',
                        description=f"This ${deal.amount:,.0f} deal has been in the {deal.stage} "
                                   f"stage for {days_in_stage} days. Consider re-engaging the "
                                   f"prospect or identifying blockers.",
                        impact='high' if deal.amount > 25000 else 'medium',
                        action_label='Review Deal',
                        action_url=f'/opportunities/{deal.id}',
                        dismissable=False,
                        confidence_score=0.85,
                        reasoning=f"Deal stuck in {deal.stage} for {days_in_stage} days vs 7-day average",
                        expires_at=timezone.now() + timedelta(days=5)
                    )
                    
        except (ImportError, Exception) as e:
            logger.debug(f"Deal velocity recommendations skipped: {e}")
    
    def _generate_churn_risk_recommendations(self):
        """Identify customers at risk of churning"""
        try:
            from contact_management.models import Contact, Organization
            from activity_feed.models import Activity
            
            # Find organizations with declining engagement
            orgs_with_activity = Organization.objects.annotate(
                total_contacts=Count('contacts'),
                recent_activities=Count(
                    'activities',
                    filter=Q(activities__created_at__gte=timezone.now() - timedelta(days=30))
                ),
                older_activities=Count(
                    'activities',
                    filter=Q(
                        activities__created_at__lt=timezone.now() - timedelta(days=30),
                        activities__created_at__gte=timezone.now() - timedelta(days=60)
                    )
                )
            ).filter(
                total_contacts__gte=3,
                older_activities__gt=F('recent_activities') * 2  # 50%+ decline
            )[:3]
            
            for org in orgs_with_activity:
                decline_pct = 100 - (org.recent_activities / max(org.older_activities, 1) * 100)
                
                self._create_recommendation(
                    recommendation_type='warning',
                    title=f'Churn risk detected: {org.name}',
                    description=f"Engagement with {org.name} has dropped by {decline_pct:.0f}% "
                               f"in the last 30 days. This may indicate dissatisfaction or "
                               f"intent to switch providers.",
                    impact='high',
                    action_label='Investigate',
                    action_url=f'/organizations/{org.id}',
                    dismissable=False,
                    confidence_score=0.8,
                    reasoning=f"Engagement decline: {org.recent_activities} recent vs {org.older_activities} previous month",
                    expires_at=timezone.now() + timedelta(days=7)
                )
                
        except (ImportError, Exception) as e:
            logger.debug(f"Churn risk recommendations skipped: {e}")
    
    def _generate_upsell_opportunities(self):
        """Identify upsell and cross-sell opportunities"""
        try:
            from contact_management.models import Organization
            from opportunity_management.models import Opportunity
            
            # Find growing organizations with successful past deals
            growing_orgs = Organization.objects.annotate(
                contact_count=Count('contacts'),
                won_deals=Count('opportunities', filter=Q(opportunities__status='won')),
                total_revenue=Sum('opportunities__amount', filter=Q(opportunities__status='won'))
            ).filter(
                won_deals__gte=1,
                contact_count__gte=5
            ).order_by('-total_revenue')[:3]
            
            for org in growing_orgs:
                # Check when the last deal was closed
                last_deal = Opportunity.objects.filter(
                    organization=org,
                    status='won'
                ).order_by('-closed_at').first()
                
                if last_deal:
                    months_since_last_deal = (timezone.now() - last_deal.closed_at).days / 30
                    
                    if months_since_last_deal > 6:
                        self._create_recommendation(
                            recommendation_type='opportunity',
                            title=f'Upsell opportunity: {org.name}',
                            description=f"{org.name} closed their last deal {months_since_last_deal:.0f} months ago. "
                                       f"With {org.contact_count} contacts and ${org.total_revenue:,.0f} lifetime value, "
                                       f"they may be ready for an upgrade or additional services.",
                            impact='high',
                            action_label='Explore Upsell',
                            action_url=f'/organizations/{org.id}',
                            dismissable=True,
                            confidence_score=0.75,
                            reasoning=f"Growing org with {months_since_last_deal:.1f} months since last purchase",
                            expires_at=timezone.now() + timedelta(days=14)
                        )
                        
        except (ImportError, Exception) as e:
            logger.debug(f"Upsell recommendations skipped: {e}")
    
    def _generate_best_time_recommendations(self):
        """Analyze communication patterns to suggest optimal contact times"""
        try:
            from activity_feed.models import Activity
            from contact_management.models import Contact
            
            # Analyze successful interactions by time of day
            successful_activities = Activity.objects.filter(
                actor=self.user,
                action__in=['called', 'emailed', 'met'],
                created_at__gte=timezone.now() - timedelta(days=90)
            ).annotate(
                hour=F('created_at__hour'),
                weekday=F('created_at__week_day')
            )
            
            # Find patterns (simplified)
            hour_counts = defaultdict(int)
            for activity in successful_activities:
                hour_counts[activity.created_at.hour] += 1
            
            if hour_counts:
                best_hour = max(hour_counts, key=hour_counts.get)
                best_hour_formatted = f"{best_hour}:00" if best_hour < 12 else f"{best_hour-12}:00 PM"
                
                self._create_recommendation(
                    recommendation_type='insight',
                    title='Best outreach time identified',
                    description=f"Your outreach is most effective at {best_hour_formatted}. "
                               f"Based on your past 90 days of activity, this time slot "
                               f"shows the highest engagement rates.",
                    impact='medium',
                    action_label='Schedule Calls',
                    action_url='/calendar',
                    dismissable=True,
                    confidence_score=0.7,
                    reasoning=f"Analysis of {sum(hour_counts.values())} activities showed {hour_counts[best_hour]} at peak hour",
                    expires_at=timezone.now() + timedelta(days=30)
                )
                
        except (ImportError, Exception) as e:
            logger.debug(f"Best time recommendations skipped: {e}")
    
    def _generate_pipeline_health_recommendations(self):
        """Analyze overall pipeline health and suggest improvements"""
        try:
            from opportunity_management.models import Opportunity
            
            # Get pipeline snapshot
            open_deals = Opportunity.objects.filter(
                Q(owner=self.user) | Q(assigned_to=self.user),
                status='open'
            )
            
            total_pipeline = open_deals.aggregate(
                total_value=Sum('amount'),
                deal_count=Count('id'),
                avg_age=Avg('created_at')
            )
            
            pipeline_value = total_pipeline['total_value'] or 0
            deal_count = total_pipeline['deal_count'] or 0
            
            # Check for pipeline imbalances
            stage_distribution = open_deals.values('stage').annotate(
                count=Count('id'),
                value=Sum('amount')
            )
            
            # Find if pipeline is top-heavy (many early-stage deals)
            stage_data = {s['stage']: s for s in stage_distribution}
            
            early_stages = sum(
                stage_data.get(s, {}).get('count', 0) 
                for s in ['qualification', 'prospecting', 'new']
            )
            late_stages = sum(
                stage_data.get(s, {}).get('count', 0) 
                for s in ['proposal', 'negotiation', 'closing']
            )
            
            if deal_count > 5 and early_stages > late_stages * 2:
                self._create_recommendation(
                    recommendation_type='insight',
                    title='Pipeline imbalance detected',
                    description=f"Your pipeline has {early_stages} early-stage deals but only "
                               f"{late_stages} in late stages. Focus on advancing deals through "
                               f"qualification to improve conversion rates.",
                    impact='medium',
                    action_label='View Pipeline',
                    action_url='/pipeline',
                    dismissable=True,
                    confidence_score=0.75,
                    reasoning=f"Early:late stage ratio is {early_stages}:{late_stages}",
                    expires_at=timezone.now() + timedelta(days=7)
                )
                
        except (ImportError, Exception) as e:
            logger.debug(f"Pipeline health recommendations skipped: {e}")
    
    def _generate_productivity_recommendations(self):
        """Analyze user productivity patterns"""
        try:
            from activity_feed.models import Activity
            from task_management.models import Task
            
            # Check for overdue tasks
            overdue_tasks = Task.objects.filter(
                assigned_to=self.user,
                status__in=['pending', 'in_progress'],
                due_date__lt=timezone.now()
            ).count()
            
            if overdue_tasks >= 5:
                self._create_recommendation(
                    recommendation_type='warning',
                    title=f'{overdue_tasks} tasks are overdue',
                    description=f"You have {overdue_tasks} overdue tasks. Completing these "
                               f"will help maintain momentum with your prospects and keep "
                               f"your pipeline moving.",
                    impact='high' if overdue_tasks > 10 else 'medium',
                    action_label='View Tasks',
                    action_url='/tasks?filter=overdue',
                    dismissable=False,
                    confidence_score=0.95,
                    reasoning=f"{overdue_tasks} overdue tasks detected",
                    expires_at=timezone.now() + timedelta(days=1)
                )
            
            # Analyze task completion rate
            last_week = timezone.now() - timedelta(days=7)
            completed_tasks = Task.objects.filter(
                assigned_to=self.user,
                status='completed',
                completed_at__gte=last_week
            ).count()
            
            if completed_tasks > 20:
                self._create_recommendation(
                    recommendation_type='tip',
                    title='Great productivity this week! 🎉',
                    description=f"You completed {completed_tasks} tasks this week. Keep up "
                               f"the momentum! Consider celebrating small wins with your team.",
                    impact='low',
                    action_label='View Stats',
                    action_url='/gamification',
                    dismissable=True,
                    confidence_score=0.9,
                    reasoning=f"{completed_tasks} tasks completed in 7 days",
                    expires_at=timezone.now() + timedelta(days=3)
                )
                
        except (ImportError, Exception) as e:
            logger.debug(f"Productivity recommendations skipped: {e}")
    
    def _generate_engagement_recommendations(self):
        """Suggest ways to improve engagement"""
        try:
            from activity_feed.models import Activity
            
            # Check activity in last 7 days
            last_week = timezone.now() - timedelta(days=7)
            activities = Activity.objects.filter(
                actor=self.user,
                created_at__gte=last_week
            ).count()
            
            if activities < 10:
                self._create_recommendation(
                    recommendation_type='tip',
                    title='Boost your CRM activity',
                    description=f"You've logged only {activities} activities this week. "
                               f"Consistent logging helps track pipeline progress and "
                               f"ensures no opportunities slip through the cracks.",
                    impact='medium',
                    action_label='Log Activity',
                    action_url='/dashboard',
                    dismissable=True,
                    confidence_score=0.7,
                    reasoning=f"Low activity: {activities} in 7 days",
                    expires_at=timezone.now() + timedelta(days=7)
                )
                
        except (ImportError, Exception) as e:
            logger.debug(f"Engagement recommendations skipped: {e}")
    
    def _generate_competitor_insights(self):
        """Surface competitive intelligence from notes and communications"""
        try:
            from opportunity_management.models import Opportunity
            
            # Look for competitor mentions in deal descriptions
            competitor_keywords = ['competitor', 'alternative', 'comparing', 'versus', 'vs']
            
            deals_with_competition = Opportunity.objects.filter(
                Q(owner=self.user) | Q(assigned_to=self.user),
                status='open'
            ).filter(
                Q(description__icontains='competitor') |
                Q(notes__icontains='alternative') |
                Q(notes__icontains='comparing')
            )[:3]
            
            for deal in deals_with_competition:
                self._create_recommendation(
                    recommendation_type='insight',
                    title=f'Competitive situation: {deal.name}',
                    description=f"This deal mentions competitors or alternatives. Consider "
                               f"preparing competitive battle cards and emphasizing your "
                               f"unique value proposition.",
                    impact='medium',
                    action_label='View Deal',
                    action_url=f'/opportunities/{deal.id}',
                    dismissable=True,
                    confidence_score=0.65,
                    reasoning="Competitor keywords detected in deal notes",
                    expires_at=timezone.now() + timedelta(days=7)
                )
                
        except (ImportError, Exception) as e:
            logger.debug(f"Competitor insights skipped: {e}")
    
    def _generate_seasonal_recommendations(self):
        """Generate recommendations based on time of year/quarter patterns"""
        now = timezone.now()
        
        # End of quarter push
        month = now.month
        day = now.day
        
        if month in [3, 6, 9, 12] and day > 20:
            days_left = 31 - day if month in [3, 12] else 30 - day
            
            self._create_recommendation(
                recommendation_type='tip',
                title=f'Quarter ending soon! ({days_left} days left)',
                description=f"The quarter ends in {days_left} days. Review your pipeline "
                           f"for any deals that can be accelerated to close this quarter.",
                impact='high',
                action_label='Review Pipeline',
                action_url='/pipeline',
                dismissable=True,
                confidence_score=0.8,
                reasoning=f"Q{(month-1)//3 + 1} ends in {days_left} days",
                expires_at=timezone.now() + timedelta(days=days_left)
            )
    
    def _generate_win_probability_alerts(self):
        """Alert on deals with high or declining win probability"""
        try:
            from opportunity_management.models import Opportunity
            
            # Find high probability deals that need attention
            hot_deals = Opportunity.objects.filter(
                Q(owner=self.user) | Q(assigned_to=self.user),
                status='open',
            ).order_by('-probability', '-amount')[:5]
            
            for deal in hot_deals:
                probability = getattr(deal, 'probability', getattr(deal, 'win_probability', 0)) or 0
                
                if probability >= 80:
                    days_since_update = (timezone.now() - deal.updated_at).days
                    
                    if days_since_update > 5:
                        self._create_recommendation(
                            recommendation_type='opportunity',
                            title=f'Hot deal needs attention: {deal.name}',
                            description=f"This deal has an {probability}% win probability but hasn't been "
                                       f"updated in {days_since_update} days. Close this deal before it cools off!",
                            impact='high',
                            action_label='Close Deal',
                            action_url=f'/opportunities/{deal.id}',
                            dismissable=False,
                            confidence_score=probability / 100,
                            reasoning=f"{probability}% probability, {days_since_update} days stale",
                            expires_at=timezone.now() + timedelta(days=3)
                        )
                        
        except (ImportError, Exception) as e:
            logger.debug(f"Win probability recommendations skipped: {e}")
    
    def _generate_relationship_mapping(self):
        """Suggest building relationships with key stakeholders"""
        try:
            from opportunity_management.models import Opportunity
            from contact_management.models import Contact
            
            # Find high-value deals with few contacts
            big_deals = Opportunity.objects.filter(
                Q(owner=self.user) | Q(assigned_to=self.user),
                status='open',
                amount__gte=50000
            ).annotate(
                contact_count=Count('contacts')
            ).filter(
                contact_count__lt=3
            )[:3]
            
            for deal in big_deals:
                self._create_recommendation(
                    recommendation_type='insight',
                    title=f'Expand relationships: {deal.name}',
                    description=f"This ${deal.amount:,.0f} deal only has {deal.contact_count} contact(s). "
                               f"Large enterprise deals typically need 5-7 stakeholder relationships. "
                               f"Consider identifying additional decision makers.",
                    impact='high',
                    action_label='Add Contacts',
                    action_url=f'/opportunities/{deal.id}',
                    dismissable=True,
                    confidence_score=0.75,
                    reasoning=f"Only {deal.contact_count} contacts for ${deal.amount:,.0f} deal",
                    expires_at=timezone.now() + timedelta(days=14)
                )
                
        except (ImportError, Exception) as e:
            logger.debug(f"Relationship mapping recommendations skipped: {e}")
    
    def _generate_email_response_insights(self):
        """Analyze email response patterns and suggest improvements"""
        try:
            from email_tracking.models import EmailTracking
            
            # Analyze recent email performance
            last_month = timezone.now() - timedelta(days=30)
            
            email_stats = EmailTracking.objects.filter(
                user=self.user,
                sent_at__gte=last_month
            ).aggregate(
                total_sent=Count('id'),
                total_opened=Count('id', filter=Q(opened_at__isnull=False)),
                total_clicked=Count('id', filter=Q(clicked_at__isnull=False)),
                total_replied=Count('id', filter=Q(replied_at__isnull=False))
            )
            
            total = email_stats['total_sent'] or 1
            open_rate = (email_stats['total_opened'] or 0) / total * 100
            reply_rate = (email_stats['total_replied'] or 0) / total * 100
            
            if open_rate < 30 and total > 10:
                self._create_recommendation(
                    recommendation_type='insight',
                    title='Improve email open rates',
                    description=f"Your email open rate is {open_rate:.1f}% (industry average: 40-50%). "
                               f"Consider A/B testing subject lines and optimizing send times. "
                               f"Your best open times are typically mid-week mornings.",
                    impact='medium',
                    action_label='View Analytics',
                    action_url='/analytics/email',
                    dismissable=True,
                    confidence_score=0.8,
                    reasoning=f"Open rate {open_rate:.1f}% on {total} emails",
                    expires_at=timezone.now() + timedelta(days=14)
                )
            
            if reply_rate < 10 and total > 20:
                self._create_recommendation(
                    recommendation_type='tip',
                    title='Boost email reply rates',
                    description=f"Your email reply rate is {reply_rate:.1f}%. Try personalizing your "
                               f"emails, asking specific questions, and including clear calls-to-action. "
                               f"Shorter emails often get better responses.",
                    impact='medium',
                    action_label='Email Templates',
                    action_url='/settings/templates',
                    dismissable=True,
                    confidence_score=0.7,
                    reasoning=f"Reply rate {reply_rate:.1f}% on {total} emails",
                    expires_at=timezone.now() + timedelta(days=14)
                )
                
        except (ImportError, Exception) as e:
            logger.debug(f"Email insights skipped: {e}")
    
    def _generate_meeting_preparation(self):
        """Prepare for upcoming meetings with deal context"""
        try:
            from task_management.models import Task
            from opportunity_management.models import Opportunity
            
            # Find meetings in the next 24 hours
            tomorrow = timezone.now() + timedelta(days=1)
            
            upcoming_meetings = Task.objects.filter(
                assigned_to=self.user,
                task_type__in=['meeting', 'call', 'demo'],
                due_date__gte=timezone.now(),
                due_date__lte=tomorrow,
                status__in=['pending', 'scheduled']
            ).select_related('opportunity')[:5]
            
            for meeting in upcoming_meetings:
                deal = getattr(meeting, 'opportunity', None)
                time_until = meeting.due_date - timezone.now()
                hours_until = time_until.total_seconds() / 3600
                
                if hours_until <= 24:
                    deal_context = ""
                    if deal:
                        deal_context = f" This is for the ${deal.amount:,.0f} {deal.name} opportunity."
                    
                    self._create_recommendation(
                        recommendation_type='action',
                        title=f'Prepare for: {meeting.title}',
                        description=f"You have a {meeting.task_type} in {hours_until:.0f} hours.{deal_context} "
                                   f"Review recent activities, prepare talking points, and set objectives.",
                        impact='high' if deal and deal.amount > 25000 else 'medium',
                        action_label='View Details',
                        action_url=f'/tasks/{meeting.id}',
                        dismissable=True,
                        confidence_score=0.95,
                        reasoning=f"Meeting in {hours_until:.1f} hours",
                        expires_at=meeting.due_date
                    )
                    
        except (ImportError, Exception) as e:
            logger.debug(f"Meeting preparation recommendations skipped: {e}")
    
    def _generate_deal_risk_scoring(self):
        """Score deals for risk factors and alert on concerning patterns"""
        try:
            from opportunity_management.models import Opportunity
            from activity_feed.models import Activity
            
            # Analyze open deals for risk factors
            open_deals = Opportunity.objects.filter(
                Q(owner=self.user) | Q(assigned_to=self.user),
                status='open',
                amount__gte=10000
            ).annotate(
                activity_count=Count('activities'),
                last_activity_date=Max('activities__created_at')
            )
            
            for deal in open_deals:
                risk_factors = []
                risk_score = 0
                
                # Check days since last activity
                if deal.last_activity_date:
                    days_inactive = (timezone.now() - deal.last_activity_date).days
                    if days_inactive > 14:
                        risk_factors.append(f"No activity in {days_inactive} days")
                        risk_score += 30
                elif deal.activity_count == 0:
                    risk_factors.append("No activities logged")
                    risk_score += 25
                
                # Check deal age vs stage
                deal_age = (timezone.now() - deal.created_at).days
                if deal_age > 90 and deal.stage in ['qualification', 'prospecting']:
                    risk_factors.append(f"In {deal.stage} for {deal_age} days")
                    risk_score += 25
                
                # Check close date
                if hasattr(deal, 'expected_close') and deal.expected_close:
                    if deal.expected_close < timezone.now().date():
                        days_past = (timezone.now().date() - deal.expected_close).days
                        risk_factors.append(f"Expected close date passed {days_past} days ago")
                        risk_score += 30
                
                # Alert if high risk
                if risk_score >= 50 and len(risk_factors) >= 2:
                    self._create_recommendation(
                        recommendation_type='warning',
                        title=f'At-risk deal: {deal.name}',
                        description=f"This ${deal.amount:,.0f} deal has multiple risk factors: "
                                   f"{'; '.join(risk_factors)}. Consider re-engaging the prospect "
                                   f"or updating the deal status.",
                        impact='high',
                        action_label='Review Deal',
                        action_url=f'/opportunities/{deal.id}',
                        dismissable=False,
                        confidence_score=min(risk_score / 100, 0.95),
                        reasoning=f"Risk score: {risk_score}/100",
                        expires_at=timezone.now() + timedelta(days=7)
                    )
                    
        except (ImportError, Exception) as e:
            logger.debug(f"Deal risk scoring skipped: {e}")


def generate_recommendations(user, max_recommendations=5):
    """
    Main entry point for generating recommendations
    
    Args:
        user: The user to generate recommendations for
        max_recommendations: Maximum number of recommendations to return
    
    Returns:
        List of AIRecommendation objects
    """
    engine = RecommendationEngine(user)
    engine.max_recommendations = max_recommendations
    return engine.generate_all()


def get_recommendation_stats(user):
    """Get statistics about recommendations for a user"""
    active_recs = AIRecommendation.objects.filter(user=user, status='active')
    
    return {
        'total_active': active_recs.count(),
        'high_impact': active_recs.filter(impact='high').count(),
        'by_type': dict(
            active_recs.values('recommendation_type')
            .annotate(count=Count('id'))
            .values_list('recommendation_type', 'count')
        ),
        'avg_confidence': active_recs.aggregate(Avg('confidence_score'))['confidence_score__avg'] or 0,
        'oldest': active_recs.order_by('created_at').first(),
        'dismissed_today': AIRecommendation.objects.filter(
            user=user,
            status='dismissed',
            dismissed_at__date=timezone.now().date()
        ).count(),
        'completed_today': AIRecommendation.objects.filter(
            user=user,
            status='completed',
            completed_at__date=timezone.now().date()
        ).count(),
    }
