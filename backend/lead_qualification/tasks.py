from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task
def calculate_lead_score_task(lead_id):
    """Background task to calculate lead score"""
    try:
        from lead_management.models import Lead
        from .scoring_engine import LeadScoringEngine
        
        lead = Lead.objects.get(id=lead_id)
        engine = LeadScoringEngine(lead)
        lead_score = engine.calculate_score()
        
        logger.info(f"Calculated score for lead {lead.name}: {lead_score.score}")
        return {
            'success': True,
            'lead_id': lead_id,
            'score': lead_score.score
        }
    except Exception as e:
        logger.error(f"Error calculating score for lead {lead_id}: {str(e)}")
        return {
            'success': False,
            'lead_id': lead_id,
            'error': str(e)
        }


@shared_task
def bulk_recalculate_scores_task():
    """Recalculate scores for all leads"""
    try:
        from .scoring_engine import recalculate_all_leads
        results = recalculate_all_leads()
        logger.info(f"Bulk recalculation completed: {results}")
        return results
    except Exception as e:
        logger.error(f"Error in bulk recalculation: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def enrich_lead_data_task(lead_id, source='api'):
    """Background task to enrich lead data from external sources"""
    try:
        from lead_management.models import Lead
        from .models import LeadEnrichmentData
        
        lead = Lead.objects.get(id=lead_id)
        
        # Mock enrichment - integrate with real services like Clearbit, Hunter.io
        enrichment_data = {
            'company_size': 'Unknown',
            'company_revenue': 'Unknown',
            'company_industry': 'Unknown',
            'enrichment_note': 'Mock enrichment - integrate real API'
        }
        
        enrichment = LeadEnrichmentData.objects.create(
            lead=lead,
            source=source,
            data=enrichment_data,
            company_size=enrichment_data.get('company_size', ''),
            company_industry=enrichment_data.get('company_industry', ''),
            is_verified=False,
            confidence_score=0.5
        )
        
        logger.info(f"Enriched lead {lead.name} from {source}")
        return {
            'success': True,
            'lead_id': lead_id,
            'enrichment_id': enrichment.id
        }
    except Exception as e:
        logger.error(f"Error enriching lead {lead_id}: {str(e)}")
        return {
            'success': False,
            'lead_id': lead_id,
            'error': str(e)
        }


@shared_task
def check_qualification_workflows():
    """Periodic task to check and execute qualification workflows"""
    try:
        from .models import QualificationWorkflow
        from lead_management.models import Lead
        from .scoring_engine import LeadScoringEngine
        
        workflows = QualificationWorkflow.objects.filter(
            is_active=True,
            trigger_type='time_based'
        )
        
        executed_count = 0
        for workflow in workflows:
            # Get leads that match time-based criteria
            trigger_config = workflow.trigger_config
            check_interval_days = trigger_config.get('check_interval_days', 1)
            
            # Find leads that need checking
            last_check = timezone.now() - timezone.timedelta(days=check_interval_days)
            leads = Lead.objects.filter(
                updated_at__gte=last_check
            )
            
            for lead in leads:
                engine = LeadScoringEngine(lead)
                engine._check_workflows(lead.score, None)
                executed_count += 1
        
        logger.info(f"Checked {executed_count} leads for qualification workflows")
        return {
            'success': True,
            'checked': executed_count
        }
    except Exception as e:
        logger.error(f"Error checking workflows: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def daily_score_recalculation():
    """Daily task to recalculate scores for active leads"""
    try:
        from lead_management.models import Lead
        from .scoring_engine import LeadScoringEngine
        
        # Only recalculate for leads that have been active in the last 30 days
        active_leads = Lead.objects.filter(
            status__in=['new', 'contacted', 'qualified'],
            updated_at__gte=timezone.now() - timezone.timedelta(days=30)
        )
        
        results = {
            'total': 0,
            'success': 0,
            'failed': 0
        }
        
        for lead in active_leads:
            results['total'] += 1
            try:
                engine = LeadScoringEngine(lead)
                engine.calculate_score()
                results['success'] += 1
            except Exception as e:
                results['failed'] += 1
                logger.error(f"Failed to calculate score for lead {lead.id}: {str(e)}")
        
        logger.info(f"Daily score recalculation completed: {results}")
        return results
    except Exception as e:
        logger.error(f"Error in daily recalculation: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
