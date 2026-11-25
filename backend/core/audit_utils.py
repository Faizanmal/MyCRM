"""
Audit Utilities
Credential redaction, canonical serialization, and cryptographic hashing.
"""
import hashlib
import json
import re

SENSITIVE_KEY_PATTERN = re.compile(
    r'(password|passwd|token|secret|api[_-]?key|access[_-]?token|auth|authorization|'
    r'private[_-]?key|credit[_-]?card|cvv|ssn|encryption[_-]?key|salt|hash)',
    re.IGNORECASE
)

SENSITIVE_VAL_PATTERN = re.compile(
    r'(Bearer\s+[a-zA-Z0-9_\-\.]+|'
    r'sk-[a-zA-Z0-9]{20,}|'
    r'ghp_[a-zA-Z0-9]{20,}|'
    r'AKIA[0-9A-Z]{16}|'
    r'(?:[0-9]{4}[- ]?){3}[0-9]{4})',
    re.IGNORECASE
)

REDACTED_MASK = '***REDACTED***'


def redact_sensitive_data(data):
    """
    Recursively sanitize dictionaries, lists, and strings to ensure credentials
    and secrets are masked with '***REDACTED***'.
    """
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            if SENSITIVE_KEY_PATTERN.search(str(k)):
                cleaned[k] = REDACTED_MASK
            else:
                cleaned[k] = redact_sensitive_data(v)
        return cleaned
    elif isinstance(data, list):
        return [redact_sensitive_data(item) for item in data]
    elif isinstance(data, tuple):
        return tuple(redact_sensitive_data(item) for item in data)
    elif isinstance(data, str):
        if SENSITIVE_VAL_PATTERN.search(data):
            return SENSITIVE_VAL_PATTERN.sub(REDACTED_MASK, data)
        return data
    else:
        return data


def canonical_json_dump(obj):
    """
    Produce a deterministic, sorted-key JSON string representation.
    """
    try:
        return json.dumps(obj, sort_keys=True, default=str)
    except Exception:
        return str(obj)


def compute_audit_record_hash(
    prev_hash: str,
    sequence_number: int,
    timestamp_iso: str,
    organization_id: str,
    user_id: str,
    action: str,
    description: str,
    content_type_id: str,
    object_id: str,
    changes: dict,
    new_values: dict,
    metadata: dict = None,
) -> str:
    """
    Compute cryptographic SHA-256 hash for an audit record.
    Forms an immutable blockchain-style linked hash chain per tenant.
    """
    canonical_payload = (
        f"{prev_hash}:"
        f"{sequence_number}:"
        f"{timestamp_iso}:"
        f"{organization_id}:"
        f"{user_id}:"
        f"{action}:"
        f"{description}:"
        f"{content_type_id}:"
        f"{object_id}:"
        f"{canonical_json_dump(changes)}:"
        f"{canonical_json_dump(new_values)}:"
        f"{canonical_json_dump(metadata or {})}"
    )
    return hashlib.sha256(canonical_payload.encode('utf-8')).hexdigest()
