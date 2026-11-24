"""
Dead-Letter Queue & Poison Pill Quarantine Engine

Safely isolates poisoned, malformed, or unrecoverable background jobs
to prevent Celery worker crash loops, while maintaining a fully auditable quarantine log.
"""

import functools
import json
import logging
import traceback

logger = logging.getLogger(__name__)


class PoisonPillError(Exception):
    """Base exception indicating an unrecoverable poison pill in task payload or execution."""
    pass


class MalformedPayloadError(PoisonPillError):
    """Payload fails schema validation or contains unparseable binary/corrupt data."""
    pass


def quarantine_job(task_name: str, payload: dict | str, error: Exception, tenant=None, task_id: str = ""):
    """
    Persist an unrecoverable task failure into the PoisonPillQuarantine table and emit an audit event.
    """
    from core.async_models import PoisonPillQuarantine

    # Normalize payload safely to JSON-serializable structures
    try:
        payload_dict = json.loads(json.dumps(payload, default=str))
    except Exception:
        payload_dict = {'raw_payload': str(payload)[:2000]}

    tb_str = traceback.format_exc()
    error_type = error.__class__.__name__
    error_msg = str(error)

    quarantine = PoisonPillQuarantine.objects.create(
        task_name=task_name,
        task_id=task_id or '',
        payload=payload_dict,
        error_type=error_type,
        error_message=error_msg,
        traceback=tb_str,
        tenant=tenant,
        status='quarantined'
    )

    logger.critical(
        "AUDIT: POISON PILL QUARANTINED [ID: %s] | Task: %s | Error: %s: %s | Tenant: %s",
        quarantine.id,
        task_name,
        error_type,
        error_msg,
        tenant.id if tenant else 'Global'
    )

    return quarantine


def quarantine_poison_pill(
    exceptions=(PoisonPillError, MalformedPayloadError, json.JSONDecodeError, ValueError, KeyError, TypeError),
    tenant_extractor=None
):
    """
    Decorator for Celery tasks to quarantine poison pill payloads instead of crash-looping workers.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            task_name = getattr(func, '__name__', str(func))
            try:
                return func(*args, **kwargs)
            except exceptions as exc:
                tenant = None
                if tenant_extractor:
                    try:
                        tenant = tenant_extractor(*args, **kwargs)
                    except Exception:
                        pass
                elif 'tenant' in kwargs:
                    tenant = kwargs['tenant']
                elif 'organization' in kwargs:
                    tenant = kwargs['organization']

                combined_payload = {'args': list(args), 'kwargs': kwargs}
                quarantine = quarantine_job(
                    task_name=task_name,
                    payload=combined_payload,
                    error=exc,
                    tenant=tenant,
                )
                return {
                    'status': 'quarantined',
                    'quarantine_id': str(quarantine.id),
                    'error_type': exc.__class__.__name__,
                    'error_message': str(exc),
                }
        return wrapper
    return decorator
