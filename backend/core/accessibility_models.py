"""
Accessibility Models and Services
WCAG 2.1 compliance, voice commands, screen reader optimization
"""

import uuid

from django.contrib.auth import get_user_model
from django.db import models


class AccessibilityPreference(models.Model):
    """User-specific accessibility settings"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='accessibility_preferences'
    )

    # Visual Settings
    high_contrast_mode = models.BooleanField(default=False)
    color_blind_mode = models.CharField(
        max_length=20,
        choices=[
            ('none', 'None'),
            ('protanopia', 'Protanopia (Red-blind)'),
            ('deuteranopia', 'Deuteranopia (Green-blind)'),
            ('tritanopia', 'Tritanopia (Blue-blind)'),
            ('achromatopsia', 'Achromatopsia (Monochrome)'),
        ],
        default='none'
    )
    font_size_multiplier = models.FloatField(default=1.0)  # 0.75 to 2.0
    reduce_motion = models.BooleanField(default=False)
    reduce_transparency = models.BooleanField(default=False)

    # Focus & Navigation
    enhanced_focus_indicators = models.BooleanField(default=True)
    keyboard_shortcuts_enabled = models.BooleanField(default=True)
    skip_links_enabled = models.BooleanField(default=True)
    focus_trap_dialogs = models.BooleanField(default=True)

    # Screen Reader Optimization
    screen_reader_mode = models.BooleanField(default=False)
    announce_notifications = models.BooleanField(default=True)
    announce_page_changes = models.BooleanField(default=True)
    detailed_aria_labels = models.BooleanField(default=True)

    # Voice Control
    voice_commands_enabled = models.BooleanField(default=False)
    voice_language = models.CharField(max_length=10, default='en-US')
    voice_speed = models.FloatField(default=1.0)  # Speech rate

    # Cognitive Accessibility
    simplified_interface = models.BooleanField(default=False)
    extended_timeouts = models.BooleanField(default=False)
    timeout_multiplier = models.FloatField(default=1.0)  # 1.0 to 5.0
    reading_mask = models.BooleanField(default=False)
    dyslexia_font = models.BooleanField(default=False)

    # Audio Settings
    audio_descriptions_enabled = models.BooleanField(default=False)
    notification_sounds = models.BooleanField(default=True)
    sound_volume = models.FloatField(default=1.0)  # 0.0 to 1.0

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Accessibility preferences for {self.user}"


class VoiceCommand(models.Model):
    """Custom voice command definitions"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Command details
    phrase = models.CharField(max_length=255)
    aliases = models.JSONField(default=list)  # Alternative phrases
    action = models.CharField(max_length=100)  # Action to perform
    action_params = models.JSONField(default=dict)  # Parameters

    # Scope
    SCOPE_CHOICES = [
        ('global', 'Global'),
        ('navigation', 'Navigation'),
        ('forms', 'Forms'),
        ('data', 'Data Actions'),
        ('custom', 'Custom'),
    ]
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='global')

    # Context
    context_required = models.CharField(max_length=100, blank=True)  # Page/component context

    # Status
    is_system = models.BooleanField(default=False)  # Built-in commands
    is_active = models.BooleanField(default=True)

    # Analytics
    usage_count = models.IntegerField(default=0)
    last_used_at = models.DateTimeField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scope', 'phrase']

    def __str__(self):
        return f"{self.phrase} -> {self.action}"


class KeyboardShortcut(models.Model):
    """Custom keyboard shortcuts"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Shortcut details
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    key_combination = models.CharField(max_length=50)  # e.g., "Ctrl+Shift+N"
    action = models.CharField(max_length=100)
    action_params = models.JSONField(default=dict)

    # Scope
    SCOPE_CHOICES = [
        ('global', 'Global'),
        ('navigation', 'Navigation'),
        ('editing', 'Editing'),
        ('search', 'Search'),
        ('custom', 'Custom'),
    ]
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='global')
    context = models.CharField(max_length=100, blank=True)  # Where it applies

    # Status
    is_system = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    can_override = models.BooleanField(default=True)

    # User overrides
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='custom_shortcuts'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['key_combination', 'user', 'context']
        ordering = ['scope', 'name']

    def __str__(self):
        return f"{self.name} ({self.key_combination})"


class AccessibilityAuditLog(models.Model):
    """Log accessibility feature usage for improvement"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # User
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='accessibility_logs'
    )
    session_id = models.CharField(max_length=100)

    # Event
    EVENT_CHOICES = [
        ('feature_enabled', 'Feature Enabled'),
        ('feature_disabled', 'Feature Disabled'),
        ('voice_command', 'Voice Command Used'),
        ('keyboard_shortcut', 'Keyboard Shortcut Used'),
        ('screen_reader_interaction', 'Screen Reader Interaction'),
        ('skip_link_used', 'Skip Link Used'),
        ('focus_trap_exit', 'Focus Trap Exit'),
        ('error_announcement', 'Error Announcement'),
    ]
    event_type = models.CharField(max_length=50, choices=EVENT_CHOICES)

    # Details
    feature_name = models.CharField(max_length=100, blank=True)
    details = models.JSONField(default=dict)

    # Context
    page_url = models.URLField(blank=True)
    component = models.CharField(max_length=100, blank=True)

    # Metadata
    user_agent = models.TextField(blank=True)
    assistive_tech = models.CharField(max_length=100, blank=True)  # Detected AT

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class AccessibilityIssue(models.Model):
    """Track reported accessibility issues"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Reporter
    reported_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_accessibility_issues'
    )

    # Issue details
    title = models.CharField(max_length=255)
    description = models.TextField()

    # Categorization
    CATEGORY_CHOICES = [
        ('visual', 'Visual'),
        ('audio', 'Audio'),
        ('motor', 'Motor'),
        ('cognitive', 'Cognitive'),
        ('screen_reader', 'Screen Reader'),
        ('keyboard', 'Keyboard Navigation'),
        ('voice', 'Voice Control'),
        ('other', 'Other'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    WCAG_CRITERIA_CHOICES = [
        ('1.1.1', 'Non-text Content'),
        ('1.2.1', 'Audio-only and Video-only'),
        ('1.3.1', 'Info and Relationships'),
        ('1.4.1', 'Use of Color'),
        ('1.4.3', 'Contrast (Minimum)'),
        ('2.1.1', 'Keyboard'),
        ('2.1.2', 'No Keyboard Trap'),
        ('2.4.1', 'Bypass Blocks'),
        ('2.4.4', 'Link Purpose'),
        ('2.4.7', 'Focus Visible'),
        ('3.1.1', 'Language of Page'),
        ('3.2.1', 'On Focus'),
        ('3.3.1', 'Error Identification'),
        ('4.1.1', 'Parsing'),
        ('4.1.2', 'Name, Role, Value'),
    ]
    wcag_criteria = models.CharField(
        max_length=10,
        choices=WCAG_CRITERIA_CHOICES,
        blank=True
    )

    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('major', 'Major'),
        ('minor', 'Minor'),
        ('enhancement', 'Enhancement'),
    ]
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='major')

    # Location
    page_url = models.URLField()
    component = models.CharField(max_length=100, blank=True)
    element_selector = models.CharField(max_length=255, blank=True)

    # Status
    STATUS_CHOICES = [
        ('new', 'New'),
        ('triaged', 'Triaged'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('wont_fix', "Won't Fix"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    # Resolution
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(blank=True)

    # Metadata
    screenshot = models.URLField(blank=True)
    assistive_tech_used = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.severity})"
