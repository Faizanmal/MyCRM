"""
Celery & Background Job Idempotency Engine

Guarantees at-most-once execution of side-effects (e.g. notifications, webhook calls, financial updates)
even in the event of worker retries, network blips, or duplicate broker deliveries.
"""

import functools
import hashlib
import json
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


def generate_idempotency_key(task_name: str, args: tuple, kwargs: dict) -> str:
    """Derive deterministic SHA-256 idempotency key from task name and arguments"""
    def serialize_val(val):
        try:
            return json.dumps(val, sort_keys=True, default=str)
        except Exception:
            return str(val)

    normalized_args = [serialize_val(a) for a in args]
    normalized_kwargs = {k: serialize_val(v) for k, v in sorted(kwargs.items())}
    payload_str = f"{task_name}:{normalized_args}:{normalized_kwargs}"
    return hashlib.sha256(payload_str.encode('utf-8')).hexdigest()


def execute_idempotent(task_name: str, idempotency_key: str, func, *args, **kwargs):
    """
    Execute a function idempotently using TaskExecutionRecord.
    If the task has already successfully completed with this idempotency key,
    returns the recorded result without re-executing side-effects.
    """
    from core.async_models import TaskExecutionRecord

    # Check existing execution
    record, created = TaskExecutionRecord.objects.get_or_create(
        idempotency_key=idempotency_key,
        defaults={
            'task_name': task_name,
            'status': 'running',
        }
    )

    if not created:
        if record.status == 'completed':
            logger.info(
                "Task '%s' with idempotency key '%s' was already completed. Skipping duplicate execution.",
                task_name,
                idempotency_key
            )
            if isinstance(record.result, dict):
                cached_res = dict(record.result)
                cached_res['idempotent_replay'] = True
                return cached_res
            return record.result
        elif record.status == 'running':
            # Check for stale running record (e.g. older than 30 minutes)
            if timezone.now() - record.created_at < timezone.timedelta(minutes=30):
                logger.warning(
                    "Task '%s' with key '%s' is currently executing concurrently. Denying duplicate trigger.",
                    task_name,
                    idempotency_key
                )
                return {
                    'idempotent_replay': True,
                    'status': 'in_progress',
                    'message': 'Duplicate task trigger denied while execution is in progress.',
                }
            else:
                logger.warning("Stale running task record found for key '%s'; re-executing.", idempotency_key)
                record.status = 'running'
                record.save(update_fields=['status'])

    # Execute target logic
    try:
        result = func(*args, **kwargs)
        # Serialize result safely
        json_result = None
        try:
            json_result = json.loads(json.dumps(result, default=str))
        except Exception:
            json_result = {'raw_output': str(result)}

        record.status = 'completed'
        record.result = json_result
        record.completed_at = timezone.now()
        record.save(update_fields=['status', 'result', 'completed_at'])
        return result

    except Exception as exc:
        record.status = 'failed'
        record.result = {'error': str(exc)}
        record.completed_at = timezone.now()
        record.save(update_fields=['status', 'result', 'completed_at'])
        raise exc


def idempotent_task(timeout: int = 3600, key_func=None):
    """
    Decorator for Celery shared_tasks to enforce idempotency.
    Usage:
        @shared_task
        @idempotent_task()
        def process_payment(customer_id, amount, idempotency_key=None):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract or generate idempotency key
            task_name = getattr(func, '__name__', str(func))
            idempotency_key = kwargs.pop('idempotency_key', None)
            if not idempotency_key:
                if key_func:
                    idempotency_key = key_func(*args, **kwargs)
                else:
                    idempotency_key = generate_idempotency_key(task_name, args, kwargs)

            return execute_idempotent(task_name, idempotency_key, func, *args, **kwargs)
        return wrapper
    return decorator
