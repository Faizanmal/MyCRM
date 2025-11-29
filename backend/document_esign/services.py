"""
Document E-Signature Service Layer
"""

from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta


class DocumentService:
    """Service for document e-signature operations"""
    
    def render_template(self, template, merge_data):
        """Render template with merge data"""
        content = template.content_html
        
        # Replace merge fields
        for field in template.merge_fields:
            placeholder = f"{{{{ {field} }}}}"
            value = merge_data.get(field, '')
            content = content.replace(placeholder, str(value))
        
        # Apply CSS
        if template.css_styles:
            content = f"<style>{template.css_styles}</style>{content}"
        
        return content
    
    def send_document(self, document, message='', expires_in_days=30):
        """Send document for signature"""
        if document.status not in ['draft']:
            return False, "Document has already been sent"
        
        # Set expiration
        document.expires_at = timezone.now() + timedelta(days=expires_in_days)
        document.status = 'sent'
        document.sent_at = timezone.now()
        document.save()
        
        # Send emails to recipients
        for recipient in document.recipients.all():
            self._send_signing_request(document, recipient, message)
        
        # Log the action
        from .models import DocumentAuditLog
        DocumentAuditLog.objects.create(
            document=document,
            action='sent',
            details=f"Sent to {document.recipients.count()} recipients"
        )
        
        # Update template stats
        if document.template:
            document.template.times_used += 1
            document.template.save()
        
        return True, "Document sent successfully"
    
    def _send_signing_request(self, document, recipient, message=''):
        """Send signing request email"""
        signing_url = f"{settings.SITE_URL}/sign/{recipient.access_token}"
        
        subject = f"Please sign: {document.name}"
        body = f"""
Hello {recipient.name},

{document.created_by.get_full_name()} has requested your signature on "{document.name}".

{message if message else ''}

Please click the link below to review and sign the document:
{signing_url}

This link will expire on {document.expires_at.strftime('%B %d, %Y') if document.expires_at else 'N/A'}.

Best regards,
{document.created_by.get_full_name()}
        """
        
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=True
            )
        except Exception:
            pass  # Log error in production
    
    def process_signature(self, recipient, fields_data, ip_address='', user_agent=''):
        """Process signature submission"""
        from .models import Signature, SignatureField, DocumentAuditLog
        
        document = recipient.document
        
        # Validate all required fields
        required_fields = recipient.fields.filter(is_required=True)
        submitted_field_ids = [f['field_id'] for f in fields_data]
        
        for field in required_fields:
            if field.id not in submitted_field_ids:
                return False, f"Missing required field: {field.field_name or field.get_field_type_display()}"
        
        # Process each field
        for field_data in fields_data:
            field_id = field_data.get('field_id')
            value = field_data.get('value', '')
            
            try:
                field = SignatureField.objects.get(id=field_id, recipient=recipient)
            except SignatureField.DoesNotExist:
                continue
            
            if field.field_type in ['signature', 'initials']:
                # Create signature record
                Signature.objects.create(
                    recipient=recipient,
                    field=field,
                    signature_type=field_data.get('signature_type', 'drawn'),
                    signature_data=value,
                    signer_name=recipient.name,
                    signer_email=recipient.email,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
            
            field.value = value
            field.filled_at = timezone.now()
            field.save()
        
        # Mark recipient as signed
        recipient.signed_at = timezone.now()
        recipient.signed_from_ip = ip_address
        recipient.save()
        
        # Log the action
        DocumentAuditLog.objects.create(
            document=document,
            recipient=recipient,
            action='signed',
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Check if all recipients have signed
        self._check_document_completion(document)
        
        return True, "Signature recorded successfully"
    
    def _check_document_completion(self, document):
        """Check if document is fully signed"""
        from .models import DocumentAuditLog
        
        signers = document.recipients.filter(recipient_type='signer')
        all_signed = all(r.signed_at is not None for r in signers)
        
        if document.require_all_signatures and all_signed:
            document.status = 'completed'
            document.completed_at = timezone.now()
            document.save()
            
            DocumentAuditLog.objects.create(
                document=document,
                action='completed',
                details="All required signatures collected"
            )
            
            # Generate signed PDF
            self._generate_signed_pdf(document)
            
            # Notify creator
            self._notify_completion(document)
            
        elif not document.require_all_signatures:
            # Update to partially signed
            signed_count = signers.filter(signed_at__isnull=False).count()
            if signed_count > 0 and signed_count < signers.count():
                document.status = 'partially_signed'
                document.save()
    
    def _generate_signed_pdf(self, document):
        """Generate final signed PDF"""
        # In production, use a PDF library like weasyprint or reportlab
        # For now, just mark as ready
        pass
    
    def _notify_completion(self, document):
        """Notify document creator of completion"""
        subject = f"Document signed: {document.name}"
        body = f"""
Your document "{document.name}" has been fully signed.

Signing Summary:
"""
        for recipient in document.recipients.all():
            if recipient.signed_at:
                body += f"- {recipient.name}: Signed on {recipient.signed_at.strftime('%B %d, %Y at %H:%M')}\n"
        
        body += """

You can download the signed document from your dashboard.
        """
        
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[document.created_by.email],
                fail_silently=True
            )
        except Exception:
            pass
    
    def decline_signature(self, recipient, reason=''):
        """Handle signature decline"""
        from .models import DocumentAuditLog
        
        document = recipient.document
        
        recipient.declined_at = timezone.now()
        recipient.decline_reason = reason
        recipient.save()
        
        document.status = 'declined'
        document.save()
        
        DocumentAuditLog.objects.create(
            document=document,
            recipient=recipient,
            action='declined',
            details=reason
        )
        
        # Notify document creator
        self._notify_decline(document, recipient, reason)
    
    def _notify_decline(self, document, recipient, reason):
        """Notify creator of decline"""
        subject = f"Document declined: {document.name}"
        body = f"""
{recipient.name} has declined to sign "{document.name}".

Reason: {reason if reason else 'No reason provided'}

You may want to follow up with them or void the document.
        """
        
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[document.created_by.email],
                fail_silently=True
            )
        except Exception:
            pass
    
    def void_document(self, document, reason=''):
        """Void a document"""
        from .models import DocumentAuditLog
        
        if document.status == 'completed':
            return False, "Cannot void a completed document"
        
        document.status = 'voided'
        document.save()
        
        DocumentAuditLog.objects.create(
            document=document,
            action='voided',
            details=reason
        )
        
        # Notify recipients
        for recipient in document.recipients.all():
            self._notify_void(document, recipient)
        
        return True, "Document voided"
    
    def _notify_void(self, document, recipient):
        """Notify recipient of void"""
        subject = f"Document voided: {document.name}"
        body = f"""
Hello {recipient.name},

The document "{document.name}" has been voided by {document.created_by.get_full_name()}.

No action is required on your part.
        """
        
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=True
            )
        except Exception:
            pass
    
    def send_reminders(self, document):
        """Send reminders to pending signers"""
        from .models import DocumentAuditLog
        
        pending_recipients = document.recipients.filter(
            recipient_type='signer',
            signed_at__isnull=True,
            declined_at__isnull=True
        )
        
        count = 0
        for recipient in pending_recipients:
            self._send_reminder(document, recipient)
            
            recipient.last_reminder_sent = timezone.now()
            recipient.reminders_sent_count += 1
            recipient.save()
            
            DocumentAuditLog.objects.create(
                document=document,
                recipient=recipient,
                action='reminder_sent'
            )
            
            count += 1
        
        return count
    
    def _send_reminder(self, document, recipient):
        """Send reminder email"""
        signing_url = f"{settings.SITE_URL}/sign/{recipient.access_token}"
        
        subject = f"Reminder: Please sign {document.name}"
        body = f"""
Hello {recipient.name},

This is a reminder that "{document.name}" is waiting for your signature.

Please click the link below to review and sign:
{signing_url}

This link will expire on {document.expires_at.strftime('%B %d, %Y') if document.expires_at else 'N/A'}.

Best regards,
{document.created_by.get_full_name()}
        """
        
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=True
            )
        except Exception:
            pass
    
    def get_signed_document_url(self, document):
        """Get URL for signed document download"""
        if document.signed_pdf:
            return document.signed_pdf.url
        return None
