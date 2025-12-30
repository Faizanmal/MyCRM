"""
Celery Tasks for Notifications and Background Jobs
"""

from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


# ==================== Notification Tasks ====================

@shared_task
def send_notification_task(user_id, notification_type, title, message, context=None, action_url=None, priority='medium'):
    """
    Async task to send a notification
    """
    from .notification_service import notification_service
    
    try:
        user = User.objects.get(id=user_id)
        result = notification_service.send(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            context=context or {},
            action_url=action_url,
            priority=priority,
        )
        logger.info(f"Notification sent to {user.username}: {result}")
        return result
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for notification")
        return None


@shared_task
def send_bulk_notification_task(user_ids, notification_type, title, message, context=None, action_url=None):
    """
    Send notification to multiple users
    """
    from .notification_service import notification_service
    
    users = User.objects.filter(id__in=user_ids)
    results = notification_service.send_to_many(
        users=list(users),
        notification_type=notification_type,
        title=title,
        message=message,
        context=context or {},
        action_url=action_url,
    )
    logger.info(f"Bulk notification sent to {len(results)} users")
    return results


# ==================== Digest Tasks ====================

@shared_task
def send_daily_digests():
    """
    Send daily digest emails to all subscribed users
    Should be scheduled to run daily (e.g., 9:00 AM)
    """
    from .settings_models import NotificationPreference
    from .notification_service import digest_service
    
    logger.info("Starting daily digest task")
    
    # Get all users with daily digest enabled
    prefs = NotificationPreference.objects.filter(
        digest_enabled=True,
        digest_frequency='daily'
    ).select_related('user')
    
    sent_count = 0
    failed_count = 0
    
    for pref in prefs:
        try:
            # Check if it's the right time for this user
            # In production, you'd want to respect user's timezone
            current_hour = timezone.localtime().hour
            digest_hour = pref.digest_time.hour
            
            if current_hour == digest_hour:
                if digest_service.send_daily_digest(pref.user):
                    sent_count += 1
                else:
                    failed_count += 1
        except Exception as e:
            logger.error(f"Failed to send digest to {pref.user.username}: {e}")
            failed_count += 1
    
    logger.info(f"Daily digests completed: {sent_count} sent, {failed_count} failed")
    return {'sent': sent_count, 'failed': failed_count}


@shared_task
def send_weekly_digests():
    """
    Send weekly digest emails to all subscribed users
    Should be scheduled to run weekly (e.g., Monday 9:00 AM)
    """
    from .settings_models import NotificationPreference
    from .notification_service import digest_service
    
    logger.info("Starting weekly digest task")
    
    prefs = NotificationPreference.objects.filter(
        digest_enabled=True,
        digest_frequency='weekly'
    ).select_related('user')
    
    sent_count = 0
    failed_count = 0
    
    for pref in prefs:
        try:
            if digest_service.send_weekly_digest(pref.user):
                sent_count += 1
            else:
                failed_count += 1
        except Exception as e:
            logger.error(f"Failed to send weekly digest to {pref.user.username}: {e}")
            failed_count += 1
    
    logger.info(f"Weekly digests completed: {sent_count} sent, {failed_count} failed")
    return {'sent': sent_count, 'failed': failed_count}


# ==================== Task Reminder Tasks ====================

@shared_task
def check_overdue_tasks():
    """
    Check for overdue tasks and send notifications
    Should be scheduled to run periodically (e.g., every hour)
    """
    from .notification_service import notification_service
    
    logger.info("Checking for overdue tasks")
    
    try:
        from task_management.models import Task
        
        # Find tasks that became overdue since last check
        now = timezone.now()
        one_hour_ago = now - timedelta(hours=1)
        
        overdue_tasks = Task.objects.filter(
            status__in=['pending', 'in_progress'],
            due_date__lt=now,
            due_date__gte=one_hour_ago,
            notified_overdue=False,  # Assuming this field exists
        ).select_related('assigned_to')
        
        notified_count = 0
        
        for task in overdue_tasks:
            if task.assigned_to:
                notification_service.send(
                    user=task.assigned_to,
                    notification_type='task_overdue',
                    title=f'Task Overdue: {task.title}',
                    message=f'Your task "{task.title}" is now overdue.',
                    context={
                        'task': {
                            'title': task.title,
                            'due_date': task.due_date,
                            'days_overdue': 0,
                            'priority': task.priority,
                        }
                    },
                    action_url=f'/tasks/{task.id}',
                    priority='high',
                )
                task.notified_overdue = True
                task.save(update_fields=['notified_overdue'])
                notified_count += 1
        
        logger.info(f"Sent {notified_count} overdue task notifications")
        return {'notified': notified_count}
        
    except ImportError:
        logger.warning("Task model not available")
        return {'notified': 0}


@shared_task
def check_due_soon_tasks():
    """
    Check for tasks due soon and send reminders
    Should be scheduled to run periodically (e.g., every 30 minutes)
    """
    from .notification_service import notification_service
    
    logger.info("Checking for tasks due soon")
    
    try:
        from task_management.models import Task
        
        now = timezone.now()
        soon = now + timedelta(hours=24)
        
        # Tasks due in next 24 hours that haven't been reminded
        upcoming_tasks = Task.objects.filter(
            status__in=['pending', 'in_progress'],
            due_date__gt=now,
            due_date__lte=soon,
            notified_due_soon=False,
        ).select_related('assigned_to')
        
        notified_count = 0
        
        for task in upcoming_tasks:
            if task.assigned_to:
                time_until = task.due_date - now
                hours_until = int(time_until.total_seconds() / 3600)
                
                notification_service.send(
                    user=task.assigned_to,
                    notification_type='task_due_soon',
                    title=f'Task Due Soon: {task.title}',
                    message=f'Your task is due in {hours_until} hours.',
                    context={
                        'task': {
                            'title': task.title,
                            'due_date': task.due_date,
                            'time_until_due': f'{hours_until} hours',
                            'priority': task.priority,
                            'description': task.description,
                        }
                    },
                    action_url=f'/tasks/{task.id}',
                    priority='medium',
                )
                task.notified_due_soon = True
                task.save(update_fields=['notified_due_soon'])
                notified_count += 1
        
        logger.info(f"Sent {notified_count} due soon task reminders")
        return {'notified': notified_count}
        
    except ImportError:
        logger.warning("Task model not available")
        return {'notified': 0}


# ==================== Deal Follow-up Tasks ====================

@shared_task
def check_stale_deals():
    """
    Check for deals that haven't been updated in a while
    """
    from .notification_service import notification_service
    
    logger.info("Checking for stale deals")
    
    try:
        from opportunity_management.models import Opportunity
        
        stale_threshold = timezone.now() - timedelta(days=7)
        
        stale_deals = Opportunity.objects.filter(
            status='open',
            updated_at__lt=stale_threshold,
        ).select_related('owner')
        
        notified_count = 0
        
        for deal in stale_deals:
            if deal.owner:
                days_stale = (timezone.now() - deal.updated_at).days
                
                notification_service.send(
                    user=deal.owner,
                    notification_type='ai_recommendations',
                    title=f'Follow Up Needed: {deal.name}',
                    message=f'This deal hasn\'t been updated in {days_stale} days. Consider reaching out.',
                    context={
                        'recommendation': {
                            'title': f'Follow up on {deal.name}',
                            'description': f'This deal has been stale for {days_stale} days.',
                            'priority': 'medium',
                            'impact': 'Prevent deal from going cold',
                        }
                    },
                    action_url=f'/deals/{deal.id}',
                )
                notified_count += 1
        
        logger.info(f"Sent {notified_count} stale deal reminders")
        return {'notified': notified_count}
        
    except ImportError:
        logger.warning("Opportunity model not available")
        return {'notified': 0}


# ==================== Cleanup Tasks ====================

@shared_task
def cleanup_old_notifications():
    """
    Delete old read notifications
    Should be scheduled to run daily
    """
    from .models import Notification
    
    cutoff = timezone.now() - timedelta(days=90)
    
    deleted, _ = Notification.objects.filter(
        is_read=True,
        created_at__lt=cutoff
    ).delete()
    
    logger.info(f"Cleaned up {deleted} old notifications")
    return {'deleted': deleted}


@shared_task
def cleanup_expired_exports():
    """
    Delete expired export files
    Should be scheduled to run daily
    """
    from .settings_models import ExportJob
    from django.core.files.storage import default_storage
    
    expired_jobs = ExportJob.objects.filter(
        expires_at__lt=timezone.now(),
        file_path__isnull=False
    )
    
    deleted_count = 0
    
    for job in expired_jobs:
        try:
            if job.file_path and default_storage.exists(job.file_path):
                default_storage.delete(job.file_path)
                deleted_count += 1
            
            job.file_path = None
            job.save(update_fields=['file_path'])
        except Exception as e:
            logger.error(f"Failed to delete export {job.id}: {e}")
    
    logger.info(f"Cleaned up {deleted_count} expired exports")
    return {'deleted': deleted_count}


@shared_task
def cleanup_old_audit_logs():
    """
    Archive or delete old audit logs
    Should be scheduled to run weekly
    """
    from .models import AuditLog
    
    # Keep audit logs for 1 year
    cutoff = timezone.now() - timedelta(days=365)
    
    # For low-risk logs, delete older ones
    deleted, _ = AuditLog.objects.filter(
        risk_level='low',
        timestamp__lt=cutoff
    ).delete()
    
    logger.info(f"Cleaned up {deleted} old audit logs")
    return {'deleted': deleted}


# ==================== Analytics Tasks ====================

@shared_task
def calculate_daily_metrics():
    """
    Calculate and cache daily metrics for all users
    Should be scheduled to run daily at midnight
    """
    from django.core.cache import cache
    
    logger.info("Calculating daily metrics")
    
    users = User.objects.filter(is_active=True)
    
    for user in users:
        try:
            # Calculate metrics for this user
            metrics = _calculate_user_metrics(user)
            
            # Cache for 24 hours
            cache_key = f"user_daily_metrics_{user.id}_{timezone.now().date()}"
            cache.set(cache_key, metrics, 86400)
            
        except Exception as e:
            logger.error(f"Failed to calculate metrics for {user.username}: {e}")
    
    logger.info(f"Calculated metrics for {users.count()} users")
    return {'users_processed': users.count()}


def _calculate_user_metrics(user):
    """Calculate metrics for a user"""
    today = timezone.now().date()
    
    try:
        from opportunity_management.models import Opportunity
        from task_management.models import Task
        
        deals_today = Opportunity.objects.filter(
            owner=user,
            status='won',
            closed_at__date=today
        ).count()
        
        tasks_completed = Task.objects.filter(
            assigned_to=user,
            status='completed',
            completed_at__date=today
        ).count()
        
        return {
            'deals_closed': deals_today,
            'tasks_completed': tasks_completed,
            'date': str(today),
        }
    except ImportError:
        return {'date': str(today)}


# ==================== AI Recommendation Tasks ====================

@shared_task
def generate_ai_recommendations():
    """
    Generate AI recommendations for all users
    Should be scheduled to run daily
    """
    from .ai_recommendation_service import RecommendationEngine
    
    logger.info("Generating AI recommendations")
    
    users = User.objects.filter(is_active=True)
    
    for user in users:
        try:
            engine = RecommendationEngine(user)
            recommendations = engine.generate_all()
            
            # Store recommendations in cache or database
            # ...
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations for {user.username}: {e}")
    
    logger.info(f"Generated recommendations for {users.count()} users")
    return {'users_processed': users.count()}
