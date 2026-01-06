"""
Bulk Operations API

Provides bulk action endpoints for:
- Bulk update
- Bulk delete
- Bulk assign
- Bulk status change
"""

import logging
from typing import Any

from django.db import transaction
from django.db.models import Model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class BulkOperationService:
    """Service for handling bulk operations on models."""

    MAX_BULK_SIZE = 1000  # Maximum items per bulk operation

    @classmethod
    def validate_ids(cls, ids: list[int], queryset) -> tuple[list[Model], list[int]]:
        """
        Validate IDs and return found objects and missing IDs.
        """
        if len(ids) > cls.MAX_BULK_SIZE:
            raise ValueError(f"Maximum {cls.MAX_BULK_SIZE} items allowed per operation")

        objects = list(queryset.filter(id__in=ids))
        found_ids = {obj.id for obj in objects}
        missing_ids = [id for id in ids if id not in found_ids]

        return objects, missing_ids

    @classmethod
    @transaction.atomic
    def bulk_update(
        cls,
        queryset,
        ids: list[int],
        update_data: dict[str, Any],
        allowed_fields: list[str]
    ) -> dict[str, Any]:
        """
        Perform bulk update on objects.
        """
        # Filter to only allowed fields
        sanitized_data = {
            k: v for k, v in update_data.items()
            if k in allowed_fields
        }

        if not sanitized_data:
            raise ValueError("No valid fields to update")

        objects, missing_ids = cls.validate_ids(ids, queryset)

        if not objects:
            raise ValueError("No valid objects found")

        # Perform update
        count = queryset.filter(id__in=[obj.id for obj in objects]).update(**sanitized_data)

        return {
            'updated': count,
            'missing_ids': missing_ids,
        }

    @classmethod
    @transaction.atomic
    def bulk_delete(cls, queryset, ids: list[int]) -> dict[str, Any]:
        """
        Perform bulk delete on objects.
        """
        objects, missing_ids = cls.validate_ids(ids, queryset)

        if not objects:
            raise ValueError("No valid objects found")

        count = queryset.filter(id__in=[obj.id for obj in objects]).delete()[0]

        return {
            'deleted': count,
            'missing_ids': missing_ids,
        }

    @classmethod
    @transaction.atomic
    def bulk_assign(
        cls,
        queryset,
        ids: list[int],
        assignee_id: int,
        assignee_field: str = 'assigned_to'
    ) -> dict[str, Any]:
        """
        Bulk assign objects to a user.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            assignee = User.objects.get(id=assignee_id)
        except User.DoesNotExist:
            raise ValueError("Invalid assignee")

        objects, missing_ids = cls.validate_ids(ids, queryset)

        if not objects:
            raise ValueError("No valid objects found")

        count = queryset.filter(id__in=[obj.id for obj in objects]).update(
            **{assignee_field: assignee}
        )

        return {
            'assigned': count,
            'assignee': assignee.get_full_name() or assignee.username,
            'missing_ids': missing_ids,
        }


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_update_leads(request):
    """Bulk update leads."""
    try:
        from lead_management.models import Lead

        ids = request.data.get('ids', [])
        update_data = request.data.get('data', {})

        if not ids:
            return Response({
                'success': False,
                'message': 'No IDs provided'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get user's accessible leads
        queryset = Lead.objects.filter(created_by=request.user)

        # Allowed fields for bulk update
        allowed_fields = ['status', 'source', 'assigned_to', 'score']

        result = BulkOperationService.bulk_update(
            queryset, ids, update_data, allowed_fields
        )

        return Response({
            'success': True,
            'message': f"Updated {result['updated']} leads",
            'data': result
        })

    except ValueError as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Bulk update leads error: {e}")
        return Response({
            'success': False,
            'message': 'An error occurred'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_delete_leads(request):
    """Bulk delete leads."""
    try:
        from lead_management.models import Lead

        ids = request.data.get('ids', [])

        if not ids:
            return Response({
                'success': False,
                'message': 'No IDs provided'
            }, status=status.HTTP_400_BAD_REQUEST)

        queryset = Lead.objects.filter(created_by=request.user)
        result = BulkOperationService.bulk_delete(queryset, ids)

        return Response({
            'success': True,
            'message': f"Deleted {result['deleted']} leads",
            'data': result
        })

    except ValueError as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Bulk delete leads error: {e}")
        return Response({
            'success': False,
            'message': 'An error occurred'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_assign_leads(request):
    """Bulk assign leads to a user."""
    try:
        from lead_management.models import Lead

        ids = request.data.get('ids', [])
        assignee_id = request.data.get('assignee_id')

        if not ids:
            return Response({
                'success': False,
                'message': 'No IDs provided'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not assignee_id:
            return Response({
                'success': False,
                'message': 'No assignee provided'
            }, status=status.HTTP_400_BAD_REQUEST)

        queryset = Lead.objects.filter(created_by=request.user)
        result = BulkOperationService.bulk_assign(
            queryset, ids, assignee_id, 'assigned_to'
        )

        return Response({
            'success': True,
            'message': f"Assigned {result['assigned']} leads to {result['assignee']}",
            'data': result
        })

    except ValueError as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Bulk assign leads error: {e}")
        return Response({
            'success': False,
            'message': 'An error occurred'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_update_tasks(request):
    """Bulk update tasks."""
    try:
        from task_management.models import Task

        ids = request.data.get('ids', [])
        update_data = request.data.get('data', {})

        if not ids:
            return Response({
                'success': False,
                'message': 'No IDs provided'
            }, status=status.HTTP_400_BAD_REQUEST)

        queryset = Task.objects.filter(created_by=request.user)
        allowed_fields = ['status', 'priority', 'assigned_to', 'due_date']

        result = BulkOperationService.bulk_update(
            queryset, ids, update_data, allowed_fields
        )

        return Response({
            'success': True,
            'message': f"Updated {result['updated']} tasks",
            'data': result
        })

    except ValueError as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Bulk update tasks error: {e}")
        return Response({
            'success': False,
            'message': 'An error occurred'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_complete_tasks(request):
    """Bulk mark tasks as complete."""
    try:
        from task_management.models import Task

        ids = request.data.get('ids', [])

        if not ids:
            return Response({
                'success': False,
                'message': 'No IDs provided'
            }, status=status.HTTP_400_BAD_REQUEST)

        queryset = Task.objects.filter(created_by=request.user)

        result = BulkOperationService.bulk_update(
            queryset, ids, {'status': 'completed'}, ['status']
        )

        return Response({
            'success': True,
            'message': f"Completed {result['updated']} tasks",
            'data': result
        })

    except ValueError as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Bulk complete tasks error: {e}")
        return Response({
            'success': False,
            'message': 'An error occurred'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# URL patterns to add to urls.py:
# path('bulk/leads/update/', bulk_update_leads, name='bulk-update-leads'),
# path('bulk/leads/delete/', bulk_delete_leads, name='bulk-delete-leads'),
# path('bulk/leads/assign/', bulk_assign_leads, name='bulk-assign-leads'),
# path('bulk/tasks/update/', bulk_update_tasks, name='bulk-update-tasks'),
# path('bulk/tasks/complete/', bulk_complete_tasks, name='bulk-complete-tasks'),
