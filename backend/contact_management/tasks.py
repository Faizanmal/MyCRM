"""
Celery Background Tasks for Contact and Account Management
Handles asynchronous bulk imports, scoring updates, and event notifications.
"""
import logging
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

logger = logging.getLogger(__name__)
User = get_user_model()


def is_feature_enabled(flag_name: str, default: bool = True) -> bool:
    """Check if a CRM core feature flag is enabled."""
    return getattr(settings, flag_name, default)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_bulk_contact_import(self, organization_id: int, contacts_data: list, user_id: int = None, correlation_id: str = None):
    """
    Asynchronously import contacts for an organization with bounded memory streaming.
    """
    if not is_feature_enabled('FEATURE_ASYNC_IMPORT', True):
        logger.warning(f"Async import disabled by feature flag. Org: {organization_id}")
        return {'status': 'disabled', 'imported': 0, 'updated': 0, 'errors': ['Feature flag disabled']}

    from multi_tenant.models import Organization
    from .services import ContactService
    logger.info(
        f"[AsyncImport] Starting bulk contact import for org={organization_id}, "
        f"count={len(contacts_data)}, user={user_id}, correlation_id={correlation_id}"
    )

    try:
        org = Organization.objects.filter(id=organization_id).first()
        user = User.objects.filter(id=user_id).first() if user_id else None
        service = ContactService(user=user, organization=org)
        results = service.import_contacts_stream(
            stream_or_path=contacts_data,
            batch_size=1000
        )
        logger.info(
            f"[AsyncImport] Completed bulk contact import for org={organization_id}: "
            f"created={results.get('created', 0)}, updated={results.get('updated', 0)}, "
            f"errors={len(results.get('errors', []))}"
        )
        return {
            'status': 'completed',
            'organization_id': organization_id,
            'correlation_id': correlation_id,
            'created': results.get('created', 0),
            'updated': results.get('updated', 0),
            'errors': results.get('errors', []),
        }
    except Exception as exc:
        logger.error(f"[AsyncImport] Bulk contact import failed for org={organization_id}: {exc}", exc_info=True)
        try:
            self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            return {
                'status': 'failed',
                'organization_id': organization_id,
                'correlation_id': correlation_id,
                'error': str(exc),
            }


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_bulk_account_import(self, organization_id: int, accounts_data: list, user_id: int = None, correlation_id: str = None):
    """
    Asynchronously import accounts for an organization with bounded memory streaming.
    """
    if not is_feature_enabled('FEATURE_ASYNC_IMPORT', True):
        logger.warning(f"Async import disabled by feature flag. Org: {organization_id}")
        return {'status': 'disabled', 'imported': 0, 'updated': 0, 'errors': ['Feature flag disabled']}

    from multi_tenant.models import Organization
    from .services import AccountService
    logger.info(
        f"[AsyncImport] Starting bulk account import for org={organization_id}, "
        f"count={len(accounts_data)}, user={user_id}, correlation_id={correlation_id}"
    )

    try:
        org = Organization.objects.filter(id=organization_id).first()
        user = User.objects.filter(id=user_id).first() if user_id else None
        service = AccountService(user=user, organization=org)
        results = service.import_accounts_stream(
            stream_or_path=accounts_data,
            batch_size=1000
        )
        logger.info(
            f"[AsyncImport] Completed bulk account import for org={organization_id}: "
            f"created={results.get('created', 0)}, updated={results.get('updated', 0)}, "
            f"errors={len(results.get('errors', []))}"
        )
        return {
            'status': 'completed',
            'organization_id': organization_id,
            'correlation_id': correlation_id,
            'created': results.get('created', 0),
            'updated': results.get('updated', 0),
            'errors': results.get('errors', []),
        }
    except Exception as exc:
        logger.error(f"[AsyncImport] Bulk account import failed for org={organization_id}: {exc}", exc_info=True)
        try:
            self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            return {
                'status': 'failed',
                'organization_id': organization_id,
                'correlation_id': correlation_id,
                'error': str(exc),
            }


@shared_task
def recalculate_account_health_scores(organization_id: int = None):
    """
    Periodically or trigger-based health score recalculation for accounts.
    """
    from .models import Account
    qs = Account.objects.filter(is_deleted=False)
    if organization_id:
        qs = qs.filter(organization_id=organization_id)

    updated_count = 0
    for account in qs.iterator(chunk_size=500):
        # Base health score calculation based on contacts and open opportunities count
        contacts_count = account.contacts.filter(is_deleted=False, is_merged=False).count()
        # Compute health: more active contacts -> higher health
        score = min(100, max(10, 50 + (contacts_count * 5)))
        if account.health_score != score:
            account.health_score = score
            account.save(update_fields=['health_score', 'updated_at'])
            updated_count += 1

    logger.info(f"[HealthScore] Updated health scores for {updated_count} accounts")
    return {'updated_count': updated_count}
