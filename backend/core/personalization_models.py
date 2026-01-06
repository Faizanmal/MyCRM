"""
Personalized User Experience Models - Adaptive UI, smart defaults, and user preferences.
"""

import uuid

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models


class UserPreferenceProfile(models.Model):
    """Stores comprehensive user preferences for personalization."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preference_profile'
    )

    # Dashboard preferences
    default_dashboard = models.CharField(max_length=100, default='overview')
    dashboard_layout = models.JSONField(default=dict)  # Widget positions and sizes
    pinned_widgets = ArrayField(models.CharField(max_length=100), default=list)
    hidden_widgets = ArrayField(models.CharField(max_length=100), default=list)

    # Navigation preferences
    favorite_pages = ArrayField(models.CharField(max_length=200), default=list)
    recent_pages = models.JSONField(default=list)  # List of {path, timestamp}
    sidebar_collapsed = models.BooleanField(default=False)
    sidebar_favorites = ArrayField(models.CharField(max_length=100), default=list)

    # Display preferences
    list_density = models.CharField(
        max_length=20,
        choices=[('compact', 'Compact'), ('comfortable', 'Comfortable'), ('spacious', 'Spacious')],
        default='comfortable'
    )
    default_list_view = models.CharField(
        max_length=20,
        choices=[('table', 'Table'), ('grid', 'Grid'), ('kanban', 'Kanban')],
        default='table'
    )
    items_per_page = models.PositiveIntegerField(default=25)

    # Notification preferences
    notification_channels = models.JSONField(default=dict)  # {channel: enabled}
    notification_quiet_hours = models.JSONField(default=dict)  # {start, end, timezone}
    notification_digest = models.CharField(
        max_length=20,
        choices=[('realtime', 'Real-time'), ('hourly', 'Hourly'), ('daily', 'Daily')],
        default='realtime'
    )

    # Smart features
    smart_suggestions_enabled = models.BooleanField(default=True)
    predictive_actions_enabled = models.BooleanField(default=True)
    auto_complete_enabled = models.BooleanField(default=True)

    # Context preferences
    default_filters = models.JSONField(default=dict)  # {page: filter_config}
    saved_views = models.JSONField(default=dict)  # {entity: [views]}

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'personalization_user_preference_profile'
        verbose_name = 'User Preference Profile'
        verbose_name_plural = 'User Preference Profiles'


class UserBehaviorEvent(models.Model):
    """Tracks user behavior for learning preferences."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='behavior_events'
    )

    # Event details
    event_type = models.CharField(max_length=50)  # page_view, click, search, etc.
    event_category = models.CharField(max_length=50)  # navigation, action, preference
    event_target = models.CharField(max_length=200)  # Element or page targeted
    event_data = models.JSONField(default=dict)

    # Context
    page_path = models.CharField(max_length=500)
    session_id = models.CharField(max_length=100)
    device_type = models.CharField(max_length=20)  # desktop, mobile, tablet

    # Timing
    duration_ms = models.PositiveIntegerField(null=True)  # Time spent on action
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'personalization_user_behavior_event'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['session_id']),
        ]


class SmartDefault(models.Model):
    """AI-learned default values for forms and actions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='smart_defaults'
    )

    # Context
    entity_type = models.CharField(max_length=50)  # lead, contact, opportunity, etc.
    field_name = models.CharField(max_length=100)
    context = models.JSONField(default=dict)  # Conditions for this default

    # Default value
    default_value = models.JSONField()
    confidence = models.FloatField(default=0.0)  # 0-1 confidence score
    source = models.CharField(
        max_length=20,
        choices=[('learned', 'AI Learned'), ('explicit', 'User Set'), ('org', 'Organization')]
    )

    # Usage tracking
    times_used = models.PositiveIntegerField(default=0)
    times_overridden = models.PositiveIntegerField(default=0)
    last_used_at = models.DateTimeField(null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'personalization_smart_default'
        unique_together = ['user', 'entity_type', 'field_name', 'context']


class ContextualHelp(models.Model):
    """Contextual help and onboarding content."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Targeting
    page_pattern = models.CharField(max_length=200)  # Regex or glob pattern
    element_selector = models.CharField(max_length=200, blank=True)
    user_segment = models.CharField(max_length=50, blank=True)  # new, intermediate, advanced

    # Content
    title = models.CharField(max_length=200)
    content = models.TextField()
    content_type = models.CharField(
        max_length=20,
        choices=[
            ('tooltip', 'Tooltip'),
            ('popover', 'Popover'),
            ('modal', 'Modal'),
            ('tour_step', 'Tour Step'),
            ('inline', 'Inline Help'),
        ]
    )

    # Display settings
    trigger = models.CharField(
        max_length=20,
        choices=[('hover', 'Hover'), ('click', 'Click'), ('auto', 'Automatic'), ('manual', 'Manual')],
        default='auto'
    )
    position = models.CharField(max_length=20, default='bottom')  # top, bottom, left, right
    delay_ms = models.PositiveIntegerField(default=0)

    # Targeting rules
    show_once = models.BooleanField(default=False)
    show_for_new_users_only = models.BooleanField(default=False)
    min_days_since_signup = models.PositiveIntegerField(default=0)
    required_features = ArrayField(models.CharField(max_length=100), default=list)

    # Media
    image_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'personalization_contextual_help'
        ordering = ['-priority', 'title']


class UserHelpProgress(models.Model):
    """Tracks which help content users have seen."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='help_progress'
    )
    help_content = models.ForeignKey(
        ContextualHelp,
        on_delete=models.CASCADE,
        related_name='user_progress'
    )

    seen_at = models.DateTimeField(auto_now_add=True)
    dismissed = models.BooleanField(default=False)
    found_helpful = models.BooleanField(null=True)  # null = no feedback

    class Meta:
        db_table = 'personalization_user_help_progress'
        unique_together = ['user', 'help_content']


class OnboardingTour(models.Model):
    """Multi-step onboarding tours."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)

    # Targeting
    target_audience = models.CharField(
        max_length=50,
        choices=[
            ('all', 'All Users'),
            ('new', 'New Users'),
            ('role_based', 'Role Based'),
            ('feature', 'Feature Users'),
        ],
        default='new'
    )
    target_roles = ArrayField(models.CharField(max_length=50), default=list)

    # Settings
    auto_start = models.BooleanField(default=False)
    can_skip = models.BooleanField(default=True)
    show_progress = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'personalization_onboarding_tour'


class OnboardingStep(models.Model):
    """Individual steps in an onboarding tour."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tour = models.ForeignKey(
        OnboardingTour,
        on_delete=models.CASCADE,
        related_name='steps'
    )

    order = models.PositiveIntegerField()

    # Content
    title = models.CharField(max_length=200)
    content = models.TextField()

    # Targeting
    page_path = models.CharField(max_length=200)
    element_selector = models.CharField(max_length=200)

    # Display
    position = models.CharField(max_length=20, default='bottom')
    highlight_element = models.BooleanField(default=True)
    allow_interaction = models.BooleanField(default=False)

    # Actions
    required_action = models.CharField(max_length=100, blank=True)  # click, input, etc.
    action_selector = models.CharField(max_length=200, blank=True)

    # Media
    image_url = models.URLField(blank=True)

    class Meta:
        db_table = 'personalization_onboarding_step'
        ordering = ['tour', 'order']
        unique_together = ['tour', 'order']


class UserTourProgress(models.Model):
    """Tracks user progress through tours."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tour_progress'
    )
    tour = models.ForeignKey(
        OnboardingTour,
        on_delete=models.CASCADE,
        related_name='user_progress'
    )

    current_step = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('not_started', 'Not Started'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('skipped', 'Skipped'),
        ],
        default='not_started'
    )

    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'personalization_user_tour_progress'
        unique_together = ['user', 'tour']


class AdaptiveUIRule(models.Model):
    """Rules for adapting UI based on user behavior."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Conditions (AND logic)
    conditions = models.JSONField(default=list)
    # Example: [
    #   {"type": "behavior", "metric": "page_views", "page": "/deals", "operator": ">=", "value": 10},
    #   {"type": "time", "metric": "days_since_signup", "operator": ">=", "value": 7}
    # ]

    # Actions
    actions = models.JSONField(default=list)
    # Example: [
    #   {"type": "show_widget", "widget": "deals_summary"},
    #   {"type": "set_default", "field": "dashboard", "value": "deals_focused"}
    # ]

    priority = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'personalization_adaptive_ui_rule'
        ordering = ['-priority']


class UserInsight(models.Model):
    """AI-generated insights about user behavior and preferences."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='insights'
    )

    insight_type = models.CharField(max_length=50)
    # workflow_optimization, unused_feature, productivity_tip, etc.

    title = models.CharField(max_length=200)
    description = models.TextField()
    recommendation = models.TextField(blank=True)

    # Data supporting the insight
    supporting_data = models.JSONField(default=dict)
    confidence = models.FloatField(default=0.0)

    # User interaction
    status = models.CharField(
        max_length=20,
        choices=[
            ('new', 'New'),
            ('viewed', 'Viewed'),
            ('acted', 'Acted Upon'),
            ('dismissed', 'Dismissed'),
        ],
        default='new'
    )

    # Validity
    valid_until = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'personalization_user_insight'
        ordering = ['-created_at']


class QuickAction(models.Model):
    """User-configured quick actions and shortcuts."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quick_actions'
    )

    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='zap')
    color = models.CharField(max_length=20, default='blue')

    # Action definition
    action_type = models.CharField(
        max_length=30,
        choices=[
            ('navigate', 'Navigate'),
            ('create', 'Create Record'),
            ('search', 'Search'),
            ('filter', 'Apply Filter'),
            ('command', 'Run Command'),
            ('workflow', 'Start Workflow'),
        ]
    )
    action_config = models.JSONField(default=dict)

    # Keyboard shortcut
    keyboard_shortcut = models.CharField(max_length=50, blank=True)

    # Placement
    show_in_toolbar = models.BooleanField(default=True)
    show_in_command_palette = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'personalization_quick_action'
        ordering = ['order', 'name']
