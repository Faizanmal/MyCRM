"""
Analytics and Reporting API

Provides analytics endpoints for:
- Dashboard metrics
- Sales performance
- Pipeline analytics
- Activity tracking
- Trend analysis
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal

from django.db.models import Count, Sum, Avg, F, Q
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)
User = get_user_model()


def get_date_range(period: str = 'month') -> tuple[datetime, datetime]:
    """Get start and end dates for a period."""
    now = timezone.now()
    
    if period == 'today':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == 'week':
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == 'month':
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == 'quarter':
        quarter_start_month = ((now.month - 1) // 3) * 3 + 1
        start = now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == 'year':
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    else:
        # Default to last 30 days
        start = now - timedelta(days=30)
        end = now
    
    return start, end


def get_comparison_period(start: datetime, end: datetime) -> tuple[datetime, datetime]:
    """Get the previous period for comparison."""
    duration = end - start
    prev_end = start
    prev_start = prev_end - duration
    return prev_start, prev_end


def calculate_change_percent(current: float, previous: float) -> Optional[float]:
    """Calculate percentage change between two values."""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100, 1)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_metrics(request):
    """Get key dashboard metrics."""
    period = request.query_params.get('period', 'month')
    start, end = get_date_range(period)
    prev_start, prev_end = get_comparison_period(start, end)
    
    try:
        from lead_management.models import Lead
        from contact_management.models import Contact
        from opportunity_management.models import Opportunity
        from task_management.models import Task
        
        # Current period metrics
        leads_count = Lead.objects.filter(
            created_at__gte=start,
            created_at__lte=end
        ).count()
        
        contacts_count = Contact.objects.filter(
            created_at__gte=start,
            created_at__lte=end
        ).count()
        
        opportunities = Opportunity.objects.filter(
            created_at__gte=start,
            created_at__lte=end
        )
        
        active_deals = opportunities.exclude(stage__in=['closed_won', 'closed_lost']).count()
        
        won_deals = opportunities.filter(stage='closed_won')
        revenue = won_deals.aggregate(total=Sum('value'))['total'] or 0
        
        tasks_completed = Task.objects.filter(
            status='completed',
            updated_at__gte=start,
            updated_at__lte=end
        ).count()
        
        # Previous period for comparison
        prev_leads = Lead.objects.filter(
            created_at__gte=prev_start,
            created_at__lt=prev_end
        ).count()
        
        prev_revenue = Opportunity.objects.filter(
            stage='closed_won',
            created_at__gte=prev_start,
            created_at__lt=prev_end
        ).aggregate(total=Sum('value'))['total'] or 0
        
        return Response({
            'success': True,
            'data': {
                'leads': {
                    'value': leads_count,
                    'change': calculate_change_percent(leads_count, prev_leads),
                    'trend': 'up' if leads_count > prev_leads else 'down' if leads_count < prev_leads else 'neutral'
                },
                'contacts': {
                    'value': contacts_count,
                },
                'activeDeals': {
                    'value': active_deals,
                },
                'revenue': {
                    'value': float(revenue),
                    'change': calculate_change_percent(float(revenue), float(prev_revenue)),
                    'trend': 'up' if revenue > prev_revenue else 'down' if revenue < prev_revenue else 'neutral'
                },
                'tasksCompleted': {
                    'value': tasks_completed,
                },
                'period': period,
                'dateRange': {
                    'start': start.isoformat(),
                    'end': end.isoformat(),
                }
            }
        })
    except Exception as e:
        logger.error(f"Error fetching dashboard metrics: {e}")
        return Response({
            'success': False,
            'message': 'Failed to fetch dashboard metrics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def revenue_analytics(request):
    """Get revenue analytics with trends."""
    period = request.query_params.get('period', 'month')
    group_by = request.query_params.get('group_by', 'day')
    
    try:
        from opportunity_management.models import Opportunity
        
        # Determine date range
        if period == 'year':
            start = timezone.now() - timedelta(days=365)
            trunc_func = TruncMonth
        elif period == 'quarter':
            start = timezone.now() - timedelta(days=90)
            trunc_func = TruncWeek
        else:
            start = timezone.now() - timedelta(days=30)
            trunc_func = TruncDay if group_by == 'day' else TruncWeek
        
        # Get revenue by period
        revenue_data = Opportunity.objects.filter(
            stage='closed_won',
            created_at__gte=start
        ).annotate(
            period=trunc_func('created_at')
        ).values('period').annotate(
            revenue=Sum('value'),
            count=Count('id')
        ).order_by('period')
        
        # Get pipeline value
        pipeline_data = Opportunity.objects.exclude(
            stage__in=['closed_won', 'closed_lost']
        ).aggregate(
            total_value=Sum('value'),
            weighted_value=Sum(F('value') * F('probability') / 100)
        )
        
        return Response({
            'success': True,
            'data': {
                'trend': [
                    {
                        'date': item['period'].isoformat() if item['period'] else None,
                        'revenue': float(item['revenue'] or 0),
                        'deals': item['count']
                    }
                    for item in revenue_data
                ],
                'pipeline': {
                    'totalValue': float(pipeline_data['total_value'] or 0),
                    'weightedValue': float(pipeline_data['weighted_value'] or 0),
                }
            }
        })
    except Exception as e:
        logger.error(f"Error fetching revenue analytics: {e}")
        return Response({
            'success': False,
            'message': 'Failed to fetch revenue analytics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pipeline_analytics(request):
    """Get pipeline analytics by stage."""
    try:
        from opportunity_management.models import Opportunity
        
        # Pipeline by stage
        pipeline_stages = Opportunity.objects.exclude(
            stage__in=['closed_won', 'closed_lost']
        ).values('stage').annotate(
            count=Count('id'),
            value=Sum('value'),
            avg_value=Avg('value')
        ).order_by('stage')
        
        # Conversion rates
        total_opportunities = Opportunity.objects.count()
        won_opportunities = Opportunity.objects.filter(stage='closed_won').count()
        lost_opportunities = Opportunity.objects.filter(stage='closed_lost').count()
        
        conversion_rate = (won_opportunities / total_opportunities * 100) if total_opportunities > 0 else 0
        
        # Average deal size
        avg_deal_size = Opportunity.objects.filter(
            stage='closed_won'
        ).aggregate(avg=Avg('value'))['avg'] or 0
        
        # Average sales cycle
        won_deals = Opportunity.objects.filter(stage='closed_won')
        if won_deals.exists():
            avg_cycle_days = won_deals.aggregate(
                avg_days=Avg(F('updated_at') - F('created_at'))
            )['avg_days']
            avg_cycle = avg_cycle_days.days if avg_cycle_days else 0
        else:
            avg_cycle = 0
        
        return Response({
            'success': True,
            'data': {
                'stages': [
                    {
                        'stage': item['stage'],
                        'count': item['count'],
                        'value': float(item['value'] or 0),
                        'avgValue': float(item['avg_value'] or 0)
                    }
                    for item in pipeline_stages
                ],
                'metrics': {
                    'conversionRate': round(conversion_rate, 1),
                    'avgDealSize': float(avg_deal_size),
                    'avgSalesCycle': avg_cycle,
                    'totalDeals': total_opportunities,
                    'wonDeals': won_opportunities,
                    'lostDeals': lost_opportunities,
                }
            }
        })
    except Exception as e:
        logger.error(f"Error fetching pipeline analytics: {e}")
        return Response({
            'success': False,
            'message': 'Failed to fetch pipeline analytics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_analytics(request):
    """Get activity analytics."""
    period = request.query_params.get('period', 'week')
    start, end = get_date_range(period)
    
    try:
        from task_management.models import Task
        
        # Tasks by status
        tasks_by_status = Task.objects.filter(
            created_at__gte=start
        ).values('status').annotate(
            count=Count('id')
        )
        
        # Tasks by priority
        tasks_by_priority = Task.objects.filter(
            created_at__gte=start
        ).values('priority').annotate(
            count=Count('id')
        )
        
        # Daily activity
        daily_activity = Task.objects.filter(
            created_at__gte=start
        ).annotate(
            day=TruncDay('created_at')
        ).values('day').annotate(
            created=Count('id'),
            completed=Count('id', filter=Q(status='completed'))
        ).order_by('day')
        
        # Overdue tasks
        overdue_count = Task.objects.filter(
            status__in=['pending', 'in_progress'],
            due_date__lt=timezone.now()
        ).count()
        
        return Response({
            'success': True,
            'data': {
                'byStatus': {item['status']: item['count'] for item in tasks_by_status},
                'byPriority': {item['priority']: item['count'] for item in tasks_by_priority},
                'dailyActivity': [
                    {
                        'date': item['day'].isoformat() if item['day'] else None,
                        'created': item['created'],
                        'completed': item['completed']
                    }
                    for item in daily_activity
                ],
                'overdue': overdue_count,
            }
        })
    except Exception as e:
        logger.error(f"Error fetching activity analytics: {e}")
        return Response({
            'success': False,
            'message': 'Failed to fetch activity analytics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def team_performance(request):
    """Get team performance analytics."""
    period = request.query_params.get('period', 'month')
    start, end = get_date_range(period)
    
    try:
        from lead_management.models import Lead
        from opportunity_management.models import Opportunity
        from task_management.models import Task
        
        # Get team members (users with activity)
        team_stats = []
        
        users_with_activity = User.objects.filter(
            Q(lead_assigns__created_at__gte=start) |
            Q(opportunity_set__created_at__gte=start) |
            Q(task_assignments__created_at__gte=start)
        ).distinct()
        
        for user in users_with_activity:
            leads_handled = Lead.objects.filter(
                assigned_to=user,
                created_at__gte=start
            ).count()
            
            deals_won = Opportunity.objects.filter(
                owner=user,
                stage='closed_won',
                updated_at__gte=start
            )
            
            revenue = deals_won.aggregate(total=Sum('value'))['total'] or 0
            
            tasks_completed = Task.objects.filter(
                assigned_to=user,
                status='completed',
                updated_at__gte=start
            ).count()
            
            team_stats.append({
                'id': user.id,
                'name': user.get_full_name() or user.username,
                'leads': leads_handled,
                'dealsWon': deals_won.count(),
                'revenue': float(revenue),
                'tasksCompleted': tasks_completed,
            })
        
        # Sort by revenue
        team_stats.sort(key=lambda x: x['revenue'], reverse=True)
        
        return Response({
            'success': True,
            'data': {
                'team': team_stats,
                'period': period,
            }
        })
    except Exception as e:
        logger.error(f"Error fetching team performance: {e}")
        return Response({
            'success': False,
            'message': 'Failed to fetch team performance'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lead_source_analytics(request):
    """Get lead source analytics."""
    period = request.query_params.get('period', 'month')
    start, end = get_date_range(period)
    
    try:
        from lead_management.models import Lead
        
        # Leads by source
        source_stats = Lead.objects.filter(
            created_at__gte=start
        ).values('source').annotate(
            count=Count('id'),
            converted=Count('id', filter=Q(status='won'))
        ).order_by('-count')
        
        # Calculate conversion rates
        result = []
        for item in source_stats:
            conversion = (item['converted'] / item['count'] * 100) if item['count'] > 0 else 0
            result.append({
                'source': item['source'] or 'Unknown',
                'count': item['count'],
                'converted': item['converted'],
                'conversionRate': round(conversion, 1)
            })
        
        return Response({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"Error fetching lead source analytics: {e}")
        return Response({
            'success': False,
            'message': 'Failed to fetch lead source analytics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# URL patterns to add to urls.py:
# path('analytics/dashboard/', dashboard_metrics, name='analytics-dashboard'),
# path('analytics/revenue/', revenue_analytics, name='analytics-revenue'),
# path('analytics/pipeline/', pipeline_analytics, name='analytics-pipeline'),
# path('analytics/activity/', activity_analytics, name='analytics-activity'),
# path('analytics/team/', team_performance, name='analytics-team'),
# path('analytics/lead-sources/', lead_source_analytics, name='analytics-lead-sources'),
