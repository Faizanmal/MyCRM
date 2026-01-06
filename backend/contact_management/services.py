"""
MyCRM Contact Management Service

This module provides comprehensive business logic for contact management,
including CRUD operations, search, enrichment, and analytics.
"""

import logging
from datetime import timedelta
from typing import Any

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

logger = logging.getLogger(__name__)


class ContactService(CachedService):
    """
    Service for managing contacts.

    Provides comprehensive contact management including:
    - CRUD operations with validation
    - Advanced search and filtering
    - Contact scoring and enrichment
    - Duplicate detection
    - Bulk operations
    - Activity tracking
    """

    # Lazy model import to avoid circular dependencies
    @property
    def model(self):
        from contact_management.models import Contact
        return Contact

    cache_prefix = 'contact'
    cache_ttl = 300  # 5 minutes

    # Search configuration
    SEARCH_FIELDS = [
        'first_name',
        'last_name',
        'email',
        'company',
        'phone',
        'job_title'
    ]

    # Lifecycle stages
    LIFECYCLE_STAGES = [
        'subscriber',
        'lead',
        'marketing_qualified',
        'sales_qualified',
        'opportunity',
        'customer',
        'evangelist'
    ]

    def get_queryset(self) -> QuerySet:
        """Get queryset with common select_related and prefetch_related."""
        qs = super().get_queryset()
        return qs.select_related(
            'owner',
            'assigned_to',
            'company'
        ).prefetch_related(
            'tags',
            'activities'
        )

    @with_logging
    def search_contacts(
        self,
        query: str = None,
        filters: dict[str, Any] = None,
        order_by: str = '-created_at',
        page: int = 1,
        page_size: int = 20
    ) -> tuple[QuerySet, int]:
        """
        Advanced contact search with filtering and pagination.

        Args:
            query: Free text search query
            filters: Dictionary of filter parameters
            order_by: Field to order results by
            page: Page number (1-indexed)
            page_size: Number of results per page

        Returns:
            Tuple of (queryset, total_count)
        """
        qs = self.get_queryset()
        filters = filters or {}

        # Apply text search
        if query:
            search_query = Q()
            for field in self.SEARCH_FIELDS:
                search_query |= Q(**{f'{field}__icontains': query})
            qs = qs.filter(search_query)

        # Apply filters
        if 'status' in filters:
            qs = qs.filter(status=filters['status'])

        if 'lifecycle_stage' in filters:
            qs = qs.filter(lifecycle_stage=filters['lifecycle_stage'])

        if 'owner_id' in filters:
            qs = qs.filter(owner_id=filters['owner_id'])

        if 'company' in filters:
            qs = qs.filter(company__icontains=filters['company'])

        if 'tags' in filters:
            tags = filters['tags']
            if isinstance(tags, str):
                tags = [tags]
            qs = qs.filter(tags__name__in=tags)

        if 'created_after' in filters:
            qs = qs.filter(created_at__gte=filters['created_after'])

        if 'created_before' in filters:
            qs = qs.filter(created_at__lte=filters['created_before'])

        if 'score_min' in filters:
            qs = qs.filter(score__gte=filters['score_min'])

        if 'score_max' in filters:
            qs = qs.filter(score__lte=filters['score_max'])

        # Get total count before pagination
        total_count = qs.count()

        # Apply ordering
        qs = qs.order_by(order_by)

        # Apply pagination
        offset = (page - 1) * page_size
        qs = qs[offset:offset + page_size]

        return qs, total_count

    @with_logging
    @with_transaction
    def create_contact(self, data: dict[str, Any]) -> Any:
        """
        Create a new contact with validation and duplicate detection.

        Args:
            data: Contact data dictionary

        Returns:
            Created contact instance
        """
        # Check for duplicates by email
        email = data.get('email')
        if email and self.exists(email=email):
            raise ValidationException({
                'email': ['A contact with this email already exists']
            })

        # Set default lifecycle stage
        if 'lifecycle_stage' not in data:
            data['lifecycle_stage'] = 'subscriber'

        # Set default status
        if 'status' not in data:
            data['status'] = 'active'

        # Calculate initial score
        data['score'] = self._calculate_contact_score(data)

        # Create contact
        contact = self.create(data)

        # Publish creation event
        EventPublisher.publish(
            event_type='created',
            entity_type='contact',
            entity_id=contact.pk,
            data={'email': contact.email, 'company': contact.company},
            user_id=self.user.pk if self.user else None,
            organization_id=self.organization.pk if self.organization else None
        )

        # Trigger enrichment if enabled
        self._trigger_enrichment(contact)

        return contact

    @with_logging
    @with_transaction
    def update_contact(self, contact_id: Any, data: dict[str, Any]) -> Any:
        """
        Update a contact with validation.

        Args:
            contact_id: Contact ID
            data: Updated data dictionary

        Returns:
            Updated contact instance
        """
        contact = self.get(contact_id)

        # Check email uniqueness if changing
        new_email = data.get('email')
        if new_email and new_email != contact.email and self.exists(email=new_email):
            raise ValidationException({
                'email': ['A contact with this email already exists']
            })

        # Track lifecycle stage changes
        old_stage = contact.lifecycle_stage
        new_stage = data.get('lifecycle_stage', old_stage)

        # Update contact
        contact = self.update(contact_id, data)

        # Recalculate score if relevant fields changed
        if any(k in data for k in ['email', 'phone', 'company', 'job_title']):
            contact.score = self._calculate_contact_score(contact.__dict__)
            contact.save(update_fields=['score'])

        # Publish update event
        EventPublisher.publish(
            event_type='updated',
            entity_type='contact',
            entity_id=contact.pk,
            data={'updated_fields': list(data.keys())},
            user_id=self.user.pk if self.user else None,
            organization_id=self.organization.pk if self.organization else None
        )

        # Handle lifecycle stage transition
        if old_stage != new_stage:
            self._handle_lifecycle_transition(contact, old_stage, new_stage)

        return contact

    @with_logging
    @with_transaction
    def merge_contacts(
        self,
        primary_id: Any,
        secondary_id: Any,
        field_choices: dict[str, str] = None
    ) -> Any:
        """
        Merge two contacts into one.

        Args:
            primary_id: ID of the contact to keep
            secondary_id: ID of the contact to merge into primary
            field_choices: Dict mapping field names to 'primary' or 'secondary'

        Returns:
            Merged contact instance
        """
        primary = self.get(primary_id)
        secondary = self.get(secondary_id)
        field_choices = field_choices or {}

        # Merge fields based on choices or non-empty values
        mergeable_fields = [
            'phone', 'mobile', 'company', 'job_title', 'department',
            'website', 'linkedin_url', 'twitter_handle',
            'address_line1', 'city', 'state', 'postal_code', 'country'
        ]

        for field in mergeable_fields:
            primary_value = getattr(primary, field, None)
            secondary_value = getattr(secondary, field, None)

            choice = field_choices.get(field, 'primary')

            if choice == 'secondary' and secondary_value or not primary_value and secondary_value:
                setattr(primary, field, secondary_value)

        # Keep higher score
        if secondary.score > primary.score:
            primary.score = secondary.score

        # Merge tags
        if hasattr(primary, 'tags') and hasattr(secondary, 'tags'):
            for tag in secondary.tags.all():
                primary.tags.add(tag)

        primary.save()

        # Move related records to primary
        self._transfer_related_records(primary, secondary)

        # Soft delete secondary contact
        self.delete(secondary_id)

        # Publish merge event
        EventPublisher.publish(
            event_type='merged',
            entity_type='contact',
            entity_id=primary.pk,
            data={'merged_from': str(secondary_id)},
            user_id=self.user.pk if self.user else None,
            organization_id=self.organization.pk if self.organization else None
        )

        logger.info(f"Merged contact {secondary_id} into {primary_id}")
        return primary

    @with_logging
    def find_duplicates(
        self,
        contact_id: Any = None,
        email: str = None,
        phone: str = None,
        company: str = None,
        name: str = None
    ) -> QuerySet:
        """
        Find potential duplicate contacts.

        Args:
            contact_id: Optional ID of contact to find duplicates for
            email: Email to match
            phone: Phone to match
            company: Company to match
            name: Name to match

        Returns:
            QuerySet of potential duplicates
        """
        qs = self.get_queryset()
        conditions = Q()

        # Get comparison data from existing contact
        if contact_id:
            contact = self.get(contact_id)
            email = email or contact.email
            phone = phone or contact.phone
            company = company or contact.company
            name = name or f"{contact.first_name} {contact.last_name}"
            qs = qs.exclude(pk=contact_id)

        # Build match conditions
        if email:
            conditions |= Q(email__iexact=email)

        if phone:
            # Normalize phone for comparison
            normalized_phone = ''.join(filter(str.isdigit, phone))
            conditions |= Q(phone__endswith=normalized_phone[-10:])

        if company and name:
            # Fuzzy match on company + name combination
            name_parts = name.split()
            if len(name_parts) >= 2:
                conditions |= Q(
                    company__icontains=company,
                    first_name__icontains=name_parts[0],
                    last_name__icontains=name_parts[-1]
                )

        return qs.filter(conditions).distinct()

    @with_logging
    @with_transaction
    def bulk_update_lifecycle(
        self,
        contact_ids: list[Any],
        lifecycle_stage: str
    ) -> int:
        """
        Bulk update lifecycle stage for multiple contacts.

        Args:
            contact_ids: List of contact IDs
            lifecycle_stage: New lifecycle stage

        Returns:
            Number of updated contacts
        """
        if lifecycle_stage not in self.LIFECYCLE_STAGES:
            raise ValidationException({
                'lifecycle_stage': [f'Invalid stage. Must be one of: {", ".join(self.LIFECYCLE_STAGES)}']
            })

        contacts = self.get_queryset().filter(pk__in=contact_ids)
        count = contacts.update(
            lifecycle_stage=lifecycle_stage,
            updated_at=timezone.now()
        )

        # Publish bulk update event
        EventPublisher.publish(
            event_type='bulk_updated',
            entity_type='contact',
            entity_id=None,
            data={
                'contact_ids': [str(cid) for cid in contact_ids],
                'lifecycle_stage': lifecycle_stage
            },
            user_id=self.user.pk if self.user else None,
            organization_id=self.organization.pk if self.organization else None
        )

        # Invalidate cache
        self.invalidate_cache()

        return count

    @with_logging
    def get_contact_analytics(self) -> dict[str, Any]:
        """
        Get aggregate analytics for contacts.

        Returns:
            Dictionary of analytics data
        """
        cache_key = 'analytics:overview'

        def compute_analytics():
            qs = self.get_queryset()

            # Count by status
            status_counts = dict(
                qs.values('status')
                .annotate(count=Count('id'))
                .values_list('status', 'count')
            )

            # Count by lifecycle stage
            stage_counts = dict(
                qs.values('lifecycle_stage')
                .annotate(count=Count('id'))
                .values_list('lifecycle_stage', 'count')
            )

            # Count by source
            source_counts = dict(
                qs.values('source')
                .annotate(count=Count('id'))
                .values_list('source', 'count')
            )

            # Score distribution
            score_stats = qs.aggregate(
                avg_score=Avg('score'),
                total_count=Count('id')
            )

            # Recent activity
            thirty_days_ago = timezone.now() - timedelta(days=30)
            recent_count = qs.filter(created_at__gte=thirty_days_ago).count()

            return {
                'total_contacts': score_stats['total_count'] or 0,
                'average_score': round(score_stats['avg_score'] or 0, 1),
                'by_status': status_counts,
                'by_lifecycle_stage': stage_counts,
                'by_source': source_counts,
                'created_last_30_days': recent_count
            }

        return self.get_cached(cache_key, compute_analytics, ttl=600)

    def _calculate_contact_score(self, data: dict[str, Any]) -> int:
        """
        Calculate contact score based on completeness and quality.

        Args:
            data: Contact data dictionary

        Returns:
            Score from 0-100
        """
        score = 0

        # Email (25 points)
        if data.get('email'):
            score += 25

        # Phone (15 points)
        if data.get('phone') or data.get('mobile'):
            score += 15

        # Company (15 points)
        if data.get('company'):
            score += 15

        # Job title (10 points)
        if data.get('job_title'):
            score += 10

        # Full name (10 points)
        if data.get('first_name') and data.get('last_name'):
            score += 10

        # Address (10 points)
        if data.get('city') and data.get('country'):
            score += 10

        # Social profiles (10 points)
        if data.get('linkedin_url'):
            score += 5
        if data.get('twitter_handle'):
            score += 5

        # Website (5 points)
        if data.get('website'):
            score += 5

        return min(score, 100)

    def _trigger_enrichment(self, contact) -> None:
        """Trigger contact enrichment if configured."""
        try:
            from data_enrichment.tasks import enrich_contact
            enrich_contact.delay(str(contact.pk))
            logger.debug(f"Triggered enrichment for contact {contact.pk}")
        except ImportError:
            logger.debug("Data enrichment module not available")

    def _handle_lifecycle_transition(
        self,
        contact,
        old_stage: str,
        new_stage: str
    ) -> None:
        """Handle lifecycle stage transition side effects."""
        logger.info(
            f"Contact {contact.pk} lifecycle transition: {old_stage} -> {new_stage}"
        )

        # Notify owner of significant transitions
        significant_transitions = ['sales_qualified', 'opportunity', 'customer']
        if new_stage in significant_transitions and contact.owner:
            NotificationService.send_email(
                to=contact.owner.email,
                subject=f"Contact {contact.email} moved to {new_stage}",
                template='emails/lifecycle_transition.html',
                context={
                    'contact': contact,
                    'old_stage': old_stage,
                    'new_stage': new_stage
                }
            )

    def _transfer_related_records(self, primary, secondary) -> None:
        """Transfer related records from secondary to primary contact."""
        # Transfer activities
        if hasattr(secondary, 'activities'):
            secondary.activities.update(contact=primary)

        # Transfer notes
        if hasattr(secondary, 'notes'):
            secondary.notes.update(contact=primary)

        # Transfer opportunities
        if hasattr(secondary, 'opportunities'):
            secondary.opportunities.update(contact=primary)

        # Transfer email tracking
        if hasattr(secondary, 'email_tracking'):
            secondary.email_tracking.update(contact=primary)

        logger.debug(f"Transferred related records from {secondary.pk} to {primary.pk}")
