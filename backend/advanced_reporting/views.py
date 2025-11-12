from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg

from .models import Dashboard, DashboardWidget, Report, ReportSchedule, ReportExecution, KPI, KPIValue
from .serializers import (
    DashboardSerializer, DashboardWidgetSerializer, ReportSerializer,
    ReportScheduleSerializer, ReportExecutionSerializer, KPISerializer,
    KPIValueSerializer
)
from .tasks import execute_report_task, calculate_kpi_task


class DashboardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing dashboards
    """
    serializer_class = DashboardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        """Return dashboards owned by user or shared with them"""
        user = self.request.user
        return Dashboard.objects.filter(
            Q(owner=user) | Q(shared_with=user) | Q(is_public=True)
        ).distinct().prefetch_related('widgets', 'shared_with')
    
    def perform_create(self, serializer):
        """Set owner to current user"""
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a dashboard with all widgets"""
        dashboard = self.get_object()
        
        # Create new dashboard
        new_dashboard = Dashboard.objects.create(
            name=f"{dashboard.name} (Copy)",
            description=dashboard.description,
            owner=request.user,
            layout_config=dashboard.layout_config,
            refresh_interval=dashboard.refresh_interval,
            is_default=False
        )
        
        # Copy all widgets
        for widget in dashboard.widgets.all():
            DashboardWidget.objects.create(
                dashboard=new_dashboard,
                widget_type=widget.widget_type,
                title=widget.title,
                position_x=widget.position_x,
                position_y=widget.position_y,
                width=widget.width,
                height=widget.height,
                configuration=widget.configuration,
                data_source=widget.data_source,
                refresh_interval=widget.refresh_interval
            )
        
        serializer = self.get_serializer(new_dashboard)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share dashboard with users"""
        dashboard = self.get_object()
        
        if dashboard.owner != request.user:
            return Response(
                {'error': 'Only dashboard owner can share'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_ids = request.data.get('user_ids', [])
        is_public = request.data.get('is_public', False)
        
        dashboard.is_public = is_public
        if user_ids:
            dashboard.shared_with.set(user_ids)
        dashboard.save()
        
        serializer = self.get_serializer(dashboard)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Get data for all widgets in dashboard"""
        dashboard = self.get_object()
        
        widget_data = []
        for widget in dashboard.widgets.all():
            data = self._get_widget_data(widget, request.user)
            widget_data.append({
                'widget_id': widget.id,
                'widget_type': widget.widget_type,
                'name': widget.name,
                'data': data,
                'updated_at': timezone.now()
            })
        
        return Response(widget_data)
    
    def _get_widget_data(self, widget, user):
        """Get data for a specific widget based on its type and configuration"""
        from contact_management.models import Contact
        from lead_management.models import Lead
        from opportunity_management.models import Opportunity
        
        widget_type = widget.widget_type
        config = widget.query_config or {}
        
        try:
            if widget_type == 'metric':
                # Single metric value
                model_name = config.get('model', 'Lead')
                aggregation = config.get('aggregation', 'count')
                
                if model_name == 'Lead':
                    queryset = Lead.objects.all()
                elif model_name == 'Opportunity':
                    queryset = Opportunity.objects.all()
                elif model_name == 'Contact':
                    queryset = Contact.objects.all()
                else:
                    return {'value': 0}
                
                if aggregation == 'count':
                    value = queryset.count()
                elif aggregation == 'sum':
                    field = config.get('field', 'value')
                    value = queryset.aggregate(total=Sum(field))['total'] or 0
                elif aggregation == 'avg':
                    field = config.get('field', 'value')
                    value = queryset.aggregate(avg=Avg(field))['avg'] or 0
                else:
                    value = queryset.count()
                
                return {'value': value, 'label': config.get('label', 'Total')}
            
            elif widget_type == 'chart':
                # Chart data
                chart_type = config.get('chart_type', 'bar')
                model_name = config.get('model', 'Lead')
                group_by = config.get('group_by', 'status')
                
                if model_name == 'Lead':
                    queryset = Lead.objects.all()
                elif model_name == 'Opportunity':
                    queryset = Opportunity.objects.all()
                elif model_name == 'Contact':
                    queryset = Contact.objects.all()
                else:
                    return {'labels': [], 'values': []}
                
                # Group by field
                data = queryset.values(group_by).annotate(count=Count('id'))
                
                return {
                    'labels': [item[group_by] for item in data],
                    'values': [item['count'] for item in data],
                    'chart_type': chart_type
                }
            
            elif widget_type == 'table':
                # Table data
                model_name = config.get('model', 'Lead')
                limit = config.get('limit', 10)
                
                if model_name == 'Lead':
                    queryset = Lead.objects.all()[:limit]
                    rows = [
                        {
                            'id': obj.id,
                            'name': f"{obj.first_name} {obj.last_name}",
                            'email': obj.email,
                            'status': obj.status
                        }
                        for obj in queryset
                    ]
                elif model_name == 'Opportunity':
                    queryset = Opportunity.objects.all()[:limit]
                    rows = [
                        {
                            'id': obj.id,
                            'name': obj.name,
                            'value': obj.value,
                            'stage': obj.stage
                        }
                        for obj in queryset
                    ]
                else:
                    rows = []
                
                return {'rows': rows}
            
            elif widget_type == 'kpi':
                # KPI widget
                kpi_id = config.get('kpi_id')
                if kpi_id:
                    try:
                        kpi = KPI.objects.get(id=kpi_id)
                        latest_value = kpi.values.order_by('-timestamp').first()
                        
                        return {
                            'name': kpi.name,
                            'value': latest_value.value if latest_value else 0,
                            'unit': kpi.unit,
                            'target': kpi.target_value,
                            'trend': 'up' if latest_value and latest_value.value > kpi.target_value else 'down'
                        }
                    except KPI.DoesNotExist:
                        return {'error': 'KPI not found'}
                return {'error': 'No KPI specified'}
            
            else:
                return {'error': f'Unknown widget type: {widget_type}'}
        
        except Exception as e:
            return {'error': str(e)}


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing dashboard widgets
    """
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return widgets for dashboards user has access to"""
        user = self.request.user
        return DashboardWidget.objects.filter(
            Q(dashboard__owner=user) | Q(dashboard__shared_with=user) | Q(dashboard__is_shared=True)
        ).distinct()
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Get data for a specific widget"""
        widget = self.get_object()
        dashboard_viewset = DashboardViewSet()
        data = dashboard_viewset._get_widget_data(widget, request.user)
        
        return Response({
            'widget_id': widget.id,
            'widget_type': widget.widget_type,
            'name': widget.name,
            'data': data,
            'updated_at': timezone.now()
        })


class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reports
    """
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'report_type']
    ordering_fields = ['name', 'report_type', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return reports created by user or shared with them"""
        user = self.request.user
        return Report.objects.filter(
            Q(owner=user) | Q(shared_with=user) | Q(is_public=True)
        ).distinct().prefetch_related('schedules', 'executions')
    
    def perform_create(self, serializer):
        """Set owner to current user"""
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a report immediately"""
        report = self.get_object()
        
        # Create execution record
        execution = ReportExecution.objects.create(
            report=report,
            executed_by=request.user,
            status='running'
        )
        
        # Trigger async task
        execute_report_task.delay(execution.id)
        
        serializer = ReportExecutionSerializer(execution)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """Create or update schedule for report"""
        report = self.get_object()
        
        schedule_data = request.data
        schedule_data['report'] = report.id
        
        serializer = ReportScheduleSerializer(data=schedule_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """Preview report data without saving execution"""
        report = self.get_object()
        
        # Generate preview data (limited to 100 rows)
        try:
            from .tasks import generate_report_data
            data = generate_report_data(report, limit=100)
            
            return Response({
                'report_id': report.id,
                'name': report.name,
                'preview_data': data,
                'row_count': len(data.get('rows', [])),
                'generated_at': timezone.now()
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReportScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing report schedules
    """
    serializer_class = ReportScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return schedules for reports user has access to"""
        user = self.request.user
        return ReportSchedule.objects.filter(
            Q(report__owner=user) | Q(report__shared_with=user) | Q(report__is_public=True)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a report schedule"""
        schedule = self.get_object()
        schedule.is_active = True
        schedule.save()
        
        serializer = self.get_serializer(schedule)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a report schedule"""
        schedule = self.get_object()
        schedule.is_active = False
        schedule.save()
        
        serializer = self.get_serializer(schedule)
        return Response(serializer.data)


class ReportExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing report execution history
    """
    serializer_class = ReportExecutionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['started_at', 'completed_at', 'status']
    ordering = ['-started_at']
    
    def get_queryset(self):
        """Return executions for reports user has access to"""
        user = self.request.user
        return ReportExecution.objects.filter(
            Q(report__owner=user) | Q(report__shared_with=user) | Q(report__is_public=True) | Q(executed_by=user)
        ).distinct()
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download report output file"""
        execution = self.get_object()
        
        if not execution.file_path:
            return Response(
                {'error': 'No file available for this execution'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # In production, return signed URL or file download
        return Response({
            'file_url': execution.file_path,
            'report_name': execution.report.name,
            'executed_at': execution.completed_at
        })


class KPIViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing KPIs
    """
    serializer_class = KPISerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'metric_type']
    ordering_fields = ['name', 'metric_type', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Return all active KPIs"""
        return KPI.objects.filter(is_active=True).prefetch_related('values')
    
    @action(detail=True, methods=['post'])
    def calculate(self, request, pk=None):
        """Trigger KPI calculation"""
        kpi = self.get_object()
        
        # Trigger async calculation
        calculate_kpi_task.delay(kpi.id)
        
        return Response(
            {'message': 'KPI calculation started'},
            status=status.HTTP_202_ACCEPTED
        )
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get historical KPI values"""
        kpi = self.get_object()
        
        # Get date range from query params
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timezone.timedelta(days=days)
        
        values = kpi.values.filter(timestamp__gte=start_date).order_by('timestamp')
        serializer = KPIValueSerializer(values, many=True)
        
        return Response({
            'kpi_id': kpi.id,
            'name': kpi.name,
            'unit': kpi.unit,
            'values': serializer.data,
            'period_days': days
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of all KPIs with current values"""
        kpis = self.get_queryset()
        
        summary = []
        for kpi in kpis:
            latest_value = kpi.values.order_by('-timestamp').first()
            summary.append({
                'id': kpi.id,
                'name': kpi.name,
                'metric_type': kpi.metric_type,
                'current_value': latest_value.value if latest_value else None,
                'unit': kpi.unit,
                'target_value': kpi.target_value,
                'last_updated': latest_value.timestamp if latest_value else None
            })
        
        return Response(summary)


class KPIValueViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing KPI values
    """
    serializer_class = KPIValueSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Return KPI values"""
        return KPIValue.objects.all()
