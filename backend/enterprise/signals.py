"""
Security Signals for automatic audit logging
"""

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .services import SecurityService


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful login"""
    SecurityService.log_audit_event(
        user=user,
        action='login',
        category='authentication',
        description=f'User {user.username} logged in successfully',
        severity='info',
        request=request
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log logout"""
    if user:
        SecurityService.log_audit_event(
            user=user,
            action='logout',
            category='authentication',
            description=f'User {user.username} logged out',
            severity='info',
            request=request
        )


@receiver(user_login_failed)
def log_login_failed(sender, credentials, request, **kwargs):
    """Log failed login attempt"""
    username = credentials.get('username', 'unknown')
    SecurityService.log_audit_event(
        user=None,
        action='login_failed',
        category='authentication',
        description=f'Failed login attempt for username: {username}',
        severity='warning',
        success=False,
        request=request,
        metadata={'username': username}
    )
