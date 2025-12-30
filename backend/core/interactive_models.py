"""
Interactive Features Models
Supports the new interactive UI components including:
- User preferences and dashboard customization
- AI recommendations
- Onboarding progress
- Global search suggestions
"""

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import uuid
import json


class UserPreferences(models.Model):
    """
    User preferences for UI customization
    Stores dashboard layout, theme, and other settings
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ui_preferences'
    )
    
    # Dashboard customization
    dashboard_layout = models.JSONField(
        default=dict,
        help_text='Widget positions and visibility settings'
    )
    
    # UI Settings
    sidebar_collapsed = models.BooleanField(default=False)
    theme = models.CharField(max_length=20, default='system')  # light, dark, system
    accent_color = models.CharField(max_length=20, default='blue')
    
    # Notification preferences
    enable_sounds = models.BooleanField(default=True)
    enable_desktop_notifications = models.BooleanField(default=True)
    
    # Quick actions
    pinned_actions = models.JSONField(
        default=list,
        help_text='List of pinned quick action IDs'
    )
    
    # Saved filters and views
    saved_filters = models.JSONField(
        default=dict,
        help_text='Saved filter presets per entity type'
    )
    
    # Recent items
    recent_items = models.JSONField(
        default=list,
        help_text='Recently accessed items for quick access'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_user_preferences'
        verbose_name = 'User Preference'
        verbose_name_plural = 'User Preferences'
    
    def __str__(self):
        return f"Preferences for {self.user}"
    
    def add_recent_item(self, entity_type: str, entity_id: str, title: str):
        """Add an item to recent items list"""
        item = {
            'type': entity_type,
            'id': entity_id,
            'title': title,
            'accessed_at': timezone.now().isoformat()
        }
        
        # Remove if already exists
        self.recent_items = [
            i for i in self.recent_items 
            if not (i['type'] == entity_type and i['id'] == entity_id)
        ]
        
        # Add to beginning and limit to 20 items
        self.recent_items.insert(0, item)
        self.recent_items = self.recent_items[:20]
        self.save(update_fields=['recent_items', 'updated_at'])


class OnboardingProgress(models.Model):
    """
    Track user onboarding progress and completed steps
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='onboarding_progress'
    )
    
    # Checklist completion
    completed_steps = models.JSONField(
        default=list,
        help_text='List of completed onboarding step IDs'
    )
    
    # Tour status
    tour_completed = models.BooleanField(default=False)
    tour_dismissed = models.BooleanField(default=False)
    tour_completed_at = models.DateTimeField(null=True, blank=True)
    
    # XP and gamification
    onboarding_xp = models.IntegerField(default=0)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'crm_onboarding_progress'
        verbose_name = 'Onboarding Progress'
        verbose_name_plural = 'Onboarding Progress'
    
    def __str__(self):
        return f"Onboarding for {self.user}"
    
    def complete_step(self, step_id: str, xp_reward: int = 0):
        """Mark a step as completed and award XP"""
        if step_id not in self.completed_steps:
            self.completed_steps.append(step_id)
            self.onboarding_xp += xp_reward
            self.save(update_fields=['completed_steps', 'onboarding_xp', 'completed_at'])
        return self.completed_steps
    
    def is_step_completed(self, step_id: str) -> bool:
        return step_id in self.completed_steps


class AIRecommendation(models.Model):
    """
    AI-generated recommendations for users
    """
    RECOMMENDATION_TYPES = [
        ('action', 'Action Required'),
        ('insight', 'Insight'),
        ('warning', 'Warning'),
        ('opportunity', 'Opportunity'),
        ('tip', 'Tip'),
    ]
    
    IMPACT_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('dismissed', 'Dismissed'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_recommendations'
    )
    
    # Recommendation details
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    impact = models.CharField(max_length=20, choices=IMPACT_LEVELS, default='medium')
    
    # Related entity (optional)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.CharField(max_length=255, null=True, blank=True)
    related_entity = GenericForeignKey('content_type', 'object_id')
    
    # Action
    action_label = models.CharField(max_length=100, blank=True)
    action_url = models.CharField(max_length=500, blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    dismissable = models.BooleanField(default=True)
    
    # AI metadata
    confidence_score = models.FloatField(default=0.8)
    reasoning = models.TextField(blank=True, help_text='AI reasoning for this recommendation')
    model_version = models.CharField(max_length=50, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'crm_ai_recommendations'
        verbose_name = 'AI Recommendation'
        verbose_name_plural = 'AI Recommendations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status', '-created_at']),
            models.Index(fields=['recommendation_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_recommendation_type_display()})"
    
    def dismiss(self):
        """Dismiss the recommendation"""
        self.status = 'dismissed'
        self.dismissed_at = timezone.now()
        self.save(update_fields=['status', 'dismissed_at'])
    
    def complete(self):
        """Mark recommendation as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])


class SearchQuery(models.Model):
    """
    Track search queries for analytics and suggestions
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='search_queries'
    )
    query = models.CharField(max_length=500)
    results_count = models.IntegerField(default=0)
    
    # What was clicked from results
    clicked_result_type = models.CharField(max_length=50, blank=True)
    clicked_result_id = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_search_queries'
        verbose_name = 'Search Query'
        verbose_name_plural = 'Search Queries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['query']),
        ]
    
    def __str__(self):
        return f"{self.query} by {self.user}"


class SmartFilter(models.Model):
    """
    Smart/saved filters for quick access
    """
    ENTITY_TYPES = [
        ('contact', 'Contact'),
        ('lead', 'Lead'),
        ('opportunity', 'Opportunity'),
        ('task', 'Task'),
        ('company', 'Company'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='smart_filters'
    )
    
    name = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=50, choices=ENTITY_TYPES)
    filter_config = models.JSONField(default=dict)
    
    # Display
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=20, blank=True)
    
    # Usage tracking
    use_count = models.IntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    # Sharing
    is_shared = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_smart_filters'
        verbose_name = 'Smart Filter'
        verbose_name_plural = 'Smart Filters'
        ordering = ['-use_count', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.entity_type})"
    
    def record_use(self):
        """Record filter usage"""
        self.use_count += 1
        self.last_used_at = timezone.now()
        self.save(update_fields=['use_count', 'last_used_at'])


class QuickAction(models.Model):
    """
    User-defined quick actions
    """
    ACTION_TYPES = [
        ('navigation', 'Navigation'),
        ('create', 'Create Entity'),
        ('workflow', 'Run Workflow'),
        ('external', 'External Link'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quick_actions'
    )
    
    name = models.CharField(max_length=100)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    
    # Action details
    action_config = models.JSONField(default=dict)
    url = models.CharField(max_length=500, blank=True)
    
    # Display
    icon = models.CharField(max_length=50, default='zap')
    color = models.CharField(max_length=20, default='blue')
    shortcut = models.CharField(max_length=20, blank=True)  # e.g., "Ctrl+Shift+N"
    
    # Ordering
    order = models.IntegerField(default=0)
    is_pinned = models.BooleanField(default=False)
    
    # Usage
    use_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_quick_actions'
        verbose_name = 'Quick Action'
        verbose_name_plural = 'Quick Actions'
        ordering = ['order', '-is_pinned', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.action_type})"
