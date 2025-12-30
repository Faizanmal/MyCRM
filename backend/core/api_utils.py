"""
API Utilities and Helpers

Provides utilities for API development including:
- Response formatting
- Pagination helpers
- Error handling
- Query parameter parsing
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from dataclasses import dataclass
from functools import wraps
import logging

from django.db.models import QuerySet, Model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework.serializers import Serializer

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Model)


@dataclass
class APIResponse:
    """Standardized API response structure."""
    success: bool
    data: Any = None
    message: str = ""
    errors: Optional[Dict[str, List[str]]] = None
    meta: Optional[Dict[str, Any]] = None
    
    def to_response(self, status_code: int = 200) -> Response:
        """Convert to DRF Response."""
        response_data = {
            'success': self.success,
            'data': self.data,
        }
        
        if self.message:
            response_data['message'] = self.message
            
        if self.errors:
            response_data['errors'] = self.errors
            
        if self.meta:
            response_data['meta'] = self.meta
            
        return Response(response_data, status=status_code)


def success_response(
    data: Any = None,
    message: str = "",
    meta: Optional[Dict[str, Any]] = None,
    status_code: int = 200
) -> Response:
    """Create a successful API response."""
    return APIResponse(
        success=True,
        data=data,
        message=message,
        meta=meta
    ).to_response(status_code)


def error_response(
    message: str,
    errors: Optional[Dict[str, List[str]]] = None,
    status_code: int = 400
) -> Response:
    """Create an error API response."""
    return APIResponse(
        success=False,
        message=message,
        errors=errors
    ).to_response(status_code)


def paginate_queryset(
    queryset: QuerySet,
    page: int = 1,
    page_size: int = 20,
    max_page_size: int = 100
) -> Dict[str, Any]:
    """
    Paginate a queryset and return pagination metadata.
    
    Returns:
        Dict containing 'results', 'count', 'page', 'page_size', 
        'total_pages', 'has_next', 'has_previous'
    """
    # Enforce max page size
    page_size = min(page_size, max_page_size)
    
    paginator = Paginator(queryset, page_size)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
        page = 1
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
        page = paginator.num_pages
    
    return {
        'results': list(page_obj),
        'count': paginator.count,
        'page': page,
        'page_size': page_size,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'next_page': page + 1 if page_obj.has_next() else None,
        'previous_page': page - 1 if page_obj.has_previous() else None,
    }


class PaginatedSerializer(Generic[T]):
    """Helper for paginated responses with serialization."""
    
    def __init__(
        self,
        queryset: QuerySet[T],
        serializer_class: Type[Serializer],
        request,
        page_size: int = 20
    ):
        self.queryset = queryset
        self.serializer_class = serializer_class
        self.request = request
        self.page_size = page_size
        
    def get_response(self) -> Response:
        """Get paginated response."""
        page = self._get_page_param()
        page_size = self._get_page_size_param()
        
        pagination_data = paginate_queryset(
            self.queryset, 
            page=page, 
            page_size=page_size
        )
        
        serializer = self.serializer_class(
            pagination_data['results'],
            many=True,
            context={'request': self.request}
        )
        
        return success_response(
            data=serializer.data,
            meta={
                'pagination': {
                    'count': pagination_data['count'],
                    'page': pagination_data['page'],
                    'page_size': pagination_data['page_size'],
                    'total_pages': pagination_data['total_pages'],
                    'has_next': pagination_data['has_next'],
                    'has_previous': pagination_data['has_previous'],
                }
            }
        )
    
    def _get_page_param(self) -> int:
        """Get page number from request."""
        try:
            return int(self.request.query_params.get('page', 1))
        except (ValueError, TypeError):
            return 1
    
    def _get_page_size_param(self) -> int:
        """Get page size from request."""
        try:
            return int(self.request.query_params.get('page_size', self.page_size))
        except (ValueError, TypeError):
            return self.page_size


def custom_exception_handler(exc, context):
    """
    Custom exception handler for consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Standardize error response format
        errors = None
        
        if isinstance(response.data, dict):
            # Handle validation errors
            if 'detail' not in response.data:
                errors = {}
                for key, value in response.data.items():
                    if isinstance(value, list):
                        errors[key] = value
                    else:
                        errors[key] = [str(value)]
                message = "Validation error"
            else:
                message = str(response.data.get('detail', 'An error occurred'))
        elif isinstance(response.data, list):
            message = str(response.data[0]) if response.data else "An error occurred"
        else:
            message = str(response.data)
        
        response.data = {
            'success': False,
            'message': message,
            'errors': errors,
            'status_code': response.status_code,
        }
    
    # Log unexpected errors
    if response is None or response.status_code >= 500:
        logger.error(
            f"Unhandled exception in {context.get('view', 'unknown view')}: {exc}",
            exc_info=True
        )
    
    return response


class QueryParamParser:
    """Helper for parsing and validating query parameters."""
    
    def __init__(self, request):
        self.params = request.query_params
        
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer parameter."""
        try:
            return int(self.params.get(key, default))
        except (ValueError, TypeError):
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean parameter."""
        value = self.params.get(key, '').lower()
        if value in ('true', '1', 'yes'):
            return True
        if value in ('false', '0', 'no'):
            return False
        return default
    
    def get_list(self, key: str, separator: str = ',') -> List[str]:
        """Get list parameter."""
        value = self.params.get(key, '')
        if not value:
            return []
        return [item.strip() for item in value.split(separator) if item.strip()]
    
    def get_str(self, key: str, default: str = '') -> str:
        """Get string parameter."""
        return self.params.get(key, default)
    
    def get_choice(self, key: str, choices: List[str], default: str = '') -> str:
        """Get choice parameter with validation."""
        value = self.params.get(key, default)
        return value if value in choices else default


class BulkOperationMixin:
    """Mixin for bulk operations on ViewSets."""
    
    def get_bulk_ids(self, request) -> List[int]:
        """Extract IDs from request for bulk operations."""
        ids = request.data.get('ids', [])
        if isinstance(ids, str):
            ids = [int(i.strip()) for i in ids.split(',') if i.strip().isdigit()]
        return [int(i) for i in ids if str(i).isdigit()]
    
    def bulk_update(self, request, *args, **kwargs):
        """Bulk update records."""
        ids = self.get_bulk_ids(request)
        if not ids:
            return error_response("No IDs provided", status_code=400)
        
        update_data = request.data.get('update', {})
        if not update_data:
            return error_response("No update data provided", status_code=400)
        
        queryset = self.get_queryset().filter(id__in=ids)
        count = queryset.update(**update_data)
        
        return success_response(
            data={'updated': count},
            message=f"Successfully updated {count} records"
        )
    
    def bulk_delete(self, request, *args, **kwargs):
        """Bulk delete records."""
        ids = self.get_bulk_ids(request)
        if not ids:
            return error_response("No IDs provided", status_code=400)
        
        queryset = self.get_queryset().filter(id__in=ids)
        count = queryset.count()
        queryset.delete()
        
        return success_response(
            data={'deleted': count},
            message=f"Successfully deleted {count} records"
        )


def api_view_logging(view_func):
    """Decorator to log API view calls."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        logger.info(
            f"API Call: {request.method} {request.path} "
            f"User: {request.user.id if request.user.is_authenticated else 'anonymous'}"
        )
        
        try:
            response = view_func(request, *args, **kwargs)
            logger.info(
                f"API Response: {request.path} "
                f"Status: {getattr(response, 'status_code', 'unknown')}"
            )
            return response
        except Exception as e:
            logger.exception(f"API Error: {request.path} - {str(e)}")
            raise
    
    return wrapper


# Custom API Exceptions
class ResourceNotFoundError(APIException):
    """Resource not found exception."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'The requested resource was not found.'
    default_code = 'not_found'


class ValidationError(APIException):
    """Validation error exception."""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'The provided data is invalid.'
    default_code = 'validation_error'


class PermissionDeniedError(APIException):
    """Permission denied exception."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'permission_denied'


class RateLimitExceededError(APIException):
    """Rate limit exceeded exception."""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Rate limit exceeded. Please try again later.'
    default_code = 'rate_limit_exceeded'


class ServiceUnavailableError(APIException):
    """Service unavailable exception."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'The service is temporarily unavailable.'
    default_code = 'service_unavailable'
