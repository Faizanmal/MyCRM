from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Dashboard(models.Model):
    """User dashboard configurations"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboards')
    is_default = models.BooleanField(default=False)
    layout = models.JSONField(default=dict)  # Dashboard layout configuration
    widgets = models.JSONField(default=list)  # List of widgets and their configurations
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_dashboards'
        verbose_name = 'Dashboard'
        verbose_name_plural = 'Dashboards'
    
    def __str__(self):
        return f"{self.name} - {self.user.get_full_name()}"


class Report(models.Model):
    """Custom reports"""
    REPORT_TYPE_CHOICES = [
        ('contacts', 'Contacts'),
        ('leads', 'Leads'),
        ('opportunities', 'Opportunities'),
        ('tasks', 'Tasks'),
        ('communications', 'Communications'),
        ('sales', 'Sales'),
        ('custom', 'Custom'),
    ]
    
    FORMAT_CHOICES = [
        ('table', 'Table'),
        ('chart', 'Chart'),
        ('graph', 'Graph'),
        ('summary', 'Summary'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='table')
    
    # Query configuration
    filters = models.JSONField(default=dict, blank=True)
    fields = models.JSONField(default=list, blank=True)
    group_by = models.JSONField(default=list, blank=True)
    order_by = models.JSONField(default=list, blank=True)
    
    # Chart configuration
    chart_config = models.JSONField(default=dict, blank=True)
    
    # Access control
    is_public = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(User, blank=True, related_name='shared_reports')
    
    # Ownership
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_reports'
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
    
    def __str__(self):
        return self.name


class ReportSchedule(models.Model):
    """Scheduled report generation"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='schedules')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    day_of_week = models.IntegerField(null=True, blank=True)  # 0-6 (Monday-Sunday)
    day_of_month = models.IntegerField(null=True, blank=True)  # 1-31
    time = models.TimeField(default='09:00')
    
    # Recipients
    recipients = models.JSONField(default=list, blank=True)  # List of email addresses
    
    # Status
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_report_schedules'
        verbose_name = 'Report Schedule'
        verbose_name_plural = 'Report Schedules'
    
    def __str__(self):
        return f"{self.report.name} - {self.frequency}"


class Analytics(models.Model):
    """Analytics and metrics tracking"""
    METRIC_TYPE_CHOICES = [
        ('count', 'Count'),
        ('sum', 'Sum'),
        ('average', 'Average'),
        ('percentage', 'Percentage'),
        ('growth', 'Growth Rate'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPE_CHOICES)
    
    # Data source
    model_name = models.CharField(max_length=100)  # Django model name
    field_name = models.CharField(max_length=100, blank=True, null=True)
    filters = models.JSONField(default=dict, blank=True)
    
    # Calculation
    calculation = models.TextField(blank=True, null=True)  # Custom calculation logic
    
    # Time period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_analytics'
        verbose_name = 'Analytics'
        verbose_name_plural = 'Analytics'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.period_start.strftime('%Y-%m-%d')}"


class KPIMetric(models.Model):
    """Key Performance Indicators"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    target_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    current_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    
    # Calculation
    calculation_method = models.TextField(blank=True, null=True)
    data_source = models.CharField(max_length=100, blank=True, null=True)
    
    # Display
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Ownership
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_kpi_metrics'
        verbose_name = 'KPI Metric'
        verbose_name_plural = 'KPI Metrics'
        ordering = ['display_order']
    
    def __str__(self):
        return self.name
    
    @property
    def achievement_percentage(self):
        """Calculate achievement percentage against target"""
        if self.target_value and self.current_value:
            return (self.current_value / self.target_value) * 100
        return 0


class DataExport(models.Model):
    """Track data exports"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    EXPORT_TYPE_CHOICES = [
        ('contacts', 'Contacts'),
        ('leads', 'Leads'),
        ('opportunities', 'Opportunities'),
        ('tasks', 'Tasks'),
        ('communications', 'Communications'),
        ('custom', 'Custom'),
    ]
    
    name = models.CharField(max_length=200)
    export_type = models.CharField(max_length=20, choices=EXPORT_TYPE_CHOICES)
    format = models.CharField(max_length=10, default='csv')  # csv, excel, pdf, json
    
    # Configuration
    filters = models.JSONField(default=dict, blank=True)
    fields = models.JSONField(default=list, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    record_count = models.IntegerField(default=0)
    
    # Error handling
    error_message = models.TextField(blank=True, null=True)
    
    # Ownership
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'crm_data_exports'
        verbose_name = 'Data Export'
        verbose_name_plural = 'Data Exports'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.status}"