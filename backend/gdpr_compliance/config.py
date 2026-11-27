"""
GDPR Compliance Operational Configuration & Feature Flags
Enables zero-downtime feature toggles and emergency rollback switches.
"""
import os
from django.conf import settings


def is_audit_tamper_detection_enabled() -> bool:
    """Check if cryptographic SHA-256 audit tamper verification is enabled."""
    val = os.getenv('AUDIT_TAMPER_DETECTION_ENABLED', getattr(settings, 'AUDIT_TAMPER_DETECTION_ENABLED', 'true'))
    return str(val).lower() in ('1', 'true', 'yes', 'on')


def is_dsar_export_enabled() -> bool:
    """Check if self-service or admin DSAR export generation is enabled."""
    val = os.getenv('GDPR_DSAR_EXPORT_ENABLED', getattr(settings, 'GDPR_DSAR_EXPORT_ENABLED', 'true'))
    return str(val).lower() in ('1', 'true', 'yes', 'on')


def is_legal_hold_enforcement_enabled() -> bool:
    """Check if legal hold statutory retention exceptions are actively enforced."""
    val = os.getenv('LEGAL_HOLD_ENFORCEMENT_ENABLED', getattr(settings, 'LEGAL_HOLD_ENFORCEMENT_ENABLED', 'true'))
    return str(val).lower() in ('1', 'true', 'yes', 'on')
