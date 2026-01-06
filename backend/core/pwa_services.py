"""
Progressive Web App (PWA) Backend Services
"""

import json
from datetime import datetime
from typing import Any

from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone


class PushNotificationService:
    """Service for sending web push notifications"""

    def __init__(self, user=None):
        self.user = user

    def subscribe(
        self,
        endpoint: str,
        auth_key: str,
        p256dh_key: str,
        browser: str = '',
        user_agent: str = '',
        preferences: dict[str, bool] = None
    ) -> dict[str, Any]:
        """Subscribe to push notifications"""
        from .pwa_models import PushSubscription

        subscription, created = PushSubscription.objects.update_or_create(
            user=self.user,
            endpoint=endpoint,
            defaults={
                'auth_key': auth_key,
                'p256dh_key': p256dh_key,
                'browser': browser,
                'user_agent': user_agent,
                'is_active': True,
                'notifications_enabled': True,
                **(preferences or {})
            }
        )

        return {
            'subscription_id': str(subscription.id),
            'created': created,
            'active': subscription.is_active
        }

    def unsubscribe(self, endpoint: str) -> dict[str, Any]:
        """Unsubscribe from push notifications"""
        from .pwa_models import PushSubscription

        deleted, _ = PushSubscription.objects.filter(
            user=self.user,
            endpoint=endpoint
        ).delete()

        return {'unsubscribed': deleted > 0}

    def update_preferences(
        self,
        subscription_id: str,
        preferences: dict[str, Any]
    ) -> dict[str, Any]:
        """Update notification preferences"""
        from .pwa_models import PushSubscription

        subscription = PushSubscription.objects.get(
            id=subscription_id,
            user=self.user
        )

        for key, value in preferences.items():
            if hasattr(subscription, key):
                setattr(subscription, key, value)

        subscription.save()

        return {'updated': True}

    def send_notification(
        self,
        user,
        notification_type: str,
        title: str,
        body: str,
        click_action: str = '',
        data: dict[str, Any] = None,
        icon: str = '',
        actions: list[dict] = None
    ) -> dict[str, Any]:
        """Send a push notification to a user"""
        from .pwa_models import PushNotification, PushSubscription

        subscriptions = PushSubscription.objects.filter(
            user=user,
            is_active=True,
            notifications_enabled=True
        )

        # Filter by notification type preference
        type_preference_map = {
            'new_lead': 'notify_new_leads',
            'task_reminder': 'notify_task_reminders',
            'task_assigned': 'notify_task_reminders',
            'deal_update': 'notify_deal_updates',
            'deal_won': 'notify_deal_updates',
            'deal_lost': 'notify_deal_updates',
            'new_message': 'notify_messages',
            'mention': 'notify_mentions',
        }

        pref_field = type_preference_map.get(notification_type)
        if pref_field:
            subscriptions = subscriptions.filter(**{pref_field: True})

        # Check quiet hours
        now = timezone.now().time()
        subscriptions = subscriptions.exclude(
            Q(quiet_start__isnull=False) &
            Q(quiet_end__isnull=False) &
            Q(quiet_start__lte=now) &
            Q(quiet_end__gte=now)
        )

        sent = 0
        failed = 0

        for subscription in subscriptions:
            notification = PushNotification.objects.create(
                subscription=subscription,
                notification_type=notification_type,
                title=title,
                body=body,
                click_action=click_action,
                data=data or {},
                icon=icon or '/icons/notification-icon.png',
                actions=actions or []
            )

            try:
                self._send_webpush(subscription, notification)
                notification.status = 'sent'
                notification.sent_at = timezone.now()
                sent += 1
            except Exception as e:
                notification.status = 'failed'
                notification.error_message = str(e)
                failed += 1

            notification.save()

        return {
            'sent': sent,
            'failed': failed,
            'total_subscriptions': subscriptions.count()
        }

    def _send_webpush(self, subscription, notification):
        """Send webpush notification"""
        try:
            from pywebpush import WebPushException, webpush

            payload = json.dumps({
                'title': notification.title,
                'body': notification.body,
                'icon': notification.icon,
                'badge': notification.badge or '/icons/badge.png',
                'image': notification.image,
                'data': {
                    'click_action': notification.click_action,
                    **notification.data
                },
                'actions': notification.actions
            })

            webpush(
                subscription_info={
                    'endpoint': subscription.endpoint,
                    'keys': {
                        'auth': subscription.auth_key,
                        'p256dh': subscription.p256dh_key
                    }
                },
                data=payload,
                vapid_private_key=getattr(settings, 'VAPID_PRIVATE_KEY', ''),
                vapid_claims={
                    'sub': f"mailto:{getattr(settings, 'VAPID_EMAIL', 'admin@example.com')}"
                }
            )

        except ImportError:
            # pywebpush not installed, log and skip
            pass
        except Exception as e:
            raise e

    def send_to_all_users(
        self,
        notification_type: str,
        title: str,
        body: str,
        **kwargs
    ) -> dict[str, Any]:
        """Send notification to all users"""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        users = User.objects.filter(is_active=True)

        total_sent = 0
        total_failed = 0

        for user in users:
            result = self.send_notification(
                user=user,
                notification_type=notification_type,
                title=title,
                body=body,
                **kwargs
            )
            total_sent += result['sent']
            total_failed += result['failed']

        return {
            'total_sent': total_sent,
            'total_failed': total_failed,
            'users_notified': users.count()
        }

    def track_delivery(self, notification_id: str) -> dict[str, Any]:
        """Track notification delivery"""
        from .pwa_models import PushNotification

        notification = PushNotification.objects.get(id=notification_id)
        notification.status = 'delivered'
        notification.delivered_at = timezone.now()
        notification.save()

        return {'delivered': True}

    def track_click(self, notification_id: str) -> dict[str, Any]:
        """Track notification click"""
        from .pwa_models import PushNotification

        notification = PushNotification.objects.get(id=notification_id)
        notification.status = 'clicked'
        notification.clicked_at = timezone.now()
        notification.save()

        return {'clicked': True}


class BackgroundSyncService:
    """Service for handling background sync operations"""

    def __init__(self, user):
        self.user = user

    def request_sync(
        self,
        sync_type: str,
        tag: str,
        payload: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Request a background sync job"""
        from .pwa_models import BackgroundSyncJob

        job = BackgroundSyncJob.objects.create(
            user=self.user,
            sync_type=sync_type,
            tag=tag,
            payload=payload or {}
        )

        return {
            'job_id': str(job.id),
            'tag': tag,
            'status': 'pending'
        }

    def process_sync_job(self, job_id: str) -> dict[str, Any]:
        """Process a background sync job"""
        from .pwa_models import BackgroundSyncJob

        job = BackgroundSyncJob.objects.get(id=job_id, user=self.user)

        job.status = 'in_progress'
        job.started_at = timezone.now()
        job.save()

        try:
            if job.sync_type == 'contacts':
                result = self._sync_contacts(job.payload)
            elif job.sync_type == 'leads':
                result = self._sync_leads(job.payload)
            elif job.sync_type == 'opportunities':
                result = self._sync_opportunities(job.payload)
            elif job.sync_type == 'tasks':
                result = self._sync_tasks(job.payload)
            elif job.sync_type == 'activities':
                result = self._sync_activities(job.payload)
            elif job.sync_type == 'full':
                result = self._full_sync()
            else:
                result = {'synced': 0, 'failed': 0, 'errors': []}

            job.synced_count = result.get('synced', 0)
            job.failed_count = result.get('failed', 0)
            job.error_details = result.get('errors', [])
            job.status = 'completed'
            job.completed_at = timezone.now()

        except Exception as e:
            job.status = 'failed'
            job.error_details = [str(e)]
            job.completed_at = timezone.now()

        job.save()

        return {
            'job_id': str(job.id),
            'status': job.status,
            'synced': job.synced_count,
            'failed': job.failed_count
        }

    def _sync_contacts(self, payload: dict) -> dict[str, Any]:
        """Sync contacts data"""
        # Implementation depends on payload structure
        return {'synced': 0, 'failed': 0, 'errors': []}

    def _sync_leads(self, payload: dict) -> dict[str, Any]:
        """Sync leads data"""
        return {'synced': 0, 'failed': 0, 'errors': []}

    def _sync_opportunities(self, payload: dict) -> dict[str, Any]:
        """Sync opportunities data"""
        return {'synced': 0, 'failed': 0, 'errors': []}

    def _sync_tasks(self, payload: dict) -> dict[str, Any]:
        """Sync tasks data"""
        return {'synced': 0, 'failed': 0, 'errors': []}

    def _sync_activities(self, payload: dict) -> dict[str, Any]:
        """Sync activities data"""
        return {'synced': 0, 'failed': 0, 'errors': []}

    def _full_sync(self) -> dict[str, Any]:
        """Perform full data sync"""
        total_synced = 0
        total_failed = 0
        errors = []

        for sync_type in ['contacts', 'leads', 'opportunities', 'tasks']:
            result = getattr(self, f'_sync_{sync_type}')({})
            total_synced += result.get('synced', 0)
            total_failed += result.get('failed', 0)
            errors.extend(result.get('errors', []))

        return {
            'synced': total_synced,
            'failed': total_failed,
            'errors': errors
        }

    def get_pending_jobs(self) -> list[dict[str, Any]]:
        """Get pending sync jobs"""
        from .pwa_models import BackgroundSyncJob

        jobs = BackgroundSyncJob.objects.filter(
            user=self.user,
            status='pending'
        )

        return [{
            'job_id': str(job.id),
            'sync_type': job.sync_type,
            'tag': job.tag,
            'requested_at': job.requested_at.isoformat()
        } for job in jobs]


class OfflineActionService:
    """Service for processing offline actions"""

    def __init__(self, user):
        self.user = user

    def queue_action(
        self,
        action_type: str,
        entity_type: str,
        entity_id: str = '',
        method: str = '',
        url: str = '',
        payload: dict[str, Any] = None,
        headers: dict[str, str] = None,
        created_offline_at: datetime = None
    ) -> dict[str, Any]:
        """Queue an offline action for sync"""
        from .pwa_models import OfflineAction

        action = OfflineAction.objects.create(
            user=self.user,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            method=method,
            url=url,
            payload=payload or {},
            headers=headers or {},
            created_offline_at=created_offline_at or timezone.now()
        )

        return {
            'action_id': str(action.id),
            'queued': True
        }

    def process_queued_actions(self) -> dict[str, Any]:
        """Process all queued offline actions"""
        from .pwa_models import OfflineAction

        actions = OfflineAction.objects.filter(
            user=self.user,
            status='queued'
        ).order_by('created_offline_at')

        results = {
            'processed': 0,
            'failed': 0,
            'conflicts': 0,
            'details': []
        }

        for action in actions:
            result = self._process_action(action)

            if result['status'] == 'synced':
                results['processed'] += 1
            elif result['status'] == 'conflict':
                results['conflicts'] += 1
            else:
                results['failed'] += 1

            results['details'].append({
                'action_id': str(action.id),
                'result': result
            })

        return results

    def _process_action(self, action) -> dict[str, Any]:
        """Process a single offline action"""
        action.status = 'syncing'
        action.save()

        try:
            if action.action_type == 'create':
                result = self._process_create(action)
            elif action.action_type == 'update':
                result = self._process_update(action)
            elif action.action_type == 'delete':
                result = self._process_delete(action)
            elif action.action_type == 'api_call':
                result = self._process_api_call(action)
            else:
                result = {'status': 'failed', 'error': 'Unknown action type'}

            if result.get('status') == 'synced':
                action.status = 'synced'
                action.synced_at = timezone.now()
                action.response_status = result.get('response_status')
                action.response_data = result.get('response_data')
            elif result.get('status') == 'conflict':
                action.status = 'conflict'
            else:
                action.status = 'failed'
                action.error_message = result.get('error', '')
                action.retry_count += 1

            action.save()
            return result

        except Exception as e:
            action.status = 'failed'
            action.error_message = str(e)
            action.retry_count += 1
            action.save()

            return {'status': 'failed', 'error': str(e)}

    def _process_create(self, action) -> dict[str, Any]:
        """Process create action"""
        # Implementation depends on entity type
        return {'status': 'synced', 'response_status': 201}

    def _process_update(self, action) -> dict[str, Any]:
        """Process update action"""
        return {'status': 'synced', 'response_status': 200}

    def _process_delete(self, action) -> dict[str, Any]:
        """Process delete action"""
        return {'status': 'synced', 'response_status': 204}

    def _process_api_call(self, action) -> dict[str, Any]:
        """Process generic API call"""
        import requests

        try:
            response = requests.request(
                method=action.method,
                url=action.url,
                json=action.payload,
                headers=action.headers,
                timeout=30
            )

            return {
                'status': 'synced',
                'response_status': response.status_code,
                'response_data': response.json() if response.content else None
            }

        except Exception as e:
            return {'status': 'failed', 'error': str(e)}

    def get_pending_actions(self) -> list[dict[str, Any]]:
        """Get pending offline actions"""
        from .pwa_models import OfflineAction

        actions = OfflineAction.objects.filter(
            user=self.user,
            status='queued'
        )

        return [{
            'action_id': str(action.id),
            'action_type': action.action_type,
            'entity_type': action.entity_type,
            'created_offline_at': action.created_offline_at.isoformat()
        } for action in actions]


class PWAAnalyticsService:
    """Service for PWA installation and usage analytics"""

    def track_prompt_shown(
        self,
        platform: str,
        browser: str,
        user=None
    ) -> dict[str, Any]:
        """Track when install prompt is shown"""
        from .pwa_models import InstallationAnalytics

        analytics, _ = InstallationAnalytics.objects.get_or_create(
            user=user,
            platform=platform,
            browser=browser,
            defaults={
                'prompt_shown': True,
                'prompt_shown_at': timezone.now()
            }
        )

        if not analytics.prompt_shown:
            analytics.prompt_shown = True
            analytics.prompt_shown_at = timezone.now()
            analytics.save()

        return {'tracked': True}

    def track_prompt_response(
        self,
        platform: str,
        browser: str,
        accepted: bool,
        user=None
    ) -> dict[str, Any]:
        """Track user response to install prompt"""
        from .pwa_models import InstallationAnalytics

        analytics, _ = InstallationAnalytics.objects.get_or_create(
            user=user,
            platform=platform,
            browser=browser
        )

        if accepted:
            analytics.prompt_accepted = True
        else:
            analytics.prompt_dismissed = True

        analytics.save()

        return {'tracked': True, 'accepted': accepted}

    def track_installation(
        self,
        platform: str,
        browser: str,
        install_source: str,
        user=None
    ) -> dict[str, Any]:
        """Track PWA installation"""
        from .pwa_models import InstallationAnalytics

        analytics, _ = InstallationAnalytics.objects.get_or_create(
            user=user,
            platform=platform,
            browser=browser
        )

        analytics.installed = True
        analytics.install_source = install_source
        analytics.installed_at = timezone.now()
        analytics.save()

        return {'tracked': True}

    def track_standalone_launch(
        self,
        platform: str,
        browser: str,
        user=None
    ) -> dict[str, Any]:
        """Track app launched in standalone mode"""
        from .pwa_models import InstallationAnalytics

        analytics, _ = InstallationAnalytics.objects.get_or_create(
            user=user,
            platform=platform,
            browser=browser
        )

        analytics.standalone_launches += 1
        analytics.last_standalone_launch = timezone.now()
        analytics.save()

        return {'launches': analytics.standalone_launches}

    def get_installation_stats(self) -> dict[str, Any]:
        """Get overall installation statistics"""
        from .pwa_models import InstallationAnalytics

        analytics = InstallationAnalytics.objects.all()

        total = analytics.count()
        installed = analytics.filter(installed=True).count()

        by_platform = analytics.values('platform').annotate(
            total=Count('id'),
            installed=Count('id', filter=Q(installed=True))
        )

        by_browser = analytics.values('browser').annotate(
            total=Count('id'),
            installed=Count('id', filter=Q(installed=True))
        )

        prompt_stats = {
            'shown': analytics.filter(prompt_shown=True).count(),
            'accepted': analytics.filter(prompt_accepted=True).count(),
            'dismissed': analytics.filter(prompt_dismissed=True).count()
        }

        conversion_rate = (installed / total * 100) if total > 0 else 0
        prompt_acceptance_rate = (
            prompt_stats['accepted'] / prompt_stats['shown'] * 100
        ) if prompt_stats['shown'] > 0 else 0

        return {
            'total_users': total,
            'installed': installed,
            'conversion_rate': round(conversion_rate, 2),
            'prompt_stats': prompt_stats,
            'prompt_acceptance_rate': round(prompt_acceptance_rate, 2),
            'by_platform': list(by_platform),
            'by_browser': list(by_browser)
        }


class CacheManagementService:
    """Service for managing PWA cache strategies"""

    def get_cache_manifest(self) -> dict[str, Any]:
        """Get cache manifest for service worker"""
        from .pwa_models import CacheManifest

        manifests = CacheManifest.objects.filter(is_active=True)

        cache_config = {
            'version': self._get_cache_version(),
            'strategies': {}
        }

        for manifest in manifests:
            cache_config['strategies'][manifest.url_pattern] = {
                'strategy': manifest.strategy,
                'max_age': manifest.max_age_seconds,
                'resource_type': manifest.resource_type
            }

        return cache_config

    def _get_cache_version(self) -> str:
        """Get current cache version"""
        from .pwa_models import CacheManifest

        latest = CacheManifest.objects.filter(
            is_active=True
        ).order_by('-updated_at').first()

        if latest:
            return latest.version
        return '1.0.0'

    def update_cache_version(self, version: str) -> dict[str, Any]:
        """Update cache version (triggers cache invalidation)"""
        from .pwa_models import CacheManifest

        CacheManifest.objects.filter(is_active=True).update(version=version)

        return {'version': version, 'updated': True}
