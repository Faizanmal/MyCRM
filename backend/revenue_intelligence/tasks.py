"""
Revenue Intelligence Celery Tasks
Scheduled jobs for forecasting, scoring, and snapshots
"""

from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def daily_pipeline_snapshot():
    """
    Create daily pipeline snapshots for all users
    Run daily at midnight
    """
    from .models import PipelineSnapshot
    from opportunity_management.models import Opportunity
    from django.db.models import Sum, Avg, Count, F
    
    today = timezone.now().date()
    
    for user in User.objects.filter(is_active=True):
        # Get user's pipeline
        pipeline = Opportunity.objects.filter(
            owner=user
        ).exclude(stage__in=['closed_won', 'closed_lost'])
        
        if not pipeline.exists():
            continue
        
        # Calculate metrics
        total = pipeline.aggregate(total=Sum('amount'))['total'] or 0
        weighted = pipeline.aggregate(
            total=Sum(F('amount') * F('probability') / 100)
        )['total'] or 0
        
        # Stage breakdown
        stage_breakdown = {}
        for stage in ['prospecting', 'qualification', 'proposal', 'negotiation']:
            stage_data = pipeline.filter(stage=stage).aggregate(
                count=Count('id'),
                value=Sum('amount')
            )
            stage_breakdown[stage] = {
                'count': stage_data['count'],
                'value': float(stage_data['value'] or 0)
            }
        
        # Get yesterday's snapshot for movement calculation
        yesterday = today - timedelta(days=1)
        prev_snapshot = PipelineSnapshot.objects.filter(
            user=user,
            snapshot_date=yesterday
        ).first()
        
        # Calculate movement (simplified)
        new_pipeline = 0
        if prev_snapshot:
            new_pipeline = float(total) - float(prev_snapshot.total_pipeline)
        
        # Closed today
        closed_won = Opportunity.objects.filter(
            owner=user,
            stage='closed_won',
            actual_close_date=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        closed_lost = Opportunity.objects.filter(
            owner=user,
            stage='closed_lost',
            actual_close_date=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Win rate (last 90 days)
        closed_90d = Opportunity.objects.filter(
            owner=user,
            stage__in=['closed_won', 'closed_lost'],
            actual_close_date__gte=today - timedelta(days=90)
        )
        won_count = closed_90d.filter(stage='closed_won').count()
        total_closed = closed_90d.count()
        win_rate = (won_count / total_closed * 100) if total_closed > 0 else 0
        
        PipelineSnapshot.objects.create(
            user=user,
            snapshot_date=today,
            total_pipeline=total,
            weighted_pipeline=weighted,
            deal_count=pipeline.count(),
            stage_breakdown=stage_breakdown,
            new_pipeline=max(0, new_pipeline),
            closed_won=closed_won,
            closed_lost=closed_lost,
            avg_deal_size=pipeline.aggregate(avg=Avg('amount'))['avg'] or 0,
            win_rate=win_rate,
        )
    
    logger.info(f"Created pipeline snapshots for {today}")


@shared_task
def score_all_deals():
    """
    Score all open deals
    Run daily
    """
    from .engine import DealScoringEngine
    from opportunity_management.models import Opportunity
    
    engine = DealScoringEngine()
    
    opportunities = Opportunity.objects.exclude(
        stage__in=['closed_won', 'closed_lost']
    )
    
    scored = 0
    errors = 0
    
    for opp in opportunities:
        try:
            engine.score_deal(opp)
            scored += 1
        except Exception as e:
            logger.error(f"Error scoring deal {opp.id}: {e}")
            errors += 1
    
    logger.info(f"Scored {scored} deals, {errors} errors")
    return {'scored': scored, 'errors': errors}


@shared_task
def scan_for_risk_alerts():
    """
    Scan all deals for risk factors
    Run every 4 hours
    """
    from .engine import RiskAlertEngine
    
    engine = RiskAlertEngine()
    alerts = engine.scan_deals_for_risks()
    
    logger.info(f"Created {len(alerts)} risk alerts")
    return {'alerts_created': len(alerts)}


@shared_task
def generate_weekly_forecasts():
    """
    Generate forecasts for all users
    Run weekly on Monday
    """
    from .engine import RevenueForecastEngine
    from .models import RevenueTarget
    
    engine = RevenueForecastEngine()
    today = timezone.now().date()
    
    # Get all users with active targets
    targets = RevenueTarget.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    )
    
    forecasts_generated = 0
    
    for target in targets:
        try:
            engine.generate_forecast(
                target.user,
                target.start_date,
                target.end_date
            )
            forecasts_generated += 1
        except Exception as e:
            logger.error(f"Error generating forecast for {target.user}: {e}")
    
    logger.info(f"Generated forecasts for {forecasts_generated} users")
    return {'forecasts_generated': forecasts_generated}


@shared_task
def update_target_actuals():
    """
    Update all active target achieved amounts
    Run daily
    """
    from .models import RevenueTarget
    from opportunity_management.models import Opportunity
    from django.db.models import Sum, F
    from decimal import Decimal
    
    today = timezone.now().date()
    
    targets = RevenueTarget.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    )
    
    for target in targets:
        # Calculate achieved
        achieved = Opportunity.objects.filter(
            owner=target.user,
            stage='closed_won',
            actual_close_date__gte=target.start_date,
            actual_close_date__lte=target.end_date
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Calculate pipeline
        pipeline = Opportunity.objects.filter(
            owner=target.user,
            expected_close_date__gte=target.start_date,
            expected_close_date__lte=target.end_date
        ).exclude(stage__in=['closed_won', 'closed_lost'])
        
        total_pipeline = pipeline.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        weighted = pipeline.aggregate(
            total=Sum(F('amount') * F('probability') / 100)
        )['total'] or Decimal('0')
        
        target.achieved_amount = achieved
        target.pipeline_amount = total_pipeline
        target.weighted_pipeline = weighted
        target.save()
    
    logger.info(f"Updated {targets.count()} targets")
