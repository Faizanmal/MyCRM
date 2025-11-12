"""
Advanced Search Module
Provides full-text search, filters, and search analytics
"""

from django.db.models import Q, Count, Avg, Sum, Max, Min
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.apps import apps
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class AdvancedSearch:
    """Advanced search engine with multiple search strategies"""
    
    def __init__(self, model_name, user=None):
        """
        Initialize search engine
        
        Args:
            model_name: Model to search (e.g., 'contact_management.Contact')
            user: User performing the search (for permission checks)
        """
        self.model_name = model_name
        self.model = apps.get_model(model_name)
        self.user = user
        self.queryset = self.model.objects.all()
    
    def search(self, query=None, filters=None, full_text_fields=None, 
               order_by=None, limit=None):
        """
        Perform advanced search
        
        Args:
            query: Search query string
            filters: Dict of field filters
            full_text_fields: List of fields for full-text search
            order_by: Field to order results by
            limit: Maximum number of results
        
        Returns:
            QuerySet of search results
        """
        results = self.queryset
        
        # Apply full-text search
        if query and full_text_fields:
            results = self._full_text_search(results, query, full_text_fields)
        elif query:
            # Fallback to basic search
            results = self._basic_search(results, query)
        
        # Apply filters
        if filters:
            results = self._apply_filters(results, filters)
        
        # Apply ordering
        if order_by:
            results = results.order_by(order_by)
        
        # Apply limit
        if limit:
            results = results[:limit]
        
        # Log search for analytics
        self._log_search(query, filters, results.count())
        
        return results
    
    def _full_text_search(self, queryset, query, fields):
        """
        Perform full-text search using PostgreSQL
        Note: For SQLite, falls back to basic search
        """
        try:
            # Create search vector for multiple fields
            search_vector = SearchVector(*fields)
            search_query = SearchQuery(query)
            
            # Annotate with search rank
            queryset = queryset.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query).order_by('-rank')
            
            return queryset
        except Exception as e:
            logger.warning(f"Full-text search failed, falling back to basic: {str(e)}")
            return self._basic_search(queryset, query)
    
    def _basic_search(self, queryset, query):
        """Basic search across text fields"""
        if not query:
            return queryset
        
        # Get all char and text fields
        text_fields = [
            f.name for f in self.model._meta.fields
            if f.get_internal_type() in ['CharField', 'TextField']
        ]
        
        # Build OR query for all text fields
        q_objects = Q()
        for field in text_fields:
            q_objects |= Q(**{f"{field}__icontains": query})
        
        return queryset.filter(q_objects)
    
    def _apply_filters(self, queryset, filters):
        """Apply advanced filters"""
        for field, filter_config in filters.items():
            if isinstance(filter_config, dict):
                operator = filter_config.get('operator', 'exact')
                value = filter_config.get('value')
                
                if operator == 'exact':
                    queryset = queryset.filter(**{field: value})
                elif operator == 'contains':
                    queryset = queryset.filter(**{f"{field}__icontains": value})
                elif operator == 'startswith':
                    queryset = queryset.filter(**{f"{field}__istartswith": value})
                elif operator == 'endswith':
                    queryset = queryset.filter(**{f"{field}__iendswith": value})
                elif operator == 'gt':
                    queryset = queryset.filter(**{f"{field}__gt": value})
                elif operator == 'gte':
                    queryset = queryset.filter(**{f"{field}__gte": value})
                elif operator == 'lt':
                    queryset = queryset.filter(**{f"{field}__lt": value})
                elif operator == 'lte':
                    queryset = queryset.filter(**{f"{field}__lte": value})
                elif operator == 'in':
                    queryset = queryset.filter(**{f"{field}__in": value})
                elif operator == 'range':
                    queryset = queryset.filter(**{f"{field}__range": value})
                elif operator == 'isnull':
                    queryset = queryset.filter(**{f"{field}__isnull": value})
            else:
                # Simple filter
                queryset = queryset.filter(**{field: filter_config})
        
        return queryset
    
    def faceted_search(self, facet_fields):
        """
        Perform faceted search (aggregation by fields)
        
        Args:
            facet_fields: List of fields to create facets for
        
        Returns:
            Dict of facet counts
        """
        facets = {}
        
        for field in facet_fields:
            facets[field] = self.queryset.values(field).annotate(
                count=Count('id')
            ).order_by('-count')
        
        return facets
    
    def aggregate_search(self, aggregations):
        """
        Perform aggregation on search results
        
        Args:
            aggregations: Dict of field: aggregation_type
                         e.g., {'revenue': 'sum', 'deals': 'count'}
        
        Returns:
            Dict of aggregated values
        """
        agg_dict = {}
        
        for field, agg_type in aggregations.items():
            if agg_type == 'count':
                agg_dict[f"{field}_count"] = Count(field)
            elif agg_type == 'sum':
                agg_dict[f"{field}_sum"] = Sum(field)
            elif agg_type == 'avg':
                agg_dict[f"{field}_avg"] = Avg(field)
            elif agg_type == 'max':
                agg_dict[f"{field}_max"] = Max(field)
            elif agg_type == 'min':
                agg_dict[f"{field}_min"] = Min(field)
        
        return self.queryset.aggregate(**agg_dict)
    
    def _log_search(self, query, filters, result_count):
        """Log search for analytics"""
        from .models import SearchLog
        
        try:
            SearchLog.objects.create(
                user=self.user,
                model_name=self.model_name,
                query=query or '',
                filters=filters or {},
                result_count=result_count
            )
        except Exception as e:
            logger.warning(f"Failed to log search: {str(e)}")


class SearchBuilder:
    """Fluent interface for building complex searches"""
    
    def __init__(self, model_name, user=None):
        self.search = AdvancedSearch(model_name, user)
        self._query = None
        self._filters = {}
        self._full_text_fields = None
        self._order_by = None
        self._limit = None
    
    def query(self, text):
        """Set search query"""
        self._query = text
        return self
    
    def filter(self, **kwargs):
        """Add filters"""
        self._filters.update(kwargs)
        return self
    
    def full_text(self, *fields):
        """Set fields for full-text search"""
        self._full_text_fields = fields
        return self
    
    def order_by(self, field):
        """Set ordering"""
        self._order_by = field
        return self
    
    def limit(self, count):
        """Set result limit"""
        self._limit = count
        return self
    
    def filter_by_date_range(self, field, start_date, end_date):
        """Filter by date range"""
        self._filters[field] = {
            'operator': 'range',
            'value': [start_date, end_date]
        }
        return self
    
    def filter_greater_than(self, field, value):
        """Filter greater than"""
        self._filters[field] = {
            'operator': 'gt',
            'value': value
        }
        return self
    
    def filter_less_than(self, field, value):
        """Filter less than"""
        self._filters[field] = {
            'operator': 'lt',
            'value': value
        }
        return self
    
    def filter_in(self, field, values):
        """Filter by list of values"""
        self._filters[field] = {
            'operator': 'in',
            'value': values
        }
        return self
    
    def execute(self):
        """Execute the search"""
        return self.search.search(
            query=self._query,
            filters=self._filters,
            full_text_fields=self._full_text_fields,
            order_by=self._order_by,
            limit=self._limit
        )


class SearchSuggestions:
    """Provide search suggestions and autocomplete"""
    
    @staticmethod
    def suggest(model_name, field, partial_query, limit=10):
        """
        Get search suggestions for a field
        
        Args:
            model_name: Model to search
            field: Field to suggest from
            partial_query: Partial query string
            limit: Maximum suggestions
        
        Returns:
            List of suggestions
        """
        model = apps.get_model(model_name)
        
        suggestions = model.objects.filter(
            **{f"{field}__istartswith": partial_query}
        ).values_list(field, flat=True).distinct()[:limit]
        
        return list(suggestions)
    
    @staticmethod
    def popular_searches(model_name, limit=10):
        """
        Get popular searches for a model
        
        Args:
            model_name: Model name
            limit: Maximum results
        
        Returns:
            List of popular search queries
        """
        from .models import SearchLog
        
        popular = SearchLog.objects.filter(
            model_name=model_name,
            query__isnull=False
        ).exclude(query='').values('query').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]
        
        return [item['query'] for item in popular]


class SmartSearch:
    """Intelligent search with natural language processing"""
    
    @staticmethod
    def parse_natural_query(query):
        """
        Parse natural language query into structured filters
        
        Example: "contacts created last week with email"
        Returns: {
            'model': 'contacts',
            'filters': {'created_at': {'operator': 'range', 'value': [last_week]}},
            'fields': ['email']
        }
        """
        # Basic keyword extraction
        keywords = {
            'model': None,
            'filters': {},
            'date_filters': []
        }
        
        query_lower = query.lower()
        
        # Detect model
        if 'contact' in query_lower:
            keywords['model'] = 'contact_management.Contact'
        elif 'lead' in query_lower:
            keywords['model'] = 'lead_management.Lead'
        elif 'opportunity' in query_lower or 'deal' in query_lower:
            keywords['model'] = 'opportunity_management.Opportunity'
        
        # Detect time ranges
        if 'today' in query_lower:
            keywords['date_filters'].append('today')
        elif 'yesterday' in query_lower:
            keywords['date_filters'].append('yesterday')
        elif 'last week' in query_lower:
            keywords['date_filters'].append('last_week')
        elif 'this month' in query_lower:
            keywords['date_filters'].append('this_month')
        
        # Detect field requirements
        if 'with email' in query_lower or 'has email' in query_lower:
            keywords['filters']['email__isnull'] = False
        if 'without email' in query_lower or 'no email' in query_lower:
            keywords['filters']['email__isnull'] = True
        
        return keywords
