"""
Notification Service
Central service for sending notifications across all channels
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import time

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .settings_models import NotificationPreference, NotificationTypeSetting
from .notification_templates import EmailTemplates
from .models import Notification

logger = logging.getLogger(__name__)
User = get_user_model()


class NotificationService:
    """
    Service for sending notifications through various channels
    """
    
    def __init__(self):
        self.channel_layer = None
        try:
            self.channel_layer = get_channel_layer()
        except Exception as e:
            logger.warning(f"Could not get channel layer: {e}")
    
    def send(
        self,
        user: User,
        notification_type: str,
        title: str,
        message: str,
        context: Dict[str, Any] = None,
        action_url: str = None,
        priority: str = 'medium',
    ) -> Dict[str, bool]:
        """
        Send a notification through all enabled channels
        
        Args:
            user: The recipient user
            notification_type: Type of notification (e.g., 'deal_won', 'task_due_soon')
            title: Notification title
            message: Notification message
            context: Additional context for templates
            action_url: URL for the action button
            priority: Notification priority (low/medium/high)
        
        Returns:
            Dict with success status for each channel
        """
        context = context or {}
        results = {'email': False, 'push': False, 'in_app': False, 'sms': False}
        
        # Get user preferences
        prefs = self._get_preferences(user)
        type_settings = self._get_type_settings(prefs, notification_type)
        
        # Check quiet hours
        if self._is_quiet_hours(prefs):
            if priority != 'high':
                logger.info(f"Quiet hours active for {user.username}, skipping non-urgent notification")
                return results
        
        # Send to each enabled channel
        if type_settings.get('in_app', True) and prefs.in_app_enabled:
            results['in_app'] = self._send_in_app(user, notification_type, title, message, action_url, priority)
        
        if type_settings.get('email', True) and prefs.email_enabled:
            results['email'] = self._send_email(user, notification_type, title, message, context, action_url)
        
        if type_settings.get('push', True) and prefs.push_enabled:
            results['push'] = self._send_push(user, notification_type, title, message, action_url)
        
        if type_settings.get('sms', False) and prefs.sms_enabled:
            results['sms'] = self._send_sms(user, notification_type, title, message)
        
        # Send real-time WebSocket notification
        if results['in_app']:
            self._send_websocket(user, notification_type, title, message, action_url, priority)
        
        return results
    
    def send_to_many(
        self,
        users: List[User],
        notification_type: str,
        title: str,
        message: str,
        context: Dict[str, Any] = None,
        action_url: str = None,
        priority: str = 'medium',
    ) -> Dict[int, Dict[str, bool]]:
        """Send notification to multiple users"""
        results = {}
        for user in users:
            results[user.id] = self.send(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                context=context,
                action_url=action_url,
                priority=priority,
            )
        return results
    
    def send_to_team(
        self,
        team_id: str,
        notification_type: str,
        title: str,
        message: str,
        context: Dict[str, Any] = None,
        action_url: str = None,
        exclude_users: List[int] = None,
    ):
        """Send notification to all team members"""
        from .models import TeamMember
        
        exclude_users = exclude_users or []
        members = TeamMember.objects.filter(
            team_id=team_id,
            is_active=True
        ).exclude(user_id__in=exclude_users).select_related('user')
        
        users = [m.user for m in members]
        return self.send_to_many(users, notification_type, title, message, context, action_url)
    
    def _get_preferences(self, user: User) -> NotificationPreference:
        """Get or create notification preferences for user"""
        prefs, _ = NotificationPreference.objects.get_or_create(user=user)
        return prefs
    
    def _get_type_settings(self, prefs: NotificationPreference, notification_type: str) -> Dict[str, Any]:
        """Get settings for a specific notification type"""
        try:
            setting = NotificationTypeSetting.objects.get(
                notification_preference=prefs,
                notification_type=notification_type
            )
            return {
                'email': setting.email_enabled,
                'push': setting.push_enabled,
                'in_app': setting.in_app_enabled,
                'sms': setting.sms_enabled,
                'frequency': setting.frequency,
                'priority': setting.priority,
            }
        except NotificationTypeSetting.DoesNotExist:
            return {
                'email': True,
                'push': True,
                'in_app': True,
                'sms': False,
                'frequency': 'instant',
                'priority': 'medium',
            }
    
    def _is_quiet_hours(self, prefs: NotificationPreference) -> bool:
        """Check if current time is within quiet hours"""
        if not prefs.quiet_hours_enabled:
            return False
        
        now = timezone.localtime().time()
        current_day = timezone.localtime().strftime('%a')
        
        # Check if current day is in quiet hours days
        if prefs.quiet_hours_days and current_day not in prefs.quiet_hours_days:
            return False
        
        start = prefs.quiet_hours_start
        end = prefs.quiet_hours_end
        
        # Handle overnight quiet hours (e.g., 22:00 to 08:00)
        if start > end:
            return now >= start or now <= end
        else:
            return start <= now <= end
    
    def _send_in_app(
        self,
        user: User,
        notification_type: str,
        title: str,
        message: str,
        action_url: str,
        priority: str,
    ) -> bool:
        """Create in-app notification"""
        try:
            # Map notification type to model notification type
            type_mapping = {
                'deal_won': 'success',
                'deal_lost': 'warning',
                'task_overdue': 'error',
                'security_alert': 'error',
                'mention': 'mention',
                'task_assigned': 'task',
            }
            
            Notification.objects.create(
                user=user,
                title=title,
                message=message,
                notification_type=type_mapping.get(notification_type, 'info'),
                link=action_url or '',
            )
            return True
        except Exception as e:
            logger.error(f"Failed to create in-app notification: {e}")
            return False
    
    def _send_email(
        self,
        user: User,
        notification_type: str,
        title: str,
        message: str,
        context: Dict[str, Any],
        action_url: str,
    ) -> bool:
        """Send email notification"""
        try:
            # Add common context
            context['user'] = user
            context['action_url'] = action_url
            context['title'] = title
            
            # Render HTML template
            try:
                html_content = EmailTemplates.render(notification_type, context)
            except ValueError:
                # Fallback to generic template
                html_content = f"<h2>{title}</h2><p>{message}</p>"
                if action_url:
                    html_content += f'<p><a href="{action_url}">View Details</a></p>'
            
            # Create email
            email = EmailMultiAlternatives(
                subject=title,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            
            return True
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    def _send_push(
        self,
        user: User,
        notification_type: str,
        title: str,
        message: str,
        action_url: str,
    ) -> bool:
        """Send push notification"""
        # Implementation depends on push service (Firebase, OneSignal, etc.)
        # This is a placeholder
        try:
            # Get user's push tokens
            # push_tokens = PushToken.objects.filter(user=user, is_active=True)
            
            # For now, just log
            logger.info(f"Push notification would be sent to {user.username}: {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
            return False
    
    def _send_sms(
        self,
        user: User,
        notification_type: str,
        title: str,
        message: str,
    ) -> bool:
        """Send SMS notification"""
        # Implementation depends on SMS service (Twilio, etc.)
        # This is a placeholder
        try:
            # phone = user.profile.phone if hasattr(user, 'profile') else None
            # if not phone:
            #     return False
            
            logger.info(f"SMS notification would be sent to {user.username}: {message[:50]}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS notification: {e}")
            return False
    
    def _send_websocket(
        self,
        user: User,
        notification_type: str,
        title: str,
        message: str,
        action_url: str,
        priority: str,
    ):
        """Send real-time WebSocket notification"""
        if not self.channel_layer:
            return
        
        try:
            async_to_sync(self.channel_layer.group_send)(
                f"user_{user.id}",
                {
                    'type': 'notification',
                    'data': {
                        'notification_type': notification_type,
                        'title': title,
                        'message': message,
                        'action_url': action_url,
                        'priority': priority,
                        'timestamp': timezone.now().isoformat(),
                    }
                }
            )
        except Exception as e:
            logger.warning(f"Failed to send WebSocket notification: {e}")


class DigestService:
    """
    Service for generating and sending digest emails
    """
    
    def __init__(self):
        self.notification_service = NotificationService()
    
    def send_daily_digest(self, user: User):
        """Send daily digest email to user"""
        prefs = NotificationPreference.objects.filter(user=user).first()
        
        if not prefs or not prefs.digest_enabled:
            return False
        
        if prefs.digest_frequency != 'daily':
            return False
        
        # Gather metrics
        from .settings_views import AnalyticsDashboardView
        
        context = {
            'user': user,
            'date': timezone.now(),
            'metrics': self._get_daily_metrics(user),
            'tasks_due': self._get_tasks_due_today(user),
            'upcoming_meetings': self._get_upcoming_meetings(user),
            'dashboard_url': f"{settings.FRONTEND_URL}/dashboard",
        }
        
        if prefs.digest_include_ai:
            context['ai_insights'] = self._get_ai_insights(user)
        
        try:
            html_content = EmailTemplates.render('daily_digest', context)
            
            email = EmailMultiAlternatives(
                subject=f"Your Daily CRM Digest - {timezone.now().strftime('%B %d, %Y')}",
                body="Your daily CRM digest",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            
            return True
        except Exception as e:
            logger.error(f"Failed to send daily digest to {user.username}: {e}")
            return False
    
    def send_weekly_digest(self, user: User):
        """Send weekly digest email to user"""
        prefs = NotificationPreference.objects.filter(user=user).first()
        
        if not prefs or not prefs.digest_enabled:
            return False
        
        if prefs.digest_frequency != 'weekly':
            return False
        
        now = timezone.now()
        week_start = now - timezone.timedelta(days=now.weekday())
        week_end = week_start + timezone.timedelta(days=6)
        
        context = {
            'user': user,
            'week_start': week_start,
            'week_end': week_end,
            'metrics': self._get_weekly_metrics(user, week_start, week_end),
            'top_deals': self._get_top_deals(user, week_start, week_end),
            'dashboard_url': f"{settings.FRONTEND_URL}/dashboard",
        }
        
        try:
            html_content = EmailTemplates.render('weekly_digest', context)
            
            email = EmailMultiAlternatives(
                subject=f"Your Weekly CRM Report - Week of {week_start.strftime('%B %d')}",
                body="Your weekly CRM report",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            
            return True
        except Exception as e:
            logger.error(f"Failed to send weekly digest to {user.username}: {e}")
            return False
    
    def _get_daily_metrics(self, user: User) -> Dict[str, Any]:
        """Get daily metrics for user"""
        # Mock data - replace with actual queries
        return {
            'deals_closed': 3,
            'revenue': 45000,
            'tasks_completed': 8,
            'activities': 15,
        }
    
    def _get_weekly_metrics(self, user: User, week_start, week_end) -> Dict[str, Any]:
        """Get weekly metrics for user"""
        # Mock data - replace with actual queries
        return {
            'deals_won': 5,
            'total_revenue': 125000,
            'conversion_rate': 28,
            'prev_deals_won': 4,
            'prev_revenue': 98000,
            'deals_change': 25,
            'revenue_change': 27,
            'activities': 45,
            'prev_activities': 38,
            'activity_change': 18,
        }
    
    def _get_tasks_due_today(self, user: User) -> List[Dict]:
        """Get tasks due today"""
        return []
    
    def _get_upcoming_meetings(self, user: User) -> List[Dict]:
        """Get upcoming meetings"""
        return []
    
    def _get_ai_insights(self, user: User) -> List[str]:
        """Get AI insights for user"""
        return [
            "Your response rate improved by 15% this week",
            "Consider following up with 3 stale deals",
        ]
    
    def _get_top_deals(self, user: User, week_start, week_end) -> List[Dict]:
        """Get top deals for the week"""
        return []


# Singleton instance
notification_service = NotificationService()
digest_service = DigestService()
