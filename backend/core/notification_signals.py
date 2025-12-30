"""
Signal Handlers for Automatic Notifications
Automatically trigger notifications on model events
"""

import logging
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


# ==================== Deal/Opportunity Signals ====================

@receiver(post_save, sender='opportunity_management.Opportunity')
def opportunity_saved(sender, instance, created, **kwargs):
    """Handle opportunity save events"""
    from .notification_service import notification_service
    
    try:
        if created:
            # New deal assigned
            if instance.assigned_to and instance.assigned_to != instance.owner:
                notification_service.send(
                    user=instance.assigned_to,
                    notification_type='deal_assigned',
                    title=f'New Deal Assigned: {instance.name}',
                    message=f'You have been assigned to the deal "{instance.name}" worth ${instance.amount:,.2f}',
                    context={'deal': {
                        'name': instance.name,
                        'amount': instance.amount,
                        'stage': instance.stage,
                        'expected_close': instance.expected_close_date,
                    }},
                    action_url=f'{settings.FRONTEND_URL}/deals/{instance.id}',
                    priority='high',
                )
        else:
            # Check for stage change
            if hasattr(instance, '_previous_stage') and instance._previous_stage != instance.stage:
                # Deal stage changed
                if instance.owner:
                    notification_service.send(
                        user=instance.owner,
                        notification_type='deal_stage_change',
                        title=f'Deal Stage Updated: {instance.name}',
                        message=f'Deal moved from {instance._previous_stage} to {instance.stage}',
                        context={'deal': {
                            'name': instance.name,
                            'previous_stage': instance._previous_stage,
                            'new_stage': instance.stage,
                            'amount': instance.amount,
                            'probability': instance.probability,
                        }},
                        action_url=f'{settings.FRONTEND_URL}/deals/{instance.id}',
                    )
            
            # Check for deal won
            if hasattr(instance, '_previous_status') and instance._previous_status != 'won' and instance.status == 'won':
                # Notify team about deal won
                if instance.owner:
                    notification_service.send(
                        user=instance.owner,
                        notification_type='deal_won',
                        title=f'🎉 Deal Won: {instance.name}',
                        message=f'Congratulations! You closed a ${instance.amount:,.2f} deal!',
                        context={'deal': {
                            'name': instance.name,
                            'amount': instance.amount,
                            'contact_name': getattr(instance.contact, 'full_name', 'Unknown') if instance.contact else 'Unknown',
                            'company_name': getattr(instance.organization, 'name', 'Unknown') if instance.organization else 'Unknown',
                            'owner_name': instance.owner.get_full_name() or instance.owner.username,
                        }},
                        action_url=f'{settings.FRONTEND_URL}/deals/{instance.id}',
                        priority='high',
                    )
            
            # Check for deal lost
            if hasattr(instance, '_previous_status') and instance._previous_status != 'lost' and instance.status == 'lost':
                if instance.owner:
                    notification_service.send(
                        user=instance.owner,
                        notification_type='deal_lost',
                        title=f'Deal Lost: {instance.name}',
                        message=f'The deal "{instance.name}" has been marked as lost.',
                        context={'deal': {
                            'name': instance.name,
                            'amount': instance.amount,
                            'lost_reason': getattr(instance, 'lost_reason', None),
                            'contact_name': getattr(instance.contact, 'full_name', 'Unknown') if instance.contact else 'Unknown',
                        }},
                        action_url=f'{settings.FRONTEND_URL}/deals/{instance.id}',
                    )
    except Exception as e:
        logger.error(f"Error in opportunity_saved signal: {e}")


@receiver(pre_save, sender='opportunity_management.Opportunity')
def opportunity_pre_save(sender, instance, **kwargs):
    """Track previous values before save"""
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._previous_stage = old_instance.stage
            instance._previous_status = old_instance.status
        except sender.DoesNotExist:
            pass


# ==================== Task Signals ====================

@receiver(post_save, sender='task_management.Task')
def task_saved(sender, instance, created, **kwargs):
    """Handle task save events"""
    from .notification_service import notification_service
    
    try:
        if created:
            # New task assigned
            if instance.assigned_to and instance.assigned_to != instance.created_by:
                notification_service.send(
                    user=instance.assigned_to,
                    notification_type='task_assigned',
                    title=f'New Task Assigned: {instance.title}',
                    message=f'You have been assigned a new task by {instance.created_by.get_full_name() or instance.created_by.username}',
                    context={
                        'task': {
                            'title': instance.title,
                            'due_date': instance.due_date,
                            'priority': instance.priority,
                            'description': instance.description,
                        },
                        'assigned_by': instance.created_by.get_full_name() or instance.created_by.username,
                    },
                    action_url=f'{settings.FRONTEND_URL}/tasks/{instance.id}',
                    priority='high' if instance.priority == 'high' else 'medium',
                )
    except Exception as e:
        logger.error(f"Error in task_saved signal: {e}")


# ==================== Contact Signals ====================

@receiver(post_save, sender='contact_management.Contact')
def contact_saved(sender, instance, created, **kwargs):
    """Handle contact save events"""
    try:
        if created:
            # Log new contact creation for activity feed
            from .models import Notification
            
            if instance.owner:
                # Could send team notification for high-value leads
                pass
    except Exception as e:
        logger.error(f"Error in contact_saved signal: {e}")


# ==================== Comment/Activity Signals ====================

@receiver(post_save, sender='activity_feed.Comment')
def comment_created(sender, instance, created, **kwargs):
    """Handle new comments"""
    from .notification_service import notification_service
    
    try:
        if created:
            # Find users mentioned in the comment
            import re
            mentions = re.findall(r'@(\w+)', instance.content)
            
            for username in mentions:
                try:
                    mentioned_user = User.objects.get(username=username)
                    if mentioned_user != instance.author:
                        notification_service.send(
                            user=mentioned_user,
                            notification_type='mention',
                            title=f'{instance.author.get_full_name() or instance.author.username} mentioned you',
                            message=instance.content[:200],
                            context={
                                'mentioned_by': instance.author.get_full_name() or instance.author.username,
                                'message': instance.content,
                                'context_type': 'comment',
                                'timestamp': instance.created_at,
                            },
                            action_url=f'{settings.FRONTEND_URL}/activity/{instance.id}',
                            priority='high',
                        )
                except User.DoesNotExist:
                    pass
            
            # Notify content owner about the comment
            content_owner = getattr(instance.content_object, 'owner', None)
            if content_owner and content_owner != instance.author:
                notification_service.send(
                    user=content_owner,
                    notification_type='comment',
                    title='New Comment',
                    message=f'{instance.author.get_full_name() or instance.author.username} commented on your item',
                    context={
                        'commenter': instance.author.get_full_name() or instance.author.username,
                        'comment': instance.content[:200],
                        'timestamp': instance.created_at,
                    },
                    action_url=f'{settings.FRONTEND_URL}/activity/{instance.id}',
                )
    except Exception as e:
        logger.error(f"Error in comment_created signal: {e}")


# ==================== User Signals ====================

@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    """Handle new user creation"""
    from .settings_models import UserPreference, NotificationPreference, UserRole, UserRoleAssignment
    
    try:
        if created:
            # Create default preferences
            UserPreference.objects.get_or_create(user=instance)
            NotificationPreference.objects.get_or_create(user=instance)
            
            # Assign default role
            try:
                default_role = UserRole.objects.get(name='sales_rep')
                UserRoleAssignment.objects.get_or_create(
                    user=instance,
                    role=default_role,
                )
            except UserRole.DoesNotExist:
                pass
            
            logger.info(f"Created default preferences for new user: {instance.username}")
    except Exception as e:
        logger.error(f"Error in user_created signal: {e}")


# ==================== Export Signals ====================

@receiver(post_save, sender='core.ExportJob')
def export_job_updated(sender, instance, **kwargs):
    """Handle export job updates"""
    from .notification_service import notification_service
    
    try:
        if instance.status == 'completed':
            notification_service.send(
                user=instance.user,
                notification_type='export_ready',
                title='Your Export is Ready',
                message=f'Your {instance.format.upper()} export has been completed.',
                context={
                    'export': {
                        'format': instance.format,
                        'entities': instance.entities,
                        'file_size': f"{instance.file_size / 1024:.1f} KB" if instance.file_size else "Unknown",
                        'expires_at': instance.expires_at,
                    },
                    'download_url': f'{settings.FRONTEND_URL}/settings/export?download={instance.id}',
                },
                action_url=f'{settings.FRONTEND_URL}/settings/export?download={instance.id}',
                priority='medium',
            )
        elif instance.status == 'failed':
            notification_service.send(
                user=instance.user,
                notification_type='system_updates',
                title='Export Failed',
                message=f'Your export failed: {instance.error_message}',
                action_url=f'{settings.FRONTEND_URL}/settings/export',
                priority='medium',
            )
    except Exception as e:
        logger.error(f"Error in export_job_updated signal: {e}")


# ==================== Security Signals ====================

@receiver(post_save, sender='core.AuditLog')
def security_event(sender, instance, created, **kwargs):
    """Handle security-related audit events"""
    from .notification_service import notification_service
    
    try:
        if created and instance.risk_level in ['high', 'critical']:
            if instance.user:
                notification_service.send(
                    user=instance.user,
                    notification_type='security_alert',
                    title='Security Alert',
                    message=f'A {instance.risk_level}-risk action was detected on your account: {instance.action}',
                    context={
                        'alert_type': instance.action,
                        'timestamp': instance.timestamp,
                        'ip_address': instance.ip_address,
                        'location': instance.metadata.get('location'),
                        'device': instance.metadata.get('device'),
                    },
                    action_url=f'{settings.FRONTEND_URL}/settings/security',
                    priority='high',
                )
    except Exception as e:
        logger.error(f"Error in security_event signal: {e}")


# ==================== Role Assignment Signals ====================

@receiver(post_save, sender='core.UserRoleAssignment')
def role_assigned(sender, instance, created, **kwargs):
    """Notify user when role is assigned"""
    from .notification_service import notification_service
    from .rbac_middleware import invalidate_user_permissions
    
    try:
        # Invalidate permission cache
        invalidate_user_permissions(instance.user.id)
        
        if created:
            notification_service.send(
                user=instance.user,
                notification_type='system_updates',
                title='Role Updated',
                message=f'You have been assigned the {instance.role.display_name} role.',
                action_url=f'{settings.FRONTEND_URL}/settings/profile',
            )
    except Exception as e:
        logger.error(f"Error in role_assigned signal: {e}")


@receiver(post_delete, sender='core.UserRoleAssignment')
def role_removed(sender, instance, **kwargs):
    """Handle role removal"""
    from .rbac_middleware import invalidate_user_permissions
    
    try:
        invalidate_user_permissions(instance.user.id)
    except Exception as e:
        logger.error(f"Error in role_removed signal: {e}")
