"""
Celery tasks for Predictive Lead Routing
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def process_routing_queue():
    """Process unassigned leads queue - run every 5 minutes"""
    from .services import LeadRoutingService

    service = LeadRoutingService()
    results = service.process_routing_queue()

    logger.info(f"Routing queue processed: {results}")
    return results


@shared_task
def check_escalations():
    """Check and process escalations - run every 15 minutes"""
    from .services import LeadRoutingService

    service = LeadRoutingService()
    results = service.check_and_process_escalations()

    logger.info(f"Escalations processed: {results}")
    return results


@shared_task
def update_rep_performance_metrics():
    """Update all rep performance metrics - run daily"""
    from .models import SalesRepProfile
    from .services import RepPerformanceService

    service = RepPerformanceService()
    updated = 0

    for profile in SalesRepProfile.objects.all():
        try:
            service.update_rep_performance(profile)
            updated += 1
        except Exception as e:
            logger.error(f"Failed to update performance for rep {profile.id}: {e}")

    return {'updated': updated}


@shared_task
def record_routing_analytics():
    """Record daily routing analytics - run daily"""
    from .services import AnalyticsService

    service = AnalyticsService()
    analytics = service.record_daily_analytics()

    return {'date': str(analytics.date), 'total_routed': analytics.total_leads_routed}


@shared_task
def check_capacity_and_rebalance():
    """Check rep capacity and trigger rebalancing if needed - run every hour"""
    from .models import SalesRepProfile
    from .routing_engine import LeadRebalancer
    from .services import LeadRoutingService

    reps = list(SalesRepProfile.objects.filter(is_available=True))
    rebalancer = LeadRebalancer()
    analysis = rebalancer.analyze_distribution(reps)

    if analysis.get('needs_rebalancing') and analysis.get('imbalance_ratio', 0) > 1.5:
        service = LeadRoutingService()
        result = service.trigger_rebalancing(reason='scheduled')
        return result

    return {'rebalancing_needed': False}


@shared_task
def cleanup_old_assignments():
    """Archive old assignment records - run weekly"""
    from datetime import timedelta

    from django.utils import timezone

    from .models import LeadAssignment

    cutoff = timezone.now() - timedelta(days=365)
    deleted = LeadAssignment.objects.filter(
        assigned_at__lt=cutoff,
        status__in=['converted', 'lost']
    ).delete()[0]

    return {'archived': deleted}
