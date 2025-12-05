"""
Smart Scheduling AI Celery Tasks
Background tasks for AI scheduling features
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(name='smart_scheduling.predict_no_shows_for_upcoming')
def predict_no_shows_for_upcoming():
    """Predict no-shows for all upcoming meetings in the next 48 hours"""
    from .models import Meeting
    from .ai_services import AISchedulingService
    
    cutoff = timezone.now() + timedelta(hours=48)
    
    meetings = Meeting.objects.filter(
        start_time__gt=timezone.now(),
        start_time__lte=cutoff,
        status='confirmed'
    ).select_related('host')
    
    predictions_created = 0
    
    for meeting in meetings:
        try:
            service = AISchedulingService(meeting.host)
            service.predict_no_show(str(meeting.id))
            predictions_created += 1
        except Exception as e:
            logger.error(f"Error predicting no-show for meeting {meeting.id}: {e}")
    
    logger.info(f"Created {predictions_created} no-show predictions")
    return {'predictions_created': predictions_created}


@shared_task(name='smart_scheduling.generate_meeting_preps')
def generate_meeting_preps():
    """Generate AI meeting prep for meetings in the next 24 hours"""
    from .models import Meeting
    from .ai_models import MeetingPrepAI
    from .ai_services import AISchedulingService
    
    cutoff = timezone.now() + timedelta(hours=24)
    
    # Get meetings without prep materials
    meetings_with_prep = MeetingPrepAI.objects.values_list('meeting_id', flat=True)
    
    meetings = Meeting.objects.filter(
        start_time__gt=timezone.now(),
        start_time__lte=cutoff,
        status='confirmed'
    ).exclude(id__in=meetings_with_prep).select_related('host')
    
    preps_generated = 0
    
    for meeting in meetings:
        try:
            service = AISchedulingService(meeting.host)
            service.generate_meeting_prep(str(meeting.id))
            preps_generated += 1
        except Exception as e:
            logger.error(f"Error generating prep for meeting {meeting.id}: {e}")
    
    logger.info(f"Generated {preps_generated} meeting preps")
    return {'preps_generated': preps_generated}


@shared_task(name='smart_scheduling.send_smart_reminders')
def send_smart_reminders():
    """Send due smart reminders"""
    from .ai_models import SmartReminder
    from django.core.mail import send_mail
    from django.conf import settings
    
    now = timezone.now()
    buffer = timedelta(minutes=5)
    
    # Get reminders due within the next 5 minutes
    due_reminders = SmartReminder.objects.filter(
        sent=False,
        scheduled_at__lte=now + buffer,
        scheduled_at__gte=now - buffer
    ).select_related('meeting', 'meeting__meeting_type')
    
    reminders_sent = 0
    
    for reminder in due_reminders:
        try:
            # Send based on channel
            if reminder.optimal_channel == 'email':
                send_mail(
                    subject=reminder.subject,
                    message=reminder.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[reminder.recipient_email],
                    fail_silently=False
                )
            
            # Mark as sent
            reminder.sent = True
            reminder.sent_at = timezone.now()
            reminder.delivery_status = 'sent'
            reminder.save()
            
            reminders_sent += 1
            
        except Exception as e:
            logger.error(f"Error sending reminder {reminder.id}: {e}")
            reminder.delivery_status = f'failed: {str(e)}'
            reminder.save()
    
    logger.info(f"Sent {reminders_sent} smart reminders")
    return {'reminders_sent': reminders_sent}


@shared_task(name='smart_scheduling.setup_reminders_for_new_meetings')
def setup_reminders_for_new_meetings():
    """Setup smart reminders for newly confirmed meetings"""
    from .models import Meeting
    from .ai_models import SmartReminder
    from .ai_services import AISchedulingService
    
    # Get confirmed meetings in future without reminders
    meetings_with_reminders = SmartReminder.objects.values_list('meeting_id', flat=True)
    
    meetings = Meeting.objects.filter(
        status='confirmed',
        start_time__gt=timezone.now()
    ).exclude(id__in=meetings_with_reminders).select_related('host')
    
    reminders_setup = 0
    
    for meeting in meetings:
        try:
            service = AISchedulingService(meeting.host)
            service.setup_smart_reminders(str(meeting.id))
            reminders_setup += 1
        except Exception as e:
            logger.error(f"Error setting up reminders for meeting {meeting.id}: {e}")
    
    logger.info(f"Setup reminders for {reminders_setup} meetings")
    return {'reminders_setup': reminders_setup}


@shared_task(name='smart_scheduling.detect_schedule_conflicts')
def detect_schedule_conflicts():
    """Detect and suggest reschedules for conflicting meetings"""
    from .models import Meeting
    from .ai_models import SmartReschedule
    from .ai_services import AISchedulingService
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    conflicts_detected = 0
    
    # Get all users with upcoming meetings
    users_with_meetings = User.objects.filter(
        hosted_meetings__start_time__gt=timezone.now(),
        hosted_meetings__status='confirmed'
    ).distinct()
    
    for user in users_with_meetings:
        # Get upcoming meetings ordered by time
        meetings = list(Meeting.objects.filter(
            host=user,
            start_time__gt=timezone.now(),
            status='confirmed'
        ).order_by('start_time'))
        
        # Check for overlaps
        for i in range(len(meetings) - 1):
            current = meetings[i]
            next_meeting = meetings[i + 1]
            
            # Check if meetings overlap
            if current.end_time > next_meeting.start_time:
                # Check if we already have a reschedule suggestion
                existing = SmartReschedule.objects.filter(
                    meeting=next_meeting,
                    trigger_type='conflict',
                    status='pending'
                ).exists()
                
                if not existing:
                    try:
                        service = AISchedulingService(user)
                        service.suggest_reschedule(
                            meeting_id=str(next_meeting.id),
                            trigger_type='conflict',
                            trigger_reason=f'Conflicts with {current.meeting_type.name}'
                        )
                        conflicts_detected += 1
                    except Exception as e:
                        logger.error(f"Error creating reschedule for {next_meeting.id}: {e}")
    
    logger.info(f"Detected {conflicts_detected} schedule conflicts")
    return {'conflicts_detected': conflicts_detected}


@shared_task(name='smart_scheduling.learn_user_preferences')
def learn_user_preferences():
    """Learn scheduling preferences for all active users"""
    from django.contrib.auth import get_user_model
    from .models import Meeting
    from .ai_services import AISchedulingService
    
    User = get_user_model()
    
    # Get users with at least 10 completed meetings
    ninety_days_ago = timezone.now() - timedelta(days=90)
    
    users = User.objects.filter(
        hosted_meetings__status='completed',
        hosted_meetings__start_time__gte=ninety_days_ago
    ).annotate(
        meeting_count=models.Count('hosted_meetings')
    ).filter(meeting_count__gte=10)
    
    preferences_updated = 0
    
    for user in users:
        try:
            service = AISchedulingService(user)
            service.learn_preferences()
            preferences_updated += 1
        except Exception as e:
            logger.error(f"Error learning preferences for user {user.id}: {e}")
    
    logger.info(f"Updated preferences for {preferences_updated} users")
    return {'preferences_updated': preferences_updated}


@shared_task(name='smart_scheduling.update_attendee_intelligence')
def update_attendee_intelligence():
    """Update attendee intelligence based on recent meeting outcomes"""
    from .models import Meeting
    from .ai_services import AttendeeIntelligenceService
    
    # Get recently completed/no-show meetings from last 24 hours
    yesterday = timezone.now() - timedelta(hours=24)
    
    meetings = Meeting.objects.filter(
        status__in=['completed', 'no_show'],
        updated_at__gte=yesterday
    )
    
    updated = 0
    
    for meeting in meetings:
        try:
            AttendeeIntelligenceService.update_attendee_intelligence(
                email=meeting.guest_email,
                meeting_outcome=meeting.status
            )
            updated += 1
        except Exception as e:
            logger.error(f"Error updating intelligence for {meeting.guest_email}: {e}")
    
    logger.info(f"Updated intelligence for {updated} attendees")
    return {'updated': updated}


@shared_task(name='smart_scheduling.generate_optimization_suggestions')
def generate_optimization_suggestions():
    """Generate weekly schedule optimization suggestions"""
    from django.contrib.auth import get_user_model
    from .models import Meeting
    from .ai_services import AISchedulingService
    
    User = get_user_model()
    
    # Get active users
    users = User.objects.filter(
        is_active=True,
        hosted_meetings__start_time__gte=timezone.now() - timedelta(days=7)
    ).distinct()
    
    suggestions_created = 0
    
    # Next week's date range
    start_date = timezone.now()
    end_date = start_date + timedelta(days=7)
    
    for user in users:
        try:
            service = AISchedulingService(user)
            
            # Generate focus time optimization
            service.optimize_schedule(
                start_date=start_date,
                end_date=end_date,
                optimization_type='create_focus_time'
            )
            suggestions_created += 1
            
        except Exception as e:
            logger.error(f"Error generating optimization for user {user.id}: {e}")
    
    logger.info(f"Created optimization suggestions for {suggestions_created} users")
    return {'suggestions_created': suggestions_created}


@shared_task(name='smart_scheduling.expire_old_suggestions')
def expire_old_suggestions():
    """Expire old reschedule and time suggestions"""
    from .ai_models import SmartReschedule, AITimeSuggestion
    
    now = timezone.now()
    
    # Expire reschedule suggestions
    expired_reschedules = SmartReschedule.objects.filter(
        status='pending',
        expires_at__lt=now
    ).update(status='expired')
    
    # Delete expired time suggestions
    expired_suggestions = AITimeSuggestion.objects.filter(
        expires_at__lt=now
    ).delete()
    
    logger.info(f"Expired {expired_reschedules} reschedules and {expired_suggestions[0]} time suggestions")
    return {
        'expired_reschedules': expired_reschedules,
        'expired_suggestions': expired_suggestions[0]
    }


@shared_task(name='smart_scheduling.flag_high_risk_meetings')
def flag_high_risk_meetings():
    """Flag meetings with high no-show risk for extra attention"""
    from .ai_models import NoShowPrediction
    from .ai_services import AISchedulingService
    
    # Get high-risk predictions for meetings in next 48 hours
    cutoff = timezone.now() + timedelta(hours=48)
    
    high_risk = NoShowPrediction.objects.filter(
        risk_score__gt=60,
        meeting__start_time__gt=timezone.now(),
        meeting__start_time__lte=cutoff,
        meeting__status='confirmed',
        extra_reminder_suggested=True
    ).select_related('meeting', 'meeting__host')
    
    extra_reminders_created = 0
    
    for prediction in high_risk:
        meeting = prediction.meeting
        
        try:
            # Setup additional reminder if not already done
            service = AISchedulingService(meeting.host)
            service.setup_smart_reminders(str(meeting.id))
            extra_reminders_created += 1
        except Exception as e:
            logger.error(f"Error creating extra reminder for {meeting.id}: {e}")
    
    logger.info(f"Created {extra_reminders_created} extra reminders for high-risk meetings")
    return {'extra_reminders_created': extra_reminders_created}


# Import models at task level to avoid circular imports
from django.db import models
