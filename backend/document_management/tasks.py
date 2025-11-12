"""
Celery tasks for document management
"""

from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def process_document_ocr(document_id):
    """
    Extract text from PDF or image documents using OCR
    """
    from .models import Document
    
    try:
        document = Document.objects.get(id=document_id)
        
        # For PDFs
        if document.is_pdf:
            extracted_text = extract_text_from_pdf(document.file.path)
        
        # For images
        elif document.is_image:
            extracted_text = extract_text_from_image(document.file.path)
        
        else:
            logger.info(f"Document {document_id} is not OCR-compatible")
            return
        
        # Save extracted text
        document.extracted_text = extracted_text
        document.ocr_processed = True
        document.save()
        
        logger.info(f"OCR completed for document {document_id}")
        
    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found")
    except Exception as e:
        logger.error(f"Error processing OCR for {document_id}: {str(e)}")


def extract_text_from_pdf(file_path):
    """Extract text from PDF using PyPDF2 or pdfplumber"""
    try:
        import PyPDF2
        
        text = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text.append(page.extract_text())
        
        return '\n'.join(text)
    
    except ImportError:
        logger.warning("PyPDF2 not installed. PDF text extraction skipped.")
        return ""
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return ""


def extract_text_from_image(file_path):
    """Extract text from image using Tesseract OCR"""
    try:
        import pytesseract
        from PIL import Image
        
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        
        return text
    
    except ImportError:
        logger.warning("pytesseract or Pillow not installed. Image OCR skipped.")
        return ""
    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}")
        return ""


@shared_task
def generate_document_from_template(template_id, variables, entity_type, entity_id, user_id):
    """
    Generate a document from a template with variable substitution
    """
    from .models import DocumentTemplate, Document
    from django.contrib.auth import get_user_model
    from django.core.files.base import ContentFile
    import os
    
    User = get_user_model()
    
    try:
        template = DocumentTemplate.objects.get(id=template_id)
        user = User.objects.get(id=user_id)
        
        # Read template content
        with template.file.open('r') as f:
            content = f.read()
        
        # Get file size for audit
        file_size = os.path.getsize(template.file.path) if template.file.name else 0
        
        # Replace variables
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"  # {{variable_name}}
            content = content.replace(placeholder, str(value))
        
        # Create new document
        filename = f"{template.name}_{entity_type}_{entity_id}.{template.file.name.split('.')[-1]}"
        
        document_data = {
            'name': filename,
            'category': template.template_type,
            'uploaded_by': user,
            'size': file_size,
        }
        
        # Set entity relationship with validation
        if entity_type == 'lead':
            from lead_management.models import Lead
            try:
                Lead.objects.get(id=entity_id)
                document_data['lead_id'] = entity_id
            except Lead.DoesNotExist:
                pass
        elif entity_type == 'contact':
            from contact_management.models import Contact
            try:
                Contact.objects.get(id=entity_id)
                document_data['contact_id'] = entity_id
            except Contact.DoesNotExist:
                pass
        elif entity_type == 'opportunity':
            from opportunity_management.models import Opportunity
            try:
                Opportunity.objects.get(id=entity_id)
                document_data['opportunity_id'] = entity_id
            except Opportunity.DoesNotExist:
                pass
        
        document = Document.objects.create(**document_data)
        document.file.save(filename, ContentFile(content.encode('utf-8')))
        
        logger.info(f"Document generated from template {template_id}: {document.id}")
        
        return str(document.id)
        
    except DocumentTemplate.DoesNotExist:
        logger.error(f"Template {template_id} not found")
    except Exception as e:
        logger.error(f"Error generating document from template: {str(e)}")


@shared_task
def cleanup_expired_shares():
    """
    Clean up expired document shares
    """
    from .models import DocumentShare
    from django.utils import timezone
    
    expired_shares = DocumentShare.objects.filter(
        expires_at__lt=timezone.now()
    )
    
    count = expired_shares.count()
    expired_shares.delete()
    
    logger.info(f"Cleaned up {count} expired document shares")


@shared_task
def generate_document_analytics():
    """
    Generate analytics for document usage
    """
    from .models import Document
    from django.db.models import Count, Sum
    
    analytics = {
        'total_documents': Document.objects.count(),
        'by_category': list(Document.objects.values('category').annotate(
            count=Count('id')
        )),
        'total_downloads': Document.objects.aggregate(
            total=Sum('download_count')
        )['total'] or 0,
        'most_downloaded': list(Document.objects.order_by('-download_count')[:10].values(
            'id', 'name', 'download_count'
        ))
    }
    
    logger.info(f"Document analytics generated: {analytics}")
    return analytics
