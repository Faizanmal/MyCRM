"""
Advanced Security Services
Zero-trust, DLP, and Audit Trail Services
"""

import logging
import hashlib
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.cache import cache
import re

from .security_models import (
    DeviceTrust, SecuritySession, ImmutableAuditLog,
    DataClassification, DLPPolicy, DLPIncident, AccessPolicy
)

logger = logging.getLogger(__name__)
User = get_user_model()


class DeviceTrustService:
    """Service for managing device trust"""
    
    def __init__(self, user):
        self.user = user
    
    @transaction.atomic
    def register_device(
        self,
        device_fingerprint: str,
        user_agent: str,
        ip_address: str,
        device_name: str = ''
    ) -> Dict:
        """Register a new device for the user"""
        
        # Parse user agent
        device_info = self._parse_user_agent(user_agent)
        
        device, created = DeviceTrust.objects.get_or_create(
            user=self.user,
            device_fingerprint=device_fingerprint,
            defaults={
                'device_name': device_name or f"{device_info['browser']} on {device_info['os']}",
                'device_type': device_info['device_type'],
                'user_agent': user_agent,
                'os_name': device_info['os'],
                'os_version': device_info['os_version'],
                'browser_name': device_info['browser'],
                'browser_version': device_info['browser_version'],
                'last_ip_address': ip_address,
            }
        )
        
        if not created:
            device.login_count += 1
            device.last_ip_address = ip_address
            device.save()
        
        return {
            'id': str(device.id),
            'device_name': device.device_name,
            'is_trusted': device.is_trusted,
            'trust_level': device.trust_level,
            'is_new': created
        }
    
    def verify_device(
        self,
        device_id: str,
        verification_method: str = 'mfa'
    ) -> Dict:
        """Verify and trust a device"""
        
        try:
            device = DeviceTrust.objects.get(id=device_id, user=self.user)
        except DeviceTrust.DoesNotExist:
            raise ValueError(f"Device {device_id} not found")
        
        device.is_trusted = True
        device.trust_level = 'verified'
        device.verified_at = timezone.now()
        device.verified_via = verification_method
        device.trust_expires_at = timezone.now() + timedelta(days=30)
        device.save()
        
        return {
            'id': str(device.id),
            'is_trusted': True,
            'trust_level': 'verified',
            'expires_at': device.trust_expires_at.isoformat()
        }
    
    def revoke_device(self, device_id: str, reason: str = '') -> Dict:
        """Revoke trust for a device"""
        
        try:
            device = DeviceTrust.objects.get(id=device_id, user=self.user)
        except DeviceTrust.DoesNotExist:
            raise ValueError(f"Device {device_id} not found")
        
        device.is_trusted = False
        device.is_revoked = True
        device.revoked_at = timezone.now()
        device.revoked_reason = reason
        device.save()
        
        # Terminate all sessions for this device
        SecuritySession.objects.filter(
            device=device,
            status='active'
        ).update(
            status='terminated',
            terminated_at=timezone.now(),
            termination_reason='device_revoked'
        )
        
        return {
            'id': str(device.id),
            'is_revoked': True,
            'sessions_terminated': True
        }
    
    def get_trusted_devices(self) -> List[Dict]:
        """Get all trusted devices for user"""
        
        devices = DeviceTrust.objects.filter(
            user=self.user,
            is_revoked=False
        ).order_by('-last_activity_at')
        
        return [
            {
                'id': str(d.id),
                'device_name': d.device_name,
                'device_type': d.device_type,
                'trust_level': d.trust_level,
                'is_trusted': d.is_trusted,
                'last_activity_at': d.last_activity_at.isoformat(),
                'last_ip_address': d.last_ip_address,
                'login_count': d.login_count
            }
            for d in devices
        ]
    
    def _parse_user_agent(self, user_agent: str) -> Dict:
        """Parse user agent string"""
        
        result = {
            'device_type': 'desktop',
            'os': 'Unknown',
            'os_version': '',
            'browser': 'Unknown',
            'browser_version': ''
        }
        
        # Detect device type
        if 'Mobile' in user_agent or 'Android' in user_agent:
            result['device_type'] = 'mobile'
        elif 'Tablet' in user_agent or 'iPad' in user_agent:
            result['device_type'] = 'tablet'
        
        # Detect OS
        if 'Windows' in user_agent:
            result['os'] = 'Windows'
        elif 'Mac OS' in user_agent or 'Macintosh' in user_agent:
            result['os'] = 'macOS'
        elif 'Linux' in user_agent:
            result['os'] = 'Linux'
        elif 'Android' in user_agent:
            result['os'] = 'Android'
        elif 'iOS' in user_agent or 'iPhone' in user_agent:
            result['os'] = 'iOS'
        
        # Detect browser
        if 'Chrome' in user_agent:
            result['browser'] = 'Chrome'
        elif 'Firefox' in user_agent:
            result['browser'] = 'Firefox'
        elif 'Safari' in user_agent:
            result['browser'] = 'Safari'
        elif 'Edge' in user_agent:
            result['browser'] = 'Edge'
        
        return result


class ContinuousAuthService:
    """Service for continuous authentication"""
    
    def __init__(self, user):
        self.user = user
    
    @transaction.atomic
    def create_session(
        self,
        session_key: str,
        ip_address: str,
        device: Optional[DeviceTrust] = None,
        auth_method: str = 'password',
        mfa_verified: bool = False
    ) -> SecuritySession:
        """Create a new security session"""
        
        # Calculate auth strength
        auth_strength = self._calculate_auth_strength(auth_method, mfa_verified, device)
        
        # Calculate risk score
        risk_score, risk_factors = self._assess_risk(ip_address, device)
        
        session = SecuritySession.objects.create(
            user=self.user,
            device=device,
            session_key=session_key,
            auth_method=auth_method,
            mfa_verified=mfa_verified,
            auth_strength=auth_strength,
            ip_address=ip_address,
            risk_score=risk_score,
            risk_factors=risk_factors,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        return session
    
    def verify_session(self, session_key: str) -> Dict:
        """Verify a session is still valid"""
        
        try:
            session = SecuritySession.objects.get(
                session_key=session_key,
                user=self.user
            )
        except SecuritySession.DoesNotExist:
            return {'valid': False, 'reason': 'session_not_found'}
        
        if session.status != 'active':
            return {'valid': False, 'reason': f'session_{session.status}'}
        
        if session.expires_at < timezone.now():
            session.status = 'expired'
            session.save()
            return {'valid': False, 'reason': 'session_expired'}
        
        # Check for idle timeout (15 minutes)
        idle_threshold = timezone.now() - timedelta(minutes=15)
        if session.last_activity_at < idle_threshold:
            session.status = 'idle'
            session.save()
            return {
                'valid': True,
                'requires_reauth': True,
                'reason': 'session_idle'
            }
        
        return {
            'valid': True,
            'session_id': str(session.id),
            'auth_strength': session.auth_strength,
            'risk_score': session.risk_score
        }
    
    def step_up_auth(self, session_key: str) -> Dict:
        """Require step-up authentication"""
        
        try:
            session = SecuritySession.objects.get(
                session_key=session_key,
                user=self.user
            )
        except SecuritySession.DoesNotExist:
            raise ValueError("Session not found")
        
        return {
            'session_id': str(session.id),
            'current_auth_strength': session.auth_strength,
            'required_auth_strength': 4,
            'mfa_required': not session.mfa_verified,
            'challenge_url': '/auth/challenge'
        }
    
    def terminate_session(
        self,
        session_key: str,
        reason: str = 'user_logout'
    ) -> Dict:
        """Terminate a session"""
        
        try:
            session = SecuritySession.objects.get(
                session_key=session_key,
                user=self.user
            )
        except SecuritySession.DoesNotExist:
            raise ValueError("Session not found")
        
        session.status = 'terminated'
        session.terminated_at = timezone.now()
        session.termination_reason = reason
        session.save()
        
        return {
            'session_id': str(session.id),
            'terminated': True
        }
    
    def terminate_all_sessions(self, except_current: Optional[str] = None) -> Dict:
        """Terminate all user sessions"""
        
        sessions = SecuritySession.objects.filter(
            user=self.user,
            status='active'
        )
        
        if except_current:
            sessions = sessions.exclude(session_key=except_current)
        
        count = sessions.update(
            status='terminated',
            terminated_at=timezone.now(),
            termination_reason='user_terminated_all'
        )
        
        return {'terminated_count': count}
    
    def _calculate_auth_strength(
        self,
        auth_method: str,
        mfa_verified: bool,
        device: Optional[DeviceTrust]
    ) -> int:
        """Calculate authentication strength (1-5)"""
        
        strength = 1
        
        # Auth method
        if auth_method == 'passkey':
            strength += 2
        elif auth_method == 'sso':
            strength += 1
        
        # MFA
        if mfa_verified:
            strength += 1
        
        # Trusted device
        if device and device.is_trusted:
            strength += 1
        
        return min(strength, 5)
    
    def _assess_risk(
        self,
        ip_address: str,
        device: Optional[DeviceTrust]
    ) -> tuple:
        """Assess risk score and factors"""
        
        risk_score = 0
        risk_factors = []
        
        # New device
        if not device or not device.is_trusted:
            risk_score += 20
            risk_factors.append('untrusted_device')
        
        # Check for known bad IPs (would use threat intelligence in production)
        # ...
        
        # Check for impossible travel
        if device and device.last_ip_address and device.last_ip_address != ip_address:
            # Simplified check - in production, use geo-distance calculation
            risk_score += 10
            risk_factors.append('location_change')
        
        return risk_score, risk_factors


class AuditLogService:
    """Service for immutable audit logging"""
    
    @staticmethod
    @transaction.atomic
    def log(
        user,
        action: str,
        action_category: str,
        resource_type: str,
        resource_id: str,
        ip_address: str = '',
        old_values: Dict = None,
        new_values: Dict = None,
        metadata: Dict = None,
        severity: str = 'info',
        session: Optional[SecuritySession] = None,
        compliance_frameworks: List[str] = None
    ) -> ImmutableAuditLog:
        """Create an immutable audit log entry"""
        
        # Get previous hash for chain
        previous = ImmutableAuditLog.objects.order_by('-timestamp').first()
        previous_hash = previous.log_hash if previous else ''
        
        log_entry = ImmutableAuditLog.objects.create(
            user=user,
            user_email=user.email if user else 'system@crm.local',
            user_role=getattr(user, 'role', 'unknown') if user else 'system',
            session=session,
            ip_address=ip_address or '0.0.0.0',
            action=action,
            action_category=action_category,
            severity=severity,
            resource_type=resource_type,
            resource_id=str(resource_id),
            old_values=old_values or {},
            new_values=new_values or {},
            metadata=metadata or {},
            previous_hash=previous_hash,
            compliance_frameworks=compliance_frameworks or []
        )
        
        return log_entry
    
    @staticmethod
    def search(
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        action_category: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Search audit logs"""
        
        queryset = ImmutableAuditLog.objects.all()
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if action:
            queryset = queryset.filter(action__icontains=action)
        if action_category:
            queryset = queryset.filter(action_category=action_category)
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)
        if resource_id:
            queryset = queryset.filter(resource_id=resource_id)
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        if severity:
            queryset = queryset.filter(severity=severity)
        
        logs = queryset.order_by('-timestamp')[:limit]
        
        return [
            {
                'id': str(log.id),
                'timestamp': log.timestamp.isoformat(),
                'user_email': log.user_email,
                'action': log.action,
                'action_category': log.action_category,
                'severity': log.severity,
                'resource_type': log.resource_type,
                'resource_id': log.resource_id,
                'old_values': log.old_values,
                'new_values': log.new_values,
                'ip_address': log.ip_address
            }
            for log in logs
        ]
    
    @staticmethod
    def verify_chain_integrity(start_id: str = None, end_id: str = None) -> Dict:
        """Verify the integrity of the audit log chain"""
        
        queryset = ImmutableAuditLog.objects.order_by('timestamp')
        
        if start_id:
            start_log = ImmutableAuditLog.objects.get(id=start_id)
            queryset = queryset.filter(timestamp__gte=start_log.timestamp)
        
        if end_id:
            end_log = ImmutableAuditLog.objects.get(id=end_id)
            queryset = queryset.filter(timestamp__lte=end_log.timestamp)
        
        logs = list(queryset)
        
        invalid_entries = []
        for i, log in enumerate(logs):
            # Verify hash
            expected_hash = log._generate_hash()
            if log.log_hash != expected_hash:
                invalid_entries.append({
                    'id': str(log.id),
                    'reason': 'hash_mismatch'
                })
            
            # Verify chain
            if i > 0 and log.previous_hash != logs[i-1].log_hash:
                invalid_entries.append({
                    'id': str(log.id),
                    'reason': 'chain_broken'
                })
        
        return {
            'verified': len(invalid_entries) == 0,
            'total_entries': len(logs),
            'invalid_entries': invalid_entries
        }
    
    @staticmethod
    def generate_compliance_report(
        framework: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Generate compliance report for a framework"""
        
        logs = ImmutableAuditLog.objects.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date,
            compliance_frameworks__contains=[framework]
        )
        
        # Group by category
        by_category = {}
        for log in logs:
            category = log.action_category
            if category not in by_category:
                by_category[category] = {'count': 0, 'critical': 0}
            by_category[category]['count'] += 1
            if log.severity == 'critical':
                by_category[category]['critical'] += 1
        
        return {
            'framework': framework,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_events': logs.count(),
            'by_category': by_category,
            'generated_at': timezone.now().isoformat()
        }


class DLPService:
    """Service for Data Loss Prevention"""
    
    def __init__(self, user):
        self.user = user
    
    def classify_content(self, content: str) -> Dict:
        """Classify content based on patterns"""
        
        classifications = DataClassification.objects.filter(
            patterns__len__gt=0
        ) | DataClassification.objects.filter(
            keywords__len__gt=0
        )
        
        matches = []
        highest_level = None
        
        level_order = ['public', 'internal', 'confidential', 'restricted', 'top_secret']
        
        for classification in classifications:
            matched = False
            matched_patterns = []
            
            # Check patterns
            for pattern in classification.patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    matched = True
                    matched_patterns.append(pattern)
            
            # Check keywords
            for keyword in classification.keywords:
                if keyword.lower() in content.lower():
                    matched = True
                    matched_patterns.append(f"keyword:{keyword}")
            
            if matched:
                matches.append({
                    'classification': classification.name,
                    'level': classification.level,
                    'patterns': matched_patterns
                })
                
                if not highest_level or level_order.index(classification.level) > level_order.index(highest_level):
                    highest_level = classification.level
        
        return {
            'matches': matches,
            'highest_level': highest_level,
            'classification_count': len(matches)
        }
    
    def check_action(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        classification_level: str
    ) -> Dict:
        """Check if an action is allowed by DLP policies"""
        
        # Get applicable policies
        policies = DLPPolicy.objects.filter(
            is_active=True,
            classifications__level=classification_level
        ).order_by('-priority')
        
        for policy in policies:
            # Check if user is exempt
            if self.user.id in policy.exempt_users.values_list('id', flat=True):
                continue
            
            # Check action type
            action_map = {
                'download': policy.on_download,
                'export': policy.on_export,
                'share': policy.on_share,
                'email': policy.on_email,
                'print': policy.on_print,
                'copy': policy.on_copy,
            }
            
            if action_map.get(action, False):
                # Policy applies
                if policy.action == 'block':
                    # Log incident
                    self._create_incident(
                        policy, action, resource_type, resource_id,
                        classification_level, 'blocked'
                    )
                    return {
                        'allowed': False,
                        'action': 'block',
                        'message': policy.notification_template or 'This action is not allowed.'
                    }
                
                elif policy.action == 'warn':
                    # Log incident but allow
                    self._create_incident(
                        policy, action, resource_type, resource_id,
                        classification_level, 'warned'
                    )
                    return {
                        'allowed': True,
                        'action': 'warn',
                        'message': policy.notification_template or 'This action has been logged.'
                    }
        
        return {'allowed': True, 'action': 'allow'}
    
    def _create_incident(
        self,
        policy: DLPPolicy,
        action: str,
        resource_type: str,
        resource_id: str,
        classification_level: str,
        action_taken: str
    ):
        """Create a DLP incident"""
        
        classification = DataClassification.objects.filter(
            level=classification_level
        ).first()
        
        DLPIncident.objects.create(
            policy=policy,
            user=self.user,
            user_email=self.user.email,
            action_attempted=action,
            resource_type=resource_type,
            resource_id=resource_id,
            classification=classification,
            detection_method='policy_check',
            action_taken=action_taken,
            was_blocked=action_taken == 'blocked'
        )
    
    def get_incidents(
        self,
        status: Optional[str] = None,
        days: int = 30
    ) -> List[Dict]:
        """Get DLP incidents"""
        
        since = timezone.now() - timedelta(days=days)
        
        queryset = DLPIncident.objects.filter(
            occurred_at__gte=since
        )
        
        if status:
            queryset = queryset.filter(status=status)
        
        incidents = queryset.order_by('-occurred_at')[:100]
        
        return [
            {
                'id': str(i.id),
                'user_email': i.user_email,
                'action_attempted': i.action_attempted,
                'resource_type': i.resource_type,
                'status': i.status,
                'was_blocked': i.was_blocked,
                'occurred_at': i.occurred_at.isoformat()
            }
            for i in incidents
        ]


class AccessPolicyService:
    """Service for micro-segmentation access policies"""
    
    def evaluate_access(
        self,
        user,
        request_path: str,
        request_context: Dict
    ) -> Dict:
        """Evaluate access based on policies"""
        
        # Get applicable policies
        policies = AccessPolicy.objects.filter(is_active=True).order_by('-priority')
        
        for policy in policies:
            # Check if path matches
            if not self._path_matches(request_path, policy.resource_patterns):
                continue
            
            # Evaluate conditions
            result = self._evaluate_conditions(user, policy.conditions, request_context)
            
            if result['matches']:
                return {
                    'allowed': policy.effect == 'allow',
                    'policy_id': str(policy.id),
                    'policy_name': policy.name,
                    'effect': policy.effect,
                    'conditions_met': result['conditions_met']
                }
        
        # Default allow if no policies match
        return {
            'allowed': True,
            'policy_id': None,
            'policy_name': 'default',
            'effect': 'allow'
        }
    
    def _path_matches(self, path: str, patterns: List[str]) -> bool:
        """Check if path matches any pattern"""
        
        for pattern in patterns:
            # Convert glob-like pattern to regex
            regex = pattern.replace('*', '.*').replace('?', '.')
            if re.match(f'^{regex}$', path):
                return True
        
        return False
    
    def _evaluate_conditions(
        self,
        user,
        conditions: Dict,
        context: Dict
    ) -> Dict:
        """Evaluate policy conditions"""
        
        conditions_met = []
        
        # Check roles
        if 'roles' in conditions:
            user_role = getattr(user, 'role', 'user')
            if user_role in conditions['roles']:
                conditions_met.append('role')
            else:
                return {'matches': False, 'conditions_met': []}
        
        # Check IP ranges
        if 'ip_ranges' in conditions:
            client_ip = context.get('ip_address', '')
            if self._ip_in_ranges(client_ip, conditions['ip_ranges']):
                conditions_met.append('ip_range')
            else:
                return {'matches': False, 'conditions_met': []}
        
        # Check MFA
        if conditions.get('mfa_required'):
            if context.get('mfa_verified'):
                conditions_met.append('mfa')
            else:
                return {'matches': False, 'conditions_met': []}
        
        # Check device trust
        if 'device_trust' in conditions:
            if context.get('device_trust') == conditions['device_trust']:
                conditions_met.append('device_trust')
            else:
                return {'matches': False, 'conditions_met': []}
        
        return {'matches': True, 'conditions_met': conditions_met}
    
    def _ip_in_ranges(self, ip: str, ranges: List[str]) -> bool:
        """Check if IP is in any of the ranges"""
        import ipaddress
        
        try:
            client_ip = ipaddress.ip_address(ip)
            for range_str in ranges:
                network = ipaddress.ip_network(range_str, strict=False)
                if client_ip in network:
                    return True
        except ValueError:
            pass
        
        return False
