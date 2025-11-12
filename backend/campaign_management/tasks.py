"""
Celery tasks for campaign management
"""

from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_campaign_emails(self, campaign_id):
    """
    Send emails for a campaign
    """
    from .models import Campaign, CampaignRecipient
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        
        # Get all pending recipients
        recipients = campaign.recipients.filter(status='pending')
        
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        
        for recipient in recipients:
            try:
                # Personalize content
                content = campaign.content_html
                # Replace variables like {{first_name}} with actual values
                if recipient.contact:
                    content = content.replace('{{first_name}}', recipient.contact.first_name or '')
                    content = content.replace('{{last_name}}', recipient.contact.last_name or '')
                elif recipient.lead:
                    content = content.replace('{{first_name}}', recipient.lead.name.split()[0] if recipient.lead.name else '')
                
                # Create email
                message = Mail(
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to_emails=recipient.email,
                    subject=campaign.subject,
                    html_content=content
                )
                
                # Send via SendGrid
                response = sg.send(message)
                
                if response.status_code in [200, 202]:
                    recipient.status = 'sent'
                    recipient.sent_at = timezone.now()
                    campaign.sent_count += 1
                else:
                    recipient.status = 'bounced'
                    recipient.error_message = f"SendGrid error: {response.status_code}"
                    campaign.bounced_count += 1
                
                recipient.save()
                
            except Exception as e:
                logger.error(f"Error sending to {recipient.email}: {str(e)}")
                recipient.status = 'bounced'
                recipient.error_message = str(e)
                recipient.save()
                campaign.bounced_count += 1
        
        # Update campaign status
        if campaign.recipients.filter(status='pending').count() == 0:
            campaign.status = 'completed'
            campaign.completed_at = timezone.now()
        
        campaign.save()
        
        logger.info(f"Campaign {campaign.id} sent to {campaign.sent_count} recipients")
        
    except Campaign.DoesNotExist:
        logger.error(f"Campaign {campaign_id} not found")
    except Exception as exc:
        logger.error(f"Error in send_campaign_emails: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * 5)  # Retry after 5 minutes


@shared_task
def process_campaign_segment(segment_id):
    """
    Calculate contact count for a segment based on filters
    """
    from .models import CampaignSegment, CampaignRecipient
    from contact_management.models import Contact
    from lead_management.models import Lead
    
    try:
        segment = CampaignSegment.objects.get(id=segment_id)
        filters = segment.filters
        
        # Query contacts and leads based on filters
        contacts = Contact.objects.all()
        leads = Lead.objects.all()
        
        # Apply filters dynamically
        # Example: filters = {'status': 'active', 'industry': 'Technology'}
        if 'status' in filters:
            contacts = contacts.filter(status=filters['status'])
        
        if 'lead_status' in filters:
            leads = leads.filter(status=filters['lead_status'])
        
        # Calculate total count
        total_count = contacts.count() + leads.count()
        
        segment.contact_count = total_count
        segment.save()
        
        logger.info(f"Segment {segment_id} processed: {total_count} contacts")
        
    except CampaignSegment.DoesNotExist:
        logger.error(f"Segment {segment_id} not found")
    except Exception as e:
        logger.error(f"Error processing segment: {str(e)}")


@shared_task
def create_campaign_recipients(campaign_id, segment_id=None):
    """
    Create recipient records for a campaign based on segment
    """
    from .models import Campaign, CampaignSegment, CampaignRecipient
    from contact_management.models import Contact
    from lead_management.models import Lead
    
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        
        if segment_id:
            segment = CampaignSegment.objects.get(id=segment_id)
            filters = segment.filters
        else:
            filters = {}
        
        # Get contacts and leads
        contacts = Contact.objects.all()
        leads = Lead.objects.all()
        
        # Apply filters
        if filters:
            # Apply dynamic filters here
            pass
        
        # Create recipients
        recipient_count = 0
        
        for contact in contacts:
            if contact.email:
                CampaignRecipient.objects.get_or_create(
                    campaign=campaign,
                    email=contact.email,
                    defaults={'contact': contact}
                )
                recipient_count += 1
        
        for lead in leads:
            if lead.email:
                CampaignRecipient.objects.get_or_create(
                    campaign=campaign,
                    email=lead.email,
                    defaults={'lead': lead}
                )
                recipient_count += 1
        
        campaign.total_recipients = recipient_count
        campaign.save()
        
        logger.info(f"Created {recipient_count} recipients for campaign {campaign_id}")
        
    except Campaign.DoesNotExist:
        logger.error(f"Campaign {campaign_id} not found")
    except Exception as e:
        logger.error(f"Error creating recipients: {str(e)}")


@shared_task
def track_email_open(recipient_id):
    """
    Track when a recipient opens an email
    """
    from .models import CampaignRecipient
    
    try:
        recipient = CampaignRecipient.objects.get(id=recipient_id)
        
        if recipient.status == 'sent':
            recipient.status = 'opened'
        
        if not recipient.opened_at:
            recipient.opened_at = timezone.now()
            recipient.campaign.opened_count += 1
            recipient.campaign.save()
        
        recipient.open_count += 1
        recipient.save()
        
        logger.info(f"Email opened: {recipient.email}")
        
    except CampaignRecipient.DoesNotExist:
        logger.error(f"Recipient {recipient_id} not found")


@shared_task
def track_email_click(recipient_id, url):
    """
    Track when a recipient clicks a link
    """
    from .models import CampaignRecipient, CampaignClick
    
    try:
        recipient = CampaignRecipient.objects.get(id=recipient_id)
        
        # Create click record
        CampaignClick.objects.create(
            recipient=recipient,
            url=url
        )
        
        # Update recipient status
        if recipient.status in ['sent', 'opened']:
            recipient.status = 'clicked'
        
        if not recipient.first_clicked_at:
            recipient.first_clicked_at = timezone.now()
            recipient.campaign.clicked_count += 1
            recipient.campaign.save()
        
        recipient.click_count += 1
        recipient.save()
        
        logger.info(f"Link clicked: {recipient.email} -> {url}")
        
    except CampaignRecipient.DoesNotExist:
        logger.error(f"Recipient {recipient_id} not found")
