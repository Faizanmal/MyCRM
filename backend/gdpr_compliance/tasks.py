"""
Background Celery Tasks for GDPR Compliance & DSAR Processing
Idempotent and resilient async job processing with poison-queue quarantine.
"""
import logging
from celery import shared_task
from core.async_idempotency import idempotent_task
from core.poison_queue import quarantine_poison_pill
from gdpr_compliance.models import DataExportRequest, DataDeletionRequest
from gdpr_compliance.services import generate_dsar_export, execute_gdpr_deletion

logger = logging.getLogger('crm.compliance.tasks')


@shared_task(name='gdpr_compliance.tasks.process_dsar_export_task')
@idempotent_task()
@quarantine_poison_pill()
def process_dsar_export_task(export_request_id: str):
    """
    Asynchronously generate a comprehensive DSAR export bundle with SHA-256 checksum.
    Guaranteed idempotent against duplicate broker delivery.
    """
    logger.info("Processing async DSAR export for request ID %s", export_request_id)
    try:
        export_req = DataExportRequest.objects.select_related('user', 'organization').get(id=export_request_id)
    except DataExportRequest.DoesNotExist:
        raise ValueError(f"DataExportRequest {export_request_id} does not exist.")

    if export_req.status == 'completed' and export_req.checksum:
        return {
            'status': 'already_completed',
            'export_id': str(export_req.id),
            'checksum': export_req.checksum,
        }

    export_req.status = 'processing'
    export_req.save(update_fields=['status'])

    bundle = generate_dsar_export(
        user=export_req.user,
        organization=export_req.organization,
        export_request=export_req
    )

    return {
        'status': 'completed',
        'export_id': str(export_req.id),
        'checksum': export_req.checksum,
        'record_counts': bundle.get('record_counts', {}),
    }


@shared_task(name='gdpr_compliance.tasks.execute_gdpr_deletion_task')
@idempotent_task()
@quarantine_poison_pill()
def execute_gdpr_deletion_task(deletion_request_id: str, reviewer_user_id: int = None):
    """
    Asynchronously execute a GDPR Article 17 deletion request with legal hold exceptions.
    Guaranteed idempotent against duplicate execution.
    """
    logger.info("Executing async GDPR deletion for request ID %s", deletion_request_id)
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        deletion_req = DataDeletionRequest.objects.select_related('user', 'organization').get(id=deletion_request_id)
    except DataDeletionRequest.DoesNotExist:
        raise ValueError(f"DataDeletionRequest {deletion_request_id} does not exist.")

    if deletion_req.status == 'completed':
        return {
            'status': 'already_completed',
            'deletion_id': str(deletion_req.id),
            'legal_hold_applied': bool(deletion_req.retained_legal_exceptions),
        }

    reviewer = None
    if reviewer_user_id:
        reviewer = User.objects.filter(id=reviewer_user_id).first()

    result = execute_gdpr_deletion(deletion_req, reviewer_user=reviewer)
    return {
        'status': 'completed',
        'deletion_id': str(deletion_req.id),
        'result': result,
    }
