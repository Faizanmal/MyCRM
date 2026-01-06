"""
User Preferences Models
Stores user settings, notification preferences, and customization options
"""


from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class UserPreference(models.Model):
    """
    Stores user preferences for appearance, dashboard, and behavior
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preferences'
    )

    # Appearance Settings
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('system', 'System'),
    ]
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='system')
    accent_color = models.CharField(max_length=7, default='#3b82f6')  # Hex color
    font_size = models.IntegerField(default=14, validators=[MinValueValidator(12), MaxValueValidator(20)])
    compact_mode = models.BooleanField(default=False)
    animations_enabled = models.BooleanField(default=True)
    high_contrast = models.BooleanField(default=False)

    # Dashboard Settings
    DEFAULT_VIEW_CHOICES = [
        ('overview', 'Overview'),
        ('pipeline', 'Pipeline'),
        ('activity', 'Activity'),
        ('analytics', 'Analytics'),
    ]
    default_view = models.CharField(max_length=20, choices=DEFAULT_VIEW_CHOICES, default='overview')
    sidebar_collapsed = models.BooleanField(default=False)
    show_welcome_message = models.BooleanField(default=True)
    auto_refresh_enabled = models.BooleanField(default=True)
    auto_refresh_interval = models.IntegerField(default=30, validators=[MinValueValidator(10), MaxValueValidator(300)])

    # Dashboard Layout (JSON field for widget positions)
    dashboard_layout = models.JSONField(default=dict, blank=True)

    # Privacy Settings
    share_activity_with_team = models.BooleanField(default=True)
    show_online_status = models.BooleanField(default=True)
    allow_mentions = models.BooleanField(default=True)
    data_export_enabled = models.BooleanField(default=True)

    # Sound Settings
    sound_enabled = models.BooleanField(default=True)
    sound_volume = models.IntegerField(default=70, validators=[MinValueValidator(0), MaxValueValidator(100)])

    # Keyboard Shortcuts (JSON field)
    keyboard_shortcuts = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Preference'
        verbose_name_plural = 'User Preferences'

    def __str__(self):
        return f"Preferences for {self.user.username}"

    @classmethod
    def get_or_create_for_user(cls, user):
        """Get or create preferences for a user"""
        obj, created = cls.objects.get_or_create(user=user)
        return obj

    def get_default_keyboard_shortcuts(self):
        """Return default keyboard shortcuts"""
        return {
            'search': '⌘+K',
            'newContact': '⌘+Shift+C',
            'newDeal': '⌘+Shift+D',
            'newTask': '⌘+Shift+T',
            'help': '⌘+/',
        }


class NotificationPreference(models.Model):
    """
    Stores notification preferences for different notification types
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='core_notification_preferences'
    )

    # Channel Toggles
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)

    # Quiet Hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(default='22:00')
    quiet_hours_end = models.TimeField(default='08:00')
    quiet_hours_days = models.JSONField(default=list, blank=True)  # ['Mon', 'Tue', ...]

    # Digest Settings
    digest_enabled = models.BooleanField(default=True)
    DIGEST_FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]
    digest_frequency = models.CharField(max_length=10, choices=DIGEST_FREQUENCY_CHOICES, default='daily')
    digest_time = models.TimeField(default='09:00')
    digest_include_ai = models.BooleanField(default=True)
    digest_include_metrics = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'

    def __str__(self):
        return f"Notification Preferences for {self.user.username}"


class NotificationTypeSetting(models.Model):
    """
    Individual notification type settings
    """
    notification_preference = models.ForeignKey(
        NotificationPreference,
        on_delete=models.CASCADE,
        related_name='type_settings'
    )

    NOTIFICATION_TYPE_CHOICES = [
        # Deals
        ('deal_stage_change', 'Deal Stage Changes'),
        ('deal_won', 'Deal Won'),
        ('deal_lost', 'Deal Lost'),
        ('deal_assigned', 'Deal Assigned'),
        # Tasks
        ('task_due_soon', 'Task Due Soon'),
        ('task_overdue', 'Task Overdue'),
        ('task_assigned', 'Task Assigned'),
        # Social
        ('mention', 'Mentions'),
        ('comment', 'Comments'),
        ('team_activity', 'Team Activity'),
        # System
        ('system_updates', 'System Updates'),
        ('security_alerts', 'Security Alerts'),
        # AI
        ('ai_recommendations', 'AI Recommendations'),
        ('ai_insights', 'AI Insights'),
    ]
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)

    # Channel settings for this type
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)

    FREQUENCY_CHOICES = [
        ('instant', 'Instant'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='instant')

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')

    class Meta:
        unique_together = ['notification_preference', 'notification_type']
        verbose_name = 'Notification Type Setting'
        verbose_name_plural = 'Notification Type Settings'

    def __str__(self):
        return f"{self.notification_type} settings for {self.notification_preference.user.username}"


class ExportJob(models.Model):
    """
    Tracks data export jobs
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='export_jobs'
    )

    FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('xlsx', 'Excel'),
    ]
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='csv')

    entities = models.JSONField(default=list)  # List of entity types

    DATE_RANGE_CHOICES = [
        ('all', 'All Time'),
        ('year', 'Last Year'),
        ('quarter', 'Last Quarter'),
        ('month', 'Last Month'),
    ]
    date_range = models.CharField(max_length=10, choices=DATE_RANGE_CHOICES, default='all')

    include_archived = models.BooleanField(default=False)
    include_deleted = models.BooleanField(default=False)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.BigIntegerField(null=True, blank=True)  # In bytes

    error_message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Export Job'
        verbose_name_plural = 'Export Jobs'

    def __str__(self):
        return f"Export {self.id} by {self.user.username} - {self.status}"

    def mark_processing(self):
        self.status = 'processing'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])

    def mark_completed(self, file_path, file_size):
        self.status = 'completed'
        self.progress = 100
        self.file_path = file_path
        self.file_size = file_size
        self.completed_at = timezone.now()
        self.expires_at = timezone.now() + timezone.timedelta(days=7)
        self.save()

    def mark_failed(self, error_message):
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at'])


class UserRole(models.Model):
    """
    Custom roles for role-based access control
    """
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Role hierarchy level (higher = more permissions)
    level = models.IntegerField(default=0)

    # Permissions (JSON list)
    permissions = models.JSONField(default=list)

    # Color for UI display
    color = models.CharField(max_length=50, default='bg-gray-100 text-gray-700')

    is_system_role = models.BooleanField(default=False)  # Cannot be deleted

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-level']
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'

    def __str__(self):
        return self.display_name

    @classmethod
    def get_default_roles(cls):
        """Return default system roles"""
        return [
            {
                'name': 'admin',
                'display_name': 'Administrator',
                'description': 'Full system access',
                'level': 4,
                'color': 'bg-purple-100 text-purple-700',
                'is_system_role': True,
                'permissions': [
                    'view_dashboard', 'view_admin_dashboard', 'view_analytics',
                    'view_contacts', 'create_contacts', 'edit_contacts', 'delete_contacts', 'export_contacts', 'import_contacts',
                    'view_deals', 'create_deals', 'edit_deals', 'delete_deals', 'close_deals',
                    'view_tasks', 'create_tasks', 'edit_tasks', 'delete_tasks', 'assign_tasks',
                    'view_team', 'manage_team', 'invite_users', 'remove_users', 'assign_roles',
                    'view_reports', 'create_reports', 'export_reports',
                    'view_settings', 'manage_settings', 'manage_integrations', 'view_billing', 'manage_billing',
                    'access_admin', 'manage_organization', 'view_audit_log',
                ],
            },
            {
                'name': 'manager',
                'display_name': 'Manager',
                'description': 'Team management and full CRM access',
                'level': 3,
                'color': 'bg-blue-100 text-blue-700',
                'is_system_role': True,
                'permissions': [
                    'view_dashboard', 'view_analytics',
                    'view_contacts', 'create_contacts', 'edit_contacts', 'delete_contacts', 'export_contacts', 'import_contacts',
                    'view_deals', 'create_deals', 'edit_deals', 'delete_deals', 'close_deals',
                    'view_tasks', 'create_tasks', 'edit_tasks', 'delete_tasks', 'assign_tasks',
                    'view_team', 'manage_team', 'invite_users',
                    'view_reports', 'create_reports', 'export_reports',
                    'view_settings', 'manage_settings',
                ],
            },
            {
                'name': 'sales_rep',
                'display_name': 'Sales Representative',
                'description': 'Standard CRM user access',
                'level': 2,
                'color': 'bg-green-100 text-green-700',
                'is_system_role': True,
                'permissions': [
                    'view_dashboard',
                    'view_contacts', 'create_contacts', 'edit_contacts',
                    'view_deals', 'create_deals', 'edit_deals', 'close_deals',
                    'view_tasks', 'create_tasks', 'edit_tasks',
                    'view_reports',
                    'view_settings',
                ],
            },
            {
                'name': 'viewer',
                'display_name': 'Viewer',
                'description': 'Read-only access',
                'level': 1,
                'color': 'bg-gray-100 text-gray-700',
                'is_system_role': True,
                'permissions': [
                    'view_dashboard',
                    'view_contacts',
                    'view_deals',
                    'view_tasks',
                    'view_reports',
                ],
            },
            {
                'name': 'guest',
                'display_name': 'Guest',
                'description': 'Limited access',
                'level': 0,
                'color': 'bg-yellow-100 text-yellow-700',
                'is_system_role': True,
                'permissions': [
                    'view_dashboard',
                ],
            },
        ]

    @classmethod
    def create_default_roles(cls):
        """Create all default system roles"""
        for role_data in cls.get_default_roles():
            cls.objects.update_or_create(
                name=role_data['name'],
                defaults=role_data
            )


class UserRoleAssignment(models.Model):
    """
    Assigns roles to users
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='role_assignments'
    )
    role = models.ForeignKey(
        UserRole,
        on_delete=models.CASCADE,
        related_name='assignments'
    )

    # Optional: restrict to specific team/organization
    team_id = models.CharField(max_length=100, blank=True, null=True)
    organization_id = models.CharField(max_length=100, blank=True, null=True)

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_roles'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'role', 'team_id', 'organization_id']
        verbose_name = 'User Role Assignment'
        verbose_name_plural = 'User Role Assignments'

    def __str__(self):
        return f"{self.user.username} - {self.role.display_name}"
