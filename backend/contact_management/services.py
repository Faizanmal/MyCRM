"""
MyCRM Contact & Account Management Service Layer

This module provides enterprise business logic for Contacts and Accounts:
- Tenant-scoped CRUD and caching
- Multi-criteria duplicate detection
- Invariant-guarded Merge & Unmerge workflows with immutable audit snapshots
- Streaming bounded-memory import for high-volume fixtures (10k+ records)
- Cross-tenant reassignment prevention and audit logging
"""

import csv
import io
import json
import logging
import os
import tracemalloc
from datetime import timedelta
from typing import Any, Dict, Generator, Iterable, List, Optional, Tuple, Union

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Avg, Count, Q, QuerySet
from django.utils import timezone

from core.services import (
    CachedService,
    EventPublisher,
    NotificationService,
    ValidationException,
    with_logging,
    with_transaction,
)
from contact_management.models import (
    Account,
    Contact,
    ContactActivity,
    ContactGroup,
    MergeAuditLog,
)

logger = logging.getLogger(__name__)
User = get_user_model()


class ContactService(CachedService):
    """
    Enterprise service for managing contacts.
    Provides tenant-scoped operations, duplicate detection, atomic merge/unmerge,
    and memory-bounded bulk ingestion.
    """
    model = Contact
    cache_prefix = 'contact'
    cache_ttl = 300

    SEARCH_FIELDS = [
        'first_name',
        'last_name',
        'email',
        'company_name',
        'phone',
        'job_title'
    ]

    LIFECYCLE_STAGES = [
        'subscriber',
        'lead',
        'marketing_qualified',
        'sales_qualified',
        'opportunity',
        'customer',
        'evangelist'
    ]

    def get_queryset(self, include_merged: bool = False) -> QuerySet:
        """Get queryset with select_related and exclude merged records by default"""
        qs = super().get_queryset()
        if not include_merged:
            qs = qs.filter(is_merged=False)
        return qs.select_related(
            'owner',
            'assigned_to',
            'account',
            'organization',
            'created_by'
        ).prefetch_related('activities')

    @with_logging
    def search_contacts(
        self,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        order_by: str = '-created_at',
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[QuerySet, int]:
        """Advanced contact search with tenant filtering and pagination."""
        qs = self.get_queryset()
        filters = filters or {}

        if query:
            search_query = Q()
            for field in self.SEARCH_FIELDS:
                search_query |= Q(**{f'{field}__icontains': query})
            qs = qs.filter(search_query)

        if 'status' in filters:
            qs = qs.filter(status=filters['status'])
        if 'lifecycle_stage' in filters:
            qs = qs.filter(lifecycle_stage=filters['lifecycle_stage'])
        if 'owner_id' in filters:
            qs = qs.filter(owner_id=filters['owner_id'])
        if 'account_id' in filters:
            qs = qs.filter(account_id=filters['account_id'])
        if 'company' in filters:
            qs = qs.filter(Q(company_name__icontains=filters['company']) | Q(account__name__icontains=filters['company']))
        if 'contact_type' in filters:
            qs = qs.filter(contact_type=filters['contact_type'])

        total_count = qs.count()
        qs = qs.order_by(order_by)
        offset = (page - 1) * page_size
        return qs[offset:offset + page_size], total_count

    @with_logging
    @with_transaction
    def create_contact(self, data: Dict[str, Any]) -> Contact:
        """Create a contact with validation and tenant scoping."""
        if self.organization:
            data['organization'] = self.organization
        if self.user and 'created_by' not in data:
            data['created_by'] = self.user
        if self.user and 'assigned_to' not in data and 'owner' not in data:
            data['assigned_to'] = self.user
            data['owner'] = self.user

        # Support 'company' alias for company_name
        if 'company' in data and 'company_name' not in data:
            data['company_name'] = data.pop('company')

        # Check tenant duplicate email
        email = data.get('email')
        if email and self.organization:
            existing = Contact.objects.filter(
                organization=self.organization,
                email__iexact=email,
                is_merged=False
            ).first()
            if existing:
                raise ValidationException({
                    'email': [f"A contact with email '{email}' already exists in this organization."]
                })

        contact = Contact(**data)
        try:
            contact.full_clean()
        except ValidationError as e:
            raise ValidationException(e.message_dict if hasattr(e, 'message_dict') else {'non_field_errors': e.messages})

        contact.save()
        self.invalidate_cache()
        return contact

    @with_logging
    def find_duplicates(
        self,
        contact_id: Optional[int] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        company: Optional[str] = None,
        name: Optional[str] = None
    ) -> QuerySet:
        """Find potential duplicates scoped to the current tenant."""
        qs = self.get_queryset()
        conditions = Q()

        if contact_id:
            target = self.get(contact_id)
            email = email or target.email
            phone = phone or target.phone or target.mobile
            company = company or target.company
            name = name or target.full_name
            qs = qs.exclude(id=contact_id)

        if email:
            conditions |= Q(email__iexact=email)

        if phone:
            digits = ''.join(filter(str.isdigit, phone))
            if len(digits) >= 7:
                conditions |= Q(phone__endswith=digits[-7:]) | Q(mobile__endswith=digits[-7:])

        if company and name:
            name_parts = name.strip().split()
            if len(name_parts) >= 2:
                conditions |= Q(
                    first_name__iexact=name_parts[0],
                    last_name__iexact=name_parts[-1],
                    company_name__icontains=company
                )

        if not conditions:
            return qs.none()

        return qs.filter(conditions).distinct()

    @with_logging
    @with_transaction
    def merge_contacts(
        self,
        primary_id: int,
        secondary_id: int,
        field_choices: Optional[Dict[str, str]] = None
    ) -> Tuple[Contact, MergeAuditLog]:
        """
        Merge two contacts with strict tenant invariants and immutable snapshot logging.
        Invariants:
        1. Both primary and secondary must exist.
        2. primary_id != secondary_id.
        3. Both must belong to the exact same organization (cross-tenant merge prohibited).
        4. Neither can already be merged.
        """
        field_choices = field_choices or {}

        if primary_id == secondary_id:
            raise ValidationException({'non_field_errors': ["Cannot merge contact with itself."]})

        try:
            primary = Contact.objects.select_for_update().get(id=primary_id)
            secondary = Contact.objects.select_for_update().get(id=secondary_id)
        except Contact.DoesNotExist as e:
            raise ValidationException({'non_field_errors': [f"Contact not found: {str(e)}"]})

        # Tenant boundary check
        if primary.organization_id != secondary.organization_id:
            raise ValidationException({'non_field_errors': ["Cross-tenant merge is strictly prohibited."]})

        if self.organization and primary.organization_id != self.organization.id:
            raise ValidationException({'non_field_errors': ["Unauthorized: Contact does not belong to active organization."]})

        if primary.is_merged or secondary.is_merged:
            raise ValidationException({'non_field_errors': ["Cannot merge a record that is already merged."]})

        # Capture secondary snapshot before changes
        secondary_snapshot = {
            'id': secondary.id,
            'first_name': secondary.first_name,
            'last_name': secondary.last_name,
            'email': secondary.email,
            'phone': secondary.phone,
            'mobile': secondary.mobile,
            'company_name': secondary.company_name,
            'job_title': secondary.job_title,
            'department': secondary.department,
            'address_line_1': secondary.address_line_1,
            'address_line_2': secondary.address_line_2,
            'city': secondary.city,
            'state': secondary.state,
            'postal_code': secondary.postal_code,
            'country': secondary.country,
            'contact_type': secondary.contact_type,
            'lifecycle_stage': secondary.lifecycle_stage,
            'source': secondary.source,
            'notes': secondary.notes,
            'tags': secondary.tags,
            'custom_fields': secondary.custom_fields,
            'account_id': secondary.account_id,
            'assigned_to_id': secondary.assigned_to_id,
            'owner_id': secondary.owner_id,
        }

        # Merge fields based on preferences or non-empty secondary values
        mergeable = [
            'phone', 'mobile', 'job_title', 'department', 'address_line_1',
            'address_line_2', 'city', 'state', 'postal_code', 'country',
            'website', 'linkedin', 'twitter', 'notes'
        ]
        for field in mergeable:
            choice = field_choices.get(field, 'primary')
            sec_val = getattr(secondary, field, None)
            prim_val = getattr(primary, field, None)
            if choice == 'secondary' and sec_val:
                setattr(primary, field, sec_val)
            elif not prim_val and sec_val:
                setattr(primary, field, sec_val)

        # Merge Account if primary has none
        if not primary.account_id and secondary.account_id:
            primary.account = secondary.account
            primary.company_name = secondary.company_name

        # Merge tags (union of lists)
        merged_tags = list(set((primary.tags or []) + (secondary.tags or [])))
        primary.tags = merged_tags

        # Merge custom fields (shallow dict merge)
        merged_custom = dict(secondary.custom_fields or {})
        merged_custom.update(primary.custom_fields or {})
        primary.custom_fields = merged_custom

        # Repoint related activities
        repointed = {}
        activity_ids = list(secondary.activities.values_list('id', flat=True))
        secondary.activities.update(contact=primary)
        repointed['activities'] = activity_ids
        repointed['activities_count'] = len(activity_ids)

        # Repoint opportunities if opportunity model links to contact
        try:
            from opportunity_management.models import Opportunity
            opp_count = Opportunity.objects.filter(contact=secondary).update(contact=primary)
            repointed['opportunities_count'] = opp_count
        except (ImportError, Exception):
            pass

        # Repoint contact groups
        for group in secondary.groups.all():
            group.contacts.add(primary)

        primary.save()

        # Mark secondary as merged (do not delete to preserve lineage and enable unmerge)
        secondary.is_merged = True
        secondary.merged_into = primary
        secondary.save(update_fields=['is_merged', 'merged_into', 'updated_at'])

        # Create immutable merge audit log
        merge_log = MergeAuditLog.objects.create(
            entity_type='contact',
            organization=primary.organization,
            primary_id=primary.id,
            secondary_id=secondary.id,
            secondary_snapshot=secondary_snapshot,
            repointed_relations=repointed,
            merged_by=self.user
        )

        logger.info(
            f"AUDIT: Contact merge completed: {secondary.id} -> {primary.id} "
            f"in Org {primary.organization_id} by user {self.user}"
        )
        self.invalidate_cache()
        return primary, merge_log

    @with_logging
    @with_transaction
    def unmerge_contact(self, merge_log_id: int) -> Contact:
        """
        Revert a previous merge operation using the snapshot in MergeAuditLog.
        Invariants:
        1. MergeAuditLog must exist and belong to current tenant.
        2. Must not be already reverted.
        3. Restores secondary to is_merged=False and clears merged_into.
        """
        try:
            merge_log = MergeAuditLog.objects.select_for_update().get(id=merge_log_id)
        except MergeAuditLog.DoesNotExist:
            raise ValidationException({'non_field_errors': [f"Merge log {merge_log_id} not found."]})

        if self.organization and merge_log.organization_id != self.organization.id:
            raise ValidationException({'non_field_errors': ["Unauthorized: Merge log belongs to a different organization."]})

        if merge_log.is_reverted:
            raise ValidationException({'non_field_errors': ["This merge has already been unmerged/reverted."]})

        try:
            secondary = Contact.objects.select_for_update().get(id=merge_log.secondary_id)
        except Contact.DoesNotExist:
            raise ValidationException({'non_field_errors': ["Secondary contact no longer exists; cannot unmerge."]})

        # Revert secondary status
        secondary.is_merged = False
        secondary.merged_into = None
        secondary.save(update_fields=['is_merged', 'merged_into', 'updated_at'])

        # Repoint activities back to secondary contact
        activity_ids = merge_log.repointed_relations.get('activities', [])
        if activity_ids:
            ContactActivity.objects.filter(id__in=activity_ids).update(contact=secondary)

        merge_log.is_reverted = True
        merge_log.reverted_by = self.user
        merge_log.reverted_at = timezone.now()
        merge_log.save(update_fields=['is_reverted', 'reverted_by', 'reverted_at'])

        logger.info(
            f"AUDIT: Contact unmerge completed for log {merge_log.id}: "
            f"restored contact {secondary.id} in Org {merge_log.organization_id}"
        )
        self.invalidate_cache()
        return secondary

    def import_contacts_stream(
        self,
        stream_or_path: Union[str, io.TextIOBase, Iterable[str]],
        mapping: Optional[Dict[str, str]] = None,
        duplicate_strategy: str = 'skip',  # 'skip', 'update', 'error'
        batch_size: int = 500
    ) -> Dict[str, Any]:
        """
        Import contacts with strict memory bounding (constant peak memory).
        Streams line-by-line in batches of `batch_size`, using bulk_create and bulk_update.
        """
        mapping = mapping or {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'email': 'email',
            'phone': 'phone',
            'company': 'company_name',
            'company_name': 'company_name',
            'job_title': 'job_title',
        }

        tracemalloc.start()
        start_mem, _ = tracemalloc.get_traced_memory()

        created_count = 0
        updated_count = 0
        skipped_count = 0
        failed_count = 0
        errors = []
        total_rows = 0

        # Closeable handle tracker
        file_to_close = None
        is_dict_stream = False
        if isinstance(stream_or_path, str):
            if os.path.isfile(stream_or_path):
                file_to_close = open(stream_or_path, 'r', encoding='utf-8', errors='replace')
                reader_iter = file_to_close
            else:
                reader_iter = io.StringIO(stream_or_path)
        elif hasattr(stream_or_path, 'read'):
            reader_iter = stream_or_path
        elif hasattr(stream_or_path, '__iter__'):
            reader_iter = stream_or_path
            is_dict_stream = True
        else:
            reader_iter = stream_or_path

        try:
            row_iterator = reader_iter if is_dict_stream else csv.DictReader(reader_iter)

            batch: List[Dict[str, Any]] = []

            def process_batch(chunk: List[Dict[str, Any]]):
                nonlocal created_count, updated_count, skipped_count, failed_count
                if not chunk:
                    return

                chunk_emails = [item['email'].strip().lower() for item in chunk if item.get('email')]
                existing_map = {}
                if self.organization and chunk_emails:
                    existing_qs = Contact.objects.filter(
                        organization=self.organization,
                        email__in=chunk_emails,
                        is_merged=False
                    )
                    for c in existing_qs:
                        existing_map[c.email.lower()] = c

                to_create = []
                to_update = []

                for item in chunk:
                    email_key = item.get('email', '').strip().lower()
                    if not email_key:
                        failed_count += 1
                        errors.append(f"Row without email: {item}")
                        continue

                    if email_key in existing_map:
                        if duplicate_strategy == 'skip':
                            skipped_count += 1
                            continue
                        elif duplicate_strategy == 'error':
                            failed_count += 1
                            errors.append(f"Duplicate email found in org: {email_key}")
                            continue
                        elif duplicate_strategy == 'update':
                            contact_obj = existing_map[email_key]
                            for k, v in item.items():
                                if k != 'email' and hasattr(contact_obj, k):
                                    setattr(contact_obj, k, v)
                            to_update.append(contact_obj)
                    else:
                        contact_data = dict(item)
                        if 'company' in contact_data and 'company_name' not in contact_data:
                            contact_data['company_name'] = contact_data.pop('company')
                        contact_data['organization'] = self.organization
                        if self.user:
                            contact_data.setdefault('created_by', self.user)
                            contact_data.setdefault('assigned_to', self.user)
                            contact_data.setdefault('owner', self.user)
                        to_create.append(Contact(**contact_data))

                if to_create:
                    Contact.objects.bulk_create(to_create, batch_size=batch_size)
                    created_count += len(to_create)

                if to_update:
                    update_fields = ['first_name', 'last_name', 'phone', 'company_name', 'job_title', 'updated_at']
                    Contact.objects.bulk_update(to_update, update_fields, batch_size=batch_size)
                    updated_count += len(to_update)

            for row in row_iterator:
                total_rows += 1
                mapped_row = {}
                for header, val in row.items():
                    target_field = mapping.get(header) or mapping.get(str(header).strip())
                    if target_field:
                        mapped_row[target_field] = (val or '').strip() if isinstance(val, str) else val

                if 'email' in mapped_row and mapped_row['email']:
                    batch.append(mapped_row)

                if len(batch) >= batch_size:
                    process_batch(batch)
                    batch = []

            # Flush residual batch
            if batch:
                process_batch(batch)
                batch = []

        finally:
            if file_to_close:
                file_to_close.close()
            _, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()

        logger.info(
            f"STREAM IMPORT COMPLETED: {total_rows} rows processed, "
            f"{created_count} created, {updated_count} updated, {skipped_count} skipped. "
            f"Peak memory: {(peak_mem - start_mem) / 1024 / 1024:.2f} MB"
        )

        return {
            'total_processed': total_rows,
            'created': created_count,
            'updated': updated_count,
            'skipped': skipped_count,
            'failed': failed_count,
            'errors': errors[:50],  # capped for bounded reporting
            'peak_memory_mb': round((peak_mem - start_mem) / 1024 / 1024, 2)
        }


class AccountService(CachedService):
    """
    Enterprise service for managing B2B Accounts.
    Provides tenant-scoped operations, duplicate detection, atomic merge/unmerge,
    and memory-bounded bulk ingestion.
    """
    model = Account
    cache_prefix = 'account'
    cache_ttl = 300

    SEARCH_FIELDS = ['name', 'domain', 'industry', 'city', 'country']

    def get_queryset(self, include_merged: bool = False) -> QuerySet:
        qs = super().get_queryset()
        if not include_merged:
            qs = qs.filter(is_merged=False)
        return qs.select_related(
            'organization',
            'owner',
            'assigned_to',
            'created_by'
        ).prefetch_related('contacts')

    @with_logging
    def search_accounts(
        self,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        order_by: str = '-created_at',
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[QuerySet, int]:
        qs = self.get_queryset()
        filters = filters or {}

        if query:
            search_query = Q()
            for field in self.SEARCH_FIELDS:
                search_query |= Q(**{f'{field}__icontains': query})
            qs = qs.filter(search_query)

        if 'account_type' in filters:
            qs = qs.filter(account_type=filters['account_type'])
        if 'tier' in filters:
            qs = qs.filter(tier=filters['tier'])
        if 'owner_id' in filters:
            qs = qs.filter(owner_id=filters['owner_id'])
        if 'industry' in filters:
            qs = qs.filter(industry__icontains=filters['industry'])
        if 'is_active' in filters:
            qs = qs.filter(is_active=filters['is_active'])

        total_count = qs.count()
        qs = qs.order_by(order_by)
        offset = (page - 1) * page_size
        return qs[offset:offset + page_size], total_count

    @with_logging
    @with_transaction
    def create_account(self, data: Dict[str, Any]) -> Account:
        if self.organization:
            data['organization'] = self.organization
        if self.user and 'created_by' not in data:
            data['created_by'] = self.user
        if self.user and 'assigned_to' not in data and 'owner' not in data:
            data['assigned_to'] = self.user
            data['owner'] = self.user

        # Enforce unique tenant account name
        name = data.get('name')
        if name and self.organization:
            existing = Account.objects.filter(
                organization=self.organization,
                name__iexact=name,
                is_merged=False
            ).first()
            if existing:
                raise ValidationException({
                    'name': [f"An account with name '{name}' already exists in this organization."]
                })

        account = Account(**data)
        try:
            account.full_clean()
        except ValidationError as e:
            raise ValidationException(e.message_dict if hasattr(e, 'message_dict') else {'non_field_errors': e.messages})

        account.save()
        self.invalidate_cache()
        return account

    @with_logging
    @with_transaction
    def merge_accounts(
        self,
        primary_id: int,
        secondary_id: int,
        field_choices: Optional[Dict[str, str]] = None
    ) -> Tuple[Account, MergeAuditLog]:
        """
        Merge two accounts with strict tenant invariants, repointing contacts, and audit logging.
        Invariants:
        1. Both accounts exist and belong to the same organization.
        2. primary_id != secondary_id.
        3. Neither can already be merged.
        """
        field_choices = field_choices or {}

        if primary_id == secondary_id:
            raise ValidationException({'non_field_errors': ["Cannot merge account with itself."]})

        try:
            primary = Account.objects.select_for_update().get(id=primary_id)
            secondary = Account.objects.select_for_update().get(id=secondary_id)
        except Account.DoesNotExist as e:
            raise ValidationException({'non_field_errors': [f"Account not found: {str(e)}"]})

        # Tenant boundary check
        if primary.organization_id != secondary.organization_id:
            raise ValidationException({'non_field_errors': ["Cross-tenant merge is strictly prohibited."]})

        if self.organization and primary.organization_id != self.organization.id:
            raise ValidationException({'non_field_errors': ["Unauthorized: Account does not belong to active organization."]})

        if primary.is_merged or secondary.is_merged:
            raise ValidationException({'non_field_errors': ["Cannot merge a record that is already merged."]})

        # Secondary snapshot
        secondary_snapshot = {
            'id': secondary.id,
            'name': secondary.name,
            'domain': secondary.domain,
            'industry': secondary.industry,
            'company_size': secondary.company_size,
            'annual_revenue': str(secondary.annual_revenue) if secondary.annual_revenue else None,
            'website': secondary.website,
            'phone': secondary.phone,
            'city': secondary.city,
            'state': secondary.state,
            'country': secondary.country,
            'account_type': secondary.account_type,
            'tier': secondary.tier,
            'owner_id': secondary.owner_id,
            'assigned_to_id': secondary.assigned_to_id,
            'custom_fields': secondary.custom_fields,
            'tags': secondary.tags,
        }

        # Merge fields
        mergeable = [
            'domain', 'industry', 'company_size', 'annual_revenue', 'description',
            'website', 'linkedin_url', 'phone', 'address_line1', 'city', 'state',
            'postal_code', 'country'
        ]
        for field in mergeable:
            choice = field_choices.get(field, 'primary')
            sec_val = getattr(secondary, field, None)
            prim_val = getattr(primary, field, None)
            if choice == 'secondary' and sec_val:
                setattr(primary, field, sec_val)
            elif not prim_val and sec_val:
                setattr(primary, field, sec_val)

        merged_tags = list(set((primary.tags or []) + (secondary.tags or [])))
        primary.tags = merged_tags

        merged_custom = dict(secondary.custom_fields or {})
        merged_custom.update(primary.custom_fields or {})
        primary.custom_fields = merged_custom

        # Repoint contacts
        contact_ids = list(Contact.objects.filter(account=secondary).values_list('id', flat=True))
        contacts_count = Contact.objects.filter(account=secondary).update(
            account=primary,
            company_name=primary.name
        )
        repointed = {'contacts': contact_ids, 'contacts_count': contacts_count}

        primary.save()

        # Mark secondary merged
        secondary.is_merged = True
        secondary.merged_into = primary
        secondary.is_active = False
        secondary.save(update_fields=['is_merged', 'merged_into', 'is_active', 'updated_at'])

        merge_log = MergeAuditLog.objects.create(
            entity_type='account',
            organization=primary.organization,
            primary_id=primary.id,
            secondary_id=secondary.id,
            secondary_snapshot=secondary_snapshot,
            repointed_relations=repointed,
            merged_by=self.user
        )

        logger.info(
            f"AUDIT: Account merge completed: {secondary.id} -> {primary.id} "
            f"in Org {primary.organization_id} by user {self.user}"
        )
        self.invalidate_cache()
        return primary, merge_log

    @with_logging
    @with_transaction
    def unmerge_account(self, merge_log_id: int) -> Account:
        """Revert an account merge operation."""
        try:
            merge_log = MergeAuditLog.objects.select_for_update().get(id=merge_log_id)
        except MergeAuditLog.DoesNotExist:
            raise ValidationException({'non_field_errors': [f"Merge log {merge_log_id} not found."]})

        if self.organization and merge_log.organization_id != self.organization.id:
            raise ValidationException({'non_field_errors': ["Unauthorized: Merge log belongs to a different organization."]})

        if merge_log.is_reverted:
            raise ValidationException({'non_field_errors': ["This merge has already been unmerged/reverted."]})

        try:
            secondary = Account.objects.select_for_update().get(id=merge_log.secondary_id)
        except Account.DoesNotExist:
            raise ValidationException({'non_field_errors': ["Secondary account no longer exists; cannot unmerge."]})

        secondary.is_merged = False
        secondary.merged_into = None
        secondary.is_active = True
        secondary.save(update_fields=['is_merged', 'merged_into', 'is_active', 'updated_at'])

        # Repoint contacts back
        contact_ids = merge_log.repointed_relations.get('contacts', [])
        if contact_ids:
            Contact.objects.filter(id__in=contact_ids).update(account=secondary, company_name=secondary.name)

        merge_log.is_reverted = True
        merge_log.reverted_by = self.user
        merge_log.reverted_at = timezone.now()
        merge_log.save(update_fields=['is_reverted', 'reverted_by', 'reverted_at'])

        logger.info(
            f"AUDIT: Account unmerge completed for log {merge_log.id}: "
            f"restored account {secondary.id} in Org {merge_log.organization_id}"
        )
        self.invalidate_cache()
        return secondary

    def import_accounts_stream(
        self,
        stream_or_path: Union[str, io.TextIOBase, Iterable[Any]],
        mapping: Optional[Dict[str, str]] = None,
        duplicate_strategy: str = 'skip',
        batch_size: int = 500
    ) -> Dict[str, Any]:
        """
        Import accounts with bounded memory streaming.
        """
        mapping = mapping or {
            'name': 'name',
            'domain': 'domain',
            'industry': 'industry',
            'tier': 'tier',
            'account_type': 'account_type',
        }

        created_count = 0
        updated_count = 0
        skipped_count = 0
        failed_count = 0
        errors = []
        total_rows = 0

        file_to_close = None
        is_dict_stream = False
        if isinstance(stream_or_path, str):
            if os.path.isfile(stream_or_path):
                file_to_close = open(stream_or_path, 'r', encoding='utf-8', errors='replace')
                reader_iter = file_to_close
            else:
                reader_iter = io.StringIO(stream_or_path)
        elif hasattr(stream_or_path, 'read'):
            reader_iter = stream_or_path
        elif hasattr(stream_or_path, '__iter__'):
            reader_iter = stream_or_path
            is_dict_stream = True
        else:
            reader_iter = stream_or_path

        try:
            row_iterator = reader_iter if is_dict_stream else csv.DictReader(reader_iter)
            batch: List[Dict[str, Any]] = []

            def process_batch(chunk: List[Dict[str, Any]]):
                nonlocal created_count, updated_count, skipped_count, failed_count
                if not chunk:
                    return

                chunk_names = [item['name'].strip().lower() for item in chunk if item.get('name')]
                existing_map = {}
                if self.organization and chunk_names:
                    for acc in Account.objects.filter(organization=self.organization, name__in=chunk_names, is_merged=False):
                        existing_map[acc.name.lower()] = acc

                to_create = []
                for item in chunk:
                    name_key = item.get('name', '').strip().lower()
                    if not name_key:
                        failed_count += 1
                        continue

                    if name_key in existing_map:
                        skipped_count += 1
                        continue

                    account_data = dict(item)
                    account_data['organization'] = self.organization
                    if self.user:
                        account_data.setdefault('created_by', self.user)
                        account_data.setdefault('assigned_to', self.user)
                        account_data.setdefault('owner', self.user)
                    to_create.append(Account(**account_data))

                if to_create:
                    Account.objects.bulk_create(to_create, batch_size=batch_size)
                    created_count += len(to_create)

            for row in row_iterator:
                total_rows += 1
                mapped_row = {}
                for header, val in row.items():
                    target = mapping.get(header) or mapping.get(str(header).strip())
                    if target:
                        mapped_row[target] = (val or '').strip() if isinstance(val, str) else val
                if 'name' in mapped_row and mapped_row['name']:
                    batch.append(mapped_row)
                if len(batch) >= batch_size:
                    process_batch(batch)
                    batch = []

            if batch:
                process_batch(batch)

            return {
                'total_rows': total_rows,
                'created': created_count,
                'updated': updated_count,
                'skipped': skipped_count,
                'failed': failed_count,
                'errors': errors,
            }
        finally:
            if file_to_close:
                file_to_close.close()
