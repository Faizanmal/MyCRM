"""
Integration Marketplace - Services
App management, webhook builder, and rate limiting
"""

import os
import json
import hashlib
import hmac
import requests
import re
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional

from django.db.models import Sum, Avg, Count
from django.utils import timezone
from django.template import Template, Context


class MarketplaceService:
    """Service for marketplace operations"""
    
    def search_apps(self, query: str = '', category: str = '', 
                   tags: List[str] = None) -> List[Dict]:
        """Search marketplace apps"""
        
        from .marketplace_models import MarketplaceApp
        
        apps = MarketplaceApp.objects.filter(status='published')
        
        if query:
            apps = apps.filter(
                models.Q(name__icontains=query) |
                models.Q(tagline__icontains=query) |
                models.Q(description__icontains=query)
            )
        
        if category:
            apps = apps.filter(category=category)
        
        if tags:
            for tag in tags:
                apps = apps.filter(tags__contains=[tag])
        
        return list(apps)
    
    def get_featured_apps(self, limit: int = 10) -> List[Dict]:
        """Get featured apps"""
        
        from .marketplace_models import MarketplaceApp
        
        apps = MarketplaceApp.objects.filter(
            status='published'
        ).order_by('-rating_avg', '-install_count')[:limit]
        
        return list(apps)
    
    def install_app(self, app, user, config: Dict = None) -> Dict[str, Any]:
        """Install an app for a user"""
        
        from .marketplace_models import AppInstallation
        
        installation, created = AppInstallation.objects.get_or_create(
            app=app,
            user=user,
            defaults={
                'status': 'active',
                'config': config or {},
            }
        )
        
        if not created and installation.status == 'uninstalled':
            installation.status = 'active'
            installation.config = config or installation.config
            installation.uninstalled_at = None
            installation.save()
        
        # Update install count
        app.install_count += 1
        app.save()
        
        return {
            'installation_id': str(installation.id),
            'status': installation.status,
            'created': created,
        }
    
    def uninstall_app(self, app, user) -> Dict[str, Any]:
        """Uninstall an app"""
        
        from .marketplace_models import AppInstallation
        
        try:
            installation = AppInstallation.objects.get(app=app, user=user)
            installation.status = 'uninstalled'
            installation.uninstalled_at = timezone.now()
            installation.save()
            
            app.install_count = max(0, app.install_count - 1)
            app.save()
            
            return {'status': 'uninstalled'}
        except AppInstallation.DoesNotExist:
            return {'error': 'App not installed'}
    
    def get_oauth_url(self, app, user, redirect_uri: str) -> str:
        """Generate OAuth authorization URL"""
        
        import urllib.parse
        
        if not app.oauth_authorize_url:
            return None
        
        state = hashlib.sha256(
            f"{app.id}{user.id}{timezone.now().isoformat()}".encode()
        ).hexdigest()[:32]
        
        params = {
            'client_id': app.oauth_client_id,
            'redirect_uri': redirect_uri,
            'scope': ' '.join(app.oauth_scopes),
            'state': state,
            'response_type': 'code',
        }
        
        return f"{app.oauth_authorize_url}?{urllib.parse.urlencode(params)}"
    
    def exchange_oauth_code(self, app, user, code: str, 
                            redirect_uri: str) -> Dict[str, Any]:
        """Exchange OAuth code for tokens"""
        
        from .marketplace_models import AppInstallation
        
        try:
            response = requests.post(
                app.oauth_token_url,
                data={
                    'client_id': app.oauth_client_id,
                    'client_secret': app.oauth_client_secret,
                    'code': code,
                    'redirect_uri': redirect_uri,
                    'grant_type': 'authorization_code',
                },
                timeout=30
            )
            
            if response.status_code == 200:
                tokens = response.json()
                
                installation = AppInstallation.objects.get(app=app, user=user)
                installation.access_token = tokens.get('access_token', '')
                installation.refresh_token = tokens.get('refresh_token', '')
                
                expires_in = tokens.get('expires_in')
                if expires_in:
                    installation.token_expires_at = timezone.now() + timedelta(seconds=expires_in)
                
                installation.save()
                
                return {'status': 'success'}
            else:
                return {'error': 'Failed to exchange code'}
                
        except Exception as e:
            return {'error': str(e)}


class WebhookBuilderService:
    """Service for custom webhook building and management"""
    
    def __init__(self):
        self.event_registry = self._build_event_registry()
    
    def _build_event_registry(self) -> Dict[str, Dict]:
        """Build the event registry"""
        
        return {
            'contact.created': {
                'entity': 'contact',
                'action': 'created',
                'description': 'Triggered when a new contact is created',
                'payload_fields': ['id', 'first_name', 'last_name', 'email', 'company', 'created_at'],
            },
            'contact.updated': {
                'entity': 'contact',
                'action': 'updated',
                'description': 'Triggered when a contact is updated',
                'payload_fields': ['id', 'first_name', 'last_name', 'email', 'company', 'updated_at', 'changes'],
            },
            'contact.deleted': {
                'entity': 'contact',
                'action': 'deleted',
                'description': 'Triggered when a contact is deleted',
                'payload_fields': ['id', 'deleted_at'],
            },
            'lead.created': {
                'entity': 'lead',
                'action': 'created',
                'description': 'Triggered when a new lead is created',
                'payload_fields': ['id', 'first_name', 'last_name', 'email', 'company', 'source', 'created_at'],
            },
            'lead.qualified': {
                'entity': 'lead',
                'action': 'qualified',
                'description': 'Triggered when a lead is qualified',
                'payload_fields': ['id', 'first_name', 'last_name', 'qualified_at', 'qualification_score'],
            },
            'opportunity.created': {
                'entity': 'opportunity',
                'action': 'created',
                'description': 'Triggered when an opportunity is created',
                'payload_fields': ['id', 'name', 'amount', 'stage', 'owner', 'created_at'],
            },
            'opportunity.stage_changed': {
                'entity': 'opportunity',
                'action': 'stage_changed',
                'description': 'Triggered when opportunity stage changes',
                'payload_fields': ['id', 'name', 'previous_stage', 'new_stage', 'changed_at'],
            },
            'opportunity.won': {
                'entity': 'opportunity',
                'action': 'won',
                'description': 'Triggered when an opportunity is won',
                'payload_fields': ['id', 'name', 'amount', 'closed_at'],
            },
            'opportunity.lost': {
                'entity': 'opportunity',
                'action': 'lost',
                'description': 'Triggered when an opportunity is lost',
                'payload_fields': ['id', 'name', 'amount', 'lost_reason', 'closed_at'],
            },
            'task.created': {
                'entity': 'task',
                'action': 'created',
                'description': 'Triggered when a task is created',
                'payload_fields': ['id', 'title', 'assigned_to', 'due_date', 'priority'],
            },
            'task.completed': {
                'entity': 'task',
                'action': 'completed',
                'description': 'Triggered when a task is completed',
                'payload_fields': ['id', 'title', 'completed_at', 'completed_by'],
            },
            'email.sent': {
                'entity': 'email',
                'action': 'sent',
                'description': 'Triggered when an email is sent',
                'payload_fields': ['id', 'subject', 'to', 'from', 'sent_at'],
            },
            'email.opened': {
                'entity': 'email',
                'action': 'opened',
                'description': 'Triggered when an email is opened',
                'payload_fields': ['id', 'subject', 'opened_at', 'opened_by'],
            },
            'call.completed': {
                'entity': 'call',
                'action': 'completed',
                'description': 'Triggered when a call is completed',
                'payload_fields': ['id', 'contact', 'duration', 'outcome', 'completed_at'],
            },
        }
    
    def get_available_events(self) -> List[Dict]:
        """Get all available webhook events"""
        
        events = []
        for event_name, event_info in self.event_registry.items():
            events.append({
                'name': event_name,
                **event_info,
            })
        return events
    
    def create_webhook(self, user, config: Dict) -> Dict[str, Any]:
        """Create a new custom webhook"""
        
        from .marketplace_models import CustomWebhook
        
        webhook = CustomWebhook.objects.create(
            user=user,
            name=config['name'],
            description=config.get('description', ''),
            url=config['url'],
            method=config.get('method', 'POST'),
            events=config.get('events', []),
            auth_type=config.get('auth_type', 'none'),
            auth_config=config.get('auth_config', {}),
            custom_headers=config.get('custom_headers', {}),
            payload_template=config.get('payload_template', ''),
            conditions=config.get('conditions', []),
            retry_enabled=config.get('retry_enabled', True),
        )
        
        return {
            'webhook_id': str(webhook.id),
            'name': webhook.name,
            'status': 'created',
        }
    
    def test_webhook(self, webhook) -> Dict[str, Any]:
        """Test a webhook with sample payload"""
        
        sample_payload = {
            'event': 'test',
            'timestamp': timezone.now().isoformat(),
            'data': {
                'message': 'This is a test webhook delivery',
            },
        }
        
        return self.deliver_webhook(webhook, 'test', sample_payload)
    
    def deliver_webhook(self, webhook, event: str, payload: Dict) -> Dict[str, Any]:
        """Deliver a webhook"""
        
        from .marketplace_models import WebhookDeliveryLog
        
        # Build headers
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'MyCRM-Webhook/1.0',
            'X-Webhook-Event': event,
            'X-Webhook-ID': str(webhook.id),
            **webhook.custom_headers,
        }
        
        # Add authentication
        if webhook.auth_type == 'bearer':
            headers['Authorization'] = f"Bearer {webhook.auth_config.get('token', '')}"
        elif webhook.auth_type == 'api_key':
            key_name = webhook.auth_config.get('header_name', 'X-API-Key')
            headers[key_name] = webhook.auth_config.get('api_key', '')
        elif webhook.auth_type == 'hmac':
            secret = webhook.auth_config.get('secret', '')
            signature = hmac.new(
                secret.encode(),
                json.dumps(payload).encode(),
                hashlib.sha256
            ).hexdigest()
            headers['X-Webhook-Signature'] = f"sha256={signature}"
        
        # Apply payload template if exists
        if webhook.payload_template:
            try:
                template = Template(webhook.payload_template)
                context = Context(payload)
                body = template.render(context)
            except Exception:
                body = json.dumps(payload)
        else:
            body = json.dumps(payload)
        
        # Create log entry
        log = WebhookDeliveryLog.objects.create(
            webhook=webhook,
            event=event,
            request_url=webhook.url,
            request_method=webhook.method,
            request_headers=headers,
            request_body=body,
            status='pending',
        )
        
        # Deliver
        start_time = timezone.now()
        try:
            response = requests.request(
                method=webhook.method,
                url=webhook.url,
                headers=headers,
                data=body,
                timeout=30
            )
            
            duration = (timezone.now() - start_time).total_seconds() * 1000
            
            log.response_status = response.status_code
            log.response_headers = dict(response.headers)
            log.response_body = response.text[:5000]  # Limit response size
            log.duration_ms = int(duration)
            log.status = 'success' if response.status_code < 400 else 'failed'
            log.save()
            
            # Update webhook stats
            webhook.total_triggers += 1
            webhook.last_triggered = timezone.now()
            if log.status == 'success':
                webhook.successful_deliveries += 1
                webhook.last_success = timezone.now()
            else:
                webhook.failed_deliveries += 1
                webhook.last_failure = timezone.now()
            webhook.save()
            
            return {
                'status': log.status,
                'status_code': response.status_code,
                'duration_ms': log.duration_ms,
            }
            
        except Exception as e:
            log.status = 'failed'
            log.error_message = str(e)
            log.save()
            
            webhook.total_triggers += 1
            webhook.failed_deliveries += 1
            webhook.last_triggered = timezone.now()
            webhook.last_failure = timezone.now()
            webhook.save()
            
            return {
                'status': 'failed',
                'error': str(e),
            }
    
    def check_conditions(self, webhook, event: str, payload: Dict) -> bool:
        """Check if webhook conditions are met"""
        
        if not webhook.conditions:
            return True
        
        for condition in webhook.conditions:
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            
            # Get field value from payload
            field_value = payload
            for key in field.split('.'):
                if isinstance(field_value, dict):
                    field_value = field_value.get(key)
                else:
                    field_value = None
                    break
            
            # Evaluate condition
            if operator == 'equals':
                if field_value != value:
                    return False
            elif operator == 'not_equals':
                if field_value == value:
                    return False
            elif operator == 'contains':
                if value not in str(field_value):
                    return False
            elif operator == 'greater_than':
                if not (field_value and float(field_value) > float(value)):
                    return False
            elif operator == 'less_than':
                if not (field_value and float(field_value) < float(value)):
                    return False
        
        return True


class RateLimitingService:
    """Service for API rate limiting"""
    
    def __init__(self):
        self.default_limits = {
            'second': 10,
            'minute': 100,
            'hour': 1000,
            'day': 10000,
        }
    
    def check_rate_limit(self, user=None, api_key: str = None, 
                        endpoint: str = '/') -> Dict[str, Any]:
        """Check if rate limit is exceeded"""
        
        from .marketplace_models import APIRateLimit
        
        # Find applicable rate limit
        rate_limit = None
        
        if user:
            rate_limit = APIRateLimit.objects.filter(
                user=user,
                is_active=True
            ).first()
        elif api_key:
            rate_limit = APIRateLimit.objects.filter(
                api_key=api_key,
                is_active=True
            ).first()
        
        if not rate_limit:
            # Use default limits
            return {
                'allowed': True,
                'limit': self.default_limits['hour'],
                'remaining': self.default_limits['hour'],
                'reset': (timezone.now() + timedelta(hours=1)).isoformat(),
            }
        
        # Check if period has reset
        period_duration = self._get_period_duration(rate_limit.period)
        if rate_limit.period_start:
            period_end = rate_limit.period_start + period_duration
            if timezone.now() > period_end:
                rate_limit.current_count = 0
                rate_limit.period_start = timezone.now()
                rate_limit.is_exceeded = False
                rate_limit.save()
        else:
            rate_limit.period_start = timezone.now()
            rate_limit.save()
        
        remaining = max(0, rate_limit.requests_limit - rate_limit.current_count)
        reset_time = rate_limit.period_start + period_duration
        
        return {
            'allowed': not rate_limit.is_exceeded and remaining > 0,
            'limit': rate_limit.requests_limit,
            'remaining': remaining,
            'reset': reset_time.isoformat(),
        }
    
    def record_request(self, user=None, api_key: str = None, 
                      endpoint: str = '/', status_code: int = 200,
                      response_time_ms: int = 0, ip_address: str = None) -> None:
        """Record an API request"""
        
        from .marketplace_models import APIRateLimit, APIUsageLog
        
        # Log the request
        APIUsageLog.objects.create(
            user=user,
            api_key=api_key,
            endpoint=endpoint,
            method='GET',  # Would be passed in production
            status_code=status_code,
            response_time_ms=response_time_ms,
            ip_address=ip_address,
        )
        
        # Update rate limit counter
        rate_limit = None
        if user:
            rate_limit = APIRateLimit.objects.filter(
                user=user,
                is_active=True
            ).first()
        elif api_key:
            rate_limit = APIRateLimit.objects.filter(
                api_key=api_key,
                is_active=True
            ).first()
        
        if rate_limit:
            rate_limit.current_count += 1
            if rate_limit.current_count >= rate_limit.requests_limit:
                rate_limit.is_exceeded = True
            rate_limit.save()
    
    def _get_period_duration(self, period: str) -> timedelta:
        """Get timedelta for period"""
        
        durations = {
            'second': timedelta(seconds=1),
            'minute': timedelta(minutes=1),
            'hour': timedelta(hours=1),
            'day': timedelta(days=1),
        }
        return durations.get(period, timedelta(hours=1))
    
    def get_usage_metrics(self, user=None, period: str = 'daily') -> Dict[str, Any]:
        """Get API usage metrics"""
        
        from .marketplace_models import APIUsageLog, APIUsageMetrics
        from django.db.models import Avg, Count, Max, Min
        
        today = timezone.now().date()
        
        if period == 'hourly':
            start = timezone.now() - timedelta(hours=1)
        elif period == 'daily':
            start = timezone.now() - timedelta(days=1)
        else:
            start = timezone.now() - timedelta(days=7)
        
        logs = APIUsageLog.objects.filter(created_at__gte=start)
        if user:
            logs = logs.filter(user=user)
        
        metrics = logs.aggregate(
            total=Count('id'),
            avg_response_time=Avg('response_time_ms'),
            max_response_time=Max('response_time_ms'),
            min_response_time=Min('response_time_ms'),
        )
        
        successful = logs.filter(status_code__lt=400).count()
        failed = logs.filter(status_code__gte=400).count()
        rate_limited = logs.filter(was_rate_limited=True).count()
        
        # Endpoint breakdown
        endpoint_breakdown = list(
            logs.values('endpoint').annotate(count=Count('id')).order_by('-count')[:10]
        )
        
        # Status code breakdown
        status_breakdown = list(
            logs.values('status_code').annotate(count=Count('id')).order_by('-count')
        )
        
        return {
            'period': period,
            'start': start.isoformat(),
            'total_requests': metrics['total'] or 0,
            'successful_requests': successful,
            'failed_requests': failed,
            'rate_limited_requests': rate_limited,
            'avg_response_time_ms': int(metrics['avg_response_time'] or 0),
            'max_response_time_ms': metrics['max_response_time'] or 0,
            'min_response_time_ms': metrics['min_response_time'] or 0,
            'endpoint_breakdown': endpoint_breakdown,
            'status_breakdown': status_breakdown,
        }
    
    def create_rate_limit(self, user=None, api_key: str = None,
                         limit: int = 1000, period: str = 'hour') -> Dict[str, Any]:
        """Create or update a rate limit"""
        
        from .marketplace_models import APIRateLimit
        
        if user:
            rate_limit, created = APIRateLimit.objects.update_or_create(
                user=user,
                defaults={
                    'requests_limit': limit,
                    'period': period,
                    'is_active': True,
                }
            )
        elif api_key:
            rate_limit, created = APIRateLimit.objects.update_or_create(
                api_key=api_key,
                defaults={
                    'requests_limit': limit,
                    'period': period,
                    'is_active': True,
                }
            )
        else:
            return {'error': 'User or API key required'}
        
        return {
            'rate_limit_id': str(rate_limit.id),
            'limit': rate_limit.requests_limit,
            'period': rate_limit.period,
            'created': created,
        }
