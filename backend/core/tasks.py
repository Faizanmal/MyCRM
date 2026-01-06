"""
Core Module Celery Tasks
Background tasks for lead scoring, workflows, and analytics
"""
import logging

from celery import shared_task
from django.db.models import Q
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def retrain_lead_scoring_model(self):
    """
    Retrain the lead scoring ML model
    Runs weekly to improve predictions based on new data
    """
    try:
        from core.lead_scoring import LeadScoringEngine
        from lead_management.models import Lead

        logger.info("Starting lead scoring model retraining...")

        # Get leads with conversion data
        leads = Lead.objects.filter(
            Q(status='converted') | Q(status='lost')
        ).select_related('assigned_to', 'owner')

        if leads.count() < 50:
            logger.warning(f"Not enough training data ({leads.count()} leads). Need at least 50.")
            return {
                'success': False,
                'message': 'Insufficient training data'
            }

        # Train model
        engine = LeadScoringEngine()
        metrics = engine.train_model(leads)

        # Save model
        engine.save_model()

        logger.info(f"Model retrained successfully. Accuracy: {metrics['test_accuracy']:.2f}")

        return {
            'success': True,
            'metrics': metrics,
            'trained_at': timezone.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to retrain lead scoring model: {str(e)}")
        raise self.retry(exc=e, countdown=300)  # Retry after 5 minutes


@shared_task(bind=True)
def score_lead(self, lead_id):
    """
    Score a single lead using the trained ML model
    """
    try:
        from core.lead_scoring import LeadScoringEngine
        from lead_management.models import Lead

        lead = Lead.objects.get(id=lead_id)
        engine = LeadScoringEngine()

        # Load model if not already loaded
        if not engine.model:
            engine.load_model()

        # Score the lead
        score = engine.score_lead(lead)

        # Update lead score
        lead.lead_score = score
        lead.save(update_fields=['lead_score', 'updated_at'])

        logger.info(f"Lead {lead_id} scored: {score}")

        return {
            'success': True,
            'lead_id': lead_id,
            'score': score
        }

    except Exception as e:
        logger.error(f"Failed to score lead {lead_id}: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@shared_task(bind=True)
def bulk_score_leads(self, lead_ids=None):
    """
    Score multiple leads in bulk
    """
    try:
        from core.lead_scoring import LeadScoringEngine
        from lead_management.models import Lead

        if lead_ids:
            leads = Lead.objects.filter(id__in=lead_ids)
        else:
            # Score all active leads
            leads = Lead.objects.filter(status__in=['new', 'contacted', 'qualified'])

        engine = LeadScoringEngine()
        engine.load_model()

        scored_count = 0
        for lead in leads:
            try:
                score = engine.score_lead(lead)
                lead.lead_score = score
                lead.save(update_fields=['lead_score', 'updated_at'])
                scored_count += 1
            except Exception as e:
                logger.error(f"Failed to score lead {lead.id}: {str(e)}")

        logger.info(f"Bulk scored {scored_count} leads")

        return {
            'success': True,
            'scored': scored_count,
            'total': leads.count()
        }

    except Exception as e:
        logger.error(f"Failed to bulk score leads: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@shared_task(bind=True, max_retries=3)
def execute_workflow(self, workflow_id, trigger_data=None):
    """
    Execute a workflow asynchronously
    """
    try:
        from core.models import Workflow
        from core.workflows import WorkflowEngine

        workflow = Workflow.objects.get(id=workflow_id)

        if not workflow.is_active:
            logger.warning(f"Workflow {workflow_id} is not active")
            return {'success': False, 'message': 'Workflow is not active'}

        success = WorkflowEngine.execute_workflow(workflow, trigger_data)

        return {
            'success': success,
            'workflow_id': workflow_id,
            'executed_at': timezone.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to execute workflow {workflow_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True)
def import_csv_data(self, resource_type, file_path, mapping, user_id):
    """
    Import CSV data in background
    """
    try:
        # Import logic here (similar to CSV import view)
        # This is a placeholder for the actual implementation

        logger.info(f"CSV import started for {resource_type}")

        return {
            'success': True,
            'resource_type': resource_type,
            'completed_at': timezone.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to import CSV: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
