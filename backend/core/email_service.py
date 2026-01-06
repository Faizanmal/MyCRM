"""
Email Integration Module
Handles email sending, templates, tracking, and integration with email providers
"""

import logging
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template
from django.utils import timezone

User = get_user_model()
logger = logging.getLogger(__name__)


class EmailService:
    """Core email service"""

    @staticmethod
    def send_email(to_emails, subject, body, from_email=None, html_body=None,
                   attachments=None, cc=None, bcc=None, template_id=None,
                   context=None, track=True, user=None):
        """
        Send email with optional tracking

        Args:
            to_emails: List of recipient emails or single email
            subject: Email subject
            body: Plain text body
            from_email: Sender email (default: settings.DEFAULT_FROM_EMAIL)
            html_body: HTML body (optional)
            attachments: List of attachment file paths
            cc: CC recipients
            bcc: BCC recipients
            template_id: Email template ID (optional)
            context: Template context variables
            track: Whether to track email opens/clicks
            user: User sending the email

        Returns:
            EmailLog instance
        """
        if isinstance(to_emails, str):
            to_emails = [to_emails]

        from_email = from_email or settings.DEFAULT_FROM_EMAIL or 'noreply@mycrm.com'

        # Use template if provided
        if template_id:
            subject, body, html_body = EmailTemplateManager.render_template(
                template_id, context or {}
            )

        # Add tracking if enabled
        if track and html_body:
            tracking_id = EmailTracker.create_tracking_id()
            html_body = EmailTracker.inject_tracking_pixel(html_body, tracking_id)
        else:
            tracking_id = None

        # Create email message
        msg = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=from_email,
            to=to_emails,
            cc=cc,
            bcc=bcc
        )

        if html_body:
            msg.attach_alternative(html_body, "text/html")

        # Attach files
        if attachments:
            for attachment_path in attachments:
                msg.attach_file(attachment_path)

        # Send email
        try:
            msg.send()
            status = 'sent'
            error_message = None
            logger.info(f"Email sent to {', '.join(to_emails)}")
        except Exception as e:
            status = 'failed'
            error_message = str(e)
            logger.error(f"Failed to send email: {str(e)}")

        # Log email
        from .models import EmailLog
        email_log = EmailLog.objects.create(
            to_emails=to_emails,
            cc_emails=cc or [],
            bcc_emails=bcc or [],
            subject=subject,
            body=body,
            html_body=html_body or '',
            status=status,
            error_message=error_message,
            tracking_id=tracking_id,
            sent_by=user
        )

        return email_log

    @staticmethod
    def send_bulk_email(recipients, subject, body, **kwargs):
        """
        Send bulk emails

        Args:
            recipients: List of email addresses
            subject: Email subject
            body: Email body
            **kwargs: Additional email parameters

        Returns:
            List of EmailLog instances
        """
        logs = []
        for recipient in recipients:
            log = EmailService.send_email(
                to_emails=[recipient],
                subject=subject,
                body=body,
                **kwargs
            )
            logs.append(log)

        logger.info(f"Sent bulk email to {len(recipients)} recipients")
        return logs


class EmailTemplateManager:
    """Manage email templates"""

    @staticmethod
    def render_template(template_id, context):
        """
        Render email template with context

        Args:
            template_id: Template UUID or ID
            context: Dict of template variables

        Returns:
            Tuple of (subject, plain_text, html)
        """
        from core.models import NotificationTemplate

        template = NotificationTemplate.objects.get(id=template_id)

        # Render subject
        subject_template = Template(template.subject_template)
        subject = subject_template.render(Context(context))

        # Render body
        body_template = Template(template.body_template)
        body = body_template.render(Context(context))

        # Convert to HTML if needed
        html = EmailTemplateManager._text_to_html(body)

        return subject, body, html

    @staticmethod
    def _text_to_html(text):
        """Convert plain text to HTML"""
        # Simple text to HTML conversion
        html = text.replace('\n', '<br>')
        return f"<html><body>{html}</body></html>"

    @staticmethod
    def create_template(name, subject, body, template_type='email', variables=None, user=None):
        """
        Create a new email template

        Args:
            name: Template name
            subject: Subject template
            body: Body template
            template_type: Type of template
            variables: List of available variables
            user: User creating the template

        Returns:
            NotificationTemplate instance
        """
        from core.models import NotificationTemplate

        template = NotificationTemplate.objects.create(
            name=name,
            notification_type=template_type,
            subject_template=subject,
            body_template=body,
            variables=variables or [],
            created_by=user
        )

        logger.info(f"Created email template: {name}")
        return template


class EmailTracker:
    """Track email opens and clicks"""

    @staticmethod
    def create_tracking_id():
        """Generate unique tracking ID"""
        import uuid
        return str(uuid.uuid4())

    @staticmethod
    def inject_tracking_pixel(html_body, tracking_id):
        """Inject tracking pixel into HTML email"""
        tracking_url = f"{settings.BASE_URL}/api/email/track/open/{tracking_id}/"
        tracking_pixel = f'<img src="{tracking_url}" width="1" height="1" alt="" />'

        # Insert before closing body tag
        if '</body>' in html_body:
            html_body = html_body.replace('</body>', f'{tracking_pixel}</body>')
        else:
            html_body += tracking_pixel

        return html_body

    @staticmethod
    def track_open(tracking_id):
        """Record email open"""
        from .models import EmailLog

        try:
            email_log = EmailLog.objects.get(tracking_id=tracking_id)
            if not email_log.opened_at:
                email_log.opened_at = timezone.now()
                email_log.open_count = 1
            else:
                email_log.open_count += 1
            email_log.save()

            logger.info(f"Email opened: {tracking_id}")
        except EmailLog.DoesNotExist:
            logger.warning(f"Email log not found for tracking ID: {tracking_id}")

    @staticmethod
    def track_click(tracking_id, url):
        """Record link click"""
        from .models import EmailClick, EmailLog

        try:
            email_log = EmailLog.objects.get(tracking_id=tracking_id)

            EmailClick.objects.create(
                email_log=email_log,
                url=url
            )

            email_log.click_count += 1
            email_log.save()

            logger.info(f"Email link clicked: {tracking_id} - {url}")
        except EmailLog.DoesNotExist:
            logger.warning(f"Email log not found for tracking ID: {tracking_id}")


class EmailValidator:
    """Validate email addresses"""

    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    @staticmethod
    def is_valid(email):
        """Check if email is valid"""
        return bool(EmailValidator.EMAIL_REGEX.match(email))

    @staticmethod
    def validate_bulk(emails):
        """
        Validate list of emails

        Returns:
            Tuple of (valid_emails, invalid_emails)
        """
        valid = []
        invalid = []

        for email in emails:
            if EmailValidator.is_valid(email):
                valid.append(email)
            else:
                invalid.append(email)

        return valid, invalid


class EmailCampaignManager:
    """Manage email campaigns"""

    @staticmethod
    def create_campaign(name, template_id, recipient_list, schedule_time=None, user=None):
        """
        Create email campaign

        Args:
            name: Campaign name
            template_id: Email template ID
            recipient_list: List of recipients or queryset
            schedule_time: When to send (None = send now)
            user: User creating campaign

        Returns:
            EmailCampaign instance
        """
        from .models import EmailCampaign

        campaign = EmailCampaign.objects.create(
            name=name,
            template_id=template_id,
            recipient_count=len(recipient_list) if isinstance(recipient_list, list) else recipient_list.count(),
            scheduled_time=schedule_time,
            status='scheduled' if schedule_time else 'draft',
            created_by=user
        )

        # Store recipients
        campaign.recipients = recipient_list if isinstance(recipient_list, list) else list(recipient_list.values_list('email', flat=True))
        campaign.save()

        logger.info(f"Created email campaign: {name}")
        return campaign

    @staticmethod
    def send_campaign(campaign_id):
        """Send email campaign"""
        from .models import EmailCampaign

        campaign = EmailCampaign.objects.get(id=campaign_id)
        campaign.status = 'sending'
        campaign.started_at = timezone.now()
        campaign.save()

        # Send emails in parallel
        email_logs = []
        for recipient in campaign.recipients:
            log = EmailService.send_email(
                to_emails=[recipient],
                template_id=campaign.template_id,
                context={},
                user=campaign.created_by
            )
            email_logs.append(log)

        campaign.status = 'sent'
        campaign.sent_count = len(email_logs)
        campaign.completed_at = timezone.now()
        campaign.save()

        logger.info(f"Campaign sent: {campaign.name} - {len(email_logs)} emails")
        return campaign


class EmailParser:
    """Parse incoming emails"""

    @staticmethod
    def parse_email(raw_email):
        """
        Parse raw email content

        Returns:
            Dict with email components
        """
        import email
        from email.header import decode_header as email_decode_header

        msg = email.message_from_string(raw_email)

        # Decode subject
        subject = EmailParser._decode_header(msg['Subject'], email_decode_header)

        # Get sender
        from_email = msg['From']

        # Get recipients
        to_emails = msg['To'].split(',') if msg['To'] else []

        # Get body
        body = EmailParser._get_email_body(msg)

        return {
            'subject': subject,
            'from': from_email,
            'to': to_emails,
            'body': body,
            'date': msg['Date']
        }

    @staticmethod
    def _decode_header(header, decode_header_func):
        """Decode email header"""
        if not header:
            return ''

        decoded = decode_header_func(header)
        return ''.join([
            text.decode(encoding or 'utf-8') if isinstance(text, bytes) else text
            for text, encoding in decoded
        ])

    @staticmethod
    def _get_email_body(msg):
        """Extract email body"""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    return part.get_payload(decode=True).decode()
        else:
            return msg.get_payload(decode=True).decode()

        return ''
