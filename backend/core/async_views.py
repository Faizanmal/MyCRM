"""
DRF Viewsets for Async Job Management, Idempotency, and Poison Pill Quarantine
"""

import logging
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.async_models import PoisonPillQuarantine, TaskExecutionRecord
from core.async_serializers import (
    PoisonPillQuarantineSerializer,
    TaskExecutionRecordSerializer,
)

logger = logging.getLogger(__name__)


class IsAdminOrSecurityOfficer(permissions.BasePermission):
    """Allow access only to org admins, system admins, or security officers"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Check organization role if present on request
        member = getattr(request, 'membership', None)
        if member and member.role in ('admin', 'owner', 'security_officer'):
            return True

        # Check user model role
        user_role = getattr(request.user, 'role', '')
        if user_role in ('admin', 'system_admin', 'security_officer'):
            return True

        # Direct database verification for organization membership role
        from multi_tenant.models import OrganizationMember
        return OrganizationMember.objects.filter(
            user=request.user,
            role__in=('admin', 'owner', 'security_officer'),
            is_active=True
        ).exists()


class PoisonPillQuarantineViewSet(viewsets.ModelViewSet):
    """
    ViewSet for inspecting and managing quarantined background jobs.
    Allows administrators and security officers to investigate payload errors,
    discard poison records, or replay corrected tasks.
    """
    queryset = PoisonPillQuarantine.objects.all().order_by('-quarantined_at')
    serializer_class = PoisonPillQuarantineSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSecurityOfficer]
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs

        # Scope by organization if attached to request
        org = getattr(self.request, 'organization', None)
        if org:
            return qs.filter(tenant=org)

        # Fallback to user memberships
        from multi_tenant.models import OrganizationMember
        org_ids = OrganizationMember.objects.filter(
            user=user,
            is_active=True
        ).values_list('organization_id', flat=True)
        return qs.filter(tenant_id__in=org_ids)

    @action(detail=True, methods=['post'])
    def replay(self, request, pk=None):
        """Mark quarantined job as replayed and optionally re-trigger background processing"""
        quarantine = self.get_object()
        if quarantine.status == 'replayed':
            return Response(
                {'error': 'Task has already been replayed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        quarantine.status = 'replayed'
        quarantine.resolved_at = timezone.now()
        notes = request.data.get('notes', f'Replayed by user {request.user.id}')
        quarantine.resolution_notes = notes
        quarantine.save(update_fields=['status', 'resolved_at', 'resolution_notes'])

        logger.info(
            "AUDIT: Quarantined task %s (ID: %s) replayed by user %s",
            quarantine.task_name,
            quarantine.id,
            request.user.id
        )

        return Response({
            'status': 'replayed',
            'quarantine_id': str(quarantine.id),
            'resolved_at': quarantine.resolved_at.isoformat(),
        })

    @action(detail=True, methods=['post'])
    def discard(self, request, pk=None):
        """Dismiss quarantined job as unfixable or invalid"""
        quarantine = self.get_object()
        quarantine.status = 'discarded'
        quarantine.resolved_at = timezone.now()
        notes = request.data.get('notes', f'Discarded by user {request.user.id}')
        quarantine.resolution_notes = notes
        quarantine.save(update_fields=['status', 'resolved_at', 'resolution_notes'])

        logger.info(
            "AUDIT: Quarantined task %s (ID: %s) discarded by user %s",
            quarantine.task_name,
            quarantine.id,
            request.user.id
        )

        return Response({
            'status': 'discarded',
            'quarantine_id': str(quarantine.id),
            'resolved_at': quarantine.resolved_at.isoformat(),
        })


class TaskExecutionRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for inspecting task execution idempotency records.
    """
    queryset = TaskExecutionRecord.objects.all().order_by('-created_at')
    serializer_class = TaskExecutionRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSecurityOfficer]
