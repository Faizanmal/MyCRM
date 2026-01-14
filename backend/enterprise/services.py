"""
Security Services for Zero-Trust Implementation
"""

import hashlib
import re

from django.utils import timezone

from .models import SecurityAuditLog, ThreatIndicator


class SecurityService:
    """Core security service for zero-trust architecture"""

    @staticmethod
    def log_audit_event(
        user,
        action,
        category,
        description,
        resource_type=None,
        resource_id=None,
        resource_name=None,
        old_values=None,
        new_values=None,
        severity='info',
        success=True,
        error_message='',
        request=None
    ):
        """Log a security audit event"""
        ip_address = None
        user_agent = ''

        if request:
            ip_address = SecurityService.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')

        return SecurityAuditLog.objects.create(
            user=user,
            action=action,
            category=category,
            severity=severity,
            description=description,
            resource_type=resource_type or '',
            resource_id=str(resource_id) if resource_id else '',
            resource_name=resource_name or '',
            old_values=old_values or {},
            new_values=new_values or {},
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message
        )

    @staticmethod
    def get_client_ip(request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def check_threat_indicators(indicator_type, value):
        """Check if a value matches any threat indicators"""
        indicator = ThreatIndicator.objects.filter(
            indicator_type=indicator_type,
            value=value,
            is_active=True
        ).first()

        if indicator:
            if indicator.expires_at and indicator.expires_at < timezone.now():
                return None

            indicator.hit_count += 1
            indicator.last_hit = timezone.now()
            indicator.save()

            return indicator

        return None

    @staticmethod
    def evaluate_policy(policy, user_id, context):
        """Evaluate an access policy against context"""
        results = {
            'allowed': True,
            'matched_rules': [],
            'actions': []
        }

        for rule in policy.rules:
            condition = rule.get('condition', {})
            matched = SecurityService._evaluate_condition(condition, context)

            if matched:
                results['matched_rules'].append(rule.get('name', 'Unnamed rule'))
                action = rule.get('action', 'allow')
                results['actions'].append(action)

                if action == 'deny':
                    results['allowed'] = False
                elif action == 'require_mfa':
                    results['require_mfa'] = True

        return results

    @staticmethod
    def _evaluate_condition(condition, context):
        """Evaluate a single condition"""
        operator = condition.get('operator', 'equals')
        field = condition.get('field')
        value = condition.get('value')

        context_value = context.get(field)

        if operator == 'equals':
            return context_value == value
        elif operator == 'not_equals':
            return context_value != value
        elif operator == 'contains':
            return value in str(context_value)
        elif operator == 'in':
            return context_value in value
        elif operator == 'not_in':
            return context_value not in value
        elif operator == 'greater_than':
            return float(context_value) > float(value)
        elif operator == 'less_than':
            return float(context_value) < float(value)
        elif operator == 'regex':
            return bool(re.match(value, str(context_value)))

        return False

    @staticmethod
    def calculate_risk_score(session, device, user, request):
        """Calculate risk score for a session"""
        score = 0
        factors = []

        # Device trust
        if device:
            if device.trust_level == 'blocked':
                score += 100
                factors.append('blocked_device')
            elif device.trust_level == 'suspicious':
                score += 50
                factors.append('suspicious_device')
            elif device.trust_level == 'unknown':
                score += 20
                factors.append('unknown_device')
        else:
            score += 30
            factors.append('no_device_fingerprint')

        # Location anomaly
        if device and session:
            if session.country and device.last_country:
                if session.country != device.last_country:
                    score += 25
                    factors.append('location_change')

        # Check threat indicators
        ip = SecurityService.get_client_ip(request)
        if ip:
            threat = SecurityService.check_threat_indicators('ip', ip)
            if threat:
                if threat.threat_level == 'critical':
                    score += 80
                elif threat.threat_level == 'high':
                    score += 50
                elif threat.threat_level == 'medium':
                    score += 30
                factors.append(f'threat_ip_{threat.threat_level}')

        # Time-based risk
        now = timezone.now()
        if now.hour < 6 or now.hour > 22:
            score += 10
            factors.append('unusual_hours')

        return min(score, 100), factors

    @staticmethod
    def generate_fingerprint_hash(components):
        """Generate a consistent fingerprint hash"""
        fingerprint_string = '|'.join([
            str(components.get('user_agent', '')),
            str(components.get('screen_resolution', '')),
            str(components.get('timezone', '')),
            str(components.get('language', '')),
            str(components.get('canvas_hash', '')),
            str(components.get('webgl_hash', '')),
            str(components.get('audio_hash', '')),
            str(components.get('font_hash', '')),
        ])

        return hashlib.sha256(fingerprint_string.encode()).hexdigest()


class DataLossPreventionService:
    """DLP service for data classification and protection"""

    @staticmethod
    def classify_content(content, classifications=None):
        """Classify content based on patterns and keywords"""
        from .models import DataClassification

        if classifications is None:
            classifications = DataClassification.objects.filter(is_active=True)

        matches = []

        for classification in classifications:
            # Check patterns
            for pattern in classification.patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    matches.append({
                        'classification': classification.name,
                        'sensitivity': classification.sensitivity_level,
                        'match_type': 'pattern',
                        'pattern': pattern
                    })

            # Check keywords
            for keyword in classification.keywords:
                if keyword.lower() in content.lower():
                    matches.append({
                        'classification': classification.name,
                        'sensitivity': classification.sensitivity_level,
                        'match_type': 'keyword',
                        'keyword': keyword
                    })

        # Return highest sensitivity match
        sensitivity_order = ['public', 'internal', 'confidential', 'restricted', 'secret']

        if matches:
            matches.sort(key=lambda x: sensitivity_order.index(x['sensitivity']), reverse=True)
            return matches[0]

        return None

    @staticmethod
    def check_export_allowed(content, user, export_type):
        """Check if content can be exported"""
        classification = DataLossPreventionService.classify_content(content)

        if not classification:
            return {'allowed': True}

        from .models import DataClassification

        try:
            data_class = DataClassification.objects.get(
                name=classification['classification']
            )
        except DataClassification.DoesNotExist:
            return {'allowed': True}

        if not data_class.export_allowed:
            return {
                'allowed': False,
                'reason': f"Export not allowed for {data_class.get_sensitivity_level_display()} data",
                'classification': classification
            }

        return {'allowed': True, 'classification': classification}
