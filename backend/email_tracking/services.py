"""
Email Tracking Services
Core email sending and tracking logic
"""

import contextlib
import re
from datetime import timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.template import Context, Template
from django.utils import timezone

from .models import EmailTemplate, TrackedEmail


class EmailTrackingService:
    """Service for sending and tracking emails"""

    def __init__(self):
        self.tracking_base_url = getattr(settings, 'EMAIL_TRACKING_URL', 'http://localhost:8000/api/v1/email-tracking')

    def send_email(self, sender, to_email, subject, body_html, to_name='', body_text='',
                   contact_id=None, opportunity_id=None, template_id=None, schedule_at=None):
        """
        Create and send a tracked email
        """
        from contact_management.models import Contact
        from opportunity_management.models import Opportunity

        # Get related objects
        contact = None
        if contact_id:
            with contextlib.suppress(Contact.DoesNotExist):
                contact = Contact.objects.get(id=contact_id)

        opportunity = None
        if opportunity_id:
            with contextlib.suppress(Opportunity.DoesNotExist):
                opportunity = Opportunity.objects.get(id=opportunity_id)

        template = None
        if template_id:
            try:
                template = EmailTemplate.objects.get(id=template_id)
                template.times_used += 1
                template.save()
            except EmailTemplate.DoesNotExist:
                pass

        # Create tracked email
        email = TrackedEmail.objects.create(
            sender=sender,
            from_email=sender.email,
            from_name=sender.get_full_name(),
            to_email=to_email,
            to_name=to_name,
            contact=contact,
            opportunity=opportunity,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            template=template,
            scheduled_at=schedule_at,
            status='scheduled' if schedule_at else 'draft',
        )

        # Add tracking to email
        tracked_html = self._add_tracking(email, body_html)
        email.body_html = tracked_html
        email.save()

        # Send immediately if not scheduled
        if not schedule_at:
            self._send_email(email)

        return email

    def _add_tracking(self, email, html_content):
        """Add tracking pixel and wrap links"""

        # Add tracking pixel before </body>
        tracking_pixel = f'<img src="{self.tracking_base_url}/pixel/{email.tracking_id}/" width="1" height="1" style="display:none;" />'

        if '</body>' in html_content.lower():
            html_content = re.sub(
                r'(</body>)',
                f'{tracking_pixel}\\1',
                html_content,
                flags=re.IGNORECASE
            )
        else:
            html_content += tracking_pixel

        # Wrap all links for click tracking
        def wrap_link(match):
            url = match.group(2)
            # Don't wrap mailto: or tel: links
            if url.startswith(('mailto:', 'tel:', '#')):
                return match.group(0)

            tracking_url = f"{self.tracking_base_url}/click/{email.tracking_id}/?url={urlencode({'': url})[1:]}"
            return f'{match.group(1)}"{tracking_url}"'

        html_content = re.sub(
            r'(href=)["\']([^"\']+)["\']',
            wrap_link,
            html_content
        )

        return html_content

    def _send_email(self, email):
        """Actually send the email via configured provider"""
        from django.conf import settings

        try:
            provider = getattr(settings, 'EMAIL_PROVIDER', 'django')

            if provider == 'sendgrid':
                # SendGrid integration
                success = self._send_via_sendgrid(email)
            elif provider == 'ses':
                # AWS SES integration
                success = self._send_via_ses(email)
            else:
                # Default Django email backend
                success = self._send_via_django(email)

            if success:
                email.status = 'sent'
                email.sent_at = timezone.now()
                email.save()
                return True
            else:
                email.status = 'failed'
                email.metadata['error'] = 'Failed to send via provider'
                email.save()
                return False

        except Exception as e:
            email.status = 'failed'
            email.metadata['error'] = str(e)
            email.save()
            return False

    def _send_via_django(self, email):
        """Send using Django's default email backend"""
        from django.core.mail import EmailMultiAlternatives
        from django.utils.html import strip_tags

        msg = EmailMultiAlternatives(
            subject=email.subject,
            body=email.body_text or strip_tags(email.body_html),
            from_email=f"{email.from_name} <{email.from_email}>" if email.from_name else email.from_email,
            to=[email.to_email],
        )

        if email.body_html:
            msg.attach_alternative(email.body_html, "text/html")

        msg.send()
        return True

    def _send_via_sendgrid(self, email):
        """Send using SendGrid API"""
        import json

        from django.conf import settings

        try:
            import requests

            api_key = getattr(settings, 'SENDGRID_API_KEY', None)
            if not api_key:
                # Fallback to Django email
                return self._send_via_django(email)

            data = {
                "personalizations": [{
                    "to": [{"email": email.to_email, "name": email.to_name or ""}],
                    "subject": email.subject
                }],
                "from": {
                    "email": email.from_email,
                    "name": email.from_name or ""
                },
                "content": [
                    {"type": "text/plain", "value": email.body_text or ""},
                    {"type": "text/html", "value": email.body_html}
                ]
            }

            response = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                data=json.dumps(data)
            )

            return response.status_code in [200, 202]

        except ImportError:
            # requests not installed, fallback to Django
            return self._send_via_django(email)

    def _send_via_ses(self, email):
        """Send using AWS SES"""
        from django.conf import settings

        try:
            import boto3
            from botocore.exceptions import ClientError

            region = getattr(settings, 'AWS_SES_REGION', 'us-east-1')
            client = boto3.client('ses', region_name=region)

            response = client.send_email(
                Source=f"{email.from_name} <{email.from_email}>" if email.from_name else email.from_email,
                Destination={
                    'ToAddresses': [email.to_email]
                },
                Message={
                    'Subject': {'Data': email.subject},
                    'Body': {
                        'Text': {'Data': email.body_text or ''},
                        'Html': {'Data': email.body_html}
                    }
                }
            )

            return response.get('MessageId') is not None

        except (ImportError, ClientError):
            # boto3 not installed or SES error, fallback to Django
            return self._send_via_django(email)

    def render_template(self, template, context_data):
        """Render email template with context"""
        subject = Template(template.subject).render(Context(context_data))
        body_html = Template(template.body_html).render(Context(context_data))
        body_text = Template(template.body_text).render(Context(context_data)) if template.body_text else ''

        return subject, body_html, body_text

    def get_contact_context(self, contact):
        """Get template context from contact"""
        return {
            'first_name': contact.first_name,
            'last_name': contact.last_name,
            'full_name': contact.full_name,
            'email': contact.email,
            'company': contact.company_name or '',
            'job_title': contact.job_title or '',
            'phone': contact.phone or '',
        }


class SequenceProcessor:
    """Process email sequences"""

    def process_pending_steps(self):
        """Process all pending sequence steps"""
        from .models import SequenceEnrollment

        now = timezone.now()

        # Get enrollments ready for next action
        pending = SequenceEnrollment.objects.filter(
            status='active',
            next_action_at__lte=now
        ).select_related('sequence', 'contact')

        processed = 0

        for enrollment in pending:
            try:
                self._process_enrollment(enrollment)
                processed += 1
            except Exception:
                # Log error but continue processing others
                continue

        return processed

    def _process_enrollment(self, enrollment):
        """Process a single enrollment"""
        from .models import SequenceStep

        sequence = enrollment.sequence

        # Get current step
        try:
            step = sequence.steps.get(order=enrollment.current_step)
        except SequenceStep.DoesNotExist:
            # Sequence completed
            enrollment.status = 'completed'
            enrollment.completed_at = timezone.now()
            enrollment.save()
            sequence.total_completed += 1
            sequence.save()
            return

        if step.step_type == 'email':
            self._send_sequence_email(enrollment, step)
        elif step.step_type == 'task':
            self._create_sequence_task(enrollment, step)

        # Move to next step
        next_step = sequence.steps.filter(order__gt=step.order).order_by('order').first()

        if next_step:
            enrollment.current_step = next_step.order

            # Calculate next action time
            if next_step.step_type == 'wait':
                enrollment.next_action_at = timezone.now() + timedelta(
                    days=next_step.delay_days,
                    hours=next_step.delay_hours
                )
            else:
                enrollment.next_action_at = timezone.now()
        else:
            enrollment.status = 'completed'
            enrollment.completed_at = timezone.now()
            sequence.total_completed += 1
            sequence.save()

        enrollment.save()

    def _send_sequence_email(self, enrollment, step):
        """Send email for sequence step"""
        service = EmailTrackingService()

        # Get template or use override
        subject = step.subject_override or (step.template.subject if step.template else 'Follow up')
        body_html = step.body_override or (step.template.body_html if step.template else '')

        # Render with contact context
        context = service.get_contact_context(enrollment.contact)

        subject = Template(subject).render(Context(context))
        body_html = Template(body_html).render(Context(context))

        # Send email
        service.send_email(
            sender=enrollment.enrolled_by,
            to_email=enrollment.contact.email,
            to_name=enrollment.contact.full_name,
            subject=subject,
            body_html=body_html,
            contact_id=enrollment.contact.id,
        )

        # Update stats
        step.sent_count += 1
        step.save()

    def _create_sequence_task(self, enrollment, step):
        """Create task for sequence step"""
        from task_management.models import Task

        context = {
            'first_name': enrollment.contact.first_name,
            'last_name': enrollment.contact.last_name,
            'company': enrollment.contact.company_name or '',
        }

        title = Template(step.task_title).render(Context(context))
        description = Template(step.task_description).render(Context(context))

        Task.objects.create(
            title=title,
            description=description,
            assigned_to=enrollment.enrolled_by,
            contact=enrollment.contact,
            due_date=timezone.now().date() + timedelta(days=1),
            priority='high',
        )
