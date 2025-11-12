"""
Enterprise Security Module for MyCRM
Provides advanced security features for enterprise-grade CRM
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import logging
import hashlib
import json

User = get_user_model()
logger = logging.getLogger(__name__)


class SecurityAuditLog:
    """Enhanced audit logging for enterprise security compliance"""
    
    @staticmethod
    def log_event(user, action, resource=None, ip_address=None, user_agent=None, 
                  metadata=None, risk_level='low'):
        """
        Log security events for audit trail
        
        Args:
            user: User performing the action
            action: Action being performed (e.g., 'login', 'data_access', 'data_modification')
            resource: Resource being accessed (optional)
            ip_address: Client IP address
            user_agent: Client user agent
            metadata: Additional metadata (dict)
            risk_level: 'low', 'medium', 'high', 'critical'
        """
        from .models import AuditLog
        
        AuditLog.objects.create(
            user=user,
            action=action,
            resource=resource,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {},
            risk_level=risk_level,
            timestamp=timezone.now()
        )
        
        # Log to system logger for external SIEM integration
        logger.info(
            f"AUDIT: User {user.username if user else 'Anonymous'} "
            f"performed {action} on {resource or 'system'} "
            f"from {ip_address} - Risk: {risk_level}"
        )


class RateLimitManager:
    """Advanced rate limiting with multiple strategies"""
    
    @staticmethod
    def check_rate_limit(identifier, action, limit=100, window=3600):
        """
        Check if rate limit is exceeded
        
        Args:
            identifier: Unique identifier (user_id, ip_address, etc.)
            action: Action being rate limited
            limit: Number of allowed requests
            window: Time window in seconds
        
        Returns:
            tuple: (is_allowed, remaining_requests, reset_time)
        """
        cache_key = f"rate_limit:{action}:{identifier}"
        current_time = timezone.now()
        window_start = current_time - timedelta(seconds=window)
        
        # Get current requests in window
        requests = cache.get(cache_key, [])
        
        # Remove old requests outside the window
        requests = [req_time for req_time in requests if req_time > window_start]
        
        if len(requests) >= limit:
            return False, 0, window_start + timedelta(seconds=window)
        
        # Add current request
        requests.append(current_time)
        cache.set(cache_key, requests, window)
        
        return True, limit - len(requests), window_start + timedelta(seconds=window)
    
    @staticmethod
    def apply_rate_limit(view_func):
        """Decorator for applying rate limits to views"""
        def wrapper(request, *args, **kwargs):
            # Get identifier (user ID or IP)
            identifier = str(request.user.id) if request.user.is_authenticated else request.META.get('REMOTE_ADDR')
            action = f"{request.method}_{view_func.__name__}"
            
            # Different limits for different user types
            if request.user.is_authenticated:
                if request.user.role == 'admin':
                    limit = 1000  # Higher limit for admins
                else:
                    limit = 500   # Standard limit for authenticated users
            else:
                limit = 100   # Lower limit for anonymous users
            
            is_allowed, remaining, reset_time = RateLimitManager.check_rate_limit(
                identifier, action, limit
            )
            
            if not is_allowed:
                return JsonResponse(
                    {
                        'error': 'Rate limit exceeded',
                        'detail': f'Request limit of {limit} per hour exceeded',
                        'reset_time': reset_time.isoformat()
                    },
                    status=429
                )
            
            # Add rate limit headers
            response = view_func(request, *args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(limit)
                response.headers['X-RateLimit-Remaining'] = str(remaining)
                response.headers['X-RateLimit-Reset'] = reset_time.isoformat()
            
            return response
        return wrapper


class DataEncryption:
    """Enterprise-grade data encryption utilities"""
    
    @staticmethod
    def encrypt_sensitive_data(data):
        """Encrypt sensitive data using AES encryption"""
        from cryptography.fernet import Fernet
        
        # In production, this should come from environment variables
        key = settings.ENCRYPTION_KEY if hasattr(settings, 'ENCRYPTION_KEY') else Fernet.generate_key()
        cipher_suite = Fernet(key)
        
        if isinstance(data, str):
            data = data.encode()
        
        return cipher_suite.encrypt(data).decode()
    
    @staticmethod
    def decrypt_sensitive_data(encrypted_data):
        """Decrypt sensitive data"""
        from cryptography.fernet import Fernet
        
        key = settings.ENCRYPTION_KEY if hasattr(settings, 'ENCRYPTION_KEY') else None
        if not key:
            raise ValueError("Encryption key not found in settings")
        
        cipher_suite = Fernet(key)
        return cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    @staticmethod
    def hash_password_custom(password, salt=None):
        """Custom password hashing with additional security"""
        import bcrypt
        
        if salt is None:
            salt = bcrypt.gensalt()
        
        return bcrypt.hashpw(password.encode(), salt)


class ThreatDetection:
    """Advanced threat detection and prevention"""
    
    @staticmethod
    def detect_suspicious_activity(user, request):
        """
        Detect suspicious user activity patterns
        
        Returns:
            dict: Threat assessment with risk score and reasons
        """
        risk_score = 0
        risk_factors = []
        
        # Check for unusual login patterns
        if user.is_authenticated:
            # Different IP address
            last_ip = cache.get(f"user_last_ip:{user.id}")
            current_ip = request.META.get('REMOTE_ADDR')
            
            if last_ip and last_ip != current_ip:
                risk_score += 20
                risk_factors.append('Different IP address')
            
            cache.set(f"user_last_ip:{user.id}", current_ip, 86400)  # 24 hours
            
            # Unusual time pattern
            current_hour = timezone.now().hour
            if current_hour < 6 or current_hour > 22:  # Outside business hours
                risk_score += 10
                risk_factors.append('Outside business hours')
            
            # Multiple rapid requests
            request_count = cache.get(f"user_requests:{user.id}:{timezone.now().minute}", 0)
            if request_count > 50:  # More than 50 requests per minute
                risk_score += 30
                risk_factors.append('High request rate')
        
        # Check user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'bot' in user_agent.lower() or not user_agent:
            risk_score += 25
            risk_factors.append('Suspicious user agent')
        
        # Determine risk level
        if risk_score >= 50:
            risk_level = 'high'
        elif risk_score >= 30:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'requires_additional_auth': risk_score >= 40
        }


class AdvancedPermissions:
    """Enhanced RBAC (Role-Based Access Control) system"""
    
    @staticmethod
    def check_resource_permission(user, resource, action):
        """
        Check if user has permission to perform action on resource
        
        Args:
            user: User object
            resource: Resource name (e.g., 'contact', 'lead', 'opportunity')
            action: Action (e.g., 'view', 'create', 'update', 'delete')
        
        Returns:
            bool: True if permission granted
        """
        # Super admin has all permissions
        if user.role == 'admin':
            return True
        
        # Define permission matrix
        permission_matrix = {
            'sales_rep': {
                'contact': ['view', 'create', 'update'],
                'lead': ['view', 'create', 'update'],
                'opportunity': ['view', 'create', 'update'],
                'task': ['view', 'create', 'update'],
                'communication': ['view', 'create', 'update'],
                'report': ['view']
            },
            'marketing': {
                'contact': ['view', 'create', 'update'],
                'lead': ['view', 'create', 'update'],
                'opportunity': ['view'],
                'task': ['view', 'create', 'update'],
                'communication': ['view', 'create', 'update'],
                'report': ['view']
            },
            'customer_support': {
                'contact': ['view', 'update'],
                'lead': ['view'],
                'opportunity': ['view'],
                'task': ['view', 'create', 'update'],
                'communication': ['view', 'create', 'update'],
                'report': ['view']
            },
            'manager': {
                'contact': ['view', 'create', 'update', 'delete'],
                'lead': ['view', 'create', 'update', 'delete'],
                'opportunity': ['view', 'create', 'update', 'delete'],
                'task': ['view', 'create', 'update', 'delete'],
                'communication': ['view', 'create', 'update'],
                'report': ['view', 'create', 'update']
            }
        }
        
        user_permissions = permission_matrix.get(user.role, {})
        resource_permissions = user_permissions.get(resource, [])
        
        return action in resource_permissions
    
    @staticmethod
    def get_user_permissions(user):
        """Get all permissions for a user"""
        if user.role == 'admin':
            return {'all': True}
        
        return AdvancedPermissions.check_resource_permission.__defaults__[0].get(user.role, {})


class SecurityMiddleware:
    """Custom security middleware for enterprise features"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Pre-request security checks
        self.security_headers(request)
        self.threat_detection(request)
        
        response = self.get_response(request)
        
        # Post-request security processing
        self.add_security_headers(response)
        self.log_security_event(request, response)
        
        return response
    
    def security_headers(self, request):
        """Add security headers to request"""
        pass
    
    def threat_detection(self, request):
        """Perform threat detection on request"""
        # Check if user attribute exists (authentication middleware may not have run yet)
        if hasattr(request, 'user') and request.user.is_authenticated:
            threat_assessment = ThreatDetection.detect_suspicious_activity(request.user, request)
            if threat_assessment['risk_level'] == 'high':
                SecurityAuditLog.log_event(
                    request.user,
                    'high_risk_activity',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    metadata=threat_assessment,
                    risk_level='high'
                )
    
    def add_security_headers(self, response):
        """Add security headers to response"""
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Content-Security-Policy'] = "default-src 'self'"
        
        return response
    
    def log_security_event(self, request, response):
        """Log security events"""
        if response.status_code >= 400:
            # Check if user attribute exists before accessing it
            user = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user
            
            SecurityAuditLog.log_event(
                user,
                f'http_{response.status_code}',
                resource=request.path,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                risk_level='medium' if response.status_code >= 500 else 'low'
            )