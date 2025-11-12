from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Dashboard(models.Model):
    """Custom dashboards with widgets"""
    
    DASHBOARD_TYPES = [
        ('sales', 'Sales Dashboard'),
        ('marketing', 'Marketing Dashboard'),
        ('executive', 'Executive Dashboard'),
        ('team', 'Team Dashboard'),
        ('custom', 'Custom Dashboard'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    dashboard_type = models.CharField(max_length=50, choices=DASHBOARD_TYPES)
    layout = models.JSONField(default=dict, help_text="Dashboard layout configuration")
    is_default = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False, help_text="Visible to all users")
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_dashboards')
    shared_with = models.ManyToManyField(User, related_name='shared_dashboards', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_dashboard'
        ordering = ['name']
        indexes = [
            models.Index(fields=['owner', 'dashboard_type']),
            models.Index(fields=['is_default', 'is_public']),
        ]
    
    def __str__(self):
        return self.name


class DashboardWidget(models.Model):
    """Individual widgets for dashboards"""
    
    WIDGET_TYPES = [
        ('metric', 'Metric Card'),
        ('chart_line', 'Line Chart'),
        ('chart_bar', 'Bar Chart'),
        ('chart_pie', 'Pie Chart'),
        ('chart_area', 'Area Chart'),
        ('table', 'Data Table'),
        ('funnel', 'Funnel Chart'),
        ('heatmap', 'Heat Map'),
        ('list', 'List View'),
        ('progress', 'Progress Bar'),
        ('gauge', 'Gauge'),
        ('map', 'Geographic Map'),
    ]
    
    DATA_SOURCES = [
        ('leads', 'Leads'),
        ('contacts', 'Contacts'),
        ('opportunities', 'Opportunities'),
        ('tasks', 'Tasks'),
        ('campaigns', 'Campaigns'),
        ('activities', 'Activities'),
        ('custom_query', 'Custom Query'),
    ]
    
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='widgets')
    name = models.CharField(max_length=200)
    widget_type = models.CharField(max_length=50, choices=WIDGET_TYPES)
    data_source = models.CharField(max_length=50, choices=DATA_SOURCES)
    
    # Widget configuration
    query_config = models.JSONField(default=dict, help_text="Query parameters for data fetching")
    display_config = models.JSONField(default=dict, help_text="Display settings (colors, labels, etc.)")
    refresh_interval = models.IntegerField(default=300, help_text="Refresh interval in seconds")
    
    # Layout position
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=4, help_text="Grid width (1-12)")
    height = models.IntegerField(default=4, help_text="Grid height units")
    
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_dashboard_widget'
        ordering = ['dashboard', 'order']
        indexes = [
            models.Index(fields=['dashboard', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.name}"


class Report(models.Model):
    """Custom reports with filters and export options"""
    
    REPORT_TYPES = [
        ('sales_performance', 'Sales Performance'),
        ('lead_analysis', 'Lead Analysis'),
        ('pipeline_forecast', 'Pipeline Forecast'),
        ('campaign_roi', 'Campaign ROI'),
        ('team_productivity', 'Team Productivity'),
        ('revenue_analysis', 'Revenue Analysis'),
        ('custom', 'Custom Report'),
    ]
    
    EXPORT_FORMATS = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    
    # Report configuration
    data_sources = models.JSONField(default=list, help_text="List of data sources")
    filters = models.JSONField(default=dict, help_text="Report filters")
    columns = models.JSONField(default=list, help_text="Columns to include")
    grouping = models.JSONField(default=list, help_text="Group by fields")
    sorting = models.JSONField(default=list, help_text="Sort order")
    calculations = models.JSONField(default=dict, help_text="Calculations and aggregations")
    
    # Export settings
    export_format = models.CharField(max_length=20, choices=EXPORT_FORMATS, default='pdf')
    include_charts = models.BooleanField(default=True)
    include_summary = models.BooleanField(default=True)
    
    # Sharing
    is_public = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_reports')
    shared_with = models.ManyToManyField(User, related_name='advanced_shared_reports', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_generated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'crm_report'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'report_type']),
            models.Index(fields=['is_public']),
        ]
    
    def __str__(self):
        return self.name


class ReportSchedule(models.Model):
    """Scheduled report delivery"""
    
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]
    
    DELIVERY_METHODS = [
        ('email', 'Email'),
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
        ('webhook', 'Webhook'),
    ]
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='schedules')
    name = models.CharField(max_length=200)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHODS)
    
    # Schedule configuration
    schedule_time = models.TimeField(help_text="Time to send (24-hour format)")
    day_of_week = models.IntegerField(null=True, blank=True, help_text="0=Monday, 6=Sunday")
    day_of_month = models.IntegerField(null=True, blank=True, help_text="1-31")
    
    # Delivery configuration
    recipients = models.JSONField(default=list, help_text="Email addresses or user IDs")
    delivery_config = models.JSONField(default=dict, help_text="Additional delivery settings")
    
    is_active = models.BooleanField(default=True)
    last_sent_at = models.DateTimeField(null=True, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='report_schedules')
    
    class Meta:
        db_table = 'crm_report_schedule'
        ordering = ['next_run_at']
        indexes = [
            models.Index(fields=['is_active', 'next_run_at']),
            models.Index(fields=['report']),
        ]
    
    def __str__(self):
        return f"{self.report.name} - {self.get_frequency_display()}"


class ReportExecution(models.Model):
    """Log of report executions"""
    
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='executions')
    schedule = models.ForeignKey(ReportSchedule, on_delete=models.SET_NULL, null=True, blank=True, related_name='executions')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    filters_used = models.JSONField(default=dict)
    rows_returned = models.IntegerField(null=True, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    executed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='report_executions')
    
    class Meta:
        db_table = 'crm_report_execution'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['report', '-started_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.report.name} - {self.status} - {self.started_at}"


class KPI(models.Model):
    """Key Performance Indicators"""
    
    KPI_TYPES = [
        ('revenue', 'Revenue'),
        ('conversion_rate', 'Conversion Rate'),
        ('win_rate', 'Win Rate'),
        ('average_deal_size', 'Average Deal Size'),
        ('sales_cycle_length', 'Sales Cycle Length'),
        ('lead_response_time', 'Lead Response Time'),
        ('customer_acquisition_cost', 'Customer Acquisition Cost'),
        ('custom', 'Custom KPI'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    kpi_type = models.CharField(max_length=50, choices=KPI_TYPES)
    
    # Calculation
    calculation_formula = models.TextField(help_text="Python expression or query")
    data_source = models.JSONField(default=dict)
    
    # Target settings
    target_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50, default='number', help_text="e.g., currency, percentage")
    
    # Display settings
    display_format = models.CharField(max_length=50, default='number')
    color_good = models.CharField(max_length=7, default='#10B981')
    color_warning = models.CharField(max_length=7, default='#F59E0B')
    color_bad = models.CharField(max_length=7, default='#EF4444')
    
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kpis')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_kpi'
        ordering = ['name']
        indexes = [
            models.Index(fields=['kpi_type', 'is_active']),
            models.Index(fields=['owner']),
        ]
    
    def __str__(self):
        return self.name


class KPIValue(models.Model):
    """Historical KPI values"""
    
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE, related_name='values')
    value = models.DecimalField(max_digits=15, decimal_places=2)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Comparison with previous period
    previous_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    change_percentage = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    
    metadata = models.JSONField(default=dict, help_text="Additional context")
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_kpi_value'
        ordering = ['-period_end']
        indexes = [
            models.Index(fields=['kpi', '-period_end']),
        ]
        unique_together = ['kpi', 'period_start', 'period_end']
    
    def __str__(self):
        return f"{self.kpi.name} - {self.value} ({self.period_start.date()})"
