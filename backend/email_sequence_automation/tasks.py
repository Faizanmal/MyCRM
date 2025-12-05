"""
Celery tasks for Email Sequence Automation
Handles background processing of sequences, analytics, and triggers
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def process_sequence_actions():
    """Process all due sequence actions - run every minute"""
    from .services import SequenceExecutionService
    
    service = SequenceExecutionService()
    results = service.process_due_actions()
    
    logger.info(f"Processed sequence actions: {results}")
    return results


@shared_task
def evaluate_ab_tests():
    """Evaluate all running A/B tests - run every hour"""
    from .models import ABTest
    from .services import ABTestingService
    
    service = ABTestingService()
    
    running_tests = ABTest.objects.filter(status='running')
    evaluated = 0
    winners_selected = 0
    
    for test in running_tests:
        try:
            result = service.evaluate_test(test)
            evaluated += 1
            if result.get('ready_to_declare'):
                winners_selected += 1
        except Exception as e:
            logger.error(f"Error evaluating A/B test {test.id}: {e}")
    
    return {'evaluated': evaluated, 'winners_selected': winners_selected}


@shared_task
def record_daily_analytics():
    """Record daily analytics for all active sequences - run daily"""
    from .models import EmailSequence
    from .services import AnalyticsService
    
    service = AnalyticsService()
    
    active_sequences = EmailSequence.objects.filter(status='active')
    recorded = 0
    
    for sequence in active_sequences:
        try:
            service.record_daily_analytics(str(sequence.id))
            recorded += 1
        except Exception as e:
            logger.error(f"Error recording analytics for sequence {sequence.id}: {e}")
    
    return {'recorded': recorded}


@shared_task
def check_inactivity_triggers():
    """Check for inactivity-based triggers - run daily"""
    from .models import AutomatedTrigger
    from .services import TriggerEvaluationService
    from contact_management.models import Contact
    from django.db.models import Max
    
    service = TriggerEvaluationService()
    
    # Get all active inactivity triggers
    triggers = AutomatedTrigger.objects.filter(
        trigger_type='inactivity',
        is_active=True
    )
    
    enrolled = 0
    
    for trigger in triggers:
        days = trigger.trigger_config.get('days', 7)
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Find contacts without recent activity
        inactive_contacts = Contact.objects.annotate(
            last_activity=Max('activities__created_at')
        ).filter(
            last_activity__lt=cutoff_date
        ).values_list('id', flat=True)
        
        for contact_id in inactive_contacts:
            try:
                sequences = service.evaluate_triggers('inactivity', {
                    'contact_id': contact_id,
                    'last_activity_at': cutoff_date
                })
                enrolled += len(sequences)
            except Exception as e:
                logger.error(f"Error processing inactivity trigger for contact {contact_id}: {e}")
    
    return {'enrolled': enrolled}


@shared_task
def cleanup_completed_enrollments():
    """Archive old completed enrollments - run weekly"""
    from .models import SequenceEnrollment, SequenceActivity
    
    # Archive enrollments completed more than 90 days ago
    cutoff_date = timezone.now() - timedelta(days=90)
    
    old_enrollments = SequenceEnrollment.objects.filter(
        status__in=['completed', 'exited', 'converted'],
        completed_at__lt=cutoff_date
    )
    
    # Archive activities for old enrollments
    activities_deleted = SequenceActivity.objects.filter(
        enrollment__in=old_enrollments,
        timestamp__lt=cutoff_date
    ).delete()[0]
    
    return {'activities_archived': activities_deleted}


@shared_task
def update_sequence_stats():
    """Update sequence aggregate statistics - run hourly"""
    from .models import EmailSequence, SequenceEmail
    from django.db.models import Avg
    
    sequences = EmailSequence.objects.filter(status='active')
    updated = 0
    
    for sequence in sequences:
        emails = SequenceEmail.objects.filter(step__sequence=sequence, total_sent__gt=0)
        
        if emails.exists():
            avg_stats = emails.aggregate(
                avg_open=Avg('total_opened') * 100 / Avg('total_sent'),
                avg_click=Avg('total_clicked') * 100 / Avg('total_sent'),
                avg_reply=Avg('total_replied') * 100 / Avg('total_sent')
            )
            
            sequence.avg_open_rate = avg_stats.get('avg_open', 0) or 0
            sequence.avg_click_rate = avg_stats.get('avg_click', 0) or 0
            sequence.avg_reply_rate = avg_stats.get('avg_reply', 0) or 0
            sequence.save(update_fields=['avg_open_rate', 'avg_click_rate', 'avg_reply_rate'])
            updated += 1
    
    return {'updated': updated}


@shared_task
def send_scheduled_sequence_email(enrollment_id: str, email_id: str):
    """Send a specific scheduled email for an enrollment"""
    from .models import SequenceEnrollment, SequenceEmail
    from .services import SequenceExecutionService
    
    try:
        enrollment = SequenceEnrollment.objects.get(id=enrollment_id)
        email = SequenceEmail.objects.get(id=email_id)
        
        if enrollment.status != 'active':
            return {'status': 'skipped', 'reason': 'enrollment not active'}
        
        service = SequenceExecutionService()
        result = service._process_email_step(enrollment, email.step)
        
        return {'status': 'sent' if result.get('email_sent') else 'failed'}
        
    except (SequenceEnrollment.DoesNotExist, SequenceEmail.DoesNotExist) as e:
        logger.error(f"Error sending scheduled email: {e}")
        return {'status': 'error', 'error': str(e)}
