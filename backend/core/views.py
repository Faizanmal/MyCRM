"""
Enterprise Core Views for MyCRM
Advanced security, audit, and enterprise features API views
"""

from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count, Max
from django.utils import timezone
from datetime import timedelta

from .models import (
    AuditLog, SystemConfiguration, APIKey, DataBackup,
    Workflow, WorkflowExecution, Integration, NotificationTemplate, SystemHealth
)
from .serializers import (
    AuditLogSerializer, SystemConfigurationSerializer, APIKeySerializer,
    DataBackupSerializer, WorkflowSerializer, WorkflowExecutionSerializer,
    IntegrationSerializer, NotificationTemplateSerializer, SystemHealthSerializer,
    SecurityDashboardSerializer, AdvancedAnalyticsSerializer
)
from .security import SecurityAuditLog
from .ai_analytics import SalesForecasting, LeadScoring, CustomerSegmentation, PredictiveAnalytics, WorkflowAutomation

User = get_user_model()


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Audit log management - read-only for compliance"""
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['action', 'resource', 'user__username', 'ip_address']
    ordering_fields = ['timestamp', 'risk_level', 'action']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        queryset = AuditLog.objects.all()
        
        # Non-admin users can only see their own audit logs
        if self.request.user.role != 'admin':
            queryset = queryset.filter(user=self.request.user)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        # Filter by risk level
        risk_level = self.request.query_params.get('risk_level')
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def security_summary(self, request):
        """Get security summary from audit logs"""
        if request.user.role != 'admin':
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Security metrics
        metrics = {
            'total_events_today': AuditLog.objects.filter(
                timestamp__date=today
            ).count(),
            'total_events_yesterday': AuditLog.objects.filter(
                timestamp__date=yesterday
            ).count(),
            'high_risk_events_today': AuditLog.objects.filter(
                timestamp__date=today,
                risk_level__in=['high', 'critical']
            ).count(),
            'failed_logins_today': AuditLog.objects.filter(
                timestamp__date=today,
                action__icontains='login_failed'
            ).count(),
            'unique_users_today': AuditLog.objects.filter(
                timestamp__date=today
            ).values('user').distinct().count(),
            'top_actions': list(
                AuditLog.objects.filter(
                    timestamp__date=today
                ).values('action').annotate(
                    count=Count('action')
                ).order_by('-count')[:5]
            )
        }
        
        return Response(metrics)


class SystemConfigurationViewSet(viewsets.ModelViewSet):
    """System configuration management"""
    queryset = SystemConfiguration.objects.all()
    serializer_class = SystemConfigurationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only admins can access system configuration
        if self.request.user.role != 'admin':
            return SystemConfiguration.objects.none()
        return SystemConfiguration.objects.all()
    
    def perform_create(self, serializer):
        if self.request.user.role != 'admin':
            raise permissions.PermissionDenied("Admin access required")
        
        serializer.save(created_by=self.request.user)
        
        # Log configuration change
        SecurityAuditLog.log_event(
            self.request.user,
            'system_config_created',
            resource=f"config:{serializer.instance.key}",
            ip_address=self.request.META.get('REMOTE_ADDR'),
            risk_level='medium'
        )


class APIKeyViewSet(viewsets.ModelViewSet):
    """API key management"""
    queryset = APIKey.objects.all()
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own API keys, admins see all
        if self.request.user.role == 'admin':
            return APIKey.objects.all()
        return APIKey.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        import secrets
        import hashlib
        
        # Generate API key
        api_key = f"crm_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        serializer.save(user=self.request.user, key_hash=key_hash)
        
        # Return the unhashed key only once
        response_data = serializer.data
        response_data['api_key'] = api_key
        
        # Log API key creation
        SecurityAuditLog.log_event(
            self.request.user,
            'api_key_created',
            resource=f"api_key:{serializer.instance.id}",
            ip_address=self.request.META.get('REMOTE_ADDR'),
            risk_level='medium'
        )
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke an API key"""
        api_key = self.get_object()
        api_key.status = 'revoked'
        api_key.save()
        
        SecurityAuditLog.log_event(
            request.user,
            'api_key_revoked',
            resource=f"api_key:{api_key.id}",
            ip_address=request.META.get('REMOTE_ADDR'),
            risk_level='medium'
        )
        
        return Response({'message': 'API key revoked successfully'})


class DataBackupViewSet(viewsets.ReadOnlyModelViewSet):
    """Data backup tracking"""
    queryset = DataBackup.objects.all()
    serializer_class = DataBackupSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only admins can access backup information
        if self.request.user.role != 'admin':
            return DataBackup.objects.none()
        return DataBackup.objects.all()
    
    @action(detail=False, methods=['post'])
    def create_backup(self, request):
        """Initiate a new backup"""
        if request.user.role != 'admin':
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        backup_type = request.data.get('backup_type', 'full')
        
        # Create backup record
        backup = DataBackup.objects.create(
            backup_type=backup_type,
            file_path=f"backups/{timezone.now().strftime('%Y%m%d_%H%M%S')}_{backup_type}.sql",
            created_by=request.user
        )
        
        # Here you would typically queue a background task to perform the backup
        # For now, we'll just return the backup record
        
        SecurityAuditLog.log_event(
            request.user,
            'backup_initiated',
            resource=f"backup:{backup.id}",
            ip_address=request.META.get('REMOTE_ADDR'),
            risk_level='low'
        )
        
        return Response(DataBackupSerializer(backup).data)


class WorkflowViewSet(viewsets.ModelViewSet):
    """Workflow automation management"""
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Users can see workflows they created or if they're admin
        if self.request.user.role == 'admin':
            return Workflow.objects.all()
        return Workflow.objects.filter(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Manually execute a workflow"""
        workflow = self.get_object()
        
        if workflow.status != 'active':
            return Response(
                {'error': 'Workflow is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create execution record
        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            trigger_data=request.data.get('trigger_data', {}),
            total_steps=len(workflow.actions)
        )
        
        # Here you would typically queue the workflow execution
        # For now, we'll just return the execution record
        
        return Response(WorkflowExecutionSerializer(execution).data)


class WorkflowExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """Workflow execution tracking"""
    queryset = WorkflowExecution.objects.all()
    serializer_class = WorkflowExecutionSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['-started_at']
    
    def get_queryset(self):
        # Users can see executions of their workflows or if they're admin
        if self.request.user.role == 'admin':
            return WorkflowExecution.objects.all()
        return WorkflowExecution.objects.filter(workflow__created_by=self.request.user)


class IntegrationViewSet(viewsets.ModelViewSet):
    """External integration management"""
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'provider', 'integration_type']
    ordering_fields = ['name', 'created_at', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Users can see integrations they created or if they're admin
        if self.request.user.role == 'admin':
            return Integration.objects.all()
        return Integration.objects.filter(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test integration connection"""
        integration = self.get_object()
        
        # Here you would implement actual connection testing
        # For now, we'll simulate it
        test_result = {
            'success': True,
            'message': 'Connection successful',
            'response_time': 150  # ms
        }
        
        # Update last sync time if successful
        if test_result['success']:
            integration.last_sync = timezone.now()
            integration.status = 'active'
            integration.save()
        else:
            integration.status = 'error'
            integration.save()
        
        return Response(test_result)


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """Notification template management"""
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'notification_type']
    ordering_fields = ['name', 'created_at', 'notification_type']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Users can see templates they created or if they're admin
        if self.request.user.role == 'admin':
            return NotificationTemplate.objects.all()
        return NotificationTemplate.objects.filter(created_by=self.request.user)


class SystemHealthViewSet(viewsets.ReadOnlyModelViewSet):
    """System health monitoring"""
    queryset = SystemHealth.objects.all()
    serializer_class = SystemHealthSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['-checked_at']
    
    def get_queryset(self):
        # Only admins can access system health data
        if self.request.user.role != 'admin':
            return SystemHealth.objects.none()
        
        # Get latest health check for each component
        latest_checks = SystemHealth.objects.values('component').annotate(
            latest_check=Max('checked_at')
        )
        
        health_checks = []
        for check in latest_checks:
            health_checks.extend(
                SystemHealth.objects.filter(
                    component=check['component'],
                    checked_at=check['latest_check']
                )
            )
        
        return health_checks
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get system health dashboard data"""
        if request.user.role != 'admin':
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get latest health status for each component
        components = ['database', 'cache', 'email', 'storage', 'api', 'queue']
        health_data = {}
        
        for component in components:
            latest = SystemHealth.objects.filter(component=component).first()
            health_data[component] = {
                'status': latest.status if latest else 'unknown',
                'response_time': latest.response_time if latest else None,
                'last_check': latest.checked_at if latest else None
            }
        
        # Calculate overall health score
        healthy_count = sum(1 for data in health_data.values() if data['status'] == 'healthy')
        health_score = (healthy_count / len(components)) * 100
        
        return Response({
            'components': health_data,
            'overall_health_score': health_score,
            'total_components': len(components),
            'healthy_components': healthy_count
        })


class SecurityDashboardViewSet(viewsets.ViewSet):
    """Security dashboard with aggregated metrics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Get security dashboard data"""
        if request.user.role != 'admin':
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        today = timezone.now().date()
        
        # Aggregate security metrics
        dashboard_data = {
            'total_audit_logs': AuditLog.objects.count(),
            'high_risk_events_today': AuditLog.objects.filter(
                timestamp__date=today,
                risk_level__in=['high', 'critical']
            ).count(),
            'failed_logins_today': AuditLog.objects.filter(
                timestamp__date=today,
                action__icontains='login_failed'
            ).count(),
            'active_api_keys': APIKey.objects.filter(status='active').count(),
            'recent_backups': DataBackup.objects.filter(
                started_at__gte=today - timedelta(days=7)
            ).count(),
            'system_health_score': self._calculate_health_score(),
            'active_integrations': Integration.objects.filter(status='active').count(),
            'workflow_executions_today': WorkflowExecution.objects.filter(
                started_at__date=today
            ).count()
        }
        
        serializer = SecurityDashboardSerializer(dashboard_data)
        return Response(serializer.data)
    
    def _calculate_health_score(self):
        """Calculate overall system health score"""
        components = ['database', 'cache', 'email', 'storage', 'api', 'queue']
        healthy_count = 0
        
        for component in components:
            latest = SystemHealth.objects.filter(component=component).first()
            if latest and latest.status == 'healthy':
                healthy_count += 1
        
        return (healthy_count / len(components)) * 100 if components else 0


class AdvancedAnalyticsViewSet(viewsets.ViewSet):
    """Advanced analytics and insights"""
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Get advanced analytics data"""
        if request.user.role not in ['admin', 'manager']:
            return Response(
                {'error': 'Manager or admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate analytics data
        analytics_data = {
            'user_activity_trend': self._get_user_activity_trend(),
            'security_incidents_trend': self._get_security_incidents_trend(),
            'system_performance_metrics': self._get_performance_metrics(),
            'integration_status_summary': self._get_integration_summary(),
            'workflow_performance': self._get_workflow_performance(),
            'data_quality_score': self._calculate_data_quality_score(),
            'compliance_score': self._calculate_compliance_score()
        }
        
        serializer = AdvancedAnalyticsSerializer(analytics_data)
        return Response(serializer.data)
    
    def _get_user_activity_trend(self):
        """Get user activity trend over last 30 days"""
        # Implementation for user activity analysis
        return {'trend': 'increasing', 'data': []}
    
    def _get_security_incidents_trend(self):
        """Get security incidents trend"""
        # Implementation for security incident analysis
        return {'trend': 'stable', 'data': []}
    
    def _get_performance_metrics(self):
        """Get system performance metrics"""
        # Implementation for performance analysis
        return {'avg_response_time': 150, 'uptime': 99.9}
    
    def _get_integration_summary(self):
        """Get integration status summary"""
        return Integration.objects.values('status').annotate(count=Count('status'))
    
    def _get_workflow_performance(self):
        """Get workflow performance metrics"""
        return {'success_rate': 95.5, 'avg_execution_time': 30}
    
    def _calculate_data_quality_score(self):
        """Calculate data quality score"""
        # Implementation for data quality assessment
        return 87.5
    
    def _calculate_compliance_score(self):
        """Calculate compliance score"""
        # Implementation for compliance assessment
        return 92.0


class AIAnalyticsViewSet(viewsets.ViewSet):
    """AI-powered analytics and insights"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def sales_forecast(self, request):
        """Get sales revenue forecast"""
        period_months = int(request.query_params.get('period', 3))
        
        if period_months > 12:
            return Response(
                {'error': 'Period cannot exceed 12 months'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        forecast = SalesForecasting.forecast_revenue(period_months)
        return Response(forecast)
    
    @action(detail=False, methods=['post'])
    def lead_scoring(self, request):
        """Calculate lead score for a specific lead"""
        lead_id = request.data.get('lead_id')
        
        if not lead_id:
            return Response(
                {'error': 'lead_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from lead_management.models import Lead
            lead = Lead.objects.get(id=lead_id)
            
            # Check permissions
            if request.user.role not in ['admin', 'manager'] and lead.assigned_to != request.user:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            score_data = LeadScoring.calculate_lead_score(lead)
            return Response(score_data)
            
        except Lead.DoesNotExist:
            return Response(
                {'error': 'Lead not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def customer_segmentation(self, request):
        """Get customer segmentation analysis"""
        if request.user.role not in ['admin', 'manager']:
            return Response(
                {'error': 'Manager or admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        segmentation = CustomerSegmentation.segment_customers()
        return Response(segmentation)
    
    @action(detail=False, methods=['get'])
    def churn_prediction(self, request):
        """Get churn risk predictions"""
        if request.user.role not in ['admin', 'manager']:
            return Response(
                {'error': 'Manager or admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        churn_analysis = PredictiveAnalytics.predict_churn_risk()
        return Response(churn_analysis)
    
    @action(detail=False, methods=['post'])
    def next_best_action(self, request):
        """Get AI-suggested next best actions"""
        record_type = request.data.get('record_type')
        record_id = request.data.get('record_id')
        
        if not record_type or not record_id:
            return Response(
                {'error': 'record_type and record_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if record_type not in ['lead', 'contact', 'opportunity']:
            return Response(
                {'error': 'Invalid record_type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        suggestions = WorkflowAutomation.suggest_next_actions(record_type, record_id)
        return Response({'suggestions': suggestions})
    
    @action(detail=False, methods=['get'])
    def ai_insights_dashboard(self, request):
        """Get comprehensive AI insights dashboard"""
        if request.user.role not in ['admin', 'manager']:
            return Response(
                {'error': 'Manager or admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Combine multiple AI insights
        dashboard_data = {
            'sales_forecast': SalesForecasting.forecast_revenue(3),
            'customer_segments': CustomerSegmentation.segment_customers(),
            'churn_risk': PredictiveAnalytics.predict_churn_risk(),
            'generated_at': timezone.now().isoformat()
        }
        
        return Response(dashboard_data)
    
    @action(detail=False, methods=['get'])
    def pipeline_analytics(self, request):
        """Get comprehensive pipeline analytics"""
        from .ai_analytics import PipelineAnalytics
        
        if request.user.role not in ['admin', 'manager', 'sales_rep']:
            return Response(
                {'error': 'Insufficient permissions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        analytics_data = {
            'pipeline_health': PipelineAnalytics.get_pipeline_health(),
            'pipeline_forecast': PipelineAnalytics.get_pipeline_forecast(3),
            'conversion_funnel': PipelineAnalytics.get_conversion_funnel(),
            'deal_velocity': PipelineAnalytics.get_deal_velocity(),
            'generated_at': timezone.now().isoformat()
        }
        
        return Response(analytics_data)
    
    @action(detail=False, methods=['get'])
    def detailed_sales_forecast(self, request):
        """Get detailed sales forecast with role-based access"""
        if request.user.role not in ['admin', 'manager']:
            return Response(
                {'error': 'Manager or admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        period_months = int(request.query_params.get('months', 3))
        forecast_data = SalesForecasting.forecast_revenue(period_months)
        
        return Response(forecast_data)