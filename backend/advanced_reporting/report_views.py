"""
Custom Report Builder Views
"""

from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .report_models import (
    DataSource,
    ReportDashboard,
    ReportFolder,
    ReportSubscription,
    ReportTemplate,
    ReportWidget,
    SavedReport,
    ScheduledReport,
)
from .report_serializers import (
    AddDashboardWidgetSerializer,
    CloneReportSerializer,
    CreateDashboardSerializer,
    CreateReportSerializer,
    CreateScheduleSerializer,
    CreateWidgetSerializer,
    DataSourceSerializer,
    ExecuteReportSerializer,
    ExportReportSerializer,
    ReportDashboardListSerializer,
    ReportDashboardSerializer,
    ReportFolderSerializer,
    ReportSubscriptionSerializer,
    ReportTemplateListSerializer,
    ReportTemplateSerializer,
    ReportWidgetSerializer,
    SavedReportListSerializer,
    SavedReportSerializer,
    ScheduledReportSerializer,
    ShareDashboardSerializer,
    UpdateLayoutSerializer,
)
from .report_services import (
    DashboardService,
    DataSourceService,
    ReportBuilderService,
    ScheduleService,
)


class ReportTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for report templates"""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return ReportTemplateListSerializer
        return ReportTemplateSerializer

    def get_queryset(self):
        queryset = ReportTemplate.objects.filter(
            Q(user=self.request.user) |
            Q(visibility='organization') |
            Q(visibility='public')
        )

        # Filter by folder
        folder = self.request.query_params.get('folder')
        if folder:
            queryset = queryset.filter(folder=folder)

        # Filter by type
        report_type = self.request.query_params.get('type')
        if report_type:
            queryset = queryset.filter(report_type=report_type)

        # Filter by data source
        data_source = self.request.query_params.get('data_source')
        if data_source:
            queryset = queryset.filter(data_source=data_source)

        # Favorites only
        if self.request.query_params.get('favorites') == 'true':
            queryset = queryset.filter(is_favorite=True)

        return queryset.order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def create_report(self, request):
        """Create a new report with full configuration"""
        serializer = CreateReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ReportBuilderService(request.user)
        result = service.create_report(
            name=serializer.validated_data['name'],
            report_type=serializer.validated_data['report_type'],
            data_source=serializer.validated_data['data_source'],
            config=serializer.validated_data
        )

        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a report"""
        serializer = ExecuteReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ReportBuilderService(request.user)
        result = service.execute_report(
            report_id=pk,
            parameters=serializer.validated_data.get('parameters')
        )

        return Response(result)

    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        """Clone a report"""
        serializer = CloneReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ReportBuilderService(request.user)
        result = service.clone_report(
            report_id=pk,
            new_name=serializer.validated_data['new_name']
        )

        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Toggle favorite status"""
        report = self.get_object()
        report.is_favorite = not report.is_favorite
        report.save(update_fields=['is_favorite'])

        return Response({'is_favorite': report.is_favorite})

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recently viewed reports"""
        reports = self.get_queryset().filter(
            last_viewed_at__isnull=False
        ).order_by('-last_viewed_at')[:10]

        return Response(ReportTemplateListSerializer(reports, many=True).data)


class ReportWidgetViewSet(viewsets.ModelViewSet):
    """ViewSet for report widgets"""

    serializer_class = ReportWidgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        report_id = self.request.query_params.get('report_id')
        if report_id:
            return ReportWidget.objects.filter(report_id=report_id)
        return ReportWidget.objects.filter(report__user=self.request.user)

    @action(detail=False, methods=['post'])
    def create_widget(self, request):
        """Create a widget for a report"""
        serializer = CreateWidgetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report_id = request.data.get('report_id')
        if not report_id:
            return Response(
                {'error': 'report_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        widget = ReportWidget.objects.create(
            report_id=report_id,
            name=serializer.validated_data['name'],
            widget_type=serializer.validated_data['widget_type'],
            data_source=serializer.validated_data['data_source'],
            query=serializer.validated_data.get('query', {}),
            aggregation=serializer.validated_data.get('aggregation', ''),
            config=serializer.validated_data.get('config', {}),
            position_x=serializer.validated_data.get('position_x', 0),
            position_y=serializer.validated_data.get('position_y', 0),
            width=serializer.validated_data.get('width', 4),
            height=serializer.validated_data.get('height', 3)
        )

        return Response(
            ReportWidgetSerializer(widget).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def preview(self, request, pk=None):
        """Preview widget data"""
        widget = self.get_object()

        # Execute widget query
        from .report_services import ReportQueryBuilder

        query_builder = ReportQueryBuilder(
            data_source=widget.data_source,
            columns=[],
            filters=[],
            grouping=[],
            sorting=[],
            parameters=request.data.get('parameters', {})
        )

        data = query_builder.execute()

        return Response({
            'widget_id': str(widget.id),
            'widget_type': widget.widget_type,
            'data': data
        })


class SavedReportViewSet(viewsets.ModelViewSet):
    """ViewSet for saved/executed reports"""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return SavedReportListSerializer
        return SavedReportSerializer

    def get_queryset(self):
        return SavedReport.objects.filter(
            user=self.request.user
        ).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """Export a saved report"""
        serializer = ExportReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ReportBuilderService(request.user)
        result = service.export_report(
            saved_report_id=pk,
            export_format=serializer.validated_data['format']
        )

        return Response(result)

    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Get report data only"""
        saved = self.get_object()

        if saved.status != 'completed':
            return Response(
                {'error': f'Report status: {saved.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(saved.result_data)


class ScheduledReportViewSet(viewsets.ModelViewSet):
    """ViewSet for scheduled reports"""

    serializer_class = ScheduledReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ScheduledReport.objects.filter(
            user=self.request.user
        ).order_by('-created_at')

    @action(detail=False, methods=['post'])
    def create_schedule(self, request):
        """Create a new schedule"""
        serializer = CreateScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ScheduleService(request.user)
        result = service.create_schedule(
            report_id=str(serializer.validated_data['report_id']),
            schedule_config=serializer.validated_data
        )

        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def run_now(self, request, pk=None):
        """Run a scheduled report immediately"""
        service = ScheduleService(request.user)
        result = service.run_scheduled_report(pk)

        return Response(result)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle schedule active status"""
        schedule = self.get_object()
        schedule.is_active = not schedule.is_active
        schedule.save(update_fields=['is_active'])

        return Response({'is_active': schedule.is_active})

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming scheduled runs"""
        schedules = self.get_queryset().filter(
            is_active=True,
            next_run_at__isnull=False
        ).order_by('next_run_at')[:10]

        return Response([
            {
                'id': str(s.id),
                'name': s.name,
                'next_run_at': s.next_run_at.isoformat() if s.next_run_at else None,
                'frequency': s.frequency
            }
            for s in schedules
        ])


class ReportDashboardViewSet(viewsets.ModelViewSet):
    """ViewSet for dashboards"""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return ReportDashboardListSerializer
        return ReportDashboardSerializer

    def get_queryset(self):
        return ReportDashboard.objects.filter(
            Q(user=self.request.user) |
            Q(is_public=True) |
            Q(shared_with__contains=[str(self.request.user.id)])
        ).order_by('-updated_at')

    @action(detail=False, methods=['post'])
    def create_dashboard(self, request):
        """Create a new dashboard"""
        serializer = CreateDashboardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = DashboardService(request.user)
        result = service.create_dashboard(
            name=serializer.validated_data['name'],
            config=serializer.validated_data
        )

        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_widget(self, request, pk=None):
        """Add a widget to dashboard"""
        serializer = AddDashboardWidgetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = DashboardService(request.user)
        result = service.add_widget(
            dashboard_id=pk,
            widget_config=serializer.validated_data
        )

        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def update_layout(self, request, pk=None):
        """Update widget layout"""
        serializer = UpdateLayoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = DashboardService(request.user)
        result = service.update_layout(
            dashboard_id=pk,
            widgets=serializer.validated_data['widgets']
        )

        return Response(result)

    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Get dashboard data"""
        filters = request.query_params.dict()

        service = DashboardService(request.user)
        result = service.get_dashboard_data(
            dashboard_id=pk,
            filters=filters
        )

        return Response(result)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share a dashboard"""
        serializer = ShareDashboardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = DashboardService(request.user)
        result = service.share_dashboard(
            dashboard_id=pk,
            share_config=serializer.validated_data
        )

        return Response(result)

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set as default dashboard"""
        # Unset other defaults
        ReportDashboard.objects.filter(
            user=request.user, is_default=True
        ).update(is_default=False)

        dashboard = self.get_object()
        dashboard.is_default = True
        dashboard.save(update_fields=['is_default'])

        return Response({'is_default': True})

    @action(detail=False, methods=['get'])
    def default(self, request):
        """Get default dashboard"""
        dashboard = self.get_queryset().filter(is_default=True).first()

        if not dashboard:
            dashboard = self.get_queryset().first()

        if not dashboard:
            return Response({'error': 'No dashboards found'}, status=404)

        service = DashboardService(request.user)
        result = service.get_dashboard_data(str(dashboard.id))

        return Response(result)


class PublicDashboardView(APIView):
    """View for public/embedded dashboards"""

    permission_classes = [AllowAny]

    def get(self, request, token):
        """Get public dashboard by token"""
        try:
            dashboard = ReportDashboard.objects.get(
                public_token=token,
                is_public=True
            )
        except ReportDashboard.DoesNotExist:
            return Response(
                {'error': 'Dashboard not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        dashboard.view_count += 1
        dashboard.save(update_fields=['view_count'])

        service = DashboardService(dashboard.user)
        result = service.get_dashboard_data(str(dashboard.id))

        return Response(result)


class DataSourceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for data sources"""

    serializer_class = DataSourceSerializer
    permission_classes = [IsAuthenticated]
    queryset = DataSource.objects.filter(is_active=True)

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available data sources"""
        service = DataSourceService()
        sources = service.get_available_sources()

        return Response(sources)

    @action(detail=True, methods=['get'])
    def fields(self, request, pk=None):
        """Get fields for a data source"""
        service = DataSourceService()
        result = service.get_source_fields(pk)

        return Response(result)

    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """Preview data from a source"""
        from .report_services import ReportQueryBuilder

        query_builder = ReportQueryBuilder(
            data_source=pk,
            columns=[],
            filters=[],
            grouping=[],
            sorting=[],
            parameters={'limit': 10}
        )

        data = query_builder.execute()

        return Response(data)


class ReportFolderViewSet(viewsets.ModelViewSet):
    """ViewSet for report folders"""

    serializer_class = ReportFolderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReportFolder.objects.filter(
            user=self.request.user,
            parent__isnull=True  # Top-level folders
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get folder tree"""
        folders = self.get_queryset()
        return Response(ReportFolderSerializer(folders, many=True).data)


class ReportSubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for report subscriptions"""

    serializer_class = ReportSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReportSubscription.objects.filter(
            user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle subscription active status"""
        subscription = self.get_object()
        subscription.is_active = not subscription.is_active
        subscription.save(update_fields=['is_active'])

        return Response({'is_active': subscription.is_active})
