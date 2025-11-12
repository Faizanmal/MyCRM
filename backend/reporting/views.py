from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Dashboard, Report, ReportSchedule, Analytics, KPIMetric, DataExport
from .serializers import (
    DashboardSerializer, ReportSerializer, ReportScheduleSerializer,
    AnalyticsSerializer, KPIMetricSerializer, DataExportSerializer
)

User = get_user_model()


class DashboardViewSet(viewsets.ModelViewSet):
    """Dashboard management viewset"""
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Dashboard.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """Get user's default dashboard"""
        dashboard = self.get_queryset().filter(is_default=True).first()
        if not dashboard:
            dashboard = self.get_queryset().first()
        
        if dashboard:
            return Response(DashboardSerializer(dashboard).data)
        else:
            return Response({'message': 'No dashboard found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set dashboard as default"""
        dashboard = self.get_object()
        
        # Remove default flag from other dashboards
        self.get_queryset().update(is_default=False)
        
        # Set this dashboard as default
        dashboard.is_default = True
        dashboard.save()
        
        return Response(DashboardSerializer(dashboard).data)


class ReportViewSet(viewsets.ModelViewSet):
    """Report management viewset"""
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Users can see their own reports and public reports
        return Report.objects.filter(
            Q(created_by=self.request.user) | Q(is_public=True) | Q(shared_with=self.request.user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """Export report in specified format"""
        report = self.get_object()
        format_type = request.query_params.get('format', 'pdf')
        
        # Here you would implement the actual export logic
        # For now, we'll just return a success message
        
        return Response({
            'message': f'Report exported as {format_type}',
            'report_id': report.id,
            'format': format_type
        })
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share report with other users"""
        report = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        if not user_ids:
            return Response(
                {'error': 'User IDs are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        users = User.objects.filter(id__in=user_ids)
        report.shared_with.add(*users)
        
        return Response({
            'message': f'Report shared with {users.count()} users',
            'shared_with': [user.get_full_name() for user in users]
        })


class ReportScheduleViewSet(viewsets.ModelViewSet):
    """Report schedule management viewset"""
    queryset = ReportSchedule.objects.all()
    serializer_class = ReportScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ReportSchedule.objects.filter(report__created_by=self.request.user)


class AnalyticsViewSet(viewsets.ModelViewSet):
    """Analytics management viewset"""
    queryset = Analytics.objects.all()
    serializer_class = AnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'value']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def dashboard_metrics(self, request):
        """Get dashboard metrics"""
        # Get basic CRM metrics
        from contact_management.models import Contact
        from lead_management.models import Lead
        from opportunity_management.models import Opportunity
        from task_management.models import Task
        
        # Contact metrics
        total_contacts = Contact.objects.count()
        new_contacts_this_month = Contact.objects.filter(
            created_at__month=timezone.now().month,
            created_at__year=timezone.now().year
        ).count()
        
        # Lead metrics
        total_leads = Lead.objects.count()
        converted_leads = Lead.objects.filter(status='converted').count()
        conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
        
        # Opportunity metrics
        total_opportunities = Opportunity.objects.count()
        total_pipeline_value = Opportunity.objects.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Task metrics
        total_tasks = Task.objects.count()
        completed_tasks = Task.objects.filter(status='completed').count()
        overdue_tasks = Task.objects.filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count()
        
        return Response({
            'contacts': {
                'total': total_contacts,
                'new_this_month': new_contacts_this_month
            },
            'leads': {
                'total': total_leads,
                'converted': converted_leads,
                'conversion_rate': round(conversion_rate, 2)
            },
            'opportunities': {
                'total': total_opportunities,
                'pipeline_value': total_pipeline_value
            },
            'tasks': {
                'total': total_tasks,
                'completed': completed_tasks,
                'overdue': overdue_tasks
            }
        })
    
    @action(detail=False, methods=['get'])
    def sales_pipeline(self, request):
        """Get sales pipeline data"""
        from opportunity_management.models import Opportunity
        
        pipeline_data = []
        for stage_choice in Opportunity.STAGE_CHOICES:
            stage_name = stage_choice[0]
            stage_display = stage_choice[1]
            
            opportunities = Opportunity.objects.filter(stage=stage_name)
            count = opportunities.count()
            total_value = opportunities.aggregate(total=Sum('amount'))['total'] or 0
            
            pipeline_data.append({
                'stage': stage_name,
                'stage_display': stage_display,
                'count': count,
                'total_value': total_value
            })
        
        return Response(pipeline_data)
    
    @action(detail=False, methods=['get'])
    def activity_timeline(self, request):
        """Get activity timeline data"""
        from communication_management.models import Communication
        
        # Get communications from last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        communications = Communication.objects.filter(
            communication_date__gte=thirty_days_ago
        ).order_by('communication_date')
        
        # Group by date
        timeline_data = {}
        for comm in communications:
            date_key = comm.communication_date.date().isoformat()
            if date_key not in timeline_data:
                timeline_data[date_key] = {
                    'date': date_key,
                    'communications': 0,
                    'calls': 0,
                    'emails': 0,
                    'meetings': 0
                }
            
            timeline_data[date_key]['communications'] += 1
            if comm.communication_type == 'call':
                timeline_data[date_key]['calls'] += 1
            elif comm.communication_type == 'email':
                timeline_data[date_key]['emails'] += 1
            elif comm.communication_type == 'meeting':
                timeline_data[date_key]['meetings'] += 1
        
        return Response(list(timeline_data.values()))


class KPIMetricViewSet(viewsets.ModelViewSet):
    """KPI metric management viewset"""
    queryset = KPIMetric.objects.all()
    serializer_class = KPIMetricSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return KPIMetric.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DataExportViewSet(viewsets.ModelViewSet):
    """Data export management viewset"""
    queryset = DataExport.objects.all()
    serializer_class = DataExportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DataExport.objects.filter(requested_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        """Download exported data"""
        export = self.get_object()
        
        if export.status != 'completed':
            return Response(
                {'error': 'Export is not ready for download'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Here you would implement the actual download logic
        # For now, we'll just return the file path
        
        return Response({
            'file_path': export.file_path,
            'file_size': export.file_size,
            'record_count': export.record_count
        })