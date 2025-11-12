"""
Celery tasks for integration hub
"""

from celery import shared_task
import requests
import json
import logging
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def trigger_webhook(self, event, payload):
    """
    Trigger webhooks subscribed to a specific event
    """
    from .models import Webhook, WebhookDelivery
    
    # Find active webhooks for this event
    webhooks = Webhook.objects.filter(
        is_active=True,
        status='active',
        events__contains=event
    )
    
    for webhook in webhooks:
        # Create delivery record
        delivery = WebhookDelivery.objects.create(
            webhook=webhook,
            event=event,
            payload=payload,
            status='pending'
        )
        
        # Queue delivery
        deliver_webhook.delay(str(webhook.id), str(delivery.id))


@shared_task(bind=True, max_retries=3)
def deliver_webhook(self, webhook_id, delivery_id):
    """
    Deliver a webhook payload to target URL
    """
    from .models import Webhook, WebhookDelivery
    import time
    
    try:
        webhook = Webhook.objects.get(id=webhook_id)
        delivery = WebhookDelivery.objects.get(id=delivery_id)
        
        # Prepare payload
        payload_json = json.dumps(delivery.payload)
        
        # Generate signature
        signature = webhook.generate_signature(payload_json)
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': signature,
            'X-Webhook-Event': delivery.event,
            'X-Webhook-Delivery': str(delivery.id),
        }
        
        # Add custom headers
        if webhook.custom_headers:
            headers.update(webhook.custom_headers)
        
        # Make request
        start_time = time.time()
        
        try:
            response = requests.post(
                webhook.url,
                data=payload_json,
                headers=headers,
                timeout=30
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Update delivery record
            delivery.status = 'success' if response.status_code < 400 else 'failed'
            delivery.status_code = response.status_code
            delivery.response_body = response.text[:1000]  # Limit size
            delivery.delivered_at = timezone.now()
            delivery.duration_ms = duration_ms
            delivery.attempts += 1
            delivery.save()
            
            # Update webhook stats
            webhook.total_deliveries += 1
            if delivery.status == 'success':
                webhook.successful_deliveries += 1
                webhook.status = 'active'
            else:
                webhook.failed_deliveries += 1
                
                # Retry if needed
                if delivery.attempts < webhook.max_retries:
                    delivery.status = 'retrying'
                    delivery.next_retry_at = timezone.now() + timedelta(seconds=webhook.retry_delay)
                    delivery.save()
                    
                    # Schedule retry
                    deliver_webhook.apply_async(
                        args=[webhook_id, delivery_id],
                        countdown=webhook.retry_delay
                    )
            
            webhook.last_delivery_at = timezone.now()
            webhook.save()
            
            logger.info(f"Webhook delivered: {webhook.name} - {delivery.event} - Status: {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            # Network/connection error
            delivery.status = 'failed'
            delivery.error_message = str(e)
            delivery.attempts += 1
            delivery.save()
            
            webhook.failed_deliveries += 1
            webhook.total_deliveries += 1
            
            # Retry if needed
            if delivery.attempts < webhook.max_retries:
                delivery.status = 'retrying'
                delivery.next_retry_at = timezone.now() + timedelta(seconds=webhook.retry_delay)
                delivery.save()
                
                deliver_webhook.apply_async(
                    args=[webhook_id, delivery_id],
                    countdown=webhook.retry_delay
                )
            else:
                webhook.status = 'failed'
            
            webhook.save()
            
            logger.error(f"Webhook delivery failed: {webhook.name} - {str(e)}")
            
    except Webhook.DoesNotExist:
        logger.error(f"Webhook {webhook_id} not found")
    except WebhookDelivery.DoesNotExist:
        logger.error(f"Webhook delivery {delivery_id} not found")
    except Exception as e:
        logger.error(f"Error delivering webhook: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task
def sync_third_party_integration(integration_id):
    """
    Sync data with third-party integration
    """
    from .models import ThirdPartyIntegration, IntegrationLog
    
    try:
        integration = ThirdPartyIntegration.objects.get(id=integration_id)
        
        # Log sync attempt
        sync_log = IntegrationLog.objects.create(
            integration=integration,
            event_type='sync_start',
            description=f"Syncing {integration.provider} integration"
        )
        
        # Provider-specific sync logic
        if integration.provider == 'slack':
            sync_slack(integration)
        elif integration.provider == 'google_calendar':
            sync_google_calendar(integration)
        # Add more providers as needed
        
        integration.last_sync_at = timezone.now()
        integration.error_count = 0
        integration.status = 'active'
        integration.save()
        
        # Update sync log status
        sync_log.status = 'success'
        sync_log.save()
        
        logger.info(f"Integration synced: {integration.name}")
        
    except ThirdPartyIntegration.DoesNotExist:
        logger.error(f"Integration {integration_id} not found")
    except Exception as e:
        logger.error(f"Error syncing integration: {str(e)}")
        
        try:
            integration = ThirdPartyIntegration.objects.get(id=integration_id)
            integration.error_count += 1
            integration.error_message = str(e)
            integration.status = 'error'
            integration.save()
        except ThirdPartyIntegration.DoesNotExist:
            logger.error(f"Failed to update integration error status: Integration {integration_id} not found")


def sync_slack(integration):
    """Sync with Slack"""
    # Placeholder for Slack sync logic
    logger.info(f"Syncing Slack integration: {integration.name}")
    pass


def sync_google_calendar(integration):
    """Sync with Google Calendar"""
    # Placeholder for Google Calendar sync logic
    logger.info(f"Syncing Google Calendar integration: {integration.name}")
    pass


@shared_task
def retry_failed_webhook_deliveries():
    """
    Retry failed webhook deliveries that are due for retry
    """
    from .models import WebhookDelivery
    
    deliveries = WebhookDelivery.objects.filter(
        status='retrying',
        next_retry_at__lte=timezone.now()
    )
    
    for delivery in deliveries:
        deliver_webhook.delay(str(delivery.webhook.id), str(delivery.id))
    
    logger.info(f"Retrying {deliveries.count()} failed webhook deliveries")
