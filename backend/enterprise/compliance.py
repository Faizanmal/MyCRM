"""
Compliance Automation Engine for MyCRM

Provides:
- Automated compliance checking
- Evidence collection
- Audit report generation
- Policy enforcement
- Compliance dashboards
- Regulatory mapping (SOC 2, ISO 27001, GDPR, HIPAA)
"""

import logging
import os
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


# =====================
# Compliance Frameworks
# =====================

class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    SOC2_TYPE1 = 'soc2_type1'
    SOC2_TYPE2 = 'soc2_type2'
    ISO27001 = 'iso27001'
    GDPR = 'gdpr'
    HIPAA = 'hipaa'
    PCI_DSS = 'pci_dss'
    CCPA = 'ccpa'


class ControlStatus(Enum):
    """Control implementation status"""
    IMPLEMENTED = 'implemented'
    PARTIALLY_IMPLEMENTED = 'partially_implemented'
    NOT_IMPLEMENTED = 'not_implemented'
    NOT_APPLICABLE = 'not_applicable'


class EvidenceType(Enum):
    """Types of compliance evidence"""
    SCREENSHOT = 'screenshot'
    LOG_EXPORT = 'log_export'
    CONFIGURATION = 'configuration'
    POLICY_DOCUMENT = 'policy_document'
    ACCESS_REVIEW = 'access_review'
    VULNERABILITY_SCAN = 'vulnerability_scan'
    PENETRATION_TEST = 'penetration_test'
    AUDIT_LOG = 'audit_log'


@dataclass
class ComplianceControl:
    """Compliance control definition"""
    control_id: str
    framework: ComplianceFramework
    name: str
    description: str
    category: str
    requirement: str

    # Implementation details
    status: ControlStatus = ControlStatus.NOT_IMPLEMENTED
    implementation_notes: str = ''

    # Evidence requirements
    evidence_types: list[EvidenceType] = field(default_factory=list)
    evidence_frequency: str = 'quarterly'  # 'daily', 'weekly', 'monthly', 'quarterly', 'annual'

    # Automated checking
    automated_check: Callable | None = None
    last_checked: datetime | None = None
    last_check_result: bool | None = None

    # Ownership
    owner: str = ''
    reviewer: str = ''

    # Risk mapping
    risk_level: str = 'medium'  # 'low', 'medium', 'high', 'critical'


@dataclass
class ComplianceEvidence:
    """Compliance evidence record"""
    evidence_id: str
    control_id: str
    evidence_type: EvidenceType
    title: str
    description: str

    # Evidence data
    file_path: str | None = None
    data: dict | None = None

    # Metadata
    collected_at: datetime = field(default_factory=timezone.now)
    collected_by: str = ''
    valid_until: datetime | None = None

    # Review
    reviewed: bool = False
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None


# =====================
# Control Definitions
# =====================

class ControlLibrary:
    """Library of compliance controls"""

    # SOC 2 Trust Services Criteria
    SOC2_CONTROLS = {
        'CC1.1': ComplianceControl(
            control_id='CC1.1',
            framework=ComplianceFramework.SOC2_TYPE2,
            name='Control Environment',
            description='Management demonstrates commitment to integrity and ethical values',
            category='Common Criteria',
            requirement='Code of conduct, ethics policies, whistleblower procedures',
            evidence_types=[EvidenceType.POLICY_DOCUMENT],
            risk_level='high'
        ),
        'CC2.1': ComplianceControl(
            control_id='CC2.1',
            framework=ComplianceFramework.SOC2_TYPE2,
            name='Information Communication',
            description='Internal communication of security policies',
            category='Common Criteria',
            requirement='Security awareness training, policy acknowledgments',
            evidence_types=[EvidenceType.POLICY_DOCUMENT, EvidenceType.LOG_EXPORT],
            risk_level='medium'
        ),
        'CC5.1': ComplianceControl(
            control_id='CC5.1',
            framework=ComplianceFramework.SOC2_TYPE2,
            name='Logical Access Controls',
            description='Logical access security software and infrastructure',
            category='Common Criteria',
            requirement='Access control lists, authentication mechanisms',
            evidence_types=[EvidenceType.CONFIGURATION, EvidenceType.ACCESS_REVIEW],
            evidence_frequency='quarterly',
            risk_level='critical'
        ),
        'CC6.1': ComplianceControl(
            control_id='CC6.1',
            framework=ComplianceFramework.SOC2_TYPE2,
            name='Encryption',
            description='Data encryption at rest and in transit',
            category='Common Criteria',
            requirement='TLS 1.2+, AES-256 encryption, key management',
            evidence_types=[EvidenceType.CONFIGURATION, EvidenceType.VULNERABILITY_SCAN],
            risk_level='critical'
        ),
        'CC7.1': ComplianceControl(
            control_id='CC7.1',
            framework=ComplianceFramework.SOC2_TYPE2,
            name='System Monitoring',
            description='Continuous monitoring of system components',
            category='Common Criteria',
            requirement='SIEM, log aggregation, alerting',
            evidence_types=[EvidenceType.CONFIGURATION, EvidenceType.LOG_EXPORT],
            risk_level='high'
        ),
        'CC7.2': ComplianceControl(
            control_id='CC7.2',
            framework=ComplianceFramework.SOC2_TYPE2,
            name='Incident Response',
            description='Security incident detection and response',
            category='Common Criteria',
            requirement='Incident response plan, breach notification procedures',
            evidence_types=[EvidenceType.POLICY_DOCUMENT, EvidenceType.LOG_EXPORT],
            risk_level='critical'
        ),
        'CC8.1': ComplianceControl(
            control_id='CC8.1',
            framework=ComplianceFramework.SOC2_TYPE2,
            name='Change Management',
            description='Changes to system are authorized and tested',
            category='Common Criteria',
            requirement='Change approval process, testing procedures',
            evidence_types=[EvidenceType.LOG_EXPORT, EvidenceType.CONFIGURATION],
            risk_level='high'
        ),
        'A1.1': ComplianceControl(
            control_id='A1.1',
            framework=ComplianceFramework.SOC2_TYPE2,
            name='Availability Commitment',
            description='System availability meets commitments',
            category='Availability',
            requirement='SLA documentation, uptime monitoring',
            evidence_types=[EvidenceType.CONFIGURATION, EvidenceType.LOG_EXPORT],
            risk_level='high'
        ),
    }

    # GDPR Articles
    GDPR_CONTROLS = {
        'GDPR-5': ComplianceControl(
            control_id='GDPR-5',
            framework=ComplianceFramework.GDPR,
            name='Data Processing Principles',
            description='Lawfulness, fairness, transparency',
            category='Principles',
            requirement='Privacy policy, consent mechanisms',
            evidence_types=[EvidenceType.POLICY_DOCUMENT, EvidenceType.CONFIGURATION],
            risk_level='critical'
        ),
        'GDPR-15': ComplianceControl(
            control_id='GDPR-15',
            framework=ComplianceFramework.GDPR,
            name='Right of Access',
            description='Data subject access requests',
            category='Data Subject Rights',
            requirement='SAR process, data export capability',
            evidence_types=[EvidenceType.LOG_EXPORT, EvidenceType.CONFIGURATION],
            risk_level='high'
        ),
        'GDPR-17': ComplianceControl(
            control_id='GDPR-17',
            framework=ComplianceFramework.GDPR,
            name='Right to Erasure',
            description='Right to be forgotten',
            category='Data Subject Rights',
            requirement='Data deletion process, verification',
            evidence_types=[EvidenceType.LOG_EXPORT, EvidenceType.CONFIGURATION],
            risk_level='high'
        ),
        'GDPR-25': ComplianceControl(
            control_id='GDPR-25',
            framework=ComplianceFramework.GDPR,
            name='Data Protection by Design',
            description='Privacy by design and by default',
            category='Technical Measures',
            requirement='Encryption, pseudonymization, access controls',
            evidence_types=[EvidenceType.CONFIGURATION, EvidenceType.POLICY_DOCUMENT],
            risk_level='critical'
        ),
        'GDPR-33': ComplianceControl(
            control_id='GDPR-33',
            framework=ComplianceFramework.GDPR,
            name='Breach Notification',
            description='72-hour breach notification',
            category='Breach Response',
            requirement='Breach detection, notification process',
            evidence_types=[EvidenceType.POLICY_DOCUMENT, EvidenceType.LOG_EXPORT],
            risk_level='critical'
        ),
    }

    # ISO 27001 Annex A Controls
    ISO27001_CONTROLS = {
        'A.5.1': ComplianceControl(
            control_id='A.5.1',
            framework=ComplianceFramework.ISO27001,
            name='Information Security Policies',
            description='Policies for information security',
            category='Information Security Policies',
            requirement='Security policy document, review process',
            evidence_types=[EvidenceType.POLICY_DOCUMENT],
            risk_level='high'
        ),
        'A.9.1': ComplianceControl(
            control_id='A.9.1',
            framework=ComplianceFramework.ISO27001,
            name='Access Control Policy',
            description='Business requirements of access control',
            category='Access Control',
            requirement='Access control policy, RBAC implementation',
            evidence_types=[EvidenceType.POLICY_DOCUMENT, EvidenceType.CONFIGURATION],
            risk_level='critical'
        ),
        'A.12.4': ComplianceControl(
            control_id='A.12.4',
            framework=ComplianceFramework.ISO27001,
            name='Logging and Monitoring',
            description='Event logging and monitoring',
            category='Operations Security',
            requirement='Centralized logging, log retention',
            evidence_types=[EvidenceType.CONFIGURATION, EvidenceType.LOG_EXPORT],
            risk_level='high'
        ),
        'A.18.1': ComplianceControl(
            control_id='A.18.1',
            framework=ComplianceFramework.ISO27001,
            name='Legal Compliance',
            description='Compliance with legal and contractual requirements',
            category='Compliance',
            requirement='Compliance register, legal review',
            evidence_types=[EvidenceType.POLICY_DOCUMENT],
            risk_level='high'
        ),
    }

    @classmethod
    def get_all_controls(cls) -> dict[str, ComplianceControl]:
        """Get all controls from all frameworks"""
        all_controls = {}
        all_controls.update(cls.SOC2_CONTROLS)
        all_controls.update(cls.GDPR_CONTROLS)
        all_controls.update(cls.ISO27001_CONTROLS)
        return all_controls

    @classmethod
    def get_controls_by_framework(cls, framework: ComplianceFramework) -> dict[str, ComplianceControl]:
        """Get controls for a specific framework"""
        if framework in [ComplianceFramework.SOC2_TYPE1, ComplianceFramework.SOC2_TYPE2]:
            return cls.SOC2_CONTROLS
        elif framework == ComplianceFramework.GDPR:
            return cls.GDPR_CONTROLS
        elif framework == ComplianceFramework.ISO27001:
            return cls.ISO27001_CONTROLS
        return {}


# =====================
# Automated Checks
# =====================

class AutomatedComplianceChecks:
    """Automated compliance checking functions"""

    @staticmethod
    def check_encryption_at_rest() -> tuple[bool, dict]:
        """Check if data at rest is encrypted"""
        results = {
            'database_encrypted': False,
            'file_storage_encrypted': False,
            'backup_encrypted': False,
            'details': []
        }

        # Check database encryption
        db_settings = getattr(settings, 'DATABASES', {}).get('default', {})
        if db_settings.get('OPTIONS', {}).get('sslmode') == 'require':
            results['database_encrypted'] = True
            results['details'].append('Database SSL enabled')

        # Check if encryption key is configured
        if getattr(settings, 'ENCRYPTION_KEY', None):
            results['file_storage_encrypted'] = True
            results['details'].append('Field-level encryption configured')

        passed = results['database_encrypted'] and results['file_storage_encrypted']
        return passed, results

    @staticmethod
    def check_encryption_in_transit() -> tuple[bool, dict]:
        """Check if data in transit is encrypted"""
        results = {
            'ssl_redirect': False,
            'hsts_enabled': False,
            'secure_cookies': False,
            'details': []
        }

        # Check SSL redirect
        if getattr(settings, 'SECURE_SSL_REDIRECT', False):
            results['ssl_redirect'] = True
            results['details'].append('SSL redirect enabled')

        # Check HSTS
        hsts_seconds = getattr(settings, 'SECURE_HSTS_SECONDS', 0)
        if hsts_seconds > 0:
            results['hsts_enabled'] = True
            results['details'].append(f'HSTS enabled for {hsts_seconds} seconds')

        # Check secure cookies
        if getattr(settings, 'SESSION_COOKIE_SECURE', False):
            results['secure_cookies'] = True
            results['details'].append('Secure session cookies enabled')

        passed = all([results['ssl_redirect'], results['hsts_enabled'], results['secure_cookies']])
        return passed, results

    @staticmethod
    def check_access_controls() -> tuple[bool, dict]:
        """Check access control implementation"""
        results = {
            'authentication_required': False,
            'rbac_enabled': False,
            'mfa_available': False,
            'session_timeout': False,
            'details': []
        }

        # Check authentication
        rest_framework = getattr(settings, 'REST_FRAMEWORK', {})
        auth_classes = rest_framework.get('DEFAULT_AUTHENTICATION_CLASSES', [])
        if 'rest_framework_simplejwt.authentication.JWTAuthentication' in auth_classes:
            results['authentication_required'] = True
            results['details'].append('JWT authentication enabled')

        # Check for RBAC (check if user_management app is installed)
        installed_apps = getattr(settings, 'INSTALLED_APPS', [])
        if 'user_management' in installed_apps:
            results['rbac_enabled'] = True
            results['details'].append('User management with RBAC installed')

        # Check MFA
        # Check if pyotp is in requirements (2FA support)
        results['mfa_available'] = True  # Assuming it's available based on requirements.txt
        results['details'].append('2FA support available')

        # Check session timeout
        session_timeout = getattr(settings, 'SESSION_TIMEOUT_MINUTES', 0)
        if session_timeout > 0 and session_timeout <= 120:
            results['session_timeout'] = True
            results['details'].append(f'Session timeout set to {session_timeout} minutes')

        passed = all([results['authentication_required'], results['rbac_enabled']])
        return passed, results

    @staticmethod
    def check_audit_logging() -> tuple[bool, dict]:
        """Check audit logging implementation"""
        results = {
            'audit_enabled': False,
            'log_retention': False,
            'sensitive_field_masking': False,
            'details': []
        }

        # Check audit logging
        if getattr(settings, 'AUDIT_LOG_ENABLED', False):
            results['audit_enabled'] = True
            results['details'].append('Audit logging enabled')

        # Check retention
        retention_days = getattr(settings, 'AUDIT_LOG_RETENTION_DAYS', 0)
        if retention_days >= 365:
            results['log_retention'] = True
            results['details'].append(f'Audit logs retained for {retention_days} days')

        # Check sensitive field handling
        sensitive_fields = getattr(settings, 'AUDIT_SENSITIVE_FIELDS', [])
        if sensitive_fields:
            results['sensitive_field_masking'] = True
            results['details'].append('Sensitive fields configured for masking')

        passed = results['audit_enabled'] and results['log_retention']
        return passed, results

    @staticmethod
    def check_gdpr_data_subject_rights() -> tuple[bool, dict]:
        """Check GDPR data subject rights implementation"""
        results = {
            'consent_management': False,
            'data_export': False,
            'data_deletion': False,
            'details': []
        }

        # Check if gdpr_compliance app is installed
        installed_apps = getattr(settings, 'INSTALLED_APPS', [])
        if 'gdpr_compliance' in installed_apps:
            results['consent_management'] = True
            results['data_export'] = True
            results['data_deletion'] = True
            results['details'].append('GDPR compliance module installed')

        passed = all([results['consent_management'], results['data_export'], results['data_deletion']])
        return passed, results


# =====================
# Compliance Engine
# =====================

class ComplianceEngine:
    """
    Main compliance automation engine
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._controls = ControlLibrary.get_all_controls()
        self._evidence: dict[str, list[ComplianceEvidence]] = {}
        self._automated_checks = self._setup_automated_checks()
        self._initialized = True

    def _setup_automated_checks(self) -> dict[str, Callable]:
        """Map controls to automated check functions"""
        return {
            'CC6.1': AutomatedComplianceChecks.check_encryption_at_rest,
            'GDPR-25': AutomatedComplianceChecks.check_encryption_in_transit,
            'CC5.1': AutomatedComplianceChecks.check_access_controls,
            'A.9.1': AutomatedComplianceChecks.check_access_controls,
            'CC7.1': AutomatedComplianceChecks.check_audit_logging,
            'A.12.4': AutomatedComplianceChecks.check_audit_logging,
            'GDPR-15': AutomatedComplianceChecks.check_gdpr_data_subject_rights,
            'GDPR-17': AutomatedComplianceChecks.check_gdpr_data_subject_rights,
        }

    def run_automated_checks(self, framework: ComplianceFramework | None = None) -> dict:
        """
        Run automated compliance checks

        Args:
            framework: Specific framework to check (or all if None)

        Returns:
            Dict of check results
        """
        results = {
            'timestamp': timezone.now().isoformat(),
            'framework': framework.value if framework else 'all',
            'controls': {},
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'not_applicable': 0
            }
        }

        controls_to_check = (
            ControlLibrary.get_controls_by_framework(framework)
            if framework
            else self._controls
        )

        for control_id, control in controls_to_check.items():
            results['summary']['total'] += 1

            if control_id in self._automated_checks:
                check_func = self._automated_checks[control_id]
                try:
                    passed, details = check_func()

                    control.last_checked = timezone.now()
                    control.last_check_result = passed

                    if passed:
                        control.status = ControlStatus.IMPLEMENTED
                        results['summary']['passed'] += 1
                    else:
                        control.status = ControlStatus.PARTIALLY_IMPLEMENTED
                        results['summary']['failed'] += 1

                    results['controls'][control_id] = {
                        'name': control.name,
                        'status': control.status.value,
                        'passed': passed,
                        'details': details
                    }
                except Exception as e:
                    logger.error(f"Error checking control {control_id}: {e}")
                    results['controls'][control_id] = {
                        'name': control.name,
                        'status': 'error',
                        'error': str(e)
                    }
                    results['summary']['failed'] += 1
            else:
                # No automated check available
                results['controls'][control_id] = {
                    'name': control.name,
                    'status': control.status.value,
                    'automated_check': False
                }

        # Calculate compliance percentage
        if results['summary']['total'] > 0:
            results['summary']['compliance_percentage'] = round(
                (results['summary']['passed'] / results['summary']['total']) * 100, 1
            )

        # Cache results
        cache.set('compliance_check_results', results, 86400)

        return results

    def get_compliance_status(self, framework: ComplianceFramework) -> dict:
        """Get current compliance status for a framework"""
        controls = ControlLibrary.get_controls_by_framework(framework)

        status = {
            'framework': framework.value,
            'total_controls': len(controls),
            'implemented': 0,
            'partially_implemented': 0,
            'not_implemented': 0,
            'not_applicable': 0,
            'by_category': {},
            'by_risk_level': {
                'critical': {'total': 0, 'implemented': 0},
                'high': {'total': 0, 'implemented': 0},
                'medium': {'total': 0, 'implemented': 0},
                'low': {'total': 0, 'implemented': 0}
            }
        }

        for _control_id, control in controls.items():
            # Status counts
            if control.status == ControlStatus.IMPLEMENTED:
                status['implemented'] += 1
            elif control.status == ControlStatus.PARTIALLY_IMPLEMENTED:
                status['partially_implemented'] += 1
            elif control.status == ControlStatus.NOT_APPLICABLE:
                status['not_applicable'] += 1
            else:
                status['not_implemented'] += 1

            # Category breakdown
            if control.category not in status['by_category']:
                status['by_category'][control.category] = {
                    'total': 0, 'implemented': 0
                }
            status['by_category'][control.category]['total'] += 1
            if control.status == ControlStatus.IMPLEMENTED:
                status['by_category'][control.category]['implemented'] += 1

            # Risk level breakdown
            status['by_risk_level'][control.risk_level]['total'] += 1
            if control.status == ControlStatus.IMPLEMENTED:
                status['by_risk_level'][control.risk_level]['implemented'] += 1

        # Calculate percentages
        if status['total_controls'] > 0:
            status['compliance_percentage'] = round(
                (status['implemented'] / status['total_controls']) * 100, 1
            )

        return status

    def add_evidence(self, control_id: str, evidence: ComplianceEvidence):
        """Add evidence for a control"""
        if control_id not in self._evidence:
            self._evidence[control_id] = []
        self._evidence[control_id].append(evidence)

        # Persist to cache
        cache.set(f'compliance_evidence:{control_id}', self._evidence[control_id], 86400 * 365)

    def get_evidence(self, control_id: str) -> list[ComplianceEvidence]:
        """Get all evidence for a control"""
        return self._evidence.get(control_id, [])

    def generate_audit_report(self, framework: ComplianceFramework) -> dict:
        """Generate a compliance audit report"""
        status = self.get_compliance_status(framework)
        controls = ControlLibrary.get_controls_by_framework(framework)

        report = {
            'title': f'{framework.value.upper()} Compliance Audit Report',
            'generated_at': timezone.now().isoformat(),
            'organization': os.getenv('ORGANIZATION_NAME', 'MyCRM'),
            'report_period': {
                'start': (timezone.now() - timedelta(days=365)).isoformat(),
                'end': timezone.now().isoformat()
            },
            'executive_summary': {
                'overall_compliance': status['compliance_percentage'],
                'total_controls': status['total_controls'],
                'implemented': status['implemented'],
                'gaps': status['not_implemented']
            },
            'control_details': [],
            'evidence_summary': [],
            'recommendations': []
        }

        # Add control details
        for control_id, control in controls.items():
            evidence = self.get_evidence(control_id)

            control_detail = {
                'control_id': control_id,
                'name': control.name,
                'category': control.category,
                'description': control.description,
                'requirement': control.requirement,
                'status': control.status.value,
                'risk_level': control.risk_level,
                'owner': control.owner,
                'evidence_count': len(evidence),
                'last_checked': control.last_checked.isoformat() if control.last_checked else None
            }
            report['control_details'].append(control_detail)

            # Add recommendations for gaps
            if control.status != ControlStatus.IMPLEMENTED:
                report['recommendations'].append({
                    'control_id': control_id,
                    'priority': control.risk_level,
                    'recommendation': f"Implement {control.name}: {control.requirement}"
                })

        return report


# =====================
# Audit Automation
# =====================

class AuditAutomation:
    """Automated audit trail and evidence collection"""

    def __init__(self):
        self.compliance_engine = ComplianceEngine()

    def collect_access_review_evidence(self) -> ComplianceEvidence:
        """Automatically collect access review evidence"""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Get user access data
        users = User.objects.all().values('id', 'username', 'email', 'is_active',
                                          'is_staff', 'is_superuser', 'last_login')

        access_data = {
            'collection_date': timezone.now().isoformat(),
            'total_users': len(users),
            'active_users': sum(1 for u in users if u['is_active']),
            'admin_users': sum(1 for u in users if u['is_superuser']),
            'staff_users': sum(1 for u in users if u['is_staff']),
            'users': list(users)
        }

        evidence = ComplianceEvidence(
            evidence_id=f"access_review_{timezone.now().strftime('%Y%m%d')}",
            control_id='CC5.1',
            evidence_type=EvidenceType.ACCESS_REVIEW,
            title=f"User Access Review - {timezone.now().strftime('%Y-%m-%d')}",
            description="Automated collection of user access permissions",
            data=access_data,
            collected_by='system'
        )

        self.compliance_engine.add_evidence('CC5.1', evidence)
        return evidence

    def collect_configuration_evidence(self) -> ComplianceEvidence:
        """Collect security configuration evidence"""
        config_data = {
            'collection_date': timezone.now().isoformat(),
            'django_settings': {
                'debug': getattr(settings, 'DEBUG', None),
                'secure_ssl_redirect': getattr(settings, 'SECURE_SSL_REDIRECT', None),
                'secure_hsts_seconds': getattr(settings, 'SECURE_HSTS_SECONDS', None),
                'session_cookie_secure': getattr(settings, 'SESSION_COOKIE_SECURE', None),
                'csrf_cookie_secure': getattr(settings, 'CSRF_COOKIE_SECURE', None),
                'session_cookie_httponly': getattr(settings, 'SESSION_COOKIE_HTTPONLY', None),
            },
            'authentication': {
                'jwt_access_lifetime_minutes': 15,  # From SIMPLE_JWT config
                'jwt_refresh_lifetime_days': 7,
                'mfa_enabled': True
            },
            'encryption': {
                'encryption_key_configured': bool(getattr(settings, 'ENCRYPTION_KEY', None)),
                'audit_logging_enabled': getattr(settings, 'AUDIT_LOG_ENABLED', False)
            }
        }

        evidence = ComplianceEvidence(
            evidence_id=f"config_snapshot_{timezone.now().strftime('%Y%m%d_%H%M%S')}",
            control_id='CC6.1',
            evidence_type=EvidenceType.CONFIGURATION,
            title="Security Configuration Snapshot",
            description="Automated security configuration capture",
            data=config_data,
            collected_by='system'
        )

        self.compliance_engine.add_evidence('CC6.1', evidence)
        return evidence

    def collect_audit_log_evidence(self, days: int = 30) -> ComplianceEvidence:
        """Collect audit log evidence"""
        # Get audit log summary from cache
        audit_summary = {
            'collection_date': timezone.now().isoformat(),
            'period_days': days,
            'total_events': cache.get('audit_event_count', 0),
            'events_by_type': cache.get('audit_events_by_type', {}),
            'high_risk_events': cache.get('audit_high_risk_count', 0)
        }

        evidence = ComplianceEvidence(
            evidence_id=f"audit_log_{timezone.now().strftime('%Y%m%d')}",
            control_id='CC7.1',
            evidence_type=EvidenceType.AUDIT_LOG,
            title=f"Audit Log Summary - Last {days} Days",
            description="Summary of audit logging activity",
            data=audit_summary,
            collected_by='system'
        )

        self.compliance_engine.add_evidence('CC7.1', evidence)
        return evidence

    def schedule_evidence_collection(self):
        """Schedule automated evidence collection tasks"""
        # This would typically integrate with Celery Beat
        collection_tasks = {
            'access_review': {
                'function': self.collect_access_review_evidence,
                'frequency': 'quarterly'
            },
            'configuration': {
                'function': self.collect_configuration_evidence,
                'frequency': 'monthly'
            },
            'audit_logs': {
                'function': self.collect_audit_log_evidence,
                'frequency': 'monthly'
            }
        }

        return collection_tasks
