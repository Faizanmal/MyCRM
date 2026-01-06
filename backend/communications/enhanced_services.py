"""
Enhanced Communication Hub Services
"""

from datetime import datetime
from typing import Any

import openai
from django.conf import settings
from django.db.models import Avg, Q, Sum
from django.utils import timezone


class UnifiedInboxService:
    """Service for managing the unified inbox"""

    def __init__(self, user):
        self.user = user

    def get_inbox_summary(self) -> dict[str, Any]:
        """Get inbox summary with counts by channel and status"""
        from .enhanced_models import UnifiedInboxMessage

        messages = UnifiedInboxMessage.objects.filter(user=self.user)

        # Count by status
        status_counts = {}
        for status, _ in UnifiedInboxMessage.STATUS_CHOICES:
            status_counts[status] = messages.filter(status=status).count()

        # Count by channel
        channel_counts = {}
        for channel, _ in UnifiedInboxMessage.CHANNEL_TYPES:
            channel_counts[channel] = messages.filter(channel=channel).count()

        # Unread by priority
        priority_unread = {}
        for priority, _ in UnifiedInboxMessage.PRIORITY_CHOICES:
            priority_unread[priority] = messages.filter(
                status='unread', priority=priority
            ).count()

        return {
            'total': messages.count(),
            'unread': status_counts.get('unread', 0),
            'by_status': status_counts,
            'by_channel': channel_counts,
            'unread_by_priority': priority_unread,
            'starred': messages.filter(is_starred=True).count(),
            'snoozed': messages.filter(status='snoozed').count(),
        }

    def search_inbox(
        self,
        query: str = '',
        channels: list[str] = None,
        status: str = None,
        priority: str = None,
        labels: list[str] = None,
        contact_id: str = None,
        from_date: datetime = None,
        to_date: datetime = None,
        starred_only: bool = False,
        limit: int = 50
    ) -> list[dict[str, Any]]:
        """Search inbox with multiple filters"""
        from .enhanced_models import UnifiedInboxMessage

        messages = UnifiedInboxMessage.objects.filter(user=self.user)

        if query:
            messages = messages.filter(
                Q(subject__icontains=query) |
                Q(body__icontains=query) |
                Q(from_name__icontains=query) |
                Q(from_address__icontains=query)
            )

        if channels:
            messages = messages.filter(channel__in=channels)

        if status:
            messages = messages.filter(status=status)

        if priority:
            messages = messages.filter(priority=priority)

        if labels:
            messages = messages.filter(labels__contains=labels)

        if contact_id:
            messages = messages.filter(contact_id=contact_id)

        if from_date:
            messages = messages.filter(received_at__gte=from_date)

        if to_date:
            messages = messages.filter(received_at__lte=to_date)

        if starred_only:
            messages = messages.filter(is_starred=True)

        return list(messages[:limit].values())

    def bulk_update_status(
        self, message_ids: list[str], status: str
    ) -> dict[str, Any]:
        """Bulk update message status"""
        from .enhanced_models import UnifiedInboxMessage

        messages = UnifiedInboxMessage.objects.filter(
            user=self.user, id__in=message_ids
        )

        update_fields = {'status': status}

        if status == 'read':
            update_fields['read_at'] = timezone.now()
        elif status == 'archived':
            pass  # Just change status

        updated = messages.update(**update_fields)

        return {'updated_count': updated}

    def apply_label(
        self, message_ids: list[str], label: str, remove: bool = False
    ) -> dict[str, Any]:
        """Add or remove label from messages"""
        from .enhanced_models import UnifiedInboxMessage

        messages = UnifiedInboxMessage.objects.filter(
            user=self.user, id__in=message_ids
        )

        updated = 0
        for message in messages:
            labels = message.labels or []
            if remove:
                if label in labels:
                    labels.remove(label)
                    message.labels = labels
                    message.save(update_fields=['labels'])
                    updated += 1
            else:
                if label not in labels:
                    labels.append(label)
                    message.labels = labels
                    message.save(update_fields=['labels'])
                    updated += 1

        return {'updated_count': updated}

    def snooze_message(
        self, message_id: str, snooze_until: datetime
    ) -> dict[str, Any]:
        """Snooze a message until specified time"""
        from .enhanced_models import UnifiedInboxMessage

        message = UnifiedInboxMessage.objects.get(
            id=message_id, user=self.user
        )

        message.status = 'snoozed'
        message.snoozed_until = snooze_until
        message.save(update_fields=['status', 'snoozed_until'])

        return {
            'message_id': str(message.id),
            'snoozed_until': snooze_until.isoformat()
        }

    def get_thread(self, thread_id: str) -> list[dict[str, Any]]:
        """Get all messages in a thread"""
        from .enhanced_models import UnifiedInboxMessage

        messages = UnifiedInboxMessage.objects.filter(
            user=self.user, thread_id=thread_id
        ).order_by('received_at')

        return list(messages.values())

    def link_to_crm(
        self,
        message_id: str,
        contact_id: str = None,
        lead_id: str = None,
        opportunity_id: str = None
    ) -> dict[str, Any]:
        """Link message to CRM objects"""
        from .enhanced_models import UnifiedInboxMessage

        message = UnifiedInboxMessage.objects.get(
            id=message_id, user=self.user
        )

        if contact_id:
            message.contact_id = contact_id
        if lead_id:
            message.lead_id = lead_id
        if opportunity_id:
            message.opportunity_id = opportunity_id

        message.save()

        return {'message_id': str(message.id), 'linked': True}

    def generate_ai_reply(self, message_id: str) -> dict[str, Any]:
        """Generate AI-suggested reply for a message"""
        from .enhanced_models import UnifiedInboxMessage

        message = UnifiedInboxMessage.objects.get(
            id=message_id, user=self.user
        )

        # Build context
        context = {
            'channel': message.channel,
            'from_name': message.from_name,
            'subject': message.subject,
            'body': message.body[:2000],
            'sentiment': message.sentiment,
        }

        # Get previous messages in thread for context
        if message.thread_id:
            thread_messages = UnifiedInboxMessage.objects.filter(
                thread_id=message.thread_id
            ).order_by('-received_at')[:5]
            context['thread_history'] = [
                {'direction': m.direction, 'body': m.body[:500]}
                for m in thread_messages
            ]

        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a helpful sales assistant. Generate a professional,
                        friendly reply to the incoming message. Keep it concise and focused
                        on moving the conversation forward."""
                    },
                    {
                        "role": "user",
                        "content": f"""Generate a reply for this {context['channel']} message:
                        From: {context['from_name']}
                        Subject: {context['subject']}
                        Message: {context['body']}

                        Sentiment: {context['sentiment'] or 'unknown'}"""
                    }
                ],
                max_tokens=500
            )

            suggested_reply = response.choices[0].message.content

            # Save the suggestion
            message.suggested_reply = suggested_reply
            message.save(update_fields=['suggested_reply'])

            return {
                'message_id': str(message.id),
                'suggested_reply': suggested_reply
            }

        except Exception as e:
            return {
                'message_id': str(message.id),
                'suggested_reply': '',
                'error': str(e)
            }


class MultiChannelCampaignService:
    """Service for managing multi-channel campaigns"""

    def __init__(self, user):
        self.user = user

    def create_campaign(
        self,
        name: str,
        channels: list[str],
        target_audience: dict[str, Any],
        goals: dict[str, Any] = None,
        budget: float = None
    ) -> dict[str, Any]:
        """Create a new multi-channel campaign"""
        from .enhanced_models import MultiChannelCampaign

        campaign = MultiChannelCampaign.objects.create(
            user=self.user,
            name=name,
            channels=channels,
            target_audience=target_audience,
            goals=goals or {},
            budget=budget
        )

        # Calculate target count based on audience criteria
        target_count = self._calculate_audience_size(target_audience)
        campaign.target_count = target_count
        campaign.save(update_fields=['target_count'])

        return {
            'id': str(campaign.id),
            'name': campaign.name,
            'target_count': target_count,
            'channels': channels
        }

    def _calculate_audience_size(
        self, criteria: dict[str, Any]
    ) -> int:
        """Calculate audience size based on criteria"""
        # This would query contacts/leads based on criteria
        # Simplified for now
        return 0

    def add_campaign_step(
        self,
        campaign_id: str,
        step_type: str,
        name: str,
        order: int,
        config: dict[str, Any] = None,
        subject: str = '',
        body: str = '',
        delay_days: int = 0,
        delay_hours: int = 0,
        conditions: list[dict] = None
    ) -> dict[str, Any]:
        """Add a step to a campaign"""
        from .enhanced_models import CampaignStep, MultiChannelCampaign

        campaign = MultiChannelCampaign.objects.get(
            id=campaign_id, user=self.user
        )

        step = CampaignStep.objects.create(
            campaign=campaign,
            step_type=step_type,
            name=name,
            order=order,
            config=config or {},
            subject=subject,
            body=body,
            delay_days=delay_days,
            delay_hours=delay_hours,
            conditions=conditions or []
        )

        return {
            'id': str(step.id),
            'campaign_id': str(campaign.id),
            'step_type': step_type,
            'name': name,
            'order': order
        }

    def update_step_order(
        self, campaign_id: str, step_orders: dict[str, int]
    ) -> dict[str, Any]:
        """Reorder campaign steps"""
        from .enhanced_models import CampaignStep, MultiChannelCampaign

        campaign = MultiChannelCampaign.objects.get(
            id=campaign_id, user=self.user
        )

        for step_id, order in step_orders.items():
            CampaignStep.objects.filter(
                id=step_id, campaign=campaign
            ).update(order=order)

        return {'updated': True}

    def start_campaign(self, campaign_id: str) -> dict[str, Any]:
        """Start a campaign"""
        from .enhanced_models import MultiChannelCampaign

        campaign = MultiChannelCampaign.objects.get(
            id=campaign_id, user=self.user
        )

        if campaign.status not in ['draft', 'scheduled', 'paused']:
            return {'error': 'Campaign cannot be started'}

        # Add recipients based on target audience
        recipients_added = self._add_recipients_from_audience(campaign)

        campaign.status = 'running'
        campaign.start_date = timezone.now()
        campaign.save(update_fields=['status', 'start_date'])

        return {
            'id': str(campaign.id),
            'status': 'running',
            'recipients_added': recipients_added
        }

    def _add_recipients_from_audience(
        self, campaign
    ) -> int:
        """Add recipients to campaign based on audience criteria"""
        # This would query contacts based on criteria and add them
        # Simplified implementation
        return 0

    def pause_campaign(self, campaign_id: str) -> dict[str, Any]:
        """Pause a running campaign"""
        from .enhanced_models import MultiChannelCampaign

        campaign = MultiChannelCampaign.objects.get(
            id=campaign_id, user=self.user
        )

        if campaign.status != 'running':
            return {'error': 'Campaign is not running'}

        campaign.status = 'paused'
        campaign.save(update_fields=['status'])

        return {'id': str(campaign.id), 'status': 'paused'}

    def get_campaign_analytics(
        self, campaign_id: str
    ) -> dict[str, Any]:
        """Get detailed analytics for a campaign"""
        from .enhanced_models import CampaignRecipient, CampaignStep, MultiChannelCampaign

        campaign = MultiChannelCampaign.objects.get(
            id=campaign_id, user=self.user
        )

        recipients = CampaignRecipient.objects.filter(campaign=campaign)
        steps = CampaignStep.objects.filter(campaign=campaign)

        # Overall metrics
        total_recipients = recipients.count()

        recipient_stats = recipients.aggregate(
            total_opens=Sum('opens'),
            total_clicks=Sum('clicks'),
            total_replies=Sum('replies'),
            total_conversions=Sum('conversions')
        )

        # Step-by-step metrics
        step_analytics = []
        for step in steps.order_by('order'):
            step_analytics.append({
                'id': str(step.id),
                'name': step.name,
                'type': step.step_type,
                'sent': step.sent_count,
                'delivered': step.delivered_count,
                'opened': step.opened_count,
                'clicked': step.clicked_count,
                'replied': step.replied_count,
                'open_rate': (step.opened_count / step.sent_count * 100) if step.sent_count > 0 else 0,
                'click_rate': (step.clicked_count / step.sent_count * 100) if step.sent_count > 0 else 0
            })

        # Recipient status breakdown
        status_breakdown = {}
        for status, _ in CampaignRecipient.STATUS_CHOICES:
            status_breakdown[status] = recipients.filter(status=status).count()

        return {
            'campaign_id': str(campaign.id),
            'campaign_name': campaign.name,
            'status': campaign.status,
            'total_recipients': total_recipients,
            'overall_metrics': {
                'sent': campaign.total_sent,
                'delivered': campaign.total_delivered,
                'opens': recipient_stats['total_opens'] or 0,
                'clicks': recipient_stats['total_clicks'] or 0,
                'replies': recipient_stats['total_replies'] or 0,
                'conversions': recipient_stats['total_conversions'] or 0,
            },
            'step_analytics': step_analytics,
            'recipient_status': status_breakdown,
            'budget': float(campaign.budget or 0),
            'spent': float(campaign.spent or 0)
        }

    def ab_test_step(
        self,
        campaign_id: str,
        step_id: str,
        variants: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Set up A/B test for a campaign step"""
        from .enhanced_models import CampaignStep

        step = CampaignStep.objects.get(
            id=step_id, campaign_id=campaign_id
        )

        step.step_type = 'ab_test'
        step.config = {
            'variants': variants,
            'split_ratio': [100 // len(variants)] * len(variants),
            'winner_metric': 'open_rate',
            'auto_select_winner': True,
            'winner_threshold': 0.95  # Statistical confidence
        }
        step.save()

        return {
            'step_id': str(step.id),
            'variants': len(variants),
            'status': 'configured'
        }


class EmailTrackingService:
    """Service for advanced email tracking"""

    def __init__(self, user):
        self.user = user

    def create_tracking(
        self,
        recipient_email: str,
        subject: str,
        contact_id: str = None
    ) -> dict[str, Any]:
        """Create tracking record for an email"""
        import uuid

        from .enhanced_models import AdvancedEmailTracking

        tracking_id = str(uuid.uuid4())

        AdvancedEmailTracking.objects.create(
            user=self.user,
            tracking_id=tracking_id,
            recipient_email=recipient_email,
            subject=subject,
            contact_id=contact_id,
            sent_at=timezone.now()
        )

        return {
            'tracking_id': tracking_id,
            'pixel_url': f'/api/track/open/{tracking_id}',
            'click_base_url': f'/api/track/click/{tracking_id}'
        }

    def record_event(
        self,
        tracking_id: str,
        event_type: str,
        url: str = None,
        device_info: dict[str, Any] = None,
        location_info: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Record a tracking event"""
        from .enhanced_models import AdvancedEmailTracking, EmailTrackingEvent

        tracking = AdvancedEmailTracking.objects.get(tracking_id=tracking_id)

        # Create event
        event = EmailTrackingEvent.objects.create(
            tracking=tracking,
            event_type=event_type,
            url=url or '',
            device_type=device_info.get('device_type', '') if device_info else '',
            browser=device_info.get('browser', '') if device_info else '',
            os=device_info.get('os', '') if device_info else '',
            user_agent=device_info.get('user_agent', '') if device_info else '',
            ip_address=location_info.get('ip') if location_info else None,
            country=location_info.get('country', '') if location_info else '',
            city=location_info.get('city', '') if location_info else ''
        )

        now = timezone.now()

        # Update tracking record
        if event_type == 'delivered':
            tracking.delivered = True
            tracking.delivered_at = now

        elif event_type == 'opened':
            tracking.opened = True
            tracking.open_count += 1
            if not tracking.first_opened_at:
                tracking.first_opened_at = now
                tracking.time_to_open_seconds = int(
                    (now - tracking.sent_at).total_seconds()
                )
            tracking.last_opened_at = now

            # Update device tracking
            if device_info:
                device = {
                    'type': device_info.get('device_type'),
                    'browser': device_info.get('browser'),
                    'os': device_info.get('os')
                }
                if device not in tracking.devices:
                    tracking.devices.append(device)

        elif event_type == 'clicked':
            tracking.clicked = True
            tracking.click_count += 1
            if not tracking.first_clicked_at:
                tracking.first_clicked_at = now
            tracking.last_clicked_at = now

            if url and url not in tracking.clicked_urls:
                tracking.clicked_urls.append(url)

        elif event_type == 'replied':
            tracking.replied = True
            tracking.replied_at = now

        elif event_type == 'bounced':
            tracking.bounced = True
            tracking.bounced_at = now

        elif event_type == 'unsubscribed':
            tracking.unsubscribed = True
            tracking.unsubscribed_at = now

        elif event_type == 'complained':
            tracking.complained = True
            tracking.complained_at = now

        # Recalculate engagement score
        tracking.calculate_engagement_score()
        tracking.save()

        return {'recorded': True, 'event_id': str(event.id)}

    def get_engagement_analytics(
        self,
        from_date: datetime = None,
        to_date: datetime = None
    ) -> dict[str, Any]:
        """Get email engagement analytics"""
        from .enhanced_models import AdvancedEmailTracking

        tracking = AdvancedEmailTracking.objects.filter(user=self.user)

        if from_date:
            tracking = tracking.filter(sent_at__gte=from_date)
        if to_date:
            tracking = tracking.filter(sent_at__lte=to_date)

        total = tracking.count()

        if total == 0:
            return {'total_emails': 0}

        delivered = tracking.filter(delivered=True).count()
        opened = tracking.filter(opened=True).count()
        clicked = tracking.filter(clicked=True).count()
        replied = tracking.filter(replied=True).count()
        bounced = tracking.filter(bounced=True).count()
        unsubscribed = tracking.filter(unsubscribed=True).count()

        avg_metrics = tracking.aggregate(
            avg_engagement=Avg('engagement_score'),
            avg_time_to_open=Avg('time_to_open_seconds'),
            avg_open_count=Avg('open_count'),
            avg_click_count=Avg('click_count')
        )

        return {
            'total_emails': total,
            'delivery_rate': delivered / total * 100,
            'open_rate': opened / total * 100,
            'click_rate': clicked / total * 100,
            'reply_rate': replied / total * 100,
            'bounce_rate': bounced / total * 100,
            'unsubscribe_rate': unsubscribed / total * 100,
            'avg_engagement_score': float(avg_metrics['avg_engagement'] or 0),
            'avg_time_to_open_minutes': (avg_metrics['avg_time_to_open'] or 0) / 60,
            'avg_opens_per_email': float(avg_metrics['avg_open_count'] or 0),
            'avg_clicks_per_email': float(avg_metrics['avg_click_count'] or 0)
        }

    def predict_unsubscribe_risk(
        self, contact_id: str
    ) -> dict[str, Any]:
        """Predict unsubscribe risk for a contact"""
        from .enhanced_models import AdvancedEmailTracking

        # Get recent tracking data for the contact
        tracking = AdvancedEmailTracking.objects.filter(
            user=self.user,
            contact_id=contact_id
        ).order_by('-sent_at')[:20]

        if not tracking.exists():
            return {'risk': 'unknown', 'score': 0}

        # Analyze patterns
        total = tracking.count()
        recent_opened = tracking[:5].filter(opened=True).count()
        overall_opened = tracking.filter(opened=True).count()
        unsubscribed_before = tracking.filter(unsubscribed=True).exists()
        complained_before = tracking.filter(complained=True).exists()

        # Calculate risk score
        risk_score = 0

        # Declining engagement
        if recent_opened < overall_opened / total * 5:
            risk_score += 30

        # Low overall engagement
        if overall_opened / total < 0.2:
            risk_score += 25

        # Previous complaints
        if complained_before:
            risk_score += 40

        # Previous unsubscribe attempts
        if unsubscribed_before:
            risk_score += 50

        # Determine risk level
        if risk_score >= 70:
            risk_level = 'high'
        elif risk_score >= 40:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        return {
            'contact_id': contact_id,
            'risk': risk_level,
            'score': min(100, risk_score),
            'factors': {
                'declining_engagement': recent_opened < overall_opened / total * 5 if total > 0 else False,
                'low_overall_engagement': overall_opened / total < 0.2 if total > 0 else False,
                'previous_complaints': complained_before,
                'previous_unsubscribes': unsubscribed_before
            }
        }

    def get_best_send_time(
        self, contact_id: str = None
    ) -> dict[str, Any]:
        """Analyze best time to send emails"""
        from .enhanced_models import EmailTrackingEvent

        events = EmailTrackingEvent.objects.filter(
            tracking__user=self.user,
            event_type='opened'
        )

        if contact_id:
            events = events.filter(tracking__contact_id=contact_id)

        # Aggregate opens by hour and day
        hourly_opens = {}
        daily_opens = {}

        for event in events:
            hour = event.created_at.hour
            day = event.created_at.strftime('%A')

            hourly_opens[hour] = hourly_opens.get(hour, 0) + 1
            daily_opens[day] = daily_opens.get(day, 0) + 1

        best_hour = max(hourly_opens, key=hourly_opens.get) if hourly_opens else 9
        best_day = max(daily_opens, key=daily_opens.get) if daily_opens else 'Tuesday'

        return {
            'best_hour': best_hour,
            'best_day': best_day,
            'hourly_distribution': hourly_opens,
            'daily_distribution': daily_opens
        }


class CommunicationPreferenceService:
    """Service for managing communication preferences"""

    def get_or_create_preferences(self, contact_id: str) -> dict[str, Any]:
        """Get or create communication preferences for a contact"""
        from .enhanced_models import CommunicationPreference

        prefs, created = CommunicationPreference.objects.get_or_create(
            contact_id=contact_id
        )

        return {
            'id': str(prefs.id),
            'contact_id': contact_id,
            'email_enabled': prefs.email_enabled,
            'sms_enabled': prefs.sms_enabled,
            'phone_enabled': prefs.phone_enabled,
            'social_enabled': prefs.social_enabled,
            'email_frequency': prefs.email_frequency,
            'opted_in_topics': prefs.opted_in_topics,
            'opted_out_topics': prefs.opted_out_topics,
            'best_contact_times': prefs.best_contact_times,
            'most_engaged_channel': prefs.most_engaged_channel,
            'global_unsubscribe': prefs.global_unsubscribe,
            'created': created
        }

    def update_preferences(
        self,
        contact_id: str,
        **preferences
    ) -> dict[str, Any]:
        """Update communication preferences"""
        from .enhanced_models import CommunicationPreference

        prefs = CommunicationPreference.objects.get(contact_id=contact_id)

        for key, value in preferences.items():
            if hasattr(prefs, key):
                setattr(prefs, key, value)

        prefs.save()

        return {'updated': True}

    def handle_unsubscribe(
        self,
        contact_id: str,
        reason: str = '',
        topics: list[str] = None
    ) -> dict[str, Any]:
        """Handle unsubscribe request"""
        from .enhanced_models import CommunicationPreference

        prefs, _ = CommunicationPreference.objects.get_or_create(
            contact_id=contact_id
        )

        if topics:
            # Topic-specific unsubscribe
            for topic in topics:
                if topic not in prefs.opted_out_topics:
                    prefs.opted_out_topics.append(topic)
                if topic in prefs.opted_in_topics:
                    prefs.opted_in_topics.remove(topic)
        else:
            # Global unsubscribe
            prefs.global_unsubscribe = True
            prefs.email_enabled = False

        prefs.unsubscribed_at = timezone.now()
        prefs.unsubscribe_reason = reason
        prefs.save()

        return {
            'contact_id': contact_id,
            'global_unsubscribe': prefs.global_unsubscribe,
            'opted_out_topics': prefs.opted_out_topics
        }

    def analyze_engagement_patterns(
        self, contact_id: str
    ) -> dict[str, Any]:
        """Analyze engagement patterns for a contact"""
        from .enhanced_models import AdvancedEmailTracking, UnifiedInboxMessage

        # Email engagement
        email_tracking = AdvancedEmailTracking.objects.filter(
            contact_id=contact_id
        ).order_by('-sent_at')[:50]

        # Message engagement
        messages = UnifiedInboxMessage.objects.filter(
            contact_id=contact_id
        ).order_by('-received_at')[:50]

        # Calculate channel engagement
        channel_engagement = {}
        for msg in messages:
            channel = msg.channel
            if channel not in channel_engagement:
                channel_engagement[channel] = {'count': 0, 'replied': 0}
            channel_engagement[channel]['count'] += 1
            if msg.status == 'replied':
                channel_engagement[channel]['replied'] += 1

        # Find most engaged channel
        most_engaged = None
        highest_rate = 0
        for channel, stats in channel_engagement.items():
            rate = stats['replied'] / stats['count'] if stats['count'] > 0 else 0
            if rate > highest_rate:
                highest_rate = rate
                most_engaged = channel

        # Calculate response times
        response_times = []
        for msg in messages.filter(direction='inbound', replied_at__isnull=False):
            if msg.received_at and msg.replied_at:
                delta = (msg.replied_at - msg.received_at).total_seconds() / 3600
                response_times.append(delta)

        avg_response_time = sum(response_times) / len(response_times) if response_times else None

        return {
            'contact_id': contact_id,
            'channel_engagement': channel_engagement,
            'most_engaged_channel': most_engaged,
            'avg_response_time_hours': avg_response_time,
            'total_messages': messages.count(),
            'total_emails_tracked': email_tracking.count()
        }
