"""
Settings API Views
Views for user preferences, notification settings, export jobs, RBAC, and analytics
"""

import logging
from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .settings_models import (
    ExportJob,
    NotificationPreference,
    NotificationTypeSetting,
    UserPreference,
    UserRole,
    UserRoleAssignment,
)
from .settings_serializers import (
    ExportJobCreateSerializer,
    ExportJobSerializer,
    NotificationPreferenceSerializer,
    NotificationPreferenceUpdateSerializer,
    NotificationTypeSettingSerializer,
    UserPreferenceSerializer,
    UserRoleAssignmentSerializer,
    UserRoleSerializer,
)

logger = logging.getLogger(__name__)


# ==================== User Preferences ViewSet ====================

class UserPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user preferences
    """
    serializer_class = UserPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserPreference.objects.filter(user=self.request.user)

    def list(self, request):
        """Get current user's preferences"""
        preferences = UserPreference.get_or_create_for_user(request.user)
        serializer = self.get_serializer(preferences)
        return Response(serializer.data)

    def create(self, request):
        """Create or update preferences"""
        preferences = UserPreference.get_or_create_for_user(request.user)
        serializer = self.get_serializer(preferences, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def update_preferences(self, request):
        """Update specific preferences"""
        preferences = UserPreference.get_or_create_for_user(request.user)
        serializer = self.get_serializer(preferences, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def reset_to_defaults(self, request):
        """Reset preferences to defaults"""
        preferences = UserPreference.get_or_create_for_user(request.user)

        # Reset to default values
        preferences.theme = 'system'
        preferences.accent_color = '#3b82f6'
        preferences.font_size = 14
        preferences.compact_mode = False
        preferences.animations_enabled = True
        preferences.high_contrast = False
        preferences.default_view = 'overview'
        preferences.sidebar_collapsed = False
        preferences.show_welcome_message = True
        preferences.auto_refresh_enabled = True
        preferences.auto_refresh_interval = 30
        preferences.dashboard_layout = {}
        preferences.share_activity_with_team = True
        preferences.show_online_status = True
        preferences.allow_mentions = True
        preferences.data_export_enabled = True
        preferences.sound_enabled = True
        preferences.sound_volume = 70
        preferences.keyboard_shortcuts = preferences.get_default_keyboard_shortcuts()
        preferences.save()

        serializer = self.get_serializer(preferences)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def update_layout(self, request):
        """Update dashboard layout"""
        preferences = UserPreference.get_or_create_for_user(request.user)
        preferences.dashboard_layout = request.data.get('layout', {})
        preferences.save(update_fields=['dashboard_layout', 'updated_at'])
        return Response({'status': 'success', 'layout': preferences.dashboard_layout})

    @action(detail=False, methods=['patch'])
    def update_shortcuts(self, request):
        """Update keyboard shortcuts"""
        preferences = UserPreference.get_or_create_for_user(request.user)
        preferences.keyboard_shortcuts = request.data.get('shortcuts', {})
        preferences.save(update_fields=['keyboard_shortcuts', 'updated_at'])
        return Response({'status': 'success', 'shortcuts': preferences.keyboard_shortcuts})


# ==================== Notification Preferences ViewSet ====================

class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notification preferences
    """
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)

    def get_or_create_preferences(self):
        """Get or create notification preferences for current user"""
        prefs, created = NotificationPreference.objects.get_or_create(user=self.request.user)
        if created:
            # Create default type settings
            self.create_default_type_settings(prefs)
        return prefs

    def create_default_type_settings(self, prefs):
        """Create default notification type settings"""
        default_settings = [
            # Deals
            {'notification_type': 'deal_stage_change', 'priority': 'high'},
            {'notification_type': 'deal_won', 'priority': 'high'},
            {'notification_type': 'deal_lost', 'priority': 'medium'},
            {'notification_type': 'deal_assigned', 'priority': 'high'},
            # Tasks
            {'notification_type': 'task_due_soon', 'priority': 'high'},
            {'notification_type': 'task_overdue', 'priority': 'high', 'sms_enabled': True},
            {'notification_type': 'task_assigned', 'priority': 'medium'},
            # Social
            {'notification_type': 'mention', 'priority': 'high'},
            {'notification_type': 'comment', 'priority': 'medium', 'email_enabled': False},
            {'notification_type': 'team_activity', 'priority': 'low', 'email_enabled': False, 'push_enabled': False},
            # System
            {'notification_type': 'system_updates', 'priority': 'low', 'push_enabled': False},
            {'notification_type': 'security_alerts', 'priority': 'high', 'sms_enabled': True},
            # AI
            {'notification_type': 'ai_recommendations', 'priority': 'medium', 'email_enabled': False},
            {'notification_type': 'ai_insights', 'priority': 'low', 'push_enabled': False},
        ]

        for setting in default_settings:
            NotificationTypeSetting.objects.create(
                notification_preference=prefs,
                **setting
            )

    def list(self, request):
        """Get current user's notification preferences"""
        prefs = self.get_or_create_preferences()
        serializer = self.get_serializer(prefs)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def update_preferences(self, request):
        """Update notification preferences"""
        prefs = self.get_or_create_preferences()
        serializer = NotificationPreferenceUpdateSerializer(prefs, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(NotificationPreferenceSerializer(prefs).data)

    @action(detail=False, methods=['patch'])
    def update_channel(self, request):
        """Toggle a notification channel"""
        prefs = self.get_or_create_preferences()
        channel = request.data.get('channel')
        enabled = request.data.get('enabled')

        if channel in ['email', 'push', 'in_app', 'sms']:
            setattr(prefs, f'{channel.replace("-", "_")}_enabled', enabled)
            prefs.save()
            return Response({'status': 'success', 'channel': channel, 'enabled': enabled})

        return Response({'error': 'Invalid channel'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'])
    def update_type_setting(self, request):
        """Update settings for a specific notification type"""
        prefs = self.get_or_create_preferences()
        notification_type = request.data.get('notification_type')

        setting, created = NotificationTypeSetting.objects.get_or_create(
            notification_preference=prefs,
            notification_type=notification_type
        )

        serializer = NotificationTypeSettingSerializer(setting, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def update_quiet_hours(self, request):
        """Update quiet hours settings"""
        prefs = self.get_or_create_preferences()

        prefs.quiet_hours_enabled = request.data.get('enabled', prefs.quiet_hours_enabled)
        prefs.quiet_hours_start = request.data.get('start_time', prefs.quiet_hours_start)
        prefs.quiet_hours_end = request.data.get('end_time', prefs.quiet_hours_end)
        prefs.quiet_hours_days = request.data.get('days', prefs.quiet_hours_days)
        prefs.save()

        return Response({
            'enabled': prefs.quiet_hours_enabled,
            'start_time': str(prefs.quiet_hours_start),
            'end_time': str(prefs.quiet_hours_end),
            'days': prefs.quiet_hours_days,
        })

    @action(detail=False, methods=['patch'])
    def update_digest(self, request):
        """Update digest settings"""
        prefs = self.get_or_create_preferences()

        prefs.digest_enabled = request.data.get('enabled', prefs.digest_enabled)
        prefs.digest_frequency = request.data.get('frequency', prefs.digest_frequency)
        prefs.digest_time = request.data.get('time', prefs.digest_time)
        prefs.digest_include_ai = request.data.get('include_ai', prefs.digest_include_ai)
        prefs.digest_include_metrics = request.data.get('include_metrics', prefs.digest_include_metrics)
        prefs.save()

        return Response({
            'enabled': prefs.digest_enabled,
            'frequency': prefs.digest_frequency,
            'time': str(prefs.digest_time),
            'include_ai': prefs.digest_include_ai,
            'include_metrics': prefs.digest_include_metrics,
        })


# ==================== Export Jobs ViewSet ====================

class ExportJobViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing data export jobs
    """
    serializer_class = ExportJobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ExportJob.objects.filter(user=self.request.user)

    def create(self, request):
        """Create a new export job"""
        serializer = ExportJobCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job = ExportJob.objects.create(
            user=request.user,
            **serializer.validated_data
        )

        # In production, queue a Celery task here
        # For now, mark as processing immediately
        job.mark_processing()

        # Trigger async processing
        # process_export_job.delay(job.id)

        return Response(
            ExportJobSerializer(job, context={'request': request}).data,
            status=status.HTTP_202_ACCEPTED
        )

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get export job status"""
        job = self.get_object()
        return Response({
            'id': job.id,
            'status': job.status,
            'progress': job.progress,
            'error': job.error_message,
        })

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download export file"""
        job = self.get_object()

        if job.status != 'completed':
            return Response(
                {'error': 'Export not yet completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if job.expires_at and job.expires_at < timezone.now():
            return Response(
                {'error': 'Export has expired'},
                status=status.HTTP_410_GONE
            )

        # In production, return file from storage
        # For now, generate sample data
        from .export_views import DataExportService

        service = DataExportService(request.user, {
            'entities': job.entities,
            'date_range': job.date_range,
            'include_archived': job.include_archived,
            'include_deleted': job.include_deleted,
        })

        data = service.export_all()

        if job.format == 'json':
            import json

            from django.http import HttpResponse
            response = HttpResponse(
                json.dumps(data, indent=2, default=str),
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="export_{job.id}.json"'
            return response
        else:
            from django.http import HttpResponse
            response = HttpResponse(
                service.to_csv(data),
                content_type='text/csv'
            )
            response['Content-Disposition'] = f'attachment; filename="export_{job.id}.csv"'
            return response

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get export history"""
        jobs = self.get_queryset().order_by('-created_at')[:20]
        serializer = ExportJobSerializer(jobs, many=True, context={'request': request})
        return Response({'exports': serializer.data})

    @action(detail=True, methods=['delete'])
    def cancel(self, request, pk=None):
        """Cancel a pending export job"""
        job = self.get_object()

        if job.status in ['pending', 'processing']:
            job.mark_failed('Cancelled by user')
            return Response({'status': 'cancelled'})

        return Response(
            {'error': 'Cannot cancel completed or failed jobs'},
            status=status.HTTP_400_BAD_REQUEST
        )


# ==================== User Roles ViewSet ====================

class UserRoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user roles
    """
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserRole.objects.all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_system_role:
            return Response(
                {'error': 'Cannot delete system roles'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def initialize_defaults(self, request):
        """Initialize default system roles"""
        if not request.user.is_staff:
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

        UserRole.create_default_roles()
        roles = UserRole.objects.all()
        serializer = self.get_serializer(roles, many=True)
        return Response({'roles': serializer.data, 'message': 'Default roles initialized'})


# ==================== User Role Assignments ViewSet ====================

class UserRoleAssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user role assignments
    """
    serializer_class = UserRoleAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Admins can see all assignments
        if user.is_staff:
            return UserRoleAssignment.objects.all()

        # Users can only see their own assignments
        return UserRoleAssignment.objects.filter(user=user)

    def create(self, request):
        """Assign a role to a user"""
        if not request.user.is_staff:
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(assigned_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def my_roles(self, request):
        """Get current user's roles and permissions"""
        assignments = UserRoleAssignment.objects.filter(user=request.user).select_related('role')

        roles = [a.role for a in assignments]
        permissions = set()
        for role in roles:
            permissions.update(role.permissions)

        highest_level = max([r.level for r in roles]) if roles else 0

        return Response({
            'user_id': request.user.id,
            'email': request.user.email,
            'name': request.user.get_full_name() or request.user.username,
            'roles': UserRoleSerializer(roles, many=True).data,
            'permissions': list(permissions),
            'is_admin': request.user.is_staff or highest_level >= 4,
            'highest_role_level': highest_level,
        })

    @action(detail=False, methods=['post'])
    def check_permission(self, request):
        """Check if current user has a specific permission"""
        permission = request.data.get('permission')

        if not permission:
            return Response({'error': 'Permission required'}, status=status.HTTP_400_BAD_REQUEST)

        assignments = UserRoleAssignment.objects.filter(user=request.user).select_related('role')

        for assignment in assignments:
            if permission in assignment.role.permissions:
                return Response({'has_permission': True})

        # Also check if user is admin
        if request.user.is_staff:
            return Response({'has_permission': True})

        return Response({'has_permission': False})


# ==================== Analytics API View ====================

class AnalyticsDashboardView(APIView):
    """
    API View for admin analytics dashboard
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get complete analytics dashboard data"""
        time_range = request.query_params.get('range', 'year')

        # Calculate date range
        now = timezone.now()
        if time_range == 'week':
            start_date = now - timedelta(days=7)
        elif time_range == 'month':
            start_date = now - timedelta(days=30)
        elif time_range == 'quarter':
            start_date = now - timedelta(days=90)
        else:  # year
            start_date = now - timedelta(days=365)

        previous_start = start_date - (now - start_date)

        # Get analytics data
        overview = self._get_overview(start_date, now, previous_start)
        revenue_by_month = self._get_revenue_by_month(start_date, now)
        deals_by_stage = self._get_deals_by_stage()
        team_performance = self._get_team_performance(start_date, now)
        funnel = self._get_funnel_data()
        lead_sources = self._get_lead_sources()

        return Response({
            'overview': overview,
            'revenue_by_month': revenue_by_month,
            'deals_by_stage': deals_by_stage,
            'team_performance': team_performance,
            'funnel': funnel,
            'lead_sources': lead_sources,
        })

    def _get_overview(self, start_date, end_date, previous_start):
        """Get overview metrics"""
        try:
            from contact_management.models import Contact
            from opportunity_management.models import Opportunity

            # Current period
            current_deals = Opportunity.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date,
                status='won'
            )

            total_revenue = current_deals.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            total_deals = current_deals.count()

            # Previous period for comparison
            previous_deals = Opportunity.objects.filter(
                created_at__gte=previous_start,
                created_at__lt=start_date,
                status='won'
            )
            previous_revenue = previous_deals.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            previous_deals_count = previous_deals.count()

            # Calculate growth
            revenue_growth = 0
            if previous_revenue > 0:
                revenue_growth = float((total_revenue - previous_revenue) / previous_revenue * 100)

            deals_growth = 0
            if previous_deals_count > 0:
                deals_growth = float((total_deals - previous_deals_count) / previous_deals_count * 100)

            # Conversion rate
            total_opportunities = Opportunity.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            ).count()
            conversion_rate = (total_deals / total_opportunities * 100) if total_opportunities > 0 else 0

            # Active leads
            active_leads = Contact.objects.filter(
                lead_status='active',
                updated_at__gte=start_date
            ).count()

            return {
                'total_revenue': float(total_revenue),
                'revenue_growth': round(revenue_growth, 1),
                'total_deals': total_deals,
                'deals_growth': round(deals_growth, 1),
                'conversion_rate': round(conversion_rate, 1),
                'conversion_growth': 5.2,  # Mock
                'active_leads': active_leads,
                'leads_growth': -3.8,  # Mock
            }
        except ImportError:
            return self._mock_overview()

    def _mock_overview(self):
        """Return mock overview data"""
        return {
            'total_revenue': 1250750,
            'revenue_growth': 18.5,
            'total_deals': 234,
            'deals_growth': 12.3,
            'conversion_rate': 24.5,
            'conversion_growth': 5.2,
            'active_leads': 1567,
            'leads_growth': -3.8,
        }

    def _get_revenue_by_month(self, start_date, end_date):
        """Get revenue by month"""
        try:
            from opportunity_management.models import Opportunity

            monthly_data = Opportunity.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date,
                status='won'
            ).annotate(
                month=TruncMonth('closed_at')
            ).values('month').annotate(
                revenue=Sum('amount'),
                deals_count=Count('id')
            ).order_by('month')

            return [
                {
                    'month': d['month'].strftime('%b %Y') if d['month'] else 'Unknown',
                    'revenue': float(d['revenue'] or 0),
                    'deals_count': d['deals_count'],
                }
                for d in monthly_data
            ]
        except ImportError:
            return self._mock_revenue_by_month()

    def _mock_revenue_by_month(self):
        """Return mock monthly revenue"""
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return [
            {'month': m, 'revenue': 85000 + i * 8000, 'deals_count': 15 + i}
            for i, m in enumerate(months)
        ]

    def _get_deals_by_stage(self):
        """Get deals by stage"""
        try:
            from opportunity_management.models import Opportunity

            stage_data = Opportunity.objects.filter(
                status='open'
            ).values('stage').annotate(
                count=Count('id'),
                value=Sum('amount')
            )

            return [
                {
                    'stage': d['stage'],
                    'count': d['count'],
                    'value': float(d['value'] or 0),
                }
                for d in stage_data
            ]
        except ImportError:
            return self._mock_deals_by_stage()

    def _mock_deals_by_stage(self):
        """Return mock deals by stage"""
        return [
            {'stage': 'Prospecting', 'count': 145, 'value': 1450000},
            {'stage': 'Qualification', 'count': 98, 'value': 980000},
            {'stage': 'Proposal', 'count': 67, 'value': 670000},
            {'stage': 'Negotiation', 'count': 45, 'value': 450000},
            {'stage': 'Closed Won', 'count': 234, 'value': 2340000},
            {'stage': 'Closed Lost', 'count': 89, 'value': 890000},
        ]

    def _get_team_performance(self, start_date, end_date):
        """Get team member performance"""
        try:
            from django.contrib.auth import get_user_model

            from activity_feed.models import Activity
            from opportunity_management.models import Opportunity

            User = get_user_model()

            team_data = []
            for user in User.objects.filter(is_active=True)[:10]:
                deals = Opportunity.objects.filter(
                    owner=user,
                    created_at__gte=start_date,
                    status='won'
                )

                activities = Activity.objects.filter(
                    actor=user,
                    created_at__gte=start_date
                ).count()

                team_data.append({
                    'id': user.id,
                    'name': user.get_full_name() or user.username,
                    'avatar': None,
                    'deals_count': deals.count(),
                    'deals_value': float(deals.aggregate(total=Sum('amount'))['total'] or 0),
                    'activities_count': activities,
                    'conversion_rate': 25.0,  # Mock
                    'trend': 10.0,  # Mock
                })

            return sorted(team_data, key=lambda x: x['deals_value'], reverse=True)
        except ImportError:
            return self._mock_team_performance()

    def _mock_team_performance(self):
        """Return mock team performance"""
        return [
            {'id': 1, 'name': 'Alex Chen', 'avatar': None, 'deals_count': 45, 'deals_value': 256000, 'activities_count': 234, 'conversion_rate': 32, 'trend': 15},
            {'id': 2, 'name': 'Sarah Johnson', 'avatar': None, 'deals_count': 38, 'deals_value': 198000, 'activities_count': 189, 'conversion_rate': 28, 'trend': 8},
            {'id': 3, 'name': 'Mike Wilson', 'avatar': None, 'deals_count': 35, 'deals_value': 175000, 'activities_count': 210, 'conversion_rate': 25, 'trend': -3},
            {'id': 4, 'name': 'Emily Davis', 'avatar': None, 'deals_count': 32, 'deals_value': 165000, 'activities_count': 156, 'conversion_rate': 27, 'trend': 12},
            {'id': 5, 'name': 'James Brown', 'avatar': None, 'deals_count': 28, 'deals_value': 142000, 'activities_count': 178, 'conversion_rate': 22, 'trend': -5},
        ]

    def _get_funnel_data(self):
        """Get sales funnel data"""
        return [
            {'stage': 'Website Visits', 'count': 10000, 'conversion_rate': 100},
            {'stage': 'Leads Generated', 'count': 1500, 'conversion_rate': 15},
            {'stage': 'MQLs', 'count': 450, 'conversion_rate': 30},
            {'stage': 'SQLs', 'count': 180, 'conversion_rate': 40},
            {'stage': 'Opportunities', 'count': 90, 'conversion_rate': 50},
            {'stage': 'Customers', 'count': 35, 'conversion_rate': 39},
        ]

    def _get_lead_sources(self):
        """Get lead sources breakdown"""
        return [
            {'source': 'Organic Search', 'count': 350, 'percentage': 35},
            {'source': 'Referral', 'count': 250, 'percentage': 25},
            {'source': 'LinkedIn', 'count': 200, 'percentage': 20},
            {'source': 'Paid Ads', 'count': 120, 'percentage': 12},
            {'source': 'Events', 'count': 80, 'percentage': 8},
        ]
