"""
Dashboard Widgets System
Customizable dashboard widgets for metrics and KPIs
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class DashboardWidget(models.Model):
    """Widget configuration for user dashboards"""
    
    WIDGET_TYPES = [
        ('metric', 'Metric Card'),
        ('chart_line', 'Line Chart'),
        ('chart_bar', 'Bar Chart'),
        ('chart_pie', 'Pie Chart'),
        ('chart_area', 'Area Chart'),
        ('table', 'Data Table'),
        ('funnel', 'Funnel Chart'),
        ('goal', 'Goal Progress'),
        ('leaderboard', 'Leaderboard'),
        ('timeline', 'Activity Timeline'),
        ('map', 'Geographic Map'),
        ('list', 'Recent Items List'),
    ]
    
    SIZE_CHOICES = [
        ('small', 'Small (1x1)'),
        ('medium', 'Medium (2x1)'),
        ('large', 'Large (2x2)'),
        ('wide', 'Wide (4x1)'),
        ('full', 'Full Width (4x2)'),
    ]
    
    REFRESH_INTERVALS = [
        (0, 'Manual'),
        (60, '1 minute'),
        (300, '5 minutes'),
        (900, '15 minutes'),
        (1800, '30 minutes'),
        (3600, '1 hour'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Widget identification
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    widget_type = models.CharField(max_length=30, choices=WIDGET_TYPES)
    
    # Data source
    data_source = models.CharField(max_length=100, help_text="API endpoint or data source identifier")
    query_params = models.JSONField(default=dict, help_text="Parameters for data query")
    
    # Display settings
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, default='medium')
    color_scheme = models.CharField(max_length=50, default='blue')
    icon = models.CharField(max_length=50, blank=True, help_text="Icon identifier")
    
    # Chart-specific settings
    chart_config = models.JSONField(default=dict, help_text="Chart.js or similar config")
    
    # Data formatting
    value_format = models.CharField(max_length=50, default='number', help_text="number, currency, percentage, etc.")
    value_prefix = models.CharField(max_length=10, blank=True, help_text="e.g., $")
    value_suffix = models.CharField(max_length=10, blank=True, help_text="e.g., %")
    
    # Refresh settings
    refresh_interval = models.IntegerField(choices=REFRESH_INTERVALS, default=300)
    last_refreshed_at = models.DateTimeField(null=True, blank=True)
    
    # Permissions
    is_public = models.BooleanField(default=False, help_text="Available to all users")
    shared_with_users = models.ManyToManyField(User, related_name='shared_widgets', blank=True)
    shared_with_roles = models.JSONField(default=list, blank=True, help_text="Role IDs that can view this widget")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_widgets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'crm_dashboard_widgets'
        verbose_name = 'Dashboard Widget'
        verbose_name_plural = 'Dashboard Widgets'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class UserDashboard(models.Model):
    """User's personalized dashboard configuration"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboards')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Layout
    layout_config = models.JSONField(default=dict, help_text="Grid layout configuration")
    
    # Default dashboard
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_user_dashboards'
        verbose_name = 'User Dashboard'
        verbose_name_plural = 'User Dashboards'
        ordering = ['-is_default', 'name']
        unique_together = [['user', 'name']]
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class DashboardWidgetPlacement(models.Model):
    """Widget placement on a specific dashboard"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    dashboard = models.ForeignKey(UserDashboard, on_delete=models.CASCADE, related_name='widget_placements')
    widget = models.ForeignKey(DashboardWidget, on_delete=models.CASCADE)
    
    # Position in grid
    row = models.IntegerField(default=0)
    column = models.IntegerField(default=0)
    width = models.IntegerField(default=2, help_text="Grid columns")
    height = models.IntegerField(default=1, help_text="Grid rows")
    
    # Display order
    order = models.IntegerField(default=0)
    
    # Widget overrides (optional)
    custom_title = models.CharField(max_length=200, blank=True)
    custom_query_params = models.JSONField(default=dict, blank=True)
    
    is_visible = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_dashboard_widget_placements'
        verbose_name = 'Widget Placement'
        verbose_name_plural = 'Widget Placements'
        ordering = ['order', 'row', 'column']
        unique_together = [['dashboard', 'widget']]
    
    def __str__(self):
        return f"{self.widget.name} on {self.dashboard.name}"


class WidgetDataCache(models.Model):
    """Cache widget data to improve performance"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    widget = models.ForeignKey(DashboardWidget, on_delete=models.CASCADE, related_name='cached_data')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, help_text="User-specific cache")
    
    # Cached data
    data = models.JSONField()
    query_params = models.JSONField(default=dict, help_text="Params used to generate this cache")
    
    # Cache metadata
    cached_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    hit_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'crm_widget_data_cache'
        verbose_name = 'Widget Data Cache'
        verbose_name_plural = 'Widget Data Caches'
        indexes = [
            models.Index(fields=['widget', 'user', 'expires_at']),
        ]
    
    def __str__(self):
        return f"Cache for {self.widget.name}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
