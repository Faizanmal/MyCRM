"""
Custom Report Builder Models
Drag-and-drop report designer, real-time dashboards, scheduled reports
"""

import uuid
from django.db import models
from django.conf import settings


class ReportTemplate(models.Model):
    """User-created report templates"""
    
    REPORT_TYPES = [
        ('table', 'Table Report'),
        ('chart', 'Chart Report'),
        ('dashboard', 'Dashboard'),
        ('pivot', 'Pivot Table'),
        ('summary', 'Summary Report'),
        ('detail', 'Detail Report'),
    ]
    
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('team', 'Team'),
        ('organization', 'Organization'),
        ('public', 'Public'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='report_templates'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    
    # Data source configuration
    data_source = models.CharField(max_length=100)  # e.g., 'opportunities', 'contacts'
    base_query = models.JSONField(default=dict)  # Base query/filters
    
    # Visual configuration
    layout_config = models.JSONField(default=dict)  # Drag-and-drop layout
    columns = models.JSONField(default=list)  # Column definitions
    grouping = models.JSONField(default=list)  # Group by fields
    sorting = models.JSONField(default=list)  # Sort configuration
    
    # Filters
    filters = models.JSONField(default=list)  # Filter definitions
    dynamic_filters = models.JSONField(default=list)  # User-adjustable filters
    
    # Chart configuration (for chart reports)
    chart_config = models.JSONField(default=dict, blank=True)
    
    # Calculated fields
    calculated_fields = models.JSONField(default=list)  # Formula fields
    
    # Visibility and sharing
    visibility = models.CharField(
        max_length=20, choices=VISIBILITY_CHOICES, default='private'
    )
    shared_with = models.JSONField(default=list)  # User/team IDs
    
    # Metadata
    is_favorite = models.BooleanField(default=False)
    folder = models.CharField(max_length=255, blank=True)
    tags = models.JSONField(default=list)
    
    # Usage tracking
    view_count = models.IntegerField(default=0)
    last_viewed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'report_templates'
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name


class ReportWidget(models.Model):
    """Individual widgets for dashboard reports"""
    
    WIDGET_TYPES = [
        ('metric', 'Single Metric'),
        ('chart_bar', 'Bar Chart'),
        ('chart_line', 'Line Chart'),
        ('chart_pie', 'Pie Chart'),
        ('chart_donut', 'Donut Chart'),
        ('chart_area', 'Area Chart'),
        ('chart_scatter', 'Scatter Plot'),
        ('table', 'Data Table'),
        ('list', 'List'),
        ('funnel', 'Funnel Chart'),
        ('gauge', 'Gauge'),
        ('heatmap', 'Heatmap'),
        ('map', 'Geographic Map'),
        ('text', 'Text/Markdown'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='widgets'
    )
    name = models.CharField(max_length=255)
    widget_type = models.CharField(max_length=50, choices=WIDGET_TYPES)
    
    # Position and size (grid-based)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=4)  # Grid columns (out of 12)
    height = models.IntegerField(default=3)  # Grid rows
    
    # Data configuration
    data_source = models.CharField(max_length=100)
    query = models.JSONField(default=dict)
    aggregation = models.CharField(max_length=50, blank=True)  # sum, avg, count, etc.
    
    # Visual configuration
    config = models.JSONField(default=dict)  # Widget-specific config
    colors = models.JSONField(default=list)  # Color scheme
    
    # Interactivity
    drill_down_enabled = models.BooleanField(default=False)
    drill_down_config = models.JSONField(default=dict)
    click_action = models.JSONField(default=dict)  # What happens on click
    
    # Refresh settings
    auto_refresh = models.BooleanField(default=False)
    refresh_interval = models.IntegerField(default=300)  # seconds
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'report_widgets'
        ordering = ['position_y', 'position_x']
    
    def __str__(self):
        return f"{self.name} ({self.widget_type})"


class SavedReport(models.Model):
    """Executed/saved report instances"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
        ('html', 'HTML'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.SET_NULL,
        null=True,
        related_name='saved_reports'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_reports'
    )
    name = models.CharField(max_length=255)
    
    # Execution info
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    execution_time_ms = models.IntegerField(null=True, blank=True)
    
    # Parameters used
    parameters = models.JSONField(default=dict)  # Filter values, date range, etc.
    
    # Results
    result_data = models.JSONField(default=dict)  # Report data
    row_count = models.IntegerField(null=True, blank=True)
    
    # Export
    export_format = models.CharField(
        max_length=20, choices=FORMAT_CHOICES, default='json'
    )
    file_url = models.URLField(blank=True)  # If exported to file
    file_size = models.IntegerField(null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'saved_reports'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.status}"


class ScheduledReport(models.Model):
    """Scheduled report delivery"""
    
    FREQUENCY_CHOICES = [
        ('once', 'One Time'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]
    
    DELIVERY_CHOICES = [
        ('email', 'Email'),
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
        ('webhook', 'Webhook'),
        ('sftp', 'SFTP'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='scheduled_reports'
    )
    name = models.CharField(max_length=255)
    
    # Schedule configuration
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    schedule_time = models.TimeField()  # Time to run
    day_of_week = models.IntegerField(null=True, blank=True)  # 0=Monday, 6=Sunday
    day_of_month = models.IntegerField(null=True, blank=True)  # 1-31
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Report parameters
    parameters = models.JSONField(default=dict)  # Default filter values
    export_format = models.CharField(max_length=20, default='pdf')
    
    # Delivery configuration
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES)
    delivery_config = models.JSONField(default=dict)  # Method-specific config
    recipients = models.JSONField(default=list)  # Email addresses, channels, etc.
    
    # Options
    include_empty = models.BooleanField(default=False)  # Send even if no data
    attach_file = models.BooleanField(default=True)
    include_link = models.BooleanField(default=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    last_status = models.CharField(max_length=20, blank=True)
    run_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scheduled_reports'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.frequency})"


class ReportDashboard(models.Model):
    """Real-time dashboards combining multiple widgets"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='report_dashboards'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Layout
    layout_type = models.CharField(
        max_length=20,
        choices=[('grid', 'Grid'), ('free', 'Free Form')],
        default='grid'
    )
    grid_columns = models.IntegerField(default=12)
    layout_config = models.JSONField(default=dict)
    
    # Theme
    theme = models.CharField(max_length=50, default='light')
    custom_css = models.TextField(blank=True)
    
    # Global filters
    global_filters = models.JSONField(default=list)
    date_range_filter = models.JSONField(default=dict)
    
    # Sharing
    is_public = models.BooleanField(default=False)
    public_token = models.CharField(max_length=100, blank=True)
    shared_with = models.JSONField(default=list)
    embed_enabled = models.BooleanField(default=False)
    
    # Auto-refresh
    auto_refresh = models.BooleanField(default=False)
    refresh_interval = models.IntegerField(default=60)  # seconds
    
    # Usage
    is_favorite = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)  # Default dashboard for user
    view_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'report_dashboards'
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name


class DashboardWidget(models.Model):
    """Widgets placed on a dashboard"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(
        ReportDashboard,
        on_delete=models.CASCADE,
        related_name='dashboard_widgets'
    )
    widget = models.ForeignKey(
        ReportWidget,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='dashboard_placements'
    )
    
    # Allow standalone widget config for quick widgets
    widget_type = models.CharField(max_length=50, blank=True)
    config = models.JSONField(default=dict)
    
    # Position
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=4)
    height = models.IntegerField(default=3)
    
    # Override settings
    title_override = models.CharField(max_length=255, blank=True)
    config_overrides = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dashboard_widgets'
        ordering = ['position_y', 'position_x']


class DataSource(models.Model):
    """Available data sources for reports"""
    
    SOURCE_TYPES = [
        ('model', 'Database Model'),
        ('query', 'Custom Query'),
        ('api', 'External API'),
        ('file', 'File Upload'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    
    # Model-based source
    model_name = models.CharField(max_length=100, blank=True)
    app_label = models.CharField(max_length=100, blank=True)
    
    # Available fields
    fields = models.JSONField(default=list)  # Field definitions
    relationships = models.JSONField(default=list)  # Related models
    
    # Aggregations allowed
    allowed_aggregations = models.JSONField(default=list)
    
    # Permissions
    requires_permission = models.CharField(max_length=100, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'report_data_sources'
        ordering = ['display_name']
    
    def __str__(self):
        return self.display_name


class ReportFolder(models.Model):
    """Folders for organizing reports"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='report_folders'
    )
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    color = models.CharField(max_length=20, blank=True)
    icon = models.CharField(max_length=50, blank=True)
    
    # Sharing
    is_shared = models.BooleanField(default=False)
    shared_with = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'report_folders'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ReportSubscription(models.Model):
    """User subscriptions to reports"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='report_subscriptions'
    )
    scheduled_report = models.ForeignKey(
        ScheduledReport,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    
    # Delivery preferences
    delivery_method = models.CharField(max_length=20, default='email')
    delivery_address = models.CharField(max_length=255)  # Email, Slack channel, etc.
    
    # Options
    include_summary = models.BooleanField(default=True)
    include_full_report = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'report_subscriptions'
        unique_together = ['user', 'scheduled_report']
    
    def __str__(self):
        return f"{self.user.email} -> {self.scheduled_report.name}"
