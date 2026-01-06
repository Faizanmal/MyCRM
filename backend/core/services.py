"""
MyCRM Core Services Module

This module provides the foundational service layer classes that implement
business logic abstraction, caching, and common CRUD operations.

Usage:
    from core.services import BaseService, CachedService

    class ContactService(CachedService):
        model = Contact
        cache_prefix = 'contact'
        cache_ttl = 300

        def get_by_email(self, email: str):
            return self.get_cached(
                key=f'email:{email}',
                queryset_fn=lambda: self.model.objects.filter(email=email).first()
            )
"""

import hashlib
import json
import logging
from collections.abc import Callable
from functools import wraps
from typing import Any, Generic, TypeVar

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.db.models import Q, QuerySet
from django.utils import timezone

logger = logging.getLogger(__name__)

# Type variable for generic model handling
ModelType = TypeVar('ModelType', bound=models.Model)


class ServiceException(Exception):
    """Base exception for service layer errors."""

    def __init__(self, message: str, code: str = None, details: dict = None):
        self.message = message
        self.code = code or 'service_error'
        self.details = details or {}
        super().__init__(message)


class EntityNotFoundException(ServiceException):
    """Raised when an entity is not found."""

    def __init__(self, entity: str, identifier: Any):
        super().__init__(
            message=f"{entity} not found: {identifier}",
            code='entity_not_found',
            details={'entity': entity, 'identifier': str(identifier)}
        )


class PermissionException(ServiceException):
    """Raised when permission is denied."""

    def __init__(self, action: str, resource: str):
        super().__init__(
            message=f"Permission denied: {action} on {resource}",
            code='permission_denied',
            details={'action': action, 'resource': resource}
        )


class ValidationException(ServiceException):
    """Raised when validation fails."""

    def __init__(self, errors: dict[str, list[str]]):
        message = "Validation failed"
        super().__init__(
            message=message,
            code='validation_error',
            details={'errors': errors}
        )


def with_transaction(func: Callable) -> Callable:
    """Decorator to wrap service method in database transaction."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with transaction.atomic():
            return func(*args, **kwargs)
    return wrapper


def with_logging(func: Callable) -> Callable:
    """Decorator to add logging to service methods."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        service_name = args[0].__class__.__name__ if args else 'Unknown'
        method_name = func.__name__

        logger.debug(f"[{service_name}] {method_name} called")
        start_time = timezone.now()

        try:
            result = func(*args, **kwargs)
            duration = (timezone.now() - start_time).total_seconds()
            logger.debug(f"[{service_name}] {method_name} completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = (timezone.now() - start_time).total_seconds()
            logger.error(
                f"[{service_name}] {method_name} failed after {duration:.3f}s: {str(e)}"
            )
            raise
    return wrapper


class BaseService(Generic[ModelType]):
    """
    Base service class providing common CRUD operations and business logic patterns.

    Attributes:
        model: The Django model class this service operates on
        serializer_class: Optional DRF serializer for validation

    Example:
        class ContactService(BaseService):
            model = Contact

            def get_active_contacts(self, organization_id):
                return self.filter(
                    organization_id=organization_id,
                    status='active'
                )
    """

    model: type[ModelType] = None
    serializer_class = None

    def __init__(self, user=None, organization=None):
        """
        Initialize the service.

        Args:
            user: The current user making the request
            organization: The organization context
        """
        self.user = user
        self.organization = organization
        self._validate_configuration()

    def _validate_configuration(self):
        """Validate service configuration."""
        if self.model is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define 'model' attribute"
            )

    def _get_base_queryset(self) -> QuerySet[ModelType]:
        """
        Get the base queryset with organization filtering.
        Override for custom base filtering.
        """
        qs = self.model.objects.all()

        # Apply organization filter if model has organization field
        if self.organization and hasattr(self.model, 'organization'):
            qs = qs.filter(organization=self.organization)
        elif self.organization and hasattr(self.model, 'organization_id'):
            qs = qs.filter(organization_id=self.organization.id)

        # Apply soft delete filter if model supports it
        if hasattr(self.model, 'is_deleted'):
            qs = qs.filter(is_deleted=False)

        return qs

    def get_queryset(self) -> QuerySet[ModelType]:
        """
        Get the queryset for this service.
        Override to add custom filtering, annotations, etc.
        """
        return self._get_base_queryset()

    @with_logging
    def get(self, pk: Any) -> ModelType:
        """
        Get a single instance by primary key.

        Args:
            pk: Primary key value

        Returns:
            Model instance

        Raises:
            EntityNotFoundException: If not found
        """
        try:
            return self.get_queryset().get(pk=pk)
        except ObjectDoesNotExist:
            raise EntityNotFoundException(
                entity=self.model.__name__,
                identifier=pk
            )

    @with_logging
    def get_or_none(self, pk: Any) -> ModelType | None:
        """
        Get a single instance or None if not found.

        Args:
            pk: Primary key value

        Returns:
            Model instance or None
        """
        try:
            return self.get_queryset().get(pk=pk)
        except ObjectDoesNotExist:
            return None

    @with_logging
    def filter(self, **kwargs) -> QuerySet[ModelType]:
        """
        Filter instances by keyword arguments.

        Args:
            **kwargs: Filter parameters

        Returns:
            Filtered queryset
        """
        return self.get_queryset().filter(**kwargs)

    @with_logging
    def search(
        self,
        query: str,
        search_fields: list[str],
        **filters
    ) -> QuerySet[ModelType]:
        """
        Search instances across multiple fields.

        Args:
            query: Search query string
            search_fields: List of field names to search
            **filters: Additional filter parameters

        Returns:
            Filtered queryset
        """
        qs = self.get_queryset()

        if filters:
            qs = qs.filter(**filters)

        if query and search_fields:
            search_query = Q()
            for field in search_fields:
                search_query |= Q(**{f'{field}__icontains': query})
            qs = qs.filter(search_query)

        return qs

    @with_logging
    @with_transaction
    def create(self, data: dict[str, Any]) -> ModelType:
        """
        Create a new instance.

        Args:
            data: Dictionary of field values

        Returns:
            Created model instance
        """
        # Add organization if not provided
        if self.organization and 'organization' not in data:
            if hasattr(self.model, 'organization'):
                data['organization'] = self.organization
            elif hasattr(self.model, 'organization_id'):
                data['organization_id'] = self.organization.id

        # Add created_by if not provided
        if self.user and 'created_by' not in data and hasattr(self.model, 'created_by'):
            data['created_by'] = self.user

        # Validate if serializer is configured
        if self.serializer_class:
            serializer = self.serializer_class(data=data)
            if not serializer.is_valid():
                raise ValidationException(serializer.errors)
            data = serializer.validated_data

        instance = self.model(**data)
        instance.full_clean()
        instance.save()

        logger.info(f"Created {self.model.__name__} with ID {instance.pk}")
        return instance

    @with_logging
    @with_transaction
    def update(self, pk: Any, data: dict[str, Any]) -> ModelType:
        """
        Update an existing instance.

        Args:
            pk: Primary key of instance to update
            data: Dictionary of field values to update

        Returns:
            Updated model instance
        """
        instance = self.get(pk)

        # Add modified_by if not provided
        if self.user and 'modified_by' not in data and hasattr(instance, 'modified_by'):
            data['modified_by'] = self.user

        # Validate if serializer is configured
        if self.serializer_class:
            serializer = self.serializer_class(instance, data=data, partial=True)
            if not serializer.is_valid():
                raise ValidationException(serializer.errors)
            data = serializer.validated_data

        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        instance.full_clean()
        instance.save()

        logger.info(f"Updated {self.model.__name__} with ID {pk}")
        return instance

    @with_logging
    @with_transaction
    def delete(self, pk: Any, hard_delete: bool = False) -> None:
        """
        Delete an instance (soft delete by default).

        Args:
            pk: Primary key of instance to delete
            hard_delete: If True, permanently delete. If False, soft delete.
        """
        instance = self.get(pk)

        if hard_delete or not hasattr(instance, 'is_deleted'):
            instance.delete()
            logger.info(f"Hard deleted {self.model.__name__} with ID {pk}")
        else:
            instance.is_deleted = True
            instance.deleted_at = timezone.now()
            if self.user and hasattr(instance, 'deleted_by'):
                instance.deleted_by = self.user
            instance.save()
            logger.info(f"Soft deleted {self.model.__name__} with ID {pk}")

    @with_logging
    @with_transaction
    def bulk_create(self, data_list: list[dict[str, Any]]) -> list[ModelType]:
        """
        Create multiple instances efficiently.

        Args:
            data_list: List of dictionaries with field values

        Returns:
            List of created model instances
        """
        instances = []
        for data in data_list:
            # Add organization if not provided
            if self.organization and 'organization' not in data:
                if hasattr(self.model, 'organization'):
                    data['organization'] = self.organization

            instance = self.model(**data)
            instances.append(instance)

        created = self.model.objects.bulk_create(instances)
        logger.info(f"Bulk created {len(created)} {self.model.__name__} instances")
        return created

    @with_logging
    @with_transaction
    def bulk_update(
        self,
        instances: list[ModelType],
        fields: list[str]
    ) -> int:
        """
        Update multiple instances efficiently.

        Args:
            instances: List of model instances with updated values
            fields: List of field names that were updated

        Returns:
            Number of updated instances
        """
        count = self.model.objects.bulk_update(instances, fields)
        logger.info(f"Bulk updated {count} {self.model.__name__} instances")
        return count

    def exists(self, **kwargs) -> bool:
        """Check if any matching instances exist."""
        return self.get_queryset().filter(**kwargs).exists()

    def count(self, **kwargs) -> int:
        """Count matching instances."""
        qs = self.get_queryset()
        if kwargs:
            qs = qs.filter(**kwargs)
        return qs.count()


class CachedService(BaseService[ModelType]):
    """
    Service with caching support.

    Attributes:
        cache_prefix: Prefix for cache keys
        cache_ttl: Cache time-to-live in seconds
        cache_enabled: Whether caching is enabled
    """

    cache_prefix: str = None
    cache_ttl: int = 300  # 5 minutes
    cache_enabled: bool = True

    def _validate_configuration(self):
        """Validate service configuration."""
        super()._validate_configuration()
        if self.cache_prefix is None:
            self.cache_prefix = self.model.__name__.lower()

    def _get_cache_key(self, key: str) -> str:
        """Generate a full cache key with prefix and organization."""
        org_id = self.organization.id if self.organization else 'global'
        return f"{self.cache_prefix}:{org_id}:{key}"

    def _get_content_hash(self, content: Any) -> str:
        """Generate a hash for cache key based on content."""
        content_str = json.dumps(content, sort_keys=True, default=str)
        return hashlib.md5(content_str.encode()).hexdigest()[:8]

    def get_cached(
        self,
        key: str,
        queryset_fn: Callable[[], Any],
        ttl: int = None
    ) -> Any:
        """
        Get a value from cache or execute queryset function.

        Args:
            key: Cache key (will be prefixed)
            queryset_fn: Function to execute if cache miss
            ttl: Optional TTL override

        Returns:
            Cached or computed value
        """
        if not self.cache_enabled or not getattr(settings, 'CACHES', None):
            return queryset_fn()

        full_key = self._get_cache_key(key)
        value = cache.get(full_key)

        if value is not None:
            logger.debug(f"Cache hit: {full_key}")
            return value

        logger.debug(f"Cache miss: {full_key}")
        value = queryset_fn()
        cache.set(full_key, value, ttl or self.cache_ttl)
        return value

    def invalidate_cache(self, key: str = None) -> None:
        """
        Invalidate cache entries.

        Args:
            key: Specific key to invalidate, or None to invalidate all
        """
        if key:
            full_key = self._get_cache_key(key)
            cache.delete(full_key)
            logger.debug(f"Invalidated cache: {full_key}")
        else:
            # Pattern invalidation requires Redis
            pattern = self._get_cache_key('*')
            logger.debug(f"Invalidating cache pattern: {pattern}")
            # Note: Pattern deletion requires Redis backend
            # cache.delete_pattern(pattern)

    @with_logging
    def get(self, pk: Any) -> ModelType:
        """Get with caching."""
        return self.get_cached(
            key=f'pk:{pk}',
            queryset_fn=lambda: super(CachedService, self).get(pk)
        )

    @with_transaction
    def create(self, data: dict[str, Any]) -> ModelType:
        """Create and invalidate cache."""
        instance = super().create(data)
        self.invalidate_cache()
        return instance

    @with_transaction
    def update(self, pk: Any, data: dict[str, Any]) -> ModelType:
        """Update and invalidate cache."""
        instance = super().update(pk, data)
        self.invalidate_cache(f'pk:{pk}')
        return instance

    @with_transaction
    def delete(self, pk: Any, hard_delete: bool = False) -> None:
        """Delete and invalidate cache."""
        super().delete(pk, hard_delete)
        self.invalidate_cache(f'pk:{pk}')


class NotificationService:
    """Service for sending notifications across channels."""

    @staticmethod
    def send_email(
        to: str,
        subject: str,
        template: str,
        context: dict[str, Any] = None,
        from_email: str = None
    ) -> bool:
        """Send an email notification."""
        from django.core.mail import send_mail
        from django.template.loader import render_to_string

        try:
            html_content = render_to_string(template, context or {})
            send_mail(
                subject=subject,
                message='',
                html_message=html_content,
                from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to],
            )
            logger.info(f"Email sent to {to}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {str(e)}")
            return False

    @staticmethod
    def send_push_notification(
        user_id: Any,
        title: str,
        body: str,
        data: dict[str, Any] = None
    ) -> bool:
        """Send a push notification."""
        # Implementation depends on push service (FCM, APNs, etc.)
        logger.info(f"Push notification to user {user_id}: {title}")
        return True

    @staticmethod
    def send_websocket_message(
        channel: str,
        message_type: str,
        data: dict[str, Any]
    ) -> bool:
        """Send a WebSocket message via Django Channels."""
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                channel,
                {
                    'type': message_type,
                    'data': data
                }
            )
            logger.debug(f"WebSocket message sent to {channel}")
            return True
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {str(e)}")
            return False


class EventPublisher:
    """Service for publishing domain events."""

    @staticmethod
    def publish(
        event_type: str,
        entity_type: str,
        entity_id: Any,
        data: dict[str, Any] = None,
        user_id: Any = None,
        organization_id: Any = None
    ):
        """
        Publish a domain event.

        Args:
            event_type: Type of event (created, updated, deleted, etc.)
            entity_type: Type of entity (contact, lead, opportunity, etc.)
            entity_id: ID of the entity
            data: Additional event data
            user_id: ID of user who triggered the event
            organization_id: Organization context
        """
        from django.utils import timezone

        event = {
            'event_type': event_type,
            'entity_type': entity_type,
            'entity_id': str(entity_id),
            'data': data or {},
            'user_id': str(user_id) if user_id else None,
            'organization_id': str(organization_id) if organization_id else None,
            'timestamp': timezone.now().isoformat()
        }

        logger.info(f"Event published: {event_type} - {entity_type}:{entity_id}")

        # Send via Celery task for async processing
        try:
            from .tasks import process_domain_event
            process_domain_event.delay(event)
        except ImportError:
            # If task not available, process synchronously
            logger.warning("Celery task not available, skipping async event processing")

        # Also send via WebSocket for real-time updates
        if organization_id:
            NotificationService.send_websocket_message(
                channel=f'org_{organization_id}',
                message_type='domain_event',
                data=event
            )
