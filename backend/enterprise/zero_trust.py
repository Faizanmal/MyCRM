"""
Zero-Trust Security Architecture for MyCRM

Implements the principle: "Never Trust, Always Verify"

Features:
- Continuous authentication verification
- Risk-based access decisions
- Device trust verification
- Microsegmentation policies
- Session-based access tokens
- Just-in-time access provisioning
- Behavioral anomaly detection
"""

import logging
import hashlib
import json
from typing import Dict, Optional, List, Any, Callable
from datetime import datetime, timedelta
from functools import wraps
from dataclasses import dataclass, field
from enum import Enum
import re

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse, HttpRequest
from django.utils import timezone
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class RiskLevel(Enum):
    """Risk levels for access decisions"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class AccessDecision(Enum):
    """Access decision outcomes"""
    ALLOW = 'allow'
    DENY = 'deny'
    CHALLENGE = 'challenge'  # Require additional verification
    STEP_UP = 'step_up'  # Require MFA


@dataclass
class RequestContext:
    """Context information for access decisions"""
    user_id: Optional[int] = None
    ip_address: str = ''
    user_agent: str = ''
    device_fingerprint: str = ''
    geo_location: Optional[Dict] = None
    request_path: str = ''
    request_method: str = ''
    timestamp: datetime = field(default_factory=timezone.now)
    headers: Dict = field(default_factory=dict)
    session_id: Optional[str] = None
    mfa_verified: bool = False
    device_trusted: bool = False
    
    @classmethod
    def from_request(cls, request: HttpRequest) -> 'RequestContext':
        """Create context from Django request"""
        return cls(
            user_id=request.user.id if request.user.is_authenticated else None,
            ip_address=cls._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            device_fingerprint=request.META.get('HTTP_X_DEVICE_FINGERPRINT', ''),
            geo_location=cls._get_geo_location(request),
            request_path=request.path,
            request_method=request.method,
            headers=dict(request.headers),
            session_id=request.session.session_key,
            mfa_verified=request.session.get('mfa_verified', False),
            device_trusted=request.session.get('device_trusted', False)
        )
    
    @staticmethod
    def _get_client_ip(request: HttpRequest) -> str:
        """Extract real client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        
        x_real_ip = request.META.get('HTTP_X_REAL_IP')
        if x_real_ip:
            return x_real_ip
        
        return request.META.get('REMOTE_ADDR', '')
    
    @staticmethod
    def _get_geo_location(request: HttpRequest) -> Optional[Dict]:
        """Get geo location from headers (set by CDN/proxy)"""
        return {
            'country': request.META.get('HTTP_CF_IPCOUNTRY', ''),
            'city': request.META.get('HTTP_CF_IPCITY', ''),
            'region': request.META.get('HTTP_CF_IPREGION', ''),
        }


@dataclass
class AccessPolicy:
    """Access control policy definition"""
    name: str
    description: str = ''
    resource_pattern: str = '*'  # Regex pattern for resources
    allowed_roles: List[str] = field(default_factory=list)
    required_attributes: Dict[str, Any] = field(default_factory=dict)
    conditions: List[Callable[[RequestContext], bool]] = field(default_factory=list)
    risk_threshold: RiskLevel = RiskLevel.MEDIUM
    require_mfa: bool = False
    require_device_trust: bool = False
    allowed_ip_ranges: List[str] = field(default_factory=list)
    allowed_countries: List[str] = field(default_factory=list)
    time_restrictions: Optional[Dict] = None  # e.g., {'start': '09:00', 'end': '18:00'}
    max_session_duration: int = 3600  # seconds
    
    def matches_resource(self, resource: str) -> bool:
        """Check if policy applies to resource"""
        if self.resource_pattern == '*':
            return True
        return bool(re.match(self.resource_pattern, resource))


class RiskEngine:
    """
    Real-time risk assessment engine
    Evaluates multiple risk signals to compute a risk score
    """
    
    RISK_WEIGHTS = {
        'new_device': 25,
        'new_location': 20,
        'unusual_time': 15,
        'high_request_rate': 20,
        'failed_auth_attempts': 30,
        'sensitive_resource': 15,
        'tor_exit_node': 40,
        'known_bad_ip': 50,
        'impossible_travel': 45,
        'session_anomaly': 25,
    }
    
    def __init__(self):
        self._bad_ip_cache = set()
        self._tor_exit_nodes = set()
        self._load_threat_intelligence()
    
    def _load_threat_intelligence(self):
        """Load threat intelligence data"""
        # In production, this would load from threat intel feeds
        # For now, we'll use cached data from Redis
        try:
            bad_ips = cache.get('threat_intel:bad_ips', [])
            self._bad_ip_cache = set(bad_ips)
            
            tor_nodes = cache.get('threat_intel:tor_exit_nodes', [])
            self._tor_exit_nodes = set(tor_nodes)
        except Exception as e:
            logger.warning(f"Could not load threat intelligence: {e}")
    
    def calculate_risk_score(self, context: RequestContext, user=None) -> tuple[int, List[str]]:
        """
        Calculate risk score (0-100) and return risk factors
        
        Returns:
            tuple: (risk_score, list_of_risk_factors)
        """
        risk_score = 0
        risk_factors = []
        
        # Check for new device
        if context.user_id:
            known_devices = cache.get(f'user_devices:{context.user_id}', [])
            if context.device_fingerprint and context.device_fingerprint not in known_devices:
                risk_score += self.RISK_WEIGHTS['new_device']
                risk_factors.append('new_device')
        
        # Check for new location
        if context.user_id and context.geo_location:
            known_countries = cache.get(f'user_countries:{context.user_id}', [])
            if context.geo_location.get('country') and \
               context.geo_location['country'] not in known_countries:
                risk_score += self.RISK_WEIGHTS['new_location']
                risk_factors.append('new_location')
        
        # Check for unusual time
        if self._is_unusual_time(context):
            risk_score += self.RISK_WEIGHTS['unusual_time']
            risk_factors.append('unusual_time')
        
        # Check request rate
        if self._is_high_request_rate(context):
            risk_score += self.RISK_WEIGHTS['high_request_rate']
            risk_factors.append('high_request_rate')
        
        # Check failed auth attempts
        failed_attempts = self._get_failed_auth_attempts(context)
        if failed_attempts >= 3:
            risk_score += self.RISK_WEIGHTS['failed_auth_attempts']
            risk_factors.append(f'failed_auth_attempts:{failed_attempts}')
        
        # Check for sensitive resource access
        if self._is_sensitive_resource(context.request_path):
            risk_score += self.RISK_WEIGHTS['sensitive_resource']
            risk_factors.append('sensitive_resource')
        
        # Check known bad IPs
        if context.ip_address in self._bad_ip_cache:
            risk_score += self.RISK_WEIGHTS['known_bad_ip']
            risk_factors.append('known_bad_ip')
        
        # Check Tor exit nodes
        if context.ip_address in self._tor_exit_nodes:
            risk_score += self.RISK_WEIGHTS['tor_exit_node']
            risk_factors.append('tor_exit_node')
        
        # Check impossible travel
        if context.user_id and self._detect_impossible_travel(context):
            risk_score += self.RISK_WEIGHTS['impossible_travel']
            risk_factors.append('impossible_travel')
        
        return min(risk_score, 100), risk_factors
    
    def get_risk_level(self, score: int) -> RiskLevel:
        """Convert risk score to risk level"""
        if score < 25:
            return RiskLevel.LOW
        elif score < 50:
            return RiskLevel.MEDIUM
        elif score < 75:
            return RiskLevel.HIGH
        return RiskLevel.CRITICAL
    
    def _is_unusual_time(self, context: RequestContext) -> bool:
        """Check if access is at unusual time"""
        if not context.user_id:
            return False
        
        hour = context.timestamp.hour
        
        # Get user's typical access hours
        typical_hours = cache.get(f'user_typical_hours:{context.user_id}', list(range(8, 22)))
        
        return hour not in typical_hours
    
    def _is_high_request_rate(self, context: RequestContext) -> bool:
        """Check for high request rate"""
        cache_key = f'request_rate:{context.ip_address}'
        request_count = cache.get(cache_key, 0)
        
        # Increment counter
        cache.set(cache_key, request_count + 1, 60)
        
        # More than 100 requests per minute is suspicious
        return request_count > 100
    
    def _get_failed_auth_attempts(self, context: RequestContext) -> int:
        """Get recent failed authentication attempts"""
        cache_key = f'failed_auth:{context.ip_address}'
        return cache.get(cache_key, 0)
    
    def _is_sensitive_resource(self, path: str) -> bool:
        """Check if resource is sensitive"""
        sensitive_patterns = [
            r'^/api/admin/',
            r'^/api/users/.*/(password|tokens)/',
            r'^/api/gdpr/',
            r'^/api/billing/',
            r'^/api/export/',
            r'^/api/audit/',
        ]
        
        return any(re.match(pattern, path) for pattern in sensitive_patterns)
    
    def _detect_impossible_travel(self, context: RequestContext) -> bool:
        """Detect impossible travel (login from distant location too quickly)"""
        if not context.user_id or not context.geo_location:
            return False
        
        last_location = cache.get(f'user_last_location:{context.user_id}')
        if not last_location:
            # Store current location
            cache.set(
                f'user_last_location:{context.user_id}',
                {
                    'country': context.geo_location.get('country'),
                    'timestamp': context.timestamp.isoformat()
                },
                86400  # 24 hours
            )
            return False
        
        # Compare locations
        if last_location['country'] != context.geo_location.get('country'):
            last_time = datetime.fromisoformat(last_location['timestamp'])
            time_diff = (context.timestamp - last_time).total_seconds()
            
            # If different country within 2 hours, that's suspicious
            if time_diff < 7200:
                return True
        
        return False


class ZeroTrustPolicy:
    """
    Zero Trust Policy Engine
    Manages and evaluates access policies
    """
    
    def __init__(self):
        self.policies: List[AccessPolicy] = []
        self.risk_engine = RiskEngine()
        self._load_default_policies()
    
    def _load_default_policies(self):
        """Load default security policies"""
        # Admin access policy
        self.add_policy(AccessPolicy(
            name='admin_access',
            description='Access to admin endpoints',
            resource_pattern=r'^/api/admin/.*',
            allowed_roles=['admin', 'superuser'],
            require_mfa=True,
            require_device_trust=True,
            risk_threshold=RiskLevel.LOW,
            max_session_duration=1800
        ))
        
        # GDPR/Compliance endpoints
        self.add_policy(AccessPolicy(
            name='compliance_access',
            description='Access to GDPR and compliance endpoints',
            resource_pattern=r'^/api/(gdpr|compliance|audit)/.*',
            allowed_roles=['admin', 'compliance_officer', 'dpo'],
            require_mfa=True,
            risk_threshold=RiskLevel.LOW
        ))
        
        # User management
        self.add_policy(AccessPolicy(
            name='user_management',
            description='User management operations',
            resource_pattern=r'^/api/users/.*/.*',
            allowed_roles=['admin', 'hr_manager'],
            require_mfa=True
        ))
        
        # Data export
        self.add_policy(AccessPolicy(
            name='data_export',
            description='Data export operations',
            resource_pattern=r'^/api/.*/export.*',
            allowed_roles=['admin', 'manager', 'analyst'],
            require_mfa=True,
            risk_threshold=RiskLevel.MEDIUM
        ))
        
        # API tokens
        self.add_policy(AccessPolicy(
            name='api_tokens',
            description='API token management',
            resource_pattern=r'^/api/tokens/.*',
            require_mfa=True,
            require_device_trust=True
        ))
        
        # Standard API access
        self.add_policy(AccessPolicy(
            name='standard_api',
            description='Standard API access',
            resource_pattern=r'^/api/.*',
            risk_threshold=RiskLevel.HIGH
        ))
    
    def add_policy(self, policy: AccessPolicy):
        """Add a new policy"""
        self.policies.append(policy)
    
    def evaluate(self, context: RequestContext, user=None) -> tuple[AccessDecision, Dict]:
        """
        Evaluate access request against policies
        
        Returns:
            tuple: (decision, details)
        """
        # Calculate risk score
        risk_score, risk_factors = self.risk_engine.calculate_risk_score(context, user)
        risk_level = self.risk_engine.get_risk_level(risk_score)
        
        details = {
            'risk_score': risk_score,
            'risk_level': risk_level.value,
            'risk_factors': risk_factors,
            'evaluated_policies': [],
            'timestamp': context.timestamp.isoformat()
        }
        
        # Find applicable policies
        applicable_policies = [
            p for p in self.policies
            if p.matches_resource(context.request_path)
        ]
        
        if not applicable_policies:
            # No specific policy, use default allow with risk check
            if risk_level in [RiskLevel.CRITICAL]:
                return AccessDecision.DENY, details
            return AccessDecision.ALLOW, details
        
        # Evaluate each applicable policy
        for policy in applicable_policies:
            policy_result = self._evaluate_policy(policy, context, user, risk_level)
            details['evaluated_policies'].append({
                'name': policy.name,
                'result': policy_result.value
            })
            
            if policy_result == AccessDecision.DENY:
                details['denied_by_policy'] = policy.name
                return AccessDecision.DENY, details
            
            if policy_result == AccessDecision.CHALLENGE:
                return AccessDecision.CHALLENGE, details
            
            if policy_result == AccessDecision.STEP_UP:
                return AccessDecision.STEP_UP, details
        
        return AccessDecision.ALLOW, details
    
    def _evaluate_policy(self, policy: AccessPolicy, context: RequestContext, 
                         user, risk_level: RiskLevel) -> AccessDecision:
        """Evaluate a single policy"""
        
        # Check risk threshold
        risk_levels_ordered = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        if risk_levels_ordered.index(risk_level) > risk_levels_ordered.index(policy.risk_threshold):
            if policy.require_mfa and not context.mfa_verified:
                return AccessDecision.STEP_UP
            return AccessDecision.DENY
        
        # Check MFA requirement
        if policy.require_mfa and not context.mfa_verified:
            return AccessDecision.STEP_UP
        
        # Check device trust requirement
        if policy.require_device_trust and not context.device_trusted:
            return AccessDecision.CHALLENGE
        
        # Check role-based access
        if policy.allowed_roles and user:
            user_role = getattr(user, 'role', None)
            if user_role not in policy.allowed_roles:
                return AccessDecision.DENY
        
        # Check IP ranges
        if policy.allowed_ip_ranges:
            if not self._ip_in_ranges(context.ip_address, policy.allowed_ip_ranges):
                return AccessDecision.DENY
        
        # Check country restrictions
        if policy.allowed_countries and context.geo_location:
            if context.geo_location.get('country') not in policy.allowed_countries:
                return AccessDecision.DENY
        
        # Check time restrictions
        if policy.time_restrictions:
            if not self._check_time_restrictions(context.timestamp, policy.time_restrictions):
                return AccessDecision.DENY
        
        # Evaluate custom conditions
        for condition in policy.conditions:
            if not condition(context):
                return AccessDecision.DENY
        
        return AccessDecision.ALLOW
    
    def _ip_in_ranges(self, ip: str, ranges: List[str]) -> bool:
        """Check if IP is in allowed ranges"""
        import ipaddress
        
        try:
            ip_obj = ipaddress.ip_address(ip)
            for range_str in ranges:
                if '/' in range_str:
                    network = ipaddress.ip_network(range_str, strict=False)
                    if ip_obj in network:
                        return True
                elif ip == range_str:
                    return True
        except ValueError:
            return False
        
        return False
    
    def _check_time_restrictions(self, timestamp: datetime, restrictions: Dict) -> bool:
        """Check time restrictions"""
        current_time = timestamp.time()
        
        if 'start' in restrictions and 'end' in restrictions:
            start = datetime.strptime(restrictions['start'], '%H:%M').time()
            end = datetime.strptime(restrictions['end'], '%H:%M').time()
            
            if start <= end:
                return start <= current_time <= end
            else:
                # Handles overnight ranges (e.g., 22:00 to 06:00)
                return current_time >= start or current_time <= end
        
        return True


class ZeroTrustMiddleware:
    """
    Django middleware implementing zero-trust security
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.policy_engine = ZeroTrustPolicy()
        
        # Paths that bypass zero-trust checks
        self.bypass_paths = [
            '/api/health/',
            '/api/auth/login/',
            '/api/auth/token/refresh/',
            '/api/schema/',
            '/api/docs/',
            '/static/',
            '/media/',
        ]
    
    def __call__(self, request):
        # Check if path should bypass
        if self._should_bypass(request.path):
            return self.get_response(request)
        
        # Create request context
        context = RequestContext.from_request(request)
        
        # Get user if authenticated
        user = request.user if request.user.is_authenticated else None
        
        # Evaluate access
        decision, details = self.policy_engine.evaluate(context, user)
        
        # Log the access attempt
        self._log_access_attempt(context, decision, details)
        
        # Handle decision
        if decision == AccessDecision.DENY:
            return JsonResponse({
                'error': 'Access denied',
                'code': 'ZERO_TRUST_DENY',
                'details': {
                    'risk_score': details['risk_score'],
                    'risk_level': details['risk_level']
                }
            }, status=403)
        
        if decision == AccessDecision.STEP_UP:
            return JsonResponse({
                'error': 'MFA required',
                'code': 'MFA_REQUIRED',
                'mfa_challenge_url': '/api/auth/mfa/challenge/'
            }, status=403)
        
        if decision == AccessDecision.CHALLENGE:
            return JsonResponse({
                'error': 'Device verification required',
                'code': 'DEVICE_VERIFICATION_REQUIRED',
                'verification_url': '/api/auth/device/verify/'
            }, status=403)
        
        # Proceed with request
        response = self.get_response(request)
        
        # Add security headers
        response['X-Risk-Score'] = str(details['risk_score'])
        response['X-Zero-Trust-Decision'] = decision.value
        
        return response
    
    def _should_bypass(self, path: str) -> bool:
        """Check if path should bypass zero-trust"""
        return any(path.startswith(bypass) for bypass in self.bypass_paths)
    
    def _log_access_attempt(self, context: RequestContext, decision: AccessDecision, details: Dict):
        """Log access attempt for audit"""
        log_data = {
            'user_id': context.user_id,
            'ip_address': context.ip_address,
            'path': context.request_path,
            'method': context.request_method,
            'decision': decision.value,
            'risk_score': details['risk_score'],
            'risk_factors': details['risk_factors'],
            'timestamp': context.timestamp.isoformat()
        }
        
        if decision == AccessDecision.DENY:
            logger.warning(f"ZERO_TRUST_DENY: {json.dumps(log_data)}")
        else:
            logger.info(f"ZERO_TRUST_ACCESS: {json.dumps(log_data)}")
        
        # Store in cache for analytics
        cache_key = f"zt_access:{context.timestamp.strftime('%Y%m%d%H')}"
        access_log = cache.get(cache_key, [])
        access_log.append(log_data)
        cache.set(cache_key, access_log, 86400)  # Keep for 24 hours


# Decorator for requiring zero-trust verification
def require_zero_trust(risk_threshold: RiskLevel = RiskLevel.MEDIUM, require_mfa: bool = False):
    """
    Decorator to apply zero-trust checks to specific views
    
    Usage:
        @require_zero_trust(risk_threshold=RiskLevel.LOW, require_mfa=True)
        def sensitive_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            context = RequestContext.from_request(request)
            risk_engine = RiskEngine()
            
            risk_score, risk_factors = risk_engine.calculate_risk_score(
                context, 
                request.user if request.user.is_authenticated else None
            )
            risk_level = risk_engine.get_risk_level(risk_score)
            
            # Check risk threshold
            risk_levels_ordered = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
            if risk_levels_ordered.index(risk_level) > risk_levels_ordered.index(risk_threshold):
                return JsonResponse({
                    'error': 'Risk level too high',
                    'risk_score': risk_score,
                    'risk_factors': risk_factors
                }, status=403)
            
            # Check MFA
            if require_mfa and not context.mfa_verified:
                return JsonResponse({
                    'error': 'MFA required',
                    'code': 'MFA_REQUIRED'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


# Device trust management
class DeviceTrustManager:
    """Manage trusted devices for users"""
    
    @staticmethod
    def register_device(user_id: int, device_fingerprint: str, device_info: Dict) -> str:
        """Register a new trusted device"""
        device_id = hashlib.sha256(
            f"{user_id}:{device_fingerprint}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:32]
        
        devices = cache.get(f'user_devices:{user_id}', {})
        devices[device_id] = {
            'fingerprint': device_fingerprint,
            'info': device_info,
            'registered_at': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat(),
            'trusted': True
        }
        
        cache.set(f'user_devices:{user_id}', devices, 86400 * 30)  # 30 days
        
        # Also store fingerprint for quick lookup
        fingerprints = cache.get(f'user_device_fingerprints:{user_id}', [])
        if device_fingerprint not in fingerprints:
            fingerprints.append(device_fingerprint)
            cache.set(f'user_device_fingerprints:{user_id}', fingerprints, 86400 * 30)
        
        logger.info(f"Registered trusted device for user {user_id}: {device_id}")
        return device_id
    
    @staticmethod
    def verify_device(user_id: int, device_fingerprint: str) -> bool:
        """Verify if device is trusted"""
        fingerprints = cache.get(f'user_device_fingerprints:{user_id}', [])
        return device_fingerprint in fingerprints
    
    @staticmethod
    def revoke_device(user_id: int, device_id: str):
        """Revoke a trusted device"""
        devices = cache.get(f'user_devices:{user_id}', {})
        
        if device_id in devices:
            fingerprint = devices[device_id]['fingerprint']
            del devices[device_id]
            cache.set(f'user_devices:{user_id}', devices, 86400 * 30)
            
            # Remove fingerprint
            fingerprints = cache.get(f'user_device_fingerprints:{user_id}', [])
            if fingerprint in fingerprints:
                fingerprints.remove(fingerprint)
                cache.set(f'user_device_fingerprints:{user_id}', fingerprints, 86400 * 30)
            
            logger.info(f"Revoked trusted device for user {user_id}: {device_id}")
    
    @staticmethod
    def list_devices(user_id: int) -> Dict:
        """List all trusted devices for a user"""
        return cache.get(f'user_devices:{user_id}', {})
