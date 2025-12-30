"""
Advanced Analytics API
Sales forecasting, conversion funnels, cohort analysis, and custom metrics
"""
from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
import numpy as np

from lead_management.models import Lead
from contact_management.models import Contact
from opportunity_management.models import Opportunity
from task_management.models import Task
from activity_feed.models import Activity
from django.contrib.auth import get_user_model

User = get_user_model()


class SalesForecastView(views.APIView):
    """
    Sales forecasting based on pipeline and historical data
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get sales forecast for next periods"""
        periods_ahead = int(request.query_params.get('periods', 3))
        
        # Get current pipeline weighted value
        pipeline = Opportunity.objects.exclude(stage__in=['closed_won', 'closed_lost'])
        
        weighted_pipeline = sum([
            float(opp.amount * opp.probability / 100)
            for opp in pipeline
        ])
        
        # Calculate historical win rate
        total_closed = Opportunity.objects.filter(
            stage__in=['closed_won', 'closed_lost']
        ).count()
        
        won = Opportunity.objects.filter(stage='closed_won').count()
        win_rate = (won / total_closed * 100) if total_closed > 0 else 0
        
        # Calculate average deal size
        avg_deal_size = Opportunity.objects.filter(
            stage='closed_won'
        ).aggregate(avg_amount=Avg('amount'))['avg_amount'] or 0
        
        # Calculate average sales cycle
        closed_won_opps = Opportunity.objects.filter(
            stage='closed_won',
            actual_close_date__isnull=False
        )
        
        sales_cycles = []
        for opp in closed_won_opps:
            if opp.created_at and opp.actual_close_date:
                cycle_days = (opp.actual_close_date - opp.created_at.date()).days
                sales_cycles.append(cycle_days)
        
        avg_sales_cycle = np.mean(sales_cycles) if sales_cycles else 30
        
        # Historical monthly revenue
        last_6_months = timezone.now() - timedelta(days=180)
        monthly_revenue = Opportunity.objects.filter(
            stage='closed_won',
            actual_close_date__gte=last_6_months
        ).annotate(
            month=TruncMonth('actual_close_date')
        ).values('month').annotate(
            revenue=Sum('amount'),
            count=Count('id')
        ).order_by('month')
        
        # Calculate growth rate
        revenues = [float(m['revenue']) for m in monthly_revenue]
        if len(revenues) >= 2:
            growth_rate = (revenues[-1] - revenues[0]) / revenues[0] * 100 if revenues[0] > 0 else 0
        else:
            growth_rate = 0
        
        # Generate forecast
        forecasts = []
        base_revenue = revenues[-1] if revenues else avg_deal_size * (won / 6 if won > 0 else 1)
        
        for i in range(1, periods_ahead + 1):
            # Simple linear forecast with growth rate
            forecasted_revenue = base_revenue * (1 + (growth_rate / 100)) ** i
            
            # Confidence based on data quality
            confidence = max(50, min(95, 70 + (len(revenues) * 2)))
            
            forecasts.append({
                'period': i,
                'forecasted_revenue': round(forecasted_revenue, 2),
                'low_estimate': round(forecasted_revenue * 0.8, 2),
                'high_estimate': round(forecasted_revenue * 1.2, 2),
                'confidence': confidence
            })
        
        return Response({
            'current_pipeline': {
                'total_opportunities': pipeline.count(),
                'total_value': sum([float(o.amount) for o in pipeline]),
                'weighted_value': round(weighted_pipeline, 2)
            },
            'historical_metrics': {
                'win_rate': round(win_rate, 2),
                'average_deal_size': round(float(avg_deal_size), 2),
                'average_sales_cycle_days': round(avg_sales_cycle, 0),
                'growth_rate': round(growth_rate, 2)
            },
            'monthly_revenue': [
                {
                    'month': m['month'].strftime('%Y-%m'),
                    'revenue': float(m['revenue']),
                    'deals': m['count']
                }
                for m in monthly_revenue
            ],
            'forecast': forecasts
        })


class ConversionFunnelView(views.APIView):
    """
    Conversion funnel analysis from lead to customer
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get conversion funnel metrics"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Base queryset
        leads_qs = Lead.objects.all()
        opps_qs = Opportunity.objects.all()
        
        if start_date:
            leads_qs = leads_qs.filter(created_at__gte=start_date)
            opps_qs = opps_qs.filter(created_at__gte=start_date)
        
        if end_date:
            leads_qs = leads_qs.filter(created_at__lte=end_date)
            opps_qs = opps_qs.filter(created_at__lte=end_date)
        
        # Funnel stages
        total_leads = leads_qs.count()
        contacted_leads = leads_qs.filter(status__in=['contacted', 'qualified', 'converted']).count()
        qualified_leads = leads_qs.filter(status__in=['qualified', 'converted']).count()
        converted_leads = leads_qs.filter(status='converted').count()
        
        # Opportunity funnel
        total_opportunities = opps_qs.count()
        proposal_stage = opps_qs.filter(stage__in=['proposal', 'negotiation', 'closed_won']).count()
        negotiation_stage = opps_qs.filter(stage__in=['negotiation', 'closed_won']).count()
        closed_won = opps_qs.filter(stage='closed_won').count()
        
        # Calculate conversion rates
        def calc_rate(numerator, denominator):
            return round((numerator / denominator * 100) if denominator > 0 else 0, 2)
        
        funnel = [
            {
                'stage': 'Total Leads',
                'count': total_leads,
                'conversion_rate': 100.0,
                'drop_off': 0
            },
            {
                'stage': 'Contacted',
                'count': contacted_leads,
                'conversion_rate': calc_rate(contacted_leads, total_leads),
                'drop_off': total_leads - contacted_leads
            },
            {
                'stage': 'Qualified',
                'count': qualified_leads,
                'conversion_rate': calc_rate(qualified_leads, total_leads),
                'drop_off': contacted_leads - qualified_leads
            },
            {
                'stage': 'Converted to Opportunity',
                'count': converted_leads,
                'conversion_rate': calc_rate(converted_leads, total_leads),
                'drop_off': qualified_leads - converted_leads
            },
            {
                'stage': 'Proposal Stage',
                'count': proposal_stage,
                'conversion_rate': calc_rate(proposal_stage, total_opportunities),
                'drop_off': total_opportunities - proposal_stage
            },
            {
                'stage': 'Negotiation',
                'count': negotiation_stage,
                'conversion_rate': calc_rate(negotiation_stage, total_opportunities),
                'drop_off': proposal_stage - negotiation_stage
            },
            {
                'stage': 'Closed Won',
                'count': closed_won,
                'conversion_rate': calc_rate(closed_won, total_opportunities),
                'drop_off': negotiation_stage - closed_won
            }
        ]
        
        # Overall conversion rate
        overall_conversion = calc_rate(closed_won, total_leads)
        
        return Response({
            'funnel': funnel,
            'overall_conversion_rate': overall_conversion,
            'total_leads': total_leads,
            'total_opportunities': total_opportunities,
            'total_closed_won': closed_won,
            'period': {
                'start': start_date,
                'end': end_date
            }
        })


class CohortAnalysisView(views.APIView):
    """
    Cohort analysis for customer retention and behavior
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get cohort analysis data"""
        cohort_type = request.query_params.get('type', 'monthly')  # monthly, quarterly
        metric = request.query_params.get('metric', 'retention')  # retention, revenue
        
        # Get customers (contacts with type='customer')
        customers = Contact.objects.filter(contact_type='customer').order_by('created_at')
        
        cohorts = defaultdict(lambda: {'total': 0, 'periods': defaultdict(int)})
        
        for customer in customers:
            # Determine cohort (month of first purchase/creation)
            if cohort_type == 'monthly':
                cohort_key = customer.created_at.strftime('%Y-%m')
            else:
                quarter = (customer.created_at.month - 1) // 3 + 1
                cohort_key = f"{customer.created_at.year}-Q{quarter}"
            
            cohorts[cohort_key]['total'] += 1
            
            # Calculate periods since cohort start
            # (This is simplified - in real scenario, track actual activity)
            current_period = timezone.now()
            if cohort_type == 'monthly':
                months_diff = (current_period.year - customer.created_at.year) * 12 + \
                             (current_period.month - customer.created_at.month)
                cohorts[cohort_key]['periods'][months_diff] += 1
            else:
                quarters_diff = (current_period.year - customer.created_at.year) * 4 + \
                               ((current_period.month - 1) // 3 - (customer.created_at.month - 1) // 3)
                cohorts[cohort_key]['periods'][quarters_diff] += 1
        
        # Format response
        cohort_data = []
        for cohort_key in sorted(cohorts.keys()):
            cohort = cohorts[cohort_key]
            periods_data = []
            
            for period in range(max(cohort['periods'].keys()) + 1 if cohort['periods'] else 1):
                count = cohort['periods'].get(period, 0)
                retention_rate = (count / cohort['total'] * 100) if cohort['total'] > 0 else 0
                
                periods_data.append({
                    'period': period,
                    'count': count,
                    'retention_rate': round(retention_rate, 2)
                })
            
            cohort_data.append({
                'cohort': cohort_key,
                'total_customers': cohort['total'],
                'periods': periods_data
            })
        
        return Response({
            'cohort_type': cohort_type,
            'metric': metric,
            'cohorts': cohort_data
        })


class CustomMetricsView(views.APIView):
    """
    Custom business metrics and KPIs
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get custom business metrics"""
        period = request.query_params.get('period', '30')  # days
        period_days = int(period)
        start_date = timezone.now() - timedelta(days=period_days)
        
        # Lead metrics
        total_leads = Lead.objects.filter(created_at__gte=start_date).count()
        qualified_leads = Lead.objects.filter(
            created_at__gte=start_date,
            status='qualified'
        ).count()
        
        # Opportunity metrics
        opportunities = Opportunity.objects.filter(created_at__gte=start_date)
        total_opportunities = opportunities.count()
        won_opportunities = opportunities.filter(stage='closed_won').count()
        
        total_revenue = opportunities.filter(stage='closed_won').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Task metrics
        tasks = Task.objects.filter(created_at__gte=start_date)
        completed_tasks = tasks.filter(status='completed').count()
        overdue_tasks = tasks.filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count()
        
        # Activity metrics
        avg_lead_score = Lead.objects.filter(
            created_at__gte=start_date
        ).aggregate(avg=Avg('lead_score'))['avg'] or 0
        
        # Calculate trends (compare with previous period)
        prev_start = start_date - timedelta(days=period_days)
        prev_leads = Lead.objects.filter(
            created_at__gte=prev_start,
            created_at__lt=start_date
        ).count()
        
        lead_growth = ((total_leads - prev_leads) / prev_leads * 100) if prev_leads > 0 else 0
        
        return Response({
            'period_days': period_days,
            'start_date': start_date.isoformat(),
            'metrics': {
                'leads': {
                    'total': total_leads,
                    'qualified': qualified_leads,
                    'qualification_rate': round((qualified_leads / total_leads * 100) if total_leads > 0 else 0, 2),
                    'average_score': round(float(avg_lead_score), 2),
                    'growth_rate': round(lead_growth, 2)
                },
                'opportunities': {
                    'total': total_opportunities,
                    'won': won_opportunities,
                    'win_rate': round((won_opportunities / total_opportunities * 100) if total_opportunities > 0 else 0, 2),
                    'total_revenue': float(total_revenue),
                    'average_deal_size': float(total_revenue / won_opportunities) if won_opportunities > 0 else 0
                },
                'tasks': {
                    'total': tasks.count(),
                    'completed': completed_tasks,
                    'completion_rate': round((completed_tasks / tasks.count() * 100) if tasks.count() > 0 else 0, 2),
                    'overdue': overdue_tasks
                },
                'efficiency': {
                    'tasks_per_opportunity': round(tasks.count() / total_opportunities if total_opportunities > 0 else 0, 2),
                    'revenue_per_lead': float(total_revenue / total_leads) if total_leads > 0 else 0
                }
            }
        })


class DashboardAnalyticsView(views.APIView):
    """
    Aggregated dashboard analytics for the main dashboard
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get dashboard analytics data"""
        today = timezone.now()
        thirty_days_ago = today - timedelta(days=30)
        sixty_days_ago = today - timedelta(days=60)
        
        # 1. Revenue Metrics
        current_revenue = Opportunity.objects.filter(
            stage='closed_won',
            actual_close_date__gte=thirty_days_ago,
            actual_close_date__lte=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        previous_revenue = Opportunity.objects.filter(
            stage='closed_won',
            actual_close_date__gte=sixty_days_ago,
            actual_close_date__lt=thirty_days_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        revenue_change = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
        
        # 2. Deals Won Metrics
        current_deals = Opportunity.objects.filter(
            stage='closed_won',
            actual_close_date__gte=thirty_days_ago,
            actual_close_date__lte=today
        ).count()
        
        previous_deals = Opportunity.objects.filter(
            stage='closed_won',
            actual_close_date__gte=sixty_days_ago,
            actual_close_date__lt=thirty_days_ago
        ).count()
        
        deals_change = ((current_deals - previous_deals) / previous_deals * 100) if previous_deals > 0 else 0
        
        # 3. New Leads Metrics
        current_leads = Lead.objects.filter(
            created_at__gte=thirty_days_ago,
            created_at__lte=today
        ).count()
        
        previous_leads = Lead.objects.filter(
            created_at__gte=sixty_days_ago,
            created_at__lt=thirty_days_ago
        ).count()
        
        leads_change = ((current_leads - previous_leads) / previous_leads * 100) if previous_leads > 0 else 0
        
        # 4. Conversion Rate (Closed Won / Total Opportunities created in period)
        # Note: This is an approximation. Ideally track cohort conversion.
        current_opps_created = Opportunity.objects.filter(
            created_at__gte=thirty_days_ago,
            created_at__lte=today
        ).count()
        
        previous_opps_created = Opportunity.objects.filter(
            created_at__gte=sixty_days_ago,
            created_at__lt=thirty_days_ago
        ).count()
        
        current_conversion = (current_deals / current_opps_created * 100) if current_opps_created > 0 else 0
        previous_conversion = (previous_deals / previous_opps_created * 100) if previous_opps_created > 0 else 0
        
        conversion_change = ((current_conversion - previous_conversion) / previous_conversion * 100) if previous_conversion > 0 else 0
        
        # 5. Pipeline Overview
        pipeline_stages = ['prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won']
        pipeline_data = []
        
        stage_colors = {
            'prospecting': '#3b82f6',
            'qualification': '#8b5cf6',
            'proposal': '#f59e0b',
            'negotiation': '#22c55e',
            'closed_won': '#ef4444' # Usually won is green, but following the mock data colors
        }
        
        for stage in pipeline_stages:
            opps = Opportunity.objects.filter(stage=stage)
            count = opps.count()
            value = opps.aggregate(total=Sum('amount'))['total'] or 0
            
            pipeline_data.append({
                'name': stage.title().replace('_', ' '),
                'count': count,
                'value': float(value),
                'color': stage_colors.get(stage, '#cbd5e1')
            })
            
        # 6. Recent Activities
        recent_activities = []
        activities = Activity.objects.select_related('user', 'content_type').order_by('-timestamp')[:10]
        
        icons = {
            'lead': 'users',
            'contact': 'users',
            'opportunity': 'dollar-sign',
            'task': 'calendar',
            'note': 'file-text'
        }
        
        for activity in activities:
            entity_type = activity.content_type.model if activity.content_type else 'activity'
            recent_activities.append({
                'id': str(activity.id),
                'type': entity_type,
                'title': activity.description or f"New {entity_type}",
                'description': activity.object_repr or '',
                'timestamp': activity.timestamp.isoformat(),
                'icon_name': icons.get(entity_type, 'activity')
            })
            
        # 7. Top Performers (by revenue)
        top_performers = []
        users = User.objects.all()
        
        for user in users:
            revenue = Opportunity.objects.filter(
                owner=user,
                stage='closed_won',
                actual_close_date__gte=thirty_days_ago
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            deals_count = Opportunity.objects.filter(
                owner=user,
                stage='closed_won',
                actual_close_date__gte=thirty_days_ago
            ).count()
            
            if revenue > 0 or deals_count > 0:
                top_performers.append({
                    'name': user.get_full_name() or user.username,
                    'deals': deals_count,
                    'revenue': float(revenue)
                })
        
        top_performers.sort(key=lambda x: x['revenue'], reverse=True)
        top_performers = top_performers[:5]
        
        # 8. Weekly Goal
        # For now, hardcoded target, current is revenue this week
        start_of_week = today - timedelta(days=today.weekday())
        weekly_revenue = Opportunity.objects.filter(
            stage='closed_won',
            actual_close_date__gte=start_of_week
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        weekly_target = 100000 # Example target
        
        return Response({
            'revenue': {
                'value': float(current_revenue),
                'previousValue': float(previous_revenue),
                'change': round(revenue_change, 1),
                'trend': 'up' if revenue_change >= 0 else 'down',
                'label': 'Revenue',
                'format': 'currency'
            },
            'deals': {
                'value': current_deals,
                'previousValue': previous_deals,
                'change': round(deals_change, 1),
                'trend': 'up' if deals_change >= 0 else 'down',
                'label': 'Deals Won',
                'format': 'number'
            },
            'leads': {
                'value': current_leads,
                'previousValue': previous_leads,
                'change': round(leads_change, 1),
                'trend': 'up' if leads_change >= 0 else 'down',
                'label': 'New Leads',
                'format': 'number'
            },
            'conversionRate': {
                'value': round(current_conversion, 1),
                'previousValue': round(previous_conversion, 1),
                'change': round(conversion_change, 1),
                'trend': 'up' if conversion_change >= 0 else 'down',
                'label': 'Conversion',
                'format': 'percentage'
            },
            'pipeline': pipeline_data,
            'recentActivities': recent_activities,
            'topPerformers': top_performers,
            'weeklyGoal': {
                'current': float(weekly_revenue),
                'target': weekly_target
            }
        })
