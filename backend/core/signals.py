"""
Django signals for enterprise features
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import SystemHealth
from .security import SecurityAuditLog

User = get_user_model()


@receiver(post_save, sender=User)
def user_created_or_updated(sender, instance, created, **kwargs):
    """Log user creation or updates"""
    action = 'user_created' if created else 'user_updated'
    
    SecurityAuditLog.log_event(
        user=instance if not created else None,
        action=action,
        resource=f'user:{instance.id}',
        metadata={
            'username': instance.username,
            'email': instance.email,
            'role': getattr(instance, 'role', 'unknown'),
            'is_active': instance.is_active
        },
        risk_level='medium' if action == 'user_created' else 'low'
    )


@receiver(post_delete)
def model_deleted(sender, instance, **kwargs):
    """Log model deletions"""
    # Only log for important models
    important_models = [
        'Contact', 'Lead', 'Opportunity', 'Task', 'User'
    ]
    
    if sender.__name__ in important_models:
        SecurityAuditLog.log_event(
            user=getattr(instance, 'deleted_by', None),
            action=f'{sender.__name__.lower()}_deleted',
            resource=f'{sender.__name__.lower()}:{instance.id}',
            metadata={'model': sender.__name__},
            risk_level='medium'
        )


@receiver(pre_save)
def model_updated(sender, instance, **kwargs):
    """Log important model updates"""
    # Only log for important models and if instance already exists
    important_models = [
        'Contact', 'Lead', 'Opportunity', 'Task'
    ]
    
    if sender.__name__ in important_models and instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            
            # Check for significant changes
            significant_fields = getattr(sender, 'AUDIT_FIELDS', [])
            if significant_fields:
                changes = {}
                for field in significant_fields:
                    old_value = getattr(old_instance, field, None)
                    new_value = getattr(instance, field, None)
                    if old_value != new_value:
                        changes[field] = {
                            'old': str(old_value),
                            'new': str(new_value)
                        }
                
                if changes:
                    SecurityAuditLog.log_event(
                        user=getattr(instance, 'updated_by', None),
                        action=f'{sender.__name__.lower()}_updated',
                        resource=f'{sender.__name__.lower()}:{instance.id}',
                        metadata={'changes': changes},
                        risk_level='low'
                    )
        except sender.DoesNotExist:
            pass  # New instance, will be logged by post_save


def schedule_health_checks():
    """Schedule periodic system health checks"""
    from django.core.management import call_command
    
    # This would typically be called by a task scheduler like Celery
    try:
        call_command('check_system_health')
    except Exception as e:
        # Log health check failure
        SystemHealth.objects.create(
            component='system',
            status='critical',
            error_message=str(e),
            checked_at=timezone.now()
        )