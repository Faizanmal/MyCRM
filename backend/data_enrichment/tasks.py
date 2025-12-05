"""
Data Enrichment Celery Tasks
Background tasks for enrichment operations
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(name='data_enrichment.enrich_contact_async')
def enrich_contact_async(record_id: str, record_type: str = 'contact'):
    """Asynchronously enrich a contact or lead"""
    from .services import EnrichmentService
    
    service = EnrichmentService()
    
    try:
        if record_type == 'contact':
            from contact_management.models import Contact
            contact = Contact.objects.get(id=record_id)
            
            result = service.enrich_contact_or_lead(
                email=contact.email,
                contact=contact
            )
        else:
            from lead_management.models import Lead
            lead = Lead.objects.get(id=record_id)
            
            result = service.enrich_contact_or_lead(
                email=lead.email,
                lead=lead
            )
        
        logger.info(f"Enriched {record_type} {record_id}: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error enriching {record_type} {record_id}: {e}")
        return {'error': str(e)}


@shared_task(name='data_enrichment.process_bulk_enrichment_job')
def process_bulk_enrichment_job(job_id: str):
    """Process a bulk enrichment job"""
    from .services import BulkEnrichmentService
    
    service = BulkEnrichmentService()
    
    try:
        job = service.process_bulk_job(job_id)
        logger.info(f"Completed bulk job {job_id}: {job.successful_records}/{job.total_records} successful")
        return {
            'job_id': job_id,
            'status': job.status,
            'successful': job.successful_records,
            'failed': job.failed_records
        }
    except Exception as e:
        logger.error(f"Error processing bulk job {job_id}: {e}")
        return {'error': str(e)}


@shared_task(name='data_enrichment.refresh_stale_profiles')
def refresh_stale_profiles():
    """Refresh enrichment profiles that are stale (>30 days old)"""
    from .models import EnrichmentProfile
    from .services import EnrichmentService
    
    cutoff = timezone.now() - timedelta(days=30)
    
    stale_profiles = EnrichmentProfile.objects.filter(
        last_enriched_at__lt=cutoff,
        status='enriched'
    )[:100]  # Limit to 100 per run
    
    service = EnrichmentService()
    refreshed = 0
    
    for profile in stale_profiles:
        try:
            profile.status = 'stale'
            profile.save()
            
            service.enrich_contact_or_lead(
                email=profile.email,
                contact=profile.contact,
                lead=profile.lead
            )
            refreshed += 1
        except Exception as e:
            logger.error(f"Error refreshing profile {profile.email}: {e}")
    
    logger.info(f"Refreshed {refreshed} stale profiles")
    return {'refreshed': refreshed}


@shared_task(name='data_enrichment.fetch_company_news')
def fetch_company_news_task():
    """Fetch news for all tracked companies"""
    from .models import CompanyEnrichment
    from .services import EnrichmentService
    
    service = EnrichmentService()
    
    # Get companies enriched in last 90 days
    cutoff = timezone.now() - timedelta(days=90)
    companies = CompanyEnrichment.objects.filter(
        last_enriched_at__gte=cutoff
    )
    
    news_fetched = 0
    
    for company in companies[:50]:  # Limit to 50 per run
        try:
            alerts = service.fetch_company_news(company.domain, days_back=7)
            news_fetched += len(alerts)
        except Exception as e:
            logger.error(f"Error fetching news for {company.domain}: {e}")
    
    logger.info(f"Fetched {news_fetched} news alerts")
    return {'news_fetched': news_fetched}


@shared_task(name='data_enrichment.refresh_intent_signals')
def refresh_intent_signals():
    """Refresh intent signals for tracked companies"""
    from .models import CompanyEnrichment, IntentSignal
    from .services import EnrichmentService
    
    service = EnrichmentService()
    
    # Get companies with recent activity
    cutoff = timezone.now() - timedelta(days=30)
    companies = CompanyEnrichment.objects.filter(
        last_enriched_at__gte=cutoff
    )[:30]
    
    signals_created = 0
    
    for company in companies:
        try:
            signals = service.get_intent_signals(company.domain)
            signals_created += len(signals)
        except Exception as e:
            logger.error(f"Error getting intent for {company.domain}: {e}")
    
    logger.info(f"Created {signals_created} intent signals")
    return {'signals_created': signals_created}


@shared_task(name='data_enrichment.expire_old_intent_signals')
def expire_old_intent_signals():
    """Delete expired intent signals"""
    from .models import IntentSignal
    
    deleted = IntentSignal.objects.filter(
        expires_at__lt=timezone.now()
    ).delete()
    
    logger.info(f"Deleted {deleted[0]} expired intent signals")
    return {'deleted': deleted[0]}


@shared_task(name='data_enrichment.notify_intent_signal')
def notify_intent_signal(signal_id: str):
    """Send notification for strong intent signal"""
    from .models import IntentSignal
    
    try:
        signal = IntentSignal.objects.get(id=signal_id)
        
        # In production, this would send email/notification
        # For now, just log
        logger.info(f"Strong intent signal notification: {signal.topic} for {signal.company}")
        
        return {'notified': True, 'signal_id': signal_id}
        
    except IntentSignal.DoesNotExist:
        return {'notified': False, 'error': 'Signal not found'}


@shared_task(name='data_enrichment.process_sales_trigger_alert')
def process_sales_trigger_alert(alert_id: str):
    """Process a sales trigger news alert"""
    from .models import NewsAlert
    
    try:
        alert = NewsAlert.objects.get(id=alert_id)
        
        # Generate recommended action based on alert type
        recommendations = {
            'funding': 'Reach out about expanded budget and growth plans',
            'expansion': 'Discuss how your solution can support their expansion',
            'executive_change': 'Introduce yourself to new decision makers',
            'acquisition': 'Position your solution for the combined organization',
            'product_launch': 'Discuss how you can support their new initiative'
        }
        
        alert.recommended_action = recommendations.get(
            alert.alert_type,
            'Review opportunity and plan outreach'
        )
        alert.save()
        
        # In production, would create task or notification
        logger.info(f"Processed sales trigger: {alert.title}")
        
        return {'processed': True, 'alert_id': alert_id}
        
    except NewsAlert.DoesNotExist:
        return {'processed': False, 'error': 'Alert not found'}


@shared_task(name='data_enrichment.reset_daily_provider_limits')
def reset_daily_provider_limits():
    """Reset daily request counts for all providers"""
    from .models import EnrichmentProvider
    
    today = timezone.now().date()
    
    providers = EnrichmentProvider.objects.exclude(last_request_reset=today)
    
    for provider in providers:
        provider.daily_requests_used = 0
        provider.last_request_reset = today
        provider.save()
    
    logger.info(f"Reset daily limits for {providers.count()} providers")
    return {'providers_reset': providers.count()}


@shared_task(name='data_enrichment.enrich_pending_profiles')
def enrich_pending_profiles():
    """Process pending enrichment profiles"""
    from .models import EnrichmentProfile
    from .services import EnrichmentService
    
    pending = EnrichmentProfile.objects.filter(status='pending')[:50]
    
    service = EnrichmentService()
    enriched = 0
    
    for profile in pending:
        try:
            service.enrich_contact_or_lead(
                email=profile.email,
                contact=profile.contact,
                lead=profile.lead
            )
            enriched += 1
        except Exception as e:
            logger.error(f"Error enriching pending profile {profile.email}: {e}")
    
    logger.info(f"Enriched {enriched} pending profiles")
    return {'enriched': enriched}


@shared_task(name='data_enrichment.sync_technographics')
def sync_technographics():
    """Sync technographic data for companies"""
    from .models import CompanyEnrichment
    from .services import EnrichmentService
    
    service = EnrichmentService()
    
    # Get companies without recent technographic data
    cutoff = timezone.now() - timedelta(days=30)
    companies = CompanyEnrichment.objects.filter(
        technographics__last_detected__lt=cutoff
    ).distinct()[:30]
    
    synced = 0
    
    for company in companies:
        try:
            result = service.engine.get_technographics(company.domain)
            if result.success:
                # Process technographics
                service._process_technographics(company, result.data.get('technologies', []))
                synced += 1
        except Exception as e:
            logger.error(f"Error syncing technographics for {company.domain}: {e}")
    
    logger.info(f"Synced technographics for {synced} companies")
    return {'synced': synced}


@shared_task(name='data_enrichment.generate_enrichment_report')
def generate_enrichment_report():
    """Generate daily enrichment statistics report"""
    from .services import EnrichmentStatsService
    
    stats = EnrichmentStatsService.get_enrichment_stats()
    provider_stats = EnrichmentStatsService.get_provider_stats()
    
    report = {
        'date': timezone.now().date().isoformat(),
        'overall_stats': stats,
        'provider_stats': provider_stats
    }
    
    logger.info(f"Enrichment report generated: {stats}")
    return report
