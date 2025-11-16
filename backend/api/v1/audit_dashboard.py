"""
Audit Trail and Dashboard API Views
"""
from rest_framework import viewsets, views, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import timedelta

from core.audit_models import AuditTrail, FieldHistory, DataSnapshot
from core.dashboard_models import DashboardWidget, UserDashboard, DashboardWidgetPlacement, WidgetDataCache
from rest_framework import serializers


# Audit Trail Serializers
class AuditTrailSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    model_name = serializers.CharField(source='content_type.model', read_only=True)
    
    class Meta:
        model = AuditTrail
        fields = [
            'id', 'user', 'user_name', 'user_email', 'content_type', 'model_name',
            'object_id', 'object_repr', 'action', 'description', 'changes',
            'old_values', 'new_values', 'ip_address', 'user_agent', 'request_id',
            'metadata', 'timestamp'
        ]
        read_only_fields = fields


class FieldHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    
    class Meta:
        model = FieldHistory
        fields = [
            'id', 'content_type', 'object_id', 'field_name', 'field_label',
            'old_value', 'new_value', 'old_value_display', 'new_value_display',
            'changed_by', 'changed_by_name', 'changed_at'
        ]
        read_only_fields = fields


# Dashboard Serializers
class DashboardWidgetSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'name', 'description', 'widget_type', 'data_source', 'query_params',
            'size', 'color_scheme', 'icon', 'chart_config', 'value_format',
            'value_prefix', 'value_suffix', 'refresh_interval', 'last_refreshed_at',
            'is_public', 'shared_with_users', 'shared_with_roles', 'created_by',
            'created_by_name', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'last_refreshed_at']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class DashboardWidgetPlacementSerializer(serializers.ModelSerializer):
    widget_detail = DashboardWidgetSerializer(source='widget', read_only=True)
    
    class Meta:
        model = DashboardWidgetPlacement
        fields = [
            'id', 'dashboard', 'widget', 'widget_detail', 'row', 'column',
            'width', 'height', 'order', 'custom_title', 'custom_query_params',
            'is_visible', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserDashboardSerializer(serializers.ModelSerializer):
    widget_placements = DashboardWidgetPlacementSerializer(many=True, read_only=True)
    widget_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UserDashboard
        fields = [
            'id', 'user', 'name', 'description', 'layout_config', 'is_default',
            'widget_placements', 'widget_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_widget_count(self, obj):
        return obj.widget_placements.filter(is_visible=True).count()
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# ViewSets
class AuditTrailViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View audit trail records (read-only)
    """
    queryset = AuditTrail.objects.select_related('user', 'content_type').all()
    serializer_class = AuditTrailSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'user', 'content_type']
    search_fields = ['object_repr', 'description', 'user_email']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        # Filter by model type
        model_name = self.request.query_params.get('model')
        if model_name:
            try:
                ct = ContentType.objects.get(model=model_name.lower())
                queryset = queryset.filter(content_type=ct)
            except ContentType.DoesNotExist:
                pass
        
        # Filter by object
        object_id = self.request.query_params.get('object_id')
        if object_id:
            queryset = queryset.filter(object_id=object_id)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get audit trail statistics"""
        queryset = self.get_queryset()
        
        # Action breakdown
        action_counts = {}
        for action_choice in AuditTrail.ACTION_TYPES:
            action_key = action_choice[0]
            count = queryset.filter(action=action_key).count()
            action_counts[action_key] = count
        
        # Top users
        top_users = queryset.values('user__username', 'user_email').annotate(
            count=models.Count('id')
        ).order_by('-count')[:10]
        
        # Activity by day (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_activity = queryset.filter(
            timestamp__gte=thirty_days_ago
        ).extra(
            select={'day': 'date(timestamp)'}
        ).values('day').annotate(
            count=models.Count('id')
        ).order_by('day')
        
        return Response({
            'total_records': queryset.count(),
            'action_breakdown': action_counts,
            'top_users': list(top_users),
            'daily_activity': list(daily_activity)
        })


class FieldHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View field change history
    """
    queryset = FieldHistory.objects.select_related('changed_by', 'content_type').all()
    serializer_class = FieldHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['field_name', 'changed_by', 'content_type']
    ordering_fields = ['changed_at']
    ordering = ['-changed_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by object
        object_id = self.request.query_params.get('object_id')
        model_name = self.request.query_params.get('model')
        
        if object_id and model_name:
            try:
                ct = ContentType.objects.get(model=model_name.lower())
                queryset = queryset.filter(content_type=ct, object_id=object_id)
            except ContentType.DoesNotExist:
                pass
        
        return queryset


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    """
    Dashboard widget management
    """
    queryset = DashboardWidget.objects.select_related('created_by').all()
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['widget_type', 'is_public', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Show user's own widgets + public widgets + shared widgets
        queryset = queryset.filter(
            models.Q(created_by=user) |
            models.Q(is_public=True) |
            models.Q(shared_with_users=user)
        ).distinct()
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Get widget data"""
        widget = self.get_object()
        
        # Check cache first
        cache_entry = WidgetDataCache.objects.filter(
            widget=widget,
            user=request.user,
            expires_at__gt=timezone.now()
        ).first()
        
        if cache_entry:
            cache_entry.hit_count += 1
            cache_entry.save(update_fields=['hit_count'])
            return Response({
                'data': cache_entry.data,
                'cached': True,
                'cached_at': cache_entry.cached_at
            })
        
        # Fetch fresh data based on data_source
        data = self._fetch_widget_data(widget, request.user)
        
        # Cache the data
        expires_at = timezone.now() + timedelta(seconds=widget.refresh_interval)
        WidgetDataCache.objects.create(
            widget=widget,
            user=request.user,
            data=data,
            query_params=widget.query_params,
            expires_at=expires_at
        )
        
        return Response({
            'data': data,
            'cached': False
        })
    
    def _fetch_widget_data(self, widget, user):
        """Fetch data for widget based on data_source"""
        # This is a simplified implementation
        # In production, route to appropriate data source
        
        if widget.data_source == 'leads_count':
            from lead_management.models import Lead
            return {'value': Lead.objects.count(), 'label': 'Total Leads'}
        
        elif widget.data_source == 'opportunities_value':
            from opportunity_management.models import Opportunity
            from django.db.models import Sum
            total = Opportunity.objects.aggregate(total=Sum('amount'))['total'] or 0
            return {'value': float(total), 'label': 'Pipeline Value'}
        
        elif widget.data_source == 'tasks_overdue':
            from task_management.models import Task
            count = Task.objects.filter(
                due_date__lt=timezone.now(),
                status__in=['pending', 'in_progress']
            ).count()
            return {'value': count, 'label': 'Overdue Tasks'}
        
        # Default empty data
        return {}


class UserDashboardViewSet(viewsets.ModelViewSet):
    """
    User dashboard management
    """
    queryset = UserDashboard.objects.prefetch_related('widget_placements__widget').all()
    serializer_class = UserDashboardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set as default dashboard"""
        dashboard = self.get_object()
        
        # Unset other defaults
        UserDashboard.objects.filter(user=request.user).update(is_default=False)
        
        # Set this as default
        dashboard.is_default = True
        dashboard.save()
        
        return Response({'success': True})
    
    @action(detail=True, methods=['post'])
    def add_widget(self, request, pk=None):
        """Add widget to dashboard"""
        dashboard = self.get_object()
        widget_id = request.data.get('widget_id')
        
        try:
            widget = DashboardWidget.objects.get(id=widget_id)
        except DashboardWidget.DoesNotExist:
            return Response(
                {'error': 'Widget not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create placement
        placement = DashboardWidgetPlacement.objects.create(
            dashboard=dashboard,
            widget=widget,
            row=request.data.get('row', 0),
            column=request.data.get('column', 0),
            width=request.data.get('width', 2),
            height=request.data.get('height', 1)
        )
        
        serializer = DashboardWidgetPlacementSerializer(placement)
        return Response(serializer.data)
    
    @action(detail=True, methods=['delete'])
    def remove_widget(self, request, pk=None):
        """Remove widget from dashboard"""
        dashboard = self.get_object()
        widget_id = request.data.get('widget_id')
        
        DashboardWidgetPlacement.objects.filter(
            dashboard=dashboard,
            widget_id=widget_id
        ).delete()
        
        return Response({'success': True})


from django.db import models
