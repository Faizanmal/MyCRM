from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    ConsentType,
    DataAccessLog,
    DataBreachIncident,
    DataDeletionRequest,
    DataExportRequest,
    DataProcessingActivity,
    LegalHold,
    PrivacyNotice,
    UserConsent,
    UserPrivacyPreference,
)
from .serializers import (
    ConsentTypeSerializer,
    DataAccessLogSerializer,
    DataBreachIncidentListSerializer,
    DataBreachIncidentSerializer,
    DataDeletionRequestSerializer,
    DataExportRequestSerializer,
    DataProcessingActivitySerializer,
    LegalHoldSerializer,
    PrivacyNoticeSerializer,
    UserConsentListSerializer,
    UserConsentSerializer,
    UserPrivacyPreferenceSerializer,
)
from .services import (
    execute_gdpr_deletion,
    generate_dsar_export,
    verify_dsar_checksum,
)


class ConsentTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing consent types."""
    permission_classes = [IsAuthenticated]
    serializer_class = ConsentTypeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_required', 'is_active', 'legal_basis']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'category']
    ordering = ['category', 'name']

    def get_queryset(self):
        return ConsentType.objects.all()


class UserConsentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user consents."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'consent_type', 'is_granted']
    ordering_fields = ['consent_date', 'withdrawn_at']
    ordering = ['-consent_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return UserConsentListSerializer
        return UserConsentSerializer

    def get_queryset(self):
        queryset = UserConsent.objects.all()

        # Users can only see their own consents unless they're staff
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        # Filter active consents
        if self.request.query_params.get('active_only') == 'true':
            queryset = queryset.filter(is_granted=True, withdrawn_at__isnull=True)

        return queryset.select_related('user', 'consent_type')

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

    @action(detail=True, methods=['post'])
    def withdraw(self, request, _pk=None):
        """Withdraw consent."""
        consent = self.get_object()

        if consent.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only withdraw your own consents'},
                status=status.HTTP_403_FORBIDDEN
            )

        if consent.withdrawn_at:
            return Response(
                {'error': 'Consent already withdrawn'},
                status=status.HTTP_400_BAD_REQUEST
            )

        consent.withdrawn_at = timezone.now()
        consent.withdrawal_reason = request.data.get('reason', '')
        consent.save(update_fields=['withdrawn_at', 'withdrawal_reason'])

        return Response(UserConsentSerializer(consent).data)

    @action(detail=False, methods=['get'])
    def my_consents(self, request):
        """Get current user's consents."""
        consents = UserConsent.objects.filter(user=request.user).select_related('consent_type')
        serializer = UserConsentSerializer(consents, many=True)
        return Response(serializer.data)


class DataExportRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for managing data export requests with cryptographic integrity verification."""
    permission_classes = [IsAuthenticated]
    serializer_class = DataExportRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'request_type', 'format']
    ordering_fields = ['requested_at', 'completed_at']
    ordering = ['-requested_at']

    def _get_organization(self):
        org = getattr(self.request, 'organization', None)
        if not org:
            from multi_tenant.middleware import get_current_organization
            org = get_current_organization()
        if not org and self.request.user and self.request.user.is_authenticated:
            from multi_tenant.models import OrganizationMember
            member = OrganizationMember.objects.filter(user=self.request.user, is_active=True).first()
            if member:
                org = member.organization
        return org

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return DataExportRequest.objects.none()

        org = self._get_organization()
        if not org:
            return DataExportRequest.objects.none()

        queryset = DataExportRequest.objects.filter(organization=org)
        if not user.is_staff:
            queryset = queryset.filter(user=user)

        return queryset.select_related('user')

    def perform_create(self, serializer):
        org = self._get_organization()
        if not org:
            raise serializers.ValidationError('Organization context required for data export.')

        pending_count = DataExportRequest.objects.filter(
            organization=org,
            user=self.request.user,
            status__in=['pending', 'processing']
        ).count()

        if pending_count > 0:
            raise serializers.ValidationError(
                'You already have a pending export request. Please wait for it to complete.'
            )

        export_request = serializer.save(user=self.request.user, organization=org)
        generate_dsar_export(self.request.user, org, export_request)

    @action(detail=True, methods=['post', 'get'])
    def process_export(self, request, pk=None):
        """Generate DSAR export bundle immediately with SHA-256 integrity checksum."""
        export_request = self.get_object()
        bundle = generate_dsar_export(export_request.user, export_request.organization, export_request)
        return Response({
            'status': 'completed',
            'export_id': str(export_request.id),
            'checksum': export_request.checksum,
            'record_counts': bundle.get('record_counts', {}),
            'export_payload': bundle,
        })

    @action(detail=True, methods=['get'])
    def verify(self, request, pk=None):
        """Cryptographically verify the integrity checksum of the DSAR export bundle."""
        export_request = self.get_object()
        if not export_request.export_payload:
            return Response({'error': 'Export has not been generated yet'}, status=status.HTTP_400_BAD_REQUEST)

        is_valid, msg = verify_dsar_checksum(export_request.export_payload)
        return Response({
            'export_id': str(export_request.id),
            'checksum': export_request.checksum,
            'is_valid': is_valid,
            'message': msg,
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an export request."""
        export_request = self.get_object()

        if export_request.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only cancel your own requests'},
                status=status.HTTP_403_FORBIDDEN
            )

        if export_request.status not in ['pending', 'processing']:
            return Response(
                {'error': 'Can only cancel pending or processing requests'},
                status=status.HTTP_400_BAD_REQUEST
            )

        export_request.status = 'cancelled'
        export_request.save(update_fields=['status'])

        return Response(DataExportRequestSerializer(export_request).data)

    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get current user's export requests."""
        queryset = self.get_queryset().filter(user=request.user)
        serializer = DataExportRequestSerializer(queryset, many=True)
        return Response(serializer.data)


class DataDeletionRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for managing data deletion requests with legal hold exceptions."""
    permission_classes = [IsAuthenticated]
    serializer_class = DataDeletionRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'deletion_type']
    ordering_fields = ['requested_at', 'reviewed_at', 'completed_at']
    ordering = ['-requested_at']

    def _get_organization(self):
        org = getattr(self.request, 'organization', None)
        if not org:
            from multi_tenant.middleware import get_current_organization
            org = get_current_organization()
        if not org and self.request.user and self.request.user.is_authenticated:
            from multi_tenant.models import OrganizationMember
            member = OrganizationMember.objects.filter(user=self.request.user, is_active=True).first()
            if member:
                org = member.organization
        return org

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return DataDeletionRequest.objects.none()

        org = self._get_organization()
        if not org:
            return DataDeletionRequest.objects.none()

        queryset = DataDeletionRequest.objects.filter(organization=org)
        if not user.is_staff:
            queryset = queryset.filter(user=user)

        if self.request.query_params.get('pending_review') == 'true' and user.is_staff:
            queryset = queryset.filter(status='pending')

        return queryset.select_related('user', 'reviewed_by')

    def perform_create(self, serializer):
        org = self._get_organization()
        if not org:
            raise serializers.ValidationError('Organization context required for data deletion.')

        pending_count = DataDeletionRequest.objects.filter(
            organization=org,
            user=self.request.user,
            status__in=['pending', 'approved', 'processing']
        ).count()

        if pending_count > 0:
            raise serializers.ValidationError(
                'You already have a pending deletion request.'
            )

        serializer.save(user=self.request.user, organization=org)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve and execute a deletion request with legal hold retention exceptions."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff can approve deletion requests'},
                status=status.HTTP_403_FORBIDDEN
            )

        deletion_request = self.get_object()
        if deletion_request.status != 'pending':
            return Response(
                {'error': 'Can only approve pending requests'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = execute_gdpr_deletion(deletion_request, reviewer_user=request.user)
        return Response({
            'request': DataDeletionRequestSerializer(deletion_request).data,
            'execution_result': result,
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a deletion request (staff only)."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff can reject deletion requests'},
                status=status.HTTP_403_FORBIDDEN
            )

        deletion_request = self.get_object()
        if deletion_request.status != 'pending':
            return Response(
                {'error': 'Can only reject pending requests'},
                status=status.HTTP_400_BAD_REQUEST
            )

        deletion_request.status = 'rejected'
        deletion_request.reviewed_at = timezone.now()
        deletion_request.reviewed_by = request.user
        deletion_request.rejection_reason = request.data.get('reason', '')
        deletion_request.save(update_fields=['status', 'reviewed_at', 'reviewed_by', 'rejection_reason'])

        return Response(DataDeletionRequestSerializer(deletion_request).data)


class LegalHoldViewSet(viewsets.ModelViewSet):
    """
    Manage Legal Holds and statutory retention exceptions for GDPR compliance.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LegalHoldSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'hold_type']
    search_fields = ['subject_identifier', 'reason']
    ordering_fields = ['created_at', 'released_at']
    ordering = ['-created_at']

    def _get_organization(self):
        org = getattr(self.request, 'organization', None)
        if not org:
            from multi_tenant.middleware import get_current_organization
            org = get_current_organization()
        if not org and self.request.user and self.request.user.is_authenticated:
            from multi_tenant.models import OrganizationMember
            member = OrganizationMember.objects.filter(user=self.request.user, is_active=True).first()
            if member:
                org = member.organization
        return org

    def get_queryset(self):
        org = self._get_organization()
        if not org:
            return LegalHold.objects.none()
        return LegalHold.objects.filter(organization=org).select_related('created_by', 'released_by')

    def perform_create(self, serializer):
        org = self._get_organization()
        if not org:
            raise serializers.ValidationError('Organization context required for legal hold.')
        serializer.save(organization=org, created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        """Release an active legal hold."""
        hold = self.get_object()
        if not hold.is_active:
            return Response({'error': 'Legal hold is already released'}, status=status.HTTP_400_BAD_REQUEST)

        reason = request.data.get('reason', '')
        hold.release(released_by=request.user, reason=reason)
        return Response(LegalHoldSerializer(hold).data)


class DataProcessingActivityViewSet(viewsets.ModelViewSet):
    """ViewSet for managing data processing activities (Article 30 records)."""
    permission_classes = [IsAuthenticated]
    serializer_class = DataProcessingActivitySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['legal_basis', 'is_active', 'third_country_transfers']
    search_fields = ['name', 'description', 'purpose']
    ordering_fields = ['name', 'created_at', 'last_reviewed']
    ordering = ['name']

    def get_queryset(self):
        return DataProcessingActivity.objects.all()


class DataBreachIncidentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing data breach incidents."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['severity', 'status', 'breach_type', 'authority_notified', 'users_notified']
    search_fields = ['incident_id', 'title', 'description']
    ordering_fields = ['discovered_at', 'reported_at', 'severity']
    ordering = ['-discovered_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return DataBreachIncidentListSerializer
        return DataBreachIncidentSerializer

    def get_queryset(self):
        queryset = DataBreachIncident.objects.all()

        # Check if notification is overdue (72 hours)
        if self.request.query_params.get('notification_overdue') == 'true':
            threshold = timezone.now() - timedelta(hours=72)
            queryset = queryset.filter(
                discovered_at__lt=threshold,
                authority_notified=False,
                notification_required=True
            )

        return queryset.select_related('reported_by')

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)

    @action(detail=True, methods=['post'])
    def notify_authority(self, request, _pk=None):
        """Mark breach as notified to authorities."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff can mark authority notifications'},
                status=status.HTTP_403_FORBIDDEN
            )

        incident = self.get_object()
        incident.authority_notified = True
        incident.authority_notification_date = timezone.now()
        incident.save(update_fields=['authority_notified', 'authority_notification_date'])

        return Response(DataBreachIncidentSerializer(incident).data)

    @action(detail=True, methods=['post'])
    def notify_users(self, request, _pk=None):
        """Mark breach as notified to affected users."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff can mark user notifications'},
                status=status.HTTP_403_FORBIDDEN
            )

        incident = self.get_object()
        incident.users_notified = True
        incident.user_notification_date = timezone.now()
        incident.save(update_fields=['users_notified', 'user_notification_date'])

        # Trigger notification emails
        # from .tasks import send_breach_notifications
        # send_breach_notifications.delay(incident.id)

        return Response(DataBreachIncidentSerializer(incident).data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get breach statistics."""
        total = DataBreachIncident.objects.count()
        by_severity = DataBreachIncident.objects.values('severity').annotate(count=Count('id'))
        by_status = DataBreachIncident.objects.values('status').annotate(count=Count('id'))

        # Overdue notifications
        threshold = timezone.now() - timedelta(hours=72)
        overdue = DataBreachIncident.objects.filter(
            discovered_at__lt=threshold,
            authority_notified=False,
            notification_required=True
        ).count()

        return Response({
            'total_incidents': total,
            'by_severity': list(by_severity),
            'by_status': list(by_status),
            'overdue_notifications': overdue
        })


class DataAccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing data access logs (read-only)."""
    permission_classes = [IsAuthenticated]
    serializer_class = DataAccessLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'accessed_by', 'access_type', 'content_type']
    ordering_fields = ['accessed_at']
    ordering = ['-accessed_at']

    def get_queryset(self):
        queryset = DataAccessLog.objects.all()

        # Users can only see logs of their own data unless they're staff
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        return queryset.select_related('user', 'accessed_by', 'content_type')

    @action(detail=False, methods=['get'])
    def my_data_access(self, request):
        """Get access logs for current user's data."""
        logs = DataAccessLog.objects.filter(user=request.user).select_related('accessed_by')
        serializer = DataAccessLogSerializer(logs, many=True)
        return Response(serializer.data)


class PrivacyNoticeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing privacy notices."""
    permission_classes = [IsAuthenticated]
    serializer_class = PrivacyNoticeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['notice_type', 'is_current', 'language']
    search_fields = ['title', 'content']
    ordering_fields = ['effective_date', 'version', 'created_at']
    ordering = ['-effective_date']

    def get_queryset(self):
        return PrivacyNotice.objects.all().select_related('created_by')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current active privacy notices."""
        notices = PrivacyNotice.objects.filter(is_current=True)
        serializer = PrivacyNoticeSerializer(notices, many=True)
        return Response(serializer.data)


class UserPrivacyPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user privacy preferences."""
    permission_classes = [IsAuthenticated]
    serializer_class = UserPrivacyPreferenceSerializer

    def get_queryset(self):
        queryset = UserPrivacyPreference.objects.all()

        # Users can only see their own preferences unless they're staff
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        return queryset.select_related('user').prefetch_related('accepted_privacy_notices')

    @action(detail=False, methods=['get', 'put', 'patch'])
    def my_preferences(self, request):
        """Get or update current user's privacy preferences."""
        preferences, created = UserPrivacyPreference.objects.get_or_create(
            user=request.user
        )

        if request.method == 'GET':
            serializer = UserPrivacyPreferenceSerializer(preferences)
            return Response(serializer.data)
        else:
            serializer = UserPrivacyPreferenceSerializer(
                preferences,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def accept_notice(self, request, _pk=None):
        """Accept a privacy notice."""
        preferences = self.get_object()

        if preferences.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only update your own preferences'},
                status=status.HTTP_403_FORBIDDEN
            )

        notice_id = request.data.get('notice_id')
        if not notice_id:
            return Response(
                {'error': 'notice_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            notice = PrivacyNotice.objects.get(id=notice_id)
            preferences.accepted_privacy_notices.add(notice)
            return Response(UserPrivacyPreferenceSerializer(preferences).data)
        except PrivacyNotice.DoesNotExist:
            return Response(
                {'error': 'Privacy notice not found'},
                status=status.HTTP_404_NOT_FOUND
            )
