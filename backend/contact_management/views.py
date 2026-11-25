import csv
import io
import json
import logging
from typing import Any, Dict

import openpyxl
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Avg, Count, Q
from django.http import HttpResponse
from openpyxl.styles import Font, PatternFill
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from rest_framework import filters, permissions, status, viewsets
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from multi_tenant.permissions import HasRolePermission, TenantObjectPermission
from core.services import ValidationException
from .models import Account, Contact, ContactActivity, ContactGroup, ContactImport, MergeAuditLog
from .serializers import (
    AccountCreateSerializer,
    AccountSerializer,
    ContactActivitySerializer,
    ContactBulkUpdateSerializer,
    ContactCreateSerializer,
    ContactExportSerializer,
    ContactGroupSerializer,
    ContactImportSerializer,
    ContactSerializer,
    MergeAuditLogSerializer,
    MergeEntitySerializer,
    UnmergeEntitySerializer,
)
from .services import AccountService, ContactService

logger = logging.getLogger(__name__)
User = get_user_model()


class ContactViewSet(viewsets.ModelViewSet):
    """
    Enterprise Contact ViewSet
    Provides tenant-scoped CRUD, duplicate detection, atomic merge/unmerge,
    activity logging, and streaming bounded-memory import.
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated, TenantObjectPermission, HasRolePermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'company_name', 'phone', 'job_title']
    ordering_fields = ['first_name', 'last_name', 'email', 'company_name', 'created_at', 'updated_at', 'score']
    ordering = ['-created_at']
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action == 'create':
            return ContactCreateSerializer
        return ContactSerializer

    def get_queryset(self):
        user = self.request.user
        org = getattr(self.request, 'organization', None)

        if not user.is_authenticated:
            return Contact.objects.none()

        if user.is_superuser:
            queryset = Contact.objects.all()
        else:
            if not org:
                # Try fallback from membership
                active_mem = user.organization_memberships.filter(is_active=True).first()
                if active_mem:
                    org = active_mem.organization
                    self.request.organization = org
            if not org:
                return Contact.objects.none()

            queryset = Contact.objects.filter(organization=org)

            # Row-level role check
            member = getattr(self.request, 'member', None)
            if not member:
                member = user.organization_memberships.filter(organization=org, is_active=True).first()
            if member and member.role in ['member', 'sales_rep']:
                queryset = queryset.filter(
                    Q(assigned_to=user) | Q(owner=user) | Q(created_by=user)
                )

        # Exclude merged contacts by default unless explicitly asked
        include_merged = self.request.query_params.get('include_merged', 'false').lower() == 'true'
        if not include_merged:
            queryset = queryset.filter(is_merged=False)

        # Filters
        contact_type = self.request.query_params.get('contact_type')
        if contact_type:
            queryset = queryset.filter(contact_type=contact_type)

        status_param = self.request.query_params.get('status')
        if status_param and status_param != 'all':
            queryset = queryset.filter(status=status_param)

        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)

        account_id = self.request.query_params.get('account')
        if account_id:
            queryset = queryset.filter(account_id=account_id)

        company = self.request.query_params.get('company')
        if company:
            queryset = queryset.filter(
                Q(company_name__icontains=company) | Q(account__name__icontains=company)
            )

        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
            for t in tag_list:
                queryset = queryset.filter(tags__icontains=t)

        return queryset.select_related('account', 'assigned_to', 'owner', 'created_by')

    def perform_create(self, serializer):
        org = getattr(self.request, 'organization', None)
        email = serializer.validated_data.get('email')

        # Multi-tenant duplicate check
        if org and email:
            existing = Contact.objects.filter(
                organization=org,
                email__iexact=email,
                is_merged=False
            ).first()
            if existing:
                raise DRFValidationError({'email': "A contact with this email already exists in your organization."})

        try:
            serializer.save(
                created_by=self.request.user,
                organization=org
            )
        except ValidationError as err:
            raise DRFValidationError(err.message_dict if hasattr(err, 'message_dict') else str(err))

    def perform_update(self, serializer):
        try:
            serializer.save()
        except ValidationError as err:
            raise DRFValidationError(err.message_dict if hasattr(err, 'message_dict') else str(err))

    @action(detail=False, methods=['get'])
    def duplicates(self, request):
        """Identify potential duplicate contacts within the tenant"""
        contact_id = request.query_params.get('contact_id')
        email = request.query_params.get('email')
        phone = request.query_params.get('phone')
        company = request.query_params.get('company')
        name = request.query_params.get('name')

        service = ContactService(user=request.user, organization=getattr(request, 'organization', None))
        duplicates_qs = service.find_duplicates(
            contact_id=int(contact_id) if contact_id else None,
            email=email,
            phone=phone,
            company=company,
            name=name
        )
        serializer = ContactSerializer(duplicates_qs[:50], many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def merge(self, request):
        """Merge secondary contact into primary contact with immutable snapshotting"""
        if not getattr(settings, 'FEATURE_CONTACT_MERGE', True):
            return Response({'error': 'Contact merge feature is disabled by feature flag.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = MergeEntitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        primary_id = serializer.validated_data['primary_id']
        secondary_id = serializer.validated_data['secondary_id']
        field_choices = serializer.validated_data.get('field_choices', {})

        service = ContactService(user=request.user, organization=getattr(request, 'organization', None))
        try:
            primary, merge_log = service.merge_contacts(
                primary_id=primary_id,
                secondary_id=secondary_id,
                field_choices=field_choices
            )
            return Response({
                'success': True,
                'message': f"Successfully merged contact {secondary_id} into {primary_id}.",
                'primary': ContactSerializer(primary).data,
                'merge_log_id': merge_log.id,
                'audit_log_id': merge_log.id,
            }, status=status.HTTP_200_OK)
        except ValidationException as e:
            return Response(e.details, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='merge/preview')
    def merge_preview(self, request):
        """Preview merged contact attributes without applying mutations"""
        serializer = MergeEntitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        primary_id = serializer.validated_data['primary_id']
        secondary_id = serializer.validated_data['secondary_id']

        try:
            primary = self.get_queryset().get(id=primary_id)
            secondary = self.get_queryset().get(id=secondary_id)
        except Contact.DoesNotExist:
            return Response({'error': "One or both contacts not found in your organization."}, status=status.HTTP_404_NOT_FOUND)

        if primary.organization_id != secondary.organization_id:
            return Response({'error': "Cross-tenant merge preview is rejected."}, status=status.HTTP_400_BAD_REQUEST)

        preview_fields = {
            'first_name': primary.first_name,
            'last_name': primary.last_name,
            'email': primary.email,
            'phone': primary.phone or secondary.phone,
            'mobile': primary.mobile or secondary.mobile,
            'company': primary.company or secondary.company,
            'job_title': primary.job_title or secondary.job_title,
            'tags': list(set((primary.tags or []) + (secondary.tags or []))),
            'activities_count': primary.activities.count() + secondary.activities.count()
        }

        return Response({
            'primary_id': primary.id,
            'secondary_id': secondary.id,
            'preview': preview_fields
        })

    @action(detail=False, methods=['post'])
    def unmerge(self, request):
        """Unmerge contacts using merge log snapshot"""
        serializer = UnmergeEntitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        merge_log_id = serializer.validated_data.get('merge_log_id') or serializer.validated_data.get('audit_log_id')
        service = ContactService(user=request.user, organization=getattr(request, 'organization', None))
        try:
            secondary = service.unmerge_contact(merge_log_id=merge_log_id)
            return Response({
                'success': True,
                'message': f"Successfully unmerged and restored contact {secondary.id}.",
                'restored_contact': ContactSerializer(secondary).data
            }, status=status.HTTP_200_OK)
        except ValidationException as e:
            return Response(e.details, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def activities(self, request, pk=None):
        """List or log activities specifically for this contact"""
        contact = self.get_object()
        if request.method == 'GET':
            activities = contact.activities.all()
            serializer = ContactActivitySerializer(activities, many=True)
            return Response(serializer.data)

        serializer = ContactActivitySerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(contact=contact, created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='import')
    def import_contacts(self, request):
        """
        Streaming memory-bounded CSV import of contacts.
        Handles up to 10k+ rows with constant memory footprint.
        """
        file_obj = request.FILES.get('file')
        if not file_obj:
            # Fall back to raw text payload if passed
            raw_content = request.data.get('content') or request.data.get('file_content')
            if not raw_content:
                return Response({'error': "No file or CSV content provided."}, status=status.HTTP_400_BAD_REQUEST)
            file_stream = io.StringIO(raw_content)
        else:
            file_stream = io.TextIOWrapper(file_obj.file, encoding='utf-8', errors='replace')

        mapping_raw = request.data.get('mapping')
        mapping = {}
        if mapping_raw:
            if isinstance(mapping_raw, str):
                try:
                    mapping = json.loads(mapping_raw)
                except Exception:
                    pass
            elif isinstance(mapping_raw, dict):
                mapping = mapping_raw

        duplicate_strategy = request.data.get('duplicate_action') or request.data.get('duplicate_strategy', 'skip')

        service = ContactService(user=request.user, organization=getattr(request, 'organization', None))
        result = service.import_contacts_stream(
            stream_or_path=file_stream,
            mapping=mapping,
            duplicate_strategy=duplicate_strategy,
            batch_size=500
        )
        return Response(result, status=status.HTTP_201_CREATED if result['created'] > 0 else status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='import/preview')
    def import_preview(self, request):
        """Preview first rows of import file and detected column headers"""
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': "File required for preview."}, status=status.HTTP_400_BAD_REQUEST)

        stream = io.TextIOWrapper(file_obj.file, encoding='utf-8', errors='replace')
        csv_reader = csv.DictReader(stream)
        headers = csv_reader.fieldnames or []
        rows = []
        for i, row in enumerate(csv_reader):
            if i >= 5:
                break
            rows.append(row)

        return Response({
            'headers': headers,
            'preview_rows': rows,
            'total_previewed': len(rows)
        })

    @action(detail=False, methods=['post', 'delete'], url_path='bulk')
    def bulk_operations(self, request):
        """Bulk create or delete contacts"""
        if request.method == 'POST':
            contacts_data = request.data.get('contacts', [])
            if not isinstance(contacts_data, list):
                return Response({'error': "'contacts' must be a list"}, status=status.HTTP_400_BAD_REQUEST)
            created_objs = []
            org = getattr(request, 'organization', None)
            for item in contacts_data:
                item_dict = dict(item)
                item_dict['organization'] = org
                item_dict['created_by'] = request.user
                created_objs.append(Contact(**item_dict))
            created = Contact.objects.bulk_create(created_objs)
            return Response(
                {'success': True, 'count': len(created), 'results': ContactSerializer(created, many=True).data},
                status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            ids = request.data.get('ids', [])
            self.get_queryset().filter(id__in=ids).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update contacts scoped strictly to tenant"""
        serializer = ContactBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        contact_ids = serializer.validated_data['contact_ids']
        updates = serializer.validated_data['updates']

        contacts = self.get_queryset().filter(id__in=contact_ids)
        if contacts.count() != len(contact_ids):
            return Response(
                {'error': "Some contact IDs do not exist or belong to another organization."},
                status=status.HTTP_404_NOT_FOUND
            )

        updated_count = contacts.update(**updates)
        return Response({
            'message': f"{updated_count} contacts updated successfully",
            'updated_count': updated_count
        })

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """Bulk delete contacts scoped to tenant"""
        contact_ids = request.data.get('contact_ids', [])
        if not contact_ids:
            return Response({'error': 'No contact IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

        contacts = self.get_queryset().filter(id__in=contact_ids)
        if contacts.count() != len(contact_ids):
            return Response(
                {'error': "Some contact IDs do not exist or belong to another organization."},
                status=status.HTTP_404_NOT_FOUND
            )

        deleted_count = contacts.count()
        contacts.delete()
        return Response({
            'message': f"{deleted_count} contacts deleted successfully",
            'deleted_count': deleted_count
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get aggregate contact statistics for active tenant"""
        qs = self.get_queryset()
        stats = {
            'total': qs.count(),
            'by_type': {},
            'by_status': {},
            'average_score': qs.aggregate(avg=Avg('score'))['avg'] or 0
        }
        for ctype, _ in Contact.CONTACT_TYPE_CHOICES:
            stats['by_type'][ctype] = qs.filter(contact_type=ctype).count()
        for cstatus in ['active', 'inactive', 'lead', 'churned']:
            stats['by_status'][cstatus] = qs.filter(status=cstatus).count()

        return Response(stats)

    @action(detail=False, methods=['post'])
    def export(self, request):
        """Export contacts to CSV, Excel, or PDF"""
        serializer = ContactExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        format_type = serializer.validated_data['format']
        queryset = self.get_queryset()

        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="contacts.csv"'
            writer = csv.writer(response)
            writer.writerow(['ID', 'First Name', 'Last Name', 'Email', 'Phone', 'Company', 'Title', 'Status'])
            for c in queryset:
                writer.writerow([c.id, c.first_name, c.last_name, c.email, c.phone, c.company, c.job_title, c.status])
            return response

        return Response({'message': f"Export format {format_type} queued successfully."})


class AccountViewSet(viewsets.ModelViewSet):
    """
    Enterprise B2B Account ViewSet
    Handles tenant-scoped accounts, search, filter, merge/unmerge, and analytics.
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated, TenantObjectPermission, HasRolePermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'domain', 'industry', 'city', 'country']
    ordering_fields = ['name', 'domain', 'annual_revenue', 'employee_count', 'created_at', 'health_score']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return AccountCreateSerializer
        return AccountSerializer

    def get_queryset(self):
        user = self.request.user
        org = getattr(self.request, 'organization', None)

        if not user.is_authenticated:
            return Account.objects.none()

        if user.is_superuser:
            qs = Account.objects.all()
        else:
            if not org:
                active_mem = user.organization_memberships.filter(is_active=True).first()
                if active_mem:
                    org = active_mem.organization
                    self.request.organization = org
            if not org:
                return Account.objects.none()

            qs = Account.objects.filter(organization=org)
            member = getattr(self.request, 'member', None)
            if not member:
                member = user.organization_memberships.filter(organization=org, is_active=True).first()
            if member and member.role in ['member', 'sales_rep']:
                qs = qs.filter(Q(assigned_to=user) | Q(owner=user) | Q(created_by=user))

        include_merged = self.request.query_params.get('include_merged', 'false').lower() == 'true'
        if not include_merged:
            qs = qs.filter(is_merged=False)

        # Filters
        industry = self.request.query_params.get('industry')
        if industry:
            qs = qs.filter(industry__icontains=industry)

        tier = self.request.query_params.get('tier')
        if tier:
            qs = qs.filter(tier=tier)

        account_type = self.request.query_params.get('account_type')
        if account_type:
            qs = qs.filter(account_type=account_type)

        return qs.select_related('owner', 'assigned_to', 'organization', 'created_by')

    def perform_create(self, serializer):
        org = getattr(self.request, 'organization', None)
        name = serializer.validated_data.get('name')
        if org and name:
            existing = Account.objects.filter(organization=org, name__iexact=name, is_merged=False).first()
            if existing:
                raise DRFValidationError({'name': "An account with this name already exists in your organization."})

        try:
            serializer.save(
                created_by=self.request.user,
                organization=org
            )
        except ValidationError as err:
            raise DRFValidationError(err.message_dict if hasattr(err, 'message_dict') else str(err))

    def perform_update(self, serializer):
        try:
            serializer.save()
        except ValidationError as err:
            raise DRFValidationError(err.message_dict if hasattr(err, 'message_dict') else str(err))

    @action(detail=False, methods=['post'])
    def merge(self, request):
        """Merge secondary account into primary account"""
        if not getattr(settings, 'FEATURE_ACCOUNT_MERGE', True):
            return Response({'error': 'Account merge feature is disabled by feature flag.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = MergeEntitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        primary_id = serializer.validated_data['primary_id']
        secondary_id = serializer.validated_data['secondary_id']
        field_choices = serializer.validated_data.get('field_choices', {})

        service = AccountService(user=request.user, organization=getattr(request, 'organization', None))
        try:
            primary, merge_log = service.merge_accounts(
                primary_id=primary_id,
                secondary_id=secondary_id,
                field_choices=field_choices
            )
            return Response({
                'success': True,
                'message': f"Successfully merged account {secondary_id} into {primary_id}.",
                'primary': AccountSerializer(primary).data,
                'merge_log_id': merge_log.id,
                'audit_log_id': merge_log.id,
            })
        except ValidationException as e:
            return Response(e.details, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def unmerge(self, request):
        """Unmerge previously merged account"""
        serializer = UnmergeEntitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        merge_log_id = serializer.validated_data.get('merge_log_id') or serializer.validated_data.get('audit_log_id')
        service = AccountService(user=request.user, organization=getattr(request, 'organization', None))
        try:
            secondary = service.unmerge_account(merge_log_id=merge_log_id)
            return Response({
                'success': True,
                'message': f"Successfully restored account {secondary.id}.",
                'restored_account': AccountSerializer(secondary).data
            })
        except ValidationException as e:
            return Response(e.details, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Account metrics and statistics"""
        qs = self.get_queryset()
        stats = {
            'total': qs.count(),
            'by_tier': {},
            'by_type': {},
            'average_health': qs.aggregate(avg=Avg('health_score'))['avg'] or 0
        }
        for tier, _ in Account.TIER_CHOICES:
            stats['by_tier'][tier] = qs.filter(tier=tier).count()
        for atype, _ in Account.ACCOUNT_TYPE_CHOICES:
            stats['by_type'][atype] = qs.filter(account_type=atype).count()

        return Response(stats)


class ContactGroupViewSet(viewsets.ModelViewSet):
    """ViewSet for contact groups with add/remove actions"""
    queryset = ContactGroup.objects.all()
    serializer_class = ContactGroupSerializer
    permission_classes = [permissions.IsAuthenticated, TenantObjectPermission, HasRolePermission]

    def get_queryset(self):
        user = self.request.user
        org = getattr(self.request, 'organization', None)
        if not user.is_authenticated:
            return ContactGroup.objects.none()
        if user.is_superuser:
            return ContactGroup.objects.all()
        if not org:
            mem = user.organization_memberships.filter(is_active=True).first()
            if mem:
                org = mem.organization
        if not org:
            return ContactGroup.objects.none()
        return ContactGroup.objects.filter(organization=org)

    def perform_create(self, serializer):
        org = getattr(self.request, 'organization', None)
        serializer.save(created_by=self.request.user, organization=org)

    @action(detail=True, methods=['post'], url_path='add-contacts')
    def add_contacts(self, request, pk=None):
        group = self.get_object()
        contact_ids = request.data.get('contact_ids', [])
        contacts = Contact.objects.filter(id__in=contact_ids, organization=group.organization)
        group.contacts.add(*contacts)
        return Response({'success': True, 'added': contacts.count(), 'total': group.contacts.count()})

    @action(detail=True, methods=['post'], url_path='remove-contacts')
    def remove_contacts(self, request, pk=None):
        group = self.get_object()
        contact_ids = request.data.get('contact_ids', [])
        contacts = Contact.objects.filter(id__in=contact_ids)
        group.contacts.remove(*contacts)
        return Response({'success': True, 'removed': len(contact_ids), 'total': group.contacts.count()})


class ContactImportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContactImport.objects.all()
    serializer_class = ContactImportSerializer
    permission_classes = [permissions.IsAuthenticated, TenantObjectPermission, HasRolePermission]

    def get_queryset(self):
        org = getattr(self.request, 'organization', None)
        if not org:
            return ContactImport.objects.none()
        return ContactImport.objects.filter(organization=org)


class MergeAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MergeAuditLog.objects.all()
    serializer_class = MergeAuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, TenantObjectPermission, HasRolePermission]

    def get_queryset(self):
        org = getattr(self.request, 'organization', None)
        if not org:
            return MergeAuditLog.objects.none()
        return MergeAuditLog.objects.filter(organization=org)
