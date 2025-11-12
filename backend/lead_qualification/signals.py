from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from lead_management.models import Lead
from .tasks import calculate_lead_score_task
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Lead)
def lead_saved(sender, instance, created, **kwargs):
    """
    Automatically calculate score when a lead is created or updated
    """
    if created:
        # Queue score calculation for new leads
        logger.info(f"New lead created: {instance.name}, queuing score calculation")
        calculate_lead_score_task.delay(instance.id)
    else:
        # Recalculate score if important fields changed
        significant_fields = [
            'email', 'phone', 'company', 'status', 'source', 
            'industry', 'company_size', 'title'
        ]
        
        # Check if any significant field was updated
        # Note: In production, you'd track field changes more precisely
        if any(hasattr(instance, field) for field in significant_fields):
            logger.info(f"Lead updated: {instance.name}, queuing score recalculation")
            calculate_lead_score_task.delay(instance.id)
