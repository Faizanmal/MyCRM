"""
Zero-Trust Security Views
"""

from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    AccessPolicy,
    DataClassification,
    DeviceFingerprint,
    SecurityAuditLog,
    SecurityIncident,
    SecuritySession,
    ThreatIndicator,
)
from .serializers import (
    AccessPolicySerializer,
    DataClassificationSerializer,
    DeviceFingerprintSerializer,
    RegisterDeviceSerializer,
    SecurityAuditLogDetailSerializer,
    SecurityAuditLogSerializer,
    SecurityIncidentDetailSerializer,
    SecurityIncidentSerializer,
    SecuritySessionSerializer,
    ThreatIndicatorSerializer,
)
from .services import SecurityService


class DeviceFingerprintViewSet(viewsets.ModelViewSet):
    """Manage user devices"""
    serializer_class = DeviceFingerprintSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'delete']

    def get_queryset(self):
        return DeviceFingerprint.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new device"""
        serializer = RegisterDeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        fingerprint_hash = data['fingerprint_hash']

        device, created = DeviceFingerprint.objects.update_or_create(
            fingerprint_hash=fingerprint_hash,
            defaults={
                'user': request.user,
                'device_name': data.get('device_name', ''),
                'user_agent': data.get('user_agent', ''),
                'screen_resolution': data.get('screen_resolution', ''),
                'timezone': data.get('timezone', ''),
                'language': data.get('language', ''),
                'canvas_hash': data.get('canvas_hash', ''),
                'webgl_hash': data.get('webgl_hash', ''),
            }
        )

        if not created:
            device.login_count += 1
            device.save()

        return Response(DeviceFingerprintSerializer(device).data)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a device via MFA"""
        device = self.get_object()
        # Verification logic would be implemented here
        device.is_verified = True
        device.verified_at = timezone.now()
        device.verification_method = 'mfa'
        device.trust_level = 'verified'
        device.trust_score = 80
        device.save()

        return Response(DeviceFingerprintSerializer(device).data)

    @action(detail=True, methods=['post'])
    def trust(self, request, pk=None):
        """Mark device as trusted"""
        device = self.get_object()
        device.trust_level = 'trusted'
        device.trust_score = 100
        device.save()

        return Response(DeviceFingerprintSerializer(device).data)

    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        """Block a device"""
        device = self.get_object()
        device.trust_level = 'blocked'
        device.trust_score = 0
        device.save()

        # Terminate active sessions
        SecuritySession.objects.filter(
            device=device,
            status='active'
        ).update(
            status='terminated',
            terminated_at=timezone.now(),
            termination_reason='Device blocked'
        )

        return Response(DeviceFingerprintSerializer(device).data)


class SecuritySessionViewSet(viewsets.ReadOnlyModelViewSet):
    """View and manage security sessions"""
    serializer_class = SecuritySessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SecuritySession.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """Terminate a session"""
        session = self.get_object()
        session.status = 'terminated'
        session.terminated_at = timezone.now()
        session.termination_reason = request.data.get('reason', 'User terminated')
        session.save()

        return Response({"message": "Session terminated"})

    @action(detail=False, methods=['post'])
    def terminate_all(self, request):
        """Terminate all sessions except current"""
        current_session = request.data.get('current_session_id')

        terminated = SecuritySession.objects.filter(
            user=request.user,
            status='active'
        ).exclude(id=current_session).update(
            status='terminated',
            terminated_at=timezone.now(),
            termination_reason='User terminated all sessions'
        )

        return Response({"terminated_count": terminated})


class SecurityAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """View security audit logs"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = SecurityAuditLog.objects.all()

        # Filter by user for non-admins
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        # Filters
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)

        resource_type = self.request.query_params.get('resource_type')
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)

        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)

        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SecurityAuditLogDetailSerializer
        return SecurityAuditLogSerializer

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get audit log summary"""
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)

        logs = self.get_queryset()

        return Response({
            'total_events': logs.count(),
            'by_category': logs.values('category').annotate(count=Count('id')),
            'by_severity': logs.values('severity').annotate(count=Count('id')),
            'recent_critical': SecurityAuditLogSerializer(
                logs.filter(severity='critical').order_by('-timestamp')[:10],
                many=True
            ).data,
            'events_last_7_days': logs.filter(timestamp__date__gte=week_ago).count()
        })


class AccessPolicyViewSet(viewsets.ModelViewSet):
    """Manage access policies"""
    serializer_class = AccessPolicySerializer
    permission_classes = [IsAdminUser]
    queryset = AccessPolicy.objects.all()

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test a policy against a user"""
        policy = self.get_object()
        user_id = request.data.get('user_id')
        context = request.data.get('context', {})

        # Evaluate policy
        result = SecurityService.evaluate_policy(policy, user_id, context)

        return Response(result)


class ThreatIndicatorViewSet(viewsets.ModelViewSet):
    """Manage threat indicators"""
    serializer_class = ThreatIndicatorSerializer
    permission_classes = [IsAdminUser]
    queryset = ThreatIndicator.objects.all()

    @action(detail=False, methods=['post'])
    def check(self, request):
        """Check if a value matches any threat indicators"""
        indicator_type = request.data.get('type')
        value = request.data.get('value')

        match = ThreatIndicator.objects.filter(
            indicator_type=indicator_type,
            value=value,
            is_active=True
        ).first()

        if match:
            match.hit_count += 1
            match.last_hit = timezone.now()
            match.save()

            return Response({
                'match': True,
                'indicator': ThreatIndicatorSerializer(match).data
            })

        return Response({'match': False})


class SecurityIncidentViewSet(viewsets.ModelViewSet):
    """Manage security incidents"""
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = SecurityIncident.objects.all()

        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)

        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SecurityIncidentDetailSerializer
        return SecurityIncidentSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign incident to user"""
        incident = self.get_object()
        user_id = request.data.get('user_id')

        incident.assigned_to_id = user_id
        incident.save()

        return Response(SecurityIncidentSerializer(incident).data)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update incident status"""
        incident = self.get_object()
        new_status = request.data.get('status')

        incident.status = new_status

        if new_status == 'contained':
            incident.contained_at = timezone.now()
        elif new_status == 'resolved':
            incident.resolved_at = timezone.now()

        incident.save()

        return Response(SecurityIncidentSerializer(incident).data)


class DataClassificationViewSet(viewsets.ModelViewSet):
    """Manage data classifications"""
    serializer_class = DataClassificationSerializer
    permission_classes = [IsAdminUser]
    queryset = DataClassification.objects.all()


class SecurityDashboardView(APIView):
    """Security dashboard overview"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = timezone.now().date()

        sessions = SecuritySession.objects.all()
        devices = DeviceFingerprint.objects.all()
        incidents = SecurityIncident.objects.all()
        logs = SecurityAuditLog.objects.filter(timestamp__date=today)

        return Response({
            'active_sessions': sessions.filter(status='active').count(),
            'suspicious_sessions': sessions.filter(status='suspicious').count(),
            'trusted_devices': devices.filter(trust_level='trusted').count(),
            'blocked_devices': devices.filter(trust_level='blocked').count(),
            'open_incidents': incidents.exclude(status__in=['resolved', 'false_positive']).count(),
            'critical_incidents': incidents.filter(severity='critical', status='new').count(),
            'recent_threats': ThreatIndicatorSerializer(
                ThreatIndicator.objects.filter(is_active=True).order_by('-created_at')[:5],
                many=True
            ).data,
            'login_attempts_today': logs.filter(action='login').count(),
            'failed_logins_today': logs.filter(action='login', success=False).count(),
            'incidents_by_status': incidents.values('status').annotate(count=Count('id')),
            'incidents_by_severity': incidents.values('severity').annotate(count=Count('id'))
        })


class RiskAssessmentView(APIView):
    """Assess security risk for current session"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        risk_factors = []
        risk_score = 0
        recommendations = []

        # Check device trust
        device_fingerprint = request.headers.get('X-Device-Fingerprint')
        if device_fingerprint:
            device = DeviceFingerprint.objects.filter(
                fingerprint_hash=device_fingerprint,
                user=request.user
            ).first()

            if not device:
                risk_factors.append("Unknown device")
                risk_score += 20
                recommendations.append("Register this device for better security")
            elif device.trust_level == 'unknown':
                risk_factors.append("Unverified device")
                risk_score += 10
                recommendations.append("Verify this device using MFA")
            elif device.trust_level == 'suspicious':
                risk_factors.append("Suspicious device")
                risk_score += 40
        else:
            risk_factors.append("No device fingerprint")
            risk_score += 15

        # Check for MFA
        if not request.user.mfa_enabled if hasattr(request.user, 'mfa_enabled') else True:
            risk_factors.append("MFA not enabled")
            risk_score += 25
            recommendations.append("Enable Multi-Factor Authentication")

        # Determine risk level
        if risk_score >= 60:
            overall_risk = 'high'
        elif risk_score >= 30:
            overall_risk = 'medium'
        else:
            overall_risk = 'low'

        return Response({
            'overall_risk': overall_risk,
            'risk_score': risk_score,
            'factors': risk_factors,
            'recommendations': recommendations
        })
